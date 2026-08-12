# Claude — Indian Trading Skills

## Mongo Trade Agent

For local MongoDB multi-horizon trade/investment suggestions:

- Skill: `skills/mongo-trade-agent/SKILL.md`
- Why rules: `skills/mongo-trade-agent/references/priority-why.md`
- Scoring: `skills/mongo-trade-agent/references/conviction-sentiment.md`
- Helper: `skills/nsedata-trade-advisor/scripts/query_suggestions.py`
- Report: `skills/nsedata-trade-advisor/assets/four-horizon-report.md`

**Always:**
1. Use **all columns** from the given scan collection document(s).
2. Lead with **Priority | Symbol | LastDay% | Today% | Sentiment | Conviction | Prob% | Why** — add **Table** when multiple tables are given.
3. **MUST** then emit Executive Summary, News & Extension Snapshot, Scan Columns, asked horizon detail table(s), Watchlist/Avoid, Disclaimer (template `four-horizon-report.md`). Do not stop at Priority.
4. **MUST put Cursor Canvas last** — copy `skills/mongo-trade-agent/assets/priority-canvas-snippet.tsx` into a **new** uniquely named `.canvas.tsx` every query (never overwrite; never `Pill tone` — use Text + backgroundColor), **always** open via `open_resource` (`file:///...`), mention basename after Disclaimer. On Windows avoid `[label](C:/...)` links. Colours render in Canvas; chat keeps the full tables.
5. Highlights (Canvas snippet): buy Symbol orange if LastDay% or Today% > 3; sell orange if LastDay% or Today% < -3; colour **MLBuy** / **MLSell** tokens in Why via Text `#C6F6D5` / `#FEB2B2`; **News catalyst** Positive `#C6F6D5` / Negative `#FEB2B2` / Mixed `#FEFCBF`; **Sentiment** green when Bullish + positive news, red when Bearish + negative news.
6. Include News catalyst and May extend?.
7. Disclaimer: educational, not SEBI advice — then Canvas.
8. % / colour detail: `skills/mongo-trade-agent/references/pct-highlight.md`; news colours: `skills/mongo-trade-agent/references/news-extension.md`

## Mongo AI Analysis (persist)

- Skill: `skills/mongo-ai-analysis/SKILL.md`
- Helper: `skills/nsedata-trade-advisor/scripts/save_ai_analysis.py`
- Collection: `Nsedata.ai-analysis`
- High conviction top 2 for 3–5 days / short-term / long-term only
- Save entry, targets, stoploss, R:R, sentiment/conviction/Prob%, last 5 trading days
- Do not re-insert when `dedupe_key` exists

Default URI: `mongodb://localhost:27017` (`Nsedata`, `chartlink`).
