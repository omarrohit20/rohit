#!/usr/bin/env python3
"""Build High- and Med-conviction Bullish investment ideas into three Nsedata collections.

Examples:
  python skills/investment-ideas/scripts/run_investment_ideas.py
  python skills/investment-ideas/scripts/run_investment_ideas.py --only breakout
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import math
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

try:
    from pymongo import MongoClient
except ImportError:
    print("pymongo is required: pip install pymongo", file=sys.stderr)
    sys.exit(1)

try:
    import requests
except ImportError:
    requests = None  # type: ignore

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ADVISOR_DIR = SKILL_DIR.parent / "nsedata-trade-advisor" / "scripts"
sys.path.insert(0, str(ADVISOR_DIR))

import query_suggestions as qs  # noqa: E402

DEFAULT_URI = "mongodb://localhost:27017"
DB_NAME = "Nsedata"
COLL_LONG = "investment-long-term"
COLL_MEDIUM = "investment-medium-term"
COLL_SHORT = "investment-short-term"
COLLECTIONS = (COLL_LONG, COLL_MEDIUM, COLL_SHORT)
# Rows older than this many days (by insertion_date) are deleted each run.
# The same window caps the target estimate so a target never outlives its row.
PURGE_DAYS = {
    COLL_LONG: 90,
    COLL_MEDIUM: 30,
    COLL_SHORT: 10,
}
# Minimum upside from buy_price to target_price, in percent. Rows at or below it
# are not saved, and existing ones are deleted on each run. --long-min-return,
# --medium-min-return and --short-min-return override.
MIN_RETURN_PCT = {
    COLL_LONG: 50.0,
    COLL_MEDIUM: 30.0,
    COLL_SHORT: 20.0,
}
# A symbol already in a longer horizon is not kept in a shorter one.
COVERED_BY = {
    COLL_MEDIUM: (COLL_LONG,),
    COLL_SHORT: (COLL_LONG, COLL_MEDIUM),
}
HORIZON_LABEL = {
    COLL_LONG: "long-term (up to 3 months)",
    COLL_MEDIUM: "medium-term (up to 1 month)",
    COLL_SHORT: "short-term (up to 10 days)",
}

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)
NSE_PAGE = "https://www.nseindia.com/companies-listing/corporate-filings-shareholding-pattern"
NSE_ORIGIN = "https://www.nseindia.com"
NSE_CACHE_COLL = "nse_shareholding_cache"
SCREENER_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}

INDUSTRY_KEYS = (
    "engineering",
    "capital goods",
    "defence",
    "defense",
    "railway",
    "power equipment",
    "infrastructure",
)

BREAKOUTS = (
    {
        "table": "breakoutYH",
        "fallback": None,
        "collection": COLL_LONG,
        "scorer": "long",
        "lookback": True,
        "window": "6 months",
    },
    {
        "table": "breakoutY2H",
        "fallback": None,
        "collection": COLL_LONG,
        "scorer": "long",
        "lookback": True,
        "window": "6 months",
    },
    {
        "table": "breakoutMH",
        "fallback": None,
        "collection": COLL_LONG,
        "scorer": "long",
        "lookback": False,
        "window": "the live scan window",
    },
    {
        "table": "nearY5H",
        "fallback": None,
        "collection": COLL_LONG,
        "scorer": "long",
        "lookback": True,
        "window": "6 months",
    },
    {
        "table": "breakoutM2H",
        "fallback": None,
        "collection": COLL_MEDIUM,
        "scorer": "swing",
        "lookback": False,
        "window": "the live scan window",
    },
    {
        "table": "movingavg_crossed_up",
        "fallback": None,
        "collection": COLL_MEDIUM,
        "scorer": "swing",
        "lookback": False,
        "window": "the live scan window",
    },
    {
        "table": "breakoutW2H",
        "fallback": "breakoutW2HR",
        "collection": COLL_SHORT,
        "scorer": "short",
        "lookback": False,
        "window": "the live scan window",
    },
)

GENERIC_HOLDERS = {
    "promoter & promoter group",
    "promoter and promoter group",
    "public",
    "institutions",
    "institutions (domestic)",
    "institutions (foreign)",
    "mutual funds",
    "non institution",
    "non-institution",
    "central government",
    "state government",
    "indian",
    "foreign",
    "any other",
}
# Blank-category rows in NSE's public table that are buckets, not holders.
PUBLIC_BUCKETS = {
    "other",
    "others",
    "clearing members",
    "esop or esos or esps",
    "huf",
    "trusts",
}


def months_ago(months: int, today: date | None = None) -> date:
    today = today or date.today()
    year = today.year
    month = today.month - months
    while month <= 0:
        month += 12
        year -= 1
    return date(year, month, min(today.day, 28))


def parse_date(value: Any) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()[:11]
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d-%b-%Y", "%d-%B-%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def parse_number(value: Any) -> float | None:
    if value is None:
        return None
    text = html_lib.unescape(str(value)).strip()
    text = text.replace(",", "").replace("%", "")
    if text in {"", "-", "—", "NA", "N/A"}:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    if number != number:  # NaN
        return None
    return number


def to_crores(value: Any) -> float | None:
    number = parse_number(value)
    if number is None or number <= 0:
        return None
    # Nsedata stores crores. Only rupee-scale figures need scaling.
    if number >= 1e8:
        number = number / 1e7
    return number


def marketcap_bucket(crores: float) -> str | None:
    if crores < 5000:
        return "smallcap"
    if crores <= 20000:
        return "midcap"
    return None


def is_capital_goods(industry: str | None) -> bool:
    text = (industry or "").lower()
    if "construction" in text and "material" not in text:
        return True
    return any(key in text for key in INDUSTRY_KEYS)


def strip_tags(fragment: str) -> str:
    text = re.sub(r"<[^>]+>", " ", fragment)
    text = html_lib.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def html_rows(page: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for tr in re.findall(r"<tr\b[^>]*>(.*?)</tr>", page, flags=re.I | re.S):
        cells = re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", tr, flags=re.I | re.S)
        rows.append([strip_tags(cell) for cell in cells])
    return rows


def _section(page: str, section_id: str) -> str:
    match = re.search(rf'id="{re.escape(section_id)}"', page)
    if not match:
        return ""
    rest = page[match.start() :]
    nxt = re.search(r"<section\b", rest[20:])
    return rest[: nxt.start() + 20] if nxt else rest[:250000]


def parse_market_cap(page: str) -> float | None:
    match = re.search(
        r"Market Cap\s*</span>\s*<span class=\"nowrap value\">\s*(?:₹|Rs\.?)?\s*"
        r"<span class=\"number\">([\d,]+(?:\.\d+)?)</span>",
        page,
        flags=re.I,
    )
    if not match:
        return None
    return parse_number(match.group(1))


def parse_annual_sales(page: str) -> float | None:
    section = _section(page, "profit-loss") or page
    rows = html_rows(section)
    header_index = None
    headers: list[str] = []
    for index, row in enumerate(rows):
        if any(re.search(r"Mar\s+20\d\d", cell) for cell in row):
            header_index = index
            headers = row[1:]
            break
    if header_index is None:
        return None
    for row in rows[header_index + 1 :]:
        if not row:
            continue
        label = re.sub(r"\s+", " ", row[0].lower().replace("+", " ")).strip()
        if label not in {"sales", "revenue"}:
            continue
        annual: list[float] = []
        for index, raw in enumerate(row[1:]):
            header = headers[index].lower() if index < len(headers) else ""
            if "ttm" in header:
                continue
            number = parse_number(raw)
            if number is not None:
                annual.append(number)
        if annual:
            return annual[-1]
    return None


def _order_book_unit_to_crore(number: float, unit: str | None) -> float | None:
    unit = (unit or "").lower().rstrip(".")
    if unit in {"", "crore", "cr"}:
        return number if unit else None
    if unit in {"lakh", "lac", "lakhs"}:
        return number / 100.0
    if unit in {"million", "mn"}:
        return number / 10.0
    if unit in {"bn", "billion"}:
        return number * 100.0
    return None


def parse_order_book(page: str) -> float | None:
    for row in html_rows(page):
        if not row:
            continue
        label = row[0].lower()
        if "order book" not in label and "order backlog" not in label:
            continue
        if "export" in label or "usd" in label:
            continue
        numbers = [parse_number(cell) for cell in row[1:]]
        numbers = [n for n in numbers if n is not None and n > 0]
        if not numbers:
            continue
        if "crore" in label or "inr" in label or "rs" in label:
            return numbers[-1]
    plain = strip_tags(page)
    patterns = (
        re.compile(
            r"(?:order\s*book(?:\s+position)?|order\s+backlog)"
            r"(?:\s*(?:of|at|stands at|stood at|is|was|worth|size))?"
            r"\s*(?:of\s+)?(?:about\s+|around\s+|nearly\s+)?"
            r"(?:rs\.?|inr|₹)?\s*([\d,]+(?:\.\d+)?)\s*(crore|cr\.?|lakh|lac|million|bn|billion)?",
            re.I,
        ),
        re.compile(
            r"(?:rs\.?|inr|₹)\s*([\d,]+(?:\.\d+)?)\s*(crore|cr\.?|lakh|lac|million|bn|billion)"
            r"\s+(?:of\s+)?(?:order\s*book|order\s+backlog)",
            re.I,
        ),
    )
    for pattern in patterns:
        for match in pattern.finditer(plain):
            start = max(0, match.start() - 40)
            prefix = plain[start:match.start()].lower()
            if "export" in prefix or "usd" in prefix:
                continue
            number = parse_number(match.group(1))
            if number is None or number <= 0:
                continue
            unit = match.group(2)
            crores = _order_book_unit_to_crore(number, unit)
            if crores is None and unit is None and "crore" in plain[match.end(): match.end() + 24].lower():
                crores = number
            if crores is not None and crores > 0:
                return crores
    return None


def parse_pros_cons(page: str) -> tuple[list[str], list[str]]:
    """Screener's auto-generated Pros and Cons bullets."""
    out: list[list[str]] = []
    for cls in ("pros", "cons"):
        match = re.search(rf'<div class="{cls}"[^>]*>(.*?)</div>', page, flags=re.S)
        items = re.findall(r"<li[^>]*>(.*?)</li>", match.group(1), flags=re.S) if match else []
        out.append([strip_tags(item).rstrip(".") for item in items if strip_tags(item)])
    return out[0], out[1]


