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
    st.title('Learning')


    col1, col2, col3, col4 = st.columns(4)
    with col1:
        df = rb.getdf('morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['forecast_day_PCT10_change'] > -2) &
                (df['forecast_day_PCT7_change'] > -1) &
                (df['forecast_day_PCT5_change'] > -1) &
                (df['forecast_day_PCT7_change'] < 1) &
                (df['forecast_day_PCT5_change'] < 1) 
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Test0', color='LG')
    with col2:
        df = rb.getdf('morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('09:2', case=False, na=False)) &
                (df['forecast_day_PCT10_change'] < -6) &
                (df['forecast_day_PCT7_change'] < -6) &
                (df['forecast_day_PCT5_change'] < -6) 
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Test1 - First15minutelowest', color='LG')
    with col3:
        df = rb.getdf('morning-volume-breakout-sell')
        filtered_df = df
        try:
            filtered_df = df[
                (df['forecast_day_PCT10_change'] < 2) &
                (df['forecast_day_PCT7_change'] < 1) &
                (df['forecast_day_PCT5_change'] < 1) &
                (df['forecast_day_PCT7_change'] > -1) &
                (df['forecast_day_PCT5_change'] > -1) 
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Test2', color='LG')
    with col4:
        df = rb.getdf('morning-volume-breakout-sell')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('09:2', case=False, na=False)) &
                (df['forecast_day_PCT10_change'] > 6) &
                (df['forecast_day_PCT7_change'] > 6) &
                (df['forecast_day_PCT5_change'] > 6)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Test3 - First15minutehighest', color='LG')
    

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        df = rb.getintersectdf('week2lh-not-reached','crossed-day-high')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                ((df['PCT_day_change_pre1'] < -0.3) | (df['PCT_day_change_pre2'] < -0.3)) &
                (abs(df['week2HighChange']) > 1.1) &
                #(~df['systemtime'].str.contains('09:', case=False, na=False)) &
                # (~df['systemtime'].str.contains('10:00', case=False, na=False)) &
                # (~df['systemtime'].str.contains('10:05', case=False, na=False)) &
                # (~df['systemtime'].str.contains('10:10', case=False, na=False)) &
                # (~df['systemtime'].str.contains('10:15', case=False, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                ((df['forecast_day_PCT10_change'] > 3) | ((df['forecast_day_PCT10_change'] < -2) & (df['forecast_day_PCT5_change'] < 0)))
            ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 2:
            rb.render(st, filtered_df, 'week2lh-not-reached + Crossed Day High', column_conf=rb.column_config_merged, column_order=rb.column_order_p, color='LG')
        else:
            rb.render(st, empty_df, 'week2lh-not-reached + Crossed Day High', column_conf=rb.column_config_merged, column_order=rb.column_order_p, color='LG')
    with col2:
        df = rb.getdf('crossed-day-high')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('09:2', case=False, na=False)) &
                (~df['systemtime'].str.contains('09:3', case=False, na=False)) &
                (~df['systemtime'].str.contains('09:4', case=False, na=False)) &
                (df['highTail'] < 1.5) &
                (((df['forecast_day_PCT10_change'] > 2) & (df['forecast_day_PCT7_change'] > 2) & (df['forecast_day_PCT5_change'] > 2)) | ((df['forecast_day_PCT10_change'] < -6) & (df['forecast_day_PCT5_change'] < 0))) &
                (df['PCT_day_change'] > -1) & 
                (df['PCT_day_change'] < 1) &
                (df['PCT_day_change_pre1'] > -1.5) & 
                (df['PCT_day_change_pre1'] < 1.5) &
                (df['PCT_day_change_pre2'] < 2)
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Crossed Day Highs', column_order=rb.column_order_p, color='LG')
    # with col3:
    #     df = rb.getintersectdf('supertrend-morning-buy','crossed-day-high')
    #     filtered_df = df
    #     try:
    #         filtered_df = df[
    #             (abs(df['week2LowChange']) > 1) &
    #             (~df['systemtime'].str.contains('11:', case=False, na=False)) &
    #             ((df['forecast_day_PCT10_change'] > 0) & (df['forecast_day_PCT7_change'] > 0) & (df['forecast_day_PCT5_change'] > 0))
    #         ]
    #     except KeyError as e:
    #         print("")
    #     rb.render(st, filtered_df, 'supertrend-morning-buy+Crossed Day Highs', color='LG')
    with col3:
        df = rb.getintersectdf('week2lh-not-reached','crossed-day-low')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                ((df['PCT_day_change_pre1'] > 0.3) | (df['PCT_day_change_pre2'] > 0.3)) &
                (abs(df['week2LowChange']) > 1.1) &
                (df['lowTail'] < 1.5) &
                # (~df['systemtime'].str.contains('09:', case=False, na=False)) &
                # (~df['systemtime'].str.contains('10:00', case=False, na=False)) &
                # (~df['systemtime'].str.contains('10:05', case=False, na=False)) &
                # (~df['systemtime'].str.contains('10:10', case=False, na=False)) &
                # (~df['systemtime'].str.contains('10:15', case=False, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                ((df['forecast_day_PCT10_change'] < -3) | ((df['forecast_day_PCT10_change'] > 2) & (df['forecast_day_PCT5_change'] > 0)))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 2:
            rb.render(st, filtered_df, 'week2lh-not-reached + Crossed Day Low', column_conf=rb.column_config_merged, column_order=rb.column_order_p, color='LG')
        else:
            rb.render(st, empty_df, 'week2lh-not-reached + Crossed Day Low', column_conf=rb.column_config_merged, column_order=rb.column_order_p, color='LG')
    with col4:
        df = rb.getdf('crossed-day-low')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('09:2', case=False, na=False)) &
                (~df['systemtime'].str.contains('09:3', case=False, na=False)) &
                (~df['systemtime'].str.contains('09:4', case=False, na=False)) &
                (((df['forecast_day_PCT10_change'] < -2) & (df['forecast_day_PCT7_change'] < -2) & (df['forecast_day_PCT5_change'] < -2)) | ((df['forecast_day_PCT10_change'] > 6) & (df['forecast_day_PCT5_change'] > 0))) &
                (df['PCT_day_change'] > -1) & 
                (df['PCT_day_change'] < 1) &
                (df['PCT_day_change_pre1'] > -1.5) & 
                (df['PCT_day_change_pre1'] < 1.5) &
                (df['PCT_day_change_pre2'] > -2)
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Crossed Day Lows', color='LG')
    # with col6:
    #     df = rb.getintersectdf('supertrend-morning-sell','crossed-day-low')
    #     filtered_df = df
    #     try:
    #         filtered_df = df[
    #             (abs(df['week2HighChange']) > 1) &
    #             (~df['systemtime'].str.contains('11:', case=False, na=False)) &
    #             ((df['forecast_day_PCT10_change'] < 0) & (df['forecast_day_PCT7_change'] < 0) & (df['forecast_day_PCT5_change'] < 0))
    #         ]
    #     except KeyError as e:
    #         print("")
    #     rb.render(st, filtered_df, 'supertrend-morning-sell+Crossed Day Lows', color='LG')


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

    
    col1, col2, col3, col5, col6, col7 = st.columns(6)
    with col1:
        df = rb.getdf('Breakout-Buy-after-10')
        rb.render(st, df, 'TodayUpOrIndexStockUpGT0.5 : Breakout Buy after 10', color='G', height=200)
    with col2:
        df = rb.getdf('1-Bbuyy-morningUp-downConsolidation')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('09:', case=False, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, na=False)) 
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayOrTodayGT0.5 : Only one dip: 1-Bbuyy-morningUp-downConsolidation', color='LG', height=200)
    with col3:
        df = rb.getdf('1-Bbuyy-morningUp-downConsolidation')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] < 1) &
                (~df['systemtime'].str.contains('09:', case=False, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, na=False)) 
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayOrTodayGT0.5 : Only one dip: 1-Bbuyy-morningUp-downConsolidation', color='G', height=200)
    # with col4:
    #     df = rb.getdf('1-Bbuyy-morningUp-downConsolidation')
    #     filtered_df = df
    #     try:
    #         filtered_df = df[
    #             (~df['systemtime'].str.contains('09:', case=False, na=False)) &
    #             (~df['systemtime'].str.contains('10:', case=False, na=False)) &
    #             (~df['systemtime'].str.contains('11:3', case=False, na=False)) &
    #             (~df['systemtime'].str.contains('11:4', case=False, na=False)) &
    #             (~df['systemtime'].str.contains('11:5', case=False, na=False)) 
    #         ]
    #     except KeyError as e:
    #         print("")
    #     except KeyError as e:
    #         print("")
    #     rb.render(st, filtered_df, 'LastDayOrTodayNOTGT0.5 : Only one dip: 1-Bbuyy-morningUp-downConsolidation', color='G', height=200)
    with col5:
        df = rb.getdf('Breakout-Sell-after-10')
        rb.render(st, df, 'TodayDownOrIndexStockDownLT-0.5 : Breakout Sell after 10', color='R', height=200)
    with col6:
        df = rb.getdf('1-Sselll-morningDown-upConsolidation')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('09:', case=False, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, na=False)) 
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayOrTodayLT-0.5: Only one up: 1-Sselll-morningDown-upConsolidation', color='LG', height=200)
    with col7:
        df = rb.getdf('1-Sselll-morningDown-upConsolidation')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] > -1) &
                (~df['systemtime'].str.contains('09:', case=False, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, na=False)) 
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayOrTodayLT-0.5: Only one up: 1-Sselll-morningDown-upConsolidation', color='R', height=200)
    # with col8:
    #     df = rb.getdf('1-Sselll-morningDown-upConsolidation')
    #     filtered_df = df
    #     try:
    #         filtered_df = df[
    #             (~df['systemtime'].str.contains('09:', case=False, na=False)) &
    #             (~df['systemtime'].str.contains('10:', case=False, na=False)) &
    #             (~df['systemtime'].str.contains('11:3', case=False, na=False)) &
    #             (~df['systemtime'].str.contains('11:4', case=False, na=False)) &
    #             (~df['systemtime'].str.contains('11:5', case=False, na=False)) 
    #         ]
    #     except KeyError as e:
    #         print("")
    #     rb.render(st, filtered_df, 'LastDayOrTodayNOTLT-0.5: Only one up: 1-Sselll-morningDown-upConsolidation', color='R', height=200)



