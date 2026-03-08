# Create a streamlit app that shows the mongodb data
from streamlit_autorefresh import st_autorefresh
import streamlit as st
import rbase as rb
import pandas as pd


# Run the autorefresh approximately every 30000 milliseconds (30 seconds)

def main():
    #st_autorefresh(interval=30000, key="data_refresher")

    # setting the screen size (ignore if already set by index)
    try:
        st.set_page_config(layout="wide",
                           page_title="DashboardShortTerm",
                           initial_sidebar_state="expanded",)
    except Exception:
        pass

    # main title
    st.title('ShortTerm')

    rb.testLearning = True

    col0, col1 = st.columns(2)
    with col0:
        df = rb.getdf_raw('breakoutYH')
        rb.render_rawdata(st, df,'breakoutYH')
    with col1:
        df = rb.getdf_raw('breakoutY2H')
        rb.render_rawdata(st, df,'breakoutY2H')
    

    

if __name__ == '__main__':
    main()