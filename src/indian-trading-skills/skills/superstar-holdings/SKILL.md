---
name: superstar-holdings
description: >-
  Track stocks held by Indian celebrity / superstar investors (Vijay Kedia, Dolly
  Khanna, Ashish Kacholia, Mukul Agrawal, Rare Enterprises and others) from NSE
  shareholding filings and bulk/block deals. Keeps every holding, new buys since
  the last run, increases, cuts, holdings below their maximum, and exits in local
  MongoDB with a rule-based conviction and why, for the reports dashboard. Use
  when asked for superstar, celebrity, or big-investor holdings or portfolio changes.
---

# Superstar holdings

NSE shareholding filings (named public holders above 1%) and NSE bulk/block deals become
`Nsedata.superstar_holdings`. The Streamlit page is `reports/superstar_holdings.py`.

Do **not** place live orders. Output is educational, not SEBI advice.

## Run this skill

From `indian-trading-skills/`:

```bash
python skills/superstar-holdings/scripts/run_superstar_holdings.py
```

From `src/`: `superstar_holdings.bat` (same flags), or
`python indian-trading-skills/skills/superstar-holdings/scripts/run_superstar_holdings.py`.

Safe to run daily, weekly, or monthly. A stock is re-asked only when a newer quarter can
exist and it was not checked in the last `--recheck-days`; once its latest quarter end is
read it is skipped until the next quarter ends. The first full run reads up to 4 quarters
for every stock in `Nsedata.scrip` and takes hours; it saves progress per stock, so an
interrupted run resumes where it stopped. Later runs take minutes or seconds.

| Flag | Default | Meaning |
|------|---------|---------|
| `--symbols` | all | Comma-separated symbols (testing) |
| `--limit` | none | First N symbols only (testing) |
| `--backfill-quarters` | `4` | Quarters read on a stock's first check (gives "max holding") |
| `--recheck-days` | `3` | Ask NSE about the same stock at most this often |
| `--refresh` | off | Ignore saved state and re-check every stock |
| `--skip-deals` | off | Skip the NSE bulk/block deal snapshot |
| `--deal-days` | `30` | Window over stored deals |
| `--skip-screener` | off | No Screener calls (pros for new buys) |
| `--sleep` | `1.0` | Pause between NSE / Screener calls |
| `--uri` | `mongodb://localhost:27017` | MongoDB |

## What is saved

| Collection | Key | Contents |
|------------|-----|----------|
| `superstar_holdings` | `scrip\|investor` | Current state: `status`, `latest_pct`, `prev_pct`, `change_pct`, `max_pct`, `drop_from_max_pct`, `below_max`, `investors_holding_count`, `conviction`, `sentiment`, `why`, `deal_signal`, `changed_run_id`, `changed_at`, company, industry, market cap |
| `superstar_holdings_history` | `scrip\|investor\|quarter` | `pct` and matched holder names per filed quarter |
| `superstar_scan_state` | `scrip` | Quarters read and last check time |
| `superstar_runs` | `run_id` | Counts per run; "changed last run" uses the latest `run_id` |

NSE responses are cached in `Nsedata.nse_shareholding_cache` and deals in
`Nsedata.nse_large_deals` (shared with `investment-ideas`).

Statuses: `NEW`, `NEW_DEAL` (bulk/block buy, not yet in a filing), `INCREASED`, `UNCHANGED`,
`DECREASED`, `HOLDING` (only one quarter read), `EXITED_OR_BELOW_1PCT` (NSE names only holders
above 1%, so a cut below 1% looks like an exit).

Conviction is rule-based (no LLM): holding change and streak, stake size, number of tracked
investors in the stock, bulk/block deal side, price set-up (`derive_conviction_sentiment`),
news from `Nsedata.scrip_news`, and the top Screener pro for new buys. High ≥ 5 points,
Med ≥ 3. `why` lists the strongest reasons.

Investors and name variants: [references/investors.md](references/investors.md). Edit the
table to add one; no code change. Detail logs go to `output/run.log`.

## After the run

Relay only the printed `SUMMARY superstar-holdings` block (counts, per-investor table, top
changes). Do not query Mongo or read the log unless asked. Then one line: educational only,
not SEBI advice.
