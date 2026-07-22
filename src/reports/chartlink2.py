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
                           page_title="Dashboard2",
                           initial_sidebar_state="expanded",)
    except Exception:
        pass

    # main title
    st.title('chartlink2')

    # page-specific flags
    rb.chartlink2 = True

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
            
            count_9_3 = df[
                (
                    (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False))
                )
            ]

            if (len(count_9_3) >= 6):
                filtered_df = filtered_df[
                (
                    (df['forecast_day_PCT5_change'] > 4) | 
                    (df['forecast_day_PCT10_change'] < -4) | 
                    (
                        (~df['systemtime'].str.contains('09:', case=False, regex=True, na=False)) &
                        (~df['systemtime'].str.contains('10:0', case=False, regex=True, na=False)) &
                        (~df['systemtime'].str.contains('10:1', case=False, regex=True, na=False))
                    )
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
            
            filtered_df = filtered_df[
                (
                    (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False))&
                    (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False))
                )
            ]

            count_9_3 = df[
                (
                    (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False))
                )
            ]

            if (len(count_9_3) >= 8):
                filtered_df = filtered_df[
                (
                    (df['forecast_day_PCT5_change'] > 4) | 
                    (df['forecast_day_PCT10_change'] < -4) | 
                    (
                        (~df['systemtime'].str.contains('09:', case=False, regex=True, na=False)) &
                        (~df['systemtime'].str.contains('10:0', case=False, regex=True, na=False)) &
                        (~df['systemtime'].str.contains('10:1', case=False, regex=True, na=False))
                    )
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
                    (
                        ~(df['systemtime'].str.contains('09:', case=False, regex=True, na=False)) & 
                        ((df['PCT_day_change'] < 1.5) & (df['PCT_change'] < 1.5)) &
                        ((((df['forecast_day_PCT5_change'] < -1) | (df['forecast_day_PCT7_change'] < -1)))
                        | (df['forecast_day_PCT5_change'] > 3)
                        ) &
                        (df['forecast_day_PCT10_change'] > -2) & 
                        (df['forecast_day_PCT7_change'] > -1) & 
                        (df['forecast_day_PCT5_change'] > -1) & 
                        (df['forecast_day_PCT10_change'] < 3)
                    )
                    | 
                    (
                        (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                        ((df['PCT_day_change'] < 0.5) | (df['PCT_day_change_pre1'] < 0.5) | (df['PCT_day_change_pre2'] < 0.5)) &
                        ((df['PCT_day_change'] > 0.5) | (abs(df['PCT_day_change_pre1']) > 0.5) | (abs(df['PCT_day_change_pre2']) > 0.5)) &
                        ((df['PCT_day_change'] < 2) | (df['PCT_day_change_pre1'] < 2)) &
                        ((df['PCT_day_change'] > -0.3) | (df['PCT_day_change_pre2'] > -0.3)) &
                        ((df['yearHighChange'] < 0) | (df['monthHighChange'] < 0) | (df['forecast_day_PCT10_change'] < -6)) &
                        (
                            (((df['forecast_day_PCT10_change'] < -6) & (df['forecast_day_PCT5_change'] > 0)))
                        )
                    )
                )
                ]
            
            count_9_3 = df[
                (
                    (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False))
                )
            ]

            if (len(count_9_3) >= 8):
                filtered_df = filtered_df[
                (
                    (df['forecast_day_PCT5_change'] > 4) | 
                    (df['forecast_day_PCT10_change'] < -4) | 
                    (
                        (~df['systemtime'].str.contains('09:', case=False, regex=True, na=False)) &
                        (~df['systemtime'].str.contains('10:0', case=False, regex=True, na=False)) &
                        (~df['systemtime'].str.contains('10:1', case=False, regex=True, na=False))
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
            
            count_9_3 = df[
                    (
                        (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False))
                    )
                ]

            if (len(count_9_3) >= 6):
                filtered_df = filtered_df[
                (
                    (df['forecast_day_PCT5_change'] > 4) | 
                    (df['forecast_day_PCT10_change'] < -4) | 
                    (
                        (~df['systemtime'].str.contains('09:', case=False, regex=True, na=False)) &
                        (~df['systemtime'].str.contains('10:0', case=False, regex=True, na=False)) &
                        (~df['systemtime'].str.contains('10:1', case=False, regex=True, na=False))
                    )
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
            
            filtered_df = filtered_df[
                (
                    (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False))&
                    (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False))
                )
            ]

            count_9_3 = df[
                (
                    (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False))
                )
            ]

            if (len(count_9_3) >= 8):
                filtered_df = filtered_df[
                (
                    (df['forecast_day_PCT5_change'] > 4) | 
                    (df['forecast_day_PCT10_change'] < -4) | 
                    (
                        (~df['systemtime'].str.contains('09:', case=False, regex=True, na=False)) &
                        (~df['systemtime'].str.contains('10:0', case=False, regex=True, na=False)) &
                        (~df['systemtime'].str.contains('10:1', case=False, regex=True, na=False))
                    )
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
                    (
                        ~(df['systemtime'].str.contains('09:', case=False, regex=True, na=False)) &
                        ((df['PCT_day_change'] > -1.5) & (df['PCT_change'] > -1.5)) &
                        ((((df['forecast_day_PCT5_change'] > 1) | (df['forecast_day_PCT7_change'] > 1)))
                        | (df['forecast_day_PCT5_change'] < -3)
                        ) &
                        (df['forecast_day_PCT10_change'] < 2) & 
                        (df['forecast_day_PCT7_change'] < 1) & 
                        (df['forecast_day_PCT5_change'] < 1) & 
                        (df['forecast_day_PCT10_change'] > -3)
                    )
                    | 
                    (
                        (~df['systemtime'].str.contains('09:', case=False, regex=True, na=False)) &
                        ((df['PCT_day_change'] > -0.5) | (df['PCT_day_change_pre1'] > -0.5) | (df['PCT_day_change_pre2'] > -0.5)) &
                        ((df['PCT_day_change'] < -0.5) | (abs(df['PCT_day_change_pre1']) > 0.5) | (abs(df['PCT_day_change_pre2']) > 0.5)) &
                        ((df['PCT_day_change'] > -2) | (df['PCT_day_change_pre1'] > -2)) &
                        ((df['PCT_day_change'] < 0.3) | (df['PCT_day_change_pre2'] < 0.3)) &
                        ((df['yearLowChange'] > 0) | (df['monthLowChange'] > 0) | (df['forecast_day_PCT10_change'] > 6)) &
                        (
                            (((df['forecast_day_PCT10_change'] > 6) & (df['forecast_day_PCT5_change'] < 0))) 
                        )
                    )
                )
            ]

            count_9_3 = df[
                (
                    (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False))
                )
            ]

            if (len(count_9_3) >= 8):
                filtered_df = filtered_df[
                (
                    (df['forecast_day_PCT5_change'] > 4) | 
                    (df['forecast_day_PCT10_change'] < -4) | 
                    (
                        (~df['systemtime'].str.contains('09:', case=False, regex=True, na=False)) &
                        (~df['systemtime'].str.contains('10:0', case=False, regex=True, na=False)) &
                        (~df['systemtime'].str.contains('10:1', case=False, regex=True, na=False))
                    )
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
            
            count_9_3 = df[
                (
                    (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False))
                )
            ]

            if (len(count_9_3) >= 6):
                filtered_df = filtered_df[
                (
                    (df['forecast_day_PCT5_change'] > 4) | 
                    (df['forecast_day_PCT10_change'] < -4) | 
                    (
                        (~df['systemtime'].str.contains('09:', case=False, regex=True, na=False)) &
                        (~df['systemtime'].str.contains('10:0', case=False, regex=True, na=False)) &
                        (~df['systemtime'].str.contains('10:1', case=False, regex=True, na=False))
                    )
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
            
            count_9_3 = df[
                (
                    (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False))
                )
            ]

            if (len(count_9_3) >= 8):
                filtered_df = filtered_df[
                (
                    (df['forecast_day_PCT5_change'] > 4) | 
                    (df['forecast_day_PCT10_change'] < -4) | 
                    (
                        (~df['systemtime'].str.contains('09:', case=False, regex=True, na=False)) &
                        (~df['systemtime'].str.contains('10:0', case=False, regex=True, na=False)) &
                        (~df['systemtime'].str.contains('10:1', case=False, regex=True, na=False))
                    )
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
                (~df['systemtime'].str.contains('09:', case=False, regex=True, na=False)) & 
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
        
            count_9_3 = df[
                (
                    (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False))
                )
            ]

            if (len(count_9_3) >= 8):
                filtered_df = filtered_df[
                (
                    (df['forecast_day_PCT5_change'] > 4) | 
                    (df['forecast_day_PCT10_change'] < -4) | 
                    (
                        (~df['systemtime'].str.contains('09:', case=False, regex=True, na=False)) &
                        (~df['systemtime'].str.contains('10:0', case=False, regex=True, na=False)) &
                        (~df['systemtime'].str.contains('10:1', case=False, regex=True, na=False))
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
            
            count_9_3 = df[
                (
                    (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False))
                )
            ]

            if (len(count_9_3) >= 6):
                filtered_df = filtered_df[
                (
                    (df['forecast_day_PCT5_change'] > 4) | 
                    (df['forecast_day_PCT10_change'] < -4) | 
                    (
                        (~df['systemtime'].str.contains('09:', case=False, regex=True, na=False)) &
                        (~df['systemtime'].str.contains('10:0', case=False, regex=True, na=False)) &
                        (~df['systemtime'].str.contains('10:1', case=False, regex=True, na=False))
                    )
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
        
            count_9_3 = df[
                (
                    (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False))
                )
            ]

            if (len(count_9_3) >= 8):
                filtered_df = filtered_df[
                (
                    (df['forecast_day_PCT5_change'] > 4) | 
                    (df['forecast_day_PCT10_change'] < -4) | 
                    (
                        (~df['systemtime'].str.contains('09:', case=False, regex=True, na=False)) &
                        (~df['systemtime'].str.contains('10:0', case=False, regex=True, na=False)) &
                        (~df['systemtime'].str.contains('10:1', case=False, regex=True, na=False))
                    )
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
                (~df['systemtime'].str.contains('09:', case=False, regex=True, na=False)) &
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
            
            count_9_3 = df[
                (
                    (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False))
                )
            ]

            if (len(count_9_3) >= 8):
                filtered_df = filtered_df[
                (
                    (df['forecast_day_PCT5_change'] > 4) | 
                    (df['forecast_day_PCT10_change'] < -4) | 
                    (
                        (~df['systemtime'].str.contains('09:', case=False, regex=True, na=False)) &
                        (~df['systemtime'].str.contains('10:0', case=False, regex=True, na=False)) &
                        (~df['systemtime'].str.contains('10:1', case=False, regex=True, na=False))
                    )
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
                    ((df['monthLowChange'] < 15) | (df['monthHighChange'] < -4) | df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
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
                    (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                    (df['PCT_day_change'] < 1.3) &
                    (df['PCT_day_change'] > -1.3) &
                    ((df['forecast_day_PCT10_change'] > 7) & (df['forecast_day_PCT7_change'] > 7) & (df['forecast_day_PCT5_change'] > 7) & ((df['forecast_day_PCT10_change'] > 10) | (df['forecast_day_PCT7_change'] > 10) | (df['forecast_day_PCT5_change'] > 10)))
                )
                |
                (
                    (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                    ((df['monthLowChange'] < 15) | (df['monthHighChange'] < -4) | df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
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
                    (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                    (df['PCT_day_change'] > -2) &
                    (df['PCT_day_change_pre1'] > -2) &
                    (df['PCT_day_change_pre2'] > -2) &
                    ((df['PCT_day_change'] < 1) & (df['PCT_day_change_pre1'] < 1) & (df['PCT_day_change_pre2'] < 1)) &
                    ((df['forecast_day_PCT10_change'] < -7))
                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Crossed Day Highs', color='LG', renderf10buy00=True)
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
                    ((df['monthLowChange'] > 4) | (df['monthHighChange'] > -15) | df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
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
                    (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                    (df['PCT_day_change'] < 1.3) &
                    (df['PCT_day_change'] > -1.3) &
                    ((df['forecast_day_PCT10_change'] < -7) & (df['forecast_day_PCT7_change'] < -7) & (df['forecast_day_PCT5_change'] < -7) & ((df['forecast_day_PCT10_change'] < -10) | (df['forecast_day_PCT7_change'] < -10) | (df['forecast_day_PCT5_change'] < -10)))
                
                )
                |
                (
                    (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                    ((df['monthLowChange'] > 4) | (df['monthHighChange'] > -15) | df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
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
                    (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                    (df['PCT_day_change'] < 2) &
                    (df['PCT_day_change_pre1'] < 2) &
                    (df['PCT_day_change_pre2'] < 2) &
                    ((df['PCT_day_change'] > -1) & (df['PCT_day_change_pre1'] > -1) & (df['PCT_day_change_pre2'] > -1)) &
                    ((df['forecast_day_PCT10_change'] > 7))
                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Crossed Day Lows', color='LG', renderf10sell00=True)


    col0, col1, col2, col3, col4, col5 = st.columns(6)
    with col0:
        df = rb.getdf('supertrend-morning-buy')
        rb.render(st, df, 'Supertrend Morning Buy', color='LG', renderf10buy00=True)
    with col1:
        df = rb.getdf('09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)')
        filtered_df = df
        try:
            filtered_df = df[
                ( (abs(df['forecast_day_PCT10_change']) > 2) | (df['monthLowChange'] < 15) | (df['monthHighChange'] < -4) | df['systemtime'].str.contains('10:', case=False, regex=True, na=False))   
                ]
        except KeyError as e:
            pass
        rb.render(st, filtered_df, 'Crossed 2 Day Highs', color='LG', renderf10buy00=True)
    with col2:
        df = rb.getdf('crossed-day-high')
        filtered_df = df
        try:
            filtered_df = df[
                ( (abs(df['forecast_day_PCT10_change']) > 2) | (df['monthLowChange'] < 15) | (df['monthHighChange'] < -4) | df['systemtime'].str.contains('10:', case=False, regex=True, na=False))   
                ]
        except KeyError as e:
            pass
        rb.render(st, filtered_df, 'Crossed Day Highs', color='LG', renderf10buy00=True)
    with col3:
        df = rb.getdf('supertrend-morning-sell')
        rb.render(st, df, 'Supertrend Morning Sell', color='LG', renderf10sell00=True)
    with col4:
        df = rb.getdf('09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)')
        filtered_df = df
        try:
            filtered_df = df[
                ( (abs(df['forecast_day_PCT10_change']) > 2) | (df['monthLowChange'] > 4) | (df['monthHighChange'] > -15) | df['systemtime'].str.contains('10:', case=False, regex=True, na=False))   
                ]
        except KeyError as e:
            pass
        rb.render(st, filtered_df, 'Crossed 2 Day Lows', color='LG', renderf10sell00=True)
    with col5:
        df = rb.getdf('crossed-day-low')
        filtered_df = df
        try:
            filtered_df = df[
                ( (abs(df['forecast_day_PCT10_change']) > 2) | (df['monthLowChange'] > 4) | (df['monthHighChange'] > -15) | df['systemtime'].str.contains('10:', case=False, regex=True, na=False))   
                ]
        except KeyError as e:
            pass
        rb.render(st, filtered_df, 'Crossed Day Lows', color='LG', renderf10sell00=True)


    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        df = rb.getintersectdf('buy-morning-volume-breakout(Check-News)', 'morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('09:4', case=False, na=False)) &
                (df['yearLowChange'] > 15) &
                (df['forecast_day_PCT10_change'] > -8) &
                (df['PCT_day_change_pre2'] > -0.5) &
                (df['PCT_day_change'] < -1.5)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'buy-morning-volume-breakout(Trending)', column_conf=rb.column_config_default, column_order=rb.column_order_default, renderml=True, color='LG')
    with col2:
        df = rb.getintersectdf('buy-morning-volume-breakout(Check-News)', 'morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('09:4', case=False, na=False)) &
                (df['yearLowChange'] > 15) &
                (df['PCT_day_change'] < 3) &
                (df['PCT_day_change'] > -1.5) &
                ((df['PCT_day_change'] < 1) | (df['PCT_day_change_pre1'] < 1)) &
                (
                    (df['forecast_day_PCT10_change'] > 3) & (df['forecast_day_PCT10_change'] < 10)
                    |
                    ((df['forecast_day_PCT7_change'] < -1.3) & (df['forecast_day_PCT5_change'] < -1.3) & (df['forecast_day_PCT10_change'] > -2) & (df['forecast_day_PCT10_change'] < 10))
                )
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'buy-morning-volume-breakout(Trending)', column_conf=rb.column_config_default, column_order=rb.column_order_default, renderml=True, color='LG')
    with col3:
        df = rb.getdf('buy-morning-volume-breakout(Check-News)')
        filtered_df = df
        rb.render(st, filtered_df, 'buy-morning-volume-breakout(Trending)', column_conf=rb.column_config_default, column_order=rb.column_order_default, renderml=True, color='LG')
    with col4:
        df = rb.getintersectdf('sell-morning-volume-breakout(Check-News)', 'morning-volume-breakout-sell')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('09:4', case=False, na=False)) &
                (df['forecast_day_PCT10_change'] < 8) &
                (df['PCT_day_change_pre2'] < 0.5) &
                (df['PCT_day_change'] > 1.5)
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'sell-morning-volume-breakout(Trending)', column_conf=rb.column_config_default, column_order=rb.column_order_default, renderml=True, color='LG')
    with col5:
        df = rb.getintersectdf('sell-morning-volume-breakout(Check-News)', 'morning-volume-breakout-sell')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('09:4', case=False, na=False)) &
                (df['PCT_day_change'] > -3) &
                (df['PCT_day_change'] < 1.5) &
                ((df['PCT_day_change'] > -1) | (df['PCT_day_change_pre1'] > -1)) &
                (
                    (df['forecast_day_PCT10_change'] < -3) & (df['forecast_day_PCT10_change'] > -10)
                    |
                    ((df['forecast_day_PCT7_change'] > 1.3) & (df['forecast_day_PCT5_change'] > 1.3) & (df['forecast_day_PCT10_change'] < 2) & (df['forecast_day_PCT10_change'] > -10))
                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'sell-morning-volume-breakout(Trending)', column_conf=rb.column_config_default, column_order=rb.column_order_default, renderml=True, color='LG')
    with col6:
        df = rb.getdf('sell-morning-volume-breakout(Check-News)')
        filtered_df = df
        rb.render(st, filtered_df, 'sell-morning-volume-breakout(Trending)', column_conf=rb.column_config_default, column_order=rb.column_order_default, renderml=True, color='LG')


    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        df = rb.getintersectdf('buy-morning-volume-breakout(Check-News)', 'morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['PCT_day_change_pre2'] > -1) | (df['PCT_day_change_pre1'] < 0)) &
                (df['PCT_day_change'] > -1.5) &
                (df['yearLowChange'] > 15) &
                (~df['systemtime'].str.contains('09:', case=False, na=False)) &
                (~df['systemtime'].str.contains('10:00', case=False, na=False)) &
                (~df['systemtime'].str.contains('10:4', case=False, na=False)) &
                (~df['systemtime'].str.contains('10:5', case=False, na=False)) &
                (~df['systemtime'].str.contains('12:', case=False, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, na=False)) 
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'TOP5 : buy-morning-volume-breakout(Trending)', column_conf=rb.column_config_default, column_order=rb.column_order_default, renderml=True, color='LG')
    with col2:
        df = rb.getintersectdf('buy_all_processor', 'buy-morning-volume-breakout(Check-News)')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                #((df['forecast_day_PCT10_change'] > 2) | (df['forecast_day_PCT10_change'] < -6)) &
                (df['PCT_day_change'] > -1.5) &
                (df['forecast_day_PCT10_change'] > -2) &
                (df['forecast_day_PCT10_change'] < 10) &
                (df['yearLowChange'] > 15) &
                (~df['processor'].str.contains('cash-buy-morning-volume')) &
                (~df['processor'].str.contains('Check-News')) &
                (~df['processor'].str.contains('supertrend')) &
                (~df['processor'].str.contains('Sell-morningDown')) &
                (~df['processor'].str.contains('buy-breakout')) &
                (~df['processor'].str.contains('Breakout-Buy-after-10')) &
                (~df['processor'].str.contains('1-Bbuyy-morningUp-downConsolidation')) &
                #(~df['processor'].str.contains('buy-dayconsolidation-breakout-01')) 
                (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('09:4', case=False, regex=True, na=False))
                #(~df['systemtime'].str.contains('11:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'BuyAllProcessor + buy-morning-volume-breakout(Trending)', column_order=rb.column_order_p, color='G')
        else:
            rb.render(st, empty_df, 'BuyAllProcessor + buy-morning-volume-breakout(Trending)', column_order=rb.column_order_p, color='G')
    with col3:
        df = rb.getintersectdf('09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)', 'buy-morning-volume-breakout(Check-News)')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['PCT_day_change_pre2'] > 1) | (df['PCT_day_change_pre1'] > 1)) &
                (df['yearLowChange'] > 15)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Crossed-2Day-High + buy-morning-volume-breakout(Trending)', column_order=rb.column_order_p, color='G')
    with col4:
        df = rb.getintersectdf('sell-morning-volume-breakout(Check-News)', 'morning-volume-breakout-sell')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['PCT_day_change_pre2'] < 1) | (df['PCT_day_change_pre1'] > 0)) &
                (df['PCT_day_change'] < 1.5) &
                (~df['systemtime'].str.contains('09:', case=False, na=False)) &
                (~df['systemtime'].str.contains('10:00', case=False, na=False)) &
                (~df['systemtime'].str.contains('10:4', case=False, na=False)) &
                (~df['systemtime'].str.contains('10:5', case=False, na=False)) &
                (~df['systemtime'].str.contains('12:', case=False, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, na=False)) 
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'TOP5 : sell-morning-volume-breakout(Trending)', column_conf=rb.column_config_default, column_order=rb.column_order_default, renderml=True, color='LG')
    with col5:
        df = rb.getintersectdf('sell_all_processor', 'sell-morning-volume-breakout(Check-News)')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] < 1.5) &
                (df['forecast_day_PCT10_change'] < 2) &
                (df['forecast_day_PCT10_change'] > -10) &
                #((df['forecast_day_PCT10_change'] < -2) | ((df['forecast_day_PCT10_change'] > 6) & (df['forecast_day_PCT5_change'] > 0))) &
                (~df['processor'].str.contains('cash-sell-morning-volume')) &
                (~df['processor'].str.contains('Check-News')) &
                (~df['processor'].str.contains('supertrend')) &
                (~df['processor'].str.contains('Buy-morningup')) &
                (~df['processor'].str.contains('sell-breakout')) &
                (~df['processor'].str.contains('Breakout-Sell-after-10')) &
                (~df['processor'].str.contains('1-Sselll-morningDown')) &
                #(~df['processor'].str.contains('sell-dayconsolidation-breakout-01')) &
                (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('09:4', case=False, regex=True, na=False))
                #(~df['systemtime'].str.contains('11:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'SellAllProcessor + sell-morning-volume-breakout(Trending)', column_order=rb.column_order_p, color='R')
        else:
            rb.render(st, empty_df, 'SellAllProcessor + sell-morning-volume-breakout(Trending)', column_order=rb.column_order_p, color='R') 
    with col6:
        df = rb.getintersectdf('09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)', 'sell-morning-volume-breakout(Check-News)')
        filtered_df = df
        rb.render(st, filtered_df, 'Crossed-2Day-Low + sell-morning-volume-breakout(Trending)', column_order=rb.column_order_p, color='R')


    col0, col1, col2, col3 = st.columns(4)
    with col0:
        df = rb.getdf('Breakout-Beey-2')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df_2 = df[
                    (df['systemtime'].str.contains('09:2', case=False, regex=True, na=False))
                ]

            filtered_df = df[
                (
                    (
                        (df['filter3'].str.startswith('BreakHighYear', na=False)) |
                        (df['filter3'].str.startswith('BreakHighMonth6', na=False)) |
                        (df['filter3'].str.startswith('BreakHighMonth3', na=False)) |
                        (df['filter3'].str.startswith('NearHighYear', na=False)) |
                        (df['filter3'].str.startswith('NearHighMonth6', na=False)) |
                        (df['filter3'].str.startswith('NearHighMonth3', na=False)) |
                        (df['filter3'].str.startswith('ReversalLowYear', na=False)) |
                        (df['filter3'].str.startswith('ReversalLowMonth6', na=False)) |
                        (df['filter3'].str.startswith('ReversalLowMonth3', na=False))
                    ) &
                    (df['PCT_day_change'] > 0.9) &
                    (df['PCT_day_change'] < 1.7) &
                    ((df['yearHighChange'] < -10) | (df['yearHighChange'] > 0))
                )
            ]
            filtered_df = filtered_df[
                (df['systemtime'].str.contains('09:', case=False, regex=True, na=False))
            ]

            if len(filtered_df_2) > 10:
                filtered_df = filtered_df[
                    (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False))&
                    (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Breakout-Beey-2 0.9to1.7', color='LG')
    with col1:
        df = rb.getdf('Breakout-Beey-2')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df_2 = df[
                    (df['systemtime'].str.contains('09:2', case=False, regex=True, na=False))
                ]

            filtered_df = df[
                (
                    (
                        (~df['filter3'].str.startswith('BreakLowYear', na=False)) &
                        (~df['filter3'].str.startswith('BreakLowMonth', na=False))   
                    ) &
                    (df['PCT_day_change'] < 1) &
                    (df['PCT_day_change'] > -1) &
                    (
                        (df['PCT_day_change_pre2'] > 0.1) |
                        ((df['PCT_day_change'] > 0) & (df['PCT_day_change_pre1'] >= -0.1)) |
                        (((df['PCT_day_change_pre1'] + df['PCT_day_change_pre2']) < -4) & (
                            ~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)))
                    )
                )
                ]
            filtered_df = filtered_df[
                (df['systemtime'].str.contains('09:', case=False, regex=True, na=False))
            ]

            if len(filtered_df) > 4 or len(filtered_df_2) > 10:
                filtered_df = filtered_df[
                    (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False))&
                    (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Breakout-Beey-2 -1to1', color='LG')
    with col2:
        df = rb.getdf('Breakout-Siill-2')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df_2 = df[
                    (df['systemtime'].str.contains('09:2', case=False, regex=True, na=False))
                ]

            filtered_df = df[
                (
                    (
                        (df['filter3'].str.startswith('BreakLowYear', na=False)) |
                        (df['filter3'].str.startswith('BreakLowMonth6', na=False)) |
                        (df['filter3'].str.startswith('BreakLowMonth3', na=False)) |
                        (df['filter3'].str.startswith('NearLowYear', na=False)) |
                        (df['filter3'].str.startswith('NearLowMonth6', na=False)) |
                        (df['filter3'].str.startswith('NearLowMonth3', na=False)) |
                        (df['filter3'].str.startswith('ReversalHighYear', na=False)) |
                        (df['filter3'].str.startswith('ReversalHighMonth6', na=False)) |
                        (df['filter3'].str.startswith('ReversalHighMonth3', na=False))
                    ) &
                    (df['PCT_day_change'] < -0.9) &
                    (df['PCT_day_change'] > -1.7) &
                    ((df['yearLowChange'] > 10) | (df['yearLowChange'] < 0))
                )
            ]
            filtered_df = filtered_df[
                (df['systemtime'].str.contains('09:', case=False, regex=True, na=False))
            ]

            if len(filtered_df_2) > 10:
                filtered_df = filtered_df[
                    (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False))&
                    (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Breakout-Siill-2 -1.7to-0.9', color='LG')
    with col3:
        df = rb.getdf('Breakout-Siill-2')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df_2 = df[
                    (df['systemtime'].str.contains('09:2', case=False, regex=True, na=False))
                ]

            filtered_df = df[
                (
                    (
                        (~df['filter3'].str.startswith('BreakHighYear', na=False)) &
                        (~df['filter3'].str.startswith('BreakHighMonth', na=False))  
                    ) &
                    (df['PCT_day_change'] < 1) &
                    (df['PCT_day_change'] > -1) &
                    (
                        (df['PCT_day_change_pre2'] < -0.1) |
                        ((df['PCT_day_change'] < 0) & (df['PCT_day_change_pre1'] <= 0.1)) |
                        (((df['PCT_day_change_pre1'] + df['PCT_day_change_pre2']) > 4) & (
                            ~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)))
                    )
                )
            ]
            filtered_df = filtered_df[
                (df['systemtime'].str.contains('09:', case=False, regex=True, na=False))
            ]

            if len(filtered_df) > 4 or len(filtered_df_2) > 10:
                filtered_df = filtered_df[
                    (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False))&
                    (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Breakout-Siill-2 -1to1', color='LG')
    

    col0, col1, col2, col3 = st.columns(4)
    with col0:
        df = rb.getdf('Breakout-Beey-2')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (df['filter3'].str.startswith('ReversalLow', na=False)) &
                    (df['lowTail'] > 1.5) &
                    (df['highTail'] < 1.3) &
                    (df['PCT_day_change'] < 1) &
                    (df['PCT_day_change_pre1'] < 2)
                )
                |
                (
                    (df['lowTail'] > 1.3) &
                    (df['highTail'] < 1) &
                    ((df['PCT_day_change_pre1'] > 2) | (df['PCT_day_change_pre2'] > 2)) &
                    (df['PCT_day_change'] < -1)
                )
                |
                (
                    ( 1.5 < df['PCT_day_change']) &
                    (df['PCT_day_change'] < 2.5) &
                    (-1.5 < df['PCT_day_change_pre1']) &
                    (df['PCT_day_change_pre1'] < -0.5) &
                    (-1.5 < df['PCT_day_change_pre2']) &
                    (df['PCT_day_change_pre2'] < -0.5)
                )
                ]
            filtered_df = filtered_df[
                    (df['systemtime'].str.contains('09:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df,'Breakout-Beey-2 lowTail GT1.3', color='LG')
    with col1:
        df = rb.getdf('Breakout-Beey-2')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (df['forecast_day_PCT10_change'] > 8) &
                (df['yearLowChange'] > 15) &
                (df['PCT_day_change'] > -1) &
                (df['highTail'] > 1.3) &
                (df['lowTail'] < 1)
            ]
            filtered_df = filtered_df[
                (df['systemtime'].str.contains('09:', case=False, regex=True, na=False))
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Breakout-Beey-2 highTail GT1.3', color='LG')
    with col2:
        df = rb.getdf('Breakout-Siill-2')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (df['filter3'].str.startswith('ReversalHigh', na=False)) &
                    (df['highTail'] > 1.5) &
                    (df['lowTail'] < 1.3) &
                    (df['PCT_day_change'] > -1) &
                    (df['PCT_day_change_pre1'] > -2)
                )
                |
                (
                    (df['highTail'] > 1.3) &
                    (df['lowTail'] < 1) &
                    ((df['PCT_day_change_pre1'] < -2) | (df['PCT_day_change_pre2'] < -2)) &
                    (df['PCT_day_change'] > 1)
                )
                |
                (
                    (-2.5 < df['PCT_day_change']) &
                    (df['PCT_day_change'] < -1.5) &
                    (0.5 < df['PCT_day_change_pre1']) &
                    (df['PCT_day_change_pre1'] < 1.5) &
                    (0.5 < df['PCT_day_change_pre2']) &
                    (df['PCT_day_change_pre2'] < 1.5)
                )
            ]
            filtered_df = filtered_df[
                (df['systemtime'].str.contains('09:', case=False, regex=True, na=False))
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Breakout-Siill-2 highTail GT1.3', color='LG')
    with col3:
        df = rb.getdf('Breakout-Siill-2')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (df['forecast_day_PCT10_change'] < -8) &
                (df['yearHighChange'] < -15) &
                (df['PCT_day_change'] < 1) &
                (df['lowTail'] > 1.3) &
                (df['highTail'] < 1)
            ]
            filtered_df = filtered_df[
                (df['systemtime'].str.contains('09:', case=False, regex=True, na=False))
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Breakout-Siill-2 lowTail GT1.3', color='LG')
    

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        df = rb.getdf('Breakout-Beey-2')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df_2 = df[
                    (df['systemtime'].str.contains('09:2', case=False, regex=True, na=False))
                ]
            if len(filtered_df_2) < 10:
                filtered_df = filtered_df[
                    (~df['systemtime'].str.contains('09:', case=False, regex=True, na=False))
                ]
            else:
                filtered_df = empty_df
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Breakout-Beey-2 after 10', color='LG')
    with col2:
        df = rb.getdf('Breakout-Beey-2')
        rb.render(st, df, 'Breakout-Beey-2', color='LG')
    with col3:
        df = rb.getdf('Breakout-Siill-2')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df_2 = df[
                    (df['systemtime'].str.contains('09:2', case=False, regex=True, na=False))
                ]
            if len(filtered_df_2) < 10:
                filtered_df = filtered_df[
                    (~df['systemtime'].str.contains('09:', case=False, regex=True, na=False))
                ]
            else:
                filtered_df = empty_df
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Breakout-Siill-2 after10', color='LG')
    with col4:
        df = rb.getdf('Breakout-Siill-2')
        rb.render(st, df, 'Breakout-Siill-2', color='LG')

    
    col10, col1, col2, col30, col3, col4 = st.columns(6)
    with col10:
        df = rb.getdf('Breakout-Beey-2')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (df['PCT_day_change'] > 0.5) &
                    (df['PCT_day_change'] < 3) &
                    (df['forecast_day_PCT10_change'] < -5)
                )
            ]
        except KeyError as e:
            print("")
        if len(filtered_df) < 20:
            rb.render(st, filtered_df, 'F10LT-5 - Breakout-Beey-2', color='LG')
        else:
            rb.render(st, empty_df, 'F10LT-5 - Breakout-Beey-2', color='LG')
    with col1:
        df = rb.getdf('Breakout-Beey-2')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                    (
                        (
                            (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                            (~df['systemtime'].str.contains('11:', case=False, na=False))
                            # (df['yearHighChange'] < 0) &
                            # ((df['PCT_day_change_pre1'] > 1) | (df['PCT_day_change_pre2'] > 1)) &
                            # ((df['PCT_day_change_pre1'] < -1) | (df['PCT_day_change_pre2'] < -1)) &
                            # ((df['PCT_day_change_pre1'] < 2) & (df['PCT_day_change_pre2'] < 2)) &
                            # (df['PCT_day_change'] > -1.3) &
                            # (df['PCT_day_change'] < 1)
                        ) 
                    ) 
                    
                ) &
                (
                    (
                        (~df['filter3'].str.contains('ReversalHighYear', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakHighYear2', case=False, regex=True, na=False))
                    ) |
                    (
                        (~df['filter3'].str.contains('ReversalHighYear', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakHighYear2', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakHighYear', case=False, regex=True, na=False))
                    ) |
                    (
                        (~df['filter3'].str.contains('ReversalHighMonth6', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakHighMonth6', case=False, regex=True, na=False))
                    ) |
                    (
                        # (~df['filter3'].str.contains('ReversalHighMonth3', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakHighMonth3', case=False, regex=True, na=False))
                    )
                )
            ]
        except KeyError as e:
            print("")
        if len(filtered_df) < 20:
            rb.render(st, filtered_df, 'BreakHigh - Breakout-Beey-2', color='LG')
        else:
            rb.render(st, empty_df, 'BreakHigh - Breakout-Beey-2', color='LG')
    with col2:
        df = rb.getdf('Breakout-Beey-2')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                    (
                        (
                            (df['yearLowChange'] > 0) &
                            ((df['PCT_day_change_pre1'] < -1) | (df['PCT_day_change_pre2'] < -1)) &
                            ((df['PCT_day_change_pre1'] > -1) | (df['PCT_day_change_pre2'] > -1)) &
                            ((df['PCT_day_change_pre1'] < 2) & (df['PCT_day_change_pre2'] < 2)) &
                            #(df['PCT_day_change'] > -1) &
                            (df['PCT_day_change'] < 1.3)
                        ) |
                        (
                            # (~df['filter3'].str.contains('ReversalLowMonth3', case=False, regex=True, na=False)) &
                            (df['filter3'].str.contains('BreakLowMonth3', case=False, regex=True, na=False))
                        )
                    )
                    
                ) &
                (
                    (
                        (~df['filter3'].str.contains('ReversalLowYear', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakLowYear2', case=False, regex=True, na=False))
                    ) |
                    (
                        (~df['filter3'].str.contains('ReversalLowYear', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakLowYear2', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakLowYear', case=False, regex=True, na=False))
                    ) |
                    (
                        (~df['filter3'].str.contains('ReversalLowMonth5', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakLowMonth6', case=False, regex=True, na=False))
                    ) |
                    (
                        # (~df['filter3'].str.contains('ReversalLowMonth3', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakLowMonth3', case=False, regex=True, na=False))
                    )
                )
            ]
        except KeyError as e:
            print("")
        if len(filtered_df) < 20:
            rb.render(st, filtered_df, 'ReversalBreakLow - Breakout-Beey-2', color='LG')
        else:
            rb.render(st, empty_df, 'ReversalBreakLow - Breakout-Beey-2', color='LG')
    with col30:
        df = rb.getdf('Breakout-Siill-2')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (df['PCT_day_change'] < -0.5) &
                    (df['PCT_day_change'] > -3) &
                    (df['forecast_day_PCT10_change'] > 5)
                )
            ]
        except KeyError as e:
            print("")
        if len(filtered_df) < 20:
            rb.render(st, filtered_df, 'F10GT5 - Breakout-Siill-2', color='LG')
        else:
            rb.render(st, empty_df, 'F10GT5 - Breakout-Siill-2', color='LG')
    with col3:
        df = rb.getdf('Breakout-Siill-2')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                    (
                        (
                            (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                            (~df['systemtime'].str.contains('11:', case=False, na=False)) 
                            # (df['yearLowChange'] > 0) &
                            # ((df['PCT_day_change_pre1'] < -1) | (df['PCT_day_change_pre2'] < -1)) &
                            # ((df['PCT_day_change_pre1'] > 1) | (df['PCT_day_change_pre2'] > 1)) &
                            # ((df['PCT_day_change_pre1'] > -2) & (df['PCT_day_change_pre2'] > -2)) &
                            # (df['PCT_day_change'] > -1) &
                            # (df['PCT_day_change'] < 1.3)
                        )
                    )
                    
                ) &
                (
                    (
                        (~df['filter3'].str.contains('ReversalLowYear', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakLowYear2', case=False, regex=True, na=False))
                    ) |
                    (
                        (~df['filter3'].str.contains('ReversalLowYear', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakLowYear2', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakLowYear', case=False, regex=True, na=False))
                    ) |
                    (
                        (~df['filter3'].str.contains('ReversalLowMonth5', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakLowMonth6', case=False, regex=True, na=False))
                    ) |
                    (
                        # (~df['filter3'].str.contains('ReversalLowMonth3', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakLowMonth3', case=False, regex=True, na=False))
                    )
                )
            ]
        except KeyError as e:
            print("")
        if len(filtered_df) < 20:
            rb.render(st, filtered_df, 'BreakLow - Breakout-Siill-2', color='LG')
        else:
            rb.render(st, empty_df, 'BreakLow - Breakout-Siill-2', color='LG')
    with col4:
        df = rb.getdf('Breakout-Siill-2')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                    (
                        (
                            (df['yearHighChange'] < 0) &
                            ((df['PCT_day_change_pre1'] > 1) | (df['PCT_day_change_pre2'] > 1)) &
                            ((df['PCT_day_change_pre1'] < 1) | (df['PCT_day_change_pre2'] < 1)) &
                            ((df['PCT_day_change_pre1'] > -2) & (df['PCT_day_change_pre2'] > -2)) &
                            (df['PCT_day_change'] > -1.3)
                            # (df['PCT_day_change'] < 1)
                        ) |
                        (
                            # (~df['filter3'].str.contains('ReversalHighMonth3', case=False, regex=True, na=False)) &
                            (df['filter3'].str.contains('BreakHighMonth3', case=False, regex=True, na=False))
                        )
                    )
                    
                ) &
                (
                    (
                        (~df['filter3'].str.contains('ReversalHighYear', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakHighYear2', case=False, regex=True, na=False))
                    ) |
                    (
                        (~df['filter3'].str.contains('ReversalHighYear', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakHighYear2', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakHighYear', case=False, regex=True, na=False))
                    ) |
                    (
                        (~df['filter3'].str.contains('ReversalHighMonth6', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakHighMonth6', case=False, regex=True, na=False))
                    ) |
                    (
                        # (~df['filter3'].str.contains('ReversalHighMonth3', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakHighMonth3', case=False, regex=True, na=False))
                    )
                )
            ]
        except KeyError as e:
            print("")
        if len(filtered_df) < 20:
            rb.render(st, filtered_df, 'ReversalBreakHigh - Breakout-Siill-2', color='LG')
        else:
            rb.render(st, empty_df, 'ReversalBreakHigh - Breakout-Siill-2', color='LG')
    


if __name__ == '__main__':
    main()