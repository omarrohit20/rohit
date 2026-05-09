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
        df = rb.getdf_sandlterm('breakoutYH')
        rb.render_sandlterm_data(st, df,'breakoutYH', color='G')
    with col1:
        df = rb.getdf_sandlterm('breakoutY2H')
        rb.render_sandlterm_data(st, df,'breakoutY2H', color='G')


    col0, col1, col2 = st.columns(3)
    with col0:
        df = rb.getdf_sandlterm('breakoutW2HR')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['monthHighChange'] < -3) | (df['month3HighChange'] < -15)) &
                ((df['monthHighChange'] > -5.5) | (df['month3HighChange'] < -20)) &
                (df['week2LowChange'] < 5.5) &
                (df['week2LowChange'] != df['weekLowChange']) &
                ((df['yearLowChange'] > 0) | (df['month2HighChange'] > -10))
                ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df,'breakoutW2HR', color='G')
    with col1:
        df = rb.getdf_sandlterm('breakoutW2HR')
        filtered_df = df
        try:
            filtered_df = df[
                (df['monthHighChange'] > -3.5) &
                ((df['monthHighChange'] < -3) | (df['month3HighChange'] < -15))
                ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df,'breakoutW2HR', color='G')
    with col2:
        df = rb.getdf_sandlterm('breakoutW2HR')
        rb.render_sandlterm_data(st, df,'breakoutW2HR', color='G')


    

    

if __name__ == '__main__':
    main()