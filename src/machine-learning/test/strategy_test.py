import os, logging, sys, json, csv, time
sys.path.insert(0, '../')
from pymongo import MongoClient
import pprint

from util.util import pct_change_filter, getScore, all_day_pct_change_negative, all_day_pct_change_positive, no_doji_or_spinning_buy_india, no_doji_or_spinning_sell_india, scrip_patterns_to_dict
from util.util import is_algo_buy, is_algo_sell
from util.util import get_regressionResult
from util.util import test_short_term_filter3, test_short_term_filter, buy_test_345, buy_test, buy_test_pct_change, buy_test_all, buy_test_tech, buy_test_tech_all, buy_test_tech_all_pct_change, buy_other_indicator, buy_all_rule, buy_year_high, buy_year_low, buy_up_trend, buy_down_trend, buy_final
from util.util import sell_test_345, sell_test, sell_test_pct_change, sell_test_all, sell_test_tech, sell_test_tech_all, sell_test_tech_all_pct_change, sell_other_indicator, sell_all_rule, sell_year_high, sell_year_low, sell_up_trend, sell_down_trend, sell_final
from util.util import buy_oi, sell_oi, all_withoutml
from util.util import buy_all_filter, buy_all_common, sell_all_filter, sell_all_common
from util.util import buy_all_rule_classifier, sell_all_rule_classifier
from util.util import is_algo_buy_classifier, is_algo_sell_classifier
from util.util import sell_day_high, buy_day_low
from util.util_base import CLOSEPRICE
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

def curs_to_csv_short_term(curser, filename):
    data = list(curser)
    fields = ['filterTest', 'avg5', 'countgt5', 'countlt5', 'avg10', 'countgt10', 'countlt10', 'count']
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


