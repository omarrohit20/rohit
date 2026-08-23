import json
from pathlib import Path

files = {
    "morning-volume-breakout-buy": "_q_mvb21.json",
    "Breakout-Beey-2": "_q_bb221.json",
    "cash-buuy": "_q_cash21.json",
}

merged = []
for name, f in files.items():
    raw = Path(f).read_text(encoding="utf-8-sig")
    # strip any stderr prefix lines before JSON
    start = raw.find("{")
    d = json.loads(raw[start:])
    meta = d.get("meta", {})
    print("=" * 80)
    print(f"TABLE: {name} scanned={meta.get('scanned')} analyzed={meta.get('analyzed')} at={meta.get('generated_at')}")
    print("scan_columns:", meta.get("scan_columns") or d.get("scan_columns"))
    rows = d.get("priority_table") or []
    print(f"priority count={len(rows)}")
    for i, r in enumerate(rows, 1):
        sym = r.get("symbol") or r.get("scrip")
        why = (r.get("why") or r.get("why_hint") or "")[:180]
        print(
            f"{i:2d} {sym} side={r.get('trade_side')} sent={r.get('sentiment')} "
            f"conv={r.get('conviction')} prob={r.get('probability_score')} "
            f"ld={r.get('last_day_pct')} td={r.get('today_pct')} "
            f"orange={r.get('row_highlight_orange')} green={r.get('row_highlight_green')} "
            f"mlB={r.get('ml_buy')} mlS={r.get('ml_sell')}"
        )
        print(f"    why: {why}")
        merged.append({**r, "table": name, "symbol": sym})

    # weak candidates
    scored = []
    for c in d.get("candidates") or []:
        intr = c.get("intraday") or {}
        sc = intr.get("score") if isinstance(intr, dict) else c.get("score")
        scored.append((sc if sc is not None else -99, c.get("scrip"), c.get("last_day_pct"), c.get("today_pct"), (c.get("why_hint") or "")[:90]))
    scored.sort(key=lambda x: x[0])
    print("weakest:")
    for row in scored[:4]:
        print(" ", row)
    # rankings entry
    for r in (d.get("rankings") or {}).get("intraday") or []:
        print(" rank", r.get("scrip") or r.get("symbol"), "entry", r.get("entry"), "prob", r.get("probability_score"))

print("\nMERGED by prob:")
merged.sort(key=lambda x: (x.get("probability_score") or 0), reverse=True)
for i, r in enumerate(merged[:15], 1):
    print(i, r["table"], r["symbol"], r.get("probability_score"), r.get("last_day_pct"), r.get("today_pct"), r.get("row_highlight_orange"), r.get("row_highlight_green"))

Path("_merged21.json").write_text(json.dumps(merged, indent=2, default=str), encoding="utf-8")
