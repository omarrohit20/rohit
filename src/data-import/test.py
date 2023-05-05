#import yfinance as yf
#data = yf.download("INFY.NS", start="2017-01-01", end="2017-04-30")
#print(data)


from nsepython import *
print(indices)
symbol = "INFY"
series = "EQ"
start_date = "08-04-2023"
end_date ="28-04-2023"
print(equity_history(symbol,series,start_date,end_date))