#!/usr/bin/env python3
"""Query local Nsedata/chartlink MongoDB and score multi-horizon trade suggestions.

Example:
  python skills/nsedata-trade-advisor/scripts/query_suggestions.py \\
    --db Nsedata --collection highBuy --limit 20 --horizons all
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime
from typing import Any

try:
    from pymongo import MongoClient
except ImportError:
    print("pymongo is required: pip install pymongo", file=sys.stderr)
    sys.exit(1)


DEFAULT_URI = "mongodb://localhost:27017"
HORIZONS = ("intraday", "swing3_5", "short_term", "long_term")


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        f = float(value)
        if math.isnan(f) or math.isinf(f):
            return default
        return f
    except (TypeError, ValueError):
        return default


def unpack_ohlcv(doc: dict | None, limit: int | None = None) -> list[dict]:
    """Convert embedded history document to chronological OHLCV rows."""
    if not doc:
        return []
    cols = doc.get("column_names") or []
    data = doc.get("data") or []
    if not cols or not data:
        return []

    idx = {name: i for i, name in enumerate(cols)}
    required = ("Date", "Open", "High", "Low", "Close", "Volume")
    if any(r not in idx for r in required):
        return []

    rows: list[dict] = []
    for row in data:
        if not isinstance(row, (list, tuple)) or len(row) <= idx["Close"]:
            continue
        rows.append(
            {
                "date": row[idx["Date"]],
                "open": _safe_float(row[idx["Open"]]),
                "high": _safe_float(row[idx["High"]]),
                "low": _safe_float(row[idx["Low"]]),
                "close": _safe_float(row[idx["Close"]]),
                "volume": _safe_float(row[idx["Volume"]]),
            }
        )

    # Stored newest-first → chronological
    rows.reverse()
    if limit and len(rows) > limit:
        rows = rows[-limit:]
    return rows


def sma(closes: list[float], period: int) -> float | None:
    if len(closes) < period:
        return None
    return sum(closes[-period:]) / period


def rsi(closes: list[float], period: int = 14) -> float | None:
    if len(closes) < period + 1:
        return None
    gains = []
    losses = []
    for i in range(-period, 0):
        diff = closes[i] - closes[i - 1]
        gains.append(max(diff, 0.0))
        losses.append(max(-diff, 0.0))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def atr(bars: list[dict], period: int = 14) -> float | None:
    if len(bars) < period + 1:
        return None
    trs = []
    for i in range(1, len(bars)):
        h, l, pc = bars[i]["high"], bars[i]["low"], bars[i - 1]["close"]
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    window = trs[-period:]
    return sum(window) / period


def vwap(bars: list[dict]) -> float | None:
    if not bars:
        return None
    num = 0.0
    den = 0.0
    for b in bars:
        typical = (b["high"] + b["low"] + b["close"]) / 3.0
        vol = b["volume"] or 0.0
        num += typical * vol
        den += vol
    if den <= 0:
        return sum((b["high"] + b["low"] + b["close"]) / 3.0 for b in bars) / len(bars)
    return num / den


def session_bars(bars_15m: list[dict]) -> list[dict]:
    """Keep bars from the latest trade date in the 15m series."""
    if not bars_15m:
        return []
    last_date = str(bars_15m[-1]["date"])[:10]
    return [b for b in bars_15m if str(b["date"])[:10] == last_date]


def swing_high_low(bars: list[dict], lookback: int = 20) -> tuple[float | None, float | None]:
    window = bars[-lookback:] if len(bars) >= lookback else bars
    if not window:
        return None, None
    return max(b["high"] for b in window), min(b["low"] for b in window)


def round_tick(price: float) -> float:
    if price >= 1000:
        return round(price * 2) / 2.0
    if price >= 100:
        return round(price, 1)
    return round(price, 2)


def parse_db_collection(db: str, collection: str) -> tuple[str, str]:
    """Allow chartlink.morning-volume-breakout-buy style names."""
    if "." in collection and db == "Nsedata":
        # User may pass fully-qualified name in --collection
        parts = collection.split(".", 1)
        if parts[0] in ("Nsedata", "chartlink", "nsehistnew"):
            return parts[0], parts[1]
    if collection.startswith("chartlink."):
        return "chartlink", collection.split(".", 1)[1]
    return db, collection


def fetch_scan_docs(client: MongoClient, db_name: str, collection: str, limit: int) -> list[dict]:
    coll = client[db_name][collection]
    # Prefer newest date/eventtime when present
    sort_keys = []
    sample = coll.find_one()
    if sample:
        if "date" in sample:
            sort_keys.append(("date", -1))
        if "eventtime" in sample:
            sort_keys.append(("eventtime", -1))
        if "systemtime" in sample:
            sort_keys.append(("systemtime", -1))
    cursor = coll.find({}).sort(sort_keys).limit(limit) if sort_keys else coll.find({}).limit(limit)
    return list(cursor)


def enrich_symbol(client: MongoClient, scrip: str) -> dict:
    ns = client["Nsedata"]
    history = ns["history"].find_one({"dataset_code": scrip})
    history15 = ns["history15m"].find_one({"dataset_code": scrip})
    technical = ns["technical"].find_one({"dataset_code": scrip})
    fundamental = ns["fundamental"].find_one({"scrip": scrip})
    daily = unpack_ohlcv(history, limit=260)
    bars_15m = unpack_ohlcv(history15, limit=200)
    return {
        "daily": daily,
        "bars_15m": bars_15m,
        "technical": technical or {},
        "fundamental": fundamental or {},
    }


def score_intraday(scan: dict, daily: list[dict], bars_15m: list[dict]) -> dict | None:
    session = session_bars(bars_15m)
    if len(session) < 3:
        # Fall back to scan snapshot only
        close = _safe_float(scan.get("close"))
        if close <= 0:
            return None
        pct = _safe_float(scan.get("PCT_day_change"))
        score = 0
        if pct > 0.5:
            score += 2
        elif pct > 0:
            score += 1
        elif pct < -1:
            score -= 2
        tags = f"{scan.get('intradaytech') or ''} {scan.get('ml') or ''} {scan.get('mlData') or ''}"
        if any(t in tags for t in ("BreakHigh", "MLBuy", "TOP5B", "buyUp", "AnchisBuyUp")):
            score += 2
        if "ReversalLow" in tags or "ReversalLow" in str(scan.get("filter3") or ""):
            score += 1
        atr_est = close * 0.01
        stop = round_tick(close - atr_est)
        t1 = round_tick(close + atr_est)
        t2 = round_tick(close + 1.5 * atr_est)
        return {
            "bias": "bullish" if score >= 2 else ("bearish" if score <= -2 else "neutral"),
            "score": score,
            "close": close,
            "vwap": None,
            "day_high": _safe_float(scan.get("high"), close),
            "day_low": _safe_float(scan.get("low"), close),
            "entry": close,
            "t1": t1,
            "t2": t2,
            "stop": stop,
            "rr": round((t1 - close) / max(close - stop, 1e-9), 2),
            "notes": f"scan-only; PCT_day={pct}; tags={tags.strip()[:80]}",
        }

    close = session[-1]["close"]
    day_high = max(b["high"] for b in session)
    day_low = min(b["low"] for b in session)
    day_open = session[0]["open"]
    vw = vwap(session)
    atr_v = atr(session, min(14, max(2, len(session) - 1))) or (close * 0.008)
    pct = _safe_float(scan.get("PCT_day_change"))
    tags = f"{scan.get('intradaytech') or ''} {scan.get('ml') or ''} {scan.get('mlData') or ''}"

    score = 0
    if vw and close > vw:
        score += 2
    elif vw and close < vw:
        score -= 1
    if close > day_open:
        score += 1
    if pct > 0.5:
        score += 1
    if any(t in tags for t in ("BreakHigh", "MLBuy", "TOP5B", "buyUp", "AnchisBuyUp")):
        score += 2
    if "ReversalLow" in tags or "ReversalLow" in str(scan.get("filter3") or ""):
        score += 1

    # Opening range = first 2 bars (~30m of 15m)
    orb = session[:2]
    orb_high = max(b["high"] for b in orb)
    orb_low = min(b["low"] for b in orb)

    t1 = round_tick(min(day_high, close + atr_v) if close < day_high else close + atr_v)
    t2 = round_tick(close + 1.5 * atr_v)
    stop = round_tick(min(orb_low, close - atr_v))
    if stop >= close:
        stop = round_tick(close - atr_v)

    return {
        "bias": "bullish" if score >= 2 else ("bearish" if score <= -2 else "neutral"),
        "score": score,
        "close": close,
        "vwap": round_tick(vw) if vw else None,
        "day_high": day_high,
        "day_low": day_low,
        "entry": close,
        "t1": t1,
        "t2": t2,
        "stop": stop,
        "rr": round((t1 - close) / max(close - stop, 1e-9), 2),
        "notes": f"VWAP={'above' if vw and close > vw else 'below'}; ORB {orb_low}-{orb_high}; {tags.strip()[:60]}",
    }


def score_swing_3_5(scan: dict, daily: list[dict]) -> dict | None:
    if len(daily) < 5:
        close = _safe_float(scan.get("close"))
        if close <= 0:
            return None
        daily_closes = [close]
    else:
        daily_closes = [b["close"] for b in daily]
        close = daily_closes[-1]

    f3 = _safe_float(scan.get("forecast_day_PCT3_change"))
    f5 = _safe_float(scan.get("forecast_day_PCT5_change"))
    week_high_chg = _safe_float(scan.get("weekHighChange"))
    week_low_chg = _safe_float(scan.get("weekLowChange"))
    atr_v = atr(daily[-20:], 14) if len(daily) >= 15 else close * 0.02
    atr_v = atr_v or close * 0.02

    score = 0
    if f3 > 0:
        score += 1
    if f5 > 1:
        score += 2
    elif f5 > 0:
        score += 1
    elif f5 < -2:
        score -= 2

    filters = " ".join(
        str(scan.get(k) or "")
        for k in ("filter", "filter3", "filter5", "intradaytech", "ml", "mlData")
    )
    if "ReversalLow" in filters:
        score += 2
    if "BreakHigh" in filters:
        score += 2
    if week_low_chg > 2:
        score += 1
    if week_high_chg > -1 and week_high_chg < 2:
        score += 1  # near week high without large extension

    # Recent 3-day momentum
    if len(daily_closes) >= 4:
        mom = (daily_closes[-1] / daily_closes[-4] - 1) * 100
        if mom > 1:
            score += 1
        elif mom < -3:
            score -= 1

    t1 = round_tick(close + atr_v)
    t2 = round_tick(close + 1.5 * atr_v)
    stop = round_tick(close - atr_v)
    return {
        "bias": "bullish" if score >= 2 else ("bearish" if score <= -2 else "neutral"),
        "score": score,
        "close": close,
        "entry": close,
        "t1": t1,
        "t2": t2,
        "stop": stop,
        "rr": round((t1 - close) / max(close - stop, 1e-9), 2),
        "forecast_pct3": f3,
        "forecast_pct5": f5,
        "notes": f"f3={f3}, f5={f5}, weekH={week_high_chg}, weekL={week_low_chg}",
    }


def score_short_term(scan: dict, daily: list[dict], technical: dict) -> dict | None:
    if len(daily) < 20:
        return None
    closes = [b["close"] for b in daily]
    close = closes[-1]
    sma20 = sma(closes, 20)
    sma50 = sma(closes, 50) if len(closes) >= 50 else None
    rsi_v = rsi(closes, 14)
    atr_v = atr(daily, 14) or close * 0.02
    swing_h, swing_l = swing_high_low(daily, 20)

    score = 0
    if sma20 and close > sma20:
        score += 2
    if sma50 and sma20 and sma20 > sma50:
        score += 1
    if rsi_v is not None:
        if 40 <= rsi_v <= 65:
            score += 1
        elif rsi_v > 75:
            score -= 2
        elif rsi_v < 30:
            score -= 1

    st = str(technical.get("short_term") or "")
    # Convention in data: digits like '11' / '01' — treat non-empty bullish-leaning tags lightly
    if st and st not in ("NA", "00", "0"):
        score += 1

    change_sma25 = _safe_float(technical.get("changeSMA25"), _safe_float(scan.get("SMA25")))
    if change_sma25 > 0:
        score += 1
    elif change_sma25 < -2:
        score -= 1

    t1 = round_tick(min(swing_h, close + atr_v) if swing_h else close + atr_v)
    t2 = round_tick(close + 2 * atr_v)
    t3 = round_tick(close + 3 * atr_v)
    stop = round_tick(max(swing_l, close - 1.5 * atr_v) if swing_l else close - 1.5 * atr_v)
    if stop >= close:
        stop = round_tick(close - 1.5 * atr_v)

    return {
        "bias": "bullish" if score >= 2 else ("bearish" if score <= -2 else "neutral"),
        "score": score,
        "close": close,
        "sma20": round_tick(sma20) if sma20 else None,
        "sma50": round_tick(sma50) if sma50 else None,
        "rsi14": round(rsi_v, 1) if rsi_v is not None else None,
        "entry": close,
        "t1": t1,
        "t2": t2,
        "t3": t3,
        "stop": stop,
        "rr": round((t1 - close) / max(close - stop, 1e-9), 2),
        "notes": f"short_term={st}; SMA25chg={change_sma25}",
    }


def score_long_term(scan: dict, daily: list[dict], technical: dict, fundamental: dict) -> dict | None:
    if len(daily) < 60:
        return None
    closes = [b["close"] for b in daily]
    close = closes[-1]
    lookback = daily[-252:] if len(daily) >= 252 else daily
    high52 = max(b["high"] for b in lookback)
    low52 = min(b["low"] for b in lookback)
    sma200 = sma(closes, 200) if len(closes) >= 200 else sma(closes, min(100, len(closes)))
    pos = ((close - low52) / (high52 - low52) * 100) if high52 > low52 else 50.0

    year_high_chg = _safe_float(scan.get("yearHighChange"), _safe_float(technical.get("yearHighChange")))
    year_low_chg = _safe_float(scan.get("yearLowChange"), _safe_float(technical.get("yearLowChange")))
    pe = _safe_float(fundamental.get("peratio"), _safe_float(scan.get("peratio")))

    score = 0
    if sma200 and close > sma200:
        score += 2
    if 20 <= pos <= 80:
        score += 1
    if pos < 20 and year_low_chg > 5:
        score += 1  # recovering from lows
    if year_high_chg > -5 and year_high_chg < 5:
        score += 1  # near highs — breakout potential
    if year_high_chg < -25:
        score -= 1

    lt = str(technical.get("long_term") or "")
    if lt and lt not in ("NA", "00", "0"):
        score += 1
    if 0 < pe < 25:
        score += 1
    elif pe > 50:
        score -= 1

    rng = high52 - low52
    t1 = round_tick(high52 if close < high52 else close + 0.272 * rng)
    t2 = round_tick(close + 0.618 * rng) if rng > 0 else round_tick(close * 1.15)
    invalidation = round_tick(sma200) if sma200 else round_tick(low52)
    stop = invalidation
    if stop >= close:
        stop = round_tick(close * 0.92)
    rr = round((t1 - close) / max(close - stop, 1e-9), 2)

    return {
        "bias": "bullish" if score >= 2 else ("bearish" if score <= -2 else "neutral"),
        "score": score,
        "close": close,
        "high52": high52,
        "low52": low52,
        "range_position_pct": round(pos, 1),
        "sma200": round_tick(sma200) if sma200 else None,
        "pe": pe if pe else None,
        "entry": close,
        "t1": t1,
        "t2": t2,
        "stop": stop,
        "rr": rr,
        "invalidation": invalidation,
        "notes": f"long_term={lt}; yearH={year_high_chg}; yearL={year_low_chg}; PE={pe or 'n/a'}",
    }


# Signal-like keys often present on Nsedata / chartlink scan rows
_SIGNAL_KEYS = (
    "filter",
    "filter1",
    "filter2",
    "filter3",
    "filter4",
    "filter5",
    "filter6",
    "filterbuy",
    "filtersell",
    "intradaytech",
    "shorttermtech",
    "ml",
    "mlData",
    "keyIndicator",
    "processor",
    "tobuy",
    "tosell",
    "resultDeclared",
)


def scan_column_names(docs: list[dict]) -> list[str]:
    """Union of all keys across scan docs (excluding _id)."""
    keys: set[str] = set()
    for doc in docs:
        keys.update(k for k in doc.keys() if k != "_id")
    return sorted(keys)


def extract_scan_signals(scan: dict) -> dict[str, Any]:
    """Pull every useful column from the scan row for Why / Priority scoring."""
    signals: dict[str, Any] = {}
    tag_parts: list[str] = []

    for key in _SIGNAL_KEYS:
        val = scan.get(key)
        if val is None or val == "":
            continue
        text = str(val).strip()
        if not text or text in ("$", "|", "$ | $"):
            continue
        signals[key] = text[:200]
        # Keep distinctive tokens for why_hint
        for token in (
            "BreakHighYe",
            "BreakHighMe",
            "BreakHighY",
            "BreakHighM",
            "NearHighYe",
            "NearHighY",
            "NearLowMo",
            "ReversalLow",
            "AnchisBuyUp",
            "MLBuy",
            "buyUp",
            "TOP5B",
            "TOP10B",
            "TOP15B",
            "TOP25B",
        ):
            if token in text and token not in tag_parts:
                tag_parts.append(token)

    # Numeric / tape fields — keep whatever exists
    for key in (
        "PCT_change",
        "PCT_day_change",
        "Ldchange",
        "ldchange",
        "volume",
        "close",
        "high",
        "low",
        "open",
        "forecast_day_PCT_change",
        "forecast_day_PCT3_change",
        "forecast_day_PCT5_change",
        "weekHighChange",
        "weekLowChange",
        "monthHighChange",
        "monthLowChange",
        "yearHighChange",
        "yearLowChange",
    ):
        if key in scan and scan[key] is not None and scan[key] != "":
            signals[key] = scan[key]

    # Any other stringy tag-like fields not in the fixed list
    for key, val in scan.items():
        if key in signals or key in ("_id", "scrip", "dataset_code", "date", "eventtime", "systemtime", "epochtime", "industry", "index", "name"):
            continue
        if isinstance(val, str) and len(val) > 2 and any(
            t in val for t in ("Break", "Reversal", "Buy", "Sell", "TOP", "Near", "ML", "Consol")
        ):
            signals[key] = val[:200]
            for token in ("BreakHighMe", "BreakHighYe", "ReversalLow", "AnchisBuyUp", "MLBuy", "NearHighYe"):
                if token in val and token not in tag_parts:
                    tag_parts.append(token)

    pct_day = _safe_float(scan.get("PCT_day_change"))
    pct = _safe_float(scan.get("PCT_change"))
    ld = scan.get("Ldchange", scan.get("ldchange"))
    tape_bits: list[str] = []
    if pct_day:
        tape_bits.append(f"day {pct_day:+.2f}%")
    if pct and abs(pct - pct_day) > 0.05:
        tape_bits.append(f"chg {pct:+.2f}%")
    if ld is not None and ld != "":
        try:
            tape_bits.append(f"Ld {float(ld):+.2f}")
        except (TypeError, ValueError):
            pass

    why_hint = " + ".join(tag_parts[:4]) if tag_parts else "scan signals thin"
    if tape_bits:
        why_hint = f"{why_hint}; {', '.join(tape_bits)}"
    industry = scan.get("industry")
    if industry:
        why_hint = f"{why_hint} [{industry}]"

    return {
        "tags": tag_parts,
        "fields": signals,
        "why_hint": why_hint[:180],
    }


def analyze_candidate(
    client: MongoClient,
    scan: dict,
    horizons: set[str],
) -> dict | None:
    scrip = scan.get("scrip") or scan.get("dataset_code")
    if not scrip:
        return None
    enrich = enrich_symbol(client, scrip)
    scan_signals = extract_scan_signals(scan)
    # Keep full scan row (minus huge/_id) for agent column awareness
    scan_full = {k: v for k, v in scan.items() if k != "_id"}
    result: dict[str, Any] = {
        "scrip": scrip,
        "industry": scan.get("industry"),
        "date": scan.get("date") or scan.get("eventtime"),
        "scan_pct_change": _safe_float(scan.get("PCT_change")),
        "scan_pct_day_change": _safe_float(scan.get("PCT_day_change")),
        "scan_signals": scan_signals,
        "why_hint": scan_signals["why_hint"],
        "scan_row": scan_full,
    }
    if "intraday" in horizons:
        result["intraday"] = score_intraday(scan, enrich["daily"], enrich["bars_15m"])
    if "swing3_5" in horizons:
        result["swing3_5"] = score_swing_3_5(scan, enrich["daily"])
    if "short_term" in horizons:
        result["short_term"] = score_short_term(scan, enrich["daily"], enrich["technical"])
    if "long_term" in horizons:
        result["long_term"] = score_long_term(
            scan, enrich["daily"], enrich["technical"], enrich["fundamental"]
        )
    return result


def derive_conviction_sentiment(block: dict, scan_signals: dict | None = None) -> dict:
    """Attach conviction, sentiment, and probability_score (0–100) to a horizon block."""
    score = _safe_float(block.get("score"))
    rr_raw = block.get("rr")
    rr = _safe_float(rr_raw) if rr_raw is not None else 0.0
    # If R:R missing but targets/stop exist, estimate for conviction banding
    if rr <= 0 and block.get("t1") is not None and block.get("stop") is not None:
        entry = _safe_float(block.get("entry") or block.get("close"))
        t1 = _safe_float(block.get("t1"))
        stop = _safe_float(block.get("stop"))
        if entry > stop:
            rr = (t1 - entry) / max(entry - stop, 1e-9)
    bias = (block.get("bias") or "neutral").lower()
    tags = (scan_signals or {}).get("tags") or []
    tag_n = len(tags) if isinstance(tags, list) else 0

    sentiment_map = {
        "bullish": "Bullish",
        "bearish": "Bearish",
        "neutral": "Neutral",
    }
    sentiment = sentiment_map.get(bias, "Neutral")

    # Probability: center at 50, scale by score/R:R/tags (clamped 10–95)
    probability = 50.0 + (score * 5.0)
    if rr >= 2.0:
        probability += 8.0
    elif rr >= 1.5:
        probability += 4.0
    elif rr >= 1.0:
        probability += 2.0
    elif rr > 0 and rr < 1.0:
        probability -= 6.0
    if tag_n >= 3:
        probability += 4.0
    elif tag_n >= 1:
        probability += 2.0
    # Directional: bearish setups still get a probability of the *bearish* thesis
    if bias == "neutral":
        probability = min(probability, 58.0)
    probability_score = int(max(10, min(95, round(probability))))

    abs_score = abs(score)
    # High: strong score with workable R:R, or elite score even at ~1.0 R:R
    if abs_score >= 5 and rr >= 1.0:
        conviction = "High"
    elif abs_score >= 4 and rr >= 1.2:
        conviction = "High"
    elif abs_score >= 4 and tag_n >= 2 and rr >= 0.9:
        conviction = "High"
    elif abs_score >= 5 and rr >= 0.8:
        conviction = "High"
    elif abs_score >= 2:
        conviction = "Med"
    else:
        conviction = "Low"

    return {
        "sentiment": sentiment,
        "conviction": conviction,
        "probability_score": probability_score,
    }


def rank_horizon(results: list[dict], key: str, top_n: int = 5) -> list[dict]:
    scored = []
    seen: set[str] = set()
    for r in results:
        block = r.get(key)
        if not block:
            continue
        scrip = r["scrip"]
        meta_fields = derive_conviction_sentiment(block, r.get("scan_signals"))
        # Dedupe repeated scan processor rows; keep first (highest score after sort)
        row = {
            "scrip": scrip,
            "industry": r.get("industry"),
            "date": r.get("date"),
            **block,
            **meta_fields,
            "why_hint": r.get("why_hint"),
            "scan_signals": r.get("scan_signals"),
            # Agent fills via web search / india-news-tracker
            "news_catalyst": None,
            "may_extend": None,
            "why": None,  # Agent builds Priority|Symbol|Why from why_hint + news
        }
        scored.append(row)
    scored.sort(
        key=lambda x: (
            x.get("probability_score", 0),
            x.get("score", 0),
            x.get("rr", 0),
        ),
        reverse=True,
    )
    deduped: list[dict] = []
    for row in scored:
        if row["scrip"] in seen:
            continue
        seen.add(row["scrip"])
        deduped.append(row)
        if len(deduped) >= top_n:
            break
    return deduped


def build_priority_table(results: list[dict], horizons: set[str], top_n: int = 5) -> list[dict]:
    """Draft Priority|Symbol|Why rows (why still needs news polish by agent)."""
    # Prefer intraday ranking if present, else first available horizon
    order = ["intraday", "swing3_5", "short_term", "long_term"]
    primary = next((h for h in order if h in horizons), "intraday")
    ranked = rank_horizon(results, primary, top_n=top_n)
    table = []
    for i, row in enumerate(ranked, start=1):
        table.append(
            {
                "priority": i,
                "symbol": row["scrip"],
                "why": row.get("why_hint") or row.get("notes") or "",
                "score": row.get("score"),
                "rr": row.get("rr"),
                "sentiment": row.get("sentiment"),
                "conviction": row.get("conviction"),
                "probability_score": row.get("probability_score"),
                "news_catalyst": None,
                "may_extend": None,
            }
        )
    return table


def build_report(results: list[dict], meta: dict, horizons: set[str], top_n: int) -> dict:
    scan_cols: list[str] = []
    for r in results:
        row = r.get("scan_row") or {}
        scan_cols.extend(row.keys())
    report = {
        "meta": meta,
        "scan_columns": sorted(set(scan_cols)),
        "priority_table": build_priority_table(results, horizons, top_n=top_n),
        "rankings": {},
        "candidates": results,
        "output_columns": {
            "required": [
                "priority_table",
                "news_catalyst",
                "may_extend",
                "why",
                "sentiment",
                "conviction",
                "probability_score",
            ],
            "priority_shape": [
                "Priority",
                "Symbol",
                "Sentiment",
                "Conviction",
                "Prob%",
                "Why",
            ],
            "priority_shape_multi_table": [
                "Priority",
                "Table",
                "Symbol",
                "Sentiment",
                "Conviction",
                "Prob%",
                "Why",
            ],
            "sentiment_values": ["Bullish", "Bearish", "Neutral", "Mixed"],
            "conviction_values": ["High", "Med", "Low"],
            "probability_score": "integer 0–100 (helper emits 10–95)",
            "may_extend_values": ["Yes", "Possible", "Only if X", "Weak", "No"],
            "note": (
                "Lead the user report with priority_table including Sentiment, "
                "Conviction, and Prob% (probability_score). Use ALL scan_columns. "
                "Polish why with news; fill news_catalyst and may_extend. "
                "When multiple tables, add Table column."
            ),
        },
    }
    mapping = {
        "intraday": "intraday",
        "swing3_5": "swing3_5",
        "short_term": "short_term",
        "long_term": "long_term",
    }
    for h in horizons:
        report["rankings"][h] = rank_horizon(results, mapping[h], top_n=top_n)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Nsedata multi-horizon trade suggestions")
    parser.add_argument("--uri", default=DEFAULT_URI, help="MongoDB connection URI")
    parser.add_argument("--db", default="Nsedata", help="Database name (default Nsedata)")
    parser.add_argument(
        "--collection",
        required=True,
        help="Scan collection (e.g. highBuy or chartlink.morning-volume-breakout-buy)",
    )
    parser.add_argument("--limit", type=int, default=20, help="Max scan docs to analyze")
    parser.add_argument(
        "--horizons",
        default="all",
        help="Comma list: intraday,swing3_5,short_term,long_term or 'all'",
    )
    parser.add_argument("--top", type=int, default=5, help="Top N per horizon")
    parser.add_argument("--output", help="Write JSON to file instead of stdout")
    args = parser.parse_args()

    if args.horizons.strip().lower() == "all":
        horizons = set(HORIZONS)
    else:
        horizons = {h.strip() for h in args.horizons.split(",") if h.strip()}
        unknown = horizons - set(HORIZONS)
        if unknown:
            print(f"Unknown horizons: {unknown}. Valid: {HORIZONS}", file=sys.stderr)
            return 2

    db_name, collection = parse_db_collection(args.db, args.collection)

    client = MongoClient(args.uri, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
    except Exception as exc:  # noqa: BLE001
        print(f"Cannot connect to MongoDB at {args.uri}: {exc}", file=sys.stderr)
        return 1

    if collection not in client[db_name].list_collection_names():
        print(f"Collection {db_name}.{collection} not found", file=sys.stderr)
        print(f"Available: {client[db_name].list_collection_names()}", file=sys.stderr)
        return 1

    scans = fetch_scan_docs(client, db_name, collection, args.limit)
    results = []
    for scan in scans:
        analyzed = analyze_candidate(client, scan, horizons)
        if analyzed:
            results.append(analyzed)

    meta = {
        "database": db_name,
        "collection": collection,
        "uri": args.uri,
        "scanned": len(scans),
        "analyzed": len(results),
        "horizons": sorted(horizons),
        "scan_columns": scan_column_names(scans),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "disclaimer": "Educational analysis only — not SEBI-registered advice.",
        "report_lead": (
            "Priority | Symbol | Sentiment | Conviction | Prob% | Why "
            "(add Table when multiple collections)"
        ),
    }
    report = build_report(results, meta, horizons, args.top)
    text = json.dumps(report, indent=2, default=str)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"Wrote {args.output}", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
