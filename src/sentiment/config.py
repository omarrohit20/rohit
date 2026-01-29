import os

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# Updated to use currently supported model
GROQ_MODEL = "llama-3.3-70b-versatile"  # Alternative: "mixtral-8x7b-32768" or "gemma2-9b-it"

# News Sources
NEWS_SOURCES = [
    "https://pulse.zerodha.com/",
    "https://www.moneycontrol.com/news/business/markets/",
    "https://www.ndtvprofit.com/business",
    "https://economictimes.indiatimes.com/markets/stocks/news"
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
    "volume buzzers",
    "sensex sinks",
    "sensex sink",
    "sensex tumbles",
    "sensex tumble",
    "sensex falls",
    "sensex fall",
    "sensex drops",
    "sensex drop",
    "sensex plunges",
    "sensex plunge",
    "sensex slides",
    "sensex slide",
    "sensex declines",
    "sensex decline",
    "nifty sinks",
    "nifty sink",
    "nifty tumbles",
    "nifty tumble",
    "nifty falls",
    "nifty fall",
    "nifty drops",
    "nifty drop",
    "nifty plunges",
    "nifty plunge",
    "nifty slides",
    "nifty slide",
    "nifty declines",
    "nifty decline",
    "biggest weekly drop",
    "biggest weekly decline",
    "biggest weekly fall",
    "largest weekly drop",
    "largest weekly decline",
    "biggest daily drop",
    "biggest daily decline",
    "bears regain",
    "bears regain control",
    "bears take control",
    "bear market",
    "bull market",
    "market selloff",
    "market correction",
    "broader indices",
    "broader market",
    "indices log",
    "indices slide",
    "indices fall",
    "indices drop",
    "indices decline",
    "market volatility",
    "volatile week",
    "volatile session",
    "closing bell",
    "market closing",
    "market opening",
    "opening bell",
    "market snapshot",
    "market wrap",
    "weekly decline",
    "weekly drop",
    "weekly fall",
    "weekly loss",
    "volume surge",
    "Nifty rises",
    "Sensex rises",
    "Nifty gains",
    "Sensex gains",
    "Nifty climbs",
    "Sensex climbs",
    "Nifty soars",
    "Sensex soars",
    "Nifty rallies",
    "Sensex rallies",
    "Nifty jumps",
    "Sensex jumps",
    "Nifty tanks",
    "Sensex tanks",
    "Nifty slips",
    "Sensex slips",
    "Nifty plunges",
    "Sensex plunges",
    "Nifty hits",
    "Sensex hits",
    "Gainers & Losers",
    "Market Wrap",
    "ITI"
]

# MongoDB Configuration
MONGODB_HOST = "localhost"
MONGODB_PORT = 27017
MONGODB_DATABASE = "chartlink"
MONGODB_COLLECTION = "sentiment_analysis"
