"""Long, medium, and short investment ideas stored in Nsedata."""
import pandas as pd
import streamlit as st

import rbase as rb
import news_preview

SECTIONS = (
    (
        "investment-long-term",
        "Long-term",
        "Kept. This collection is not purged.",
    ),
    (
        "investment-medium-term",
        "Medium-term",
        "Rows whose insertion date is older than 3 months are removed on the next job run.",
    ),
    (
        "investment-short-term",
        "Short-term",
        "Rows whose insertion date is older than 20 days are removed on the next job run.",
    ),
)

PREFERRED = [
    "scrip",
    "symbol",
    "company",
    "idea_type",
    "buy_price",
    "target_price",
    "stoploss",
    "conviction",
    "sentiment",
    "probability_score",
    "investor_name",
    "holding_pct",
    "holding_change_pct",
    "top_holder_name",
    "top_holder_pct",
    "top_public_holder_name",
    "top_public_holder_pct",
    "marketcap_bucket",
    "order_book_cr",
    "marketcap_cr",
    "sales_cr",
    "hit_count",
    "why",
    "source",
    "as_of_date",
    "insertion_date",
    "horizon_label",
]

JOB_HINT = (
    "No rows yet. Run "
    "`python indian-trading-skills/skills/investment-ideas/scripts/run_investment_ideas.py`."
)


def _load(collection: str) -> pd.DataFrame:
    docs = list(rb.dbnse[collection].find({}, {"_id": 0}))
    if not docs:
        return pd.DataFrame()
    frame = pd.DataFrame(docs)
    if "symbol" in frame.columns:
        frame["scrip"] = frame["symbol"]
    if "insertion_date" in frame.columns:
        frame["_sort"] = pd.to_datetime(frame["insertion_date"], errors="coerce")
        frame = frame.sort_values("_sort", ascending=False, na_position="last").drop(columns=["_sort"])
    return frame.reset_index(drop=True)


def _filter(frame: pd.DataFrame, idea_type: str, query: str) -> pd.DataFrame:
    out = frame
    if idea_type and idea_type != "All" and "idea_type" in out.columns:
        out = out[out["idea_type"].astype(str) == idea_type]
    text = (query or "").strip().lower()
    if text:
        haystacks = []
        for column in ("scrip", "symbol", "company", "investor_name", "top_holder_name", "why"):
            if column in out.columns:
                haystacks.append(out[column].fillna("").astype(str).str.lower())
        if haystacks:
            mask = haystacks[0].str.contains(text, regex=False)
            for series in haystacks[1:]:
                mask = mask | series.str.contains(text, regex=False)
            out = out[mask]
    return out.reset_index(drop=True)


def _show(frame: pd.DataFrame, widget_name: str) -> None:
    columns = [column for column in PREFERRED if column in frame.columns]
    extra = [column for column in frame.columns if column not in columns and column != "dedupe_key"]
    order = columns + extra
    height = max(180, min(640, 56 + 36 * max(len(frame), 1)))
    config = {
        "buy_price": st.column_config.NumberColumn("Buy", format="%.2f"),
        "target_price": st.column_config.NumberColumn("Target", format="%.2f"),
        "stoploss": st.column_config.NumberColumn("Stop", format="%.2f"),
        "probability_score": st.column_config.NumberColumn("Prob%"),
        "why": st.column_config.TextColumn("Why", width="large"),
        "holding_pct": st.column_config.NumberColumn("Holding %", format="%.2f"),
        "order_book_cr": st.column_config.NumberColumn("Order book cr", format="%.1f"),
        "marketcap_cr": st.column_config.NumberColumn("Mcap cr", format="%.1f"),
        "sales_cr": st.column_config.NumberColumn("Sales cr", format="%.1f"),
    }
    news_preview.display_dataframe(
        st,
        frame,
        height=height,
        column_order=order,
        column_config=config,
        use_container_width=True,
        news_widget_id=widget_name,
    )


def main():
    try:
        st.set_page_config(layout="wide", page_title="Investment ideas", initial_sidebar_state="expanded")
    except Exception:
        pass
    rb._ensure_chart_preview_sidebar()
    st.title("Investment ideas")
    st.caption("High conviction and Bullish only. Click a row index to open the chart when a scrip is present.")

    for collection, title, note in SECTIONS:
        st.subheader(title)
        st.caption(note)
        try:
            frame = _load(collection)
        except Exception as exc:
            st.error(f"Could not read `{collection}`: {exc}")
            continue
        if frame.empty:
            st.info(JOB_HINT)
            continue
        type_options = ["All", "breakout", "orderbook", "celebrity"]
        picked, query = st.columns([1, 2])
        with picked:
            idea_type = st.selectbox(
                "Idea type",
                type_options,
                format_func=lambda value: {"orderbook": "Order book", "breakout": "Breakout", "celebrity": "Celebrity"}.get(value, value),
                key=f"idea_type_{collection}",
            )
        with query:
            search = st.text_input("Symbol or investor", key=f"search_{collection}")
        shown = _filter(frame, idea_type, search)
        st.caption(f"{len(shown)} rows")
        if shown.empty:
            st.info("No rows match this filter.")
            continue
        _show(shown, f"{collection}:{idea_type}:{search}")

    st.caption("Educational only, not SEBI advice.")


if __name__ == "__main__":
    main()
