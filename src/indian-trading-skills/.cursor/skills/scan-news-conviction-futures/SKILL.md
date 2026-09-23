---
name: scan-news-conviction-futures
description: >-
  All Nsedata.scrip futures=Yes names: upsert scrip_news only when a new
  company/analyst headline is in today or yesterday and not already stored.
---

# Scan News Conviction Futures (Cursor)

Canonical: [`skills/scan-news-conviction-futures/SKILL.md`](../../../skills/scan-news-conviction-futures/SKILL.md)

Skill name: **`scan-news-conviction-futures`**

```bash
python skills/scan-news-conviction-futures/scripts/ingest_futures_news.py
python skills/scan-news-conviction-futures/scripts/ingest_futures_news.py --company-news-days 2
```

Writes **only** `Nsedata.scrip_news`. **Skip** unless a new company/analyst headline from today/yesterday is not already stored (company name must appear in the title).

End of run prints **SUMMARY NEWS DIGEST**: company news + analyst headlines (no sectoral).
