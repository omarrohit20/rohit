---
name: scan-news-conviction-futures
description: >-
  All Nsedata.scrip futures=Yes names: scrape news if scrip_news was not
  created/updated in the last 3 days, or if new company-specific news is in the
  last 2 days; upsert Nsedata.scrip_news only; print summary.
---

# Scan News Conviction Futures (Cursor)

Canonical: [`skills/scan-news-conviction-futures/SKILL.md`](../../../skills/scan-news-conviction-futures/SKILL.md)

Skill name: **`scan-news-conviction-futures`**

```bash
python skills/scan-news-conviction-futures/scripts/ingest_futures_news.py
python skills/scan-news-conviction-futures/scripts/ingest_futures_news.py --stale-days 3 --news-days 7
```

Writes **only** `Nsedata.scrip_news`. Skip scrips whose `scrip_news` was created or updated in the last three days **unless new company-specific news is in the last 2 days**.

End of run prints **SUMMARY NEWS DIGEST**: company news list + high-conviction sectoral news.