def parse_screener(page: str) -> dict[str, Any]:
    pros, cons = parse_pros_cons(page)
    return {
        "marketcap_cr": parse_market_cap(page),
        "sales_cr": parse_annual_sales(page),
        "order_book_cr": parse_order_book(page),
        "pros": pros,
        "cons": cons,
    }


NEWS_DAYS = 30
NEWS_SKIP_WORDS = {"the", "india", "indian", "limited", "ltd", "industries", "company"}
# Quote and estimate listing pages that Google News returns as articles.
NEWS_LISTING = re.compile(
    r"(?:nse|bse):[A-Z0-9&_-]+\s*$|analyst insights, price targets|\([A-Z0-9&-]+\.(?:NS|BO)\)"
    r"|share price(?: live)?(?: today)?\b|stock price live|stock price & chart|stock forecast"
    r"|stock analysis\s*$|circuit today|price, data and peers"
    # Round-ups that list many companies.
    r"|among \d+\+? (?:companies|stocks)|picks \d+ stocks|top stock picks|stocks to (?:buy|watch)"
    r"|stocks in news|top gainers|trade spotlight|buy, sell or hold",
    re.I,
)


def load_news(db) -> dict[str, dict]:
    fields = {"_id": 0, "scrip": 1, "news": 1, "analyst_calls": 1, "overall_sentiment": 1, "conviction": 1}
    return {str(doc["scrip"]): doc for doc in db["scrip_news"].find({}, fields) if doc.get("scrip")}


NEWS_MARKET_WORDS = re.compile(r"\b(?:shares?|stocks?|ltd|limited|nse|bse|q[1-4]|results?|ipo)\b", re.I)


def _news_mentions(title: str, symbol: str, company: str) -> bool:
    """Ticker as a whole word, or the company's first two significant words as words.

    Short tickers (LT, PNB) only match through the company name. A one-word name
    (Titan, Trent) also needs a market word, so namesakes in other news are skipped.
    """
    if len(symbol) >= 4 and re.search(rf"(?<![A-Za-z0-9]){re.escape(symbol)}(?![A-Za-z0-9])", title):
        return True
    words = list(
        dict.fromkeys(w for w in re.split(r"[^a-z0-9]+", company.lower()) if len(w) > 2 and w not in NEWS_SKIP_WORDS)
    )
    if not words:
        return False
    text = title.lower()
    if not all(re.search(rf"\b{re.escape(word)}\b", text) for word in words[:2]):
        return False
    return len(words) > 1 or bool(NEWS_MARKET_WORDS.search(title))


def news_impact(news: dict[str, dict], symbol: str, company: str) -> dict[str, Any]:
    """Strongest recent headline about this company from Nsedata.scrip_news.

    Returns the stored fields plus `text`, a clause for `why`. Articles must name the
    company (scrip_news sometimes holds another company's story) and be within NEWS_DAYS.
    """
    doc = news.get(symbol)
    if not doc:
        return {"text": "news: none on file"}
    cutoff = datetime.now() - timedelta(days=NEWS_DAYS)
    picked: list[tuple[int, datetime, dict]] = []
    for article in (doc.get("news") or []) + (doc.get("analyst_calls") or []):
        title = str(article.get("title") or "").strip()
        for _ in range(2):  # Google News appends " - Source", sometimes twice
            head, sep, source = title.rpartition(" - ")
            if not (sep and head and len(source.split()) <= 4):
                break
            title = head.strip()
        if not title or NEWS_LISTING.search(title) or not _news_mentions(title, symbol, company):
            continue
        try:
            published = parsedate_to_datetime(str(article.get("published"))).replace(tzinfo=None)
        except (TypeError, ValueError):
            continue
        if published < cutoff:
            continue
        picked.append((int(article.get("impact_score") or 0), published, {**article, "title": title}))
    sentiment = doc.get("overall_sentiment") or "Neutral"
    conviction = doc.get("conviction") or "Low"
    out: dict[str, Any] = {"news_sentiment": sentiment, "news_conviction": conviction}
    if not picked:
        out["text"] = f"news: {sentiment} ({conviction}), no company news in last {NEWS_DAYS} days"
        return out
    impact, published, top = max(picked, key=lambda item: (item[0], item[1]))
    out.update(
        {
            "news_headline": top["title"],
            "news_event": top.get("event_type") or "General",
            "news_impact_score": impact,
            "news_date": published.date().isoformat(),
            "news_link": top.get("link") or "",
        }
    )
    out["text"] = (
        f"news: {sentiment} ({conviction}) - {top['title']} "
        f"[{out['news_event']}, {top.get('sentiment') or 'Neutral'}, impact {impact}, {published:%d %b}]"
    )
    return out


