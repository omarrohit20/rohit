---
name: scan-news-conviction-futures
description: >-
  Ingest company news and analyst headlines for ALL Nsedata.scrip rows with
  futures=Yes. Upsert scrip_news when a new company/analyst headline is from
  today or yesterday, or a board/results/dividend event is today or tomorrow,
  and the title is not already stored. Score sentiment and conviction; print a
  run summary. Use when asked to refresh futures scrip news, F&O news
  conviction, or scan-news-conviction-futures.
---

# Scan News Conviction — Futures

All **futures** scrips (`Nsedata.scrip` `futures=Yes`) → scrape and **write when
there is a new company/analyst headline from today or yesterday, or a
board/results/dividend event dated today or tomorrow, that is not already
on `scrip_news`** → merge new headlines → recompute **sentiment + conviction** →
**`Nsedata.scrip_news` only**.

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
| `--retain-days` | `2` | Delete **futures-only** `scrip_news` rows older than this (rows with breakout scan-table tags are kept) |
| `--company-news-days` | `2` | Published-headline window (2 = today + yesterday). Also writes for board/results/dividend dated **today or tomorrow** if the title is new |
| `--news-days` | `7` | Unused (headline window uses `--company-news-days`) |
| `--stale-days` | `3` | Unused (no stale-age trigger) |
| `--min-impact` | `4` | Keep high-impact items (1–10) |
| `--sleep` | `0.35` | Pause between Google News requests |
| `--limit` | `0` | Max scrips to check (`0` = all) |
| `--scrips` | | Comma-separated filter, e.g. `RELIANCE,TCS` |

## Universe

| DB | Collection | Filter |
|----|------------|--------|
| `Nsedata` | `scrip` | `futures=Yes` |

Do **not** use breakout scan tables. Include every futures scrip.

## Write rule

For each futures scrip, read `Nsedata.scrip_news` by `scrip` and fetch company/analyst headlines.

| Condition | Action |
|-----------|--------|
| New company/analyst headline **published today or yesterday**, not already stored | **Insert** or **update** |
| New **board / results / dividend** headline whose **event date is today or tomorrow**, not already stored | **Insert** or **update** (T−1/today calendar; filing may be older) |
| New **regulatory** headline for a high-exposure scrip, impact ≥ 6, **High conviction** | **Insert** or **update** |
| None of the above | **Skip** — do not write |

There is **no** automatic update based on document age alone.

## Company + analyst headlines (futures skill)

**Does not scrape or score sectoral headlines.** Uses `kind=news` and `kind=analyst` only.

Search uses **ticker and company short form** from `Nsedata.scrip.company` (example: `DATAPATTNS` and `"Data Patterns"`). Google News also runs a **guidance/concall/results/board meeting/interim dividend** query so TV-style chatter and T−1 event positioning are fetched. India RSS keeps items that mention the ticker **or** the short/full company name.

Before a write, each **new** headline must pass **all** checks:

- Published within **today and yesterday** only (`--company-news-days` default `2` = 2 calendar dates). **Undated** RSS items still count as today when the title has a company catalyst (results, guidance, concall, outlook, order, etc.)
- **Board / results / dividend calendar items** also count when the **event date in the headline is today or tomorrow** (not later). A 4 Nov filing for a 10 Nov board is stored on 9 Nov or 10 Nov only. Generic “stocks to watch” wraps are still dropped.
- **Company name primarily in the title** — scrip or `Nsedata.scrip.company` must appear in the headline; summary-only matches are ignored
- Drop market/sector roundups (Nifty/Sensex wrap, top gainers/losers, FII flows, etc.)
- Drop weak price-only headlines (`share price`, `in focus`) without a company catalyst
- Drop multi-stock listicles naming 3+ symbols
- Analyst items must also match upgrade/downgrade/target/rating patterns in the title
- **Ignore already-stored headlines** — if the same title is already on `scrip_news`, skip it (no write unless another new headline exists)

## Regulatory sector news (high exposure + High conviction)

**IRDAI / RBI / SEBI** sector headlines (no company name required in title) apply when:

- Scrip is on the theme **high-exposure list** (see `references/regulatory_exposure.md`), or headline explicitly flags the scrip as *most exposed* / *hit hardest*
- `impact_score >= 6`
- Recomputed **conviction is High** after scoring (single aligned regulatory headline qualifies)
- Published today/yesterday and not already stored

Stored on `regulatory_news`. Generic sectoral headlines still require ≥3 count.

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
breakout table tags). New headlines are **appended** to stored articles (deduped by title).

**30-day overwrite:** if `insertion_date` (else `updated_at`) is **≥ 30 days**
old, replace the whole document and set a **new** `insertion_date`.

## After the run

Always print the script **SUMMARY** block: futures count, purged (expired futures-only),
skipped (no new headline), insert/update/overwrite, errors, sentiment/conviction tallies, High conviction
list, directional High/Med list.

Then print **SUMMARY NEWS DIGEST** — **company news + analyst headlines** from scrips processed this run (no sectoral section).

## Prerequisites

- MongoDB `mongodb://localhost:27017`
- `pip install pymongo feedparser`
- Outbound access to at least one configured RSS source. The script checks feed access before database writes and stops if all sources are unreachable.

Reuse scrape/score/upsert from **scan-news-conviction**
(`ingest_scan_news.py`) and RSS classification from **india-news-tracker**.
