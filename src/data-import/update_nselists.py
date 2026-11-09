"""Refresh NSE list CSVs: futures (F&O), Nifty 500 universe, and cash (NSE + BSE)."""

from __future__ import annotations

import argparse
import csv
import gzip
import io
import re
import sys
import time
from pathlib import Path

import requests
import yfinance as yf

NSELIST = Path(__file__).resolve().parent / "nselist"
OUT_FUTURES = NSELIST / "ind_niftyfuturelist.csv"
OUT_500 = NSELIST / "ind_nifty500list.csv"
OUT_CASH = NSELIST / "ind_niftycash.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

INDEX_METADATA_CSVS = [
    "ind_nifty500list.csv",
    "ind_niftytotalmarket_list.csv",
    "ind_niftymicrocap250_list.csv",
    "ind_niftymidsmallcap400list.csv",
    "ind_niftysmallcap100list.csv",
    "ind_niftymidcap100list.csv",
]

YF_BATCH = 80
TOP_MCAP_COUNT = 750
MCAP_MIN = 1e10  # 1000 crore
BHAVCOPY_DATE = "20260924"
RIGHTS_RE = re.compile(r"-RE\d*$", re.I)

# Index underlyings in fo_mktlots.csv (not single stocks).
_FO_INDEX_SYMBOLS = frozenset(
    {
        "NIFTY",
        "BANKNIFTY",
        "FINNIFTY",
        "MIDCPNIFTY",
        "NIFTYNXT50",
        "NIFTYIT",
        "NIFTYCPSE",
        "NIFTYPSE",
    }
)


def fetch_csv(url: str, label: str = "") -> list[dict]:
    tag = f"[{label}] " if label else ""
    print(f"{tag}GET {url}")
    t0 = time.time()
    response = requests.get(url, headers=HEADERS, timeout=60)
    response.raise_for_status()
    rows = list(csv.DictReader(io.StringIO(response.text)))
    print(f"{tag}  {len(rows)} rows in {time.time() - t0:.1f}s")
    return rows


def _csv_field(row: dict, field: str) -> str:
    want = field.strip().upper()
    for key, val in row.items():
        if key.strip().split(",")[0].upper() == want:
            return str(val).strip().strip(",")
    return ""


def fetch_active_nse_listings() -> dict[str, dict]:
    rows = fetch_csv("https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv")
    active: dict[str, dict] = {}
    for row in rows:
        series = row[" SERIES"].strip()
        if series not in ("EQ", "BE", "BZ"):
            continue
        symbol = row["SYMBOL"].strip()
        active[symbol] = {
            "company": row["NAME OF COMPANY"].strip(),
            "series": series,
            "isin": row[" ISIN NUMBER"].strip(),
        }
    return active


def fetch_index_metadata() -> dict[str, dict]:
    metadata: dict[str, dict] = {}
    base = "https://nsearchives.nseindia.com/content/indices/"
    for name in INDEX_METADATA_CSVS:
        try:
            rows = fetch_csv(base + name, label=f"500-meta-{name}")
        except Exception:
            continue
        for row in rows:
            symbol = row["Symbol"].strip()
            metadata[symbol] = {
                "company": row["Company Name"].strip(),
                "industry": row["Industry"].strip(),
                "series": row["Series"].strip() or "EQ",
                "isin": row["ISIN Code"].strip(),
            }
    return metadata


def fetch_nifty500_symbols() -> set[str]:
    rows = fetch_csv(
        "https://nsearchives.nseindia.com/content/indices/ind_nifty500list.csv",
        label="500-nifty",
    )
    return {row["Symbol"].strip() for row in rows}


def _mcap_rupees_to_crores(market_cap) -> float:
    try:
        val = float(market_cap or 0)
    except (TypeError, ValueError):
        return 0.0
    if val <= 0:
        return 0.0
    return round(val / 1e7, 2)


def fetch_market_caps_ns(symbols: set[str], label: str = "mcap") -> dict[str, float]:
    """Symbol -> market cap in INR crores (.NS tickers)."""
    return _fetch_market_caps_crores({symbol: "NS" for symbol in symbols}, label=label)


