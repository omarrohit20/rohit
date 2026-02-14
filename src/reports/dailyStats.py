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
                           page_title="DailyStatsDashboard",
                           initial_sidebar_state="expanded",)
    except Exception:
        pass

    # main title
    st.title('DailyStatsDashboard')


    # Industry Analysis Chart with Dropdown
    st.divider()
    st.subheader('Industry Analysis - Regression High')
    
    try:
        # Get regressionhigh data
        df_industry = rb.getintersectdf_ml('regressionhigh', 'regressionlow')
        
        if not df_industry.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Count of stocks per industry
                industry_count = df_industry['industry'].value_counts().reset_index()
                industry_count.columns = ['Industry', 'Count']
                industry_count = industry_count.sort_values('Count', ascending=False).head(15)
                
                st.write("**Stock Count by Industry**")
                st.bar_chart(industry_count.set_index('Industry')['Count'])
            
            with col2:
                # Average PCT_day_change per industry
                industry_avg = df_industry.groupby('industry')['PCT_day_change'].mean().reset_index()
                industry_avg.columns = ['Industry', 'Avg_Daily_Change']
                industry_avg = industry_avg.sort_values('Avg_Daily_Change', ascending=False).head(15)
                
                st.write("**Average Daily % Change by Industry**")
                st.bar_chart(industry_avg.set_index('Industry')['Avg_Daily_Change'])
            
            # Detailed industry table
            st.write("**Industry Stats Summary**")
            industry_stats = df_industry.groupby('industry').agg({
                'scrip': 'count',
                'PCT_day_change': ['mean', 'min', 'max', 'std']
            }).round(2)
            industry_stats.columns = ['Count', 'Avg_Change', 'Min_Change', 'Max_Change', 'Std_Dev']
            industry_stats = industry_stats.sort_values('Count', ascending=False)
            
            st.dataframe(industry_stats, use_container_width=True)
            
            # Industry Dropdown Selection
            st.divider()
            st.subheader('Industry Stocks Detail')
            
            # Search by stock name
            col1, col2 = st.columns([2, 1])
            with col1:
                stock_search = st.text_input("**Search by Stock Name**", placeholder="Enter stock name (e.g., SBIN, TCS, INFY)")
            
            # Determine selected industry based on search or dropdown
            industries = sorted(df_industry['industry'].dropna().unique())
            
            if stock_search:
                # Search for the stock and get its industry
                matching_stocks = df_industry[df_industry['scrip'].str.contains(stock_search, case=False, na=False)]
                if not matching_stocks.empty:
                    selected_industry = matching_stocks.iloc[0]['industry']
                    st.info(f"Found stock in industry: **{selected_industry}**")
                else:
                    st.warning(f"Stock '{stock_search}' not found in data")
                    selected_industry = industries[0]
            else:
                with col2:
                    selected_industry = st.selectbox(
                        "**Or Select Industry**",
                        options=industries,
                        index=0
                    )
            
            # Filter data for selected industry
            industry_filtered = df_industry[df_industry['industry'] == selected_industry].copy()
            industry_filtered = industry_filtered.sort_values('PCT_day_change', ascending=False)
            
            if not industry_filtered.empty:
                st.write(f"**{selected_industry}** - Total Stocks: {len(industry_filtered)}")
                
                # Summary stats for selected industry
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("Total Stocks", len(industry_filtered))
                with col2:
                    avg_change = industry_filtered['PCT_day_change'].mean()
                    st.metric("Avg Daily Change %", f"{avg_change:.2f}%")
                with col3:
                    max_change = industry_filtered['PCT_day_change'].max()
                    st.metric("Max Daily Change %", f"{max_change:.2f}%")
                with col4:
                    min_change = industry_filtered['PCT_day_change'].min()
                    st.metric("Min Daily Change %", f"{min_change:.2f}%")
                with col5:
                    std_change = industry_filtered['PCT_day_change'].std()
                    st.metric("Std Dev", f"{std_change:.2f}")
                
                # Display all stocks from selected industry
                st.write("**All Stocks in Selected Industry**")
                
                # Select columns to display
                display_columns = ['scrip', 'PCT_day_change', 'PCT_change', 
                                 'highTail', 'lowTail', 'kNeighboursValue_reg', 
                                 'mlpValue_reg', 'systemtime']
                
                # Filter to only columns that exist
                existing_cols = [col for col in display_columns if col in industry_filtered.columns]
                display_df = industry_filtered[existing_cols].reset_index(drop=True)
                
                rb.render(st, industry_filtered, f'{selected_industry} - All Stocks', 
                         column_conf=rb.column_config_ml, column_order=rb.column_order_ml,
                         renderml=True, color='G', height=400)
            else:
                st.write(f"No data available for {selected_industry}")
        else:
            st.write("No data available for industry analysis")
    except Exception as e:
        st.write(f"Error generating industry chart: {e}")

    


    
if __name__ == '__main__':
    main()