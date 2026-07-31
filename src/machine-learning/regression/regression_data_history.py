"""
Build full-history regression_data (non-ML) for every bar — not only the latest day.

Extends the original OHLCV dataframe with calculated high+low regression fields
(no ML), plus filter/filter1-6, series_trend, intradaytech, shorttermtech tags.

Saves ONE numeric dataframe per scrip to MongoDB `regressiondata`, and filter/tech
string columns to companion collection `regressiondata_filters` (keeps each doc
under Mongo's 16MB BSON limit). Use load_dataframe(scrip) to merge both.

Usage (from this directory):
  python regression_data_history.py Yes
  python regression_data_history.py No
  python regression_data_history.py Yes RELIANCE   # single scrip smoke test
"""
import os
import sys
import time
import json
import logging

sys.path.insert(0, '../')

from pymongo import MongoClient, ASCENDING
from multiprocessing.dummy import Pool as ThreadPool

import pandas as pd
pd.options.mode.chained_assignment = None
import numpy as np

from util.util import historical_data, buy_other_indicator, is_filter_risky
from util.util_base import trend_calculator
from regression_result import (
    intraday_tech_data,
    shortterm_tech_data_buy,
    shortterm_tech_data_sell,
)
from talib.abstract import EMA, SMA

directory = '../../output' + '/regression_data_history/' + time.strftime("%d%m%y-%H%M%S")
logname = '../../output' + '/regression_data_history/log' + time.strftime("%d%m%y-%H%M%S")
os.makedirs(os.path.dirname(logname), exist_ok=True)
logging.basicConfig(filename=logname, filemode='a', level=logging.INFO)
log = logging.getLogger(__name__)

connection = MongoClient('localhost', 27017)
db = connection.Nsedata

COLLECTION = 'regressiondata'
COLLECTION_FILTERS = 'regressiondata_filters'
forecast_out = 1
dR = 2
MIN_BARS = 100

FILTER_STR_COLS = (
    'filter', 'filter1', 'filter2', 'filter3', 'filter4', 'filter5', 'filter6',
    'series_trend', 'intradaytech', 'shorttermtech',
)
_ML_STUB_KEYS = (
    'mlpValue_reg', 'kNeighboursValue_reg', 'mlpValue_cla', 'kNeighboursValue_cla',
    'mlpValue_reg_other', 'kNeighboursValue_reg_other',
    'mlpValue_cla_other', 'kNeighboursValue_cla_other',
    'forecast_mlpValue_reg', 'forecast_kNeighboursValue_reg',
    'forecast_mlpValue_cla', 'forecast_kNeighboursValue_cla',
)
_FILTER_ACC_KEYS = (
    'filter_345_avg', 'filter_345_count', 'filter_345_pct',
    'filter_avg', 'filter_count', 'filter_pct',
    'filter_pct_change_avg', 'filter_pct_change_count', 'filter_pct_change_pct',
    'filter_all_avg', 'filter_all_count', 'filter_all_pct',
    'filter_tech_avg', 'filter_tech_count', 'filter_tech_pct',
    'filter_tech_all_avg', 'filter_tech_all_count', 'filter_tech_all_pct',
    'filter_tech_all_pct_change_avg', 'filter_tech_all_pct_change_count',
    'filter_tech_all_pct_change_pct',
)


