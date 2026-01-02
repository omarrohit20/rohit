# Create a streamlit app that shows the mongodb data
from streamlit_autorefresh import st_autorefresh
import streamlit as st
import rbase as rb
import pandas as pd

def main():
    st_autorefresh(interval=30000, key="data_refresher")

    # setting the screen size
    st.set_page_config(layout="wide",
                       page_title="Dashboard",
                       initial_sidebar_state="expanded",)

    # main title
    st.title('10:00 -11:15 AM last 15-20 Minute trend: TrendingMarketOnlyUpDown')

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        df = rb.getdf('supertrend-morningdown-buy')
        filtered_df = df
        rb.render(st, filtered_df, 'UpNow Supertrend MorningDown Buys', color='G')
    with col2:
        df = rb.getintersectdf('buy-check-morning-down-breakup-02', 'crossed-day-high')
        filtered_df = df
        rb.render(st, filtered_df, 'Buy Check Morning Down Breakup 02s', color='G')
    with col3:
        df = rb.getdf('buy-check-morning-down-breakup-02')
        filtered_df = df
        rb.render(st, filtered_df, 'Buy Check Morning Down Breakup 02s', color='LG')
    with col4:
        df = rb.getdf('supertrend-morningup-sell')
        filtered_df = df
        rb.render(st, filtered_df, 'DownNow Supertrend  Morningup Sells', color='R')
    with col5:
        df = rb.getintersectdf('sell-check-morning-up-breakdown-02', 'crossed-day-low')
        filtered_df = df
        rb.render(st, filtered_df, 'Sell Check Morning Up Breakdown 02s', color='R')
    with col6:
        df = rb.getdf('sell-check-morning-up-breakdown-02')
        filtered_df = df
        rb.render(st, filtered_df, 'Sell Check Morning Up Breakdown 02s', color='LG')
    


    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        df = rb.getintersectdf('buy_all_processor', 'supertrend-morning-buy')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('09:', case=False, na=False)) &
                (~df['systemtime_merged'].str.contains('09:2', case=False, na=False)) &
                (~df['systemtime_merged'].str.contains('09:3', case=False, na=False)) &
                (~df['systemtime_merged'].str.contains('09:4', case=False, na=False)) &
                (df['processor'] != 'cash-buy-morning-volume') &
                (df['processor'] != 'supertrend-morning-buy') &
                (df['PCT_day_change'] > -0.5) &
                ((df['forecast_day_PCT10_change'] > 2) | (df['forecast_day_PCT10_change'] < -6)) &
                (~df['processor'].str.contains('09_30:checkChartBuy/', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Buy All Processors + Supertrend Morning Buy', column_order=rb.column_order_p, color='G')
    with col2:
        df = rb.getintersectdf('buy_all_processor', '09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['forecast_day_PCT10_change'] > 2) | (df['forecast_day_PCT10_change'] < -6)) &
                (~df['processor'].str.contains('09_30:checkChartBuy/Sell', case=False, na=False)) &
                (~df['processor'].str.contains('1-Bbuyy-morningUp', case=False, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Buy All Processor    +   Crossed 2 Day High', column_order=rb.column_order_p, color='G')
    with col3:
        df = rb.getintersectdf('buy_all_processor', 'crossed-day-high')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] >= -0.5) &
                (df['PCT_day_change'] <= 1) &
                (df['PCT_change'] < 1) &
                (df['week2HighChange'] > 2) &
                ((df['forecast_day_PCT10_change'] > 2) | (df['forecast_day_PCT10_change'] < -6)) &
                (~df['processor'].str.contains('09_30:checkChartBuy/', case=False, regex=True, na=False)) &
                (~df['processor'].str.contains('1-Bbuyy', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Buy All Processor + Crossed Day High + week2highGT2', column_order=rb.column_order_p, color='G')
    with col4:
        df = rb.getintersectdf('sell_all_processor', 'supertrend-morning-sell')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('09:', case=False, na=False)) &
                (~df['systemtime_merged'].str.contains('09:2', case=False, na=False)) &
                (~df['systemtime_merged'].str.contains('09:3', case=False, na=False)) &
                (~df['systemtime_merged'].str.contains('09:4', case=False, na=False)) &
                (df['processor'] != 'cash-sell-morning-volume') &
                (df['processor'] != 'supertrend-morning-sell') &
                (df['PCT_day_change'] > -0.5) &
                ((df['forecast_day_PCT10_change'] < -2) | (df['forecast_day_PCT10_change'] > 6)) &
                (~df['processor'].str.contains('09_30:checkChartSell/', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Sell All Processors + Supertrend Morning Sell', column_order=rb.column_order_p, color='R')
    with col5:
        df = rb.getintersectdf('sell_all_processor', '09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['forecast_day_PCT10_change'] < -2) | (df['forecast_day_PCT10_change'] > 6)) &
                (~df['processor'].str.contains('09_30:checkChartSell/Buy', case=False, na=False)) &
                (~df['processor'].str.contains('1-Sselll-morningDown', case=False, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Sell All Processor   +   Crossed 2 Day Low', column_order=rb.column_order_p, color='R')
    with col6:
        df = rb.getintersectdf('sell_all_processor', 'crossed-day-low')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['forecast_day_PCT10_change'] < -2) | (df['forecast_day_PCT10_change'] > 6)) &
                (df['week2LowChange'] < -2) &
                (~df['processor'].str.contains('09_30:checkChartSell/', case=False, regex=True, na=False)) &
                (~df['processor'].str.contains('1-Sselll', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Sell All Processor + Crossed Day Low + week2LowChangeLT-2', column_order=rb.column_order_p, color='R')
    
    col0, col1, col2, col00, col3, col4 = st.columns(6)
    with col0:
        df = rb.getdf('supertrend-morning-buy')
        rb.render(st, df, 'Supertrend Morning Buy', color='LG')
    with col1:
        df = rb.getdf('09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)')
        rb.render(st, df, 'Crossed 2 Day Highs', color='LG')
    with col2:
        df = rb.getdf('crossed-day-high')
        rb.render(st, df, 'Crossed Day Highs', color='LG')
    with col00:
        df = rb.getdf('supertrend-morning-sell')
        rb.render(st, df, 'Supertrend Morning Sell', color='LG')
    with col3:
        df = rb.getdf('09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)')
        rb.render(st, df, 'Crossed 2 Day Lows', color='LG')
    with col4:
        df = rb.getdf('crossed-day-low')
        rb.render(st, df, 'Crossed Day Lows', color='LG')


    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        df = rb.getintersectdf('buy_all_processor', 'buy-breakout')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                ((df['forecast_day_PCT10_change'] > 2) | (df['forecast_day_PCT10_change'] < -6)) &
                (~df['processor'].str.contains('buy-breakout')) &
                (~df['processor'].str.contains('supertrend-morning-buy')) &
                (~df['processor'].str.contains('09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)')) &
                (~df['processor'].str.contains('buy-dayconsolidation-breakout-01')) &
                (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('09:4', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'BuyAllProcessor + BuyBreakout', column_order=rb.column_order_p, color='G')
        else:
            rb.render(st, empty_df, 'BuyAllProcessor + BuyBreakout', column_order=rb.column_order_p, color='G')
    with col2:
        df = rb.getdf('buy_all_processor')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['forecast_day_PCT10_change'] > 2) | (df['forecast_day_PCT10_change'] < -6)) &
                (~df['processor'].str.contains('09_30:checkChartSell', case=False, na=False)) &
                (df['mlData'].str.contains('Stairs', case=False, na=False)) &
                (df['mlData'].str.contains('ZPre1', case=False, na=False)) &
                (~df['mlData'].str.contains('DownStairs', case=False, na=False)) &
                (~df['processor'].str.contains('supertrend', case=False, na=False)) &
                (~df['processor'].str.contains('09_30:checkChartBuy/')) &
                (~df['systemtime'].str.contains('09:', case=False, na=False)) &
                (~df['systemtime'].str.contains('10:00:', case=False, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BuyAllProcessor+ZPre1_Upstairs', column_order=rb.column_order_default, color='G')
    with col3:
        df = rb.getdf('morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('09:2', case=False, na=False)) &
                (~df['systemtime'].str.contains('09:30', case=False, na=False)) &
                ((df['forecast_day_PCT10_change'] > 2) | (df['forecast_day_PCT10_change'] < -6)) &
                (df['mlData'].str.contains("0@@CROSSED2") | df['mlData'].str.contains("0@@SUPER"))
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'morning-volume-breakout-buy', color='G')
    with col4:
        df = rb.getintersectdf('sell_all_processor', 'sell-breakout')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                ((df['forecast_day_PCT10_change'] < -2) | (df['forecast_day_PCT10_change'] > 6)) &
                (~df['processor'].str.contains('sell-breakout'))&
                (~df['processor'].str.contains('09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)')) &
                (~df['processor'].str.contains('supertrend-morning-sell'))&
                (~df['processor'].str.contains('sell-dayconsolidation-breakout-01')) &
                (~df['processor'].str.contains('09_30:checkChartSell')) &
                (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('09:3', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('09:4', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'SellAllProcessor + SellBreakout', column_order=rb.column_order_p, color='R')
        else:
            rb.render(st, empty_df, 'SellAllProcessor + SellBreakout', column_order=rb.column_order_p, color='R') 
    with col5:
        df = rb.getdf('sell_all_processor')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['forecast_day_PCT10_change'] < -2) | (df['forecast_day_PCT10_change'] > 6)) &
                (~df['processor'].str.contains('09_30:checkChartBuy', case=False, na=False)) &
                (df['mlData'].str.contains('stairs', case=False, na=False)) &
                (df['mlData'].str.contains('ZPre', case=False, na=False)) &
                (~df['mlData'].str.contains('UpStairs', case=False, na=False)) &
                (~df['processor'].str.contains('supertrend', case=False, na=False)) &
                (~df['processor'].str.contains('09_30:checkChartSell/')) &
                (~df['systemtime'].str.contains('09:', case=False, na=False)) &
                (~df['systemtime'].str.contains('10:00:', case=False, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'SellAllProcessor+ZPre1Down', column_order=rb.column_order_default, color='R')
    with col6:
        df = rb.getdf('morning-volume-breakout-sell')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('09:2', case=False, na=False)) &
                (~df['systemtime'].str.contains('09:30', case=False, na=False)) &
                ((df['forecast_day_PCT10_change'] < -2) | (df['forecast_day_PCT10_change'] > 6)) &
                (df['mlData'].str.contains("0@@CROSSED2") | df['mlData'].str.contains("0@@SUPER"))
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'morning-volume-breakout-sell', color='R')


    col1, col2, col3, col4, col5, col6 = st.columns(6)
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
        rb.render(st, filtered_df, 'CrossedDay:LastDayDownTodayUp#########################################', color='G')
    with col2:
        df = rb.getintersectdf('week2lh-not-reached','crossed-day-high')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                ((abs(df['week2HighChange']) > 2) | (abs(df['weekHighChange']) > 2)) &
                (df['PCT_day_change'] > -1.3) & (df['PCT_day_change'] < 0.7) &
                ((abs(df['PCT_day_change_pre1']) > 1) | (abs(df['PCT_day_change_pre2']) > 1)) &
                (~df['systemtime'].str.contains('09:2', case=False, na=False)) &
                (~df['systemtime'].str.contains('09:3', case=False, na=False)) &
                (~df['systemtime_merged'].str.contains('09:', case=False, na=False)) &
                (~df['systemtime_merged'].str.contains('10:0', case=False, na=False))
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'week2lh-not-reached + CrossedDayHigh(LastDayDOJI)###############', column_order=rb.column_order_p, color='G')
    with col3:
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
        rb.render(st, filtered_df, 'week2lh-not-reached + CrossedDayHigh + (LastDayPCTDayChangeLT-1)', column_order=rb.column_order_p, color='G')
    with col4:
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
        rb.render(st, filtered_df, 'CrossedDay-LastDayUpTodayDown##################################', color='R')
    with col5:
        df = rb.getintersectdf('week2lh-not-reached','crossed-day-low')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                ((abs(df['week2LowChange']) > 2) | (abs(df['weekLowChange']) > 2)) &
                (df['PCT_day_change'] > -0.7) & (df['PCT_day_change'] < 1.3) &
                ((abs(df['PCT_day_change_pre1']) > 1) | (abs(df['PCT_day_change_pre2']) > 1)) &
                (~df['systemtime'].str.contains('09:2', case=False, na=False)) &
                (~df['systemtime'].str.contains('09:3', case=False, na=False)) &
                (~df['systemtime_merged'].str.contains('09:', case=False, na=False)) &
                (~df['systemtime_merged'].str.contains('10:0', case=False, na=False))
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'week2lh-not-reached+CrossedDayLow(LastDayDOJI)#################', column_order=rb.column_order_p, color='R')
    with col6:
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
        rb.render(st, filtered_df, 'week2lh-not-reached + Crossed Day Low + (LastDayPCTDayChangeGT 1)#####', column_order=rb.column_order_p, color='R')


    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        df = rb.getintersectdf('week2lh-not-reached','crossed-day-high')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                ((df['PCT_day_change_pre1'] < -0.3) | (df['PCT_day_change_pre2'] < -0.3)) &
                (~df['systemtime'].str.contains('09:', case=False, na=False)) &
                (~df['systemtime'].str.contains('10:0', case=False, na=False)) &
                (~df['systemtime'].str.contains('10:1', case=False, na=False)) &
                ((df['forecast_day_PCT10_change'] > 4) | (df['forecast_day_PCT10_change'] < -6))
            ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 2:
            rb.render(st, filtered_df, 'week2lh-not-reached + Crossed Day High ###############################', column_conf=rb.column_config_merged, column_order=rb.column_order_p, color='G')
        else:
            rb.render(st, filtered_df, 'week2lh-not-reached + Crossed Day High ###############################', column_conf=rb.column_config_merged, column_order=rb.column_order_p, color='G')
    with col2:
        df = rb.getdf('crossed-day-high')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('09:', case=False, na=False)) &
                (~df['systemtime'].str.contains('10:0', case=False, na=False)) &
                (~df['systemtime'].str.contains('10:1', case=False, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                ((df['forecast_day_PCT10_change'] > 2) | (df['forecast_day_PCT10_change'] < -6)) &
                (df['PCT_day_change'] > -1) & (df['PCT_day_change'] < 1) &
                (df['PCT_day_change_pre1'] > -1.5) & (df['PCT_day_change_pre1'] < 1.5) &
                (df['PCT_day_change_pre2'] < 2)
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Crossed Day Highs ########################################################', column_order=rb.column_order_p, color='G')
    with col3:
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
        rb.render(st, filtered_df, 'BUY: week2lh-not-reached + Crossed Day Low\High + (Last2DayPCTChangeLT-1)', column_order=rb.column_order_p, color='G')
    with col4:
        df = rb.getintersectdf('week2lh-not-reached','crossed-day-low')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                ((df['PCT_day_change_pre1'] > 0.3) | (df['PCT_day_change_pre2'] > 0.3)) &
                (~df['systemtime'].str.contains('09:', case=False, na=False)) &
                (~df['systemtime'].str.contains('10:0', case=False, na=False)) &
                (~df['systemtime'].str.contains('10:1', case=False, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                ((df['forecast_day_PCT10_change'] < -4) | (df['forecast_day_PCT10_change'] > 6))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 2:
            rb.render(st, filtered_df, 'week2lh-not-reached + Crossed Day Low ##############################', column_conf=rb.column_config_merged, column_order=rb.column_order_p, color='R')
        else:
            rb.render(st, filtered_df, 'week2lh-not-reached + Crossed Day Low ##############################', column_conf=rb.column_config_merged, column_order=rb.column_order_p, color='R')
    with col5:
        df = rb.getdf('crossed-day-low')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('09:', case=False, na=False)) &
                (~df['systemtime'].str.contains('10:0', case=False, na=False)) &
                (~df['systemtime'].str.contains('10:1', case=False, na=False)) &
                ((df['forecast_day_PCT10_change'] < -2) | (df['forecast_day_PCT10_change'] > 6)) &
                (df['PCT_day_change'] > -1) & (df['PCT_day_change'] < 1) &
                (df['PCT_day_change_pre1'] > -1.5) & (df['PCT_day_change_pre1'] < 1.5) &
                (df['PCT_day_change_pre2'] > -2)
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Crossed Day Lows ######################################################', color='R')
    with col6:
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
        rb.render(st, filtered_df, 'SELL: week2lh-not-reached + Crossed Day High\Low + (Last2DayPCTChangeGT1)', column_order=rb.column_order_p, color='R')
    


if __name__ == '__main__':
    main()
