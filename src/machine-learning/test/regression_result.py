import os, logging, sys, json, csv
sys.path.insert(0, '../')

from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import Color, PatternFill, Font, Border
from pymongo import MongoClient
from multiprocessing.dummy import Pool as ThreadPool

import quandl, math, time
import pandas as pd
import numpy as np
from talib.abstract import *

import datetime
import time
import gc

from util.util import getScore, all_day_pct_change_negative, all_day_pct_change_positive, no_doji_or_spinning_buy_india, no_doji_or_spinning_sell_india, scrip_patterns_to_dict
from util.util import is_algo_buy, is_algo_sell
from util.util import get_regressionResult
from util.util import buy_pattern_from_history, buy_all_rule, buy_year_high, buy_year_low, buy_up_trend, buy_down_trend, buy_final, buy_high_indicators, buy_pattern
from util.util import sell_pattern_from_history, sell_all_rule, sell_year_high, sell_year_low, sell_up_trend, sell_down_trend, sell_final, sell_high_indicators, sell_pattern
from util.util import buy_pattern_without_mlalgo, sell_pattern_without_mlalgo, buy_oi, sell_oi, all_withoutml
from util.util import buy_oi_candidate, sell_oi_candidate
from util.util import buy_all_filter, buy_all_common, sell_all_filter, sell_all_common
from util.util import buy_all_rule_classifier, sell_all_rule_classifier
from util.util import is_algo_buy_classifier, is_algo_sell_classifier
from util.util import sell_oi_negative, sell_day_high, buy_oi_negative, buy_day_low



connection = MongoClient('localhost', 27017)
db = connection.histnse

buyPatternsDict=scrip_patterns_to_dict('../../data-import/nselist/patterns-buy.csv')
sellPatternsDict=scrip_patterns_to_dict('../../data-import/nselist/patterns-sell.csv')

directory = '../../output/final'
logname = '../../output/final' + '/all-result' + time.strftime("%d%m%y-%H%M%S")
      
def result_data(regression_high, regression_low, scrip):
    regression_data = regression_high
    regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_low['mlpValue_reg'], 
                                            regression_low['kNeighboursValue_reg'],
                                            regression_low['mlpValue_cla'], 
                                            regression_low['kNeighboursValue_cla'],
                                            )
    re_oi = buy_oi_candidate(regression_data, regressionResult, True, None)
    cl_oi = buy_oi_candidate(regression_data, regressionResult, False, None)
    if(cl_oi and re_oi):
        all_withoutml(regression_data, regressionResult, None)   
    
    buyIndiaAvgReg, result = buy_pattern_from_history(regression_data, regressionResult, None)
    if (buy_all_rule(regression_data, regressionResult, buyIndiaAvgReg, None)
        and buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvgReg, None)
        ):
        buy_all_filter(regression_data, regressionResult, True, None)
        buy_all_common(regression_data, regressionResult, True, None)
        buy_all_filter(regression_data, regressionResult, False, None)
        buy_all_common(regression_data, regressionResult, False, None)
        if (buy_all_rule(regression_data, regressionResult, buyIndiaAvgReg, None)
            or buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvgReg, None)):
            if(len(regression_high['filter']) > 3):
                db.ws_buyAll.insert_one(json.loads(json.dumps(regression_high))) 
            #print('')
    
    regression_data = regression_low
    regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_high['mlpValue_reg'], 
                                            regression_high['kNeighboursValue_reg'],
                                            regression_high['mlpValue_cla'], 
                                            regression_high['kNeighboursValue_cla']
                                            )
    re_oi = sell_oi_candidate(regression_data, regressionResult, True, None)
    cl_oi = sell_oi_candidate(regression_data, regressionResult, False, None)
    if(cl_oi and re_oi):
        all_withoutml(regression_data, regressionResult, None)
     
    sellIndiaAvgReg, result = sell_pattern_from_history(regression_data, regressionResult, None)
    if (sell_all_rule(regression_data, regressionResult, sellIndiaAvgReg, None)
        and sell_all_rule_classifier(regression_data, regressionResult, sellIndiaAvgReg, None)
        ):
        buy_all_filter(regression_data, regressionResult, True, None)
        buy_all_common(regression_data, regressionResult, True, None)
        buy_all_filter(regression_data, regressionResult, False, None)
        buy_all_common(regression_data, regressionResult, False, None)
        if (sell_all_rule(regression_data, regressionResult, sellIndiaAvgReg, None)
            or sell_all_rule_classifier(regression_data, regressionResult, sellIndiaAvgReg, None)):
            #print('')
            if(len(regression_low['filter']) > 3):
                db.ws_sellAll.insert_one(json.loads(json.dumps(regression_low))) 
                                  
