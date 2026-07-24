---
name: nsedata-trade-advisor
description: >-
  Query local MongoDB Nsedata/chartlink scan collections and produce ranked
  trading and investment suggestions for intraday, 3-5 days, short-term, and
  long-term horizons. Use when the user asks for Mongo-based trade ideas,
  analyzes highBuy/breakout/chartlink tables, or wants multi-horizon targets
  from their local Indian market database.
---

# Nsedata Multi-Horizon Trade Advisor

Connect to the user's **local MongoDB** (`Nsedata` + `chartlink`), query a **given scan collection**, enrich with OHLCV/`technical`/`fundamental`, and return ranked suggestions across four horizons.

**Prerequisite:** MongoDB running on `localhost:27017`. Prefer MongoDB MCP (see **mongodb-local-mcp**). If MCP is unavailable, run the Python helper below.

## Time Horizons

| Horizon | Holding | Primary data |
|---------|---------|--------------|
| **Intraday** | Same session (exit by 3:30 PM IST) | `history15m` + scan `PCT_day_change` / `intradaytech` / `ml*` |
| **3–5 days** | ~3–5 sessions | Last ~10 daily bars + `forecast_day_PCT3/5_change` + week H/L changes |
| **Short-term** | 1–20 trading days | 60 daily bars + `technical.short_term` + SMA/RSI |
| **Long-term** | 1–12+ months | 252+ daily bars + year H/L + `fundamental.peratio` |

All prices in **INR (₹)**. Educational analysis only — not SEBI-registered advice.

## Workflow

```
Task Progress:
- [ ] Step 1: Confirm Mongo connectivity (MCP or pymongo helper)
- [ ] Step 2: Resolve database + collection from user ("given table")
- [ ] Step 3: Sample/scan candidates from that collection
- [ ] Step 4: Enrich each scrip from history / history15m / technical / fundamental
- [ ] Step 5: Score all four horizons (or user-requested subset)
- [ ] Step 6: Present ranked report using the template
```

### Step 1 — Connect

1. Try MCP: `list-databases` → expect `Nsedata`, `chartlink`.
2. If MCP missing, run the helper (works for Cursor, Claude, Copilot):

```bash
python skills/nsedata-trade-advisor/scripts/query_suggestions.py \
  --db Nsedata --collection highBuy --limit 20 --horizons all
```

Chartlink example:

```bash
python skills/nsedata-trade-advisor/scripts/query_suggestions.py \
  --db chartlink --collection morning-volume-breakout-buy --limit 20 --horizons intraday,swing3_5
```

### Step 2 — Resolve the given table

| User says | Database | Collection |
|-----------|----------|------------|
| `highBuy` | `Nsedata` | `highBuy` |
| `breakoutMH` | `Nsedata` | `breakoutMH` |
| `chartlink.morning-volume-breakout-buy` | `chartlink` | `morning-volume-breakout-buy` |
| Unspecified | Ask once; default `Nsedata.highBuy` | |

Schema details: [references/nsedata-schema.md](references/nsedata-schema.md).

### Step 3 — Fetch scan rows

MCP `find` (limit 30–50), sort by `date` or `eventtime` descending.

**Do not project a short field list.** Load the full document. Discover columns via `collection-schema` or helper `meta.scan_columns`. Use every signal field present: `filter*`, `intradaytech`, `ml`/`mlData`, `PCT_*`, `Ldchange`, forecasts, week/month/year structure, chartlink `tobuy`/`keyIndicator`, etc.

### Step 4 — Enrich

For each `scrip`:

| Need | Collection | Match |
|------|------------|-------|
| Daily OHLCV | `Nsedata.history` | `dataset_code` = scrip |
| 15m OHLCV | `Nsedata.history15m` | `dataset_code` = scrip |
| Technicals | `Nsedata.technical` | `dataset_code` = scrip |
| Fundamentals | `Nsedata.fundamental` | `scrip` = scrip |

**Critical:** `history` / `history15m` store `data` as **newest-first** arrays with `column_names: [Date, Open, High, Low, Close, Volume]`. Reverse to chronological before computing indicators. Prefer the Python helper for unpacking.

### Step 5 — Horizon scoring (summary)

Full indicator math matches the helper and [../mongodb-financial-analysis/references/target-methodology.md](../mongodb-financial-analysis/references/target-methodology.md).

**Intraday:** VWAP, session H/L, opening-range stop, +points for price > VWAP, BreakHigh/MLBuy/TOP5B tags, ReversalLow, AnchisBuyUp, NearHigh*.

**3–5 days:** Positive `forecast_day_PCT3/5_change`, ReversalLow/BreakHigh filters, week structure, 1–1.5× ATR targets.

**Short-term:** Close > SMA20 > SMA50, RSI 40–65, swing S/R, 1–3× ATR targets; avoid RSI > 75 fresh longs.

**Long-term:** Close > SMA200, 52w range position, PE overlay, Fib/52w-high targets; invalidation near SMA200 / year low.

Reject setups with R:R < 1:1.5 when possible; mark as watchlist instead.

### Step 6 — Output

Use [assets/four-horizon-report.md](assets/four-horizon-report.md). **Lead with:**

| Priority | Symbol | Why |
|----------|--------|-----|
| 1 | | scan tags + tape + news |

Always include:

1. Data source (db, collection, candidate count, **scan_columns**)
2. Priority | Symbol | Why (top 5)
3. Top per horizon with entry / T1–T2 / stop / R:R
4. **News catalyst** and **May extend?** for every ranked symbol
5. Alignment note + disclaimer

Helper JSON provides `priority_table`, `why_hint`, `scan_columns`, and null `news_catalyst` / `may_extend` / `why` — polish Why with news before presenting.

**May extend? values:** `Yes` · `Possible` · `Only if X` · `Weak` · `No`

## Agent / Platform Notes

| Platform | How to use |
|----------|------------|
| **Cursor** | Project [`.cursor/mcp.json`](../../.cursor/mcp.json) + this skill; or run Python helper |
| **Claude Desktop** | Merge [../mongodb-local-mcp/assets/claude-desktop-mcp-config.example.json](../mongodb-local-mcp/assets/claude-desktop-mcp-config.example.json) into `claude_desktop_config.json`; keep this skill in project knowledge |
| **GitHub Copilot** | Keep `skills/nsedata-trade-advisor/` in repo context; run `query_suggestions.py` for data (MCP optional) |

## Example Prompts

```
Using nsedata-trade-advisor, query chartlink morning-volume-breakout-buy
and suggest what may go up further today and over 3-5 days.
```

```
Analyze Nsedata.highBuy for short-term and long-term investment candidates;
rank top 5 with targets and stops.
```

```
Run the query_suggestions helper on breakoutMH and summarize all four horizons.
```

## Related Skills

- **mongodb-local-mcp** — MCP setup / troubleshooting
- **mongodb-financial-analysis** — generic flat-candle schemas only; prefer this skill for `Nsedata`/`chartlink`
- **india-news-tracker** — news catalysts for shortlisted symbols
