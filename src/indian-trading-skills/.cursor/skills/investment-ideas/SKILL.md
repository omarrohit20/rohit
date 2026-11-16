---
name: investment-ideas
description: >-
  Build long, medium, and short investment ideas from local Nsedata breakout
  scans, Screener order books, and NSE celebrity small/midcap holding increases.
  Save only High or Med conviction Bullish names with a why, buy price, and target into
  investment-long-term, investment-medium-term, and investment-short-term, with
  target %, target reason, target date, and days to target. Use
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
| `--only` | all | `breakout`, `orderbook`, `deals`, or `celebrity` |
| `--months` | `6` | Lookback for `breakoutYH`, `breakoutY2H`, and `nearY5H` |
| `--celebrity-months` | `3` | Latest quarter end must fall inside this window |
| `--deal-days` | `30` | Window over stored NSE bulk/block deals |
| `--sleep` | `1.0` | Pause between Screener and NSE HTTP calls |
| `--uri` | `mongodb://localhost:27017` | MongoDB |
| `--long-min-return` | `50` | Minimum target upside % for `investment-long-term` |
| `--medium-min-return` | `30` | Minimum target upside % for `investment-medium-term` |
| `--short-min-return` | `20` | Minimum target upside % for `investment-short-term` |

## What is saved

### Why

Every `why` ends with a **news clause** from `Nsedata.scrip_news`: the stored sentiment and conviction, then the highest-impact (then latest) headline from the last 30 days with its event type, sentiment, impact score, and date — or `no company news in last 30 days`, or `none on file`. A headline counts only when it names the company (ticker of 4+ letters as a word, or the first two significant words of the company name; a one-word name also needs a market word such as shares, stock, Ltd, or results). Quote and estimate listing pages and multi-company round-ups are ignored. The pick is also stored as `news_sentiment`, `news_conviction`, `news_headline`, `news_event`, `news_impact_score`, `news_date`, and `news_link`.

| Idea type | `why` |
|-----------|-------|
| Breakout | Scan hits in the window, level (5-year / year / month / week high, or moving averages crossed up), 200-day average, scan tags; news clause |
| Deal | Tracked investor or institution, net shares bought in NSE bulk/block deals, average deal price, latest deal date; news clause |
| Celebrity | Investor holding change and market-cap bucket; **possible draws** (top 2 Screener Pros) and **watch** (top Screener Con) — Screener cannot say why an investor bought, so these are the visible fundamentals; news clause |
| Order book | Order book vs market cap and sales, **years of revenue visibility** (order book / sales, also `order_book_years`), **strengths** (top 2 Screener Pros), **watch** (top Con); news clause; largest holders |

Celebrity and order-book rows also store `screener_pros` and `screener_cons`. Celebrity fetches the Screener page only for names with a holding increase.

Only rows with **conviction High or Med** and **sentiment Bullish**. The row stores its actual `conviction`. Low (or not Bullish) is counted as skipped and is not written. A document without `why` is not inserted. **Celebrity is the exception:** every listed-investor buy is saved with its actual `conviction` and `sentiment`, whatever they are.

Target upside (`target_pct`) must be **above 50%** for long-term (`--long-min-return`), **above 30%** for medium-term (`--medium-min-return`), and **above 20%** for short-term (`--short-min-return`). Lower ones are not saved (`return-at-or-below-N%` under other skips), and each run deletes existing rows whose (target − buy) / buy is at or below the minimum. Celebrity rows are exempt from these minimums and from that delete.

A symbol is kept only in its longest horizon: medium-term excludes long-term symbols, and short-term excludes long-term and medium-term symbols. Breakout tables run long, then medium, then short; a save is skipped when the symbol is already in a longer horizon; and a final sweep after all stages deletes medium-term rows covered by long-term, then short-term rows covered by either (`covered-by-long-term`, `covered-by-medium-term`).

