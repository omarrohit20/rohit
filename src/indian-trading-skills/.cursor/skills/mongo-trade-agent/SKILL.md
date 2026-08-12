---
name: mongo-trade-agent
description: >-
  Connect to local MongoDB (Nsedata/chartlink), query one or more scan tables
  using ALL document columns, and return ranked suggestions with
  Priority|Symbol|LastDay%|Today%|Why (add Table when multiple collections) plus
  Sentiment, Conviction, Prob%, News catalyst, and May extend?. MUST emit full
  report (Priority, Executive Summary, News, Scan Columns, horizon tables,
  Avoid, Disclaimer) and MUST place Cursor Canvas last. Orange-row,
  MLBuy/MLSell, and News catalyst sentiment highlights (green/red/yellow).
  Persist High-conviction top-2 via mongo-ai-analysis into Nsedata.ai-analysis
  when asked to save.
---

# Mongo Trade Agent (Cursor)

Canonical: [`skills/mongo-trade-agent/SKILL.md`](../../../skills/mongo-trade-agent/SKILL.md)

1. Run `query_suggestions.py` on each given collection (once per table if multiple).
2. Use **all** `scan_columns` / `scan_row` fields.
3. Lead report with **Priority | Symbol | LastDay% | Today% | Sentiment | Conviction | Prob% | Why** — add **Table** when multiple tables.
4. **MUST** emit Executive Summary, News, Scan Columns, asked horizon tables, Avoid, Disclaimer (template `four-horizon-report.md`). Do not stop at Priority.
5. **MUST put Cursor Canvas last** — copy `skills/mongo-trade-agent/assets/priority-canvas-snippet.tsx` into a **new** uniquely named `.canvas.tsx` every query (never overwrite; never freestyle `Pill tone` highlights — use Text + backgroundColor); **always** open via `open_resource` (`file:///...`). On Windows do not use `[label](C:/...)` chat links. Follow `skills/mongo-trade-agent/references/priority-canvas.md` + the Cursor canvas skill.
6. Highlights (Canvas snippet): buy Symbol orange if LastDay% or Today% **> 3**; sell orange if **< -3**; colour the **MLBuy** / **MLSell** tokens in Why via Text `#C6F6D5` / `#FEB2B2` — not the scrip; **News catalyst** Positive `#C6F6D5` / Negative `#FEB2B2` / Mixed `#FEFCBF`; **Sentiment** green when Bullish + positive news, red when Bearish + negative news (`news-extension.md`).
7. Fill News catalyst + May extend?
8. To save picks: `skills/mongo-ai-analysis/SKILL.md` + `save_ai_analysis.py`.
