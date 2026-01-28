import os

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
# Updated to use currently supported model
GROQ_MODEL = "llama-3.3-70b-versatile"  # Alternative: "mixtral-8x7b-32768" or "gemma2-9b-it"

# News Sources
NEWS_SOURCES = [
    "https://pulse.zerodha.com/",
    "https://www.moneycontrol.com/news/business/stocks/",
    "https://www.moneycontrol.com/news/business/markets/stock-market-live-updates-gift-nifty-indicates-a-firm-start-us-asian-markets-mixed-2-liveblog-13793449.html"

]

# NSE 500 stocks data URL (sample - replace with actual source)
NSE_500_CSV_URL = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"

# Output Configuration
OUTPUT_FILE = "sentiment_analysis_output.json"

# Exclusion Keywords
EXCLUDE_KEYWORDS = [
    "top gainers",
    "top losers",
    "most active",
    "volume buzzers"
]
