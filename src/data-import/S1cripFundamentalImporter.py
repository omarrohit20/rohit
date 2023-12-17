import time
from nsetools import Nse
import csv
from pymongo import MongoClient
connection = MongoClient('localhost', 27017)
db = connection.Nsedata
db.drop_collection('fundamental')

#nse = Nse()
# for data in db.scrip.find():
#     try:
#         stock = nse.get_quote((data['scrip']).encode('UTF8'))
#         if stock is not None:
#             db.fundamental.insert_one(stock)
#         else:
#             stock = nse.get_quote((data['scrip']).encode('UTF8'))
#             if stock is not None:
#                 db.fundamental.insert_one(stock)
#             else:
#                 print('fundamental ', str(data['scrip']))
#     except:
#         time.sleep(2)
#         try:
#             stock = nse.get_quote((data['scrip']).encode('UTF8'))
#             if stock is not None:
#                 db.fundamental.insert_one(stock)
#             else:
#                 stock = nse.get_quote((data['scrip']).encode('UTF8'))
#                 if stock is not None:
#                     db.fundamental.insert_one(stock)
#                 else:
#                     print('fundamental ', str(data['scrip']))
#         except:
#             print('fundamental failed', str(data['scrip']))
#             pass

count = 0
with open('nselist/fundamental.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        try:
            if (count != 0):
                print(row[0])
                db.fundamental.insert_one({
                    "scrip": row[0],
                    "marketcap": row[1],
                    "netprofit": row[2],
                    "peratio": row[3],
                    "publicholding": row[4]
                })
            count = count + 1
        except:
            pass
print(count)

connection.close()
print('Done fundamental')