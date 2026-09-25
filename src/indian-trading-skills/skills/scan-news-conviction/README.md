# Scan News Conviction

Scrape company, sectoral, and analyst news for **breakout / moving-average scan scrips**, score **sentiment** and **conviction**, and upsert **`Nsedata.scrip_news`**.

Agent instructions: [SKILL.md](SKILL.md). Scoring: [references/scoring.md](references/scoring.md).

## What it writes

**Only** `Nsedata.scrip_news` (one document per `scrip`).

| Field | Values / notes |
|-------|----------------|
| `overall_sentiment` | `Bullish` · `Bearish` · `Neutral` · `Mixed` |
| `conviction` | `High` · `Med` · `Low` |
| `news` | Company headlines (≤7 days, high impact, deduped) |
| `sectoral_news` | Sector headlines (stored only if count ≥ 3) |
| `analyst_calls` | Upgrades / downgrades / targets |
| `insertion_date` | First insert (kept on normal updates) |
| `updated_at` | Every successful scrape |

If `insertion_date` (else `updated_at`) is **≥ 30 days** old, the document is replaced and `insertion_date` is reset.

## Universe

Scan tables (last **5 days** of `date` / `eventtime`; if none match, the live snapshot is used):

`breakoutM2HR`, `breakoutM2LR`, `breakoutMHR`, `breakoutMLR`, `breakoutW2HR`, `breakoutW2LR`, `movingavg_crossed_up`, `movingavg_crossed_down`, `breakoutY2H`, `breakoutYH`

Filters:

- Cap **&lt; 500** scrips (`--limit` default **499**).
- **Never drop** the futures list (`Nsedata.scrip` `futures=Yes`). Those names are always in the universe.
- From **`breakoutW2HR` / `breakoutW2LR` only**: exclude non-futures. Other tables keep cash and futures.

## Run

From `indian-trading-skills/`:

```bash
python skills/scan-news-conviction/scripts/ingest_scan_news.py
```

From `src/`:

```bash
python indian-trading-skills/skills/scan-news-conviction/scripts/ingest_scan_news.py
```

| Flag | Default | Meaning |
|------|---------|---------|
| `--days` | `5` | Scan-table lookback |
| `--news-days` | `7` | Max headline age |
| `--min-impact` | `4` | Keep high-impact items (1–10) |
| `--sleep` | `0.35` | Pause between Google News requests |
| `--limit` | `499` | Max scrips (&lt; 500). Futures are never dropped. |
| `--scrips` | | Comma-separated filter, e.g. `RELIANCE,TCS` |
| `--recompute-only` | | Recalculate scores on existing `scrip_news` (no scrape) |
| `--retain-futures-days` | `2` | Delete **futures-skill-only** rows older than this (breakout-tagged rows kept) |

Needs MongoDB `mongodb://localhost:27017` and `pip install pymongo feedparser`. RSS classification comes from **india-news-tracker**.

## After the run

Prints **SUMMARY NEWS DIGEST**:

1. **Company news** from scrips processed this run.
2. **High conviction sectoral news** (High-conviction scrips only; titles de-duplicated).

## Related

- [scan-news-conviction-futures](../scan-news-conviction-futures/README.md) — all F&O names, stale skip + company-news exception
- [mongo-trade-agent](../mongo-trade-agent/README.md) — reads `scrip_news` for Sentiment / Conviction / News catalyst
