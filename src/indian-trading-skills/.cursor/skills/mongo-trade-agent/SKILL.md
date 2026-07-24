---
name: mongo-trade-agent
description: >-
  Connect to local MongoDB (Nsedata/chartlink), query one or more scan tables
  using ALL document columns, and return ranked suggestions with
  Priority|Symbol|Why (add Table when multiple collections) plus Sentiment,
  Conviction, Prob%, News catalyst, and May extend?. Persist High-conviction
  top-2 via mongo-ai-analysis into Nsedata.ai-analysis when asked to save.
---

# Mongo Trade Agent (Cursor)

Canonical: [`skills/mongo-trade-agent/SKILL.md`](../../../skills/mongo-trade-agent/SKILL.md)

1. Run `query_suggestions.py` on each given collection (once per table if multiple).
2. Use **all** `scan_columns` / `scan_row` fields.
3. Lead report with **Priority | Symbol | Sentiment | Conviction | Prob% | Why** — add **Table** when multiple tables.
4. Fill News catalyst + May extend?
5. Template: `skills/nsedata-trade-advisor/assets/four-horizon-report.md`.
6. To save picks: `skills/mongo-ai-analysis/SKILL.md` + `save_ai_analysis.py`.
