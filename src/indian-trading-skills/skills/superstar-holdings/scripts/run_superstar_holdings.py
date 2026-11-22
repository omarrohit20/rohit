#!/usr/bin/env python3
"""Track celebrity (superstar) investor holdings from NSE shareholding filings.

Writes Nsedata.superstar_holdings (current state per stock and investor),
superstar_holdings_history (one row per stock, investor and quarter),
superstar_scan_state (which quarters were read per stock) and superstar_runs.

Repeat runs are cheap: a stock is re-checked only when a newer quarter can exist,
and NSE responses are cached in Nsedata.nse_shareholding_cache.

Examples:
  python skills/superstar-holdings/scripts/run_superstar_holdings.py
  python skills/superstar-holdings/scripts/run_superstar_holdings.py --symbols RADICO,VIKASLIFE
"""

from __future__ import annotations

import argparse
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

try:
    from pymongo import MongoClient, UpdateOne
except ImportError:
    print("pymongo is required: pip install pymongo", file=sys.stderr)
    sys.exit(1)

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
IDEAS_DIR = SKILL_DIR.parent / "investment-ideas" / "scripts"
sys.path.insert(0, str(IDEAS_DIR))

import run_investment_ideas as ii  # noqa: E402  (also puts query_suggestions on sys.path)

qs = ii.qs

DEFAULT_URI = "mongodb://localhost:27017"
DB_NAME = "Nsedata"
COLL_STATE = "superstar_holdings"
COLL_HISTORY = "superstar_holdings_history"
COLL_SCAN = "superstar_scan_state"
COLL_RUNS = "superstar_runs"
INVESTORS_FILE = SKILL_DIR / "references" / "investors.md"
LOG_FILE = SKILL_DIR / "output" / "run.log"

# Quarters kept per stock when classifying (2 years).
MAX_QUARTERS = 8
# Statuses
NEW = "NEW"
NEW_DEAL = "NEW_DEAL"
INCREASED = "INCREASED"
UNCHANGED = "UNCHANGED"
DECREASED = "DECREASED"
EXITED = "EXITED_OR_BELOW_1PCT"
HOLDING = "HOLDING"  # only one quarter read, so no change can be measured
ACTIVE = {NEW, NEW_DEAL, INCREASED, UNCHANGED, DECREASED, HOLDING}
SCREENER_STATUSES = {NEW, NEW_DEAL, INCREASED}
SCREENER_MAX_AGE = timedelta(days=30)
TOP_ROWS = 10


# --------------------------------------------------------------------------- pure logic


def last_quarter_end(today: date) -> date:
    """Most recent calendar quarter end on or before today."""
    for month, day in ((12, 31), (9, 30), (6, 30), (3, 31)):
        end = date(today.year, month, day)
        if end <= today:
            return end
    return date(today.year - 1, 12, 31)


def needs_check(state: dict | None, today: date, recheck_days: int, refresh: bool) -> bool:
    """Skip a stock whose newest possible quarter is already read, or that was checked recently."""
    if refresh or not state:
        return True
    last = ii.parse_date(state.get("last_quarter"))
    if last and last >= last_quarter_end(today):
        return False
    checked = state.get("checked_at")
    if isinstance(checked, datetime) and datetime.now() - checked < timedelta(days=recheck_days):
        return False
    return True


def _r2(value: float | None) -> float | None:
    return None if value is None else round(float(value), 2)


