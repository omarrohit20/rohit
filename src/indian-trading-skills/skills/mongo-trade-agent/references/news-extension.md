# News Catalyst & May Extend

Rules used by **mongo-trade-agent** when enriching Mongo rankings.

## Required fields

| Field | Format |
|-------|--------|
| `news_catalyst` | One line (≤120 chars). Filing, earnings, JV, sector data, or `No fresh news` |
| `may_extend` | Exactly: `Yes` \| `Possible` \| `Only if X` \| `Weak` \| `No` |
| `news_sentiment` | `Positive` \| `Negative` \| `Mixed` \| `Neutral` (for highlight; see below) |

## News catalyst highlight (Canvas; mark in chat when useful)

Colour the **News catalyst** cell (not the whole Priority row) from the news
tone. Apply in **News & Extension Snapshot**, horizon **News catalyst** columns,
and any Canvas news board. Stacks with orange-row / MLBuy / MLSell rules.

| News tone | When | Cell background |
|-----------|------|-----------------|
| **Positive** | Bullish catalyst (beat, upgrade, JV, buyback, strong guidance, supportive sector) | Light green `#C6F6D5` |
| **Negative** | Bearish catalyst (miss, downgrade, fraud/regulatory hit, weak guidance, adverse sector) | Light red `#FEB2B2` |
| **Mixed** | Conflicting headlines, or news conflicts with tape/helper bias (Sentiment → `Mixed`) | Light yellow `#FEFCBF` |
| **Neutral** / `No fresh news` | No clear polarity or no catalyst | No news colour |

Classify from the catalyst text (and india-news-tracker when used). Prefer the
news tone over tape Sentiment when they differ only for this cell colour; still
set row Sentiment / Conviction per [conviction-sentiment.md](conviction-sentiment.md).

Chat has no reliable HTML colours — optional cue: append `· +news` / `· −news` /
`· mixed news` after the catalyst when coloured in Canvas.

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

1. **News & Extension Snapshot** table (all ranked symbols) — include Sentiment / Conviction / Prob% when present; **highlight News catalyst** per table above (Canvas)
2. Same columns on each horizon detail table (same news colours on News catalyst)
3. Never omit; never invent a catalyst — prefer `No fresh news`
4. If news conflicts with helper bias, set Sentiment to `Mixed`, use **Mixed** (yellow) news highlight, and trim Conviction / Prob% per [conviction-sentiment.md](conviction-sentiment.md)
