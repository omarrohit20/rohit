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
                           page_title="Dashboard1",
                           initial_sidebar_state="expanded",)
    except Exception:
        pass

    # main title
    st.title('9:30 - 10:00 Last day trend : No Reversal: chartlink-1')

    # Global collection selector at top
    st.divider()
    st.subheader("📊 Collection Filter")
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        collections = ["All"] + rb.get_chartlink_collections()
        selected_coll = st.selectbox(
            "Select DB Collection for Scrip Filtering:",
            collections,
            help="Select a collection to filter scrips. Only scrips in that collection will be shown in all widgets."
        )
        rb.set_selected_collection(selected_coll)
    
    with col_filter2:
        if selected_coll != "All":
            scrips = rb.get_collection_scrips(selected_coll)
            st.info(f"✓ {len(scrips)} scrips in '{selected_coll}' collection")
        else:
            st.info("✓ Showing all scrips (no filter applied)")
    
    st.divider()

    # page-specific flag
    rb.chartlink1 = True
    

    
    col2, col4 = st.columns(2)
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
        filtered_9 = df
        try:
            filtered_9 = df[
                (df['systemtime'].str.contains('09:25', case=False, regex=True, na=False)) 
                ]
        except KeyError as e:
            print("")
        if len(filtered_9) < 5:
            rb.render(st, filtered_df, 'MorningDown:ABSLT1-CheckRecommendations', color='LG', height=200)
        else:
            rb.render(st, empty_df, 'MorningDown:ABSLT1-CheckRecommendations', color='LG', height=200)
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
        filtered_9 = df
        try:
            filtered_9 = df[
                (df['systemtime'].str.contains('09:25', case=False, regex=True, na=False)) 
                ]
        except KeyError as e:
            print("")
        if len(filtered_9) < 5:
            rb.render(st, filtered_df, 'MorningUp:ABSLT1-CheckRecommendations', color='LG', height=200)
        else:
            rb.render(st, empty_df, 'MorningUp:ABSLT1-CheckRecommendations', color='LG', height=200)
  

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
                (df['PCT_day_change'] < -1.3) &
                (df['PCT_day_change'] > -3) &
                (df['PCT_change'] < -1.3) &
                (df['PCT_change'] > -3) &
                (df['PCT_day_change_pre1'] < 1) &
                (df['PCT_day_change_pre2'] < 1) &
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
                (df['yearLowChange'] < 70) &
                (df['month3LowChange'] < 15) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                (df['mlData'].str.contains("Z&&&") & (df['yearLowChange'] > 10)) 
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'SQROFFAt10:LastDayDownTodayLT-0.3:Consolidation-CheckRecommendations', color='LG')


    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        df = rb.getdf('morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                #(df['lowTail'] >= 1) &
                (abs(df['monthHighChange']) < abs(df['monthLowChange'])) &
                (df['PCT_day_change_pre1'] >= 1.5) &
                (df['PCT_day_change_pre1'] <= 4) &
                (df['PCT_day_change_pre2'] <= -1) &
                (df['PCT_day_change_pre2'] >= -4) &
                (df['PCT_day_change'] >= -0.7) &
                (df['PCT_day_change'] <= 0.7)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'DOJI Breakout Buy - Pre2LT0', color='LG', height=150)
    with col2:
        df = rb.getdf('morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['forecast_day_PCT10_change'] > 2) | ((df['forecast_day_PCT10_change'] < -6) & (df['forecast_day_PCT5_change'] < 0))) &
                (~df['systemtime'].str.contains('09:20', case=False, na=False)) &
                (df['filter5'].str.contains('DOJI', case=False, regex=True, na=False)) &
                (df['PCT_day_change_pre2'] <= 1) &
                (df['PCT_day_change_pre2'] > -0.5) &
                (df['lowTail'] < 1) &
                (df['PCT_day_change_pre1'] >= 1.5) &
                (df['PCT_day_change_pre1'] <= 3.5) &
                (df['week2HighChange'] >= -2) &
                (df['week2HighChange'] <= 5) &
                (df['year5HighChange'] < -10) &
                ((df['PCT_day_change'] >= 0.2) | (df['PCT_day_change_pre1'] >= 1.7)) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'DOJI Breakout Buy', color='LG', height=150)
    with col3:
        df = rb.getdf('morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['forecast_day_PCT10_change'] > 2) | ((df['forecast_day_PCT10_change'] < -6) & (df['forecast_day_PCT5_change'] < 0))) &
                (df['yearLowChange'] > 15) &
                #(df['yearHighChange'] > -35) &
                (df['lowTail'] < 1) &
                (df['PCT_day_change_pre1'] >= -1) &
                (df['PCT_day_change_pre1'] <= 1) &
                (df['PCT_day_change_pre2'] >= 2) &
                (df['PCT_day_change_pre2'] <= 4) &
                (df['PCT_day_change'] >= -1) &
                (df['PCT_day_change'] <= 0)
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'PctDayChangePre2 - Doji Buy', color='LG', height=150)
    with col4:
        df = rb.getdf('morning-volume-breakout-sell')
        filtered_df = df
        try:
            filtered_df = df[
                #(df['highTail'] >= 1) &
                (abs(df['monthHighChange']) > abs(df['monthLowChange'])) &
                (df['PCT_day_change_pre1'] >= -4) &
                (df['PCT_day_change_pre1'] <= -1.5) &
                (df['PCT_day_change_pre2'] <= 4) &
                (df['PCT_day_change_pre2'] >= 1) &
                (df['PCT_day_change'] >= -0.7) &
                (df['PCT_day_change'] <= 0.7)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'DOJI Breakout Sell - Pre2GT0', color='LG', height=150)
    with col5:
        df = rb.getdf('morning-volume-breakout-sell')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['forecast_day_PCT10_change'] < -2) | ((df['forecast_day_PCT10_change'] > 6) & (df['forecast_day_PCT5_change'] > 0))) &
                (~df['systemtime'].str.contains('09:20', case=False, na=False)) &
                (df['filter5'].str.contains('DOJI', case=False, regex=True, na=False)) &
                (df['PCT_day_change_pre2'] >= -1) &
                (df['PCT_day_change_pre2'] <= 0.5) &
                (df['highTail'] < 1) &
                (df['PCT_day_change_pre1'] >= -3.5) &
                (df['PCT_day_change_pre1'] <= -1) &
                (df['week2LowChange'] >= -5) &
                (df['week2LowChange'] <= 2) &
                (df['monthHighChange'] > -10) &
                ((df['PCT_day_change'] <= -0.2) | (df['PCT_day_change_pre1'] <= -1.7)) &
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'DOJI Breakout Sell', color='LG', height=150)
    with col6:
        df = rb.getdf('morning-volume-breakout-sell')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['forecast_day_PCT10_change'] < -2) | ((df['forecast_day_PCT10_change'] > 6) & (df['forecast_day_PCT5_change'] > 0))) &
                (df['yearHighChange'] < -15) &
                (df['highTail'] < 1) &
                (df['PCT_day_change_pre2'] >= -4) &
                (df['PCT_day_change_pre2'] <= -2) &
                (df['PCT_day_change_pre1'] >= -1) &
                (df['PCT_day_change_pre1'] <= 1) &
                (df['PCT_day_change'] >= 0) &
                (df['PCT_day_change'] <= 1)
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'PctDayChangePre2 - Doji Sell', color='LG', height=150)
    

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        df = rb.getdf('morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['forecast_day_PCT10_change'] > 2) | ((df['forecast_day_PCT10_change'] < -6) & (df['forecast_day_PCT5_change'] < 0))) &
                (df['forecast_day_PCT10_change'] >-9) &
                (~df['systemtime'].str.contains('09:20', case=False, na=False)) &
                (df['PCT_day_change'] > -3) &
                (df['PCT_day_change'] < 2) &
                (df['year5HighChange'] < -25) &
                (df['week2HighChange'] > -2) &
                (abs(df['week2HighChange']) > 1) &
                (df['yearLowChange'] > 15) &
                (df['month3HighChange'] > -15) &
                (df['PCT_change'] > 0)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'year5HighChangeLT-30 : week2High', color='LG')
    with col2:
        df = rb.getdf('morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['forecast_day_PCT10_change'] >-9) &
                (df['PCT_day_change'] < 2.5) &
                (df['PCT_day_change'] > -3) &
                (df['PCT_change'] > 0) &
                (df['month3HighChange'] > -20) &
                (df['year5HighChange'] < -25) &
                (df['yearHighChange'] < -20)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'year5HighChangeLT-30 + week2High', color='LG')
    with col3:
        #df = rb.getdf('morning-volume-breakout-sell')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        rb.render(st, empty_df, 'year5LowChangeGT30 : week2Low', color='LG')
    with col4:
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        rb.render(st, empty_df, 'year5LowChangeGT30 + week2Low', color='LG')

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        df = rb.getdf('morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['forecast_day_PCT10_change'] > 2) | ((df['forecast_day_PCT10_change'] < -6) & (df['forecast_day_PCT5_change'] < 0))) &
                (~df['systemtime'].str.contains('09:20', case=False, na=False)) &
                (df['yearLowChange'] > 5) &
                (df['week2HighChange'] > 0) &
                (df['monthHighChange'] < 5) &
                (df['PCT_day_change'] > 1) &
                (~df['filter5'].str.contains('BothGT2', case=False, regex=True, na=False)) &
                (df['forecast_day_PCT10_change'] > -1) &
                (df['week2LowChange'] > 2) &
                (df['lowTail'] < 1) &
                (df['PCT_day_change_pre1'] >= -1) &
                (df['PCT_day_change_pre1'] <= 2) &
                (df['PCT_day_change_pre2'] >= -1) &
                (df['PCT_day_change_pre2'] <= 3) &
                (df['weekHighChange'] > 0) &
                (df['month3HighChange'] > -15) &
                (df['monthLowChange'] < 10)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'week2HighGT0 : Avoid-GT2-And-Top5', color='LG', height=150)
    with col2:
        df = rb.getdf('morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['forecast_day_PCT10_change'] > 2) | ((df['forecast_day_PCT10_change'] < -6) & (df['forecast_day_PCT5_change'] < 0))) &
                (~df['systemtime'].str.contains('09:20', case=False, na=False)) &
                (df['yearLowChange'] > 5) &
                (df['week2HighChange'] > -1) &
                (df['monthHighChange'] < 5) &
                (df['PCT_day_change_pre2'] < 3) &
                (df['PCT_day_change_pre1'] < 3) &
                (df['PCT_day_change'] >= -1.5) &
                (df['PCT_day_change'] <= 1) &
                (~df['filter5'].str.contains('BothGT2', case=False, regex=True, na=False)) &
                (df['intradaytech'].str.contains('#TOP', case=False, regex=True, na=False)) &
                (df['lowTail'] < 1) &
                #(~df['systemtime'].str.contains('09:4', case=False, regex=True, na=False)) &
                (df['week2LowChange'] > 2) &
                (df['monthHighChange'] > 0) &
                (df['year5HighChange'] < 0) &
                (df['mlData'].str.contains('0@@', case=False, regex=True, na=False)) &
                (df['PCT_day_change_pre1'] < 1)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'week2HighGT0-1 : Avoid-GT2-And-Top5', color='LG', height=150)
    with col3:
        df = rb.getdf('morning-volume-breakout-sell')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['forecast_day_PCT10_change'] < -2) | ((df['forecast_day_PCT10_change'] > 6) & (df['forecast_day_PCT5_change'] > 0))) &
                (~df['systemtime'].str.contains('09:20', case=False, na=False)) &
                (df['yearHighChange'] < -5) &
                (df['week2LowChange'] < 0) &
                (df['monthLowChange'] > -5) &
                (df['PCT_day_change'] < -1) &
                (~df['filter5'].str.contains('BothLT2', case=False, regex=True, na=False)) &
                (df['forecast_day_PCT10_change'] < 1) &
                (df['week2HighChange'] < -2) &
                (df['highTail'] < 1) &
                (df['PCT_day_change_pre1'] >= -2) &
                (df['PCT_day_change_pre1'] <= 1) &
                (df['PCT_day_change_pre2'] >= -3) &
                (df['PCT_day_change_pre2'] <= 1) &
                (df['weekLowChange'] < 0) &
                (df['month3LowChange'] < 15) &
                (df['monthHighChange'] > -10)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'week2LowLT0 : Avoid-LT(-2)-And-Top5', color='LG', height=150)
    with col4:
        df = rb.getdf('morning-volume-breakout-sell')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['forecast_day_PCT10_change'] < -2) | ((df['forecast_day_PCT10_change'] > 6) & (df['forecast_day_PCT5_change'] > 0))) &
                (~df['systemtime'].str.contains('09:20', case=False, na=False)) &
                (df['yearHighChange'] < -5) &
                (df['week2LowChange'] < 1) &
                (df['monthLowChange'] > -5) &
                (df['PCT_day_change_pre1'] < 3) &
                (df['PCT_day_change_pre2'] < 3) &
                (df['PCT_day_change'] >= -1.5) &
                (df['PCT_day_change'] <= 1) &
                (~df['filter5'].str.contains('BothLT-2', case=False, regex=True, na=False)) &
                (df['lowTail'] < 1) &
                (df['intradaytech'].str.contains('#TOP', case=False, regex=True, na=False)) &
                (df['monthLowChange'] < 10) &
                (df['highTail'] < 1.5) &
                #(~df['systemtime'].str.contains('09:4', case=False, regex=True, na=False)) &
                (df['week2HighChange'] < -2) &
                (df['mlData'].str.contains('0@@', case=False, regex=True, na=False)) &
                (df['monthLowChange'] < 0)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'week2LowLT0-1 : Avoid-LT(-2)-And-Top5', color='LG', height=150)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        df = rb.getintersectdf('morning-volume-breakout-buy', 'crossed-day-high')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                (df['yearLowChange'] > 5) &
                (df['week2HighChange'] > -1) &
                (df['monthHighChange'] < 5) &
                (df['month3HighChange'] < 2) &
                (df['month3HighChange'] > -4) &
                (df['PCT_day_change'] < 3) &
                (df['PCT_day_change'] > -1.5) &
                (~df['filter5'].str.contains('BothGT2', case=False, regex=True, na=False)) &
                (df['lowTail'] < 1) &
                (df['highTail'] < 1) &
                (df['forecast_day_PCT10_change'] > -1) &
                (df['week2LowChange'] > 0) &
                (df['PCT_day_change_pre2'] < 2) 
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'week2HighGT0 + crossed-day-high', color='LG')
    with col2:
        df = rb.getdf('morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                (df['yearLowChange'] > 5) &
                (df['week2HighChange'] > -1) &
                (df['monthHighChange'] < 5) &
                (df['PCT_day_change'] < 3) &
                (df['PCT_day_change'] > -1.5) &
                (~df['filter5'].str.contains('BothGT2', case=False, regex=True, na=False)) &
                (df['lowTail'] < 1.5) &
                (df['forecast_day_PCT10_change'] > -1) &
                (df['week2LowChange'] > 0) &
                (df['PCT_day_change_pre2'] < 2)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'week2HighGT0', color='LG')
    with col3:
        df = rb.getintersectdf('morning-volume-breakout-sell', 'crossed-day-low')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                (df['yearHighChange'] < -5) &
                (df['week2LowChange'] < 0) &
                (df['monthLowChange'] > -5) &
                (df['month3LowChange'] > -2) &
                (df['month3LowChange'] < 4) &
                (df['PCT_day_change'] > -3) &
                (df['PCT_day_change'] < 1.3) &
                (~df['filter5'].str.contains('BothLT-2', case=False, regex=True, na=False)) &
                (df['lowTail'] < 1) &
                (df['highTail'] < 1) &
                (df['forecast_day_PCT10_change'] < 1) &
                (df['week2HighChange'] < -2) &
                # (df['highTail'] < 1) &
                # (df['weekHighChange'] < -1) &
                # (df['PCT_day_change_pre1'] > -2) &
                (df['PCT_day_change_pre2'] > -2)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'week2LowLT0 + crossed-day-low', color='LG')
    with col4:
        df = rb.getdf('morning-volume-breakout-sell')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                (df['yearHighChange'] < -5) &
                (df['week2LowChange'] < 0) &
                (df['monthLowChange'] > -5) &
                (df['PCT_day_change'] > -3) &
                (df['PCT_day_change'] < 1.3) &
                (~df['filter5'].str.contains('BothLT-2', case=False, regex=True, na=False)) &
                (df['highTail'] < 1.5) &
                (df['forecast_day_PCT10_change'] < 1) &
                (df['week2HighChange'] < -2) &
                (df['highTail'] < 1) &
                (df['weekHighChange'] < -1) &
                (df['PCT_day_change_pre1'] > -2) &
                (df['PCT_day_change_pre2'] > -2)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'week2LowLT0', color='LG')

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        df = rb.getdf('morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['forecast_day_PCT10_change'] < 0.5) &
                (~df['systemtime'].str.contains('09:20', case=False, na=False)) &
                (df['PCT_day_change'] < 2) &
                (df['monthLowChange'] < 4) &
                (df['monthHighChange'] < -5) &
                (df['month3HighChange'] < -5) &
                (df['month3LowChange'] > 3) &
                (df['PCT_day_change_pre1'] < 2) &
                (df['year5HighChange'] < -10) &
                (df['weekLowChange'] > 1) &
                (df['week2LowChange'] > 1) &
                (df['PCT_change'] > -1.5) &
                (df['yearHighChange'] > -25) &
                (abs(df['monthHighChange']) > abs( df['monthLowChange']))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'MorningVolumeBreakoutBuys + NearMonthLow', color='LG', height=150)
    with col2:
        df = rb.getdf('morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['forecast_day_PCT10_change'] < 0.5) &
                (df['PCT_day_change'] < 2) &
                (df['monthLowChange'] < 5) &
                (df['monthHighChange'] < -3) &
                (df['month3HighChange'] < -3) &
                (df['month3LowChange'] > 3) &
                (df['PCT_day_change_pre1'] < 2) &
                (df['year5HighChange'] < -10) &
                (df['month3HighChange'] > -10) &
                (df['weekHighChange'] > -2) &
                (df['weekHighChange'] < -1) &
                (abs(df['monthHighChange']) > abs( df['monthLowChange']))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'MorningVolumeBreakoutBuys + NearMonthLow', color='LG', height=150)
    with col3:
        df = rb.getdf('morning-volume-breakout-sell')
        filtered_df = df
        try:
            filtered_df = df[
                (df['forecast_day_PCT10_change'] > -0.5) &
                (~df['systemtime'].str.contains('09:20', case=False, na=False)) &
                (df['PCT_day_change'] < -1.5) &
                (df['PCT_day_change'] > -4.5) &
                (df['PCT_day_change_pre1'] > 0.5) &
                (df['monthHighChange'] > -5) &
                (df['forecast_day_PCT10_change'] < 4) &
                (df['PCT_change'] < -2) &
                (df['monthLowChange'] > 5) &
                (df['month3LowChange'] > 5) &
                (abs(df['monthHighChange']) < abs( df['monthLowChange']))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'MorningVolumeBreakoutSells + NearMonthHigh', color='LG', height=150)
    with col4:
        df = rb.getdf('morning-volume-breakout-sell')
        filtered_df = df
        try:
            filtered_df = df[
                (df['forecast_day_PCT10_change'] > -0.5) &
                (df['PCT_day_change'] > -2) &
                (df['monthHighChange'] > -5) &
                (df['monthLowChange'] > 3) &
                (df['month3LowChange'] > 3) &
                (df['month3HighChange'] < -3) &
                (df['PCT_day_change_pre1'] > -2) &
                (df['year5HighChange'] < -10) &
                (df['month3LowChange'] < 10) &
                (df['weekLowChange'] < 2) &
                (df['weekLowChange'] > 1) &
                (abs(df['monthHighChange']) < abs( df['monthLowChange']))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'MorningVolumeBreakoutSells + NearMonthHigh', color='LG', height=150)


    col0, col1, col2, col00, col3, col4 = st.columns(6)
    with col0:
        df = rb.getdf('morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['yearLowChange'] > 10) &
                ((df['yearLowChange'] > 15) | (df['month3HighChange'] > -2)) &
                (df['month3HighChange'] < 2.5) &
                (df['monthHighChange'] > 0) &
                (df['PCT_day_change'] < 3) &
                (df['PCT_day_change_pre1'] < 5) &
                (df['PCT_day_change_pre2'] < 5) &
                (df['PCT_day_change'] > 1.5) &
                (df['PCT_day_change_pre1'] > -1.5) &
                (df['PCT_day_change_pre2'] > -1.5) &
                (df['week2HighChange'] > -0.5) &
                ((df['mlData'].str.contains("BYYWEEK2HIGH>GT0"))) &
                ( (df['month3LowChange'] > 10) | (df['filter'].str.contains("MLBuy"))) &
                (df['systemtime'].str.contains('09:', case=False, regex=True, na=False)) 
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BYYWEEK2HIGH>GT0', color='LG')
    with col1:
        df = rb.getintersectdf('morning-volume-breakout-buy', 'breakoutMH')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                ((df['forecast_day_PCT10_change'] > 2) | ((df['forecast_day_PCT10_change'] < -6) & (df['forecast_day_PCT5_change'] < 0))) &
                (~df['systemtime'].str.contains('09:20', case=False, na=False)) &
                ((df['PCT_day_change'] < 2) | (df['week2LowChange'] < 7)) &
                (df['PCT_day_change'] > -1.5) &
                (df['PCT_day_change_pre1'] > -1) &
                (df['PCT_day_change_pre2'] > -1) &
                (df['PCT_day_change_pre1'] < 2)
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) <= 3:
            rb.render(st, filtered_df, 'morning-volume-breakout-buy + breakoutMH', color='LG', height=150)
        else:
            rb.render(st, filtered_df, 'morning-volume-breakout-buy + breakoutMH', color='LG', height=150)
    with col2:
        df = rb.getintersectdf('morning-volume-breakout-buy', 'breakoutM2H')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                ((df['forecast_day_PCT10_change'] > 2) | ((df['forecast_day_PCT10_change'] < -6) & (df['forecast_day_PCT5_change'] < 0))) &
                ((df['PCT_day_change'] < 2) | (df['week2LowChange'] < 7)) &
                (df['PCT_day_change'] > -1.5) &
                (df['PCT_day_change_pre1'] > -1) &
                (df['PCT_day_change_pre2'] > -1) &
                (df['PCT_day_change_pre1'] < 2)
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) <= 3:
            rb.render(st, filtered_df, 'morning-volume-breakout-buy + breakoutM2H', color='LG', height=150)
        else:
            rb.render(st, empty_df, 'morning-volume-breakout-buy + breakoutM2H', color='LG', height=150)
    with col00:
        df = rb.getdf('morning-volume-breakout-sell')
        filtered_df = df
        try:
            filtered_df = df[
                (df['yearHighChange'] < -10) &
                ((df['yearHighChange'] < -15) | (df['month3LowChange'] < 2)) &
                (df['PCT_day_change'] > -3) &
                (df['PCT_day_change_pre1'] > -5) &
                (df['PCT_day_change_pre2'] > -5) &
                (df['PCT_day_change'] < -1.5) &
                (df['PCT_day_change_pre1'] < 1.5) &
                (df['PCT_day_change_pre2'] < 1.5) &
                (df['week2LowChange'] < 0.5) &
                ((df['mlData'].str.contains("SLLWEEK2LOW<LT0"))) &
                ((df['month3HighChange'] < -10) | (df['filter'].str.contains("MLSell"))) &
                (df['systemtime'].str.contains('09:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'SLLWEEK2LOW<LT0', color='LG')
    with col3:
        df = rb.getintersectdf('morning-volume-breakout-sell', 'breakoutML')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                ((df['forecast_day_PCT10_change'] < -2) | ((df['forecast_day_PCT10_change'] > 6) & (df['forecast_day_PCT5_change'] > 0))) &
                (~df['systemtime'].str.contains('09:20', case=False, na=False)) &
                ((df['PCT_day_change'] > -2) | (df['week2HighChange'] > -7)) &
                (df['PCT_day_change'] < 1.5) &
                (df['PCT_day_change_pre1'] < 1) &
                (df['PCT_day_change_pre2'] < 1) &
                (df['PCT_day_change_pre1'] > -2) &
                df['month3LowChange'] > -0.5
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) <= 3:
            rb.render(st, filtered_df, 'morning-volume-breakout-sell + breakoutML', color='LG', height=150)
        else:
            rb.render(st, empty_df, 'morning-volume-breakout-sell + breakoutML', color='LG', height=150)
    with col4:
        df = rb.getintersectdf('morning-volume-breakout-sell', 'breakoutM2L')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                ((df['forecast_day_PCT10_change'] < -2) | ((df['forecast_day_PCT10_change'] > 6) & (df['forecast_day_PCT5_change'] > 0))) &
                ((df['PCT_day_change'] > -2) | (df['week2HighChange'] > -7)) &
                (df['PCT_day_change'] < 1.5) &
                (df['PCT_day_change_pre1'] < 1) &
                (df['PCT_day_change_pre2'] < 1) &
                (df['PCT_day_change_pre1'] > -2) &
                df['month3LowChange'] > -0.5
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) <= 3:
            rb.render(st, filtered_df, 'morning-volume-breakout-sell + breakoutM2L', color='LG', height=150)
        else:
            rb.render(st, empty_df, 'morning-volume-breakout-sell + breakoutM2L', color='LG', height=150)

    col0, col00 = st.columns(2)
    with col0:
        df = rb.getdf('morning-volume-breakout-buy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['yearLowChange'] > 10) &
                ((df['yearLowChange'] > 15) | (df['month3HighChange'] > -2)) &
                #(df['month3HighChange'] < 2.5) &
                #(df['monthHighChange'] > 0) &
                (df['PCT_day_change'] < 3) &
                (df['PCT_day_change_pre1'] < 5) &
                (df['PCT_day_change_pre2'] < 5) &
                (df['PCT_day_change'] > -1.5) &
                (df['PCT_day_change_pre1'] > -1.5) &
                (df['PCT_day_change_pre2'] > -1.5) &
                (df['week2HighChange'] > -0.5) &
                ((df['mlData'].str.contains("BYYWEEK2HIGH>GT0"))) &
                #((df['month3LowChange'] > 10) | (df['filter'].str.contains("MLBuy")))
                (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BYYWEEK2HIGH>GT0', color='LG')
    with col00:
        df = rb.getdf('morning-volume-breakout-sell')
        filtered_df = df
        try:
            filtered_df = df[
                (df['yearHighChange'] < -10) &
                ((df['yearHighChange'] < -15) | (df['month3LowChange'] < 2)) &
                (df['PCT_day_change'] > -3) &
                (df['PCT_day_change_pre1'] > -5) &
                (df['PCT_day_change_pre2'] > -5) &
                (df['PCT_day_change'] < 1.5) &
                (df['PCT_day_change_pre1'] < 1.5) &
                (df['PCT_day_change_pre2'] < 1.5) &
                (df['week2LowChange'] < 0.5) &
                ((df['mlData'].str.contains("SLLWEEK2LOW<LT0"))) &
                #((df['month3HighChange'] < -10) | (df['filter'].str.contains("MLSell")))
                (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'SLLWEEK2LOW<LT0', color='LG')


    col2, col20, col5, col50 = st.columns(4)
    with col2:
        df = rb.getintersectdf('week2lh-not-reached', 'crossed-day-high')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (~df['filter3'].str.startswith('ReversalHighYear', na=False)) &
                (~df['filter3'].str.startswith('ReversalHighMonth6', na=False)) 
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'week2lh-not-reached + Crossed Day High', column_conf=rb.column_config_merged,
                      column_order=rb.column_order_p, color='LG')
        else:
            rb.render(st, empty_df, 'week2lh-not-reached + Crossed Day High', column_conf=rb.column_config_merged,
                      column_order=rb.column_order_p, color='LG')
    with col20:
        df = rb.getintersectdf('week2lh-not-reached',
                               '09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (~df['filter3'].str.startswith('ReversalHighYear', na=False)) &
                (~df['filter3'].str.startswith('ReversalHighMonth6', na=False)) 
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'week2lh-not-reached + Crossed 2Day High', column_conf=rb.column_config_merged,
                      column_order=rb.column_order_p, color='LG')
        else:
            rb.render(st, empty_df, 'week2lh-not-reached + Crossed 2Day High', column_conf=rb.column_config_merged,
                      column_order=rb.column_order_p, color='LG')
    with col5:
        df = rb.getintersectdf('week2lh-not-reached', 'crossed-day-low')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (~df['filter3'].str.startswith('ReversalLowYear', na=False)) &
                (~df['filter3'].str.startswith('ReversalLowMonth6', na=False)) 
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'week2lh-not-reached + Crossed Day Low', column_conf=rb.column_config_merged,
                      column_order=rb.column_order_p, color='LG')
        else:
            rb.render(st, empty_df, 'week2lh-not-reached + Crossed Day Low', column_conf=rb.column_config_merged,
                      column_order=rb.column_order_p, color='LG')
    with col50:
        df = rb.getintersectdf('week2lh-not-reached',
                               '09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (~df['filter3'].str.startswith('ReversalLowYear', na=False)) &
                (~df['filter3'].str.startswith('ReversalLowMonth6', na=False)) 
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'week2lh-not-reached + Crossed 2Day Low', column_conf=rb.column_config_merged,
                      column_order=rb.column_order_p, color='LG')
        else:
            rb.render(st, empty_df, 'week2lh-not-reached + Crossed 2Day Low', column_conf=rb.column_config_merged,
                      column_order=rb.column_order_p, color='LG')

    
    col0, col1, col2, col3 = st.columns(4)
    with col0:
        df = rb.getintersectdf('09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)', 'crossed-day-high')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'Crossed 2 Day High + Crossed Day High', column_conf=rb.column_config_merged,
                      column_order=rb.column_order_p, color='LG')
        else:
            rb.render(st, empty_df, 'Crossed 2 Day High + Crossed Day High', column_conf=rb.column_config_merged,
                      column_order=rb.column_order_p, color='LG')
    with col1:
        df = rb.getintersectdf('supertrend-morning-buy', 'crossed-day-high')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'supertrend-morning-buy + Crossed Day High', column_conf=rb.column_config_merged,
                      column_order=rb.column_order_p, color='LG')
        else:
            rb.render(st, empty_df, 'supertrend-morning-buy + Crossed Day High', column_conf=rb.column_config_merged,
                      column_order=rb.column_order_p, color='LG')
    with col2:
        df = rb.getintersectdf('09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)', 'crossed-day-low')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'Crossed 2 Day Low + Crossed Day Low', column_conf=rb.column_config_merged,
                      column_order=rb.column_order_p, color='LG')
        else:
            rb.render(st, empty_df, 'Crossed 2 Day Low + Crossed Day Low', column_conf=rb.column_config_merged,
                      column_order=rb.column_order_p, color='LG')
    with col3:
        df = rb.getintersectdf('supertrend-morning-sell', 'crossed-day-low')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'supertrend-morning-sell + Crossed Day Low', column_conf=rb.column_config_merged,
                      column_order=rb.column_order_p, color='LG')
        else:
            rb.render(st, empty_df, 'supertrend-morning-sell + Crossed Day Low', column_conf=rb.column_config_merged,
                      column_order=rb.column_order_p, color='LG')

    
    col1, col3 = st.columns(2)
    with col1:
        df = rb.getintersectdf('buy_all_processor', 'week2lh-not-reached')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (~df['filter3'].str.startswith('ReversalHighYear', na=False)) &
                (~df['filter3'].str.startswith('ReversalHighMonth6', na=False)) &
                # ((df['forecast_day_PCT10_change'] >=2) | (df['forecast_day_PCT10_change'] <= -6)) &
                (~df['processor'].str.contains('cash-buy-morning-volume')) &
                (~df['processor'].str.contains('Check-News')) &
                (~df['processor'].str.contains('supertrend')) &
                (~df['processor'].str.contains('09_30:checkChartBuy')) &
                (~df['processor'].str.contains('Sell-morningDown')) &
                (~df['processor'].str.contains('buy-breakout')) &
                (~df['processor'].str.contains('Breakout-Buy-after-10')) &
                #(~df['processor'].str.contains('1-Bbuyy-morningUp-downConsolidation')) &
                # (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:00', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:05', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'BuyAllProcessor + week2lh-not-reached', color='LG')
        else:
            rb.render(st, empty_df, 'BuyAllProcessor + week2lh-not-reached', color='LG')
    with col3:
        df = rb.getintersectdf('sell_all_processor', 'week2lh-not-reached')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (~df['filter3'].str.startswith('ReversalLowYear', na=False)) &
                (~df['filter3'].str.startswith('ReversalLowMonth6', na=False)) &
                # ((df['forecast_day_PCT10_change'] <= -2) | (df['forecast_day_PCT10_change'] > 6)) &
                (~df['processor'].str.contains('cash-sell-morning-volume')) &
                (~df['processor'].str.contains('Check-News')) &
                (~df['processor'].str.contains('supertrend')) &
                (~df['processor'].str.contains('09_30:checkChartSell')) &
                (~df['processor'].str.contains('Buy-morningup')) &
                (~df['processor'].str.contains('sell-breakout')) &
                (~df['processor'].str.contains('Breakout-Sell-after-10')) &
                #(~df['processor'].str.contains('1-Sselll-morningDown')) &
                # (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:00', case=False, regex=True, na=False)) &
                # (~df['systemtime'].str.contains('10:05', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'SellAllProcessor + week2lh-not-reached', color='LG')
        else:
            rb.render(st, empty_df, 'SellAllProcessor + week2lh-not-reached', color='LG')


    col10, col1, col2, col30, col3, col4 = st.columns(6)
    with col10:
        df = rb.getdf('buy_all_processor')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (~df['filter3'].str.startswith('ReversalHighYear', na=False)) &
                (~df['filter3'].str.startswith('ReversalHighMonth6', na=False)) &
                (~df['processor'].str.contains('cash-buy-morning-volume')) &
                (~df['processor'].str.contains('crossed-day-high')) &
                (~df['processor'].str.contains('09_30:checkChartBuy')) &
                (df['filter'].str.contains('MLBuy', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'BuyAllProcessor-MLBuy', color='LG')
        else:
            rb.render(st, empty_df, 'BuyAllProcessor-MLBuy', color='LG')
    with col1:
        df = rb.getdf('buy_all_processor')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (~df['filter3'].str.startswith('ReversalHighYear', na=False)) &
                (~df['filter3'].str.startswith('ReversalHighMonth6', na=False)) &
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
                ((df['PCT_day_change_pre1'] > 0.1) | (df['PCT_day_change_pre2'] > 0.1) | (~df['processor'].str.contains('buy-breakout'))) &
                (~df['processor'].str.contains('Breakout-Buy-after-10')) &
                (~df['processor'].str.contains('1-Bbuyy-morningUp')) &
                (~df['systemtime'].str.contains('10:3', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:4', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:5', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'BuyAllProcessor', color='LG')
        else:
            rb.render(st, empty_df, 'BuyAllProcessor', color='LG')
    with col2:
        df = rb.getdf('buy_all_processor')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (~df['filter3'].str.startswith('ReversalHighYear', na=False)) &
                (~df['filter3'].str.startswith('ReversalHighMonth6', na=False)) &
                (abs(df['monthHighChange']) >= 2.5) &
                (abs(df['yearLowChange']) >= 5) &
                (~df['processor'].str.contains('cash-buy-morning-volume')) &
                (~df['processor'].str.contains('Check-News')) &
                (~df['processor'].str.contains('supertrend')) &
                (~df['processor'].str.contains('09_30:checkChartBuy')) &
                (~df['processor'].str.contains('Sell-morningDown')) &
                (~df['processor'].str.contains('buy-breakout')) &
                (~df['processor'].str.contains('Breakout-Buy-after-10')) &
                (~df['processor'].str.contains('1-Bbuyy-morningUp')) &
                (~df['systemtime'].str.contains('10:3', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:4', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:5', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'BuyAllProcessor', color='LG')
        else:
            rb.render(st, empty_df, 'BuyAllProcessor', color='LG')
    with col30:
        df = rb.getdf('sell_all_processor')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (~df['filter3'].str.startswith('ReversalLowYear', na=False)) &
                (~df['filter3'].str.startswith('ReversalLowMonth6', na=False)) &
                (~df['processor'].str.contains('cash-sell-morning-volume')) &
                (~df['processor'].str.contains('crossed-day-low')) &
                (~df['processor'].str.contains('09_30:checkChartSell')) &
                (df['filter'].str.contains('MLSell', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'SellAllProcessor-MLSell', color='LG')
        else:
            rb.render(st, empty_df, 'SellAllProcessor-MLSell', color='LG')
    with col3:
        df = rb.getdf('sell_all_processor')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (~df['filter3'].str.startswith('ReversalLowYear', na=False)) &
                (~df['filter3'].str.startswith('ReversalLowMonth6', na=False)) &
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
                ((df['PCT_day_change_pre1'] < -0.1) | (df['PCT_day_change_pre2'] < -0.1) | (~df['processor'].str.contains('sell-breakout'))) &
                (~df['processor'].str.contains('Breakout-Sell-after-10')) &
                (~df['processor'].str.contains('1-Sselll-morningDown')) &
                (~df['systemtime'].str.contains('10:3', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:4', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:5', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'SellAllProcessor', color='LG')
        else:
            rb.render(st, empty_df, 'SellAllProcessor', color='LG')
    with col4:
        df = rb.getdf('sell_all_processor')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (~df['filter3'].str.startswith('ReversalLowYear', na=False)) &
                (~df['filter3'].str.startswith('ReversalLowMonth6', na=False)) &
                (abs(df['monthLowChange']) >= 2.5) &
                (abs(df['yearHighChange']) >= 5) &
                (~df['processor'].str.contains('cash-sell-morning-volume')) &
                (~df['processor'].str.contains('Check-News')) &
                (~df['processor'].str.contains('supertrend')) &
                (~df['processor'].str.contains('09_30:checkChartSell')) &
                (~df['processor'].str.contains('Buy-morningup')) &
                (~df['processor'].str.contains('sell-breakout')) &
                (~df['processor'].str.contains('Breakout-Sell-after-10')) &
                (~df['processor'].str.contains('1-Sselll-morningDown')) &
                (~df['systemtime'].str.contains('10:3', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:4', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('10:5', case=False, regex=True, na=False)) &
                (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        if len(filtered_df) >= 1:
            rb.render(st, filtered_df, 'SellAllProcessor', color='LG')
        else:
            rb.render(st, empty_df, 'SellAllProcessor', color='LG')


if __name__ == '__main__':
    main()


