# Create a streamlit app that shows the mongodb data
from streamlit_autorefresh import st_autorefresh
import streamlit as st
import rbase as rb
import pandas as pd

# Run the autorefresh approximately every 30000 milliseconds (30 seconds)
st_autorefresh(interval=30000, key="data_refresher")

# setting the screen size
st.set_page_config(layout="wide",
                   page_title="Dashboard",
                   initial_sidebar_state="expanded",)

# main title
st.title('10:00 -11:15 AM last 15-20 Minute trend: TrendingMarketOnlyUpDown')

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
            (df['PCT_day_change'] > -0.5) &
            (~df['processor'].str.contains('09_30:checkChartBuy/', case=False, regex=True, na=False))
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

col1, col2 = st.columns(2)
with col1:
    df = rb.getintersectdf('buy_all_processor', 'crossed-day-high')
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] >= -0.5) &
            (df['PCT_day_change'] <= 1) &
            (df['PCT_change'] < 1) &
            (df['week2HighChange'] > 2) &
            (~df['processor'].str.contains('09_30:checkChartBuy/', case=False, regex=True, na=False))
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'Buy All Processor + Crossed Day High + week2highGT2', column_order=rb.column_order_p, color='G')
with col2:
    df = rb.getintersectdf('sell_all_processor', 'crossed-day-low')
    filtered_df = df
    try:
        filtered_df = df[
            (df['week2LowChange'] < -2)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'Sell All Processor + Crossed Day Low + week2LowChangeLT-2', column_order=rb.column_order_p, color='R')

col1, col2, col3, col4 = st.columns(4)
with col1:
    df = rb.getintersectdf('buy_all_processor', '09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)')
    filtered_df = df
    try:
        filtered_df = df[
            (~df['processor'].str.contains('09_30:checkChartBuy/Sell', case=False, na=False)) &
            (~df['processor'].str.contains('1-Bbuyy-morningUp', case=False, na=False))
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'Buy All Processor + Crossed 2 Day High', column_order=rb.column_order_p, color='G')
with col2:
    df = rb.getdf('09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)')
    filtered_df = df
    rb.render(st, filtered_df, 'Crossed 2 Day Highs', color='LG')
with col3:
    df = rb.getintersectdf('sell_all_processor', '09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)')
    filtered_df = df
    try:
        filtered_df = df[
            (~df['processor'].str.contains('09_30:checkChartSell/Buy', case=False, na=False)) &
            (~df['processor'].str.contains('1-Sselll-morningDown', case=False, na=False))
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'Sell All Processor + Crossed 2 Day Low', column_order=rb.column_order_p, color='R')
with col4:
    df = rb.getdf('09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)')
    filtered_df = df
    rb.render(st, filtered_df, 'Crossed 2 Day Lows', color='LG')

col1, col2 = st.columns(2)
with col1:
    df = rb.getintersectdf('buy_all_processor', 'buy-breakout')
    expected_columns = list(set(df.columns))
    empty_df = pd.DataFrame(columns=expected_columns)
    filtered_df = df
    try:
        filtered_df = df[
            (~df['processor'].str.contains('buy-breakout')) &
            (~df['processor'].str.contains('supertrend-morning-buy')) &
            (~df['processor'].str.contains('09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)')) &
            (~df['processor'].str.contains('buy-dayconsolidation-breakout-01')) &
            (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
            (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False)) &
            (~df['systemtime'].str.contains('09:40', case=False, regex=True, na=False))
            ]
    except KeyError as e:
        print("")
    if len(filtered_df) >= 2:
        rb.render(st, filtered_df, 'Buy All Processor + Buy Breakout', column_order=rb.column_order_p, color='G')
    else:
        rb.render(st, empty_df, 'Buy All Processor + Buy Breakout', column_order=rb.column_order_p, color='G')
with col2:
    df = rb.getintersectdf('sell_all_processor', 'sell-breakout')
    expected_columns = list(set(df.columns))
    empty_df = pd.DataFrame(columns=expected_columns)
    filtered_df = df
    try:
        filtered_df = df[
            (~df['processor'].str.contains('sell-breakout'))&
            (~df['processor'].str.contains('09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)')) &
            (~df['processor'].str.contains('supertrend-morning-sell'))&
            (~df['processor'].str.contains('sell-dayconsolidation-breakout-01')) &
            (~df['processor'].str.contains('09_30:checkChartSell')) &
            (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
            (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False)) &
            (~df['systemtime'].str.contains('09:40', case=False, regex=True, na=False))
            ]
    except KeyError as e:
        print("")
    if len(filtered_df) >= 2:
        rb.render(st, filtered_df, 'Sell All Processor + Sell Breakout', column_order=rb.column_order_p, color='R')
    else:
        rb.render(st, empty_df, 'Sell All Processor + Sell Breakout', column_order=rb.column_order_p, color='R')

