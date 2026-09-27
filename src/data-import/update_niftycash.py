"""Refresh ind_niftycash.csv from live NSE + BSE sources."""

import csv
import gzip
import io
import re
import sys
from pathlib import Path

import requests
import yfinance as yf

OUT = Path(__file__).resolve().parent / "nselist" / "ind_niftycash.csv"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
MCAP_MIN = 1e10  # 1000 crore
BHAVCOPY_DATE = "20260924"
BSE_BATCH = 80
RIGHTS_RE = re.compile(r"-RE\d*$", re.I)


def fetch_nse_equities():
    response = requests.get(
        "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv",
        headers=HEADERS,
        timeout=60,
    )
    response.raise_for_status()
    stocks = {}
    isins = set()
    for row in csv.DictReader(io.StringIO(response.text)):
        series = row[" SERIES"].strip()
        if series not in ("EQ", "BE", "BZ"):
            continue
        symbol = row["SYMBOL"].strip()
        name = row["NAME OF COMPANY"].strip()
        isin = row[" ISIN NUMBER"].strip()
        stocks[symbol] = name
        isins.add(isin)
    return stocks, isins


def fetch_bse_bhavcopy_symbols(nse_isins):
    response = requests.get(
        f"https://mtf.trading/bhavcopy/{BHAVCOPY_DATE}.csv.gz",
        headers=HEADERS,
        timeout=120,
    )
    response.raise_for_status()
    text = gzip.decompress(response.content).decode("utf-8")
    symbols = {}
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


def load_current_bse_only(nse_symbols):
    if not OUT.exists():
        return {}
    extras = {}
    with OUT.open(newline="", encoding="utf-8") as handle:
        for row in csv.reader(handle):
            if not row or row[0] == "Stock Name":
                continue
            name, symbol = row[0].strip(), row[1].strip()
            if symbol not in nse_symbols and not RIGHTS_RE.search(symbol):
                extras[symbol] = name
    return extras


def fetch_bse_market_caps(candidates):
    passed = {}
    symbols = sorted(candidates)
    for start in range(0, len(symbols), BSE_BATCH):
        batch = symbols[start : start + BSE_BATCH]
        tickers = yf.Tickers(" ".join(f"{symbol}.BO" for symbol in batch))
        for symbol in batch:
            try:
                info = tickers.tickers[f"{symbol}.BO"].info
            except Exception:
                continue
            market_cap = info.get("marketCap") or 0
            if market_cap < MCAP_MIN:
                continue
            name = (
                info.get("longName")
                or info.get("shortName")
                or candidates.get(symbol)
                or symbol
            )
            passed[symbol] = name.strip()
    return passed


def main():
    nse_stocks, nse_isins = fetch_nse_equities()
    bse_candidates = fetch_bse_bhavcopy_symbols(nse_isins)
    bse_candidates.update(load_current_bse_only(nse_stocks))

    print(f"NSE equities: {len(nse_stocks)}")
    print(f"BSE-only candidates for mcap check: {len(bse_candidates)}")

    bse_stocks = fetch_bse_market_caps(bse_candidates)
    print(f"BSE-only kept (mcap >= 1000 cr): {len(bse_stocks)}")

    combined = dict(nse_stocks)
    combined.update(bse_stocks)
    rows = sorted(combined.items(), key=lambda item: item[1].upper())

    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Stock Name", "Symbol"])
        for symbol, name in rows:
            writer.writerow([name, symbol])

    print(f"Wrote {len(rows)} rows to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
