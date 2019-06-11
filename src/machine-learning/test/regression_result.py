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
from util.util import buy_pattern_from_history, buy_all_rule, buy_other_indicator
from util.util import sell_pattern_from_history, sell_all_rule, sell_other_indicator
from util.util import buy_pattern_without_mlalgo, sell_pattern_without_mlalgo, buy_oi, sell_oi, all_withoutml
from util.util import buy_oi_candidate, sell_oi_candidate
from util.util import buy_all_filter, buy_all_common, sell_all_filter, sell_all_common
from util.util import buy_all_rule_classifier, sell_all_rule_classifier
from util.util import is_algo_buy_classifier, is_algo_sell_classifier
from util.util import sell_oi_negative, sell_day_high, buy_oi_negative, buy_day_low



connection = MongoClient('localhost', 27017)
db = connection.nsehistnew

buyPatternsDict=scrip_patterns_to_dict('../../data-import/nselist/patterns-buy.csv')
sellPatternsDict=scrip_patterns_to_dict('../../data-import/nselist/patterns-sell.csv')

directory = '../../output/final'
logname = '../../output/final' + '/all-result' + time.strftime("%d%m%y-%H%M%S")
      

def result_data(regression_high, regression_low, scrip):
    if(regression_high is None or regression_low is None):
        return
    
    buyIndiaAvgReg, result = buy_pattern_from_history(regression_high, None)
    sellIndiaAvgReg, result = sell_pattern_from_history(regression_low, None)
    
    regression_data = regression_high
    regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_low['mlpValue_reg'], 
                                            regression_low['kNeighboursValue_reg'],
                                            regression_low['mlpValue_cla'], 
                                            regression_low['kNeighboursValue_cla'],
                                            )
    buy_pattern_without_mlalgo(regression_data, regressionResult)
    if (buy_all_rule(regression_data, regressionResult, buyIndiaAvgReg, None)
        and buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvgReg, None)
        ):
        buy_other_indicator(regression_data, regressionResult, True, None)
        buy_other_indicator(regression_data, regressionResult, False, None)
        buy_filter_accuracy(regression_data, regressionResult, False, None)
        buy_all_common(regression_data, regressionResult, True, None)
    if (sell_all_rule(regression_data, regressionResult, buyIndiaAvgReg, None)
        and sell_all_rule_classifier(regression_data, regressionResult, buyIndiaAvgReg, None)
        ):
        sell_other_indicator(regression_data, regressionResult, True, None)
        sell_other_indicator(regression_data, regressionResult, False, None)
        sell_filter_accuracy(regression_data, regressionResult, False, None)
        sell_all_common(regression_data, regressionResult, True, None)
    if (buy_all_rule(regression_data, regressionResult, buyIndiaAvgReg, None)
        and buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvgReg, None)
        ):
        db.ws_highBothBuy.insert_one(json.loads(json.dumps(regression_high)))
        
    if (sell_all_rule(regression_data, regressionResult, buyIndiaAvgReg, None)
        and sell_all_rule_classifier(regression_data, regressionResult, buyIndiaAvgReg, None)
        ):
        db.ws_highBothSell.insert_one(json.loads(json.dumps(regression_high)))
    
    regression_data = regression_low
    regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_high['mlpValue_reg'], 
                                            regression_high['kNeighboursValue_reg'],
                                            regression_high['mlpValue_cla'], 
                                            regression_high['kNeighboursValue_cla']
                                            )
    sell_pattern_without_mlalgo(regression_data, regressionResult)
    if (sell_all_rule(regression_data, regressionResult, sellIndiaAvgReg, None)
        and sell_all_rule_classifier(regression_data, regressionResult, sellIndiaAvgReg, None)
        ):
        sell_other_indicator(regression_data, regressionResult, True, None)
        sell_other_indicator(regression_data, regressionResult, False, None)
        sell_filter_accuracy(regression_data, regressionResult, False, None)
        sell_all_common(regression_data, regressionResult, True, None)
    if (buy_all_rule(regression_data, regressionResult, buyIndiaAvgReg, None)
        and buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvgReg, None)
        ):
        buy_other_indicator(regression_data, regressionResult, True, None)
        buy_other_indicator(regression_data, regressionResult, False, None)
        buy_filter_accuracy(regression_data, regressionResult, False, None) 
        buy_all_common(regression_data, regressionResult, True, None)
    
    if (sell_all_rule(regression_data, regressionResult, sellIndiaAvgReg, None)
        and sell_all_rule_classifier(regression_data, regressionResult, sellIndiaAvgReg, None)
        ):
        db.ws_lowBothSell.insert_one(json.loads(json.dumps(regression_low)))   
    if (buy_all_rule(regression_data, regressionResult, buyIndiaAvgReg, None)
        and buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvgReg, None)
        ):
        db.ws_lowBothBuy.insert_one(json.loads(json.dumps(regression_low)))
                                    
