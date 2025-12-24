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
st.title('9:30 - 10:00 Last day trend : No Reversal: chartlink-1')

rb.chartlink1 = False

col1, col2, col3, col4 = st.columns(4)
with col1:
    df = rb.getdf('morning-volume-breakout-buy')
    filtered_df = df
    try:
        filtered_df = df[
            (~df['systemtime'].str.contains('09:20', case=False, na=False)) &
            (df['filter5'].str.contains('DOJI', case=False, regex=True, na=False)) &
            (df['lowTail'] < 1) &
            (df['PCT_day_change_pre2'] > -0.5) &
            (df['week2HighChange'] >= -2) &
            (df['week2HighChange'] <= 5) &
            (df['PCT_day_change_pre1'] >= 1) &
            (df['PCT_day_change_pre1'] <= 3.5) &
            (df['year5HighChange'] < -10) &
            ((df['PCT_day_change_pre1'] >= 1.7) | (df['PCT_day_change_pre2'] >= 1.7)) &
            (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False))
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'DOJI Breakout Buy', color='LG')
with col2:
    df = rb.getdf('morning-volume-breakout-buy')
    filtered_df = df
    try:
        filtered_df = df[
            (df['yearLowChange'] > 15) &
            #(df['yearHighChange'] > -35) &
            (df['lowTail'] < 1) &
            (df['PCT_day_change_pre2'] >= 2) &
            (df['PCT_day_change_pre2'] <= 4) &
            (df['PCT_day_change'] >= -2) &
            (df['PCT_day_change'] <= 0)
        ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'PctDayChangePre2 - Doji Buy', color='LG')
with col3:
    df = rb.getdf('morning-volume-breakout-sell')
    filtered_df = df
    try:
        filtered_df = df[
            (~df['systemtime'].str.contains('09:20', case=False, na=False)) &
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
    rb.render(st, filtered_df, 'DOJI Breakout Sell', color='LG')
with col4:
    df = rb.getdf('morning-volume-breakout-sell')
    filtered_df = df
    try:
        filtered_df = df[
            (df['yearHighChange'] < -15) &
            (df['highTail'] < 1) &
            (df['PCT_day_change_pre2'] >= -4) &
            (df['PCT_day_change_pre2'] <= -2) &
            (df['PCT_day_change'] >= 0) &
            (df['PCT_day_change'] <= 2)
        ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'PctDayChangePre2 - Doji Sell', color='LG')

col1, col2, col3, col4 = st.columns(4)
with col1:
    df = rb.getdf('morning-volume-breakout-buy')
    filtered_df = df
    try:
        filtered_df = df[
            (~df['systemtime'].str.contains('09:20', case=False, na=False)) &
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
            (~df['systemtime'].str.contains('09:20', case=False, na=False)) &
            (df['week2LowChange'] < 0) &
            (df['monthLowChange'] > -5) &
            (df['PCT_day_change'] >= -2.5) &
            (df['PCT_day_change'] <= 1) &
            (~df['filter5'].str.contains('BothLT-2', case=False, regex=True, na=False)) &
            (df['highTail'] < 1.5) &
            (df['forecast_day_PCT10_change'] < 1) &
            (df['week2HighChange'] < -2) &
            (df['highTail'] < 1) &
            (df['mlData'].str.contains('LT2', case=False, regex=True, na=False)) &
            (df['weekLowChange'] > 1) &
            (df['PCT_day_change_pre1'] <= 1.5) &
            (df['PCT_day_change_pre1'] >= -2.3) &
            (df['PCT_day_change_pre2'] <= 1.5) &
            (df['PCT_day_change_pre2'] >= -3) &
            (df['weekLowChange'] < 0)
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
            (~df['systemtime'].str.contains('09:20', case=False, na=False)) &
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
            (~df['systemtime'].str.contains('09:20', case=False, na=False)) &
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
            (~df['systemtime'].str.contains('09:20', case=False, na=False)) &
            (df['PCT_day_change'] > -3) &
            (df['PCT_day_change'] < 2) &
            (df['year5HighChange'] < -25) &
            (df['week2HighChange'] > -2) &
            (abs(df['week2HighChange']) > 1) &
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
    #df = rb.getdf('morning-volume-breakout-sell')
    expected_columns = list(set(df.columns))
    empty_df = pd.DataFrame(columns=expected_columns)
    rb.render(st, empty_df, 'year5LowChangeGT30 : week2Low', color='LG')
with col4:
    expected_columns = list(set(df.columns))
    empty_df = pd.DataFrame(columns=expected_columns)
    rb.render(st, empty_df, 'year5LowChangeGT30 + week2Low', color='LG')

col1, col2, col3, col4 = st.columns(4)
with col1:
    df = rb.getdf('morning-volume-breakout-buy')
    filtered_df = df
    try:
        filtered_df = df[
            (~df['systemtime'].str.contains('09:20', case=False, na=False)) &
            (df['PCT_day_change'] < 2) &
            (df['monthLowChange'] < 4) &
            (df['monthHighChange'] < -1) &
            (df['month3HighChange'] < 0) &
            (df['month3LowChange'] > 3) &
            (df['PCT_day_change_pre1'] < 2) &
            (df['year5HighChange'] < -10) &
            (df['weekLowChange'] > 1) &
            (df['week2LowChange'] > 1) &
            (df['PCT_change'] > -1.5) &
            (df['yearHighChange'] > -25)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'MorningVolumeBreakoutBuys + NearMonthLow', color='G')
with col2:
    df = rb.getdf('morning-volume-breakout-buy')
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] < 2) &
            (df['monthLowChange'] < 5) &
            (df['monthHighChange'] < -1) &
            (df['month3HighChange'] < 0) &
            (df['month3LowChange'] > 3) &
            (df['PCT_day_change_pre1'] < 2) &
            (df['year5HighChange'] < -10) &
            (df['month3HighChange'] > -10) &
            (df['weekHighChange'] > -2) &
            (df['weekHighChange'] < -1)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'MorningVolumeBreakoutBuys + NearMonthLow', color='LG')
