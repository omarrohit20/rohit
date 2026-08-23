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
    st.title('Historical Analysis')


    

    # movingavg_crossed_up filters tuned for historical fwd 5d return > 10%
    # (regressiondata scan: baseline ~8.4%; these lift hit-rate to ~13-15%)
    col0, col1, col2, col3, col4 = st.columns(5)
    with col0:
        df = rb.getdf_sandlterm('movingavg_crossed_up')
        filtered_df = df
        try:
            # lift 1.76 — PCT_change > 3
            filtered_df = df[df['PCT_change'] > 3]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'maCrossUp:>10%/5d PCT>3', color='LG')
    with col1:
        df = rb.getdf_sandlterm('movingavg_crossed_up')
        filtered_df = df
        try:
            # lift 1.69 — deep year DD + recent high run + green day
            filtered_df = df[
                (df['yearHighChange'] < -30) &
                (df['forecast_day_PCT5_change'] > 5) &
                (df['PCT_day_change'] > 1.5)
            ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'maCrossUp:>10%/5d yH<-30 PCT5>5 day>1.5', color='LG')
    with col2:
        df = rb.getdf_sandlterm('movingavg_crossed_up')
        filtered_df = df
        try:
            # lift 1.52 — deep drawdown + strong day candle
            filtered_df = df[
                (
                    (df['yearHighChange'] < -30) |
                    (df['month3HighChange'] < -15)
                ) &
                (df['PCT_day_change'] > 3)
            ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'maCrossUp:>10%/5d deepDD day>3', color='LG')
    with col3:
        df = rb.getdf_sandlterm('movingavg_crossed_up')
        filtered_df = df
        try:
            # lift 1.51 — deep drawdown + 5d high already >5%
            filtered_df = df[
                (
                    (df['yearHighChange'] < -30) |
                    (df['month3HighChange'] < -15)
                ) &
                (df['forecast_day_PCT5_change'] > 5)
            ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'maCrossUp:>10%/5d deepDD PCT5>5', color='LG')
    with col4:
        df = rb.getdf_sandlterm('movingavg_crossed_up')
        filtered_df = df
        try:
            # lift 1.60 — 5d high run already >10%
            filtered_df = df[df['forecast_day_PCT5_change'] > 10]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'maCrossUp:>10%/5d PCT5>10', color='LG')
    




if __name__ == '__main__':
    main()