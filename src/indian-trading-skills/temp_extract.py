import subprocess, json, os
collections = ["morning-volume-breakout-buy", "Breakout-Beey-2", "cash-buuy"]
cwd = r"C:\git\rohit\src\indian-trading-skills"
out = []
for coll in collections:
    cmd = ["python", "skills/nsedata-trade-advisor/scripts/query_suggestions.py", "--db", "chartlink", "--collection", coll, "--limit", "12", "--horizons", "intraday", "--top", "8"]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    print("===", coll, "===")
    if res.returncode != 0:
        print(res.stderr)
        continue
    report = json.loads(res.stdout)
    for rank in report.get("rankings", {}).get("intraday", []):
        out.append({
            "table": coll,
            "symbol": rank.get("symbol"),
            "sentiment": rank.get("sentiment"),
            "conviction": rank.get("conviction"),
            "prob": rank.get("probability_score"),
            "last_day_pct": rank.get("last_day_pct"),
            "today_pct": rank.get("today_pct"),
            "why": rank.get("why"),
            "bias": rank.get("bias"),
        })
print(json.dumps(out, indent=2))