def news_fields(impact: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in impact.items() if k != "text"}


def load_investors(path: Path) -> list[tuple[str, list[str]]]:
    investors: list[tuple[str, list[str]]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) < 2 or not re.search(r"[A-Za-z]", parts[0]):
            continue
        if parts[0].lower() == "investor":
            continue
        variants = [item.strip() for item in re.split(r"[;|]", parts[1]) if item.strip()]
        if parts[0] not in variants:
            variants.insert(0, parts[0])
        investors.append((parts[0], variants))
    return investors


def _norm_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def names_match(holder: str, variant: str) -> bool:
    holder_n = _norm_name(holder)
    variant_n = _norm_name(variant)
    if len(variant_n) < 6 or not holder_n:
        return False
    if variant_n in holder_n:
        return True
    words = variant_n.split()
    if len(words) < 2:
        return False
    pos = 0
    for word in words:
        found = holder_n.find(word, pos)
        if found < 0:
            return False
        pos = found + len(word)
    return True


def pct_text(value: float | None) -> str:
    if value is None:
        return ""
    if abs(value - round(value)) < 0.05:
        return f"{round(value):.0f}%"
    return f"{value:.1f}%"


def buy_price_from_daily(daily: list[dict]) -> float | None:
    if not daily:
        return None
    closes = [bar["close"] for bar in daily if bar.get("close")]
    if not closes or closes[-1] <= 0:
        return None
    close = closes[-1]
    average = qs.sma(closes, 20)
    if average and close > average * 1.08:
        return qs.round_tick(average)
    return qs.round_tick(close)


def daily_scan(symbol: str, daily: list[dict]) -> dict:
    """Scan-style fields from daily bars, for ideas that have no scan row.

    The scorers read 3/5-day change and distance from last week's high and low.
    Without them a bare {scrip, close} scan can never reach High or Med conviction.
    """
    closes = [bar["close"] for bar in daily if bar.get("close")]
    if not closes:
        return {"scrip": symbol, "close": None}
    close = closes[-1]

    def change(days: int) -> float:
        base = closes[-1 - days] if len(closes) > days else 0
        return round((close / base - 1) * 100, 2) if base else 0.0

    scan: dict[str, Any] = {
        "scrip": symbol,
        "close": close,
        "forecast_day_PCT3_change": change(3),
        "forecast_day_PCT5_change": change(5),
    }
    week = [bar for bar in daily[-6:-1] if bar.get("high") and bar.get("low")]
    if week:
        scan["weekHighChange"] = round((close / max(bar["high"] for bar in week) - 1) * 100, 2)
        scan["weekLowChange"] = round((close / min(bar["low"] for bar in week) - 1) * 100, 2)
    return scan


def local_gate(
    client, symbol: str, kind: str, collection: str, stats: RunStats
) -> tuple[dict, dict | None, dict | None]:
    """Score from local Mongo only, so HTTP is spent only on names that can be saved.

    Returns (enrich, block, meta). meta is None when the name is not High/Med Bullish
    or its target upside is at or below the collection minimum (upsert_idea would
    reject it anyway).
    """
    enrich = qs.enrich_symbol(client, symbol)
    scan = daily_scan(symbol, enrich["daily"])
    block = score_block(kind, scan, enrich)
    meta = passes_gate(block, scan)
    if not meta:
        stats.skip_low(collection)
        return enrich, block, None
    price = buy_price_from_daily(enrich["daily"])
    upside = target_plan(collection, kind, block, price, enrich["daily"]).get("target_pct") or 0
    minimum = MIN_RETURN_PCT[collection]
    if not upside > minimum:
        stats.extra[f"{collection}:return-at-or-below-{minimum:g}%"] += 1
        return enrich, block, None
    return enrich, block, meta


def score_block(kind: str, scan: dict, enrich: dict) -> dict | None:
    daily = enrich["daily"]
    if kind == "long":
        return qs.score_long_term(scan, daily, enrich["technical"], enrich["fundamental"])
    if kind == "short":
        return qs.score_short_term(scan, daily, enrich["technical"])
    return qs.score_swing_3_5(scan, daily)


def _block_atr(kind: str, block: dict, daily: list[dict]) -> float:
    close = float(block.get("close") or 0)
    bars = daily[-20:] if kind == "swing" else daily
    value = qs.atr(bars, 14) if len(bars) >= 15 else None
    return value or close * 0.02


def target_reason(kind: str, block: dict, daily: list[dict]) -> str:
    """Say how the scorer picked t1."""
    close = float(block.get("close") or 0)
    if kind == "long":
        high52 = block.get("high52")
        if high52 and close < float(high52):
            return f"52-week high {qs.round_tick(float(high52))}"
        return "new-high extension: 27.2% of the 52-week range above the close"
    atr_v = _block_atr(kind, block, daily)
    if kind == "short" and float(block["t1"]) < qs.round_tick(close + atr_v):
        return "20-day swing high"
    return f"1 ATR(14) above the close (ATR {qs.round_tick(atr_v)})"


def target_plan(collection: str, kind: str, block: dict, buy: float | None, daily: list[dict]) -> dict:
    """Target price, % upside from buy, reason, estimated days and date to reach it.

    Days use the random-walk rule of thumb (distance / ATR) squared trading days,
    converted to calendar days and capped at the collection's purge window.
    """
    target = qs.round_tick(float(block["t1"]))
    plan: dict[str, Any] = {"target_price": target, "target_reason": target_reason(kind, block, daily)}
    if not buy or buy <= 0:
        return plan
    plan["target_pct"] = round((target - buy) / buy * 100, 2)
    atr_v = _block_atr(kind, block, daily)
    trading = math.ceil(((target - buy) / atr_v) ** 2) if atr_v > 0 and target > buy else 1
    days = math.ceil(max(trading, 1) * 7 / 5)
    limit = PURGE_DAYS[collection]
    if days > limit:
        days = limit
        plan["target_reason"] += f"; estimate capped at the {limit}-day window"
    plan["target_days"] = days
    plan["target_date"] = (date.today() + timedelta(days=days)).isoformat()
    return plan


ACCEPTED_CONVICTION = {"High", "Med"}
# Idea types saved whatever their conviction, sentiment, or target upside.
UNGATED_IDEAS = {"celebrity"}


def passes_gate(block: dict | None, scan: dict) -> dict | None:
    if not block or block.get("t1") is None:
        return None
    meta = qs.derive_conviction_sentiment(block, qs.extract_scan_signals(scan))
    if meta.get("conviction") in ACCEPTED_CONVICTION and meta.get("sentiment") == "Bullish":
        return meta
    return None


