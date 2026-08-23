# Sentiment and conviction scoring

Used by `ingest_scan_news.py` after scrape + 7-day / dedupe / impact filters.

## Sentiment (`overall_sentiment`)

Count Bullish vs Bearish among kept articles:

| Condition | Value |
|-----------|--------|
| Bullish count > Bearish and Bullish ≥ 1 | `Bullish` |
| Bearish count > Bullish and Bearish ≥ 1 | `Bearish` |
| Both > 0 | `Mixed` |
| Else | `Neutral` |

## Conviction

Let `hi` = items with `impact_score >= 6`, `aligned` = items whose sentiment matches overall Bullish/Bearish.

| Conviction | When |
|------------|------|
| **High** | Overall is Bullish or Bearish, **and** `aligned >= 3`, **and** (`hi >= 2` or average impact ≥ 6) |
| **Med** | Overall is Mixed with `hi >= 1`, **or** directional with `aligned >= 2`, **or** average impact ≥ 5 |
| **Low** | Everything else (thin news, Neutral, weak impact) |

## Impact

`india-news-tracker` `score_impact` (1–10). Ingest keeps items ≥ `--min-impact` (default 4), then takes the top slices per kind (news / sectoral / analyst).
