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
                           page_title="DashboardShortTerm",
                           initial_sidebar_state="expanded",)
    except Exception:
        pass

    # main title
    st.title('ShortTerm')

    rb.testLearning = True

    col0, col1 = st.columns(2)
    with col0:
        df = rb.getdf_sandlterm('breakoutYH')
        rb.render_sandlterm_data(st, df,'breakoutYH', color='LG')
    with col1:
        df = rb.getdf_sandlterm('breakoutY2H')
        rb.render_sandlterm_data(st, df,'breakoutY2H', color='LG')


    col0, col1, col2, col3 = st.columns(4)
    with col0:
        df = rb.getdf_sandlterm('breakoutW2HR')
        filtered_df = df
        try:
            filtered_df = df[
                (df['weekHighChange'] > 0) &
                ((df['weekHighChange'] > 2) | (df['weekLowChange'] > 5)) &
                ((df['monthLowChange'] > 1) | (df['monthLowChange'] < -3)) &
                ((df['month3HighChange'] > -20) | (df['monthHighChange'] < -10)) &
                ((df['year2LowChange'] > 10) | (df['monthLowChange'] < -3)) &
                ((df['monthHighChange'] < -3) | (df['month3HighChange'] < -15)) &
                ((df['monthHighChange'] > -5.5) | (df['month3HighChange'] < -20)) &
                (df['monthHighChange'] < 5) &
                (df['week2LowChange'] < 5.5) &
                (df['week2LowChange'] != df['weekLowChange']) &
                ((df['yearLowChange'] > 0) | (df['month2HighChange'] > -10))
            ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df,'breakoutW2HR-95%', color='LG')
    with col1:
        df = rb.getdf_sandlterm('breakoutW2HR')
        filtered_df = df
        try:
            filtered_df = df[
                (df['weekHighChange'] > 0) &
                ((df['weekHighChange'] > 2) | (df['weekLowChange'] > 5)) &
                ((df['monthLowChange'] > 1) | (df['monthLowChange'] < -3)) &
                ((df['month3HighChange'] > -20) | (df['monthHighChange'] < -10)) &
                ((df['year2LowChange'] > 10) | (df['monthLowChange'] < -3)) &
                (df['monthHighChange'] < 5) &
                (df['monthHighChange'] > -3.5) &
                ((df['monthHighChange'] < -3) | (df['month3HighChange'] < -15))
                ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df,'breakoutW2HR', color='LG')
    with col2:
        df = rb.getdf_sandlterm('breakoutW2HR')
        filtered_df = df
        try:
            filtered_df = df[
                (df['year2LowChange'] > 10) &
                (df[['forecast_day_PCT3_change','forecast_day_PCT4_change',
                    'forecast_day_PCT5_change','forecast_day_PCT7_change',
                    'forecast_day_PCT10_change']].max(axis=1) > 5) &
                (df['week2LowChange'] < 5.5) &
                (df['monthHighChange'] < 5)
                ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df,'breakoutW2HR-80%', color='LG')
    with col3:
        df = rb.getdf_sandlterm('breakoutW2HR')
        rb.render_sandlterm_data(st, df,'breakoutW2HR', color='LG')

    col0, col1, col2 = st.columns(3)
    with col0:
        df = rb.getdf_sandlterm('breakoutMHR')
        filtered_df = df
        try:
            filtered_df = df[
                (df['forecast_day_PCT10_change'] > 10) &
                (df['PCT_day_change'] > 3) &
                (df['yearHighChange'] < -20)
            ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df,'breakoutMHR-95%', color='LG')
    with col1:
        df = rb.getdf_sandlterm('breakoutMHR')
        filtered_df = df
        try:
            filtered_df = df[
                (df['forecast_day_PCT10_change'] > 10) &
                (df['year5HighChange'] < -30) &
                (df['yearHighChange'] < -20) &
                (df['weekHighChange'] > 2)
            ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df,'breakoutMHR-80%', color='LG')
    with col2:
        df = rb.getdf_sandlterm('breakoutMHR')
        rb.render_sandlterm_data(st, df,'breakoutMHR', color='LG')

    col0, col1, col2 = st.columns(3)
    with col0:
        df = rb.getdf_sandlterm('breakoutM2HR')
        filtered_df = df
        try:
            filtered_df = df[
                (df['year5HighChange'] < -40) &
                (df['yearHighChange'] > -10) &
                (df['weekHighChange'] > 2) &
                (df['month3LowChange'] > 50)
            ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'breakoutM2HR-95%', color='LG')
    with col1:
        df = rb.getdf_sandlterm('breakoutM2HR')
        filtered_df = df
        try:
            filtered_df = df[
                (df['yearHighChange'] > -10) &
                (df['month2HighChange'] > 1) &
                (df['weekHighChange'] > 2) &
                (df['month3LowChange'] > 50)
            ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'breakoutM2HR', color='LG')
    with col2:
        df = rb.getdf_sandlterm('breakoutM2HR')
        rb.render_sandlterm_data(st, df, 'breakoutM2HR', color='LG')
    

    col0, col1, col2 = st.columns(3)
    with col0:
        df = rb.getdf_sandlterm('breakoutM2HR')
        filtered_df = df
        try:
            filtered_df = df[
                (df['year5HighChange'] < -20) &
                (df['year2HighChange'] < -10) &
                (df['yearHighChange'] < -10) &
                (df['month3HighChange'] > -10) &
                (df['monthHighChange'] > -2) &
                (df['monthHighChange'] < 2)
                ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'breakoutM2HR', color='LG')
    with col1:
        df = rb.getdf_sandlterm('breakoutM2HR')
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (df['yearHighChange'] <-10) &
                    (df['month3LowChange'] > 50) &
                    #(df['monthLowChange'] < 20) &
                    #(df['week2LowChange'] < 20) &
                    #(df['weekLowChange'] < 10) &
                    (df['PCT_day_change'] < 4)

                ) |
                (
                    ((df['PCT_day_change'] < 1) | (df['PCT_change'] < 1)) &
                    (df['yearHighChange'] < -10) &
                    (df['month6HighChange'] < -5) &
                    (df['weekHighChange'] < 2) &
                    (df['month3LowChange'] < 20)
                )
                #((df['PCT_day_change'] < 1) | (df['PCT_change'] < 1)) &
                #(df['month6HighChange'] < -5)

                #(df['month3HighChange'] > -3.5) &
                #((df['month3HighChange'] < -3) | (df['month6HighChange'] < -15))
                ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'breakoutM2HR', color='LG')
    with col2:
        df = rb.getdf_sandlterm('breakoutM2HR')
        rb.render_sandlterm_data(st, df, 'breakoutM2HR', color='LG')
    

    col0, col1, col2 = st.columns(3)
    with col0:
        df = rb.getdf_sandlterm('breakoutW2LR')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] < -4) &
                (df['PCT_change'] < -5) &
                (df['weekHighChange'] < -2) &
                (df['yearLowChange'] < 10)
            ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df,'breakoutW2LR-75%', color='LG')
    with col1:
        df = rb.getdf_sandlterm('breakoutW2LR')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] < -4) &
                (df['PCT_change'] < -5) &
                (df['weekHighChange'] < -2) &
                (df['yearLowChange'] < 10)
            ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df,'breakoutW2LR-75%', color='LG')
    with col2:
        df = rb.getdf_sandlterm('breakoutW2LR')
        rb.render_sandlterm_data(st, df,'breakoutW2LR', color='LG')


    col0, col1, col2 = st.columns(3)
    with col0:
        df = rb.getdf_sandlterm('breakoutMLR')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] < -5) &
                (df['monthHighChange'] < -10) &
                (df['yearLowChange'] < 10)
            ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df,'breakoutMLR-75%', color='LG')
    with col1:
        df = rb.getdf_sandlterm('breakoutMLR')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] < -5) &
                (df['monthHighChange'] < -10) &
                (df['yearLowChange'] < 10)
            ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df,'breakoutMLR-75%', color='LG')
    with col2:
        df = rb.getdf_sandlterm('breakoutMLR')
        rb.render_sandlterm_data(st, df,'breakoutMLR', color='LG')


    col0, col1, col2 = st.columns(3)
    with col0:
        df = rb.getdf_sandlterm('breakoutM2LR')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] < -5) &
                (df['PCT_change'] < -5) &
                (df['monthHighChange'] < -10) &
                (df['weekLowChange'] < -5)
            ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'breakoutM2LR-95%', color='LG')
    with col1:
        df = rb.getdf_sandlterm('breakoutM2LR')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_day_change'] < -5) &
                (df['PCT_change'] < -5) &
                (df['monthHighChange'] < -10) &
                (df['weekLowChange'] < -5)
            ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'breakoutM2LR-95%', color='LG')
    with col2:
        df = rb.getdf_sandlterm('breakoutM2LR')
        rb.render_sandlterm_data(st, df, 'breakoutM2LR', color='LG')
    

    col0, col1, col2, col3, col4, col5 = st.columns(6)
    with col0:
        df = rb.getdf_sandlterm('movingavg_crossed_up')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['forecast_day_PCT3_change'] > 5) | (df['forecast_day_PCT3_change'] < -5)
                ) &
                (
                (df['yearHighChange'] < -30) |
                (df['month3HighChange'] < -15)
                )
                ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'movingavg_crossed_up', color='LG')
    with col1:
        df = rb.getdf_sandlterm('movingavg_crossed_up')
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (df['month3HighChange'] > -10) &
                    (df['month3LowChange'] < 10) &
                    (df['weekLowChange'] < 1) &
                    (df['week2LowChange'] < 2.5)
                )
                &
                (
                    (abs(df['PCT_day_change']) > 1.5) | 
                    (abs(df['PCT_change']) > 2)
                )
                ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'movingavg_crossed_up', color='LG')
    with col2:
        df = rb.getdf_sandlterm('movingavg_crossed_up')
        rb.render_sandlterm_data(st, df, 'movingavg_crossed_up', color='LG')
    with col3:
        df = rb.getdf_sandlterm('movingavg_crossed_down')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['forecast_day_PCT3_change'] < -5) | (df['forecast_day_PCT3_change'] > 5)
                 ) &
                (
                (df['yearLowChange'] > 30) |
                (df['month3LowChange'] > 15)
                )
                ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'movingavg_crossed_down', color='LG')
    with col4:
        df = rb.getdf_sandlterm('movingavg_crossed_down')
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (df['month3LowChange'] < 10) &
                    (df['month3HighChange'] > -10) &
                    (df['weekHighChange'] > -1) &
                    (df['week2HighChange'] > -2.5)
                )
                &
                (
                    (abs(df['PCT_day_change']) > 1.5) | 
                    (abs(df['PCT_change']) > 2)
                )
            ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'movingavg_crossed_down', color='LG')
    with col5:
        df = rb.getdf_sandlterm('movingavg_crossed_down')
        rb.render_sandlterm_data(st, df, 'movingavg_crossed_down', color='LG')


    col0, col1, col2, col3, col4, col5 = st.columns(6)
    with col0:
        df = rb.getdf_sandlterm('movingavg_crossed_up')
        filtered_df = df
        try:
            filtered_df = df[
                (df['yearHighChange'] < -30) |
                (df['month3HighChange'] < -15) 
                ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'movingavg_crossed_up', color='LG')
    with col1:
        df = rb.getdf_sandlterm('movingavg_crossed_up')
        filtered_df = df
        try:
            filtered_df = df[
                (abs(df['PCT_day_change']) > 1.5) | 
                (abs(df['PCT_change']) > 2)
                ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'movingavg_crossed_up', color='LG')
    with col2:
        df = rb.getdf_sandlterm('movingavg_crossed_up')
        rb.render_sandlterm_data(st, df, 'movingavg_crossed_up', color='LG')
    with col3:
        df = rb.getdf_sandlterm('movingavg_crossed_down')
        filtered_df = df
        try:
            filtered_df = df[
                (df['yearLowChange'] > 30) |
                (df['month3LowChange'] > 15) 
                ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'movingavg_crossed_down', color='LG')
    with col4:
        df = rb.getdf_sandlterm('movingavg_crossed_down')
        filtered_df = df
        try:
            filtered_df = df[
                (abs(df['PCT_day_change']) > 1.5) | 
                (abs(df['PCT_change']) > 2)
                ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'movingavg_crossed_down', color='LG')
    with col5:
        df = rb.getdf_sandlterm('movingavg_crossed_down')
        rb.render_sandlterm_data(st, df, 'movingavg_crossed_down', color='LG')
        





if __name__ == '__main__':
    main()