with col3:
    df = rb.getdf('morning-volume-breakout-sell')
    filtered_df = df
    try:
        filtered_df = df[
            (~df['systemtime'].str.contains('09:20', case=False, na=False)) &
            (df['PCT_day_change'] < -1.5) &
            (df['PCT_day_change'] > -4.5) &
            (df['PCT_day_change_pre1'] > 0.5) &
            (df['monthHighChange'] > -5) &
            (df['forecast_day_PCT10_change'] < 4) &
            (df['PCT_change'] < -2) &
            (df['monthLowChange'] > 0) &
            (df['month3LowChange'] > 0)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'MorningVolumeBreakoutSells + NearMonthHigh', color='R')
with col4:
    df = rb.getdf('morning-volume-breakout-sell')
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] > -2) &
            (df['monthHighChange'] > -5) &
            (df['monthLowChange'] > 1) &
            (df['month3LowChange'] > 0) &
            (df['month3HighChange'] < -3) &
            (df['PCT_day_change_pre1'] > -2) &
            (df['year5HighChange'] < -10) &
            (df['month3LowChange'] < 10) &
            (df['weekLowChange'] < 2) &
            (df['weekLowChange'] > 1)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'MorningVolumeBreakoutSells + NearMonthHigh', color='LG')

col1, col2, col3, col4 = st.columns(4)
with col1:
    df = rb.getdf('morning-volume-breakout-buy')
    filtered_df = df
    try:
        filtered_df = df[
            (~df['systemtime'].str.contains('09:20', case=False, na=False)) &
            (df['PCT_day_change'] > 0.85) &
            (df['PCT_day_change'] < 3) &
            (df['month3LowChange'] > 0) &
            (df['monthLowChange'] > 0) &
            (df['monthHighChange'] > -10) &
            (df['PCT_day_change_pre1'] < 1) &
            (df['filter5'].str.contains('PRE1or2LT0', case=False, regex=True, na=False)) &
            (df['PCT_day_change_pre2'] > 1) &
            (df['filter5'].str.contains('PRE1or2LT0,', case=False, regex=True, na=False)) &
            (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
            (df['PCT_day_change'] < 2.5) &
            (df['forecast_day_PCT10_change'] > 0) &
            (df['monthHighChange'] > 0)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'LDayMarketUpGT1(TodayOpenedFlat) : PCTDayChangePre2GT1', color='LG')
with col2:
    df = rb.getdf('Breakout-Beey-2')
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] < 0.3) &
            (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
            (df['week2LowChange'] >= 1.5) &
            (df['week2LowChange'] <= 10) &
            (df['yearHighChange'] < -5) &
            (df['weekLowChange'] < 3) &
            (df['month3HighChange'] < -2)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'Breakout Beey 2s - Weekly High not reached - LT(-1)', color='LG')
