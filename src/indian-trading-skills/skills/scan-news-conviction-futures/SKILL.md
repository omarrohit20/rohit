---
name: scan-news-conviction-futures
description: >-
  Ingest news, sectoral news, and analyst calls for ALL Nsedata.scrip rows with
  futures=Yes. Process a scrip when Nsedata.scrip_news was not created or
  updated in the last three days, or when new company-specific news appears in
  the last two days (3-day skip does not apply). Score sentiment and conviction;
  upsert scrip_news only. Print a run summary. Use when asked to refresh futures
  scrip news, F&O news conviction, or scan-news-conviction-futures.
---

# Scan News Conviction — Futures

All **futures** scrips (`Nsedata.scrip` `futures=Yes`) → scrape if `scrip_news`
is missing or stale (**> 3 days** since create/update), **unless there is
new company-specific news in the last 2 days** (then scrape anyway) → **sentiment +
conviction** → **`Nsedata.scrip_news` only**.

Scoring, dedupe, and high-impact rules match
[`scan-news-conviction`](../scan-news-conviction/SKILL.md). See
[../scan-news-conviction/references/scoring.md](../scan-news-conviction/references/scoring.md).

## Run this skill

Skill name: **`scan-news-conviction-futures`**

```bash
python skills/scan-news-conviction-futures/scripts/ingest_futures_news.py
```

From `src/`:

```bash
python indian-trading-skills/skills/scan-news-conviction-futures/scripts/ingest_futures_news.py
```

| Flag | Default | Meaning |
|------|---------|---------|
| `--stale-days` | `3` | Skip scrip if `scrip_news` `insertion_date` or `updated_at` is within this window, **unless new company-specific news in last 2 days** |
| `--retain-days` | `2` | Delete **futures-only** `scrip_news` rows older than this (rows with breakout scan-table tags are kept) |
| `--company-news-days` | `2` | Company news calendar window (2 = today + yesterday); ignores already-stored headlines |
| `--news-days` | `7` | Unused (company news only) |
| `--min-impact` | `4` | Keep high-impact items (1–10) |
| `--sleep` | `0.35` | Pause between Google News requests |
| `--limit` | `0` | Max due scrips (`0` = all due) |
| `--scrips` | | Comma-separated filter, e.g. `RELIANCE,TCS` |

## Universe

| DB | Collection | Filter |
|----|------------|--------|
| `Nsedata` | `scrip` | `futures=Yes` |

Do **not** use breakout scan tables. Include every futures scrip.

## Freshness (last three days)

For each futures scrip, read `Nsedata.scrip_news` by `scrip`.

| Condition | Action |
|-----------|--------|
| No `scrip_news` row | **Create** (scrape + insert) |
| `max(insertion_date, updated_at)` **older than 3 days**, or both missing | **Update** (scrape + upsert) |
| Created or updated **within the last 3 days**, **and new company-specific news in the last 2 days** not already on `scrip_news` | **Do not skip** — scrape + upsert |
| Created or updated **within the last 3 days**, and **no** such new company news | **Skip** |

## Company news only (futures skill)

**Does not scrape or score sectoral or analyst headlines.** Only `kind=news` company headlines are fetched, stored, and used for sentiment/conviction.

Before scoring/sentiment, each company headline must pass **all** checks:

- Published within **today and yesterday** only (`--company-news-days` default `2` = 2 calendar dates)
- Must mention the **scrip** or `Nsedata.scrip.company` name
- Drop market/sector roundups (Nifty/Sensex wrap, top gainers/losers, FII flows, etc.)
- Drop macro/global headlines unless the company is the clear subject in the title
- Drop weak price-only headlines (`share price`, `in focus`) without a company catalyst
- Drop multi-stock listicles naming 3+ symbols
- **Ignore already-stored headlines** — if the same title is already on `scrip_news`, it was factored in earlier (e.g. yesterday) and is not treated as a new catalyst

The **fresh-skip exception** uses the same rules and only fires on **new** company headlines.

## Retention purge (futures-only rows)

At the **start of every run**, before scrape/upsert:

| Condition | Action |
|-----------|--------|
| `scan_tables` is **only** `futures` (no breakout scan-table tag) and `max(insertion_date, updated_at)` is **older than 2 days** | **Delete** the `scrip_news` row |
| Row has any breakout scan-table tag (`breakoutM2HR`, `breakoutW2LR`, etc.) | **Ignore** — never deleted by this skill |

Fresh futures-only rows (≤ 2 days) are kept until they expire or are refreshed.

## What is written

**Only** `Nsedata.scrip_news`. Do not write other collections.

One document per `scrip` (upsert). Same fields as `scan-news-conviction`.
Merge `scan_tables` with existing tags and add `futures` (do not wipe prior
breakout table tags).

**30-day overwrite:** if `insertion_date` (else `updated_at`) is **≥ 30 days**
old, replace the whole document and set a **new** `insertion_date`.

## After the run

Always print the script **SUMMARY** block: futures count, purged (expired futures-only),
skipped (fresh), insert/update/overwrite, errors, sentiment/conviction tallies, High conviction
list, directional High/Med list.

Then print **SUMMARY NEWS DIGEST** — **company news only** from scrips processed this run (no sectoral section).

## Prerequisites

- MongoDB `mongodb://localhost:27017`
- `pip install pymongo feedparser`

Reuse scrape/score/upsert from **scan-news-conviction**
(`ingest_scan_news.py`) and RSS classification from **india-news-tracker**.
