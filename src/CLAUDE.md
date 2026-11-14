# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A personal Indian-equities (NSE) trading research system on Windows. The parts are loosely coupled Python scripts that talk to each other only through a **local MongoDB** (`localhost:27017`), never through imports. Each script opens its own `MongoClient`. There is no build step, linter, or test suite for `src/` itself. The files in `machine-learning/test/` and `test/` are ad-hoc scripts, not pytest suites. The interpreter in use is Python 3.10. The `.python-version` files (3.5.0) are stale.

The git repo root is `C:\git\rohit`. This `src/` folder is one level below it, and the root `.gitignore` uses `src/...` paths.

## Databases

- `Nsedata`: the master data. `scrip` is the universe; `futures: "Yes"/"No"` marks F&O stocks and drives many filters. It also holds daily/15-minute price history, `scrip_news` (news sentiment and conviction), `ai-analysis`, the `investment-*` collections, and the regression output collections (`breakoutYH`, `breakoutY2H`, `breakoutW2HR`, `movingavg_crossed_up`/`_down`, …).
- `chartlink`: intraday scan hits scraped from chartink.com. There is one collection per screener "processor" name, e.g. `buy-morning-volume-breakout(Check-News)`.

Collection names are string literals spread across the scrapers, regression, and reports. Renaming a collection means grepping every pipeline.

## Pipelines

The top-level `.bat` files are the entry points. They `cd` into a subfolder and run scripts with stdin detached (`<nul`) so Python never blocks waiting for input.

1. **Data import** (`data_import.bat` → `data-import/importer-history.bat`): `S0cripImporter.py` loads the scrip universe. The `S2cripHistoryImporter*.py` scripts pull OHLC history, mostly from Yahoo (`S2cripHistoryImporterYahoo.py all|update Yes|No`, where the second argument is the `futures` flag) and write to `Nsedata`. `S1` imports fundamentals and `S3` imports results.
2. **Regression / signals** (`regression.bat` → `machine-learning/regression/regression_run_futures.bat`): `regression.py <futures Yes|No> <Yes|No>` computes TA-Lib indicators, then `regression_result.py` writes the signal collections. The shared helpers live in `machine-learning/util/` (`util.py`, `technical.py`, `util_buy.py`/`util_sell.py`). Scripts reach them with `sys.path.insert(0, '../')`, so **run them from inside `machine-learning/regression/`**. `cleanupdata.py` runs last.
3. **Chartink intraday scrapers** (`all_the_scripts.bat` → `chartlink_import/`): six `bpm_*.py` scripts run in parallel (b = buy, s = sell; `_vol`, `_mcup`/`_mcdown`, `_indices`). Each one opens a persistent Playwright Chromium profile under `chartlink_import/profiles/pN` (a logged-in session; don't delete it) and loops through the trading day. Inside that loop, time windows (`config.py`) gate calls to `sbase.process_url_volBreakout(url, processor, start, end)`. That function intercepts chartink's `/backtest/process` response and writes to `chartlink.<processor>`. The huge comments above each call are the chartink screener formulas, kept for reference.
4. **Reports UI** (`reports.bat`): run `streamlit run index.py` from `reports/`. `index.py` auto-discovers every `*.py` page in `reports/`, except the files in its `exclude` set. It either imports a page in-process and calls its `main()`, or launches it as a separate Streamlit process on a free port. **New pages must expose `main()`**. If a page is a helper module rather than a page, add it to `exclude`.
   - `rbase.py` is the shared backend for every page. It holds the Mongo handles (`dbcl` = chartlink, `dbnse` = Nsedata), cached `getdf()` loaders, the global sidebar filters (industry, market cap, %-change bands, news sentiment, index), row/column highlight stylers, and sidebar prefs that persist to Mongo. Add shared logic there rather than in individual pages.
   - `PERFORMANCE_ISSUES.md`, `OPTIMIZATION_EXAMPLES.md`, and `BEFORE_AFTER_COMPARISON.md` at the repo root document known `rbase.py` problems: full-collection loads and per-row `count_documents` calls. Use the `_lookup` TTL cache and `_cnt`/`_scrips` helpers rather than adding per-row queries.
5. **Sentiment** (`reports-sentiments.bat` → `sentiment/`): scrapes Zerodha Pulse and MoneyControl, then scores sentiment with the Groq LLM (`GROQ_API_KEY`, `config.py`). Run it with `python main.py` or as the Streamlit app `sentiment_analysis.py`.

## `indian-trading-skills/`

A separate sub-project of Claude skills (`skills/*/SKILL.md` plus scripts). It has its own `CLAUDE.md`, `AGENTS.md`, `pyproject.toml`, and venv. **Read its `CLAUDE.md` when working there.** The skills read and write the same local Mongo. For example, `scan-news-conviction(-futures)` writes `Nsedata.scrip_news`, which the report filters in `rbase.py` consume. Tests and lint run from that folder:

```
pip install -e .[dev]
pytest                                   # testpaths set in pyproject.toml
pytest skills/nse-vcp-screener/scripts/tests/test_x.py::test_name
ruff check .
```

## Rules

- **Upstox is opt-in** (from `.cursor/rules/upstox-login.mdc`). Never call Upstox MCP tools or `mcp_auth`, or run `upstox-python-sdk`, unless the user explicitly asks for live data or a live order. Keep Upstox out of the live `mcp.json` files.
- Don't place live orders. Trading output is educational only, not SEBI advice.
- `output/`, `*.log` files, and `chartlink_import/profiles/` are generated or runtime state. Don't commit them.
