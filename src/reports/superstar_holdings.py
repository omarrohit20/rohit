"""Celebrity / superstar investor holdings (Nsedata.superstar_holdings)."""
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

import news_preview
import rbase as rb

COLL = "superstar_holdings"
RUNS = "superstar_runs"
JOB_HINT = (
    "No rows yet. Run `python indian-trading-skills/skills/superstar-holdings/scripts/"
    "run_superstar_holdings.py` (or `superstar_holdings.bat`)."
)
ACTIVE = ["NEW", "NEW_DEAL", "INCREASED", "UNCHANGED", "DECREASED", "HOLDING"]
EXITED = "EXITED_OR_BELOW_1PCT"
ICON = {
    "NEW": "🟢 NEW",
    "NEW_DEAL": "🟢 NEW (deal)",
    "INCREASED": "🟢 INCREASED",
    "UNCHANGED": "⚪ UNCHANGED",
    "HOLDING": "⚪ HOLDING",
    "DECREASED": "🔴 DECREASED",
    EXITED: "🔴 EXITED / <1%",
}
CONV_RANK = {"High": 0, "Med": 1, "Low": 2}
ORDER = [
    "scrip", "company", "investor_name", "status_label", "conviction", "latest_pct", "prev_pct",
    "change_pct", "max_pct", "drop_from_max_pct", "investors_holding_count", "why", "deal_signal",
    "close", "price_sentiment", "news_sentiment", "marketcap", "marketcap_bucket", "industry",
    "as_of_quarter", "first_seen_quarter", "max_quarter", "consecutive_increases", "changed_at",
]
CONFIG = {
    "investor_name": st.column_config.TextColumn("Investor"),
    "status_label": st.column_config.TextColumn("Status"),
    "latest_pct": st.column_config.NumberColumn("Now %", format="%.2f"),
    "prev_pct": st.column_config.NumberColumn("Prev %", format="%.2f"),
    "change_pct": st.column_config.NumberColumn("Chg %", format="%+.2f"),
    "max_pct": st.column_config.NumberColumn("Max %", format="%.2f"),
    "drop_from_max_pct": st.column_config.NumberColumn("Below max %", format="%.2f"),
    "investors_holding_count": st.column_config.NumberColumn("# celebs"),
    "why": st.column_config.TextColumn("Why", width="large"),
    "deal_signal": st.column_config.TextColumn("Bulk/block deal", width="medium"),
    "marketcap": st.column_config.NumberColumn("Mcap cr", format="%.0f"),
    "consecutive_increases": st.column_config.NumberColumn("Qtrs up"),
    "changed_at": st.column_config.DatetimeColumn("Changed", format="DD MMM YY"),
}


@st.cache_data(ttl=60)
def _load() -> pd.DataFrame:
    docs = list(rb.dbnse[COLL].find({}, {"_id": 0, "screener_cons": 0, "matched_holder_names": 0}))
    return pd.DataFrame(docs)


@st.cache_data(ttl=60)
def _last_runs():
    runs = list(rb.dbnse[RUNS].find({"finished_at": {"$exists": True}}, {"_id": 0}).sort("started_at", -1).limit(1))
    return runs[0] if runs else None


