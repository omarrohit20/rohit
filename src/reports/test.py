# Create a streamlit app that shows the mongodb data
from operator import truediv
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
                (df['monthLowChange'] < 50) &
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
                (df['monthLowChange'] < 50) &
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
        filtered_df = None
        try:
            filtered_df = df[
                (
                    (
                        (df['monthLowChange'] < 50) &
                        (df['scrip'].isin(rb.dbnse.scrip.distinct('scrip', {'futures': 'Yes'}))) &
                        (df['yearHighChange'] < -25) &
                        (df['month3HighChange'] > -1) &
                        (df['monthHighChange'] < 9)
                    ) |
                    (
                        (df['yearHighChange'] == df['month3HighChange']) &
                        (df['yearLowChange'] > 50) &
                        #(df['year5HighChange'] > -30) &
                        (df['year5HighChange'] < -10) &
                        (df['year2HighChange'] > -30) &
                        (df['year2HighChange'] < -10) &
                        (df['yearHighChange'] > -30) &
                        (df['yearHighChange'] < -10) &
                        (df['monthHighChange'] < 0) &
                        (df['month3HighChange'] > -30) &
                        (df['month3HighChange'] < -10)
                    )   
                ) 
                ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'breakoutW2HR', color='LG')
    with col3:
        df = rb.getintersectdf('breakoutW2HR', 'movingavg_crossed_up')
        rb.render_sandlterm_data(st, df,'breakoutW2HR : movingavg', color='LG')

    
    col0, col1, col2, col3 = st.columns(4)
    with col0:
        df = rb.getdf_sandlterm('breakoutMHR')
        filtered_df = df
        try:
            filtered_df = df[
                (df['monthLowChange'] < 50) &
                (df['year5HighChange'] < -40) &
                (df['yearHighChange'] > -10) &
                (df['weekHighChange'] > 2) &
                (df['month3LowChange'] > 50)
            ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'breakoutMHR-95%', color='LG')
    with col1:
        df = rb.getdf_sandlterm('breakoutMHR')
        filtered_df = df
        try:
            filtered_df = df[
                (df['monthLowChange'] < 50) &
                (df['yearHighChange'] > -10) &
                (df['month2HighChange'] > 1) &
                (df['weekHighChange'] > 2) &
                (df['month3LowChange'] > 50)
            ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'breakoutMHR', color='LG')
    with col2:
        df = rb.getintersectdf('breakoutMHR', 'movingavg_crossed_up')
        filtered_df = None
        try:
            filtered_df = df[
                (
                    (df['monthLowChange'] < 50) &
                    (df['forecast_day_PCT10_change'] < 10) &
                    (df['yearHighChange'] < -25) &
                    (df['month3HighChange'] > -1) &
                    (df['monthHighChange'] < 9)
                ) 
                ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'breakoutMHR', color='LG')
    with col3:
        df = rb.getintersectdf('breakoutMHR', 'movingavg_crossed_up')
        rb.render_sandlterm_data(st, df,'breakoutMHR  : movingavg', color='LG')    
    
    
    col0, col1, col2, col3 = st.columns(4)
    with col0:
        df = rb.getdf_sandlterm('breakoutMHR')
        filtered_df = df
        try:
            filtered_df = df[
                (df['monthLowChange'] < 50) &
                (df['year2LowChange'] < 80) &
                (df['year5HighChange'] < -20) &
                (df['year2HighChange'] < -10) &
                (df['yearHighChange'] < -10) &
                (df['yearHighChange'] > -20) &
                (df['month3HighChange'] > -10) &
                (df['monthHighChange'] > -2) &
                (df['monthHighChange'] < 2)
                ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'breakoutMHR', color='LG')
    with col1:
        df = rb.getdf_sandlterm('breakoutMHR')
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (
                        #(df['yearHighChange'] <-10) &
                        (df['month3LowChange'] > 30) &
                        #(df['monthLowChange'] < 20) &
                        #(df['week2LowChange'] < 20) &
                        #(df['weekLowChange'] < 10) &
                        (df['PCT_day_change'] < 4)

                    ) |
                    (
                        
                        #(df['yearHighChange'] < -10) &
                        (df['month6HighChange'] < -5) &
                        (df['weekHighChange'] < 2) &
                        (df['month3LowChange'] < 20)
                    )
                ) &
                 
                #((df['PCT_day_change'] < 1) | (df['PCT_change'] < 1)) &
                #(df['month6HighChange'] < -5)
                #((df['month3HighChange'] < -3) | (df['month6HighChange'] < -15))
                (df['monthLowChange'] < 50) &
                (df['month3LowChange'] > 15) &
                (df['monthLowChange'] < 15) &
                ((df['PCT_day_change'] < 1) | (df['PCT_change'] < 1)) &
                (abs(df['month3HighChange']) < 2) &
                (df['yearHighChange'] > -15)
                ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'breakoutMHR', color='LG')
    with col2:
        df = rb.getdf_sandlterm('breakoutMHR')
        filtered_df = None
        try:
            filtered_df = df[
                (
                    (df['monthLowChange'] < 50) &
                    (df['scrip'].isin(rb.dbnse.scrip.distinct('scrip', {'futures': 'Yes'}))) &
                    (df['yearHighChange'] < -25) &
                    (df['month3HighChange'] > -1) &
                    (df['monthHighChange'] < 9)
                ) 
                ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'breakoutMHR', color='LG')
    with col3:
        df = rb.getdf_sandlterm('breakoutMHR')
        rb.render_sandlterm_data(st, df,'breakoutMHR', color='LG')


    col0, col1, col2, col3 = st.columns(4)
    with col0:
        df = rb.getdf_sandlterm('breakoutM2HR')
        filtered_df = df
        try:
            filtered_df = df[
                (df['monthLowChange'] < 50) &
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
                (df['monthLowChange'] < 50) &
                (df['yearHighChange'] > -10) &
                (df['month2HighChange'] > 1) &
                (df['weekHighChange'] > 2) &
                (df['month3LowChange'] > 50)
            ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'breakoutM2HR', color='LG')
    with col2:
        df = rb.getintersectdf('breakoutM2HR', 'movingavg_crossed_up')
        filtered_df = None
        try:
            filtered_df = df[
                (
                    (df['monthLowChange'] < 50) &
                    (df['yearHighChange'] < -25) &
                    (df['month3HighChange'] > -1) &
                    (df['monthHighChange'] < 9)
                ) 
                ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'breakoutM2HR', color='LG')
    with col3:
        df = rb.getintersectdf('breakoutM2HR', 'movingavg_crossed_up')
        rb.render_sandlterm_data(st, df,'breakoutM2HR  : movingavg', color='LG')    
    

    col0, col1, col2, col3 = st.columns(4)
    with col0:
        df = rb.getdf_sandlterm('breakoutM2HR')
        filtered_df = df
        try:
            filtered_df = df[
                (df['weekHighChange'] > -3) &
                (df['monthLowChange'] < 50) &
                (df['year2LowChange'] < 80) &
                (df['year5HighChange'] < -20) &
                (df['year2HighChange'] < -10) &
                (df['yearHighChange'] < -10) &
                (df['yearHighChange'] > -20) &
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
                    (
                        #(df['yearHighChange'] <-10) &
                        (df['month3LowChange'] > 30) &
                        #(df['monthLowChange'] < 20) &
                        #(df['week2LowChange'] < 20) &
                        #(df['weekLowChange'] < 10) &
                        (df['PCT_day_change'] < 4)

                    ) |
                    (
                        
                        #(df['yearHighChange'] < -10) &
                        (df['month6HighChange'] < -5) &
                        (df['weekHighChange'] < 2) &
                        (df['month3LowChange'] < 20)
                    )
                ) &
                 
                #((df['PCT_day_change'] < 1) | (df['PCT_change'] < 1)) &
                #(df['month6HighChange'] < -5)
                #((df['month3HighChange'] < -3) | (df['month6HighChange'] < -15))
                (df['weekHighChange'] > -3) &
                (df['monthLowChange'] < 15) &
                ((df['PCT_day_change'] < 1) | (df['PCT_change'] < 1)) &
                (abs(df['month3HighChange']) < 2) &
                (df['yearHighChange'] > -15)
                ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'breakoutM2HR', color='LG')
    with col2:
        df = rb.getdf_sandlterm('breakoutM2HR')
        filtered_df = None
        try:
            filtered_df = df[
                (
                    (df['weekHighChange'] > -3) &
                    (df['monthLowChange'] < 50) &
                    (df['scrip'].isin(rb.dbnse.scrip.distinct('scrip', {'futures': 'Yes'}))) &
                    (df['yearHighChange'] < -25) &
                    (df['month3HighChange'] > -1) &
                    (df['monthHighChange'] < 9)
                ) 
                ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'breakoutM2HR', color='LG')
    with col3:
        df = rb.getdf_sandlterm('breakoutM2HR')
        rb.render_sandlterm_data(st, df,'breakoutM2HR', color='LG')


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
        df = rb.getintersectdf('breakoutW2LR', 'movingavg_crossed_down')
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
        df = rb.getintersectdf('breakoutMLR', 'movingavg_crossed_down')
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
        df = rb.getintersectdf('breakoutM2LR', 'movingavg_crossed_down')
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

    news_col_order = [
        "scrip",
        "insertion_date",
        "overall_sentiment",
        "conviction",
        "industry",
        "scan_tables",
        "article_count",
    ] + [c for c in rb.column_order_sandlterm if c not in {"scrip", "date", "industry"}]

    col0, col1 = st.columns(2)
    with col0:
        df = _high_conviction_news_df("Bullish")
        rb.render_sandlterm_data(
            st, df, "Bullish · High conviction", color="LG", column_order=news_col_order
        )
    with col1:
        df = _high_conviction_news_df("Bearish")
        rb.render_sandlterm_data(
            st, df, "Bearish · High conviction", color="LG", column_order=news_col_order
        )


