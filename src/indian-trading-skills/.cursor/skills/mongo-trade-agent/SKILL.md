---
name: mongo-trade-agent
description: >-
  Connect to local MongoDB (Nsedata/chartlink), query one or more scan tables
  using ALL document columns, and return ranked suggestions with
  Priority|Symbol|LastDay%|Today%|Why (add Table when multiple collections) plus
  Sentiment, Conviction, Prob%, News catalyst, and May extend?. Always show
  Priority picks in chat AND open them in a Cursor Canvas. Orange-row and
  MLBuy/MLSell token highlights. Persist High-conviction top-2 via
  mongo-ai-analysis into Nsedata.ai-analysis when asked to save.
---

# Mongo Trade Agent (Cursor)

Canonical: [`skills/mongo-trade-agent/SKILL.md`](../../../skills/mongo-trade-agent/SKILL.md)

1. Run `query_suggestions.py` on each given collection (once per table if multiple).
2. Use **all** `scan_columns` / `scan_row` fields.
3. Lead report with **Priority | Symbol | LastDay% | Today% | Sentiment | Conviction | Prob% | Why** — add **Table** when multiple tables.
4. **Always show Priority picks in chat (markdown table) AND open a Cursor Canvas** (colours in Canvas). Follow `skills/mongo-trade-agent/references/priority-canvas.md` + the Cursor canvas skill. Link the `.canvas.tsx` in chat.
5. Highlights (Canvas): buy row orange if LastDay% or Today% **> 3**; sell row orange if **< 3**; colour the **MLBuy** / **MLSell** tokens in Why (green / red) — not the scrip.
6. Fill News catalyst + May extend?
7. Template: `skills/nsedata-trade-advisor/assets/four-horizon-report.md` (chat remainder).
8. To save picks: `skills/mongo-ai-analysis/SKILL.md` + `save_ai_analysis.py`.
