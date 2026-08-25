# Create a streamlit app that shows the mongodb data
from datetime import datetime, timedelta
import time
import pandas as pd
import numpy as np
import pymongo
import streamlit as st
from pymongo import MongoClient
import chart_preview as _chart_preview
import news_preview as _news_preview

connection = MongoClient(
    'localhost',
    27017,
    serverSelectionTimeoutMS=2500,
    maxPoolSize=16,
)
dbcl = connection.chartlink
dbnse = connection.Nsedata

# In-process TTL cache for Mongo counts / scrip sets (avoids per-row DB hits
# and Streamlit cache hashing of entire dataframe rows).
_LOOKUP_TTL = 15.0
_LOOKUPS = {}


def _lookup(key, builder):
    now = time.time()
    hit = _LOOKUPS.get(key)
    if hit and (now - hit[0]) < _LOOKUP_TTL:
        return hit[1]
    val = builder()
    _LOOKUPS[key] = (now, val)
    return val


def _cnt(coll_name, regex):
    def _b():
        try:
            return dbcl[coll_name].count_documents({'systemtime': {'$regex': regex}})
        except Exception:
            return 0
    return _lookup(('c', coll_name, regex), _b)


def _estimated_len(coll_name):
    def _b():
        try:
            return dbcl[coll_name].estimated_document_count()
        except Exception:
            return 0
    return _lookup(('n', coll_name), _b)


def _scrips(coll_name, regex=None, extra=None):
    def _b():
        q = {}
        if regex:
            q['systemtime'] = {'$regex': regex}
        if extra:
            q.update(extra)
        try:
            return frozenset(
                d['scrip']
                for d in dbcl[coll_name].find(q, {'scrip': 1, '_id': 0})
                if d.get('scrip')
            )
        except Exception:
            return frozenset()
    extra_key = None
    if extra:
        extra_key = tuple(sorted((k, str(v)) for k, v in extra.items()))
    return _lookup(('s', coll_name, regex, extra_key), _b)


def _has_scrip(coll_name, scrip, regex=None, extra=None):
    if not scrip:
        return False
    return scrip in _scrips(coll_name, regex, extra)


def _mvb_filtered_lens(kind):
    """Cached row counts for morning-volume-breakout buy/sell subsets."""
    def _b():
        df = getdf(f'morning-volume-breakout-{kind}')
        if df is None or getattr(df, 'empty', True) or 'systemtime' not in df.columns:
            n = 0 if df is None else len(df)
            return n, n
        st = df['systemtime'].astype(str)
        buy_df = df[
            (~st.str.contains('09:2', case=False, regex=True, na=False)) &
            (~st.str.contains('09:5', case=False, regex=True, na=False)) &
            (~st.str.contains('10:', case=False, regex=True, na=False)) &
            (~st.str.contains('11:', case=False, regex=True, na=False))
        ]
        buy_df_2 = df[~st.str.contains('09:2', case=False, regex=True, na=False)]
        return len(buy_df), len(buy_df_2)
    return _lookup(('mvb_lens', kind), _b)


def _chartlink_names():
    def _b():
        try:
            return set(dbcl.list_collection_names())
        except Exception:
            return set()
    return _lookup('cl_names', _b)

PAGE_MODULE_CACHE = {}

# Global collection filter
selected_collection = None

column_config_default={
    "scrip": "scrip",
    "PCT_day_change": st.column_config.NumberColumn(
            "Dch",
            format="%.2f"),
    "systemtime": "systemtime",
    "industry": "industry",
    "mlData": "mlData",
    "PCT_change": st.column_config.NumberColumn(
            "PCT_change",
            format="%.2f"),
    "PCT_day_change_pre1": st.column_config.NumberColumn(
            "PCT_day_change_pre1",
            format="%.2f"),
    "PCT_day_change_pre2":  st.column_config.NumberColumn(
            "PCT_day_change_pre2",
            format="%.2f"),
    "highTail":  st.column_config.NumberColumn(
            "highTail",
            format="%.2f"),
    "lowTail":  st.column_config.NumberColumn(
            "lowTail",
            format="%.2f"),
    "year5HighChange":  st.column_config.NumberColumn(
            "year5HighChange",
            format="%.2f"),
    "yearHighChange":  st.column_config.NumberColumn(
            "yearHighChange",
            format="%.2f"),
    "yearLowChange":  st.column_config.NumberColumn(
            "yearLowChange",
            format="%.2f"),
    "month3HighChange":  st.column_config.NumberColumn(
            "month3HighChange",
            format="%.2f"),
    "month3LowChange":  st.column_config.NumberColumn(
            "month3LowChange",
            format="%.2f"),
    "monthHighChange":  st.column_config.NumberColumn(
            "monthHighChange",
            format="%.2f"),
    "monthLowChange":  st.column_config.NumberColumn(
            "monthLowChange",
            format="%.2f"),
    "week2HighChange":  st.column_config.NumberColumn(
            "week2HighChange",
            format="%.2f"),
    "week2LowChange":  st.column_config.NumberColumn(
            "week2LowChange",
            format="%.2f"),
    "weekHighChange":  st.column_config.NumberColumn(
            "weekHighChange",
            format="%.2f"),
    "weekLowChange":  st.column_config.NumberColumn(
            "weekLowChange",
            format="%.2f"),
    "forecast_day_PCT10_change":  st.column_config.NumberColumn(
            "f10ch",
            format="%.2f"),
    "forecast_day_PCT7_change":  st.column_config.NumberColumn(
            "forecast_day_PCT7_change",
            format="%.2f"),
    "forecast_day_PCT5_change":  st.column_config.NumberColumn(
            "forecast_day_PCT5_change",
            format="%.2f"),
    "filter5": "filter5",
    "filter": "filter",
    "filter3": "filter3",
    "processor": "processor"
}

column_config_ml={
    "scrip": "scrip",
    "PCT_day_change": st.column_config.NumberColumn(
            "Dch",
            format="%.2f"),
    "industry": "industry",
    "PCT_change": st.column_config.NumberColumn(
            "PCT_change",
            format="%.2f"),
    "PCT_day_change_pre1": st.column_config.NumberColumn(
            "PCT_day_change_pre1",
            format="%.2f"),
    "PCT_day_change_pre2":  st.column_config.NumberColumn(
            "PCT_day_change_pre2",
            format="%.2f"),
    "highTail":  st.column_config.NumberColumn(
            "highTail",
            format="%.2f"),
    "lowTail":  st.column_config.NumberColumn(
            "lowTail",
            format="%.2f"),
    "kNeighboursValue_reg":  st.column_config.NumberColumn(
            "kNeighboursValue_reg",
            format="%.2f"),
    "mlpValue_reg":  st.column_config.NumberColumn(
            "mlpValue_reg",
            format="%.2f"),
    "kNeighboursValue_reg_merged":  st.column_config.NumberColumn(
            "kNeighboursValue_reg_merged",
            format="%.2f"),
    "mlpValue_reg_merged":  st.column_config.NumberColumn(
            "mlpValue_reg_merged",
            format="%.2f"),
    "year5HighChange":  st.column_config.NumberColumn(
            "year5HighChange",
            format="%.2f"),
    "yearHighChange":  st.column_config.NumberColumn(
            "yearHighChange",
            format="%.2f"),
    "yearLowChange":  st.column_config.NumberColumn(
            "yearLowChange",
            format="%.2f"),
    "month3HighChange":  st.column_config.NumberColumn(
            "month3HighChange",
            format="%.2f"),
    "month3LowChange":  st.column_config.NumberColumn(
            "month3LowChange",
            format="%.2f"),
    "monthHighChange":  st.column_config.NumberColumn(
            "monthHighChange",
            format="%.2f"),
    "monthLowChange":  st.column_config.NumberColumn(
            "monthLowChange",
            format="%.2f"),
    "week2HighChange":  st.column_config.NumberColumn(
            "week2HighChange",
            format="%.2f"),
    "week2LowChange":  st.column_config.NumberColumn(
            "week2LowChange",
            format="%.2f"),
    "weekHighChange":  st.column_config.NumberColumn(
            "weekHighChange",
            format="%.2f"),
    "weekLowChange":  st.column_config.NumberColumn(
            "weekLowChange",
            format="%.2f"),
    "forecast_day_PCT10_change":  st.column_config.NumberColumn(
            "f10ch",
            format="%.2f"),
    "forecast_day_PCT7_change":  st.column_config.NumberColumn(
            "forecast_day_PCT7_change",
            format="%.2f"),
    "forecast_day_PCT5_change":  st.column_config.NumberColumn(
            "forecast_day_PCT5_change",
            format="%.2f"),
    "filter5": "filter5",
    "filter": "filter",
    "filter3": "filter3"
}

