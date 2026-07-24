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
2. Lead with **Priority | Symbol | Sentiment | Conviction | Prob% | Why** — add **Table** when multiple tables are given.
3. Include News catalyst and May extend?.
4. Disclaimer: educational, not SEBI advice.

## Mongo AI Analysis (persist)

- Skill: `skills/mongo-ai-analysis/SKILL.md`
- Helper: `skills/nsedata-trade-advisor/scripts/save_ai_analysis.py`
- Collection: `Nsedata.ai-analysis`
- High conviction top 2 for 3–5 days / short-term / long-term only
- Save entry, targets, stoploss, R:R, sentiment/conviction/Prob%, last 5 trading days
- Do not re-insert when `dedupe_key` exists

Default URI: `mongodb://localhost:27017` (`Nsedata`, `chartlink`).