def import_short_term_data_in_db_and_save():
    print('\n\n\n\n############################################')
    print('export_data_patterns_from_db')
    print('############################################')
    pipelinefiltertest = [{"$project": {"close_post5_change": "$close_post5_change",
                              "close_post10_change": "$close_post10_change",
                              "close_post20_change": "$close_post20_change",
                              "filterTest": "$filterTest",
                              }},
                {"$project": {"_id": "$_id",
                              "___group": {"filterTest": "$filterTest"},
                              "close_post5_change": "$close_post5_change",
                              "close_post10_change": "$close_post10_change",
                              "close_post20_change": "$close_post20_change",
                              }},
                {"$group": {"_id": "$___group",
                            "avg5": {"$avg": "$close_post5_change"},
                            "countgt5": {"$sum": {"$cond": [{"$gt": ['$close_post5_change', 5]}, 1, 0]}},
                            "countlt5": {"$sum": {"$cond": [{"$lt": ['$close_post5_change', -5]}, 1, 0]}},
                            "avg10": {"$avg": "$close_post10_change"},
                            "countgt10": {"$sum": {"$cond": [{"$gt": ['$close_post10_change', 10]}, 1, 0]}},
                            "countlt10": {"$sum": {"$cond": [{"$lt": ['$close_post10_change', -10]}, 1, 0]}},
                            "count": {"$sum": 1},
                            }},
                {"$project": {"_id": False, "filterTest": "$_id.filterTest", "avg5": True, "countgt5":True, "countlt5": True, "avg10": True,
                              "countgt10": True, "countlt10": True, "count": True}}
                ]

    pipelinefilter3 = [{"$project": {"close_post5_change": "$close_post5_change",
                              "close_post10_change": "$close_post10_change",
                              "close_post20_change": "$close_post20_change",
                              "filterTest": "$filterTest",
                              }},
                {"$project": {"_id": "$_id",
                              "___group": {"filterTest": "$filterTest"},
                              "close_post5_change": "$close_post5_change",
                              "close_post10_change": "$close_post10_change",
                              "close_post20_change": "$close_post20_change",
                              }},
                {"$group": {"_id": "$___group",
                            "avg5": {"$avg": "$close_post5_change"},
                            "countgt5": {"$sum": {"$cond": [{"$gt": ['$close_post5_change', 5]}, 1, 0]}},
                            "countlt5": {"$sum": {"$cond": [{"$lt": ['$close_post5_change', -5]}, 1, 0]}},
                            "avg10": {"$avg": "$close_post10_change"},
                            "countgt10": {"$sum": {"$cond": [{"$gt": ['$close_post10_change', 10]}, 1, 0]}},
                            "countlt10": {"$sum": {"$cond": [{"$lt": ['$close_post10_change', -10]}, 1, 0]}},
                            "count": {"$sum": 1},
                            }},
                {"$project": {"_id": False, "filterTest": "$_id.filterTest", "avg5": True, "countgt5":True, "countlt5": True, "avg10": True,
                              "countgt10": True, "countlt10": True, "count": True}}
                ]

    pipelinefilter4 = [{"$project": {"close_post5_change": "$close_post5_change",
                              "close_post10_change": "$close_post10_change",
                              "close_post20_change": "$close_post20_change",
                              "filter4": "$filter4",
                              }},
                {"$project": {"_id": "$_id",
                              "___group": {"filter4": "$filter4"},
                              "close_post5_change": "$close_post5_change",
                              "close_post10_change": "$close_post10_change",
                              "close_post20_change": "$close_post20_change",
                              }},
                {"$group": {"_id": "$___group",
                            "avg5": {"$avg": "$close_post5_change"},
                            "countgt5": {"$sum": {"$cond": [{"$gt": ['$close_post5_change', 5]}, 1, 0]}},
                            "countlt5": {"$sum": {"$cond": [{"$lt": ['$close_post5_change', -5]}, 1, 0]}},
                            "avg10": {"$avg": "$close_post10_change"},
                            "countgt10": {"$sum": {"$cond": [{"$gt": ['$close_post10_change', 10]}, 1, 0]}},
                            "countlt10": {"$sum": {"$cond": [{"$lt": ['$close_post10_change', -10]}, 1, 0]}},
                            "count": {"$sum": 1},
                            }},
                {"$project": {"_id": False, "filterTest": "$_id.filter4", "avg5": True, "countgt5":True, "countlt5": True, "avg10": True,
                              "countgt10": True, "countlt10": True, "count": True}}
                ]

    print('############################################')
    print('import_data_in_db')
    print('############################################')


    print('buy_test_short_term_filter')
    dbresult.drop_collection('buy_test_short_term_filter')
    curs = db.ws_high.find({})
    for data in curs:
        if (data['close'] > CLOSEPRICE and data['PCT_day_change'] != 0):
            data['filterTest'] = ''
            data['buyIndia_avg'] = 0
            data['buyIndia_count'] = 0
            data['sellIndia_avg'] = 0
            data['sellIndia_count'] = 0
            data['contract'] = 0
            del data['_id']
            flag = test_short_term_filter(data, data, True, None)
            if (flag):
                dbresult.buy_test_short_term_filter.insert_one(json.loads(json.dumps(data)))
            flag = test_short_term_filter3(data, data, True, None)
            if (flag):
                dbresult.buy_test_short_term_filter3.insert_one(json.loads(json.dumps(data)))

    print('buy_test_short_term')
    curser = dbresult.buy_test_short_term_filter.aggregate(pipelinefiltertest, allowDiskUse=True)
    curs_to_csv_short_term(curser, '../../data-import/nselist/buy_test_short_term_filter.csv')
    curser = dbresult.buy_test_short_term_filter.aggregate(pipelinefilter4, allowDiskUse=True)
    curs_to_csv_short_term(curser, '../../data-import/nselist/buy_test_short_term_filter4.csv')

    curser = dbresult.buy_test_short_term_filter3.aggregate(pipelinefilter3, allowDiskUse=True)
    curs_to_csv_short_term(curser, '../../data-import/nselist/buy_test_short_term_filter3.csv')
    dbresult.drop_collection('buy_test_short_term_filter')
    dbresult.drop_collection('buy_test_short_term_filter3')
    
    print('sell_test_short_term')
    dbresult.drop_collection('sell_test_short_term_filter')
    curs = db.ws_low.find({})
    for data in curs:
        if (data['close'] > CLOSEPRICE and data['PCT_day_change'] != 0):
            data['filterTest'] = ''
            data['buyIndia_avg'] = 0
            data['buyIndia_count'] = 0
            data['sellIndia_avg'] = 0
            data['sellIndia_count'] = 0
            data['contract'] = 0
            del data['_id']
            flag = test_short_term_filter(data, data, True, None)
            if (flag):
                dbresult.sell_test_short_term_filter.insert_one(json.loads(json.dumps(data)))
            flag = test_short_term_filter3(data, data, True, None)
            if (flag):
                dbresult.sell_test_short_term_filter3.insert_one(json.loads(json.dumps(data)))
    print('sell_test_short_term')
    curser = dbresult.sell_test_short_term_filter.aggregate(pipelinefiltertest, allowDiskUse=True)
    curs_to_csv_short_term(curser, '../../data-import/nselist/sell_test_short_term_filter.csv')
    curser = dbresult.sell_test_short_term_filter.aggregate(pipelinefilter4, allowDiskUse=True)
    curs_to_csv_short_term(curser, '../../data-import/nselist/sell_test_short_term_filter4.csv')

    curser = dbresult.sell_test_short_term_filter3.aggregate(pipelinefilter3, allowDiskUse=True)
    curs_to_csv_short_term(curser, '../../data-import/nselist/sell_test_short_term_filter3.csv')
    dbresult.drop_collection('sell_test_short_term_filter')
    dbresult.drop_collection('sell_test_short_term_filter3')

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
        if(data['close'] > CLOSEPRICE and data['PCT_day_change'] != 0):
            data['filterTest'] = ''
            data['buyIndia_avg'] = 0
            data['buyIndia_count'] = 0
            data['sellIndia_avg'] = 0
            data['sellIndia_count'] = 0
            data['contract'] = 0
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
        if(data['close'] > CLOSEPRICE and data['PCT_day_change'] != 0):
            data['filterTest'] = ''
            data['buyIndia_avg'] = 0
            data['buyIndia_count'] = 0
            data['sellIndia_avg'] = 0
            data['sellIndia_count'] = 0
            data['contract'] = 0
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
        if(data['close'] > CLOSEPRICE and data['PCT_day_change'] != 0):
            data['filterTest'] = ''
            data['buyIndia_avg'] = 0
            data['buyIndia_count'] = 0
            data['sellIndia_avg'] = 0
            data['sellIndia_count'] = 0
            data['contract'] = 0
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
        if(data['close'] > CLOSEPRICE and data['PCT_day_change'] != 0):
            data['filterTest'] = ''
            data['buyIndia_avg'] = 0
            data['buyIndia_count'] = 0
            data['sellIndia_avg'] = 0
            data['sellIndia_count'] = 0
            data['contract'] = 0
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
        if(data['close'] > CLOSEPRICE and data['PCT_day_change'] != 0):
            data['filterTest'] = ''
            data['buyIndia_avg'] = 0
            data['buyIndia_count'] = 0
            data['sellIndia_avg'] = 0
            data['sellIndia_count'] = 0
            data['contract'] = 0
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
        if(data['close'] > CLOSEPRICE and data['PCT_day_change'] != 0):
            data['filterTest'] = ''
            data['buyIndia_avg'] = 0
            data['buyIndia_count'] = 0
            data['sellIndia_avg'] = 0
            data['sellIndia_count'] = 0
            data['contract'] = 0
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
        if(data['close'] > CLOSEPRICE and data['PCT_day_change'] != 0):
            data['filterTest'] = ''
            data['buyIndia_avg'] = 0
            data['buyIndia_count'] = 0
            data['sellIndia_avg'] = 0
            data['sellIndia_count'] = 0
            data['contract'] = 0
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
        if(data['close'] > CLOSEPRICE and data['PCT_day_change'] != 0):
            data['filterTest'] = ''
            data['buyIndia_avg'] = 0
            data['buyIndia_count'] = 0
            data['sellIndia_avg'] = 0
            data['sellIndia_count'] = 0
            data['contract'] = 0
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
        if(data['close'] > CLOSEPRICE and data['PCT_day_change'] != 0):
            data['filterTest'] = ''
            data['buyIndia_avg'] = 0
            data['buyIndia_count'] = 0
            data['sellIndia_avg'] = 0
            data['sellIndia_count'] = 0
            data['contract'] = 0
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
        if(data['close'] > CLOSEPRICE and data['PCT_day_change'] != 0):
            data['filterTest'] = ''
            data['buyIndia_avg'] = 0
            data['buyIndia_count'] = 0
            data['sellIndia_avg'] = 0
            data['sellIndia_count'] = 0
            data['contract'] = 0
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
        if(data['close'] > CLOSEPRICE and data['PCT_day_change'] != 0):
            data['filterTest'] = ''
            data['buyIndia_avg'] = 0
            data['buyIndia_count'] = 0
            data['sellIndia_avg'] = 0
            data['sellIndia_count'] = 0
            data['contract'] = 0
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
        if(data['close'] > CLOSEPRICE and data['PCT_day_change'] != 0):
            data['filterTest'] = ''
            data['buyIndia_avg'] = 0
            data['buyIndia_count'] = 0
            data['sellIndia_avg'] = 0
            data['sellIndia_count'] = 0
            data['contract'] = 0
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
        if(data['close'] > CLOSEPRICE and data['PCT_day_change'] != 0):
            data['filterTest'] = ''
            data['buyIndia_avg'] = 0
            data['buyIndia_count'] = 0
            data['sellIndia_avg'] = 0
            data['sellIndia_count'] = 0
            data['contract'] = 0
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
        if(data['close'] > CLOSEPRICE and data['PCT_day_change'] != 0):
            data['filterTest'] = ''
            data['buyIndia_avg'] = 0
            data['buyIndia_count'] = 0
            data['sellIndia_avg'] = 0
            data['sellIndia_count'] = 0
            data['contract'] = 0
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
    import_short_term_data_in_db_and_save()
    #export_tech_patterns_from_db() 
    import_data_in_db_and_save()
    db_cleanup()