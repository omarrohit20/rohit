# Copilot Instructions — Indian Trading Skills

## Mongo Trade Agent

When querying local Mongo / scan tables for **intraday / 3–5 day / short-term / long-term** ideas:

1. Follow `skills/mongo-trade-agent/SKILL.md` and `AGENTS.md`.
2. URI `mongodb://localhost:27017` — DBs `Nsedata`, `chartlink`.
3. Run once per collection (if multiple tables are given, run for each):

```bash
python skills/nsedata-trade-advisor/scripts/query_suggestions.py --db <DB> --collection <NAME> --limit 20 --horizons all
```

4. Consider **every column** on the scan row (`scan_columns` / `scan_row` / tags in `why_hint`).
5. **Lead output** with Sentiment, Conviction, and Prob% on every pick:

**Single table:**

| Priority | Symbol | Sentiment | Conviction | Prob% | Why |
|----------|--------|-----------|------------|-------|-----|
| 1 | SYMBOL | Bullish | High | 78 | tags + % move + news |

**Multiple tables:** include table name on every result row:

| Priority | Table | Symbol | Sentiment | Conviction | Prob% | Why |
|----------|-------|--------|-----------|------------|-------|-----|
| 1 | highBuy | SYMBOL | Bullish | High | 78 | tags + % move + news |

6. Add News catalyst + May extend? for each pick (keep Table when multi-source).
7. Full template: `skills/nsedata-trade-advisor/assets/four-horizon-report.md`.
8. To **persist** High-conviction top-2 (3–5d / short / long) into `Nsedata.ai-analysis`, follow `skills/mongo-ai-analysis/SKILL.md` and run `save_ai_analysis.py`.

## General

- Prefer repo skills/scripts over inventing prices.
- Read-only Mongo unless the user asks to save into `ai-analysis` (or otherwise write).
