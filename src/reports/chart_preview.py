"""Clickable row index (0, 1, 2, …) opens the full chart page in a new tab.

Scrip values are not changed, so existing Styler colours stay on the data columns.
"""
import pandas as pd
import streamlit as st
from urllib.parse import quote

PROVIDERS = [
    "TradingView",
    "Chartink",
    "Moneycontrol",
    "Groww",
    "Trendlyne",
    "Custom",
]

PROVIDER_TEMPLATES = {
    "TradingView": "https://www.tradingview.com/chart/?symbol=NSE:{scrip}&interval={interval}",
    "Chartink": "https://chartink.com/stocks/{scrip_lower}.html",
    "Moneycontrol": "https://www.moneycontrol.com/india/stockpricequote/{scrip_lower}",
    "Groww": "https://groww.in/stocks/{scrip_lower}",
    "Trendlyne": "https://trendlyne.com/equity/{scrip}/",
}

_SESSION_ENABLED = "chart_preview_enabled"
_SESSION_PROVIDER = "chart_preview_provider"
_SESSION_CUSTOM = "chart_preview_custom_url"

# Internal col; header is blank so it looks like the default index
_INDEX_COL = "_idx"


def is_enabled():
    return bool(st.session_state.get(_SESSION_ENABLED, True))


def current_template():
    provider = st.session_state.get(_SESSION_PROVIDER, "TradingView")
    if provider == "Custom":
        tpl = (st.session_state.get(_SESSION_CUSTOM) or "").strip()
        return tpl or PROVIDER_TEMPLATES["TradingView"]
    return PROVIDER_TEMPLATES.get(provider, PROVIDER_TEMPLATES["TradingView"])


def render_sidebar_controls():
    st.sidebar.markdown("---")
    st.sidebar.subheader("Chart page")
    st.sidebar.checkbox(
        "Open chart from row index",
        value=st.session_state.get(_SESSION_ENABLED, True),
        key=_SESSION_ENABLED,
        help="Click 0, 1, 2, … to open the full chart page in a new tab.",
    )
    if _SESSION_PROVIDER not in st.session_state:
        st.session_state[_SESSION_PROVIDER] = "TradingView"
    st.sidebar.selectbox(
        "Chart provider",
        PROVIDERS,
        key=_SESSION_PROVIDER,
        disabled=not st.session_state.get(_SESSION_ENABLED, False),
    )
    if st.session_state.get(_SESSION_PROVIDER) == "Custom":
        st.sidebar.text_input(
            "Custom page URL",
            value=st.session_state.get(
                _SESSION_CUSTOM,
                PROVIDER_TEMPLATES["TradingView"],
            ),
            key=_SESSION_CUSTOM,
            help="Use {scrip}, {scrip_lower}, and {interval} placeholders.",
        )
    st.sidebar.caption("Click the row number. TradingView uses 5-minute.")


def _scrip_full_page_url(value):
    if value is None:
        return None
    try:
        if isinstance(value, float) and pd.isna(value):
            return None
    except Exception:
        pass
    scrip = str(value).strip()
    if not scrip or scrip.lower() == "nan":
        return None
    url = current_template()
    return (
        url.replace("{scrip_lower}", quote(scrip.lower(), safe=""))
        .replace("{scrip}", quote(scrip, safe=""))
        .replace("{interval}", "5")
    )


def _underlying_df(data):
    if data is None or isinstance(data, str):
        return None
    if hasattr(data, "data") and hasattr(data, "to_html"):
        return data.data
    return data


def _index_urls(df):
    urls = []
    scrips = df["scrip"].tolist() if "scrip" in df.columns else [None] * len(df)
    for i, scrip in enumerate(scrips):
        page = _scrip_full_page_url(scrip)
        if not page:
            urls.append(None)
            continue
        joiner = "&" if "?" in page else "?"
        urls.append(f"{page}{joiner}_i={i}")
    return urls


def _with_clickable_index(data):
    df = _underlying_df(data)
    if df is None or len(df) == 0:
        return data
    urls = _index_urls(df)

    if hasattr(data, "to_html") and hasattr(data, "data"):
        view = data.copy() if hasattr(data, "copy") else data
        view.data = view.data.copy()
        if _INDEX_COL in view.data.columns:
            view.data = view.data.drop(columns=[_INDEX_COL])
        view.data.insert(0, _INDEX_COL, urls)
        # Styler keeps a snapshot of columns from init; Streamlit re-runs
        # highlighters against data.columns and then looks up this snapshot.
        view.columns = view.data.columns
        try:
            view.index = view.data.index
        except Exception:
            pass
        return view

    out = df.copy()
    if _INDEX_COL in out.columns:
        out = out.drop(columns=[_INDEX_COL])
    out.insert(0, _INDEX_COL, urls)
    return out


def display_dataframe(
    st_mod,
    data,
    height=110,
    column_order=None,
    column_config=None,
    use_container_width=True,
):
    kwargs = {"height": height, "use_container_width": use_container_width}
    order = list(column_order) if column_order is not None else None
    conf = dict(column_config) if column_config else {}
    view = data

    if is_enabled() and data is not None and not isinstance(data, str):
        try:
            empty = bool(getattr(data, "empty", False))
        except Exception:
            empty = False
        if not empty:
            view = _with_clickable_index(data)
            kwargs["hide_index"] = True
            try:
                conf[_INDEX_COL] = st.column_config.LinkColumn(
                    " ",
                    help="Open full chart page in a new tab",
                    display_text=r"_i=(\d+)",
                    width="small",
                )
            except TypeError:
                try:
                    conf[_INDEX_COL] = st.column_config.LinkColumn(
                        " ",
                        display_text=r"_i=(\d+)",
                    )
                except TypeError:
                    conf[_INDEX_COL] = st.column_config.LinkColumn(" ")
            if order is not None:
                order = [c for c in order if c != _INDEX_COL]
                order = [_INDEX_COL] + order

    if order is not None:
        kwargs["column_order"] = order
    if conf:
        kwargs["column_config"] = conf
    elif column_config is not None:
        kwargs["column_config"] = column_config

    st_mod.dataframe(view, **kwargs)
