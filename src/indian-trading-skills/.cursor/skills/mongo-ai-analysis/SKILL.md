---
name: mongo-ai-analysis
description: >-
  Persist high-conviction top-2 suggestions (3–5 days, short-term, long-term)
  into Nsedata.ai-analysis with targets, stoploss, R:R, sentiment/conviction.
---

# Mongo AI Analysis (Cursor)

Canonical: [`skills/mongo-ai-analysis/SKILL.md`](../../../skills/mongo-ai-analysis/SKILL.md)

```bash
python skills/nsedata-trade-advisor/scripts/save_ai_analysis.py --setup-only
python skills/nsedata-trade-advisor/scripts/save_ai_analysis.py \
  --db Nsedata --collection highBuy --limit 25
```
