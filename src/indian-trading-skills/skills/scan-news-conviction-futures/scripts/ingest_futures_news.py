#!/usr/bin/env python3
"""All futures scrips → upsert only when new company/analyst headline today/yesterday.

Skill: scan-news-conviction-futures
Writes: Nsedata.scrip_news only
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from pymongo import MongoClient

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scan-news-conviction" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
import ingest_scan_news as ingest  # noqa: E402

DEFAULT_URI = ingest.DEFAULT_URI
SCAN_DB = ingest.SCAN_DB
TARGET_COLLECTION = ingest.TARGET_COLLECTION
SCRIP_COLLECTION = "scrip"
UNIVERSE_TAG = ingest.FUTURES_SKILL_TAG
DEFAULT_RETAIN_DAYS = ingest.DEFAULT_FUTURES_RETAIN_DAYS
DEFAULT_COMPANY_NEWS_DAYS = ingest.DEFAULT_FUTURES_COMPANY_NEWS_DAYS


def collect_futures_scrips(client: MongoClient) -> dict[str, dict]:
    found: dict[str, dict] = {}
    for doc in client[SCAN_DB][SCRIP_COLLECTION].find(
        {"futures": "Yes"},
        {"scrip": 1, "industry": 1, "company": 1, "index": 1},
    ):
        scrip = ingest._norm_scrip(doc.get("scrip"))
        if not scrip:
            continue
        rec = found.setdefault(
            scrip,
            {"industry": "", "company": "", "scan_tables": {UNIVERSE_TAG}},
        )
        rec["scan_tables"].add(UNIVERSE_TAG)
        ind = doc.get("industry")
        if ind and not rec["industry"]:
            rec["industry"] = str(ind).strip()
        comp = doc.get("company")
        if comp and not rec["company"]:
            rec["company"] = str(comp).strip()
    return found


def merge_scan_tables(existing: dict | None, extra: list[str]) -> list[str]:
    tables = set(extra)
    if existing:
        for t in existing.get("scan_tables") or []:
            if t:
                tables.add(str(t))
    return sorted(tables)


def print_summary(
    *,
    now: datetime,
    futures_count: int,
    skipped: list[str],
    processed: list[dict[str, Any]],
    errors: list[tuple[str, str]],
    counts: dict[str, int],
    purge_count: int,
    purge_scrips: list[str],
    retain_days: int,
    company_news_days: int,
) -> None:
    sent = Counter(p["sentiment"] for p in processed)
    conv = Counter(p["conviction"] for p in processed)
    high = [p for p in processed if p["conviction"] == "High"]
    directional = [
        p
        for p in processed
        if p["sentiment"] in ("Bullish", "Bearish") and p["conviction"] in ("High", "Med")
    ]

    print("\n========================================================================")
    print("SUMMARY - scan-news-conviction-futures")
    print("========================================================================")
    print(f"Ran at:              {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print("Universe:            Nsedata.scrip where futures=Yes")
    print(f"Target (only):       {SCAN_DB}.{TARGET_COLLECTION}")
    print(
        f"Update rule:         only when new company/analyst headline in last "
        f"{company_news_days} calendar days (today/yesterday) not already stored"
    )
    print(
        f"Retention purge:     delete futures-only rows older than {retain_days} days (breakout-tagged rows kept)"
    )
    print(f"Purged (expired):    {purge_count}")
    print(f"Futures scrips:      {futures_count}")
    print(f"Skipped (no new):    {len(skipped)}")
    print(f"Written insert:      {counts.get('insert', 0)}")
    print(f"Written update:      {counts.get('update', 0)}")
    print(f"Written overwrite:   {counts.get('overwrite', 0)}")
    print(f"Errors:              {len(errors)}")
    print()
    print(
        "Sentiment (processed): "
        + (", ".join(f"{k}={v}" for k, v in sorted(sent.items())) or "none")
    )
    print(
        "Conviction (processed): "
        + (", ".join(f"{k}={v}" for k, v in sorted(conv.items())) or "none")
    )

    if high:
        print("\nHigh conviction:")
        for p in high:
            print(
                f"  {p['scrip']:12} {p['action']:9} {p['sentiment']:8} items={p['items']}  {p['industry']}"
            )

    if directional:
        print("\nDirectional High/Med:")
        for p in directional:
            print(
                f"  {p['scrip']:12} {p['conviction']:4} {p['sentiment']:8} {p['action']:9} items={p['items']}"
            )

    if errors:
        print("\nErrors:")
        for scrip, err in errors:
            print(f"  {scrip}: {err}")

    if purge_scrips and len(purge_scrips) <= 40:
        print("\nPurged (futures-only, expired): " + ", ".join(purge_scrips))
    elif purge_scrips:
        print(
            f"\nPurged sample ({min(20, len(purge_scrips))} of {len(purge_scrips)}): "
            + ", ".join(purge_scrips[:20])
        )

    if skipped and len(skipped) <= 40:
        print("\nSkipped (no new today/yesterday headline): " + ", ".join(skipped))
    elif skipped:
        print(
            f"\nSkipped sample ({min(20, len(skipped))} of {len(skipped)}): "
            + ", ".join(skipped[:20])
        )

    print("========================================================================")
    ingest.print_news_digest(processed, skill_name="scan-news-conviction-futures")


def main() -> None:
    ingest._configure_stdio()
    parser = argparse.ArgumentParser(description="scan-news-conviction-futures ingest")
    parser.add_argument("--uri", default=DEFAULT_URI)
    parser.add_argument(
        "--stale-days",
        type=int,
        default=3,
        help="Unused (updates only on new today/yesterday headlines not already stored)",
    )
    parser.add_argument(
        "--retain-days",
        type=int,
        default=DEFAULT_RETAIN_DAYS,
        help="Delete futures-only scrip_news rows older than this many days (breakout-tagged rows kept)",
    )
    parser.add_argument(
        "--company-news-days",
        type=int,
        default=DEFAULT_COMPANY_NEWS_DAYS,
        help="Only write when company/analyst headlines from these calendar days are new (2 = today + yesterday)",
    )
    parser.add_argument(
        "--news-days",
        type=int,
        default=7,
        help="Unused (futures skill uses --company-news-days for headline window)",
    )
    parser.add_argument("--min-impact", type=int, default=4)
    parser.add_argument("--sleep", type=float, default=0.35)
    parser.add_argument("--scrips", default="")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    now = datetime.now()
    client = MongoClient(args.uri, serverSelectionTimeoutMS=8000)
    client.admin.command("ping")
    coll = client[SCAN_DB][TARGET_COLLECTION]
    ingest.setup_indexes(coll)

    purge_count, purge_scrips = ingest.purge_stale_futures_skill_rows(
        coll, now, args.retain_days
    )
    ingest.print_futures_skill_purge(purge_count, purge_scrips, args.retain_days)

    universe = collect_futures_scrips(client)
    if args.scrips:
        want = {ingest._norm_scrip(s) for s in args.scrips.split(",") if ingest._norm_scrip(s)}
        universe = {k: v for k, v in universe.items() if k in want}

    all_scrips = sorted(universe.keys())
    existing_by_scrip = {
        ingest._norm_scrip(d.get("scrip")): d
        for d in coll.find(
            {"scrip": {"$in": all_scrips}},
            {
                "scrip": 1,
                "insertion_date": 1,
                "updated_at": 1,
                "scan_tables": 1,
                "news": 1,
                "analyst_calls": 1,
                "articles": 1,
            },
        )
        if ingest._norm_scrip(d.get("scrip"))
    }

    due = all_scrips
    if args.limit:
        due = due[: args.limit]

    print("Skill: scan-news-conviction-futures")
    print(f"Futures scrips: {len(all_scrips)}")
    print(
        f"Write only when new company/analyst headline in last {args.company_news_days} calendar days "
        "(today/yesterday; company name in title; not already stored)"
    )
    print(
        f"Headlines: company + analyst only; title must primarily name scrip/company; no sectoral"
    )
    print(f"Candidates: {len(due)}")
    print(f"Writes only: {SCAN_DB}.{TARGET_COLLECTION}")

    counts = {"insert": 0, "update": 0, "overwrite": 0}
    processed: list[dict[str, Any]] = []
    skipped: list[str] = []
    errors: list[tuple[str, str]] = []

    for i, scrip in enumerate(due, 1):
        meta = universe[scrip]
        existing = existing_by_scrip.get(scrip)
        tables = merge_scan_tables(existing, sorted(meta["scan_tables"]))
        industry = meta.get("industry") or ""
        company = meta.get("company") or ""
        print(f"[{i}/{len(due)}] {scrip}")
        try:
            raw = ingest.fetch_futures_company_analyst_news(scrip, args.sleep)
            fresh_arts = ingest.dedupe_fresh_calendar(raw, args.company_news_days, now)
            before = len(fresh_arts)
            filtered = ingest.filter_futures_company_news(
                fresh_arts,
                scrip,
                company,
                existing,
                now,
                args.company_news_days,
            )
            dropped = before - len(filtered)
            if not filtered:
                skipped.append(scrip)
                if dropped:
                    print(
                        f"    skip: no new today/yesterday headline "
                        f"({dropped} dropped: not in title/already stored/generic)"
                    )
                else:
                    print("    skip: no new today/yesterday headline")
                continue
            if dropped:
                print(
                    f"    dropped {dropped} headline(s) (no title company name/already stored/generic)"
                )
            cleaned = ingest.select_futures_company_news(filtered, args.min_impact)
            merged = ingest.merge_stored_and_new_articles(existing, cleaned)
            action = ingest.upsert_scrip(coll, scrip, industry, tables, merged)
            counts[action] = counts.get(action, 0) + 1
            row = ingest.summary_row(scrip, industry, tables, merged, action)
            processed.append(row)
            print(
                f"    {action}  new={len(cleaned)} total={row['items']}  "
                f"sentiment={row['sentiment']}  conviction={row['conviction']}"
            )
        except Exception as exc:
            errors.append((scrip, str(exc)))
            print(f"    ERROR: {exc}", file=sys.stderr)

    print_summary(
        now=now,
        futures_count=len(all_scrips),
        skipped=skipped,
        processed=processed,
        errors=errors,
        counts=counts,
        purge_count=purge_count,
        purge_scrips=purge_scrips,
        retain_days=args.retain_days,
        company_news_days=args.company_news_days,
    )
    client.close()


if __name__ == "__main__":
    main()
