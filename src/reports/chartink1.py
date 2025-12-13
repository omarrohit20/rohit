# Create a streamlit app that shows the mongodb data
from streamlit_autorefresh import st_autorefresh
import streamlit as st
import rbase as rb

# Run the autorefresh approximately every 30000 milliseconds (30 seconds)
st_autorefresh(interval=30000, key="data_refresher")

# setting the screen size
st.set_page_config(layout="wide",
                   page_title="Dashboard",
                   initial_sidebar_state="expanded",)

# main title
st.title('chartink-1')


col1, col2, col3, col4 = st.columns(4)
with col1:
    df = rb.getdf('morning-volume-breakout-buy')
    filtered_df = df
    try:
        filtered_df = df[
            (df['filter5'].str.contains('DOJI', case=False, regex=True, na=False)) &
            (df['lowTail'] < 1) &
            (df['PCT_day_change_pre2'] > -0.5) &
            (df['week2HighChange'] >= -2) &
            (df['week2HighChange'] <= 5) &
            (df['PCT_day_change_pre1'] >= 1) &
            (df['PCT_day_change_pre1'] <= 3.5) &
            (df['year5HighChange'] < -10) &
            (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False))
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'DOJI Breakout Buy', color='G')
with col2:
    df = rb.getdf('morning-volume-breakout-buy')
    filtered_df = df
    try:
        filtered_df = df[
            (df['lowTail'] < 1) &
            (df['PCT_day_change_pre2'] >= 2) &
            (df['PCT_day_change_pre2'] <= 4) &
            (df['PCT_day_change'] >= -2) &
            (df['PCT_day_change'] <= 0)
        ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'PctDayChangePre2 - Doji Buy', color='G')
with col3:
    df = rb.getdf('morning-volume-breakout-sell')
    filtered_df = df
    try:
        filtered_df = df[
            (df['filter5'].str.contains('DOJI', case=False, regex=True, na=False)) &
            (df['PCT_day_change_pre2'] >= -1) &
            (df['PCT_day_change_pre2'] <= 0.5) &
            (df['highTail'] < 1) &
            (df['PCT_day_change_pre1'] >= -3.5) &
            (df['PCT_day_change_pre1'] <= -1.5) &
            (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
            (df['week2LowChange'] >= -5) &
            (df['week2LowChange'] <= 2) &
            (df['monthHighChange'] > -10)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'DOJI Breakout Sell', color='R')
with col4:
    df = rb.getdf('morning-volume-breakout-sell')
    filtered_df = df
    try:
        filtered_df = df[
            (df['highTail'] < 1) &
            (df['PCT_day_change_pre2'] >= -4) &
            (df['PCT_day_change_pre2'] <= -2) &
            (df['PCT_day_change'] >= 0) &
            (df['PCT_day_change'] <= 2)
        ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'PctDayChangePre2 - Doji Sell', color='R')












