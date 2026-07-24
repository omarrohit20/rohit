# Nsedata / Chartlink Schema Reference

Real local MongoDB layout used by **nsedata-trade-advisor**. Connection: `mongodb://localhost:27017`.

## Databases

| Database | Role |
|----------|------|
| `Nsedata` | Primary scans, daily/15m history, technicals, fundamentals, scrip master |
| `chartlink` | Morning / intraday scan processors |
| `nsehistnew` | Supplemental history / technical snapshots |

## Symbol Keys

| Context | Field |
|---------|-------|
| Scan collections | `scrip` |
| History / technical | `dataset_code` |
| Fundamentals | `scrip` |

Always join scans → history with `scrip` == `dataset_code`.

---

## Nsedata Collections

### Master & enrichment

| Collection | Purpose | Key fields |
|------------|---------|------------|
| `scrip` | Universe (~750) | `scrip`, `company`, `industry`, `index`, `futures` |
| `fundamental` | Valuation snapshot | `scrip`, `marketcap`, `peratio`, `netprofit`, `publicholding` |
| `technical` | Precomputed TA | `dataset_code`, `short_term`, `long_term`, `changeSMA*`, `yearHigh`/`yearLow`, Buy/Sell indicators |
| `sttips` | Filter tip stats | `scrip`, `filter`, `avg5`, `avg10`, `pct5`, `pct10` |
| `ai-analysis` | Persisted High-conviction AI picks (3–5d / short / long) | `horizon`, `table_name`, `source_table`, `symbol`, `date` (from source table or `NA`), `insertion_date`, `entry`, `targets`, `stoploss`, `risk_reward`, `conviction`, `sentiment`, `probability_score`, `last_5_trading_days`, `dedupe_key` |

### `ai-analysis` (persisted suggestions)

Created/managed by `skills/nsedata-trade-advisor/scripts/save_ai_analysis.py` and skill **mongo-ai-analysis**.

| Logical table (`table_name`) | `horizon` | Content |
|------------------------------|-----------|---------|
| `ai-analysis-3-5-days` | `swing3_5` | Top 2 High-conviction 3–5 day picks |
| `ai-analysis-short-term` | `short_term` | Top 2 High-conviction short-term picks |
| `ai-analysis-long-term` | `long_term` | Top 2 High-conviction long-term picks |

Unique on `dedupe_key` = `horizon|source_db|source_table|symbol|<table date or insertion_date>` (no re-insert).
`date` = source scan `date`/`eventtime` normalized to `YYYY-MM-DD`, or **`NA`** if absent.
`insertion_date` / `insertion_datetime` = when the document was written.

### OHLCV (embedded arrays)

Both `history` and `history15m` store one document per symbol:

```javascript
{
  dataset_code: "RELIANCE",
  name: "RELIANCE",
  end_date: "2026-07-15",          // or ISO with offset for 15m
  futures: "Yes",
  column_names: ["Date", "Open", "High", "Low", "Close", "Volume"],
  data: [
    ["2026-07-15", 1294.1, 1310.9, 1294.1, 1295.5, 9577497],  // NEWEST first
    // ... older bars
  ]
}
```

| Collection | Bars | Notes |
|------------|------|-------|
| `history` | ~5000 daily | Newest-first; use first N for recent lookback |
| `history15m` | ~200 fifteen-minute | Newest-first; last session for intraday |
| `historym` | Sparse | MoneyControl source; prefer `history` |

**Unpack rule:** map `column_names` → indices, reverse to chronological order before indicators.

### Scan / signal collections

| Collection | Typical use |
|------------|-------------|
| `highBuy` | Broad buy-side scan with ML forecasts, filters, MAs |
| `lowSell` | Sell-side counterpart |
| `breakoutMH`, `breakoutMHR`, `breakoutML`, `breakoutMLR` | Month high/low breakouts |
| `breakoutM2H`, `breakoutM2HR`, `breakoutM2L`, `breakoutM2LR` | 2-month breakouts |
| `breakoutYH`, `breakoutY2H` | Year / 2-year high breakouts |
| `breakoutW2HR`, `breakoutW2LR` | 2-week breakouts |
| `nearY5H` | Near 5-year high |
| `reversalY2LLT50`, `reversalY2LLT60`, `reversalY2LLT70` | Reversal from 2y low |
| `movingavg_crossed_up`, `movingavg_crossed_down` | MA cross events |
| `regressionhigh`, `regressionlow` | Regression channel extremes |
| `scrip_futures`, `resultScripFutures` | F&O / results universe |

