"""Long, medium, and short investment ideas stored in Nsedata."""
import pandas as pd
import streamlit as st

import rbase as rb
import news_preview

SECTIONS = (
    (
        "investment-long-term",
        "Long-term",
        "Target upside above 50% only. Rows whose insertion date is older than 3 months are removed on the next job run.",
    ),
    (
        "investment-medium-term",
        "Medium-term",
        "Target upside above 30% only, excluding long-term names. Rows whose insertion date is older than 1 month are removed on the next job run.",
    ),
    (
        "investment-short-term",
        "Short-term",
        "Target upside above 20% only, excluding long- and medium-term names. Rows whose insertion date is older than 10 days are removed on the next job run.",
    ),
)

PREFERRED = [
    "scrip",
    "symbol",
    "company",
    "idea_type",
    "buy_price",
    "target_price",
    "target_pct",
    "target_days",
    "target_date",
    "target_reason",
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
    "news_sentiment",
    "news_conviction",
    "news_headline",
    "news_event",
    "news_impact_score",
    "news_date",
    "order_book_years",
    "screener_pros",
    "screener_cons",
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
    _fill_target(frame)
    if "insertion_date" in frame.columns:
        frame["_sort"] = pd.to_datetime(frame["insertion_date"], errors="coerce")
        frame = frame.sort_values("_sort", ascending=False, na_position="last").drop(columns=["_sort"])
    return frame.reset_index(drop=True)


def _fill_target(frame: pd.DataFrame) -> None:
    """Fill target % and days for rows saved before the job stored them."""
    def stored(column: str) -> pd.Series:
        if column in frame.columns:
            return pd.to_numeric(frame[column], errors="coerce")
        return pd.Series(float("nan"), index=frame.index)

    if {"buy_price", "target_price"} <= set(frame.columns):
        buy = pd.to_numeric(frame["buy_price"], errors="coerce")
        target = pd.to_numeric(frame["target_price"], errors="coerce")
        pct = ((target - buy) / buy.where(buy > 0) * 100).round(2)
        frame["target_pct"] = stored("target_pct").fillna(pct)
    if {"target_date", "insertion_date"} <= set(frame.columns):
        due = pd.to_datetime(frame["target_date"], errors="coerce")
        start = pd.to_datetime(frame["insertion_date"], errors="coerce")
        frame["target_days"] = stored("target_days").fillna((due - start).dt.days)


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
        "target_pct": st.column_config.NumberColumn("Target %", format="%.1f%%"),
        "target_days": st.column_config.NumberColumn("Days", format="%d"),
        "target_date": st.column_config.TextColumn("Target by"),
        "target_reason": st.column_config.TextColumn("Target reason", width="medium"),
        "stoploss": st.column_config.NumberColumn("Stop", format="%.2f"),
        "probability_score": st.column_config.NumberColumn("Prob%"),
        "why": st.column_config.TextColumn("Why", width="large"),
        "news_sentiment": st.column_config.TextColumn("News"),
        "news_conviction": st.column_config.TextColumn("News conviction"),
        "news_headline": st.column_config.TextColumn("Headline", width="large"),
        "news_event": st.column_config.TextColumn("Event"),
        "news_impact_score": st.column_config.NumberColumn("Impact"),
        "news_date": st.column_config.TextColumn("News date"),
        "order_book_years": st.column_config.NumberColumn("Order book yrs", format="%.1f"),
        "screener_pros": st.column_config.ListColumn("Pros"),
        "screener_cons": st.column_config.ListColumn("Cons"),
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
    st.caption("High or Med conviction, Bullish only (celebrity buys: any conviction and target). Click a row index to open the chart when a scrip is present.")

    type_options = ["All", "breakout", "orderbook", "celebrity"]
    picked, query = st.columns([1, 2])
    with picked:
        idea_type = st.selectbox(
            "Idea type",
            type_options,
            format_func=lambda value: {"orderbook": "Order book", "breakout": "Breakout", "celebrity": "Celebrity"}.get(value, value),
            key="idea_type",
        )
    with query:
        search = st.text_input("Symbol or investor", key="search")

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
        shown = _filter(frame, idea_type, search)
        st.caption(f"{len(shown)} rows")
        if shown.empty:
            st.info("No rows match this filter.")
            continue
        _show(shown, f"{collection}:{idea_type}:{search}")

    st.caption("Educational only, not SEBI advice.")


if __name__ == "__main__":
    main()
