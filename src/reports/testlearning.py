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
        df = rb.getdf('buy-morning-volume-breakout(Check-News)')
        filtered_df = df
        try:
            filtered_df = df[
                (df['weekHighChange'] > -4) &
                ((df['week2LowChange'] > 0) | (df['weekLowChange'] > 0)) &
                (df['monthLowChange'] > 0) &
                (df['month3LowChange'] > 0)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'buy-morning-volume-breakout(Check-News)', column_conf=rb.column_config_default, column_order=rb.column_order_default, renderml=True, color='LG')
    with col2:
        df = rb.getdf('buy-morning-volume-breakout(Check-News)')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['weekLowChange'] > 3)) &
                ((df['week2LowChange'] > 1) & (df['weekLowChange'] > 1))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'buy-morning-volume-breakout(Check-News)', column_conf=rb.column_config_default, column_order=rb.column_order_default, renderml=True, color='LG')
    with col3:
        df = rb.getdf('buy-morning-volume-breakout(Check-News)')
        filtered_df = df
        rb.render(st, filtered_df, 'buy-morning-volume-breakout(Check-News)', column_conf=rb.column_config_default, column_order=rb.column_order_default, renderml=True, color='LG')
    with col4:
        df = rb.getdf('sell-morning-volume-breakout(Check-News)')
        filtered_df = df
        try:
            filtered_df = df[
                (df['weekLowChange'] < 4) &
                ((df['week2HighChange'] < 0) | (df['weekHighChange'] < 0)) &
                (df['monthHighChange'] < 0) &
                (df['month3HighChange'] < 0)
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'sell-morning-volume-breakout(Check-News)', column_conf=rb.column_config_default, column_order=rb.column_order_default, renderml=True, color='LG')
    with col5:
        df = rb.getdf('sell-morning-volume-breakout(Check-News)')
        filtered_df = df
        try:
            filtered_df = df[
                ((df['weekHighChange'] < -3)) &
                ((df['week2HighChange'] < -1) & (df['weekHighChange'] < -1))
            ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'sell-morning-volume-breakout(Check-News)', column_conf=rb.column_config_default, column_order=rb.column_order_default, renderml=True, color='LG')
    with col6:
        df = rb.getdf('sell-morning-volume-breakout(Check-News)')
        filtered_df = df
        rb.render(st, filtered_df, 'sell-morning-volume-breakout(Check-News)', column_conf=rb.column_config_default, column_order=rb.column_order_default, renderml=True, color='LG')


