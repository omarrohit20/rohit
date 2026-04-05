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

# Display Positive and Negative Sentiment Stocks at the start
st.markdown("## 📈 Positive & Negative Sentiment Stocks")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🟢 Positive Sentiment")
    positive_df = df[df['Sentiment'] == 'Positive'].sort_values('News Count', ascending=False)
    if not positive_df.empty:
        st.dataframe(positive_df[['Scrip', 'Company', 'News Count']].head(10), use_container_width=True)
    else:
        st.info("No positive sentiment stocks found.")

with col2:
    st.subheader("🔴 Negative Sentiment")
    negative_df = df[df['Sentiment'] == 'Negative'].sort_values('News Count', ascending=False)
    if not negative_df.empty:
        st.dataframe(negative_df[['Scrip', 'Company', 'News Count']].head(10), use_container_width=True)
    else:
        st.info("No negative sentiment stocks found.")

st.markdown("---")

# Comprehensive News Table
st.markdown("---")
st.subheader("📰 All News Articles - Comprehensive View")

# Flatten all news data into a table
all_news_data = []
for idx, row in df.iterrows():
    news_items = row['News']
    for news in news_items:
        all_news_data.append({
            'Scrip': row['Scrip'],
            'Company': row['Company'],
            'Overall Sentiment': row['Sentiment'],
            'Headline': news.get('headline', 'No Headline'),
            'Date': news.get('Date', 'N/A'),
            'Time': news.get('Time', ''),
            'Impact': news.get('impact', 'Neutral'),
            'Severity': news.get('severity', 'Unknown'),
            'Link': news.get('link', '#')
        })

if all_news_data:
    news_df = pd.DataFrame(all_news_data)
    
    # Sort by Impact for High and Medium severity: High Positive first, High Negative second, Medium Positive third, Medium Negative fourth, then everything else
    def get_sort_order(row):
        severity = row['Severity']
        impact = row['Impact']
        
        if severity == 'High':
            if impact == 'Positive':
                return 0
            elif impact == 'Negative':
                return 1
            else:
                return 2
        elif severity == 'Medium':
            if impact == 'Positive':
                return 3
            elif impact == 'Negative':
                return 4
            else:
                return 5
        else:
            return 6  # All Low/Unknown severity items at the end
    
    news_df['sort_order'] = news_df.apply(get_sort_order, axis=1)
    news_df = news_df.sort_values('sort_order').drop('sort_order', axis=1)
    
    # Function to apply row styling for High and Medium severity
    def style_news_table(row):
        severity = row['Severity']
        impact = row['Impact']
        
        if severity in ['High', 'Medium']:
            if impact == 'Positive':
                return ['background-color: #d4edda'] * len(row)  # Light green
            elif impact == 'Negative':
                return ['background-color: #f8d7da'] * len(row)  # Light red
        
        return [''] * len(row)  # No special color for Low/Unknown severity or neutral impact
    
    # Apply styling
    styled_df = news_df.style.apply(style_news_table, axis=1)
    
    # Add filters for the comprehensive table
    col1, col2, col3 = st.columns(3)
    
    with col1:
        impact_filter = st.multiselect(
            "Filter by Impact:",
            options=['Positive', 'Negative', 'Neutral'],
            default=['Positive', 'Negative', 'Neutral'],
            key='impact_filter'
        )
    
    with col2:
        severity_filter = st.multiselect(
            "Filter by Severity:",
            options=['High', 'Medium', 'Low', 'Unknown'],
            default=['High', 'Medium', 'Low', 'Unknown'],
            key='severity_filter'
        )
    
    with col3:
        sentiment_filter_table = st.multiselect(
            "Filter by Overall Sentiment:",
            options=['Positive', 'Negative', 'Neutral'],
            default=['Positive', 'Negative', 'Neutral'],
            key='sentiment_filter_table'
        )
    
    # Apply filters
    filtered_news_df = news_df.copy()
    if impact_filter:
        filtered_news_df = filtered_news_df[filtered_news_df['Impact'].isin(impact_filter)]
    if severity_filter:
        filtered_news_df = filtered_news_df[filtered_news_df['Severity'].isin(severity_filter)]
    if sentiment_filter_table:
        filtered_news_df = filtered_news_df[filtered_news_df['Overall Sentiment'].isin(sentiment_filter_table)]
    
    # Apply styling to filtered df
    filtered_styled_df = filtered_news_df.style.apply(style_news_table, axis=1)
    
    st.write(f"Showing {len(filtered_news_df)} news articles")
    
    # Display the styled table
    st.dataframe(
        filtered_styled_df,
        column_config={
            'Link': st.column_config.LinkColumn('Link', display_text='🔗 Read Article'),
            'Overall Sentiment': st.column_config.TextColumn('Overall Sentiment', width='medium'),
            'Headline': st.column_config.TextColumn('Headline', width='large'),
            'Scrip': st.column_config.TextColumn('Scrip', width='small'),
            'Company': st.column_config.TextColumn('Company', width='medium'),
            'Date': st.column_config.TextColumn('Date', width='small'),
            'Time': st.column_config.TextColumn('Time', width='small'),
            'Impact': st.column_config.TextColumn('Impact', width='small'),
            'Severity': st.column_config.TextColumn('Severity', width='small')
        },
        use_container_width=True,
        hide_index=True
    )
    
    # Export option for the comprehensive table
    if st.button("💾 Export All News to CSV", use_container_width=True):
        csv = filtered_news_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"all_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
else:
    st.info("No news articles available.")

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
