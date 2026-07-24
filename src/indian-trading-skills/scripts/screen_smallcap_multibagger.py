#!/usr/bin/env python3
"""Screen Nifty Smallcap 250 for multibagger-style growth + quality candidates."""

import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import yfinance as yf
from niftystocks import ns

warnings.filterwarnings("ignore")


def analyze(ticker: str) -> dict | None:
    try:
        tk = yf.Ticker(ticker)
        info = tk.info or {}
        hist = tk.history(period="3y")
        if hist.empty or len(hist) < 200:
            return None

        price = hist["Close"].iloc[-1]
        ret1y = (price / hist["Close"].iloc[-252] - 1) * 100 if len(hist) >= 252 else None
        ret3y = (price / hist["Close"].iloc[0] - 1) * 100

        mcap = info.get("marketCap") or 0
        if mcap <= 0 or mcap > 30_000 * 1e7:
            return None

        roe = info.get("returnOnEquity")
        de = info.get("debtToEquity")
        rev_g = info.get("revenueGrowth")
        earn_g = info.get("earningsGrowth")
        pe = info.get("trailingPE")
        pb = info.get("priceToBook")
        name = info.get("shortName") or ticker.replace(".NS", "")

        # Relaxed filters for sparse yfinance fundamentals on Indian smallcaps
        if roe is not None and roe < 0.08:
            return None
        if de is not None and de > 250:
            return None
        if rev_g is not None and rev_g < 0.05:
            return None

        # Need at least one growth/quality signal
        quality_signals = 0
        if roe is not None and roe >= 0.12:
            quality_signals += 1
        if rev_g is not None and rev_g >= 0.10:
            quality_signals += 1
        if earn_g is not None and earn_g >= 0.10:
            quality_signals += 1
        if ret1y is not None and ret1y >= 15:
            quality_signals += 1
        if ret3y >= 50:
            quality_signals += 1
        if quality_signals < 2:
            return None

        roe_score = min((roe or 0), 0.40) / 0.40 * 25
        rev_score = min((rev_g or 0), 0.50) / 0.50 * 25
        earn_score = min((earn_g or 0), 0.50) / 0.50 * 10 if earn_g else 0
        mom1y = min((ret1y or 0), 100) / 100 * 15
        mom3y = min((ret3y or 0), 300) / 300 * 15
        debt_score = max(0, (100 - de) / 100) * 10 if de is not None else 5
        score = roe_score + rev_score + earn_score + mom1y + mom3y + debt_score

        return {
            "symbol": ticker.replace(".NS", ""),
            "name": name[:35],
            "mcap_cr": round(mcap / 1e7, 0),
            "roe_pct": round(roe * 100, 1),
            "rev_g_pct": round(rev_g * 100, 1),
            "earn_g_pct": round(earn_g * 100, 1) if earn_g else None,
            "de": round(de, 1) if de is not None else None,
            "pe": round(pe, 1) if pe else None,
            "pb": round(pb, 1) if pb else None,
            "ret1y_pct": round(ret1y, 1) if ret1y else None,
            "ret3y_pct": round(ret3y, 1),
            "score": round(score, 1),
        }
    except Exception:
        return None


def main() -> None:
    tickers = ns.get_nifty_smallcap250_with_ns()
    print(f"Universe: {len(tickers)} stocks")

    rows: list[dict] = []
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = {executor.submit(analyze, t): t for t in tickers}
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            if result:
                rows.append(result)
            if i % 50 == 0:
                print(f"Processed {i}/{len(tickers)}...")

    df = pd.DataFrame(rows)
    if df.empty:
        print("No stocks passed filters.")
        return

    df = df.sort_values("score", ascending=False)
    print("\n=== TOP 20 MULTIBAGGER-STYLE SMALLCAP CANDIDATES ===")
    print(df.head(20).to_string(index=False))
    print(f"\nTotal passed filters: {len(df)}")


if __name__ == "__main__":
    main()
