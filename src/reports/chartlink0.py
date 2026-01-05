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
    st.title('9:20 - 09:40 Morning : chartlink-0')

    # Navigation hint
    st.sidebar.info("Need other report pages? Run `streamlit run src/reports/index.py` and choose pages from the Reports Index.")

    # page-specific flags
    rb.chartlink0 = True
    try:
        rb.chartlink1 = False
    except Exception:
        pass

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        df = rb.getdf('morning-volume-breakout-buy')
        rb.render(st, df, 'morning-volume-breakout-buy ##############', color='G', height=300)
    with col2:
        df = rb.getdf('morning-volume-breakout-buy')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] > -1) &
                (df['PCT_day_change'] < 1.5) &
                (df['PCT_day_change_pre1'] < 2) &
                #((df['PCT_day_change_pre1'] > 0) | (df['PCT_day_change_pre2'] > 0)) &
                (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) < 20:
            rb.render(st, filtered_df, 'MorningDown:ABSLT1-CheckRecommendations', color='LG', height=300)
        else:
            rb.render(st, empty_df, 'MorningDown:ABSLT1-CheckRecommendations', color='LG', height=300)
    with col3:
        df = rb.getdf('morning-volume-breakout-sell')
        rb.render(st, df, 'morning-volume-breakout-sell ######################', color='R', height=300)
    with col4:
        df = rb.getdf('morning-volume-breakout-sell')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] > -1.5) &
                (df['PCT_day_change'] < 1) &
                (df['PCT_day_change_pre1'] > -2) &
                #((df['PCT_day_change_pre1'] < 0) | (df['PCT_day_change_pre2'] < 0)) &
                (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) < 20:
            rb.render(st, filtered_df, 'MorningUp:ABSLT1-CheckRecommendations', color='LG', height=300)
        else:
            rb.render(st, empty_df, 'MorningUp:ABSLT1-CheckRecommendations', color='LG', height=300)
    

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        df = rb.getdf('morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] < 3) &
                (df['PCT_change'] < 3) &
                (
                    df['mlData'].str.contains("#UpStairs") | 
                    df['mlData'].str.contains("UpPostLunchConsolidation")
                ) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayUpTodayOpenedGT0.3:PreUpstairs-CheckRecommendations(+)', color='LG')
    with col2:
        df = rb.getdf('morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['forecast_day_PCT10_change'] > 3.5) | ((df['forecast_day_PCT10_change'] < -6) & (df['forecast_day_PCT5_change'] < 0))) &
                (df['yearLowChange'] > 10) &
                (df['yearHighChange'] >= -70) &
                #(df['month3HighChange'] > -15) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                ((df['mlData'].str.contains("Z&&&") & (df['yearHighChange'] <= -10)) |
                    (
                        (df['week2HighChange'] > -1) &
                        (df['monthHighChange'] < 5) &
                        (df['yearHighChange'] > -35) &
                        (df['PCT_day_change'] > -0.7) &
                        (df['PCT_day_change'] < 0.7) &
                        (~df['filter5'].str.contains('BothGT2', case=False, regex=True, na=False)) &
                        (df['lowTail'] < 1.5) &
                        (df['forecast_day_PCT10_change'] > -1) &
                        (df['week2LowChange'] > 0) &
                        ((df['PCT_day_change_pre1'] > 1) | (df['PCT_day_change_pre2'] > 1)) &
                        (df['PCT_day_change_pre2'] < 3.5) &
                        (df['mlData'].str.contains("TOP"))
                    ) |
                    (
                        (df['PCT_day_change'] < 2.5) &
                        (df['PCT_day_change'] > -3) &
                        (df['PCT_change'] > 0) &
                        (df['month3HighChange'] > -20) &
                        (df['year5HighChange'] < -25) &
                        (df['yearHighChange'] < -20)
                    )
                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'SQROFFAt10:LastDayUpTodayGT0.3:Consolidation-CheckRecommendations', color='LG')
    with col3:
        df = rb.getdf('morning-volume-breakout-sell')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] > -3) &
                (df['PCT_change'] > -3) &
                (
                    df['mlData'].str.contains("#DownStairs") | 
                    df['mlData'].str.contains("DownPostLunchConsolidation")
                ) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayDownTodayOpenedLT-0.3:PreDownstairs-CheckRecommendations(-)', color='LG')
    with col4:
        df = rb.getdf('morning-volume-breakout-sell')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['forecast_day_PCT10_change'] < -3.5) | ((df['forecast_day_PCT10_change'] > 6) & (df['forecast_day_PCT5_change'] > 0))) &
                (df['yearHighChange'] < -10) &
                (df['yearlowChange'] < 70) &
                #(df['month3LowChange'] < 15) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                (df['mlData'].str.contains("Z&&&")) 
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'SQROFFAt10:LastDayDownTodayLT-0.3:Consolidation-CheckRecommendations', color='LG')

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        df = rb.getdf('morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] > 1.5) &
                (df['PCT_day_change'] < 4) &
                (df['PCT_change'] > 1.8) &
                (df['PCT_change'] < 4) &
                (df['PCT_day_change_pre1'] > -1.3) &
                (df['PCT_day_change_pre1'] < 1) &
                (df['PCT_day_change_pre2'] > -2.3) &
                (df['PCT_day_change_pre2'] < 1) &
                ((df['mlData'].str.contains("TOP") | df['systemtime'].str.contains("09:20"))) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayGT1:TodayNotDown(Aftert09:45-IfGT1.3(+))', color='LG', height=150)
    with col2:
        df = rb.getdf('morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] > -3) &
                (df['PCT_day_change'] < -1.75) &
                (df['PCT_day_change_pre1'] < 0) &
                ((df['mlData'].str.contains("TOP") | df['systemtime'].str.contains("09:20"))) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayGT1:TodayNotDown : Uptrend(-)', color='LG', height=150)
    with col3:
        df = rb.getdf('morning-volume-breakout-sell')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] > -4) &
                (df['PCT_day_change'] < -1.5) &
                (df['PCT_change'] > -4) &
                (df['PCT_change'] < -1.75) &
                (df['PCT_day_change_pre1'] > -1) &
                (df['PCT_day_change_pre1'] < 1.3) &
                (df['PCT_day_change_pre2'] > -1) &
                (df['PCT_day_change_pre2'] < 2.3) &
                ((df['mlData'].str.contains("TOP") | df['systemtime'].str.contains("09:20"))) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")

        rb.render(st, filtered_df, 'LastDayLT-1:TodayNotUp(Aftert09:45-IfLT-1.3(-))', color='LG', height=150)
    with col4:
        df = rb.getdf('morning-volume-breakout-sell')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] > 1.75) &
                (df['PCT_day_change'] < 3) &
                (df['PCT_day_change_pre1'] > 0) &
                ((df['mlData'].str.contains("TOP") | df['systemtime'].str.contains("09:20"))) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayLT-1:TodayNotUp : Downtrend(+)', color='LG', height=150)

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
                (df['week2LowChange'] < 15) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'RISKY:LDayMarketUpTodayUp(+)', color='LG', height=150)
    with col2:
        df = rb.getdf('morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['weekLowChange'] > -0.3) | (df['weekLowChange'] < -3)) &
                (df['week2LowChange'] < 5) &
                (df['week2HighChange'] < -2) &
                (df['PCT_day_change'] > -3.5) &
                (df['PCT_day_change'] < -1.5) &
                (df['PCT_change'] > -4) &
                (df['PCT_change'] < -1) &
                (df['month3HighChange'] > -15) &
                (df['PCT_day_change_pre1'] > -1) &
                (df['highTail'] < 1) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False))
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayMarketLT-1:OrDowntrend : todayUpGT0.5(-)', color='G', height=150)
    with col3:
        df = rb.getdf('morning-volume-breakout-sell')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] > -7) &
                (df['PCT_day_change'] < -4) &
                (~df['filter5'].str.contains("BothLT-1.5")) &
                (df['week2HighChange'] > -15) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'RISKY:LDayMarketDownTodayDown(-)', color='LG', height=150)
    with col4:
        df = rb.getdf('morning-volume-breakout-sell')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['weekHighChange'] < 0) | (df['weekHighChange'] > 3)) &
                (df['week2LowChange'] > 2) &
                (df['week2HighChange'] > -5) &
                (df['PCT_day_change'] > 0.75) &
                (df['PCT_day_change'] < 4.5) &
                (df['PCT_change'] > 1) &
                (df['PCT_change'] < 4.5) &
                (df['month3LowChange'] < 10) &
                (df['filter5'].str.contains("PRE1or2GT1")) &
                (df['lowTail'] < 1) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayMarketGT1:OrUptrend : todayDownLT-0.5(+)', color='R', height=150)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        df = rb.getdf('morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] < -3.5) &
                (df['PCT_change'] < -3.5) &
                (df['week2LowChange'] < 0) &
                (df['yearHighChange'] < 0) &
                (~df['systemtime'].str.contains("09:20")) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayDownTodayUp:buyAfterSettledA10(-)', color='LG', height=150)
    with col2:
        df = rb.getdf('morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['year5HighChange'] < 0) &
                (df['lowTail'] < 1.5) &
                (df['PCT_day_change'] < -1.5) &
                (df['PCT_change'] < -1.5) &
                (df['month3HighChange'] < -10) &
                (df['week2HighChange'] < 5) &
                (df['week2LowChange'] > 0) &
                (df['filter5'].str.contains("AnyLT-1")) &
                (df['month3LowChange'] > 0) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayMarketLT-1 : todayUpGT0.5(-)', color='G', height=150)
    with col3:
        df = rb.getdf('morning-volume-breakout-sell')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] > 3.5) &
                (df['PCT_change'] > 3.5) &
                (df['week2HighChange'] > 0) &
                (df['yearLowChange'] > 0) &
                (~df['systemtime'].str.contains("09:20")) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayUpTodayDown:sellAfterSettledA10(+)', color='LG', height=150)
    with col4:
        df = rb.getdf('morning-volume-breakout-sell')
        filtered_df = df
        try:
            filtered_df = df[
                (df['highTail'] < 1.5) &
                (df['PCT_day_change'] > 1.5) &
                (df['PCT_change'] > 1.5) &
                (df['month3LowChange'] > 10) &
                (df['week2HighChange'] < 0) &
                (df['week2LowChange'] > -5) &
                (df['filter5'].str.contains("AnyGT1")) &
                (df['month3HighChange'] < 0) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayMarketGT1 : todayDownLT-0.5(+)', color='R', height=150)


    col1, col2, col3, col30, col4, col5, col6, col60 = st.columns(8)
    with col1:
        df = rb.getdf('morning-volume-breakout-buy')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (df['forecast_day_PCT10_change'] >= 1) &
                (df['forecast_day_PCT10_change'] <= 3) &
                (df['PCT_day_change_pre1'] > -0.1) &
                (df['PCT_day_change_pre2'] > -0.1) &
                (df['PCT_day_change_pre1'] < 1.3) &
                (df['PCT_day_change_pre2'] < 1.3) &
                ((df['PCT_day_change'] > 1) | (df['PCT_day_change_pre1'] > 1) | (df['PCT_day_change_pre2'] > 1)) &
                (df['mlData'].str.contains('#TOP', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(df) > 5:
            rb.render(st, filtered_df, 'Buy Momentum', color='G', height=200)
        else:
            rb.render(st, empty_df, 'Buy Momentum', color='G', height=200)
    with col2:
        df = rb.getdf('morning-volume-breakout-buy')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (df['forecast_day_PCT10_change'] > 2) &
                ((df['PCT_day_change'] < -1.3) | (df['PCT_day_change_pre1'] < -1.3)) &
                ((df['PCT_day_change'] < 0.5) & (df['PCT_day_change_pre1'] < 0.5)) &
                ((df['PCT_day_change'] > -3) & (df['PCT_day_change_pre1'] > -3)) &
                (df['PCT_day_change_pre2'] > -1) &
                #(df['mlData'].str.contains('#TOP', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(df) > 5:
            rb.render(st, filtered_df, 'Buy Momentum', color='G', height=200)
        else:
            rb.render(st, empty_df, 'Buy Momentum', color='G', height=200)
    with col3:
        df = rb.getdf('morning-volume-breakout-buy')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                ((df['forecast_day_PCT10_change'] < -6) & (df['forecast_day_PCT5_change'] < 0)) &
                ((df['PCT_day_change'] < -2) | (df['PCT_day_change_pre1'] < -2)) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False))
            ]
        except KeyError as e:
            print("")
        if len(df) > 5:
            rb.render(st, filtered_df, 'Short Covering', color='G', height=200)
        else:
            rb.render(st, empty_df, 'Short Covering', color='G', height=200)
    with col30:
        df = rb.getdf('morning-volume-breakout-buy')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (df['forecast_day_PCT10_change'] < -3) &
                (df['PCT_day_change'] > 1.5) &
                (~df['systemtime'].str.contains('9:2', case=False, regex=True, na=False))
            ]
        except KeyError as e:
            print("")
        if len(df) > 5:
            rb.render(st, filtered_df, 'Short Cover Continue', color='G', height=200)
        else:
            rb.render(st, empty_df, 'Short Cover Continue', color='G', height=200)
    with col4:
        df = rb.getdf('morning-volume-breakout-sell')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (df['forecast_day_PCT10_change'] >= -3) &
                (df['forecast_day_PCT10_change'] <= -1) &
                (df['PCT_day_change_pre1'] < 0.1) &
                (df['PCT_day_change_pre2'] < 0.1) &
                (df['PCT_day_change_pre1'] > -1.3) &
                (df['PCT_day_change_pre2'] > -1.3) &
                ((df['PCT_day_change'] < -1) | (df['PCT_day_change_pre1'] < -1) | (df['PCT_day_change_pre2'] < -1)) &
                (df['mlData'].str.contains('#TOP', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(df) > 5:
            rb.render(st, filtered_df, 'Sell Momentum', color='R', height=200)
        else:
            rb.render(st, empty_df, 'Sell Momentum', color='R', height=200)
    with col5:
        df = rb.getdf('morning-volume-breakout-sell')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (df['forecast_day_PCT10_change'] < -2) &
                ((df['PCT_day_change'] > 1.3) | (df['PCT_day_change_pre1'] > 1.3)) &
                ((df['PCT_day_change'] > -0.5) & (df['PCT_day_change_pre1'] > -0.5)) &
                ((df['PCT_day_change'] < 3) & (df['PCT_day_change_pre1'] < 3)) &
                (df['PCT_day_change_pre2'] < 1) &
                #(df['mlData'].str.contains('#TOP', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(df) > 5:
            rb.render(st, filtered_df, 'Sell Momentum', color='G', height=200)
        else:
            rb.render(st, empty_df, 'Sell Momentum', color='G', height=200)
    with col6:
        df = rb.getdf('morning-volume-breakout-sell')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                ((df['forecast_day_PCT10_change'] > 6) & (df['forecast_day_PCT5_change'] > 0)) &
                ((df['PCT_day_change'] > 2) | (df['PCT_day_change_pre1'] > 2)) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False))
            ]
        except KeyError as e:
            print("")
        if len(df) > 5:
            rb.render(st, filtered_df, 'Profit Booking', color='R', height=200)
        else:
            rb.render(st, empty_df, 'Profit Booking', color='R', height=200)
    with col60:
        df = rb.getdf('morning-volume-breakout-sell')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (df['forecast_day_PCT10_change'] > 3) &
                (df['PCT_day_change'] < -1.5) &
                (~df['systemtime'].str.contains('9:2', case=False, regex=True, na=False))
            ]
        except KeyError as e:
            print("")
        if len(df) > 5:
            rb.render(st, filtered_df, 'Profit Book Continue', color='R', height=200)
        else:
            rb.render(st, empty_df, 'Profit Book Continue', color='R', height=200)


    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        df = rb.getdf('morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                df['mlData'].str.contains("Z&&&") &
                df['mlData'].str.contains("0@@SUPER")
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'SuperTrend-ConsolidationBuy', color='G')
    with col2:
        df = rb.getdf('morning-volume-breakout-buy')
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                (df['mlData'].str.contains("MLBuy") | 
                    (
                        df['mlData'].str.contains("MLhighBuy") &
                        ~df['systemtime'].str.contains('09:5', case=False, regex=True, na=False)
                    )
                ) 
                ]
        except KeyError as e:
            print("")
        if len(df) > 5:
            rb.render(st, filtered_df, 'MLBuy', color='G', height=200)
        else:
            rb.render(st, empty_df, 'MLBuy', color='G', height=200)
    with col3:
        df = rb.getdf('morning-volume-breakout-buy')
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (df['filter'].str.contains("[MLBuy]:")) &
                (abs(df['PCT_day_change']) < 2) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(df) > 5:
            rb.render(st, filtered_df, 'MLBuy', color='G', height=200)
        else:
            rb.render(st, empty_df, 'MLBuy', color='G', height=200)
    with col4:
        df = rb.getdf('morning-volume-breakout-sell')
        filtered_df = df
        try:
            filtered_df = df[
                df['mlData'].str.contains("Z&&&") &
                df['mlData'].str.contains("0@@SUPER")
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'SuperTrend-ConsolidationSell', color='R')
    with col5:
        df = rb.getdf('morning-volume-breakout-sell')
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                (df['mlData'].str.contains("MLSell") | 
                    (
                        df['mlData'].str.contains("MLlowSell") &
                        ~df['systemtime'].str.contains('09:5', case=False, regex=True, na=False)
                    )
                ) 
                ]
        except KeyError as e:
            print("")
        if len(df) > 5:
            rb.render(st, filtered_df, 'MLSell', color='R', height=200)
        else:
            rb.render(st, empty_df, 'MLSell', color='R', height=200)
    with col6:
        df = rb.getdf('morning-volume-breakout-sell')
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (df['filter'].str.contains("MLSell")) &
                (abs(df['PCT_day_change']) < 2) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False))
            ]
        except KeyError as e:
            print("")
        if len(df) > 5:
            rb.render(st, filtered_df, 'MLSell', color='R', height=200)
        else:
            rb.render(st, empty_df, 'MLSell', color='R', height=200)


if __name__ == '__main__':
    main()








