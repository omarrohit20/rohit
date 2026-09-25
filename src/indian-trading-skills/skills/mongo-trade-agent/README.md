# Mongo Trade Agent

Ranked **intraday / 3–5 day / short-term / long-term** trade ideas from local MongoDB scan tables (`Nsedata`, `chartlink`). Uses **every column** on the scan row, then news, sentiment, and conviction.

Agent instructions: [SKILL.md](SKILL.md).

## What it does

1. Connects to `mongodb://localhost:27017`.
2. Reads one or more scan collections you name.
3. Scores suggestions with `query_suggestions.py` (once per collection).
4. Enriches top symbols from `Nsedata.scrip_news` (then live news if needed).
5. Returns a full report in chat, with a **new** Cursor Canvas last.

It does **not** scrape news itself. Refresh news first with [scan-news-conviction](../scan-news-conviction/README.md) and/or [scan-news-conviction-futures](../scan-news-conviction-futures/README.md).

## Prerequisites

- MongoDB running; databases `Nsedata` and `chartlink`
- `pip install pymongo`
- Helper: `skills/nsedata-trade-advisor/scripts/query_suggestions.py`

Platform (Cursor / Claude / Copilot MCP): [references/platform-setup.md](references/platform-setup.md).

## Score a scan table

From `indian-trading-skills/`:

```bash
python skills/nsedata-trade-advisor/scripts/query_suggestions.py \
  --db chartlink --collection buy_all_processor --limit 25 --horizons intraday
```

Multiple tables — run once per collection, then merge in the report with a **Table** column:

```bash
python skills/nsedata-trade-advisor/scripts/query_suggestions.py \
  --db Nsedata --collection highBuy --limit 25 --horizons all
python skills/nsedata-trade-advisor/scripts/query_suggestions.py \
  --db chartlink --collection buy_all_processor --limit 25 --horizons all
```

Do not dump raw JSON. Summarize into the report template.

## Report order (required)

1. **Priority** markdown table (chat, early)
2. Executive Summary
3. News & Extension Snapshot
4. Scan Columns Used
5. Horizon detail table(s) for the asked horizon(s)
6. Watchlist / Avoid
7. Disclaimer
8. **Cursor Canvas last** — copy [assets/priority-canvas-snippet.tsx](assets/priority-canvas-snippet.tsx) into a **new** uniquely named `.canvas.tsx` (never overwrite)

Template: [../nsedata-trade-advisor/assets/four-horizon-report.md](../nsedata-trade-advisor/assets/four-horizon-report.md).  
Canvas rules: [references/priority-canvas.md](references/priority-canvas.md).

### Priority columns

| Priority | Symbol | LastDay% | Today% | Sentiment | Conviction | Prob% | Why |
|----------|--------|----------|--------|-----------|------------|-------|-----|

Multi-table: add **Table** after Priority. Also fill **News catalyst** and **May extend?** (`Yes` / `Possible` / `Only if X` / `Weak` / `No`).

## Persist picks (optional)

High-conviction top 2 for 3–5 days / short-term / long-term → `Nsedata.ai-analysis` via **mongo-ai-analysis**:

```bash
python skills/nsedata-trade-advisor/scripts/save_ai_analysis.py --setup-only
python skills/nsedata-trade-advisor/scripts/save_ai_analysis.py \
  --db <DB> --collection <SCAN_TABLE> --limit 25
```

## Related files

| Path | Role |
|------|------|
| [SKILL.md](SKILL.md) | Agent workflow |
| [references/priority-why.md](references/priority-why.md) | Why / scan tags |
| [references/conviction-sentiment.md](references/conviction-sentiment.md) | Sentiment, conviction, Prob% |
| [references/pct-highlight.md](references/pct-highlight.md) | LastDay% / Today% / orange rows |
| [references/news-extension.md](references/news-extension.md) | News catalyst colours |

Educational analysis only — not SEBI-registered advice.
