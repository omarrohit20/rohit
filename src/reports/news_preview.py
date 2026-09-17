"""News preview via an ℹ strip to the LEFT of the table (not inside it).

The dataframe is unchanged — same chart_preview / Styler path as before.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
import time

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

PURPLE_BG = "#E9D5FF"
YELLOW_BG = "#FFF59D"
# Match scan-news-conviction: sectoral headlines count only when there are >= 3.
MIN_SECTORAL_FOR_SENTIMENT = 3

_SESSION_ENABLED = "news_preview_enabled"
_NEWS_SENTIMENT_KEY = "news_sentiment_filter"
NEWS_SENTIMENT_CHOICES = ("All", "Bullish", "Bearish", "Bullish or Bearish")
_ROW_H = 35
_HEADER_H = 36


def is_enabled():
    return bool(st.session_state.get(_SESSION_ENABLED, True))


def current_news_sentiment():
    try:
        choice = str(st.session_state.get(_NEWS_SENTIMENT_KEY) or "")
    except Exception:
        choice = ""
    if choice in NEWS_SENTIMENT_CHOICES:
        return choice
    return "All"


def render_sidebar_controls():
    st.sidebar.markdown("---")
    st.sidebar.subheader("News & sentiment")
    st.sidebar.checkbox(
        "Show news info icons",
        value=st.session_state.get(_SESSION_ENABLED, True),
        key=_SESSION_ENABLED,
        help="ℹ sits to the left of the table. Hover for conviction, sentiment, and news. Leave to close; stay on the preview to keep it open.",
    )
    if _NEWS_SENTIMENT_KEY not in st.session_state:
        st.session_state[_NEWS_SENTIMENT_KEY] = "All"
    st.sidebar.selectbox(
        "News sentiment",
        list(NEWS_SENTIMENT_CHOICES),
        key=_NEWS_SENTIMENT_KEY,
        help="Keep table rows whose scrip_news overall_sentiment is Bullish, Bearish, or either.",
    )
    choice = current_news_sentiment()
    if choice != "All":
        try:
            import rbase as _rb
            n = len(_rb.news_sentiment_scrips(choice))
            st.sidebar.caption(f"{n} scrips with {choice.lower()} news")
        except Exception:
            pass



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


@st.cache_data(ttl=3600)
def _fetch_news_docs(cache_ver=5):
    del cache_ver
    try:
        from pymongo import MongoClient
    except Exception:
        return []
    try:
        client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2500)
        docs = list(
            client.Nsedata.scrip_news.find(
                {},
                {
                    "_id": 0,
                    "scrip": 1,
                    "industry": 1,
                    "overall_sentiment": 1,
                    "conviction": 1,
                    "scan_tables": 1,
                    "insertion_date": 1,
                    "updated_at": 1,
                    "news": 1,
                    "sectoral_news": 1,
                    "analyst_calls": 1,
                },
            )
        )
        client.close()
        return docs
    except Exception:
        return []


_NEWS_CACHE = {"t": 0.0, "map": {}, "ver": 0}
_NEWS_CACHE_VER = 5
_NEWS_TTL = 3600.0


def load_news_map():
    now = time.time()
    if (
        _NEWS_CACHE["map"]
        and _NEWS_CACHE.get("ver") == _NEWS_CACHE_VER
        and (now - _NEWS_CACHE["t"]) < _NEWS_TTL
    ):
        return _NEWS_CACHE["map"]
    out = {}
    for doc in _fetch_news_docs(cache_ver=5):
        key = _scrip_key(doc.get("scrip"))
        if key:
            out[key] = _public_doc(doc)
    _NEWS_CACHE["t"] = now
    _NEWS_CACHE["ver"] = _NEWS_CACHE_VER
    _NEWS_CACHE["map"] = out
    return out


def _fmt_dt(value):
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    return str(value or "")


def _to_date(value):
    ts = pd.to_datetime(value, errors="coerce")
    if ts is None or pd.isna(ts):
        return None
    try:
        return ts.date()
    except Exception:
        return None


def is_today_or_yesterday(value, today=None):
    """True when a scan-news date is today or yesterday (calendar days)."""
    d = _published_on_date(value)
    if d is None:
        return False
    cur = today or datetime.now().date()
    return d in (cur, cur - timedelta(days=1))


def _published_on_date(value):
    """Parse an article published timestamp to a calendar date."""
    if value is None or value == "":
        return None
    d = _to_date(value)
    if d is not None:
        return d
    text = str(value).strip()
    if not text:
        return None
    try:
        from email.utils import parsedate_to_datetime

        dt = parsedate_to_datetime(text)
        if dt is not None:
            if getattr(dt, "tzinfo", None) is not None:
                dt = dt.astimezone().replace(tzinfo=None)
            return dt.date()
    except Exception:
        pass
    return None


def _fmt_published(value):
    d = _published_on_date(value)
    if d is not None:
        return d.strftime("%Y-%m-%d")
    text = str(value or "").strip()
    return text[:16] if text else ""


def _published_recency(value, today=None):
    d = _published_on_date(value)
    if d is None:
        return ""
    cur = today or datetime.now().date()
    if d == cur:
        return "today"
    if d == cur - timedelta(days=1):
        return "yesterday"
    return ""


def _company_news_items(doc):
    items = (doc or {}).get("news") or []
    if not isinstance(items, list):
        return []
    out = []
    for it in items:
        if not isinstance(it, dict):
            continue
        kind = str(it.get("kind") or "news").strip().lower()
        if kind and kind != "news":
            continue
        if str(it.get("title") or it.get("link") or "").strip():
            out.append(it)
    return out


def _company_news_published_dates(doc=None, today=None):
    cur = today or datetime.now().date()
    dates = set()
    for it in _company_news_items(doc):
        d = _published_on_date(it.get("published"))
        if d in (cur, cur - timedelta(days=1)):
            dates.add(d)
    return dates


def has_company_news_today(doc=None, today=None):
    cur = today or datetime.now().date()
    return cur in _company_news_published_dates(doc, today=today)


def has_company_news_yesterday(doc=None, today=None):
    cur = today or datetime.now().date()
    return (cur - timedelta(days=1)) in _company_news_published_dates(doc, today=today)


def has_company_news_today_or_yesterday(doc=None, today=None):
    """True when any company news headline was published today or yesterday."""
    return bool(_company_news_published_dates(doc, today=today))


def company_news_recency(doc=None, today=None):
    """Return 'today', 'yesterday', or '' for company-news icon highlight."""
    if has_company_news_today(doc, today=today):
        return "today"
    if has_company_news_yesterday(doc, today=today):
        return "yesterday"
    return ""


def _nonempty_articles(items):
    if not items:
        return False
    if not isinstance(items, list):
        return bool(str(items).strip())
    for it in items:
        if isinstance(it, dict):
            if str(it.get("title") or it.get("link") or "").strip():
                return True
        elif str(it or "").strip():
            return True
    return False


def _sectoral_for_sentiment(items):
    """Sectoral headlines are ignored unless there are at least 3."""
    items = items or []
    if not isinstance(items, list) or len(items) < MIN_SECTORAL_FOR_SENTIMENT:
        return []
    return items


def has_news_and_sentiment(doc):
    """True when scrip_news has sentiment and at least one scoring news item."""
    if not doc:
        return False
    sentiment = str(doc.get("overall_sentiment") or "").strip()
    if not sentiment:
        return False
    return (
        _nonempty_articles(doc.get("news"))
        or _nonempty_articles(_sectoral_for_sentiment(doc.get("sectoral_news")))
        or _nonempty_articles(doc.get("analyst_calls"))
    )


def should_yellow_highlight(doc=None, today=None):
    """Yellow when company news was published today or yesterday."""
    return has_company_news_today_or_yesterday(doc, today=today)


def _trim_articles(items, n=10):
    out = []
    for it in (items or [])[:n]:
        published = it.get("published") or ""
        out.append(
            {
                "title": it.get("title") or "",
                "link": it.get("link") or "",
                "sentiment": it.get("sentiment") or "",
                "source": it.get("source") or "",
                "impact_score": it.get("impact_score"),
                "published": published,
                "published_date": _fmt_published(published),
                "published_recency": _published_recency(published),
            }
        )
    return out


def _public_doc(doc: dict) -> dict:
    news = _trim_articles(doc.get("news"), 10)
    sectoral_raw = doc.get("sectoral_news") or []
    sectoral = _trim_articles(_sectoral_for_sentiment(sectoral_raw), 6)
    analyst = _trim_articles(doc.get("analyst_calls"), 6)
    sentiment = doc.get("overall_sentiment") or "Neutral"
    # Thin sectoral-only rows must not stay Bullish/Bearish in the preview.
    if not news and not analyst and len(sectoral_raw) < MIN_SECTORAL_FOR_SENTIMENT:
        sentiment = "Neutral"
    return {
        "scrip": doc.get("scrip"),
        "industry": doc.get("industry") or "",
        "overall_sentiment": sentiment,
        "conviction": doc.get("conviction") or "Low",
        "scan_tables": doc.get("scan_tables") or [],
        "insertion_date": _fmt_dt(doc.get("insertion_date")),
        "updated_at": _fmt_dt(doc.get("updated_at")),
        "news": news,
        "sectoral_news": sectoral,
        "analyst_calls": analyst,
    }


def _icon_strip_page(scrips, news_map, height):
    icons = []
    for scrip in scrips:
        doc = news_map.get(scrip)
        if not doc or (not has_news_and_sentiment(doc) and not should_yellow_highlight(doc)):
            icons.append('<div class="nws-ico empty"></div>')
            continue
        esc = (
            str(scrip)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace('"', "&quot;")
        )
        recency = company_news_recency(doc)
        sent = str((doc or {}).get("overall_sentiment") or "").strip().lower()
        sent_cls = " bull" if sent == "bullish" else (" bear" if sent == "bearish" else "")
        if recency == "today":
            cls = "nws-ico recent-today" + sent_cls
            title = f"{esc} news · company news today"
        elif recency == "yesterday":
            cls = "nws-ico recent-yesterday" + sent_cls
            title = f"{esc} news · company news yesterday"
        else:
            cls = "nws-ico" + sent_cls
            title = f"{esc} news"
        icons.append(f'<div class="{cls}" data-scrip="{esc}" title="{title}">ℹ</div>')
    icons_html = "".join(icons)
    payload = json.dumps({"news": news_map})
    h = int(height)
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  html,body{{margin:0;padding:0;background:transparent;overflow:clip;height:100%;width:100%;
    overscroll-behavior:none;touch-action:none;}}
  .pad{{height:{_HEADER_H}px;flex:0 0 {_HEADER_H}px;}}
  .list{{height:{max(h - _HEADER_H, 40)}px;overflow:clip;overscroll-behavior:none;touch-action:none;}}
  .track{{will-change:transform;}}
  .nws-ico{{height:{_ROW_H}px;line-height:{_ROW_H}px;text-align:center;cursor:pointer;
    font-size:16px;color:#1d4ed8;user-select:none;}}
  .nws-ico.empty{{cursor:default;}}
  .nws-ico.bull{{color:#39FF14;font-weight:700;text-shadow:0 0 6px #39FF14;}}
  .nws-ico.bear{{color:#FF073A;font-weight:700;text-shadow:0 0 6px #FF073A;}}
  .nws-ico:hover{{background:#dbeafe;border-radius:4px;}}
  .nws-ico.empty:hover{{background:transparent;}}
  .nws-ico.recent-today{{background:{PURPLE_BG};border-radius:4px;font-weight:700;
    box-shadow:inset 0 0 0 1px #a855f7;}}
  .nws-ico.recent-today:hover{{background:#d8b4fe;}}
  .nws-ico.recent-yesterday{{background:{YELLOW_BG};border-radius:4px;font-weight:700;
    box-shadow:inset 0 0 0 1px #ca8a04;}}
  .nws-ico.recent-yesterday:hover{{background:#ffe566;}}
</style></head>
<body>
<div class="pad"></div>
<div class="list"><div class="track">{icons_html}</div></div>
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
  function listHtml(items, emptyText, highlightDates) {{
    if (!items || !items.length) return '<p style="color:#94a3b8">' + emptyText + '</p>';
    return '<ul style="margin:4px 0 12px;padding-left:0;list-style:none">' + items.map(function(it) {{
      const t = esc(it.title);
      const href = it.link ? '<a href="' + esc(it.link) + '" target="_blank" rel="noopener" style="color:#93c5fd">' + t + '</a>' : t;
      const imp = it.impact_score != null ? ' · impact ' + it.impact_score : '';
      const dt = esc(it.published_date || '');
      const datePart = dt ? '<span style="color:#64748b;margin-right:6px;font-weight:600">' + dt + '</span>' : '';
      let rowStyle = 'margin:4px 0;padding:6px 8px;border-radius:4px;';
      if (highlightDates) {{
        if (it.published_recency === 'today') rowStyle += 'background:{PURPLE_BG};';
        else if (it.published_recency === 'yesterday') rowStyle += 'background:{YELLOW_BG};';
      }}
      return '<li style="' + rowStyle + '">' + datePart + href + ' <span style="color:#94a3b8">(' + esc(it.sentiment) + ' · ' + esc(it.source) + imp + ')</span></li>';
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
      + '<strong>News</strong>' + listHtml(d.news, 'No company news', true)
      + '<strong>Sectoral</strong>' + listHtml(d.sectoral_news, 'No sector news', false)
      + '<strong>Analyst calls</strong>' + listHtml(d.analyst_calls, 'No analyst items', true);
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
  document.querySelectorAll('.nws-ico[data-scrip]').forEach(function(el) {{
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

  const track = document.querySelector('.track');
  const list = document.querySelector('.list');
  const pad = document.querySelector('.pad');
  let scroller = null;
  let df = null;
  function applyY(y) {{
    if (track) track.style.transform = 'translateY(' + (-(y || 0)) + 'px)';
  }}
  function pinLocal() {{
    document.documentElement.scrollTop = 0;
    document.body.scrollTop = 0;
    if (list) list.scrollTop = 0;
  }}
  function isVisible(el) {{
    if (!el || !el.isConnected) return false;
    const cs = P.defaultView.getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || el.offsetHeight < 20) return false;
    const r = el.getBoundingClientRect();
    return r.height >= 20 && r.width >= 20;
  }}
  function pickRightOf(frame, grids) {{
    const fr = frame.getBoundingClientRect();
    let best = null, bestScore = 1e12;
    for (let i = 0; i < grids.length; i++) {{
      const el = grids[i];
      if (!isVisible(el)) continue;
      const r = el.getBoundingClientRect();
      const dy = r.top - fr.top;
      if (dy > 48 || dy < -80) continue;
      let dx = r.left - fr.right;
      if (dx < -12) continue;
      const score = Math.abs(dy) * 12 + dx;
      if (score < bestScore) {{ best = el; bestScore = score; }}
    }}
    return best;
  }}
  function locateGrid() {{
    const frame = window.frameElement;
    if (!frame) return null;
    let col = frame.parentElement;
    for (let i = 0; i < 24 && col; i++) {{
      const tid = col.getAttribute && col.getAttribute('data-testid');
      if (tid === 'stColumn') {{
        const row = col.parentElement;
        if (row) {{
          const hit = pickRightOf(frame, row.querySelectorAll('[data-testid="stDataFrame"]'));
          if (hit) return hit;
        }}
        break;
      }}
      col = col.parentElement;
    }}
    return pickRightOf(frame, P.querySelectorAll('[data-testid="stDataFrame"]'));
  }}
  function findScroller(root) {{
    if (!root) return null;
    const named = root.querySelector('.dvn-scroller')
      || root.querySelector('[class*="dvn-scroller"]')
      || root.querySelector('[class*="gdg-"][class*="scroll"]');
    if (named && named.scrollHeight - named.clientHeight >= 0) return named;
    const nodes = root.querySelectorAll('div');
    let best = null, bestDelta = 0;
    for (let i = 0; i < nodes.length; i++) {{
      const n = nodes[i];
      const delta = n.scrollHeight - n.clientHeight;
      if (delta < 8 || n.clientHeight < 24) continue;
      const oy = P.defaultView.getComputedStyle(n).overflowY;
      if (oy !== 'auto' && oy !== 'scroll' && oy !== 'overlay') continue;
      if (delta > bestDelta) {{ best = n; bestDelta = delta; }}
    }}
    return best;
  }}
  function syncMetrics(root, s) {{
    if (!root || !s || !pad) return;
    const headerH = Math.round(s.getBoundingClientRect().top - root.getBoundingClientRect().top);
    if (headerH >= 20 && headerH <= 120 && pad._h !== headerH) {{
      pad._h = headerH;
      pad.style.height = headerH + 'px';
      pad.style.flexBasis = headerH + 'px';
      if (list) list.style.height = Math.max({h} - headerH, 40) + 'px';
    }}
    const cell = s.querySelector('[role="gridcell"]');
    let rowH = { _ROW_H };
    if (cell) {{
      const ch = cell.getBoundingClientRect().height;
      if (ch >= 20 && ch <= 64) rowH = Math.round(ch);
    }}
    if (track && track._rh !== rowH) {{
      track._rh = rowH;
      document.querySelectorAll('.nws-ico').forEach(function(el) {{
        el.style.height = rowH + 'px';
        el.style.lineHeight = rowH + 'px';
      }});
    }}
  }}
  function resolve() {{
    const next = locateGrid();
    if (next !== df) {{
      df = next;
      scroller = findScroller(df);
      if (scroller && !scroller._nwsListen) {{
        scroller._nwsListen = true;
        scroller.addEventListener('scroll', function() {{ applyY(scroller.scrollTop); }}, {{passive: true}});
      }}
    }} else if (df && (!scroller || !scroller.isConnected)) {{
      scroller = findScroller(df);
    }}
    return scroller;
  }}
  function sync() {{
    pinLocal();
    const s = resolve();
    if (s) {{
      syncMetrics(df, s);
      applyY(s.scrollTop);
    }}
  }}
  document.addEventListener('wheel', function(e) {{
    e.preventDefault();
    e.stopPropagation();
    pinLocal();
    const s = resolve();
    if (!s) return;
    s.scrollTop += e.deltaY;
    applyY(s.scrollTop);
  }}, {{passive: false}});
  document.addEventListener('touchmove', function(e) {{ e.preventDefault(); }}, {{passive: false}});
  (function tick() {{
    sync();
    requestAnimationFrame(tick);
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

    news_map = load_news_map()
    scrips = _scrip_list(data) if is_enabled() else []
    table_news = {
        s: news_map[s]
        for s in scrips
        if s in news_map
        and (
            has_news_and_sentiment(news_map[s])
            or should_yellow_highlight(news_map[s])
        )
    } if scrips else {}
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

    left, right = st_mod.columns([0.05, 0.95])
    with left:
        page = _icon_strip_page(scrips, table_news, height)
        components.html(page, height=int(height), scrolling=False)
    with right:
        chart_preview.display_dataframe(
            st_mod,
            data,
            height=height,
            column_order=column_order,
            column_config=column_config,
            use_container_width=use_container_width,
        )