# Sentiment Analysis Tables
    st.divider()
    st.subheader('News Sentiment Analysis')
    
    col1, col2 = st.columns(2)
    
    # Load sentiment data once
    try:
        from pymongo import MongoClient
        connection = MongoClient('localhost', 27017)
        dbcl = connection.chartlink
        sentiment_collection = dbcl['sentiment']
        sentiment_data = list(sentiment_collection.find())
        connection.close()
    except Exception as e:
        sentiment_data = []
        st.write(f"Error loading sentiment data: {e}")
    
    with col1:
        # Positive Sentiment Table
        try:
            if sentiment_data:
                # Filter for positive sentiment
                positive_data = []
                for item in sentiment_data:
                    if item.get('news_analysis', {}).get('overall_sentiment') == 'Positive':
                        # Flatten the structure for display
                        news_items = item.get('news_analysis', {}).get('news', [])
                        for news in news_items:
                            positive_data.append({
                                'scrip': item.get('scrip', ''),
                                'company': item.get('company', ''),
                                'headline': news.get('headline', ''),
                                'impact': news.get('impact', ''),
                                'severity': news.get('severity', '')
                            })
                
                if positive_data:
                    df_positive = pd.DataFrame(positive_data)
                    rb.render_rawdata(st, df_positive, 'Positive Sentiment News', color='G', height=300)
                else:
                    st.write("No positive sentiment news found")
            else:
                st.write("No sentiment data available")
        except Exception as e:
            st.write(f"Error processing positive sentiment: {e}")
    
    with col2:
        # Negative Sentiment Table
        try:
            if sentiment_data:
                # Filter for negative sentiment
                negative_data = []
                for item in sentiment_data:
                    if item.get('news_analysis', {}).get('overall_sentiment') == 'Negative':
                        # Flatten the structure for display
                        news_items = item.get('news_analysis', {}).get('news', [])
                        for news in news_items:
                            negative_data.append({
                                'scrip': item.get('scrip', ''),
                                'company': item.get('company', ''),
                                'headline': news.get('headline', ''),
                                'impact': news.get('impact', ''),
                                'severity': news.get('severity', '')
                            })
                
                if negative_data:
                    df_negative = pd.DataFrame(negative_data)
                    rb.render_rawdata(st, df_negative, 'Negative Sentiment News', color='R', height=300)
                else:
                    st.write("No negative sentiment news found")
            else:
                st.write("No sentiment data available")
        except Exception as e:
            st.write(f"Error processing negative sentiment: {e}")
    st.divider()


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
                ((df['PCT_day_change'] < 0) | (df['PCT_day_change_pre1'] < 0)) &
                ((df['PCT_day_change_pre2'] < 0) | (df['PCT_day_change_pre1'] < 0)) &
                ((df['month3HighChange'] < 0))
                )
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Crossed Day Lows', color='LG', renderf10sell=True)


    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
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
        df = rb.getintersectdf_ml('regressionhigh', 'regressionlow')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change_pre1'] < 3) &
                (df['PCT_change_pre2'] < 3) &
                ((df['PCT_change_pre1'] > 1) | (df['PCT_change_pre2'] > 1)) &
                ((df['PCT_change_pre1'] < 0.5) | (df['PCT_change_pre2'] < 0.5)) &
                (df['PCT_day_change'] < 2.5) &
                (df['PCT_day_change'] > -1.3) &
                ((df['kNeighboursValue_reg'] > 0.5) & (df['mlpValue_reg'] > 0.5)) &
                ((df['kNeighboursValue_reg'] > 1) | (df['mlpValue_reg'] > 1)) &
                ((df['kNeighboursValue_reg_merged'] > 1) | (df['mlpValue_reg_merged'] > 1)) &
                ((df['forecast_day_PCT10_change'] > 2) | (df['forecast_day_PCT10_change'] < -2))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'MLBUY', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='G')
    with col4:
        df = rb.getintersectdf_ml('regressionhigh', 'regressionlow')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change_pre1'] < 3) &
                (df['PCT_change_pre2'] < 3) &
                ((df['PCT_change_pre1'] > 1) | (df['PCT_change_pre2'] > 1)) &
                ((df['PCT_change_pre1'] < 0.5) | (df['PCT_change_pre2'] < 0.5)) &
                (df['PCT_day_change'] < 2.5) &
                (df['PCT_day_change'] > -0.7) &
                # (df['highTail'] < 1.3) &
                # ((df['kNeighboursValue_reg'] > 0.5) & (df['mlpValue_reg'] > 0.5)) &
                # ((df['kNeighboursValue_reg'] > 1) | (df['mlpValue_reg'] > 1)) &
                ((df['kNeighboursValue_reg_merged'] > 1) | (df['mlpValue_reg_merged'] > 1)) &
                ((df['forecast_day_PCT10_change'] > 5) | (df['forecast_day_PCT10_change'] < -5))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'MLBUY', column_conf=rb.column_config_ml, column_order=rb.column_order_ml,
                  renderml=True, color='G')
    with col5:
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
    with col6:
        df = rb.getintersectdf_ml('regressionlow', 'regressionhigh')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] > -4) &
                (df['kNeighboursValue_reg'] < -2) &
                (df['mlpValue_reg'] < -2)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'MLSELL', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='LG')
    with col7:
        df = rb.getintersectdf_ml('regressionlow', 'regressionhigh')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change_pre1'] > -3) &
                (df['PCT_change_pre2'] > -3) &
                ((df['PCT_change_pre1'] < -1) | (df['PCT_change_pre2'] < -1)) &
                ((df['PCT_change_pre1'] > -0.5) | (df['PCT_change_pre2'] > -0.5)) &
                (df['PCT_day_change'] > -2.5) &
                (df['PCT_day_change'] < 1.3) &
                ((df['kNeighboursValue_reg'] < -0.5) & (df['mlpValue_reg'] < -0.5)) &
                ((df['kNeighboursValue_reg'] < -1) | (df['mlpValue_reg'] < -1)) &
                ((df['kNeighboursValue_reg_merged'] < -1) | (df['mlpValue_reg_merged'] < -1)) &
                ((df['forecast_day_PCT10_change'] < -2) | (df['forecast_day_PCT10_change'] > 2))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'MLSELL', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='R')
    with col8:
        df = rb.getintersectdf_ml('regressionlow', 'regressionhigh')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change_pre1'] > -3) &
                (df['PCT_change_pre2'] > -3) &
                ((df['PCT_change_pre1'] < -1) | (df['PCT_change_pre2'] < -1)) &
                ((df['PCT_change_pre1'] > -0.5) | (df['PCT_change_pre2'] > -0.5)) &
                (df['PCT_day_change'] > -2.5) &
                (df['PCT_day_change'] < 0.7) &
                # (df['lowTail'] < 1.3) &
                # ((df['kNeighboursValue_reg'] < -0.5) & (df['mlpValue_reg'] < -0.5)) &
                # ((df['kNeighboursValue_reg'] < -1) | (df['mlpValue_reg'] < -1)) &
                ((df['kNeighboursValue_reg_merged'] < -1) | (df['mlpValue_reg_merged'] < -1)) &
                ((df['forecast_day_PCT10_change'] < -5) | (df['forecast_day_PCT10_change'] > 5))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'MLSELL', column_conf=rb.column_config_ml, column_order=rb.column_order_ml,
                  renderml=True, color='R')

    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        df = rb.getintersectdf_ml('regressionhigh', 'regressionlow')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] < 4.5) &
                (df['PCT_day_change'] < 4) &
                (df['PCT_day_change'] > 2) &
                ((df['PCT_day_change'] < 1) | (df['PCT_day_change_pre1'] < 1) | (df['PCT_day_change_pre2'] < -0.5)) &
                ((df['kNeighboursValue_reg'] > 2) | (df['mlpValue_reg'] > 2)) &
                ((df['PCT_day_change_pre1'] > 0 ) | (df['PCT_day_change_pre2'] > 0)) &
                (df['forecast_day_PCT10_change'] > 2)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'MLBUY', column_conf=rb.column_config_ml, column_order=rb.column_order_ml,
                  renderml=True, color='LG')
    with col2:
        df = rb.getintersectdf_ml('regressionhigh', 'regressionlow')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] < 1.5) &
                (df['PCT_day_change'] < 1.5) &
                (df['PCT_change'] > -0.5) &
                (df['PCT_day_change'] > -0.5) &
                ((df['PCT_day_change_pre1'] > 0.3) | (df['PCT_day_change_pre2'] > 0.3)) &
                (df['forecast_day_PCT10_change'] > 3) &
                (df['highTail'] > 2.5) &
                (df['lowTail'] < 1.3)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayDown:Buy-HighTail', column_conf=rb.column_config_ml, column_order=rb.column_order_ml,
                  renderml=True, color='LG')    
    with col3:
        df = rb.getintersectdf_ml('regressionlow', 'regressionhigh')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] > -4.5) &
                (df['PCT_day_change'] > -4) &
                (df['PCT_day_change'] < -2) &
                ((df['PCT_day_change'] > -1) | (df['PCT_day_change_pre1'] > -1) | (df['PCT_day_change_pre2'] > 0.5)) &
                ((df['kNeighboursValue_reg'] < -2) | (df['mlpValue_reg'] < -2)) &
                ((df['PCT_day_change_pre1'] < 0 ) | (df['PCT_day_change_pre2'] < 0)) &
                (df['forecast_day_PCT10_change'] < -2)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'MLSELL', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='LG')
    with col4:
        df = rb.getintersectdf_ml('regressionhigh', 'regressionlow')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] > -1.5) &
                (df['PCT_day_change'] > -1.5) &
                (df['PCT_change'] < 0.5) &
                (df['PCT_day_change'] < 0.5) &
                ((df['PCT_day_change_pre1'] < -0.3) | (df['PCT_day_change_pre2'] < -0.3)) &
                (df['forecast_day_PCT10_change'] < -3) &
                (df['lowTail'] > 2.5) &
                (df['highTail'] < 1.3)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayUp:Sell-LowTail', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='LG')
    

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        df = rb.getintersectdf_ml('regressionlow', 'regressionhigh')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] > -4.5) &
                (df['PCT_day_change'] > -4) &
                (df['PCT_day_change'] < -2) &
                ((df['PCT_day_change_pre1'] > -2 ) | (df['monthHighChange'] < 0)) &
                (df['forecast_day_PCT10_change'] > 5) &
                ((df['kNeighboursValue_reg'] != 0) | (df['mlpValue_reg'] != 0))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'UpTrendMayBuy', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='LG')
    with col2:
        df = rb.getintersectdf_ml('regressionlow', 'regressionhigh')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] > -4.5) &
                (df['PCT_day_change'] > -4) &
                (df['PCT_day_change'] < -2) &
                ((df['PCT_day_change_pre1'] > -2 ) | (df['monthHighChange'] < 0)) &
                (df['forecast_day_PCT10_change'] > 5)
                #((df['kNeighboursValue_reg'] < -2) | (df['mlpValue_reg'] < -2))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'UpTrendMayBuy', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='LG')
    with col3:
        df = rb.getintersectdf_ml('regressionhigh', 'regressionlow')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] < 4.5) &
                (df['PCT_day_change'] < 4) &
                (df['PCT_day_change'] > 2) &
                ((df['PCT_day_change_pre1'] < 2 ) | (df['monthLowChange'] > 0)) &
                (df['forecast_day_PCT10_change'] < -5) &
                ((df['kNeighboursValue_reg'] != 0) | (df['mlpValue_reg'] != 0))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'DownTrendMaySell', column_conf=rb.column_config_ml, column_order=rb.column_order_ml,
                  renderml=True, color='LG')
    with col4:
        df = rb.getintersectdf_ml('regressionhigh', 'regressionlow')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] < 4.5) &
                (df['PCT_day_change'] < 4) &
                (df['PCT_day_change'] > 2) &
                ((df['PCT_day_change_pre1'] < 2 ) | (df['monthLowChange'] > 0)) &
                (df['forecast_day_PCT10_change'] < -5) 
                #((df['kNeighboursValue_reg'] > 2) | (df['mlpValue_reg'] > 2))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'DownTrendMaySell', column_conf=rb.column_config_ml, column_order=rb.column_order_ml,
                  renderml=True, color='LG')


    col1, col2, col3, col4 = st.columns(4)
    with col1:
        df = rb.getintersectdf_ml('regressionlow', 'regressionhigh')
        filtered_df = df
        try:
            filtered_df = df[
                (df['forecast_day_PCT10_change'] > -2) &
                (df['forecast_day_PCT7_change'] > -1) &
                (df['forecast_day_PCT5_change'] > -1) &
                (df['forecast_day_PCT7_change'] < 1) &
                (df['forecast_day_PCT5_change'] < 1) &
                ((df['kNeighboursValue_reg'] != 0) | (df['mlpValue_reg'] != 0))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Test0', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='LG')
    with col2:
        df = rb.getintersectdf_ml('regressionlow', 'regressionhigh')
        filtered_df = df
        try:
            filtered_df = df[
                (df['forecast_day_PCT10_change'] < -3) &
                (df['forecast_day_PCT7_change'] < 1) &
                (df['forecast_day_PCT5_change'] < 1) &
                ((df['kNeighboursValue_reg'] != 0) | (df['mlpValue_reg'] != 0))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Test1', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='LG')
    with col3:
        df = rb.getintersectdf_ml('regressionlow', 'regressionhigh')
        filtered_df = df
        try:
            filtered_df = df[
                (df['forecast_day_PCT10_change'] < 2) &
                (df['forecast_day_PCT7_change'] < 1) &
                (df['forecast_day_PCT5_change'] < 1) &
                (df['forecast_day_PCT7_change'] > -1) &
                (df['forecast_day_PCT5_change'] > -1) &
                ((df['kNeighboursValue_reg'] != 0) | (df['mlpValue_reg'] != 0))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Test2', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='LG')
    with col4:
        df = rb.getintersectdf_ml('regressionlow', 'regressionhigh')
        filtered_df = df
        try:
            filtered_df = df[
                (df['forecast_day_PCT10_change'] > 3) &
                (df['forecast_day_PCT7_change'] > 1) &
                (df['forecast_day_PCT5_change'] > 1) &
                ((df['kNeighboursValue_reg'] != 0) | (df['mlpValue_reg'] != 0))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Test3', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='LG')
    





    
if __name__ == '__main__':
    main()