# Create a streamlit app that shows the mongodb data
from streamlit_autorefresh import st_autorefresh
import streamlit as st
import rbase as rb
import pandas as pd


def _futures_df(df):
    """Keep F&O rows only: Nsedata.scrip futures=Yes, or index tagged futures."""
    if df is None or getattr(df, 'empty', True):
        return df
    mask = None
    try:
        scrips = rb.get_futures_scrip_set()
        if 'scrip' in df.columns and scrips:
            mask = df['scrip'].isin(scrips)
    except Exception:
        pass
    try:
        if 'index' in df.columns:
            tagged = df['index'].astype(str).str.contains('futures', case=False, na=False)
            mask = tagged if mask is None else (mask | tagged)
    except Exception:
        pass
    return df if mask is None else df[mask]


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


    
    
    col0, col1, col2, col3 = st.columns(4)
    with col0:
        df = _futures_df(rb.getdfResult('highBuy'))
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
        df = _futures_df(rb.getdfResult('highBuy'))
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
        df = _futures_df(rb.getdfResult('lowSell'))
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
        df = _futures_df(rb.getdfResult('lowSell'))
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
        df = _futures_df(rb.getdfResult('highBuy'))
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
        df = _futures_df(rb.getdfResult('highBuy'))
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
        df = _futures_df(rb.getdfResult('lowSell'))
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
        df = _futures_df(rb.getdfResult('lowSell'))
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
        df = _futures_df(rb.getdfResult('highBuy'))
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
        df = _futures_df(rb.getdfResult('highBuy'))
        filtered_df = df
        try:
            filtered_df = df[
                (df['filter3'].str.contains('BreakHighMonth6', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakHighMonth6', column_conf=rb.column_config_result, column_order=rb.column_order_result, height=200, renderml=True, color='LG')  
    with col2:
        df = _futures_df(rb.getdfResult('lowSell'))
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
        df = _futures_df(rb.getdfResult('lowSell'))
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
        df = _futures_df(rb.getdfResult('highBuy'))
        filtered_df = df
        try:
            filtered_df = df[
                (df['filter3'].str.contains('BreakHighMonth3', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakHighMonth3', column_conf=rb.column_config_result, column_order=rb.column_order_result, height=200, renderml=True, color='LG')  
    with col1:
        df = _futures_df(rb.getdfResult('highBuy'))
        filtered_df = df
        try:
            filtered_df = df[
                (df['filter3'].str.contains('BreakHighMonth3', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakHighMonth3', column_conf=rb.column_config_result, column_order=rb.column_order_result, height=200, renderml=True, color='LG')  
    with col2:
        df = _futures_df(rb.getdfResult('lowSell'))
        filtered_df = df
        try:
            filtered_df = df[
                (df['filter3'].str.contains('BreakLowMonth3', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakLowMonth3', column_conf=rb.column_config_result, column_order=rb.column_order_result, height=200, renderml=True, color='LG')
    with col3:
        df = _futures_df(rb.getdfResult('lowSell'))
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