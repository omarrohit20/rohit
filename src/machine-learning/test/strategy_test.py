import os, logging, sys, json, csv, time
sys.path.insert(0, '../')
from pymongo import MongoClient
import pprint

from util.util import pct_change_filter, getScore, all_day_pct_change_negative, all_day_pct_change_positive, no_doji_or_spinning_buy_india, no_doji_or_spinning_sell_india, scrip_patterns_to_dict
from util.util import is_algo_buy, is_algo_sell
from util.util import get_regressionResult
from util.util import buy_test_345, buy_test, buy_test_pct_change, buy_test_all, buy_test_tech, buy_test_tech_all, buy_test_tech_all_pct_change, buy_other_indicator, buy_pattern_from_history, buy_all_rule, buy_year_high, buy_year_low, buy_up_trend, buy_down_trend, buy_final, buy_high_indicators, buy_pattern
from util.util import sell_test_345, sell_test, sell_test_pct_change, sell_test_all, sell_test_tech, sell_test_tech_all, sell_test_tech_all_pct_change, sell_other_indicator, sell_pattern_from_history, sell_all_rule, sell_year_high, sell_year_low, sell_up_trend, sell_down_trend, sell_final, sell_high_indicators, sell_pattern
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

def tech_buy_curs_to_csv(curser, filename):
    data = list(curser)
    fields = ['buyIndia', 'avg', 'count']
    with open(filename, 'w') as outfile:   
        write = csv.DictWriter(outfile, fieldnames=fields)
        for record in data: 
            write.writerow(record)
            
def tech_sell_curs_to_csv(curser, filename):
    data = list(curser)
    fields = ['sellIndia', 'avg', 'count']
    with open(filename, 'w') as outfile:   
        write = csv.DictWriter(outfile, fieldnames=fields)
        for record in data: 
            write.writerow(record)            

def db_cleanup():
    dbresult.drop_collection('buy_test_345')  
    dbresult.drop_collection('buy_test')
    dbresult.drop_collection('buy_test_pct_change')
    dbresult.drop_collection('buy_test_all')
    dbresult.drop_collection('buy_test_tech')
    dbresult.drop_collection('buy_test_tech_all')
    dbresult.drop_collection('buy_test_tech_all_pct_change')
    
    dbresult.drop_collection('sell_test_345')  
    dbresult.drop_collection('sell_test')
    dbresult.drop_collection('sell_test_pct_change')
    dbresult.drop_collection('sell_test_all')
    dbresult.drop_collection('sell_test_tech')
    dbresult.drop_collection('sell_test_tech_all')
    dbresult.drop_collection('sell_test_tech_all_pct_change')

