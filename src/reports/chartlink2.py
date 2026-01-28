# Create a streamlit app that shows the mongodb data
from streamlit_autorefresh import st_autorefresh
import streamlit as st
import rbase as rb
import pandas as pd

# Run the autorefresh approximately every 30000 milliseconds (30 seconds)

def main():
    st_autorefresh(interval=30000, key="data_refresher")

    # setting the screen size (ignore if already set by index)
    try:
        st.set_page_config(layout="wide",
                           page_title="Dashboard",
                           initial_sidebar_state="expanded",)
    except Exception:
        pass

    # main title
    st.title('chartlink2')

    col0, col1, col2, col00, col3, col4 = st.columns(6)
    with col0:
        df = rb.getdf('supertrend-morning-buy')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False)) &
                ((df['PCT_day_change'] < 0.5) | (df['PCT_day_change_pre1'] < 0.5) | (df['PCT_day_change_pre2'] < 0.5)) &
                ((df['PCT_day_change'] < 2) | (df['PCT_day_change_pre1'] < 2)) &
                ((df['PCT_day_change'] > -0.3) | (df['PCT_day_change_pre2'] > -0.3)) &
                ((df['yearHighChange'] < 0) | (df['monthHighChange'] < 0) | (df['forecast_day_PCT10_change'] < -6)) &
                (
                    ((df['systemtime'].str.contains('9:', case=False, regex=True, na=False)) & (df['forecast_day_PCT10_change'] > 2) & (df['forecast_day_PCT10_change'] < 7)) |
                    ((df['forecast_day_PCT10_change'] < -6) & (df['forecast_day_PCT5_change'] > 0)) |
                    ((df['systemtime'].str.contains('11:', case=False, regex=True, na=False)) & (df['forecast_day_PCT10_change'] <= -0.5))
                )
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Supertrend Morning Buy', color='LG', renderf10buy=True)
    with col1:
        df = rb.getdf('09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)')
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (((df['PCT_day_change'] < 2) | (df['PCT_day_change_pre1'] < 2)) &
                    ((df['PCT_day_change'] < 1.5) & (df['PCT_change'] < 1.5)) &
                    ((df['forecast_day_PCT10_change'] < 1) | (df['forecast_day_PCT5_change'] < 1) | (df['forecast_day_PCT7_change'] < 1) ) &
                    (df['forecast_day_PCT10_change'] > -2) & 
                    (df['forecast_day_PCT7_change'] > -1) & 
                    (df['forecast_day_PCT5_change'] > -1) & 
                    (df['forecast_day_PCT10_change'] < 3))
                    |
                    (((df['PCT_day_change'] < 0.5) | (df['PCT_day_change_pre1'] < 0.5) | (df['PCT_day_change_pre2'] < 0.5)) &
                    ((df['PCT_day_change'] > 0.5) | (abs(df['PCT_day_change_pre1']) > 0.5) | (abs(df['PCT_day_change_pre2']) > 0.5)) &
                    ((df['PCT_day_change'] < 2) | (df['PCT_day_change_pre1'] < 2)) &
                    ((df['PCT_day_change'] > -0.3) | (df['PCT_day_change_pre2'] > -0.3)) &
                    ((df['yearHighChange'] < 0) | (df['monthHighChange'] < 0) | (df['forecast_day_PCT10_change'] < -6)) &
                    (
                        ((df['systemtime'].str.contains('9:', case=False, regex=True, na=False)) & (df['forecast_day_PCT10_change'] > 2) & (df['forecast_day_PCT10_change'] < 15)) |
                        (((df['forecast_day_PCT10_change'] < -6) & (df['forecast_day_PCT5_change'] > 0))) |
                        ((df['systemtime'].str.contains('11:', case=False, regex=True, na=False)) & (df['forecast_day_PCT10_change'] <= -0.5))
                    ))
                )
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Crossed 2 Day Highs', color='LG', renderf10buy=True)
    with col2:
        df = rb.getdf('crossed-day-high')
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (~(df['systemtime'].str.contains('9:', case=False, regex=True, na=False)) & 
                    ((df['PCT_day_change'] < 1.5) & (df['PCT_change'] < 1.5)) &
                    ((((df['forecast_day_PCT5_change'] < -1) | (df['forecast_day_PCT7_change'] < -1)))
                     | (df['forecast_day_PCT5_change'] > 3)
                     ) &
                    (df['forecast_day_PCT10_change'] > -2) & 
                    (df['forecast_day_PCT7_change'] > -1) & 
                    (df['forecast_day_PCT5_change'] > -1) & 
                    (df['forecast_day_PCT10_change'] < 3))
                    | 
                    (((df['PCT_day_change'] < 0.5) | (df['PCT_day_change_pre1'] < 0.5) | (df['PCT_day_change_pre2'] < 0.5)) &
                    ((df['PCT_day_change'] > 0.5) | (abs(df['PCT_day_change_pre1']) > 0.5) | (abs(df['PCT_day_change_pre2']) > 0.5)) &
                    ((df['PCT_day_change'] < 2) | (df['PCT_day_change_pre1'] < 2)) &
                    ((df['PCT_day_change'] > -0.3) | (df['PCT_day_change_pre2'] > -0.3)) &
                    ((df['yearHighChange'] < 0) | (df['monthHighChange'] < 0) | (df['forecast_day_PCT10_change'] < -6)) &
                    (
                        ((df['systemtime'].str.contains('9:', case=False, regex=True, na=False)) & (df['forecast_day_PCT10_change'] > 2) & (df['forecast_day_PCT10_change'] < 7) & (df['yearHighChange'] <= -10) & (df['yearHighChange'] >= -70) & (df['PCT_day_change'] <= 1.5)) |
                        (((df['forecast_day_PCT10_change'] < -6) & (df['forecast_day_PCT5_change'] > 0)))
                    )
                    )
                )
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Crossed Day Highs', color='LG', renderf10buy=True)
    with col00:
        df = rb.getdf('supertrend-morning-sell')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('9:', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False)) &
                ((df['PCT_day_change'] > -0.5) | (df['PCT_day_change_pre1'] > -0.5) | (df['PCT_day_change_pre2'] > -0.5)) &
                ((df['PCT_day_change'] > -2) | (df['PCT_day_change_pre1'] > -2)) &
                ((df['PCT_day_change'] < 0.3) | (df['PCT_day_change_pre2'] < 0.3)) &
                ((df['yearLowChange'] > 0) | (df['monthLowChange'] > 0) | (df['forecast_day_PCT10_change'] > 6)) &
                (
                    ((df['systemtime'].str.contains('9:', case=False, regex=True, na=False)) & (df['forecast_day_PCT10_change'] < -2) & (df['forecast_day_PCT10_change'] > -7)) |
                    (((df['forecast_day_PCT10_change'] > 6) & (df['forecast_day_PCT5_change'] < 0))) |
                    ((df['systemtime'].str.contains('11:', case=False, regex=True, na=False)) & (df['forecast_day_PCT10_change'] >= 0.5))
                )
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Supertrend Morning Sell', color='LG', renderf10sell=True)
    with col3:
        df = rb.getdf('09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)')
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (~(df['systemtime'].str.contains('9:', case=False, regex=True, na=False)) & 
                    ((df['PCT_day_change'] > -1.5) & (df['PCT_day_change_pre1'] > -1.5)) &
                    ((df['forecast_day_PCT5_change'] > -1) | (df['forecast_day_PCT5_change'] > -1) | (df['forecast_day_PCT7_change'] > -1)) &
                    (df['forecast_day_PCT10_change'] < 2) & 
                    (df['forecast_day_PCT7_change'] < 1) & 
                    (df['forecast_day_PCT5_change'] < 1) & 
                    (df['forecast_day_PCT10_change'] > -3))
                    | 
                    ((~df['systemtime'].str.contains('9:', case=False, regex=True, na=False)) &
                    ((df['PCT_day_change'] > -0.5) | (df['PCT_day_change_pre1'] > -0.5) | (df['PCT_day_change_pre2'] > -0.5)) &
                    ((df['PCT_day_change'] < -0.5) | (abs(df['PCT_day_change_pre1']) > 0.5) | (abs(df['PCT_day_change_pre2']) > 0.5)) &
                    ((df['PCT_day_change'] > -2) | (df['PCT_day_change_pre1'] > -2)) &
                    ((df['PCT_day_change'] < 0.3) | (df['PCT_day_change_pre2'] < 0.3)) &
                    ((df['yearLowChange'] > 0) | (df['monthLowChange'] > 0) | (df['forecast_day_PCT10_change'] > 6)) &
                    (
                        ((df['systemtime'].str.contains('9:', case=False, regex=True, na=False)) & (df['forecast_day_PCT10_change'] < -2) & (df['forecast_day_PCT10_change'] > -15)) |
                        (((df['forecast_day_PCT10_change'] > 6) & (df['forecast_day_PCT5_change'] < 0))) |
                        ((df['systemtime'].str.contains('11:', case=False, regex=True, na=False)) & (df['forecast_day_PCT10_change'] >= 0.5))
                    ))
                )
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Crossed 2 Day Lows', color='LG', renderf10sell=True)
    with col4:
        df = rb.getdf('crossed-day-low')
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (~(df['systemtime'].str.contains('9:', case=False, regex=True, na=False)) &
                    ((df['PCT_day_change'] > -1.5) & (df['PCT_change'] > -1.5)) &
                    ((((df['forecast_day_PCT5_change'] > 1) | (df['forecast_day_PCT7_change'] > 1)))
                     | (df['forecast_day_PCT5_change'] < -3)
                    ) &
                    (df['forecast_day_PCT10_change'] < 2) & 
                    (df['forecast_day_PCT7_change'] < 1) & 
                    (df['forecast_day_PCT5_change'] < 1) & 
                    (df['forecast_day_PCT10_change'] > -3))
                    | 
                    ((~df['systemtime'].str.contains('9:', case=False, regex=True, na=False)) &
                    ((df['PCT_day_change'] > -0.5) | (df['PCT_day_change_pre1'] > -0.5) | (df['PCT_day_change_pre2'] > -0.5)) &
                    ((df['PCT_day_change'] < -0.5) | (abs(df['PCT_day_change_pre1']) > 0.5) | (abs(df['PCT_day_change_pre2']) > 0.5)) &
                    ((df['PCT_day_change'] > -2) | (df['PCT_day_change_pre1'] > -2)) &
                    ((df['PCT_day_change'] < 0.3) | (df['PCT_day_change_pre2'] < 0.3)) &
                    ((df['yearLowChange'] > 0) | (df['monthLowChange'] > 0) | (df['forecast_day_PCT10_change'] > 6)) &
                    (
                        ((df['systemtime'].str.contains('9:', case=False, regex=True, na=False)) & (df['forecast_day_PCT10_change'] < -2) & (df['forecast_day_PCT10_change'] > -7) & (df['yearLowChange'] > 10) & (df['yearLowChange'] <= 70) & (df['PCT_day_change'] >= -1.5)) |
                        (((df['forecast_day_PCT10_change'] > 6) & (df['forecast_day_PCT5_change'] < 0))) 
                    ))
                )
            ]
                
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Crossed Day Lows', color='LG', renderf10sell=True)


    col0, col1, col2, col00, col3, col4 = st.columns(6)
    with col0:
        df = rb.getdf('supertrend-morning-buy')
        filtered_df = df
        try:
            filtered_df = df[
                (abs(df['week2LowChange']) > 1) &
                (~df['systemtime'].str.contains('09:', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:0', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False)) &
                ((df['PCT_day_change'] < 2) & (df['PCT_day_change_pre1'] < 2)) &
                ((df['forecast_day_PCT7_change'] < 3) & (df['forecast_day_PCT5_change'] < 3)) &
                (df['forecast_day_PCT7_change'] > -2) & (df['forecast_day_PCT5_change'] > -2) &
                ((df['forecast_day_PCT10_change'] < 2) | (df['forecast_day_PCT10_change'] > 6)) &
                ((df['PCT_day_change'] > 0) | (df['PCT_day_change_pre1'] > 0) | (df['PCT_day_change_pre2'] > 0))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Supertrend Morning Buy', color='LG', renderf10buy=True)
    with col1:
        df = rb.getdf('09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)')
        filtered_df = df
        try:
            filtered_df = df[
                (
                (df['PCT_day_change'] < 1) &
                ((df['PCT_day_change'] <= -1.5) | (df['PCT_day_change_pre1'] <= -1.5) | (df['PCT_day_change_pre1'] <= -1.5)) &
                ((df['PCT_day_change'] < 2) | (df['PCT_day_change_pre1'] < 2)) &
                (df['forecast_day_PCT10_change'] < -3.3) & (df['forecast_day_PCT10_change'] > -8) &
                ((df['forecast_day_PCT5_change'] < 0) | (df['forecast_day_PCT7_change'] < 0)))
                |
                ((~df['systemtime'].str.contains('09:', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:0', case=False, regex=True, na=False)) &
                ((df['PCT_day_change'] < 2) & (df['PCT_day_change_pre1'] < 2)) &
                ((df['forecast_day_PCT7_change'] < 3) & (df['forecast_day_PCT5_change'] < 3)) &
                ((df['forecast_day_PCT10_change'] > -3) & (df['forecast_day_PCT7_change'] > -3) & (df['forecast_day_PCT5_change'] > -3)) &
                ((df['PCT_day_change'] > 0) | (df['PCT_day_change_pre1'] > 0)) &
                ((df['PCT_day_change_pre2'] > 0) | (df['PCT_day_change_pre1'] > 0)) &
                ((df['month3LowChange'] > 0)))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Crossed 2 Day Highs', color='LG', renderf10buy=True)
    with col2:
        df = rb.getdf('crossed-day-high')
        filtered_df = df
        try:
            filtered_df = df[
                (
                (~df['systemtime'].str.contains('9:', case=False, regex=True, na=False)) & 
                #(~df['systemtime'].str.contains('11:', case=False, regex=True, na=False)) &
                (df['PCT_day_change'] < 1) &
                ((df['PCT_day_change'] <= -1.5) | (df['PCT_day_change_pre1'] <= -1.5) | (df['PCT_day_change_pre1'] <= -1.5)) &
                ((df['PCT_day_change'] < 2) | (df['PCT_day_change_pre1'] < 2)) &
                (df['forecast_day_PCT10_change'] < -3.3) & (df['forecast_day_PCT10_change'] > -8) &
                ((df['forecast_day_PCT5_change'] < 0) | (df['forecast_day_PCT7_change'] < 0))
                )
                |
                (
                (abs(df['week2LowChange']) > 1) &
                (~df['systemtime'].str.contains('09:', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:0', case=False, regex=True, na=False)) &
                ((df['PCT_day_change'] < 2) & (df['PCT_day_change_pre1'] < 2)) &
                ((df['forecast_day_PCT7_change'] < 3) & (df['forecast_day_PCT5_change'] < 3)) &
                ((df['forecast_day_PCT10_change'] > -3) & (df['forecast_day_PCT7_change'] > -2) & (df['forecast_day_PCT5_change'] > -2)) &
                (df['forecast_day_PCT10_change'] < 2) &
                ((df['PCT_day_change'] > 0) | (df['PCT_day_change_pre1'] > 0)) &
                ((df['PCT_day_change_pre2'] > 0) | (df['PCT_day_change_pre1'] > 0)) &
                ((df['month3LowChange'] > 0))
                )
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Crossed Day Highs', color='LG', renderf10buy=True)
    with col00:
        df = rb.getdf('supertrend-morning-sell')
        filtered_df = df
        try:
            filtered_df = df[
                (abs(df['week2HighChange']) > 1) &
                (~df['systemtime'].str.contains('09:', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:0', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False)) &
                ((df['PCT_day_change'] > -2) & (df['PCT_day_change_pre1'] > -2)) &
                ((df['forecast_day_PCT7_change'] > -3) & (df['forecast_day_PCT5_change'] > -3))  &
                (df['forecast_day_PCT7_change'] < 2) & (df['forecast_day_PCT5_change'] < 2) &
                ((df['forecast_day_PCT10_change'] > -2) | (df['forecast_day_PCT10_change'] < -6)) &
                ((df['PCT_day_change'] < 0) | (df['PCT_day_change_pre1'] < 0) | (df['PCT_day_change_pre2'] < 0))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Supertrend Morning Sell', color='LG', renderf10sell=True)
    with col3:
        df = rb.getdf('09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] > -1) &
                ((df['PCT_day_change'] >= 1.5) | (df['PCT_day_change_pre1'] >= 1.5) | (df['PCT_day_change_pre1'] >= 1.5)) &
                (((df['PCT_day_change'] > -2) | (df['PCT_day_change_pre1'] > -2)) &
                (df['forecast_day_PCT10_change'] > 3.3) & (df['forecast_day_PCT10_change'] < 8) &
                ((df['forecast_day_PCT5_change'] > 0) | (df['forecast_day_PCT7_change'] > 0)) &
                ~(df['systemtime'].str.contains('9:', case=False, regex=True, na=False)))
                |
                ((~df['systemtime'].str.contains('09:', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:0', case=False, regex=True, na=False)) &
                ((df['PCT_day_change'] > -2) & (df['PCT_day_change_pre1'] > -2)) &
                ((df['forecast_day_PCT7_change'] > -3) & (df['forecast_day_PCT5_change'] > -3))  &
                ((df['forecast_day_PCT10_change'] < 3) &(df['forecast_day_PCT7_change'] < 3) & (df['forecast_day_PCT5_change'] < 3)) &
                ((df['PCT_day_change'] < 0) | (df['PCT_day_change_pre1'] < 0)) &
                ((df['PCT_day_change_pre2'] < 0) | (df['PCT_day_change_pre1'] < 0)) &
                ((df['month3HighChange'] < 0)))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Crossed 2 Day Lows', color='LG', renderf10sell=True)
    with col4:
        df = rb.getdf('crossed-day-low')
        filtered_df = df
        try:
            filtered_df = df[
                (
                (~df['systemtime'].str.contains('9:', case=False, regex=True, na=False)) &
                #(~df['systemtime'].str.contains('11:', case=False, regex=True, na=False)) &
                (df['PCT_day_change'] > -1) &
                ((df['PCT_day_change'] >= 1.5) | (df['PCT_day_change_pre1'] >= 1.5) | (df['PCT_day_change_pre1'] >= 1.5)) &
                ((df['PCT_day_change'] > -2) | (df['PCT_day_change_pre1'] > -2)) &
                (df['forecast_day_PCT10_change'] > 3.3) & (df['forecast_day_PCT10_change'] < 8) &
                ((df['forecast_day_PCT5_change'] > 0) | (df['forecast_day_PCT7_change'] > 0))
                )
                |
                (
                (abs(df['week2HighChange']) > 1) &
                (~df['systemtime'].str.contains('09:', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:0', case=False, regex=True, na=False)) &
                ((df['PCT_day_change'] > -2) & (df['PCT_day_change_pre1'] > -2)) &
                ((df['forecast_day_PCT7_change'] > -3) & (df['forecast_day_PCT5_change'] > -3)) &
                ((df['forecast_day_PCT10_change'] < 3) & (df['forecast_day_PCT7_change'] < 2) & (df['forecast_day_PCT5_change'] < 2)) &
                (df['forecast_day_PCT10_change'] > -2) &
                ((df['PCT_day_change'] < 0) | (df['PCT_day_change_pre1'] < 0)) &
                ((df['PCT_day_change_pre2'] < 0) | (df['PCT_day_change_pre1'] < 0)) &
                ((df['month3HighChange'] < 0))
                )
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Crossed Day Lows', color='LG', renderf10sell=True)


    col0, col1, col2, col3, col4, col5 = st.columns(6)
    with col0:
        df = rb.getdf('supertrend-morning-buy')
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (df['PCT_day_change'] < 1.3) &
                    (df['PCT_day_change'] > -1.3) &
                    ((df['forecast_day_PCT10_change'] > 7) & (df['forecast_day_PCT7_change'] > 7) & (df['forecast_day_PCT5_change'] > 7) & ((df['forecast_day_PCT10_change'] > 10) | (df['forecast_day_PCT7_change'] > 10) | (df['forecast_day_PCT5_change'] > 10)))
                )
                |
                (
                    (df['PCT_day_change'] < 1.5) &
                    #((df['PCT_day_change'] > 1) | (df['PCT_day_change_pre1'] > 1) | (df['PCT_day_change_pre2'] > 1)) &
                    ((df['PCT_day_change'] > -1) & (df['PCT_day_change_pre1'] > -1) & (df['PCT_day_change_pre2'] > -1)) &
                    ((df['forecast_day_PCT10_change'] > -2) & (df['forecast_day_PCT10_change'] < 1) & (df['forecast_day_PCT7_change'] > -2) & (df['forecast_day_PCT7_change'] < 2) & (df['forecast_day_PCT5_change'] > -2) & (df['forecast_day_PCT5_change'] < 2))
                )
                |
                (
                    (~df['systemtime'].str.contains('09:', case=False, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                    (df['PCT_day_change'] < 1.3) &
                    (df['PCT_day_change'] > -1.3) &
                    ((df['forecast_day_PCT10_change'] > 7)) 
                )
                |
                (
                    ((df['PCT_day_change'] < 1) & (df['PCT_day_change_pre1'] < 1) & (df['PCT_day_change_pre2'] < 1)) &
                    ((df['forecast_day_PCT10_change'] < -7))
                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Supertrend Morning Buy', color='LG', renderf10buy00=True)
    with col1:
        df = rb.getdf('09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)')
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (df['PCT_day_change'] < 1.3) &
                    (df['PCT_day_change'] > -1.3) &
                    ((df['forecast_day_PCT10_change'] > 7) & (df['forecast_day_PCT7_change'] > 7) & (df['forecast_day_PCT5_change'] > 7) & ((df['forecast_day_PCT10_change'] > 10) | (df['forecast_day_PCT7_change'] > 10) | (df['forecast_day_PCT5_change'] > 10)))
                )
                |
                (
                    (df['PCT_day_change'] < 1.5) &
                    #((df['PCT_day_change'] > 1) | (df['PCT_day_change_pre1'] > 1) | (df['PCT_day_change_pre2'] > 1)) &
                    #((df['PCT_day_change'] > -1) & (df['PCT_day_change_pre1'] > -1) & (df['PCT_day_change_pre2'] > -1)) &
                    ((df['forecast_day_PCT10_change'] > -2) & (df['forecast_day_PCT10_change'] < 1) & (df['forecast_day_PCT7_change'] > -2) & (df['forecast_day_PCT7_change'] < 2) & (df['forecast_day_PCT5_change'] > -2) & (df['forecast_day_PCT5_change'] < 2))
                )
                |
                (
                    (~df['systemtime'].str.contains('09:', case=False, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                    (df['PCT_day_change'] < 1.3) &
                    (df['PCT_day_change'] > -1.3) &
                    ((df['forecast_day_PCT10_change'] > 7)) 
                )
                |
                (
                    ((df['PCT_day_change'] < 1) & (df['PCT_day_change_pre1'] < 1) & (df['PCT_day_change_pre2'] < 1)) &
                    (df['forecast_day_PCT10_change'] < -7)
                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Crossed 2 Day Highs', color='LG', renderf10buy00=True)
    with col2:
        df = rb.getdf('crossed-day-high')
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (df['PCT_day_change'] < 1.3) &
                    (df['PCT_day_change'] > -1.3) &
                    ((df['forecast_day_PCT10_change'] > 7) & (df['forecast_day_PCT7_change'] > 7) & (df['forecast_day_PCT5_change'] > 7) & ((df['forecast_day_PCT10_change'] > 10) | (df['forecast_day_PCT7_change'] > 10) | (df['forecast_day_PCT5_change'] > 10)))
                )
                |
                (
                    (df['PCT_day_change'] < 1.5) &
                    #((df['PCT_day_change'] > 1) | (df['PCT_day_change_pre1'] > 1) | (df['PCT_day_change_pre2'] > 1)) &
                    ((df['PCT_day_change'] > -1) & (df['PCT_day_change_pre1'] > -1) & (df['PCT_day_change_pre2'] > -1)) &
                    ((df['forecast_day_PCT10_change'] > -2) & (df['forecast_day_PCT10_change'] < 1) & (df['forecast_day_PCT7_change'] > -2) & (df['forecast_day_PCT7_change'] < 2) & (df['forecast_day_PCT5_change'] > -2) & (df['forecast_day_PCT5_change'] < 2))
                )
                |
                (
                    (~df['systemtime'].str.contains('09:', case=False, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                    (df['PCT_day_change'] < 1.3) &
                    (df['PCT_day_change'] > -1.3) &
                    ((df['forecast_day_PCT10_change'] > 7)) 
                )
                |
                (
                    (df['PCT_day_change'] > -2) &
                    (df['PCT_day_change_pre1'] > -2) &
                    (df['PCT_day_change_pre2'] > -2) &
                    ((df['PCT_day_change'] < 1) & (df['PCT_day_change_pre1'] < 1) & (df['PCT_day_change_pre2'] < 1)) &
                    ((df['forecast_day_PCT10_change'] < -7))
                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Crossed Day Highs', color='LG', renderf10buy01=True)
    with col3:
        df = rb.getdf('supertrend-morning-sell')
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (df['PCT_day_change'] < 1.3) &
                    (df['PCT_day_change'] > -1.3) &
                    ((df['forecast_day_PCT10_change'] < -7) & (df['forecast_day_PCT7_change'] < -7) & (df['forecast_day_PCT5_change'] < -7) & ((df['forecast_day_PCT10_change'] < -10) | (df['forecast_day_PCT7_change'] < -10) | (df['forecast_day_PCT5_change'] < -10)))
                
                )
                |
                (
                    (df['PCT_day_change'] > -1.5) &
                    #((df['PCT_day_change'] < -1) | (df['PCT_day_change_pre1'] < -1) | (df['PCT_day_change_pre2'] < -1)) &
                    ((df['PCT_day_change'] < 1) & (df['PCT_day_change_pre1'] < 1) & (df['PCT_day_change_pre2'] < 1)) &
                    ((df['forecast_day_PCT10_change'] < 2) & (df['forecast_day_PCT10_change'] > -1) & (df['forecast_day_PCT7_change'] > -2) & (df['forecast_day_PCT7_change'] < 2) & (df['forecast_day_PCT5_change'] > -2) & (df['forecast_day_PCT5_change'] < 2))
                )
                |
                (
                    (~df['systemtime'].str.contains('09:', case=False, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                    (df['PCT_day_change'] < 1.3) &
                    (df['PCT_day_change'] > -1.3) &
                    ((df['forecast_day_PCT10_change'] < -7)) 
                )
                |
                (
                    ((df['PCT_day_change'] > -1) & (df['PCT_day_change_pre1'] > -1) & (df['PCT_day_change_pre2'] > -1)) &
                    (df['forecast_day_PCT10_change'] > 7)
                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Supertrend Morning Sell', color='LG', renderf10sell00=True)
    with col4:
        df = rb.getdf('09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)')
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (df['PCT_day_change'] < 1.3) &
                    (df['PCT_day_change'] > -1.3) &
                    ((df['forecast_day_PCT10_change'] < -7) & (df['forecast_day_PCT7_change'] < -7) & (df['forecast_day_PCT5_change'] < -7) & ((df['forecast_day_PCT10_change'] < -10) | (df['forecast_day_PCT7_change'] < -10) | (df['forecast_day_PCT5_change'] < -10)))
                
                )
                |
                (
                    (df['PCT_day_change'] > -1.5) &
                    #((df['PCT_day_change'] < -1) | (df['PCT_day_change_pre1'] < -1) | (df['PCT_day_change_pre2'] < -1)) &
                    #((df['PCT_day_change'] < 1) & (df['PCT_day_change_pre1'] < 1) & (df['PCT_day_change_pre2'] < 1)) &
                    ((df['forecast_day_PCT10_change'] < 2) & (df['forecast_day_PCT10_change'] > -1) & (df['forecast_day_PCT7_change'] > -2) & (df['forecast_day_PCT7_change'] < 2) & (df['forecast_day_PCT5_change'] > -2) & (df['forecast_day_PCT5_change'] < 2))
                )
                |
                (
                    (~df['systemtime'].str.contains('09:', case=False, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                    (df['PCT_day_change'] < 1.3) &
                    (df['PCT_day_change'] > -1.3) &
                    ((df['forecast_day_PCT10_change'] < -7)) 
                )
                |
                (
                    ((df['PCT_day_change'] > -1) & (df['PCT_day_change_pre1'] > -1) & (df['PCT_day_change_pre2'] > -1)) &
                    (df['forecast_day_PCT10_change'] > 7)
                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Crossed 2 Day Lows', color='LG', renderf10sell00=True)
    with col5:
        df = rb.getdf('crossed-day-low')
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (df['PCT_day_change'] < 1.3) &
                    (df['PCT_day_change'] > -1.3) &
                    ((df['forecast_day_PCT10_change'] < -7) & (df['forecast_day_PCT7_change'] < -7) & (df['forecast_day_PCT5_change'] < -7) & ((df['forecast_day_PCT10_change'] < -10) | (df['forecast_day_PCT7_change'] < -10) | (df['forecast_day_PCT5_change'] < -10)))
                
                )
                |
                (
                    (df['PCT_day_change'] > -1.5) &
                    #((df['PCT_day_change'] < -1) | (df['PCT_day_change_pre1'] < -1) | (df['PCT_day_change_pre2'] < -1)) &
                    ((df['PCT_day_change'] < 1) & (df['PCT_day_change_pre1'] < 1) & (df['PCT_day_change_pre2'] < 1)) &
                    ((df['forecast_day_PCT10_change'] < 2) & (df['forecast_day_PCT10_change'] > -1) & (df['forecast_day_PCT7_change'] > -2) & (df['forecast_day_PCT7_change'] < 2) & (df['forecast_day_PCT5_change'] > -2) & (df['forecast_day_PCT5_change'] < 2))
                )
                |
                (
                    (~df['systemtime'].str.contains('09:', case=False, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                    (df['PCT_day_change'] < 1.3) &
                    (df['PCT_day_change'] > -1.3) &
                    ((df['forecast_day_PCT10_change'] < -7)) 
                )
                |
                (
                    (df['PCT_day_change'] < 2) &
                    (df['PCT_day_change_pre1'] < 2) &
                    (df['PCT_day_change_pre2'] < 2) &
                    ((df['PCT_day_change'] > -1) & (df['PCT_day_change_pre1'] > -1) & (df['PCT_day_change_pre2'] > -1)) &
                    ((df['forecast_day_PCT10_change'] > 7))
                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Crossed Day Lows', color='LG', renderf10sell01=True)


    col0, col1, col2, col3, col4, col5 = st.columns(6)
    with col0:
        df = rb.getdf('supertrend-morning-buy')
        rb.render(st, df, 'Supertrend Morning Buy', color='LG', renderf10buy00=True)
    with col1:
        df = rb.getdf('09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)')
        rb.render(st, df, 'Crossed 2 Day Highs', color='LG', renderf10buy00=True)
    with col2:
        df = rb.getdf('crossed-day-high')
        rb.render(st, df, 'Crossed Day Highs', color='LG', renderf10buy00=True)
    with col3:
        df = rb.getdf('supertrend-morning-sell')
        rb.render(st, df, 'Supertrend Morning Sell', color='LG', renderf10sell00=True)
    with col4:
        df = rb.getdf('09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)')
        rb.render(st, df, 'Crossed 2 Day Lows', color='LG', renderf10sell00=True)
    with col5:
        df = rb.getdf('crossed-day-low')
        rb.render(st, df, 'Crossed Day Lows', color='LG', renderf10sell01=True)


    col3, col6 = st.columns(2)
    with col3:
        df = rb.getdf('morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['forecast_day_PCT10_change'] > -9) &
                (df['mlData'].str.contains("0@@"))
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'morning-volume-breakout-buy ##############', color='LG', height=150)
    with col6:
        df = rb.getdf('morning-volume-breakout-sell')
        filtered_df = df
        try:
            filtered_df = df[
                (df['forecast_day_PCT10_change'] < 9) &
                (df['mlData'].str.contains("0@@"))
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'morning-volume-breakout-sell ##############', color='LG', height=150)


    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        df = rb.getdf('1-Bbuyy-morningUp-downConsolidation')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] < 1) &
                (df['PCT_day_change'] > -3) &
                (~df['systemtime'].str.contains('09:', case=False, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, na=False)) 
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayOrTodayGT0.5 : Only one dip: 1-Bbuyy-morningUp-downConsolidation', color='G', height=200)
    with col2:
        df = rb.getdf('1-Bbuyy-morningUp-downConsolidation')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] > -3) &
                (~df['systemtime'].str.contains('09:', case=False, na=False))
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayOrTodayGT0.5 : Only one dip: 1-Bbuyy-morningUp-downConsolidation', color='LG', height=200)
    with col3:
        df = rb.getdf('Breakout-Buy-after-10')
        rb.render(st, df, 'TodayUpOrIndexStockUpGT0.5 : Breakout Buy after 10', color='LG', height=200)
    with col4:
        df = rb.getdf('1-Sselll-morningDown-upConsolidation')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] > -1) &
                (df['PCT_day_change'] < 3) &
                (~df['systemtime'].str.contains('09:', case=False, na=False))
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayOrTodayLT-0.5: Only one up: 1-Sselll-morningDown-upConsolidation', color='R', height=200)
    with col5:
        df = rb.getdf('1-Sselll-morningDown-upConsolidation')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] < 3) &
                (~df['systemtime'].str.contains('09:', case=False, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, na=False)) 
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayOrTodayLT-0.5: Only one up: 1-Sselll-morningDown-upConsolidation', color='LG', height=200)
    with col6:
        df = rb.getdf('Breakout-Sell-after-10')
        rb.render(st, df, 'TodayDownOrIndexStockDownLT-0.5 : Breakout Sell after 10', color='LG', height=200)
    

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        df = rb.getintersectdf('week2lh-not-reached','crossed-day-high')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (
                    ((df['PCT_day_change_pre1'] < -0.3) | (df['PCT_day_change_pre2'] < -0.3)) &
                    ((df['PCT_day_change'] > -1.5) & (df['PCT_day_change_pre1'] > -1.5) & (df['PCT_day_change_pre2'] > -1.5)) &
                    (df['forecast_day_PCT10_change'] > -1)
                )
                |
                (
                    ((df['PCT_day_change_pre1'] < -0.3) | (df['PCT_day_change_pre2'] < -0.3)) &
                    (df['PCT_day_change'] < 1) &
                    (df['PCT_day_change'] > -1) &
                    (df['PCT_day_change_pre1'] < 1) &
                    (df['PCT_day_change_pre1'] > -1) &
                    (abs(df['week2HighChange']) > 1.1) &
                    #(~df['systemtime'].str.contains('09:', case=False, na=False)) &
                    # (~df['systemtime'].str.contains('10:00', case=False, na=False)) &
                    # (~df['systemtime'].str.contains('10:05', case=False, na=False)) &
                    # (~df['systemtime'].str.contains('10:10', case=False, na=False)) &
                    # (~df['systemtime'].str.contains('10:15', case=False, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                    ((df['forecast_day_PCT10_change'] > 3) | ((df['forecast_day_PCT10_change'] < -2) & (df['forecast_day_PCT5_change'] < 0)))
                )
            ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'week2lh-not-reached + Crossed Day High', column_conf=rb.column_config_merged, column_order=rb.column_order_p, color='G')
        else:
            rb.render(st, empty_df, 'week2lh-not-reached + Crossed Day High', column_conf=rb.column_config_merged, column_order=rb.column_order_p, color='G')
    with col2:
        df = rb.getintersectdf('week2lh-not-reached','crossed-day-high')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'week2lh-not-reached + Crossed Day High', column_conf=rb.column_config_merged, column_order=rb.column_order_p, color='LG')
        else:
            rb.render(st, empty_df, 'week2lh-not-reached + Crossed Day High', column_conf=rb.column_config_merged, column_order=rb.column_order_p, color='LG')
    with col3:
        df = rb.getintersectdf('week2lh-not-reached','crossed-day-low')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (
                    ((df['PCT_day_change_pre1'] > 0.3) | (df['PCT_day_change_pre2'] > 0.3)) &
                    ((df['PCT_day_change_pre1'] < 1.5) & (df['PCT_day_change_pre1'] < 1.5) & (df['PCT_day_change_pre2'] < 1.5)) &
                    (df['lowTail'] < 1.5) &
                    (df['forecast_day_PCT10_change'] < 1)
                )
                |
                (
                    ((df['PCT_day_change_pre1'] > 0.3) | (df['PCT_day_change_pre2'] > 0.3)) &
                    (df['PCT_day_change'] < 1) &
                    (df['PCT_day_change'] > -1) &
                    (df['PCT_day_change_pre1'] < 1) &
                    (df['PCT_day_change_pre1'] > -1) &
                    (abs(df['week2LowChange']) > 1.1) &
                    (df['lowTail'] < 1.5) &
                    # (~df['systemtime'].str.contains('09:', case=False, na=False)) &
                    # (~df['systemtime'].str.contains('10:00', case=False, na=False)) &
                    # (~df['systemtime'].str.contains('10:05', case=False, na=False)) &
                    # (~df['systemtime'].str.contains('10:10', case=False, na=False)) &
                    # (~df['systemtime'].str.contains('10:15', case=False, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                    ((df['forecast_day_PCT10_change'] < -3) | ((df['forecast_day_PCT10_change'] > 2) & (df['forecast_day_PCT5_change'] > 0)))
                )
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'week2lh-not-reached + Crossed Day Low', column_conf=rb.column_config_merged, column_order=rb.column_order_p, color='R')
        else:
            rb.render(st, empty_df, 'week2lh-not-reached + Crossed Day Low', column_conf=rb.column_config_merged, column_order=rb.column_order_p, color='R')
    with col4:
        df = rb.getintersectdf('week2lh-not-reached','crossed-day-low')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'week2lh-not-reached + Crossed Day Low', column_conf=rb.column_config_merged, column_order=rb.column_order_p, color='LG')
        else:
            rb.render(st, empty_df, 'week2lh-not-reached + Crossed Day Low', column_conf=rb.column_config_merged, column_order=rb.column_order_p, color='LG')
    

    
if __name__ == '__main__':
    main()