def result_data_reg(regression_high, regression_low, scrip):
    if(regression_high is None or regression_low is None):
        return
    
    regression_data = regression_high
    if(regression_data is not None):
        buyIndiaAvg, result = buy_pattern_from_history(regression_data, None)
        regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_low['mlpValue_reg'], 
                                            regression_low['kNeighboursValue_reg'],
                                            regression_low['mlpValue_cla'], 
                                            regression_low['kNeighboursValue_cla'],
                                            )
        buy_pattern_without_mlalgo(regression_data, regressionResult)
        buy_other_indicator(regression_data, regressionResult, True, None)
        buy_all_rule(regression_data, regressionResult, buyIndiaAvg, None)
        db.ws_high.insert_one(json.loads(json.dumps(regression_high)))
                
    regression_data = regression_low
    if(regression_data is not None):
        sellIndiaAvg, result = sell_pattern_from_history(regression_data, None)
        regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_high['mlpValue_reg'], 
                                            regression_high['kNeighboursValue_reg'],
                                            regression_high['mlpValue_cla'], 
                                            regression_high['kNeighboursValue_cla']
                                            )
        sell_pattern_without_mlalgo(regression_data, regressionResult)
        sell_other_indicator(regression_data, regressionResult, True, None)
        sell_all_rule(regression_data, regressionResult, sellIndiaAvg, None) 
        db.ws_low.insert_one(json.loads(json.dumps(regression_low)))
        
def result_data_cla(regression_high, regression_low, scrip):
    if(regression_high is None or regression_low is None):
        return
    
    regression_data = regression_high
    if(regression_data is not None):
        buyIndiaAvg, result = buy_pattern_from_history(regression_data, None)
        regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_low['mlpValue_reg'], 
                                            regression_low['kNeighboursValue_reg'],
                                            regression_low['mlpValue_cla'], 
                                            regression_low['kNeighboursValue_cla'],
                                            )
        buy_pattern_without_mlalgo(regression_data, regressionResult)
        if buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvg, None):
            buy_other_indicator(regression_data, regressionResult, True, None)
            db.ws_highBuyCla.insert_one(json.loads(json.dumps(regression_high)))
        
                
    regression_data = regression_low
    if(regression_data is not None):
        sellIndiaAvg, result = sell_pattern_from_history(regression_data, None)
        regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_high['mlpValue_reg'], 
                                            regression_high['kNeighboursValue_reg'],
                                            regression_high['mlpValue_cla'], 
                                            regression_high['kNeighboursValue_cla']
                                            )
        sell_pattern_without_mlalgo(regression_data, regressionResult)
        if sell_all_rule_classifier(regression_data, regressionResult, sellIndiaAvg, None):
            sell_other_indicator(regression_data, regressionResult, True, None)
            db.ws_lowSellCla.insert_one(json.loads(json.dumps(regression_low)))
                                         

def calculateParallel(threads=2, futures=None):
    pool = ThreadPool(threads)
    scrips = []
    for data in db.scrip.find({'futures':futures}):
        scrips.append(data['scrip'])
    scrips.sort()
    pool.map(result_data, scrips)
    pool.map(result_data_cla, scrips)
    pool.map(result_data_reg, scrips)
                      
if __name__ == "__main__":
    if not os.path.exists(directory):
        os.makedirs(directory)
    calculateParallel(1, sys.argv[1])
    connection.close()
    saveReports(sys.argv[1])