def breakout_why(table: str, hit_count: int, window: str, scan: dict, daily: list[dict]) -> str:
    bits: list[str] = []
    if table in {"breakoutYH", "breakoutY2H"}:
        bits.append("near year high")
    elif table == "breakoutMH":
        bits.append("near month high")
    elif table in {"breakoutW2H", "breakoutW2HR"}:
        bits.append("near week high")
    elif table == "breakoutM2H":
        bits.append("near 2-month high")
    elif table == "nearY5H":
        bits.append("near 5-year high")
    elif table == "movingavg_crossed_up":
        bits.append("moving averages crossed up")
    closes = [bar["close"] for bar in daily if bar.get("close")]
    if len(closes) >= 200:
        average = qs.sma(closes, 200)
        if average and closes[-1] > average:
            bits.append("above 200-day average")
    for tag in (qs.extract_scan_signals(scan).get("tags") or [])[:3]:
        if tag not in bits:
            bits.append(tag)
    detail = ", ".join(bits) if bits else "breakout scan"
    times = "time" if hit_count == 1 else "times"
    return f"{table} printed {hit_count} {times} in {window}; {detail}"


class RunStats:
    def __init__(self) -> None:
        self.by_coll: dict[str, dict[str, Any]] = {
            name: {"inserted": 0, "updated": 0, "deleted": 0, "skipped": 0, "rows": []}
            for name in COLLECTIONS
        }
        self.extra: Counter[str] = Counter()

    def skip_low(self, collection: str, count: int = 1) -> None:
        self.by_coll[collection]["skipped"] += count


def ensure_indexes(db) -> None:
    for name in COLLECTIONS:
        db[name].create_index("dedupe_key", unique=True)


def purge_old(db, stats: RunStats) -> None:
    now = datetime.now()
    for name, days in PURGE_DAYS.items():
        if not days:
            continue
        cutoff = now - timedelta(days=days)
        cutoff_text = cutoff.strftime("%Y-%m-%d")
        result = db[name].delete_many(
            {
                "$or": [
                    {"insertion_date": {"$lt": cutoff}},
                    {"insertion_date": {"$lt": cutoff_text, "$type": "string"}},
                ]
            }
        )
        stats.by_coll[name]["deleted"] += result.deleted_count
    for name, minimum in MIN_RETURN_PCT.items():
        upside = {
            "$multiply": [
                {"$divide": [{"$subtract": ["$target_price", "$buy_price"]}, "$buy_price"]},
                100,
            ]
        }
        result = db[name].delete_many(
            {
                "idea_type": {"$nin": sorted(UNGATED_IDEAS)},
                "buy_price": {"$gt": 0},
                "target_price": {"$ne": None},
                "$expr": {"$lte": [upside, minimum]},
            }
        )
        stats.by_coll[name]["deleted"] += result.deleted_count


def upsert_idea(coll, doc: dict, stats: RunStats, collection: str) -> None:
    why = (doc.get("why") or "").strip()
    if not why or doc.get("buy_price") is None or doc.get("target_price") is None:
        stats.extra[f"{collection}:missing-why-or-price"] += 1
        return
    ungated = doc.get("idea_type") in UNGATED_IDEAS
    minimum = MIN_RETURN_PCT.get(collection)
    if not ungated and minimum is not None and not (doc.get("target_pct") or 0) > minimum:
        stats.extra[f"{collection}:return-at-or-below-{minimum:g}%"] += 1
        return
    for longer in COVERED_BY.get(collection, ()):
        if coll.database[longer].find_one({"symbol": doc["symbol"]}, {"_id": 1}):
            stats.extra[f"{collection}:covered-by-{longer.removeprefix('investment-')}"] += 1
            return
    doc["why"] = why
    if not ungated:
        doc["sentiment"] = "Bullish"
    key = doc["dedupe_key"]
    now = datetime.now()
    insert_only = {
        "insertion_date": datetime(now.year, now.month, now.day),
        "insertion_datetime": now,
    }
    payload = {k: v for k, v in doc.items() if k not in insert_only}
    result = coll.update_one(
        {"dedupe_key": key},
        {"$set": payload, "$setOnInsert": insert_only},
        upsert=True,
    )
    bucket = stats.by_coll[collection]
    if result.upserted_id is not None:
        bucket["inserted"] += 1
    else:
        bucket["updated"] += 1
    bucket["rows"].append(payload)


def drop_covered_by_longer(db, stats: RunStats) -> None:
    """Delete rows whose symbol is in a longer horizon (run after every stage).

    Medium is swept before short so short is checked against the final medium set.
    """
    for collection in (COLL_MEDIUM, COLL_SHORT):
        bucket = stats.by_coll[collection]
        for longer in COVERED_BY[collection]:
            symbols = db[longer].distinct("symbol")
            if not symbols:
                continue
            result = db[collection].delete_many({"symbol": {"$in": symbols}})
            if not result.deleted_count:
                continue
            bucket["deleted"] += result.deleted_count
            stats.extra[f"{collection}:covered-by-{longer.removeprefix('investment-')}"] += result.deleted_count
            covered = set(symbols)
            bucket["rows"] = [row for row in bucket["rows"] if row.get("symbol") not in covered]


def scrip_map(db) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for doc in db["scrip"].find({}, {"_id": 0, "scrip": 1, "company": 1, "industry": 1, "marketcap": 1}):
        symbol = doc.get("scrip")
        if symbol:
            out[str(symbol)] = doc
    return out


def fundamental_caps(db) -> dict[str, float]:
    caps: dict[str, float] = {}
    for doc in db["fundamental"].find({}, {"_id": 0, "scrip": 1, "marketcap": 1}):
        symbol = doc.get("scrip")
        crores = to_crores(doc.get("marketcap"))
        if symbol and crores is not None:
            caps[str(symbol)] = crores
    return caps


def collection_exists_and_nonempty(db, name: str) -> bool:
    if name not in set(db.list_collection_names()):
        return False
    return db[name].estimated_document_count() > 0


def group_breakout_rows(rows: list[dict], since: date | None) -> dict[str, list[tuple[date | None, dict]]]:
    grouped: dict[str, list[tuple[date | None, dict]]] = defaultdict(list)
    for row in rows:
        symbol = row.get("scrip")
        if not symbol:
            continue
        stamp = parse_date(row.get("date") or row.get("eventtime"))
        if since and (stamp is None or stamp < since):
            continue
        grouped[str(symbol)].append((stamp, row))
    return grouped


