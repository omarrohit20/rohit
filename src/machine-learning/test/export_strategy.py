import os, logging, sys, json, csv, time
sys.path.insert(0, '../')
from pymongo import MongoClient
import pprint

from bson.son import SON

connection = MongoClient('localhost', 27017)
db = connection.nsehistnew
dbresult = connection.result

 
def curs_to_csv(curser, filename):
    data = list(curser)
    fields = ['filterTest', 'avg', 'count', 'countgt', 'countlt']
    with open(filename, 'w') as outfile:   
        write = csv.DictWriter(outfile, fieldnames=fields)
        for record in data: 
            write.writerow(record)
            


pipeline = [{"$project":{"Act_PCT_day_change":"$Act_PCT_day_change",
                         "filterTest":"$filterTest",
                         }},
            {"$project":{"_id":"$_id",
                         "___group":{"filterTest":"$filterTest"},
                         "Act_PCT_day_change":"$Act_PCT_day_change",
                         }},
            {"$group":{"_id":"$___group",
                       "avg":{"$avg":"$Act_PCT_day_change"},
                       "count":{"$sum":1},
                       "countgt":{"$sum" : {"$cond": [{"$gt": ['$Act_PCT_day_change', 0]}, 1, 0]}},
                       "countlt":{"$sum": {"$cond": [{"$lt": ['$Act_PCT_day_change', 0]}, 1, 0]}},
                       }},
            {"$sort":SON({"_id":1})},
            {"$project":{"_id":False,"filterTest":"$_id.filterTest","avg":True,"count":True,"countgt":True,"countlt":True}},
            {"$sort":SON({"filterTest":1})}
            ]

print('buy_test_345')
curser = dbresult.buy_test_345.aggregate(pipeline)
curs_to_csv(curser, '../../output/filter-345-buy.csv')

print('buy_test')
curser = dbresult.buy_test.aggregate(pipeline)
curs_to_csv(curser, '../../output/filter-buy.csv')

print('buy_test_pct_change')
curser = dbresult.buy_test_pct_change.aggregate(pipeline)
curs_to_csv(curser, '../../output/filter-pct-change-buy.csv')

print('buy_test_all')
curser = dbresult.buy_test_all.aggregate(pipeline)
curs_to_csv(curser, '../../output/filter-all-buy.csv')



print('sell_test_345')
curser = dbresult.sell_test_345.aggregate(pipeline)
curs_to_csv(curser, '../../output/filter-345-sell.csv')

print('sell_test')
curser = dbresult.sell_test.aggregate(pipeline)
curs_to_csv(curser, '../../output/filter-sell.csv')

print('sell_test_pct_change')
curser = dbresult.sell_test_pct_change.aggregate(pipeline)
curs_to_csv(curser, '../../output/filter-pct-change-sell.csv')

print('sell_test_all')
curser = dbresult.sell_test_all.aggregate(pipeline)
curs_to_csv(curser, '../../output/filter-all-sell.csv')

