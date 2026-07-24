# Agents — Indian Trading Skills

## Mongo Trade Agent (primary for local DB)

When the user asks for trade/investment ideas from **local MongoDB**, a **given table/collection**, or multi-horizon suggestions (**intraday**, **3–5 days**, **short-term**, **long-term**):

1. Read and follow `skills/mongo-trade-agent/SKILL.md`.
2. Connect to `mongodb://localhost:27017` (`Nsedata`, `chartlink`).
3. Run once per collection (if the user names multiple tables, run for each):

```bash
python skills/nsedata-trade-advisor/scripts/query_suggestions.py \
  --db <DB> --collection <COLLECTION> --limit 20 --horizons all
```

4. **Use ALL columns** from each scan document (`meta.scan_columns` / `scan_row`) — filters, ml/intradaytech, PCT/Ldchange, forecasts, etc. Do not score from a short fixed field list.
5. Lead the user report with Sentiment, Conviction, and Prob% on every pick:

**Single table:**

| Priority | Symbol | Sentiment | Conviction | Prob% | Why |
|----------|--------|-----------|------------|-------|-----|
| 1 | … | Bullish | High | 78 | scan tags + tape + news in one sentence |

**Multiple tables:** every result must include the table name:

| Priority | Table | Symbol | Sentiment | Conviction | Prob% | Why |
|----------|-------|--------|-----------|------------|-------|-----|
| 1 | highBuy | … | Bullish | High | 78 | … |
| 2 | buy_all_processor | … | Bullish | Med | 65 | … |

Example Why style: `Q1 results today + AnchisBuyUp / ReversalLow; already +2% into the print`

6. Also fill **News catalyst** and **May extend?** (`Yes` / `Possible` / `Only if X` / `Weak` / `No`). Keep **Table** on those rows when multi-source.
7. Use template `skills/nsedata-trade-advisor/assets/four-horizon-report.md`.
8. Disclaimer: educational only, not SEBI advice.

## Mongo AI Analysis (persist High-conviction picks)

When the user asks to **save / persist / store** suggestions into Mongo (or after a swing+ report):

1. Follow `skills/mongo-ai-analysis/SKILL.md`.
2. Target collection: `Nsedata.ai-analysis`.
3. Persist **High conviction · top 2 only** for **3–5 days**, **short-term**, **long-term** (logical tables via `table_name`).
4. Always store entry, targets, stoploss, risk_reward, sentiment, conviction, probability_score, last 5 trading days (no holidays).
5. Skip insert when `dedupe_key` already exists.

```bash
python skills/nsedata-trade-advisor/scripts/save_ai_analysis.py --setup-only
python skills/nsedata-trade-advisor/scripts/save_ai_analysis.py \
  --db <DB> --collection <COLLECTION> --limit 25
```

## Other skills

Use skills under `skills/` as needed. Mongo MCP setup: `skills/mongodb-local-mcp/SKILL.md`.