def import_data_in_db_and_save():
    print('\n\n\n\n############################################')
    print('export_data_patterns_from_db')
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
            #{"$sort":SON({"_id":1})},
            {"$project":{"_id":False,"filterTest":"$_id.filterTest","avg":True,"count":True,"countgt":True,"countlt":True}}
            #{"$sort":SON({"filterTest":1})},
            #{"allowDiskUse":True }
            ]
    
    print('############################################')
    print('import_data_in_db')
    print('############################################')
    
    print('buy_test_345')
    dbresult.drop_collection('buy_test_345')       
    curs = db.ws_high.find({})
    for data in curs:
        data['filterTest'] = ''
        flag = buy_test_345(data, data, True, None)
        if(flag):
            del data['_id']
            dbresult.buy_test_345.insert_one(json.loads(json.dumps(data)))
    print('buy_test_345')
    curser = dbresult.buy_test_345.aggregate(pipeline, allowDiskUse=True)
    curs_to_csv(curser, '../../data-import/nselist/filter-345-buy.csv')
    dbresult.drop_collection('buy_test_345')    
        
         
    print('buy_test')
    dbresult.drop_collection('buy_test')
    curs = db.ws_high.find({})
    for data in curs:
        data['filterTest'] = ''
        flag = buy_test(data, data, True, None)
        if(flag):
            del data['_id']
            dbresult.buy_test.insert_one(json.loads(json.dumps(data)))
    print('buy_test')
    curser = dbresult.buy_test.aggregate(pipeline, allowDiskUse=True)
    curs_to_csv(curser, '../../data-import/nselist/filter-buy.csv')
    dbresult.drop_collection('buy_test')
         
         
    print('buy_test_pct_change')
    dbresult.drop_collection('buy_test_pct_change')
    curs = db.ws_high.find({})
    for data in curs:
        data['filterTest'] = ''
        flag = buy_test_pct_change(data, data, True, None)
        if(flag):
            del data['_id']
            dbresult.buy_test_pct_change.insert_one(json.loads(json.dumps(data)))
    print('buy_test_pct_change')
    curser = dbresult.buy_test_pct_change.aggregate(pipeline, allowDiskUse=True)
    curs_to_csv(curser, '../../data-import/nselist/filter-pct-change-buy.csv')
    dbresult.drop_collection('buy_test_pct_change')
        
        
    print('buy_test_all')
    dbresult.drop_collection('buy_test_all')         
    curs = db.ws_high.find({})
    for data in curs:
        data['filterTest'] = ''
        flag = buy_test_all(data, data, True, None)
        if(flag):
            del data['_id']
            dbresult.buy_test_all.insert_one(json.loads(json.dumps(data)))
    print('buy_test_all')
    curser = dbresult.buy_test_all.aggregate(pipeline, allowDiskUse=True)
    curs_to_csv(curser, '../../data-import/nselist/filter-all-buy.csv')
    dbresult.drop_collection('buy_test_all')
        
                
    print('buy_test_tech')
    dbresult.drop_collection('buy_test_tech')     
    curs = db.ws_high.find({})
    for data in curs:
        data['filterTest'] = ''
        flag = buy_test_tech(data, data, True, None)
        if(flag):
            del data['_id']
            dbresult.buy_test_tech.insert_one(json.loads(json.dumps(data)))
    print('buy_test_tech')
    curser = dbresult.buy_test_tech.aggregate(pipeline, allowDiskUse=True)
    curs_to_csv(curser, '../../data-import/nselist/filter-tech-buy.csv')
    dbresult.drop_collection('buy_test_tech')
       
                
    print('buy_test_tech_all')
    dbresult.drop_collection('buy_test_tech_all')       
    curs = db.ws_high.find({})
    for data in curs:
        data['filterTest'] = ''
        flag = buy_test_tech_all(data, data, True, None)
        if(flag):
            del data['_id']
            dbresult.buy_test_tech_all.insert_one(json.loads(json.dumps(data)))
    print('buy_test_tech_all')
    curser = dbresult.buy_test_tech_all.aggregate(pipeline, allowDiskUse=True)
    curs_to_csv(curser, '../../data-import/nselist/filter-tech-all-buy.csv')
    dbresult.drop_collection('buy_test_tech_all')
     
              
    print('buy_test_tech_all_pct_change')
    dbresult.drop_collection('buy_test_tech_all_pct_change')       
    curs = db.ws_high.find({})
    for data in curs:
        data['filterTest'] = ''
        flag = buy_test_tech_all_pct_change(data, data, True, None)
        if(flag):
            del data['_id']
            dbresult.buy_test_tech_all_pct_change.insert_one(json.loads(json.dumps(data)))  
    print('buy_test_tech_all_pct_change')
    curser = dbresult.buy_test_tech_all_pct_change.aggregate(pipeline, allowDiskUse=True)
    curs_to_csv(curser, '../../data-import/nselist/filter-tech-all-pct-change-buy.csv')
    dbresult.drop_collection('buy_test_tech_all_pct_change')
     
 
     
    print('sell_test_345')
    dbresult.drop_collection('sell_test_345') 
    curs = db.ws_low.find({})
    for data in curs:
        data['filterTest'] = ''
        flag = sell_test_345(data, data, True, None)
        if(flag):
            del data['_id']
            dbresult.sell_test_345.insert_one(json.loads(json.dumps(data))) 
    print('sell_test_345')
    curser = dbresult.sell_test_345.aggregate(pipeline, allowDiskUse=True)
    curs_to_csv(curser, '../../data-import/nselist/filter-345-sell.csv')
    dbresult.drop_collection('sell_test_345') 
      
       
    print('sell_test')
    dbresult.drop_collection('sell_test')
    curs = db.ws_low.find({})
    for data in curs:
        data['filterTest'] = ''
        flag = sell_test(data, data, True, None)
        if(flag):
            del data['_id']
            dbresult.sell_test.insert_one(json.loads(json.dumps(data))) 
    print('sell_test')
    curser = dbresult.sell_test.aggregate(pipeline, allowDiskUse=True)
    curs_to_csv(curser, '../../data-import/nselist/filter-sell.csv')
    dbresult.drop_collection('sell_test')
      
       
    print('sell_test_pct_change')
    dbresult.drop_collection('sell_test_pct_change')
    curs = db.ws_low.find({})        
    for data in curs:
        data['filterTest'] = ''
        flag = sell_test_pct_change(data, data, True, None)
        if(flag):
            del data['_id']
            dbresult.sell_test_pct_change.insert_one(json.loads(json.dumps(data)))
    print('sell_test_pct_change')
    curser = dbresult.sell_test_pct_change.aggregate(pipeline, allowDiskUse=True)
    curs_to_csv(curser, '../../data-import/nselist/filter-pct-change-sell.csv') 
    dbresult.drop_collection('sell_test_pct_change')
               
    print('sell_test_all')
    dbresult.drop_collection('sell_test_all')
    curs = db.ws_low.find({})        
    for data in curs:
        data['filterTest'] = ''
        flag = sell_test_all(data, data, True, None)
        if(flag):
            del data['_id']
            dbresult.sell_test_all.insert_one(json.loads(json.dumps(data)))
    print('sell_test_all')
    curser = dbresult.sell_test_all.aggregate(pipeline, allowDiskUse=True)
    curs_to_csv(curser, '../../data-import/nselist/filter-all-sell.csv') 
    dbresult.drop_collection('sell_test_all')
              
    print('sell_test_tech')  
    dbresult.drop_collection('sell_test_tech')      
    curs = db.ws_low.find({})
    for data in curs:
        data['filterTest'] = ''
        flag = sell_test_tech(data, data, True, None)
        if(flag):
            del data['_id']
            dbresult.sell_test_tech.insert_one(json.loads(json.dumps(data)))
    print('sell_test_tech')
    curser = dbresult.sell_test_tech.aggregate(pipeline, allowDiskUse=True)
    curs_to_csv(curser, '../../data-import/nselist/filter-tech-sell.csv')
    dbresult.drop_collection('sell_test_tech')
      
              
    print('sell_test_tech_all') 
    dbresult.drop_collection('sell_test_tech_all')       
    curs = db.ws_low.find({})
    for data in curs:
        data['filterTest'] = ''
        flag = sell_test_tech_all(data, data, True, None)
        if(flag):
            del data['_id']
            dbresult.sell_test_tech_all.insert_one(json.loads(json.dumps(data)))
    print('sell_test_tech_all')
    curser = dbresult.sell_test_tech_all.aggregate(pipeline, allowDiskUse=True)
    curs_to_csv(curser, '../../data-import/nselist/filter-tech-all-sell.csv')
    dbresult.drop_collection('sell_test_tech_all')
             
    print('sell_test_tech_all_pct_change')  
    dbresult.drop_collection('sell_test_tech_all_pct_change')      
    curs = db.ws_low.find({})
    for data in curs:
        data['filterTest'] = ''
        flag = sell_test_tech_all_pct_change(data, data, True, None)
        if(flag):
            del data['_id']
            dbresult.sell_test_tech_all_pct_change.insert_one(json.loads(json.dumps(data)))
    print('sell_test_tech_all_pct_change')
    curser = dbresult.sell_test_tech_all_pct_change.aggregate(pipeline, allowDiskUse=True)
    curs_to_csv(curser, '../../data-import/nselist/filter-tech-all-pct-change-sell.csv') 
    dbresult.drop_collection('sell_test_tech_all_pct_change')
 