def classify(series: list[tuple[str, float | None]]) -> dict | None:
    """Classify one investor in one stock.

    `series` is every quarter read for the stock, oldest first, as (ISO date, pct).
    pct is None when the investor was not a named holder (>1%) that quarter.
    Returns None when the investor never held the stock.
    """
    series = sorted(series, key=lambda item: item[0])[-MAX_QUARTERS:]
    present = [(q, p) for q, p in series if p is not None and p > 0]
    if not present:
        return None
    max_quarter, max_pct = max(present, key=lambda item: (item[1], item[0]))
    latest_q, latest = series[-1]
    prev = series[-2][1] if len(series) >= 2 else None
    last_held_q, last_held = present[-1]

    ups = 0
    for (_, before), (_, after) in zip(reversed(series[:-1]), reversed(series)):
        if before is None or after is None or round(after, 2) <= round(before, 2):
            break
        ups += 1

    out: dict[str, Any] = {
        "latest_pct": _r2(latest) if latest else 0.0,
        "prev_pct": _r2(prev),
        "max_pct": _r2(max_pct),
        "max_quarter": max_quarter,
        "first_seen_quarter": present[0][0],
        "as_of_quarter": latest_q,
        "last_held_quarter": last_held_q,
        "last_held_pct": _r2(last_held),
        "quarters_read": len(series),
        "consecutive_increases": ups,
    }
    if not latest:
        out["status"] = EXITED
        out["change_pct"] = _r2(-(prev or last_held))
        out["drop_from_max_pct"] = _r2(max_pct)
        out["below_max"] = True
        return out
    if len(series) == 1:
        status = HOLDING
        change = 0.0
    elif not prev:
        status = NEW
        change = latest
    else:
        change = latest - prev
        if round(change, 2) > 0:
            status = INCREASED
        elif round(change, 2) < 0:
            status = DECREASED
        else:
            status = UNCHANGED
    drop = max(0.0, max_pct - latest)
    out.update(
        {
            "status": status,
            "change_pct": _r2(change),
            "drop_from_max_pct": _r2(drop),
            "below_max": round(drop, 2) > 0,
        }
    )
    return out


def score_conviction(
    row: dict,
    investor: str,
    holders: int,
    price: dict | None,
    news: dict | None,
    deal: dict | None,
    pros: list[str] | None,
) -> dict:
    """Rule-based conviction (no LLM) and a one-line `why` for a holding."""
    points = 0
    reasons: list[tuple[int, str]] = []  # (weight, text)
    status = row.get("status")
    latest, prev = row.get("latest_pct"), row.get("prev_pct")
    q = str(row.get("as_of_quarter") or "")[:7]

    if status in (NEW, NEW_DEAL):
        points += 2
        reasons.append((3, f"{investor} new buy {ii.pct_text(latest)}" + (f" ({q})" if q else "")))
    elif status == INCREASED:
        points += 2 + (1 if row.get("consecutive_increases", 0) >= 2 else 0)
        ups = row.get("consecutive_increases", 0)
        streak = f", {ups} qtrs up" if ups >= 2 else ""
        reasons.append((3, f"{investor} raised {ii.pct_text(prev)}→{ii.pct_text(latest)}{streak}"))
    elif status in (UNCHANGED, HOLDING):
        points += 1
        reasons.append((1, f"{investor} holds {ii.pct_text(latest)}"))
    elif status == DECREASED:
        points -= 2
        reasons.append((3, f"{investor} cut {ii.pct_text(prev)}→{ii.pct_text(latest)}"))
    elif status == EXITED:
        points -= 3
        reasons.append((3, f"{investor} exited or below 1% (was {ii.pct_text(row.get('last_held_pct'))})"))

    if status in ACTIVE and (latest or 0) >= 5:
        points += 1
        reasons.append((2, f"large stake {ii.pct_text(latest)}"))

    if status in ACTIVE and row.get("below_max") and (row.get("max_pct") or 0) > 0:
        drop_share = (row.get("drop_from_max_pct") or 0) / row["max_pct"]
        if drop_share >= 0.33:
            points -= 1
        reasons.append((1, f"{ii.pct_text(row.get('drop_from_max_pct'))} below peak {ii.pct_text(row.get('max_pct'))}"))

    if holders >= 3:
        points += 2
        reasons.append((2, f"{holders} celebrities hold"))
    elif holders == 2:
        points += 1
        reasons.append((2, "2 celebrities hold"))

    if deal:
        if deal["side"] == "BUY":
            points += 2
        else:
            points -= 2
        reasons.append((3, deal["text"]))

    if price:
        conv, sent = price.get("conviction"), price.get("sentiment")
        if sent == "Bullish":
            points += 2 if conv == "High" else 1 if conv == "Med" else 0
        elif sent == "Bearish":
            points -= 1
        if sent:
            reasons.append((1, f"price {sent} ({conv}, {price.get('probability_score')}%)"))

    if news:
        sent = news.get("news_sentiment")
        if sent == "Bullish":
            points += 1
        elif sent == "Bearish":
            points -= 1
        if news.get("news_headline"):
            reasons.append((1, f"news {sent}: {news['news_headline'][:80]}"))

    if pros:
        reasons.append((1, pros[0][:80]))

    conviction = "High" if points >= 5 else "Med" if points >= 3 else "Low"
    sentiment = "Bullish" if points >= 3 else "Bearish" if points <= 0 else "Neutral"
    ordered = [text for _, text in sorted(reasons, key=lambda item: -item[0])]
    return {
        "conviction": conviction,
        "sentiment": sentiment,
        "conviction_points": points,
        "why": "; ".join(ordered[:5]),
    }


