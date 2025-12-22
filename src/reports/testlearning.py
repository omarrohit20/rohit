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
st.title('Learning')

col1, col2 = st.columns(2)
with col1:
    df = rb.getintersectdf('week2lh-not-reached','crossed-day-high')
    expected_columns = list(set(df.columns))
    empty_df = pd.DataFrame(columns=expected_columns)
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] > -1.3) & (df['PCT_day_change'] < 0.7) &
            ((abs(df['PCT_day_change_pre1']) > 1) | (abs(df['PCT_day_change_pre2']) > 1)) &
            (~df['systemtime'].str.contains('09:2', case=False, na=False)) &
            (~df['systemtime'].str.contains('09:3', case=False, na=False)) &
            (~df['systemtime_merged'].str.contains('09:', case=False, na=False))
        ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'week2lh-not-reached + Crossed Day High', column_order=rb.column_order_p, color='LG')
with col2:
    df = rb.getintersectdf('week2lh-not-reached','crossed-day-low')
    expected_columns = list(set(df.columns))
    empty_df = pd.DataFrame(columns=expected_columns)
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] > -0.7) & (df['PCT_day_change'] < 1.3) &
            ((abs(df['PCT_day_change_pre1']) > 1) | (abs(df['PCT_day_change_pre2']) > 1)) &
            (~df['systemtime'].str.contains('09:2', case=False, na=False)) &
            (~df['systemtime'].str.contains('09:3', case=False, na=False)) &
            (~df['systemtime_merged'].str.contains('09:', case=False, na=False))
        ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'week2lh-not-reached + Crossed Day Low', column_order=rb.column_order_p, color='LG')

col1, col2 = st.columns(2)
with col1:
    df = rb.getintersectdf('week2lh-not-reached','crossed-day-high')
    expected_columns = list(set(df.columns))
    empty_df = pd.DataFrame(columns=expected_columns)
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] > 1) &
            (df['PCT_day_change_pre1'] > 1) &
            (~df['systemtime'].str.contains('09:2', case=False, na=False)) &
            (~df['systemtime'].str.contains('09:3', case=False, na=False)) &
            (~df['systemtime'].str.contains('09:', case=False, na=False)) 
            #(~df['systemtime_merged'].str.contains('09:', case=False, na=False))
        ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'week2lh-not-reached + Crossed Day High', column_order=rb.column_order_p, color='LG')
with col2:
    df = rb.getintersectdf('week2lh-not-reached','crossed-day-low')
    expected_columns = list(set(df.columns))
    empty_df = pd.DataFrame(columns=expected_columns)
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] < -1) &
            (df['PCT_day_change_pre1'] < -1) &
            (~df['systemtime'].str.contains('09:2', case=False, na=False)) &
            (~df['systemtime'].str.contains('09:3', case=False, na=False)) &
            (~df['systemtime'].str.contains('09:', case=False, na=False)) 
            #(~df['systemtime_merged'].str.contains('09:', case=False, na=False))
        ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'week2lh-not-reached + Crossed Day Low', column_order=rb.column_order_p, color='LG')


col1, col2 = st.columns(2)
with col1:
    df = rb.getintersectdf('week2lh-not-reached','crossed-day-high')
    expected_columns = list(set(df.columns))
    empty_df = pd.DataFrame(columns=expected_columns)
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] < -1) &
            #(df['PCT_day_change_pre1'] < -1) &
            (~df['systemtime'].str.contains('09:2', case=False, na=False)) &
            (~df['systemtime'].str.contains('09:3', case=False, na=False)) &
            (~df['systemtime'].str.contains('09', case=False, na=False)) 
            #(~df['systemtime_merged'].str.contains('09:', case=False, na=False))
        ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'week2lh-not-reached + Crossed Day High', column_order=rb.column_order_p, color='LG')
with col2:
    df = rb.getintersectdf('week2lh-not-reached','crossed-day-low')
    expected_columns = list(set(df.columns))
    empty_df = pd.DataFrame(columns=expected_columns)
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] > 1) &
            #(df['PCT_day_change_pre1'] < -1) &
            (~df['systemtime'].str.contains('09:2', case=False, na=False)) &
            (~df['systemtime'].str.contains('09:3', case=False, na=False)) &
            (~df['systemtime'].str.contains('09', case=False, na=False)) 
            #(~df['systemtime_merged'].str.contains('09:', case=False, na=False))
        ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'week2lh-not-reached + Crossed Day Low', column_order=rb.column_order_p, color='LG')


