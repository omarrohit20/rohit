# Priority Picks → Chat early + Cursor Canvas last (required)

Always present the **same Priority picks board in both places**:

1. **Chat (early)** — full markdown Priority table (readable inline; colours may
   not render because chat strips HTML `style`)
2. **Cursor Canvas (last in the reply)** — same data with orange rows +
   MLBuy/MLSell token colours + News catalyst green/red/yellow

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

1. **Create a brand-new** `.canvas.tsx` with coloured highlights (never overwrite
   an existing canvas). Can write anytime during the turn.
2. In the chat reply, **lead** with the full Priority markdown table (**no**
   Canvas link yet).
3. **MUST** continue with Executive Summary → News → Scan Columns → horizon
   detail table(s) → Avoid → Disclaimer.
4. **MUST** open the new canvas via MCP `cursor-app-control` → `open_resource`
   (`file:///C:/Users/.../canvases/<unique>.canvas.tsx`) so it loads beside
   chat. Then end the reply with the filename + one-line note that colours
   are in Canvas.

**Windows:** Do **not** rely on clickable markdown links to `C:\...` or
`C:/...` paths — Cursor treats `C:` as a URI scheme and the click fails
(“Unable to resolve resource”). Opening via `open_resource` is the reliable
path; users can also use the **Canvas** panel/tab and pick the new file.

## Where (Canvas) — NEW FILE EVERY QUERY

**Never reuse or overwrite** a previous canvas. Cursor often fails to reopen or
refresh a mutated `.canvas.tsx`; each query must get a **new filename**.

Write **only** under the current workspace canvases directory:

```
~/.cursor/projects/<workspace>/canvases/<unique-name>.canvas.tsx
```

On this machine the workspace folder is typically:

```
C:\Users\User\.cursor\projects\c-git-rohit-src-indian-trading-skills\canvases\
```

Do **not** write under a parent project path (e.g. `...\c-git-rohit\canvases\`)
unless that is the active workspace root.

### Filename pattern (required)

```
{horizon}-priority-{collection}-{YYYYMMDD-HHmmss}.canvas.tsx
```

| Part | Rule |
|------|------|
| `horizon` | `intraday` · `swing` · `short-term` · `long-term` · `multi` |
| `collection` | kebab-case table name(s); join multi with `-` (truncate if huge) |
| `YYYYMMDD-HHmmss` | local timestamp when the canvas is created |

Examples:

- `intraday-priority-sell-all-processor-20260730-113530.canvas.tsx`
- `intraday-priority-buy-all-processor-20260730-120015.canvas.tsx`
- `swing-priority-highBuy-buy-all-processor-20260730-121000.canvas.tsx`

If that path already exists (clock collision), append `-2`, `-3`, etc. **Never**
overwrite.

Component `export default function` name may be any valid PascalCase identifier
derived from the file (e.g. `IntradayPrioritySellAllProcessor20260730113530`).

## Must include (identical columns in chat + Canvas)

1. **Priority table** with columns:
   - Single source: Priority | Symbol | LastDay% | Today% | Sentiment | Conviction | Prob% | Why
   - Multi source: add **Table**
2. **Canvas only — colours:**
   - Prefer Table `rowTone="warning"` when buy and (`LastDay% > 3` or `Today% > 3`),
     or sell and (`LastDay% < -3` or `Today% < -3`) (SDK equivalent of orange row)
   - In Why: `MLBuy` → light green `#C6F6D5`, `MLSell` → light red `#FEB2B2`
   - **News catalyst** cell: Positive → `#C6F6D5`, Negative → `#FEB2B2`,
     Mixed → `#FEFCBF` (see [news-extension.md](news-extension.md)); include a
     short News snapshot table in Canvas when catalysts exist
3. Short legend in Canvas (and optionally one line in chat) — include news colours
4. Embed pick data **inline** in Canvas (no `fetch`, no network)
5. Import **only** from `cursor/canvas`

Use helper fields: `last_day_pct`, `today_pct`, `ml_buy`, `ml_sell`,
`row_highlight_orange`, `trade_side`, `probability_score`, `why`, plus
`news_catalyst` / `news_sentiment` / `may_extend` when enriching.

## Chat Priority table (required — early)

Use a normal markdown pipe table with the same rows as Canvas. Optional text
cues when a row would be orange / has ML tags / news polarity (chat has no
reliable colours):

- Append `· orange` in Why when `row_highlight_orange`
- Keep literal `MLBuy` / `MLSell` in Why when present
- Append `· +news` / `· −news` / `· mixed news` on News catalyst when coloured in Canvas

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

Opened beside chat via Canvas panel.

File: `intraday-priority-sell-all-processor-20260730-113530.canvas.tsx`

(If the panel closed: Canvas tab → that filename, or ask to reopen.)
```

### Opening on Windows (required)

After writing the `.canvas.tsx`, **always** call MCP `open_resource` with a
`file:///` URI (forward slashes, three slashes after `file:`):

```
file:///C:/Users/User/.cursor/projects/<workspace>/canvases/<unique-name>.canvas.tsx
```

In the chat reply **do not** use markdown links like
`[label](C:/Users/...)` or `[label](C:\Users\...)` — those clicks break on
Windows. Instead:

1. State that the canvas was opened beside chat.
2. Put the **basename only** in backticks (e.g.
   `` `intraday-priority-sell-all-processor-20260730-113530.canvas.tsx` ``).
3. Optionally paste the full path in backticks as a fallback for Ctrl+P /
   Canvas tab search — still no `[markdown](C:...)` link.

## Do not

- Skip the chat Priority table (Canvas-only is not enough)
- Skip the Canvas (chat-only loses colours)
- **Reuse / overwrite** `intraday-priority-picks.canvas.tsx` or any prior canvas
- Put Canvas **before** Executive Summary / other tables
- End the reply after Priority without exec summary / other tables / Canvas
- Dump raw JSON instead of the table
- Write the canvas outside the active workspace `canvases/` folder
- Use clickable markdown `[text](C:/...)` / `[text](C:\...)` links on Windows
  (broken — use `open_resource` instead)

## Reference

Colour rules: [pct-highlight.md](pct-highlight.md).  
News catalyst colours: [news-extension.md](news-extension.md).  
Prior fixed name `intraday-priority-picks.canvas.tsx` is **deprecated** — keep
only as a historical example; do not update it for new queries.