def match_investor(rows: list[dict], variants: list[str]) -> tuple[float | None, list[str]]:
    """Total % held by an investor across matching named holders, with the matched names."""
    total = 0.0
    names: list[str] = []
    for row in rows:
        blob = " ".join(str(row.get(k) or "") for k in ("shareholderName", "nameOfPAC", "COL_I", "COL_II"))
        if not any(ii.names_match(blob, variant) for variant in variants):
            continue
        parsed = ii.holder_name_and_pct(row)
        if not parsed:
            continue
        names.append(parsed[0])
        total += parsed[1]
    return (total if names else None), names


def match_deal_client(client: str, investors: list[tuple[str, list[str]]]) -> str | None:
    for canonical, variants in investors:
        if any(ii.names_match(client, variant) for variant in variants):
            return canonical
    return None


def mcap_bucket(crores: float | None) -> str:
    if not crores:
        return "unknown"
    if crores < 5000:
        return "smallcap"
    if crores <= 20000:
        return "midcap"
    return "largecap"


# --------------------------------------------------------------------------- run


@dataclass
class Stats:
    extra: Counter = field(default_factory=Counter)  # store_deal_snapshot writes here
    checked: int = 0
    fetched_quarters: int = 0
    symbols_changed: int = 0
    changes: Counter = field(default_factory=Counter)
    changed_rows: list = field(default_factory=list)


class Log:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.fh = path.open("a", encoding="utf-8")

    def __call__(self, msg: str) -> None:
        self.fh.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} {msg}\n")
        self.fh.flush()


def ensure_indexes(db) -> None:
    db[COLL_STATE].create_index("key", unique=True)
    db[COLL_STATE].create_index("scrip")
    db[COLL_HISTORY].create_index("key", unique=True)
    db[COLL_HISTORY].create_index("scrip")
    db[COLL_SCAN].create_index("scrip", unique=True)
    db[ii.NSE_CACHE_COLL].create_index("path", unique=True)


def load_universe(db, symbols: list[str] | None, limit: int | None) -> dict[str, dict]:
    caps = ii.fundamental_caps(db)
    out: dict[str, dict] = {}
    for doc in db["scrip"].find({}, {"_id": 0, "scrip": 1, "company": 1, "industry": 1, "marketcap": 1}):
        sym = str(doc.get("scrip") or "").strip().upper()
        if not sym or (symbols and sym not in symbols):
            continue
        crores = ii.to_crores(doc.get("marketcap")) or caps.get(sym)
        out[sym] = {
            "company": doc.get("company") or sym,
            "industry": doc.get("industry") or "",
            "marketcap": round(crores, 2) if crores else None,
        }
    for sym in symbols or []:  # symbols not in Nsedata.scrip still get checked
        out.setdefault(sym, {"company": sym, "industry": "", "marketcap": caps.get(sym)})
    if limit:
        out = dict(list(sorted(out.items()))[:limit])
    return out


