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

col1, col2, col3, col4 = st.columns(4)
with col1:
    df = rb.getdf('morning-volume-breakout-buy')
    filtered_df = df
    try:
        filtered_df = df[
            (df['week2HighChange'] > 0) &
            (df['monthHighChange'] < 5) &
            (df['PCT_day_change'] > 1) &
            (~df['filter5'].str.contains('BothGT2', case=False, regex=True, na=False)) &
            (df['lowTail'] < 1.5) &
            (df['forecast_day_PCT10_change'] > -1) &
            (df['week2LowChange'] > 2) &
            (df['lowTail'] < 1) &
            (df['intradaytech'].str.contains('#LT2', case=False, regex=True, na=False)) &
            (df['PCT_day_change'] < 2.5) &
            (df['weekLowChange'] > 1) &
            (df['PCT_day_change_pre1'] >= -1.5) &
            (df['PCT_day_change_pre1'] <= 2.3) &
            (df['PCT_day_change_pre2'] >= -1.5) &
            (df['PCT_day_change_pre2'] <= 3) &
            (df['weekHighChange'] > 0) &
            (df['year5HighChange'] < 0)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'week2HighGT0 : #LT2 : Avoid index up', color='G')
with col2:
    df = rb.getdf('morning-volume-breakout-buy')
    filtered_df = df
    try:
        filtered_df = df[
            (df['week2HighChange'] > -1) &
            (df['monthHighChange'] < 5) &
            (df['PCT_day_change_pre2'] < 3) &
            (df['PCT_day_change_pre1'] < 3) &
            (df['PCT_day_change'] >= -1.5) &
            (df['PCT_day_change'] <= 1) &
            (~df['filter5'].str.contains('BothGT2', case=False, regex=True, na=False)) &
            (df['intradaytech'].str.contains('#TOP', case=False, regex=True, na=False)) &
            (df['lowTail'] < 1) &
            (~df['systemtime'].str.contains('09:4', case=False, regex=True, na=False)) &
            (df['week2LowChange'] > 2) &
            (df['monthHighChange'] > 0) &
            (df['year5HighChange'] < 0) &
            (df['PCT_day_change_pre1'] < 1)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'week2HighGT0-1 : Avoid-GT2-And-Top5', color='G')
with col3:
    df = rb.getdf('morning-volume-breakout-sell')
    filtered_df = df
    try:
        filtered_df = df[
            (df['week2LowChange'] < 0) &
            (df['monthLowChange'] > -5) &
            (df['PCT_day_change'] >= -1.5) &
            (df['PCT_day_change'] <= -0.8) &
            (~df['filter5'].str.contains('BothLT-2', case=False, regex=True, na=False)) &
            (df['highTail'] < 1.5) &
            (df['forecast_day_PCT10_change'] < 1) &
            (df['week2HighChange'] < -2) &
            (df['highTail'] < 1) &
            (df['mlData'].str.contains('LT2', case=False, regex=True, na=False)) &
            (~df['systemtime'].str.contains('09:5', case=False, regex=True, na=False)) &
            (~df['systemtime'].str.contains('09:4', case=False, regex=True, na=False)) &
            (df['weekHighChange'] < -1) &
            (df['PCT_day_change_pre1'] > -2)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'week2LowLT0-1 : #LT2', color='R')
with col4:
    df = rb.getdf('morning-volume-breakout-sell')
    filtered_df = df
    try:
        filtered_df = df[
            (df['week2LowChange'] < 1) &
            (df['monthLowChange'] > -5) &
            (df['PCT_day_change_pre1'] < 3) &
            (df['PCT_day_change_pre2'] < 3) &
            (df['PCT_day_change'] >= -1.5) &
            (df['PCT_day_change'] <= 1) &
            (~df['filter5'].str.contains('BothLT-2', case=False, regex=True, na=False)) &
            (df['lowTail'] < 1) &
            (df['intradaytech'].str.contains('#TOP', case=False, regex=True, na=False)) &
            (df['monthLowChange'] < 10) &
            (df['highTail'] < 1.5) &
            (~df['systemtime'].str.contains('09:4', case=False, regex=True, na=False)) &
            (df['week2HighChange'] < -2) &
            (df['monthLowChange'] < 0)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'week2LowLT0-1 : Avoid-LT(-2)-And-Top5', color='R')

