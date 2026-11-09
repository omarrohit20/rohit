---
name: scan-news-conviction-futures
description: >-
  All Nsedata.scrip futures=Yes names: upsert scrip_news when a new
  company/analyst headline is in today or yesterday, or a board/results/dividend
  event is today or tomorrow, and not already stored.
---

# Scan News Conviction Futures (Cursor)

Canonical: [`skills/scan-news-conviction-futures/SKILL.md`](../../../skills/scan-news-conviction-futures/SKILL.md)

Skill name: **`scan-news-conviction-futures`**

```bash
python skills/scan-news-conviction-futures/scripts/ingest_futures_news.py
python skills/scan-news-conviction-futures/scripts/ingest_futures_news.py --company-news-days 2
```

Writes **only** `Nsedata.scrip_news`. **Write** when a new company/analyst headline from today/yesterday is not already stored, **or** a board/results/dividend event is **today or tomorrow** (company name must appear in the title). Search ticker **and** company short form (e.g. DATAPATTNS / Data Patterns); include guidance/concall/board/dividend queries; undated catalyst headlines count as today.

End of run prints **SUMMARY NEWS DIGEST**: company news + analyst headlines (no sectoral).
