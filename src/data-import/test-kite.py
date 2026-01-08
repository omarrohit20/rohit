import pandas as pd
from kiteconnect import KiteConnect
from datetime import datetime, timedelta
import sys

# -----------------------------
# CONFIGURATION
# -----------------------------
#kite connect
API_KEY = ""
API_SECRET = ""  # Keep this secret; do not commit the real value
#https://kite.zerodha.com/connect/login?v=3&api_key=
REQUEST_TOKEN = ""  # Obtained from the login redirect URL
INSTRUMENT_TOKEN = 738561  # Example: INFY NSE token
INTERVAL = "day"  # Options: "minute", "5minute", "15minute", "day", etc.
DAYS_BACK = 3650  # Number of days of historical data

# -----------------------------
# INITIALIZE KITE AND GENERATE ACCESS TOKEN
# -----------------------------
try:
    kite = KiteConnect(api_key=API_KEY)

    if not API_SECRET or not REQUEST_TOKEN or "your_" in API_SECRET or "your_" in REQUEST_TOKEN:
        raise ValueError("Set API_SECRET and REQUEST_TOKEN before running.")

    session = kite.generate_session(
        request_token=REQUEST_TOKEN,
        api_secret=API_SECRET,
    )
    access_token = session["access_token"]
    kite.set_access_token(access_token)
    print("Access token generated successfully.")
except Exception as e:
    print(f"Error initializing KiteConnect or generating access token: {e}")
    sys.exit(1)

# -----------------------------
# DATE RANGE
# -----------------------------
to_date = datetime.today()
from_date = to_date - timedelta(days=DAYS_BACK)

# -----------------------------
# FETCH HISTORICAL DATA
# -----------------------------
try:
    data = kite.historical_data(
        instrument_token=INSTRUMENT_TOKEN,
        from_date=from_date.strftime("%Y-%m-%d"),
        to_date=to_date.strftime("%Y-%m-%d"),
        interval=INTERVAL,
        continuous=False,
        oi=False,  # Set True if you want Open Interest
    )
except Exception as e:
    print(f"Error fetching historical data: {e}")
    sys.exit(1)

# -----------------------------
# LOAD INTO DATAFRAME
# -----------------------------
if not data:
    print("No data returned. Check token, date range, or market holidays.")
    sys.exit(0)

df = pd.DataFrame(data)

# Ensure datetime is parsed
df['date'] = pd.to_datetime(df['date'])

print(df.head())

# -----------------------------
# OPTIONAL: SAVE TO CSV
# -----------------------------
df.to_csv("nse_historical_data.csv", index=False)
print("Data saved to nse_historical_data.csv")
