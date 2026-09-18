---
name: scan-news-conviction
description: >-
  Ingest last-5-day scrips from Nsedata breakoutM2HR, breakoutM2LR, breakoutMHR,
  breakoutMLR, breakoutW2HR, breakoutW2LR, movingavg_crossed_up,
  movingavg_crossed_down, breakoutY2H, and breakoutYH (max 499 names; never drop
  the futures list; from breakoutW2HR/breakoutW2LR exclude non-futures only). Scrape
  company news, sectoral news, and analyst calls; score sentiment and conviction;
  keep only high-impact items from the last 7 days with duplicates removed. Upsert
  Nsedata.scrip_news (insertion_date; overwrite if the record is older than
  30 days). Use when asked to refresh scan news, conviction, or scrip news DB.
---

# Scan News Conviction

Local MongoDB scan tables → web news scrape → **sentiment + conviction** →
`Nsedata.scrip_news`.

## Run this skill

Skill name: **`scan-news-conviction`**

```bash
python skills/scan-news-conviction/scripts/ingest_scan_news.py
```

From `src/`:

```bash
python indian-trading-skills/skills/scan-news-conviction/scripts/ingest_scan_news.py
```

| Flag | Default | Meaning |
|------|---------|---------|
| `--days` | `5` | How far back to read scan-table `date` / `eventtime` |
| `--news-days` | `7` | Drop headlines older than this |
| `--min-impact` | `4` | Keep high-impact items (1–10); still keep a short top list if few pass |
| `--sleep` | `0.35` | Pause between Google News requests |
| `--limit` | `499` | Max scrips (always **< 500**). Futures names are never dropped to meet the cap. |
| `--scrips` | | Comma-separated filter, e.g. `RELIANCE,TCS` |
| `--recompute-only` | | Recalculate `overall_sentiment` / `conviction` on existing `scrip_news` (no scrape) |
| `--retain-futures-days` | `2` | Delete **futures-skill-only** `scrip_news` rows older than this (breakout-tagged rows kept) |

## Scan sources

| DB | Collections |
|----|-------------|
| `Nsedata` | `breakoutM2HR`, `breakoutM2LR`, `breakoutMHR`, `breakoutMLR`, `breakoutW2HR`, `breakoutW2LR`, `movingavg_crossed_up`, `movingavg_crossed_down`, `breakoutY2H`, `breakoutYH` |

If no rows match the 5-day date filter, the live snapshot of that collection is used.

**Universe filters**

- Hard cap: **fewer than 500** scrips (`--limit` default 499).
- **Never drop the futures list** (`Nsedata.scrip` `futures=Yes`). Every futures scrip is in the universe even if it is not on a scan table. Non-futures are trimmed first if the cap is exceeded.
- From **`breakoutW2HR`** and **`breakoutW2LR` only**: exclude non-futures. Futures on those tables stay. Other scan tables keep cash and futures.

## What is stored (`Nsedata.scrip_news`)

One document per `scrip` (upsert):

| Field | Notes |
|-------|--------|
| `scrip`, `industry`, `scan_tables` | Identity |
| `overall_sentiment` | `Bullish` · `Bearish` · `Neutral` · `Mixed` |
| `conviction` | `High` · `Med` · `Low` |
| `news` | Company headlines (deduped, ≤7 days, high impact) |
| `sectoral_news` | Sector headlines |
| `analyst_calls` | Upgrades / downgrades / targets |
| `articles` | Combined list |
| `insertion_date` | First insert (kept on normal updates) |
| `updated_at` | Every successful scrape |

**30-day overwrite:** if `insertion_date` (else `updated_at`) is **≥ 30 days** old, replace the whole document and set a **new** `insertion_date`.

## Futures-skill retention purge

At the **start of every run** (including `--recompute-only`), before scrape/upsert:

| Condition | Action |
|-----------|--------|
| `scan_tables` is **only** `futures` (written by `scan-news-conviction-futures`) and `max(insertion_date, updated_at)` is **older than 2 days** | **Delete** the `scrip_news` row |
| Row has any breakout scan-table tag | **Ignore** — never deleted |

## Quality rules

1. **Age** — drop items published more than **7 days** ago.
2. **Duplicates** — same normalized title (and near-duplicate first-8-words) kept once.
3. **Impact** — rank by india-news-tracker impact score; keep top high-impact items (`--min-impact`, default 4) plus a small top-N fallback so a scrip is not empty.
4. **Conviction** — High if sentiment is directional with several high-impact aligned headlines; Med if mixed/fewer catalysts; else Low. See [references/scoring.md](references/scoring.md).
5. **Sectoral threshold** — sectoral headlines count toward `overall_sentiment` only when there are **≥ 3** of them; fewer than 3 are dropped from `sectoral_news` / `articles`. Company news and analyst calls always count, regardless of how few there are.

## Prerequisites

- MongoDB `mongodb://localhost:27017`
- `pip install pymongo feedparser`

Reuse RSS classification from **india-news-tracker** (`news_fetcher.py`).

## After the run

Print a **SUMMARY NEWS DIGEST** (shared with `scan-news-conviction-futures`):

1. **Company news** — every stored `kind=news` headline from scrips processed this run (scrip, sentiment, impact, title).
2. **High conviction sectoral news** — stored sectoral headlines for scrips whose `conviction` is **High** (deduped by title).
