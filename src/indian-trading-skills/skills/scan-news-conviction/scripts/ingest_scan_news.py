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
    "breakoutMHR",
    "breakoutW2HR",
    "movingavg_crossed_up",
    "breakoutY2H",
    "breakoutYH",
]
ANALYST_RE = re.compile(
    r"upgrade|downgrade|target price|analyst|outperform|underperform|"
    r"buy rating|sell rating|initiate coverage|brokerage|price target",
    re.I,
)
OVERWRITE_DAYS = 30


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


def collect_scrips(client: MongoClient, days: int) -> dict[str, dict]:
    db = client[SCAN_DB]
    found: dict[str, dict] = {}
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
            rec = found.setdefault(scrip, {"industry": "", "scan_tables": set()})
            rec["scan_tables"].add(table)
            ind = doc.get("industry")
            if ind and not rec["industry"]:
                rec["industry"] = str(ind).strip()
    return found


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
    other = [a for a in ranked if a.get("kind") not in {"news", "sectoral", "analyst"}][:4]
    combined = news + sectoral + analyst + other
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


def overall_sentiment(articles: list[dict]) -> str:
    bull = sum(1 for a in articles if a.get("sentiment") == "Bullish")
    bear = sum(1 for a in articles if a.get("sentiment") == "Bearish")
    if bull > bear and bull:
        return "Bullish"
    if bear > bull and bear:
        return "Bearish"
    if bull and bear:
        return "Mixed"
    return "Neutral"


def conviction_for(articles: list[dict], sentiment: str) -> str:
    if not articles:
        return "Low"
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


def upsert_scrip(coll, scrip: str, industry: str, tables: list[str], articles: list[dict]) -> str:
    now = datetime.now()
    sentiment = overall_sentiment(articles)
    conviction = conviction_for(articles, sentiment)
    news = [a for a in articles if a.get("kind") == "news"]
    sectoral = [a for a in articles if a.get("kind") == "sectoral"]
    analyst = [a for a in articles if a.get("kind") == "analyst"]
    payload = {
        "scrip": scrip,
        "industry": industry,
        "scan_tables": tables,
        "articles": articles,
        "news": news,
        "sectoral_news": sectoral,
        "analyst_calls": analyst,
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


def main() -> None:
    parser = argparse.ArgumentParser(description="scan-news-conviction ingest")
    parser.add_argument("--uri", default=DEFAULT_URI)
    parser.add_argument("--days", type=int, default=5, help="Scan-table lookback")
    parser.add_argument("--news-days", type=int, default=7, help="Max headline age")
    parser.add_argument("--min-impact", type=int, default=4)
    parser.add_argument("--sleep", type=float, default=0.35)
    parser.add_argument("--scrips", default="")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    now = datetime.now()
    client = MongoClient(args.uri, serverSelectionTimeoutMS=8000)
    client.admin.command("ping")
    coll = client[SCAN_DB][TARGET_COLLECTION]
    setup_indexes(coll)

    universe = collect_scrips(client, args.days)
    if args.scrips:
        want = {_norm_scrip(s) for s in args.scrips.split(",") if _norm_scrip(s)}
        universe = {k: v for k, v in universe.items() if k in want}
    scrips = sorted(universe.keys())
    if args.limit:
        scrips = scrips[: args.limit]

    print(f"Skill: scan-news-conviction")
    print(f"Scan tables: {', '.join(SCAN_TABLES)}")
    print(f"Scrips (last {args.days}d): {len(scrips)}")
    counts = {"insert": 0, "update": 0, "overwrite": 0}

    for i, scrip in enumerate(scrips, 1):
        meta = universe[scrip]
        tables = sorted(meta["scan_tables"])
        industry = meta.get("industry") or ""
        print(f"[{i}/{len(scrips)}] {scrip} ({', '.join(tables)})")
        raw = scrape_scrip(scrip, industry, args.days, args.sleep)
        cleaned = select_high_impact(dedupe_fresh(raw, args.news_days, now), args.min_impact)
        action = upsert_scrip(coll, scrip, industry, tables, cleaned)
        counts[action] = counts.get(action, 0) + 1
        sent = overall_sentiment(cleaned)
        conv = conviction_for(cleaned, sent)
        print(f"    {action}  items={len(cleaned)}  sentiment={sent}  conviction={conv}")

    print(
        f"\nDone. insert={counts['insert']} update={counts['update']} "
        f"overwrite={counts['overwrite']} collection={SCAN_DB}.{TARGET_COLLECTION}"
    )
    client.close()


if __name__ == "__main__":
    main()
