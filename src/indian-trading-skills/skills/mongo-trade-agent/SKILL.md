---
name: mongo-trade-agent
description: >-
  Connect to local MongoDB (Nsedata/chartlink), query one or more given scan
  tables using ALL document columns, and return ranked suggestions for
  intraday, 3-5 days, short-term, and long-term with
  Priority|Symbol|LastDay%|Today%|Why (Table when multiple collections) plus
  Sentiment, Conviction, Prob%, News catalyst, and May extend?. MUST emit the
  full report (Priority, Executive Summary, News, Scan Columns, horizon tables,
  Avoid, Disclaimer) and MUST place Cursor Canvas last. Orange-row,
  MLBuy/MLSell token, and News catalyst sentiment highlights (green/red/yellow)
  per pct-highlight + news-extension rules. Use for Mongo trade ideas,
  chartlink/Nsedata scans, or Claude/Cursor/Copilot Mongo trading agent setup.
---

# Mongo Trade Agent

Local MongoDB → **full scan-row columns** → ranked multi-horizon suggestions.

## Hard requirements (never skip)

For **every** buy/sell / multi-horizon query after scoring:

| # | Block | Required? |
|---|--------|-----------|
| 1 | **Priority** markdown table in chat | **MUST** |
| 2 | **Executive Summary** (+ horizon bias table) | **MUST** |
| 3 | **News & Extension Snapshot** | **MUST** |
| 4 | **Scan Columns Used** | **MUST** |
| 5 | **Horizon detail table(s)** for the asked horizon(s) | **MUST** |
| 6 | **Watchlist / Avoid** | **MUST** |
| 7 | **Disclaimer** | **MUST** |
| 8 | **Cursor Canvas** (**new file** + link; never overwrite) | **MUST — last in the reply** |

**Do not** stop after Priority. **Do not** put Canvas before Executive Summary or
other tables. Thin / missing collections shrink rows — they do **not** allow
omitting these blocks (state “not available / no candidates” in the section).

Template: [../nsedata-trade-advisor/assets/four-horizon-report.md](../nsedata-trade-advisor/assets/four-horizon-report.md).  
Canvas rules: [references/priority-canvas.md](references/priority-canvas.md).  
**Fixed Canvas snippet (copy every query):** [assets/priority-canvas-snippet.tsx](assets/priority-canvas-snippet.tsx).

## Priority picks → Chat (early) + Canvas (last)

Present the same Priority board in **two places**, in this order:

1. **Early in chat** — full markdown Priority table (all columns; readable inline)
2. **After all other report tables** — create a **brand-new** Cursor Canvas and
   link it (colours: orange rows + MLBuy / MLSell tokens + News catalyst
   green/red/yellow). **Never overwrite** a previous `.canvas.tsx`.

Chat strips HTML styles, so colours appear reliably only in Canvas — but the
markdown Priority table must still appear early in chat.

1. Read and follow the Cursor **canvas** skill.
2. Follow [references/priority-canvas.md](references/priority-canvas.md).
3. **MUST copy** [assets/priority-canvas-snippet.tsx](assets/priority-canvas-snippet.tsx)
   into a **new** file under `~/.cursor/projects/<workspace>/canvases/` named
   `{horizon}-priority-{collection}-{YYYYMMDD-HHmmss}.canvas.tsx` — fill `meta` /
   `picks` / `newsRows` only. Do **not** freestyle highlights or use `Pill tone`
   (SDK ignores tones). Do **not** reuse `intraday-priority-picks.canvas.tsx`.
4. **MUST** open the new file via `open_resource`
   (`file:///C:/Users/.../canvases/<unique>.canvas.tsx`). On Windows, do **not**
   use markdown `[label](C:/...)` links (known Cursor bug — clicks fail).
5. Chat order: Priority markdown → **must** Executive Summary → News → Scan
   Columns → horizon tables → Avoid → Disclaimer → **Canvas basename last**
   (backticks + “opened beside chat”).

### Column shapes (chat + Canvas)

| Priority | Symbol | LastDay% | Today% | Sentiment | Conviction | Prob% | Why |
|----------|--------|----------|--------|-----------|------------|-------|-----|

**Multi-table:** add **Table** after Priority.