with col3:
    df = rb.getdf('morning-volume-breakout-sell')
    filtered_df = df
    try:
        filtered_df = df[
            (~df['systemtime'].str.contains('09:20', case=False, na=False)) &
            (df['PCT_day_change'] < -0.85) &
            (df['PCT_day_change'] > -3) &
            (~df['filter'].str.contains('buy', case=False, regex=True, na=False)) &
            (df['month3HighChange'] < 0) &
            (df['monthHighChange'] < 0) &
            (df['monthLowChange'] < 10) &
            (df['PCT_day_change_pre1'] > -1) &
            (df['filter5'].str.contains('PRE1or2GT0', case=False, regex=True, na=False)) &
            (df['PCT_day_change_pre2'] < -1) &
            (~df['systemtime'].str.contains('09:20', case=False, regex=True, na=False)) &
            (df['forecast_day_PCT10_change'] < 0)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'LDayMarketDownLT-1(TodayOpenedFlat) : PCTDayChangePre2LT-1', color='LG')
with col4:
    df = rb.getdf('Breakout-Siill-2')
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] > -0.3) &
            (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
            (df['week2HighChange'] >= -10) &
            (df['week2HighChange'] <= -1.5) &
            (df['weekHighChange'] > -3) &
            (df['month3LowChange'] > 2) &
            (~df['systemtime'].str.contains('09:5', case=False, regex=True, na=False))
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'Breakout Siill 2s - Weekly Low not reached -GT(1)', color='LG')