def _sort(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    rank = frame.get("conviction", pd.Series(index=frame.index, dtype=object)).map(CONV_RANK).fillna(3)
    chg = pd.to_numeric(frame.get("change_pct"), errors="coerce").abs().fillna(0)
    return frame.assign(_r=rank, _c=-chg).sort_values(["_r", "_c", "scrip"]).drop(columns=["_r", "_c"])


def _show(frame: pd.DataFrame, widget: str) -> None:
    if frame.empty:
        st.info("No rows match these filters.")
        return
    frame = _sort(frame)
    order = [c for c in ORDER if c in frame.columns]
    height = max(160, min(640, 56 + 36 * len(frame)))
    st.caption(f"{len(frame)} rows")
    news_preview.display_dataframe(
        st, frame.reset_index(drop=True), height=height, column_order=order,
        column_config=CONFIG, use_container_width=True, news_widget_id=widget,
    )


def _filters(df: pd.DataFrame) -> pd.DataFrame:
    c1, c2, c3, c4 = st.columns(4)
    investors = sorted(df["investor_name"].dropna().unique())
    pick_inv = c1.multiselect("Investor", investors, key="ss_investor")
    pick_status = c2.multiselect("Status", list(ICON), format_func=ICON.get, key="ss_status")
    pick_conv = c3.multiselect("Conviction", ["High", "Med", "Low"], key="ss_conv")
    pick_cap = c4.multiselect("Market cap", ["smallcap", "midcap", "largecap", "unknown"], key="ss_cap")
    c5, c6, c7, c8 = st.columns(4)
    min_pct = c5.number_input("Min holding %", 0.0, 100.0, 0.0, 0.5, key="ss_minpct")
    min_celebs = c6.number_input("Held by at least N celebrities", 1, 20, 1, key="ss_minceleb")
    days = c7.number_input("Changed in last N days (0 = any)", 0, 3650, 0, key="ss_days")
    search = c8.text_input("Search scrip / company / why", key="ss_search")

    out = df
    if pick_inv:
        out = out[out["investor_name"].isin(pick_inv)]
    if pick_status:
        out = out[out["status"].isin(pick_status)]
    if pick_conv and "conviction" in out:
        out = out[out["conviction"].isin(pick_conv)]
    if pick_cap and "marketcap_bucket" in out:
        out = out[out["marketcap_bucket"].isin(pick_cap)]
    if min_pct:
        out = out[pd.to_numeric(out["latest_pct"], errors="coerce").fillna(0) >= min_pct]
    if min_celebs > 1:
        out = out[pd.to_numeric(out["investors_holding_count"], errors="coerce").fillna(0) >= min_celebs]
    if days and "changed_at" in out:
        since = datetime.now() - timedelta(days=int(days))
        out = out[pd.to_datetime(out["changed_at"], errors="coerce") >= since]
    text = (search or "").strip().lower()
    if text:
        blob = out[[c for c in ("scrip", "company", "why") if c in out]].fillna("").astype(str).agg(" ".join, axis=1)
        out = out[blob.str.lower().str.contains(text, regex=False)]
    return out


def main():
    try:
        st.set_page_config(layout="wide", page_title="Superstar holdings", initial_sidebar_state="expanded")
    except Exception:
        pass
    rb._ensure_chart_preview_sidebar()
    rb.compact_page_top()
    st.title("Superstar investor holdings")

    try:
        df = _load()
    except Exception as exc:
        st.error(f"Could not read `{COLL}`: {exc}")
        return
    if df.empty:
        st.info(JOB_HINT)
        return
    run = _last_runs()
    run_id = run.get("run_id") if run else None
    if run:
        st.caption(
            f"Last run {run['finished_at']:%d %b %Y %H:%M} · checked {run.get('checked', 0)} stocks · "
            f"{run.get('symbols_changed', 0)} changed. Source: NSE shareholding (named holders > 1%) "
            "and NSE bulk/block deals."
        )

    df["status_label"] = df["status"].map(ICON).fillna(df["status"])
    use_global = st.checkbox(
        "Apply left sidebar filters (index, industries, market cap, news sentiment, data filtering)",
        value=True,
        key="ss_global",
    )
    if use_global:
        total = len(df)
        df = rb.filter_df_by_scrip_index(df)
        hidden = total - len(df)
        if hidden:
            st.caption(f"Sidebar filters hide {hidden} of {total} rows. Untick the box above to see all.")
    df = _filters(df)

    active = df[df["status"].isin(ACTIVE)]
    new_run = df[df.get("changed_run_id") == run_id] if run_id and "changed_run_id" in df else df.iloc[0:0]
    below = active[active["below_max"].fillna(False).astype(bool)] if "below_max" in active else active.iloc[0:0]
    m = st.columns(6)
    m[0].metric("Holdings", len(active))
    m[1].metric("Stocks", active["scrip"].nunique())
    m[2].metric("Changed last run", len(new_run))
    m[3].metric("Increased / new", int(active["status"].isin(["NEW", "NEW_DEAL", "INCREASED"]).sum()))
    m[4].metric("Below max", len(below))
    m[5].metric("Exited / <1%", int((df["status"] == EXITED).sum()))

    tabs = st.tabs([
        "All holdings", "Changed last run", "New buys", "Increased", "Decreased from max",
        "Exited / <1%", "By investor", "Multi-celebrity stocks",
    ])
    with tabs[0]:
        _show(active, "ss_all")
    with tabs[1]:
        _show(new_run, "ss_run")
    with tabs[2]:
        _show(df[df["status"].isin(["NEW", "NEW_DEAL"])], "ss_new")
    with tabs[3]:
        _show(df[df["status"] == "INCREASED"], "ss_inc")
    with tabs[4]:
        _show(below, "ss_below")
    with tabs[5]:
        _show(df[df["status"] == EXITED], "ss_exit")
    with tabs[6]:
        if active.empty:
            st.info("No holdings match these filters.")
        else:
            summary = active.groupby("investor_name").agg(
                stocks=("scrip", "nunique"),
                new=("status", lambda s: int(s.isin(["NEW", "NEW_DEAL"]).sum())),
                increased=("status", lambda s: int((s == "INCREASED").sum())),
                decreased=("status", lambda s: int((s == "DECREASED").sum())),
                high_conviction=("conviction", lambda s: int((s == "High").sum())),
            ).sort_values("stocks", ascending=False)
            st.dataframe(summary, use_container_width=True)
            who = st.selectbox("Investor portfolio", list(summary.index), key="ss_who")
            _show(active[active["investor_name"] == who], f"ss_inv_{who}")
    with tabs[7]:
        multi = active[pd.to_numeric(active["investors_holding_count"], errors="coerce").fillna(0) >= 2]
        if multi.empty:
            st.info("No stock is held by two or more tracked investors (with current filters).")
        else:
            pivot = multi.pivot_table(
                index=["scrip", "company"], columns="investor_name", values="latest_pct", aggfunc="max"
            )
            pivot.insert(0, "# celebs", pivot.notna().sum(axis=1))
            st.dataframe(pivot.sort_values("# celebs", ascending=False), use_container_width=True)

    st.caption("Educational only, not SEBI advice.")


if __name__ == "__main__":
    main()