def run_breakouts(db, client, args, stats: RunStats, scrips: dict[str, dict], news: dict[str, dict]) -> None:
    since = months_ago(args.months) if args.months else None
    enrich_cache: dict[str, dict] = {}
    for spec in BREAKOUTS:
        table = spec["table"]
        if not collection_exists_and_nonempty(db, table) and spec["fallback"]:
            table = spec["fallback"]
        if not collection_exists_and_nonempty(db, table):
            stats.extra[f"missing:{spec['table']}"] += 1
            print(f"breakout {spec['table']}: no rows")
            continue
        window = f"{args.months} months" if spec["lookback"] else spec["window"]
        lookback = since if spec["lookback"] else None
        rows = list(db[table].find({}))
        grouped = group_breakout_rows(rows, lookback)
        print(f"breakout {table}: {len(grouped)} symbols")
        ordered = sorted(grouped.items(), key=lambda item: len(item[1]), reverse=True)
        for symbol, hits in ordered:
            hits.sort(key=lambda item: item[0] or date.min)
            signal_date, scan = hits[-1]
            hit_count = len(hits)
            if symbol not in enrich_cache:
                enrich_cache[symbol] = qs.enrich_symbol(client, symbol)
            enrich = enrich_cache[symbol]
            block = score_block(spec["scorer"], scan, enrich)
            meta = passes_gate(block, scan)
            if not meta:
                stats.skip_low(spec["collection"])
                continue
            price = buy_price_from_daily(enrich["daily"])
            info = scrips.get(symbol, {})
            as_of = (signal_date or date.today()).isoformat()
            company = info.get("company") or symbol
            impact = news_impact(news, symbol, company)
            doc = {
                "idea_type": "breakout",
                "symbol": symbol,
                "company": company,
                "industry": scan.get("industry") or info.get("industry") or "",
                "horizon_label": HORIZON_LABEL[spec["collection"]],
                "buy_price": price,
                **target_plan(spec["collection"], spec["scorer"], block, price, enrich["daily"]),
                "stoploss": qs.round_tick(float(block["stop"])) if block.get("stop") is not None else None,
                "conviction": meta["conviction"],
                "sentiment": "Bullish",
                "probability_score": int(meta["probability_score"]),
                "why": f"{breakout_why(table, hit_count, window, scan, enrich['daily'])}; {impact['text']}",
                **news_fields(impact),
                "source": table,
                "source_table": table,
                "hit_count": hit_count,
                "as_of_date": as_of,
                "dedupe_key": f"breakout|{table}|{symbol}|{as_of}",
            }
            if block.get("t2") is not None:
                doc["t2"] = qs.round_tick(float(block["t2"]))
            upsert_idea(db[spec["collection"]], doc, stats, spec["collection"])


class NseClient:
    def __init__(self, pause: float, cache=None) -> None:
        self.pause = pause
        self.cache = cache  # Mongo collection of NSE shareholding responses
        self.cookie = str(Path.home() / ".cache")
        cache_dir = Path.home() / "AppData" / "Local" / "Temp"
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.cookie = str(cache_dir / "investment_ideas_nse_cookies.txt")
        self.curl = shutil.which("curl") or shutil.which("curl.exe")
        self._primed = False

    def prime(self) -> None:
        if not self.curl:
            raise RuntimeError("curl is required for NSE shareholding")
        # --max-time: without it a stalled NSE handshake blocks the run forever.
        subprocess.run(
            [
                self.curl, "-sS", "-c", self.cookie, "-b", self.cookie, "-A", USER_AGENT,
                "-o", "NUL", "-L", "--connect-timeout", "10", "--max-time", "30", NSE_PAGE,
            ],
            check=False,
            capture_output=True,
        )
        self._primed = True

    def get_json(self, path: str) -> Any:
        # A filed quarter (ndsId) never changes; the quarter list is refreshed daily.
        # Without this cache the celebrity stage costs ~2,500 calls (~55 min) per run.
        max_age = None
        if "corporate-share-holdings-equities" in path:
            max_age = timedelta(days=3650)
        elif "corporate-share-holdings-master" in path:
            max_age = timedelta(days=1)
        if self.cache is not None and max_age is not None:
            hit = self.cache.find_one({"path": path, "fetched_at": {"$gte": datetime.now() - max_age}})
            if hit:
                return hit["payload"]
        payload = self._get_json(path)
        if self.cache is not None and max_age is not None:
            self.cache.update_one(
                {"path": path}, {"$set": {"payload": payload, "fetched_at": datetime.now()}}, upsert=True
            )
        return payload

    def _get_json(self, path: str) -> Any:
        if not self._primed:
            self.prime()
        url = path if path.startswith("http") else NSE_ORIGIN + path
        time.sleep(self.pause)
        body = self._fetch(url)
        if body[:1] in {b"<", b""} or not body.lstrip().startswith((b"{", b"[")):
            self.prime()
            time.sleep(self.pause)
            body = self._fetch(url)
        text = body.decode("utf-8", "replace").strip()
        if not text.startswith(("{", "[")):
            raise RuntimeError(text[:180])
        return json.loads(text)

    def _fetch(self, url: str) -> bytes:
        proc = subprocess.run(
            [
                self.curl,
                "-sS",
                "-L",
                "-c",
                self.cookie,
                "-b",
                self.cookie,
                "-A",
                USER_AGENT,
                "-H",
                "Accept: application/json, text/plain, */*",
                "-H",
                f"Referer: {NSE_PAGE}",
                "--connect-timeout",
                "10",
                "--max-time",
                "30",
                url,
            ],
            check=False,
            capture_output=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.decode("utf-8", "replace")[:180])
        return proc.stdout or b""


_SCREENER_SESSION = None


def fetch_screener(symbol: str) -> str | None:
    global _SCREENER_SESSION
    if requests is None:
        raise RuntimeError("requests is required for Screener")
    if _SCREENER_SESSION is None:
        _SCREENER_SESSION = requests.Session()
        _SCREENER_SESSION.headers.update(SCREENER_HEADERS)
    for path in (f"/company/{urllib.parse.quote(symbol)}/consolidated/", f"/company/{urllib.parse.quote(symbol)}/"):
        response = _SCREENER_SESSION.get("https://www.screener.in" + path, timeout=(10, 30))
        if response.status_code == 404:
            continue
        response.raise_for_status()
        text = response.text
        if "Page not found" in text or "does not exist" in text.lower():
            continue
        return text
    return None


def quarter_records(rows: Any) -> list[tuple[date, dict]]:
    if isinstance(rows, dict):
        rows = rows.get("data") or rows.get("rows") or []
    if not isinstance(rows, list):
        return []
    by_date: dict[date, dict] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        stamp = parse_date(row.get("date"))
        if stamp and stamp not in by_date:
            by_date[stamp] = row
    return sorted(by_date.items(), key=lambda item: item[0], reverse=True)


def as_row_list(payload: Any) -> list[dict]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        for key in ("data", "rows", "result"):
            value = payload.get(key)
            if isinstance(value, list):
                return [row for row in value if isinstance(row, dict)]
    return []


def holder_name_and_pct(row: dict) -> tuple[str, float] | None:
    name = str(row.get("shareholderName") or row.get("nameOfPAC") or row.get("COL_II") or row.get("COL_I") or "").strip()
    pct = parse_number(row.get("noOfSharesHeld") if row.get("shareholderName") else None)
    if pct is None:
        pct = parse_number(row.get("COL_VIII") or row.get("perStake") or row.get("holding") or row.get("percentage"))
    if not name or pct is None or name.lower().startswith(("total", "sub-total")):
        return None
    return name, pct


def largest_holders(summary_rows: list[dict], named_rows: list[dict]) -> dict[str, Any]:
    ranked: list[tuple[str, float, bool]] = []
    for row in summary_rows:
        parsed = holder_name_and_pct(row)
        if not parsed:
            continue
        name, pct = parsed
        ranked.append((name, pct, "promoter" in name.lower()))
    named: list[tuple[str, float]] = []
    for row in named_rows:
        parsed = holder_name_and_pct(row)
        if not parsed:
            continue
        name, pct = parsed
        if name.lower() in GENERIC_HOLDERS:
            continue
        named.append((name, pct))
        ranked.append((name, pct, False))
    if not ranked and not named:
        return {}
    top_name, top_pct, _ = max(ranked, key=lambda item: item[1]) if ranked else (named[0][0], named[0][1], False)
    public = max(named, key=lambda item: item[1]) if named else None
    out: dict[str, Any] = {"top_holder_name": top_name, "top_holder_pct": top_pct}
    if public and public[0] != top_name:
        out["top_public_holder_name"] = public[0]
        out["top_public_holder_pct"] = public[1]
    return out


