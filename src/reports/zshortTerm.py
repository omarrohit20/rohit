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

    rb.shortTerm = True

    col0, col1 = st.columns(2)
    with col0:
        df = rb.getdf_sandlterm('breakoutYH')
        rb.render_sandlterm_data(st, df,'breakoutYH', color='G')
    with col1:
        df = rb.getdf_sandlterm('breakoutY2H')
        rb.render_sandlterm_data(st, df,'breakoutY2H', color='G')


    col0, col1, col2 = st.columns(3)
    with col0:
        df = rb.getdf_sandlterm('breakoutW2HR')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['monthHighChange'] < -3) | (df['month3HighChange'] < -15)) &
                ((df['monthHighChange'] > -5.5) | (df['month3HighChange'] < -20)) &
                (df['monthHighChange'] < 5) &
                (df['week2LowChange'] < 5.5) &
                (df['week2LowChange'] != df['weekLowChange']) &
                ((df['yearLowChange'] > 0) | (df['month2HighChange'] > -10))
                ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df,'breakoutW2HR', color='G')
    with col1:
        df = rb.getdf_sandlterm('breakoutW2HR')
        filtered_df = df
        try:
            filtered_df = df[
                (df['monthHighChange'] < 5) &
                (df['monthHighChange'] > -3.5) &
                ((df['monthHighChange'] < -3) | (df['month3HighChange'] < -15))
                ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df,'breakoutW2HR', color='G')
    with col2:
        df = rb.getdf_sandlterm('breakoutW2HR')
        rb.render_sandlterm_data(st, df,'breakoutW2HR', color='LG')


    col0, col1, col2 = st.columns(3)
    with col0:
        df = rb.getdf_sandlterm('breakoutMHR')
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
        rb.render_sandlterm_data(st, filtered_df,'breakoutMHR', color='LG')
    with col1:
        df = rb.getdf_sandlterm('breakoutMHR')
        filtered_df = df
        try:
            filtered_df = df[
                (df['year5HighChange'] < -30) &
                (df['year2HighChange'] < -10) &
                (df['month3HighChange'] < -5)
                ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df,'breakoutMHR', color='LG')
    with col2:
        df = rb.getdf_sandlterm('breakoutMHR')
        rb.render_sandlterm_data(st, df,'breakoutMHR', color='LG')

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
                (df['month3HighChange'] > -3.5) &
                ((df['month3HighChange'] < -3) | (df['month6HighChange'] < -15))
                ]
        except KeyError as e:
            print("")
        rb.render_sandlterm_data(st, filtered_df, 'breakoutM2HR', color='LG')
    with col2:
        df = rb.getdf_sandlterm('breakoutM2HR')
        rb.render_sandlterm_data(st, df, 'breakoutM2HR', color='LG')
    
    
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
                (df['filter3'].str.contains('BreakHighYear2', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakHighYear2', column_conf=rb.column_config_result, column_order=rb.column_order_result, renderml=True, color='LG')
    with col1:
        df = rb.getdfResult('highBuy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['filter3'].str.contains('BreakHighYear2', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakHighYear2', column_conf=rb.column_config_result, column_order=rb.column_order_result, renderml=True, color='LG')
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
                (df['filter3'].str.contains('BreakLowYear2', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakLowYear2', column_conf=rb.column_config_result, column_order=rb.column_order_result, renderml=True, color='LG')
    with col3:
        df = rb.getdfResult('highBuy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['filter3'].str.contains('BreakLowYear2', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakLowYear2', column_conf=rb.column_config_result, column_order=rb.column_order_result, renderml=True, color='LG')
    
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
                (df['filter3'].str.contains('BreakHighYear', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakHighYear', column_conf=rb.column_config_result, column_order=rb.column_order_result, renderml=True, color='LG')
    with col1:
        df = rb.getdfResult('highBuy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['filter3'].str.contains('BreakHighYear', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakHighYear', column_conf=rb.column_config_result, column_order=rb.column_order_result, renderml=True, color='LG')
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
                (df['filter3'].str.contains('BreakLowYear', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakLowYear', column_conf=rb.column_config_result, column_order=rb.column_order_result, renderml=True, color='LG')
    with col3:
        df = rb.getdfResult('highBuy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['filter3'].str.contains('BreakLowYear', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakLowYear', column_conf=rb.column_config_result, column_order=rb.column_order_result, renderml=True, color='LG')
    
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
        rb.render(st, filtered_df, 'BreakHighMonth6', column_conf=rb.column_config_result, column_order=rb.column_order_result, renderml=True, color='LG')  
    with col1:
        df = rb.getdfResult('highBuy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['filter3'].str.contains('BreakHighMonth6', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakHighMonth6', column_conf=rb.column_config_result, column_order=rb.column_order_result, renderml=True, color='LG')  
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
        rb.render(st, filtered_df, 'BreakLowMonth6', column_conf=rb.column_config_result, column_order=rb.column_order_result, renderml=True, color='LG')
    with col3:
        df = rb.getdfResult('highBuy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['filter3'].str.contains('BreakLowMonth6', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakLowMonth6', column_conf=rb.column_config_result, column_order=rb.column_order_result, renderml=True, color='LG')
    
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
        rb.render(st, filtered_df, 'BreakHighMonth3', column_conf=rb.column_config_result, column_order=rb.column_order_result, renderml=True, color='LG')  
    with col1:
        df = rb.getdfResult('highBuy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['filter3'].str.contains('BreakHighMonth3', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakHighMonth3', column_conf=rb.column_config_result, column_order=rb.column_order_result, renderml=True, color='LG')  
    with col2:
        df = rb.getdfResult('highBuy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['filter3'].str.contains('BreakLowMonth3', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakLowMonth3', column_conf=rb.column_config_result, column_order=rb.column_order_result, renderml=True, color='LG')
    with col3:
        df = rb.getdfResult('highBuy')
        filtered_df = df
        try:
            filtered_df = df[
                (df['filter3'].str.contains('BreakLowMonth3', case=False, regex=True, na=False))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'BreakLowMonth3', column_conf=rb.column_config_result, column_order=rb.column_order_result, renderml=True, color='LG')
    
    

if __name__ == '__main__':
    main()