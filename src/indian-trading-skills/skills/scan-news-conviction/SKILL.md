---
name: scan-news-conviction
description: >-
  Ingest last-5-day scrips from Nsedata breakoutM2HR, breakoutMHR, breakoutW2HR,
  movingavg_crossed_up, breakoutY2H, and breakoutYH. Scrape company news,
  sectoral news, and analyst calls; score sentiment and conviction; keep only
  high-impact items from the last 7 days with duplicates removed. Upsert
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
| `--limit` | `0` | Max scrips (`0` = all) |
| `--scrips` | | Comma-separated filter, e.g. `RELIANCE,TCS` |

## Scan sources

| DB | Collections |
|----|-------------|
| `Nsedata` | `breakoutM2HR`, `breakoutMHR`, `breakoutW2HR`, `movingavg_crossed_up`, `breakoutY2H`, `breakoutYH` |

If no rows match the 5-day date filter, the live snapshot of that collection is used.

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

## Quality rules

1. **Age** — drop items published more than **7 days** ago.
2. **Duplicates** — same normalized title (and near-duplicate first-8-words) kept once.
3. **Impact** — rank by india-news-tracker impact score; keep top high-impact items (`--min-impact`, default 4) plus a small top-N fallback so a scrip is not empty.
4. **Conviction** — High if sentiment is directional with several high-impact aligned headlines; Med if mixed/fewer catalysts; else Low. See [references/scoring.md](references/scoring.md).

## Prerequisites

- MongoDB `mongodb://localhost:27017`
- `pip install pymongo feedparser`

Reuse RSS classification from **india-news-tracker** (`news_fetcher.py`).
