import time
from nsetools import Nse
from pymongo import MongoClient
connection = MongoClient('localhost', 27017)
db = connection.Nsedata
#db.drop_collection('fundamental')
    
nse = Nse()
for data in db.scrip.find():
    try:
        stock = nse.get_quote((data['scrip']).encode('UTF8'))
        if stock is not None:
            db.fundamental.insert_one(stock)
        else:
            stock = nse.get_quote((data['scrip']).encode('UTF8'))
            if stock is not None:
                db.fundamental.insert_one(stock)
            else:
                print 'fundamental ', str(data['scrip'])    
    except:
        time.sleep(2)
        try:
            stock = nse.get_quote((data['scrip']).encode('UTF8'))
            if stock is not None:
                db.fundamental.insert_one(stock)
            else:
                stock = nse.get_quote((data['scrip']).encode('UTF8'))
                if stock is not None:
                    db.fundamental.insert_one(stock)
                else:
                    print 'fundamental ', str(data['scrip'])   
        except:
            print 'fundamental ', str(data['scrip'])  
            pass


connection.close()
print 'Done fundamental'