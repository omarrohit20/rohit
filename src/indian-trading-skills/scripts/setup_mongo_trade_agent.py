#!/usr/bin/env python3
"""Install Mongo Trade Agent wiring for Cursor / Claude / Copilot.

Usage:
  python scripts/setup_mongo_trade_agent.py
  python scripts/setup_mongo_trade_agent.py --personal-skill
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_SRC = ROOT / "skills" / "mongo-trade-agent"
MCP_EXAMPLE = ROOT / "skills" / "mongodb-local-mcp" / "assets" / "cursor-mcp-config.example.json"


def ping_mongo(uri: str) -> bool:
    try:
        from pymongo import MongoClient
    except ImportError:
        print("pymongo not installed. Run: pip install pymongo", file=sys.stderr)
        return False
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=4000)
        client.admin.command("ping")
        dbs = client.list_database_names()
        print(f"Mongo OK at {uri}")
        for name in ("Nsedata", "chartlink"):
            mark = "yes" if name in dbs else "MISSING"
            print(f"  - {name}: {mark}")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"Mongo ping failed: {exc}", file=sys.stderr)
        return False


def ensure_cursor_skill() -> None:
    dest = ROOT / ".cursor" / "skills" / "mongo-trade-agent"
    dest.mkdir(parents=True, exist_ok=True)
    target = dest / "SKILL.md"
    if not target.exists():
        shutil.copy2(SKILL_SRC / "SKILL.md", target)
        print(f"Wrote {target}")
    else:
        print(f"Exists {target}")


def install_personal_skill() -> None:
    home = Path.home()
    dest = home / ".cursor" / "skills" / "mongo-trade-agent"
    dest.mkdir(parents=True, exist_ok=True)
    for item in SKILL_SRC.rglob("*"):
        if item.is_file():
            rel = item.relative_to(SKILL_SRC)
            out = dest / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, out)
    # Helper pointer for personal skill (scripts stay in repo)
    pointer = dest / "REPO_PATH.txt"
    pointer.write_text(str(ROOT), encoding="utf-8")
    print(f"Installed personal skill -> {dest}")


def ensure_mcp() -> None:
    mcp_path = ROOT / ".cursor" / "mcp.json"
    if mcp_path.exists():
        print(f"Exists {mcp_path}")
        return
    mcp_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(MCP_EXAMPLE, mcp_path)
    print(f"Wrote {mcp_path}")


def print_next_steps() -> None:
    print(
        """
Next steps
----------
Cursor:  restart Cursor -> Settings -> MCP -> confirm MongoDB server
Claude:  merge skills/mongodb-local-mcp/assets/claude-desktop-mcp-config.example.json
         into claude_desktop_config.json, then restart Claude Desktop
Copilot: AGENTS.md + .github/copilot-instructions.md are ready

Smoke test:
  python skills/nsedata-trade-advisor/scripts/query_suggestions.py \\
    --db Nsedata --collection highBuy --limit 5 --horizons all --top 3
"""
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Setup Mongo Trade Agent")
    parser.add_argument(
        "--uri",
        default="mongodb://localhost:27017",
        help="MongoDB URI",
    )
    parser.add_argument(
        "--personal-skill",
        action="store_true",
        help="Also copy skill to ~/.cursor/skills/mongo-trade-agent",
    )
    parser.add_argument(
        "--skip-mongo-ping",
        action="store_true",
        help="Skip Mongo connectivity check",
    )
    args = parser.parse_args()

    print(f"Repo: {ROOT}")
    if not SKILL_SRC.exists():
        print(f"Missing skill at {SKILL_SRC}", file=sys.stderr)
        return 1

    ensure_cursor_skill()
    ensure_mcp()
    if args.personal_skill:
        install_personal_skill()

    ok = True
    if not args.skip_mongo_ping:
        ok = ping_mongo(args.uri)

    # Confirm agent files
    for path in (
        ROOT / "AGENTS.md",
        ROOT / "CLAUDE.md",
        ROOT / ".github" / "copilot-instructions.md",
        ROOT / "skills" / "nsedata-trade-advisor" / "scripts" / "query_suggestions.py",
    ):
        print(("OK  " if path.exists() else "MISS") + f" {path.relative_to(ROOT)}")

    print_next_steps()
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
