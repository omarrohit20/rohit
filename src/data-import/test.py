import yfinance as yf
data = yf.download("INFY.NS", start="2017-01-01", end="2017-04-30")
print(data)