from datetime import date
from nsepy import get_history
from nsepy.derivatives import get_expiry_date
# Stock options (Similarly for index options, set index = True)
stock_fut = get_history(symbol="ACC",
                        start=date(2018,6,10),
                        end=date(2018,6,25),
                        futures=True,
                        expiry_date=get_expiry_date(2018,6))
print(stock_fut)