### Common scan fields (`highBuy` and peers)

| Field | Meaning |
|-------|---------|
| `scrip`, `date`, `industry`, `index` | Identity |
| `open`, `high`, `low`, `close`, `volume` | Latest bar |
| `PCT_change`, `PCT_day_change` | % vs prior / day |
| `PCT_change_pre1`…`pre5`, `PCT_day_change_pre*` | Recent momentum trail |
| `filter`, `filter1`…`filter6`, `filterbuy`, `filtersell` | Signal tags (ReversalLow, BreakHigh, SMA tags) |
| `intradaytech`, `shorttermtech`, `ml`, `mlData` | Intraday / ML tags (`#TOP5B###`, `BreakHighMe`, …) |
| `forecast_day_PCT_change`, `forecast_day_PCT3/5/7/10_change` | Model day-horizon forecasts |
| `weekHighChange`, `weekLowChange`, `month*`, `year*` | Distance to structural highs/lows (%) |
| `SMA4/9/25/50/100/200`, `EMA6`, `EMA14` | MA position / slope proxies |
| `marketcap`, `peratio` | Often denormalized from fundamentals |

---

## Chartlink Collections

Morning/intraday processors. Documents are leaner than `highBuy` but share `scrip`, `PCT_*`, forecast, and structure-change fields.

Examples:

- `morning-volume-breakout-buy` / `morning-volume-breakout-sell`
- `breakout-morning-buy`
- `09_30:checkChartBuy`
- `09_30:checkChartBuy/Sell-morningDown(...)`
- `highBuy`, `lowSell` (mirrors)
- `crossed-day-high`, `crossed-day-low`
- `buy_all_processor`, `sell_all_processor`

Extra fields: `eventtime`, `systemtime`, `epochtime`, `processor`, `tobuy`, `tosell`, `keyIndicator`, `resultDeclared`.

---

## Horizon → Data Mapping

| Horizon | Scan inputs | OHLCV | Enrichment |
|---------|-------------|-------|------------|
| Intraday | `PCT_day_change`, `intradaytech`, `ml`/`mlData` | `history15m` (session) | chartlink morning collections |
| 3–5 days | `forecast_day_PCT3/5_change`, week high/low changes, Reversal/Break filters | `history` last ~10 days | — |
| Short-term (1–20d) | `technical.short_term`, SMA25/50, filter trails | `history` last 60 days | — |
| Long-term | `technical.long_term`, year high/low, PE | `history` last 252+ days | `fundamental` |

---

## Example MCP Queries

### Sample a scan collection

```json
{
  "database": "Nsedata",
  "collection": "highBuy",
  "filter": {},
  "sort": { "date": -1 },
  "limit": 30,
  "projection": {
    "scrip": 1, "date": 1, "close": 1, "PCT_change": 1, "PCT_day_change": 1,
    "industry": 1, "intradaytech": 1, "ml": 1, "filter3": 1, "filter5": 1,
    "forecast_day_PCT3_change": 1, "forecast_day_PCT5_change": 1,
    "weekHighChange": 1, "weekLowChange": 1, "yearHighChange": 1, "yearLowChange": 1
  }
}
```

### Fetch daily history doc

```json
{
  "database": "Nsedata",
  "collection": "history",
  "filter": { "dataset_code": "RELIANCE" },
  "limit": 1
}
```

### Fetch 15m history doc

```json
{
  "database": "Nsedata",
  "collection": "history15m",
  "filter": { "dataset_code": "RELIANCE" },
  "limit": 1
}
```

### Technical + fundamental

```json
{ "database": "Nsedata", "collection": "technical", "filter": { "dataset_code": "RELIANCE" }, "limit": 1 }
```

```json
{ "database": "Nsedata", "collection": "fundamental", "filter": { "scrip": "RELIANCE" }, "limit": 1 }
```

Prefer the Python helper for unpacking `data` arrays and computing indicators; MCP is best for discovery and sampling.

### Fetch saved AI analysis

```json
{
  "database": "Nsedata",
  "collection": "ai-analysis",
  "filter": { "table_name": "ai-analysis-3-5-days" },
  "sort": { "analysis_date": -1, "rank": 1 },
  "limit": 20
}
```
