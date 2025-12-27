# Streamlit navigation index for pages in this folder
import streamlit as st
from pathlib import Path

st.set_page_config(layout="wide", page_title="Reports Index", initial_sidebar_state="expanded")

st.title("Reports — Page Navigator")
st.markdown("Use this file as the entry point for reports. Run with `streamlit run src/reports/index.py` and select a page from the sidebar.")

# Discover python files in the same folder
base = Path(__file__).parent
exclude = {Path(__file__).name, "__init__.py", "rbase.py", "temp.py"}
py_files = [p.name for p in base.glob("*.py") if p.name not in exclude]
py_files.sort()

selected = st.sidebar.selectbox("Open page", py_files)

st.sidebar.markdown("---")
# Option: in-process navigation
in_process = st.sidebar.checkbox("Load pages in-process (single Streamlit app)", value=True)
st.sidebar.write("Select a page above to start it. In-process mode imports the module and calls `main()` (recommended). Otherwise it will start a separate Streamlit process.")

import subprocess
import sys
import socket
import os


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
            st.markdown(f"Open the page in a new tab: http://localhost:{port}")
            if st.button("Stop page"):
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                except Exception:
                    proc.kill()
                del st.session_state['page_processes'][selected]
                st.warning(f"Stopped `{selected}`")
