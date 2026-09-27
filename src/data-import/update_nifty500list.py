"""Refresh ind_nifty500list.csv from Nifty 500 + top 750 NSE stocks by market cap."""

import csv
import io
import sys
from pathlib import Path

import requests
import yfinance as yf

OUT = Path(__file__).resolve().parent / "nselist" / "ind_nifty500list.csv"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
INDEX_CSVS = [
    "ind_nifty500list.csv",
    "ind_niftytotalmarket_list.csv",
    "ind_niftymicrocap250_list.csv",
    "ind_niftymidsmallcap400list.csv",
    "ind_niftysmallcap100list.csv",
    "ind_niftymidcap100list.csv",
]
YF_BATCH = 80
TOP_MCAP_COUNT = 750


def fetch_csv(url):
    response = requests.get(url, headers=HEADERS, timeout=60)
    response.raise_for_status()
    return list(csv.DictReader(io.StringIO(response.text)))


def fetch_active_nse_listings():
    rows = fetch_csv("https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv")
    active = {}
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


def fetch_index_metadata():
    metadata = {}
    base = "https://nsearchives.nseindia.com/content/indices/"
    for name in INDEX_CSVS:
        try:
            rows = fetch_csv(base + name)
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


def fetch_nifty500_symbols():
    rows = fetch_csv(
        "https://nsearchives.nseindia.com/content/indices/ind_nifty500list.csv"
    )
    return {row["Symbol"].strip() for row in rows}


def fetch_market_caps(symbols):
    market_caps = {}
    ordered = sorted(symbols)
    suffix = {symbol: ".NS" for symbol in ordered}
    for start in range(0, len(ordered), YF_BATCH):
        batch = ordered[start : start + YF_BATCH]
        tickers = yf.Tickers(
            " ".join(f"{symbol}{suffix[symbol]}" for symbol in batch)
        )
        for symbol in batch:
            try:
                market_cap = (
                    tickers.tickers[f"{symbol}{suffix[symbol]}"].info.get("marketCap") or 0
                )
            except Exception:
                market_cap = 0
            if market_cap > 0:
                market_caps[symbol] = market_cap
    return market_caps


def load_current_metadata():
    if not OUT.exists():
        return {}
    metadata = {}
    with OUT.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            symbol = row["Symbol"].strip()
            metadata[symbol] = {
                "company": row["Company Name"].strip(),
                "industry": row["Industry"].strip(),
                "series": row["Series"].strip() or "EQ",
                "isin": row["ISIN Code"].strip(),
            }
    return metadata


def build_row(symbol, active, metadata, current):
    meta = metadata.get(symbol) or current.get(symbol) or {}
    active_row = active[symbol]
    return {
        "Company Name": meta.get("company") or active_row["company"],
        "Industry": meta.get("industry", ""),
        "Symbol": symbol,
        "Series": meta.get("series") or active_row["series"],
        "ISIN Code": meta.get("isin") or active_row["isin"],
    }


def main():
    active = fetch_active_nse_listings()
    metadata = fetch_index_metadata()
    current = load_current_metadata()
    nifty500 = fetch_nifty500_symbols()

    eq_symbols = {symbol for symbol, row in active.items() if row["series"] == "EQ"}
    nifty500_active = nifty500 & set(active.keys())

    print(f"Active NSE listings (EQ/BE/BZ): {len(active)}")
    print(f"Active NSE EQ listings: {len(eq_symbols)}")
    print(f"Official Nifty 500 symbols: {len(nifty500)}")
    print(f"Official Nifty 500 active on NSE: {len(nifty500_active)}")

    market_caps = fetch_market_caps(eq_symbols)
    print(f"Market caps fetched: {len(market_caps)}")

    top750 = {
        symbol
        for symbol, _ in sorted(market_caps.items(), key=lambda item: item[1], reverse=True)[
            :TOP_MCAP_COUNT
        ]
    }
    selected = (nifty500_active | top750) & set(active.keys())
    print(f"Top {TOP_MCAP_COUNT} by market cap: {len(top750)}")
    print(f"Final universe after union + active filter: {len(selected)}")

    rows = [
        build_row(symbol, active, metadata, current)
        for symbol in sorted(selected, key=lambda sym: build_row(sym, active, metadata, current)["Company Name"].upper())
    ]

    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["Company Name", "Industry", "Symbol", "Series", "ISIN Code"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
