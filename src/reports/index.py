# Streamlit navigation index for pages in this folder
import streamlit as st
from pathlib import Path
import os
import urllib.parse

st.set_page_config(layout="wide", page_title="Reports Index", initial_sidebar_state="expanded")

# Discover python files in the same folder
base = Path(__file__).parent
exclude = {Path(__file__).name, "__init__.py", "rbase.py", "temp.py", "chart_preview.py", "news_preview.py", "index.py", "create_indexes.py"}
py_files = [p.name for p in base.glob("*.py") if p.name not in exclude]
py_files.sort()

def _query_get(name, default=None):
    """Read one query param as a string (Streamlit may return str or list)."""
    v = None
    try:
        v = st.query_params.get(name)
    except Exception:
        try:
            v = st.experimental_get_query_params().get(name)
        except Exception:
            v = None
    if v is None:
        return default
    if isinstance(v, (list, tuple)):
        return v[0] if v else default
    return str(v)


def _find_index_from_param(p):
    if not p:
        return None
    try:
        decoded = urllib.parse.unquote_plus(p)
    except Exception:
        decoded = p
    if decoded in py_files:
        return py_files.index(decoded)
    b = os.path.basename(decoded)
    if b in py_files:
        return py_files.index(b)
    return None


def _as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _seed_from_query():
    """Restore sidebar widgets from the URL on a fresh browser load."""
    if st.session_state.get("_ui_restored"):
        return
    st.session_state["_ui_restored"] = True

    idx = _find_index_from_param(_query_get("path"))
    if idx is None:
        idx = _find_index_from_param(_query_get("fullpath"))
    if idx is None:
        idx = 0
    if py_files:
        st.session_state["selected_page"] = py_files[idx]

    if "in_process" not in st.session_state:
        st.session_state["in_process"] = _as_bool(_query_get("in_process"), True)

    if "chart_preview_enabled" not in st.session_state:
        st.session_state["chart_preview_enabled"] = _as_bool(_query_get("chart"), True)
    provider = _query_get("provider")
    _providers = {"TradingView", "Chartink", "Moneycontrol", "Groww", "Trendlyne", "Custom"}
    if provider in _providers and "chart_preview_provider" not in st.session_state:
        st.session_state["chart_preview_provider"] = provider
    custom = _query_get("custom")
    if custom and "chart_preview_custom_url" not in st.session_state:
        st.session_state["chart_preview_custom_url"] = custom

    if "news_preview_enabled" not in st.session_state:
        st.session_state["news_preview_enabled"] = _as_bool(_query_get("news"), True)


def _desired_query():
    out = {
        "path": str(st.session_state.get("selected_page") or ""),
        "in_process": "1" if st.session_state.get("in_process", True) else "0",
        "chart": "1" if st.session_state.get("chart_preview_enabled", True) else "0",
        "news": "1" if st.session_state.get("news_preview_enabled", True) else "0",
        "provider": str(st.session_state.get("chart_preview_provider") or "TradingView"),
    }
    custom = st.session_state.get("chart_preview_custom_url")
    if custom:
        out["custom"] = str(custom)
    return out


def _sync_query_params():
    """Keep the URL in sync so a refresh restores page + sidebar settings."""
    desired = _desired_query()
    current = {k: _query_get(k) for k in desired}
    extra_fullpath = _query_get("fullpath")
    if current == desired and not extra_fullpath:
        return
    try:
        qp = st.query_params
        qp.from_dict(desired)
        return
    except Exception:
        pass
    try:
        setter = getattr(st, "set_query_params", None) or getattr(st, "experimental_set_query_params", None)
        if setter:
            setter(**desired)
    except Exception:
        pass


_seed_from_query()

if st.session_state.get("selected_page") not in py_files and py_files:
    st.session_state["selected_page"] = py_files[0]

in_process = st.sidebar.checkbox("Load pages in-process (single Streamlit app)", key="in_process")
selected = st.sidebar.selectbox("Open page", py_files, key="selected_page")