# Sentiment Analysis Tables
    st.divider()
    st.subheader('News Sentiment Analysis')
    
    col1, col2 = st.columns(2)
    
    # Load sentiment data once
    try:
        from pymongo import MongoClient
        connection = MongoClient('localhost', 27017)
        dbcl = connection.chartlink
        sentiment_collection = dbcl['sentiment']
        sentiment_data = list(sentiment_collection.find())
        connection.close()
    except Exception as e:
        sentiment_data = []
        st.write(f"Error loading sentiment data: {e}")
    
    with col1:
        # Positive Sentiment Table
        try:
            if sentiment_data:
                # Filter for positive sentiment
                positive_data = []
                for item in sentiment_data:
                    if item.get('news_analysis', {}).get('overall_sentiment') == 'Positive':
                        # Flatten the structure for display
                        news_items = item.get('news_analysis', {}).get('news', [])
                        for news in news_items:
                            positive_data.append({
                                'scrip': item.get('scrip', ''),
                                'company': item.get('company', ''),
                                'headline': news.get('headline', ''),
                                'impact': news.get('impact', ''),
                                'severity': news.get('severity', '')
                            })
                
                if positive_data:
                    df_positive = pd.DataFrame(positive_data)
                    rb.render_rawdata(st, df_positive, 'Positive Sentiment News', color='G', height=300)
                else:
                    st.write("No positive sentiment news found")
            else:
                st.write("No sentiment data available")
        except Exception as e:
            st.write(f"Error processing positive sentiment: {e}")
    
    with col2:
        # Negative Sentiment Table
        try:
            if sentiment_data:
                # Filter for negative sentiment
                negative_data = []
                for item in sentiment_data:
                    if item.get('news_analysis', {}).get('overall_sentiment') == 'Negative':
                        # Flatten the structure for display
                        news_items = item.get('news_analysis', {}).get('news', [])
                        for news in news_items:
                            negative_data.append({
                                'scrip': item.get('scrip', ''),
                                'company': item.get('company', ''),
                                'headline': news.get('headline', ''),
                                'impact': news.get('impact', ''),
                                'severity': news.get('severity', '')
                            })
                
                if negative_data:
                    df_negative = pd.DataFrame(negative_data)
                    rb.render_rawdata(st, df_negative, 'Negative Sentiment News', color='R', height=300)
                else:
                    st.write("No negative sentiment news found")
            else:
                st.write("No sentiment data available")
        except Exception as e:
            st.write(f"Error processing negative sentiment: {e}")
    st.divider()

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

    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        df = rb.getintersectdf_ml('regressionhigh', 'regressionlow')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] < 4.5) &
                (df['PCT_day_change'] < 4) &
                (df['PCT_day_change'] > 2) &
                ((df['PCT_day_change'] < 1) | (df['PCT_day_change_pre1'] < 1) | (df['PCT_day_change_pre2'] < -0.5)) &
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
                (df['PCT_change'] > -1) &
                (df['PCT_day_change'] > -1.5) &
                ((df['PCT_day_change_pre1'] > 0.3) | (df['PCT_day_change_pre2'] > 0.3)) &
                (((df['forecast_day_PCT10_change'] > 5) & (df['forecast_day_PCT7_change'] > 3) & (df['forecast_day_PCT5_change'] > 3))
                | ((df['forecast_day_PCT10_change'] < -3) & (df['forecast_day_PCT7_change'] < 0) & (df['forecast_day_PCT5_change'] < 0))
                ) &
                (df['highTail'] > 2.5) &
                (df['lowTail'] < 1.3)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayDown:Buy-HighTail', column_conf=rb.column_config_ml, column_order=rb.column_order_ml,
                  renderml=True, color='LG')    
    with col3:
        df = rb.getintersectdf_ml('regressionlow', 'regressionhigh')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] > -4.5) &
                (df['PCT_day_change'] > -4) &
                (df['PCT_day_change'] < -2) &
                ((df['PCT_day_change'] > -1) | (df['PCT_day_change_pre1'] > -1) | (df['PCT_day_change_pre2'] > 0.5)) &
                ((df['kNeighboursValue_reg'] < -2) | (df['mlpValue_reg'] < -2)) &
                ((df['PCT_day_change_pre1'] < 0 ) | (df['PCT_day_change_pre2'] < 0)) &
                (df['forecast_day_PCT10_change'] < -2)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'MLSELL', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='LG')
    with col4:
        df = rb.getintersectdf_ml('regressionhigh', 'regressionlow')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] > -1.5) &
                (df['PCT_day_change'] > -1.5) &
                (df['PCT_change'] < 1) &
                (df['PCT_day_change'] < 1.5) &
                (((df['forecast_day_PCT10_change'] < -5) & (df['forecast_day_PCT7_change'] < -3) & (df['forecast_day_PCT5_change'] < -3))
                | ((df['forecast_day_PCT10_change'] > 3) & (df['forecast_day_PCT7_change'] > 0) & (df['forecast_day_PCT5_change'] > 0))
                ) &
                (df['forecast_day_PCT10_change'] < -3) &
                (df['lowTail'] > 2.5) &
                (df['highTail'] < 1.3)
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'LastDayUp:Sell-LowTail', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='LG')
    

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        df = rb.getintersectdf_ml('regressionlow', 'regressionhigh')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] > -4.5) &
                (df['PCT_day_change'] > -4) &
                (df['PCT_day_change'] < -2) &
                ((df['PCT_day_change_pre1'] > -2 ) | (df['monthHighChange'] < 0)) &
                (df['forecast_day_PCT10_change'] > 5) &
                ((df['kNeighboursValue_reg'] != 0) | (df['mlpValue_reg'] != 0))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'UpTrendMayBuy', column_conf=rb.column_config_ml, column_order=rb.column_order_ml, renderml=True, color='LG')
    with col2:
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
    with col3:
        df = rb.getintersectdf_ml('regressionhigh', 'regressionlow')
        filtered_df = df
        try:
            filtered_df = df[
                (df['PCT_change'] < 4.5) &
                (df['PCT_day_change'] < 4) &
                (df['PCT_day_change'] > 2) &
                ((df['PCT_day_change_pre1'] < 2 ) | (df['monthLowChange'] > 0)) &
                (df['forecast_day_PCT10_change'] < -5) &
                ((df['kNeighboursValue_reg'] != 0) | (df['mlpValue_reg'] != 0))
                ]
        except KeyError as e:
            print("")
        rb.render(st, filtered_df, 'DownTrendMaySell', column_conf=rb.column_config_ml, column_order=rb.column_order_ml,
                  renderml=True, color='LG')
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