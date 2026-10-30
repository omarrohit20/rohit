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
                           page_title="TestLearning",
                           initial_sidebar_state="expanded",)
    except Exception:
        pass

    # main title
    st.title('Learning')

    rb.testLearning = True

    col1, col2 = st.columns(2)
    with col1:
        df = rb._filter_scan_news(rb.getintersectdf_ml('regressionhigh', 'regressionlow'), 'Bullish')
        # df = rb.getintersectdf_ml('regressionhigh', 'regressionlow')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] > -1.3) &
                (df['PCT_day_change'] > -1.3) &
                (df['PCT_day_change'] < 0.5) &
                (df['PCT_change'] < 1) &
                ((df['PCT_day_change_pre1'] > 2 ) | (df['PCT_day_change_pre2'] > 2 )) &
                ((df['PCT_day_change_pre1'] < 1 ) | (df['PCT_day_change_pre2'] < 1 )) &
                # ((df['PCT_day_change_pre1'] < -1 ) | (df['PCT_day_change_pre2'] < -1 )) &
                (df['forecast_day_PCT10_change'] > 8) &
                #(df['forecast_day_PCT10_change'] < 15) &
                ((df['kNeighboursValue_reg'] != 0) | (df['mlpValue_reg'] != 0))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BuyAtOpening:SellIfNiftyLT(-0.5)OrOpenedDown', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='LG')
    with col2:
        df = rb.getintersectdf_ml('regressionhigh', 'regressionlow')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] > 0.5) &
                (df['PCT_day_change'] < 1.5) &
                ((df['lowTail'] > 0.9) | (df['PCT_day_change'] > 0.9)) &
                ((df['PCT_day_change_pre1'] > -2 ) & (df['PCT_day_change_pre2'] > -2 )) &
                ((df['PCT_day_change_pre1'] < -1.3 ) & (df['PCT_day_change_pre2'] < -1.3 )) &
                ((df['kNeighboursValue_reg'] != 0) | (df['mlpValue_reg'] != 0))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BuyAfter10:00-IfLT(-1.5)|SellAfter09:30-IfGT(1)', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='LG')
    
    col3, col4 = st.columns(2)
    with col3:
        df = rb._filter_scan_news(rb.getintersectdf_ml('regressionlow', 'regressionhigh'), 'Bearish')
        # df = rb.getintersectdf_ml('regressionlow', 'regressionhigh')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] < 1.3) &
                (df['PCT_day_change'] < 1.3) &
                (df['PCT_day_change'] > -0.5) &
                (df['PCT_change'] > -1) &
                ((df['PCT_day_change_pre1'] < -2 ) | (df['PCT_day_change_pre2'] < -2 )) &
                ((df['PCT_day_change_pre1'] > -1 ) | (df['PCT_day_change_pre2'] > -1 )) &
                #((df['PCT_day_change_pre1'] > 1 ) | (df['PCT_day_change_pre2'] > 1 )) &
                (df['forecast_day_PCT10_change'] < -8) &
                #(df['forecast_day_PCT10_change'] > -15) &
                ((df['kNeighboursValue_reg'] != 0) | (df['mlpValue_reg'] != 0))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'SellAtOpening:BuyIfNiftyGT(0.5)OrOpenedUp', column_conf=rb.column_config_ml, column_order=rb.column_order_ml,
                  renderml=True, color='LG')
    with col4:
        df = rb.getintersectdf_ml('regressionlow', 'regressionhigh')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] < -0.5) &
                (df['PCT_day_change'] > -1.5) &
                ((df['highTail'] > 0.9) | (df['PCT_day_change'] < -0.9)) &
                ((df['PCT_day_change_pre1'] < 2 ) & (df['PCT_day_change_pre2'] < 2 )) &
                ((df['PCT_day_change_pre1'] > 1.3 ) & (df['PCT_day_change_pre2'] > 1.3 )) &
                ((df['kNeighboursValue_reg'] != 0) | (df['mlpValue_reg'] != 0))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Sell-After-10:00-IfGT(1.5)|BuyAfter09:30-IfLT(-1)', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='LG')

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        df = rb._filter_scan_news(rb.getintersectdf_ml('regressionlow', 'regressionhigh'), 'Bullish')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] > -4.5) &
                (df['PCT_day_change'] > -4) &
                (df['PCT_day_change'] < -2) &
                ((df['PCT_day_change_pre1'] > -2 ) | (df['monthHighChange'] < 0)) &
                ((df['PCT_day_change_pre1'] > 1 ) | (df['PCT_day_change_pre2'] > 1)) &
                (df['forecast_day_PCT5_change'] < 4) &
                (df['forecast_day_PCT10_change'] > 5) &
                ((df['kNeighboursValue_reg'] != 0) | (df['mlpValue_reg'] != 0))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'UpTrendMayBuy', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='LG', height=150)
    with col2:
        df = rb._filter_scan_news(rb.getintersectdf_ml('regressionlow', 'regressionhigh'), 'Bullish')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] > -4.5) &
                (df['PCT_day_change'] > -4) &
                (df['PCT_day_change'] < -2) &
                ((df['PCT_day_change_pre1'] > -2 ) | (df['monthHighChange'] < 0)) &
                ((df['PCT_day_change_pre1'] > 1 ) | (df['PCT_day_change_pre2'] > 1)) &
                (df['forecast_day_PCT5_change'] < 4) &
                (df['forecast_day_PCT10_change'] > 5)
                #((df['kNeighboursValue_reg'] < -2) | (df['mlpValue_reg'] < -2))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'UpTrendMayBuy', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='LG', height=150)
    with col3:
        df = rb._filter_scan_news(rb.getintersectdf_ml('regressionhigh', 'regressionlow'), 'Bearish')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] < 4.5) &
                (df['PCT_day_change'] < 4) &
                (df['PCT_day_change'] > 2) &
                ((df['PCT_day_change_pre1'] < 2 ) | (df['monthLowChange'] > 0)) &
                ((df['PCT_day_change_pre1'] < -1 ) | (df['PCT_day_change_pre2'] < -1)) &
                (df['forecast_day_PCT5_change'] > -4) &
                (df['forecast_day_PCT10_change'] < -5) &
                ((df['kNeighboursValue_reg'] != 0) | (df['mlpValue_reg'] != 0))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'DownTrendMaySell', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='LG', height=150)
    with col4:
        df = rb._filter_scan_news(rb.getintersectdf_ml('regressionhigh', 'regressionlow'), 'Bearish')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] < 4.5) &
                (df['PCT_day_change'] < 4) &
                (df['PCT_day_change'] > 2) &
                ((df['PCT_day_change_pre1'] < 2 ) | (df['monthLowChange'] > 0)) &
                ((df['PCT_day_change_pre1'] < -1 ) | (df['PCT_day_change_pre2'] < -1)) &
                (df['forecast_day_PCT5_change'] > -4) &
                (df['forecast_day_PCT10_change'] < -5) 
                #((df['kNeighboursValue_reg'] > 2) | (df['mlpValue_reg'] > 2))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'DownTrendMaySell', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='LG', height=150)


    st.divider()

    
    col01, col1, col02, col2, col3 = st.columns(5)
    with col01:
        df = rb.getintersectdf('morning-volume-bs', 'cash-buuy')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)

        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] >= 0) &
                (df['PCT_day_change'] <= 1.5) &
                ((df['PCT_day_change'] >=1) | (df['PCT_day_change_pre1'] >=1) | (df['PCT_day_change_pre2'] >=1)) &
                ((df['PCT_change'] >=1) & (df['PCT_day_change_pre1'] >=0) & (df['PCT_day_change_pre2'] >=0)) &
                (~df['systemtime'].str.contains('09:15', case=False, na=False)) 
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'UP: morning-volume-bs', color='LG', renderf10buy01=True, height=300)
    with col1:
        df = rb.getintersectdf('morning-volume-bs', 'cash-buuy')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)

        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('10:', case=False, na=False)) 
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'UP: morning-volume-bs', color='LG', renderf10buy01=True, height=300)
        
    with col02:
        df = rb.getintersectdf('morning-volume-bs', 'cash-seell')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] <= 0) &
                (df['PCT_day_change'] >= -1.5) &
                ((df['PCT_day_change'] <=-1) | (df['PCT_day_change_pre1'] <=-1) | (df['PCT_day_change_pre2'] <=-1)) &
                ((df['PCT_change'] <=-1) & (df['PCT_day_change_pre1'] <=0) & (df['PCT_day_change_pre2'] <=0)) &
                (~df['systemtime'].str.contains('10:', case=False, na=False)) 
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'DOWN: morning-volume-bs', color='LG', renderf10sell01=True, height=300)
    with col2:
        df = rb.getintersectdf('morning-volume-bs', 'cash-seell')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('10:', case=False, na=False)) 
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'DOWN: morning-volume-bs', color='LG', renderf10sell01=True, height=300)
        
    with col3:
        df = rb.getdf('morning-volume-bs')
        rb.render(st, df, 'morning-volume-bs', color='LG', height=300)
    
    
    
    

    col1, col2 = st.columns(2)
    with col1:
        df = rb.getdf('cash-buuy')
        rb.render(st, df, 'cash-buuy', color='LG', renderf10buy01=True,height=300)
    with col2:
        df = rb.getdf('cash-seell')
        rb.render(st, df, 'cash-seell', color='LG', renderf10sell01=True, height=300)



    col0, col1, col2, col3, col4, col5 = st.columns(6)
    with col0:
        df = rb.getdf('supertrend-morning-buy')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('10:3', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:4', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:5', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False)) &
                (((df['forecast_day_PCT10_change']) < -4) | ((df['forecast_day_PCT10_change']) > 4)) &
                (((df['forecast_day_PCT10_change']) < -4) | ((df['PCT_day_change_pre1']) > 1) | ((df['PCT_day_change_pre2']) > 1)) &
                ((df['forecast_day_PCT10_change']) > -15) & 
                ((df['forecast_day_PCT10_change']) < 15)

            ]

            filtered_df = filtered_df[
                (
                    (
                        (
                            (df['mlData'].str.contains("LastUp")) |
                            (df['mlData'].str.contains("LastDown")) |
                            (df['mlData'].str.contains("Last-Up")) |
                            (df['mlData'].str.contains("Last-Down"))
                        )
                        &
                        (((df['forecast_day_PCT10_change']) < -4) | ((df['forecast_day_PCT10_change']) > 4))
                        &
                        (df['PCT_day_change'] < 3)
                    ) 
                    |
                    (
                        (((df['forecast_day_PCT10_change']) < -4) & ((df['forecast_day_PCT5_change']) > -1))
                    )

                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'DOWNTREND : Supertrend Morning Buy', color='LG', renderf10buy01=True)
    with col1:
        df = rb.getdf('09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('10:3', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:4', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:5', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False)) &
                (((df['forecast_day_PCT10_change']) < -4) | ((df['forecast_day_PCT10_change']) > 4)) &
                (((df['forecast_day_PCT10_change']) < -4) | ((df['PCT_day_change_pre1']) > 1) | ((df['PCT_day_change_pre2']) > 1)) &
                ((df['forecast_day_PCT10_change']) > -15) & 
                ((df['forecast_day_PCT10_change']) < 15) 
            ]

            filtered_df = filtered_df[
                (
                    (
                        (
                            (df['mlData'].str.contains("LastUp")) |
                            (df['mlData'].str.contains("LastDown")) |
                            (df['mlData'].str.contains("Last-Up")) |
                            (df['mlData'].str.contains("Last-Down"))
                        ) 
                        &
                        (((df['forecast_day_PCT10_change']) < -4) | ((df['forecast_day_PCT10_change']) > 4))
                        &
                        (df['PCT_day_change'] < 3)
                        &
                        (
                            ((df['highTail'] > 1.5) | (df['lowTail'] > 1.5))
                        )
                    ) 
                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'DOWNTREND : Crossed 2 Day Highs', color='LG', renderf10buy01=True)
    with col2:
        df = rb.getdf('crossed-day-high')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('10:3', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:4', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:5', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False)) &
                (((df['forecast_day_PCT10_change']) < -4)) &
                ((df['forecast_day_PCT10_change']) > -15) & 
                ((df['forecast_day_PCT10_change']) < 15)
            ]

            filtered_df = filtered_df[
                (
                    (
                        (
                            (df['mlData'].str.contains("LastUp")) |
                            (df['mlData'].str.contains("LastDown")) |
                            (df['mlData'].str.contains("Last-Up")) |
                            (df['mlData'].str.contains("Last-Down"))
                        )
                        &
                        (((df['forecast_day_PCT10_change']) < -4) | ((df['forecast_day_PCT10_change']) > 4))
                        &
                        (df['PCT_day_change'] < 3)
                    ) 
                    |
                    (
                        (((df['forecast_day_PCT10_change']) < -4) & ((df['forecast_day_PCT5_change']) > -1))
                    )

                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'DOWNTREND : Crossed Day Highs', color='LG', renderf10buy01=True)
    with col3:
        df = rb.getdf('supertrend-morning-sell')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('10:3', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:4', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:5', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False)) &
                (((df['forecast_day_PCT10_change']) < -4) | ((df['forecast_day_PCT10_change']) > 4)) &
                (((df['forecast_day_PCT10_change']) > 4) | ((df['PCT_day_change_pre1']) < -1) | ((df['PCT_day_change_pre2']) < -1)) &
                ((df['forecast_day_PCT10_change']) > -15) & 
                ((df['forecast_day_PCT10_change']) < 15)
            ]

            filtered_df = filtered_df[
                (
                    (
                        (
                            (df['mlData'].str.contains("LastUp")) |
                            (df['mlData'].str.contains("LastDown")) |
                            (df['mlData'].str.contains("Last-Up")) |
                            (df['mlData'].str.contains("Last-Down"))
                        )
                        &
                        (((df['forecast_day_PCT10_change']) < -4) | ((df['forecast_day_PCT10_change']) > 4))
                        &
                        (df['PCT_day_change'] > -3)
                    ) 
                    |
                    (
                        (((df['forecast_day_PCT10_change']) > 4) & ((df['forecast_day_PCT5_change']) < 1))
                    )

                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'UPTREND : Supertrend Morning Sell', color='LG', renderf10sell01=True)
    with col4:
        df = rb.getdf('09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('10:3', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:4', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:5', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False)) &
                (((df['forecast_day_PCT10_change']) < -4) | ((df['forecast_day_PCT10_change']) > 4)) &
                (((df['forecast_day_PCT10_change']) > 4) | ((df['PCT_day_change_pre1']) < -1) | ((df['PCT_day_change_pre2']) < -1)) &
                ((df['forecast_day_PCT10_change']) > -15) & 
                ((df['forecast_day_PCT10_change']) < 15) 
            ]

            filtered_df = filtered_df[
                (
                    (
                        (
                            (df['mlData'].str.contains("LastUp")) |
                            (df['mlData'].str.contains("LastDown")) |
                            (df['mlData'].str.contains("Last-Up")) |
                            (df['mlData'].str.contains("Last-Down"))
                        ) 
                        &
                        (((df['forecast_day_PCT10_change']) < -4) | ((df['forecast_day_PCT10_change']) > 4))
                        &
                        (df['PCT_day_change'] > -3)
                        &
                        (
                            ((df['highTail'] > 1.5) | (df['lowTail'] > 1.5))
                        )
                    )
                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'UPTREND : Crossed 2 Day Lows', color='LG', renderf10sell01=True)
    with col5:
        df = rb.getdf('crossed-day-low')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('10:3', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:4', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:5', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False)) &
                (((df['forecast_day_PCT10_change']) > 4)) &
                ((df['forecast_day_PCT10_change']) > -15) & 
                ((df['forecast_day_PCT10_change']) < 15)
            ]

            filtered_df = filtered_df[
                (
                    (
                        (
                            (df['mlData'].str.contains("LastUp")) |
                            (df['mlData'].str.contains("LastDown")) |
                            (df['mlData'].str.contains("Last-Up")) |
                            (df['mlData'].str.contains("Last-Down"))
                        )
                        &
                        (((df['forecast_day_PCT10_change']) < -4) | ((df['forecast_day_PCT10_change']) > 4))
                        &
                        (df['PCT_day_change'] > -3)
                    ) 
                    |
                    (
                        (((df['forecast_day_PCT10_change']) > 4) & ((df['forecast_day_PCT5_change']) < 1))
                    )

                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'UPTREND : Crossed Day Lows', color='LG', renderf10sell01=True)



    col0, col1, col2, col3, col4, col5 = st.columns(6)
    with col0:
        df = rb.getdf('supertrend-morning-buy')
        try:
            df = df[
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('12:', case=False, regex=True, na=False))
            ]
        except KeyError as e:
            print("")
        rb.render(st, df, 'Supertrend Morning Buy', color='LG', renderf10buy01=True, height=150)
    with col1:
        df = rb.getdf('09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)')
        try:
            df = df[
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('12:', case=False, regex=True, na=False))
            ]
        except KeyError as e:
            print("")
        rb.render(st, df, 'Crossed 2 Day Highs', color='LG', renderf10buy01=True, height=150)
    with col2:
        df = rb.getdf('crossed-day-high')
        try:
            df = df[
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('12:', case=False, regex=True, na=False))
            ]
        except KeyError as e:
            print("")
        rb.render(st, df, 'Crossed Day Highs', color='LG', renderf10buy01=True, height=150)
    with col3:
        df = rb.getdf('supertrend-morning-sell')
        try:
            df = df[
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('12:', case=False, regex=True, na=False))
            ]
        except KeyError as e:
            print("")
        rb.render(st, df, 'Supertrend Morning Sell', color='LG', renderf10sell01=True, height=150)
    with col4:
        df = rb.getdf('09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)')
        try:
            df = df[
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('12:', case=False, regex=True, na=False))
            ]
        except KeyError as e:
            print("")
        rb.render(st, df, 'Crossed 2 Day Lows', color='LG', renderf10sell01=True, height=150)
    with col5:
        df = rb.getdf('crossed-day-low')
        try:
            df = df[
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('12:', case=False, regex=True, na=False))
            ]
        except KeyError as e:
            print("")
        rb.render(st, df, 'Crossed Day Lows', color='LG', renderf10sell01=True, height=150)

    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        df = rb.getintersectdf('morning-volume-bs', 'cash-buuy')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        if 'scrip' in filtered_df.columns:
            filtered_df = filtered_df.sort_values('scrip')
        rb.render(st, filtered_df, 'UP: morning-volume-bs', color='LG', noColourFilter=True, height=500)
    with col2:
        df = rb.getdf('breakout-morning-buy')
        if 'scrip' in df.columns:
            df = df.sort_values('scrip')
        rb.render(st, df, 'breakout-morning-buy', color='LG', height=500)
    with col3:
        df = rb.getintersectdf('morning-volume-bs', 'cash-seell')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        if 'scrip' in filtered_df.columns:
            filtered_df = filtered_df.sort_values('scrip')
        rb.render(st, filtered_df, 'DOWN: morning-volume-bs', color='LG', noColourFilter=True, height=500)
    with col4:
        df = rb.getdf('breakout-morning-sell')
        if 'scrip' in df.columns:
            df = df.sort_values('scrip')
        rb.render(st, df, 'breakout-morning-sell', color='LG', height=500)


if __name__ == '__main__':
    main()