column_config_sandlterm={
    "scrip": "scrip",
    "industry": "industry",
    "date": "date",
    "close": st.column_config.NumberColumn(
            "close",
            format="%.2f"),
    "year5HighChange":  st.column_config.NumberColumn(
            "year5HighChange",
            format="%.2f"),
    "year2HighChange":  st.column_config.NumberColumn(
            "year2HighChange",
            format="%.2f"),
    "yearHighChange":  st.column_config.NumberColumn(
            "yearHighChange",
            format="%.2f"),
    "month3HighChange":  st.column_config.NumberColumn(
            "month3HighChange",
            format="%.2f"),
    "monthHighChange":  st.column_config.NumberColumn(
            "monthHighChange",
            format="%.2f"),
    "week2HighChange":  st.column_config.NumberColumn(
            "week2HighChange",
            format="%.2f"),
    "weekHighChange":  st.column_config.NumberColumn(
            "weekHighChange",
            format="%.2f"),
    "year5LowChange":  st.column_config.NumberColumn(
            "year5LowChange",
            format="%.2f"),    
    "year2LowChange":  st.column_config.NumberColumn(
            "year2LowChange",
            format="%.2f"),
    "yearLowChange":  st.column_config.NumberColumn(
            "yearLowChange",
            format="%.2f"),
    "month3LowChange":  st.column_config.NumberColumn(
            "month3LowChange",
            format="%.2f"),
    "monthLowChange":  st.column_config.NumberColumn(
            "monthLowChange",
            format="%.2f"),
    "week2LowChange":  st.column_config.NumberColumn(
            "week2LowChange",
            format="%.2f"),
    "weekLowChange":  st.column_config.NumberColumn(
            "weekLowChange",
            format="%.2f"),
    "PCT_day_change": st.column_config.NumberColumn(
            "Dch",
            format="%.2f"),
    "PCT_change": st.column_config.NumberColumn(
            "PCT_change",
            format="%.2f"),
}

column_config_result={
    "scrip": "scrip",
    "PCT_day_change": st.column_config.NumberColumn(
            "Dch",
            format="%.2f"),
    "industry": "industry",
    "PCT_change": st.column_config.NumberColumn(
            "PCT_change",
            format="%.2f"),
    "PCT_day_change_pre1": st.column_config.NumberColumn(
            "PCT_day_change_pre1",
            format="%.2f"),
    "PCT_day_change_pre2":  st.column_config.NumberColumn(
            "PCT_day_change_pre2",
            format="%.2f"),
    "highTail":  st.column_config.NumberColumn(
            "highTail",
            format="%.2f"),
    "lowTail":  st.column_config.NumberColumn(
            "lowTail",
            format="%.2f"),
    "kNeighboursValue_reg":  st.column_config.NumberColumn(
            "kNeighboursValue_reg",
            format="%.2f"),
    "mlpValue_reg":  st.column_config.NumberColumn(
            "mlpValue_reg",
            format="%.2f"),
    "kNeighboursValue_reg_other":  st.column_config.NumberColumn(
            "kNeighboursValue_reg_other",
            format="%.2f"),
    "mlpValue_reg_other":  st.column_config.NumberColumn(
            "mlpValue_reg_other",
            format="%.2f"),
    "year5HighChange":  st.column_config.NumberColumn(
            "year5HighChange",
            format="%.2f"),
    "yearHighChange":  st.column_config.NumberColumn(
            "yearHighChange",
            format="%.2f"),
    "yearLowChange":  st.column_config.NumberColumn(
            "yearLowChange",
            format="%.2f"),
    "month3HighChange":  st.column_config.NumberColumn(
            "month3HighChange",
            format="%.2f"),
    "month3LowChange":  st.column_config.NumberColumn(
            "month3LowChange",
            format="%.2f"),
    "monthHighChange":  st.column_config.NumberColumn(
            "monthHighChange",
            format="%.2f"),
    "monthLowChange":  st.column_config.NumberColumn(
            "monthLowChange",
            format="%.2f"),
    "week2HighChange":  st.column_config.NumberColumn(
            "week2HighChange",
            format="%.2f"),
    "week2LowChange":  st.column_config.NumberColumn(
            "week2LowChange",
            format="%.2f"),
    "weekHighChange":  st.column_config.NumberColumn(
            "weekHighChange",
            format="%.2f"),
    "weekLowChange":  st.column_config.NumberColumn(
            "weekLowChange",
            format="%.2f"),
    "forecast_day_PCT10_change":  st.column_config.NumberColumn(
            "f10ch",
            format="%.2f"),
    "forecast_day_PCT7_change":  st.column_config.NumberColumn(
            "forecast_day_PCT7_change",
            format="%.2f"),
    "forecast_day_PCT5_change":  st.column_config.NumberColumn(
            "forecast_day_PCT5_change",
            format="%.2f"),
    "filter5": "filter5",
    "filter": "filter",
    "filter3": "filter3",
    "intradaytech": "intradaytech",
    "index": "index"
}

column_config_merged={
    "scrip": "scrip",
    "PCT_day_change": st.column_config.NumberColumn(
            "Dch",
            format="%.2f"),
    "systemtime": "systemtime",
    "industry": "industry",
    "mlData": "mlData",
    "PCT_change": st.column_config.NumberColumn(
            "PCT_change",
            format="%.2f"),
    "PCT_day_change_pre1": st.column_config.NumberColumn(
            "PCT_day_change_pre1",
            format="%.2f"),
    "PCT_day_change_pre2":  st.column_config.NumberColumn(
            "PCT_day_change_pre2",
            format="%.2f"),
    "highTail":  st.column_config.NumberColumn(
            "highTail",
            format="%.2f"),
    "lowTail":  st.column_config.NumberColumn(
            "lowTail",
            format="%.2f"),
    "year5HighChange":  st.column_config.NumberColumn(
            "year5HighChange",
            format="%.2f"),
    "yearHighChange":  st.column_config.NumberColumn(
            "yearHighChange",
            format="%.2f"),
    "yearLowChange":  st.column_config.NumberColumn(
            "yearLowChange",
            format="%.2f"),
    "month3HighChange":  st.column_config.NumberColumn(
            "month3HighChange",
            format="%.2f"),
    "month3LowChange":  st.column_config.NumberColumn(
            "month3LowChange",
            format="%.2f"),
    "monthHighChange":  st.column_config.NumberColumn(
            "monthHighChange",
            format="%.2f"),
    "monthLowChange":  st.column_config.NumberColumn(
            "monthLowChange",
            format="%.2f"),
    "week2HighChange":  st.column_config.NumberColumn(
            "week2HighChange",
            format="%.2f"),
    "week2LowChange":  st.column_config.NumberColumn(
            "week2LowChange",
            format="%.2f"),
    "weekHighChange":  st.column_config.NumberColumn(
            "weekHighChange",
            format="%.2f"),
    "weekLowChange":  st.column_config.NumberColumn(
            "weekLowChange",
            format="%.2f"),
    "forecast_day_PCT10_change":  st.column_config.NumberColumn(
            "f10ch",
            format="%.2f"),
    "forecast_day_PCT7_change":  st.column_config.NumberColumn(
            "forecast_day_PCT7_change",
            format="%.2f"),
    "forecast_day_PCT5_change":  st.column_config.NumberColumn(
            "forecast_day_PCT5_change",
            format="%.2f"),
    "filter5": "filter5",
    "filter": "filter",
    "filter3": "filter3",
    "processor": "processor",
    "systemtime_merged": "systemtime_merged",
    "processor_merged": "processor_merged"
}

column_order_default=["scrip",
    "PCT_day_change",
    "systemtime",
    "forecast_day_PCT10_change",
    "mlData",
    "industry",
    "PCT_change",
    "PCT_day_change_pre1",
    "PCT_day_change_pre2",
    "highTail",
    "lowTail",
    "year5HighChange",
    "yearHighChange",
    "yearLowChange",
    "month3HighChange",
    "month3LowChange",
    "monthHighChange",
    "monthLowChange",
    "week2HighChange",
    "week2LowChange",
    "weekHighChange",
    "weekLowChange",
    "forecast_day_PCT7_change",
    "forecast_day_PCT5_change",
    "filter5",
    "filter",
    "filter3",
    "processor"
]

column_order_ml=["scrip",
    "PCT_day_change",
    "industry",
    "PCT_change",
    "PCT_day_change_pre1",
    "PCT_day_change_pre2",
    "forecast_day_PCT10_change",
    "highTail",
    "lowTail",
    "kNeighboursValue_reg",
    "mlpValue_reg",
    "kNeighboursValue_reg_merged",
    "mlpValue_reg_merged",
    "year5HighChange",
    "yearHighChange",
    "yearLowChange",
    "month3HighChange",
    "month3LowChange",
    "monthHighChange",
    "monthLowChange",
    "week2HighChange",
    "week2LowChange",
    "weekHighChange",
    "weekLowChange",
    "forecast_day_PCT7_change",
    "forecast_day_PCT5_change",
    "filter5",
    "filter",
    "filter3",
]

column_order_sandlterm=["scrip",
    "date",
    "industry",
    "close",
    "year5HighChange",
    "year2HighChange",
    "yearHighChange",
    "month3HighChange",
    "monthHighChange",
    "week2HighChange",
    "weekHighChange",
    "year5LowChange",
    "year2LowChange",
    "yearLowChange",
    "month3LowChange",
    "monthLowChange",
    "week2LowChange",
    "weekLowChange",
    "PCT_day_change",
    "PCT_change",
]

column_order_result=["scrip",
    "PCT_day_change",
    "industry",
    "PCT_change",
    "PCT_day_change_pre1",
    "PCT_day_change_pre2",
    "forecast_day_PCT10_change",
    "highTail",
    "lowTail",
    "kNeighboursValue_reg",
    "mlpValue_reg",
    "kNeighboursValue_reg_other",
    "mlpValue_reg_other",
    "year5HighChange",
    "yearHighChange",
    "yearLowChange",
    "month3HighChange",
    "month3LowChange",
    "monthHighChange",
    "monthLowChange",
    "week2HighChange",
    "week2LowChange",
    "weekHighChange",
    "weekLowChange",
    "forecast_day_PCT7_change",
    "forecast_day_PCT5_change",
    "filter5",
    "filter",
    "filter3",
    "intradaytech",
    "index"
]

