import os, logging, sys, json, csv, time
sys.path.insert(0, '../')
from pymongo import MongoClient
import pprint

from util.util import pct_change_filter, getScore, all_day_pct_change_negative, all_day_pct_change_positive, no_doji_or_spinning_buy_india, no_doji_or_spinning_sell_india, scrip_patterns_to_dict
from util.util import is_algo_buy, is_algo_sell
from util.util import get_regressionResult
from util.util import buy_test_345, buy_test, buy_test_pct_change, buy_test_all, buy_other_indicator, buy_pattern_from_history, buy_all_rule, buy_year_high, buy_year_low, buy_up_trend, buy_down_trend, buy_final, buy_high_indicators, buy_pattern
from util.util import sell_test_345, sell_test, sell_test_pct_change, sell_test_all, sell_other_indicator, sell_pattern_from_history, sell_all_rule, sell_year_high, sell_year_low, sell_up_trend, sell_down_trend, sell_final, sell_high_indicators, sell_pattern
from util.util import buy_pattern_without_mlalgo, sell_pattern_without_mlalgo, buy_oi, sell_oi, all_withoutml
from util.util import buy_oi_candidate, sell_oi_candidate
from util.util import buy_all_filter, buy_all_common, sell_all_filter, sell_all_common
from util.util import buy_all_rule_classifier, sell_all_rule_classifier
from util.util import is_algo_buy_classifier, is_algo_sell_classifier
from util.util import sell_oi_negative, sell_day_high, buy_oi_negative, buy_day_low
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

def import_data_in_db():
    print('############################################')
    print('import_data_in_db')
    print('############################################')
    dbresult.drop_collection('buy_test_345')        
    dbresult.drop_collection('buy_test')
    dbresult.drop_collection('buy_test_pct_change')
    dbresult.drop_collection('buy_test_all')
    curs = db.ws_high.find({})
    print('buy_test_345')
    for data in curs:
        data['filterTest'] = ''
        flag = buy_test_345(data, data, True, None)
        if(flag):
            del data['_id']
            dbresult.buy_test_345.insert_one(json.loads(json.dumps(data))) 
    
    print('buy_test')
    curs = db.ws_high.find({})
    for data in curs:
        data['filterTest'] = ''
        flag = buy_test(data, data, True, None)
        if(flag):
            del data['_id']
            dbresult.buy_test.insert_one(json.loads(json.dumps(data))) 
    
    print('buy_test_pct_change')
    curs = db.ws_high.find({})
    for data in curs:
        data['filterTest'] = ''
        flag = buy_test_pct_change(data, data, True, None)
        if(flag):
            del data['_id']
            dbresult.buy_test_pct_change.insert_one(json.loads(json.dumps(data)))
    
    print('buy_test_all')        
    curs = db.ws_high.find({})
    for data in curs:
        data['filterTest'] = ''
        flag = buy_test_all(data, data, True, None)
        if(flag):
            del data['_id']
            dbresult.buy_test_all.insert_one(json.loads(json.dumps(data)))  
    
    dbresult.drop_collection('sell_test_345')  
    dbresult.drop_collection('sell_test')
    dbresult.drop_collection('sell_test_pct_change')
    dbresult.drop_collection('sell_test_all')
    curs = db.ws_low.find({})
    print('sell_test_345')
    for data in curs:
        data['filterTest'] = ''
        flag = sell_test_345(data, data, True, None)
        if(flag):
            del data['_id']
            dbresult.sell_test_345.insert_one(json.loads(json.dumps(data))) 
    
    print('sell_test')
    curs = db.ws_low.find({})
    for data in curs:
        data['filterTest'] = ''
        flag = sell_test(data, data, True, None)
        if(flag):
            del data['_id']
            dbresult.sell_test.insert_one(json.loads(json.dumps(data))) 
    
    print('sell_test_pct_change')
    curs = db.ws_low.find({})        
    for data in curs:
        data['filterTest'] = ''
        flag = sell_test_pct_change(data, data, True, None)
        if(flag):
            del data['_id']
            dbresult.sell_test_pct_change.insert_one(json.loads(json.dumps(data))) 
            
    print('sell_test_all')
    curs = db.ws_low.find({})        
    for data in curs:
        data['filterTest'] = ''
        flag = sell_test_all(data, data, True, None)
        if(flag):
            del data['_id']
            dbresult.sell_test_all.insert_one(json.loads(json.dumps(data))) 
            
def export_data_patterns_from_db():
    print('\n\n\n\n############################################')
    print('import_data_in_db')
    print('############################################')
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
    curs_to_csv(curser, '../../data-import/nselist/filter-345-buy.csv')
    
    print('buy_test')
    curser = dbresult.buy_test.aggregate(pipeline)
    curs_to_csv(curser, '../../data-import/nselist/filter-buy.csv')
    
    print('buy_test_pct_change')
    curser = dbresult.buy_test_pct_change.aggregate(pipeline)
    curs_to_csv(curser, '../../data-import/nselist/filter-pct-change-buy.csv')
    
    print('buy_test_all')
    curser = dbresult.buy_test_all.aggregate(pipeline)
    curs_to_csv(curser, '../../data-import/nselist/filter-all-buy.csv')
    
    print('sell_test_345')
    curser = dbresult.sell_test_345.aggregate(pipeline)
    curs_to_csv(curser, '../../data-import/nselist/filter-345-sell.csv')
    
    print('sell_test')
    curser = dbresult.sell_test.aggregate(pipeline)
    curs_to_csv(curser, '../../data-import/nselist/filter-sell.csv')
    
    print('sell_test_pct_change')
    curser = dbresult.sell_test_pct_change.aggregate(pipeline)
    curs_to_csv(curser, '../../data-import/nselist/filter-pct-change-sell.csv')
    
    print('sell_test_all')
    curser = dbresult.sell_test_all.aggregate(pipeline)
    curs_to_csv(curser, '../../data-import/nselist/filter-all-sell.csv')
    
    pipeline = [{"$project":{"buyIndia":"$buyIndia","Act_PCT_day_change":"$Act_PCT_day_change"}},
                {"$project":{"_id":"$_id","___group":{"buyIndia":"$buyIndia"},"Act_PCT_day_change":"$Act_PCT_day_change"}},
                {"$group":{"_id":"$___group","avg":{"$avg":"$Act_PCT_day_change"},"count":{"$sum":1}}},{"$sort":SON({"_id":1})},
                {"$project":{"_id":false,"buyIndia":"$_id.buyIndia","avg":true,"count":true}},
                {"$sort":SON({"buyIndia":1})}
                ]
    print('patterns-buy')
    curser = db.ws_high.aggregate(pipeline)
    curs_to_csv(curser, '../../data-import/nselist/patterns-buy.csv')
    
    pipeline = [{"$project":{"sellIndia":"$sellIndia","Act_PCT_day_change":"$Act_PCT_day_change"}},
                {"$project":{"_id":"$_id","___group":{"sellIndia":"$sellIndia"},"Act_PCT_day_change":"$Act_PCT_day_change"}},
                {"$group":{"_id":"$___group","avg":{"$avg":"$Act_PCT_day_change"},"count":{"$sum":1}}},{"$sort":SON({"_id":1})},
                {"$project":{"_id":false,"sellIndia":"$_id.sellIndia","avg":true,"count":true}},
                {"$sort":SON({"sellIndia":1})}
                ]
    print('patterns-sell')
    curser = db.ws_low.aggregate(pipeline)
    curs_to_csv(curser, '../../data-import/nselist/patterns-sell.csv')
    
if __name__ == "__main__":    
    import_data_in_db()
    export_data_patterns_from_db()