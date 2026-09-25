#!/usr/bin/env python3
"""Last-5-day scan scrips → scrape news/sector/analyst → sentiment + conviction → Mongo.

Skill: scan-news-conviction
Collection: Nsedata.scrip_news
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

try:
    from pymongo import ASCENDING, MongoClient
except ImportError:
    print("pymongo is required: pip install pymongo", file=sys.stderr)
    sys.exit(1)

try:
    import feedparser
except ImportError:
    print("feedparser is required: pip install feedparser", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "skills" / "india-news-tracker" / "scripts"))
import news_fetcher as nf  # noqa: E402

DEFAULT_URI = "mongodb://localhost:27017"
SCAN_DB = "Nsedata"
TARGET_COLLECTION = "scrip_news"
SCAN_TABLES = [
    "breakoutM2HR",
    "breakoutM2LR",
    "breakoutMHR",
    "breakoutMLR",
    "breakoutW2HR",
    "breakoutW2LR",
    "movingavg_crossed_up",
    "movingavg_crossed_down",
    "breakoutY2H",
    "breakoutYH",
]
ANALYST_RE = re.compile(
    r"upgrade|downgrade|target price|analyst|outperform|underperform|"
    r"buy rating|sell rating|initiate coverage|brokerage|price target",
    re.I,
)
OVERWRITE_DAYS = 30
# Sectoral headlines only count toward overall sentiment / conviction
# when there are at least this many. Company news and analyst calls always count.
MIN_SECTORAL_FOR_SENTIMENT = 3
FUTURES_SKILL_TAG = "futures"
DEFAULT_FUTURES_RETAIN_DAYS = 2
DEFAULT_FUTURES_COMPANY_NEWS_DAYS = 2
FUTURES_SCORING_KINDS = frozenset({"news", "analyst", "regulatory"})
REGULATORY_KIND = "regulatory"
REGULATORY_SECTOR_MIN_IMPACT = 6
REGULATORY_STORAGE_CONVICTION = "High"
EXPOSURE_LANGUAGE_RE = re.compile(
    r"\b("
    r"most exposed|higher exposure|greater exposure|hit hardest|worst hit|"
    r"most impacted|high(?:er)? exposure|material(?:ly)? impacted|"
    r"unit economics.*?unravels|earnings.*?(?:fall|drop|cut)"
    r")\b",
    re.I,
)
REGULATORY_THEMES: dict[str, dict[str, Any]] = {
    "irdai_distribution": {
        "pattern": re.compile(
            r"\b("
            r"irdai|insurance regulator|distribution reform|commission cap|"
            r"bancassurance|expense of management|\beom\b|credit[\s-]?protect|"
            r"loan[\s-]?linked insurance|insurance bundling"
            r")\b",
            re.I,
        ),
        "high_exposure_scrips": frozenset(
            {
                "POLICYBZR",
                "HDFCLIFE",
                "MAXFIN",
                "IDFCFIRSTB",
                "INDUSINDBK",
                "AXISBANK",
                "HDFCBANK",
                "STARHEALTH",
                "ICICIGI",
            }
        ),
    },
    "rbi_banking": {
        "pattern": re.compile(
            r"\b("
            r"\brbi\b|reserve bank|monetary policy|repo rate|crr|slr|"
            r"nbfc regulation|digital lending|npa norm|asset classification"
            r")\b",
            re.I,
        ),
        "high_exposure_scrips": frozenset(
            {
                "IDFCFIRSTB",
                "INDUSINDBK",
                "AXISBANK",
                "HDFCBANK",
                "RBLBANK",
                "AUBANK",
            }
        ),
    },
    "sebi_market": {
        "pattern": re.compile(
            r"\b("
            r"\bsebi\b|securities and exchange board|fno ban|derivatives rule|"
            r"margin norm|insider trading norm|takeover code"
            r")\b",
            re.I,
        ),
        "high_exposure_scrips": frozenset({"POLICYBZR", "BSE", "MCX"}),
    },
}
GENERIC_MARKET_NEWS_RE = re.compile(
    r"\b("
    r"nifty\s*50?|nifty\s+bank|sensex|bank\s+nifty|"
    r"market\s+(?:today|wrap|close|open|update|outlook|mood|pulse|watch|live)|"
    r"stock\s+market\s+(?:today|update|wrap)|"
    r"stocks?\s+to\s+watch|top\s+(?:gainers|losers|picks|movers)|"
    r"sector(?:al)?\s+(?:outlook|rally|view|update|performance)|"
    r"investors?\s+(?:watch|await|should)|"
    r"pre[\s-]?market|post[\s-]?market|opening\s+bell|closing\s+bell|"
    r"weekly\s+wrap|market\s+recap|market\s+live|hot\s+stocks|"
    r"why\s+(?:the\s+)?(?:market|nifty|sensex)\b|"
    r"fii\s+(?:flow|activity|selling|buying)|dii\s+(?:flow|activity)|"
    r"global\s+(?:cues|markets)|wall\s+street|"
    r"crude\s+oil\s+(?:prices?|falls?|rises?)|rupee\s+(?:vs|against)"
    r")\b",
    re.I,
)
WEAK_PRICE_HEADLINE_RE = re.compile(
    r"\b(share price|stock price|in focus|technical view|trading at|"
    r"hits?\s+52[\s-]?week|approaches?\s+52[\s-]?week)\b",
    re.I,
)
COMPANY_CATALYST_RE = re.compile(
    r"\b(results|earnings|profit|revenue|dividend|split|bonus|buyback|"
    r"order|contract|deal|stake|merger|acquisition|upgrade|downgrade|"
    r"target|guidance|board|ceo|md|cfo|sebi|rbi|penalty|fine|"
    r"block deal|bulk deal|promoter|filing|announcement|outlook)\b",
    re.I,
)
BROAD_MARKET_EVENT_TYPES = frozenset({"Macro", "Global"})
COMPANY_SPECIFIC_EVENT_TYPES = frozenset(
    {
        "Earnings",
        "Corporate Action",
        "M&A",
        "Management",
        "Regulatory",
        "Institutional",
        "IPO",
        "Rating",
    }
)
COMPANY_SUFFIX_RE = re.compile(
    r"\b(ltd\.?|limited|inc\.?|corp\.?|corporation|plc|co\.?)\b",
    re.I,
)
SCRIP_COLLECTION = "scrip"
# Weekly 2H/2L scans: drop cash names; keep futures. Other tables keep everyone.
FUTURES_ONLY_TABLES = frozenset({"breakoutW2HR", "breakoutW2LR"})
MAX_SCRIPS = 499  # hard cap: less than 500; futures are never dropped to meet it


def _norm_scrip(value: Any) -> str | None:
    if value is None:
        return None
    s = str(value).strip().upper()
    return None if (not s or s in {"NAN", "NONE"}) else s


def _title_key(title: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (title or "").lower())[:56]


def _near_dup_key(title: str) -> str:
    words = re.findall(r"[a-z0-9]+", (title or "").lower())[:8]
    return " ".join(words)


def _company_match_tokens(company: str) -> list[str]:
    if not company:
        return []
    cleaned = COMPANY_SUFFIX_RE.sub("", company)
    cleaned = re.sub(r"[^a-z0-9\s&]", " ", cleaned.lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    tokens = [t for t in cleaned.split() if len(t) >= 4]
    if cleaned:
        tokens.append(cleaned)
    seen: set[str] = set()
    out: list[str] = []
    for token in tokens:
        if token and token not in seen:
            seen.add(token)
            out.append(token)
    return out


def _mentions_scrip_or_company(text: str, scrip: str, company: str = "") -> bool:
    if not text:
        return False
    text_l = text.lower()
    if re.search(rf"\b{re.escape(scrip.lower())}\b", text_l):
        return True
    for token in _company_match_tokens(company):
        if token in text_l:
            return True
    return False


def headline_primarily_mentions_company(title: str, scrip: str, company: str = "") -> bool:
    """Headline must name the scrip or company; summary-only matches do not count."""
    return _mentions_scrip_or_company((title or "").strip(), scrip, company)


def _is_multi_stock_roundup(title: str, summary: str, scrip: str) -> bool:
    mentioned = nf.detect_stocks(title, summary)
    symbols = {str(s).upper() for s in mentioned}
    return len(symbols) >= 3 and scrip.upper() in symbols


def is_company_specific_news(article: dict, scrip: str, company: str = "") -> bool:
    """True when kind=news is about this company, not a generic market/sector headline."""
    if article.get("kind") != "news":
        return True

    title = (article.get("title") or "").strip()
    summary = (article.get("summary") or "").strip()
    text = f"{title} {summary}".strip()
    if not text or not _mentions_scrip_or_company(text, scrip, company):
        return False

    if GENERIC_MARKET_NEWS_RE.search(title):
        return False
    if _is_multi_stock_roundup(title, summary, scrip):
        return False

    event_type = article.get("event_type") or "General"
    title_mentions = _mentions_scrip_or_company(title, scrip, company)

    if event_type in BROAD_MARKET_EVENT_TYPES and not title_mentions:
        return False

    if event_type in ("Uncategorized", "General"):
        if not title_mentions:
            return False
        if WEAK_PRICE_HEADLINE_RE.search(title) and not COMPANY_CATALYST_RE.search(title):
            return False

    if event_type in COMPANY_SPECIFIC_EVENT_TYPES:
        return True

    return title_mentions


def is_futures_headline_news(article: dict, scrip: str, company: str = "") -> bool:
    """Futures skill: company or analyst headline with company name primarily in title."""
    kind = article.get("kind")
    if kind not in FUTURES_SCORING_KINDS:
        return False

    title = (article.get("title") or "").strip()
    summary = (article.get("summary") or "").strip()
    if not headline_primarily_mentions_company(title, scrip, company):
        return False
    if GENERIC_MARKET_NEWS_RE.search(title):
        return False
    if _is_multi_stock_roundup(title, summary, scrip):
        return False

    if kind == "analyst":
        return bool(ANALYST_RE.search(title) or article.get("event_type") == "Rating")

    event_type = article.get("event_type") or "General"
    if event_type in BROAD_MARKET_EVENT_TYPES:
        return False
    if event_type in ("Uncategorized", "General"):
        if WEAK_PRICE_HEADLINE_RE.search(title) and not COMPANY_CATALYST_RE.search(title):
            return False
    return True


def match_regulatory_theme(article: dict) -> str | None:
    title = (article.get("title") or "").strip()
    summary = (article.get("summary") or "").strip()
    text = f"{title} {summary}".strip()
    if not text:
        return None
    for theme_id, meta in REGULATORY_THEMES.items():
        if meta["pattern"].search(text):
            return theme_id
    return None


def is_regulatory_sector_headline(article: dict) -> bool:
    return match_regulatory_theme(article) is not None


def _headline_flags_scrip_exposure(article: dict, scrip: str, company: str = "") -> bool:
    title = (article.get("title") or "").strip()
    summary = (article.get("summary") or "").strip()
    text = f"{title} {summary}".strip()
    if not EXPOSURE_LANGUAGE_RE.search(text):
        return False
    return _mentions_scrip_or_company(text, scrip, company)


def is_high_exposure_regulatory_scrip(
    scrip: str, theme_id: str, article: dict, company: str = ""
) -> bool:
    scrip_u = _norm_scrip(scrip) or ""
    if not scrip_u:
        return False
    theme = REGULATORY_THEMES.get(theme_id) or {}
    if scrip_u in theme.get("high_exposure_scrips", frozenset()):
        return True
    return _headline_flags_scrip_exposure(article, scrip_u, company)


def tag_regulatory_article(article: dict, theme_id: str, scrip: str) -> dict:
    row = dict(article)
    row["kind"] = REGULATORY_KIND
    row["regulatory_theme"] = theme_id
    row["applies_to_scrip"] = _norm_scrip(scrip)
    impact = int(row.get("impact_score") or 0)
    if impact < REGULATORY_SECTOR_MIN_IMPACT:
        row["impact_score"] = REGULATORY_SECTOR_MIN_IMPACT
    return row


def apply_regulatory_news_for_scrip(
    candidates: list[dict], scrip: str, company: str = ""
) -> list[dict]:
    """Attach high-impact regulatory headlines to high-exposure scrips only."""
    out: list[dict] = []
    for article in candidates:
        theme_id = match_regulatory_theme(article)
        if not theme_id:
            continue
        if int(article.get("impact_score") or 0) < REGULATORY_SECTOR_MIN_IMPACT:
            continue
        if GENERIC_MARKET_NEWS_RE.search(article.get("title") or ""):
            continue
        if not is_high_exposure_regulatory_scrip(scrip, theme_id, article, company):
            continue
        out.append(tag_regulatory_article(article, theme_id, scrip))
    return out


def fetch_regulatory_sector_news(sleep_s: float) -> list[dict]:
    """Shared regulatory headline pool (IRDAI / RBI / SEBI sector reforms)."""
    merged: list[dict] = []
    try:
        for it in nf.fetch_rss_feeds(days_back=3):
            article = _as_article(
                it.title, it.summary, it.link, it.source, it.published, "sectoral"
            )
            if is_regulatory_sector_headline(article):
                merged.append(article)
    except SystemExit:
        pass
    except Exception as exc:
        print(f"  warn: RSS regulatory: {exc}", file=sys.stderr)

    queries = [
        ("IRDAI insurance distribution commission reform India", "Google IRDAI"),
        ("IRDAI bancassurance bank commission India stocks", "Google IRDAI Banks"),
        ("RBI banking regulation circular India stocks", "Google RBI"),
        ("SEBI regulation circular India listed companies", "Google SEBI"),
    ]
    for query, source in queries:
        merged.extend(_parse_feed(_google_rss(query), source, "sectoral"))
        if sleep_s:
            time.sleep(sleep_s)
    return merged


def is_futures_regulatory_news(
    article: dict, scrip: str, company: str = ""
) -> bool:
    if article.get("kind") != REGULATORY_KIND:
        return False
    theme_id = article.get("regulatory_theme") or match_regulatory_theme(article)
    if not theme_id:
        return False
    if int(article.get("impact_score") or 0) < REGULATORY_SECTOR_MIN_IMPACT:
        return False
    if GENERIC_MARKET_NEWS_RE.search(article.get("title") or ""):
        return False
    return is_high_exposure_regulatory_scrip(scrip, theme_id, article, company)


def is_futures_scoring_news(article: dict, scrip: str, company: str = "") -> bool:
    kind = article.get("kind")
    if kind == REGULATORY_KIND:
        return is_futures_regulatory_news(article, scrip, company)
    if kind not in {"news", "analyst"}:
        return False
    return is_futures_headline_news(article, scrip, company)


def filter_company_specific_news(
    articles: list[dict], scrip: str, company: str = ""
) -> list[dict]:
    return [a for a in articles if is_company_specific_news(a, scrip, company)]


def stored_company_news_title_keys(doc: dict | None) -> set[str]:
    if not doc:
        return set()
    keys: set[str] = set()
    for a in list(doc.get("news") or []):
        key = _title_key(a.get("title") or "")
        if key:
            keys.add(key)
    for a in doc.get("articles") or []:
        if a.get("kind") == "news":
            key = _title_key(a.get("title") or "")
            if key:
                keys.add(key)
    return keys


def stored_futures_headline_title_keys(doc: dict | None) -> set[str]:
    if not doc:
        return set()
    keys: set[str] = set()
    for a in list(doc.get("news") or []) + list(doc.get("analyst_calls") or []):
        key = _title_key(a.get("title") or "")
        if key:
            keys.add(key)
    for a in list(doc.get("regulatory_news") or []):
        key = _title_key(a.get("title") or "")
        if key:
            keys.add(key)
    for a in doc.get("articles") or []:
        if a.get("kind") in FUTURES_SCORING_KINDS:
            key = _title_key(a.get("title") or "")
            if key:
                keys.add(key)
    return keys


def is_new_company_news(article: dict, stored_doc: dict | None) -> bool:
    """False when this company headline is already stored on scrip_news."""
    if article.get("kind") != "news":
        return True
    key = _title_key(article.get("title") or "")
    if not key:
        return True
    return key not in stored_company_news_title_keys(stored_doc)


def is_new_futures_headline(article: dict, stored_doc: dict | None) -> bool:
    """False when this company/analyst headline is already stored on scrip_news."""
    if article.get("kind") not in FUTURES_SCORING_KINDS:
        return True
    key = _title_key(article.get("title") or "")
    if not key:
        return True
    return key not in stored_futures_headline_title_keys(stored_doc)


def filter_futures_company_news(
    articles: list[dict],
    scrip: str,
    company: str,
    stored_doc: dict | None,
    now: datetime,
    company_news_days: int = DEFAULT_FUTURES_COMPANY_NEWS_DAYS,
) -> list[dict]:
    """Futures skill: company, analyst, or high-exposure regulatory headlines."""
    out: list[dict] = []
    for a in articles:
        if a.get("kind") not in FUTURES_SCORING_KINDS:
            continue
        if not is_published_within_calendar_days(a.get("published"), now, company_news_days):
            continue
        if not is_futures_scoring_news(a, scrip, company):
            continue
        if not is_new_futures_headline(a, stored_doc):
            continue
        out.append(a)
    return out


def has_new_futures_scoring_news(
    scrip: str,
    now: datetime,
    sleep_s: float,
    stored_doc: dict | None = None,
    company: str = "",
    company_news_days: int = DEFAULT_FUTURES_COMPANY_NEWS_DAYS,
    regulatory_pool: list[dict] | None = None,
) -> bool:
    """True when fresh company/analyst/regulatory headline not already stored."""
    raw = fetch_futures_company_analyst_news(scrip, sleep_s)
    if regulatory_pool is None:
        regulatory_pool = fetch_regulatory_sector_news(sleep_s)
    raw.extend(apply_regulatory_news_for_scrip(regulatory_pool, scrip, company))
    return any(
        is_published_within_calendar_days(a.get("published"), now, company_news_days)
        and is_futures_scoring_news(a, scrip, company)
        and is_new_futures_headline(a, stored_doc)
        for a in raw
    )


def parse_published(value: Any) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value).strip()
        dt = None
        try:
            dt = parsedate_to_datetime(text)
        except Exception:
            pass
        if dt is None:
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d %b %Y", "%d %B %Y"):
                try:
                    dt = datetime.strptime(text[:32], fmt)
                    break
                except Exception:
                    continue
        if dt is None:
            return None
    if dt.tzinfo is not None:
        dt = dt.astimezone().replace(tzinfo=None)
    return dt


def is_fresh(published: Any, news_days: int, now: datetime) -> bool:
    dt = parse_published(published)
    if dt is None:
        return True
    return dt >= now - timedelta(days=news_days)


def is_published_within_calendar_days(
    published: Any, now: datetime, window_days: int
) -> bool:
    """Calendar-date window. window_days=2 -> today and yesterday only."""
    if window_days <= 0:
        return False
    dt = parse_published(published)
    if dt is None:
        return False
    pub_date = dt.date()
    cur = now.date()
    oldest = cur - timedelta(days=window_days - 1)
    return oldest <= pub_date <= cur


def _date_cutoff_query(days: int) -> dict:
    cutoff = datetime.now() - timedelta(days=days)
    cutoff_s = cutoff.strftime("%Y-%m-%d")
    return {
        "$or": [
            {"date": {"$gte": cutoff}},
            {"date": {"$gte": cutoff_s}},
            {"eventtime": {"$gte": cutoff}},
            {"eventtime": {"$gte": cutoff_s}},
        ]
    }


def futures_scrip_set(client: MongoClient) -> set[str]:
    found: set[str] = set()
    for doc in client[SCAN_DB][SCRIP_COLLECTION].find({"futures": "Yes"}, {"scrip": 1}):
        scrip = _norm_scrip(doc.get("scrip"))
        if scrip:
            found.add(scrip)
    return found


def collect_scrips(
    client: MongoClient, days: int, futures: set[str] | None = None
) -> tuple[dict[str, dict], dict[str, int]]:
    """Scan-table universe. Non-futures are excluded only from breakoutW2HR / breakoutW2LR.

    Every futures scrip is merged in so the futures list is never excluded.
    """
    if futures is None:
        futures = futures_scrip_set(client)
    db = client[SCAN_DB]
    found: dict[str, dict] = {}
    stats = {"w2_non_futures_skipped": 0}
    query = _date_cutoff_query(days)
    for table in SCAN_TABLES:
        coll = db[table]
        docs = list(coll.find(query, {"scrip": 1, "industry": 1}))
        if not docs:
            docs = list(coll.find({}, {"scrip": 1, "industry": 1}))
        for doc in docs:
            scrip = _norm_scrip(doc.get("scrip"))
            if not scrip:
                continue
            if table in FUTURES_ONLY_TABLES and scrip not in futures:
                stats["w2_non_futures_skipped"] += 1
                continue
            rec = found.setdefault(scrip, {"industry": "", "company": "", "scan_tables": set()})
            rec["scan_tables"].add(table)
            ind = doc.get("industry")
            if ind and not rec["industry"]:
                rec["industry"] = str(ind).strip()
    for doc in db[SCRIP_COLLECTION].find(
        {"futures": "Yes"}, {"scrip": 1, "industry": 1, "company": 1}
    ):
        scrip = _norm_scrip(doc.get("scrip"))
        if not scrip:
            continue
        rec = found.setdefault(scrip, {"industry": "", "company": "", "scan_tables": set()})
        rec["scan_tables"].add(FUTURES_SKILL_TAG)
        ind = doc.get("industry")
        if ind and not rec["industry"]:
            rec["industry"] = str(ind).strip()
        comp = doc.get("company")
        if comp and not rec["company"]:
            rec["company"] = str(comp).strip()
    _enrich_company_names(client, found)
    return found, stats


def _enrich_company_names(client: MongoClient, found: dict[str, dict]) -> None:
    """Fill company names from Nsedata.scrip for exposure matching."""
    missing = [s for s, rec in found.items() if not rec.get("company")]
    if not missing:
        return
    for doc in client[SCAN_DB][SCRIP_COLLECTION].find(
        {"scrip": {"$in": missing}}, {"scrip": 1, "company": 1}
    ):
        scrip = _norm_scrip(doc.get("scrip"))
        comp = doc.get("company")
        if scrip and scrip in found and comp and not found[scrip].get("company"):
            found[scrip]["company"] = str(comp).strip()


def cap_universe(
    universe: dict[str, dict],
    futures: set[str],
    max_scrips: int = MAX_SCRIPS,
) -> tuple[dict[str, dict], int]:
    """Keep every futures scrip; fill remaining slots with non-futures (most scan tables first)."""
    if max_scrips <= 0 or len(universe) <= max_scrips:
        return universe, 0
    fut_keys = sorted(k for k in universe if k in futures)
    non_keys = sorted(
        (k for k in universe if k not in futures),
        key=lambda k: (-len(universe[k].get("scan_tables") or []), k),
    )
    keep = list(fut_keys)
    if len(keep) >= max_scrips:
        print(
            f"  warn: futures count {len(keep)} >= cap {max_scrips}; "
            "keeping all futures, dropping all non-futures",
            file=sys.stderr,
        )
        kept = {k: universe[k] for k in keep}
        return kept, len(universe) - len(kept)
    room = max_scrips - len(keep)
    keep.extend(non_keys[:room])
    kept = {k: universe[k] for k in keep}
    return kept, len(universe) - len(kept)


def _google_rss(query: str) -> str:
    return (
        "https://news.google.com/rss/search?q="
        + quote_plus(query)
        + "&hl=en-IN&gl=IN&ceid=IN:en"
    )


def _entry_published(entry: Any) -> str:
    if hasattr(entry, "published"):
        return str(entry.published)
    if hasattr(entry, "updated"):
        return str(entry.updated)
    return ""


def _as_article(title, summary, link, source, published, kind_hint: str) -> dict:
    event_type = nf.classify_event(title, summary)
    sentiment = nf.detect_sentiment(title, summary)
    sectors = nf.detect_sectors(title, summary)
    ni = nf.NewsItem(
        title=title,
        source=source,
        published=published or "",
        link=link or "",
        summary=summary or "",
    )
    ni.event_type = event_type
    ni.sentiment = sentiment
    ni.sectors = sectors
    ni.stocks_mentioned = nf.detect_stocks(title, summary)
    impact = nf.score_impact(ni)
    kind = kind_hint
    if ANALYST_RE.search(title or "") or event_type == "Rating":
        kind = "analyst"
    return {
        "title": title,
        "summary": (summary or "")[:400],
        "link": link or "",
        "source": source,
        "published": published or "",
        "event_type": event_type,
        "sentiment": sentiment,
        "sectors": sectors,
        "kind": kind,
        "impact_score": impact,
    }


def _parse_feed(url: str, source: str, kind_hint: str) -> list[dict]:
    items = []
    try:
        feed = feedparser.parse(url)
    except Exception as exc:
        print(f"  warn: feed failed {source}: {exc}", file=sys.stderr)
        return items
    for entry in getattr(feed, "entries", [])[:18]:
        title = str(entry.get("title") or "").strip()
        if not title:
            continue
        summary = re.sub(r"<[^>]+>", "", str(entry.get("summary") or ""))[:400]
        items.append(
            _as_article(
                title,
                summary,
                str(entry.get("link") or ""),
                source,
                _entry_published(entry),
                kind_hint,
            )
        )
    return items


def scrape_scrip(scrip: str, industry: str, days: int, sleep_s: float) -> list[dict]:
    merged: list[dict] = []
    try:
        for it in nf.fetch_rss_feeds(days_back=max(days, 7), stock_filter=scrip):
            kind = "news"
            if ANALYST_RE.search(it.title) or it.event_type == "Rating":
                kind = "analyst"
            elif it.sectors and it.event_type in ("Macro", "Global", "Uncategorized", "General"):
                kind = "sectoral"
            merged.append(
                _as_article(
                    it.title, it.summary, it.link, it.source, it.published, kind
                )
            )
    except SystemExit:
        pass
    except Exception as exc:
        print(f"  warn: RSS {scrip}: {exc}", file=sys.stderr)

    queries = [
        (_google_rss(f"{scrip} NSE OR BSE stock"), "Google News", "news"),
        (
            _google_rss(f'{scrip} analyst OR upgrade OR downgrade OR "target price"'),
            "Google News Analyst",
            "analyst",
        ),
    ]
    if industry:
        queries.append(
            (
                _google_rss(f"{industry} sector India stocks news"),
                "Google News Sector",
                "sectoral",
            )
        )
    for url, source, kind in queries:
        merged.extend(_parse_feed(url, source, kind))
        if sleep_s:
            time.sleep(sleep_s)

    if industry:
        try:
            for it in nf.fetch_rss_feeds(days_back=max(days, 7), sector_filter=industry)[:15]:
                merged.append(
                    _as_article(
                        it.title,
                        it.summary,
                        it.link,
                        it.source,
                        it.published,
                        "sectoral",
                    )
                )
        except Exception:
            pass
    return merged


def is_published_today(published: Any, now: datetime) -> bool:
    dt = parse_published(published)
    if dt is None:
        return False
    return dt.date() == now.date()


def stored_company_news_today(doc: dict | None, now: datetime) -> bool:
    if not doc:
        return False
    items = list(doc.get("news") or [])
    for a in doc.get("articles") or []:
        if a.get("kind") == "news":
            items.append(a)
    return any(is_published_today(a.get("published"), now) for a in items)


def fetch_company_news(scrip: str, sleep_s: float) -> list[dict]:
    """Company headlines only (no sectoral / analyst Google queries)."""
    merged: list[dict] = []
    try:
        for it in nf.fetch_rss_feeds(days_back=2, stock_filter=scrip):
            kind = "news"
            if ANALYST_RE.search(it.title) or it.event_type == "Rating":
                kind = "analyst"
            elif it.sectors and it.event_type in ("Macro", "Global", "Uncategorized", "General"):
                kind = "sectoral"
            if kind != "news":
                continue
            merged.append(
                _as_article(it.title, it.summary, it.link, it.source, it.published, "news")
            )
    except SystemExit:
        pass
    except Exception as exc:
        print(f"  warn: RSS company {scrip}: {exc}", file=sys.stderr)
    merged.extend(_parse_feed(_google_rss(f"{scrip} NSE OR BSE stock"), "Google News", "news"))
    if sleep_s:
        time.sleep(sleep_s)
    return [a for a in merged if a.get("kind") == "news"]


def fetch_futures_company_analyst_news(scrip: str, sleep_s: float) -> list[dict]:
    """Company + analyst headlines only; no sectoral feeds."""
    merged: list[dict] = []
    try:
        for it in nf.fetch_rss_feeds(days_back=2, stock_filter=scrip):
            kind = "news"
            if ANALYST_RE.search(it.title) or it.event_type == "Rating":
                kind = "analyst"
            elif it.sectors and it.event_type in ("Macro", "Global", "Uncategorized", "General"):
                kind = "sectoral"
            if kind not in FUTURES_SCORING_KINDS:
                continue
            merged.append(
                _as_article(it.title, it.summary, it.link, it.source, it.published, kind)
            )
    except SystemExit:
        pass
    except Exception as exc:
        print(f"  warn: RSS futures {scrip}: {exc}", file=sys.stderr)

    queries = [
        (_google_rss(f"{scrip} NSE OR BSE stock"), "Google News", "news"),
        (
            _google_rss(f'{scrip} analyst OR upgrade OR downgrade OR "target price"'),
            "Google News Analyst",
            "analyst",
        ),
    ]
    for url, source, kind in queries:
        merged.extend(_parse_feed(url, source, kind))
        if sleep_s:
            time.sleep(sleep_s)
    return [a for a in merged if a.get("kind") in FUTURES_SCORING_KINDS]


def has_company_news_today(
    scrip: str,
    now: datetime,
    sleep_s: float,
    stored_doc: dict | None = None,
) -> bool:
    if stored_company_news_today(stored_doc, now):
        return True
    return any(is_published_today(a.get("published"), now) for a in fetch_company_news(scrip, sleep_s))


def stored_company_specific_news_today(
    doc: dict | None, now: datetime, scrip: str, company: str = ""
) -> bool:
    if not doc:
        return False
    items = list(doc.get("news") or [])
    for a in doc.get("articles") or []:
        if a.get("kind") == "news":
            items.append(a)
    return any(
        is_published_today(a.get("published"), now)
        and is_company_specific_news(a, scrip, company)
        for a in items
    )


def has_company_specific_news_today(
    scrip: str,
    now: datetime,
    sleep_s: float,
    stored_doc: dict | None = None,
    company: str = "",
) -> bool:
    if stored_company_specific_news_today(stored_doc, now, scrip, company):
        return True
    articles = fetch_company_news(scrip, sleep_s)
    return any(
        is_published_today(a.get("published"), now)
        and is_company_specific_news(a, scrip, company)
        for a in articles
    )


def has_new_company_specific_news(
    scrip: str,
    now: datetime,
    sleep_s: float,
    stored_doc: dict | None = None,
    company: str = "",
    company_news_days: int = DEFAULT_FUTURES_COMPANY_NEWS_DAYS,
    regulatory_pool: list[dict] | None = None,
) -> bool:
    """True when there is fresh company/analyst/regulatory headline not already stored."""
    return has_new_futures_scoring_news(
        scrip,
        now,
        sleep_s,
        stored_doc,
        company,
        company_news_days,
        regulatory_pool,
    )


def dedupe_fresh(articles: list[dict], news_days: int, now: datetime) -> list[dict]:
    out = []
    seen_title = set()
    seen_near = set()
    for a in articles:
        if not is_fresh(a.get("published"), news_days, now):
            continue
        tk = _title_key(a.get("title") or "")
        nk = _near_dup_key(a.get("title") or "")
        if not tk or tk in seen_title or (nk and nk in seen_near):
            continue
        seen_title.add(tk)
        if nk:
            seen_near.add(nk)
        out.append(a)
    return out


def dedupe_fresh_calendar(
    articles: list[dict], window_days: int, now: datetime
) -> list[dict]:
    """Dedupe with calendar today/yesterday window; drop unparseable dates."""
    out = []
    seen_title = set()
    seen_near = set()
    for a in articles:
        if not is_published_within_calendar_days(a.get("published"), now, window_days):
            continue
        tk = _title_key(a.get("title") or "")
        nk = _near_dup_key(a.get("title") or "")
        if not tk or tk in seen_title or (nk and nk in seen_near):
            continue
        seen_title.add(tk)
        if nk:
            seen_near.add(nk)
        out.append(a)
    return out


def select_high_impact(articles: list[dict], min_impact: int) -> list[dict]:
    ranked = sorted(articles, key=lambda a: int(a.get("impact_score") or 0), reverse=True)

    def take(kind: str, n: int) -> list[dict]:
        pool = [a for a in ranked if a.get("kind") == kind]
        strong = [a for a in pool if int(a.get("impact_score") or 0) >= min_impact]
        if len(strong) >= 3:
            return strong[:n]
        return (strong + [a for a in pool if a not in strong])[:n]

    news = take("news", 10)
    sectoral = take("sectoral", 6)
    analyst = take("analyst", 6)
    regulatory = take(REGULATORY_KIND, 4)
    other = [
        a
        for a in ranked
        if a.get("kind") not in {"news", "sectoral", "analyst", REGULATORY_KIND}
    ][:4]
    combined = news + sectoral + analyst + regulatory + other
    # stable unique by title key
    seen = set()
    uniq = []
    for a in combined:
        k = _title_key(a.get("title") or "")
        if k in seen:
            continue
        seen.add(k)
        uniq.append(a)
    return uniq


def select_futures_company_news(articles: list[dict], min_impact: int) -> list[dict]:
    """Futures skill: high-impact company + analyst headlines (no sectoral)."""
    ranked = sorted(
        [a for a in articles if a.get("kind") in FUTURES_SCORING_KINDS],
        key=lambda a: int(a.get("impact_score") or 0),
        reverse=True,
    )

    def take(kind: str, n: int) -> list[dict]:
        pool = [a for a in ranked if a.get("kind") == kind]
        strong = [a for a in pool if int(a.get("impact_score") or 0) >= min_impact]
        if len(strong) >= 3:
            return strong[:n]
        return (strong + [a for a in pool if a not in strong])[:n]

    combined = take("news", 10) + take("analyst", 6) + take(REGULATORY_KIND, 4)
    seen = set()
    uniq = []
    for a in combined:
        k = _title_key(a.get("title") or "")
        if k in seen:
            continue
        seen.add(k)
        uniq.append(a)
    return uniq


def articles_for_overall_sentiment(articles: list[dict]) -> list[dict]:
    """Company, analyst, and regulatory always count; sectoral only if count >= 3."""
    sectoral = [a for a in articles if a.get("kind") == "sectoral"]
    if len(sectoral) >= MIN_SECTORAL_FOR_SENTIMENT:
        return list(articles)
    return [a for a in articles if a.get("kind") != "sectoral"]


def conviction_from_articles(articles: list[dict]) -> tuple[str, str]:
    scoring = articles_for_overall_sentiment(articles)
    sentiment = overall_sentiment(scoring)
    conviction = conviction_for(scoring, sentiment)
    return sentiment, conviction


def drop_regulatory_unless_high_conviction(articles: list[dict]) -> list[dict]:
    """Keep regulatory headlines only when recomputed conviction is High."""
    if not any(a.get("kind") == REGULATORY_KIND for a in articles):
        return articles
    _, conviction = conviction_from_articles(articles)
    if conviction == REGULATORY_STORAGE_CONVICTION:
        return articles
    return [a for a in articles if a.get("kind") != REGULATORY_KIND]


def futures_should_write(
    new_articles: list[dict], merged_articles: list[dict]
) -> bool:
    """Write when new company/analyst headlines exist, or new regulatory with High conviction."""
    if not new_articles:
        return False
    non_reg = [a for a in new_articles if a.get("kind") != REGULATORY_KIND]
    if non_reg:
        return True
    _, conviction = conviction_from_articles(merged_articles)
    return conviction == REGULATORY_STORAGE_CONVICTION


def merge_stored_and_new_articles(
    existing: dict | None, new_articles: list[dict]
) -> list[dict]:
    """Append new headlines to stored scrip_news articles; dedupe by title."""
    if not new_articles:
        return articles_from_doc(existing) if existing else []
    if not existing:
        return list(new_articles)
    merged = articles_from_doc(existing)
    seen = {_title_key(a.get("title") or "") for a in merged if _title_key(a.get("title") or "")}
    for article in new_articles:
        key = _title_key(article.get("title") or "")
        if key and key in seen:
            continue
        merged.append(article)
        if key:
            seen.add(key)
    return merged


def articles_from_doc(doc: dict) -> list[dict]:
    """Rebuild a kind-tagged article list from a stored scrip_news document."""
    stored = list(doc.get("articles") or [])
    if stored and any(a.get("kind") for a in stored):
        return stored
    rebuilt: list[dict] = []
    for kind, key in (
        ("news", "news"),
        ("sectoral", "sectoral_news"),
        ("analyst", "analyst_calls"),
        (REGULATORY_KIND, "regulatory_news"),
    ):
        for item in doc.get(key) or []:
            row = dict(item)
            row["kind"] = row.get("kind") or kind
            rebuilt.append(row)
    return rebuilt or stored


def overall_sentiment(articles: list[dict]) -> str:
    scored = articles_for_overall_sentiment(articles)
    bull = sum(1 for a in scored if a.get("sentiment") == "Bullish")
    bear = sum(1 for a in scored if a.get("sentiment") == "Bearish")
    if bull > bear and bull:
        return "Bullish"
    if bear > bull and bear:
        return "Bearish"
    if bull and bear:
        return "Mixed"
    return "Neutral"


def conviction_for(articles: list[dict], sentiment: str) -> str:
    articles = articles_for_overall_sentiment(articles)
    if not articles:
        return "Low"
    regulatory = [a for a in articles if a.get("kind") == REGULATORY_KIND]
    if regulatory and sentiment in ("Bullish", "Bearish"):
        aligned_reg = [
            a
            for a in regulatory
            if a.get("sentiment") == sentiment
            and int(a.get("impact_score") or 0) >= REGULATORY_SECTOR_MIN_IMPACT
        ]
        if aligned_reg:
            return REGULATORY_STORAGE_CONVICTION
    hi = [a for a in articles if int(a.get("impact_score") or 0) >= 6]
    aligned = [
        a
        for a in articles
        if sentiment in ("Bullish", "Bearish") and a.get("sentiment") == sentiment
    ]
    avg = sum(int(a.get("impact_score") or 0) for a in articles) / max(1, len(articles))
    if sentiment in ("Bullish", "Bearish") and len(aligned) >= 3 and (len(hi) >= 2 or avg >= 6):
        return "High"
    if (sentiment == "Mixed" and hi) or (sentiment in ("Bullish", "Bearish") and len(aligned) >= 2) or avg >= 5:
        return "Med"
    return "Low"


def _as_naive(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.astimezone().replace(tzinfo=None)
    return dt


def split_article_kinds(
    articles: list[dict],
) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    news = [a for a in articles if a.get("kind") == "news"]
    sectoral = [a for a in articles if a.get("kind") == "sectoral"]
    analyst = [a for a in articles if a.get("kind") == "analyst"]
    regulatory = [a for a in articles if a.get("kind") == REGULATORY_KIND]
    return news, sectoral, analyst, regulatory


def summary_row(scrip: str, industry: str, tables: list[str], articles: list[dict], action: str) -> dict[str, Any]:
    scoring = articles_for_overall_sentiment(articles)
    sentiment = overall_sentiment(scoring)
    conviction = conviction_for(scoring, sentiment)
    news, sectoral, analyst, regulatory = split_article_kinds(scoring)
    return {
        "scrip": scrip,
        "industry": industry or "",
        "scan_tables": tables,
        "action": action,
        "sentiment": sentiment,
        "conviction": conviction,
        "items": len(scoring),
        "news": news,
        "sectoral": sectoral,
        "analyst": analyst,
        "regulatory": regulatory,
    }


def _headline_line(scrip: str, industry: str, article: dict) -> str:
    title = (article.get("title") or "").replace("\n", " ").strip()
    if len(title) > 140:
        title = title[:137] + "..."
    impact = article.get("impact_score") or 0
    sent = article.get("sentiment") or ""
    pub = (article.get("published") or "")[:16]
    extra = f"  {industry}" if industry else ""
    when = f"  {pub}" if pub else ""
    return f"  {scrip:12} [{sent:8} i={impact}]{when}{extra}\n    {title}"


def print_news_digest(rows: list[dict[str, Any]], skill_name: str = "") -> None:
    """End-of-run list of company news and high-conviction sectoral headlines."""
    header = f"SUMMARY NEWS DIGEST - {skill_name}" if skill_name else "SUMMARY NEWS DIGEST"
    print("\n" + "=" * 72)
    print(header)
    print("=" * 72)

    company: list[tuple[int, str, str, dict]] = []
    for row in rows:
        for a in row.get("news") or []:
            company.append((int(a.get("impact_score") or 0), row["scrip"], row.get("industry") or "", a))
    company.sort(key=lambda t: (-t[0], t[1]))

    print(f"\nCOMPANY NEWS ({len(company)})")
    if not company:
        print("  (none)")
    else:
        for _impact, scrip, industry, article in company:
            print(_headline_line(scrip, industry, article))

    sectoral_lines: list[tuple[int, str, str, dict]] = []
    seen = set()
    high_rows = [r for r in rows if r.get("conviction") == "High"]
    for row in high_rows:
        for a in row.get("sectoral") or []:
            key = _title_key(a.get("title") or "")
            if not key or key in seen:
                continue
            seen.add(key)
            sectoral_lines.append(
                (int(a.get("impact_score") or 0), row["scrip"], row.get("industry") or "", a)
            )
    sectoral_lines.sort(key=lambda t: (-t[0], t[1]))

    print(f"\nHIGH CONVICTION SECTORAL NEWS ({len(sectoral_lines)})")
    print(f"  High-conviction scrips this run: {len(high_rows)}")
    if not sectoral_lines:
        print("  (none stored — High conviction needs >= 3 sectoral items, or none High this run)")
        for row in high_rows:
            n_sec = len(row.get("sectoral") or [])
            print(f"  {row['scrip']:12} {row['sentiment']:8} sectoral={n_sec}  {row.get('industry') or ''}")
    else:
        for _impact, scrip, industry, article in sectoral_lines:
            print(_headline_line(scrip, industry, article))

    regulatory_lines: list[tuple[int, str, str, dict]] = []
    for row in high_rows:
        for a in row.get("regulatory") or []:
            regulatory_lines.append(
                (int(a.get("impact_score") or 0), row["scrip"], row.get("industry") or "", a)
            )
    regulatory_lines.sort(key=lambda t: (-t[0], t[1]))
    print(f"\nHIGH CONVICTION REGULATORY NEWS ({len(regulatory_lines)})")
    if not regulatory_lines:
        print("  (none — regulatory headlines require High conviction + impact >= 6)")
    else:
        for _impact, scrip, industry, article in regulatory_lines:
            theme = article.get("regulatory_theme") or ""
            line = _headline_line(scrip, industry, article)
            if theme:
                line = line.replace("\n    ", f"\n    [{theme}] ", 1)
            print(line)
    print("=" * 72)


def upsert_scrip(coll, scrip: str, industry: str, tables: list[str], articles: list[dict]) -> str:
    now = datetime.now()
    articles = drop_regulatory_unless_high_conviction(articles)
    articles = articles_for_overall_sentiment(articles)
    sentiment = overall_sentiment(articles)
    conviction = conviction_for(articles, sentiment)
    news, sectoral, analyst, regulatory = split_article_kinds(articles)
    payload = {
        "scrip": scrip,
        "industry": industry,
        "scan_tables": tables,
        "articles": articles,
        "news": news,
        "sectoral_news": sectoral,
        "analyst_calls": analyst,
        "regulatory_news": regulatory,
        "overall_sentiment": sentiment,
        "conviction": conviction,
        "article_count": len(articles),
        "updated_at": now,
    }
    existing = coll.find_one({"scrip": scrip})
    if existing:
        stamp = _as_naive(existing.get("insertion_date") or existing.get("updated_at"))
        if stamp and (now - stamp).days >= OVERWRITE_DAYS:
            payload["insertion_date"] = now
            coll.replace_one({"scrip": scrip}, payload)
            return "overwrite"
        coll.update_one({"scrip": scrip}, {"$set": payload})
        return "update"
    payload["insertion_date"] = now
    coll.insert_one(payload)
    return "insert"


def setup_indexes(coll) -> None:
    coll.create_index([("scrip", ASCENDING)], unique=True)
    coll.create_index([("insertion_date", ASCENDING)])
    coll.create_index([("updated_at", ASCENDING)])


def doc_last_touch(doc: dict | None) -> datetime | None:
    if not doc:
        return None
    dates = [
        _as_naive(doc.get("insertion_date")),
        _as_naive(doc.get("updated_at")),
    ]
    dates = [d for d in dates if d]
    return max(dates) if dates else None


def is_from_breakout_scan_table(doc: dict) -> bool:
    return any(str(t) in SCAN_TABLES for t in (doc.get("scan_tables") or []) if t)


def is_futures_skill_only(doc: dict) -> bool:
    tables = {str(t) for t in (doc.get("scan_tables") or []) if t}
    return bool(tables) and tables <= {FUTURES_SKILL_TAG}


def purge_stale_futures_skill_rows(
    coll, now: datetime, retain_days: int = DEFAULT_FUTURES_RETAIN_DAYS
) -> tuple[int, list[str]]:
    """Drop scrip_news rows written only by scan-news-conviction-futures."""
    cutoff = now - timedelta(days=retain_days)
    deleted: list[str] = []
    for doc in coll.find(
        {"scan_tables": FUTURES_SKILL_TAG},
        {"scrip": 1, "scan_tables": 1, "insertion_date": 1, "updated_at": 1},
    ):
        if is_from_breakout_scan_table(doc) or not is_futures_skill_only(doc):
            continue
        stamp = doc_last_touch(doc)
        if stamp is None or stamp >= cutoff:
            continue
        scrip = _norm_scrip(doc.get("scrip"))
        if not scrip:
            continue
        coll.delete_one({"_id": doc["_id"]})
        deleted.append(scrip)
    return len(deleted), sorted(deleted)


def print_futures_skill_purge(
    purge_count: int, purge_scrips: list[str], retain_days: int
) -> None:
    if purge_count:
        print(
            f"Purged {purge_count} expired futures-skill-only {TARGET_COLLECTION} rows "
            f"(>{retain_days} days; breakout-tagged rows ignored)"
        )
    else:
        print(
            f"No expired futures-skill-only {TARGET_COLLECTION} rows to purge "
            f"(>{retain_days} days)"
        )
    if purge_scrips and len(purge_scrips) <= 40:
        print("Purged scrips: " + ", ".join(purge_scrips))
    elif purge_scrips:
        print(
            f"Purged sample ({min(20, len(purge_scrips))} of {len(purge_scrips)}): "
            + ", ".join(purge_scrips[:20])
        )


def recompute_scrip_news(coll) -> dict[str, int]:
    """Recalculate overall_sentiment / conviction; apply regulatory + sectoral rules."""
    counts = {"checked": 0, "updated": 0, "unchanged": 0}
    now = datetime.now()
    for doc in coll.find({}):
        counts["checked"] += 1
        full = drop_regulatory_unless_high_conviction(articles_from_doc(doc))
        articles = articles_for_overall_sentiment(full)
        sentiment = overall_sentiment(articles)
        conviction = conviction_for(articles, sentiment)
        news, sectoral, analyst, regulatory = split_article_kinds(articles)
        prev_sent = doc.get("overall_sentiment")
        prev_conv = doc.get("conviction")
        prev_sectoral = len(doc.get("sectoral_news") or [])
        prev_regulatory = len(doc.get("regulatory_news") or [])
        same_score = prev_sent == sentiment and prev_conv == conviction
        same_sectoral = prev_sectoral == len(sectoral)
        same_regulatory = prev_regulatory == len(regulatory)
        if (
            same_score
            and same_sectoral
            and same_regulatory
            and len(doc.get("articles") or []) == len(articles)
        ):
            counts["unchanged"] += 1
            continue
        coll.update_one(
            {"_id": doc["_id"]},
            {
                "$set": {
                    "articles": articles,
                    "news": news,
                    "sectoral_news": sectoral,
                    "analyst_calls": analyst,
                    "regulatory_news": regulatory,
                    "article_count": len(articles),
                    "overall_sentiment": sentiment,
                    "conviction": conviction,
                    "updated_at": now,
                }
            },
        )
        counts["updated"] += 1
        scrip = doc.get("scrip") or doc.get("_id")
        print(
            f"    {scrip}: {prev_sent}/{prev_conv} -> {sentiment}/{conviction} "
            f"sectoral {prev_sectoral}->{len(sectoral)} "
            f"regulatory {prev_regulatory}->{len(regulatory)}"
        )
    return counts


def _configure_stdio() -> None:
    """Avoid Windows cp1252 crashes on rupee/en-dash in headline digest."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if not reconfigure:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def main() -> None:
    _configure_stdio()
    parser = argparse.ArgumentParser(description="scan-news-conviction ingest")
    parser.add_argument("--uri", default=DEFAULT_URI)
    parser.add_argument("--days", type=int, default=5, help="Scan-table lookback")
    parser.add_argument("--news-days", type=int, default=7, help="Max headline age")
    parser.add_argument("--min-impact", type=int, default=4)
    parser.add_argument("--sleep", type=float, default=0.35)
    parser.add_argument("--scrips", default="")
    parser.add_argument(
        "--limit",
        type=int,
        default=MAX_SCRIPS,
        help=f"Max scrips (default {MAX_SCRIPS}, always < 500). Futures are never dropped.",
    )
    parser.add_argument(
        "--recompute-only",
        action="store_true",
        help="Recalculate overall_sentiment/conviction on existing scrip_news; do not scrape",
    )
    parser.add_argument(
        "--retain-futures-days",
        type=int,
        default=DEFAULT_FUTURES_RETAIN_DAYS,
        help="Delete futures-skill-only scrip_news rows older than this (breakout-tagged rows kept)",
    )
    args = parser.parse_args()

    now = datetime.now()
    client = MongoClient(args.uri, serverSelectionTimeoutMS=8000)
    client.admin.command("ping")
    coll = client[SCAN_DB][TARGET_COLLECTION]
    setup_indexes(coll)

    purge_count, purge_scrips = purge_stale_futures_skill_rows(
        coll, now, args.retain_futures_days
    )
    print_futures_skill_purge(purge_count, purge_scrips, args.retain_futures_days)

    if args.recompute_only:
        print("Skill: scan-news-conviction (recompute existing scrip_news)")
        print(
            f"Sectoral news counts toward sentiment only if "
            f"count >= {MIN_SECTORAL_FOR_SENTIMENT}; company, analyst, and regulatory "
            f"(High conviction, impact >= {REGULATORY_SECTOR_MIN_IMPACT}) always count"
        )
        counts = recompute_scrip_news(coll)
        print(
            f"\nDone. checked={counts['checked']} updated={counts['updated']} "
            f"unchanged={counts['unchanged']} purged_futures_skill={purge_count} "
            f"collection={SCAN_DB}.{TARGET_COLLECTION}"
        )
        client.close()
        return

    futures = futures_scrip_set(client)
    universe, collect_stats = collect_scrips(client, args.days, futures)
    if args.scrips:
        want = {_norm_scrip(s) for s in args.scrips.split(",") if _norm_scrip(s)}
        universe = {k: v for k, v in universe.items() if k in want}
    cap = args.limit if args.limit > 0 else MAX_SCRIPS
    cap = min(cap, MAX_SCRIPS)
    raw_count = len(universe)
    universe, trimmed = cap_universe(universe, futures, cap)
    scrips = sorted(universe.keys())
    n_fut = sum(1 for s in scrips if s in futures)

    print("Skill: scan-news-conviction")
    print(f"Scan tables: {', '.join(SCAN_TABLES)}")
    print(
        f"W2HR/W2LR: futures only (skipped non-futures rows: "
        f"{collect_stats['w2_non_futures_skipped']})"
    )
    print(f"Cap: {cap} (<500); futures list never excluded")
    print(
        f"Scrips (last {args.days}d): {len(scrips)} "
        f"(raw={raw_count} trimmed_non_futures={trimmed} futures={n_fut})"
    )
    counts = {"insert": 0, "update": 0, "overwrite": 0}
    processed: list[dict[str, Any]] = []

    regulatory_pool = dedupe_fresh(
        fetch_regulatory_sector_news(args.sleep), args.news_days, now
    )
    print(
        f"Regulatory pool: {len(regulatory_pool)} headlines "
        f"(high-exposure scrips only; stored if conviction=High, impact>={REGULATORY_SECTOR_MIN_IMPACT})"
    )

    for i, scrip in enumerate(scrips, 1):
        meta = universe[scrip]
        tables = sorted(meta["scan_tables"])
        industry = meta.get("industry") or ""
        company = meta.get("company") or ""
        print(f"[{i}/{len(scrips)}] {scrip} ({', '.join(tables)})")
        raw = scrape_scrip(scrip, industry, args.days, args.sleep)
        raw.extend(apply_regulatory_news_for_scrip(regulatory_pool, scrip, company))
        cleaned = select_high_impact(dedupe_fresh(raw, args.news_days, now), args.min_impact)
        action = upsert_scrip(coll, scrip, industry, tables, cleaned)
        counts[action] = counts.get(action, 0) + 1
        row = summary_row(
            scrip,
            industry,
            tables,
            articles_for_overall_sentiment(
                drop_regulatory_unless_high_conviction(cleaned)
            ),
            action,
        )
        processed.append(row)
        print(
            f"    {action}  items={row['items']}  sentiment={row['sentiment']}  "
            f"conviction={row['conviction']}"
        )

    print(
        f"\nDone. insert={counts['insert']} update={counts['update']} "
        f"overwrite={counts['overwrite']} purged_futures_skill={purge_count} "
        f"collection={SCAN_DB}.{TARGET_COLLECTION}"
    )
    print_news_digest(processed, skill_name="scan-news-conviction")
    client.close()


if __name__ == "__main__":
    main()
