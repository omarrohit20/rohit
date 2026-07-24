# Multi-Horizon Suggestions — [Collection or Collections]

**Database:** [Nsedata / chartlink / both]  
**Collection:** `[name]` — or **Collections:** `[name1]`, `[name2]`, …  
**As of:** [date] IST  
**Candidates scanned:** [N] (break out per table when multi-source)  
**Data:** full scan-row columns + `history` / `history15m` + `technical` / `fundamental` + news

> **Multi-table rule:** If more than one collection was queried, every ranked
> result / Priority / horizon / News / Avoid row **must** include a **Table**
> column (collection name). Use `db.collection` when names collide across DBs.
>
> **Scoring rule:** Every Priority and horizon result row **must** include
> **Sentiment**, **Conviction**, and **Prob%** (`probability_score`).

---

## Priority Picks (required — lead with this)

### Single table

Use this exact shape. **Why** must cite real scan-table fields (filters, ML tags, % change, Ldchange, BreakHigh/Reversal, industry) **and** news when present.

| Priority | Symbol | Sentiment | Conviction | Prob% | Why |
|----------|--------|-----------|------------|-------|-----|
| 1 | TECHM | Bullish | High | 78 | Q1 results today + AnchisBuyUp / ReversalLow; already +2% into the print |
| 2 | ABB | Bullish | Med | 68 | MLBuy + NearHighYe; Moneycontrol spotlight buy (zone ~7150–7225 → ~7730) after yesterday’s volume surge |
| 3 | DIXON | Bullish | Med | 65 | BreakHighMe + Vivo JV still the live story |
| 4 | SWIGGY | Bullish | High | 72 | MLBuy + strongest tape (+4%+); Indian-ownership / Instamart optionality still in play |
| 5 | BAJFINANC | Bullish | Med | 62 | BreakHighMe + strong AUM update; results later (30 Jul) so more momentum than news today |

### Multiple tables (required when 2+ collections)

| Priority | Table | Symbol | Sentiment | Conviction | Prob% | Why |
|----------|-------|--------|-----------|------------|-------|-----|
| 1 | highBuy | TECHM | Bullish | High | 78 | Q1 results today + AnchisBuyUp / ReversalLow; already +2% into the print |
| 2 | buy_all_processor | ABB | Bullish | Med | 68 | MLBuy + NearHighYe; Moneycontrol spotlight buy after volume surge |
| 3 | highBuy | DIXON | Bullish | Med | 65 | BreakHighMe + Vivo JV still the live story |

**Field values:** Sentiment = Bullish / Bearish / Neutral / Mixed · Conviction = High / Med / Low · Prob% = 0–100 integer.

Rules for **Why** (one dense sentence):
1. Lead with the strongest **scan-table signals** (`intradaytech` / `ml` / `mlData` / `filter*` / `BreakHigh*` / `Reversal*` / `NearHigh*` / `AnchisBuyUp` / TOP buckets).
2. Add **tape** (`PCT_day_change`, `PCT_change`, price vs VWAP, volume if present).
3. Add **News catalyst** if any; otherwise say momentum-only.
4. End with extension cue when useful (e.g. “results later”, “only if loan clears”).

Also fill May extend? in the snapshot below for the same symbols.

---

## Executive Summary

[2–3 sentences: which horizons align, top Priority pick, main risk]

| Horizon | Table | Top pick | Sentiment | Conviction | Prob% | May extend? |
|---------|-------|----------|-----------|------------|-------|-------------|
| Intraday | [name or — if single] | | Bullish / Bearish / Neutral / Mixed | High / Med / Low | 0–100 | Yes / Possible / Weak / No |
| 3–5 days | | | | | | |
| Short-term | | | | | | |
| Long-term | | | | | | |

*(Omit Table column only when a single collection was used.)*

---

## News & Extension Snapshot

| Table | Symbol | Horizon | Sentiment | Conviction | Prob% | News catalyst | May extend? |
|-------|--------|---------|-----------|------------|-------|---------------|-------------|
| [or omit Table if single] | | | | | | [1-line or "No fresh news"] | Yes / Possible / Only if X / Weak / No |

---

## Scan Columns Used

List the **actual fields present** on documents in this collection (from `collection-schema` / sample doc). Do not ignore tags just because they are not in a fixed shortlist.

When multiple tables: use one subsection per table (`### Table: highBuy`).

Example families (use whatever exists on the row):  
`scrip`, `industry`, `close`, `PCT_change`, `PCT_day_change`, `Ldchange`, `volume`, `filter`…`filter6`, `intradaytech`, `shorttermtech`, `ml`, `mlData`, `forecast_day_PCT*_change`, week/month/year high-low changes, `keyIndicator`, `tobuy`/`tosell`, `processor`, `eventtime`.

---

## Intraday (Same Session)

| Rank | Table | Symbol | Sentiment | Conviction | Prob% | Score | Close (₹) | Entry | T1 | T2 | Stop | R:R | News catalyst | May extend? | Why / Notes |
|------|-------|--------|-----------|------------|-------|-------|-----------|-------|----|----|------|-----|---------------|-------------|-------------|
| 1 | | | | | | | | | | | | | | | |
| 2 | | | | | | | | | | | | | | | |
| 3 | | | | | | | | | | | | | | | |

*(Omit Table column only for single-collection reports.)*

---

## 3–5 Days

| Rank | Table | Symbol | Sentiment | Conviction | Prob% | Score | Close (₹) | Entry | T1 | T2 | Stop | R:R | News catalyst | May extend? | Why / Notes |
|------|-------|--------|-----------|------------|-------|-------|-----------|-------|----|----|------|-----|---------------|-------------|-------------|
| 1 | | | | | | | | | | | | | | | |
| 2 | | | | | | | | | | | | | | | |
| 3 | | | | | | | | | | | | | | | |

---

## Short-Term (1–20 Days)

| Rank | Table | Symbol | Sentiment | Conviction | Prob% | Score | Close (₹) | Entry | T1 | T2 | T3 | Stop | R:R | News catalyst | May extend? | Why / Notes |
|------|-------|--------|-----------|------------|-------|-------|-----------|-------|----|----|----|------|-----|---------------|-------------|-------------|
| 1 | | | | | | | | | | | | | | | | |
| 2 | | | | | | | | | | | | | | | | |
| 3 | | | | | | | | | | | | | | | | |

---

## Long-Term / Investment

| Rank | Table | Symbol | Sentiment | Conviction | Prob% | Score | Close (₹) | Entry zone | T1 | T2 | Invalidation | PE | News catalyst | May extend? | Why / Notes |
|------|-------|--------|-----------|------------|-------|-------|-----------|------------|----|----|--------------|----|---------------|-------------|-------------|
| 1 | | | | | | | | | | | | | | | |
| 2 | | | | | | | | | | | | | | | |
| 3 | | | | | | | | | | | | | | | |

---

## Watchlist / Avoid

| Table | Symbol | Sentiment | Conviction | Prob% | Why skip |
|-------|--------|-----------|------------|-------|----------|
| | | | | | Weak R:R / below VWAP / adverse news / duplicate noise |

---

## Disclaimer

Educational analysis only — not SEBI-registered investment advice. Verify live LTP, circuits, and corporate actions before trading.