col1, col2, col3, col4 = st.columns(4)
with col1:
    df = rb.getdf('morning-volume-breakout-buy')
    filtered_df = df
    try:
        filtered_df = df[
            (df['week2HighChange'] > 0) &
            (df['monthHighChange'] < 5) &
            (df['PCT_day_change'] > 1) &
            (~df['filter5'].str.contains('BothGT2', case=False, regex=True, na=False)) &
            (df['forecast_day_PCT10_change'] > -1) &
            (df['week2LowChange'] > 2) &
            (df['lowTail'] < 1) &
            (df['PCT_day_change_pre1'] >= -1) &
            (df['PCT_day_change_pre1'] <= 2) &
            (df['PCT_day_change_pre2'] >= -1) &
            (df['PCT_day_change_pre2'] <= 3) &
            (df['weekHighChange'] > 0) &
            (df['month3HighChange'] > -15) &
            (df['monthLowChange'] < 10)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'week2HighGT0 : Avoid-GT2-And-Top5 : Avoid index up', color='G')
with col2:
    df = rb.getdf('morning-volume-breakout-buy')
    filtered_df = df
    try:
        filtered_df = df[
            (df['week2HighChange'] > -1) &
            (df['monthHighChange'] < 5) &
            (df['PCT_day_change'] > -1.5) &
            (~df['filter5'].str.contains('BothGT2', case=False, regex=True, na=False)) &
            (df['lowTail'] < 1.5) &
            (df['forecast_day_PCT10_change'] > -1) &
            (df['week2LowChange'] > 0) &
            (df['PCT_day_change_pre2'] < 2)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'week2HighGT0', color='LG')
with col3:
    df = rb.getdf('morning-volume-breakout-sell')
    filtered_df = df
    try:
        filtered_df = df[
            (df['week2LowChange'] < 0) &
            (df['monthLowChange'] > -5) &
            (df['PCT_day_change'] < -1) &
            (~df['filter5'].str.contains('BothLT2', case=False, regex=True, na=False)) &
            (df['forecast_day_PCT10_change'] < 1) &
            (df['week2HighChange'] < -2) &
            (df['highTail'] < 1) &
            (df['PCT_day_change_pre1'] >= -2) &
            (df['PCT_day_change_pre1'] <= 1) &
            (df['PCT_day_change_pre2'] >= -3) &
            (df['PCT_day_change_pre2'] <= 1) &
            (df['weekLowChange'] < 0) &
            (df['month3LowChange'] < 15) &
            (df['monthHighChange'] > -10)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'week2LowLT0 : Avoid-LT(-2)-And-Top5', color='R')
with col4:
    df = rb.getdf('morning-volume-breakout-sell')
    filtered_df = df
    try:
        filtered_df = df[
            (df['week2LowChange'] < 0) &
            (df['monthLowChange'] > -5) &
            (df['PCT_day_change'] < 1.3) &
            (~df['filter5'].str.contains('BothLT-2', case=False, regex=True, na=False)) &
            (df['highTail'] < 1.5) &
            (df['forecast_day_PCT10_change'] < 1) &
            (df['week2HighChange'] < -2) &
            (df['highTail'] < 1) &
            (df['weekHighChange'] < -1) &
            (df['PCT_day_change_pre1'] > -2) &
            (df['PCT_day_change_pre2'] > -2)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'week2LowLT0', color='LG')

col1, col2, col3, col4 = st.columns(4)
with col1:
    df = rb.getdf('morning-volume-breakout-buy')
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] > -3) &
            (df['PCT_day_change'] < 2) &
            (df['year5HighChange'] < -25) &
            (df['week2HighChange'] > -2) &
            (df['yearLowChange'] > 15) &
            (df['month3HighChange'] > -15) &
            (df['PCT_change'] > 0)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'year5HighChangeLT-30 : week2High', color='G')
with col2:
    df = rb.getdf('morning-volume-breakout-buy')
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] < 2.5) &
            (df['PCT_day_change'] > -3) &
            (df['PCT_change'] > 0) &
            (df['month3HighChange'] > -20) &
            (df['year5HighChange'] < -25) &
            (df['yearHighChange'] < -20)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'year5HighChangeLT-30 + week2High', color='LG')
with col3:
    df = rb.getdf('morning-volume-breakout-sell')
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] < -1) &
            (df['PCT_day_change'] > -3) &
            (df['yearLowChange'] > 25) &
            (df['week2LowChange'] < 2) &
            (df['yearHighChange'] < -15) &
            (df['month3LowChange'] < 15) &
            (df['PCT_change'] < 0)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'year5LowChangeGT30 : week2Low', color='LG')
with col4:
    df = rb.getdf('morning-volume-breakout-sell')
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] < -1) &
            (df['PCT_day_change'] > -2.5) &
            (df['PCT_change'] < 0) &
            (df['month3LowChange'] < 20) &
            (df['yearLowChange'] > 25) &
            (df['yearLowChange'] > 20)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'year5LowChangeGT30 + week2Low', color='LG')