def investor_percent(rows: list[dict], variants: list[str]) -> float | None:
    total = 0.0
    hit = False
    for row in rows:
        blob = " ".join(
            str(row.get(key) or "")
            for key in ("shareholderName", "nameOfPAC", "COL_I", "COL_II")
        )
        if not any(names_match(blob, variant) for variant in variants):
            continue
        parsed = holder_name_and_pct(row)
        if not parsed:
            continue
        total += parsed[1]
        hit = True
    return total if hit else None


def nse_symbol_path(symbol: str, record_id: str | None = None, index: str = "", sub_index: str | None = None) -> str:
    if record_id:
        query = {"ndsId": record_id, "index": index}
        if sub_index:
            query["subIndex"] = sub_index
        return "/api/corporate-share-holdings-equities?" + urllib.parse.urlencode(query)
    return "/api/corporate-share-holdings-master?" + urllib.parse.urlencode(
        {"index": "equities", "symbol": symbol}
    )


def named_public_holders(nse: NseClient, symbol: str, record_id: str) -> list[dict]:
    """Named holders above 1% from the full public-shareholder table.

    NSE's `subIndex=shareholders` view now returns an empty list. The full table
    mixes category headings (`category` "1", "a", ...) with named holders, which
    have a blank `category`; sub-totals and catch-all buckets are dropped.
    """
    rows = as_row_list(nse.get_json(nse_symbol_path(symbol, record_id, "public-shareholder")))
    named: list[dict] = []
    for row in rows:
        if str(row.get("category") or "").strip():
            continue
        name = str(row.get("COL_I") or row.get("COL_II") or "").strip()
        lowered = name.lower()
        if not name or lowered.startswith(("sub-total", "total")) or lowered in PUBLIC_BUCKETS:
            continue
        named.append(row)
    return named


def shareholding_bundle(nse: NseClient, symbol: str, record_id: str) -> tuple[list[dict], list[dict]]:
    summary = as_row_list(nse.get_json(nse_symbol_path(symbol, record_id, "summary")))
    return summary, named_public_holders(nse, symbol, record_id)


def run_orderbook(
    db, client, args, stats: RunStats, scrips: dict[str, dict], nse: NseClient, news: dict[str, dict]
) -> None:
    coll = db[COLL_LONG]
    week_ago = datetime.now() - timedelta(days=7)
    symbols = [symbol for symbol, info in scrips.items() if is_capital_goods(info.get("industry"))]
    print(f"orderbook universe: {len(symbols)}")
    failures = 0
    for index, symbol in enumerate(symbols, start=1):
        if index % 25 == 0:
            print(f"orderbook progress {index}/{len(symbols)}")
        cached = coll.find_one(
            {"idea_type": "orderbook", "symbol": symbol, "page_fetched_at": {"$gte": week_ago}},
            {"_id": 1},
        )
        if cached:
            stats.extra["orderbook:cached"] += 1
            continue
        enrich, block, meta = local_gate(client, symbol, "long", COLL_LONG, stats)
        if not meta:
            continue
        try:
            time.sleep(args.sleep)
            page = fetch_screener(symbol)
            failures = 0
        except Exception as exc:
            failures += 1
            stats.extra["orderbook:http-error"] += 1
            print(f"screener {symbol}: {exc}")
            if failures >= 8:
                print("Screener stopped after 8 consecutive failures")
                break
            continue
        if not page:
            stats.extra["orderbook:no-page"] += 1
            continue
        parsed = parse_screener(page)
        order_book = parsed["order_book_cr"]
        market_cap = parsed["marketcap_cr"]
        sales = parsed["sales_cr"]
        if order_book is None:
            stats.extra["orderbook:no-numeric-order-book"] += 1
            continue
        if market_cap is None or sales is None or sales <= 0 or market_cap <= 0:
            stats.extra["orderbook:missing-mcap-or-sales"] += 1
            continue
        if not (order_book > market_cap and order_book > sales):
            stats.extra["orderbook:below-mcap-or-sales"] += 1
            continue
        try:
            quarters = quarter_records(nse.get_json(nse_symbol_path(symbol)))
            holders: dict[str, Any] = {}
            if quarters:
                summary, named = shareholding_bundle(nse, symbol, str(quarters[0][1].get("recordId")))
                holders = largest_holders(summary, named)
        except Exception as exc:
            stats.extra["orderbook:shareholding-error"] += 1
            print(f"nse holders {symbol}: {exc}")
            holders = {}
        top = holders.get("top_holder_name")
        top_pct = holders.get("top_holder_pct")
        holder_bit = f"; largest holder {top} {pct_text(top_pct)}" if top else ""
        public = holders.get("top_public_holder_name")
        if public and public != top:
            holder_bit += f"; largest non-promoter {public} {pct_text(holders.get('top_public_holder_pct'))}"
        info = scrips.get(symbol, {})
        as_of = date.today().isoformat()
        price = buy_price_from_daily(enrich["daily"])
        company = info.get("company") or symbol
        impact = news_impact(news, symbol, company)
        pros = parsed["pros"]
        cons = parsed["cons"]
        outlook = f"; strengths: {'; '.join(pros[:2])}" if pros else ""
        watch = f"; watch: {cons[0]}" if cons else ""
        doc = {
            "idea_type": "orderbook",
            "symbol": symbol,
            "company": company,
            "industry": info.get("industry") or "",
            "horizon_label": HORIZON_LABEL[COLL_LONG],
            "buy_price": price,
            **target_plan(COLL_LONG, "long", block, price, enrich["daily"]),
            "stoploss": qs.round_tick(float(block["stop"])) if block.get("stop") is not None else None,
            "conviction": meta["conviction"],
            "sentiment": "Bullish",
            "probability_score": int(meta["probability_score"]),
            "why": (
                f"Order book {order_book / market_cap:.1f}x market cap and "
                f"{order_book / sales:.1f}x sales, about {order_book / sales:.1f} years of "
                f"revenue visibility{outlook}{watch}; {impact['text']}{holder_bit}"
            ),
            **news_fields(impact),
            "order_book_years": round(order_book / sales, 2),
            "screener_pros": pros,
            "screener_cons": cons,
            "source": "screener",
            "as_of_date": as_of,
            "order_book_cr": round(order_book, 2),
            "marketcap_cr": round(market_cap, 2),
            "sales_cr": round(sales, 2),
            "page_fetched_at": datetime.now(),
            "dedupe_key": f"orderbook|{symbol}|{as_of}",
        }
        if block.get("t2") is not None:
            doc["t2"] = qs.round_tick(float(block["t2"]))
        doc.update({k: v for k, v in holders.items() if v is not None})
        upsert_idea(coll, doc, stats, COLL_LONG)


