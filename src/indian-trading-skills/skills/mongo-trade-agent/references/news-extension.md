# News Catalyst & May Extend

Rules used by **mongo-trade-agent** when enriching Mongo rankings.

## Required fields

| Field | Format |
|-------|--------|
| `news_catalyst` | One line (≤120 chars). Filing, earnings, JV, sector data, or `No fresh news` |
| `may_extend` | Exactly: `Yes` \| `Possible` \| `Only if X` \| `Weak` \| `No` |

## Decision matrix

| Situation | may_extend |
|-----------|------------|
| Fresh catalyst still unfolding for this horizon | Yes |
| Soft/older news; tape + R:R can continue | Possible |
| Binary pending event | Only if [event] |
| Extended move, weak R:R, or no news | Weak |
| Adverse news or broken VWAP/setup | No |

## Sources (priority)

1. Exchange filings / company announcements (BSE/NSE)
2. Tier-1 financial media (last 1–7 days)
3. Sector data (exports, rates, policy) when stock-specific news is thin
4. **india-news-tracker** skill when available

## Output placement

1. **News & Extension Snapshot** table (all ranked symbols) — include Sentiment / Conviction / Prob% when present
2. Same columns on each horizon detail table
3. Never omit; never invent a catalyst — prefer `No fresh news`
4. If news conflicts with helper bias, set Sentiment to `Mixed` and trim Conviction / Prob% per [conviction-sentiment.md](conviction-sentiment.md)
