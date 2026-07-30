# Priority Picks → Chat early + Cursor Canvas last (required)

Always present the **same Priority picks board in both places**:

1. **Chat (early)** — full markdown Priority table (readable inline; colours may
   not render because chat strips HTML `style`)
2. **Cursor Canvas (last in the reply)** — same data with orange rows +
   MLBuy/MLSell token colours

Applies to **every** buy and sell / multi-horizon query that produces Priority
picks (intraday, 3–5 days, short-term, long-term).

**Hard rule:** Canvas is **mandatory** and must appear **at the end** of the
chat reply — after Executive Summary, News, Scan Columns, horizon tables,
Watchlist/Avoid, and Disclaimer. Never end after Priority alone. Never put the
Canvas link before those tables.

Follow the Cursor **canvas** skill
(`~/.cursor/skills-cursor/canvas/SKILL.md`) when writing the Canvas file.

## When

After scoring (`query_suggestions.py`) and merging Priority rows:

1. Write/update the `.canvas.tsx` with coloured highlights (can happen anytime
   during the turn).
2. In the chat reply, **lead** with the full Priority markdown table (**no**
   Canvas link yet).
3. **MUST** continue with Executive Summary → News → Scan Columns → horizon
   detail table(s) → Avoid → Disclaimer.
4. **MUST end** the reply with the Canvas markdown link (and a one-line note
   that colours render in Canvas).

## Where (Canvas)

```
~/.cursor/projects/<workspace>/canvases/intraday-priority-picks.canvas.tsx
```

Reuse the same filename for intraday Priority boards (overwrite with fresh
data). For other horizons, use a distinct name, e.g.
`swing-priority-picks.canvas.tsx`.

## Must include (identical columns in chat + Canvas)

1. **Priority table** with columns:
   - Single source: Priority | Symbol | LastDay% | Today% | Sentiment | Conviction | Prob% | Why
   - Multi source: add **Table**
2. **Canvas only — colours:**
   - Row background `#FFE4C4` when buy and (`LastDay% > 3` or `Today% > 3`),
     or sell and (`LastDay% < 3` or `Today% < 3`)
   - In Why: `MLBuy` → `#C6F6D5`, `MLSell` → `#FEB2B2`
3. Short legend in Canvas (and optionally one line in chat)
4. Embed pick data **inline** in Canvas (no `fetch`, no network)
5. Import **only** from `cursor/canvas`

Use helper fields: `last_day_pct`, `today_pct`, `ml_buy`, `ml_sell`,
`row_highlight_orange`, `trade_side`, `probability_score`, `why`.

## Chat Priority table (required — early)

Use a normal markdown pipe table with the same rows as Canvas. Optional text
cues when a row would be orange / has ML tags (chat has no reliable colours):

- Append `· orange` in Why when `row_highlight_orange`
- Keep literal `MLBuy` / `MLSell` in Why when present

Example chat shape:

```markdown
## Priority Picks

| Priority | Table | Symbol | LastDay% | Today% | Sentiment | Conviction | Prob% | Why |
| … |

## Executive Summary
…

## News & Extension Snapshot
…

## Intraday (Same Session)
…

## Watchlist / Avoid
…

## Disclaimer
…

## Coloured Priority Canvas (required — last)
[Open coloured board](…/canvases/intraday-priority-picks.canvas.tsx)
```

## Do not

- Skip the chat Priority table (Canvas-only is not enough)
- Skip the Canvas (chat-only loses colours)
- Put Canvas **before** Executive Summary / other tables
- End the reply after Priority without exec summary / other tables / Canvas
- Dump raw JSON instead of the table

## Reference implementation

`canvases/intraday-priority-picks.canvas.tsx`

Colour rules: [pct-highlight.md](pct-highlight.md).
