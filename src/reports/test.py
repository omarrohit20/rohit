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
        df = rb.getintersectdf('Breakout-Beey-2', 'breakoutYH')
        #df = rb.getdf_sandlterm('breakoutYH')
        rb.render_sandlterm_data(st, df,'breakoutYH', color='G')
    with col1:
        df = rb.getintersectdf('Breakout-Beey-2', 'breakoutY2H')
        #df = rb.getdf_sandlterm('breakoutY2H')
        rb.render_sandlterm_data(st, df,'breakoutY2H', color='G')


    col0, col1, col2 = st.columns(3)
    with col0:
        df = rb.getintersectdf('Breakout-Beey-2', 'breakoutW2HR')
        #df = rb.getdf_sandlterm('breakoutW2HR')
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
        rb.render(st, filtered_df,'breakoutW2HR', color='G')
    with col1:
        df = rb.getintersectdf('Breakout-Beey-2', 'breakoutW2HR')
        #df = rb.getdf_sandlterm('breakoutW2HR')
        filtered_df = df
        try:
            filtered_df = df[
                (df['monthHighChange'] > -3.5) &
                ((df['monthHighChange'] < -3) | (df['month3HighChange'] < -15))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df,'breakoutW2HR', color='G')
    with col2:
        df = rb.getintersectdf('Breakout-Beey-2', 'breakoutW2HR')
        #df = rb.getdf_sandlterm('breakoutW2HR')
        rb.render(st, df,'breakoutW2HR', color='LG')


    col0, col1, col2 = st.columns(3)
    with col0:
        df = rb.getintersectdf('Breakout-Beey-2', 'breakoutMHR')
        #df = rb.getdf_sandlterm('breakoutMHR')
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
        rb.render(st, filtered_df,'breakoutMHR', color='LG')
    with col1:
        df = rb.getintersectdf('Breakout-Beey-2', 'breakoutMHR')
        #df = rb.getdf_sandlterm('breakoutMHR')
        try:
            filtered_df = df[
                (df['year5HighChange'] < -30) &
                (df['year2HighChange'] < -10) &
                (df['month3HighChange'] < -5)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df,'breakoutMHR', color='LG')
    with col2:
        df = rb.getintersectdf('Breakout-Beey-2', 'breakoutMHR')
        #df = rb.getdf_sandlterm('breakoutMHR')
        rb.render(st, df,'breakoutMHR', color='LG')

    col0, col1, col2 = st.columns(3)
    with col0:
        df = rb.getintersectdf('Breakout-Beey-2', 'breakoutM2HR')
        #df = rb.getdf_sandlterm('breakoutM2HR')
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
        rb.render(st, filtered_df, 'breakoutM2HR', color='LG')
    with col1:
        df = rb.getintersectdf('Breakout-Beey-2', 'breakoutM2HR')
        #df = rb.getdf_sandlterm('breakoutM2HR')
        filtered_df = df
        try:
            filtered_df = df[
                (df['monthHighChange'] > -3.5) &
                ((df['monthHighChange'] < -3) | (df['month3HighChange'] < -15))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'breakoutM2HR', color='LG')
    with col2:
        df = rb.getintersectdf('Breakout-Beey-2', 'breakoutM2HR')
        #df = rb.getdf_sandlterm('breakoutM2HR')
        rb.render(st, df, 'breakoutM2HR', color='LG')
    

    

if __name__ == '__main__':
    main()