def _log_mcap_batch(label: str, exchange: str, batch_ok: list[tuple[str, float]]) -> None:
    parts = [f"{symbol}={cap:,.2f}" for symbol, cap in batch_ok]
    if not parts:
        print(f"[{label}]   (no marketCap for this batch)")
        return
    # Keep one line per batch; wrap long batches in chunks for readability.
    chunk = 8
    for i in range(0, len(parts), chunk):
        segment = parts[i : i + chunk]
        prefix = f"[{label}]   "
        if i == 0:
            prefix += f"{exchange} "
        print(f"{prefix}{', '.join(segment)}")


def _fetch_market_caps_crores(
    symbol_exchange: dict[str, str], label: str = "mcap"
) -> dict[str, float]:
    market_caps: dict[str, float] = {}
    if not symbol_exchange:
        print(f"[{label}] market cap: nothing to fetch")
        return market_caps
    groups: dict[str, list[str]] = {"NS": [], "BO": []}
    for symbol, exchange in symbol_exchange.items():
        ex = exchange if exchange in groups else "NS"
        groups[ex].append(symbol)
    print(
        f"[{label}] market cap: {len(symbol_exchange)} symbols "
        f"(NSE .NS={len(groups['NS'])}, BSE .BO={len(groups['BO'])})"
    )
    grand_start = time.time()
    for exchange, suffix in (("NS", ".NS"), ("BO", ".BO")):
        ordered = sorted(groups[exchange])
        if not ordered:
            continue
        total_batches = (len(ordered) + YF_BATCH - 1) // YF_BATCH
        print(f"[{label}] {exchange}: fetching {len(ordered)} tickers in {total_batches} batches")
        for batch_idx, start in enumerate(range(0, len(ordered), YF_BATCH), 1):
            batch = ordered[start : start + YF_BATCH]
            t0 = time.time()
            tickers = yf.Tickers(" ".join(f"{symbol}{suffix}" for symbol in batch))
            batch_ok: list[tuple[str, float]] = []
            for symbol in batch:
                key = f"{symbol}{suffix}"
                try:
                    raw = tickers.tickers[key].info.get("marketCap") or 0
                except Exception:
                    raw = 0
                cap = _mcap_rupees_to_crores(raw)
                if cap > 0:
                    market_caps[symbol] = cap
                    batch_ok.append((symbol, cap))
            elapsed = time.time() - t0
            span = batch[0] if len(batch) == 1 else f"{batch[0]}..{batch[-1]}"
            print(
                f"[{label}] {exchange} batch {batch_idx}/{total_batches} "
                f"{span} | caps {len(batch_ok)}/{len(batch)} | {elapsed:.1f}s "
                f"| running total {len(market_caps)}"
            )
            _log_mcap_batch(label, exchange, batch_ok)
    print(f"[{label}] market cap done: {len(market_caps)} symbols in {time.time() - grand_start:.1f}s")
    return market_caps


def load_current_500_metadata() -> dict[str, dict]:
    if not OUT_500.exists():
        return {}
    metadata: dict[str, dict] = {}
    with OUT_500.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            symbol = row["Symbol"].strip()
            metadata[symbol] = {
                "company": row["Company Name"].strip(),
                "industry": row["Industry"].strip(),
                "series": row["Series"].strip() or "EQ",
                "isin": row["ISIN Code"].strip(),
                "marketcap": row.get("Marketcap", "").strip(),
            }
    return metadata


def build_500_row(
    symbol: str,
    active: dict,
    metadata: dict,
    current: dict,
    market_caps: dict[str, float],
) -> dict:
    meta = metadata.get(symbol) or current.get(symbol) or {}
    active_row = active[symbol]
    mcap = market_caps.get(symbol, 0.0) or 0.0
    if mcap <= 0 and meta.get("marketcap"):
        try:
            mcap = float(meta["marketcap"])
        except ValueError:
            mcap = 0.0
    return {
        "Company Name": meta.get("company") or active_row["company"],
        "Industry": meta.get("industry", ""),
        "Symbol": symbol,
        "Series": meta.get("series") or active_row["series"],
        "ISIN Code": meta.get("isin") or active_row["isin"],
        "Marketcap": mcap if mcap > 0 else "",
    }


