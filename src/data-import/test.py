#import yfinance as yf
#data = yf.download("INFY.NS", start="2017-01-01", end="2017-04-30")
#print(data)

import yfinance as yf

# Define the ticker symbol
ticker_symbol = "TCS.NS"

# Create a Ticker object
ticker = yf.Ticker(ticker_symbol)

# Fetch historical market data
historical_data = ticker.history(period="1y")  # data for the last year
print("Historical Data:")
print(historical_data)

# Fetch basic financials
financials = ticker.financials
print("\nFinancials:")
print(financials)

# Fetch stock actions like dividends and splits
actions = ticker.actions
print("\nStock Actions:")
print(actions)




