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
st.title('chartink-0')

col1, col2 = st.columns(2)
with col1:
    df = rb.getdf('morning-volume-breakout-buy')
    rb.render(st, df, 'morning-volume-breakout-buy', color='G')
with col2:
    df = rb.getdf('morning-volume-breakout-sell')
    rb.render(st, df, 'morning-volume-breakout-sell', color='R')


col1, col2, col3, col4 = st.columns(4)
with col1:
    df = rb.getdf('morning-volume-breakout-buy')
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] > 2) &
            (df['PCT_day_change'] < 4) &
            (df['PCT_day_change_pre1'] < 1) &
            ((df['mlData'].str.contains("TOP") | df['systemtime'].str.contains("09:20")))
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'LastDayGT1:TodayNotDown : Aftert10:00AM-Try', color='G', height=150)
with col2:
    df = rb.getdf('morning-volume-breakout-buy')
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] > -3) &
            (df['PCT_day_change'] < -1.75) &
            (df['PCT_day_change_pre1'] < 0) &
            ((df['mlData'].str.contains("TOP") | df['systemtime'].str.contains("09:20")))
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'LastDayGT1:TodayNotDown', color='G', height=150)
with col3:
    df = rb.getdf('morning-volume-breakout-sell')
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] > -4) &
            (df['PCT_day_change'] < -1.75) &
            (df['PCT_day_change_pre1'] > -1) &
            ((df['mlData'].str.contains("TOP") | df['systemtime'].str.contains("09:20")))
            ]
    except KeyError as e:
        print("")

    rb.render(st, filtered_df, 'LastDayLT-1:TodayNotUp : Aftert10:00AM-Try', color='R', height=150)
with col4:
    df = rb.getdf('morning-volume-breakout-sell')
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] > 1.75) &
            (df['PCT_day_change'] < 3) &
            (df['PCT_day_change_pre1'] > 0) &
            ((df['mlData'].str.contains("TOP") | df['systemtime'].str.contains("09:20")))
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'LastDayLT-1:TodayNotUp', color='R', height=150)


col1, col2, col3, col4 = st.columns(4)
with col1:
    df = rb.getdf('morning-volume-breakout-buy')
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] > 4) &
            (df['PCT_day_change'] < 7) &
            (~df['filter5'].str.contains("BothGT1.5")) &
            (~df['filter5'].str.contains("PRE1or2GT2")) &
            (df['week2LowChange'] < 15)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'RISKY:LDayMarketUpTodayUp', color='LG', height=150)
with col2:
    df = rb.getdf('morning-volume-breakout-buy')
    filtered_df = df
    try:
        filtered_df = df[
            (df['week2LowChange'] < 5) &
            (df['week2HighChange'] < -2) &
            (df['PCT_day_change'] > -3.5) &
            (df['PCT_day_change'] < -1.5) &
            (df['PCT_day_change'] > -4) &
            (df['PCT_day_change'] < -1) &
            (df['month3HighChange'] > -15) &
            (df['filter5'].str.contains("PRE1or2LT-1")) &
            (df['highTail'] < 1)
        ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'LastDayMarketLT-1:OrDowntrend : todayUpGT0.5', color='G', height=150)
with col3:
    df = rb.getdf('morning-volume-breakout-sell')
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] > -7) &
            (df['PCT_day_change'] < -4) &
            (~df['filter5'].str.contains("BothLT-1.5")) &
            (df['week2HighChange'] > -15)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'RISKY:LDayMarketDownTodayDown', color='LG', height=150)
with col4:
    df = rb.getdf('morning-volume-breakout-sell')
    filtered_df = df
    try:
        filtered_df = df[
            (df['week2LowChange'] > 2) &
            (df['week2HighChange'] > -5) &
            (df['PCT_day_change'] > 0.75) &
            (df['PCT_day_change'] < 4.5) &
            (df['PCT_day_change'] > 1) &
            (df['PCT_day_change'] < 4.5) &
            (df['month3LowChange'] < 10) &
            (df['filter5'].str.contains("PRE1or2GT1")) &
            (df['lowTail'] < 1)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'LastDayMarketGT1:OrUptrend : todayDownLT-0.5', color='R', height=150)


col1, col2, col3, col4 = st.columns(4)
with col1:
    df = rb.getdf('morning-volume-breakout-buy')
    rb.render(st, df, 'LastDayDownTodayUpGT1(Pre1or2GT2)', color='G', height=150)
with col2:
    df = rb.getdf('morning-volume-breakout-buy')
    rb.render(st, df, 'LastDayMarketLT-1 : todayUpGT0.5', color='G', height=150)
with col3:
    df = rb.getdf('morning-volume-breakout-sell')
    rb.render(st, df, 'LastDayUpTodayDown(Pre1or2LT-2)', color='R', height=150)
with col4:
    df = rb.getdf('morning-volume-breakout-sell')
    rb.render(st, df, 'LastDayMarketGT1 : todayDownLT-0.5', color='R', height=150)