### Highlight rules (Canvas; mark in chat Why / News when useful)

| Rule | Action |
|------|--------|
| Buy + (`LastDay% > 3` **or** `Today% > 3`) | Full row background light orange `#FFE4C4` |
| Sell + (`LastDay% < -3` **or** `Today% < -3`) | Full row background light orange `#FFE4C4` |
| DB data contains `MLBuy` | Highlight token **MLBuy** light green `#C6F6D5` (in Why) |
| DB data contains `MLSell` | Highlight token **MLSell** light red `#FEB2B2` (in Why) |
| News catalyst **Positive** | News cell light green `#C6F6D5` |
| News catalyst **Negative** | News cell light red `#FEB2B2` |
| News catalyst **Mixed** | News cell light yellow `#FEFCBF` |
| News **Neutral** / `No fresh news` | No news colour |
| Sentiment **Bullish** + news **Positive** | Sentiment cell light green `#C6F6D5` |
| Sentiment **Bearish** + news **Negative** | Sentiment cell light red `#FEB2B2` |

- **LastDay%** ← `PCT_day_change_pre1` / `Ldchange` / `ldchange`
- **Today%** ← `PCT_day_change`
- Helper fields: `last_day_pct`, `today_pct`, `ml_buy`, `ml_sell`, `row_highlight_orange`

Full detail: [references/pct-highlight.md](references/pct-highlight.md).  
News colours: [references/news-extension.md](references/news-extension.md).  
Sentiment / Conviction / Prob% rules: [references/conviction-sentiment.md](references/conviction-sentiment.md).

Also include **News catalyst** and **May extend?** for each pick (with news highlight).

## Prerequisites

| Item | Default |
|------|---------|
| MongoDB | `mongodb://localhost:27017` |
| Databases | `Nsedata`, `chartlink` |
| Helper | `skills/nsedata-trade-advisor/scripts/query_suggestions.py` |
| News | Web search / **india-news-tracker** |
| Priority UI | **Chat table early + Cursor Canvas last** ([priority-canvas.md](references/priority-canvas.md)) |

Platform setup: [references/platform-setup.md](references/platform-setup.md).  
Why / column rules: [references/priority-why.md](references/priority-why.md).

## When Invoked

1. Ping Mongo (MCP or helper).
2. Resolve given table(s) (`buy_all_processor` → `chartlink`, etc.). If the user
   names **more than one** collection/table, treat each as a separate scan source.
3. **Discover all fields** on sample docs per collection (`collection-schema` or
   helper `scan_columns`) — do not drop columns.
4. Score horizons with `query_suggestions.py` **once per collection** (keeps full
   scan payload + `why_hint` + **sentiment / conviction / probability_score** +
   **last_day_pct / today_pct / ml_* / row_highlight_orange**).
   Tag every ranked row with `db.collection` / table name.
5. Enrich top symbols with news → fill News catalyst / May extend?; polish
   Sentiment / Conviction / Prob% if news conflicts (see conviction-sentiment.md).
   Prefer **persisted** copy in `Nsedata.scrip_news` (see ingest below) before
   live web search.
6. **Show Priority board in chat** (markdown table only at this point).
7. **MUST** present Executive Summary, News & Extension Snapshot, Scan Columns
   Used, asked horizon detail table(s), Watchlist/Avoid, and Disclaimer from
   [../nsedata-trade-advisor/assets/four-horizon-report.md](../nsedata-trade-advisor/assets/four-horizon-report.md).
8. **MUST** create a **new** Canvas file (unique timestamped name) and **end
   the reply** with the Canvas link ([priority-canvas.md](references/priority-canvas.md)).
   Open it with `open_resource` when possible.

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

Do not dump raw JSON. Summarize into the full report template; Canvas last.

## Persist scan news (last 5 days)

Use skill **`scan-news-conviction`** (not this folder’s scripts):

```bash
python skills/scan-news-conviction/scripts/ingest_scan_news.py
```

High-impact, ≤7-day, deduped news + sentiment + conviction → `Nsedata.scrip_news`.
Overwrite the scrip document if it is older than 30 days. See
[../scan-news-conviction/SKILL.md](../scan-news-conviction/SKILL.md).