st.sidebar.markdown("---")
st.sidebar.write("Select a page above to start it. In-process mode imports the module and calls `main()` (recommended). Otherwise it will start a separate Streamlit process.")

try:
    import chart_preview as _chart_preview
    _chart_preview.render_sidebar_controls()
except Exception:
    pass
try:
    import importlib
    import news_preview as _news_preview
    _mt = Path(_news_preview.__file__).stat().st_mtime
    _prev = st.session_state.get("_news_preview_mtime")
    st.session_state["_news_preview_mtime"] = _mt
    if _prev is None or _prev != _mt:
        importlib.reload(_news_preview)
    _news_preview.render_sidebar_controls()
except Exception:
    pass

_sync_query_params()

import subprocess
import sys
import socket
import os
import urllib.parse
import importlib.util


def _find_free_port(start=8501, end=8600):
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            res = s.connect_ex(('127.0.0.1', port))
            if res != 0:
                return port
    raise RuntimeError("No free port found")

if 'page_processes' not in st.session_state:
    st.session_state['page_processes'] = {}


def _load_page_module(sel_path):
    import rbase as rb
    path = str(sel_path)
    try:
        mtime = sel_path.stat().st_mtime
    except OSError:
        mtime = 0
    hit = rb.PAGE_MODULE_CACHE.get(path)
    if hit and hit[0] == mtime:
        return hit[1]
    spec = importlib.util.spec_from_file_location(sel_path.stem, sel_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rb.PAGE_MODULE_CACHE[path] = (mtime, module)
    return module

if selected:
    sel_path = base / selected
    # st.subheader(f"{selected}")

    if in_process:
        # Attempt to import and call main() from the module
        try:
            import rbase as rb
            rb.chartlink0 = False
            rb.chartlink1 = False
            rb.testLearning = False
        except Exception:
            pass

        try:
            module = _load_page_module(sel_path)
            if hasattr(module, 'main'):
                try:
                    module.main()
                except Exception as e:
                    st.error(f"Error running `{selected}` in-process: {e}")
                    st.exception(e)
            else:
                st.warning(f"`{selected}` does not provide a `main()` function; falling back to process-per-page mode.")
                in_process = False
        except Exception as e:
            st.error(f"Failed to load `{selected}` in-process: {e}")
            st.exception(e)
            in_process = False

    if not in_process:
        # If already started, reuse process info
        proc_info = st.session_state['page_processes'].get(selected)
        running = False
        if proc_info:
            proc = proc_info['proc']
            port = proc_info['port']
            if proc.poll() is None:
                running = True
            else:
                # process ended; remove it
                del st.session_state['page_processes'][selected]
                proc_info = None

        if not proc_info:
            try:
                port = _find_free_port()
                cmd = [sys.executable, "-m", "streamlit", "run", str(sel_path), "--server.port", str(port), "--server.headless", "true"]
                creationflags = 0
                if os.name == 'nt' and hasattr(subprocess, 'CREATE_NEW_PROCESS_GROUP'):
                    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
                proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=creationflags)
                st.session_state['page_processes'][selected] = {'proc': proc, 'port': port}
                running = True
                st.success(f"Started `{selected}` on port {port}")
            except Exception as e:
                st.error(f"Failed to start `{selected}`: {e}")
                st.exception(e)

        if running:
            proc = st.session_state['page_processes'][selected]['proc']
            port = st.session_state['page_processes'][selected]['port']
            # include the file path as a query param in the URL
            encoded_fullpath = urllib.parse.quote_plus(str(sel_path))
            encoded_name = urllib.parse.quote_plus(selected)
            url = f"http://localhost:{port}/?path={encoded_name}&fullpath={encoded_fullpath}"
            st.markdown(f"Open the page in a new tab: {url}")
            if st.button("Stop page"):
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                except Exception:
                    proc.kill()
                del st.session_state['page_processes'][selected]
                st.warning(f"Stopped `{selected}`")
