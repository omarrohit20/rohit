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
                (~df['systemtime'].str.contains('10:00', case=False, na=False)) &
                (~df['systemtime'].str.contains('10:05', case=False, na=False)) &
                (~df['systemtime'].str.contains('10:10', case=False, na=False)) &
                (~df['systemtime'].str.contains('10:15', case=False, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                ((df['forecast_day_PCT10_change'] > 2) | (df['forecast_day_PCT10_change'] < -6))
            ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 2:
            rb.render(st, filtered_df, 'week2lh-not-reached + Crossed Day High', column_conf=rb.column_config_merged, column_order=rb.column_order_p, color='LG')
        else:
            rb.render(st, filtered_df, 'week2lh-not-reached + Crossed Day High', column_conf=rb.column_config_merged, column_order=rb.column_order_p, color='LG')
    with col2:
        df = rb.getdf('crossed-day-high')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('09:2', case=False, na=False)) &
                (~df['systemtime'].str.contains('09:3', case=False, na=False)) &
                (~df['systemtime'].str.contains('09:4', case=False, na=False)) &
                ((df['forecast_day_PCT10_change'] > 2) | (df['forecast_day_PCT10_change'] < -6)) &
                (df['PCT_day_change'] > -1) & (df['PCT_day_change'] < 1) &
                (df['PCT_day_change_pre1'] > -1.5) & (df['PCT_day_change_pre1'] < 1.5) &
                (df['PCT_day_change_pre2'] < 2)
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Crossed Day Highs', column_order=rb.column_order_p, color='G')
    with col3:
        df = rb.getdf('crossed-day-high')
        filtered_df = df
        rb.render(st, filtered_df, 'Crossed Day Highs', color='LG')
    with col4:
        df = rb.getintersectdf('week2lh-not-reached','crossed-day-low')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                ((df['PCT_day_change_pre1'] > 0.3) | (df['PCT_day_change_pre2'] > 0.3)) &
                (~df['systemtime'].str.contains('09:', case=False, na=False)) &
                (~df['systemtime'].str.contains('10:00', case=False, na=False)) &
                (~df['systemtime'].str.contains('10:05', case=False, na=False)) &
                (~df['systemtime'].str.contains('10:10', case=False, na=False)) &
                (~df['systemtime'].str.contains('10:15', case=False, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                ((df['forecast_day_PCT10_change'] < -2) | (df['forecast_day_PCT10_change'] > 6))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 2:
            rb.render(st, filtered_df, 'week2lh-not-reached + Crossed Day Low', column_conf=rb.column_config_merged, column_order=rb.column_order_p, color='LG')
        else:
            rb.render(st, filtered_df, 'week2lh-not-reached + Crossed Day Low', column_conf=rb.column_config_merged, column_order=rb.column_order_p, color='LG')
    with col5:
        df = rb.getdf('crossed-day-low')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('09:2', case=False, na=False)) &
                (~df['systemtime'].str.contains('09:3', case=False, na=False)) &
                (~df['systemtime'].str.contains('09:4', case=False, na=False)) &
                ((df['forecast_day_PCT10_change'] < -2) | (df['forecast_day_PCT10_change'] > 6)) &
                (df['PCT_day_change'] > -1) & (df['PCT_day_change'] < 1) &
                (df['PCT_day_change_pre1'] > -1.5) & (df['PCT_day_change_pre1'] < 1.5) &
                (df['PCT_day_change_pre2'] > -2)
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'Crossed Day Lows', color='LG')
    with col6:
        df = rb.getdf('crossed-day-low')
        filtered_df = df
        rb.render(st, filtered_df, 'Crossed Day Lows', color='LG')

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

    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        df = rb.getintersectdf_ml('regressionhigh', 'regressionlow')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] < 4.5) &
                (df['PCT_day_change'] < 4) &
                (df['PCT_day_change'] > 2) &
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
                (df['highTail'] > 2.5)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayDown:Buy-HighTail', column_conf=rb.column_config_ml, column_order=rb.column_order_ml,
                  renderml=True, color='G')    
    with col3:
        df = rb.getintersectdf_ml('regressionhigh', 'regressionlow')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] < 1.5) &
                (df['PCT_day_change'] < 1.5) &
                (df['PCT_change'] > -0.5) &
                (df['PCT_day_change'] > -0.5) &
                #((df['PCT_day_change_pre1'] < 0.3) & (df['PCT_day_change_pre2'] < 0.3)) &
                (df['forecast_day_PCT10_change'] < -3) &
                (df['highTail'] > 2.5)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayDown:Sell-HighTail', column_conf=rb.column_config_ml, column_order=rb.column_order_ml,
                  renderml=True, color='R')
    with col4:
        df = rb.getintersectdf_ml('regressionlow', 'regressionhigh')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] > -4.5) &
                (df['PCT_day_change'] > -4) &
                (df['PCT_day_change'] < -2) &
                ((df['kNeighboursValue_reg'] < -2) | (df['mlpValue_reg'] < -2)) &
                ((df['PCT_day_change_pre1'] < 0 ) | (df['PCT_day_change_pre2'] < 0)) &
                (df['forecast_day_PCT10_change'] < -2)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'MLSELL', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='LG')
    with col5:
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
                (df['lowTail'] > 2.5)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayUp:Sell-LowTail', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='R')
    with col6:
        df = rb.getintersectdf_ml('regressionhigh', 'regressionlow')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] > -1.5) &
                (df['PCT_day_change'] > -1.5) &
                (df['PCT_change'] < 0.5) &
                (df['PCT_day_change'] < 0.5) &
                #((df['PCT_day_change_pre1'] > 0.3) & (df['PCT_day_change_pre2'] > 0.3)) &
                (df['forecast_day_PCT10_change'] > 3) &
                (df['lowTail'] > 2.5)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayUp:Buy-LowTail', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='LG')


    col1, col4 = st.columns(2)
    with col1:
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

if __name__ == '__main__':
    main()