def update_nifty500_list() -> int:
    print("[500] --- start ---")
    t_phase = time.time()
    active = fetch_active_nse_listings()
    print(f"[500] NSE listings loaded: {len(active)} ({time.time() - t_phase:.1f}s)")
    t_phase = time.time()
    metadata = fetch_index_metadata()
    print(f"[500] index metadata: {len(metadata)} symbols ({time.time() - t_phase:.1f}s)")
    current = load_current_500_metadata()
    nifty500 = fetch_nifty500_symbols()

    eq_symbols = {symbol for symbol, row in active.items() if row["series"] == "EQ"}
    nifty500_active = nifty500 & set(active.keys())

    print(f"[500] Active NSE listings (EQ/BE/BZ): {len(active)}")
    print(f"[500] Active NSE EQ listings: {len(eq_symbols)}")
    print(f"[500] Official Nifty 500 symbols: {len(nifty500)}")
    print(f"[500] Official Nifty 500 active on NSE: {len(nifty500_active)}")

    market_caps = fetch_market_caps_ns(eq_symbols, label="500-eq")
    print(f"[500] Market caps (EQ universe): {len(market_caps)}")

    top750 = {
        symbol
        for symbol, _ in sorted(market_caps.items(), key=lambda item: item[1], reverse=True)[
            :TOP_MCAP_COUNT
        ]
    }
    selected = (nifty500_active | top750) & set(active.keys())
    missing = selected - set(market_caps)
    if missing:
        print(f"[500] topping up market cap for {len(missing)} symbols not in EQ fetch")
        market_caps.update(fetch_market_caps_ns(missing, label="500-extra"))
    print(f"[500] Top {TOP_MCAP_COUNT} by market cap: {len(top750)}")
    print(f"[500] Final universe: {len(selected)}")

    rows = [
        build_500_row(symbol, active, metadata, current, market_caps)
        for symbol in sorted(
            selected,
            key=lambda sym: build_500_row(sym, active, metadata, current, market_caps)[
                "Company Name"
            ].upper(),
        )
    ]

    with OUT_500.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "Company Name",
                "Industry",
                "Symbol",
                "Series",
                "ISIN Code",
                "Marketcap",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"[500] Wrote {len(rows)} rows to {OUT_500}")
    return len(rows)


def fetch_bse_bhavcopy_symbols(nse_isins: set[str]) -> dict[str, str]:
    response = requests.get(
        f"https://mtf.trading/bhavcopy/{BHAVCOPY_DATE}.csv.gz",
        headers=HEADERS,
        timeout=120,
    )
    response.raise_for_status()
    text = gzip.decompress(response.content).decode("utf-8")
    symbols: dict[str, str] = {}
    for row in csv.DictReader(io.StringIO(text)):
        if row.get("exchange") != "BSE" or row.get("FinInstrmTp") != "STK":
            continue
        isin = row["ISIN"].strip()
        if isin in nse_isins:
            continue
        volume = float(row.get("TtlTradgVol") or 0)
        turnover = float(row.get("TtlTrfValue") or 0)
        if volume <= 0 or turnover < 50_000:
            continue
        symbol = row["TckrSymb"].strip()
        if RIGHTS_RE.search(symbol):
            continue
        symbols[symbol] = row["FinInstrmNm"].strip().title()
    return symbols


def load_current_bse_only(nse_symbols: set[str]) -> dict[str, str]:
    if not OUT_CASH.exists():
        return {}
    extras: dict[str, str] = {}
    with OUT_CASH.open(newline="", encoding="utf-8") as handle:
        for row in csv.reader(handle):
            if not row or row[0] == "Stock Name":
                continue
            name, symbol = row[0].strip(), row[1].strip()
            if symbol not in nse_symbols and not RIGHTS_RE.search(symbol):
                extras[symbol] = name
    return extras


def fetch_bse_market_caps(candidates: dict[str, str]) -> dict[str, str]:
    caps = _fetch_market_caps_crores(
        {symbol: "BO" for symbol in candidates}, label="cash-bse-filter"
    )
    passed: dict[str, str] = {}
    for symbol, name in candidates.items():
        crores = caps.get(symbol, 0.0)
        if crores * 1e7 < MCAP_MIN:
            continue
        passed[symbol] = name
    return passed