def fetch_symbol(db, nse, sym: str, state: dict | None, investors, backfill: int, stats: Stats, log) -> bool:
    """Read new quarters for one stock. Returns True when history changed."""
    quarters = ii.quarter_records(nse.get_json(ii.nse_symbol_path(sym)))
    now = datetime.now()
    if not quarters:
        db[COLL_SCAN].update_one(
            {"scrip": sym}, {"$set": {"scrip": sym, "checked_at": now, "no_filing": True}}, upsert=True
        )
        return False
    scanned = set((state or {}).get("quarters_scanned") or [])
    wanted = [(d, row) for d, row in quarters[:backfill] if d.isoformat() not in scanned]
    if not wanted:
        db[COLL_SCAN].update_one({"scrip": sym}, {"$set": {"checked_at": now}}, upsert=True)
        return False
    ops = []
    for qdate, row in wanted:
        named = ii.named_public_holders(nse, sym, str(row.get("recordId")))
        stats.fetched_quarters += 1
        q = qdate.isoformat()
        for canonical, variants in investors:
            pct, names = match_investor(named, variants)
            if pct is None or pct <= 0:
                continue
            ops.append(
                UpdateOne(
                    {"key": f"{sym}|{canonical}|{q}"},
                    {
                        "$set": {
                            "key": f"{sym}|{canonical}|{q}",
                            "scrip": sym,
                            "investor_name": canonical,
                            "quarter": q,
                            "pct": round(pct, 2),
                            "matched_holder_names": names,
                            "fetched_at": now,
                        }
                    },
                    upsert=True,
                )
            )
        scanned.add(q)
    if ops:
        db[COLL_HISTORY].bulk_write(ops, ordered=False)
    latest = max(scanned)
    db[COLL_SCAN].update_one(
        {"scrip": sym},
        {
            "$set": {
                "scrip": sym,
                "quarters_scanned": sorted(scanned)[-MAX_QUARTERS * 2 :],
                "last_quarter": latest,
                "checked_at": now,
                "no_filing": False,
            }
        },
        upsert=True,
    )
    log(f"{sym}: read {len(wanted)} quarter(s), {len(ops)} celebrity row(s)")
    return True


def rebuild_symbol(db, sym: str, run_id: str, info: dict, stats: Stats) -> None:
    """Recompute superstar_holdings rows for one stock from history."""
    scan = db[COLL_SCAN].find_one({"scrip": sym}) or {}
    quarters = sorted(scan.get("quarters_scanned") or [])[-MAX_QUARTERS:]
    if not quarters:
        return
    by_investor: dict[str, dict[str, float]] = defaultdict(dict)
    for doc in db[COLL_HISTORY].find({"scrip": sym, "quarter": {"$in": quarters}}):
        by_investor[doc["investor_name"]][doc["quarter"]] = doc["pct"]
    rows = {}
    for investor, pcts in by_investor.items():
        result = classify([(q, pcts.get(q)) for q in quarters])
        if result:
            rows[investor] = result
    existing = {d["investor_name"]: d for d in db[COLL_STATE].find({"scrip": sym})}
    holders = sum(1 for r in rows.values() if r["status"] in ACTIVE) + sum(
        1 for inv, d in existing.items() if inv not in rows and d.get("status") == NEW_DEAL
    )
    now = datetime.now()
    for investor, row in rows.items():
        old = existing.get(investor) or {}
        changed = old.get("status") != row["status"] or old.get("as_of_quarter") != row["as_of_quarter"]
        doc = {
            "key": f"{sym}|{investor}",
            "scrip": sym,
            "company": info.get("company") or sym,
            "industry": info.get("industry") or "",
            "marketcap": info.get("marketcap"),
            "marketcap_bucket": mcap_bucket(info.get("marketcap")),
            "investor_name": investor,
            "investors_holding_count": holders,
            "source": "nse-shareholding",
            "updated_at": now,
            **row,
        }
        if changed:
            doc["changed_run_id"] = run_id
            doc["changed_at"] = now
            doc["prev_status"] = old.get("status")
            stats.changes[row["status"]] += 1
            stats.changed_rows.append(doc)
        db[COLL_STATE].update_one({"key": doc["key"]}, {"$set": doc}, upsert=True)
    # Every celebrity in this stock shares the same holder count.
    db[COLL_STATE].update_many({"scrip": sym}, {"$set": {"investors_holding_count": holders}})


