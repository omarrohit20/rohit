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

connection = MongoClient('localhost', 27017)
db = connection.nsehistnew
dbresult = connection.result

# dbresult.drop_collection('buy_other_indicator')
# curs = db.ws_highAll.find({})
# for data in curs:
#     data['filterTest'] = ''
#     flag = buy_other_indicator(data, data, True, None)
#     if(flag):
#         del data['_id']
#         dbresult.buy_other_indicator.insert_one(json.loads(json.dumps(data))) 
# 
# dbresult.drop_collection('sell_other_indicator')        
# curs = db.ws_lowAll.find({})
# for data in curs:
#     data['filterTest'] = ''
#     flag = sell_other_indicator(data, data, True, None)
#     if(flag):
#         del data['_id']
#         dbresult.sell_other_indicator.insert_one(json.loads(json.dumps(data))) 
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