col1, col2 = st.columns(2)
with col1:
    df = rb.getdf('buy_all_processor')
    filtered_df = df
    try:
        filtered_df = df[
            (~df['processor'].str.contains('09_30:checkChartSell', case=False, na=False)) &
            (df['mlData'].str.contains('Stairs', case=False, na=False)) &
            (df['mlData'].str.contains('ZPre1', case=False, na=False)) &
            (~df['mlData'].str.contains('DownStairs', case=False, na=False)) &
            (~df['systemtime'].str.contains('09:', case=False, na=False)) &
            (~df['systemtime'].str.contains('10:00:', case=False, na=False))
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'Buy All Processor + ZPre1_Upstairs', column_order=rb.column_order_default, color='G')
with col2:
    df = rb.getdf('sell_all_processor')
    filtered_df = df
    try:
        filtered_df = df[
            (~df['processor'].str.contains('09_30:checkChartBuy', case=False, na=False)) &
            (df['mlData'].str.contains('stairs', case=False, na=False)) &
            (df['mlData'].str.contains('ZPre', case=False, na=False)) &
            (~df['mlData'].str.contains('UpStairs', case=False, na=False)) &
            (~df['systemtime'].str.contains('09:', case=False, na=False)) &
            (~df['systemtime'].str.contains('10:00:', case=False, na=False))
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'Sell All Processor + ZPre1_Downstairs', column_order=rb.column_order_default, color='R')

col1, col2, col3, col4 = st.columns(4)
with col1:
    df = rb.getdf('morning-volume-breakout-buy')
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] < -1) &
            (df['mlData'].str.contains("0@@C")) &
            (~df['systemtime'].str.contains("10:"))
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'CrossedDay-LastDayDownTodayUp', color='G')
with col2:
    df = rb.getintersectdf('week2lh-not-reached','crossed-day-high')
    expected_columns = list(set(df.columns))
    empty_df = pd.DataFrame(columns=expected_columns)
    filtered_df = df
    try:
        filtered_df = df[
            (~df['systemtime'].str.contains('09:', case=False, na=False)) &
            (~df['systemtime'].str.contains('10:00', case=False, na=False)) &
            (~df['systemtime'].str.contains('10:05', case=False, na=False)) &
            (~df['systemtime'].str.contains('10:10', case=False, na=False)) &
            (~df['systemtime'].str.contains('10:15', case=False, na=False))
        ]
    except KeyError as e:
        print("")
    if len(filtered_df) >= 2:
        rb.render(st, filtered_df, 'week2lh-not-reached + Crossed Day High', column_order=rb.column_order_p, color='LG')
    else:
        rb.render(st, empty_df, 'week2lh-not-reached + Crossed Day High', column_order=rb.column_order_p, color='LG')

with col3:
    df = rb.getdf('morning-volume-breakout-sell')
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] > 1) &
            (df['mlData'].str.contains("0@@C")) &
            (~df['systemtime'].str.contains("10:"))
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'CrossedDay-LastDayUpTodayDown', color='R')
with col4:
    df = rb.getintersectdf('week2lh-not-reached','crossed-day-low')
    expected_columns = list(set(df.columns))
    empty_df = pd.DataFrame(columns=expected_columns)
    filtered_df = df
    try:
        filtered_df = df[
            (~df['systemtime'].str.contains('09:', case=False, na=False)) &
            (~df['systemtime'].str.contains('10:00', case=False, na=False)) &
            (~df['systemtime'].str.contains('10:05', case=False, na=False)) &
            (~df['systemtime'].str.contains('10:10', case=False, na=False)) &
            (~df['systemtime'].str.contains('10:15', case=False, na=False))
            ]
    except KeyError as e:
        print("")
    if len(filtered_df) >= 2:
        rb.render(st, filtered_df, 'week2lh-not-reached + Crossed Day Low', column_order=rb.column_order_p, color='LG')
    else:
        rb.render(st, empty_df, 'week2lh-not-reached + Crossed Day Low', column_order=rb.column_order_p, color='LG')

