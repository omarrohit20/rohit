# Priority | Symbol | Why (+ Sentiment · Conviction · Prob%)

Mandatory lead table for every mongo-trade-agent report.

Also see [conviction-sentiment.md](conviction-sentiment.md).

## Format — single table (verbatim shape)

| Priority | Symbol | Sentiment | Conviction | Prob% | Why |
|----------|--------|-----------|------------|-------|-----|
| 1 | TECHM | Bullish | High | 78 | Q1 results today + AnchisBuyUp / ReversalLow; already +2% into the print |
| 2 | ABB | Bullish | Med | 68 | MLBuy + NearHighYe; Moneycontrol spotlight buy (zone ~7150–7225 → ~7730) after yesterday’s volume surge |
| 3 | DIXON | Bullish | Med | 65 | BreakHighMe + Vivo JV still the live story |
| 4 | SWIGGY | Bullish | High | 72 | MLBuy + strongest tape (+4%+); Indian-ownership / Instamart optionality still in play |
| 5 | BAJFINANC | Bullish | Med | 62 | BreakHighMe + strong AUM update; results later (30 Jul) so more momentum than news today |

Still state **Collection: `[name]`** in the report header.

## Format — multiple tables (required when 2+ collections)

When the user gives more than one scan table, **every** lead / horizon / snapshot
row must include the table (collection) name:

| Priority | Table | Symbol | Sentiment | Conviction | Prob% | Why |
|----------|-------|--------|-----------|------------|-------|-----|
| 1 | highBuy | TECHM | Bullish | High | 78 | Q1 results today + AnchisBuyUp / ReversalLow; already +2% into the print |
| 2 | buy_all_processor | ABB | Bullish | Med | 68 | MLBuy + NearHighYe; Moneycontrol spotlight buy after volume surge |
| 3 | highBuy | DIXON | Bullish | Med | 65 | BreakHighMe + Vivo JV still the live story |
| 4 | morning-volume-breakout-buy | SWIGGY | Bullish | High | 72 | MLBuy + strongest tape (+4%+) |
| 5 | highBuy | BAJFINANC | Bullish | Med | 62 | BreakHighMe + AUM update; results later |

Rules:
- Use the collection short name (e.g. `highBuy`) or `db.collection` if ambiguous across DBs.
- Do **not** drop Table / Sentiment / Conviction / Prob% from detail tables when multi-source.
- Same symbol from two tables → **two rows**, each with its own Table and scores.
- Optional: group with `### Table: <name>` sections, but the Table column is still required on merged boards.

## Field values

| Field | Allowed |
|-------|---------|
| Sentiment | `Bullish` · `Bearish` · `Neutral` · `Mixed` |
| Conviction | `High` · `Med` · `Low` |
| Prob% | Integer 0–100 (from helper `probability_score`) |

Prefer helper-emitted values from `query_suggestions.py`; polish with news per
[conviction-sentiment.md](conviction-sentiment.md).

## Building Why from ALL columns

1. Collect tag strings from every non-null scan field that looks like a signal (`filter*`, `*tech`, `ml*`, `keyIndicator`, processor flags).
2. Add numeric tape: `PCT_day_change`, `PCT_change`, `Ldchange`, volume spikes.
3. Add news one-liner if found.
4. Compress into **one sentence** (≤160 chars preferred).

## Priority ordering

1. Higher **probability_score** then horizon score + better R:R  
2. Live news catalyst for this horizon  
3. Stronger structural tags (BreakHighY > BreakHighMe > ReversalLow alone)  
4. Prefer unique scrips (dedupe repeated scan rows **within the same table**; across tables keep both and label Table)

## Do not

- Invent tags not on the document
- Use only price % while ignoring `ml` / `filter` / `intradaytech`
- Omit the Priority table even if the user asks for a single horizon
- Omit **Table** when multiple collections were queried
- Omit **Sentiment**, **Conviction**, or **Prob%** from report results
