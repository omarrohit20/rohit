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
st.title('TrendingMarketOnlyUpDown')

col1, col2, col3, col4 = st.columns(4)
with col1:
    df = rb.getintersectdf('buy-check-morning-down-breakup-02', 'crossed-day-high')
    filtered_df = df
    rb.render(st, filtered_df, 'Buy Check Morning Down Breakup 02s', color='G')
with col2:
    df = rb.getdf('supertrend-morningdown-buy')
    filtered_df = df
    rb.render(st, filtered_df, 'UpNow Supertrend MorningDown Buys', color='G')
with col3:
    df = rb.getintersectdf('sell-check-morning-up-breakdown-02', 'crossed-day-low')
    filtered_df = df
    rb.render(st, filtered_df, 'Sell Check Morning Up Breakdown 02s', color='R')
with col4:
    df = rb.getdf('supertrend-morningup-sell')
    filtered_df = df
    rb.render(st, filtered_df, 'DownNow Supertrend  Morningup Sells', color='R')


col1, col2, col3, col4 = st.columns(4)
with col1:
    df = rb.getintersectdf('buy_all_processor', 'supertrend-morning-buy')
    filtered_df = df
    try:
        filtered_df = df[
            (df['processor'] != 'cash-buy-morning-volume') &
            (df['processor'] != 'supertrend-morning-buy') &
            (df['PCT_day_change'] > -0.5)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'Buy All Processors + Supertrend Morning Buy', column_order=rb.column_order_p, color='G')
with col2:
    df = rb.getdf('supertrend-morning-buy')
    filtered_df = df
    try:
        filtered_df = df[
            (~df['systemtime'].str.contains('10:00:00', case=False, regex=True, na=False)) &
            (~df['systemtime'].str.contains('10:05:00', case=False, regex=True, na=False)) &
            (~df['systemtime'].str.contains('10:10:00', case=False, regex=True, na=False)) &
            (~df['systemtime'].str.contains('09:', case=False, regex=True, na=False))
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'Supertrend Morning Buy', color='LG')
with col3:
    df = rb.getintersectdf('sell_all_processor', 'supertrend-morning-sell')
    filtered_df = df
    try:
        filtered_df = df[
            (df['processor'] != 'cash-sell-morning-volume') &
            (df['processor'] != 'supertrend-morning-sell') &
            (df['PCT_day_change'] > -0.5)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'Sell All Processors + Supertrend Morning Sell', column_order=rb.column_order_p, color='R')
with col4:
    df = rb.getdf('supertrend-morning-sell')
    filtered_df = df
    try:
        filtered_df = df[
            (~df['systemtime'].str.contains('10:00:00', case=False, regex=True, na=False)) &
            (~df['systemtime'].str.contains('10:05:00', case=False, regex=True, na=False)) &
            (~df['systemtime'].str.contains('10:10:00', case=False, regex=True, na=False)) &
            (~df['systemtime'].str.contains('09:', case=False, regex=True, na=False))
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'Supertrend Morning Sell', color='LG')