def apply_deals(db, investors, days: int, run_id: str, universe: dict, stats: Stats) -> dict:
    """Celebrity bulk/block deals from Nsedata.nse_large_deals -> deal_signal on holdings."""
    since = (date.today() - timedelta(days=days)).isoformat()
    groups: dict[tuple[str, str], dict] = {}
    for row in db[ii.DEALS_COLL].find({"date": {"$gte": since}}):
        who = match_deal_client(str(row.get("client") or ""), investors)
        if not who:
            continue
        g = groups.setdefault((row["symbol"], who), {"net": 0.0, "value": 0.0, "qty": 0.0, "date": "", "types": set()})
        sign = 1 if row["side"] == "BUY" else -1
        g["net"] += sign * row["qty"]
        g["qty"] += row["qty"]
        g["value"] += row["qty"] * (row.get("price") or 0)
        g["date"] = max(g["date"], row["date"])
        g["types"].add(row["deal_type"])
    deals: dict[tuple[str, str], dict] = {}
    now = datetime.now()
    for (sym, who), g in groups.items():
        if not g["net"]:
            continue
        side = "BUY" if g["net"] > 0 else "SELL"
        avg = g["value"] / g["qty"] if g["qty"] and g["value"] else None
        at = f" @ {qs.round_tick(avg)}" if avg else ""
        text = f"{side} {abs(g['net']):,.0f} sh{at} on {g['date']} ({'/'.join(sorted(g['types']))})"
        deals[(sym, who)] = {"side": side, "text": text, "date": g["date"]}
        key = f"{sym}|{who}"
        found = db[COLL_STATE].find_one({"key": key}, {"_id": 0, "status": 1, "deal_signal": 1})
        if found:
            if found.get("deal_signal") != text:
                db[COLL_STATE].update_one({"key": key}, {"$set": {"deal_signal": text, "deal_date": g["date"]}})
            continue
        if side != "BUY":
            continue
        info = universe.get(sym) or {}
        doc = {
            "key": key,
            "scrip": sym,
            "company": info.get("company") or sym,
            "industry": info.get("industry") or "",
            "marketcap": info.get("marketcap"),
            "marketcap_bucket": mcap_bucket(info.get("marketcap")),
            "investor_name": who,
            "status": NEW_DEAL,
            "latest_pct": None,
            "change_pct": None,
            "as_of_quarter": g["date"],
            "first_seen_quarter": g["date"],
            "investors_holding_count": 1,
            "deal_signal": text,
            "deal_date": g["date"],
            "source": "nse-deal",
            "changed_run_id": run_id,
            "changed_at": now,
            "updated_at": now,
        }
        db[COLL_STATE].update_one({"key": key}, {"$set": doc}, upsert=True)
        stats.changes[NEW_DEAL] += 1
        stats.changed_rows.append(doc)
    return deals


