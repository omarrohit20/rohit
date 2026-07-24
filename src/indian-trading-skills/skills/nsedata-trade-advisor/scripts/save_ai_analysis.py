#!/usr/bin/env python3
"""Save high-conviction multi-horizon suggestions into Nsedata.ai-analysis.

Horizons persisted (separate logical tables via `horizon` field):
  - swing3_5   → 3–5 days
  - short_term → short-term (1–20 days)
  - long_term  → long-term / investment

Rules:
  - High conviction only, top 2 per horizon per source table
  - Store sentiment, conviction, probability_score
  - Store entry, targets (t1/t2/t3), stoploss, risk_reward
  - Attach last 5 trading days (skip weekends / NSE holidays / zero-volume)
  - Skip insert when dedupe_key already exists

Examples:
  python skills/nsedata-trade-advisor/scripts/save_ai_analysis.py \\
    --db Nsedata --collection highBuy --limit 25

  python skills/nsedata-trade-advisor/scripts/save_ai_analysis.py \\
    --db chartlink --collections buy_all_processor,morning-volume-breakout-buy

  python skills/nsedata-trade-advisor/scripts/save_ai_analysis.py \\
    --raw-json path/to/scan_docs.json --source-table manual_raw
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from pymongo import ASCENDING, MongoClient
from pymongo.errors import DuplicateKeyError

# Reuse scoring from sibling module
sys.path.insert(0, str(Path(__file__).resolve().parent))
import query_suggestions as qs  # noqa: E402

DEFAULT_URI = "mongodb://localhost:27017"
TARGET_DB = "Nsedata"
TARGET_COLLECTION = "ai-analysis"

HORIZON_META = {
    "swing3_5": {
        "label": "3-5 days",
        "table_name": "ai-analysis-3-5-days",
    },
    "short_term": {
        "label": "short-term",
        "table_name": "ai-analysis-short-term",
    },
    "long_term": {
        "label": "long-term",
        "table_name": "ai-analysis-long-term",
    },
}

# NSE holidays (common market holidays 2024–2027). Extend as needed.
# History docs usually omit holidays already; this is a safety filter.
NSE_HOLIDAYS = {
    # 2024
    "2024-01-26",
    "2024-03-08",
    "2024-03-25",
    "2024-03-29",
    "2024-04-11",
    "2024-04-17",
    "2024-05-01",
    "2024-06-17",
    "2024-07-17",
    "2024-08-15",
    "2024-10-02",
    "2024-11-01",
    "2024-11-15",
    "2024-12-25",
    # 2025
    "2025-02-26",
    "2025-03-14",
    "2025-03-31",
    "2025-04-10",
    "2025-04-14",
    "2025-04-18",
    "2025-05-01",
    "2025-08-15",
    "2025-08-27",
    "2025-10-02",
    "2025-10-21",
    "2025-10-22",
    "2025-11-05",
    "2025-12-25",
    # 2026
    "2026-01-26",
    "2026-03-03",
    "2026-03-26",
    "2026-03-31",
    "2026-04-03",
    "2026-04-14",
    "2026-05-01",
    "2026-05-28",
    "2026-06-26",
    "2026-08-15",
    "2026-09-14",
    "2026-10-02",
    "2026-10-20",
    "2026-11-08",
    "2026-11-09",
    "2026-11-24",
    "2026-12-25",
    # 2027 (partial known)
    "2027-01-26",
    "2027-03-22",
    "2027-04-14",
    "2027-05-01",
    "2027-08-15",
    "2027-10-02",
    "2027-12-25",
}


def ensure_ai_analysis_collection(client: MongoClient) -> Any:
    """Create Nsedata.ai-analysis + unique dedupe index if missing."""
    db = client[TARGET_DB]
    names = db.list_collection_names()
    if TARGET_COLLECTION not in names:
        db.create_collection(TARGET_COLLECTION)
        print(f"Created collection {TARGET_DB}.{TARGET_COLLECTION}")
    else:
        print(f"Collection exists: {TARGET_DB}.{TARGET_COLLECTION}")

    coll = db[TARGET_COLLECTION]
    # Unique identity: same horizon+source+symbol+analysis_date → skip
    coll.create_index(
        [
            ("dedupe_key", ASCENDING),
        ],
        unique=True,
        name="uniq_dedupe_key",
    )
    coll.create_index(
        [
            ("horizon", ASCENDING),
            ("source_table", ASCENDING),
            ("analysis_date", ASCENDING),
            ("rank", ASCENDING),
        ],
        name="idx_horizon_table_date_rank",
    )
    coll.create_index(
        [("symbol", ASCENDING), ("horizon", ASCENDING), ("analysis_date", ASCENDING)],
        name="idx_symbol_horizon_date",
    )
    coll.create_index([("table_name", ASCENDING), ("analysis_date", ASCENDING)], name="idx_table_date")
    coll.create_index([("date", ASCENDING), ("insertion_date", ASCENDING)], name="idx_source_date_insertion")
    return coll


def _bar_date_str(bar: dict) -> str | None:
    raw = bar.get("date")
    if raw is None:
        return None
    text = str(raw)[:10]
    try:
        datetime.strptime(text, "%Y-%m-%d")
        return text
    except ValueError:
        return None


def is_trading_day(day: str) -> bool:
    """True if weekday and not in NSE holiday set."""
    try:
        d = datetime.strptime(day, "%Y-%m-%d").date()
    except ValueError:
        return False
    if d.weekday() >= 5:  # Sat/Sun
        return False
    if day in NSE_HOLIDAYS:
        return False
    return True


def last_n_trading_days(daily: list[dict], n: int = 5) -> list[dict]:
    """Return last N trading sessions from chronological daily bars.

    Ignores weekends, NSE holidays, and zero/negative volume bars.
    """
    out: list[dict] = []
    for bar in reversed(daily):
        day = _bar_date_str(bar)
        if not day or not is_trading_day(day):
            continue
        vol = qs._safe_float(bar.get("volume"))
        if vol <= 0:
            continue
        out.append(
            {
                "date": day,
                "open": qs.round_tick(qs._safe_float(bar["open"])),
                "high": qs.round_tick(qs._safe_float(bar["high"])),
                "low": qs.round_tick(qs._safe_float(bar["low"])),
                "close": qs.round_tick(qs._safe_float(bar["close"])),
                "volume": int(vol),
            }
        )
        if len(out) >= n:
            break
    out.reverse()  # chronological
    return out


def analysis_date_from_bars(bars: list[dict], fallback: str | None = None) -> str:
    if bars:
        return bars[-1]["date"]
    return fallback or date.today().isoformat()


def normalize_table_date(value: Any) -> str:
    """Normalize scan-table date/eventtime to YYYY-MM-DD, else 'NA'."""
    if value is None:
        return "NA"
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    text = str(value).strip()
    if not text or text.lower() in {"none", "null", "nan", "na"}:
        return "NA"
    # ISO datetime / date
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%Y%m%d"):
        try:
            sample = text[:10] if fmt != "%Y%m%d" else text[:8]
            return datetime.strptime(sample, fmt).date().isoformat()
        except ValueError:
            continue
    return "NA"


def make_dedupe_key(
    horizon: str,
    source_db: str,
    source_table: str,
    symbol: str,
    table_date: str,
) -> str:
    # Prefer source-table date; NA still unique per insert day via insertion handled separately
    return f"{horizon}|{source_db}|{source_table}|{symbol}|{table_date}"


def build_doc(
    *,
    horizon: str,
    source_db: str,
    source_table: str,
    rank: int,
    row: dict,
    daily: list[dict],
) -> dict:
    meta = HORIZON_META[horizon]
    trading_5 = last_n_trading_days(daily, 5)
    last_bar_date = analysis_date_from_bars(trading_5)
    # Date from source scan table (date / eventtime); NA if missing
    table_date = normalize_table_date(row.get("date"))
    symbol = row["scrip"]
    stop = row.get("stop")
    if stop is None:
        stop = row.get("invalidation")
    targets = {
        "t1": row.get("t1"),
        "t2": row.get("t2"),
        "t3": row.get("t3"),  # short-term may have t3
    }
    # Drop null t3 for cleaner docs on swing
    if targets.get("t3") is None:
        targets.pop("t3", None)

    inserted_at = datetime.now()
    insertion_date = inserted_at.date().isoformat()
    insertion_datetime = inserted_at.isoformat(timespec="seconds")

    # Dedupe on table date when present; if NA, include insertion_date so same-day re-runs skip
    dedupe_date = table_date if table_date != "NA" else insertion_date

    return {
        "horizon": horizon,
        "horizon_label": meta["label"],
        "table_name": meta["table_name"],
        "source_db": source_db,
        "source_table": source_table,
        "symbol": symbol,
        "industry": row.get("industry"),
        # Source scan-table date (required field)
        "date": table_date,
        # When this document was inserted
        "insertion_date": insertion_date,
        "insertion_datetime": insertion_datetime,
        # Last trading bar date from history (informational)
        "analysis_date": last_bar_date,
        "rank": rank,
        "conviction": row.get("conviction"),
        "sentiment": row.get("sentiment"),
        "probability_score": row.get("probability_score"),
        "score": row.get("score"),
        "bias": row.get("bias"),
        "close": row.get("close"),
        "entry": row.get("entry"),
        "targets": targets,
        "stoploss": stop,
        "risk_reward": row.get("rr"),
        "why_hint": row.get("why_hint"),
        "notes": row.get("notes"),
        "last_5_trading_days": trading_5,
        "dedupe_key": make_dedupe_key(horizon, source_db, source_table, symbol, dedupe_date),
        "created_at": insertion_datetime,  # alias of insertion_datetime
    }


def high_conviction_top2(ranked: list[dict]) -> list[dict]:
    highs = [r for r in ranked if (r.get("conviction") or "").lower() == "high"]
    return highs[:2]


def analyze_scans(
    client: MongoClient,
    scans: list[dict],
) -> list[dict]:
    horizons = {"swing3_5", "short_term", "long_term"}
    results = []
    for scan in scans:
        analyzed = qs.analyze_candidate(client, scan, horizons)
        if analyzed:
            results.append(analyzed)
    return results


def persist_for_source(
    client: MongoClient,
    coll: Any,
    source_db: str,
    source_table: str,
    scans: list[dict],
    dry_run: bool = False,
) -> dict[str, Any]:
    results = analyze_scans(client, scans)
    summary: dict[str, Any] = {
        "source": f"{source_db}.{source_table}",
        "scanned": len(scans),
        "analyzed": len(results),
        "horizons": {},
    }

    for horizon in HORIZON_META:
        ranked = qs.rank_horizon(results, horizon, top_n=20)
        top2 = high_conviction_top2(ranked)
        inserted = 0
        skipped = 0
        docs_out = []
        for i, row in enumerate(top2, start=1):
            enrich = qs.enrich_symbol(client, row["scrip"])
            doc = build_doc(
                horizon=horizon,
                source_db=source_db,
                source_table=source_table,
                rank=i,
                row=row,
                daily=enrich["daily"],
            )
            docs_out.append(
                {
                    "symbol": doc["symbol"],
                    "date": doc["date"],
                    "insertion_date": doc["insertion_date"],
                    "conviction": doc["conviction"],
                    "sentiment": doc["sentiment"],
                    "probability_score": doc["probability_score"],
                    "entry": doc["entry"],
                    "targets": doc["targets"],
                    "stoploss": doc["stoploss"],
                    "risk_reward": doc["risk_reward"],
                    "dedupe_key": doc["dedupe_key"],
                }
            )
            if dry_run:
                continue
            existing = coll.find_one({"dedupe_key": doc["dedupe_key"]}, {"_id": 1})
            if existing:
                skipped += 1
                continue
            try:
                coll.insert_one(doc)
                inserted += 1
            except DuplicateKeyError:
                skipped += 1

        summary["horizons"][horizon] = {
            "table_name": HORIZON_META[horizon]["table_name"],
            "high_conviction_candidates": len(
                [r for r in ranked if (r.get("conviction") or "").lower() == "high"]
            ),
            "top2": docs_out,
            "inserted": inserted,
            "skipped_existing": skipped,
        }
    return summary


def last_n_calendar_cutoff(n_trading_days: int = 5) -> str:
    """Approximate cutoff date string covering ~n trading days (skip weekends/holidays)."""
    d = date.today()
    kept = 0
    guard = 0
    cutoff = d
    while kept < n_trading_days and guard < 40:
        day = d.isoformat()
        if is_trading_day(day):
            kept += 1
            cutoff = d
        d = d - timedelta(days=1)
        guard += 1
    return cutoff.isoformat()

def filter_scans_last_trading_days(scans: list[dict], n_trading_days: int = 5) -> list[dict]:
    """Keep scan rows whose date/eventtime falls in the last N trading days."""
    if n_trading_days <= 0 or not scans:
        return scans
    # Collect distinct trading dates present in the scan set (newest first)
    date_set: set[str] = set()
    for s in scans:
        nd = normalize_table_date(s.get("date") or s.get("eventtime"))
        if nd != "NA" and is_trading_day(nd):
            date_set.add(nd)
    if not date_set:
        # Fallback: calendar cutoff when scan dates are missing/unparseable
        cutoff = last_n_calendar_cutoff(n_trading_days)
        out = []
        for s in scans:
            nd = normalize_table_date(s.get("date") or s.get("eventtime"))
            if nd == "NA" or nd >= cutoff:
                out.append(s)
        return out

    recent = sorted(date_set, reverse=True)[:n_trading_days]
    allowed = set(recent)
    return [
        s
        for s in scans
        if normalize_table_date(s.get("date") or s.get("eventtime")) in allowed
    ]


def fetch_scans_for_collection(
    client: MongoClient,
    db_name: str,
    collection: str,
    limit: int,
    last_trading_days: int = 0,
) -> list[dict]:
    """Fetch scan docs; optionally filter to last N trading days of table dates.

    When filtering by trading days, pull a larger window first so the date filter
    has enough rows (limit applies after filter, newest first).
    """
    pull = limit
    if last_trading_days and last_trading_days > 0:
        pull = max(limit * 8, 200)
    scans = qs.fetch_scan_docs(client, db_name, collection, pull)
    if last_trading_days and last_trading_days > 0:
        before = len(scans)
        scans = filter_scans_last_trading_days(scans, last_trading_days)
        print(
            f"  date filter last {last_trading_days} trading days: "
            f"{before} -> {len(scans)} docs"
        )
    if limit and len(scans) > limit:
        scans = scans[:limit]
    return scans


def load_raw_scans(path: str) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict) and "candidates" in data:
        # Accept query_suggestions report shape
        rows = []
        for c in data["candidates"]:
            row = c.get("scan_row") or c
            rows.append(row)
        return rows
    if isinstance(data, dict) and "scans" in data:
        return list(data["scans"])
    if isinstance(data, list):
        return data
    raise ValueError("raw JSON must be a list of scan docs, or {scans:[...]} / report candidates")


def parse_collections(args: argparse.Namespace) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    if args.collections:
        for item in args.collections.split(","):
            item = item.strip()
            if not item:
                continue
            db_name, coll = qs.parse_db_collection(args.db, item)
            pairs.append((db_name, coll))
    elif args.collection:
        pairs.append(qs.parse_db_collection(args.db, args.collection))
    return pairs


def main() -> int:
    parser = argparse.ArgumentParser(description="Persist high-conviction AI analysis to Mongo")
    parser.add_argument("--uri", default=DEFAULT_URI)
    parser.add_argument("--db", default="Nsedata", help="Source database for scan tables")
    parser.add_argument("--collection", help="Single source scan collection")
    parser.add_argument(
        "--collections",
        help="Comma-separated source collections (e.g. highBuy,breakoutMH)",
    )
    parser.add_argument("--limit", type=int, default=25, help="Max scan docs per source table")
    parser.add_argument(
        "--last-trading-days",
        type=int,
        default=0,
        help="Keep only scan rows from the last N trading days of table dates (0=off)",
    )
    parser.add_argument(
        "--raw-json",
        help="Path to raw scan docs JSON (bypasses Mongo source table fetch)",
    )
    parser.add_argument(
        "--source-table",
        default="raw",
        help="Label stored as source_table when using --raw-json",
    )
    parser.add_argument(
        "--setup-only",
        action="store_true",
        help="Only create ai-analysis collection + indexes",
    )
    parser.add_argument("--dry-run", action="store_true", help="Score and print; do not insert")
    parser.add_argument("--output", help="Write summary JSON to file")
    args = parser.parse_args()

    client = MongoClient(args.uri, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
    except Exception as exc:  # noqa: BLE001
        print(f"Cannot connect to MongoDB at {args.uri}: {exc}", file=sys.stderr)
        return 1

    coll = ensure_ai_analysis_collection(client)
    if args.setup_only:
        print("Setup complete.")
        return 0

    summaries = []
    if args.raw_json:
        scans = load_raw_scans(args.raw_json)
        if args.last_trading_days and args.last_trading_days > 0:
            before = len(scans)
            scans = filter_scans_last_trading_days(scans, args.last_trading_days)
            print(
                f"  date filter last {args.last_trading_days} trading days: "
                f"{before} -> {len(scans)} docs"
            )
        db_name = args.db
        source_table = args.source_table
        print(f"Loaded {len(scans)} raw scan docs as {db_name}.{source_table}")
        summaries.append(
            persist_for_source(client, coll, db_name, source_table, scans, dry_run=args.dry_run)
        )
    else:
        pairs = parse_collections(args)
        if not pairs:
            print("Provide --collection / --collections or --raw-json", file=sys.stderr)
            return 2
        for db_name, collection in pairs:
            if collection not in client[db_name].list_collection_names():
                print(f"Skip missing collection {db_name}.{collection}", file=sys.stderr)
                continue
            scans = fetch_scans_for_collection(
                client,
                db_name,
                collection,
                args.limit,
                last_trading_days=args.last_trading_days,
            )
            print(f"Fetched {len(scans)} from {db_name}.{collection}")
            summaries.append(
                persist_for_source(
                    client, coll, db_name, collection, scans, dry_run=args.dry_run
                )
            )

    report = {
        "target": f"{TARGET_DB}.{TARGET_COLLECTION}",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "dry_run": args.dry_run,
        "last_trading_days": args.last_trading_days or None,
        "logical_tables": {h: m["table_name"] for h, m in HORIZON_META.items()},
        "results": summaries,
        "disclaimer": "Educational analysis only — not SEBI-registered advice.",
    }
    text = json.dumps(report, indent=2, default=str)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