def _high_conviction_news_df(sentiment):
    """scrip_news rows: High conviction + Bullish/Bearish, newest insertion_date first."""
    query = {
        "conviction": {"$regex": "^high$", "$options": "i"},
        "overall_sentiment": {"$regex": f"^{sentiment}$", "$options": "i"},
    }
    proj = {
        "_id": 0,
        "news": 0,
        "sectoral_news": 0,
        "analyst_calls": 0,
        "articles": 0,
    }
    try:
        docs = list(rb.dbnse.scrip_news.find(query, proj))
    except Exception:
        docs = []
    df = pd.DataFrame(docs)
    if df.empty:
        return pd.DataFrame(
            columns=["scrip", "insertion_date", "overall_sentiment", "conviction", "industry"]
        )

    if "scrip" in df.columns:
        df["scrip"] = df["scrip"].astype(str).str.strip().str.upper()

    scan_frames = []
    for coll in (
        "breakoutYH",
        "breakoutY2H",
        "breakoutW2HR",
        "breakoutMHR",
        "movingavg_crossed_up",
        "movingavg_crossed_down",
    ):
        try:
            sdf = rb.getdf_sandlterm(coll)
            if sdf is not None and not sdf.empty:
                scan_frames.append(sdf)
        except Exception:
            pass
    if scan_frames:
        scans = pd.concat(scan_frames, ignore_index=True)
        if "scrip" in scans.columns:
            scans = scans.copy()
            scans["scrip"] = scans["scrip"].astype(str).str.strip().str.upper()
            if "date" in scans.columns:
                scans = scans.rename(columns={"date": "scan_date"})
            scans = scans.drop_duplicates(subset=["scrip"], keep="first")
            overlap = [c for c in scans.columns if c in df.columns and c != "scrip"]
            scans = scans.drop(columns=overlap, errors="ignore")
            df = df.merge(scans, on="scrip", how="left")

    if "scan_tables" in df.columns:
        df["scan_tables"] = df["scan_tables"].apply(
            lambda v: ", ".join(str(x) for x in v) if isinstance(v, list) else v
        )

    if "insertion_date" in df.columns:
        df["_ins"] = pd.to_datetime(df["insertion_date"], errors="coerce")
        df = df.sort_values("_ins", ascending=False, na_position="last").drop(columns=["_ins"])
        df["insertion_date"] = pd.to_datetime(df["insertion_date"], errors="coerce")

    return df.reset_index(drop=True)


if __name__ == '__main__':
    main()