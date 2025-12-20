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
            (df['PCT_day_change'] < -1) &
            (df['PCT_day_change_pre1'] < -1) &
            (~df['systemtime'].str.contains('09:2', case=False, na=False)) &
            (~df['systemtime'].str.contains('09:3', case=False, na=False)) &
            (~df['systemtime_merged'].str.contains('09:', case=False, na=False))
        ]
    except KeyError as e:
        print("")
    rb.render(st, filtered_df, 'week2lh-not-reached + Crossed Day Low', column_order=rb.column_order_p, color='LG')


