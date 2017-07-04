from nsetools import Nse
from pymongo import MongoClient
connection = MongoClient('localhost', 27017)
db = connection.stocks.nse

nse = Nse()
all_stock_codes = nse.get_stock_codes()
    
count = 0
for scrip,company in all_stock_codes.items():
    try:
        print company
        stock = nse.get_quote('HDFC')
        if stock is not None:
            count += 1
            
            from pprint import pprint # just for neatness of display
            pprint(stock)
            db.insert(stock)
    except Exception, err:
        print Exception, err
print count

connection.close()
    
    