column_order_merged=["scrip",
    "PCT_day_change",
    "systemtime",
    "forecast_day_PCT10_change",
    "mlData",
    "industry",
    "PCT_change",
    "PCT_day_change_pre1",
    "PCT_day_change_pre2",
    "highTail",
    "lowTail",
    "year5HighChange",
    "yearHighChange",
    "yearLowChange",
    "month3HighChange",
    "month3LowChange",
    "monthHighChange",
    "monthLowChange",
    "week2HighChange",
    "week2LowChange",
    "weekHighChange",
    "weekLowChange",
    "forecast_day_PCT7_change",
    "forecast_day_PCT5_change",
    "filter5",
    "filter",
    "filter3",
    "processor",
    "systemtime_merged",
    "processor_merged"
]

column_order_p=["scrip",
    "PCT_day_change",
    "systemtime",
    "processor",
    "mlData",
    "forecast_day_PCT10_change",
    "industry",
    "PCT_change",
    "PCT_day_change_pre1",
    "PCT_day_change_pre2",
    "highTail",
    "lowTail",
    "year5HighChange",
    "yearHighChange",
    "yearLowChange",
    "month3HighChange",
    "month3LowChange",
    "monthHighChange",
    "monthLowChange",
    "week2HighChange",
    "week2LowChange",
    "weekHighChange",
    "weekLowChange",
    "forecast_day_PCT7_change",
    "forecast_day_PCT5_change",
    "filter5",
    "filter",
    "filter3",
    "systemtime_merged",
    "processor_merged"
]

chartlink1=False
chartlink0=False
chartlink2=False
testLearning=False
marketOnlyUpDown=False
zshortTerm=False

 # Function to create cumulative data in 10-minute intervals
def parse_timestamp(item):
    # Prefer explicit systemtime stored as string in DB
    sys_ts = item.get('systemtime')
    if isinstance(sys_ts, str):
        try:
            return datetime.strptime(sys_ts, '%Y-%m-%d %H:%M:%S')
        except Exception:
            # Fallback to ISO parsing if format differs
            try:
                return datetime.fromisoformat(sys_ts.replace('Z', '+00:00'))
            except Exception:
                pass
    # Other possible fields
    ts = item.get('timestamp') or item.get('time') or item.get('datetime')
    if isinstance(ts, str):
        try:
            return datetime.fromisoformat(ts.replace('Z', '+00:00'))
        except Exception:
            return None
    if ts:
        return ts
    # Last resort: use ObjectId generation time
    try:
        return item.get('_id').generation_time
    except Exception:
        return None