def rescore(db, client, deals: dict, news_docs: dict, sleep: float, use_screener: bool, log) -> None:
    """Conviction + why for every holding. Local Mongo only, except Screener for new buys."""
    price_cache: dict[str, dict | None] = {}
    now = datetime.now()
    ops = []
    for doc in db[COLL_STATE].find({}):
        sym, investor = doc["scrip"], doc["investor_name"]
        if doc.get("status") == EXITED:
            price_cache.setdefault(sym, None)  # no price work for exits
        if sym not in price_cache:
            try:
                enrich = qs.enrich_symbol(client, sym)
                scan = ii.daily_scan(sym, enrich["daily"])
                block = ii.score_block("swing", scan, enrich)
                price_cache[sym] = (
                    qs.derive_conviction_sentiment(block, qs.extract_scan_signals(scan))
                    if block and block.get("t1") is not None
                    else None
                )
                closes = [b["close"] for b in enrich["daily"] if b.get("close")]
                if price_cache[sym] is not None:
                    price_cache[sym]["close"] = closes[-1] if closes else None
            except Exception as exc:  # missing price history must not stop the run
                log(f"price {sym}: {exc}")
                price_cache[sym] = None
        price = price_cache[sym]
        news = ii.news_impact(news_docs, sym, doc.get("company") or sym) if news_docs else None
        pros = doc.get("screener_pros")
        extra: dict[str, Any] = {}
        fetched = doc.get("screener_fetched_at")
        stale = not isinstance(fetched, datetime) or now - fetched > SCREENER_MAX_AGE
        if use_screener and doc.get("status") in SCREENER_STATUSES and stale:
            try:
                time.sleep(sleep)
                page = ii.fetch_screener(sym)
                pros, cons = ii.parse_pros_cons(page) if page else ([], [])
                extra.update({"screener_pros": pros, "screener_cons": cons, "screener_fetched_at": now})
            except Exception as exc:
                log(f"screener {sym}: {exc}")
        scored = score_conviction(
            doc,
            investor,
            int(doc.get("investors_holding_count") or 1),
            price,
            news,
            deals.get((sym, investor)),
            pros,
        )
        if (sym, investor) not in deals and doc.get("deal_signal"):
            # deal fell out of the window
            extra.update({"deal_signal": None, "deal_date": None})
        fields = {
            **scored,
            **extra,
            "close": (price or {}).get("close"),
            "price_conviction": (price or {}).get("conviction"),
            "price_sentiment": (price or {}).get("sentiment"),
            "news_sentiment": (news or {}).get("news_sentiment"),
            "news_headline": (news or {}).get("news_headline"),
            "scored_at": now,
        }
        ops.append(UpdateOne({"_id": doc["_id"]}, {"$set": fields}))
    if ops:
        db[COLL_STATE].bulk_write(ops, ordered=False)


