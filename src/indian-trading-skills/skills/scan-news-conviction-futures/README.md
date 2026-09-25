# Scan News Conviction — Futures

Scrape **company news** and **analyst headlines** for **every** F&O scrip (`Nsedata.scrip` `futures=Yes`), score **sentiment** and **conviction**, and upsert **`Nsedata.scrip_news` only** when there is **new** headline news.

Does **not** use breakout scan tables. Does **not** scrape sectoral feeds.

Agent instructions: [SKILL.md](SKILL.md). Shared scrape/score/upsert: [../scan-news-conviction/scripts/ingest_scan_news.py](../scan-news-conviction/scripts/ingest_scan_news.py). Scoring: [../scan-news-conviction/references/scoring.md](../scan-news-conviction/references/scoring.md).

## When a scrip is written

| Condition | Action |
|-----------|--------|
| New company/analyst headline in **today or yesterday**, not already on `scrip_news` | **Insert** or **update** |
| New **regulatory** headline for **high-exposure** scrip, impact ≥ 6, **High conviction** | **Insert** or **update** |
| No such new headline | **Skip** (no write) |

There is **no** stale-age trigger. A scrip is not updated just because `scrip_news` is old.

`--company-news-days` default `2` (today + yesterday).

## Headline filter (company + analyst)

Each `kind=news` or `kind=analyst` headline must:

- Be published **today or yesterday**
- **Primarily name the company in the title** — scrip or `Nsedata.scrip.company` must appear in the headline (summary-only matches are ignored)
- Not be a market/sector roundup, multi-stock listicle, or weak price-only headline
- For analyst items: title must also look like an upgrade/downgrade/target/rating headline
- Not already be stored on `scrip_news`

Sectoral news is never fetched or scored for sentiment on its own.

## Regulatory sector news (high exposure + High conviction)

IRDAI / RBI / SEBI sector headlines apply to **high-exposure scrips only** (see [`../scan-news-conviction/references/regulatory_exposure.md`](../scan-news-conviction/references/regulatory_exposure.md)):

- `impact_score >= 6`
- Scrip on theme exposure list, or headline names scrip as *most exposed*
- Stored only when recomputed **conviction is High**
- Published **today or yesterday**, not already on `scrip_news`

Example: IRDAI commission-cap draft → **IDFCFIRSTB, INDUSINDBK, POLICYBZR, HDFCLIFE** (not **SBIN**).

## Retention purge

At the **start** of every run:

| Condition | Action |
|-----------|--------|
| `scan_tables` is **only** `futures` and last touch **older than 2 days** | **Delete** the row |
| Row has any breakout scan-table tag | **Keep** |

`--retain-days` default `2`. Breakout-tagged documents from **scan-news-conviction** are never deleted here.

`scan_tables` is **merged** with existing tags and `futures` is added (prior breakout tags are kept).

## Run

From `indian-trading-skills/`:

```bash
python skills/scan-news-conviction-futures/scripts/ingest_futures_news.py
```

From `src/`:

```bash
python indian-trading-skills/skills/scan-news-conviction-futures/scripts/ingest_futures_news.py
```

| Flag | Default | Meaning |
|------|---------|---------|
| `--retain-days` | `2` | Purge futures-only rows older than this |
| `--company-news-days` | `2` | Headline window (today + yesterday); write only if new vs stored |
| `--min-impact` | `4` | Keep high-impact items (1–10) |
| `--sleep` | `0.35` | Pause between Google News requests |
| `--limit` | `0` | Max scrips to check (`0` = all) |
| `--scrips` | | Comma-separated filter, e.g. `RELIANCE,TCS` |

Needs MongoDB `mongodb://localhost:27017` and `pip install pymongo feedparser`.

## After the run

Prints **SUMMARY** (counts, skips, High / directional lists, purge) then **SUMMARY NEWS DIGEST** for scrips processed this run.

## Related

- [scan-news-conviction](../scan-news-conviction/README.md) — breakout-scan universe, sectoral + analyst news
- [mongo-trade-agent](../mongo-trade-agent/README.md) — reads `scrip_news` for ranked trade ideas
