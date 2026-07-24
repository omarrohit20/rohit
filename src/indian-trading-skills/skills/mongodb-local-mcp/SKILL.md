---
name: mongodb-local-mcp
description: >-
  Connect local MongoDB to Cursor via the official MongoDB MCP server. Use when
  setting up MongoDB MCP, configuring mcp.json, troubleshooting local database
  connections, or discovering collections and schemas for Indian market data.
---

# MongoDB Local MCP Setup

Connect a local MongoDB instance to Cursor using the official [MongoDB MCP Server](https://www.npmjs.com/package/mongodb-mcp-server). Once connected, the agent can list databases, inspect schemas, and run read-only queries against your financial data.

## Prerequisites

| Requirement | Details |
|-------------|---------|
| Node.js | 20.19+ (or 22.12+, or 23+) — verify with `node -v` |
| MongoDB | Local instance running (default port 27017) |
| Cursor | MCP support enabled (Settings → MCP) |

**Start local MongoDB (if not running):**

```bash
# Windows (if installed as service)
net start MongoDB

# Or via mongod directly
mongod --dbpath C:\data\db

# macOS/Linux (Homebrew)
brew services start mongodb-community
```

## Cursor MCP Configuration

### Option A: Global config (all projects)

Edit `~/.cursor/mcp.json` (Windows: `%USERPROFILE%\.cursor\mcp.json`).

### Option B: Workspace config (this project only)

Create `.cursor/mcp.json` in the project root.

### Recommended local config (read-only)

Copy from [assets/cursor-mcp-config.example.json](assets/cursor-mcp-config.example.json) or use:

```json
{
  "mcpServers": {
    "MongoDB": {
      "command": "npx",
      "args": ["-y", "mongodb-mcp-server@latest", "--readOnly"],
      "env": {
        "MDB_MCP_CONNECTION_STRING": "mongodb://localhost:27017",
        "MDB_MCP_READ_ONLY": "true"
      }
    }
  }
}
```

Also see [assets/claude-desktop-mcp-config.example.json](assets/claude-desktop-mcp-config.example.json) for Claude Desktop (`claude_desktop_config.json`).

**Customize:**
- Root URI `mongodb://localhost:27017` exposes all DBs (`Nsedata`, `chartlink`, `nsehistnew`)
- Add auth if enabled: `mongodb://user:password@localhost:27017/?authSource=admin`
- Remove `--readOnly` and set `MDB_MCP_READ_ONLY` to `false` only when writes are needed

### Verify before restarting Cursor

```powershell
# Windows PowerShell
$env:MDB_MCP_CONNECTION_STRING="mongodb://localhost:27017"
npx -y mongodb-mcp-server@latest --readOnly --dryRun
```

```bash
# macOS/Linux
export MDB_MCP_CONNECTION_STRING="mongodb://localhost:27017"
npx -y mongodb-mcp-server@latest --readOnly --dryRun
```

Expected: configuration summary and list of registered tools (`find`, `aggregate`, `list-databases`, etc.).

**After saving mcp.json:** fully restart Cursor (close and reopen).

## MCP Tools Available

Once connected, use `CallMcpTool` with server `MongoDB`. Always read tool schemas from the MCP descriptors folder before calling.

| Tool | Purpose |
|------|---------|
| `list-databases` | Discover databases on the instance |
| `list-collections` | List collections in a database |
| `collection-schema` | Infer field types from sample documents |
| `find` | Query documents with filter and projection |
| `aggregate` | Run aggregation pipelines |
| `count` | Count documents (optionally filtered) |

For full tool reference and query patterns, see [references/mcp-tools.md](references/mcp-tools.md).

## Discovery Workflow

When the user asks to connect or explore their database, follow this sequence:

```
Task Progress:
- [ ] Step 1: Confirm MongoDB is running locally
- [ ] Step 2: Verify MCP config and restart Cursor if needed
- [ ] Step 3: Call list-databases to confirm connection
- [ ] Step 4: Call list-collections on the target database
- [ ] Step 5: Call collection-schema on key collections
- [ ] Step 6: Sample 3-5 documents with find (limit 5)
- [ ] Step 7: Summarize schema and suggest analysis path
```

**Step 1 — Check MongoDB is running:**

```bash
mongosh --eval "db.adminCommand('ping')"
```

**Steps 3-6 — Use MCP tools** (read schema first, then call):

1. `list-databases` — expect `Nsedata`, `chartlink` (and optionally `nsehistnew`)
2. `list-collections` with database name
3. `collection-schema` for each collection that looks like market data
4. `find` with `limit: 5` to see real document shape

## Expected Financial Data Schema

**Live deployment (this repo):** databases `Nsedata` + `chartlink` with embedded OHLCV arrays. See [../nsedata-trade-advisor/references/nsedata-schema.md](../nsedata-trade-advisor/references/nsedata-schema.md).

Generic layout (if using flat candle docs instead):

| Collection | Interval | Key fields |
|------------|----------|------------|
| `candles_intraday` | 1m, 5m, 15m | `symbol`, `exchange`, `interval`, `timestamp`, `open`, `high`, `low`, `close`, `volume` |
| `candles_daily` | 1d | Same OHLCV fields, one bar per trading day |
| `candles_weekly` | 1wk | Weekly aggregated OHLCV |
| `symbols` | — | `symbol`, `name`, `exchange`, `sector`, `isin` |
| `fundamentals` | — | `symbol`, `pe`, `pb`, `roe`, `marketCap`, `asOfDate` |

Full generic schema: [references/schema-conventions.md](references/schema-conventions.md).

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| MCP tools not visible | Restart Cursor; validate JSON in mcp.json |
| Connection refused | Start MongoDB; check port 27017 |
| Authentication failed | Add credentials to connection string; check `authSource` |
| Empty collections | Confirm database name (`Nsedata` / `chartlink`); connection string should be root URI without a wrong DB path |
| `npx` not found | Install Node.js 20.19+ |
| Slow queries | Check indexes on `symbol` + `timestamp`; see schema reference |

## Security Notes

- Prefer `--readOnly` / `MDB_MCP_READ_ONLY=true` for analysis workflows
- Never commit credentials in mcp.json — use env vars or Cursor's secret handling
- Local MongoDB without auth is fine for dev; enable auth for shared machines

## Next Step

After discovery on `Nsedata` / `chartlink`, use the **nsedata-trade-advisor** skill for intraday, 3–5 day, short-term, and long-term suggestions from a given scan collection.

For generic flat-candle schemas, use **mongodb-financial-analysis**.
