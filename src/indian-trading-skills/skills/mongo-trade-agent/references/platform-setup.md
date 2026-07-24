# Platform Setup — Mongo Trade Agent

Connect local MongoDB to **Cursor**, **Claude**, and **GitHub Copilot**.

## 1. Start MongoDB

```powershell
# Windows service
net start MongoDB

# Or ping via Python
python -c "from pymongo import MongoClient; MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000).admin.command('ping'); print('OK')"
```

Expected databases: `Nsedata`, `chartlink`.

## 2. Install Python dependency

```bash
pip install pymongo
# or from repo root
pip install -e ".[mongo]"
```

## 3. Cursor

### MCP (preferred)

Project file already at [`.cursor/mcp.json`](../../../.cursor/mcp.json):

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

1. Ensure Node.js 20.19+ (`node -v`)
2. Restart Cursor after saving MCP config
3. Skills load from `skills/mongo-trade-agent/` and `.cursor/skills/mongo-trade-agent/`

### Skill discovery

- Project: `.cursor/skills/mongo-trade-agent/SKILL.md`
- Repo skills: `skills/mongo-trade-agent/SKILL.md`
- Personal (optional): copy skill folder to `%USERPROFILE%\.cursor\skills\mongo-trade-agent\`

### Fallback without MCP

```bash
python skills/nsedata-trade-advisor/scripts/query_suggestions.py --db Nsedata --collection highBuy --limit 20 --horizons all
```

## 4. Claude Desktop

1. Open Claude Desktop → Settings → Developer → Edit Config
2. Merge MCP block from [../../mongodb-local-mcp/assets/claude-desktop-mcp-config.example.json](../../mongodb-local-mcp/assets/claude-desktop-mcp-config.example.json) into `claude_desktop_config.json`
3. Restart Claude Desktop
4. Add project folder / `skills/mongo-trade-agent/SKILL.md` to project knowledge

**Claude Code (CLI):** open this repo; Claude discovers `skills/**/SKILL.md` and `CLAUDE.md`.

## 5. GitHub Copilot (VS Code / Copilot Chat)

1. Repo instructions: [`.github/copilot-instructions.md`](../../../.github/copilot-instructions.md)
2. Cross-tool rules: [`AGENTS.md`](../../../AGENTS.md)
3. Optional MCP in VS Code: Settings → MCP → add same MongoDB server as Cursor
4. Always run `query_suggestions.py` when MCP is unavailable

Prompt example:

```
Follow AGENTS.md mongo-trade-agent. Query Nsedata.highBuy for intraday, 3-5 days, short-term, and long-term suggestions.
```

## 6. Smoke test

```bash
python skills/nsedata-trade-advisor/scripts/query_suggestions.py \
  --db Nsedata --collection highBuy --limit 5 --horizons all --top 3
```

Expect JSON with `meta`, `candidates`, and `rankings` for each horizon.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Connection refused | Start MongoDB on port 27017 |
| Collection not found | List with helper error output or MCP `list-collections` |
| `pymongo` missing | `pip install pymongo` |
| MCP tools missing | Restart IDE; verify `npx` / Node version |
| Empty rankings | Collection may have no `scrip` / history for symbols |