def run_celebrity(
    db,
    client,
    args,
    stats: RunStats,
    scrips: dict[str, dict],
    caps: dict[str, float],
    nse: NseClient,
    news: dict[str, dict],
) -> None:
    investors = load_investors(SKILL_DIR / "references" / "investors.md")
    if not investors:
        print("celebrity: investor list is empty")
        return
    cutoff = months_ago(args.celebrity_months)
    universe = []
    for symbol, crores in caps.items():
        bucket = marketcap_bucket(crores)
        if bucket:
            universe.append((symbol, crores, bucket))
    print(f"celebrity universe: {len(universe)} small/mid names, quarters since {cutoff.isoformat()}")
    failures = 0
    for index, (symbol, crores, bucket) in enumerate(universe, start=1):
        if index % 100 == 0:
            print(f"celebrity progress {index}/{len(universe)}")
        try:
            quarters = quarter_records(nse.get_json(nse_symbol_path(symbol)))
            failures = 0
        except Exception as exc:
            failures += 1
            stats.extra["celebrity:http-error"] += 1
            print(f"nse {symbol}: {exc}")
            if failures >= 5:
                print("NSE shareholding stopped after 5 consecutive failures")
                break
            continue
        if not quarters:
            stats.extra["celebrity:no-filing"] += 1
            continue
        latest_date, latest_row = quarters[0]
        if latest_date < cutoff:
            stats.extra["celebrity:quarter-too-old"] += 1
            continue
        try:
            latest_named = named_public_holders(nse, symbol, str(latest_row.get("recordId")))
            previous_named: list[dict] = []
            if len(quarters) > 1:
                previous_named = named_public_holders(nse, symbol, str(quarters[1][1].get("recordId")))
        except Exception as exc:
            stats.extra["celebrity:http-error"] += 1
            print(f"nse holders {symbol}: {exc}")
            continue
        raised: list[tuple[str, float, float | None]] = []
        for canonical, variants in investors:
            latest_pct = investor_percent(latest_named, variants)
            if latest_pct is None or latest_pct <= 0:
                continue
            previous_pct = investor_percent(previous_named, variants) if previous_named else None
            if previous_pct is None:
                raised.append((canonical, latest_pct, None))
            elif round(latest_pct, 2) > round(previous_pct, 2):
                raised.append((canonical, latest_pct, previous_pct))
        if not raised:
            stats.extra["celebrity:no-increase"] += 1
            continue
        # No conviction or upside gate for celebrity buys: score only to record them.
        enrich = qs.enrich_symbol(client, symbol)
        scan = daily_scan(symbol, enrich["daily"])
        block = score_block("swing", scan, enrich)
        if not block or block.get("t1") is None:
            stats.extra["celebrity:no-price-history"] += 1
            continue
        meta = qs.derive_conviction_sentiment(block, qs.extract_scan_signals(scan))
        info = scrips.get(symbol, {})
        price = buy_price_from_daily(enrich["daily"])
        plan = target_plan(COLL_MEDIUM, "swing", block, price, enrich["daily"])
        quarter = latest_date.isoformat()
        company = info.get("company") or symbol
        impact = news_impact(news, symbol, company)
        pros: list[str] = []
        cons: list[str] = []
        try:
            time.sleep(args.sleep)
            page = fetch_screener(symbol)
            if page:
                pros, cons = parse_pros_cons(page)
        except Exception as exc:
            stats.extra["celebrity:screener-error"] += 1
            print(f"screener {symbol}: {exc}")
        draw = "; possible draws: " + "; ".join(pros[:2]) if pros else ""
        watch = f"; watch: {cons[0]}" if cons else ""
        for canonical, latest_pct, previous_pct in raised:
            if previous_pct is None:
                change = f"{canonical} newly holds {pct_text(latest_pct)} in the latest quarter"
                change_pct = latest_pct
            else:
                before, after = pct_text(previous_pct), pct_text(latest_pct)
                if before == after:  # a small raise rounds away at one decimal
                    before, after = f"{previous_pct:.2f}%", f"{latest_pct:.2f}%"
                change = f"{canonical} raised holding from {before} to {after} in the latest quarter"
                change_pct = latest_pct - previous_pct
            doc = {
                "idea_type": "celebrity",
                "symbol": symbol,
                "company": company,
                "industry": info.get("industry") or "",
                "horizon_label": HORIZON_LABEL[COLL_MEDIUM],
                "buy_price": price,
                **plan,
                "stoploss": qs.round_tick(float(block["stop"])) if block.get("stop") is not None else None,
                "conviction": meta["conviction"],
                "sentiment": meta["sentiment"],
                "probability_score": int(meta["probability_score"]),
                "why": f"{change}; {bucket}{draw}{watch}; {impact['text']}",
                **news_fields(impact),
                "screener_pros": pros,
                "screener_cons": cons,
                "source": "nse-shareholding",
                "as_of_date": quarter,
                "investor_name": canonical,
                "holding_pct": round(latest_pct, 2),
                "holding_change_pct": round(change_pct, 2),
                "marketcap_cr": round(crores, 2),
                "marketcap_bucket": bucket,
                "dedupe_key": f"celebrity|{symbol}|{canonical}|{quarter}",
            }
            if block.get("t2") is not None:
                doc["t2"] = qs.round_tick(float(block["t2"]))
            upsert_idea(db[COLL_MEDIUM], doc, stats, COLL_MEDIUM)


DEALS_COLL = "nse_large_deals"
DEALS_SNAPSHOT = "/api/snapshot-capital-market-largedeal"
# Buyers worth following besides the celebrity list. Retail "operators" who buy
# and sell the same day net to zero and drop out anyway.
INSTITUTION_BUYER = re.compile(r"mutual fund|life insurance|general insurance|assurance", re.I)


def store_deal_snapshot(db, nse: NseClient, stats: RunStats) -> None:
    """Append today's NSE bulk and block deals to Nsedata.nse_large_deals.

    NSE's historical deal API is blocked for scripts; the snapshot only covers
    the latest session, so each run keeps it and the window builds up over days.
    """
    payload = nse.get_json(DEALS_SNAPSHOT)
    coll = db[DEALS_COLL]
    coll.create_index("deal_key", unique=True)
    for deal_type, key in (("bulk", "BULK_DEALS_DATA"), ("block", "BLOCK_DEALS_DATA")):
        for row in payload.get(key) or []:
            stamp = parse_date(row.get("date"))
            symbol = str(row.get("symbol") or "").strip()
            client = str(row.get("clientName") or "").strip()
            side = str(row.get("buySell") or "").strip().upper()
            qty = parse_number(row.get("qty"))
            if not (stamp and symbol and client and side in {"BUY", "SELL"} and qty):
                continue
            deal_key = f"{deal_type}|{stamp.isoformat()}|{symbol}|{client}|{side}|{qty:g}|{row.get('watp')}"
            result = coll.update_one(
                {"deal_key": deal_key},
                {
                    "$setOnInsert": {
                        "deal_key": deal_key,
                        "deal_type": deal_type,
                        "date": stamp.isoformat(),
                        "symbol": symbol,
                        "company": row.get("name") or "",
                        "client": client,
                        "side": side,
                        "qty": qty,
                        "price": parse_number(row.get("watp")),
                        "fetched_at": datetime.now(),
                    }
                },
                upsert=True,
            )
            if result.upserted_id is not None:
                stats.extra["deals:stored"] += 1


def deal_buyer(client: str, investors: list[tuple[str, list[str]]]) -> str | None:
    for canonical, variants in investors:
        if any(names_match(client, variant) for variant in variants):
            return canonical
    if INSTITUTION_BUYER.search(client):
        return client.title()
    return None


