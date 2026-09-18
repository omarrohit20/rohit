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
5. **Always show Priority picks in chat (markdown table early).** Then **MUST** emit Executive Summary, News, Scan Columns, asked horizon tables, Avoid, Disclaimer. **MUST put Cursor Canvas last** — copy `skills/mongo-trade-agent/assets/priority-canvas-snippet.tsx` into a **new** uniquely named `.canvas.tsx` every query (never overwrite; never use `Pill tone` for colours — use Text + backgroundColor); **always** open via `open_resource` (`file:///...`). On Windows do not use `[label](C:/...)` chat links (broken). Follow `skills/mongo-trade-agent/references/priority-canvas.md` + the Cursor canvas skill. Lead columns:

**Single table:**

| Priority | Symbol | LastDay% | Today% | Sentiment | Conviction | Prob% | Why |
|----------|--------|----------|--------|-----------|------------|-------|-----|
| 1 | … | +1.2 | +0.4 | Bullish | High | 78 | scan tags + tape + news in one sentence |

**Multiple tables:** every result must include the table name:

| Priority | Table | Symbol | LastDay% | Today% | Sentiment | Conviction | Prob% | Why |
|----------|-------|--------|----------|--------|-----------|------------|-------|-----|
| 1 | highBuy | … | +2.1 | +0.8 | Bullish | High | 78 | … |
| 2 | buy_all_processor | … | -0.5 | +1.0 | Bullish | Med | 65 | … |

Highlights (Canvas snippet): buy Symbol orange if LastDay%/Today% > 3; sell orange if LastDay%/Today% < -3; colour **MLBuy** / **MLSell** tokens in Why via Text `#C6F6D5` / `#FEB2B2`, not the scrip; **News catalyst** Positive light green / Negative light red / Mixed light yellow; **Sentiment** green when Bullish + positive news, red when Bearish + negative news (`news-extension.md`). **Momentum keyword chips** in Why (`MomentumWhyText`): green on UpStairs + Today% > 2 or UpPostLunchConsolidation + Today% > 3; red on DownStairs + Today% < -2 or DownPostLunchConsolidation + Today% < -3 — keyword only, not full row.

Example Why style: `Q1 results today + AnchisBuyUp / ReversalLow; already +2% into the print`

6. Also fill **News catalyst** and **May extend?** (`Yes` / `Possible` / `Only if X` / `Weak` / `No`). Keep **Table** on those rows when multi-source.
7. Use template `skills/nsedata-trade-advisor/assets/four-horizon-report.md` — do not stop at Priority.
8. Disclaimer: educational only, not SEBI advice — then Canvas link last.

## Scan News Conviction

When the user asks to scrape/save **news, sectoral news, analyst calls, sentiment, or conviction** for breakout scan tables (`breakoutM2HR`, `breakoutM2LR`, `breakoutMHR`, `breakoutMLR`, `breakoutW2HR`, `breakoutW2LR`, `movingavg_crossed_up`, `movingavg_crossed_down`, `breakoutY2H`, `breakoutYH`):

1. Follow `skills/scan-news-conviction/SKILL.md`.
2. Run:

```bash
python skills/scan-news-conviction/scripts/ingest_scan_news.py
```

Target: `Nsedata.scrip_news`. Cap **< 500** names; never drop futures; from `breakoutW2HR`/`breakoutW2LR` exclude non-futures only. High-impact, ≤7 days, deduped; upsert; overwrite if older than 30 days. After the run, print **SUMMARY NEWS DIGEST** (company news + high-conviction sectoral news).

## Scan News Conviction Futures

When the user asks to scrape/save **news, sentiment, or conviction** for **all futures stocks** (`Nsedata.scrip` `futures=Yes`):

1. Follow `skills/scan-news-conviction-futures/SKILL.md`.
2. Process a scrip if `Nsedata.scrip_news` was **not created or updated in the last 3 days**, **or if company news is published today** (3-day skip does not apply).
3. Create/update **`Nsedata.scrip_news` only**.
4. Run:

```bash
python skills/scan-news-conviction-futures/scripts/ingest_futures_news.py
```

5. After the run, report the script SUMMARY and the shared **SUMMARY NEWS DIGEST** (company news + high-conviction sectoral news).

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
