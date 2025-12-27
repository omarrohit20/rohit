# Streamlit navigation index for pages in this folder
import streamlit as st
from pathlib import Path
import os
import urllib.parse

st.set_page_config(layout="wide", page_title="Reports Index", initial_sidebar_state="expanded")

# Discover python files in the same folder
base = Path(__file__).parent
exclude = {Path(__file__).name, "__init__.py", "rbase.py", "temp.py"}
py_files = [p.name for p in base.glob("*.py") if p.name not in exclude]
py_files.sort()

# Respect query params for initial page selection
try:
    params = st.query_params
except Exception:
    params = {}

path_param = params.get('path', [None])[0]
fullpath_param = params.get('fullpath', [None])[0]

# Determine default index from query params (try filename first, then basename of path)
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


def _set_query_params(path, fullpath):
    """Set query params using available Streamlit API (prefers stable `set_query_params`)."""
    try:
        setter = getattr(st, "set_query_params", None) or getattr(st, "experimental_set_query_params", None)
        if setter:
            setter(path=path, fullpath=fullpath)
    except Exception:
        pass

default_index = None
if path_param:
    default_index = _find_index_from_param(path_param)
if default_index is None and fullpath_param:
    default_index = _find_index_from_param(fullpath_param)
if default_index is None:
    default_index = 0

# Initialize selected page from query params once (don't override user changes later)
if 'initialized_from_query' not in st.session_state:
    if path_param or fullpath_param:
        try:
            st.session_state['selected_page'] = py_files[default_index]
        except Exception:
            pass
    st.session_state['initialized_from_query'] = True

in_process = st.sidebar.checkbox("Load pages in-process (single Streamlit app)", value=True)
selected = st.sidebar.selectbox("Open page", py_files, index=default_index, key="selected_page")

# Ensure the browser URL shows the selected page (set once per change to avoid rerun loops)
try:
    cur_path = selected
    cur_full = str(base / selected)
    if st.session_state.get('_last_query_path') != cur_path:
        _set_query_params(cur_path, cur_full)
        st.session_state['_last_query_path'] = cur_path
except Exception:
    pass

st.sidebar.markdown("---")
st.sidebar.write("Select a page above to start it. In-process mode imports the module and calls `main()` (recommended). Otherwise it will start a separate Streamlit process.")

import subprocess
import sys
import socket
import os
import urllib.parse


def _find_free_port(start=8501, end=8600):
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            res = s.connect_ex(('127.0.0.1', port))
            if res != 0:
                return port
    raise RuntimeError("No free port found")

if 'page_processes' not in st.session_state:
    st.session_state['page_processes'] = {}

if selected:
    sel_path = base / selected
    st.subheader(f"{selected}")

    if in_process:
        # Attempt to import and call main() from the module
        import importlib.util
        try:
            import rbase as rb
            rb.chartlink0 = False
            rb.chartlink1 = False
        except Exception:
            pass

        try:
            spec = importlib.util.spec_from_file_location(selected[:-3], sel_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
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