def result_data_reg(regression_high, regression_low, scrip):
    regression_data = regression_high
    if(regression_data is not None):
        regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_low['mlpValue_reg'], 
                                            regression_low['kNeighboursValue_reg'],
                                            regression_low['mlpValue_cla'], 
                                            regression_low['kNeighboursValue_cla'],
                                            )
        buy_pattern_without_mlalgo(regression_data, regressionResult, None, None)
        oi = buy_oi_candidate(regression_data, regressionResult, True, None)
        if oi:
            all_withoutml(regression_data, regressionResult, None)
            if(len(regression_high['filter']) > 3):
                db.ws_buyOIReg.insert_one(json.loads(json.dumps(regression_high))) 
        buyIndiaAvg, result = buy_pattern_from_history(regression_data, regressionResult, None)
        if buy_all_rule(regression_data, regressionResult, buyIndiaAvg, None):
            buy_year_high(regression_data, regressionResult, True, None)
            buy_year_low(regression_data, regressionResult, True, None, None)
            buy_final(regression_data, regressionResult, True, None, None)
            buy_up_trend(regression_data, regressionResult, True, None)
            buy_down_trend(regression_data, regressionResult, True, None)
            buy_oi(regression_data, regressionResult, True, None)
            buy_high_indicators(regression_data, regressionResult, True, None)
            buy_pattern(regression_data, regressionResult, True, None, None)
            buy_all_rule(regression_data, regressionResult, buyIndiaAvg, None)
            if(len(regression_high['filter']) > 3):
                db.ws_buyAllReg.insert_one(json.loads(json.dumps(regression_high))) 
        all_withoutml(regression_data, regressionResult, None)
        db.ws_highAll.insert_one(json.loads(json.dumps(regression_high))) 
                
    regression_data = regression_low
    if(regression_data is not None):
        regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_high['mlpValue_reg'], 
                                            regression_high['kNeighboursValue_reg'],
                                            regression_high['mlpValue_cla'], 
                                            regression_high['kNeighboursValue_cla']
                                            )
        sell_pattern_without_mlalgo(regression_data, regressionResult, None, None)
        oi = sell_oi_candidate(regression_data, regressionResult, True, None)
        if oi:
            all_withoutml(regression_data, regressionResult, None)
            if(len(regression_low['filter']) > 3):
                db.ws_sellOIReg.insert_one(json.loads(json.dumps(regression_low))) 
        sellIndiaAvg, result = sell_pattern_from_history(regression_data, regressionResult, None)
        if sell_all_rule(regression_data, regressionResult, sellIndiaAvg, None):
            sell_year_high(regression_data, regressionResult, True, None, None)
            sell_year_low(regression_data, regressionResult, True, None)
            sell_final(regression_data, regressionResult, True, None, None)
            sell_up_trend(regression_data, regressionResult, True, None)
            #sell_down_trend(regression_data, regressionResult, None)
            sell_oi(regression_data, regressionResult, True, None)
            sell_high_indicators(regression_data, regressionResult, True, None)
            sell_pattern(regression_data, regressionResult, True, None, None)
            sell_all_rule(regression_data, regressionResult, sellIndiaAvg, None) 
            if(len(regression_low['filter']) > 3):
                db.ws_sellAllReg.insert_one(json.loads(json.dumps(regression_low)))                               
        all_withoutml(regression_data, regressionResult, None)
        db.ws_lowAll.insert_one(json.loads(json.dumps(regression_low))) 
        
def result_data_cla(regression_high, regression_low, scrip):
    regression_data = regression_high
    if(regression_data is not None):
        regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_low['mlpValue_reg'], 
                                            regression_low['kNeighboursValue_reg'],
                                            regression_low['mlpValue_cla'], 
                                            regression_low['kNeighboursValue_cla'],
                                            )
        buy_pattern_without_mlalgo(regression_data, regressionResult, None, None)
        oi = buy_oi_candidate(regression_data, regressionResult, False, None)
        if oi:
            all_withoutml(regression_data, regressionResult, None)
        buyIndiaAvg, result = buy_pattern_from_history(regression_data, regressionResult, None)
        if buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvg, None):
            buy_year_high(regression_data, regressionResult, False, None)
            buy_year_low(regression_data, regressionResult, False, None, None)
            buy_final(regression_data, regressionResult, False, None, None)
            buy_up_trend(regression_data, regressionResult, False, None)
            buy_down_trend(regression_data, regressionResult, False, None)
            buy_oi(regression_data, regressionResult, False, None)
            buy_high_indicators(regression_data, regressionResult, False, None)
            buy_pattern(regression_data, regressionResult, False, None, None)
            buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvg, None)
            if(len(regression_high['filter']) > 3):
                db.ws_buyAllCla.insert_one(json.loads(json.dumps(regression_high))) 
                
    regression_data = regression_low
    if(regression_data is not None):
        regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_high['mlpValue_reg'], 
                                            regression_high['kNeighboursValue_reg'],
                                            regression_high['mlpValue_cla'], 
                                            regression_high['kNeighboursValue_cla']
                                            )
        sell_pattern_without_mlalgo(regression_data, regressionResult, None, None)
        oi = sell_oi_candidate(regression_data, regressionResult, False, None)
        if oi:
            all_withoutml(regression_data, regressionResult, None) 
        sellIndiaAvg, result = sell_pattern_from_history(regression_data, regressionResult, None)
        if sell_all_rule_classifier(regression_data, regressionResult, sellIndiaAvg, None):
            sell_year_high(regression_data, regressionResult, False, None, None)
            sell_year_low(regression_data, regressionResult, False, None)
            sell_final(regression_data, regressionResult, False, None, None)
            sell_up_trend(regression_data, regressionResult, False, None)
            #sell_down_trend(regression_data, regressionResult, None)
            sell_oi(regression_data, regressionResult, False, None)
            sell_high_indicators(regression_data, regressionResult, False, None)
            sell_pattern(regression_data, regressionResult, False, None, None)
            sell_all_rule_classifier(regression_data, regressionResult, sellIndiaAvg, None)
            if(len(regression_low['filter']) > 3):
                db.ws_sellAllCla.insert_one(json.loads(json.dumps(regression_low)))                                
                                             
def calculateParallel(threads=2, futures=None):
    pool = ThreadPool(threads)
    scrips = []
    for data in db.scrip.find({'futures':futures}):
        scrips.append(data['scrip'].replace('&','').replace('-','_'))
    scrips.sort()
    pool.map(result_data, scrips)
    pool.map(result_data_reg, scrips)
    pool.map(result_data_cla, scrips)
                      
if __name__ == "__main__":
    if not os.path.exists(directory):
        os.makedirs(directory)
    calculateParallel(1, sys.argv[1])
    connection.close()
    saveReports(sys.argv[1])