| Collection | Contents | Retention |
|------------|----------|-----------|
| `investment-long-term` | `breakoutYH`, `breakoutY2H`, `breakoutMH`, `nearY5H`, order book | Delete `insertion_date` older than 3 months (90 days), or upside 50% or less |
| `investment-medium-term` | `breakoutM2H`, `movingavg_crossed_up`, NSE bulk/block deal buys, celebrity small/mid buys | Delete `insertion_date` older than 1 month (30 days), upside 30% or less, or symbol in long-term |
| `investment-short-term` | `breakoutW2H`, or `breakoutW2HR` when W2H is missing or empty | Delete `insertion_date` older than 10 days, upside 20% or less, or symbol in long- or medium-term |

Upsert on `dedupe_key` (a rerun updates). `insertion_date` stays on the first insert so retention still ages the row.

- Breakout: `breakout\|{source_table}\|{symbol}\|{signal_date}`
- Order book: `orderbook\|{symbol}\|{as_of_date}`
- Deal: `deal\|{symbol}\|{buyer}\|{latest_deal_date}`
- Celebrity: `celebrity\|{symbol}\|{investor_name}\|{quarter}`

`buy_price` is the latest close, or the 20-day average when the close is more than about 8% above that average. `target_price` is the scorer `t1` (`score_long_term` for long ideas, `score_short_term` for weekly breakouts, `score_swing_3_5` for medium). `t2` and `stoploss` are stored when the scorer returns them.

Every row also stores the target plan:

| Field | Meaning |
|-------|---------|
| `target_reason` | How `t1` was picked: `52-week high`, `new-high extension` (27.2% of the 52-week range), `20-day swing high`, or `1 ATR(14) above the close` |
| `target_pct` | Upside from `buy_price` to `target_price`, in percent |
| `target_days` | Estimated calendar days to reach the target: (distance / ATR14)² trading days × 7/5, capped at the collection's retention window (90 / 30 / 10). A capped estimate says so in `target_reason` |
| `target_date` | Run date + `target_days` (ISO date) |

`horizon_label` matches the retention window: long-term up to 3 months, medium-term up to 1 month, short-term up to 10 days.

Investor name variants live in [references/investors.md](references/investors.md).

## Order book, deal, and celebrity gates

Order book, deal, and celebrity names have no scan row, so the scorer gets scan fields built from daily bars (3- and 5-day change, distance from last week's high and low). The High/Med Bullish gate runs on local Mongo **before** any Screener or NSE call, so HTTP is spent only on names that can be saved.

- Deals: NSE's historical deal API is blocked, so each run stores the latest-session snapshot (`/api/snapshot-capital-market-largedeal`) in `Nsedata.nse_large_deals` and reads the last `--deal-days` from there. A buyer counts when it matches [references/investors.md](references/investors.md) or is a mutual fund or insurer, and its net quantity (buys minus sells) per symbol is positive.

- Order book: capital-goods style names in `Nsedata.scrip` (engineering, capital goods, defence, construction, railways, power equipment, infrastructure). Keep a name only when the Screener page states a numeric order book greater than both market cap and latest annual sales. No number means skip. Do not estimate one. Same-week reruns skip symbols whose saved document already has `page_fetched_at` within 7 days.
- Celebrity: `fundamental.marketcap` in crores. Small is under 5,000. Mid is 5,000–20,000. Skip large caps and missing market caps. A buy is a listed investor whose holding is higher than the previous quarter, or newly present, with the quarter end inside `--celebrity-months`. NSE shareholding responses are cached in `Nsedata.nse_shareholding_cache` (quarter list for 1 day, filed quarters indefinitely), so the first run takes about an hour and later runs a few minutes.

## After the run

Summarize **inserted**, **updated**, **deleted**, and **skipped** (Low conviction or not Bullish) counts per collection.

Lead each collection with a short table: symbol, buy, target, target %, days, target date, target reason, conviction, and why. Add the investor or top holder when the row has one.

Then one line: educational only, not SEBI advice.
