---
name: mongo-ai-analysis
description: >-
  Persist high-conviction (top 2) Mongo trade suggestions for 3–5 days,
  short-term, and long-term into local Nsedata.ai-analysis. Saves sentiment,
  conviction, Prob%, entry, targets, stoploss, R:R, and last 5 trading days
  (skipping holidays). Skips duplicates. Use when asked to save AI analysis,
  write ai-analysis collection, or persist multi-horizon picks from scan tables.
---

# Mongo AI Analysis (Persist)

Score scan tables with **mongo-trade-agent** / `query_suggestions.py`, then save
**High conviction · top 2 only** into local MongoDB collection:

`Nsedata.ai-analysis`

## Logical tables (horizon partitions)

One physical collection; three logical tables via `table_name` / `horizon`:

| Logical table | `horizon` | `table_name` |
|---------------|-----------|--------------|
| 3–5 days | `swing3_5` | `ai-analysis-3-5-days` |
| Short-term | `short_term` | `ai-analysis-short-term` |
| Long-term | `long_term` | `ai-analysis-long-term` |

Intraday is **not** persisted here.

## Prerequisites

| Item | Default |
|------|---------|
| MongoDB | `mongodb://localhost:27017` |
| Target | `Nsedata.ai-analysis` |
| Source DBs | `Nsedata`, `chartlink` |
| Helper | `skills/nsedata-trade-advisor/scripts/save_ai_analysis.py` |

## When Invoked

1. Ping Mongo.
2. Ensure collection + indexes:
   ```bash
   python skills/nsedata-trade-advisor/scripts/save_ai_analysis.py --setup-only
   ```
3. Run save against **existing scan table name(s)** or **raw JSON**:
   ```bash
   # Existing table
   python skills/nsedata-trade-advisor/scripts/save_ai_analysis.py \
     --db Nsedata --collection highBuy --limit 25

   # Multiple tables, last 5 trading days of scan dates
   python skills/nsedata-trade-advisor/scripts/save_ai_analysis.py \
     --db Nsedata --collections breakoutW2HR,breakoutMHR,breakoutM2HR \
     --last-trading-days 5 --limit 100

   # Raw scan docs / prior report candidates
   python skills/nsedata-trade-advisor/scripts/save_ai_analysis.py \
     --raw-json path/to/scans_or_report.json --source-table manual_raw
   ```
4. Present a short summary: inserted vs skipped, top-2 per horizon with
   **entry / T1–T2(–T3) / stoploss / R:R / sentiment / conviction / Prob%**.

## Persistence rules (mandatory)

1. **High conviction only** — drop Med/Low.
2. **Top 2 per horizon per source table**.
3. Save **sentiment**, **conviction**, **probability_score**.
4. Save **entry**, **targets** (`t1`/`t2`/`t3`), **stoploss**, **risk_reward**.
5. Attach **last_5_trading_days** from `Nsedata.history`:
   - Skip weekends
   - Skip NSE holidays
   - Skip zero-volume bars
6. **Do not insert again** if `dedupe_key` already exists  
   (`horizon|source_db|source_table|symbol|analysis_date`).

## Document shape (each saved pick)

```json
{
  "horizon": "swing3_5",
  "horizon_label": "3-5 days",
  "table_name": "ai-analysis-3-5-days",
  "source_db": "Nsedata",
  "source_table": "highBuy",
  "symbol": "TECHM",
  "date": "2026-07-17",
  "insertion_date": "2026-07-19",
  "insertion_datetime": "2026-07-19T23:05:00",
  "analysis_date": "2026-07-17",
  "rank": 1,
  "conviction": "High",
  "sentiment": "Bullish",
  "probability_score": 78,
  "entry": 1520.0,
  "targets": {"t1": 1545.0, "t2": 1560.0},
  "stoploss": 1490.0,
  "risk_reward": 1.8,
  "last_5_trading_days": [{"date": "...", "open": 0, "high": 0, "low": 0, "close": 0, "volume": 0}],
  "dedupe_key": "swing3_5|Nsedata|highBuy|TECHM|2026-07-17"
}
```

**Date fields:**
| Field | Meaning |
|-------|---------|
| `date` | From source scan table (`date` / `eventtime`); **`NA`** if missing |
| `insertion_date` | Calendar date when the doc was written |
| `insertion_datetime` | Full timestamp of insert |
| `analysis_date` | Last trading bar date from history (informational) |

## Query saved analysis

```javascript
// All 3–5 day picks for a date
db.getSiblingDB("Nsedata")["ai-analysis"].find({
  table_name: "ai-analysis-3-5-days",
  analysis_date: "2026-07-18"
})

// Short-term High conviction for a symbol
db.getSiblingDB("Nsedata")["ai-analysis"].find({
  horizon: "short_term",
  symbol: "TECHM"
})
```

## Report to user

Lead with three mini-tables (one per logical table), High conviction top 2 only:

| Rank | Source table | Symbol | Sentiment | Conviction | Prob% | Entry | T1 | T2 | SL | R:R |
|------|--------------|--------|-----------|------------|-------|-------|----|----|----|-----|

State inserted vs skipped counts. Disclaimer: educational, not SEBI advice.

## Related

- **mongo-trade-agent** — full multi-horizon report (includes intraday)
- **nsedata-trade-advisor** — scoring engine
