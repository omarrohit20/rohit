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

Helper emits `last_day_pct`, `today_pct`, `ml_buy`, `ml_sell`,
`row_highlight_orange`, `row_highlight_green` on ranked rows from
`query_suggestions.py`.

## Trade side

| Side | How to detect |
|------|----------------|
| **Buy** | Sentiment `Bullish`, or buy collection / tags (`tobuy`, `*buy*`, `MLBuy`, buy processors) |
| **Sell** | Sentiment `Bearish`, or sell collection / tags (`tosell`, `*sell*`, `MLSell`, sell processors) |

## Row highlight — light orange (`#FFE4C4`)

Apply **full row** / Symbol chip when:

| Side | Condition |
|------|-----------|
| **Buy** | `LastDay% > 3` **OR** `Today% > 3` → orange `#FFE4C4` |
| **Sell** | `LastDay% < -3` **OR** `Today% < -3` → orange `#FFE4C4` |

## Row highlight — light green (`#C6F6D5`)

Apply **Symbol chip** (and Canvas `rowTone="success"`) when **all** of:

1. Scan string fields contain **`BreakHighYear`** or **`BreakHighYear2`**
2. Scan string fields contain **`ReversalLow`**
3. **`Today%` between −1.3 and +1.3** inclusive (`-1.3 <= Today% <= 1.3`)

Helper flag: `row_highlight_green`.

If both green and orange apply, **green wins** on the Symbol chip (orange may still
be noted in Why as `· orange`).

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

Row orange, green setup, and ML-token colour **stack** where applicable:
green Symbol (setup) beats orange Symbol; MLBuy/MLSell tokens still colour in Why.

### Canvas implementation (mandatory)

Copy [../assets/priority-canvas-snippet.tsx](../assets/priority-canvas-snippet.tsx).
Colour **only** with `<Text style={{ backgroundColor: "…" }}>`. **Never** use
`<Pill tone="…">` for MLBuy / MLSell / news — Canvas SDK ignores Pill tones.

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

## Rendering — Chat table early + Cursor Canvas last

**Required for every buy/sell Priority board:**

1. **Chat (early)** — full markdown Priority table (same columns/rows; colours
   may not show because chat strips HTML `style`)
2. **Full report tables (mandatory)** — Executive Summary, News, Scan Columns,
   asked horizon detail table(s), Watchlist/Avoid, Disclaimer
3. **Cursor Canvas (last)** — same Priority data with orange/green rows + MLBuy/MLSell
   token colours + News catalyst green/red/yellow; link only at the end of the reply

See [priority-canvas.md](priority-canvas.md). Do not omit chat table, report
tables, or Canvas.

## Lead table shapes (chat + Canvas)

### Single table

| Priority | Symbol | LastDay% | Today% | Sentiment | Conviction | Prob% | Why |
|----------|--------|----------|--------|-----------|------------|-------|-----|

### Multiple tables

| Priority | Table | Symbol | LastDay% | Today% | Sentiment | Conviction | Prob% | Why |
|----------|-------|--------|----------|--------|-----------|------------|-------|-----|