def _build_sparse_table(arr, op):
    """Sparse table for range queries. op is np.maximum or np.minimum."""
    n = len(arr)
    if n == 0:
        return np.empty((0, 0)), np.array([], dtype=int)
    log = np.zeros(n + 1, dtype=int)
    for i in range(2, n + 1):
        log[i] = log[i // 2] + 1
    k = log[n] + 1
    st = np.empty((k, n), dtype=arr.dtype)
    st[0] = arr
    for j in range(1, k):
        span = 1 << j
        half = 1 << (j - 1)
        limit = n - span + 1
        if limit <= 0:
            break
        st[j, :limit] = op(st[j - 1, :limit], st[j - 1, half:half + limit])
    return st, log


def _range_query(st, log, lo, hi, op):
    """Vectorized range query on [lo, hi) for idempotent op (max/min)."""
    n = len(lo)
    out = np.full(n, np.nan)
    length = hi - lo
    valid = length > 0
    idx = np.where(valid)[0]
    if len(idx) == 0:
        return out
    L = lo[idx]
    R = hi[idx]
    j = log[R - L]
    right = R - (1 << j)
    out[idx] = op(st[j, L], st[j, right])
    return out


def _range_stats_fast(opens, highs, lows, closes, lo, hi, tables):
    """O(n) range stats using prebuilt sparse tables."""
    st_hmax, st_lmin, st_omax, st_omin, st_cmax, st_cmin, log = tables
    n = len(highs)
    pHigh = _range_query(st_hmax, log, lo, hi, np.maximum)
    pLow = _range_query(st_lmin, log, lo, hi, np.minimum)
    omax = _range_query(st_omax, log, lo, hi, np.maximum)
    cmax = _range_query(st_cmax, log, lo, hi, np.maximum)
    omin = _range_query(st_omin, log, lo, hi, np.minimum)
    cmin = _range_query(st_cmin, log, lo, hi, np.minimum)
    pBarHigh = np.maximum(omax, cmax)
    pBarLow = np.minimum(omin, cmin)
    pHighLast = np.full(n, np.nan)
    pLowLast = np.full(n, np.nan)
    valid = (hi - lo) > 0
    pHighLast[valid] = highs[hi[valid] - 1]
    pLowLast[valid] = lows[hi[valid] - 1]
    return pHigh, pLow, pBarHigh, pBarLow, pHighLast, pLowLast


def _safe_pct(numer, denom):
    out = np.full(len(numer), np.nan, dtype=float)
    mask = (denom != 0) & np.isfinite(denom) & np.isfinite(numer)
    out[mask] = (numer[mask] - denom[mask]) * 100.0 / denom[mask]
    return out


def _period_stats(dates, opens, highs, lows, closes):
    """
    For every bar, compute period high/low/bar extremes and % changes vs that bar,
    using the same calendar-week windows as regression_high/low.
    """
    n = len(dates)
    dt = pd.to_datetime(dates).to_numpy(dtype='datetime64[D]')
    opens = np.asarray(opens, dtype=float)
    highs = np.asarray(highs, dtype=float)
    lows = np.asarray(lows, dtype=float)
    closes = np.asarray(closes, dtype=float)

    st_hmax, log = _build_sparse_table(highs, np.maximum)
    st_lmin, _ = _build_sparse_table(lows, np.minimum)
    st_omax, _ = _build_sparse_table(opens, np.maximum)
    st_omin, _ = _build_sparse_table(opens, np.minimum)
    st_cmax, _ = _build_sparse_table(closes, np.maximum)
    st_cmin, _ = _build_sparse_table(closes, np.minimum)
    tables = (st_hmax, st_lmin, st_omax, st_omin, st_cmax, st_cmin, log)

    def bounds(start_w, end_w, use_pre1_end=False):
        start = dt - np.timedelta64(start_w * 7, 'D')
        if use_pre1_end:
            end = np.empty(n, dtype='datetime64[D]')
            end[0] = dt[0]
            end[1:] = dt[:-1]
        else:
            end = dt - np.timedelta64(end_w * 7, 'D')
        lo = np.searchsorted(dt, start, side='left')
        hi = np.searchsorted(dt, end, side='right')
        return lo, hi

    result = {}

    # year5High from 10y window; year5Low/bar/last from 5y (matches regression_high)
    lo10, hi10 = bounds(522, 12, False)
    lo5, hi5 = bounds(261, 12, False)
    y5H, _, _, _, _, _ = _range_stats_fast(opens, highs, lows, closes, lo10, hi10, tables)
    _, y5L, y5BH, y5BL, hy5, ly5 = _range_stats_fast(opens, highs, lows, closes, lo5, hi5, tables)
    result['year5High'] = y5H
    result['year5Low'] = y5L
    result['year5BarHigh'] = y5BH
    result['year5BarLow'] = y5BL
    result['high_year5'] = hy5
    result['low_year5'] = ly5
    result['year5HighChange'] = _safe_pct(highs, y5H)
    result['year5LowChange'] = _safe_pct(lows, y5L)

    specs = [
        ('year2', 104, 8, False),
        ('year', 52, 4, False),
        ('month6', 26, 4, False),
        ('month3', 13, 2, False),
        ('month2', 9, 1, False),
        ('month', 4, 1, False),
        ('week3', 3, 1, False),
        ('week2', 2, 1, False),
        ('week', 1, None, True),
    ]
    for name, start_w, end_w, use_pre1 in specs:
        lo, hi = bounds(start_w, end_w, use_pre1)
        pHigh, pLow, pBarHigh, pBarLow, pHighLast, pLowLast = _range_stats_fast(
            opens, highs, lows, closes, lo, hi, tables)
        result[f'{name}High'] = pHigh
        result[f'{name}Low'] = pLow
        result[f'{name}BarHigh'] = pBarHigh
        result[f'{name}BarLow'] = pBarLow
        result[f'high_{name}'] = pHighLast
        result[f'low_{name}'] = pLowLast
        result[f'{name}HighChange'] = _safe_pct(highs, pHigh)
        result[f'{name}LowChange'] = _safe_pct(lows, pLow)

    return result


def build_base_df(data):
    hsdate, hsopen, hshigh, hslow, hsclose, hsquantity = historical_data(data)
    df = pd.DataFrame({
        'date': hsdate,
        'open': hsopen.astype(float),
        'high': hshigh.astype(float),
        'low': hslow.astype(float),
        'close': hsclose.astype(float),
        'volume': hsquantity.astype(float),
    })
    df['volume_pre'] = df['volume'].shift(1)
    df['open_pre'] = df['open'].shift(1)
    df['high_pre'] = df['high'].shift(1)
    df['low_pre'] = df['low'].shift(1)
    df['close_pre'] = df['close'].shift(1)
    df['VOL_change'] = ((df['volume'] - df['volume_pre']) / df['volume_pre']) * 100
    df['PCT_change'] = ((df['close'] - df['close_pre']) / df['close_pre']) * 100
    df['Act_PCT_change'] = df['PCT_change'].shift(-forecast_out)
    df['PCT_day_change'] = ((df['close'] - df['open']) / df['open']) * 100
    df['PCT_day_change_pre'] = ((df['close_pre'] - df['open_pre']) / df['open_pre']) * 100
    df['Act_PCT_day_change'] = df['PCT_day_change'].shift(-forecast_out)
    df['PCT_day_LH'] = ((df['high'] - df['low']) / df['low']) * 100
    df['PCT_day_LC'] = ((df['close'] - df['low']) / df['low']) * 100
    df['PCT_day_CH'] = ((df['close'] - df['high']) / df['close']) * 100
    df['PCT_day_OL'] = ((df['low'] - df['open']) / df['open']) * 100
    df['Act_PCT_day_OL'] = df['PCT_day_OL'].shift(-forecast_out)
    df['PCT_day_HO'] = ((df['high'] - df['open']) / df['open']) * 100
    df['Act_PCT_day_HO'] = df['PCT_day_HO'].shift(-forecast_out)
    df['High_change'] = ((df['high'] - df['high_pre']) / df['high_pre']) * 100
    df['Act_High_change'] = df['High_change'].shift(-forecast_out)
    df['Low_change'] = ((df['low'] - df['low_pre']) / df['low_pre']) * 100
    df['Act_Low_change'] = df['Low_change'].shift(-forecast_out)

    df['bar_high'] = np.where(df['close'] > df['open'], df['close'], df['open'])
    df['bar_low'] = np.where(df['close'] > df['open'], df['open'], df['close'])
    df['bar_high_pre'] = np.where(df['close_pre'] > df['open_pre'], df['close_pre'], df['open_pre'])
    df['bar_low_pre'] = np.where(df['close_pre'] > df['open_pre'], df['open_pre'], df['close_pre'])
    df['uptrend'] = np.where((df['bar_high'] > df['bar_high_pre']) & (df['high'] > df['high_pre']), 1, 0)
    df['downtrend'] = np.where((df['bar_low'] < df['bar_low_pre']) & (df['low'] < df['low_pre']), -1, 0)
    df['greentrend'] = np.where((df['PCT_day_change'] > 0) & (df['PCT_day_change_pre'] > 0), 1, 0)
    df['redtrend'] = np.where((df['PCT_day_change'] < 0) & (df['PCT_day_change_pre'] < 0), -1, 0)

    for n in (1, 2, 3, 4, 5, 7, 10):
        df[f'High_change{n}'] = df['high'].pct_change(n) * 100
        df[f'Low_change{n}'] = df['low'].pct_change(n) * 100

    df['EMA6'] = EMA(df, 6)
    df['EMA14'] = EMA(df, 14)
    df['EMA9'] = EMA(df, 9)
    df['EMA21'] = EMA(df, 21)
    df['EMA50'] = EMA(df, 50)
    df['EMA100'] = EMA(df, 100)
    df['EMA200'] = EMA(df, 200)
    for p in (4, 9, 25, 50, 100, 200):
        df[f'SMA{p}_raw'] = SMA(df, p)

    ma10 = df['close'].rolling(window=10).mean()
    ma21 = df['close'].rolling(window=21).mean()
    df['ma10c'] = ma10
    df['ma21c'] = ma21
    for lag, col in ((5, 'ma10c_pre5'), (10, 'ma10c_pre10'), (20, 'ma10c_pre20'), (40, 'ma10c_pre40')):
        df[col] = ma10.shift(lag)
    for lag, col in ((5, 'ma21c_pre5'), (10, 'ma21c_pre10'), (20, 'ma21c_pre20'), (40, 'ma21c_pre40')):
        df[col] = ma21.shift(lag)
    return df


def _prepare_row_dict(row):
    """Build a regression_data-like dict for filter/tech helpers (non-ML stubs)."""
    data = {}
    for k, v in row.items():
        if isinstance(v, (float, np.floating)) and (np.isnan(v) or np.isinf(v)):
            data[k] = 0.0
        elif pd.isna(v):
            data[k] = 0.0 if not isinstance(v, str) else ''
        else:
            data[k] = v
    for k in _ML_STUB_KEYS:
        data[k] = 0.0
    data['ml'] = ''
    for k in ('oi', 'contract', 'oi_next', 'contract_next'):
        data[k] = -10000.0
    for k in _FILTER_ACC_KEYS:
        data[k] = 0
    for k in ('filterbuy', 'filtersell', 'filter', 'filter1', 'filter2',
              'filter3', 'filter4', 'filter5', 'filter6'):
        data[k] = ' '
    return data


def _compute_filters_for_row(row_dict):
    """Populate filter*, series_trend, intradaytech, shorttermtech for one bar."""
    row_dict['series_trend'] = trend_calculator(row_dict)
    buy_other_indicator(row_dict, [], True, None)
    is_filter_risky(row_dict, [], 'None', None, 'filter_avg', 'filter_count', 'filter_pct', True)
    buy_tag = shortterm_tech_data_buy(row_dict, row_dict) or ''
    sell_tag = shortterm_tech_data_sell(row_dict, row_dict) or ''
    shortterm = buy_tag
    if sell_tag:
        shortterm = (buy_tag + '|' + sell_tag) if buy_tag else sell_tag
    try:
        intraday = intraday_tech_data(row_dict, daily_only=True) or ''
    except Exception:
        intraday = ''
    return {
        'filter': row_dict.get('filter', ' ') or ' ',
        'filter1': row_dict.get('filter1', ' ') or ' ',
        'filter2': row_dict.get('filter2', ' ') or ' ',
        'filter3': row_dict.get('filter3', ' ') or ' ',
        'filter4': row_dict.get('filter4', ' ') or ' ',
        'filter5': row_dict.get('filter5', ' ') or ' ',
        'filter6': row_dict.get('filter6', ' ') or ' ',
        'series_trend': row_dict.get('series_trend', '') or '',
        'intradaytech': intraday,
        'shorttermtech': shortterm,
    }


def apply_filter_columns(df):
    """
    For every bar with enough history, compute the same non-ML filter tags used
    by regression_result (filter…filter6, series_trend, intradaytech, shorttermtech).
    """
    n = len(df)
    out = {c: [''] * n for c in FILTER_STR_COLS}
    # Need SMA / lag columns populated; skip very early bars
    start = max(MIN_BARS - 1, 0)
    records = df.to_dict('records')
    for i in range(start, n):
        try:
            row_dict = _prepare_row_dict(records[i])
            tags = _compute_filters_for_row(row_dict)
            for c, v in tags.items():
                out[c][i] = v
        except Exception as e:
            log.exception('filter row %s failed: %s', i, e)
    return pd.DataFrame(out, index=df.index)


def extend_dataframe_with_regression(scrip, df):
    """
    Extend the original OHLCV/feature dataframe with high+low non-ML regression fields.
    Returns one dataframe containing original columns + calculated columns for all rows.
    """
    out = df.copy()
    scripinfo = db.scrip.find_one({'scrip': scrip}) or {}
    close = out['close']

    out['scrip'] = scrip
    out['industry'] = scripinfo.get('industry', '')

    # MA10/MA21 already on base df (ma10c/ma21c + pre5/10/20/40); mark crossovers
    out['movingavg_crossed_up'] = (
        (out['ma21c'] < out['ma10c'])
        & (out['ma21c_pre10'] > out['ma10c_pre10'])
        & (out['ma21c_pre20'] > out['ma10c_pre20'])
        & (out['ma21c_pre40'] > out['ma10c_pre40'])
    )
    out['movingavg_crossed_down'] = (
        (out['ma21c'] > out['ma10c'])
        & (out['ma21c_pre10'] < out['ma10c_pre10'])
        & (out['ma21c_pre20'] < out['ma10c_pre20'])
        & (out['ma21c_pre40'] < out['ma10c_pre40'])
    )

    # High pipeline forecasts (High_change*) + low pipeline (Low_change*)
    out['forecast_day_VOL_change'] = out['VOL_change']
    out['forecast_day_PCT_change'] = out['High_change1']
    out['forecast_day_PCT2_change'] = out['High_change2']
    out['forecast_day_PCT3_change'] = out['High_change3']
    out['forecast_day_PCT4_change'] = out['High_change4']
    out['forecast_day_PCT5_change'] = out['High_change5']
    out['forecast_day_PCT7_change'] = out['High_change7']
    out['forecast_day_PCT10_change'] = out['High_change10']
    out['forecast_day_PCT_change_low'] = out['Low_change1']
    out['forecast_day_PCT2_change_low'] = out['Low_change2']
    out['forecast_day_PCT3_change_low'] = out['Low_change3']
    out['forecast_day_PCT4_change_low'] = out['Low_change4']
    out['forecast_day_PCT5_change_low'] = out['Low_change5']
    out['forecast_day_PCT7_change_low'] = out['Low_change7']
    out['forecast_day_PCT10_change_low'] = out['Low_change10']

    out['score'] = out['uptrend'].astype(str) + out['downtrend'].astype(str)
    out['trend'] = np.where(out['EMA21'] > out['EMA50'], 'up',
                     np.where(out['EMA21'] < out['EMA50'], 'down', 'NA'))
    out['buyIndia'] = ''
    out['sellIndia'] = ''
    out['patterns'] = ''

    for lag in range(1, 6):
        out[f'PCT_change_pre{lag}'] = out['PCT_change'].shift(lag)
        out[f'volume_pre{lag}'] = out['volume'].shift(lag)
        out[f'open_pre{lag}'] = out['open'].shift(lag)
        out[f'high_pre{lag}'] = out['high'].shift(lag)
        out[f'low_pre{lag}'] = out['low'].shift(lag)
        out[f'close_pre{lag}'] = out['close'].shift(lag)
        out[f'bar_high_pre{lag}'] = out['bar_high'].shift(lag)
        out[f'bar_low_pre{lag}'] = out['bar_low'].shift(lag)
    for lag in range(1, 9):
        out[f'PCT_day_change_pre{lag}'] = out['PCT_day_change'].shift(lag)

    stats = _period_stats(
        out['date'].values, out['open'].values, out['high'].values,
        out['low'].values, out['close'].values)
    out = pd.concat([out, pd.DataFrame(stats, index=out.index)], axis=1)

    extra = {
        'EMA6_1daysBack': out['EMA6'].shift(1),
        'EMA14_1daysBack': out['EMA14'].shift(1),
        'EMA6_2daysBack': out['EMA6'].shift(2),
        'EMA14_2daysBack': out['EMA14'].shift(2),
    }
    for lag in range(0, 9):
        e6 = out['EMA6'].shift(lag)
        e14 = out['EMA14'].shift(lag)
        name = 'ema6-14' if lag == 0 else f'ema6-14_pre{lag}'
        extra[name] = ((e6 - e14) / e14) * 100
    for p in (4, 9, 25, 50, 100, 200):
        raw = out[f'SMA{p}_raw']
        extra[f'SMA{p}'] = ((close - raw) / raw) * 100
    extra['SMA4_2daysBack'] = ((close - out['SMA4_raw'].shift(2)) / out['SMA4_raw'].shift(2)) * 100
    extra['SMA9_2daysBack'] = ((close - out['SMA9_raw'].shift(2)) / out['SMA9_raw'].shift(2)) * 100
    extra['highTail'] = np.where(
        (out['high'] - out['bar_high']) == 0, 0,
        ((out['high'] - out['bar_high']) / out['bar_high']) * 100)
    extra['lowTail'] = np.where(
        (out['bar_low'] - out['low']) == 0, 0,
        ((out['bar_low'] - out['low']) / out['bar_low']) * 100)
    for lag in (1, 2):
        h = out['high'].shift(lag)
        bh = out['bar_high'].shift(lag)
        l = out['low'].shift(lag)
        bl = out['bar_low'].shift(lag)
        extra[f'highTail_pre{lag}'] = np.where((h - bh) == 0, 0, ((h - bh) / bh) * 100)
        extra[f'lowTail_pre{lag}'] = np.where((bl - l) == 0, 0, ((bl - l) / bl) * 100)
    out = pd.concat([out, pd.DataFrame(extra, index=out.index)], axis=1)

    # Non-ML filter / tech tags for every historical bar
    filter_df = apply_filter_columns(out)
    out = pd.concat([out, filter_df], axis=1)

    # Drop intermediate SMA raw series (not needed after pct SMAs are built)
    out = out.drop(columns=[c for c in out.columns if str(c).endswith('_raw')], errors='ignore')

    skip = {
        'date', 'scrip', 'industry', 'score', 'trend',
        'buyIndia', 'sellIndia', 'patterns',
        'movingavg_crossed_up', 'movingavg_crossed_down',
        *FILTER_STR_COLS,
    }
    num_cols = [c for c in out.columns if c not in skip]
    out[num_cols] = out[num_cols].apply(pd.to_numeric, errors='coerce').round(dR)
    out = out.replace([np.inf, -np.inf], np.nan).reset_index(drop=True)
    return out


def _dataframe_to_frame(df_out):
    """Serialize dataframe to pandas split JSON with normalized date strings."""
    frame = json.loads(df_out.to_json(orient='split', date_format='iso'))
    if 'date' in frame['columns']:
        di = frame['columns'].index('date')
        for row in frame['data']:
            if isinstance(row[di], str) and 'T' in row[di]:
                row[di] = row[di][:10]
    return frame


def save_dataframe(scrip, df_out, end_date):
    """
    Save one dataframe document per scrip.

    Filter/tech string columns are stored in companion collection
    `regressiondata_filters` so the numeric history stays under Mongo's 16MB
    BSON limit.
    """
    industry = str(df_out['industry'].iloc[-1]) if 'industry' in df_out.columns and len(df_out) else ''
    filter_cols = [c for c in FILTER_STR_COLS if c in df_out.columns]
    base_df = df_out.drop(columns=filter_cols, errors='ignore')
    filter_df = df_out[filter_cols] if filter_cols else None

    base_frame = _dataframe_to_frame(base_df)
    base_doc = {
        'scrip': scrip,
        'end_date': end_date,
        'industry': industry,
        'rows': int(len(base_df)),
        'columns': base_frame['columns'],
        'dataframe': base_frame,
        'has_filters': bool(filter_cols),
    }

    col = db[COLLECTION]
    col.delete_many({'scrip': scrip})
    col.insert_one(base_doc)

    fcol = db[COLLECTION_FILTERS]
    fcol.delete_many({'scrip': scrip})
    if filter_df is not None and len(filter_cols):
        # Keep date index alignment for joins when loading
        if 'date' in df_out.columns:
            filter_df = filter_df.copy()
            filter_df.insert(0, 'date', df_out['date'].values)
        f_frame = _dataframe_to_frame(filter_df)
        fcol.insert_one({
            'scrip': scrip,
            'end_date': end_date,
            'industry': industry,
            'rows': int(len(filter_df)),
            'columns': f_frame['columns'],
            'dataframe': f_frame,
        })
    return len(df_out)


def regression_data_history(scrip):
    data = db.history.find_one({'dataset_code': scrip})
    if data is None or (np.array(data['data'])).size < MIN_BARS:
        print('Missing or very less Data for', scrip)
        return

    existing = db[COLLECTION].find_one(
        {'scrip': scrip, 'dataframe': {'$exists': True}},
        {'end_date': 1, 'has_filters': 1, 'columns': 1})
    filt_ok = db[COLLECTION_FILTERS].find_one({'scrip': scrip}, {'end_date': 1})
    cols = existing.get('columns') or [] if existing else []
    has_ma_cross = (
        'movingavg_crossed_up' in cols
        and 'movingavg_crossed_down' in cols
        and 'ma10c' in cols
        and 'ma21c' in cols
    )
    if (existing is not None
            and existing.get('end_date') == data.get('end_date')
            and existing.get('has_filters')
            and has_ma_cross
            and filt_ok is not None
            and filt_ok.get('end_date') == data.get('end_date')):
        print('Up to date, skip', scrip)
        return

    print(scrip)
    try:
        df = build_base_df(data)
        df_out = extend_dataframe_with_regression(scrip, df)
        n = save_dataframe(scrip, df_out, data.get('end_date'))
        print(f'  saved 1 dataframe ({n} rows x {len(df_out.columns)} cols) '
              f'-> {COLLECTION} + {COLLECTION_FILTERS}')
        log.info('%s saved dataframe %s rows', scrip, n)
    except Exception as e:
        print('regression_data_history failed for', scrip, e)
        log.exception('failed %s', scrip)


def ensure_indexes():
    for name, cname in ((COLLECTION, 'scrip_1_date_1'), (COLLECTION_FILTERS, 'scrip_1_date_1')):
        col = db[name]
        for idx in (cname, 'date_1'):
            try:
                col.drop_index(idx)
            except Exception:
                pass
        if name == COLLECTION:
            col.delete_many({'dataframe': {'$exists': False}})
        col.create_index([('scrip', ASCENDING)], unique=True)


def load_dataframe(scrip, include_filters=True):
    """Helper: load saved dataframe back as pandas DataFrame (merged with filters)."""
    doc = db[COLLECTION].find_one({'scrip': scrip})
    if doc is None or 'dataframe' not in doc:
        return None
    frame = doc['dataframe']
    df = pd.DataFrame(frame['data'], columns=frame['columns'], index=frame.get('index'))
    if include_filters:
        fdoc = db[COLLECTION_FILTERS].find_one({'scrip': scrip})
        if fdoc is not None and 'dataframe' in fdoc:
            fframe = fdoc['dataframe']
            fdf = pd.DataFrame(fframe['data'], columns=fframe['columns'], index=fframe.get('index'))
            # Align on position; drop duplicate date from filters if present
            if 'date' in fdf.columns and 'date' in df.columns:
                fdf = fdf.drop(columns=['date'])
            if len(fdf) == len(df):
                df = pd.concat([df.reset_index(drop=True), fdf.reset_index(drop=True)], axis=1)
            else:
                df = df.reset_index(drop=True)
                for c in fdf.columns:
                    df[c] = fdf[c].reindex(range(len(df))).values
    return df


def calculateParallel(threads=2, futures='Yes', only_scrip=None):
    ensure_indexes()
    if only_scrip:
        regression_data_history(only_scrip)
        return
    pool = ThreadPool(threads)
    scrips = [d['scrip'] for d in db.scrip.find({'futures': futures})]
    scrips.sort()
    pool.map(regression_data_history, scrips)


if __name__ == '__main__':
    if not os.path.exists(directory):
        os.makedirs(directory)
    futures = sys.argv[1] if len(sys.argv) > 1 else 'Yes'
    only = sys.argv[2] if len(sys.argv) > 2 else None
    calculateParallel(1, futures, only)
    connection.close()
