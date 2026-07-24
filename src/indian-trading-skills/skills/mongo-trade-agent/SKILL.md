---
name: mongo-trade-agent
description: >-
  Connect to local MongoDB (Nsedata/chartlink), query one or more given scan
  tables using ALL document columns, and return ranked suggestions for
  intraday, 3-5 days, short-term, and long-term with Priority|Symbol|Why
  (Table when multiple collections) plus Sentiment, Conviction, Prob%, News
  catalyst, and May extend?. Use for Mongo trade ideas, chartlink/Nsedata
  scans, or Claude/Cursor/Copilot Mongo trading agent setup.
---

# Mongo Trade Agent

Local MongoDB → **full scan-row columns** → ranked multi-horizon suggestions.

Required user-facing lead section (single table):

| Priority | Symbol | Sentiment | Conviction | Prob% | Why |
|----------|--------|-----------|------------|-------|-----|
| 1 | … | Bullish | High | 78 | scan tags + tape + news in one sentence |

**When multiple tables/collections are given**, every report and result row
**must** include the table name:

| Priority | Table | Symbol | Sentiment | Conviction | Prob% | Why |
|----------|-------|--------|-----------|------------|-------|-----|
| 1 | highBuy | … | Bullish | High | 78 | … |
| 2 | buy_all_processor | … | Bullish | Med | 65 | … |

Also include **News catalyst** and **May extend?** for each pick.

Sentiment / Conviction / Prob% rules: [references/conviction-sentiment.md](references/conviction-sentiment.md).

## Prerequisites

| Item | Default |
|------|---------|
| MongoDB | `mongodb://localhost:27017` |
| Databases | `Nsedata`, `chartlink` |
| Helper | `skills/nsedata-trade-advisor/scripts/query_suggestions.py` |
| News | Web search / **india-news-tracker** |

Platform setup: [references/platform-setup.md](references/platform-setup.md).  
Why / column rules: [references/priority-why.md](references/priority-why.md).

## When Invoked

1. Ping Mongo (MCP or helper).
2. Resolve given table(s) (`buy_all_processor` → `chartlink`, etc.). If the user
   names **more than one** collection/table, treat each as a separate scan source.
3. **Discover all fields** on sample docs per collection (`collection-schema` or
   helper `scan_columns`) — do not drop columns.
4. Score horizons with `query_suggestions.py` **once per collection** (keeps full
   scan payload + `why_hint` + **sentiment / conviction / probability_score**).
   Tag every ranked row with `db.collection` / table name.
5. Enrich top symbols with news → fill News catalyst / May extend?; polish
   Sentiment / Conviction / Prob% if news conflicts (see conviction-sentiment.md).
6. Present [../nsedata-trade-advisor/assets/four-horizon-report.md](../nsedata-trade-advisor/assets/four-horizon-report.md):
   - One table → **Priority | Symbol | Sentiment | Conviction | Prob% | Why**
   - Multiple tables → **Priority | Table | Symbol | Sentiment | Conviction | Prob% | Why**

```bash
# Single table
python skills/nsedata-trade-advisor/scripts/query_suggestions.py \
  --db chartlink --collection buy_all_processor --limit 25 --horizons intraday

# Multiple tables — run once per collection, then merge in the report with Table column
python skills/nsedata-trade-advisor/scripts/query_suggestions.py \
  --db Nsedata --collection highBuy --limit 25 --horizons all
python skills/nsedata-trade-advisor/scripts/query_suggestions.py \
  --db chartlink --collection buy_all_processor --limit 25 --horizons all
```

Do not dump raw JSON. Summarize into the report template.

## Use ALL Scan Columns

Never score from a fixed shortlist only. Read every field on the row, especially:

- Identity: `scrip`, `industry`, `index`, `date` / `eventtime`
- Tape: `open`/`high`/`low`/`close`/`volume`, `PCT_change`, `PCT_day_change`, `Ldchange` (if present), pre1–pre5 trails
- Tags: `filter`…`filter6`, `filterbuy`/`filtersell`, `intradaytech`, `shorttermtech`, `ml`, `mlData`, `keyIndicator`
- Structure: week/month/year high-low changes, forecasts `forecast_day_PCT*_change`
- Chartlink extras: `tobuy`/`tosell`, `processor`, `resultDeclared`

