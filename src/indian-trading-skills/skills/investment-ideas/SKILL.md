---
name: investment-ideas
description: >-
  Build long, medium, and short investment ideas from local Nsedata breakout
  scans, Screener order books, and NSE celebrity small/midcap holding increases.
  Save only High conviction Bullish names with a why, buy price, and target into
  investment-long-term, investment-medium-term, and investment-short-term. Use
  when asked for investment ideas, order-book multibaggers, or celebrity
  smallcap or midcap buys.
---

# Investment ideas

Local Mongo breakout scans, Screener order books, and NSE shareholding changes
become three `Nsedata` collections. The Streamlit page is `reports/investment_ideas.py`.

Do **not** place live orders. Output is educational, not SEBI advice.

## Run this skill

Skill name: **`investment-ideas`**

From `indian-trading-skills/`:

```bash
python skills/investment-ideas/scripts/run_investment_ideas.py
```

From `src/`:

```bash
python indian-trading-skills/skills/investment-ideas/scripts/run_investment_ideas.py
```

| Flag | Default | Meaning |
|------|---------|---------|
| `--only` | all | `breakout`, `orderbook`, or `celebrity` |
| `--months` | `6` | Lookback for `breakoutYH` and `breakoutY2H` |
| `--celebrity-months` | `3` | Latest quarter end must fall inside this window |
| `--sleep` | `1.0` | Pause between Screener and NSE HTTP calls |
| `--uri` | `mongodb://localhost:27017` | MongoDB |

## What is saved

Only rows with **conviction High** and **sentiment Bullish**. Med and Low are counted as skipped and are not written. A document without `why` is not inserted.

| Collection | Contents | Retention |
|------------|----------|-----------|
| `investment-long-term` | `breakoutYH`, `breakoutY2H`, `breakoutMH`, order book | Kept. Never deleted. |
| `investment-medium-term` | `breakoutM2H`, celebrity small/mid buys | Delete `insertion_date` older than 3 months |
| `investment-short-term` | `breakoutW2H`, or `breakoutW2HR` when W2H is missing or empty | Delete `insertion_date` older than 20 days |

Upsert on `dedupe_key` (a rerun updates). `insertion_date` stays on the first insert so retention still ages the row.

- Breakout: `breakout\|{source_table}\|{symbol}\|{signal_date}`
- Order book: `orderbook\|{symbol}\|{as_of_date}`
- Celebrity: `celebrity\|{symbol}\|{investor_name}\|{quarter}`

`buy_price` is the latest close, or the 20-day average when the close is more than about 8% above that average. `target_price` is the scorer `t1` (`score_long_term` for long ideas, `score_short_term` for weekly breakouts, `score_swing_3_5` for medium). `t2` and `stoploss` are stored when the scorer returns them.

Investor name variants live in [references/investors.md](references/investors.md).

## Order book and celebrity gates

- Order book: capital-goods style names in `Nsedata.scrip` (engineering, capital goods, defence, construction, railways, power equipment, infrastructure). Keep a name only when the Screener page states a numeric order book greater than both market cap and latest annual sales. No number means skip. Do not estimate one. Same-week reruns skip symbols whose saved document already has `page_fetched_at` within 7 days.
- Celebrity: `fundamental.marketcap` in crores. Small is under 5,000. Mid is 5,000–20,000. Skip large caps and missing market caps. A buy is a listed investor whose holding is higher than the previous quarter, or newly present, with the quarter end inside `--celebrity-months`.

## After the run

Summarize **inserted**, **updated**, **deleted**, and **skipped** (not High conviction) counts per collection.

Lead each collection with a short table: symbol, buy, target, conviction, and why. Add the investor or top holder when the row has one.

Then one line: educational only, not SEBI advice.
