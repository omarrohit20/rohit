#!/usr/bin/env python3
"""Build High-conviction investment ideas into three Nsedata collections.

Examples:
  python skills/investment-ideas/scripts/run_investment_ideas.py
  python skills/investment-ideas/scripts/run_investment_ideas.py --only breakout
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
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
PURGE_DAYS = {
    COLL_LONG: None,
    COLL_MEDIUM: 90,
    COLL_SHORT: 20,
}

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)
NSE_PAGE = "https://www.nseindia.com/companies-listing/corporate-filings-shareholding-pattern"
NSE_ORIGIN = "https://www.nseindia.com"
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
        "horizon_label": "long-term (about 6-18 months)",
        "scorer": "long",
        "lookback": True,
        "window": "6 months",
    },
    {
        "table": "breakoutY2H",
        "fallback": None,
        "collection": COLL_LONG,
        "horizon_label": "long-term (about 6-18 months)",
        "scorer": "long",
        "lookback": True,
        "window": "6 months",
    },
    {
        "table": "breakoutW2H",
        "fallback": "breakoutW2HR",
        "collection": COLL_SHORT,
        "horizon_label": "short-term (about 2-6 weeks)",
        "scorer": "short",
        "lookback": False,
        "window": "the live scan window",
    },
    {
        "table": "breakoutM2H",
        "fallback": None,
        "collection": COLL_MEDIUM,
        "horizon_label": "medium-term (about 1-3 months)",
        "scorer": "swing",
        "lookback": False,
        "window": "the live scan window",
    },
    {
        "table": "breakoutMH",
        "fallback": None,
        "collection": COLL_LONG,
        "horizon_label": "long-term (about 3-12 months)",
        "scorer": "long",
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


def parse_screener(page: str) -> dict[str, float | None]:
    return {
        "marketcap_cr": parse_market_cap(page),
        "sales_cr": parse_annual_sales(page),
        "order_book_cr": parse_order_book(page),
    }


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


def score_block(kind: str, scan: dict, enrich: dict) -> dict | None:
    daily = enrich["daily"]
    if kind == "long":
        return qs.score_long_term(scan, daily, enrich["technical"], enrich["fundamental"])
    if kind == "short":
        return qs.score_short_term(scan, daily, enrich["technical"])
    return qs.score_swing_3_5(scan, daily)


def passes_gate(block: dict | None, scan: dict) -> dict | None:
    if not block or block.get("t1") is None:
        return None
    meta = qs.derive_conviction_sentiment(block, qs.extract_scan_signals(scan))
    if meta.get("conviction") == "High" and meta.get("sentiment") == "Bullish":
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


def upsert_idea(coll, doc: dict, stats: RunStats, collection: str) -> None:
    why = (doc.get("why") or "").strip()
    if not why or doc.get("buy_price") is None or doc.get("target_price") is None:
        stats.extra[f"{collection}:missing-why-or-price"] += 1
        return
    doc["why"] = why
    doc["conviction"] = "High"
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


def run_breakouts(db, client, args, stats: RunStats, scrips: dict[str, dict]) -> None:
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
            doc = {
                "idea_type": "breakout",
                "symbol": symbol,
                "company": info.get("company") or symbol,
                "industry": scan.get("industry") or info.get("industry") or "",
                "horizon_label": spec["horizon_label"],
                "buy_price": price,
                "target_price": qs.round_tick(float(block["t1"])),
                "stoploss": qs.round_tick(float(block["stop"])) if block.get("stop") is not None else None,
                "conviction": "High",
                "sentiment": "Bullish",
                "probability_score": int(meta["probability_score"]),
                "why": breakout_why(table, hit_count, window, scan, enrich["daily"]),
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
    def __init__(self, pause: float) -> None:
        self.pause = pause
        self.cookie = str(Path.home() / ".cache")
        cache_dir = Path.home() / "AppData" / "Local" / "Temp"
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.cookie = str(cache_dir / "investment_ideas_nse_cookies.txt")
        self.curl = shutil.which("curl") or shutil.which("curl.exe")
        self._primed = False

    def prime(self) -> None:
        if not self.curl:
            raise RuntimeError("curl is required for NSE shareholding")
        subprocess.run(
            [self.curl, "-sS", "-c", self.cookie, "-b", self.cookie, "-A", USER_AGENT, "-o", "NUL", "-L", NSE_PAGE],
            check=False,
            capture_output=True,
        )
        self._primed = True

    def get_json(self, path: str) -> Any:
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


def fetch_screener(symbol: str) -> str | None:
    if requests is None:
        raise RuntimeError("requests is required for Screener")
    for path in (f"/company/{urllib.parse.quote(symbol)}/consolidated/", f"/company/{urllib.parse.quote(symbol)}/"):
        response = requests.get("https://www.screener.in" + path, headers=SCREENER_HEADERS, timeout=30)
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
    if not name or pct is None:
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


def shareholding_bundle(nse: NseClient, symbol: str, record_id: str) -> tuple[list[dict], list[dict]]:
    summary = as_row_list(nse.get_json(nse_symbol_path(symbol, record_id, "summary")))
    named = as_row_list(
        nse.get_json(nse_symbol_path(symbol, record_id, "public-shareholder", "shareholders"))
    )
    return summary, named


def run_orderbook(db, client, args, stats: RunStats, scrips: dict[str, dict], nse: NseClient) -> None:
    coll = db[COLL_LONG]
    week_ago = datetime.now() - timedelta(days=7)
    symbols = [symbol for symbol, info in scrips.items() if is_capital_goods(info.get("industry"))]
    print(f"orderbook universe: {len(symbols)}")
    failures = 0
    for index, symbol in enumerate(symbols, start=1):
        cached = coll.find_one(
            {"idea_type": "orderbook", "symbol": symbol, "page_fetched_at": {"$gte": week_ago}},
            {"_id": 1},
        )
        if cached:
            stats.extra["orderbook:cached"] += 1
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
        enrich = qs.enrich_symbol(client, symbol)
        scan = {"scrip": symbol, "close": enrich["daily"][-1]["close"] if enrich["daily"] else None}
        block = score_block("long", scan, enrich)
        meta = passes_gate(block, scan)
        if not meta:
            stats.skip_low(COLL_LONG)
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
        doc = {
            "idea_type": "orderbook",
            "symbol": symbol,
            "company": info.get("company") or symbol,
            "industry": info.get("industry") or "",
            "horizon_label": "long-term (kept)",
            "buy_price": buy_price_from_daily(enrich["daily"]),
            "target_price": qs.round_tick(float(block["t1"])),
            "stoploss": qs.round_tick(float(block["stop"])) if block.get("stop") is not None else None,
            "conviction": "High",
            "sentiment": "Bullish",
            "probability_score": int(meta["probability_score"]),
            "why": (
                f"Order book {order_book / market_cap:.1f}x market cap and "
                f"{order_book / sales:.1f}x sales{holder_bit}"
            ),
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
        if index % 25 == 0:
            print(f"orderbook progress {index}/{len(symbols)}")


def run_celebrity(db, client, args, stats: RunStats, scrips: dict[str, dict], caps: dict[str, float], nse: NseClient) -> None:
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
            latest_named = as_row_list(
                nse.get_json(
                    nse_symbol_path(symbol, str(latest_row.get("recordId")), "public-shareholder", "shareholders")
                )
            )
            previous_named: list[dict] = []
            if len(quarters) > 1:
                previous_named = as_row_list(
                    nse.get_json(
                        nse_symbol_path(
                            symbol,
                            str(quarters[1][1].get("recordId")),
                            "public-shareholder",
                            "shareholders",
                        )
                    )
                )
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
        enrich = qs.enrich_symbol(client, symbol)
        scan = {"scrip": symbol, "close": enrich["daily"][-1]["close"] if enrich["daily"] else None}
        block = score_block("swing", scan, enrich)
        meta = passes_gate(block, scan)
        if not meta:
            stats.skip_low(COLL_MEDIUM, len(raised))
            continue
        info = scrips.get(symbol, {})
        price = buy_price_from_daily(enrich["daily"])
        quarter = latest_date.isoformat()
        for canonical, latest_pct, previous_pct in raised:
            if previous_pct is None:
                change = f"{canonical} newly holds {pct_text(latest_pct)} in the latest quarter"
                change_pct = latest_pct
            else:
                change = (
                    f"{canonical} raised holding from {pct_text(previous_pct)} to "
                    f"{pct_text(latest_pct)} in the latest quarter"
                )
                change_pct = latest_pct - previous_pct
            doc = {
                "idea_type": "celebrity",
                "symbol": symbol,
                "company": info.get("company") or symbol,
                "industry": info.get("industry") or "",
                "horizon_label": "medium-term (about 1-3 months)",
                "buy_price": price,
                "target_price": qs.round_tick(float(block["t1"])),
                "stoploss": qs.round_tick(float(block["stop"])) if block.get("stop") is not None else None,
                "conviction": "High",
                "sentiment": "Bullish",
                "probability_score": int(meta["probability_score"]),
                "why": f"{change}; {bucket}",
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
        if index % 25 == 0:
            print(f"celebrity progress {index}/{len(universe)}")


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
        print("symbol | buy | target | conviction | why | holder")
        ordered = sorted(rows, key=lambda row: (-(row.get("hit_count") or 0), row.get("symbol") or ""))
        for row in ordered:
            holder = row.get("investor_name") or row.get("top_holder_name") or ""
            print(
                f"{row.get('symbol')} | {row.get('buy_price')} | {row.get('target_price')} | "
                f"{row.get('conviction')} | {row.get('why')} | {holder}"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Upsert High-conviction investment ideas")
    parser.add_argument("--only", choices=("breakout", "orderbook", "celebrity"))
    parser.add_argument("--months", type=int, default=6)
    parser.add_argument("--celebrity-months", type=int, default=3)
    parser.add_argument("--sleep", type=float, default=1.0)
    parser.add_argument("--uri", default=DEFAULT_URI)
    args = parser.parse_args()

    client = MongoClient(args.uri, serverSelectionTimeoutMS=4000)
    client.admin.command("ping")
    db = client[DB_NAME]
    stats = RunStats()
    ensure_indexes(db)
    purge_old(db, stats)
    scrips = scrip_map(db)
    selected = args.only or "all"
    if selected in {"all", "breakout"}:
        run_breakouts(db, client, args, stats, scrips)
    nse = None
    if selected in {"all", "orderbook", "celebrity"}:
        nse = NseClient(args.sleep)
    if selected in {"all", "orderbook"}:
        run_orderbook(db, client, args, stats, scrips, nse)
    if selected in {"all", "celebrity"}:
        run_celebrity(db, client, args, stats, scrips, fundamental_caps(db), nse)
    print_summary(stats)


if __name__ == "__main__":
    main()