def import_filter_data_in_db():
    print('############################################')
    print('import_filter_data_in_db')
    print('############################################')
    dbresult.drop_collection('buy_test')
    print('buy_test')
    curs = db.ws_high.find({})
    for data in curs:
        data['filterTest'] = ''
        flag = buy_test(data, data, True, None)
        if(flag):
            del data['_id']
            dbresult.buy_test.insert_one(json.loads(json.dumps(data))) 
    
    dbresult.drop_collection('sell_test')
    print('sell_test')
    curs = db.ws_low.find({})
    for data in curs:
        data['filterTest'] = ''
        flag = sell_test(data, data, True, None)
        if(flag):
            del data['_id']
            dbresult.sell_test.insert_one(json.loads(json.dumps(data))) 
                    
def export_tech_patterns_from_db():
    print('\n\n\n\n############################################')
    print('export_tech_patterns_from_db')
    print('############################################')   
    pipeline = [{"$project":{"buyIndia":"$buyIndia","Act_PCT_day_change":"$Act_PCT_day_change"}},
                {"$project":{"_id":"$_id","___group":{"buyIndia":"$buyIndia"},"Act_PCT_day_change":"$Act_PCT_day_change"}},
                {"$group":{"_id":"$___group","avg":{"$avg":"$Act_PCT_day_change"},"count":{"$sum":1}}},{"$sort":SON({"_id":1})},
                {"$project":{"_id":False,"buyIndia":"$_id.buyIndia","avg":True,"count":True}},
                {"$sort":SON({"buyIndia":1})}
                ]
    print('patterns-buy')
    curser = db.ws_high.aggregate(pipeline, allowDiskUse=True)
    tech_buy_curs_to_csv(curser, '../../data-import/nselist/patterns-buy.csv')
    
    pipeline = [{"$project":{"sellIndia":"$sellIndia","Act_PCT_day_change":"$Act_PCT_day_change"}},
                {"$project":{"_id":"$_id","___group":{"sellIndia":"$sellIndia"},"Act_PCT_day_change":"$Act_PCT_day_change"}},
                {"$group":{"_id":"$___group","avg":{"$avg":"$Act_PCT_day_change"},"count":{"$sum":1}}},{"$sort":SON({"_id":1})},
                {"$project":{"_id":False,"sellIndia":"$_id.sellIndia","avg":True,"count":True}},
                {"$sort":SON({"sellIndia":1})}
                ]
    print('patterns-sell')
    curser = db.ws_low.aggregate(pipeline, allowDiskUse=True)
    tech_sell_curs_to_csv(curser, '../../data-import/nselist/patterns-sell.csv')
    
if __name__ == "__main__":  
    db_cleanup()  
    import_data_in_db_and_save()
    #export_tech_patterns_from_db()
    db_cleanup()