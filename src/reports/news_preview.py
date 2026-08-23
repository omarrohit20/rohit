"""News preview via an ℹ strip to the LEFT of the table (not inside it).

The dataframe is unchanged — same chart_preview / Styler path as before.
"""
from __future__ import annotations

import json
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

_SESSION_ENABLED = "news_preview_enabled"
_ROW_H = 35
_HEADER_H = 36


def is_enabled():
    return bool(st.session_state.get(_SESSION_ENABLED, False))


def render_sidebar_controls():
    st.sidebar.markdown("---")
    st.sidebar.subheader("News & sentiment")
    st.sidebar.checkbox(
        "Show news info icons",
        value=st.session_state.get(_SESSION_ENABLED, False),
        key=_SESSION_ENABLED,
        help="ℹ sits to the left of the table. Hover for conviction, sentiment, and news. Leave to close; stay on the preview to keep it open.",
    )
    st.sidebar.caption("From skill scan-news-conviction → Nsedata.scrip_news")


def _scrip_key(value):
    if value is None:
        return ""
    try:
        if isinstance(value, float) and pd.isna(value):
            return ""
    except Exception:
        pass
    s = str(value).strip().upper()
    return "" if (not s or s in {"NAN", "NONE"}) else s


def _underlying_df(data):
    if data is None or isinstance(data, str):
        return None
    if hasattr(data, "data") and hasattr(data, "to_html"):
        return data.data
    return data


def _scrip_list(data):
    df = _underlying_df(data)
    if df is None or "scrip" not in getattr(df, "columns", []):
        return []
    return [_scrip_key(v) for v in df["scrip"].tolist()]


@st.cache_data(ttl=40)
def load_news_map():
    try:
        from pymongo import MongoClient
    except Exception:
        return {}
    try:
        client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2500)
        docs = list(client.Nsedata.scrip_news.find({}, {"_id": 0}))
        client.close()
    except Exception:
        return {}
    out = {}
    for doc in docs:
        key = _scrip_key(doc.get("scrip"))
        if key:
            out[key] = _public_doc(doc)
    return out


def _fmt_dt(value):
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    return str(value or "")


def _trim_articles(items, n=10):
    out = []
    for it in (items or [])[:n]:
        out.append(
            {
                "title": it.get("title") or "",
                "link": it.get("link") or "",
                "sentiment": it.get("sentiment") or "",
                "source": it.get("source") or "",
                "impact_score": it.get("impact_score"),
            }
        )
    return out


def _public_doc(doc: dict) -> dict:
    return {
        "scrip": doc.get("scrip"),
        "industry": doc.get("industry") or "",
        "overall_sentiment": doc.get("overall_sentiment") or "Neutral",
        "conviction": doc.get("conviction") or "Low",
        "scan_tables": doc.get("scan_tables") or [],
        "insertion_date": _fmt_dt(doc.get("insertion_date")),
        "updated_at": _fmt_dt(doc.get("updated_at")),
        "news": _trim_articles(doc.get("news"), 10),
        "sectoral_news": _trim_articles(doc.get("sectoral_news"), 6),
        "analyst_calls": _trim_articles(doc.get("analyst_calls"), 6),
    }