def create_cumulative_data(data, label):
    if not data:
        return [], []
    
    # Extract timestamps using table's stored time
    timestamps = []
    for item in data:
        ts = parse_timestamp(item)
        if ts:
            timestamps.append(ts)
    
    if not timestamps:
        return [], []
    
    # Sort timestamps
    timestamps.sort()
    
    # Find the earliest timestamp and round down to 10-minute interval
    min_time = timestamps[0].replace(second=0, microsecond=0)
    min_time = min_time.replace(minute=(min_time.minute // 10) * 10)
    
    # Find the latest timestamp
    max_time = timestamps[-1]
    
    # Create 10-minute intervals
    intervals = []
    cumulative_counts = []
    current_time = min_time
    cumulative_count = 0
    
    while current_time <= max_time + timedelta(minutes=10):
        # Count records up to current_time
        count = sum(1 for ts in timestamps if ts <= current_time)
        intervals.append(current_time)
        cumulative_counts.append(count)
        current_time += timedelta(minutes=10)
    
    return intervals, cumulative_counts
            
@st.cache_data(ttl=60)
def get_futures_scrip_set():
    """Scrips marked futures=Yes in Nsedata.scrip (F&O universe)."""
    try:
        return frozenset(
            d['scrip']
            for d in dbnse.scrip.find({'futures': 'Yes'}, {'scrip': 1})
            if d.get('scrip')
        )
    except Exception:
        return frozenset()


def highlight_sandlterm_row(df):
    """Full-row colour for sandlterm / test.py tables.

    - scrip in futures → grey
    - else industry not blank → light grey
    - else white
    """
    if df is None:
        return df
    if getattr(df, 'empty', True):
        return df.style.set_properties(**{'background-color': '#FFFFFF', 'color': 'black'})
    futures = get_futures_scrip_set()

    def _style_row(row):
        scrip = row['scrip'] if 'scrip' in row.index else None
        if scrip in futures:
            bg = '#A1A1A1'  # grey
        else:
            industry = row['industry'] if 'industry' in row.index else ''
            if industry is None or (isinstance(industry, float) and pd.isna(industry)):
                industry = ''
            if str(industry).strip():
                bg = '#D3D3D3'  # light grey
            else:
                bg = '#FFFFFF'  # white
        return [f'background-color: {bg}; color: black'] * len(row)

    return df.style.apply(_style_row, axis=1)


def highlight_category_row(df, color='NA'):
    """Highlights the entire row based on the 'Category' column value."""
    styled_df = ''
    if color == 'G':
        styled_df = df.style.set_properties(**{'background-color': '#E0FFDE', 'color': 'black'})
    elif color == 'R':
        styled_df = df.style.set_properties(**{'background-color': '#FCCFD2', 'color': 'black'})
    elif color == 'LG':
        styled_df = df.style.set_properties(**{'background-color': '#A1A1A1', 'color': 'black'})

    return styled_df

def highlight_category_column(value, systemtime, f10ch):
    """Highlights the entire row based on the 'Category' column value."""

    # if "0@@CROSSED" in value and "6@" in value and "CROSSED1DayL@GT6" not in value and "CROSSED1DayH@LT-6" not in value:
    #     return 'background-color: #fff4cf'
    # elif "0@@SUPER" in value and "6@" in value:
    #     return 'background-color: #fff4cf'
    
    
    count_9_2 = _cnt('morning-volume-breakout-buy', '09:2')

    if (count_9_2 > 10 and "H@" in value and ("09:2" in systemtime or "09:1" in systemtime)):
        return
    
    count_9_2 = _cnt('morning-volume-breakout-sell', '09:2')

    if (count_9_2 > 10 and "L@" in value and ("09:2" in systemtime or "09:1" in systemtime)):
        return

    count_9_3 = _cnt('09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)', '9:3')

    if (count_9_3 > 6 and "H@" in value and "09:" in systemtime and (float(f10ch) < 6)):
        return 

    count_9_3 = _cnt('09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)', '9:3')

    if (count_9_3 > 6 and "L@" in value and "09:" in systemtime and (float(f10ch) > -6)):
        return 

    count_9_3_s = _cnt('supertrend-morning-buy', '09:')

    if (count_9_3_s > 6 and "H@" in value and ("09:" in systemtime) and (float(f10ch) < 6)):
        return

    if (count_9_3_s > 6 and "H@" in value and "CROSSED2" not in value and (float(f10ch) < 6)):
        return

    count_9_3_s = _cnt('supertrend-morning-sell', '09:')

    if (count_9_3_s > 6 and "L@" in value and ("09:" in systemtime) and (float(f10ch) > -6)):
        return

    if (count_9_3_s > 6 and "L@" in value and "CROSSED2" not in value and (float(f10ch) > -6)):
        return
    

    # if("09:2" not in systemtime):
    
    if("H@" in value):
        if "0@@CROSSED" in value and "7@" in value and (float(f10ch) > 15) and "CROSSED1DayH@GT7@" not in value and "CROSSED1DayL@LT-7@" not in value:
            return 'background-color: #590059'
        elif "0@@SUPER" in value and "7@" in value and (float(f10ch) > 15):
            return 'background-color: #590059'
        elif "0@@CROSSED" in value and "7@" in value and (float(f10ch) >= 11) and "CROSSED1DayH@GT7@" not in value and "CROSSED1DayL@LT-7@" not in value:
            return 'background-color: #800080'
        elif "0@@SUPER" in value and "7@" in value and (float(f10ch) >= 11):
            return 'background-color: #800080'
        elif "0@@CROSSED" in value and "7@" in value and (float(f10ch) < 11):
            return 'background-color: #d8b2d8'
        elif "0@@SUPER" in value and "7@" in value and (float(f10ch) < 11):
            return 'background-color: #d8b2d8'
        elif "0@@CROSSED" in value and "2@" in value and "CROSSED1DayH@GT2@" not in value and "CROSSED1DayL@LT-2@" not in value:
            return 'background-color: #3EB9FB'
        elif "0@@SUPER" in value and "2@" in value:
            return 'background-color: #3EB9FB'
        elif "0@@CROSSED" in value and "1@" in value and (float(f10ch) > -1):
            return 'background-color: #CBEDFF'
        elif "0@@SUPER" in value and "1@" in value and (float(f10ch) > -1):
            return 'background-color: #CBEDFF'
        elif "0@@CROSSED" in value and "6@" in value and "CROSSED1DayL@GT6" not in value and "CROSSED1DayH@LT-6" not in value:
            return 'background-color: #fff4cf'
        elif "0@@SUPER" in value and "6@" in value:
            return 'background-color: #fff4cf'
        elif "0@@CROSSED" in value and (float(f10ch) > 5) and (float(f10ch) < 11):
            return 'background-color: #d8b2d8'
        elif "0@@SUPER" in value and (float(f10ch) > 5) and (float(f10ch) < 11):
            return 'background-color: #d8b2d8'
    
    if("L@" in value):
        if "0@@CROSSED" in value and "7@" in value and (float(f10ch) < -15) and "CROSSED1DayH@GT7@" not in value and "CROSSED1DayL@LT-7@" not in value:
            return 'background-color: #590059'
        elif "0@@SUPER" in value and "7@" in value and (float(f10ch) < -15):
            return 'background-color: #590059'
        elif "0@@CROSSED" in value and "7@" in value and (float(f10ch) <= -11) and "CROSSED1DayH@GT7@" not in value and "CROSSED1DayL@LT-7@" not in value:
            return 'background-color: #800080'
        elif "0@@SUPER" in value and "7@" in value and (float(f10ch) <= -11):
            return 'background-color: #800080'
        elif "0@@CROSSED" in value and "7@" in value and (float(f10ch) > -11):
            return 'background-color: #d8b2d8'
        elif "0@@SUPER" in value and "7@" in value and (float(f10ch) > -11):
            return 'background-color: #d8b2d8'
        elif "0@@CROSSED" in value and "2@" in value and "CROSSED1DayH@GT2@" not in value and "CROSSED1DayL@LT-2@" not in value:
            return 'background-color: #3EB9FB'
        elif "0@@SUPER" in value and "2@" in value:
            return 'background-color: #3EB9FB'
        elif "0@@CROSSED" in value and "1@" in value and (float(f10ch) < 1):
            return 'background-color: #CBEDFF'
        elif "0@@SUPER" in value and "1@" in value and (float(f10ch) < 1):
            return 'background-color: #CBEDFF'
        elif "0@@CROSSED" in value and "6@" in value and "CROSSED1DayL@GT6" not in value and "CROSSED1DayH@LT-6" not in value:
            return 'background-color: #fff4cf'
        elif "0@@SUPER" in value and "6@" in value:
            return 'background-color: #fff4cf'
        elif "0@@CROSSED" in value and (float(f10ch) < -5) and (float(f10ch) > -11):
            return 'background-color: #d8b2d8'
        elif "0@@SUPER" in value and (float(f10ch) < -5) and (float(f10ch) > -11):
            return 'background-color: #d8b2d8'

def _set_cell_style(styles, col, value):
    """Set a style only when col exists; never expand the styles index."""
    if col in styles.index:
        styles[col] = value
    return styles

def apply_highlight_column(row):
    """Apply highlight_category_column to mlData column with systemtime context."""
    styles = pd.Series('', index=row.index)
    try:
        if 'mlData' not in row.index:
            return styles
        ml_value = str(row.get('mlData', ''))
        systime = str(row.get('systemtime', ''))
        f10ch = str(row.get('forecast_day_PCT10_change', ''))
        _set_cell_style(styles, 'mlData', highlight_category_column(ml_value, systime, f10ch) or '')
    except Exception:
        pass
    return styles

f10_cols = [
    "forecast_day_PCT10_change",
    "forecast_day_PCT7_change",
    "forecast_day_PCT5_change",
]

def apply_f10_buy(row):
    color = highlight_category_column_f10_buy(
        row["forecast_day_PCT10_change"],
        row["forecast_day_PCT7_change"],
        row["forecast_day_PCT5_change"],
        row["systemtime"],
    )
    # use the same color for every column in the row
    return pd.Series(color, index=row.index)

def apply_f10_sell(row):
    color = highlight_category_column_f10_sell(
        row["forecast_day_PCT10_change"],
        row["forecast_day_PCT7_change"],
        row["forecast_day_PCT5_change"],
        row["systemtime"],
    )
    # use the same color for every column in the row
    return pd.Series(color, index=row.index)

@st.cache_data(ttl=10)
def highlight_category_column_f10_buy(value10, value7, value5, systemtime):
    """Highlights the entire row based on the 'Category' column value."""
    count_9_2 = _cnt('morning-volume-breakout-buy', '09:2')
    
    count_9_3 = _cnt('09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)', '9:3|9:4')

    count_9_3_s = _cnt('supertrend-morning-buy', '09:')

    count_9_3_c = _cnt('buy-morning-volume-breakout(Check-News)', '09:')

    if (count_9_2 > 10) and ("9:1" in systemtime or "09:2" in systemtime):
        return 'background-color: #A1A1A1'

    if (count_9_3_s >= 10 or count_9_3_c >= 6):
        if ("9:1" in systemtime or "09:2" in systemtime or "9:3" in systemtime or float(value10) < 6 or float(value10) > 11):
            return 'background-color: #A1A1A1'

    if (count_9_3 > 8) and "9:" in systemtime:
        if ("9:1" in systemtime or "09:2" in systemtime or "9:3" in systemtime or float(value10) < 6 or float(value10) > 11):
            return 'background-color: #A1A1A1'

    if float(value10) >= 15 and float(value7) > -2 and float(value5) > -2 and (float(value7) > (float(value10)-5) or float(value5) > (float(value10)-5)):
        return 'background-color: #590059'
    elif float(value10) >= 11 and float(value10) < 15 and float(value7) > -2 and float(value5) > -2 and (float(value7) > (float(value10)-5) or float(value5) > (float(value10)-5)):
        return 'background-color: #800080'
    elif float(value10) >= 6 and float(value10) < 11 and float(value7) > -2 and float(value5) > -2 and (float(value7) > (float(value10)-5) or float(value5) > (float(value10)-5)):
        return 'background-color: #d8b2d8'
    elif float(value10) >= 2 and float(value10) < 7 and float(value7) > -3 and float(value5) > -3 and (float(value7) > (float(value10)-4) or float(value5) > (float(value10)-4)):
        return 'background-color: #3EB9FB'
    elif float(value10) >= -2 and float(value10) < 2 and float(value7) < 2 and float(value5) < 2 and float(value7) >-2 and float(value5) > -2:
        return 'background-color: #CBEDFF'
    elif float(value10) <= -9 and float(value7) < -1 and float(value5) < -1 and ("11:" not in systemtime and "10:5" not in systemtime):
        return 'background-color: #ffd546'
    elif float(value10) <= -6 and float(value7) < 0 and float(value5) < 0  and ("11:" not in systemtime and "10:5" not in systemtime):
        return 'background-color: #fff0bc'
    elif float(value10) <= -3 and float(value7) < 2 and float(value5) < 2:
        return 'background-color: #F9FAFB'
    else:
        return 'background-color: #A1A1A1'   
        
@st.cache_data(ttl=10)
def highlight_category_column_f10_sell(value10, value7, value5, systemtime):
    count_9_2 = _cnt('morning-volume-breakout-sell', '09:2')
    
    count_9_3 = _cnt('09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)', '9:3|9:4')

    count_9_3_s = _cnt('supertrend-morning-sell', '09:')

    count_9_3_c = _cnt('sell-morning-volume-breakout(Check-News)', '09:')

    if (count_9_2 > 10) and ("9:1" in systemtime or "09:2" in systemtime):
        return 'background-color: #A1A1A1'
    
    if (count_9_3_s >= 10 or count_9_3_c >= 6):
        if ("9:1" in systemtime or "09:2" in systemtime or "9:3" in systemtime or float(value10) > -6 or float(value10) < -11):
            return 'background-color: #A1A1A1'

    if (count_9_3 > 8) and "9:" in systemtime:
        if ("9:1" in systemtime or "09:2" in systemtime or "9:3" in systemtime or float(value10) > -6 or float(value10) < -11):
            return 'background-color: #A1A1A1'

    """Highlights the entire row based on the 'Category' column value."""
    if float(value10) <= -15 and float(value5) < 2 and (float(value7) < (float(value10)+5) or float(value5) < (float(value10)+5)):
        return 'background-color: #590059'
    if float(value10) <= -11 and float(value10) > -15 and float(value7) < 2 and float(value5) < 2 and (float(value7) < (float(value10)+5) or float(value5) < (float(value10)+5)):
        return 'background-color: #800080'
    if float(value10) <= -6 and float(value10) > -11 and float(value7) < 2 and float(value5) < 2 and (float(value7) < (float(value10)+5) or float(value5) < (float(value10)+5)):
        return 'background-color: #d8b2d8'
    elif float(value10) <= -2 and float(value10) > -7 and float(value7) < 3 and float(value5) < 3 and (float(value7) < (float(value10)+4) or float(value5) < (float(value10)+4)):
        return 'background-color: #3EB9FB'
    elif float(value10) <= 2 and float(value10) > -2 and float(value7) > -2 and float(value5) > -2 and float(value7) < 2 and float(value5) < 2:
        return 'background-color: #CBEDFF'
    elif float(value10) >= 9 and float(value7) > 1 and float(value5) > 1  and ("11:" not in systemtime and "10:5" not in systemtime):
        return 'background-color: #ffd546'
    elif float(value10) >= 6 and float(value7) > 0 and float(value5) > 0  and ("11:" not in systemtime and "10:5" not in systemtime):
        return 'background-color: #fff0bc'
    elif float(value10) >= 3 and float(value7) > -2 and float(value5) > -2:
        return 'background-color: #F9FAFB'
    else:
        return 'background-color: #A1A1A1'

def apply_f10_buy_00(row):
    color = highlight_category_column_f10_buy_00(
        row["forecast_day_PCT10_change"],
        row["forecast_day_PCT7_change"],
        row["forecast_day_PCT5_change"],
        row["systemtime"],
    )
    # use the same color for every column in the row
    return pd.Series(color, index=row.index)

def apply_f10_sell_00(row):
    color = highlight_category_column_f10_sell_00(
        row["forecast_day_PCT10_change"],
        row["forecast_day_PCT7_change"],
        row["forecast_day_PCT5_change"],
        row["systemtime"],
    )
    # use the same color for every column in the row
    return pd.Series(color, index=row.index)

@st.cache_data(ttl=10)
def highlight_category_column_f10_buy_00(value10, value7, value5, systemtime):
    count_9_2 = _cnt('morning-volume-breakout-buy', '09:2')
    
    count_9_3 = _cnt('09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)', '9:3|9:4')

    count_9_3_s = _cnt('supertrend-morning-buy', '09:')

    count_9_3_c = _cnt('buy-morning-volume-breakout(Check-News)', '09:')

    if (count_9_2 > 10) and ("9:1" in systemtime or "09:2" in systemtime):
        return 'background-color: #A1A1A1'

    if (count_9_3_s >= 10 or count_9_3_c >= 6):
        if ("9:1" in systemtime or "09:2" in systemtime or "9:3" in systemtime or float(value10) < 6 or float(value10) > 11):
            return 'background-color: #A1A1A1'

    if ((count_9_3 < 8 and count_9_3_s < 6) or ("9:" not in systemtime and "10:00" not in systemtime) or (float(value10) >= 6)):
        """Highlights the entire row based on the 'Category' column value."""
        if float(value10) >= 15 and float(value7) > 7 and float(value5) > 7 and ( float(value10) > 10 or float(value7) > 10 or float(value5) > 10):
            return 'background-color: #590059'
        elif float(value10) >= 11 and float(value10) < 15 and float(value7) > 7 and float(value5) > 7 and ( float(value10) > 10 or float(value7) > 10 or float(value5) > 10):
            return 'background-color: #800080'
        elif float(value10) >= 6 and float(value10) < 11 and float(value7) > 0 and float(value5) > 0 and ( float(value10) > 7 or float(value7) > 5 or float(value5) > 5):
            return 'background-color: #d8b2d8'
        elif float(value10) >= -2 and float(value10) < 1 and float(value7) < 2 and float(value5) < 2 and float(value7) > -2 and float(value5) > -2:
            return 'background-color: #CBEDFF'
        elif float(value10) <= -9  and ("11:" not in systemtime and "10:5" not in systemtime):
            return 'background-color: #ffd546'
        elif float(value10) <= -6 and ("11:" not in systemtime and "10:5" not in systemtime):
            return 'background-color: #fff0bc'
        elif float(value10) < -3:
            return 'background-color: #A1A1A1'
        else:
            return 'background-color: #A1A1A1'
        
@st.cache_data(ttl=10)
def highlight_category_column_f10_sell_00(value10, value7, value5, systemtime):
    count_9_2 = _cnt('morning-volume-breakout-sell', '09:2')
    
    count_9_3 = _cnt('09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)', '9:3|9:4')

    count_9_3_s = _cnt('supertrend-morning-sell', '09:')

    count_9_3_c = _cnt('sell-morning-volume-breakout(Check-News)', '09:')

    if (count_9_2 > 10) and ("9:1" in systemtime or "09:2" in systemtime):
        return 'background-color: #A1A1A1'

    if (count_9_3_s >= 10 or count_9_3_c >= 6):
        if ("9:1" in systemtime or "09:2" in systemtime or "9:3" in systemtime or float(value10) > -6 or float(value10) < -11):
            return 'background-color: #A1A1A1'

    if (((count_9_3 < 8 and count_9_3_s < 6) or ("9:" not in systemtime and "10:00" not in systemtime)) or (float(value10) <= -6)):
        """Highlights the entire row based on the 'Category' column value."""
        if float(value10) <= -15 and float(value7) < -7 and float(value5) < -7 and ( float(value10) < -10 or float(value7) < -10 or float(value5) < -10):
            return 'background-color: #590059'
        elif float(value10) <= -11 and float(value10) > -15 and float(value7) < -7 and float(value5) < -7 and ( float(value10) < -10 or float(value7) < -10 or float(value5) < -10):
            return 'background-color: #800080'
        elif float(value10) <= -6 and float(value10) > -11 and float(value7) < 0 and float(value5) < 0 and ( float(value10) < -7 or float(value7) < -5 or float(value5) < -5):
            return 'background-color: #d8b2d8'
        elif float(value10) <= 2 and float(value10) > -1 and float(value7) > -2 and float(value5) > -2 and float(value7) < 2 and float(value5) < 2:
            return 'background-color: #CBEDFF'
        elif float(value10) >= 9 and ("11:" not in systemtime and "10:5" not in systemtime):
            return 'background-color: #ffd546'
        elif float(value10) >= 6 and ("11:" not in systemtime and "10:5" not in systemtime):
            return 'background-color: #fff0bc'
        elif float(value10) >= 3:
            return 'background-color: #A1A1A1'
        else:
            return 'background-color: #A1A1A1'

def apply_f10_buy_01(row):
    color = highlight_category_column_f10_buy_01(
        row["forecast_day_PCT10_change"],
        row["forecast_day_PCT7_change"],
        row["forecast_day_PCT5_change"],
        row["systemtime"],
    )
    # use the same color for every column in the row
    return pd.Series(color, index=row.index)

def apply_f10_sell_01(row):
    color = highlight_category_column_f10_sell_01(
        row["forecast_day_PCT10_change"],
        row["forecast_day_PCT7_change"],
        row["forecast_day_PCT5_change"],
        row["systemtime"],
    )
    # use the same color for every column in the row
    return pd.Series(color, index=row.index)

@st.cache_data(ttl=10)
def highlight_category_column_f10_buy_01(value10, value7, value5, systemtime):
    count_9_2 = _cnt('morning-volume-breakout-buy', '09:2')
    
    # count_9_3 = 0
    # try:
    #     coll = dbcl['09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)']
    #     count_9_3 = coll.count_documents({'systemtime': {'$regex': '9:3'}})
    # except Exception:
    #     pass

    # count_9_3_s = 0
    # try:
    #     coll = dbcl['supertrend-morning-buy']
    #     count_9_3_s = coll.count_documents({'systemtime': {'$regex': '09:'}})
    # except Exception:
    #     pass

    # count_9_3_c = 0
    # try:
    #     coll = dbcl['buy-morning-volume-breakout(Check-News)']
    #     count_9_3_c = coll.count_documents({'systemtime': {'$regex': '09:'}})
    # except Exception:
    #     pass

    # if (count_9_3_s >= 10 or count_9_3_c >= 6):
    #     return 'background-color: #A1A1A1'

    # if (((count_9_3 < 6 and count_9_3_s < 6) or ("9:3" not in systemtime and "9:4" not in systemtime))
    #     ):
    
    if (count_9_2 > 10) and ("9:1" in systemtime or "09:2" in systemtime):
        return 'background-color: #A1A1A1'
    
    """Highlights the entire row based on the 'Category' column value."""
    if float(value10) >= 15 and float(value7) > 7 and float(value5) > 7 and ( float(value10) > 10 or float(value7) > 10 or float(value5) > 10):
        return 'background-color: #590059'
    elif float(value10) >= 11 and float(value10) < 15 and float(value7) > 7 and float(value5) > 7 and ( float(value10) > 10 or float(value7) > 10 or float(value5) > 10):
        return 'background-color: #800080'
    elif float(value10) >= 6 and float(value10) < 11 and float(value7) > 0 and float(value5) > 0 and ( float(value10) > 7 or float(value7) > 5 or float(value5) > 5):
        return 'background-color: #d8b2d8'
    elif float(value10) >= -2 and float(value10) < 1 and float(value7) < 2 and float(value5) < 2 and float(value7) > -2 and float(value5) > -2:
        return 'background-color: #CBEDFF'
    elif float(value10) <= -9  and ("11:" not in systemtime and "10:5" not in systemtime):
        return 'background-color: #ffd546'
    elif float(value10) <= -6 and ("11:" not in systemtime and "10:5" not in systemtime):
        return 'background-color: #fff0bc'
    elif float(value10) < -3:
        return 'background-color: #A1A1A1'
    else:
        return 'background-color: #A1A1A1'
        
@st.cache_data(ttl=10)
def highlight_category_column_f10_sell_01(value10, value7, value5, systemtime):
    count_9_2 = _cnt('morning-volume-breakout-sell', '09:2')
    
    # count_9_3 = 0
    # try:
    #     coll = dbcl['09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)']
    #     count_9_3 = coll.count_documents({'systemtime': {'$regex': '9:3'}})
    # except Exception:
    #     pass

    # count_9_3_s = 0
    # try:
    #     coll = dbcl['supertrend-morning-sell']
    #     count_9_3_s = coll.count_documents({'systemtime': {'$regex': '09:'}})
    # except Exception:
    #     pass

    # count_9_3_c = 0
    # try:
    #     coll = dbcl['sell-morning-volume-breakout(Check-News)']
    #     count_9_3_c = coll.count_documents({'systemtime': {'$regex': '09:'}})
    # except Exception:
    #     pass

    # if (count_9_3_s >= 10 or count_9_3_c >= 6):
    #     return 'background-color: #A1A1A1'

    # if (((count_9_3 < 6 and count_9_3_s < 6) or ("9:3" not in systemtime and "9:4" not in systemtime))):
    #     """Highlights the entire row based on the 'Category' column value."""
    
    if (count_9_2 > 10) and ("9:1" in systemtime or "09:2" in systemtime):
        return 'background-color: #A1A1A1'

    if float(value10) <= -15 and float(value7) < -7 and float(value5) < -7 and ( float(value10) < -10 or float(value7) < -10 or float(value5) < -10):
        return 'background-color: #590059'
    elif float(value10) <= -11 and float(value10) > -15 and float(value7) < -7 and float(value5) < -7 and ( float(value10) < -10 or float(value7) < -10 or float(value5) < -10):
        return 'background-color: #800080'
    elif float(value10) <= -6 and float(value10) > -11 and float(value7) < 0 and float(value5) < 0 and ( float(value10) < -7 or float(value7) < -5 or float(value5) < -5):
        return 'background-color: #d8b2d8'
    elif float(value10) <= 2 and float(value10) > -1 and float(value7) > -2 and float(value5) > -2 and float(value7) < 2 and float(value5) < 2:
        return 'background-color: #CBEDFF'
    elif float(value10) >= 9 and ("11:" not in systemtime and "10:5" not in systemtime):
        return 'background-color: #ffd546'
    elif float(value10) >= 6 and ("11:" not in systemtime and "10:5" not in systemtime):
        return 'background-color: #fff0bc'
    elif float(value10) >= 3:
        return 'background-color: #A1A1A1'
    else:
        return 'background-color: #A1A1A1'

def highlight_category_column_super(value):
    """Highlights the entire row based on the 'Category' column value."""
    if "0@@SUPER" in value:
        return 'background-color: #CBC3E3'

def apply_breakout_highlight(row):
    """Return a Series of styles for a row: preserve existing mlData styles
    but force pink for mlData when systemtime contains '10:' and mlData
    indicates a 'CROSSED' event.
    """
    styles = pd.Series('', index=row.index)
    try:
        # # Only apply this special pink highlight for chartlink1 views
        # if not chartlink1 and not testLearning and not applyBreakOut:
        #     # preserve existing mlData style
        #     ml_value = str(row.get('mlData', ''))
        #     system_time = str(row.get('systemtime'))
        #     try:
        #         styles['mlData'] = highlight_category_column(ml_value, system_time) or ''
        #     except Exception:
        #         styles['mlData'] = ''
        #     return styles

        ml_value = str(row.get('mlData', ''))
        system_time = str(row.get('systemtime'))
        f10ch = float(row.get('forecast_day_PCT10_change', 0) or 0)
        f7ch = float(row.get('forecast_day_PCT7_change', 0) or 0)
        f5ch = float(row.get('forecast_day_PCT5_change', 0) or 0)
        pct_day_change = float(row.get('PCT_day_change', 0) or 0)
        pct_day_change_pre1 = float(row.get('PCT_day_change_pre1', 0) or 0)
        pct_day_change_pre2 = float(row.get('PCT_day_change_pre2', 0) or 0)
        yearHighChange = float(row.get('yearHighChange', 0) or 0)
        yearLowChange = float(row.get('yearLowChange', 0) or 0)
        week2HighChange = float(row.get('week2HighChange', 0) or 0)
        week2LowChange = float(row.get('week2LowChange', 0) or 0)
        scrip = row.get('scrip')

        # Default to existing mlData style
        existing = ''
        try:
            existing = highlight_category_column(ml_value, system_time, f10ch) or ''
        except Exception:
            existing = ''

        
        # If systemtime contains '10:' and the scrip is present in the
        # 'crossed-day-high' collection, set mlData cell to pink.
        try:
            BUY_NEWS = 'buy-morning-volume-breakout(Check-News)'
            count = _cnt(BUY_NEWS, '09:|10:00:00')

            if count < 5:
                if _has_scrip(BUY_NEWS, scrip, '09:|10:00:00|10:05|10:1|10:2|10:3') and pct_day_change < 3.5:
                    styles['scrip'] = 'background-color: #E0FFDE'
                    return styles
            else:
                if _has_scrip(BUY_NEWS, scrip, '10:2|10:3|10:4|10:50') and pct_day_change < 3.5:
                    styles['scrip'] = 'background-color: #E0FFDE'
                    return styles

            
        except Exception:
            # fallback to existing style on any DB error
            pass

        try:
            SELL_NEWS = 'sell-morning-volume-breakout(Check-News)'
            count = _cnt(SELL_NEWS, '09:|10:00:00')
            count10 = _cnt(SELL_NEWS, '10:0|10:1')

            if count < 5 and count10 < 5:
                if _has_scrip(SELL_NEWS, scrip, '09:|10:00:00|10:05|10:1|10:2|10:3') and pct_day_change > -3.5:
                    styles['scrip'] = 'background-color: #FCCFD2'
                    return styles
            elif count < 5:
                if _has_scrip(SELL_NEWS, scrip, '09:|10:00:00|10:05|10:1|10:2|10:3', extra={'yearLowChange': {'$gt': 50}}) and pct_day_change > -3.5:
                    styles['scrip'] = 'background-color: #FCCFD2'
                    return styles
            else:
                if _has_scrip(SELL_NEWS, scrip, '10:2|10:3|10:4|10:50') and pct_day_change > -3.5:
                    styles['scrip'] = 'background-color: #FCCFD2'
                    return styles
        except Exception:
            # fallback to existing style on any DB error
            pass


        try:
            buy_n, buy_n2 = _mvb_filtered_lens('buy')
            if ('10:' in system_time and '10:4' not in system_time and '10:5' not in system_time) and scrip and buy_n < 8:
                if buy_n2 < 15:
                    try:
                        if _estimated_len('crossed-day-high') < 12 and _has_scrip('crossed-day-high', scrip):
                            _set_cell_style(styles, 'mlData', 'background-color: #fb87ec')
                            return styles
                    except Exception:
                        pass
                
                try:
                    CHART_BUY = '09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)'
                    if _estimated_len(CHART_BUY) < 5 and _has_scrip(CHART_BUY, scrip):
                        _set_cell_style(styles, 'mlData', 'background-color: #fb87ec')
                        return styles
                except Exception:
                    pass

                try:
                    if _estimated_len('supertrend-morning-buy') < 5 and _has_scrip('supertrend-morning-buy', scrip, '09:5|10:'):
                        _set_cell_style(styles, 'mlData', 'background-color: #fb87ec')
                        return styles
                except Exception:
                    pass


            sell_n, sell_n2 = _mvb_filtered_lens('sell')
            if ('10:' in system_time and '10:4' not in system_time and '10:5' not in system_time) and scrip and sell_n < 8:
                if sell_n2 < 15:
                    try:
                        if _estimated_len('crossed-day-low') < 12 and _has_scrip('crossed-day-low', scrip, '09:5|10:'):
                            _set_cell_style(styles, 'mlData', 'background-color: #fb87ec')
                            return styles
                    except Exception:
                        pass

                try:
                    CHART_SELL = '09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)'
                    if _estimated_len(CHART_SELL) < 5 and _has_scrip(CHART_SELL, scrip):
                        _set_cell_style(styles, 'mlData', 'background-color: #fb87ec')
                        return styles
                except Exception:
                    pass

                try:
                    if _estimated_len('supertrend-morning-sell') < 5 and _has_scrip('supertrend-morning-sell', scrip, '09:5|10:'):
                        _set_cell_style(styles, 'mlData', 'background-color: #fb87ec')
                        return styles
                except Exception:
                    pass
        except Exception:
            # fallback to existing style on any DB error
            pass

        _set_cell_style(styles, 'mlData', existing)
    except Exception:
        pass
    return styles

def apply_breakout_highlight_volume(row):
    """Return a Series of styles for a row: preserve existing mlData styles
    but force pink for mlData when systemtime contains '10:' and mlData
    indicates a 'CROSSED' event.
    """
    styles = pd.Series('', index=row.index)
    try:
        # # Only apply this special pink highlight for chartlink1 views
        # if not chartlink1 and not testLearning and not applyBreakOut:
        #     # preserve existing mlData style
        #     ml_value = str(row.get('mlData', ''))
        #     system_time = str(row.get('systemtime'))
        #     try:
        #         styles['mlData'] = highlight_category_column(ml_value, system_time) or ''
        #     except Exception:
        #         styles['mlData'] = ''
        #     return styles

        ml_value = str(row.get('mlData', ''))
        system_time = str(row.get('systemtime'))
        f10ch = float(row.get('forecast_day_PCT10_change', 0) or 0)
        f7ch = float(row.get('forecast_day_PCT7_change', 0) or 0)
        f5ch = float(row.get('forecast_day_PCT5_change', 0) or 0)
        pct_day_change = float(row.get('PCT_day_change', 0) or 0)
        pct_day_change_pre1 = float(row.get('PCT_day_change_pre1', 0) or 0)
        pct_day_change_pre2 = float(row.get('PCT_day_change_pre2', 0) or 0)
        yearHighChange = float(row.get('yearHighChange', 0) or 0)
        yearLowChange = float(row.get('yearLowChange', 0) or 0)
        week2HighChange = float(row.get('week2HighChange', 0) or 0)
        week2LowChange = float(row.get('week2LowChange', 0) or 0)
        scrip = row.get('scrip')

        # Default to existing mlData style
        existing = ''
        try:
            existing = highlight_category_column(ml_value, system_time, f10ch) or ''
        except Exception:
            existing = ''

        if _has_scrip('Breakout-Beey-2', scrip):
            styles['scrip'] = 'background-color: #009600'
            return styles
        
        if _has_scrip('Breakout-Siill-2', scrip):
            styles['scrip'] = 'background-color: #e50e1d'
            return styles

        
    except Exception:
        pass
    return styles

def apply_breakout_highlight_ml(row):
    """Return a Series of styles for a row: preserve existing mlData styles
    but force pink for mlData when systemtime contains '10:' and mlData
    indicates a 'CROSSED' event.
    """
    styles = pd.Series('', index=row.index)
    try:
        pct_day_change = float(row.get('PCT_day_change', 0) or 0)
        scrip = row.get('scrip')

        if zshortTerm:
            if _has_scrip('Breakout-Beey-2', scrip):
                styles['scrip'] = 'background-color: #009600'
                return styles
            if _has_scrip('Breakout-Siill-2', scrip):
                styles['scrip'] = 'background-color: #e50e1d'
                return styles

    except Exception:
        pass
    return styles


def get_chartlink_collections():
    """Get list of collection names in chartlink database"""
    return sorted(_chartlink_names())

def get_collection_scrips(collection_name):
    """Get unique scrips from a collection"""
    collection = dbcl[collection_name]
    scrips = collection.distinct('scrip')
    return sorted(scrips) if scrips else []

def set_selected_collection(collection_name):
    """Set the selected collection globally"""
    global selected_collection
    selected_collection = collection_name

def get_selected_collection():
    """Get the currently selected collection"""
    global selected_collection
    return selected_collection

@st.cache_data(ttl=10)
def getdf(collection_name):
    collection = dbcl[collection_name]
    df = pd.DataFrame(list(collection.find({}, {'_id': 0})))
    
    # Filter by selected collection scrips if set
    selected_coll = get_selected_collection()
    if selected_coll and selected_coll != "All":
        try:
            scrips = get_collection_scrips(selected_coll)
            if scrips:
                df = df[df['scrip'].isin(scrips)]
        except Exception as e:
            print(f"Error filtering by collection: {e}")
    
    try:
        df['PCT_day_change'] = pd.to_numeric(df['PCT_day_change'])
        df['PCT_change'] = pd.to_numeric(df['PCT_change'], errors='coerce')
        df['PCT_day_change_pre1'] = pd.to_numeric(df['PCT_day_change_pre1'], errors='coerce')
        df['PCT_day_change_pre2'] = pd.to_numeric(df['PCT_day_change_pre2'], errors='coerce')

        df['highTail'] = pd.to_numeric(df['highTail'], errors='coerce')
        df['lowTail'] = pd.to_numeric(df['lowTail'], errors='coerce')
        df['year5HighChange'] = pd.to_numeric(df['year5HighChange'], errors='coerce')
        df['yearHighChange'] = pd.to_numeric(df['year5HighChange'], errors='coerce')
        df['yearLowChange'] = pd.to_numeric(df['yearLowChange'], errors='coerce')
        df['month3HighChange'] = pd.to_numeric(df['month3HighChange'], errors='coerce')
        df['month3LowChange'] = pd.to_numeric(df['month3LowChange'], errors='coerce')
        df['monthHighChange'] = pd.to_numeric(df['monthHighChange'], errors='coerce')
        df['monthLowChange'] = pd.to_numeric(df['monthLowChange'], errors='coerce')
        df['week2HighChange'] = pd.to_numeric(df['week2HighChange'], errors='coerce')
        df['week2LowChange'] = pd.to_numeric(df['week2LowChange'], errors='coerce')
        df['weekHighChange'] = pd.to_numeric(df['weekHighChange'], errors='coerce')
        df['weekLowChange'] = pd.to_numeric(df['weekLowChange'], errors='coerce')
        df['forecast_day_PCT10_change'] = pd.to_numeric(df['forecast_day_PCT10_change'], errors='coerce')
        df['forecast_day_PCT7_change'] = pd.to_numeric(df['forecast_day_PCT7_change'], errors='coerce')
        df['forecast_day_PCT5_change'] = pd.to_numeric(df['forecast_day_PCT5_change'], errors='coerce')
        df['systemtime'] = pd.to_datetime(df['systemtime']).dt.time.astype(str)
        df['mlData'] = df['mlData'].fillna('').astype(str)
    except KeyError as e:
        print(f"")
    return df

def _resolve_collection(collection_name):
    """Resolve a collection from chartlink (preferred) or Nsedata."""
    if collection_name in _chartlink_names():
        return dbcl[collection_name]
    return dbnse[collection_name]

def _coerce_intersect_columns(df):
    """Best-effort numeric/time coercion for intersected frames (schemas may differ)."""
    numeric_cols = [
        'PCT_day_change', 'PCT_change', 'PCT_day_change_pre1', 'PCT_day_change_pre2',
        'highTail', 'lowTail', 'year5HighChange', 'yearHighChange', 'yearLowChange',
        'month3HighChange', 'month3LowChange', 'monthHighChange', 'monthLowChange',
        'week2HighChange', 'week2LowChange', 'weekHighChange', 'weekLowChange',
        'forecast_day_PCT10_change', 'forecast_day_PCT7_change', 'forecast_day_PCT5_change',
        'forecast_day_PCT4_change', 'forecast_day_PCT3_change',
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    for col in ('systemtime', 'systemtime_merged'):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.time.astype(str)
    if 'mlData' in df.columns:
        df['mlData'] = df['mlData'].fillna('').astype(str)
    return df

@st.cache_data(ttl=10)
def getintersectdf(collection_name1, collection_name2):
    collection1 = _resolve_collection(collection_name1)
    collection2 = _resolve_collection(collection_name2)
    df1 = pd.DataFrame(list(collection1.find({}, {'_id': 0})))
    df2 = pd.DataFrame(list(collection2.find({}, {'_id': 0})))
    expected_columns = list(set(df1.columns)) if not df1.empty else []
    df = pd.DataFrame(columns=expected_columns)
    if df1.empty or df2.empty or 'scrip' not in df1.columns or 'scrip' not in df2.columns:
        return df
    try:
        df = df1.merge(
            df2,
            on='scrip',
            how='inner',
            suffixes=('', '_merged')
        )
        df = _coerce_intersect_columns(df)
    except Exception as e:
        print(f"getintersectdf error: {e}")

    return df

@st.cache_data(ttl=10)
def getintersectdf_ml(collection_name1, collection_name2):
    collection1 = dbnse[collection_name1]
    collection2 = dbnse[collection_name2]
    df1 = pd.DataFrame(list(collection1.find({}, {'_id': 0})))
    df2 = pd.DataFrame(list(collection2.find({}, {'_id': 0})))
    expected_columns = list(set(df1.columns))
    df = pd.DataFrame(columns=expected_columns)
    try:
        df = df1.merge(
            df2,
            on='scrip',
            how='inner',
            suffixes=('', '_merged')
        )
        df['PCT_day_change'] = pd.to_numeric(df['PCT_day_change'])
        df['PCT_change'] = pd.to_numeric(df['PCT_change'], errors='coerce')
        df['PCT_day_change_pre1'] = pd.to_numeric(df['PCT_day_change_pre1'], errors='coerce')
        df['PCT_day_change_pre2'] = pd.to_numeric(df['PCT_day_change_pre2'], errors='coerce')

        df['highTail'] = pd.to_numeric(df['highTail'], errors='coerce')
        df['lowTail'] = pd.to_numeric(df['lowTail'], errors='coerce')
        df['year5HighChange'] = pd.to_numeric(df['year5HighChange'], errors='coerce')
        df['yearHighChange'] = pd.to_numeric(df['year5HighChange'], errors='coerce')
        df['yearLowChange'] = pd.to_numeric(df['yearLowChange'], errors='coerce')
        df['month3HighChange'] = pd.to_numeric(df['month3HighChange'], errors='coerce')
        df['month3LowChange'] = pd.to_numeric(df['month3LowChange'], errors='coerce')
        df['monthHighChange'] = pd.to_numeric(df['monthHighChange'], errors='coerce')
        df['monthLowChange'] = pd.to_numeric(df['monthLowChange'], errors='coerce')
        df['week2HighChange'] = pd.to_numeric(df['week2HighChange'], errors='coerce')
        df['week2LowChange'] = pd.to_numeric(df['week2LowChange'], errors='coerce')
        df['weekHighChange'] = pd.to_numeric(df['weekHighChange'], errors='coerce')
        df['weekLowChange'] = pd.to_numeric(df['weekLowChange'], errors='coerce')
        df['forecast_day_PCT10_change'] = pd.to_numeric(df['forecast_day_PCT10_change'], errors='coerce')
        df['forecast_day_PCT7_change'] = pd.to_numeric(df['forecast_day_PCT7_change'], errors='coerce')
        df['forecast_day_PCT5_change'] = pd.to_numeric(df['forecast_day_PCT5_change'], errors='coerce')
        df['kNeighboursValue_reg'] = pd.to_numeric(df['kNeighboursValue_reg'], errors='coerce')
        df['mlpValue_reg'] = pd.to_numeric(df['mlpValue_reg'], errors='coerce')
        df['kNeighboursValue_reg_merged'] = pd.to_numeric(df['kNeighboursValue_reg_merged'], errors='coerce')
        df['mlpValue_reg_merged'] = pd.to_numeric(df['mlpValue_reg_merged'], errors='coerce')
    except KeyError as e:
        print(f"")

    return df

@st.cache_data(ttl=10)
def getdfResult(collection_name):
    collection = dbcl[collection_name]
    df = pd.DataFrame(list(collection.find({}, {'_id': 0})))
    
    # Filter by selected collection scrips if set
    selected_coll = get_selected_collection()
    if selected_coll and selected_coll != "All":
        try:
            scrips = get_collection_scrips(selected_coll)
            if scrips:
                df = df[df['scrip'].isin(scrips)]
        except Exception as e:
            print(f"Error filtering by collection: {e}")
    
    try:
        df['PCT_day_change'] = pd.to_numeric(df['PCT_day_change'])
        df['PCT_change'] = pd.to_numeric(df['PCT_change'], errors='coerce')
        df['PCT_day_change_pre1'] = pd.to_numeric(df['PCT_day_change_pre1'], errors='coerce')
        df['PCT_day_change_pre2'] = pd.to_numeric(df['PCT_day_change_pre2'], errors='coerce')

        df['highTail'] = pd.to_numeric(df['highTail'], errors='coerce')
        df['lowTail'] = pd.to_numeric(df['lowTail'], errors='coerce')
        df['year5HighChange'] = pd.to_numeric(df['year5HighChange'], errors='coerce')
        df['yearHighChange'] = pd.to_numeric(df['year5HighChange'], errors='coerce')
        df['yearLowChange'] = pd.to_numeric(df['yearLowChange'], errors='coerce')
        df['month3HighChange'] = pd.to_numeric(df['month3HighChange'], errors='coerce')
        df['month3LowChange'] = pd.to_numeric(df['month3LowChange'], errors='coerce')
        df['monthHighChange'] = pd.to_numeric(df['monthHighChange'], errors='coerce')
        df['monthLowChange'] = pd.to_numeric(df['monthLowChange'], errors='coerce')
        df['week2HighChange'] = pd.to_numeric(df['week2HighChange'], errors='coerce')
        df['week2LowChange'] = pd.to_numeric(df['week2LowChange'], errors='coerce')
        df['weekHighChange'] = pd.to_numeric(df['weekHighChange'], errors='coerce')
        df['weekLowChange'] = pd.to_numeric(df['weekLowChange'], errors='coerce')
        df['forecast_day_PCT10_change'] = pd.to_numeric(df['forecast_day_PCT10_change'], errors='coerce')
        df['forecast_day_PCT7_change'] = pd.to_numeric(df['forecast_day_PCT7_change'], errors='coerce')
        df['forecast_day_PCT5_change'] = pd.to_numeric(df['forecast_day_PCT5_change'], errors='coerce')
        df['systemtime'] = pd.to_datetime(df['systemtime']).dt.time.astype(str)
        df['kNeighboursValue_reg'] = pd.to_numeric(df['kNeighboursValue_reg'], errors='coerce')
        df['mlpValue_reg'] = pd.to_numeric(df['mlpValue_reg'], errors='coerce')
        df['kNeighboursValue_reg_other'] = pd.to_numeric(df['kNeighboursValue_reg_other'], errors='coerce')
        df['mlpValue_reg_other'] = pd.to_numeric(df['mlpValue_reg_other'], errors='coerce')
        df['intradaytech'] = df['intradaytech'].fillna('').astype(str)
        df['index'] = df['index'].fillna('').astype(str)
        
    except KeyError as e:
        print(f"KeyError: {e}")
    return df

def _ensure_chart_preview_sidebar():
    """Standalone report pages (not via index) still get the left-bar chart settings."""
    if 'selected_page' in st.session_state:
        return
    try:
        _chart_preview.render_sidebar_controls()
        _news_preview.render_sidebar_controls()
    except Exception as e:
        if 'duplicate' not in type(e).__name__.lower() and 'duplicate' not in str(e).lower():
            raise


def render(st, df, name, height=110, color='NA', column_order=column_order_default, column_conf=column_config_default, renderml=False, renderf10buy=False, renderf10sell=False, f10=0, renderf10buy00=False, renderf10sell00=False, renderf10buy01=False, renderf10sell01=False, applyBreakOut=False, dontapplybreakout=False, noColourFilter=False):
    _ensure_chart_preview_sidebar()
    st.write("********"+ name + "********")
    try:
        df = df[
                ((abs(df['monthLowChange']) > 3) | (abs(df['monthHighChange']) > 3)) | ((abs(df['month3LowChange']) > 10) | (abs(df['month3HighChange']) > 10))
                ]
    except KeyError as e:
        print("")
    
    try:
        df = df[
                ((abs(df['PCT_change']) - abs(df['PCT_day_change'])) < 4) 
                ]
    except KeyError as e:
        print("")

    try:
        df = df[
                (df['highTail'] < 3.3) & (df['lowTail'] < 3.3)
                ]
    except KeyError as e:
        print("")
    #
    # Main Code Execution

    if renderml:
        df_styled = highlight_category_row(df, color=color)
        if(zshortTerm) and color =='LG':
            df_styled = df_styled.apply(apply_breakout_highlight_volume, axis=1)
        _news_preview.display_dataframe(st, df_styled, height=height, column_order=column_order, column_config=column_conf, use_container_width=True)
    elif (df.empty):
        _news_preview.display_dataframe(st, df, height=height, column_order=column_order, column_config=column_conf, use_container_width=True)
    else:
        df_styled = highlight_category_row(df, color=color)
        
        if renderf10buy:
            df_styled = df_styled.apply(apply_f10_buy, axis=1)
        elif renderf10sell:
            df_styled = df_styled.apply(apply_f10_sell, axis=1)
        elif renderf10buy00:
            df_styled = df_styled.apply(apply_f10_buy_00, axis=1)
        elif renderf10sell00:
            df_styled = df_styled.apply(apply_f10_sell_00, axis=1)
        elif renderf10buy01:
            df_styled = df_styled.apply(apply_f10_buy_01, axis=1)
        elif renderf10sell01:
            df_styled = df_styled.apply(apply_f10_sell_01, axis=1)

        # highBuy/highSell-style frames may lack systemtime; skip f10 row style then
        if 'Buy' in name and 'systemtime' in df.columns:
            df_styled = df_styled.apply(apply_f10_buy_01, axis=1)
        if 'Sell' in name and 'systemtime' in df.columns:
            df_styled = df_styled.apply(apply_f10_sell_01, axis=1)
        

        
        if (not df.empty):
            if ((chartlink0) and (color == 'G' or color == 'R')):
                df_styled = df_styled.apply(apply_highlight_column, axis=1)
            else:
                df_styled = df_styled.apply(apply_highlight_column, axis=1)
    
        
        if(chartlink0 or chartlink1 or chartlink2 or zshortTerm) and (noColourFilter == False) and color =='LG':
            df_styled = df_styled.apply(apply_breakout_highlight, axis=1)
        if(chartlink0 or chartlink1 or applyBreakOut) and (dontapplybreakout != True) and (noColourFilter == False) and color =='LG':
            df_styled = df_styled.apply(apply_breakout_highlight_volume, axis=1)
        _news_preview.display_dataframe(st, df_styled, height=height, column_order=column_order, column_config=column_conf, use_container_width=True)

@st.cache_data(ttl=10)
def getdf_sandlterm(collection_name, chartink=False):
    collection = None
    if chartink:
        collection = dbcl[collection_name]
    else:
        collection = dbnse[collection_name]
    df = pd.DataFrame(list(collection.find({}, {'_id': 0})))
    
    # Filter by selected collection scrips if set
    selected_coll = get_selected_collection()
    if selected_coll and selected_coll != "All":
        try:
            scrips = get_collection_scrips(selected_coll)
            if scrips:
                df = df[df['scrip'].isin(scrips)]
        except Exception as e:
            print(f"Error filtering by collection: {e}")
    
    # try:
    #     df['PCT_day_change'] = pd.to_numeric(df['PCT_day_change'])
    #     df['PCT_change'] = pd.to_numeric(df['PCT_change'], errors='coerce')
    #     df['PCT_day_change_pre1'] = pd.to_numeric(df['PCT_day_change_pre1'], errors='coerce')
    #     df['PCT_day_change_pre2'] = pd.to_numeric(df['PCT_day_change_pre2'], errors='coerce')

    #     df['highTail'] = pd.to_numeric(df['highTail'], errors='coerce')
    #     df['lowTail'] = pd.to_numeric(df['lowTail'], errors='coerce')
    #     df['year5HighChange'] = pd.to_numeric(df['year5HighChange'], errors='coerce')
    #     df['yearHighChange'] = pd.to_numeric(df['year5HighChange'], errors='coerce')
    #     df['yearLowChange'] = pd.to_numeric(df['yearLowChange'], errors='coerce')
    #     df['month3HighChange'] = pd.to_numeric(df['month3HighChange'], errors='coerce')
    #     df['month3LowChange'] = pd.to_numeric(df['month3LowChange'], errors='coerce')
    #     df['monthHighChange'] = pd.to_numeric(df['monthHighChange'], errors='coerce')
    #     df['monthLowChange'] = pd.to_numeric(df['monthLowChange'], errors='coerce')
    #     df['week2HighChange'] = pd.to_numeric(df['week2HighChange'], errors='coerce')
    #     df['week2LowChange'] = pd.to_numeric(df['week2LowChange'], errors='coerce')
    #     df['weekHighChange'] = pd.to_numeric(df['weekHighChange'], errors='coerce')
    #     df['weekLowChange'] = pd.to_numeric(df['weekLowChange'], errors='coerce')
    #     df['forecast_day_PCT10_change'] = pd.to_numeric(df['forecast_day_PCT10_change'], errors='coerce')
    #     df['forecast_day_PCT7_change'] = pd.to_numeric(df['forecast_day_PCT7_change'], errors='coerce')
    #     df['forecast_day_PCT5_change'] = pd.to_numeric(df['forecast_day_PCT5_change'], errors='coerce')
    #     df['systemtime'] = pd.to_datetime(df['systemtime']).dt.time.astype(str)
    #     df['mlData'] = df['mlData'].fillna('').astype(str)
    # except KeyError as e:
    #     print(f"")
    return df

def render_sandlterm_data(st, df, name, height=200, color='NA', column_order=column_order_sandlterm, column_conf=column_config_sandlterm):
    _ensure_chart_preview_sidebar()
    # Newest signal date first for all sandlterm widgets
    if df is not None and not df.empty and 'date' in df.columns:
        df = df.copy()
        df['_sort_date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.sort_values('_sort_date', ascending=False, na_position='last').drop(columns=['_sort_date'])
        df = df.reset_index(drop=True)
    # test.py / sandlterm LG: futures=grey, industry set=light grey, else white
    if color == 'LG':
        df_styled = highlight_sandlterm_row(df)
    else:
        df_styled = highlight_category_row(df, color=color)
    st.write("********"+ name + "********")
    # Prefer configured order for known columns, then append any remaining df columns
    df_cols = [c for c in df.columns if c != '_id']
    preferred = [c for c in column_order if c in df_cols]
    remaining = [c for c in df_cols if c not in preferred]
    full_column_order = preferred + remaining
    _news_preview.display_dataframe(st, df_styled, height=height, column_order=full_column_order, column_config=column_conf, use_container_width=True)