def update_nifty_cash_list() -> int:
    print("[cash] --- start ---")
    t_phase = time.time()
    nse_stocks = {
        symbol: row["company"]
        for symbol, row in fetch_active_nse_listings().items()
    }
    print(f"[cash] NSE listings: {len(nse_stocks)} ({time.time() - t_phase:.1f}s)")
    nse_isins = set()
    response = requests.get(
        "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv",
        headers=HEADERS,
        timeout=60,
    )
    response.raise_for_status()
    for row in csv.DictReader(io.StringIO(response.text)):
        series = row[" SERIES"].strip()
        if series not in ("EQ", "BE", "BZ"):
            continue
        nse_isins.add(row[" ISIN NUMBER"].strip())

    print(f"[cash] loading BSE bhavcopy {BHAVCOPY_DATE} ...")
    t_bhav = time.time()
    bse_candidates = fetch_bse_bhavcopy_symbols(nse_isins)
    print(f"[cash] BSE bhavcopy parsed: {len(bse_candidates)} candidates ({time.time() - t_bhav:.1f}s)")
    bse_candidates.update(load_current_bse_only(set(nse_stocks)))

    print(f"[cash] NSE equities: {len(nse_stocks)}")
    print(f"[cash] BSE-only candidates for mcap check: {len(bse_candidates)}")

    bse_stocks = fetch_bse_market_caps(bse_candidates)
    print(f"[cash] BSE-only kept (mcap >= 1000 cr): {len(bse_stocks)}")

    combined = dict(nse_stocks)
    combined.update(bse_stocks)
    symbol_exchange = {symbol: "NS" for symbol in nse_stocks}
    for symbol in bse_stocks:
        symbol_exchange[symbol] = "BO"
    market_caps = _fetch_market_caps_crores(symbol_exchange, label="cash")
    print(f"[cash] Market caps written: {len(market_caps)}")

    rows = sorted(combined.items(), key=lambda item: item[1].upper())

    with OUT_CASH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Stock Name", "Symbol", "Marketcap"])
        for symbol, name in rows:
            mcap = market_caps.get(symbol, 0.0)
            writer.writerow([name, symbol, mcap if mcap > 0 else ""])

    print(f"[cash] Wrote {len(rows)} rows to {OUT_CASH}")
    return len(rows)


def update_nifty_futures_list() -> int:
    print("[futures] --- start ---")
    active = fetch_active_nse_listings()
    rows = fetch_csv(
        "https://nsearchives.nseindia.com/content/fo/fo_mktlots.csv", label="futures-fo"
    )
    stocks: dict[str, str] = {}
    for row in rows:
        symbol = _csv_field(row, "SYMBOL")
        if not symbol or symbol in _FO_INDEX_SYMBOLS:
            continue
        if symbol not in active:
            continue
        name = _csv_field(row, "UNDERLYING") or active[symbol]["company"]
        stocks[symbol] = name

    market_caps = fetch_market_caps_ns(set(stocks), label="futures")
    print(f"[futures] Market caps for output: {len(market_caps)}")

    sorted_rows = sorted(stocks.items(), key=lambda item: item[1].upper())
    with OUT_FUTURES.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Stock Name", "Symbol", "Marketcap"])
        for symbol, name in sorted_rows:
            mcap = market_caps.get(symbol, 0.0)
            writer.writerow([name, symbol, mcap if mcap > 0 else ""])

    print(f"[futures] Active F&O underlyings (equities): {len(sorted_rows)}")
    print(f"[futures] Wrote {len(sorted_rows)} rows to {OUT_FUTURES}")
    return len(sorted_rows)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Update nselist CSVs for futures, Nifty 500, and cash."
    )
    parser.add_argument(
        "--only",
        choices=("futures", "500", "cash", "all"),
        default="all",
        help="Update a single list (default: all three).",
    )
    args = parser.parse_args()

    NSELIST.mkdir(parents=True, exist_ok=True)
    run_t0 = time.time()
    print(f"update_nselists: mode={args.only}")

    if args.only in ("futures", "all"):
        update_nifty_futures_list()
    if args.only in ("500", "all"):
        update_nifty500_list()
    if args.only in ("cash", "all"):
        update_nifty_cash_list()
    print(f"update_nselists: finished in {time.time() - run_t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