def _icon_strip_page(scrips, news_map, height):
    icons = []
    for scrip in scrips:
        esc = (
            str(scrip)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace('"', "&quot;")
        )
        icons.append(f'<div class="nws-ico" data-scrip="{esc}" title="{esc} news">ℹ</div>')
    icons_html = "".join(icons)
    payload = json.dumps({"news": news_map})
    h = int(height)
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  html,body{{margin:0;padding:0;background:transparent;overflow:hidden;}}
  .pad{{height:{_HEADER_H}px;}}
  .list{{height:{max(h - _HEADER_H, 40)}px;overflow:hidden;}}
  .nws-ico{{height:{_ROW_H}px;line-height:{_ROW_H}px;text-align:center;cursor:pointer;
    font-size:16px;color:#1d4ed8;user-select:none;}}
  .nws-ico:hover{{background:#dbeafe;border-radius:4px;}}
</style></head>
<body>
<div class="pad"></div>
<div class="list">{icons_html}</div>
<script>
(function() {{
  const cfg = {payload};
  const P = window.parent.document;
  let pop = P.getElementById('scrip-news-pop');
  if (!pop) {{
    pop = P.createElement('div');
    pop.id = 'scrip-news-pop';
    pop.style.cssText = 'display:none;position:fixed;z-index:2147483646;width:460px;max-height:74vh;overflow:auto;'
      + 'background:#0f172a;color:#e2e8f0;border-radius:8px;box-shadow:0 12px 40px rgba(0,0,0,.45);'
      + 'padding:12px 14px;font:13px/1.4 sans-serif;';
    P.body.appendChild(pop);
  }}
  function esc(s) {{
    return String(s||'').replace(/[&<>"]/g, function(c) {{
      return {{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c];
    }});
  }}
  function listHtml(items, emptyText) {{
    if (!items || !items.length) return '<p style="color:#94a3b8">' + emptyText + '</p>';
    return '<ul style="margin:4px 0 12px;padding-left:18px">' + items.map(function(it) {{
      const t = esc(it.title);
      const href = it.link ? '<a href="' + esc(it.link) + '" target="_blank" rel="noopener" style="color:#93c5fd">' + t + '</a>' : t;
      const imp = it.impact_score != null ? ' · impact ' + it.impact_score : '';
      return '<li style="margin:4px 0">' + href + ' <span style="color:#94a3b8">(' + esc(it.sentiment) + ' · ' + esc(it.source) + imp + ')</span></li>';
    }}).join('') + '</ul>';
  }}
  function render(scrip) {{
    const d = cfg.news[scrip];
    if (!d) {{
      pop.innerHTML = '<div style="font-size:15px;font-weight:700;color:#fff">' + esc(scrip) + '</div>'
        + '<p style="color:#94a3b8">No saved news. Run skill scan-news-conviction.</p>';
      return;
    }}
    pop.innerHTML =
      '<div style="font-size:15px;font-weight:700;color:#fff">' + esc(d.scrip) + '</div>'
      + '<div style="margin:8px 0">'
      + '<span style="padding:2px 8px;border-radius:10px;background:#1e3a5f;margin-right:6px">Sentiment: ' + esc(d.overall_sentiment) + '</span>'
      + '<span style="padding:2px 8px;border-radius:10px;background:#3b2f1a">Conviction: ' + esc(d.conviction) + '</span></div>'
      + '<div style="color:#94a3b8;margin-bottom:8px">' + esc(d.industry)
      + (d.scan_tables && d.scan_tables.length ? ' · ' + esc(d.scan_tables.join(', ')) : '')
      + '<br>Inserted ' + esc(d.insertion_date) + ' · Updated ' + esc(d.updated_at) + '</div>'
      + '<strong>News</strong>' + listHtml(d.news, 'No company news')
      + '<strong>Sectoral</strong>' + listHtml(d.sectoral_news, 'No sector news')
      + '<strong>Analyst calls</strong>' + listHtml(d.analyst_calls, 'No analyst items');
  }}
  function place(el) {{
    const frame = window.frameElement;
    const r = el.getBoundingClientRect();
    let left = r.right - 2, top = r.top;
    if (frame) {{
      const fr = frame.getBoundingClientRect();
      left = fr.left + r.right - 2;
      top = fr.top + r.top;
    }}
    const vw = window.parent.innerWidth, vh = window.parent.innerHeight;
    if (left + 460 > vw - 8) left = Math.max(8, vw - 468);
    if (top + 300 > vh - 8) top = Math.max(8, vh - 308);
    pop.style.left = left + 'px';
    pop.style.top = top + 'px';
    pop.style.display = 'block';
  }}
  let hideT = null;
  function hideNow() {{
    if (pop.dataset.over === '1') return;
    pop.style.display = 'none';
  }}
  function hideSoon() {{
    clearTimeout(hideT);
    hideT = setTimeout(hideNow, 400);
  }}
  function show(el) {{
    const scrip = el.getAttribute('data-scrip');
    if (!scrip) return;
    clearTimeout(hideT);
    render(scrip);
    place(el);
  }}
  pop.onmouseenter = function() {{
    pop.dataset.over = '1';
    clearTimeout(hideT);
  }};
  pop.onmouseleave = function() {{
    pop.dataset.over = '0';
    hideSoon();
  }};
  document.querySelectorAll('.nws-ico').forEach(function(el) {{
    el.addEventListener('mouseenter', function() {{ show(el); }});
    el.addEventListener('mouseleave', hideSoon);
  }});
  if (!P._scripNewsDocClick) {{
    P._scripNewsDocClick = true;
    P.addEventListener('click', function(e) {{
      if (pop.contains(e.target)) return;
      pop.dataset.over = '0';
      pop.style.display = 'none';
    }});
  }}

  const list = document.querySelector('.list');
  function findScroller(root) {{
    if (!root) return null;
    const nodes = root.querySelectorAll('div,canvas');
    let best = null, bestDelta = 0;
    for (let i = 0; i < nodes.length; i++) {{
      const n = nodes[i];
      if (n.tagName === 'CANVAS') continue;
      const delta = n.scrollHeight - n.clientHeight;
      if (delta < 8 || n.clientHeight < 40) continue;
      const st = P.defaultView.getComputedStyle(n);
      const oy = st.overflowY;
      const score = delta + ((oy === 'auto' || oy === 'scroll' || oy === 'overlay') ? 10000 : 0);
      if (score > bestDelta) {{ best = n; bestDelta = score; }}
    }}
    return best;
  }}
  function bindScroll() {{
    const frame = window.frameElement;
    if (!frame) return false;
    let host = frame.parentElement;
    for (let i = 0; i < 8 && host; i++) {{
      if (host.getAttribute && host.getAttribute('data-testid') === 'stHorizontalBlock') break;
      host = host.parentElement;
    }}
    if (!host) return false;
    const df = host.querySelector('[data-testid="stDataFrame"]');
    const scroller = findScroller(df);
    if (!scroller || !list) return false;
    if (scroller._nwsBound) return true;
    scroller._nwsBound = true;
    const sync = function() {{ list.scrollTop = scroller.scrollTop; }};
    scroller.addEventListener('scroll', sync, {{passive: true}});
    sync();
    document.addEventListener('wheel', function(e) {{
      scroller.scrollTop += e.deltaY;
      list.scrollTop = scroller.scrollTop;
      e.preventDefault();
    }}, {{passive: false}});
    df.addEventListener('wheel', function(e) {{
      list.scrollTop = scroller.scrollTop + e.deltaY;
    }}, {{passive: true}});
    return true;
  }}
  function bindWheelOnly() {{
    const frame = window.frameElement;
    if (!frame) return false;
    let host = frame.parentElement;
    for (let i = 0; i < 8 && host; i++) {{
      if (host.getAttribute && host.getAttribute('data-testid') === 'stHorizontalBlock') break;
      host = host.parentElement;
    }}
    const df = host && host.querySelector('[data-testid="stDataFrame"]');
    if (!df || !list) return false;
    if (df._nwsWheel) return true;
    df._nwsWheel = true;
    df.addEventListener('wheel', function(e) {{ list.scrollTop += e.deltaY; }}, {{passive: true}});
    document.addEventListener('wheel', function(e) {{
      list.scrollTop += e.deltaY;
      df.dispatchEvent(new WheelEvent('wheel', {{deltaY: e.deltaY, bubbles: true}}));
      e.preventDefault();
    }}, {{passive: false}});
    return true;
  }}
  let tries = 0;
  (function retry() {{
    if (bindScroll() || bindWheelOnly() || tries > 25) return;
    tries += 1;
    setTimeout(retry, 120);
  }})();
}})();
</script>
</body></html>"""


def display_dataframe(
    st_mod,
    data,
    height=110,
    column_order=None,
    column_config=None,
    use_container_width=True,
):
    import chart_preview as chart_preview

    if not is_enabled():
        chart_preview.display_dataframe(
            st_mod,
            data,
            height=height,
            column_order=column_order,
            column_config=column_config,
            use_container_width=use_container_width,
        )
        return

    scrips = _scrip_list(data)
    left, right = st_mod.columns([0.05, 0.95])
    with left:
        if scrips:
            page = _icon_strip_page(scrips, load_news_map(), height)
            components.html(page, height=int(height) + 8, scrolling=False)
    with right:
        chart_preview.display_dataframe(
            st_mod,
            data,
            height=height,
            column_order=column_order,
            column_config=column_config,
            use_container_width=use_container_width,
        )
