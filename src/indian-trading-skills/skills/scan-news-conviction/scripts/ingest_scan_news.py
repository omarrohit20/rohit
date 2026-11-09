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
from datetime import date, datetime, timedelta
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
DEFAULT_NEWS_DAYS = 7
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
    r"block deal|bulk deal|promoter|filing|announcement|outlook|"
    r"concall|conference call|earnings call)\b",
    re.I,
)
GENERIC_COMPANY_SHORT_TOKENS = frozenset(
    {
        "india",
        "indian",
        "bank",
        "power",
        "steel",
        "energy",
        "finance",
        "financial",
        "industries",
        "industry",
        "services",
        "holdings",
        "group",
        "global",
        "international",
        "national",
        "general",
        "united",
        "enterprises",
        "products",
        "limited",
        "company",
        "corporation",
        "the",
        "and",
    }
)
GUIDANCE_GOOGLE_TERMS = (
    'results OR earnings OR guidance OR concall OR "earnings call" '
    'OR "conference call" OR outlook OR "board meeting" OR "board meet" '
    'OR "interim dividend" OR dividend OR "quarterly results"'
)
CORPORATE_EVENT_RE = re.compile(
    r"\b("
    r"board meeting|board meet|"
    r"interim dividend|final dividend|"
    r"quarterly results|unaudited financial results|"
    r"to consider.{0,60}(?:results|dividend)|"
    r"results on|dividend on"
    r")\b",
    re.I,
)
_MONTH_NUM = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}
_MONTH_NAME_RE = (
    r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|"
    r"Nov(?:ember)?|Dec(?:ember)?"
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


def company_short_name(company: str) -> str:
    """Search form used in Google/RSS, e.g. Data Patterns (India) Ltd. → Data Patterns."""
    if not company:
        return ""
    cleaned = COMPANY_SUFFIX_RE.sub("", company)
    cleaned = re.sub(r"\([^)]*\)", " ", cleaned)
    cleaned = re.sub(r"[^a-zA-Z0-9\s&]", " ", cleaned)
    drop = {"india", "indian", "of", "the", "and", "&"}
    tokens = [t for t in cleaned.split() if t.lower() not in drop]
    keep: list[str] = []
    for token in tokens:
        if len(token) >= 3:
            keep.append(token)
        if len(keep) >= 3:
            break
    if not keep:
        return ""
    if all(t.lower() in GENERIC_COMPANY_SHORT_TOKENS for t in keep):
        return ""
    if len(keep) >= 2:
        return " ".join(keep[:2])
    if keep[0].lower() in GENERIC_COMPANY_SHORT_TOKENS or len(keep[0]) < 4:
        return ""
    return keep[0]


def company_search_aliases(scrip: str, company: str = "") -> list[str]:
    """Ticker plus company short/full names for RSS matching."""
    aliases: list[str] = []
    seen: set[str] = set()
    scrip_l = (scrip or "").strip().lower()
    if scrip_l:
        seen.add(scrip_l)

    def _add(value: str) -> None:
        text = (value or "").strip()
        if not text:
            return
        key = text.lower()
        if key in seen:
            return
        seen.add(key)
        aliases.append(text)

    _add(company_short_name(company))
    _add(company)
    return aliases


def _google_or_clause(scrip: str, company: str = "") -> str:
    short = company_short_name(company)
    if short and short.upper() != (scrip or "").upper():
        return f'{scrip} OR "{short}"'
    return scrip


def google_news_queries(
    scrip: str,
    company: str = "",
    *,
    include_analyst: bool = True,
    include_guidance: bool = True,
    industry: str = "",
) -> list[tuple[str, str, str]]:
    """Google News RSS (url, source, kind) using ticker and company short name."""
    clause = _google_or_clause(scrip, company)
    queries = [
        (_google_rss(f"{clause} (NSE OR BSE OR stock)"), "Google News", "news"),
    ]
    if include_guidance:
        queries.append(
            (
                _google_rss(f"{clause} ({GUIDANCE_GOOGLE_TERMS})"),
                "Google News Guidance",
                "news",
            )
        )
    if include_analyst:
        queries.append(
            (
                _google_rss(
                    f'{clause} (analyst OR upgrade OR downgrade OR "target price")'
                ),
                "Google News Analyst",
                "analyst",
            )
        )
    if industry:
        queries.append(
            (
                _google_rss(f"{industry} sector India stocks news"),
                "Google News Sector",
                "sectoral",
            )
        )
    return queries


def _fetch_india_rss_for_scrip(
    scrip: str,
    company: str,
    days_back: int,
    allowed_kinds: set[str] | None = None,
) -> list[dict]:
    merged: list[dict] = []
    for it in nf.fetch_rss_feeds(
        days_back=days_back,
        stock_filter=scrip,
        stock_aliases=company_search_aliases(scrip, company),
    ):
        kind = "news"
        if ANALYST_RE.search(it.title) or it.event_type == "Rating":
            kind = "analyst"
        elif it.sectors and it.event_type in ("Macro", "Global", "Uncategorized", "General"):
            kind = "sectoral"
        if allowed_kinds is not None and kind not in allowed_kinds:
            continue
        merged.append(
            _as_article(it.title, it.summary, it.link, it.source, it.published, kind)
        )
    return merged


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
    successful_sources = 0
    failures = []
    try:
        for it in nf.fetch_rss_feeds(days_back=3):
            article = _as_article(
                it.title, it.summary, it.link, it.source, it.published, "sectoral"
            )
            if is_regulatory_sector_headline(article):
                merged.append(article)
        successful_sources += 1
    except SystemExit:
        pass
    except Exception as exc:
        failures.append(f"India news RSS: {exc}")
        print(f"  warn: RSS regulatory: {exc}", file=sys.stderr)

    queries = [
        ("IRDAI insurance distribution commission reform India", "Google IRDAI"),
        ("IRDAI bancassurance bank commission India stocks", "Google IRDAI Banks"),
        ("RBI banking regulation circular India stocks", "Google RBI"),
        ("SEBI regulation circular India listed companies", "Google SEBI"),
    ]
    for query, source in queries:
        try:
            merged.extend(_parse_feed(_google_rss(query), source, "sectoral"))
            successful_sources += 1
        except nf.FeedFetchError as exc:
            failures.append(f"{source}: {exc}")
            print(f"  warn: RSS {source}: {exc}", file=sys.stderr)
        if sleep_s:
            time.sleep(sleep_s)
    if successful_sources == 0:
        detail = "; ".join(failures[:3]) or "no feed source was reachable"
        raise nf.FeedFetchError(f"Regulatory news fetch failed for every source. {detail}")
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
        if not article_in_company_news_window(a, now, company_news_days):
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
    raw = fetch_futures_company_analyst_news(scrip, sleep_s, company=company)
    if regulatory_pool is None:
        regulatory_pool = fetch_regulatory_sector_news(sleep_s)
    raw.extend(apply_regulatory_news_for_scrip(regulatory_pool, scrip, company))
    return any(
        article_in_company_news_window(a, now, company_news_days)
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
    published: Any, now: datetime, window_days: int, title: str = ""
) -> bool:
    """Calendar-date window. window_days=2 -> today and yesterday only.

    Undated items with a company catalyst in the title (results, guidance,
    concall) count as published today so TV/RSS blurbs are not dropped.
    """
    if window_days <= 0:
        return False
    dt = parse_published(published)
    if dt is None:
        return bool(title and COMPANY_CATALYST_RE.search(title))
    pub_date = dt.date()
    cur = now.date()
    oldest = cur - timedelta(days=window_days - 1)
    return oldest <= pub_date <= cur


def _safe_date(year: int, month: int, day: int) -> date | None:
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _month_from_name(name: str) -> int:
    key = name.lower()
    if key.startswith("sept"):
        return 9
    return _MONTH_NUM[key[:3]]


def _headline_date_candidates(text: str, now: datetime) -> list[date]:
    """Parse calendar dates from a headline (India-first numeric order)."""
    if not text:
        return []
    today = now.date()
    found: list[date] = []
    seen: set[date] = set()

    def _add(d: date | None) -> None:
        if d is None or d in seen:
            return
        seen.add(d)
        found.append(d)

    def _with_years(month: int, day: int, year: int | None) -> None:
        if year:
            _add(_safe_date(year, month, day))
            return
        for y in (today.year - 1, today.year, today.year + 1):
            _add(_safe_date(y, month, day))

    for m in re.finditer(
        rf"\b(\d{{1,2}})\s+({_MONTH_NAME_RE})\.?,?\s*(\d{{4}})?\b",
        text,
        re.I,
    ):
        _with_years(
            _month_from_name(m.group(2)),
            int(m.group(1)),
            int(m.group(3)) if m.group(3) else None,
        )

    for m in re.finditer(
        rf"\b({_MONTH_NAME_RE})\s+(\d{{1,2}})(?:st|nd|rd|th)?,?\s*(\d{{4}})?\b",
        text,
        re.I,
    ):
        _with_years(
            _month_from_name(m.group(1)),
            int(m.group(2)),
            int(m.group(3)) if m.group(3) else None,
        )

    for m in re.finditer(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b", text):
        _add(_safe_date(int(m.group(1)), int(m.group(2)), int(m.group(3))))

    for m in re.finditer(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b", text):
        a, b, yraw = int(m.group(1)), int(m.group(2)), int(m.group(3))
        year = yraw + 2000 if yraw < 100 else yraw
        if a > 12:
            _add(_safe_date(year, b, a))
        elif b > 12:
            _add(_safe_date(year, a, b))
        else:
            _add(_safe_date(year, b, a))  # DMY

    return found


def headline_event_date_today_or_tomorrow(text: str, now: datetime) -> date | None:
    """Event date in the headline if it is today or tomorrow; else None."""
    if not text:
        return None
    today = now.date()
    tomorrow = today + timedelta(days=1)
    wanted = {today, tomorrow}
    for d in _headline_date_candidates(text, now):
        if d in wanted:
            return d
    text_l = text.lower()
    if re.search(r"\btomorrow\b", text_l):
        return tomorrow
    if re.search(r"\btoday\b", text_l):
        return today
    return None


def is_upcoming_corporate_event(article: dict, now: datetime) -> bool:
    """True when a board/results/dividend headline is for today or tomorrow only."""
    title = (article.get("title") or "").strip()
    summary = (article.get("summary") or "").strip()
    blob = f"{title} {summary}".strip()
    if not blob or not CORPORATE_EVENT_RE.search(blob):
        return False
    event_date = headline_event_date_today_or_tomorrow(blob, now)
    if event_date is None:
        return False
    article["event_date"] = event_date.isoformat()
    return True


def article_in_company_news_window(
    article: dict, now: datetime, window_days: int
) -> bool:
    """Published today/yesterday, or a corporate event dated today or tomorrow."""
    if is_upcoming_corporate_event(article, now):
        return True
    return is_published_within_calendar_days(
        article.get("published"),
        now,
        window_days,
        title=article.get("title") or "",
    )


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
    try:
        feed = feedparser.parse(url, request_headers=nf.RSS_REQUEST_HEADERS)
    except Exception as exc:
        raise nf.FeedFetchError(str(exc)) from exc
    failure = nf.feed_fetch_error(feed)
    if failure:
        raise nf.FeedFetchError(failure)
    items = []
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


def check_news_source_connectivity() -> None:
    """Fail before database writes when neither configured RSS path is reachable."""
    available = []
    failures = []
    try:
        nf.fetch_rss_feeds(days_back=1)
        available.append("India news tracker RSS")
    except Exception as exc:
        failures.append(f"India news tracker RSS: {exc}")
    try:
        _parse_feed(_google_rss("India stock market news"), "Google News preflight", "news")
        available.append("Google News RSS")
    except nf.FeedFetchError as exc:
        failures.append(f"Google News RSS: {exc}")
    if not available:
        detail = "; ".join(failures)
        raise nf.FeedFetchError(
            "News preflight failed: no RSS source is reachable. "
            f"Check network access before retrying. {detail}"
        )
    print("Feed preflight: reachable: " + ", ".join(available))


def scrape_scrip(
    scrip: str, industry: str, days: int, sleep_s: float, company: str = ""
) -> list[dict]:
    merged: list[dict] = []
    successful_sources = 0
    failures = []
    try:
        merged.extend(_fetch_india_rss_for_scrip(scrip, company, max(days, 7)))
        successful_sources += 1
    except SystemExit:
        pass
    except Exception as exc:
        failures.append(f"India news RSS: {exc}")
        print(f"  warn: RSS {scrip}: {exc}", file=sys.stderr)

    queries = google_news_queries(
        scrip, company, include_analyst=True, include_guidance=True, industry=industry
    )
    for url, source, kind in queries:
        try:
            merged.extend(_parse_feed(url, source, kind))
            successful_sources += 1
        except nf.FeedFetchError as exc:
            failures.append(f"{source}: {exc}")
            print(f"  warn: RSS {scrip} {source}: {exc}", file=sys.stderr)
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
            successful_sources += 1
        except Exception as exc:
            failures.append(f"Industry RSS: {exc}")
            print(f"  warn: RSS sector {industry}: {exc}", file=sys.stderr)
    if successful_sources == 0:
        detail = "; ".join(failures[:3]) or "no feed source was reachable"
        raise nf.FeedFetchError(f"All news sources failed for {scrip}. {detail}")
    return merged


def is_published_today(published: Any, now: datetime, title: str = "") -> bool:
    dt = parse_published(published)
    if dt is None:
        return bool(title and COMPANY_CATALYST_RE.search(title))
    return dt.date() == now.date()


def stored_company_news_today(doc: dict | None, now: datetime) -> bool:
    if not doc:
        return False
    items = list(doc.get("news") or [])
    for a in doc.get("articles") or []:
        if a.get("kind") == "news":
            items.append(a)
    return any(
        is_published_today(a.get("published"), now, title=a.get("title") or "")
        for a in items
    )


def fetch_company_news(scrip: str, sleep_s: float, company: str = "") -> list[dict]:
    """Company headlines only (no sectoral / analyst Google queries)."""
    merged: list[dict] = []
    successful_sources = 0
    failures = []
    try:
        merged.extend(
            _fetch_india_rss_for_scrip(scrip, company, 2, allowed_kinds={"news"})
        )
        successful_sources += 1
    except Exception as exc:
        failures.append(f"India news RSS: {exc}")
        print(f"  warn: RSS company {scrip}: {exc}", file=sys.stderr)
    queries = google_news_queries(
        scrip, company, include_analyst=False, include_guidance=True
    )
    for url, source, kind in queries:
        try:
            merged.extend(_parse_feed(url, source, kind))
            successful_sources += 1
        except nf.FeedFetchError as exc:
            failures.append(f"{source}: {exc}")
            print(f"  warn: RSS company {scrip} {source}: {exc}", file=sys.stderr)
        if sleep_s:
            time.sleep(sleep_s)
    if successful_sources == 0:
        detail = "; ".join(failures[:3]) or "no feed source was reachable"
        raise nf.FeedFetchError(f"Company news fetch failed for {scrip}. {detail}")
    return [a for a in merged if a.get("kind") == "news"]


def fetch_futures_company_analyst_news(
    scrip: str, sleep_s: float, company: str = ""
) -> list[dict]:
    """Company + analyst headlines only; no sectoral feeds."""
    merged: list[dict] = []
    successful_sources = 0
    failures = []
    try:
        merged.extend(
            _fetch_india_rss_for_scrip(
                scrip, company, 2, allowed_kinds=set(FUTURES_SCORING_KINDS)
            )
        )
        successful_sources += 1
    except Exception as exc:
        failures.append(f"India news RSS: {exc}")
        print(f"  warn: RSS futures {scrip}: {exc}", file=sys.stderr)

    queries = google_news_queries(
        scrip, company, include_analyst=True, include_guidance=True
    )
    for url, source, kind in queries:
        try:
            merged.extend(_parse_feed(url, source, kind))
            successful_sources += 1
        except nf.FeedFetchError as exc:
            failures.append(f"{source}: {exc}")
            print(f"  warn: RSS futures {scrip} {source}: {exc}", file=sys.stderr)
        if sleep_s:
            time.sleep(sleep_s)
    if successful_sources == 0:
        detail = "; ".join(failures[:3]) or "no feed source was reachable"
        raise nf.FeedFetchError(f"Company/analyst news fetch failed for {scrip}. {detail}")
    return [a for a in merged if a.get("kind") in FUTURES_SCORING_KINDS]


def has_company_news_today(
    scrip: str,
    now: datetime,
    sleep_s: float,
    stored_doc: dict | None = None,
    company: str = "",
) -> bool:
    if stored_company_news_today(stored_doc, now):
        return True
    return any(
        is_published_today(a.get("published"), now, title=a.get("title") or "")
        for a in fetch_company_news(scrip, sleep_s, company=company)
    )


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
        is_published_today(a.get("published"), now, title=a.get("title") or "")
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
    articles = fetch_company_news(scrip, sleep_s, company=company)
    return any(
        is_published_today(a.get("published"), now, title=a.get("title") or "")
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
    """Dedupe with today/yesterday published window, or event dated today/tomorrow."""
    out = []
    seen_title = set()
    seen_near = set()
    for a in articles:
        if not article_in_company_news_window(a, now, window_days):
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


def select_futures_company_news(
    articles: list[dict], min_impact: int, now: datetime | None = None
) -> list[dict]:
    """Futures skill: high-impact company + analyst headlines (no sectoral).

    Board/results/dividend items dated today or tomorrow always qualify as a write.
    """
    now = now or datetime.now()
    ranked = sorted(
        [a for a in articles if a.get("kind") in FUTURES_SCORING_KINDS],
        key=lambda a: int(a.get("impact_score") or 0),
        reverse=True,
    )
    for a in ranked:
        if is_upcoming_corporate_event(a, now):
            a["impact_score"] = max(int(a.get("impact_score") or 0), min_impact)

    def take(kind: str, n: int) -> list[dict]:
        pool = [a for a in ranked if a.get("kind") == kind]
        events = [a for a in pool if is_upcoming_corporate_event(a, now)]
        strong = [a for a in pool if int(a.get("impact_score") or 0) >= min_impact]
        if len(strong) >= 3:
            picked = events + [a for a in strong[:n] if a not in events]
            return picked[: n + len(events)]
        fallback = strong + [a for a in pool if a not in strong]
        picked = events + [a for a in fallback if a not in events]
        return picked[:n]

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


def retain_recent_stored_articles(
    existing: dict | None,
    articles: list[dict],
    news_days: int,
    now: datetime,
) -> list[dict]:
    """Keep still-fresh stored headlines when the current scrape found none."""
    if articles or not existing:
        return articles
    return dedupe_fresh(articles_from_doc(existing), news_days, now)


def futures_should_write(
    new_articles: list[dict],
    merged_articles: list[dict],
    now: datetime | None = None,
) -> bool:
    """Write on new company/analyst news, T-1/today board-results-dividend, or High-conviction regulatory."""
    if not new_articles:
        return False
    now = now or datetime.now()
    if any(is_upcoming_corporate_event(a, now) for a in new_articles):
        return True
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


def upsert_scrip(
    coll,
    scrip: str,
    industry: str,
    tables: list[str],
    articles: list[dict],
    news_days: int = DEFAULT_NEWS_DAYS,
) -> str:
    now = datetime.now()
    existing = coll.find_one({"scrip": scrip})
    articles = drop_regulatory_unless_high_conviction(articles)
    articles = articles_for_overall_sentiment(articles)
    if not articles:
        retained = retain_recent_stored_articles(existing, [], news_days, now)
        articles = articles_for_overall_sentiment(
            drop_regulatory_unless_high_conviction(retained)
        )
    if not articles and not existing:
        return "skip_empty"
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
    regulatory_pool = None
    if not args.recompute_only:
        try:
            check_news_source_connectivity()
            regulatory_pool = dedupe_fresh(
                fetch_regulatory_sector_news(args.sleep), args.news_days, now
            )
        except nf.FeedFetchError as exc:
            parser.error(str(exc))
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
    counts = {"insert": 0, "update": 0, "overwrite": 0, "skip_empty": 0}
    processed: list[dict[str, Any]] = []

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
        raw = scrape_scrip(scrip, industry, args.days, args.sleep, company=company)
        raw.extend(apply_regulatory_news_for_scrip(regulatory_pool, scrip, company))
        cleaned = select_high_impact(dedupe_fresh(raw, args.news_days, now), args.min_impact)
        scoring_cleaned = articles_for_overall_sentiment(
            drop_regulatory_unless_high_conviction(cleaned)
        )
        if not scoring_cleaned:
            existing = coll.find_one({"scrip": scrip})
            retained = retain_recent_stored_articles(existing, [], args.news_days, now)
            if retained:
                cleaned = retained
                print(
                    f"    no fresh headlines; preserving {len(cleaned)} stored item(s) "
                    f"within {args.news_days} days"
                )
        action = upsert_scrip(
            coll, scrip, industry, tables, cleaned, news_days=args.news_days
        )
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
        f"overwrite={counts['overwrite']} skip_empty={counts['skip_empty']} "
        f"purged_futures_skill={purge_count} "
        f"collection={SCAN_DB}.{TARGET_COLLECTION}"
    )
    print_news_digest(processed, skill_name="scan-news-conviction")
    client.close()


if __name__ == "__main__":
    main()