def print_summary(db, run_id: str, stats: Stats, elapsed: float, checked_total: int) -> None:
    status_counts = Counter(d["status"] for d in db[COLL_STATE].find({}, {"status": 1}))
    per_inv: dict[str, Counter] = defaultdict(Counter)
    for d in db[COLL_STATE].find({}, {"investor_name": 1, "status": 1, "changed_run_id": 1}):
        c = per_inv[d["investor_name"]]
        c["held" if d["status"] in ACTIVE else "exited"] += 1
        if d.get("changed_run_id") == run_id:
            c["changed"] += 1
    print("\nSUMMARY superstar-holdings")
    print(
        f"run {run_id} | {elapsed / 60:.1f} min | stocks checked {stats.checked}/{checked_total} | "
        f"quarters fetched {stats.fetched_quarters} | stocks changed {stats.symbols_changed}"
    )
    print("status totals: " + ", ".join(f"{k} {v}" for k, v in sorted(status_counts.items())))
    print("changed this run: " + (", ".join(f"{k} {v}" for k, v in sorted(stats.changes.items())) or "none"))
    print("investor | held | exited | changed this run")
    for name, c in sorted(per_inv.items(), key=lambda kv: -kv[1]["held"]):
        print(f"{name} | {c['held']} | {c['exited']} | {c['changed']}")
    rows = list(db[COLL_STATE].find({"changed_run_id": run_id}, {"_id": 0}))
    order = {"High": 0, "Med": 1, "Low": 2}
    for title, statuses in (
        ("NEW / NEW_DEAL", {NEW, NEW_DEAL}),
        ("INCREASED", {INCREASED}),
        ("DECREASED / EXITED", {DECREASED, EXITED}),
    ):
        picked = [r for r in rows if r.get("status") in statuses]
        if not picked:
            continue
        picked.sort(key=lambda r: (order.get(r.get("conviction"), 3), -abs(r.get("change_pct") or 0)))
        print(f"\n{title} (top {min(TOP_ROWS, len(picked))} of {len(picked)})")
        print("symbol | investor | prev% | now% | conviction | why")
        for r in picked[:TOP_ROWS]:
            print(
                f"{r['scrip']} | {r['investor_name']} | {r.get('prev_pct') or '-'} | "
                f"{r.get('latest_pct') or '-'} | {r.get('conviction')} | {str(r.get('why') or '')[:140]}"
            )
    print("\nEducational only, not SEBI advice.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Track celebrity investor holdings from NSE filings")
    parser.add_argument("--symbols", help="Comma-separated NSE symbols (testing)")
    parser.add_argument("--limit", type=int, help="Check only the first N symbols (testing)")
    parser.add_argument("--backfill-quarters", type=int, default=4, help="Quarters read on a stock's first run")
    parser.add_argument("--recheck-days", type=int, default=3, help="Re-ask NSE at most this often per stock")
    parser.add_argument("--refresh", action="store_true", help="Ignore scan state and re-check every stock")
    parser.add_argument("--skip-deals", action="store_true", help="Skip NSE bulk/block deal snapshot")
    parser.add_argument("--deal-days", type=int, default=30)
    parser.add_argument("--skip-screener", action="store_true", help="No Screener calls (faster)")
    parser.add_argument("--sleep", type=float, default=1.0, help="Pause between NSE/Screener calls")
    parser.add_argument("--uri", default=DEFAULT_URI)
    args = parser.parse_args()
    sys.stdout.reconfigure(line_buffering=True)

    started = time.time()
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    log = Log(LOG_FILE)
    log(f"run {run_id} start {vars(args)}")
    client = MongoClient(args.uri, serverSelectionTimeoutMS=4000)
    client.admin.command("ping")
    db = client[DB_NAME]
    ensure_indexes(db)
    investors = ii.load_investors(INVESTORS_FILE)
    symbols = [s.strip().upper() for s in args.symbols.split(",")] if args.symbols else None
    universe = load_universe(db, symbols, args.limit)
    states = {d["scrip"]: d for d in db[COLL_SCAN].find({"scrip": {"$in": list(universe)}})}
    nse = ii.NseClient(args.sleep, db[ii.NSE_CACHE_COLL])
    stats = Stats()
    db[COLL_RUNS].insert_one({"run_id": run_id, "started_at": datetime.now(), "args": vars(args)})

    today = date.today()
    todo = [s for s in sorted(universe) if needs_check(states.get(s), today, args.recheck_days, args.refresh)]
    print(f"superstar-holdings: {len(todo)}/{len(universe)} stocks to check, {len(investors)} investors")
    failures = 0
    for i, sym in enumerate(todo, 1):
        if i % 250 == 0:
            print(f"progress {i}/{len(todo)}")
        stats.checked += 1
        try:
            changed = fetch_symbol(db, nse, sym, states.get(sym), investors, args.backfill_quarters, stats, log)
            failures = 0
        except Exception as exc:
            failures += 1
            stats.extra["nse-error"] += 1
            log(f"nse {sym}: {exc}")
            if failures >= 5:
                print("NSE stopped after 5 consecutive failures; rerun later to resume")
                break
            continue
        if changed:
            stats.symbols_changed += 1
            rebuild_symbol(db, sym, run_id, universe.get(sym, {}), stats)

    deals: dict = {}
    if not args.skip_deals:
        try:
            ii.store_deal_snapshot(db, nse, stats)
        except Exception as exc:
            stats.extra["deals-error"] += 1
            log(f"deal snapshot: {exc}")
        deals = apply_deals(db, investors, args.deal_days, run_id, universe, stats)

    rescore(db, client, deals, ii.load_news(db), args.sleep, not args.skip_screener, log)

    elapsed = time.time() - started
    db[COLL_RUNS].update_one(
        {"run_id": run_id},
        {
            "$set": {
                "finished_at": datetime.now(),
                "checked": stats.checked,
                "fetched_quarters": stats.fetched_quarters,
                "symbols_changed": stats.symbols_changed,
                "changes": dict(stats.changes),
                "errors": dict(stats.extra),
            }
        },
    )
    log(f"run {run_id} done in {elapsed:.0f}s errors={dict(stats.extra)}")
    if stats.extra:
        print("notes: " +", ".join(f"{k} {v}" for k, v in sorted(stats.extra.items())) + f" (see {LOG_FILE})")
    print_summary(db, run_id, stats, elapsed, len(universe))


if __name__ == "__main__":
    main()