col1, col2, col3, col4 = st.columns(4)
with col1:
    df = rb.getdf('morning-volume-breakout-buy')
    filtered_df = df
    try:
        filtered_df = df[
            (~df['systemtime'].str.contains('09:20', case=False, na=False)) &
            (df['PCT_day_change'] >= 0.85) &
            (df['PCT_day_change'] <= 2.3) &
            (df['PCT_day_change'] < 3) &
            (df['month3LowChange'] > 0) &
            (df['monthLowChange'] > 0) &
            (df['monthHighChange'] > -10) &
            (df['PCT_day_change_pre1'] < 1) &
            (df['filter5'].str.contains('PRE1or2LT0', case=False, regex=True, na=False)) &
            (~df['systemtime'].str.contains('09:5', case=False, regex=True, na=False)) &
            (~df['systemtime'].str.contains('09:4', case=False, regex=True, na=False)) &
            (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
            (df['yearHighChange'] < -10) &
            (df['month3HighChange'] > -15) &
            (df['month3LowChange'] < 12)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'LDayMarketUpGT1(TodayOpenedFlat) :_ TOP Buy', color='LG')
with col2:
    df = rb.getdf('Breakout-Beey-2')
    filtered_df = df
    try:
        filtered_df = df[
            (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
            (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False)) &
            (df['week2LowChange'] > 1.5) &
            (~df['intradaytech'].str.contains('#TOP5', case=False, regex=True, na=False)) &
            (~df['systemtime'].str.contains('09:40', case=False, regex=True, na=False)) &
            (df['week2LowChange'] < 10)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'Breakout Beey 2s - Weekly High not reached - 09:45', color='LG')
with col3:
    df = rb.getdf('morning-volume-breakout-sell')
    filtered_df = df
    try:
        filtered_df = df[
            (~df['systemtime'].str.contains('09:20', case=False, na=False)) &
            (df['PCT_day_change'] >= -2.3) &
            (df['PCT_day_change'] <= -0.85) &
            (df['PCT_day_change'] > -3) &
            (~df['filter'].str.contains('buy', case=False, regex=True, na=False)) &
            (df['monthHighChange'] < 0) &
            (df['monthLowChange'] < 10) &
            (df['PCT_day_change_pre1'] > -1) &
            (df['filter5'].str.contains('PRE1or2GT0', case=False, regex=True, na=False)) &
            (~df['systemtime'].str.contains('09:20:00', case=False, regex=True, na=False)) &
            (df['forecast_day_PCT10_change'] < 0) &
            (df['month3HighChange'] < -5)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'LDayMarketDownLT-1(TodayOpenedFlat) : _TOP Sell', color='LG')
with col4:
    df = rb.getdf('Breakout-Siill-2')
    filtered_df = df
    try:
        filtered_df = df[
            (~df['systemtime'].str.contains('09:35', case=False, regex=True, na=False)) &
            (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
            (df['week2HighChange'] < -1.5) &
            (df['week2HighChange'] > -10) &
            (~df['systemtime'].str.contains('09:5', case=False, regex=True, na=False))
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'Breakout Siill 2s - Weekly Low not reached -GT(1)- 9:45', color='LG')

col1, col2, col3, col4 = st.columns(4)
with col1:
    df = rb.getintersectdf('morning-volume-breakout-buy', 'breakoutMH')
    expected_columns = list(set(df.columns))
    empty_df = pd.DataFrame(columns=expected_columns)
    filtered_df = df
    try:
        filtered_df = df[
            (~df['systemtime'].str.contains('09:20', case=False, na=False)) &
            ((df['PCT_day_change'] < 2) | (df['week2LowChange'] < 7)) &
            (df['PCT_day_change_pre1'] > -1) &
            (df['PCT_day_change_pre2'] > -1) &
            (df['PCT_day_change_pre1'] < 2)
            ]
    except KeyError as e:
        print("")
    if len(filtered_df) <= 3:
        rb.render(st, filtered_df, 'morning-volume-breakout-buy + breakoutMH', color='LG')
    else:
        rb.render(st, empty_df, 'morning-volume-breakout-buy + breakoutMH', color='LG')
with col2:
    df = rb.getintersectdf('morning-volume-breakout-buy', 'breakoutM2H')
    expected_columns = list(set(df.columns))
    empty_df = pd.DataFrame(columns=expected_columns)
    filtered_df = df
    try:
        filtered_df = df[
            ((df['PCT_day_change'] < 2) | (df['week2LowChange'] < 7)) &
            (df['PCT_day_change_pre1'] > -1) &
            (df['PCT_day_change_pre2'] > -1) &
            (df['PCT_day_change_pre1'] < 2)
            ]
    except KeyError as e:
        print("")
    if len(filtered_df) <= 3:
        rb.render(st, filtered_df, 'morning-volume-breakout-buy + breakoutM2H', color='LG')
    else:
        rb.render(st, empty_df, 'morning-volume-breakout-buy + breakoutM2H', color='LG')
with col3:
    df = rb.getintersectdf('morning-volume-breakout-sell', 'breakoutML')
    expected_columns = list(set(df.columns))
    empty_df = pd.DataFrame(columns=expected_columns)
    filtered_df = df
    try:
        filtered_df = df[
            (~df['systemtime'].str.contains('09:20', case=False, na=False)) &
            ((df['PCT_day_change'] > -2) | (df['week2HighChange'] > -7)) &
            (df['PCT_day_change_pre1'] < 1) &
            (df['PCT_day_change_pre2'] < 1) &
            (df['PCT_day_change_pre1'] > -2) &
            df['month3LowChange'] > -0.5
            ]
    except KeyError as e:
        print("")
    if len(filtered_df) <= 3:
        rb.render(st, filtered_df, 'morning-volume-breakout-sell + breakoutML', color='LG')
    else:
        rb.render(st, empty_df, 'morning-volume-breakout-sell + breakoutML', color='LG')
with col4:
    df = rb.getintersectdf('morning-volume-breakout-sell', 'breakoutM2L')
    expected_columns = list(set(df.columns))
    empty_df = pd.DataFrame(columns=expected_columns)
    filtered_df = df
    try:
        filtered_df = df[
            ((df['PCT_day_change'] > -2) | (df['week2HighChange'] > -7)) &
            (df['PCT_day_change_pre1'] < 1) &
            (df['PCT_day_change_pre2'] < 1) &
            (df['PCT_day_change_pre1'] > -2) &
            df['month3LowChange'] > -0.5
            ]
    except KeyError as e:
        print("")
    if len(filtered_df) <= 3:
        rb.render(st, filtered_df, 'morning-volume-breakout-sell + breakoutM2L', color='LG')
    else:
        rb.render(st, empty_df, 'morning-volume-breakout-sell + breakoutM2L', color='LG')