**Why** must quote the concrete tags present (e.g. `BreakHighMe`, `AnchisBuyUp`, `ReversalLow`, `#TOP5B###`, `NearHighYe`).

## Multiple Tables — Table Name Rules

If the user gives **2+ tables/collections**:

1. **Never omit the table name** in any ranked result, Priority pick, horizon
   detail row, News snapshot, or Watchlist/Avoid row.
2. Lead with **Priority | Table | Symbol | Sentiment | Conviction | Prob% | Why**.
3. Header must list all sources, e.g.  
   `Collections: Nsedata.highBuy, chartlink.buy_all_processor`
4. Prefer one merged Priority board across tables; if keeping separate boards,
   use a clear `### Table: <name>` heading before each board.
5. Horizon detail tables add a **Table** column (or a section per table).
6. When the same symbol appears in multiple tables, keep separate rows (do not
   collapse) and show each source table.

Single-table runs may omit the Table column, but still state **Collection: `[name]`**
in the report header — and **must** keep Sentiment / Conviction / Prob%.

## Required Report Blocks (in order)

1. Priority board with **Sentiment · Conviction · Prob% · Why** (add Table if multi)
2. Executive summary + horizon bias table (**Table** column if multi-source)
3. News & Extension Snapshot (include Sentiment / Conviction / Prob% when useful; **Table** if multi)
4. Scan Columns Used (per table when multi-source)
5. Detailed horizon tables — include **Sentiment · Conviction · Prob%** (and Table if multi)
6. Watchlist / Avoid (include Table when multi-source)
7. Disclaimer

### Required result fields (every pick)

| Field | Values |
|-------|--------|
| Sentiment | `Bullish` · `Bearish` · `Neutral` · `Mixed` |
| Conviction | `High` · `Med` · `Low` |
| Prob% | Integer 0–100 (`probability_score` from helper) |
| May extend? | `Yes` · `Possible` · `Only if X` · `Weak` · `No` |

### Why sentence pattern

`[strongest scan tags] + [tape/%] + [news or momentum-only] [; extension cue]`

Example: `Q1 results today + AnchisBuyUp / ReversalLow; already +2% into the print`

## Workflow Checklist

```
Task Progress:
- [ ] Step 1: Ping Mongo
- [ ] Step 2: Resolve db + collection(s) — note if multiple tables
- [ ] Step 3: List ALL columns from sample docs (per table)
- [ ] Step 4: Run query_suggestions.py (once per table) — read sentiment/conviction/probability_score
- [ ] Step 5: News enrich top ranked symbols; polish Sentiment/Conviction/Prob% if needed
- [ ] Step 6: Build Priority board with Sentiment|Conviction|Prob%|Why (+ Table if multi)
- [ ] Step 7: Fill News catalyst + May extend?
- [ ] Step 8: Full report + disclaimer (never omit conviction/sentiment/prob%)
- [ ] Step 9 (optional/persist): Save High-conviction top-2 for 3–5d / short / long via mongo-ai-analysis
```

## Persist to `ai-analysis` (optional but preferred for swing+ horizons)

When the user asks to **save / store / persist** suggestions, or after a full report
for 3–5 days / short-term / long-term:

```bash
python skills/nsedata-trade-advisor/scripts/save_ai_analysis.py --setup-only
python skills/nsedata-trade-advisor/scripts/save_ai_analysis.py \
  --db <DB> --collection <SCAN_TABLE> --limit 25
```

Follow **mongo-ai-analysis**: High conviction top 2 only; entry/targets/SL/R:R;
last 5 trading days (no holidays); skip duplicates.

## Related Skills

- **mongo-ai-analysis** — persist High-conviction top-2 into `Nsedata.ai-analysis`
- **nsedata-trade-advisor** — scoring helper
- **mongodb-local-mcp** — MCP setup
- **india-news-tracker** — catalysts