col1, col3 = st.columns(2)
with col1:
    df = rb.getdf('morning-volume-breakout-buy')
    filtered_df = df
    try:
        filtered_df = df[
            (~df['systemtime'].str.contains('09:2', case=False, na=False)) &
            #(~df['systemtime'].str.contains('09:3', case=False, na=False)) &
            (df['mlData'].str.contains("0@@CROSSED2") | df['mlData'].str.contains("0@@SUPER"))
        ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'morning-volume-breakout-buy', color='G', height=300)
with col3:
    df = rb.getdf('morning-volume-breakout-sell')
    filtered_df = df
    try:
        filtered_df = df[
            (~df['systemtime'].str.contains('09:2', case=False, na=False)) &
            #(~df['systemtime'].str.contains('09:3', case=False, na=False)) &
            (df['mlData'].str.contains("0@@CROSSED2") | df['mlData'].str.contains("0@@SUPER"))
        ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'morning-volume-breakout-sell', color='R', height=300)

col1, col2, col3, col4 = st.columns(4)
with col1:
    df = rb.getdf('Breakout-Buy-after-10')
    rb.render(st, df, 'TodayUpOrIndexStockUpGT0.5 : Breakout Buy after 10', color='G', height=200)
with col2:
    df = rb.getdf('1-Bbuyy-morningUp-downConsolidation')
    rb.render(st, df, 'Only one dip: 1-Bbuyy-morningUp-downConsolidation', color='G', height=200)
with col3:
    df = rb.getdf('Breakout-Sell-after-10')
    rb.render(st, df, 'TodayDownOrIndexStockDownLT-0.5 : Breakout Sell after 10', color='R', height=200)
with col4:
    df = rb.getdf('1-Sselll-morningDown-upConsolidation')
    rb.render(st, df, 'Only one up: 1-Sselll-morningDown-upConsolidation', color='R', height=200)


col1, col2, col3, col4 = st.columns(4)
with col1:
    df = rb.getdf('crossed-day-high')
    filtered_df = df
    try:
        filtered_df = df[
            (~df['systemtime'].str.contains('09:2', case=False, na=False)) &
            (~df['systemtime'].str.contains('09:3', case=False, na=False)) &
            (~df['systemtime'].str.contains('09:4', case=False, na=False)) &
            (df['PCT_day_change'] > -1) & (df['PCT_day_change'] < 1) &
            (df['PCT_day_change_pre1'] > 0.5) & (df['PCT_day_change_pre1'] < 1.5)
        ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'Crossed Day Highs', column_order=rb.column_order_p, color='G')
with col2:
    df = rb.getdf('crossed-day-high')
    filtered_df = df
    rb.render(st, filtered_df, 'Crossed Day Highs', color='LG')
with col3:
    df = rb.getdf('crossed-day-low')
    filtered_df = df
    try:
        filtered_df = df[
            (~df['systemtime'].str.contains('09:2', case=False, na=False)) &
            (~df['systemtime'].str.contains('09:3', case=False, na=False)) &
            (~df['systemtime'].str.contains('09:4', case=False, na=False)) &
            (df['PCT_day_change'] > -1) & (df['PCT_day_change'] < 1) &
            (df['PCT_day_change_pre1'] < -0.5) & (df['PCT_day_change_pre1'] > -1.5)
        ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'Crossed Day Lows', color='LG')
with col4:
    df = rb.getdf('crossed-day-low')
    filtered_df = df
    rb.render(st, filtered_df, 'Crossed Day Lows', color='LG')


col1, col2, col3, col4 = st.columns(4)
with col1:
    df = rb.getintersectdf_ml('regressionhigh', 'regressionlow')
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] < 4) &
            (df['kNeighboursValue_reg_merged'] > 3) &
            (df['mlpValue_reg_merged'] > 3) &
            ((df['kNeighboursValue_reg'] > 2) | (df['mlpValue_reg'] > 2))
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'MLBUY', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='G')
with col2:
    df = rb.getintersectdf_ml('regressionhigh', 'regressionlow')
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] < 4) &
            (df['kNeighboursValue_reg'] > 2) &
            (df['mlpValue_reg'] > 2)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'MLBUY', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='LG')
with col3:
    df = rb.getintersectdf_ml('regressionlow', 'regressionhigh')
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] > -4) &
            (df['kNeighboursValue_reg_merged'] < -3) &
            (df['mlpValue_reg_merged'] < -3) &
            ( (df['kNeighboursValue_reg'] < -2) | (df['mlpValue_reg'] < -2))
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'MLSELL', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='R')
with col4:
    df = rb.getintersectdf_ml('regressionlow', 'regressionhigh')
    filtered_df = df
    try:
        filtered_df = df[
            (df['PCT_day_change'] > -4) &
            (df['kNeighboursValue_reg_merged'] < -2) &
            (df['mlpValue_reg_merged'] < -2)
            ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'MLSELL', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='LG')