## Use ALL Scan Columns

Never score from a fixed shortlist only. Read every field on the row, especially:

- Identity: `scrip`, `industry`, `index`, `date` / `eventtime`
- Tape: `open`/`high`/`low`/`close`/`volume`, `PCT_change`, `PCT_day_change`,
  `PCT_day_change_pre1`, `Ldchange` (if present), pre1–pre5 trails
- Tags: `filter`…`filter6`, `filterbuy`/`filtersell`, `intradaytech`, `shorttermtech`, `ml`, `mlData`, `keyIndicator`
- Structure: week/month/year high-low changes, forecasts `forecast_day_PCT*_change`
- Chartlink extras: `tobuy`/`tosell`, `processor`, `resultDeclared`

**Why** must quote the concrete tags present (e.g. `BreakHighMe`, `AnchisBuyUp`, `ReversalLow`, `#TOP5B###`, `NearHighYe`).

## Multiple Tables — Table Name Rules

If the user gives **2+ tables/collections**:

1. **Never omit the table name** in any ranked result, Priority pick, horizon
   detail row, News snapshot, or Watchlist/Avoid row.
2. Lead with **Priority | Table | Symbol | LastDay% | Today% | Sentiment | Conviction | Prob% | Why** (chat; Canvas mirrors this at end).
3. Header must list all sources, e.g.  
   `Collections: Nsedata.highBuy, chartlink.buy_all_processor`
4. Prefer one merged Priority board across tables; if keeping separate boards,
   use a clear `### Table: <name>` heading before each board.
5. Horizon detail tables add a **Table** column (or a section per table).
6. When the same symbol appears in multiple tables, keep separate rows (do not
   collapse) and show each source table.

Single-table runs may omit the Table column, but still state **Collection: `[name]`**
in the report header — and **must** keep LastDay% / Today% / Sentiment / Conviction / Prob%.

## Required Report Blocks (in order — mandatory)

1. **Priority board in chat (markdown)** — LastDay% · Today% · Sentiment · Conviction · Prob% · Why (+ Table if multi). Do **not** put the Canvas link here.
2. **Executive Summary** (+ horizon bias table) — **MUST** (**Table** column if multi-source)
3. **News & Extension Snapshot** — **MUST**
4. **Scan Columns Used** — **MUST** (per table when multi-source)
5. **Detailed horizon table(s)** for the horizon(s) the user asked — **MUST** — include **LastDay% · Today% · Sentiment · Conviction · Prob%** (and Table if multi). If only intraday was asked, still emit the Intraday detail table; omit other horizon sections only when not requested.
6. **Watchlist / Avoid** — **MUST** (include Table when multi-source; say “none” if empty)
7. **Disclaimer** — **MUST**
8. **Cursor Canvas** — **MUST be last**: create a **new** uniquely named `.canvas.tsx` (never overwrite), **always** open via `open_resource` (`file:///...`), then end with the basename in backticks (no `C:` markdown links on Windows) + one-line note that colours are in Canvas

### Required result fields (every pick)

| Field | Values |
|-------|--------|
| LastDay% | Signed % from prior session (or `—`) |
| Today% | Signed % today / session (or `—`) |
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
- [ ] Step 4: Run query_suggestions.py (once per table) — read sentiment/conviction/probability_score + last_day_pct/today_pct/ml_*/row_highlight_orange
- [ ] Step 5: News enrich top ranked symbols (`Nsedata.scrip_news` then live search); polish Sentiment/Conviction/Prob% if needed
- [ ] Step 6: Priority markdown table in chat (no Canvas link yet)
- [ ] Step 7: MUST — Executive Summary (+ horizon bias)
- [ ] Step 8: MUST — News & Extension Snapshot; Fill News catalyst + May extend?
- [ ] Step 9: MUST — Scan Columns Used + asked horizon detail table(s) + Watchlist/Avoid + Disclaimer
- [ ] Step 10: MUST LAST — Create new timestamped Cursor Canvas (never overwrite); open_resource + link at end of reply
- [ ] Step 11 (optional/persist): Save High-conviction top-2 for 3–5d / short / long via mongo-ai-analysis
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
- **cursor canvas** — coloured Priority UI (**last** in reply; after full chat tables)
