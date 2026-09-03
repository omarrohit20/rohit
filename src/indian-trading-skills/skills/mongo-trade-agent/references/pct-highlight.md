# LastDay% · Today% · Row / ML Token Highlights

Mandatory columns and colour rules for every mongo-trade-agent Priority and
horizon board. See also [priority-why.md](priority-why.md) and
[priority-canvas.md](priority-canvas.md).

## Columns (always show)

| Column | Source fields (first present wins) | Meaning |
|--------|--------------------------------------|---------|
| **LastDay%** | `PCT_day_change_pre1` → `Ldchange` → `ldchange` | Prior session % change |
| **Today%** | `PCT_day_change` | Session-so-far / today % change |

Format as signed one-decimal (e.g. `+2.4`, `-1.1`). Use `—` if missing.

Helper emits `last_day_pct`, `today_pct`, `ml_buy`, `ml_sell`, `row_highlight_orange`
on ranked rows from `query_suggestions.py`.

## Trade side

| Side | How to detect |
|------|----------------|
| **Buy** | Sentiment `Bullish`, or buy collection / tags (`tobuy`, `*buy*`, `MLBuy`, buy processors) |
| **Sell** | Sentiment `Bearish`, or sell collection / tags (`tosell`, `*sell*`, `MLSell`, sell processors) |

## Row highlight — light orange (`#FFE4C4`)

Apply **full row** background when:

| Side | Condition |
|------|-----------|
| **Buy** | `LastDay% > 3` **OR** `Today% > 3` → full row background `#FFE4C4` |
| **Sell** | `LastDay% < -3` **OR** `Today% < -3` → full row background `#FFE4C4` |

## ML tag highlight — colour the token text (not the scrip)

Scan **all** string fields on the document (`filter`…`filter6`, `ml`, `mlData`,
`intradaytech`, `shorttermtech`, `keyIndicator`, `processor`, etc.). When present,
render the literal token **`MLBuy` / `MLSell`** in Why with a coloured background
— do **not** colour the Symbol/scrip cell for this rule.

| Tag in DB | Token text background |
|-----------|------------------------|
| Contains `MLBuy` (case-insensitive) | Light green `#C6F6D5` on **MLBuy** |
| Contains `MLSell` (case-insensitive) | Light red `#FEB2B2` on **MLSell** |

If both appear, show both coloured tokens in Why.

Row orange and ML-token colour **stack**: orange row + green/red **MLBuy**/**MLSell** text.

### Canvas implementation (mandatory)

Copy [../assets/priority-canvas-snippet.tsx](../assets/priority-canvas-snippet.tsx).
Colour **only** with `<Text style={{ backgroundColor: "…" }}>`. **Never** use
`<Pill tone="…">` for MLBuy / MLSell / news — Canvas SDK ignores Pill tones.

## Momentum keyword highlight — light green / light red in Why column

Colour **only the keyword token** in the Why column (same pattern as MLBuy /
MLSell chips — not the Symbol cell, not the full row).

| Keyword in Why | Today% threshold | Token background |
|----------------|------------------|------------------|
| `UpStairs` or `#UpStairs` | `> 2` | Light green `#C6F6D5` |
| `UpPostLunchConsolidation` (optional `:suffix`) | `> 3` | Light green `#C6F6D5` |
| `DownStairs` or `#DownStairs` | `< -2` | Light red `#FEB2B2` |
| `DownPostLunchConsolidation` (optional `:suffix`) | `< -3` | Light red `#FEB2B2` |

Keywords must appear literally in Why text (or `whyText` parts). `MomentumWhyText`
in `priority-canvas-snippet.tsx` parses and chips only matching tokens when the
Today% threshold is met. Other highlights (orange Symbol, MLBuy/MLSell, news,
Sentiment) are unchanged.

## News catalyst highlight — colour the News cell (not the whole Priority row)

Apply on **News catalyst** in News & Extension Snapshot, horizon detail tables,
and Canvas news boards. Full rules: [news-extension.md](news-extension.md).

| News tone | Cell background |
|-----------|-----------------|
| **Positive** | Light green `#C6F6D5` |
| **Negative** | Light red `#FEB2B2` |
| **Mixed** | Light yellow `#FEFCBF` |
| **Neutral** / `No fresh news` | No news colour |

Stacks with orange row and ML tokens when those also apply.

## Sentiment cell highlight (Canvas — aligned with news)

Colour the **Sentiment** cell only when tape bias and news tone agree:

| Sentiment | News tone | Sentiment cell background |
|-----------|-----------|---------------------------|
| **Bullish** | **Positive** | Light green `#C6F6D5` |
| **Bearish** | **Negative** | Light red `#FEB2B2` |
| Any other combo (Neutral, Mixed, mismatched news, no news) | — | No colour |

Use `pick.newsTone` or the matching `newsRows` tone. Snippet helper:
`SentimentCell` in [../assets/priority-canvas-snippet.tsx](../assets/priority-canvas-snippet.tsx).

## Rendering — Chat table early + Cursor Canvas last

**Required for every buy/sell Priority board:**

1. **Chat (early)** — full markdown Priority table (same columns/rows; colours
   may not show because chat strips HTML `style`)
2. **Full report tables (mandatory)** — Executive Summary, News, Scan Columns,
   asked horizon detail table(s), Watchlist/Avoid, Disclaimer
3. **Cursor Canvas (last)** — same Priority data with orange rows + MLBuy/MLSell
   token colours + News catalyst green/red/yellow + Sentiment green/red when
   Bullish+positive / Bearish+negative; link only at the end of the reply

See [priority-canvas.md](priority-canvas.md). Do not omit chat table, report
tables, or Canvas.

## Lead table shapes (chat + Canvas)

### Single table

| Priority | Symbol | LastDay% | Today% | Sentiment | Conviction | Prob% | Why |
|----------|--------|----------|--------|-----------|------------|-------|-----|

### Multiple tables

| Priority | Table | Symbol | LastDay% | Today% | Sentiment | Conviction | Prob% | Why |
|----------|-------|--------|----------|--------|-----------|------------|-------|-----|
