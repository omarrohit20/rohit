# Create a streamlit app that shows the mongodb data
from streamlit_autorefresh import st_autorefresh
import streamlit as st
import rbase as rb
import pandas as pd


# Run the autorefresh approximately every 30000 milliseconds (30 seconds)

def main():
    #st_autorefresh(interval=30000, key="data_refresher")

    # setting the screen size (ignore if already set by index)
    try:
        st.set_page_config(layout="wide",
                           page_title="DashboardShortTerm",
                           initial_sidebar_state="expanded",)
    except Exception:
        pass

    # main title
    st.title('ShortTerm')

    rb.testLearning = True

    col0, col1 = st.columns(2)
    with col0:
        df = rb.getintersectdf('Breakout-Beey-2', 'breakoutYH')
        #df = rb.getdf_sandlterm('breakoutYH')
        rb.render_sandlterm_data(st, df,'breakoutYH', color='G')
    with col1:
        df = rb.getintersectdf('Breakout-Beey-2', 'breakoutY2H')
        #df = rb.getdf_sandlterm('breakoutY2H')
        rb.render_sandlterm_data(st, df,'breakoutY2H', color='G')


    col0, col1, col2, col3 = st.columns(4)
    with col0:
        df = rb.getintersectdf('Breakout-Beey-2', 'breakoutW2HR')
        #df = rb.getdf_sandlterm('breakoutW2HR')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['monthHighChange'] < -3) | (df['month3HighChange'] < -15)) &
                ((df['monthHighChange'] > -5.5) | (df['month3HighChange'] < -20)) &
                (df['week2LowChange'] < 5.5) &
                (df['week2LowChange'] != df['weekLowChange']) &
                ((df['yearLowChange'] > 0) | (df['month2HighChange'] > -10))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df,'breakoutW2HR', color='G')
    with col1:
        df = rb.getintersectdf('Breakout-Beey-2', 'breakoutW2HR')
        #df = rb.getdf_sandlterm('breakoutW2HR')
        filtered_df = df
        try:
            filtered_df = df[
                (df['monthHighChange'] > -3.5) &
                ((df['monthHighChange'] < -3) | (df['month3HighChange'] < -15))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df,'breakoutW2HR', color='G')
    with col2:
        df = rb.getintersectdf('Breakout-Beey-2', 'breakoutW2HR')
        #df = rb.getdf_sandlterm('breakoutW2HR')
        rb.render(st, df,'breakoutW2HR', color='LG')
    with col3:
        df = rb.getintersectdf('Breakout-Siill-2', 'breakoutW2LR')
        #df = rb.getdf_sandlterm('breakoutW2HR')
        rb.render(st, df,'breakoutW2LR', color='LG')

    col0, col1, col2, col3 = st.columns(4)
    with col0:
        df = rb.getintersectdf('Breakout-Beey-2', 'breakoutMHR')
        #df = rb.getdf_sandlterm('breakoutMHR')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['monthHighChange'] < -3) | (df['month3HighChange'] < -15)) &
                ((df['monthHighChange'] > -5.5) | (df['month3HighChange'] < -20)) &
                (df['week2LowChange'] < 5.5) &
                (df['week2LowChange'] != df['weekLowChange']) &
                ((df['yearLowChange'] > 0) | (df['month2HighChange'] > -10))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df,'breakoutMHR', color='LG')
    with col1:
        df = rb.getintersectdf('Breakout-Beey-2', 'breakoutMHR')
        #df = rb.getdf_sandlterm('breakoutMHR')
        try:
            filtered_df = df[
                (df['year5HighChange'] < -30) &
                (df['year2HighChange'] < -10) &
                (df['month3HighChange'] < -5)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df,'breakoutMHR', color='LG')
    with col2:
        df = rb.getintersectdf('Breakout-Beey-2', 'breakoutMHR')
        #df = rb.getdf_sandlterm('breakoutMHR')
        rb.render(st, df,'breakoutMHR', color='LG')
    with col3:
        df = rb.getintersectdf('Breakout-Siill-2', 'breakoutMLR')
        #df = rb.getdf_sandlterm('breakoutW2HR')
        rb.render(st, df,'breakoutMLR', color='LG')

    col0, col1, col2, col3 = st.columns(4)
    with col0:
        df = rb.getintersectdf('Breakout-Beey-2', 'breakoutM2HR')
        #df = rb.getdf_sandlterm('breakoutM2HR')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['monthHighChange'] < -3) | (df['month3HighChange'] < -15)) &
                ((df['monthHighChange'] > -5.5) | (df['month3HighChange'] < -20)) &
                (df['week2LowChange'] < 5.5) &
                (df['week2LowChange'] != df['weekLowChange']) &
                ((df['yearLowChange'] > 0) | (df['month2HighChange'] > -10))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'breakoutM2HR', color='LG')
    with col1:
        df = rb.getintersectdf('Breakout-Beey-2', 'breakoutM2HR')
        #df = rb.getdf_sandlterm('breakoutM2HR')
        filtered_df = df
        try:
            filtered_df = df[
                (df['monthHighChange'] > -3.5) &
                ((df['monthHighChange'] < -3) | (df['month3HighChange'] < -15))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'breakoutM2HR', color='LG')
    with col2:
        df = rb.getintersectdf('Breakout-Beey-2', 'breakoutM2HR')
        #df = rb.getdf_sandlterm('breakoutM2HR')
        rb.render(st, df, 'breakoutM2HR', color='LG')
    with col3:
        df = rb.getintersectdf('Breakout-Siill-2', 'breakoutM2LR')
        #df = rb.getdf_sandlterm('breakoutW2HR')
        rb.render(st, df,'breakoutM2LR', color='LG')
    

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        df = rb.getintersectdf('buy_all_processor', 'breakoutW2HR')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] > (df['PCT_day_change'] + 0.2)) &
                (abs(df['PCT_day_change']) >= 0.35) &
                (abs(df['yearHighChange']) >= 10) &
                (abs(df['month3HighChange']) >= 5) &
                (abs(df['monthHighChange']) >= 2.5) &
                (abs(df['yearLowChange']) >= 5) &
                (~df['processor'].str.contains('cash-buy-morning-volume')) &
                (~df['processor'].str.contains('Check-News')) &
                (~df['processor'].str.contains('supertrend')) &
                (~df['processor'].str.contains('09_30:checkChartBuy')) &
                (~df['processor'].str.contains('Sell-morningDown')) &
                #(~df['processor'].str.contains('buy-breakout')) &
                (~df['processor'].str.contains('Breakout-Buy-after-10')) &
                (~df['processor'].str.contains('1-Bbuyy-morningUp')) &
                # (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:00', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:05', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'BuyAllProcessor + week2lh-not-reached', color='LG', applyBreakOut=True)
        else:
            rb.render(st, empty_df, 'BuyAllProcessor + week2lh-not-reached', color='LG', applyBreakOut=True)
    with col2:
        df = rb.getintersectdf('buy_all_processor', 'breakoutW2HR')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                ((df['PCT_day_change_pre1'] < 1.7) & (df['PCT_day_change_pre2'] < 1.7)) &
                ((df['PCT_day_change_pre1'] > 0) | (df['PCT_day_change_pre2'] > 0)) &
                (abs(df['month3HighChange']) >= 5) &
                # ((df['forecast_day_PCT10_change'] >=2) | (df['forecast_day_PCT10_change'] <= -6)) &
                (~df['processor'].str.contains('cash-buy-morning-volume')) &
                (~df['processor'].str.contains('Check-News')) &
                (~df['processor'].str.contains('supertrend')) &
                (~df['processor'].str.contains('09_30:checkChartBuy')) &
                (~df['processor'].str.contains('Sell-morningDown')) &
                #(~df['processor'].str.contains('buy-breakout')) &
                (~df['processor'].str.contains('Breakout-Buy-after-10')) &
                (~df['processor'].str.contains('1-Bbuyy-morningUp')) &
                # (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:00', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:05', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'BuyAllProcessor + week2lh-not-reached', color='LG', applyBreakOut=True)
        else:
            rb.render(st, empty_df, 'BuyAllProcessor + week2lh-not-reached', color='LG', applyBreakOut=True)
    with col3:
        df = rb.getintersectdf('sell_all_processor', 'breakoutW2LR')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] < (df['PCT_day_change'] - 0.2)) &
                (abs(df['PCT_day_change']) >= 0.35) &
                (abs(df['yearLowChange']) >= 10) &
                (abs(df['month3LowChange']) >= 5) &
                (abs(df['monthLowChange']) >= 2.5) &
                (abs(df['yearHighChange']) >= 5) &
                (~df['processor'].str.contains('cash-sell-morning-volume')) &
                (~df['processor'].str.contains('Check-News')) &
                (~df['processor'].str.contains('supertrend')) &
                (~df['processor'].str.contains('09_30:checkChartSell')) &
                (~df['processor'].str.contains('Buy-morningup')) &
                #(~df['processor'].str.contains('sell-breakout')) &
                (~df['processor'].str.contains('Breakout-Sell-after-10')) &
                (~df['processor'].str.contains('1-Sselll-morningDown')) &
                # (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:00', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:05', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'SellAllProcessor + week2lh-not-reached', color='LG', applyBreakOut=True)
        else:
            rb.render(st, empty_df, 'SellAllProcessor + week2lh-not-reached', color='LG')
    with col4:
        df = rb.getintersectdf('sell_all_processor', 'breakoutW2LR')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                ((df['PCT_day_change_pre1'] > -1.7) & (df['PCT_day_change_pre2'] > -1.7)) &
                ((df['PCT_day_change_pre1'] < 0) | (df['PCT_day_change_pre2'] < 0)) &
                (abs(df['month3LowChange']) >= 5) &
                # ((df['forecast_day_PCT10_change'] <= -2) | (df['forecast_day_PCT10_change'] > 6)) &
                (~df['processor'].str.contains('cash-sell-morning-volume')) &
                (~df['processor'].str.contains('Check-News')) &
                (~df['processor'].str.contains('supertrend')) &
                (~df['processor'].str.contains('09_30:checkChartSell')) &
                (~df['processor'].str.contains('Buy-morningup')) &
                #(~df['processor'].str.contains('sell-breakout')) &
                (~df['processor'].str.contains('Breakout-Sell-after-10')) &
                (~df['processor'].str.contains('1-Sselll-morningDown')) &
                # (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:00', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:05', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'SellAllProcessor + week2lh-not-reached', color='LG', applyBreakOut=True)
        else:
            rb.render(st, empty_df, 'SellAllProcessor + week2lh-not-reached', color='LG')


    col1, col2, col3, col4 = st.columns(4)
    with col1:
        df = rb.getintersectdf('buy_all_processor', 'breakoutMHR')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] > (df['PCT_day_change'] + 0.2)) &
                (abs(df['PCT_day_change']) >= 0.35) &
                (abs(df['yearHighChange']) >= 10) &
                (abs(df['month3HighChange']) >= 5) &
                (abs(df['monthHighChange']) >= 2.5) &
                (abs(df['yearLowChange']) >= 5) &
                (~df['processor'].str.contains('cash-buy-morning-volume')) &
                (~df['processor'].str.contains('Check-News')) &
                (~df['processor'].str.contains('supertrend')) &
                (~df['processor'].str.contains('09_30:checkChartBuy')) &
                (~df['processor'].str.contains('Sell-morningDown')) &
                #(~df['processor'].str.contains('buy-breakout')) &
                (~df['processor'].str.contains('Breakout-Buy-after-10')) &
                (~df['processor'].str.contains('1-Bbuyy-morningUp')) &
                # (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:00', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:05', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'BuyAllProcessor + week2lh-not-reached', color='LG', applyBreakOut=True)
        else:
            rb.render(st, empty_df, 'BuyAllProcessor + week2lh-not-reached', color='LG', applyBreakOut=True)
    with col2:
        df = rb.getintersectdf('buy_all_processor', 'breakoutMHR')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                ((df['PCT_day_change_pre1'] < 1.7) & (df['PCT_day_change_pre2'] < 1.7)) &
                ((df['PCT_day_change_pre1'] > 0) | (df['PCT_day_change_pre2'] > 0)) &
                (abs(df['month3HighChange']) >= 5) &
                # ((df['forecast_day_PCT10_change'] >=2) | (df['forecast_day_PCT10_change'] <= -6)) &
                (~df['processor'].str.contains('cash-buy-morning-volume')) &
                (~df['processor'].str.contains('Check-News')) &
                (~df['processor'].str.contains('supertrend')) &
                (~df['processor'].str.contains('09_30:checkChartBuy')) &
                (~df['processor'].str.contains('Sell-morningDown')) &
                #(~df['processor'].str.contains('buy-breakout')) &
                (~df['processor'].str.contains('Breakout-Buy-after-10')) &
                (~df['processor'].str.contains('1-Bbuyy-morningUp')) &
                # (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:00', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:05', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'BuyAllProcessor + week2lh-not-reached', color='LG', applyBreakOut=True)
        else:
            rb.render(st, empty_df, 'BuyAllProcessor + week2lh-not-reached', color='LG', applyBreakOut=True)
    with col3:
        df = rb.getintersectdf('sell_all_processor', 'breakoutMLR')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] < (df['PCT_day_change'] - 0.2)) &
                (abs(df['PCT_day_change']) >= 0.35) &
                (abs(df['yearLowChange']) >= 10) &
                (abs(df['month3LowChange']) >= 5) &
                (abs(df['monthLowChange']) >= 2.5) &
                (abs(df['yearHighChange']) >= 5) &
                (~df['processor'].str.contains('cash-sell-morning-volume')) &
                (~df['processor'].str.contains('Check-News')) &
                (~df['processor'].str.contains('supertrend')) &
                (~df['processor'].str.contains('09_30:checkChartSell')) &
                (~df['processor'].str.contains('Buy-morningup')) &
                #(~df['processor'].str.contains('sell-breakout')) &
                (~df['processor'].str.contains('Breakout-Sell-after-10')) &
                (~df['processor'].str.contains('1-Sselll-morningDown')) &
                # (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:00', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:05', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'SellAllProcessor + week2lh-not-reached', color='LG', applyBreakOut=True)
        else:
            rb.render(st, empty_df, 'SellAllProcessor + week2lh-not-reached', color='LG')
    with col4:
        df = rb.getintersectdf('sell_all_processor', 'breakoutMLR')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                ((df['PCT_day_change_pre1'] > -1.7) & (df['PCT_day_change_pre2'] > -1.7)) &
                ((df['PCT_day_change_pre1'] < 0) | (df['PCT_day_change_pre2'] < 0)) &
                (abs(df['month3LowChange']) >= 5) &
                # ((df['forecast_day_PCT10_change'] <= -2) | (df['forecast_day_PCT10_change'] > 6)) &
                (~df['processor'].str.contains('cash-sell-morning-volume')) &
                (~df['processor'].str.contains('Check-News')) &
                (~df['processor'].str.contains('supertrend')) &
                (~df['processor'].str.contains('09_30:checkChartSell')) &
                (~df['processor'].str.contains('Buy-morningup')) &
                #(~df['processor'].str.contains('sell-breakout')) &
                (~df['processor'].str.contains('Breakout-Sell-after-10')) &
                (~df['processor'].str.contains('1-Sselll-morningDown')) &
                # (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:00', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:05', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'SellAllProcessor + week2lh-not-reached', color='LG', applyBreakOut=True)
        else:
            rb.render(st, empty_df, 'SellAllProcessor + week2lh-not-reached', color='LG')


    col1, col2, col3, col4 = st.columns(4)
    with col1:
        df = rb.getintersectdf('buy_all_processor', 'breakoutM2HR')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] > (df['PCT_day_change'] + 0.2)) &
                (abs(df['PCT_day_change']) >= 0.35) &
                (abs(df['yearHighChange']) >= 10) &
                (abs(df['month3HighChange']) >= 5) &
                (abs(df['monthHighChange']) >= 2.5) &
                (abs(df['yearLowChange']) >= 5) &
                (~df['processor'].str.contains('cash-buy-morning-volume')) &
                (~df['processor'].str.contains('Check-News')) &
                (~df['processor'].str.contains('supertrend')) &
                (~df['processor'].str.contains('09_30:checkChartBuy')) &
                (~df['processor'].str.contains('Sell-morningDown')) &
                #(~df['processor'].str.contains('buy-breakout')) &
                (~df['processor'].str.contains('Breakout-Buy-after-10')) &
                (~df['processor'].str.contains('1-Bbuyy-morningUp')) &
                # (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:00', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:05', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'BuyAllProcessor + week2lh-not-reached', color='LG', applyBreakOut=True)
        else:
            rb.render(st, empty_df, 'BuyAllProcessor + week2lh-not-reached', color='LG', applyBreakOut=True)
    with col2:
        df = rb.getintersectdf('buy_all_processor', 'breakoutM2HR')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                ((df['PCT_day_change_pre1'] < 1.7) & (df['PCT_day_change_pre2'] < 1.7)) &
                ((df['PCT_day_change_pre1'] > 0) | (df['PCT_day_change_pre2'] > 0)) &
                (abs(df['month3HighChange']) >= 5) &
                # ((df['forecast_day_PCT10_change'] >=2) | (df['forecast_day_PCT10_change'] <= -6)) &
                (~df['processor'].str.contains('cash-buy-morning-volume')) &
                (~df['processor'].str.contains('Check-News')) &
                (~df['processor'].str.contains('supertrend')) &
                (~df['processor'].str.contains('09_30:checkChartBuy')) &
                (~df['processor'].str.contains('Sell-morningDown')) &
                #(~df['processor'].str.contains('buy-breakout')) &
                (~df['processor'].str.contains('Breakout-Buy-after-10')) &
                (~df['processor'].str.contains('1-Bbuyy-morningUp')) &
                # (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:00', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:05', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'BuyAllProcessor + week2lh-not-reached', color='LG', applyBreakOut=True)
        else:
            rb.render(st, empty_df, 'BuyAllProcessor + week2lh-not-reached', color='LG', applyBreakOut=True)
    with col3:
        df = rb.getintersectdf('sell_all_processor', 'breakoutM2LR')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] < (df['PCT_day_change'] - 0.2)) &
                (abs(df['PCT_day_change']) >= 0.35) &
                (abs(df['yearLowChange']) >= 10) &
                (abs(df['month3LowChange']) >= 5) &
                (abs(df['monthLowChange']) >= 2.5) &
                (abs(df['yearHighChange']) >= 5) &
                (~df['processor'].str.contains('cash-sell-morning-volume')) &
                (~df['processor'].str.contains('Check-News')) &
                (~df['processor'].str.contains('supertrend')) &
                (~df['processor'].str.contains('09_30:checkChartSell')) &
                (~df['processor'].str.contains('Buy-morningup')) &
                #(~df['processor'].str.contains('sell-breakout')) &
                (~df['processor'].str.contains('Breakout-Sell-after-10')) &
                (~df['processor'].str.contains('1-Sselll-morningDown')) &
                # (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:00', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:05', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'SellAllProcessor + week2lh-not-reached', color='LG', applyBreakOut=True)
        else:
            rb.render(st, empty_df, 'SellAllProcessor + week2lh-not-reached', color='LG')
    with col4:
        df = rb.getintersectdf('sell_all_processor', 'breakoutM2LR')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                ((df['PCT_day_change_pre1'] > -1.7) & (df['PCT_day_change_pre2'] > -1.7)) &
                ((df['PCT_day_change_pre1'] < 0) | (df['PCT_day_change_pre2'] < 0)) &
                (abs(df['month3LowChange']) >= 5) &
                # ((df['forecast_day_PCT10_change'] <= -2) | (df['forecast_day_PCT10_change'] > 6)) &
                (~df['processor'].str.contains('cash-sell-morning-volume')) &
                (~df['processor'].str.contains('Check-News')) &
                (~df['processor'].str.contains('supertrend')) &
                (~df['processor'].str.contains('09_30:checkChartSell')) &
                (~df['processor'].str.contains('Buy-morningup')) &
                #(~df['processor'].str.contains('sell-breakout')) &
                (~df['processor'].str.contains('Breakout-Sell-after-10')) &
                (~df['processor'].str.contains('1-Sselll-morningDown')) &
                # (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:00', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:05', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'SellAllProcessor + week2lh-not-reached', color='LG', applyBreakOut=True)
        else:
            rb.render(st, empty_df, 'SellAllProcessor + week2lh-not-reached', color='LG')


    

if __name__ == '__main__':
    main()