#from NSEDownload import stocks

# Gets data without adjustment for events
#df = stocks.get_data(symbol='RELIANCE', start_date='15-9-2021', end_date='1-10-2021')

#from nsepy import get_history
#from datetime import date
#data = get_history(symbol="SBIN", start=date(2015,1,1), end=date(2015,1,31))
#data[['Close']].plot()

from nsedt import equity as eq
from datetime import date

start_date = date(2023, 1, 1)
end_date = date(2023, 1, 10)
print(eq.get_price(start_date, end_date, symbol="TCS"))