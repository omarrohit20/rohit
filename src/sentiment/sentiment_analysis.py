import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from database import get_mongodb_handler
from datetime import datetime, timedelta

MONGODB_DATABASE = "chartlink"
MONGODB_COLLECTION = "sentiment_analysis"

# Page configuration
st.set_page_config(
    page_title="NSE Stock Sentiment Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 20px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .positive { color: #10b981; }
    .negative { color: #ef4444; }
    .neutral { color: #6b7280; }
    </style>
""", unsafe_allow_html=True)

# Initialize MongoDB connection
@st.cache_resource
def get_db_handler():
    try:
        # Use rbase MongoDB handler utility
        return get_mongodb_handler(db_name=MONGODB_DATABASE, collection_name=MONGODB_COLLECTION)
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {e}")
        st.error("Make sure MongoDB is running on localhost:27017")
        st.info("Start MongoDB service: net start MongoDB")
        return None

db_handler = get_db_handler()

def load_sentiment_data():
    """Load all sentiment data from MongoDB"""
    if not db_handler:
        return []
    
    try:
        stocks = db_handler.get_all_sentiments()
        return stocks
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return []

def convert_stocks_to_dataframe(stocks):
    """Convert stocks data to DataFrame for easier manipulation"""
    data = []
    
    for stock in stocks:
        scrip = stock.get('scrip', '')
        company = stock.get('company', '')
        sentiment = stock.get('news_analysis', {}).get('overall_sentiment', 'Neutral')
        news_count = len(stock.get('news_analysis', {}).get('news', []))
        last_updated = stock.get('last_updated', '')        
        data.append({
            'Scrip': scrip,
            'Company': company,
            'Sentiment': sentiment,
            'News Count': news_count,
            'Last Updated': last_updated,
            'News': stock.get('news_analysis', {}).get('news', [])
        })
    
    return pd.DataFrame(data)

# Header
st.title("📊 NSE Stock Sentiment Analysis Dashboard")
st.markdown("Real-time sentiment analysis of NSE 500 stocks based on news articles from multiple sources")

# Sidebar filters
st.sidebar.header("🔧 Filters & Controls")
sentiment_filter = st.sidebar.multiselect(
    "Select Sentiment Type:",
    options=['Positive', 'Negative', 'Neutral'],
    default=['Positive', 'Negative', 'Neutral'],
    key='sentiment_filter'
)

search_term = st.sidebar.text_input(
    "🔍 Search by Scrip or Company:",
    placeholder="Enter scrip code or company name",
    key='search_term'
)

refresh_btn = st.sidebar.button("🔄 Refresh Data", use_container_width=True)

if refresh_btn:
    st.cache_resource.clear()
    st.rerun()

# Load data
stocks_data = load_sentiment_data()
df = convert_stocks_to_dataframe(stocks_data)

if df.empty:
    st.warning("⚠️ No data available. Please run the sentiment analysis first.")
    st.stop()

# Filter data
filtered_df = df.copy()

# Apply sentiment filter
if sentiment_filter:
    filtered_df = filtered_df[filtered_df['Sentiment'].isin(sentiment_filter)]

# Apply search filter
if search_term:
    search_term_lower = search_term.lower()
    filtered_df = filtered_df[(filtered_df['Scrip'].str.lower().str.contains(search_term_lower)) | (filtered_df['Company'].str.lower().str.contains(search_term_lower))]

# Summary Metrics
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    positive_count = len(df[df['Sentiment'] == 'Positive'])
    st.metric(
        label="📈 Positive",
        value=positive_count,
        delta=f"{(positive_count/len(df)*100):.1f}%" if len(df) > 0 else "0%"
    )

with col2:
    negative_count = len(df[df['Sentiment'] == 'Negative'])
    st.metric(
        label="📉 Negative",
        value=negative_count,
        delta=f"{(negative_count/len(df)*100):.1f}%" if len(df) > 0 else "0%"
    )

with col3:
    neutral_count = len(df[df['Sentiment'] == 'Neutral'])
    st.metric(
        label="➖ Neutral",
        value=neutral_count,
        delta=f"{(neutral_count/len(df)*100):.1f}%" if len(df) > 0 else "0%"
    )

with col4:
    total_count = len(df)
    st.metric(
        label="📋 Total Stocks",
        value=total_count
    )

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

# Sentiment Distribution Pie Chart
with col1:
    sentiment_counts = df['Sentiment'].value_counts()
    fig_pie = px.pie(
        values=sentiment_counts.values,
        names=sentiment_counts.index,
        title="Sentiment Distribution",
        color_discrete_map={
            'Positive': '#10b981',
            'Negative': '#ef4444',
            'Neutral': '#6b7280'
        }
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# News Count Distribution
with col2:
    top_news = df.nlargest(10, 'News Count')
    fig_bar = px.bar(
        top_news,
        x='Scrip',
        y='News Count',
        color='Sentiment',
        title="Top 10 Stocks by News Count",
        color_discrete_map={
            'Positive': '#10b981',
            'Negative': '#ef4444',
            'Neutral': '#6b7280'
        }
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# Stock Details with Expandable News
st.subheader("📰 Stock Details & News")

if filtered_df.empty:
    st.warning("No stocks match your filters.")
else:
    st.write(f"Showing {len(filtered_df)} stock(s)")
    
    for idx, row in filtered_df.iterrows():
        # Determine sentiment color
        sentiment_color = {
            'Positive': '#10b981',
            'Negative': '#ef4444',
            'Neutral': '#6b7280'
        }.get(row['Sentiment'], '#6b7280')
        
        # Stock header
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            st.markdown(f"### {row['Scrip']}")
            st.markdown(f"**Company:** {row['Company']}")
        
        with col2:
            st.markdown(f"**Sentiment:** <span style='color: {sentiment_color}; font-weight: bold;'>{row['Sentiment']}</span>", unsafe_allow_html=True)
            st.markdown(f"**News Articles:** {row['News Count']}")
        
        with col3:
            if isinstance(row['Last Updated'], datetime):
                st.markdown(f"**Updated:** {row['Last Updated'].strftime('%Y-%m-%d %H:%M')}")
            else:
                st.markdown(f"**Updated:** {row['Last Updated']}")
        
        # Expandable news section
        with st.expander(f"📋 View {row['News Count']} News Articles", expanded=False):
            if row['News Count'] > 0:
                # Display each news item
                news_items = row['News']
                
                for i, news in enumerate(news_items, 1):
                    st.markdown(f"**{i}. {news.get('headline', 'No Headline')}**")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.caption(f"📅 {news.get('Date', 'N/A')} {news.get('Time', '')}")
                    
                    with col2:
                        impact = news.get('impact', 'Neutral')
                        impact_color = {
                            'Positive': '🟢',
                            'Negative': '🔴',
                            'Neutral': '⚪'
                        }.get(impact, '⚪')
                        st.caption(f"Impact: {impact_color} {impact}")
                    
                    with col3:
                        severity = news.get('severity', 'Unknown')
                        st.caption(f"Severity: {severity}")
                    
                    # News link
                    link = news.get('link', '#')
                    st.markdown(f"[🔗 Read Full Article]({link})")
                    
                    # Divider between news items
                    if i < len(news_items):
                        st.divider()
            else:
                st.info("No news articles available for this stock.")
        
        st.divider()

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Generate Report", use_container_width=True):
        st.info("Report generation feature coming soon!")

with col2:
    if st.button("💾 Export Data", use_container_width=True):
        # Remove News column before exporting
        export_df = filtered_df.drop('News', axis=1)
        csv = export_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"sentiment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

with col3:
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
