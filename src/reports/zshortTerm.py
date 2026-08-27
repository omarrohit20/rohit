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

    rb.zshortTerm = True


    col1, col2, col3, col4 = st.columns(4)
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
                            (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                            (df['weekHighChange'] > 0)
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
                        (~df['filter3'].str.contains('ReversalLowMonth3', case=False, regex=True, na=False)) &
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
                        (~df['filter3'].str.contains('ReversalHighMonth3', case=False, regex=True, na=False)) &
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
                            (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                            (df['weekLowChange'] < 0)
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
                        (~df['filter3'].str.contains('ReversalHighMonth3', case=False, regex=True, na=False)) &
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
                        (~df['filter3'].str.contains('ReversalLowMonth3', case=False, regex=True, na=False)) &
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
    
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        df = rb.getdf('morning-volume-breakout-buy')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (~df['systemtime'].str.contains('09:20', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('09:55', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                    (
                        (
                            (df['yearHighChange'] < 0) &
                            ((df['PCT_day_change_pre1'] > 1) | (df['PCT_day_change_pre2'] > 1)) &
                            ((df['PCT_day_change_pre1'] < -1) | (df['PCT_day_change_pre2'] < -1)) &
                            ((df['PCT_day_change_pre1'] < 2) & (df['PCT_day_change_pre2'] < 2)) &
                            (df['PCT_day_change'] > -1.3) &
                            (df['PCT_day_change'] < 1)
                        ) |
                        (
                            # ((df['PCT_day_change_pre1'] < 1.3) & (df['PCT_day_change_pre2'] < 1.3) & (df['PCT_day_change'] < 1.3)) &
                            (df['mlData'].str.contains('0@@', case=False, regex=True, na=False)) 
                            # ZPre1_UpStairs 
                             
                        ) |
                        (
                            ((df['PCT_day_change'] < 1)) &
                            (df['mlData'].str.contains('#ZPre', case=False, regex=True, na=False))  
                             
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
                        (~df['filter3'].str.contains('ReversalHighMonth3', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('ReversalLowMonth3', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakHighMonth6', case=False, regex=True, na=False))
                    ) |
                    (
                        (~df['filter3'].str.contains('ReversalLowMonth3', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakHighMonth3', case=False, regex=True, na=False))
                    )
                )
            ]
        except KeyError as e:
            print("")
        if len(filtered_df) < 20:
            rb.render(st, filtered_df, 'BreakHigh - Volume', color='LG')
        else:
            rb.render(st, empty_df, 'BreakHigh - Volume', color='LG')
    with col2:
        df = rb.getdf('morning-volume-breakout-buy')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (~df['systemtime'].str.contains('09:20', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('09:55', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                    (df['monthLowChange'] > 10) &
                    (
                        (
                            (df['yearLowChange'] > 0) &
                            ((df['PCT_day_change_pre1'] < -1) | (df['PCT_day_change_pre2'] < -1)) &
                            ((df['PCT_day_change_pre1'] > -1) | (df['PCT_day_change_pre2'] > -1)) &
                            ((df['PCT_day_change_pre1'] < 2) & (df['PCT_day_change_pre2'] < 2)) &
                            (df['PCT_day_change'] > -1) &
                            (df['PCT_day_change'] < 1.3)
                        ) |
                        (
                            # ((df['PCT_day_change_pre1'] < 1.3) & (df['PCT_day_change_pre2'] < 1.3) & (df['PCT_day_change'] < 1.3)) &
                            (df['mlData'].str.contains('0@@', case=False, regex=True, na=False)) 
                        ) |
                        (
                            ((df['PCT_day_change'] < 1)) &
                            (df['mlData'].str.contains('#ZPre', case=False, regex=True, na=False))  
                             
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
                        (~df['filter3'].str.contains('ReversalLowMonth6', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('ReversalHighMonth3', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('ReversalLowMonth3', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakLowMonth6', case=False, regex=True, na=False))
                    ) |
                    (
                        (~df['filter3'].str.contains('ReversalHighMonth3', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakLowMonth3', case=False, regex=True, na=False))
                    )
                )
            ]
        except KeyError as e:
            print("")
        if len(filtered_df) < 20:
            rb.render(st, filtered_df, 'ReversalBreakLow - Volume', color='LG')
        else:
            rb.render(st, empty_df, 'ReversalBreakLow - volume', color='LG')
    with col3:
        df = rb.getdf('morning-volume-breakout-sell')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (~df['systemtime'].str.contains('09:20', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('09:55', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                    (
                        (
                            (df['yearLowChange'] > 0) &
                            ((df['PCT_day_change_pre1'] < -1) | (df['PCT_day_change_pre2'] < -1)) &
                            ((df['PCT_day_change_pre1'] > 1) | (df['PCT_day_change_pre2'] > 1)) &
                            ((df['PCT_day_change_pre1'] > -2) & (df['PCT_day_change_pre2'] > -2)) &
                            (df['PCT_day_change'] > -1) &
                            (df['PCT_day_change'] < 1.3)
                        ) |
                        (
                            # ((df['PCT_day_change_pre1'] > -1.3) & (df['PCT_day_change_pre2'] > -1.3) & (df['PCT_day_change'] > -1.3)) &
                            (df['mlData'].str.contains('0@@', case=False, regex=True, na=False)) 
                        ) |
                        (
                            ((df['PCT_day_change'] > -1)) &
                            (df['mlData'].str.contains('#ZPre', case=False, regex=True, na=False))  
                             
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
                        (~df['filter3'].str.contains('ReversalLowMonth6', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('ReversalHighMonth3', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('ReversalLowMonth3', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakLowMonth6', case=False, regex=True, na=False))
                    ) |
                    (
                        (~df['filter3'].str.contains('ReversalHighMonth3', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakLowMonth3', case=False, regex=True, na=False))
                    )
                )
            ]
        except KeyError as e:
            print("")
        if len(filtered_df) < 20:
            rb.render(st, filtered_df, 'BreakLow - Volume', color='LG')
        else:
            rb.render(st, empty_df, 'BreakLow - Volume', color='LG')
    with col4:
        df = rb.getdf('morning-volume-breakout-sell')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (~df['systemtime'].str.contains('09:20', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('09:55', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                    (df['monthHighChange'] < -10) &
                    (
                        (
                            (df['yearHighChange'] < 0) &
                            ((df['PCT_day_change_pre1'] > 1) | (df['PCT_day_change_pre2'] > 1)) &
                            ((df['PCT_day_change_pre1'] < 1) | (df['PCT_day_change_pre2'] < 1)) &
                            ((df['PCT_day_change_pre1'] > -2) & (df['PCT_day_change_pre2'] > -2)) &
                            (df['PCT_day_change'] > -1.3) &
                            (df['PCT_day_change'] < 1)
                        ) |
                        (
                            # ((df['PCT_day_change_pre1'] > -1.3) & (df['PCT_day_change_pre2'] > -1.3) & (df['PCT_day_change'] > -1.3)) &
                            (df['mlData'].str.contains('0@@', case=False, regex=True, na=False))
                        ) |
                        (
                            ((df['PCT_day_change'] > -1)) &
                            (df['mlData'].str.contains('#ZPre', case=False, regex=True, na=False))   
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
                        (~df['filter3'].str.contains('ReversalHighMonth3', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('ReversalLowMonth3', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakHighMonth6', case=False, regex=True, na=False))
                    ) |
                    (
                        (~df['filter3'].str.contains('ReversalLowMonth3', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakHighMonth3', case=False, regex=True, na=False))
                    ) 
                )
            ]
        except KeyError as e:
            print("")
        if len(filtered_df) < 20:
            rb.render(st, filtered_df, 'ReversalBreakHigh - Volume', color='LG')
        else:
            rb.render(st, empty_df, 'ReversalBreakHigh - Volume', color='LG')
    

    col0, col1, col2, col3, col4, col5 = st.columns(6)
    with col0:
        df = rb.getdf('supertrend-morning-buy')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (~df['systemtime'].str.contains('09:20', case=False, regex=True, na=False)) &
                    # (~df['systemtime'].str.contains('09:55', case=False, regex=True, na=False)) &
                    # (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                    (
                        (
                            (df['yearHighChange'] < 0) &
                            ((df['PCT_day_change_pre1'] > 1) | (df['PCT_day_change_pre2'] > 1)) &
                            ((df['PCT_day_change_pre1'] < -1) | (df['PCT_day_change_pre2'] < -1)) &
                            ((df['PCT_day_change_pre1'] < 2) & (df['PCT_day_change_pre2'] < 2)) &
                            (df['PCT_day_change'] > -1.3) &
                            (df['PCT_day_change'] < 1)
                        ) |
                        (
                            # ((df['PCT_day_change_pre1'] < 1.3) & (df['PCT_day_change_pre2'] < 1.3) & (df['PCT_day_change'] < 1.3)) &
                            (df['mlData'].str.contains('0@@', case=False, regex=True, na=False)) 
                            # ZPre1_UpStairs 
                             
                        ) |
                        (
                            ((df['PCT_day_change'] < 1)) &
                            (df['mlData'].str.contains('#ZPre', case=False, regex=True, na=False))  
                             
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
                        (~df['filter3'].str.contains('ReversalLowMonth3', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakHighMonth3', case=False, regex=True, na=False))
                    )
                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakHigh - Supertrend Morning Buy', color='LG', renderf10buy00=True)
    with col1:
        df = rb.getdf('09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (~df['systemtime'].str.contains('09:20', case=False, regex=True, na=False)) &
                    # (~df['systemtime'].str.contains('09:55', case=False, regex=True, na=False)) &
                    # (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                    (
                        (
                            (df['yearHighChange'] < 0) &
                            ((df['PCT_day_change_pre1'] > 1) | (df['PCT_day_change_pre2'] > 1)) &
                            ((df['PCT_day_change_pre1'] < -1) | (df['PCT_day_change_pre2'] < -1)) &
                            ((df['PCT_day_change_pre1'] < 2) & (df['PCT_day_change_pre2'] < 2)) &
                            (df['PCT_day_change'] > -1.3) &
                            (df['PCT_day_change'] < 1)
                        ) |
                        (
                            # ((df['PCT_day_change_pre1'] < 1.3) & (df['PCT_day_change_pre2'] < 1.3) & (df['PCT_day_change'] < 1.3)) &
                            (df['mlData'].str.contains('0@@', case=False, regex=True, na=False)) 
                            # ZPre1_UpStairs 
                             
                        ) |
                        (
                            ((df['PCT_day_change'] < 1)) &
                            (df['mlData'].str.contains('#ZPre', case=False, regex=True, na=False))  
                             
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
                        (~df['filter3'].str.contains('ReversalLowMonth3', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakHighMonth3', case=False, regex=True, na=False))
                    )
                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakHigh - Crossed 2 Day Highs', color='LG', renderf10buy00=True)
    with col2:
        df = rb.getdf('crossed-day-high')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (~df['systemtime'].str.contains('09:30', case=False, regex=True, na=False)) &
                    # (~df['systemtime'].str.contains('09:55', case=False, regex=True, na=False)) &
                    # (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                    (
                        (
                            (df['yearHighChange'] < 0) &
                            ((df['PCT_day_change_pre1'] > 1) | (df['PCT_day_change_pre2'] > 1)) &
                            ((df['PCT_day_change_pre1'] < -1) | (df['PCT_day_change_pre2'] < -1)) &
                            ((df['PCT_day_change_pre1'] < 2) & (df['PCT_day_change_pre2'] < 2)) &
                            (df['PCT_day_change'] > -1.3) &
                            (df['PCT_day_change'] < 1)
                        ) |
                        (
                            # ((df['PCT_day_change_pre1'] < 1.3) & (df['PCT_day_change_pre2'] < 1.3) & (df['PCT_day_change'] < 1.3)) &
                            (df['mlData'].str.contains('0@@', case=False, regex=True, na=False)) 
                            # ZPre1_UpStairs 
                             
                        ) |
                        (
                            ((df['PCT_day_change'] < 1)) &
                            (df['mlData'].str.contains('#ZPre', case=False, regex=True, na=False))  
                             
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
                        (~df['filter3'].str.contains('ReversalLowMonth3', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakHighMonth3', case=False, regex=True, na=False))
                    )
                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakHigh - Crossed Day Highs', color='LG', renderf10buy00=True)
    with col3:
        df = rb.getdf('supertrend-morning-sell')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (~df['systemtime'].str.contains('09:20', case=False, regex=True, na=False)) &
                    # (~df['systemtime'].str.contains('09:55', case=False, regex=True, na=False)) &
                    # (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                    (
                        (
                            (df['yearLowChange'] > 0) &
                            ((df['PCT_day_change_pre1'] < -1) | (df['PCT_day_change_pre2'] < -1)) &
                            ((df['PCT_day_change_pre1'] > 1) | (df['PCT_day_change_pre2'] > 1)) &
                            ((df['PCT_day_change_pre1'] > -2) & (df['PCT_day_change_pre2'] > -2)) &
                            (df['PCT_day_change'] > -1) &
                            (df['PCT_day_change'] < 1.3)
                        ) |
                        (
                            # ((df['PCT_day_change_pre1'] > -1.3) & (df['PCT_day_change_pre2'] > -1.3) & (df['PCT_day_change'] > -1.3)) &
                            (df['mlData'].str.contains('0@@', case=False, regex=True, na=False)) 
                        ) |
                        (
                            ((df['PCT_day_change'] > -1)) &
                            (df['mlData'].str.contains('#ZPre', case=False, regex=True, na=False))  
                             
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
                        (~df['filter3'].str.contains('ReversalHighMonth3', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakLowMonth3', case=False, regex=True, na=False))
                    )
                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakLow - Supertrend Morning Sell', color='LG', renderf10sell00=True)
    with col4:
        df = rb.getdf('09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (~df['systemtime'].str.contains('09:20', case=False, regex=True, na=False)) &
                    # (~df['systemtime'].str.contains('09:55', case=False, regex=True, na=False)) &
                    # (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                    (
                        (
                            (df['yearLowChange'] > 0) &
                            ((df['PCT_day_change_pre1'] < -1) | (df['PCT_day_change_pre2'] < -1)) &
                            ((df['PCT_day_change_pre1'] > 1) | (df['PCT_day_change_pre2'] > 1)) &
                            ((df['PCT_day_change_pre1'] > -2) & (df['PCT_day_change_pre2'] > -2)) &
                            (df['PCT_day_change'] > -1) &
                            (df['PCT_day_change'] < 1.3)
                        ) |
                        (
                            # ((df['PCT_day_change_pre1'] > -1.3) & (df['PCT_day_change_pre2'] > -1.3) & (df['PCT_day_change'] > -1.3)) &
                            (df['mlData'].str.contains('0@@', case=False, regex=True, na=False)) 
                        ) |
                        (
                            ((df['PCT_day_change'] > -1)) &
                            (df['mlData'].str.contains('#ZPre', case=False, regex=True, na=False))  
                             
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
                        (~df['filter3'].str.contains('ReversalHighMonth3', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakLowMonth3', case=False, regex=True, na=False))
                    )
                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakLow - Crossed 2 Day Lows', color='LG', renderf10sell00=True)
    with col5:
        df = rb.getdf('crossed-day-low')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (~df['systemtime'].str.contains('09:30', case=False, regex=True, na=False)) &
                    # (~df['systemtime'].str.contains('09:55', case=False, regex=True, na=False)) &
                    # (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) &
                    (
                        (
                            (df['yearLowChange'] > 0) &
                            ((df['PCT_day_change_pre1'] < -1) | (df['PCT_day_change_pre2'] < -1)) &
                            ((df['PCT_day_change_pre1'] > 1) | (df['PCT_day_change_pre2'] > 1)) &
                            ((df['PCT_day_change_pre1'] > -2) & (df['PCT_day_change_pre2'] > -2)) &
                            (df['PCT_day_change'] > -1) &
                            (df['PCT_day_change'] < 1.3)
                        ) |
                        (
                            # ((df['PCT_day_change_pre1'] > -1.3) & (df['PCT_day_change_pre2'] > -1.3) & (df['PCT_day_change'] > -1.3)) &
                            (df['mlData'].str.contains('0@@', case=False, regex=True, na=False)) 
                        ) |
                        (
                            ((df['PCT_day_change'] > -1)) &
                            (df['mlData'].str.contains('#ZPre', case=False, regex=True, na=False))  
                             
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
                        (~df['filter3'].str.contains('ReversalHighMonth3', case=False, regex=True, na=False)) &
                        (df['filter3'].str.contains('BreakLowMonth3', case=False, regex=True, na=False))
                    )
                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakLow - Crossed Day Lows', color='LG', renderf10sell00=True)


    col0, col1, col2, col3, col4, col5 = st.columns(6)
    with col0:
        df = rb.getdf('supertrend-morning-buy')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (~df['systemtime'].str.contains('09:20', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('09:55', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) 
                ) &
                (
                    (
                        (df['filter3'].str.contains('ReversalLowYear2', case=False, regex=True, na=False)) |
                        (df['filter3'].str.contains('ReversalLowYear', case=False, regex=True, na=False)) |
                        (df['filter3'].str.contains('ReversalLowMonth6', case=False, regex=True, na=False)) |
                        (df['filter3'].str.contains('ReversalLowMonth3', case=False, regex=True, na=False))
                        
                    ) &
                    (
                        (~df['filter3'].str.contains('ReversalHighYear2', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('ReversalHighYear', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('ReversalHighMonth6', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('ReversalHighMonth3', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakHighYear2', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakHighYear', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakHighMonth6', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakHighMonth3', case=False, regex=True, na=False)) 
                        
                    ) 
                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'ReversalLow - Supertrend Morning Buy', height=200, color='LG', renderf10buy00=True)
    with col1:
        df = rb.getdf('09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (~df['systemtime'].str.contains('09:20', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('09:55', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) 
                ) &
                (
                    (
                        (df['filter3'].str.contains('ReversalLowYear2', case=False, regex=True, na=False)) |
                        (df['filter3'].str.contains('ReversalLowYear', case=False, regex=True, na=False)) |
                        (df['filter3'].str.contains('ReversalLowMonth6', case=False, regex=True, na=False)) |
                        (df['filter3'].str.contains('ReversalLowMonth3', case=False, regex=True, na=False))
                        
                    ) &
                    (
                        (~df['filter3'].str.contains('ReversalHighYear2', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('ReversalHighYear', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('ReversalHighMonth6', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('ReversalHighMonth3', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakHighYear2', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakHighYear', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakHighMonth6', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakHighMonth3', case=False, regex=True, na=False)) 
                        
                    ) 
                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'ReversalLow - Crossed 2 Day Highs', height=200, color='LG', renderf10buy00=True)
    with col2:
        df = rb.getdf('crossed-day-high')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (~df['systemtime'].str.contains('09:20', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('09:55', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) 
                ) &
                (
                    (
                        (df['filter3'].str.contains('ReversalLowYear2', case=False, regex=True, na=False)) |
                        (df['filter3'].str.contains('ReversalLowYear', case=False, regex=True, na=False)) |
                        (df['filter3'].str.contains('ReversalLowMonth6', case=False, regex=True, na=False)) |
                        (df['filter3'].str.contains('ReversalLowMonth3', case=False, regex=True, na=False))
                        
                    ) &
                    (
                        (~df['filter3'].str.contains('ReversalHighYear2', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('ReversalHighYear', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('ReversalHighMonth6', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('ReversalHighMonth3', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakHighYear2', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakHighYear', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakHighMonth6', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakHighMonth3', case=False, regex=True, na=False)) 
                        
                    ) 
                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'ReversalLow - Crossed Day Highs', height=200, color='LG', renderf10buy00=True)
    with col3:
        df = rb.getdf('supertrend-morning-sell')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (~df['systemtime'].str.contains('09:20', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('09:55', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) 
                ) &
                (
                    (
                        (df['filter3'].str.contains('ReversalHighYear2', case=False, regex=True, na=False)) |
                        (df['filter3'].str.contains('ReversalHighYear', case=False, regex=True, na=False)) |
                        (df['filter3'].str.contains('ReversalHighMonth6', case=False, regex=True, na=False)) |
                        (df['filter3'].str.contains('ReversalHighMonth3', case=False, regex=True, na=False))
                        
                    ) &
                    (
                        (~df['filter3'].str.contains('ReversalLowYear2', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('ReversalLowYear', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('ReversalLowMonth6', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('ReversalLowMonth3', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakLowYear2', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakLowYear', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakLowMonth6', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakLowMonth3', case=False, regex=True, na=False)) 
                        
                    ) 
                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'ReversalHigh - Supertrend Morning Sell', height=200, color='LG', renderf10sell00=True)
    with col4:
        df = rb.getdf('09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (~df['systemtime'].str.contains('09:20', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('09:55', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) 
                ) &
                (
                    (
                        (df['filter3'].str.contains('ReversalHighYear2', case=False, regex=True, na=False)) |
                        (df['filter3'].str.contains('ReversalHighYear', case=False, regex=True, na=False)) |
                        (df['filter3'].str.contains('ReversalHighMonth6', case=False, regex=True, na=False)) |
                        (df['filter3'].str.contains('ReversalHighMonth3', case=False, regex=True, na=False))
                        
                    ) &
                    (
                        (~df['filter3'].str.contains('ReversalLowYear2', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('ReversalLowYear', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('ReversalLowMonth6', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('ReversalLowMonth3', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakLowYear2', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakLowYear', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakLowMonth6', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakLowMonth3', case=False, regex=True, na=False)) 
                        
                    ) 
                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'ReversalHigh - Crossed 2 Day Lows', height=200, color='LG', renderf10sell00=True)
    with col5:
        df = rb.getdf('crossed-day-low')
        expected_columns = list(set(df.columns))
        empty_df = pd.DataFrame(columns=expected_columns)
        filtered_df = df
        try:
            filtered_df = df[
                (
                    (~df['systemtime'].str.contains('09:20', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('09:55', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, na=False)) 
                ) &
                (
                    (
                        (df['filter3'].str.contains('ReversalHighYear2', case=False, regex=True, na=False)) |
                        (df['filter3'].str.contains('ReversalHighYear', case=False, regex=True, na=False)) |
                        (df['filter3'].str.contains('ReversalHighMonth6', case=False, regex=True, na=False)) |
                        (df['filter3'].str.contains('ReversalHighMonth3', case=False, regex=True, na=False))
                        
                    ) &
                    (
                        (~df['filter3'].str.contains('ReversalLowYear2', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('ReversalLowYear', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('ReversalLowMonth6', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('ReversalLowMonth3', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakLowYear2', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakLowYear', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakLowMonth6', case=False, regex=True, na=False)) &
                        (~df['filter3'].str.contains('BreakLowMonth3', case=False, regex=True, na=False)) 
                        
                    ) 
                )
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'ReversalHigh - Crossed Day Lows', height=200, color='LG', renderf10sell00=True)

    
        
    st.divider()
    st.divider()

    
    col0, col1, col2, col3 = st.columns(4)
    with col0:
        df = rb.getdfResult('highBuy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['year5HighChange'] > -20) &
                (df['yearHighChange'] > -20) &
                (df['yearLowChange'] > 15) &
                (df['month3LowChange'] > 15) &
                (df['PCT_day_change'] > 1) &
                (df['PCT_day_change_pre1'] < 1.5) &
                (df['PCT_day_change_pre2'] < 1.5) &
                ((df['PCT_day_change_pre1'] < 1) | (df['PCT_day_change_pre2'] < 1)) &
                (~df['filter3'].str.contains('ReversalHighYear', case=False, regex=True, na=False)) &
                (df['filter3'].str.contains('BreakHighYear2', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakHighYear2', column_conf=rb.column_config_result, column_order=rb.column_order_result, height=200, renderml=True, color='LG')
    with col1:
        df = rb.getdfResult('highBuy')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['filter3'].str.contains('ReversalHighYear', case=False, regex=True, na=False)) &
                (df['filter3'].str.contains('BreakHighYear2', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakHighYear2', column_conf=rb.column_config_result, column_order=rb.column_order_result, height=200, renderml=True, color='LG')
    with col2:
        df = rb.getdfResult('highBuy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['yearLowChange'] < 20) &
                (df['yearHighChange'] < -15) &
                (df['month3HighChange'] < -15) &
                (df['PCT_day_change'] < -1) &
                (df['PCT_day_change_pre1'] > -1.5) &
                (df['PCT_day_change_pre2'] > -1.5) &
                ((df['PCT_day_change_pre1'] > -1) | (df['PCT_day_change_pre2'] > -1)) &
                (~df['filter3'].str.contains('ReversalLowYear', case=False, regex=True, na=False)) &
                (df['filter3'].str.contains('BreakLowYear2', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakLowYear2', column_conf=rb.column_config_result, column_order=rb.column_order_result, height=200, renderml=True, color='LG')
    with col3:
        df = rb.getdfResult('highBuy')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['filter3'].str.contains('ReversalLowYear', case=False, regex=True, na=False)) &
                (df['filter3'].str.contains('BreakLowYear2', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakLowYear2', column_conf=rb.column_config_result, column_order=rb.column_order_result, height=200, renderml=True, color='LG')
    
    col0, col1, col2, col3 = st.columns(4)
    with col0:
        df = rb.getdfResult('highBuy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['year5HighChange'] > -20) &
                (df['yearHighChange'] > -20) &
                (df['yearLowChange'] > 15) &
                (df['month3LowChange'] > 15) &
                (df['PCT_day_change'] > 1) &
                (df['PCT_day_change_pre1'] < 1.5) &
                (df['PCT_day_change_pre2'] < 1.5) &
                ((df['PCT_day_change_pre1'] < 1) | (df['PCT_day_change_pre2'] < 1)) &
                (~df['filter3'].str.contains('ReversalHighYear', case=False, regex=True, na=False)) &
                (~df['filter3'].str.contains('BreakHighYear2', case=False, regex=True, na=False)) &
                (df['filter3'].str.contains('BreakHighYear', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakHighYear', column_conf=rb.column_config_result, column_order=rb.column_order_result, height=200, renderml=True, color='LG')
    with col1:
        df = rb.getdfResult('highBuy')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['filter3'].str.contains('ReversalHighYear', case=False, regex=True, na=False)) &
                (~df['filter3'].str.contains('BreakHighYear2', case=False, regex=True, na=False)) &
                (df['filter3'].str.contains('BreakHighYear', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakHighYear', column_conf=rb.column_config_result, column_order=rb.column_order_result, height=200, renderml=True, color='LG')
    with col2:
        df = rb.getdfResult('highBuy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['yearLowChange'] < 20) &
                (df['yearHighChange'] < -15) &
                (df['month3HighChange'] < -15) &
                (df['PCT_day_change'] < -1) &
                (df['PCT_day_change_pre1'] > -1.5) &
                (df['PCT_day_change_pre2'] > -1.5) &
                ((df['PCT_day_change_pre1'] > -1) | (df['PCT_day_change_pre2'] > -1)) &
                (~df['filter3'].str.contains('ReversalLowYear', case=False, regex=True, na=False)) &
                (~df['filter3'].str.contains('BreakLowYear2', case=False, regex=True, na=False)) &
                (df['filter3'].str.contains('BreakLowYear', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakLowYear', column_conf=rb.column_config_result, column_order=rb.column_order_result, height=200, renderml=True, color='LG')
    with col3:
        df = rb.getdfResult('highBuy')
        filtered_df = df
        try:
            filtered_df = df[
                (~df['filter3'].str.contains('ReversalLowYear', case=False, regex=True, na=False)) &
                (~df['filter3'].str.contains('BreakLowYear2', case=False, regex=True, na=False)) &
                (df['filter3'].str.contains('BreakLowYear', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakLowYear', column_conf=rb.column_config_result, column_order=rb.column_order_result, height=200, renderml=True, color='LG')
    
    col0, col1, col2, col3 = st.columns(4)
    with col0:
        df = rb.getdfResult('highBuy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['year5HighChange'] > -20) &
                (df['yearHighChange'] > -20) &
                (df['yearLowChange'] > 15) &
                (df['month3LowChange'] > 15) &
                (df['PCT_day_change'] > 1) &
                (df['PCT_day_change_pre1'] < 1.5) &
                (df['PCT_day_change_pre2'] < 1.5) &
                ((df['PCT_day_change_pre1'] < 1) | (df['PCT_day_change_pre2'] < 1)) &
                (df['filter3'].str.contains('BreakHighMonth6', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakHighMonth6', column_conf=rb.column_config_result, column_order=rb.column_order_result, height=200, renderml=True, color='LG')  
    with col1:
        df = rb.getdfResult('highBuy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['filter3'].str.contains('BreakHighMonth6', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakHighMonth6', column_conf=rb.column_config_result, column_order=rb.column_order_result, height=200, renderml=True, color='LG')  
    with col2:
        df = rb.getdfResult('highBuy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['yearLowChange'] < 20) &
                (df['yearHighChange'] < -15) &
                (df['month3HighChange'] < -15) &
                (df['PCT_day_change'] < -1) &
                (df['PCT_day_change_pre1'] > -1.5) &
                (df['PCT_day_change_pre2'] > -1.5) &
                ((df['PCT_day_change_pre1'] > -1) | (df['PCT_day_change_pre2'] > -1)) &
                (df['filter3'].str.contains('BreakLowMonth6', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakLowMonth6', column_conf=rb.column_config_result, column_order=rb.column_order_result, height=200, renderml=True, color='LG')
    with col3:
        df = rb.getdfResult('highBuy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['filter3'].str.contains('BreakLowMonth6', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakLowMonth6', column_conf=rb.column_config_result, column_order=rb.column_order_result, height=200, renderml=True, color='LG')
    
    col0, col1, col2, col3 = st.columns(4)
    with col0:
        df = rb.getdfResult('highBuy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['filter3'].str.contains('BreakHighMonth3', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakHighMonth3', column_conf=rb.column_config_result, column_order=rb.column_order_result, height=200, renderml=True, color='LG')  
    with col1:
        df = rb.getdfResult('highBuy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['filter3'].str.contains('BreakHighMonth3', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakHighMonth3', column_conf=rb.column_config_result, column_order=rb.column_order_result, height=200, renderml=True, color='LG')  
    with col2:
        df = rb.getdfResult('highBuy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['filter3'].str.contains('BreakLowMonth3', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakLowMonth3', column_conf=rb.column_config_result, column_order=rb.column_order_result, height=200, renderml=True, color='LG')
    with col3:
        df = rb.getdfResult('highBuy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['filter3'].str.contains('BreakLowMonth3', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakLowMonth3', column_conf=rb.column_config_result, column_order=rb.column_order_result, height=200, renderml=True, color='LG')
    

    




if __name__ == '__main__':
    main()