def run_deals(db, client, args, stats: RunStats, scrips: dict[str, dict], nse: NseClient, news: dict[str, dict]) -> None:
    try:
        store_deal_snapshot(db, nse, stats)
    except Exception as exc:
        stats.extra["deals:http-error"] += 1
        print(f"nse deals snapshot: {exc}")
    investors = load_investors(SKILL_DIR / "references" / "investors.md")
    since = (date.today() - timedelta(days=args.deal_days)).isoformat()
    # (symbol, buyer) -> net qty, buy qty, buy value, latest date, deal types
    groups: dict[tuple[str, str], dict[str, Any]] = {}
    for row in db[DEALS_COLL].find({"date": {"$gte": since}}):
        buyer = deal_buyer(row["client"], investors)
        if not buyer:
            continue
        group = groups.setdefault(
            (row["symbol"], buyer), {"net": 0.0, "bought": 0.0, "value": 0.0, "date": "", "types": set()}
        )
        sign = 1 if row["side"] == "BUY" else -1
        group["net"] += sign * row["qty"]
        if sign > 0:
            group["bought"] += row["qty"]
            group["value"] += row["qty"] * (row.get("price") or 0)
            group["date"] = max(group["date"], row["date"])
            group["types"].add(row["deal_type"])
    buys = {key: group for key, group in groups.items() if group["net"] > 0 and group["bought"] > 0}
    print(f"deals: {len(buys)} net buys by tracked investors or institutions since {since}")
    gated: dict[str, tuple] = {}
    for (symbol, buyer), group in sorted(buys.items()):
        if symbol not in gated:
            gated[symbol] = local_gate(client, symbol, "swing", COLL_MEDIUM, stats)
        enrich, block, meta = gated[symbol]
        if not meta:
            continue
        info = scrips.get(symbol, {})
        company = info.get("company") or symbol
        price = buy_price_from_daily(enrich["daily"])
        impact = news_impact(news, symbol, company)
        deal_price = group["value"] / group["bought"] if group["value"] else None
        types = "/".join(sorted(group["types"]))
        at = f" at about {qs.round_tick(deal_price)}" if deal_price else ""
        doc = {
            "idea_type": "deal",
            "symbol": symbol,
            "company": company,
            "industry": info.get("industry") or "",
            "horizon_label": HORIZON_LABEL[COLL_MEDIUM],
            "buy_price": price,
            **target_plan(COLL_MEDIUM, "swing", block, price, enrich["daily"]),
            "stoploss": qs.round_tick(float(block["stop"])) if block.get("stop") is not None else None,
            "conviction": meta["conviction"],
            "sentiment": "Bullish",
            "probability_score": int(meta["probability_score"]),
            "why": (
                f"{buyer} net bought {group['net']:,.0f} shares in NSE {types} deals{at}, "
                f"latest {group['date']}; {impact['text']}"
            ),
            **news_fields(impact),
            "source": f"nse-{types}-deals",
            "as_of_date": group["date"],
            "investor_name": buyer,
            "deal_net_qty": group["net"],
            "deal_price": qs.round_tick(deal_price) if deal_price else None,
            "dedupe_key": f"deal|{symbol}|{buyer}|{group['date']}",
        }
        if block.get("t2") is not None:
            doc["t2"] = qs.round_tick(float(block["t2"]))
        upsert_idea(db[COLL_MEDIUM], doc, stats, COLL_MEDIUM)


def print_summary(stats: RunStats) -> None:
    print("\nSUMMARY investment-ideas")
    print("collection | inserted | updated | deleted | skipped")
    for name in COLLECTIONS:
        bucket = stats.by_coll[name]
        print(
            f"{name} | {bucket['inserted']} | {bucket['updated']} | "
            f"{bucket['deleted']} | {bucket['skipped']}"
        )
    if stats.extra:
        print("other skips:")
        for key, count in sorted(stats.extra.items()):
            print(f"  {key}: {count}")
    for name in COLLECTIONS:
        rows = stats.by_coll[name]["rows"]
        if not rows:
            continue
        print(f"\n{name}")
        print("symbol | buy | target | target % | days | by date | target reason | conviction | why | holder")
        ordered = sorted(rows, key=lambda row: (-(row.get("hit_count") or 0), row.get("symbol") or ""))
        for row in ordered:
            holder = row.get("investor_name") or row.get("top_holder_name") or ""
            print(
                f"{row.get('symbol')} | {row.get('buy_price')} | {row.get('target_price')} | "
                f"{row.get('target_pct')} | {row.get('target_days')} | {row.get('target_date')} | "
                f"{row.get('target_reason')} | {row.get('conviction')} | {row.get('why')} | {holder}"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Upsert High- and Med-conviction Bullish investment ideas")
    parser.add_argument("--only", choices=("breakout", "orderbook", "celebrity", "deals"))
    parser.add_argument("--months", type=int, default=6)
    parser.add_argument("--celebrity-months", type=int, default=3)
    parser.add_argument("--deal-days", type=int, default=30, help="Window for stored NSE bulk/block deals")
    parser.add_argument("--sleep", type=float, default=1.0)
    parser.add_argument("--uri", default=DEFAULT_URI)
    parser.add_argument(
        "--long-min-return",
        type=float,
        default=MIN_RETURN_PCT[COLL_LONG],
        help="Minimum target upside %% for investment-long-term (default 50)",
    )
    parser.add_argument(
        "--medium-min-return",
        type=float,
        default=MIN_RETURN_PCT[COLL_MEDIUM],
        help="Minimum target upside %% for investment-medium-term (default 30)",
    )
    parser.add_argument(
        "--short-min-return",
        type=float,
        default=MIN_RETURN_PCT[COLL_SHORT],
        help="Minimum target upside %% for investment-short-term (default 20)",
    )
    args = parser.parse_args()
    MIN_RETURN_PCT[COLL_LONG] = args.long_min_return
    MIN_RETURN_PCT[COLL_MEDIUM] = args.medium_min_return
    MIN_RETURN_PCT[COLL_SHORT] = args.short_min_return
    # Progress must reach a redirected log as it happens, not at exit.
    sys.stdout.reconfigure(line_buffering=True)

    client = MongoClient(args.uri, serverSelectionTimeoutMS=4000)
    client.admin.command("ping")
    db = client[DB_NAME]
    stats = RunStats()
    ensure_indexes(db)
    purge_old(db, stats)
    scrips = scrip_map(db)
    news = load_news(db)
    selected = args.only or "all"
    nse = None
    if selected in {"all", "orderbook", "celebrity", "deals"}:
        db[NSE_CACHE_COLL].create_index("path", unique=True)
        nse = NseClient(args.sleep, db[NSE_CACHE_COLL])
    stages = (
        ("breakout", lambda: run_breakouts(db, client, args, stats, scrips, news)),
        ("orderbook", lambda: run_orderbook(db, client, args, stats, scrips, nse, news)),
        ("deals", lambda: run_deals(db, client, args, stats, scrips, nse, news)),
        ("celebrity", lambda: run_celebrity(db, client, args, stats, scrips, fundamental_caps(db), nse, news)),
    )
    for name, stage in stages:
        if selected not in {"all", name}:
            continue
        started = time.time()
        print(f"[{datetime.now():%H:%M:%S}] {name} start")
        stage()
        print(f"[{datetime.now():%H:%M:%S}] {name} done in {time.time() - started:.0f}s")
    drop_covered_by_longer(db, stats)
    print_summary(stats)


if __name__ == "__main__":
    main()
