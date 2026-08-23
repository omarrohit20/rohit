---
name: scan-news-conviction
description: >-
  Ingest last-5-day Nsedata breakout/moving-average scan scrips, scrape
  news/sector/analyst items, score sentiment and conviction, upsert
  Nsedata.scrip_news (7-day high-impact, deduped; overwrite if older than 30 days).
---

# Scan News Conviction (Cursor)

Canonical: [`skills/scan-news-conviction/SKILL.md`](../../../skills/scan-news-conviction/SKILL.md)

Skill name: **`scan-news-conviction`**

```bash
python skills/scan-news-conviction/scripts/ingest_scan_news.py
python skills/scan-news-conviction/scripts/ingest_scan_news.py --days 5 --news-days 7
```
