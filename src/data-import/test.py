import yfinance as yf
from pymongo import MongoClient
data = yf.download("INFY.NS", start="2017-01-01", end="2017-04-30")
print(data)