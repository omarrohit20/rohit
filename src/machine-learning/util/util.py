import csv
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import Color, PatternFill, Font, Border
from pymongo import MongoClient
from multiprocessing.dummy import Pool as ThreadPool

import quandl, math, time
from nsepy import get_history
from nsepy.derivatives import get_expiry_date
from datetime import date
import datetime   
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np

connection = MongoClient('localhost',27017)
db = connection.Nsedata

soft=False
NIFTY_HIGH = False
NIFTY_LOW = False
BUY_VERY_LESS_DATA=True
SELL_VERY_LESS_DATA=True
MARKET_IN_UPTREND=False
MARKET_IN_DOWNTREND=False
TEST = False

buyMLP = 0.1
buyMLP_MIN = 0
buyKN = 0.1
buyKN_MIN = 0
sellMLP = -0.1
sellMLP_MIN = 0
sellKN = -0.1
sellKN_MIN = 0

def add_in_csv(regression_data, regressionResult, ws=None, filter=None, filter1=None, filter2=None, filter3=None, filter4=None):
    if(TEST != True):
        if(is_algo_buy(regression_data) and (filter is not None)):
            if '[MLBuy]' not in regression_data['filter']:
                regression_data['filter'] = regression_data['filter'] + '[MLBuy]' + ':'
        if(is_algo_sell(regression_data) and (filter is not None)):
            if '[MLSell]' not in regression_data['filter']:
                regression_data['filter'] = regression_data['filter'] + '[MLSell]' + ':'
        if ((filter is not None) and (filter not in regression_data['filter'])):
            regression_data['filter'] = regression_data['filter'] + filter + ','
            if ('P@[' in str(regression_data['sellIndia'])) and (('buy' or 'Buy') in regression_data['filter']):
                if '***SELLPATTERN***' not in regression_data['filter']:
                   regression_data['filter'] = regression_data['filter'] + '***SELLPATTERN***' + ','
            if ('P@[' in str(regression_data['buyIndia'])) and (('sell' or 'Sell') in regression_data['filter']):
                if '***BUYPATTERN***' not in regression_data['filter']:
                   regression_data['filter'] = regression_data['filter'] + '***BUYPATTERN***' + ','
        if ((filter1 is not None) and (filter1 not in regression_data['filter1'])):
            regression_data['filter1'] = regression_data['filter1'] + filter1 + ','
        if ((filter2 is not None) and (filter2 not in regression_data['filter2'])):
            regression_data['filter2'] = regression_data['filter2'] + filter2 + ',' 
        if ((filter3 is not None) and (filter3 not in regression_data['filter3'])):
            regression_data['filter3'] = regression_data['filter3'] + filter3 + ','
        if ((filter4 is not None) and (filter4 not in regression_data['filter4'])):
            regression_data['filter4'] = regression_data['filter4'] + filter4 + ','   
        tempRegressionResult = regressionResult.copy() 
        tempRegressionResult.append(regression_data['filter'])
        tempRegressionResult.append(regression_data['filter1'])
        tempRegressionResult.append(regression_data['filter2'])
        tempRegressionResult.append(regression_data['filter3'])
        tempRegressionResult.append(regression_data['filter4'])
        ws.append(tempRegressionResult) if (ws is not None) else False
        if(db.resultScripFutures.find_one({'scrip':regression_data['scrip']}) is None):
            db.resultScripFutures.insert_one({
                "scrip": regression_data['scrip'],
                "date": regression_data['date']
                })
    else:
        if ((filter is not None) and (filter not in regression_data['filterTest'])):
            regression_data['filterTest'] = regression_data['filterTest'] + filter + ','
            if ('P@[' in str(regression_data['sellIndia'])) and (('buy' or 'Buy') in regression_data['filterTest']):
                if '***SELLPATTERN***' not in regression_data['filterTest']:
                   regression_data['filterTest'] = regression_data['filterTest'] + '***SELLPATTERN***' + ','
            if ('P@[' in str(regression_data['buyIndia'])) and (('sell' or 'Sell') in regression_data['filterTest']):
                if '***BUYPATTERN***' not in regression_data['filterTest']:
                   regression_data['filterTest'] = regression_data['filterTest'] + '***BUYPATTERN***' + ','
        if ((filter1 is not None) and (filter1 not in regression_data['filter1'])):
            regression_data['filter1'] = regression_data['filter1'] + filter1 + ','
        if ((filter2 is not None) and (filter2 not in regression_data['filter2'])):
            regression_data['filter2'] = regression_data['filter2'] + filter2 + ',' 
        if ((filter3 is not None) and (filter3 not in regression_data['filter3'])):
            regression_data['filter3'] = regression_data['filter3'] + filter3 + ','
        if ((filter4 is not None) and (filter4 not in regression_data['filter4'])):
            regression_data['filter4'] = regression_data['filter4'] + filter4 + ','   
        
def add_in_csv_hist_pattern(regression_data, regressionResult, ws, filter, avg, count):
    if(TEST != True):
        if ((filter is not None) and (filter not in regression_data['filter'])):
            regression_data['filter'] = regression_data['filter'] + filter + ','
        tempRegressionResult = regressionResult.copy() 
        tempRegressionResult.append(regression_data['filter'])
        tempRegressionResult.append(avg)
        tempRegressionResult.append(count)
        ws.append(tempRegressionResult) if (ws is not None) else False
    else:
        if ((filter is not None) and (filter not in regression_data['filterTest'])):
            regression_data['filterTest'] = regression_data['filterTest'] + filter + ','
        tempRegressionResult = regressionResult.copy() 
        tempRegressionResult.append(regression_data['filterTest'])
        tempRegressionResult.append(avg)
        tempRegressionResult.append(count)
        ws.append(tempRegressionResult) if (ws is not None) else False

def is_algo_buy(regression_data):
    if TEST:
        return True
    if((regression_data['mlpValue_reg'] >= -1) and (regression_data['kNeighboursValue_reg'] >= -1)
        and (regression_data['mlpValue_reg_other'] >= -1) and (regression_data['kNeighboursValue_reg_other'] >= -1)
        and ((regression_data['PCT_day_change'] > 1 
                and high_tail_pct(regression_data) < 2 
                and ('P@[' not in str(regression_data['sellIndia']))
                )
             or (low_tail_pct(regression_data) > 1.5 
                and (high_tail_pct(regression_data) < low_tail_pct(regression_data))
                )
             or (regression_data['PCT_day_change'] < -2
                and regression_data['forecast_day_PCT_change'] > 0.3
                )
            )
        #and (BUY_VERY_LESS_DATA or regression_data['PCT_change'] > -1)
        #and (BUY_VERY_LESS_DATA or ((regression_data['PCT_day_change_pre1'] < 0) or (regression_data['forecast_day_VOL_change'] > 0))) #Uncomment1 If very less data
        #and (BUY_VERY_LESS_DATA or (regression_data['high']-regression_data['bar_high']) < (regression_data['bar_high']-regression_data['bar_low']))
        #and buyIndiaAvg >= -.70
        and ((last_7_day_all_up(regression_data) == False) or (regression_data['forecast_day_PCT10_change'] < 10))
        and (MARKET_IN_UPTREND or (last_4_day_all_up(regression_data) == False)) #Uncomment0 If very less data
        and breakout_or_no_consolidation(regression_data) == True
        and regression_data['close'] > 50
        ):
#         if((0.5 < regression_data['PCT_day_change'] < 1.5) and (0.5 < regression_data['PCT_change'] < 1.5)):
#             return False
#         if((1 < regression_data['PCT_day_change'] < 2) and (0 < regression_data['PCT_change'] < 2)):
#             return False
#         if((1 < regression_data['PCT_change'] < 2) and (0 < regression_data['PCT_day_change'] < 2)):
#             return False
        if((regression_data['mlpValue_reg'] > buyMLP and regression_data['kNeighboursValue_reg'] >= buyKN_MIN) 
            or (regression_data['mlpValue_reg'] >= buyMLP_MIN and regression_data['kNeighboursValue_reg'] > buyKN)
            or (regression_data['mlpValue_reg'] > 0.5 and regression_data['kNeighboursValue_reg'] > 0.5)
            or ((regression_data['mlpValue_reg'] + regression_data['kNeighboursValue_reg'] + regression_data['mlpValue_reg_other'] + regression_data['kNeighboursValue_reg_other']) > 4)
            ):
            if((0 < regression_data['PCT_day_change'] < 5) and (regression_data['mlpValue_reg_other'] >= 0 or regression_data['kNeighboursValue_reg_other'] >= 0)):
                return True
            elif(regression_data['PCT_day_change'] <= 0 or regression_data['PCT_day_change'] >=5):
                return True
    return False   
    
def is_algo_sell(regression_data):
    if TEST:
        return True
    if((regression_data['mlpValue_reg'] <= 1) and (regression_data['kNeighboursValue_reg'] <= 1)
        and (regression_data['mlpValue_reg_other'] <= 1) and (regression_data['kNeighboursValue_reg_other'] <= 1)
        and ((regression_data['PCT_day_change'] < -1 
                and low_tail_pct(regression_data) < 2
                and ('P@[' not in str(regression_data['buyIndia']))
                ) 
             or (high_tail_pct(regression_data) > 1.5 
                and (low_tail_pct(regression_data) < high_tail_pct(regression_data))
                )
             or (regression_data['PCT_day_change'] > 2
                and regression_data['forecast_day_PCT_change'] < -0.3
                )
            )
        #and (SELL_VERY_LESS_DATA or regression_data['PCT_change'] < 1)
        #and (SELL_VERY_LESS_DATA or ((regression_data['PCT_day_change_pre1'] > 0) or (regression_data['forecast_day_VOL_change'] > 0))) #Uncomment1 If very less data
        #and (SELL_VERY_LESS_DATA or (regression_data['bar_low']-regression_data['low']) < (regression_data['bar_high']-regression_data['bar_low']))
        #and sellIndiaAvg <= 0.70
        and ((last_7_day_all_down(regression_data) == False) or (regression_data['forecast_day_PCT10_change'] > -10))
        and (MARKET_IN_DOWNTREND or (last_4_day_all_down(regression_data) == False)) #Uncomment0 If very less data
        and breakout_or_no_consolidation(regression_data) == True
        and regression_data['close'] > 50
        ):
#         if((-1.5 < regression_data['PCT_day_change'] < -0.5) and (-1.5 < regression_data['PCT_change'] < -0.5)):
#             return False
#         if((-2 < regression_data['PCT_day_change'] < -1) and (-2 < regression_data['PCT_change'] < 0)):
#             return False
#         if((-2 < regression_data['PCT_change'] < -1) and (-2 < regression_data['PCT_day_change'] < 0)):
#             return False
        if((regression_data['mlpValue_reg'] < sellMLP and regression_data['kNeighboursValue_reg'] <= sellKN_MIN)
            or (regression_data['mlpValue_reg'] <= sellMLP_MIN and regression_data['kNeighboursValue_reg'] < sellKN)
            or (regression_data['mlpValue_reg'] < -0.5 and regression_data['kNeighboursValue_reg'] < -0.5)
            or ((regression_data['mlpValue_reg'] + regression_data['kNeighboursValue_reg'] + regression_data['mlpValue_reg_other'] + regression_data['kNeighboursValue_reg_other']) < -4)
            ):
            if((-5 < regression_data['PCT_day_change'] < 0) and (regression_data['mlpValue_reg_other'] <= 0 or regression_data['kNeighboursValue_reg_other'] <= 0)):
                return True
            elif(regression_data['PCT_day_change'] >= 0 or regression_data['PCT_day_change'] <=-5):
                return True
    return False

def is_algo_buy_classifier(regression_data):
    if((regression_data['mlpValue_cla'] >= 0) and (regression_data['kNeighboursValue_cla'] >= 0)
        and ((regression_data['mlpValue_cla_other'] >= 0) and (regression_data['kNeighboursValue_cla_other'] >= 0))
        and ((regression_data['mlpValue_cla_other'] >= 1) or (regression_data['kNeighboursValue_cla_other'] >= 1))
        and ((regression_data['PCT_day_change'] > 1 
                and high_tail_pct(regression_data) < 2 
                and ('P@[' not in str(regression_data['sellIndia']))
                )
             or (low_tail_pct(regression_data) > 1.5 
                and (high_tail_pct(regression_data) < low_tail_pct(regression_data))
                )
             or (regression_data['PCT_day_change'] < -2
                and regression_data['forecast_day_PCT_change'] > 0.3
                )
            )
        #and (BUY_VERY_LESS_DATA or regression_data['PCT_change'] > -1)
        #and (BUY_VERY_LESS_DATA or ((regression_data['PCT_day_change_pre1'] < 0) or (regression_data['forecast_day_VOL_change'] > 0))) #Uncomment1 If very less data
        #and (BUY_VERY_LESS_DATA or (regression_data['high']-regression_data['bar_high']) < (regression_data['bar_high']-regression_data['bar_low']))
        #and buyIndiaAvg >= -.70
        and ((last_7_day_all_up(regression_data) == False) or (regression_data['forecast_day_PCT10_change'] < 10))
        and (MARKET_IN_UPTREND or (last_4_day_all_up(regression_data) == False)) #Uncomment0 If very less data
        and breakout_or_no_consolidation(regression_data) == True
        and regression_data['close'] > 50
        ):
#         if((0.5 < regression_data['PCT_day_change'] < 1.5) and (0.5 < regression_data['PCT_change'] < 1.5)):
#             return False
#         if((1 < regression_data['PCT_day_change'] < 2) and (0 < regression_data['PCT_change'] < 2)):
#             return False
#         if((1 < regression_data['PCT_change'] < 2) and (0 < regression_data['PCT_day_change'] < 2)):
#             return False
        if((regression_data['mlpValue_cla'] >= buyMLP and regression_data['kNeighboursValue_cla'] >= buyKN_MIN) 
            or (regression_data['mlpValue_cla'] >= buyMLP_MIN and regression_data['kNeighboursValue_cla'] >= buyKN)
            or (regression_data['mlpValue_cla'] >= 0.5 and regression_data['kNeighboursValue_cla'] >= 0.5)
            or ((regression_data['mlpValue_cla'] + regression_data['kNeighboursValue_cla'] + regression_data['mlpValue_cla_other'] + regression_data['kNeighboursValue_cla_other']) > 6)
            ):
            if((0 < regression_data['PCT_day_change'] < 5) and (regression_data['mlpValue_cla_other'] >= 0 or regression_data['kNeighboursValue_cla_other'] >= 0)):
                return True
            elif(regression_data['PCT_day_change'] <= 0 or regression_data['PCT_day_change'] >=5):
                return True
    return False   
    
def is_algo_sell_classifier(regression_data):
    if((regression_data['mlpValue_cla'] <= 0) and (regression_data['kNeighboursValue_cla'] <= 0)
        and ((regression_data['mlpValue_cla_other'] <= 0) and (regression_data['kNeighboursValue_cla_other'] <= 0))
        and ((regression_data['mlpValue_cla_other'] <= -1) or (regression_data['kNeighboursValue_cla_other'] <= -1))
        and ((regression_data['PCT_day_change'] < -1 
                and low_tail_pct(regression_data) < 2
                and ('P@[' not in str(regression_data['buyIndia']))
                ) 
             or (high_tail_pct(regression_data) > 1.5 
                and (low_tail_pct(regression_data) < high_tail_pct(regression_data))
                )
             or (regression_data['PCT_day_change'] > 2
                and regression_data['forecast_day_PCT_change'] < -0.3
                )
            )
        #and (SELL_VERY_LESS_DATA or regression_data['PCT_change'] < 1)
        #and (SELL_VERY_LESS_DATA or ((regression_data['PCT_day_change_pre1'] > 0) or (regression_data['forecast_day_VOL_change'] > 0))) #Uncomment1 If very less data
        #and (SELL_VERY_LESS_DATA or (regression_data['bar_low']-regression_data['low']) < (regression_data['bar_high']-regression_data['bar_low']))
        #and sellIndiaAvg <= 0.70
        and ((last_7_day_all_down(regression_data) == False) or (regression_data['forecast_day_PCT10_change'] > -10))
        and (MARKET_IN_DOWNTREND or (last_4_day_all_down(regression_data) == False)) #Uncomment0 If very less data
        and breakout_or_no_consolidation(regression_data) == True
        and regression_data['close'] > 50
        ):
#         if((-1.5 < regression_data['PCT_day_change'] < -0.5) and (-1.5 < regression_data['PCT_change'] < -0.5)):
#             return False
#         if((-2 < regression_data['PCT_day_change'] < -1) and (-2 < regression_data['PCT_change'] < 0)):
#             return False
#         if((-2 < regression_data['PCT_change'] < -1) and (-2 < regression_data['PCT_day_change'] < 0)):
#             return False
        if((regression_data['mlpValue_cla'] <= sellMLP and regression_data['kNeighboursValue_cla'] <= sellKN_MIN)
            or (regression_data['mlpValue_cla'] <= sellMLP_MIN and regression_data['kNeighboursValue_cla'] <= sellKN)
            or (regression_data['mlpValue_cla'] <= -0.5 and regression_data['kNeighboursValue_cla'] <= -0.5)
            or ((regression_data['mlpValue_cla'] + regression_data['kNeighboursValue_cla'] + regression_data['mlpValue_cla_other'] + regression_data['kNeighboursValue_cla_other']) < -6)
            ):
            if((-5 < regression_data['PCT_day_change'] < 0) and (regression_data['mlpValue_cla_other'] <= 0 or regression_data['kNeighboursValue_cla_other'] <= 0)):
                return True
            elif(regression_data['PCT_day_change'] >= 0 or regression_data['PCT_day_change'] <=-5):
                return True
    return False

def get_reg_or_cla(regression_data, reg=True):
    if(TEST != True):
        if reg:
            mlpValue = regression_data['mlpValue_reg']
            kNeighboursValue = regression_data['kNeighboursValue_reg']
            return mlpValue, kNeighboursValue
        else:
            mlpValue = regression_data['mlpValue_cla']
            kNeighboursValue = regression_data['kNeighboursValue_cla']
            return mlpValue, kNeighboursValue
    else:
        return 0, 0
    
def get_reg_or_cla_other(regression_data, reg=True):
    if(TEST != True):
        if reg:
            mlpValue_other = regression_data['mlpValue_reg_other']
            kNeighboursValue_other = regression_data['kNeighboursValue_reg_other']
            return mlpValue_other, kNeighboursValue_other
        else:
            mlpValue_other = regression_data['mlpValue_cla_other']
            kNeighboursValue_other = regression_data['kNeighboursValue_cla_other']
            return mlpValue_other, kNeighboursValue_other
    else:
        return 0, 0

def getScore(vol_change, pct_change):
    try:
        return float(vol_change)/float(pct_change) 
    except ZeroDivisionError:
        return 0

def all_day_pct_change_negative(regression_data):
    if(regression_data['forecast_day_PCT_change'] < 0
        and regression_data['forecast_day_PCT2_change'] <= 0
        and regression_data['forecast_day_PCT3_change'] <= 0
        and regression_data['forecast_day_PCT4_change'] <= 0
        and regression_data['forecast_day_PCT5_change'] <= 0
        and regression_data['forecast_day_PCT7_change'] <= 0
        and regression_data['forecast_day_PCT10_change'] <= 0):
        return True;
    else:
        return False;
    
def all_day_pct_change_positive(regression_data):
    if(regression_data['forecast_day_PCT_change'] > 0
        and regression_data['forecast_day_PCT2_change'] > -0.5
        and regression_data['forecast_day_PCT3_change'] > -0.5
        and regression_data['forecast_day_PCT4_change'] > -0.5
        and regression_data['forecast_day_PCT5_change'] > -0.5
        and regression_data['forecast_day_PCT7_change'] > -0.5
        and regression_data['forecast_day_PCT10_change'] > -0.5):
        return True;
    else:
        return False;

def all_day_pct_change_negative_except_today(regression_data):
    if(regression_data['forecast_day_PCT2_change'] <= 0
        and regression_data['forecast_day_PCT3_change'] <= 0
        and regression_data['forecast_day_PCT4_change'] <= 0
        and regression_data['forecast_day_PCT5_change'] <= 0
        and regression_data['forecast_day_PCT7_change'] <= 0
        and regression_data['forecast_day_PCT10_change'] <= 0):
        return True;
    else:
        return False
    
def all_day_pct_change_positive_except_today(regression_data):
    if(regression_data['forecast_day_PCT2_change'] >= 0
        and regression_data['forecast_day_PCT3_change'] >= 0
        and regression_data['forecast_day_PCT4_change'] >= 0
        and regression_data['forecast_day_PCT5_change'] >= 0
        and regression_data['forecast_day_PCT7_change'] >= 0
        and regression_data['forecast_day_PCT10_change'] >= 0):
        return True;
    else:
        return False; 
     
def pct_change_negative_trend(regression_data):
    if (regression_data['forecast_day_PCT_change'] < 0
        and regression_data['forecast_day_PCT2_change'] < 0
        and regression_data['forecast_day_PCT3_change'] < 0):
        pct_change_list = [regression_data['forecast_day_PCT_change'],
                           regression_data['forecast_day_PCT2_change'],
                           regression_data['forecast_day_PCT3_change'],
                           regression_data['forecast_day_PCT4_change'],
                           regression_data['forecast_day_PCT5_change'],
                           regression_data['forecast_day_PCT7_change'],
                           regression_data['forecast_day_PCT10_change']
                           ]
        trend_change = False
        trend = True
        for pct_change in pct_change_list:
            if pct_change < 0 and trend_change == False:
                trend = True
            elif pct_change > 0 and trend_change == True: 
                trend = True    
            elif pct_change > 0 and trend_change == False:
                trend_change = True
                trend = True
            else:
                trend = False
        return trend            
    return False           
    
def pct_change_positive_trend(regression_data):
    if (regression_data['forecast_day_PCT_change'] > 0
        and regression_data['forecast_day_PCT2_change'] > 0
        and regression_data['forecast_day_PCT3_change'] > 0):
        pct_change_list = [regression_data['forecast_day_PCT_change'],
                           regression_data['forecast_day_PCT2_change'],
                           regression_data['forecast_day_PCT3_change'],
                           regression_data['forecast_day_PCT4_change'],
                           regression_data['forecast_day_PCT5_change'],
                           regression_data['forecast_day_PCT7_change'],
                           regression_data['forecast_day_PCT10_change']
                           ]
        trend_change = False
        trend = True
        for pct_change in pct_change_list:
            if pct_change > 0 and trend_change == False:
                trend = True
            elif pct_change < 0 and trend_change == True: 
                trend = True    
            elif pct_change < 0 and trend_change == False:
                trend_change = True
                trend = True
            else:
                trend = False
        return trend
    return False       

def preDayPctChangeUp_orVolHigh(regression_data):
    if(regression_data['PCT_day_change_pre1'] > 0 
       or (regression_data['volume'] > regression_data['volume_pre2'] and regression_data['volume'] > regression_data['volume_pre3'])
    ):
        return True
    else:
        return False
    
def preDayPctChangeDown_orVolHigh(regression_data):
    if(regression_data['PCT_day_change_pre1'] < 0 
       or (regression_data['volume'] > regression_data['volume_pre2'] and regression_data['volume'] > regression_data['volume_pre3'])
    ):
        return True
    else:
        return False    

def all_between_five_and_up_score(regression_data):
    if(-5 < regression_data['forecast_day_PCT_change'] < 5
        and -5 < regression_data['forecast_day_PCT2_change'] < 5
        and -5 < regression_data['forecast_day_PCT3_change'] < 5
        and -5 < regression_data['forecast_day_PCT4_change'] < 5
        and -5 < regression_data['forecast_day_PCT5_change'] < 5
        and -5 < regression_data['forecast_day_PCT7_change'] < 5
        and -6 < regression_data['forecast_day_PCT10_change'] < 6
        and str(regression_data['score']) == '10'
        and regression_data['trend'] != 'down'
        ):
        return True
    else:
        return False

def all_between_five_and_down_score(regression_data):
    if(-5 < regression_data['forecast_day_PCT_change'] < 5
        and -5 < regression_data['forecast_day_PCT2_change'] < 5
        and -5 < regression_data['forecast_day_PCT3_change'] < 5
        and -5 < regression_data['forecast_day_PCT4_change'] < 5
        and -5 < regression_data['forecast_day_PCT5_change'] < 5
        and -5 < regression_data['forecast_day_PCT7_change'] < 5
        and -6 < regression_data['forecast_day_PCT10_change'] < 6
        and str(regression_data['score']) == '0-1'
        and regression_data['trend'] != 'up'
        ):
        return True
    else:
        return False        

def all_between_zero_and_five_up_score(regression_data):
    if(0 < regression_data['forecast_day_PCT_change'] < 5
        and 0 < regression_data['forecast_day_PCT2_change'] < 5
        and 0 < regression_data['forecast_day_PCT3_change'] < 5
        and 0 < regression_data['forecast_day_PCT4_change'] < 5
        and 0 < regression_data['forecast_day_PCT5_change'] < 5
        and 0 < regression_data['forecast_day_PCT7_change'] < 5
        and 0 < regression_data['forecast_day_PCT10_change'] < 6
        and str(regression_data['score']) == '10'
        and regression_data['trend'] != 'down'
        ):
        return True
    else:
        return False

def all_between_zero_and_five_down_score(regression_data):
    if(-5 < regression_data['forecast_day_PCT_change'] < 0
        and -5 < regression_data['forecast_day_PCT2_change'] < 0
        and -5 < regression_data['forecast_day_PCT3_change'] < 0
        and -5 < regression_data['forecast_day_PCT4_change'] < 0
        and -5 < regression_data['forecast_day_PCT5_change'] < 0
        and -5 < regression_data['forecast_day_PCT7_change'] < 0
        and -6 < regression_data['forecast_day_PCT10_change'] < 0
        and str(regression_data['score']) == '0-1'
        and regression_data['trend'] != 'up'
        ):
        return True
    else:
        return False           

def abs_yearHigh_more_than_yearLow(regression_data):
    if(abs(regression_data['yearHighChange']) > abs(regression_data['yearLowChange'])):
        return True;
    else:
        return False;

def abs_yearHigh_less_than_yearLow(regression_data):
    if(abs(regression_data['yearHighChange']) < abs(regression_data['yearLowChange'])):
        return True;
    else:
        return False;

def abs_month3High_more_than_month3Low(regression_data):
    if(abs(regression_data['month3HighChange']) > abs(regression_data['month3LowChange'])):
        return True;
    else:
        return False;

def abs_month3High_less_than_month3Low(regression_data):
    if(abs(regression_data['month3HighChange']) < abs(regression_data['month3LowChange'])):
        return True;
    else:
        return False;

    
def last_5_day_all_up_except_today(regression_data):
    if(regression_data['PCT_day_change_pre1'] > 0
        and regression_data['PCT_day_change_pre2'] > 0
        and regression_data['PCT_day_change_pre3'] > 0
        and regression_data['PCT_day_change_pre4'] > 0): 
        return True
    else:
        return False 
    
def last_5_day_all_down_except_today(regression_data):
    if(regression_data['PCT_day_change_pre1'] < 0
        and regression_data['PCT_day_change_pre2'] < 0
        and regression_data['PCT_day_change_pre3'] < 0
        and regression_data['PCT_day_change_pre4'] < 0): 
        return True
    else:
        return False      

def last_4_day_all_up(regression_data):
    if(regression_data['PCT_day_change'] > 0
        and regression_data['PCT_day_change_pre1'] > 0
        and regression_data['PCT_day_change_pre2'] > 0
        and regression_data['PCT_day_change_pre3'] > 0
        #and regression_data['PCT_day_change_pre4'] > 0
        ): 
        return True
    else:
        return False 
    
def last_4_day_all_down(regression_data):
    if(regression_data['PCT_day_change'] < 0
        and regression_data['PCT_day_change_pre1'] < 0
        and regression_data['PCT_day_change_pre2'] < 0
        and regression_data['PCT_day_change_pre3'] < 0
        #and regression_data['PCT_day_change_pre4'] < 0
        ): 
        return True
    else:
        return False      

def last_7_day_all_up(regression_data):
    if(regression_data['PCT_day_change_pre1'] > 0
        and regression_data['PCT_day_change_pre2'] > 0
        and regression_data['PCT_day_change_pre3'] > 0
        and regression_data['PCT_day_change_pre4'] > 0
        and regression_data['PCT_day_change_pre5'] > 0
        and regression_data['PCT_day_change_pre6'] > 0
        and regression_data['PCT_day_change_pre7'] > 0
        ): 
        return True
    else:
        return False 
    
def last_7_day_all_down(regression_data):
    if(regression_data['PCT_day_change_pre1'] < 0
        and regression_data['PCT_day_change_pre2'] < 0
        and regression_data['PCT_day_change_pre3'] < 0
        and regression_data['PCT_day_change_pre4'] < 0
        and regression_data['PCT_day_change_pre5'] < 0
        and regression_data['PCT_day_change_pre6'] < 0
        and regression_data['PCT_day_change_pre7'] < 0
        ): 
        return True
    else:
        return False      

def historical_data_OI(data):
    ardate = np.array([str(x) for x in (np.array(data['data'])[:,3][::-1]).tolist()])
    aroipctchange = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,6][::-1]).tolist()])
    arcontractpctchange = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,7][::-1]).tolist()])
    return ardate, aroipctchange, arcontractpctchange

def high_tail_pct(regression_data):
    if(regression_data['high'] - regression_data['bar_high'] == 0):
        return 0
    else:
        return (((regression_data['high'] - regression_data['bar_high'])/regression_data['bar_high'])*100)
    
def low_tail_pct(regression_data):
    if((regression_data['bar_low'] - regression_data['low']) == 0):
        return 0
    else:
        return (((regression_data['bar_low'] - regression_data['low'])/regression_data['bar_low'])*100)

def is_recent_consolidation(regression_data):
#     if(abs(regression_data['forecast_day_PCT_change']) < 1
#         and abs(regression_data['forecast_day_PCT2_change']) < 1
#         and (abs(regression_data['forecast_day_PCT3_change']) < 1 or abs(regression_data['forecast_day_PCT4_change']) < 1)
#         and abs(regression_data['forecast_day_PCT3_change']) < 2
#         and abs(regression_data['forecast_day_PCT4_change']) < 2
#         #and abs(regression_data['PCT_day_change']) < 1
#         #and abs(regression_data['PCT_day_change_pre1']) < 1
#         ): 
#         return True
    if(abs(regression_data['forecast_day_PCT_change']) < 1.5
        and abs(regression_data['forecast_day_PCT2_change']) < 1.5
        and abs(regression_data['forecast_day_PCT3_change']) < 1.5
        and abs(regression_data['forecast_day_PCT4_change']) < 1.5
        and abs(regression_data['forecast_day_PCT5_change']) < 1.5
        and abs(regression_data['forecast_day_PCT7_change']) < 1.5
        and abs(regression_data['forecast_day_PCT10_change']) < 1.5
        ): 
        return True
    else:
        return False 

def is_short_consolidation_breakout(regression_data):
    if(is_recent_consolidation(regression_data) and abs(regression_data['PCT_day_change']) > 2.5 and abs(regression_data['PCT_change']) > 2.5):
        return True
    else:
        return False

def breakout_or_no_consolidation(regression_data):
    if(is_recent_consolidation(regression_data) == False 
       or is_short_consolidation_breakout(regression_data) == True
       ):
        return True
    else:
        return False

def high_tail_pct_filter(regression_data, regressionResult):
    if((-0.5 < regression_data['PCT_day_change'] < 0.5 and -0.5 < regression_data['PCT_change'] < 0.5)
       or (0 < regression_data['PCT_day_change'] < 1)
       ):
        if(low_tail_pct(regression_data) > 3):
            add_in_csv(regression_data, regressionResult, None, None, None, 'GLowTail-3pc')
        elif(low_tail_pct(regression_data) > 2):
            add_in_csv(regression_data, regressionResult, None, None, None, 'GLowTail-2pc')
        elif(low_tail_pct(regression_data) > 1):
            add_in_csv(regression_data, regressionResult, None, None, None, 'GLowTail-1pc')
    
    if((-0.5 < regression_data['PCT_day_change'] < 0.5 and -0.5 < regression_data['PCT_change'] < 0.5)
       or (-1 < regression_data['PCT_day_change'] < 0)
        ):
        if(high_tail_pct(regression_data) > 3):
            add_in_csv(regression_data, regressionResult, None, None, None, 'GHighTail-3pc')
        elif(high_tail_pct(regression_data) > 2):
            add_in_csv(regression_data, regressionResult, None, None, None, 'GHighTail-2pc')
        elif(high_tail_pct(regression_data) > 1):
            add_in_csv(regression_data, regressionResult, None, None, None, 'GHighTail-1pc')
            
    if(0.75 < regression_data['PCT_day_change'] < 4):
        if(high_tail_pct(regression_data) > 3):
            add_in_csv(regression_data, regressionResult, None, None, None, 'GHighTail-3pc')
        elif(high_tail_pct(regression_data) > 2):
            add_in_csv(regression_data, regressionResult, None, None, None, 'GHighTail-2pc')
        elif(high_tail_pct(regression_data) > 1.5):
            add_in_csv(regression_data, regressionResult, None, None, None, 'GHighTail-1.5pc')
    if(-4 < regression_data['PCT_day_change'] < -0.75):
        if(low_tail_pct(regression_data) > 3):
            add_in_csv(regression_data, regressionResult, None, None, None, 'GLowTail-3pc')
        elif(low_tail_pct(regression_data) > 2):
            add_in_csv(regression_data, regressionResult, None, None, None, 'GLowTail-2pc')
        elif(low_tail_pct(regression_data) > 1.5):
            add_in_csv(regression_data, regressionResult, None, None, None, 'GLowTail-1.5pc')

def tail_pct_filter(regression_data, regressionResult):
    if(regression_data['PCT_day_change'] > 0):
        if(high_tail_pct(regression_data) < 0.1):
            add_in_csv(regression_data, regressionResult, None, None, None, 'HighTailLessThan-0.1pc')
        if(high_tail_pct(regression_data) < 0.3):
            add_in_csv(regression_data, regressionResult, None, None, None, 'HighTailLessThan-0.3pc')
            if(low_tail_pct(regression_data) < 0.1):
                add_in_csv(regression_data, regressionResult, None, None, None, 'LowTailLessThan-0.1pc')
            if(low_tail_pct(regression_data) < 0.3):
                add_in_csv(regression_data, regressionResult, None, None, None, 'LowTailLessThan-0.3pc')
    if(regression_data['PCT_day_change'] < 0):
        if(low_tail_pct(regression_data) < 0.1):
            add_in_csv(regression_data, regressionResult, None, None, None, 'LowTailLessThan-0.1pc')
        if(low_tail_pct(regression_data) < 0.3):
            add_in_csv(regression_data, regressionResult, None, None, None, 'LowTailLessThan-0.3pc')
            if(high_tail_pct(regression_data) < 0.1):
                add_in_csv(regression_data, regressionResult, None, None, None, 'HighTailLessThan-0.1pc')
            if(high_tail_pct(regression_data) < 0.3):
                add_in_csv(regression_data, regressionResult, None, None, None, 'HighTailLessThan-0.3pc')
    high_tail_pct_filter(regression_data, regressionResult)

def tail_reversal_filter(regression_data, regressionResult):
    if(3 > low_tail_pct(regression_data) > 1.8
            and high_tail_pct(regression_data) < 1
            #and 'MayBuyCheckChart' in regression_data['filter1'] 
            and -3 < regression_data['PCT_day_change_pre1'] < -1
            and -3 < regression_data['PCT_day_change'] < -1
            ):
            add_in_csv(regression_data, regressionResult, None, '(Check-chart-market2to3down)MayBuy-LastDayDown', None)
    if(3 > high_tail_pct(regression_data) > 1.8
            and low_tail_pct(regression_data) < 1
            #and 'MaySellCheckChart' in regression_data['filter1'] 
            and 3 > regression_data['PCT_day_change_pre1'] > 1
            and 3 > regression_data['PCT_day_change'] > 1
            ):
            add_in_csv(regression_data, regressionResult, None, '(Check-chart-market2to3up)MaySell-LastDayUp', None)
    if(-4 < regression_data['PCT_day_change'] < -1.5 and -4 < regression_data['PCT_change'] < -1.5
        ):
        if(3.5 > low_tail_pct(regression_data) > 1.8):
            add_in_csv(regression_data, regressionResult, None, None, '(MayBuyCheckChart-Strong(check-chart-MarketNotUp2-3))', None)
        elif(low_tail_pct(regression_data) > 1.8 and regression_data['PCT_day_change'] < -2):
            add_in_csv(regression_data, regressionResult, None, None, '(MayBuyCheckChart-Strong(check-chart-MarketNotUp2-3))', None)
    elif(-4 < regression_data['PCT_day_change'] < 1 and -4 < regression_data['PCT_change'] < 1
        ):
        if(3.5 > low_tail_pct(regression_data) > 1.8):
            add_in_csv(regression_data, regressionResult, None, None, '(MayBuyCheckChart(check-chart-MarketNotUp2-3))', None)
        elif(low_tail_pct(regression_data) > 1.8 and regression_data['PCT_day_change'] < -2):
            add_in_csv(regression_data, regressionResult, None, None, '(MayBuyCheckChart(check-chart-MarketNotUp2-3))', None)
    if(1.5 < regression_data['PCT_day_change'] < 4 and 1.5 < regression_data['PCT_change'] < 4
        ):
        if(3.5 > high_tail_pct(regression_data) > 1.8):
            add_in_csv(regression_data, regressionResult, None, None, '(MaySellCheckChart-Strong(check-chart-MarketNotDown2-3))', None)
        if(high_tail_pct(regression_data) > 1.8 and regression_data['PCT_day_change'] > 2):
            add_in_csv(regression_data, regressionResult, None, None, '(MaySellCheckChart-Strong(check-chart-MarketNotDown2-3))', None)
    elif(-1 < regression_data['PCT_day_change'] < 4 and -1 < regression_data['PCT_change'] < 4
        ):
        if(3.5 > high_tail_pct(regression_data) > 1.8):
            add_in_csv(regression_data, regressionResult, None, None, '(MaySellCheckChart(check-chart-MarketNotDown2-3))', None)
        elif(high_tail_pct(regression_data) > 1.8 and regression_data['PCT_day_change'] > 2):
            add_in_csv(regression_data, regressionResult, None, None, '(MaySellCheckChart(check-chart-MarketNotDown2-3))', None)
            
def historical_data(data):
    ardate = np.array([str(x) for x in (np.array(data['data'])[:,0][::-1]).tolist()])
    aropen = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,1][::-1]).tolist()])
    arhigh = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,2][::-1]).tolist()])
    arlow  = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,3][::-1]).tolist()])
    arlast = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,4][::-1]).tolist()])
    arclose= np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,5][::-1]).tolist()])
    arquantity = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,6][::-1]).tolist()])
    arturnover = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,7][::-1]).tolist()])
    return ardate, aropen, arhigh, arlow, arlast, arclose, arquantity, arturnover

def no_doji_or_spinning_buy_india(regression_data):
    if ('SPINNINGTOP' not in str(regression_data['buyIndia']) and 'DOJI' not in str(regression_data['buyIndia'])):
        return True;
    else:
        return False
    
def no_doji_or_spinning_sell_india(regression_data): 
    if ('SPINNINGTOP' not in str(regression_data['sellIndia']) and 'DOJI' not in str(regression_data['sellIndia'])):
        return True;
    else:
        return False   

def get_open_interest_data(regression_data, db_collection):
    data = db_collection.find_one({'scrip':regression_data['scrip']})
    if(data is None or (np.array(data['data'])).size < 1):
        return '0', '0'
    ardate, aroipctchange, arcontractpctchange = historical_data_OI(data)   
    if(ardate[-1] == regression_data['date']):
        return str(round(aroipctchange[-1], 2)), str(round(arcontractpctchange[-1], 2))
    return '0', '0'
 
def scrip_patterns_to_dict(filename):  
    tempDict = {}
    count = 0
    with open(filename) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            try:
                if (count != 0):
                    dictValue = {}
                    dictValue['avg'] = row[1]
                    dictValue['count'] = row[2]
                    tempDict[row[0]] = dictValue
                count = count + 1
            except:
                pass
    return tempDict 

def get_regressionResult(regression_data, scrip, db, mlp_r_o, kneighbours_r_o, mlp_c_o, kneighbours_c_o):
    regression_data['mlpValue_reg_other'] = float(mlp_r_o)
    regression_data['kNeighboursValue_reg_other'] = float(kneighbours_r_o)
    regression_data['mlpValue_cla_other'] = float(mlp_c_o)
    regression_data['kNeighboursValue_cla_other'] = float(kneighbours_c_o)
    regression_data['filter'] = " "
    regression_data['filter1'] = " "
    regression_data['filter2'] = " "
    regression_data['filter3'] = " "
    regression_data['filter4'] = " "
    regression_data['series_trend'] = "NA"
    if pct_change_negative_trend(regression_data):
        regression_data['series_trend'] = "downTrend"
    if pct_change_positive_trend(regression_data):
         regression_data['series_trend'] = "upTrend"    
    
    regression_data['oi'] = float(-10000)
    regression_data['contract'] = float(-10000)
    if(db is not None):
        oi, contract = get_open_interest_data(regression_data, db.historyOpenInterest)
        regression_data['oi'] = float(oi)
        regression_data['contract'] = float(contract)
    
    regression_data['oi_next'] = float(-10000)
    regression_data['contract_next'] = float(-10000)
    if(db is not None):
        oi, contract = get_open_interest_data(regression_data, db.historyOpenInterestNext)
        regression_data['oi_next'] = float(oi)
        regression_data['contract_next'] = float(contract)
    resultDeclared = ""
    resultDate = ""
    resultSentiment = ""
    resultComment = ""
    if(db is not None):
        result_data = db.scrip_result.find_one({'scrip':scrip})
        if(result_data is not None):
            resultDate = result_data['result_date'].strip()
            resultSentiment = result_data['result_sentiment']
            resultComment = result_data['comment']
            start_date = (datetime.datetime.now() - datetime.timedelta(hours=0))
            start_date = datetime.datetime(start_date.year, start_date.month, start_date.day, start_date.hour)
            result_time = datetime.datetime.strptime(resultDate, "%Y-%m-%d")
            if result_time < start_date: 
                resultDeclared = resultDate 
                resultDate = ""
    regressionResult = [ ]
    regressionResult.append(regression_data['buyIndia'])
    regressionResult.append(regression_data['sellIndia'])
    if(TEST != True):
        regressionResult.append(regression_data['buyIndia_avg'])
        regressionResult.append(regression_data['buyIndia_count'])
        regressionResult.append(regression_data['sellIndia_avg'])
        regressionResult.append(regression_data['sellIndia_count'])
    regressionResult.append(regression_data['scrip'])
    regressionResult.append(regression_data['series_trend'])
    regressionResult.append(regression_data['SMA4_2daysBack'])
    regressionResult.append(regression_data['SMA9_2daysBack'])
    regressionResult.append(regression_data['SMA4'])
    regressionResult.append(regression_data['SMA9'])
    regressionResult.append(regression_data['SMA25'])
    regressionResult.append(regression_data['SMA50'])
    regressionResult.append(regression_data['SMA100'])
    regressionResult.append(regression_data['SMA200'])
    regressionResult.append(resultDate)
    regressionResult.append(resultDeclared)
    regressionResult.append(resultSentiment)
    regressionResult.append(resultComment)
    regressionResult.append(regression_data['forecast_day_VOL_change'])
    regressionResult.append(regression_data['oi'])
    regressionResult.append(regression_data['contract'])
    regressionResult.append(regression_data['oi_next'])
    regressionResult.append(regression_data['contract_next'])
    regressionResult.append(regression_data['forecast_day_PCT_change'])
    regressionResult.append(regression_data['forecast_day_PCT2_change'])
    regressionResult.append(regression_data['forecast_day_PCT3_change'])
    regressionResult.append(regression_data['forecast_day_PCT4_change'])
    regressionResult.append(regression_data['forecast_day_PCT5_change'])
    regressionResult.append(regression_data['forecast_day_PCT7_change'])
    regressionResult.append(regression_data['forecast_day_PCT10_change'])
    regressionResult.append(regression_data['mlpValue_reg'])
    regressionResult.append(regression_data['kNeighboursValue_reg'])
    regressionResult.append(regression_data['mlpValue_cla'])
    regressionResult.append(regression_data['kNeighboursValue_cla'])
    regressionResult.append(regression_data['mlpValue_reg_other'])
    regressionResult.append(regression_data['kNeighboursValue_reg_other'])
    regressionResult.append(regression_data['mlpValue_cla_other'])
    regressionResult.append(regression_data['kNeighboursValue_cla_other'])
    regressionResult.append(regression_data['year2HighChange'])
    regressionResult.append(regression_data['year2LowChange'])
    regressionResult.append(regression_data['yearHighChange'])
    regressionResult.append(regression_data['yearLowChange'])
    regressionResult.append(regression_data['month6HighChange'])
    regressionResult.append(regression_data['month6LowChange'])
    regressionResult.append(regression_data['month3HighChange'])
    regressionResult.append(regression_data['month3LowChange'])
    regressionResult.append(regression_data['trend'])
    regressionResult.append(regression_data['score'])
    regressionResult.append(str(round(high_tail_pct(regression_data), 1))) 
    regressionResult.append(str(round(low_tail_pct(regression_data), 1)))
    regressionResult.append(regression_data['PCT_day_change'])
    regressionResult.append(regression_data['PCT_change'])
    regressionResult.append(regression_data['scrip'])
    return regressionResult

def all_withoutml(regression_data, regressionResult, ws):
    add_in_csv(regression_data, regressionResult, ws, '')

def ten_days_more_than_fifteen(regression_data):
    if(25 > regression_data['forecast_day_PCT10_change'] > 5
       and (regression_data['forecast_day_PCT5_change'] > 15
         or regression_data['forecast_day_PCT7_change'] > 15
         or regression_data['forecast_day_PCT10_change'] > 15)
    ):
        return True
    else:
        return False

def ten_days_more_than_ten(regression_data):
    if(25 > regression_data['forecast_day_PCT10_change'] > 5
       and (regression_data['forecast_day_PCT5_change'] > 10
         or regression_data['forecast_day_PCT7_change'] > 10
         or regression_data['forecast_day_PCT10_change'] > 10)
    ):
        return True
    else:
        return False

def ten_days_less_than_ten(regression_data):
    if(regression_data['forecast_day_PCT5_change'] < 10
       and regression_data['forecast_day_PCT7_change'] < 10
       and regression_data['forecast_day_PCT10_change'] < 10
    ):
        return True
    else:
        return False

def ten_days_less_than_five(regression_data):
    if(regression_data['forecast_day_PCT_change'] < 5
       and regression_data['forecast_day_PCT2_change'] < 5
       and regression_data['forecast_day_PCT3_change'] < 5
       and regression_data['forecast_day_PCT4_change'] < 5
       and regression_data['forecast_day_PCT5_change'] < 5
       and regression_data['forecast_day_PCT7_change'] < 5
       and regression_data['forecast_day_PCT10_change'] < 5
    ):
        return True
    else:
        return False
 
def ten_days_less_than_minus_fifteen(regression_data):
    if(-25 < regression_data['forecast_day_PCT10_change'] < -5
       and (regression_data['forecast_day_PCT5_change'] < -15
         or regression_data['forecast_day_PCT7_change'] < -15
         or regression_data['forecast_day_PCT10_change'] < -15)
    ):
        return True
    else:
        return False 
       
def ten_days_less_than_minus_ten(regression_data):
    if(-25 < regression_data['forecast_day_PCT10_change'] < -5
       and (regression_data['forecast_day_PCT5_change'] < -10
         or regression_data['forecast_day_PCT7_change'] < -10
         or regression_data['forecast_day_PCT10_change'] < -10)
    ):
        return True
    else:
        return False

def ten_days_more_than_minus_ten(regression_data):
    if(regression_data['forecast_day_PCT5_change'] > -10 
       and regression_data['forecast_day_PCT7_change'] > -10 
       and regression_data['forecast_day_PCT10_change'] > -10
    ):
        return True
    else:
        return False
  
def ten_days_more_than_minus_five(regression_data):
    if(regression_data['forecast_day_PCT_change'] > -5
       and regression_data['forecast_day_PCT2_change'] > -5 
       and regression_data['forecast_day_PCT3_change'] > -5 
       and regression_data['forecast_day_PCT4_change'] > -5
       and regression_data['forecast_day_PCT5_change'] > -5 
       and regression_data['forecast_day_PCT7_change'] > -5 
       and regression_data['forecast_day_PCT10_change'] > -5
    ):
        return True
    else:
        return False
       
def ten_days_more_than_seven(regression_data):
    if(25 > regression_data['forecast_day_PCT10_change'] > 5
       and (regression_data['forecast_day_PCT5_change'] > 7
         or regression_data['forecast_day_PCT7_change'] > 7
         or regression_data['forecast_day_PCT10_change'] > 7)
    ):
        return True
    else:
        return False
        
def ten_days_less_than_minus_seven(regression_data):
    if(-25 < regression_data['forecast_day_PCT10_change'] < -5
       and (regression_data['forecast_day_PCT5_change'] < -7
         or regression_data['forecast_day_PCT7_change'] < -7
         or regression_data['forecast_day_PCT10_change'] < -7)
    ):
        return True
    else:
        return False    

def ten_days_more_than_five(regression_data):
    if(25 > regression_data['forecast_day_PCT10_change'] > 5
       and regression_data['forecast_day_PCT7_change'] > 5
       and regression_data['forecast_day_PCT5_change'] > 1
       and regression_data['forecast_day_PCT4_change'] > 1
       and regression_data['forecast_day_PCT3_change'] > 1
    ):
        return True
    else:
        return False
        
def ten_days_less_than_minus_five(regression_data):
    if(-25 < regression_data['forecast_day_PCT10_change'] < -5
       and regression_data['forecast_day_PCT7_change'] < -5
       and regression_data['forecast_day_PCT5_change'] < -1
       and regression_data['forecast_day_PCT4_change'] < -1
       and regression_data['forecast_day_PCT3_change'] < -1
    ):
        return True
    else:
        return False    

def buy_pattern_without_mlalgo(regression_data, regressionResult, ws_buyPattern2, ws_sellPattern2):
    if(regression_data['yearLowChange'] > 10 and regression_data['buyIndia_count'] > 1):
        if(regression_data['buyIndia_avg'] > 1.5 and high_tail_pct(regression_data) < 1.5):
            add_in_csv(regression_data, regressionResult, None, 'buyPatterns')
        elif(regression_data['buyIndia_avg'] > 0.9 and high_tail_pct(regression_data) < 1.5
            and regression_data['PCT_day_change'] < -2
            and (regression_data['PCT_day_change'] < -1 or regression_data['buyIndia_count'] > 5)
            ):
            add_in_csv(regression_data, regressionResult, None, 'buyPatterns-1')
    elif(regression_data['buyIndia_avg'] > 0.9 and high_tail_pct(regression_data) < 1.5):
        add_in_csv(regression_data, regressionResult, None, None)
        #add_in_csv(regression_data, regressionResult, None, 'buyPatterns-1-Risky')
    
    if(regression_data['yearLowChange'] > 10 and regression_data['buyIndia_count'] > 1):
        if(regression_data['buyIndia_avg'] < -1.5 and low_tail_pct(regression_data) < 1.5):
            add_in_csv(regression_data, regressionResult, None, 'sellPatterns')
        elif(regression_data['buyIndia_avg'] < -0.9 and low_tail_pct(regression_data) < 1.5
            and regression_data['PCT_day_change'] > 2
            and (regression_data['PCT_day_change'] > 1 or regression_data['buyIndia_count'] > 5)
            ):
            add_in_csv(regression_data, regressionResult, None, 'sellPatterns-1')
    elif(regression_data['buyIndia_avg'] < -0.9 and low_tail_pct(regression_data) < 1.5):
        add_in_csv(regression_data, regressionResult, None, None)
        #add_in_csv(regression_data, regressionResult, None, 'sellPatterns-1-Risky')
        
    if(regression_data['buyIndia_avg'] > 1.25 and regression_data['buyIndia_count'] > 1
        and high_tail_pct(regression_data) < 1.5
        and regression_data['SMA9'] > 1
        ):
        add_in_csv(regression_data, regressionResult, None, 'buyPatterns-(SMA9GT1)')
    
    buyPatternsDict=scrip_patterns_to_dict('../../data-import/nselist/all-buy-filter-by-PCT-Change.csv')
    if regression_data['buyIndia'] != '' and regression_data['buyIndia'] in buyPatternsDict:
        if (abs(float(buyPatternsDict[regression_data['buyIndia']]['avg'])) >= .1 and float(buyPatternsDict[regression_data['buyIndia']]['count']) >= 2):
            if(-0.5 < regression_data['PCT_day_change'] < 3 and float(buyPatternsDict[regression_data['buyIndia']]['avg']) > 1):
                avg = buyPatternsDict[regression_data['buyIndia']]['avg']
                count = buyPatternsDict[regression_data['buyIndia']]['count']
                #add_in_csv_hist_pattern(regression_data, regressionResult, ws_buyPattern2, 'wml_buy', avg, count)
            elif(-3 < regression_data['PCT_day_change'] < 0.5 and float(buyPatternsDict[regression_data['buyIndia']]['avg']) < -1):
                avg = buyPatternsDict[regression_data['buyIndia']]['avg']
                count = buyPatternsDict[regression_data['buyIndia']]['count']
                #add_in_csv_hist_pattern(regression_data, regressionResult, ws_sellPattern2, 'wml_buy', avg, count)

def buy_pattern_from_history(regression_data, ws_buyPattern2):
    buyPatternsDict=scrip_patterns_to_dict('../../data-import/nselist/patterns-buy.csv')
    buyIndiaAvg = 0
    regression_data['buyIndia_avg'] = 0
    regression_data['buyIndia_count'] = 0
    regression_data['sellIndia_avg'] = 0
    regression_data['sellIndia_count'] = 0
    flag = False
    if regression_data['buyIndia'] != '' and regression_data['buyIndia'] in buyPatternsDict:
        regression_data['buyIndia_avg'] = float(buyPatternsDict[regression_data['buyIndia']]['avg'])
        regression_data['buyIndia_count'] = float(buyPatternsDict[regression_data['buyIndia']]['count'])
        if (abs(float(buyPatternsDict[regression_data['buyIndia']]['avg'])) >= .1):
            buyIndiaAvg = float(buyPatternsDict[regression_data['buyIndia']]['avg'])
            if(int(buyPatternsDict[regression_data['buyIndia']]['count']) >= 2):
                if(is_algo_buy(regression_data)
                    and 'P@[' not in str(regression_data['sellIndia'])
                    #and regression_data['trend'] != 'up'
                    and -1 < regression_data['PCT_day_change'] < 3):
                    avg = buyPatternsDict[regression_data['buyIndia']]['avg']
                    count = buyPatternsDict[regression_data['buyIndia']]['count']
                    if(float(buyPatternsDict[regression_data['buyIndia']]['avg']) > 0.8 and int(buyPatternsDict[regression_data['buyIndia']]['count']) >= 5):
                       flag = True
                       #add_in_csv_hist_pattern(regression_data, regressionResult, ws_buyPattern2, 'buyPattern2', avg, count)
                    elif(float(buyPatternsDict[regression_data['buyIndia']]['avg']) > 0.5 
                       or (float(buyPatternsDict[regression_data['buyIndia']]['avg']) > 0.3 and (ten_days_less_than_minus_ten(regression_data) or regression_data['yearHighChange'] < -40))):
                        if(regression_data['forecast_day_PCT10_change'] < 0 and regression_data['forecast_day_PCT_change'] >= 0):
                            flag = True
                            #add_in_csv_hist_pattern(regression_data, regressionResult, ws_buyPattern2, 'buyPattern2', avg, count)
                        elif(regression_data['forecast_day_PCT10_change'] > 0):    
                            flag = True
                            #add_in_csv_hist_pattern(regression_data, regressionResult, ws_buyPattern2, 'buyPattern2', avg, count)     
    return buyIndiaAvg, flag

def buy_all_rule(regression_data, regressionResult, buyIndiaAvg, ws_buyAll):
    buy_other_indicator(regression_data, regressionResult, True, None)
    if(is_algo_buy(regression_data)
        and ((regression_data['PCT_day_change'] > 1 
                and high_tail_pct(regression_data) < 2 
                and ('P@[' not in str(regression_data['sellIndia']))
                )
             or (low_tail_pct(regression_data) > 1.5 
                and (high_tail_pct(regression_data) < low_tail_pct(regression_data))
                )
             or (regression_data['PCT_day_change'] < -2
                and regression_data['forecast_day_PCT_change'] > 0.3
                )
            )
        and (BUY_VERY_LESS_DATA or regression_data['PCT_change'] > -1)
        and (BUY_VERY_LESS_DATA or ((regression_data['PCT_day_change_pre1'] < 0) or (regression_data['forecast_day_VOL_change'] > 0))) #Uncomment1 If very less data
        and (BUY_VERY_LESS_DATA or (regression_data['high']-regression_data['bar_high']) < (regression_data['bar_high']-regression_data['bar_low']))
        and buyIndiaAvg >= -.70
        and ((last_7_day_all_up(regression_data) == False) or (regression_data['forecast_day_PCT10_change'] < 10))
        and (MARKET_IN_UPTREND or (last_4_day_all_up(regression_data) == False)) #Uncomment0 If very less data
        and breakout_or_no_consolidation(regression_data) == True
        and regression_data['close'] > 50
        ):
        if((7.5 < regression_data['month3LowChange'] < 25)
            and (-25 < regression_data['month3HighChange'] < -7.5)
            and regression_data['PCT_day_change_pre1'] < 1
            and -2 < regression_data['PCT_day_change'] < 0
            and -2 < regression_data['PCT_change'] < 0
            and (10 > regression_data['forecast_day_PCT3_change'] > 1)
            and (10 > regression_data['forecast_day_PCT4_change'] > 1)
            and (10 > regression_data['forecast_day_PCT5_change'] > 1)
            and (10 > regression_data['forecast_day_PCT7_change'] > 1)
            and (15 > regression_data['forecast_day_PCT10_change'] > 1)
            and high_tail_pct(regression_data) < 1
            and low_tail_pct(regression_data) > 1.5
            ):
            add_in_csv(regression_data, regressionResult, None, '##ALL:downLastDay-UpTrend')
        if(low_tail_pct(regression_data) < 2.5
           and regression_data['low'] > regression_data['low_pre1']
         ):
            if(regression_data['PCT_day_change'] < 0 and regression_data['PCT_change'] < 0
                and regression_data['month3HighChange'] < -15  
                ):
                add_in_csv(regression_data, regressionResult, None, 'ML:buy-0')
#             elif(regression_data['PCT_day_change'] < 2.5 and regression_data['PCT_change'] < 0.5
#                 and (regression_data['PCT_day_change'] < 0 or regression_data['PCT_day_change_pre1'] < 0)
#                 and regression_data['month3HighChange'] < -5
#                 ):
#                 add_in_csv(regression_data, regressionResult, None, 'UPTREND:ML:buy-1')
#             elif(regression_data['PCT_day_change'] < 2.5 and regression_data['PCT_change'] < 1
#                 and (regression_data['PCT_day_change'] < 0 or regression_data['PCT_day_change_pre1'] < 0)
#                 and regression_data['month3HighChange'] < -5
#                 ):
#                 add_in_csv(regression_data, regressionResult, None, 'UPTREND:ML:buy-2(Risky)')
        add_in_csv(regression_data, regressionResult, ws_buyAll, None)
        return True
    elif(is_algo_sell(regression_data)
        and ((regression_data['PCT_day_change'] < -1 
                and low_tail_pct(regression_data) < 2
                and ('P@[' not in str(regression_data['buyIndia']))
                ) 
             or (high_tail_pct(regression_data) > 1.5 
                and (low_tail_pct(regression_data) < high_tail_pct(regression_data))
                )
             or (regression_data['PCT_day_change'] > 2
                and regression_data['forecast_day_PCT_change'] < -0.3
                )
            )
        and (SELL_VERY_LESS_DATA or regression_data['PCT_change'] < 1)
        and (SELL_VERY_LESS_DATA or ((regression_data['PCT_day_change_pre1'] > 0) or (regression_data['forecast_day_VOL_change'] > 0))) #Uncomment1 If very less data
        and (SELL_VERY_LESS_DATA or (regression_data['bar_low']-regression_data['low']) < (regression_data['bar_high']-regression_data['bar_low']))
        and buyIndiaAvg <= 0.70
        and ((last_7_day_all_down(regression_data) == False) or (regression_data['forecast_day_PCT10_change'] > -10))
        and (MARKET_IN_DOWNTREND or (last_4_day_all_down(regression_data) == False)) #Uncomment0 If very less data
        and breakout_or_no_consolidation(regression_data) == True
        and regression_data['close'] > 50
        ):
        if(2 < regression_data['PCT_day_change'] < 5
            and  2 < regression_data['PCT_change'] < 5
            and high_tail_pct(regression_data) > 1.5
            and low_tail_pct(regression_data) < 1):
            add_in_csv(regression_data, regressionResult, None, 'Test:MLSellFromHighData')
    return False

def buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvg, ws_buyAll):
    buy_other_indicator(regression_data, regressionResult, False, None)
    if(is_algo_buy_classifier(regression_data)
        and ((regression_data['PCT_day_change'] > 1 
                and high_tail_pct(regression_data) < 2 
                and ('P@[' not in str(regression_data['sellIndia']))
                )
             or (low_tail_pct(regression_data) > 1.5 
                and (high_tail_pct(regression_data) < low_tail_pct(regression_data))
                )
             or (regression_data['PCT_day_change'] < -2
                and regression_data['forecast_day_PCT_change'] > 0.3
                )
            )
        and (BUY_VERY_LESS_DATA or regression_data['PCT_change'] > -1)
        and (BUY_VERY_LESS_DATA or ((regression_data['PCT_day_change_pre1'] < 0) or (regression_data['forecast_day_VOL_change'] > 0))) #Uncomment1 If very less data
        and (BUY_VERY_LESS_DATA or (regression_data['high']-regression_data['bar_high']) < (regression_data['bar_high']-regression_data['bar_low']))
        and buyIndiaAvg >= -.70
        and ((last_7_day_all_up(regression_data) == False) or (regression_data['forecast_day_PCT10_change'] < 10))
        and (MARKET_IN_UPTREND or (last_4_day_all_up(regression_data) == False)) #Uncomment0 If very less data
        and breakout_or_no_consolidation(regression_data) == True
        and regression_data['close'] > 50
        ):
        add_in_csv(regression_data, regressionResult, ws_buyAll, None)
        return True
    return False

def buy_year_high(regression_data, regressionResult, reg, ws_buyYearHigh):
    return False
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(float(regression_data['forecast_day_VOL_change']) > 70
       and regression_data['PCT_day_change_pre1'] > -0.5
       and no_doji_or_spinning_buy_india(regression_data)
       ):
        if(-15 < regression_data['yearHighChange'] < -5 and regression_data['yearLowChange'] > 30
            and -0.5 < regression_data['PCT_day_change'] < 2 and regression_data['forecast_day_PCT2_change'] <= 2
            ):
            add_in_csv(regression_data, regressionResult, ws_buyYearHigh, 'buyYearHigh-0')
            return True
    if(float(regression_data['forecast_day_VOL_change']) > 35
       and regression_data['PCT_day_change_pre1'] > -0.5
       and no_doji_or_spinning_buy_india(regression_data)
       ):
        if(-15 < regression_data['yearHighChange'] < -5 and regression_data['yearLowChange'] > 30
            and -0.5 < regression_data['PCT_day_change'] < 2 and regression_data['forecast_day_PCT2_change'] <= 2
            ):
            add_in_csv(regression_data, regressionResult, ws_buyYearHigh, 'buyYearHigh-1')
            return True
    if(float(regression_data['forecast_day_VOL_change']) > 50
       and regression_data['PCT_day_change_pre1'] > -0.5
       and no_doji_or_spinning_buy_india(regression_data)
       ):
        if(-5 <= regression_data['yearHighChange'] < -1 and regression_data['yearLowChange'] > 15 
            and -0.5 < regression_data['PCT_day_change'] < 2 and regression_data['forecast_day_PCT2_change'] <= 2
            ):
            add_in_csv(regression_data, regressionResult, ws_buyYearHigh, 'buyYearHigh-2')
            return True
    
    return False

def buy_year_low(regression_data, regressionResult, reg, ws_buyYearLow, ws_buyYearLow1):
    return False
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(1 < regression_data['yearLowChange'] < 5 and regression_data['yearHighChange'] < -30 
        and 2 < regression_data['PCT_day_change'] < 6 and 2 < regression_data['PCT_day_change'] < 6
        and regression_data['forecast_day_PCT2_change'] > 0 and regression_data['forecast_day_PCT_change'] > 0
        and float(regression_data['forecast_day_VOL_change']) > 35
        ):
        add_in_csv(regression_data, regressionResult, ws_buyYearLow, 'buyYearLow')
        return True
    elif(5 < regression_data['yearLowChange'] < 15 and regression_data['yearHighChange'] < -75 
        and 2 < regression_data['PCT_day_change'] < 5 and 2 < regression_data['PCT_day_change'] < 5
        and 5 > regression_data['forecast_day_PCT2_change'] > -0.5 and regression_data['forecast_day_PCT_change'] > 0
        and float(regression_data['forecast_day_VOL_change']) > 35
        ):
        add_in_csv(regression_data, regressionResult, ws_buyYearLow1, 'buyYearLow1')
        return True
    return False

def buy_down_trend(regression_data, regressionResult, reg, ws_buyDownTrend):
    return False
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(all_day_pct_change_negative_except_today(regression_data) 
        and regression_data['forecast_day_PCT_change'] > 0 
        and 0 < regression_data['PCT_day_change'] < 4 and 0 < regression_data['PCT_change']
        and regression_data['yearHighChange'] < -10 
        and high_tail_pct(regression_data) < 0.5
       ):
        if(last_5_day_all_down_except_today(regression_data)
            and ten_days_less_than_minus_ten(regression_data)
            and regression_data['forecast_day_PCT7_change'] < -5
            and regression_data['forecast_day_PCT10_change'] < -10
            ):
            add_in_csv(regression_data, regressionResult, ws_buyDownTrend, 'buyDownTrend-0(Risky)')
            return True
        elif(last_5_day_all_down_except_today(regression_data)
            and ten_days_less_than_minus_seven(regression_data)
            and regression_data['forecast_day_PCT7_change'] < -4
            and regression_data['forecast_day_PCT10_change'] < -4
            ):
            add_in_csv(regression_data, regressionResult, ws_buyDownTrend, 'buyDownTrend-1')
            return True
        elif(regression_data['forecast_day_PCT7_change'] < -4
            and regression_data['forecast_day_PCT10_change'] < -4
            ):
            add_in_csv(regression_data, regressionResult, ws_buyDownTrend, 'buyDownTrend-2(Risky)')
            return True
        
    return False

def buy_final(regression_data, regressionResult, reg, ws, ws1):
    return False
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(regression_data['yearHighChange'] < -10 
        and regression_data['yearLowChange'] > 5
        and regression_data['month3LowChange'] > 3
        and 4 > regression_data['PCT_day_change'] > 1 and 4 > regression_data['PCT_change'] > 1
        and abs(regression_data['PCT_day_CH']) < 0.3
        and regression_data['forecast_day_VOL_change'] > 0
        and high_tail_pct(regression_data) < 1
        and str(regression_data['score']) != '0-1'
        ):   
        if(str(regression_data['sellIndia']) == '' and -90 < regression_data['yearHighChange'] < -10
            and(ten_days_less_than_minus_ten(regression_data)
                 or (last_5_day_all_down_except_today(regression_data)
                    and ten_days_less_than_minus_seven(regression_data)
                    )
            ) 
            and regression_data['forecast_day_PCT7_change'] < -5 
            and regression_data['forecast_day_PCT5_change'] < 0.5 
            and regression_data['forecast_day_PCT4_change'] < 0.5 
            and 5 > regression_data['forecast_day_PCT2_change'] > -0.5 
            and regression_data['forecast_day_PCT_change'] > 0
            ):
            add_in_csv(regression_data, regressionResult, ws, 'buyFinal')
        elif(str(regression_data['sellIndia']) == '' and -90 < regression_data['yearHighChange'] < -10
            and(ten_days_less_than_minus_ten(regression_data)
                 or (last_5_day_all_down_except_today(regression_data)
                    and ten_days_less_than_minus_seven(regression_data)
                    )
            ) 
            and regression_data['forecast_day_PCT7_change'] <= -1 
            and regression_data['forecast_day_PCT5_change'] <= 1  
            and regression_data['forecast_day_PCT2_change'] > 0 
            and regression_data['forecast_day_PCT_change'] > 0
            ):
            add_in_csv(regression_data, regressionResult, ws, 'buyFinal1')
    return False

def buy_high_indicators(regression_data, regressionResult, reg, ws_buyHighIndicators):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    if(kNeighboursValue > 3 and kNeighboursValue_other > 3
            and mlpValue > 2 and mlpValue_other > 2
            and regression_data['PCT_day_change'] > 5
            and regression_data['PCT_change'] > 5
            ):
            if(10 < regression_data['forecast_day_PCT10_change'] < 35):
                add_in_csv(regression_data, regressionResult, ws, '##ALL:buyHighKNeighbours-StockUptrend(Risky)')
            elif(regression_data['forecast_day_PCT10_change'] < 10
                and 5 < regression_data['PCT_day_change'] < 10
                and 5 < regression_data['PCT_change'] < 10
                ):
                add_in_csv(regression_data, regressionResult, ws, '##ALL:buyHighKNeighbours(Risky)') 
    elif(mlpValue >= 2.0 and kNeighboursValue >= 1.0
       and regression_data['yearHighChange'] < -10
       and regression_data['yearLowChange'] > 10
       and (high_tail_pct(regression_data) < 1.5 and (high_tail_pct(regression_data) < low_tail_pct(regression_data)))
       ):
        if(3 > regression_data['PCT_day_change'] > 1.5 and 3 > regression_data['PCT_change'] > -0.5
           and regression_data['forecast_day_PCT_change'] > 0
           and high_tail_pct(regression_data) < 1
           ):
            add_in_csv(regression_data, regressionResult, ws_buyHighIndicators, 'buyHighIndicators(shouldNotOpenInMinus)')
            return True
        if(1 > regression_data['PCT_day_change'] > 0 and 2.5 > regression_data['PCT_change'] > -0.5):
            add_in_csv(regression_data, regressionResult, ws_buyHighIndicators, '(longDownTrend)buyHighIndicators')
            return True 
    return False
              
def buy_pattern(regression_data, regressionResult, reg, ws_buyPattern, ws_buyPattern1):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    score = ''
    if(regression_data['yearLowChange'] > 10):
        if(is_algo_buy(regression_data)
            and regression_data['buyIndia_avg'] > 1.5 
            and high_tail_pct(regression_data) < 1.5
            ):
            add_in_csv(regression_data, regressionResult, ws_buyPattern, 'buyPatternsML')
            return True   

def buy_base_line_buy(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    if((0 < regression_data['year2HighChange'] < 5) 
        and (regression_data['year2LowChange'] > 40)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Year2HighBreak')
    elif((0 < regression_data['yearHighChange'] < 5) 
        and (regression_data['yearLowChange'] > 30)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'YearHighBreak')
    elif((0 < regression_data['month6HighChange'] < 5)
        and (regression_data['month6LowChange'] > 25)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'month6HighBreak')
    elif((0 < regression_data['month3HighChange'] < 5) 
        and (regression_data['month3LowChange'] > 15)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'month3HighBreak')
    
    if((-7.5 < regression_data['year2HighChange'] < 0) 
        and (regression_data['year2LowChange'] > 40)
        ):
        if(regression_data['weekHigh'] >= regression_data['year2High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'year2HighReversal(Confirm)')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'nearYearHigh')
    elif((-7.5 < regression_data['yearHighChange'] < 0) 
        and (regression_data['yearLowChange'] > 30)
        ):
        if(regression_data['weekHigh'] >= regression_data['yearHigh']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'yearHighReversal(Confirm)')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'nearYearHigh')
    elif((-7.5 < regression_data['month6HighChange'] < 0) 
        and (regression_data['month6LowChange'] > 25)
        ):
        if(regression_data['weekHigh'] >= regression_data['month6High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'month6HighReversal(Confirm)')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'nearMonth6High')
    elif((-7.5 < regression_data['month3HighChange'] < 0) 
        and (regression_data['month3LowChange'] > 15)
        ):
        if(regression_data['weekHigh'] >= regression_data['month3High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'month3HighReversal(Confirm)')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'nearMonth3High')
        
    if((-5 < regression_data['year2LowChange'] < 0 ) 
        and (regression_data['year2HighChange'] < -40)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Year2LowBreak')
    elif((-5 < regression_data['yearLowChange'] < 0) 
        and (regression_data['year2LowChange'] > 7.5)
        and (regression_data['yearHighChange'] < -30)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'YearLowBreak')
    elif((-5 < regression_data['month6LowChange'] < 0)
        and (regression_data['yearLowChange'] > 7.5)
        and (regression_data['month6HighChange'] < -25)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'month6LowBreak')
    elif((-5 < regression_data['month3LowChange'] < 0)
        and (regression_data['month6LowChange'] > 7.5)
        and (regression_data['month3HighChange'] < -15)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'month3LowBreak')
    
    if((0 < regression_data['year2LowChange'] < 7.5) 
       and (regression_data['year2HighChange'] < -40)
       ):
        if(regression_data['weekLow'] < regression_data['year2Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'year2LowReversal(Confirm)')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'nearYear2Low')
    elif((0 < regression_data['yearLowChange'] < 7.5)
        and (regression_data['year2LowChange'] > 7.5)
        and (regression_data['yearHighChange'] < -30)
        ):
        if(regression_data['weekLow'] < regression_data['yearLow']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'yearLowReversal(Confirm)')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'nearYearLow')
    elif((0 < regression_data['month6LowChange'] < 7.5)
        and (regression_data['yearLowChange'] > 7.5)
        and (regression_data['month6HighChange'] < -25)
        ):
        if(regression_data['weekLow'] < regression_data['month6Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'month6LowReversal(Confirm)')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'nearMonth6Low')
    elif((0 < regression_data['month3LowChange'] < 7.5)
        and (regression_data['month6LowChange'] > 7.5)
        and (regression_data['month3HighChange'] < -15)
        ):
        if(regression_data['weekLow'] < regression_data['month3Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'month3LowReversal(Confirm)')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'nearMonth3Low')                
    elif(regression_data['year2LowChange'] < 0):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, '**2YearLow')
    elif(regression_data['yearLowChange'] < 0):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, '**YearLow')
    elif(regression_data['month6LowChange'] < 0):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, '**Month6Low')
    elif(regression_data['month3LowChange'] < 0):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, '**Month3Low')
    elif(regression_data['year2HighChange'] > 5):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, '**year2High')
    elif(regression_data['yearHighChange'] > 5):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, '**YearHigh')
    elif(regression_data['month6HighChange'] > 5):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, '**Month6High')
    elif(regression_data['month3HighChange'] > 5):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, '**Month3High') 
    
#     if(regression_data['sellIndia'] == ''
#         and (((2 < regression_data['PCT_change'] < 6) and (2 < regression_data['PCT_day_change'] < 6)) or ((-4 < regression_data['PCT_day_change'] < 0.5) and (-4 < regression_data['PCT_change'] < 0.5)))
#         ):
#         if(is_algo_buy(regression_data)
#             and mlpValue_other > -0.5
#             and kNeighboursValue_other > -0.5
#             and (mlpValue_other > 0.5 or kNeighboursValue_other > 0.5)
#             and high_tail_pct(regression_data) < 2
#             and regression_data['year2HighChange'] > -50
#             and regression_data['month3HighChange'] < -20
#             ):
#             if(-1 < regression_data['PCT_day_change'] < 4 and regression_data['PCT_change'] < 3
#                 and (regression_data['PCT_day_change'] > 1 or regression_data['PCT_change'] > 1)
#                 ):
#                 if(0 < regression_data['year2LowChange'] < 7.5):
#                     return False
#                 elif(0 < regression_data['yearLowChange'] < 7.5):
#                     return False
#                 elif((0 < regression_data['month6LowChange'] < 7.5) and (regression_data['month6HighChange'] < -20)):
#                     if('month6LowReversal(Confirm)' in regression_data['filter3']):
#                         add_in_csv(regression_data, regressionResult, ws, 'Test:buyMonth6LowReversalML')
#                     elif('nearMonth6Low' in regression_data['filter3']):
#                         add_in_csv(regression_data, regressionResult, ws, 'Test:buyMonth6LowML')
#                     return False
#                 elif((0 < regression_data['month3LowChange'] < 7.5) and (regression_data['month3HighChange'] < -15)):
#                     if('month3LowReversal(Confirm)' in regression_data['filter3']):
#                         add_in_csv(regression_data, regressionResult, ws, 'Test:buyMonth3LowReversalML')
#                     elif('nearMonth3Low' in regression_data['filter3']):
#                         add_in_csv(regression_data, regressionResult, ws, 'Test:buyMonth3LowML')
#                     return False
#         
#         if(0 < regression_data['PCT_day_change'] < 4.5 and regression_data['PCT_change'] < 2
#             and (regression_data['PCT_day_change'] > 1 or regression_data['PCT_change'] > 1)
#             and high_tail_pct(regression_data) < 2.5
#             and regression_data['month3HighChange'] < -15
#             ):
#             if((0 < regression_data['year2LowChange'] < 7.5) and (regression_data['year2HighChange'] < -40)):
#                 if(regression_data['weekLow'] < regression_data['year2Low']):
#                     if('year2LowReversal(Confirm)' in regression_data['filter3']):
#                         add_in_csv(regression_data, regressionResult, ws, 'Test:buyYear2LowReversal-1')
#                     elif('nearYear2Low' in regression_data['filter3']):
#                         add_in_csv(regression_data, regressionResult, ws, 'Test:buyYear2Low-1')
#                     return False
#                 else:
#                     return False
#             elif((0 < regression_data['yearLowChange'] < 7.5) and (regression_data['yearHighChange'] < -30)):
#                 if(regression_data['weekLow'] < regression_data['yearLow']):
#                     if('yearLowReversal(Confirm)' in regression_data['filter3']):
#                         add_in_csv(regression_data, regressionResult, ws, 'Test:buyYearLowReversal-1')
#                     elif('nearYearLow' in regression_data['filter3']):
#                         add_in_csv(regression_data, regressionResult, ws, 'Test:buyYearLow-1')
#                     return False
#                 else:
#                     return False
#             elif(0 < regression_data['month6LowChange'] < 7.5
#                 and regression_data['year2HighChange'] > -50
#                 and (regression_data['month6HighChange'] < -20)
#                 ):
#                 if(regression_data['weekLow'] < regression_data['month6Low']):
#                     if('month6LowReversal(Confirm)' in regression_data['filter3']):
#                         add_in_csv(regression_data, regressionResult, ws, 'Test:buyMonth6LowReversal-1')
#                     elif('nearMonth6Low' in regression_data['filter3']):
#                         add_in_csv(regression_data, regressionResult, ws, 'Test:buyMonth6Low-1')
#                     return False
#                 else:
#                     return False
#             elif(0 < regression_data['month3LowChange'] < 5
#                 and regression_data['year2HighChange'] > -50
#                 and (regression_data['month3HighChange'] < -15)
#                 ):
#                 if(regression_data['weekLow'] < regression_data['month3Low']
#                     and regression_data['PCT_day_change'] > 0
#                     ):
#                     if('month3LowReversal(Confirm)' in regression_data['filter3']):
#                         add_in_csv(regression_data, regressionResult, ws, 'Test:buyMonth3LowReversal-1')
#                     elif('nearMonth3Low' in regression_data['filter3']):
#                         add_in_csv(regression_data, regressionResult, ws, 'Test:buyMonth3Low-1')
#                     return False
#                 else:
#                     return False
            
#         if(0 < regression_data['PCT_day_change'] < 4 and regression_data['PCT_change'] < 2
#             and (regression_data['PCT_day_change'] > 1 or regression_data['PCT_change'] > 1)
#             and regression_data['year2HighChange'] > -50
#             and regression_data['month3HighChange'] < -15
#             ):
#             if(0 < regression_data['month6LowChange'] < 7.5):
#                 return False
#             elif(0 < regression_data['month3LowChange'] < 5
#                 and regression_data['weekLow'] < regression_data['month3Low']
#                 ):
#                 if('month3LowReversal(Confirm)' in regression_data['filter3']):
#                     add_in_csv(regression_data, regressionResult, ws, 'Test:buyMonth3LowReversal-2')
#                 elif('nearMonth3Low' in regression_data['filter3']):
#                     add_in_csv(regression_data, regressionResult, ws, 'Test:buyMonth3Low-2')
#                 return False
    return False

def buy_morning_star_buy(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(-8 < regression_data['forecast_day_PCT_change'] < -3
        and ((regression_data['yearLowChange'] > 15) or (regression_data['yearLowChange'] < 2))
        and high_tail_pct(regression_data) < 0.5
        and low_tail_pct(regression_data) > 3
        and regression_data['forecast_day_PCT10_change'] < -10
        ):
        if(-6 < regression_data['PCT_day_change'] < -2 and -6 < regression_data['PCT_change'] < -1
            and (regression_data['close'] - regression_data['low']) > ((regression_data['open'] - regression_data['close']))
            and (regression_data['close'] - regression_data['low']) >= ((regression_data['high'] - regression_data['open']) * 3)
            ):
            add_in_csv(regression_data, regressionResult, ws, 'morningStarBuy-HighLowerTail')
            return True
    elif(-10 < regression_data['forecast_day_PCT_change'] < -2
        and regression_data['PCT_day_change_pre1'] < 0
        and (ten_days_less_than_minus_seven(regression_data))
        and high_tail_pct(regression_data) < 0.5
        and 2 < low_tail_pct(regression_data) < 3.5
        ):
        if(-3 < regression_data['PCT_day_change'] < 0 and -3 < regression_data['PCT_change'] < 0
            and (regression_data['close'] - regression_data['low']) >= ((regression_data['open'] - regression_data['close']) * 3)
            and (regression_data['close'] - regression_data['low']) >= ((regression_data['high'] - regression_data['open']) * 3)
            and regression_data['forecast_day_PCT10_change'] < -10
            and regression_data['SMA25'] < -8.5
            ):
            add_in_csv(regression_data, regressionResult, ws, 'morningStarBuy-dayDown')
            return True
        if(0.3 < regression_data['PCT_day_change'] < 1
            and (regression_data['open'] - regression_data['low']) >= ((regression_data['open'] - regression_data['close']) * 3)
            and (regression_data['open'] - regression_data['low']) >= ((regression_data['high'] - regression_data['close']) * 3)
            and regression_data['year2HighChange'] > -50
            ):
            add_in_csv(regression_data, regressionResult, ws, 'morningStarBuy-dayUp')
            return True
#         if(high_tail_pct(regression_data) < 1.5
#            and low_tail_pct(regression_data) > 2
#            ):
#             if(-1.5 < regression_data['PCT_day_change'] < 0 and -1.5 < regression_data['PCT_change'] < 0
#                 and (regression_data['close'] - regression_data['low']) >= ((regression_data['open'] - regression_data['close']) * 3)
#                 and (regression_data['close'] - regression_data['low']) >= ((regression_data['high'] - regression_data['open']) * 3)
#                 ):
#                 add_in_csv(regression_data, regressionResult, ws, '##TEST:morningStarBuy-3(Check2-3MidCapCross)')
#                 return True
#             if(0 < regression_data['PCT_day_change'] < 1
#                 and (regression_data['open'] - regression_data['low']) >= ((regression_data['open'] - regression_data['close']) * 3)
#                 and (regression_data['open'] - regression_data['low']) >= ((regression_data['high'] - regression_data['close']) * 3)
#                 ):
#                 add_in_csv(regression_data, regressionResult, ws, '##TEST:morningStarBuy-4(Check2-3MidCapCross)')
#                 return True
    return False

def buy_evening_star_sell(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(8 > regression_data['forecast_day_PCT_change'] > 5
        and regression_data['yearLowChange'] > 15
        and low_tail_pct(regression_data) < 0.5
        and high_tail_pct(regression_data) > 3
        ):
        if(5 > regression_data['PCT_day_change'] > 2 and 5 > regression_data['PCT_change'] > 1
            and (regression_data['high']-regression_data['close']) > ((regression_data['close']-regression_data['open']))
            and (regression_data['high']-regression_data['close']) >= ((regression_data['open']-regression_data['low'])*3)
            and ((regression_data['yearHighChange'] < -15) or (regression_data['yearHighChange'] > -2))
            and regression_data['forecast_day_PCT5_change'] < 10
            ):
            add_in_csv(regression_data, regressionResult, ws, 'eveningStarBuy-0')
            return True
        elif(4 > regression_data['PCT_day_change'] > 2 and 4 > regression_data['PCT_change'] > 2
            and -15 < regression_data['yearHighChange'] 
            and regression_data['PCT_day_change_pre3'] > -1
            and regression_data['PCT_day_change_pre1'] > -1
            and regression_data['PCT_change_pre1'] > -1
            and regression_data['PCT_change_pre2'] > -1
            ):
            add_in_csv(regression_data, regressionResult, ws, 'eveningStarSell-0')
            return True
        elif(5 > regression_data['PCT_day_change'] > 2 and 5 > regression_data['PCT_change'] > 2
            and (regression_data['high']-regression_data['close']) > ((regression_data['close']-regression_data['open']))
            and (regression_data['high']-regression_data['close']) >= ((regression_data['open']-regression_data['low'])*3)
            and -15 < regression_data['yearHighChange']
            ):
            if(is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, 'ML:EveningStarBuy-1(Check2-3MidCapCross)')
                return True
            return False
    elif(
        regression_data['PCT_day_change_pre1'] > 0
        and (ten_days_more_than_seven(regression_data))
        ):
        if(low_tail_pct(regression_data) < 1.5
            and high_tail_pct(regression_data) > 1.5
            ):
            if(1.5 > regression_data['PCT_day_change'] > 0.5 and 1.5 > regression_data['PCT_change'] > 0
                and (regression_data['high']-regression_data['close']) >= ((regression_data['close']-regression_data['open']) * 3)
                and (regression_data['high']-regression_data['close']) >= ((regression_data['open']-regression_data['low'])*3)
                ):
                if(is_algo_sell(regression_data)):
                    add_in_csv(regression_data, regressionResult, ws, 'ML:eveningStarSell-2(Check2-3MidCapCross)')
                    return True
                return False
        elif((low_tail_pct(regression_data) < 0.5 or (regression_data['forecast_day_PCT_change'] > 6 and low_tail_pct(regression_data) < 1))
            and 2 < high_tail_pct(regression_data) < 3.5
            and low_tail_pct(regression_data) < 0.5
            ):
            if(2 > regression_data['PCT_day_change'] > 0.5 and 2 > regression_data['PCT_change'] > 0
                ):
                if(is_algo_sell(regression_data)):
                    add_in_csv(regression_data, regressionResult, ws, 'ML:eveningStarSell-Risky-3(Check2-3MidCapCross)')
                    return True
                return False
    return False

def buy_oi_negative(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(regression_data['redtrend'] == -1
        and regression_data['forecast_day_PCT_change'] < 0
        and regression_data['forecast_day_PCT2_change'] < -0.5
        and regression_data['forecast_day_PCT3_change'] < -0.5
        and regression_data['forecast_day_PCT4_change'] < -0.5
        and regression_data['forecast_day_PCT5_change'] < -0.5
        and regression_data['forecast_day_PCT7_change'] < -0.5
        and ten_days_less_than_minus_ten(regression_data)
        and float(regression_data['forecast_day_VOL_change']) < -40
        and regression_data['PCT_day_change_pre1'] < regression_data['PCT_day_change']
        and float(regression_data['contract']) < 0
        and float(regression_data['oi']) < 5
        and (regression_data['yearHighChange'] < -15 or regression_data['yearLowChange'] < 15)
        ):
        if(is_algo_buy(regression_data)):
            if(((-1 < regression_data['PCT_day_change'] < 0 and -1 < regression_data['PCT_change'] < -0.5)
                or (-1 < regression_data['PCT_day_change'] < -0.5 and -1 < regression_data['PCT_change'] < 0))
                ):
                add_in_csv(regression_data, regressionResult, ws, 'ML:buyNegativeOI-0-checkBase(1%down)')
                return True
            if(-2 < regression_data['PCT_day_change'] < 0 and -2 < regression_data['PCT_change'] < 0
                ):
                add_in_csv(regression_data, regressionResult, ws, 'ML:buyNegativeOI-1-checkBase(1%down)')
                return True
        return False
    return False

def buy_day_low(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(regression_data['low'] < regression_data['low_pre1']
       and regression_data['bar_low'] < regression_data['bar_low_pre1']
       ):
        if((regression_data['PCT_day_change'] < -5 or regression_data['PCT_change'] < -5)
           and float(regression_data['forecast_day_VOL_change']) < -30
           and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
           and regression_data['PCT_day_change_pre1'] < -1.5
           and regression_data['forecast_day_PCT_change'] < -5
           and ten_days_less_than_minus_ten(regression_data)
           ):
            if(is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, 'ML:dayLowBuy')
                return True
            return False
        elif((regression_data['PCT_day_change'] < -5 or regression_data['PCT_change'] < -5)
           and float(regression_data['forecast_day_VOL_change']) < -30
           and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
           and regression_data['PCT_day_change_pre1'] < -1.5
           and regression_data['forecast_day_PCT_change'] < -4.5
           and regression_data['forecast_day_PCT10_change'] > 5
           ):
            add_in_csv(regression_data, regressionResult, ws, 'dayLowVolLowBuy-0')
            return True
        elif((regression_data['PCT_day_change'] < -5 or regression_data['PCT_change'] < -5)
           and float(regression_data['forecast_day_VOL_change']) < -20
           and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
           and regression_data['PCT_day_change_pre1'] < -1.5
           and regression_data['forecast_day_PCT_change'] < -5
           #and regression_data['forecast_day_PCT10_change'] < -5
           ):
            add_in_csv(regression_data, regressionResult, ws, 'dayLowVolLowSell-0')
            return True
        elif((regression_data['PCT_day_change'] < -5 or regression_data['PCT_change'] < -5)
           and float(regression_data['forecast_day_VOL_change']) < 0
           and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
           and regression_data['PCT_day_change_pre1'] < -1.5
           and regression_data['forecast_day_PCT10_change'] < -5
           ):
            if(regression_data['month6LowChange'] < -5
                and regression_data['forecast_day_PCT10_change'] < -10
                ):
                add_in_csv(regression_data, regressionResult, ws, 'dayLowVolLowBuy-01')
                return True
            elif(regression_data['month6LowChange'] > 10
                and regression_data['yearLowChange'] > 20
                ):
                add_in_csv(regression_data, regressionResult, ws, 'dayLowVolLowSell-01')
                return True
        elif((regression_data['PCT_day_change'] < -5 and regression_data['PCT_change'] < -4)
           and float(regression_data['forecast_day_VOL_change']) < -30
           and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
           and regression_data['PCT_day_change_pre1'] < -1.5
           and -20 < regression_data['SMA50'] < 10
           and regression_data['SMA9'] > -7
           #and regression_data['PCT_day_change_pre2'] < -1.5
           ):
            add_in_csv(regression_data, regressionResult, ws, 'dayLowVolLowBuy-02-checkMorningTrend(.5SL)')
            return True
        elif((regression_data['PCT_day_change'] < -5 and regression_data['PCT_change'] < -4)
           and float(regression_data['forecast_day_VOL_change']) < 0
           and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
           and -5 < regression_data['PCT_day_change_pre1'] < -1.5
           and regression_data['PCT_day_change_pre2'] > 1.5
           and regression_data['year2LowChange'] > 10
           ):
            add_in_csv(regression_data, regressionResult, ws, 'dayLowVolLowSell-02-checkMorningTrend(.5SL)')
            return True
        elif((regression_data['PCT_day_change'] < -4 and regression_data['PCT_change'] < -2)
           and float(regression_data['forecast_day_VOL_change']) < 0
           and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
           and regression_data['PCT_day_change_pre1'] < -1.5
           and regression_data['PCT_day_change_pre2'] < -1.5
           and -20 < regression_data['SMA50']
           and regression_data['SMA9'] > -7
           ):
            add_in_csv(regression_data, regressionResult, ws, 'dayLowVolLowSell-03-checkMorningTrend(.5SL)')
            return True
        elif((regression_data['PCT_day_change'] < -4 and regression_data['PCT_change'] < -2)
           and float(regression_data['forecast_day_VOL_change']) < 0
           and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
           and regression_data['PCT_day_change_pre1'] < -1.5
           and regression_data['PCT_day_change_pre2'] < -1.5
           ):
            if(is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, 'ML:dayLowVolLowBuy-03-checkMorningTrend(.5SL)-after10:30')
                return True
            return False
        elif((regression_data['PCT_day_change'] < -4 and regression_data['PCT_change'] < -2)
           and float(regression_data['forecast_day_VOL_change']) < 0
           and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
           and regression_data['PCT_day_change_pre1'] < -1.5
           and regression_data['PCT_day_change_pre2'] < -1.5
           ):
            if(is_algo_sell(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, 'ML:dayLowVolLowSell-03-checkMorningTrend(.5SL)')
                return True
            return False
        elif((regression_data['PCT_day_change'] < -4 and regression_data['PCT_change'] < -2)
           and float(regression_data['forecast_day_VOL_change']) < 0
           and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
           and regression_data['PCT_day_change_pre1'] < -1.5
           and regression_data['PCT_day_change_pre2'] > 1.5
           ):
            add_in_csv(regression_data, regressionResult, ws, None)
            return True
#     if((regression_data['PCT_day_change'] < -2 and regression_data['PCT_change'] < -2)
#        and float(regression_data['forecast_day_VOL_change']) < -30
#        and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
#        and regression_data['forecast_day_PCT7_change'] > 7
#        and regression_data['forecast_day_PCT10_change'] > 10
#        ):
#         add_in_csv(regression_data, regressionResult, ws, '##dayLowVolLowBuy-2')
#         return True
    return False

def buy_vol_contract(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if((ten_days_more_than_ten(regression_data) == False
        or ten_days_more_than_fifteen(regression_data) == True
        or (regression_data['forecast_day_PCT5_change'] < 5 and regression_data['forecast_day_PCT7_change'] < 5)) 
        #and ((mlpValue >= 0.3 and kNeighboursValue >= 0.3) or is_algo_buy(regression_data))
        and (float(regression_data['contract']) != 0 or float(regression_data['oi']) != 0)
        and float(regression_data['contract']) > 10
        and ((regression_data['PCT_day_change'] > 1 or regression_data['PCT_change'] > 1)
            or
            (regression_data['PCT_day_change'] > 0.75 and regression_data['PCT_change'] > 0.75
            and regression_data['forecast_day_PCT_change'] < 2
            and regression_data['forecast_day_PCT2_change'] < 2
            and regression_data['forecast_day_PCT3_change'] < 2
            and regression_data['forecast_day_PCT4_change'] < 2
            and regression_data['forecast_day_PCT4_change'] < 2
            and regression_data['forecast_day_PCT5_change'] < 2
            and regression_data['forecast_day_PCT7_change'] < 2
            and regression_data['forecast_day_PCT10_change'] < 2
            )
        )
        and regression_data['forecast_day_PCT_change'] > 0
        and regression_data['forecast_day_PCT2_change'] > 0
        and regression_data['forecast_day_PCT3_change'] > 0
        and 5 > regression_data['forecast_day_PCT4_change'] > 0
        and regression_data['forecast_day_PCT5_change'] < 5
        and regression_data['forecast_day_PCT7_change'] < 5
        and regression_data['forecast_day_PCT10_change'] < 5
        and (regression_data['PCT_day_change'] < 0
            or regression_data['PCT_day_change_pre1'] < 0
            or regression_data['PCT_day_change_pre2'] < 0
            or regression_data['PCT_day_change_pre3'] < 0
            or regression_data['PCT_day_change_pre4'] < 0
           )
        and regression_data['yearHighChange'] < -2
        and preDayPctChangeUp_orVolHigh(regression_data)
        and regression_data['open'] > 50
        and last_4_day_all_up(regression_data) == False
        and high_tail_pct(regression_data) < 1.5
        and regression_data['month3HighChange'] < -7.5
        and (regression_data['forecast_day_VOL_change'] > 150
            or (regression_data['PCT_day_change_pre2'] < 0
                and (((regression_data['volume'] - regression_data['volume_pre2'])*100)/regression_data['volume_pre2']) > 100
                and (((regression_data['volume'] - regression_data['volume_pre3'])*100)/regression_data['volume_pre3']) > 100
               )
           )
       ):
        if((regression_data['forecast_day_VOL_change'] > 70 and 0.5 < regression_data['PCT_day_change'] < 2 and 1 < regression_data['PCT_change'] < 2)
            and float(regression_data['contract']) > 10
            ):
            if((mlpValue >= 0.3 and kNeighboursValue >= 0.3) or is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, 'ML:buyOI-0')
                return True
            return False
        elif((regression_data['forecast_day_VOL_change'] > 35 and 0.5 < regression_data['PCT_day_change'] < 2 and 1 < regression_data['PCT_change'] < 2)
            and float(regression_data['contract']) > 20
            #and regression_data['PCT_day_change_pre1'] > -0.5
            ):
            if((mlpValue >= 0.3 and kNeighboursValue >= 0.3) or is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, 'ML:buyOI-1')
                return True
            return False
        elif((regression_data['forecast_day_VOL_change'] > 150 and 1 < regression_data['PCT_day_change'] < 3 and 1 < regression_data['PCT_change'] < 3)
            #and regression_data['PCT_day_change_pre1'] > -0.5
            ):
            if((mlpValue >= 0.3 and kNeighboursValue >= 0.3) or is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, 'ML:buyOI-2-checkBase')
                return True
            return False
        elif(((regression_data['forecast_day_VOL_change'] > 400 and 1 < regression_data['PCT_day_change'] < 3.5 and 1 < regression_data['PCT_change'] < 3.5)
            or (regression_data['forecast_day_VOL_change'] > 500 and 1 < regression_data['PCT_day_change'] < 4.5 and 1 < regression_data['PCT_change'] < 4.5)
            )
            #and regression_data['PCT_day_change_pre1'] > -0.5
            ):
            if((mlpValue >= 0.3 and kNeighboursValue >= 0.3) or is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, 'ML:buyOI-3-checkBase')
                return True
            return False    
        elif((regression_data['forecast_day_VOL_change'] > 500 and 1 < regression_data['PCT_day_change'] < 5 and 1 < regression_data['PCT_change'] < 5)
            and float(regression_data['contract']) > 50 
            and (regression_data['forecast_day_PCT10_change'] < -8 or regression_data['forecast_day_PCT7_change'] < -8)
            ):
            if((mlpValue >= 0.3 and kNeighboursValue >= 0.3) or is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, 'ML:buyOI-4-checkBase')
                return True
            return False    
    return False

def buy_vol_contract_contrarian(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(
        (float(regression_data['contract']) != 0 or float(regression_data['oi']) != 0)
        and (ten_days_more_than_ten(regression_data) == True and ten_days_more_than_fifteen(regression_data) == False 
             and (regression_data['forecast_day_PCT5_change'] > 5 and  regression_data['forecast_day_PCT7_change'] > 5))
        and float(regression_data['contract']) > 10
        #and (regression_data['PCT_day_change'] > 1 or regression_data['PCT_change'] > 1)
        #and regression_data['forecast_day_PCT_change'] > 0.5
        #and regression_data['forecast_day_PCT2_change'] > 0.5
        #and regression_data['forecast_day_PCT3_change'] > 0
        #and regression_data['forecast_day_PCT4_change'] > 0
        #and preDayPctChangeUp_orVolHigh(regression_data)
        and regression_data['open'] > 50
        #and last_7_day_all_up(regression_data) == False
        ):
        if((regression_data['forecast_day_VOL_change'] > 70 and 0.75 < regression_data['PCT_day_change'] < 2 and 0.5 < regression_data['PCT_change'] < 2)
            and float(regression_data['contract']) > 10
            ):
            add_in_csv(regression_data, regressionResult, ws, 'Reversal(Test):sellReversalOI-0(openAroundLastCloseAnd5MinuteChart)')
            return True
        elif((regression_data['forecast_day_VOL_change'] > 35 and 0.75 < regression_data['PCT_day_change'] < 2 and 0.5 < regression_data['PCT_change'] < 2)
            and float(regression_data['contract']) > 20
            ):
            add_in_csv(regression_data, regressionResult, ws, 'Reversal(Test):sellReversalOI-1(openAroundLastCloseAnd5MinuteChart)')
            return True
        elif((regression_data['forecast_day_VOL_change'] > 150 and 0.75 < regression_data['PCT_day_change'] < 3 and 0.5 < regression_data['PCT_change'] < 3)
            and regression_data['PCT_day_change_pre1'] > -0.5
            ):
            add_in_csv(regression_data, regressionResult, ws, 'Reversal(Test):sellReversalOI-2(openAroundLastCloseAnd5MinuteChart)')
            return True
        elif(((regression_data['forecast_day_VOL_change'] > 400 and 0.75 < regression_data['PCT_day_change'] < 3.5 and 0.5 < regression_data['PCT_change'] < 3.5)
            or (regression_data['forecast_day_VOL_change'] > 500 and 0.75 < regression_data['PCT_day_change'] < 4.5 and 0.5 < regression_data['PCT_change'] < 4.5)
            )
            and regression_data['forecast_day_PCT10_change'] > 10
            ):
            if(('P@[') in regression_data['buyIndia']):
                add_in_csv(regression_data, regressionResult, ws, 'Reversal(Test):sellReversalOI-3-checkBase-(openAroundLastCloseAnd5MinuteChart)')
                return True
            elif(preDayPctChangeUp_orVolHigh(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, 'Reversal(Test):buyContinueOI-3-checkBase-(openAroundLastCloseAnd5MinuteChart)')
                return True
        elif((regression_data['forecast_day_VOL_change'] > 500 and 0.75 < regression_data['PCT_day_change'] < 5 and 0.5 < regression_data['PCT_change'] < 5)
            and float(regression_data['contract']) > 50 
            and regression_data['forecast_day_PCT10_change'] > 10
            ):
            add_in_csv(regression_data, regressionResult, ws, 'Reversal(Test):sellReversalOI-4-checkBase-(openAroundLastCloseAnd5MinuteChart)')
            return True
#     if((('P@[' not in str(regression_data['buyIndia'])) and ('P@[' not in str(regression_data['sellIndia'])))
#         and (-2 < regression_data['PCT_day_change'] < 0 and -2 < regression_data['PCT_change'] < 0)
#         and kNeighboursValue >= 1
#         and mlpValue >= 0
#         and is_recent_consolidation(regression_data) == False
#         and str(regression_data['score']) == '10'
#         and (high_tail_pct(regression_data) < 1 and (high_tail_pct(regression_data) < low_tail_pct(regression_data)))
#         ):
#             add_in_csv(regression_data, regressionResult, ws, 'Reversal(Test):buyReversalKNeighbours(downTrend)(downLastDay)')
#             return True    
    return False

def buy_trend_reversal(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if((ten_days_less_than_minus_ten(regression_data)
        or (last_5_day_all_down_except_today(regression_data)
            and ten_days_less_than_minus_seven(regression_data)
            )
        )
        and regression_data['yearLowChange'] > 15 and regression_data['yearHighChange'] < -15
        ):
        if(regression_data['forecast_day_PCT_change'] > 0 and regression_data['PCT_day_change'] > 0
            and (regression_data['PCT_day_change_pre1'] > 1)
            and regression_data['PCT_day_change'] > regression_data['PCT_day_change_pre1'] > 0
            and regression_data['forecast_day_VOL_change'] <= 20
            ):
            if(1 < regression_data['PCT_day_change'] < 5 and 1 < regression_data['PCT_change'] < 5
                and regression_data['forecast_day_VOL_change'] <= -30
                ):
                add_in_csv(regression_data, regressionResult, ws, 'finalSellContinue-00')
                return True
            elif(3 < regression_data['PCT_day_change'] < 5 and 3 < regression_data['PCT_change'] < 5
                ):
                if(is_algo_buy(regression_data)):
                    add_in_csv(regression_data, regressionResult, ws, 'ML:finalBuyContinue-00')
                    return True
                return False
            elif(regression_data['forecast_day_PCT_change'] > 0
                and regression_data['forecast_day_VOL_change'] <= 0
                ):
                add_in_csv(regression_data, regressionResult, ws, 'finalBuyContinue-00')
                return True    

    if((-2.5 < regression_data['PCT_day_change'] <= -1)
        and (regression_data['PCT_change'] <= -0.75)
        and high_tail_pct(regression_data) < 1
        and 3 > low_tail_pct(regression_data) > 2
        and ('MayBuyCheckChart' in regression_data['filter1'])
        and ('Reversal' not in regression_data['filter3'])
        ):
        if(is_algo_buy(regression_data)
            and regression_data['PCT_day_change'] <= -0.5
            ):
            add_in_csv(regression_data, regressionResult, ws, "ML:(check-chart-2-3MidCapCross)MayBuyCheckChartML-0")
            return True
        elif(regression_data['PCT_day_change'] <= -0.5):
            add_in_csv(regression_data, regressionResult, ws, "(check-chart-2-3MidCapCross)MayBuyCheckChart")
            return True
        return False
    if(('MayBuyCheckChart' in regression_data['filter1'])
        and ('Reversal' not in regression_data['filter3'])
        and high_tail_pct(regression_data) < 0.5
        and ((((-2 <= regression_data['PCT_day_change'] < -1) and (-2 <= regression_data['PCT_change'] < 0))
                and 3 > low_tail_pct(regression_data) > 1.8
                )
             or
             (((-4 <= regression_data['PCT_day_change'] < -1.5) and (-4 <= regression_data['PCT_change'] < -1))
                and 5 > low_tail_pct(regression_data) > 2.8
                )
            )
        ):
        if(is_algo_buy(regression_data)):
            add_in_csv(regression_data, regressionResult, ws, "ML:(check-chart-2-3MidCapCross)MayBuyCheckChartML-1")
            return True
        return False
    
#     if((regression_data['PCT_day_change'] < 2 and low_tail_pct(regression_data) > 4)
#         #and regression_data['PCT_change'] <= 0
#         and -75 < regression_data['year2HighChange'] < -25
#         and low_tail_pct(regression_data) < 1
#         and ('MayBuyCheckChart' in regression_data['filter1']) 
#         and ('Reversal' not in regression_data['filter3'])
#         ):
#         add_in_csv(regression_data, regressionResult, ws, "Test:MayBuyCheckChart-HighTail(Check2-3MidCapCross)")
#         return True
#     
#     if((-0.5 < regression_data['PCT_day_change'] < 0.5)
#         and (-0.5 < regression_data['PCT_change'] < 0.5)
#         and high_tail_pct(regression_data) < 0.3
#         and (0.6 < low_tail_pct(regression_data) < 0.9)
#         and regression_data['PCT_day_change_pre1'] > 0
#         ):
#         add_in_csv(regression_data, regressionResult, ws, "Test:buyHighTailLessThan0.3-3(checkHillUp)")
        
    return False            

def buy_trend_break(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
#     if(regression_data['SMA200'] == 1
#        and regression_data['PCT_day_change'] > 2 and regression_data['PCT_change'] > 2
#        ):
#         add_in_csv(regression_data, regressionResult, ws, '##TestBreakOutBuyConsolidate-0')
#         return True
    flag = False
    if(NIFTY_LOW and low_tail_pct(regression_data) > 1.5
       and -1 < regression_data['PCT_change'] < 1 and -1 < regression_data['PCT_day_change'] < 1
       and regression_data['forecast_day_PCT10_change'] < 10
       ):
        add_in_csv(regression_data, regressionResult, ws, None, '##TEST:buyCheckLastHourUp')
        flag = True
        
#         if(2 < regression_data['month3LowChange'] < 10):
#             if(ten_days_less_than_minus_ten(regression_data)
#                and regression_data['forecast_day_PCT10_change'] < -15
#                and 5 > regression_data['PCT_day_change'] > 1 and 5 > regression_data['PCT_day_change'] > 1
#                #and regression_data['forecast_day_VOL_change'] > 50
#                and abs_yearHigh_more_than_yearLow(regression_data) == True
#                ):
#                 add_in_csv(regression_data, regressionResult, ws, '##BreakOutBuyCandidate(notUpLastDay)-1')
#                 return True
        
    if(0.5 < regression_data['forecast_day_PCT10_change'] < 2
        and regression_data['forecast_day_PCT_change'] > 1
        and 2 < regression_data['PCT_day_change'] < 5.5
        and 2 < regression_data['PCT_change'] < 5.5
        and regression_data['PCT_day_change_pre1'] > -0.5
        and 0.5 < high_tail_pct(regression_data) < 2
        and regression_data['buyIndia_avg'] > -0.75
        and regression_data['sellIndia_avg'] > -0.75
        and regression_data['month3LowChange'] > 4
        and ('P@[' not in regression_data['sellIndia'])
        and abs_month3High_more_than_month3Low(regression_data)
        and (abs(regression_data['month6HighChange']) > abs(regression_data['month6LowChange']))
        ):
        add_in_csv(regression_data, regressionResult, ws, 'buy-2week-breakoutup')
    elif(0.5 < regression_data['forecast_day_PCT10_change'] < 3
        #and regression_data['forecast_day_PCT_change'] > 1
        and 2 < regression_data['PCT_day_change']
        and 2 < regression_data['PCT_change']
        and regression_data['PCT_day_change_pre1'] > -0.5
        and 0.5 < high_tail_pct(regression_data) < 2
        #and regression_data['buyIndia_avg'] > -0.75
        #and regression_data['sellIndia_avg'] > -0.75
        #and regression_data['month3LowChange'] > 4
        #and ('P@[' not in regression_data['sellIndia'])
        and abs_month3High_more_than_month3Low(regression_data)
        and (abs(regression_data['month6HighChange']) > abs(regression_data['month6LowChange']))
        ):
        add_in_csv(regression_data, regressionResult, ws, 'sell-2week-breakoutup')
    elif(0.5 < regression_data['forecast_day_PCT10_change'] < 3
        and regression_data['forecast_day_PCT_change'] > 1
        and 2 < regression_data['PCT_day_change'] < 5.5
        and 2 < regression_data['PCT_change'] < 5.5
        and high_tail_pct(regression_data) < 2.5
        and regression_data['buyIndia_avg'] > -0.75
        and regression_data['sellIndia_avg'] > -0.75
        and regression_data['month3LowChange'] > 4
        and ('P@[' not in regression_data['sellIndia'])
        and abs_month3High_more_than_month3Low(regression_data)
        ):
        if(is_algo_buy(regression_data)):
            add_in_csv(regression_data, regressionResult, ws, 'ML:buy-2week-breakoutup')
            return True
        return False
    elif(0.5 < regression_data['forecast_day_PCT10_change'] < 3
        and regression_data['forecast_day_PCT_change'] > 1
        and 2 < regression_data['PCT_day_change'] < 5.5
        and 2 < regression_data['PCT_change'] < 5.5
        and high_tail_pct(regression_data) < 1
        and regression_data['buyIndia_avg'] > -0.75
        and regression_data['sellIndia_avg'] > -0.75
        and regression_data['month3LowChange'] > 4
        and regression_data['month3HighChange'] < -4
        ):
        add_in_csv(regression_data, regressionResult, ws, '(check-chart)buy-2week-breakoutup(|-|-| or --|)')
            
        
    #     if(regression_data['yearLowChange'] < 5):
#        if(regression_data['forecast_day_PCT_change'] > 3 and regression_data['PCT_day_change'] > 3
#            and abs(regression_data['PCT_day_change']) > abs(regression_data['PCT_day_change_pre1'])
#            #and regression_data['open'] == regression_data['low']
#            and regression_data['forecast_day_VOL_change'] >= -20
#            and high_tail_pct(regression_data) < 0.5
#            ):
#                add_in_csv(regression_data, regressionResult, ws, '##finalBreakOutBuy-1test-atYearLow')
#                flag = False
#     if(5 < regression_data['yearLowChange'] < 10 and abs_yearHigh_more_than_yearLow(regression_data)
#        and regression_data['forecast_day_PCT10_change'] < 10
#        and last_7_day_all_up(regression_data) == False
#        and high_tail_pct(regression_data) < 0.7
#        ):
#        if(3 > regression_data['forecast_day_PCT_change'] > 2 and 3 > regression_data['PCT_day_change'] > 2
#            and regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change_pre2'] > 0 and regression_data['PCT_day_change_pre3'] > 0
#            and (regression_data['open'] == regression_data['low'] or regression_data['forecast_day_VOL_change'] >= 0)
#            and regression_data['forecast_day_VOL_change'] >= -50
#            ):
#                add_in_csv(regression_data, regressionResult, ws, '##finalBreakOutBuyContinue-00-test-atYearLow')
#                flag = False
#        if(2 > regression_data['forecast_day_PCT_change'] > 0 and 2 > regression_data['PCT_day_change'] > 0
#            and regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change_pre2'] > 0 and regression_data['PCT_day_change_pre3'] > 0
#            and (regression_data['forecast_day_PCT_change'] > 0.75 or regression_data['PCT_day_change_pre1'] > 0.75 or regression_data['PCT_day_change_pre2'] > 0.75 or regression_data['PCT_day_change_pre3'] > 0.75)
#            and (regression_data['open'] == regression_data['low'] or regression_data['forecast_day_VOL_change'] >= 0)
#            and regression_data['forecast_day_VOL_change'] >= -50
#            ):
#                add_in_csv(regression_data, regressionResult, ws, '##finalBreakOutBuyContinue-0-test-atYearLow')
#                flag = False    
#     if(5 < regression_data['yearLowChange'] < 12 and abs_yearHigh_more_than_yearLow(regression_data)
#        and regression_data['forecast_day_PCT10_change'] < 10
#        and last_7_day_all_up(regression_data) == False
#        and high_tail_pct(regression_data) < 0.7
#        ):
#        if(3 > regression_data['forecast_day_PCT_change'] > 2 and 3 > regression_data['PCT_day_change'] > 2
#            and regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change_pre2'] > 0 and regression_data['PCT_day_change_pre3'] > 0
#            #and regression_data['open'] == regression_data['low']
#            and regression_data['forecast_day_VOL_change'] >= 0
#            ):
#                add_in_csv(regression_data, regressionResult, ws, '##finalBreakOutBuyContinue-11-test-atYearLow')
#                flag = False
#        if(2 > regression_data['forecast_day_PCT_change'] > 0 and 2 > regression_data['PCT_day_change'] > 0
#            and regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change_pre2'] > 0 and regression_data['PCT_day_change_pre3'] > 0
#            and (regression_data['forecast_day_PCT_change'] > 0.75 or regression_data['PCT_day_change_pre1'] > 0.75 or regression_data['PCT_day_change_pre2'] > 0.75 or regression_data['PCT_day_change_pre3'] > 0.75)
#            #and regression_data['open'] == regression_data['low']
#            and regression_data['forecast_day_VOL_change'] >= 0
#            ):
#                add_in_csv(regression_data, regressionResult, ws, '##finalBreakOutBuyContinue-1-test-atYearLow')
#                flag = False
    return flag   
     
def buy_final_candidate(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(regression_data['forecast_day_PCT4_change'] <= 0.5
        and regression_data['forecast_day_PCT5_change'] <= 0.5
        and regression_data['forecast_day_PCT7_change'] <= 0.5
        and (ten_days_less_than_minus_ten(regression_data)
             or (last_5_day_all_down_except_today(regression_data)
                 and ten_days_less_than_minus_seven(regression_data)
                 )
             )
        and regression_data['yearLowChange'] > 15 and regression_data['yearHighChange'] < -15
        and regression_data['month3LowChange'] > 3
        ):
        if(regression_data['forecast_day_PCT_change'] > 0
           and regression_data['bar_high'] > regression_data['bar_high_pre1']
           #and regression_data['forecast_day_VOL_change'] > 0
           ):
            if(2 < regression_data['PCT_day_change'] < 4 and 2 < regression_data['PCT_change'] < 4
                and regression_data['PCT_day_change_pre1'] < 0
                and regression_data['forecast_day_PCT10_change'] > -20
                and regression_data['month3HighChange'] < -15
                and regression_data['SMA4'] > 0
                and regression_data['SMA9'] > -3
                and high_tail_pct(regression_data) < 1.5
                ):
                add_in_csv(regression_data, regressionResult, ws, 'buyFinalCandidate-(lastDayDown)')
                return True
            elif(2 < regression_data['PCT_day_change'] < 4 and 2 < regression_data['PCT_change'] < 4
                and no_doji_or_spinning_buy_india(regression_data)
                and regression_data['PCT_day_change_pre1'] > 0
                and regression_data['forecast_day_PCT10_change'] > -20
                and regression_data['month3HighChange'] < -15
                and regression_data['forecast_day_VOL_change'] > -20
                and high_tail_pct(regression_data) < 1.5
                ):
                if(is_algo_buy(regression_data)):
                    add_in_csv(regression_data, regressionResult, ws, 'ML:buyFinalCandidate-(lastDayUp)')
                    return True
                return False
            elif(1 < regression_data['PCT_day_change'] < 4 and 1 < regression_data['PCT_change'] < 4
                and no_doji_or_spinning_buy_india(regression_data)
                and regression_data['PCT_day_change_pre1'] > 0
                and regression_data['forecast_day_VOL_change'] < -20
                ):
                add_in_csv(regression_data, regressionResult, ws, 'sellFinalContinue-(lastDayUp)-(volLow)')
                return True
            elif(1 < regression_data['PCT_day_change'] < 4 and 1 < regression_data['PCT_change'] < 4
                and regression_data['PCT_day_change_pre1'] < 0
                ):
                if(is_algo_sell(regression_data)):
                    add_in_csv(regression_data, regressionResult, ws, 'ML:sellFinalContinue-(lastDayDown)-1')
                    return True
                return False
            elif(1 < regression_data['PCT_day_change'] < 4 and 1 < regression_data['PCT_change'] < 4
                and regression_data['PCT_day_change_pre1'] > 0
                ):
                if('P@[' in regression_data['sellIndia']):
                    add_in_csv(regression_data, regressionResult, ws, 'buyFinalCandidate-(lastDayUp)-(sellPattern)')
                    return True
                elif('P@[' not in regression_data['buyIndia']):
                    add_in_csv(regression_data, regressionResult, ws, 'sellFinalContinue-(lastDayUp)-1')
                    return True
                return False
            elif(0.5 < regression_data['PCT_day_change'] < 2.5 and 0.5 < regression_data['PCT_change'] < 2.5
                and regression_data['PCT_day_change_pre1'] < 0
                ):
                if(is_algo_sell(regression_data)):
                    add_in_csv(regression_data, regressionResult, ws, 'ML:sellFinalContinue-(lastDayDown)-2')
                    return True
                return False
            elif(0.5 < regression_data['PCT_day_change'] < 2.5 and 0.5 < regression_data['PCT_change'] < 2.5
                and regression_data['PCT_day_change_pre1'] > 0
                ):
                if('P@[' in regression_data['sellIndia']):
                    add_in_csv(regression_data, regressionResult, ws, 'buyFinalCandidate-(lastDayUp)-(sellPattern)')
                    return True
                elif(is_algo_sell(regression_data)):
                    add_in_csv(regression_data, regressionResult, ws, 'ML:sellFinalContinue-(lastDayUp)-2')
                    return True
                return False
        if((((regression_data['close'] - regression_data['open']) * 1.5 > regression_data['high'] - regression_data['low']) or (regression_data['forecast_day_PCT_change'] > 0 and regression_data['PCT_day_change'] > 1))
            and (regression_data['yearHighChange'] < -30 or regression_data['yearLowChange'] < 30)
            ):
            if(1 < regression_data['PCT_day_change'] < 2.5 and 1 < regression_data['PCT_change'] < 2.5 
                and no_doji_or_spinning_sell_india(regression_data) and no_doji_or_spinning_buy_india(regression_data)
                ):
                if(regression_data['forecast_day_VOL_change'] > -20
                    ):
                    if(is_algo_buy(regression_data)):
                        add_in_csv(regression_data, regressionResult, ws, 'ML:buyFinalCandidate-2')
                        return True
                    return False
                elif(regression_data['forecast_day_VOL_change'] < -30
                    ):
                    if(is_algo_sell(regression_data)):
                        add_in_csv(regression_data, regressionResult, ws, 'ML:sellFinalContinue-2')
                        return True
                    return False
            if(1 < regression_data['PCT_day_change'] < 4 and 1 < regression_data['PCT_change'] < 4 
                and no_doji_or_spinning_sell_india(regression_data) and no_doji_or_spinning_buy_india(regression_data)
                ):
                if(regression_data['forecast_day_VOL_change'] < -30
                    ):
                    if(is_algo_buy(regression_data)):
                        add_in_csv(regression_data, regressionResult, ws, 'ML:buyFinalCandidate-3')
                        return True
                    return False
                elif(regression_data['forecast_day_VOL_change'] > 0
                    ):
                    if(is_algo_sell(regression_data)):
                        add_in_csv(regression_data, regressionResult, ws, 'ML:sellFinalContinue-3')
                        return True
                    return False
    return False
           
def buy_oi_candidate(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    tail_pct_filter(regression_data, regressionResult)
    tail_reversal_filter(regression_data, regressionResult)
    flag = False
    if(regression_data['close'] > 50
        and ((regression_data['PCT_change'] < 4 and high_tail_pct(regression_data) < 2)
            or (regression_data['PCT_change'] > 4 and high_tail_pct(regression_data) < 3)
            or (high_tail_pct(regression_data) < low_tail_pct(regression_data)))
        ):
        if(buy_base_line_buy(regression_data, regressionResult, reg, ws)):
            flag = True
    if(buy_trend_reversal(regression_data, regressionResult, reg, ws)
        and regression_data['close'] > 50
        ):
        flag = True
    if(breakout_or_no_consolidation(regression_data) == True):
        if buy_evening_star_sell(regression_data, regressionResult, reg, ws):
            flag = True
        if buy_morning_star_buy(regression_data, regressionResult, reg, ws):
            flag = True
        if buy_oi_negative(regression_data, regressionResult, reg, ws):
            flag = True
        if buy_day_low(regression_data, regressionResult, reg, ws):
            flag = True
        if buy_vol_contract(regression_data, regressionResult, reg, ws):
            flag = True
        if buy_vol_contract_contrarian(regression_data, regressionResult, reg, ws):
            flag = True
        if buy_trend_break(regression_data, regressionResult, reg, ws):
            flag = True
        if buy_final_candidate(regression_data, regressionResult, reg, ws):
            flag = True
    return flag

def buy_oi(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(((regression_data['PCT_day_change'] > 1 or regression_data['PCT_change'] > 1)
            or
            (regression_data['PCT_day_change'] > 0.75 and regression_data['PCT_change'] > 0.75
            and regression_data['forecast_day_PCT_change'] < 2
            and regression_data['forecast_day_PCT2_change'] < 2
            and regression_data['forecast_day_PCT3_change'] < 2
            and regression_data['forecast_day_PCT4_change'] < 2
            and regression_data['forecast_day_PCT4_change'] < 2
            and regression_data['forecast_day_PCT5_change'] < 2
            and regression_data['forecast_day_PCT7_change'] < 2
            and regression_data['forecast_day_PCT10_change'] < 2
            )
        )
        and regression_data['forecast_day_PCT_change'] > 0
        and regression_data['forecast_day_PCT2_change'] > 0
        and regression_data['forecast_day_PCT3_change'] > 0
        and 5 > regression_data['forecast_day_PCT4_change'] > 0
        and regression_data['forecast_day_PCT5_change'] < 5
        and regression_data['forecast_day_PCT7_change'] < 5
        and regression_data['forecast_day_PCT10_change'] < 5
        and (regression_data['PCT_day_change'] < 0
            or regression_data['PCT_day_change_pre1'] < 0
            or regression_data['PCT_day_change_pre2'] < 0
            or regression_data['PCT_day_change_pre3'] < 0
            or regression_data['PCT_day_change_pre4'] < 0
           )
        and (regression_data['forecast_day_VOL_change'] > 150
            or (regression_data['PCT_day_change_pre2'] < 0
                and (((regression_data['volume'] - regression_data['volume_pre2'])*100)/regression_data['volume_pre2']) > 100
                and (((regression_data['volume'] - regression_data['volume_pre3'])*100)/regression_data['volume_pre3']) > 100
               )
           )
        and float(regression_data['contract']) > 100
        and(regression_data['PCT_day_change_pre1'] > 0 
               or (regression_data['volume'] > regression_data['volume_pre2'] and regression_data['volume'] > regression_data['volume_pre3'])
            )
        and regression_data['yearHighChange'] < -5
        and regression_data['open'] > 50
        and (last_4_day_all_up(regression_data) == False)
        and (high_tail_pct(regression_data) < 1)
        and regression_data['month3HighChange'] < -7.5
        ):
        if(1 < regression_data['PCT_day_change'] < 2.5 and 1 < regression_data['PCT_change'] < 2.5       
        ):
            if(regression_data['forecast_day_PCT10_change'] < 0 or regression_data['forecast_day_PCT7_change'] < 0):
                add_in_csv(regression_data, regressionResult, ws, 'openInterest-0')
                return True
            elif(regression_data['forecast_day_PCT10_change'] < 10 or (regression_data['forecast_day_PCT5_change'] < 5 and regression_data['forecast_day_PCT7_change'] < 5)):
                add_in_csv(regression_data, regressionResult, ws, 'openInterest-1')
                return True
            else:
                add_in_csv(regression_data, regressionResult, ws, 'openInterest-2-Risky')
                return True
        if(1 < regression_data['PCT_day_change'] < 4 and 1 < regression_data['PCT_change'] < 4
            and float(regression_data['forecast_day_VOL_change']) > 300 
            ):
            if(regression_data['forecast_day_PCT10_change'] < 0 or regression_data['forecast_day_PCT7_change'] < 0):
                add_in_csv(regression_data, regressionResult, ws, 'openInterest-0-checkConsolidation')
                return True
            elif(regression_data['forecast_day_PCT10_change'] < 10 or (regression_data['forecast_day_PCT5_change'] < 5 and regression_data['forecast_day_PCT7_change'] < 5)):
                add_in_csv(regression_data, regressionResult, ws, 'openInterest-1-checkConsolidation')
                return True
            else:
                add_in_csv(regression_data, regressionResult, ws, 'openInterest-2-checkConsolidation-Risky')
                return True    
    return False

def buy_other_indicator(regression_data, regressionResult, reg, ws):
    if(regression_data['close'] > 50
        ):
        buy_up_trend(regression_data, regressionResult, reg, ws)
        buy_risingMA(regression_data, regressionResult, reg, ws)
        buy_study_risingMA(regression_data, regressionResult, reg, ws)
        buy_market_uptrend(regression_data, regressionResult, reg, ws)
        buy_check_chart(regression_data, regressionResult, reg, ws)
        buy_month3_high_continue(regression_data, regressionResult, reg, ws)
        buy_heavy_uptrend_reversal(regression_data, regressionResult, reg, ws)
        buy_supertrend(regression_data, regressionResult, reg, ws)
        return True
    return False

def buy_up_trend(regression_data, regressionResult, reg, ws_buyUpTrend):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    if((regression_data['yearLowChange'] > 20 and regression_data['month3LowChange'] > 15)
       and (regression_data['yearHighChange'] < -15 or regression_data['month3HighChange'] < -10)
       and regression_data['forecast_day_PCT_change'] > 0
       and regression_data['forecast_day_PCT2_change'] > 0
       and regression_data['forecast_day_PCT3_change'] > 0
       and (regression_data['PCT_day_change_pre1'] < 0 or regression_data['PCT_day_change_pre2'] < 0)
       ):
        if(regression_data['yearHighChange'] < -10
           and 2 < regression_data['PCT_day_change'] < 3.5 and 2 < regression_data['forecast_day_PCT_change'] < 3
           and regression_data['series_trend'] != 'downTrend'
           and str(regression_data['score']) != '0-1' 
           and regression_data['forecast_day_PCT7_change'] < 0 and -6 < regression_data['forecast_day_PCT10_change'] < 0
           and high_tail_pct(regression_data) > .5
           and regression_data['SMA25'] < 4
           ):
            add_in_csv(regression_data, regressionResult, None, 'sellUpTrend-0')
            return True
        elif(regression_data['yearHighChange'] < -10
           and 2 < regression_data['PCT_day_change'] < 3.5 and 2 < regression_data['forecast_day_PCT_change'] < 3
           and regression_data['series_trend'] != 'downTrend'
           and str(regression_data['score']) != '0-1' 
           and regression_data['forecast_day_PCT7_change'] < 0 and -6 < regression_data['forecast_day_PCT10_change'] < 0
           and 1 > low_tail_pct(regression_data) > .6
           and high_tail_pct(regression_data) < .5
           ):
            add_in_csv(regression_data, regressionResult, None, 'buyUpTrend-0')
            return True
        elif(
           regression_data['yearHighChange'] < -10
           and 2 < regression_data['PCT_day_change'] < 3.5 and regression_data['PCT_change'] < 3
           and regression_data['PCT_day_change_pre1'] < 0
           and regression_data['series_trend'] != 'downTrend'
           and str(regression_data['score']) != '0-1'
           and 3.5 > regression_data['forecast_day_PCT_change'] > 1
           and regression_data['forecast_day_PCT7_change'] > 4
           and regression_data['forecast_day_PCT10_change'] < 7
           and ('ENGULFING' not in regression_data['buyIndia'])
           and (regression_data['forecast_day_PCT4_change'] < 3 or ('[' in regression_data['buyIndia']))
           ):
            add_in_csv(regression_data, regressionResult, None, 'sellUpTrend-1')
            return True
        elif(
           regression_data['yearHighChange'] < -10
           and 2 < regression_data['PCT_day_change'] < 3.5 and regression_data['PCT_change'] < 3
           and regression_data['PCT_day_change_pre1'] < 0
           and regression_data['series_trend'] != 'downTrend'
           and str(regression_data['score']) != '0-1'
           and regression_data['forecast_day_PCT5_change'] < 3
           and regression_data['forecast_day_PCT7_change'] > 1.5
           and regression_data['forecast_day_PCT10_change'] < 7
           and regression_data['weekHighChange'] > -10
           and (('[' in regression_data['buyIndia'] and 'BELTHOLD' not in regression_data['buyIndia'] and 'LONGLINE' not in regression_data['buyIndia'])
                or ('[' not in regression_data['buyIndia'] and regression_data['SMA4_2daysBack'] < 2)
                )
           ):
            add_in_csv(regression_data, regressionResult, None, 'sellUpTrend-2')
            return True
        elif(
           abs_yearHigh_less_than_yearLow(regression_data)
           and regression_data['yearHighChange'] < -10
           and 2 < regression_data['PCT_day_change'] < 3.5 and 1.5 < regression_data['PCT_change'] < 3
           and regression_data['forecast_day_PCT_change'] < regression_data['PCT_change']
           and regression_data['PCT_day_change_pre1'] < 0
           and regression_data['series_trend'] != 'downTrend'
           and str(regression_data['score']) != '0-1'
           and regression_data['forecast_day_PCT5_change'] < 3
           and regression_data['forecast_day_PCT7_change'] < 1.5
           and regression_data['forecast_day_PCT10_change'] < 7
           and regression_data['month3HighChange'] < -2.5
           and '[' not in regression_data['sellIndia']
           ):
            add_in_csv(regression_data, regressionResult, None, 'buyUpTrend-1')
            return True
    elif((regression_data['yearHighChange'] < -9 or regression_data['yearLowChange'] < 15)
       and regression_data['forecast_day_PCT_change'] > 0
       and regression_data['forecast_day_PCT2_change'] > 0
       and regression_data['forecast_day_PCT3_change'] > 0    
       ):
        if(2 < regression_data['PCT_day_change'] < 4 and regression_data['PCT_change'] < 4
            and regression_data['forecast_day_PCT_change'] < regression_data['PCT_change']
            and regression_data['series_trend'] != 'downTrend'
            and str(regression_data['score']) != '0-1'
            and (regression_data['forecast_day_PCT7_change'] < 5 or regression_data['forecast_day_PCT10_change'] < 7)
            and 'P@[' in regression_data['sellIndia']
            ):
             if(is_algo_buy(regression_data)):
                 add_in_csv(regression_data, regressionResult, None, 'buyUpTrend-1-YearHigh')
                 return True
             return False
    return False

def buy_market_uptrend(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    if(('[' not in regression_data['sellIndia'])
        and ((1.5 < regression_data['PCT_change'] < 6) 
            and (1.5 < regression_data['PCT_day_change'] < 6)
            and regression_data['close'] > regression_data['bar_high_pre1']
            )
        and regression_data['SMA4_2daysBack'] > -1
        and regression_data['SMA4'] > -1
        and regression_data['SMA9'] > -10
        #and regression_data['trend'] == 'up'
        ):
        if(('year2LowReversal(Confirm)' in regression_data['filter3']) and (regression_data['year2HighChange'] < -40)):
            add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyYear2LowReversal(Confirm)')
        if(('yearLowReversal(Confirm)' in regression_data['filter3']) and (regression_data['yearHighChange'] < -30)):
            add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyYearLowReversal(Confirm)')
        if(('month6LowReversal(Confirm)' in regression_data['filter3']) and (regression_data['month6HighChange'] < -25)):
            add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyMonth6LowReversal(Confirm)')
        if(('month3LowReversal(Confirm)' in regression_data['filter3']) and (regression_data['month3HighChange'] < -15)):
            add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyMonth3LowReversal(Confirm)')
        if(regression_data['month3HighChange'] < -20 and (regression_data['month6HighChange'] < -20 or regression_data['yearHighChange'] < -30)
            ):
            if(('nearYear2Low' in regression_data['filter3']) and (regression_data['year2HighChange'] < -40)):
                add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyYear2Low')
            if(('nearYearLow' in regression_data['filter3']) and (regression_data['yearHighChange'] < -30)):
                add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyYearLow')
            if(('nearMonth6Low' in regression_data['filter3']) and (regression_data['month6HighChange'] < -25)):
                add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyMonth6Low')
            if(('nearMonth3Low' in regression_data['filter3']) and (regression_data['month3HighChange'] < -20)):
                add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyMonth3Low')
#         if(mlpValue > 0
#             and kNeighboursValue > 0
#             and ('P@' not in regression_data['sellIndia'])
#             and (((1 < regression_data['PCT_change'] < 4) and (1 < regression_data['PCT_day_change'] < 4))
#                 )
#             ):    
#             if('yearHighBreak' in regression_data['filter3']):
#                 add_in_csv(regression_data, regressionResult, ws, '##ALL:buyYearHighBreak')
#             if('month6HighBreak' in regression_data['filter3']):
#                 add_in_csv(regression_data, regressionResult, ws, '##ALL:buyMonth6HighBreak')
#             if('month3HighBreak' in regression_data['filter3']):
#                 add_in_csv(regression_data, regr

def buy_check_chart(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    #Check for last 5 from latest up should crossover
    if(('nearMonth3High' in regression_data['filter3']) 
        or ('month3HighBreak' in regression_data['filter3'])
        or ('month3HighReversal(Confirm)' in regression_data['filter3'])
        ):
        if(regression_data['month3LowChange'] > 15
            and ((-5 < regression_data['PCT_change'] < -1) and (-5 < regression_data['PCT_day_change'] < -2))
            and regression_data['close'] < regression_data['bar_low_pre1']
            and regression_data['close'] < regression_data['bar_low_pre2']
            ):
            if(regression_data['forecast_day_PCT5_change'] < 0):
                add_in_csv(regression_data, regressionResult, ws, '##(Check-chart-buy):month3High-InMinus')
            else:
                add_in_csv(regression_data, regressionResult, ws, '##(Check-chart-sell):month3High-InMinus')
    elif(('nearMonth6High' in regression_data['filter3']) 
        or ('month6HighReversal(Confirm)' in regression_data['filter3'])
        ):
        if(regression_data['month6LowChange'] > 20
            and ((-5 < regression_data['PCT_change'] < -1) and (-5 < regression_data['PCT_day_change'] < -2))
            and regression_data['close'] < regression_data['bar_low_pre1']
            and regression_data['close'] < regression_data['bar_low_pre2']
            ):
            if(regression_data['forecast_day_PCT5_change'] < 0):
                add_in_csv(regression_data, regressionResult, ws, '##(Check-chart-buy):month6High-InMinus')
            else:
                add_in_csv(regression_data, regressionResult, ws, '##(Check-chart-sell):month6High-InMinus')
    elif(('nearYearHigh' in regression_data['filter3']) 
        or ('YearHighReversal(Confirm)' in regression_data['filter3'])
        ):
        if(regression_data['month6LowChange'] > 20
            and ((-5 < regression_data['PCT_change'] < -1) and (-5 < regression_data['PCT_day_change'] < -2))
            and regression_data['close'] < regression_data['bar_low_pre1']
            and regression_data['close'] < regression_data['bar_low_pre2']
            ):
            if(regression_data['forecast_day_PCT5_change'] < 0):
                add_in_csv(regression_data, regressionResult, ws, '##(Check-chart-buy):YearHigh-InMinus')
            else:
                add_in_csv(regression_data, regressionResult, ws, '##(Check-chart-sell):YearHigh-InMinus')
                
    
    if(('nearMonth3High' in regression_data['filter3']) 
        or ('month3HighBreak' in regression_data['filter3'])
        #or ('month3HighReversal(Confirm)' in regression_data['filter3'])
        ):
        if(regression_data['month3LowChange'] > 15
            and ((-2 < regression_data['PCT_change']) and (-2 < regression_data['PCT_day_change'] < -1))
            and regression_data['PCT_day_change_pre1'] > 1.5
            and regression_data['PCT_change_pre1'] > 1.5
            and regression_data['PCT_day_change_pre2'] > 0.5
            and regression_data['close'] > regression_data['bar_low_pre1']
            and (abs(regression_data['PCT_day_change']) * 2 < abs(regression_data['PCT_day_change_pre1'])) 
            ):
            add_in_csv(regression_data, regressionResult, ws, '##(Check-chart-sell):month3High-InMinus-PCTChangeLessThan(-2)')
    elif(('nearMonth6High' in regression_data['filter3']) 
        or ('month6HighBreak' in regression_data['filter3'])
        #or ('month6HighReversal(Confirm)' in regression_data['filter3'])
        ):
        if(regression_data['month6LowChange'] > 20
            and ((-2 < regression_data['PCT_change']) and (-2 < regression_data['PCT_day_change'] < -1))
            and regression_data['PCT_day_change_pre1'] > 1.5
            and regression_data['PCT_change_pre1'] > 1.5
            and regression_data['PCT_day_change_pre2'] > 0.5
            and regression_data['close'] > regression_data['bar_low_pre1']
            and (abs(regression_data['PCT_day_change']) * 2 < abs(regression_data['PCT_day_change_pre1']))
            ):
            add_in_csv(regression_data, regressionResult, ws, '##(Check-chart-sell):month6High-InMinus-PCTChangeLessThan(-2)')
    
#         if((('nearYear2High' in regression_data['filter3']) 
#             or ('year2HighReversal(Confirm)' in regression_data['filter3'])
#             or ('year2HighBreak' in regression_data['filter3'])
#             )):    
#             if(regression_data['year2LowChange'] > 50
#                 and regression_data['year2HighChange'] > -1
#                 and ((regression_data['PCT_change'] > 1) and (regression_data['PCT_day_change'] > 1))
#                 and regression_data['close'] > regression_data['bar_high_pre1']
#                 ):
#                 if(regression_data['PCT_change'] > 4
#                     and ('year2HighBreak' in regression_data['filter3'])
#                     ):
#                     add_in_csv(regression_data, regressionResult, ws, '##(Check-chart-sell):year2High-InPlus')
#                 else:
#                     add_in_csv(regression_data, regressionResult, ws, '##(Check-chart):year2High-InPlus')
#                     
#         elif((('nearYearHigh' in regression_data['filter3'])
#             or ('yearHighReversal(Confirm)' in regression_data['filter3'])
#             or ('yearHighBreak' in regression_data['filter3'])
#             )):
#             if(regression_data['yearLowChange'] > 40
#                 and regression_data['yearHighChange'] > -1
#                 and ((regression_data['PCT_change'] > 1) and (regression_data['PCT_day_change'] > 1))
#                 and regression_data['close'] > regression_data['bar_high_pre1']
#                 ):
#                 if(regression_data['PCT_change'] > 4
#                     and ('yearHighBreak' in regression_data['filter3'])
#                     ):
#                     add_in_csv(regression_data, regressionResult, ws, '##(Check-chart-sell):yearHigh-InPlus')
#                 else:
#                     add_in_csv(regression_data, regressionResult, ws, '##(Check-chart):yearHigh-InPlus')
    
    if((-0.5 < regression_data['PCT_change'] < 0.5)
        and (-1 < regression_data['PCT_day_change'] < 0)
        and high_tail_pct(regression_data) < 0.5
        and (0.6 <= low_tail_pct(regression_data) < 1.5)
        and (low_tail_pct(regression_data) - high_tail_pct(regression_data)) >= 0.6
        #and (regression_data['score'] == '10')
        and (regression_data['PCT_day_change_pre1'] > 2)
        ):
        if(abs_month3High_more_than_month3Low(regression_data)
            ):
            add_in_csv(regression_data, regressionResult, ws, '##ALL(Check-chart):MayBuyCheckChart-(|`|_|)')
    elif(
        (((mlpValue > 0.3) and (kNeighboursValue > 0.3) and ((mlpValue_other > 0) or (kNeighboursValue_other > 0)))
             or ((mlpValue_other > 0.3) and (kNeighboursValue_other > 0.3) and ((mlpValue > 0) or (kNeighboursValue > 0))))
        and (-2.5 < regression_data['PCT_day_change'] <= -1)
        and (-4 < regression_data['PCT_change'] <= -1)
        ):
        if(('MayBuyCheckChart' in regression_data['filter1'])
            and (-15 < regression_data['forecast_day_PCT5_change'] < -1)
            and (-15 < regression_data['forecast_day_PCT7_change'] < -1)
            and (-15 < regression_data['forecast_day_PCT10_change'] < -1)
            and high_tail_pct(regression_data) < 0.8
            ):
            if(1.8 < low_tail_pct(regression_data) < 2.5):
                add_in_csv(regression_data, regressionResult, ws, '##ALL(Check-chart):MayBuyCheckChart-(IndexNotUpInSecondHalf)')

def buy_month3_high_continue(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    if(('nearMonth3High' in regression_data['filter3']) 
        or ('month3HighBreak' in regression_data['filter3'])
        or ('month3HighReversal(Confirm)' in regression_data['filter3'])
        ):
        if((regression_data['forecast_day_PCT4_change'] < 0)
            and (regression_data['forecast_day_PCT5_change'] < 0)
            and (regression_data['forecast_day_PCT7_change'] < 0)
            and ((regression_data['forecast_day_PCT_change'] > 0 and (2 < regression_data['PCT_change'] < 3) and (2 < regression_data['PCT_day_change'] < 3))
                 or (regression_data['series_trend'] == "downTrend" and (1.5 < regression_data['PCT_change'] < 3) and (1.5 < regression_data['PCT_day_change'] < 3)))
            and regression_data['high'] > regression_data['high_pre1']
            and regression_data['bar_high'] > regression_data['bar_high_pre1']
            #and regression_data['SMA4_2daysBack'] < 0
            ):
            if(regression_data['SMA4_2daysBack'] > 0.5 and regression_data['SMA9_2daysBack'] > 0.5
                and (regression_data['SMA4_2daysBack'] > 1 or regression_data['SMA9_2daysBack'] > 1)
                and ('[') not in regression_data['sellIndia']
                ):
                add_in_csv(regression_data, regressionResult, ws, '##ALL:(Check-chart)buyMonth3High-Continue')
                return True
            elif(regression_data['SMA4_2daysBack'] < -0.5 and regression_data['SMA9_2daysBack'] < -0.5
                ):
                add_in_csv(regression_data, regressionResult, ws, '##ALL:(Check-chart)sellMonth3High-Continue')
                return True
            elif(is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, '##ALL:(Check-chart)ML:buyMonth3High-Continue')
                return True
            elif(is_algo_sell(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, '##ALL:(Check-chart)ML:sellMonth3High-Continue')
                return True
            return False
    return False

def buy_heavy_uptrend_reversal(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    if(regression_data['series_trend'] == "upTrend"
        and (0 < regression_data['forecast_day_PCT4_change'] < 15)
        and (0 < regression_data['forecast_day_PCT5_change'] < 15)
        and (0 < regression_data['forecast_day_PCT7_change'] < 15)
        and (regression_data['forecast_day_PCT10_change'] < 15)
        ):
#             if((regression_data['month3HighChange'] < -5)
#                 and ((0 < regression_data['PCT_change'] < 5) and (0 < regression_data['PCT_day_change'] < 5))
#                 ):
#                 if((4 < regression_data['PCT_change'] < 5) and (4 < regression_data['PCT_day_change'] < 5)
#                 ):
#                     add_in_csv(regression_data, regressionResult, ws, '##ALL:buyHeavyUpTrend-0-Continue')
#                 elif(ten_days_more_than_seven(regression_data)
#                      and (('nearMonth3High' in regression_data['filter3']) 
#                           or ('nearMonth6High' in regression_data['filter3'])
#                          )
#                 ):
#                     add_in_csv(regression_data, regressionResult, ws, '##ALL:buyHeavyUpTrend-1-Continue')
        if((regression_data['month3HighChange'] > -5)
            and ((0 < regression_data['PCT_change'] < 5) and (0 < regression_data['PCT_day_change'] < 5))
            and regression_data['PCT_day_change_pre1'] > 1
            ):
            if((2 < regression_data['PCT_change'] < 7) and (3 < regression_data['PCT_day_change'] < 7)
                and ten_days_more_than_seven(regression_data)
                and (('nearMonth3High' in regression_data['filter3']) 
                      or ('month3HighBreak' in regression_data['filter3'])
                      or ('nearMonth6High' in regression_data['filter3'])
                      or ('month6HighBreak' in regression_data['filter3'])
                    )
            ):
                if(regression_data['month6HighChange'] > -5
                    and (3 < regression_data['PCT_change'] or 3 < regression_data['PCT_day_change'])
                    ):
                    add_in_csv(regression_data, regressionResult, ws, '##ALL:sellHeavyUpTrend-Reversal')
                else:
                    if(regression_data['forecast_day_VOL_change'] < 0):
                        add_in_csv(regression_data, regressionResult, ws, '##ALL:buyHeavyUpTrend-Reversal-(Risky)')
                    else:
                        add_in_csv(regression_data, regressionResult, ws, '##ALL:sellHeavyUpTrend-Reversal-(Risky)')
        
def buy_supertrend(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    
    if(regression_data['close'] > 50
        ):
        if(0 < regression_data['forecast_day_PCT2_change'] < regression_data['forecast_day_PCT3_change'] < regression_data['forecast_day_PCT4_change'] < regression_data['forecast_day_PCT5_change']
            and regression_data['forecast_day_PCT5_change'] > 5
            and regression_data['forecast_day_PCT10_change'] < regression_data['forecast_day_PCT5_change']
            and regression_data['forecast_day_PCT10_change'] < regression_data['forecast_day_PCT7_change']
            and -0.5 < regression_data['PCT_day_change_pre1'] < 1.5
            and -0.5 < regression_data['PCT_day_change'] < 0.5
            and regression_data['yearHighChange'] < -5
            and regression_data['yearLowChange'] > 15
            and regression_data['month3LowChange'] > 10    
            #and regression_data['low'] > regression_data['low_pre1']
            ):
            if((regression_data['forecast_day_PCT_change'] < 0
                    and regression_data['PCT_day_change'] < 0
                    and regression_data['SMA4'] < 1.5
                    and high_tail_pct(regression_data) < 1.5
                    and regression_data['low'] > regression_data['low_pre1']
                )
                ):
                add_in_csv(regression_data, regressionResult, ws, '##ALL(Test):buySuperTrend-0')
            elif('SPINNINGTOP' in regression_data['sellIndia']
                and regression_data['low'] > regression_data['low_pre1']
                ):
                add_in_csv(regression_data, regressionResult, ws, '##ALL(Test):sellSuperTrend-0')
            elif(regression_data['PCT_day_change_pre2'] > 2
                and regression_data['PCT_change_pre2'] > 2
                and regression_data['low'] < regression_data['low_pre1']
                ):
                add_in_csv(regression_data, regressionResult, ws, '##ALL(Test):buySuperTrend-2')
            elif(regression_data['PCT_day_change_pre2'] < 0.5
                and regression_data['PCT_change_pre2'] < 0.5
                and regression_data['low'] < regression_data['low_pre1']
                ):
                add_in_csv(regression_data, regressionResult, ws, '##ALL(Test):sellSuperTrend-1')
            elif((('P@' or 'M@') in regression_data['sellIndia'])
                 or(regression_data['month3HighChange'] > 1
                    and 'Break' in regression_data['filter3']
                    and regression_data['forecast_day_PCT_change'] > 0.35
                    )
                 or(regression_data['month3HighChange'] < -25
                    and regression_data['month6HighChange'] < -30
                    )
                 or('P@[,SPINNINGTOP]' in regression_data['buyIndia']
                    and regression_data['month3HighChange'] < 0
                    and regression_data['yearHighChange'] < -20
                    )
                 or('[' not in regression_data['buyIndia']
                    and -20 < regression_data['month3HighChange'] < -10
                    and 5 < regression_data['forecast_day_PCT7_change'] < 12
                    )
                ):
                add_in_csv(regression_data, regressionResult, ws, '##ALL(Test):sellSuperTrend-2')
            elif(5 > regression_data['month3HighChange'] > 0.45
                or (regression_data['PCT_day_change'] < 0
                   and regression_data['month3LowChange'] < 25
                   and regression_data['year2HighChange'] < -10
                   and regression_data['year2HighChange'] < -30
                   )
                ):
                add_in_csv(regression_data, regressionResult, ws, '##ALL(Test):buySuperTrend-1')
        elif(0 < regression_data['forecast_day_PCT2_change'] < regression_data['forecast_day_PCT3_change'] < regression_data['forecast_day_PCT4_change'] < regression_data['forecast_day_PCT5_change']
            and regression_data['forecast_day_PCT5_change'] > 5
            and -0.5 < regression_data['PCT_day_change_pre1'] < 1.5
            and -0.5 < regression_data['PCT_day_change'] < 0.5
            and regression_data['yearHighChange'] < -5
            and regression_data['yearLowChange'] > 15
            and regression_data['month3LowChange'] > 10    
            #and regression_data['low'] > regression_data['low_pre1']
            ):
            if('SPINNINGTOP' in regression_data['sellIndia']
                and regression_data['year2LowChange'] > 50
                and regression_data['low'] > regression_data['low_pre1']
                ):
                add_in_csv(regression_data, regressionResult, ws, '##ALL(Test):buySuperTrend-0')
            elif(regression_data['PCT_day_change_pre2'] > 2
                and regression_data['PCT_change_pre2'] > 2
                and regression_data['yearHighChange'] < -20
                and regression_data['low'] < regression_data['low_pre1']
                ):
                add_in_csv(regression_data, regressionResult, ws, '##ALL(Test):buySuperTrend-1')
            elif(((('P@' or 'M@') in regression_data['sellIndia'])
                 or(regression_data['month3HighChange'] > 1
                    and 'Break' in regression_data['filter3']
                    and regression_data['forecast_day_PCT_change'] > 0.35
                    )
                 or(regression_data['month3HighChange'] < -25
                    and regression_data['month6HighChange'] < -30
                    )
                 )
                 and regression_data['PCT_day_change_pre1'] < 1
                 and ('P@' or 'M@') in regression_data['buyIndia']
                ):
                add_in_csv(regression_data, regressionResult, ws, '##ALL(Test):sellSuperTrend-0')
            elif((regression_data['PCT_day_change'] < 0
                   and regression_data['PCT_change_pre1'] > 1
                   and regression_data['month3LowChange'] < 25
                   and regression_data['year2HighChange'] < -10
                   and regression_data['year2HighChange'] < -30
                   )
                ):
                add_in_csv(regression_data, regressionResult, ws, '##ALL(Test):sellSuperTrend-1')  
            elif(0 < regression_data['forecast_day_PCT2_change'] < regression_data['forecast_day_PCT3_change'] < regression_data['forecast_day_PCT4_change'] < regression_data['forecast_day_PCT5_change']
                and regression_data['forecast_day_PCT5_change'] > 5
                and regression_data['forecast_day_PCT10_change'] > regression_data['forecast_day_PCT5_change']
                and regression_data['forecast_day_PCT10_change'] > regression_data['forecast_day_PCT7_change']
                and -0.5 < regression_data['PCT_day_change_pre1'] < 1.5
                and -0.5 < regression_data['PCT_day_change'] < 0.5
                and regression_data['yearHighChange'] < -5
                ):
                if(regression_data['forecast_day_PCT_change'] < 0
                    and regression_data['month3HighChange'] < 0
                    and ('P@' or 'M@') in regression_data['buyIndia']
                    ):
                    add_in_csv(regression_data, regressionResult, ws, '##ALL(Test):sellSuperTrend-1')
                elif(regression_data['PCT_day_change'] < 0
                    and regression_data['low'] < regression_data['low_pre1']
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None)
                elif(regression_data['PCT_day_change'] < 0
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None)
                elif(('[') not in regression_data['buyIndia']):
                    add_in_csv(regression_data, regressionResult, ws, '##ALL(Test):sellSuperTrend-1')
        return True
    return False

def buy_risingMA(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    
    if(regression_data['close'] > 50
        ):        
        if(regression_data['SMA25'] > 0
            and 0 < regression_data['SMA50'] < 10
            and regression_data['SMA200'] < regression_data['SMA100'] < 0
            and -70 < regression_data['SMA200'] < -25
            #and regression_data['PCT_day_change'] < -1.5
            and regression_data['PCT_change'] < -1.5
            #and regression_data['series_trend'] != "downTrend"
            #and all_day_pct_change_negative_except_today(regression_data) != True
            and regression_data['month3HighChange'] < -5 
            ):
            if(regression_data['PCT_day_change_pre1'] > 1
                and regression_data['SMA4'] > -2
                and '[' not in regression_data['sellIndia']
                ):
                add_in_csv(regression_data, regressionResult, ws, '##ALL:buyRisingMA')
                return True
            elif(regression_data['PCT_day_change_pre1'] < -1
                and -5 < regression_data['PCT_day_change'] < -1
                and all_day_pct_change_negative_except_today(regression_data) != True
                ):
                add_in_csv(regression_data, regressionResult, ws, '##ALL:sellRisingMA')
                return True
            elif(regression_data['PCT_day_change_pre1'] > 1
                and regression_data['SMA50'] < 1
                ):
                add_in_csv(regression_data, regressionResult, ws, '##ALL:sellRisingMA')
                return True
            elif(is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, '##ALL:ML:BuyRisingMA-Risky-0')
                return True
            elif(is_algo_sell(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, '##ALL:ML:SellRisingMA-Risky-0')
                return True
            return False
        elif(regression_data['SMA4_2daysBack'] > 0
            and regression_data['SMA9'] > 0
            and 2 < regression_data['SMA50'] < 10
            and regression_data['SMA200'] < regression_data['SMA100'] < 0
            and -70 < regression_data['SMA200'] < -10
            #and regression_data['PCT_day_change'] < -1.5
            and regression_data['PCT_change'] < -1.5
            #and regression_data['series_trend'] != "downTrend"
            #and all_day_pct_change_negative_except_today(regression_data) != True
            ):
            if(-4 < regression_data['PCT_day_change'] < -1
                and regression_data['forecast_day_PCT4_change'] < 10
                and ('[' not in regression_data['sellIndia'])
                ):
                add_in_csv(regression_data, regressionResult, ws, '##ALL:buyRisingMA-1')
                return True
            elif(('P@' or 'M@') in regression_data['buyIndia']):
                add_in_csv(regression_data, regressionResult, ws, '##ALL:sellRisingMA-1')
                return True
            elif(is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, '##ALL:ML:BuyRisingMA-Risky-1')
                return True
            elif(is_algo_sell(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, '##ALL:ML:SellRisingMA-Risky-1')
                return True
            return False
        elif(regression_data['SMA4_2daysBack'] > 0
            and regression_data['SMA9'] > 1
            and regression_data['SMA25'] > 1
            and 1 < regression_data['SMA50'] < 3
            and regression_data['SMA200'] < regression_data['SMA100'] < -1
            and -70 < regression_data['SMA200'] < -15
            and regression_data['PCT_day_change'] < 0
            and regression_data['PCT_change'] < 0
            and regression_data['series_trend'] != "downTrend"
            and all_day_pct_change_negative_except_today(regression_data) != True
            ):
            if(is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, '##ALL:ML:BuyRisingMA-Risky-2')
                return True
            elif(is_algo_sell(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, '##ALL:ML:SellRisingMA-Risky-2')
                return True
            return False
        elif(1 < regression_data['SMA9'] < 5
            and 1 < regression_data['SMA25'] < 5
            and regression_data['SMA50'] < 0
            and regression_data['SMA200'] < regression_data['SMA100'] < regression_data['SMA50']
            and regression_data['SMA200'] < -10
            and 2 < regression_data['PCT_day_change']
            and 1.5 < regression_data['PCT_change']
            and regression_data['year2HighChange'] < -40
            and regression_data['series_trend'] != "downTrend"
            and all_day_pct_change_negative_except_today(regression_data) != True
            ):
            if (regression_data['month3LowChange'] > 20
                and ('P@[' or 'M@[') in regression_data['buyIndia']
                ):
                add_in_csv(regression_data, regressionResult, ws, '##ALL:sellRisingMAuptrend-0')
                return True
            elif(regression_data['month3LowChange'] < 10
                and ('P@[' or 'M@[') in regression_data['buyIndia']
                ):
                add_in_csv(regression_data, regressionResult, ws, '##ALL:sellRisingMAuptrend-1')
                return True
            elif(high_tail_pct(regression_data) > 1.5
                and regression_data['month6HighChange'] > -80
                and ('P@[' or 'M@[') not in regression_data['buyIndia']
                ):
                add_in_csv(regression_data, regressionResult, ws, '##ALL:sellRisingMAuptrend-2')
                return True
            elif(2 < regression_data['PCT_day_change'] < 4
                and 1.5 < regression_data['PCT_change'] < 4
                and regression_data['forecast_day_PCT7_change'] > 0
                and regression_data['forecast_day_PCT10_change'] > 0
                and (regression_data['month6HighChange'] > -80 and regression_data['month3HighChange'] > -80)
                and ('P@[' or 'M@[') in regression_data['buyIndia']
                #and is_algo_buy(regression_data)
                ):
                add_in_csv(regression_data, regressionResult, ws, '##ALL:buyRisingMAuptrend-(Risky)')
                return True
            elif(2 < regression_data['PCT_day_change'] < 4
                and 1.5 < regression_data['PCT_change'] < 4
                and regression_data['forecast_day_PCT7_change'] > 0
                and regression_data['forecast_day_PCT10_change'] > 0
                and (regression_data['month6HighChange'] < -80 or regression_data['month3HighChange'] < -80)
                ):
                if(is_algo_buy(regression_data)):
                    add_in_csv(regression_data, regressionResult, ws, '##ALL:ML:buyRisingMAuptrend-Risky')
                    return True
                elif(is_algo_sell(regression_data)):
                    add_in_csv(regression_data, regressionResult, ws, '##ALL:ML:sellRisingMAuptrend-Risky')
                    return True
                return False
        elif(regression_data['SMA200'] < regression_data['SMA100'] < regression_data['SMA50'] < regression_data['SMA25'] < regression_data['SMA9']
            ):
            if((((regression_data['PCT_change'] + regression_data['PCT_change_pre1'])  < -4
                and (regression_data['PCT_change'] < -3.5 or regression_data['PCT_change_pre1'] < -3.5)
                )
                )
                and regression_data['PCT_change'] < 0
                and regression_data['year2HighChange'] < -40
                and -5 < regression_data['SMA25'] < 0
                and ('[') not in regression_data['sellIndia']
                and regression_data['series_trend'] != "downTrend"
                and all_day_pct_change_negative_except_today(regression_data) != True
                ):
                add_in_csv(regression_data, regressionResult, ws, '##ALL:buyRisingMA-down-0')
                return True
            elif((((regression_data['PCT_change'] + regression_data['PCT_change_pre1'])  < -4
                and (regression_data['PCT_change'] < -3.5 or regression_data['PCT_change_pre1'] < -3.5)
                )
                )
                and regression_data['PCT_change'] < 0
                and regression_data['year2HighChange'] < -40
                and -5 < regression_data['SMA25'] < 0
                ):
                add_in_csv(regression_data, regressionResult, ws, '##ALL:sellRisingMA-down-(Risky)')
                return True
            elif((
                -4 < regression_data['PCT_change'] < -2
                )
                and regression_data['year2HighChange'] < -30
                and -2.5 < regression_data['SMA9'] < 2
                and -5 < regression_data['SMA25'] < 0
                ):
                if(is_algo_buy(regression_data)):
                    add_in_csv(regression_data, regressionResult, ws, '##ALL:ML:buyRisingMA-down-Risky')
                    return True
                elif(is_algo_sell(regression_data)):
                    add_in_csv(regression_data, regressionResult, ws, '##ALL:ML:sellRisingMA-down-Risky')
                    return True
                return False
#         elif(regression_data['SMA200'] < regression_data['SMA100'] < regression_data['SMA50'] < regression_data['SMA25']
#             and regression_data['SMA25'] > 0
#             and regression_data['SMA50'] < 2
#             and regression_data['SMA100'] < 0
#             and regression_data['SMA200'] < 0
#             and regression_data['year2HighChange'] < -40
#             and regression_data['series_trend'] != "downTrend"
#             and all_day_pct_change_negative_except_today(regression_data) != True
#             ):
#             if(-2 < regression_data['PCT_change'] < -0.5
#                 and -2 < regression_data['PCT_change'] < -1
#                 ):
#                 add_in_csv(regression_data, regressionResult, ws, 'ALL(Test):buyRisingMA-uptrend-SMA25gt0')
                #add_in_csv(regression_data, regressionResult, ws, None)
        
        if((('nearYear2Low' in regression_data['filter3']) 
            or ('nearYearLow' in regression_data['filter3'])
            or ('nearMonth6Low' in regression_data['filter3'])
            or ('year2LowReversal(Confirm)' in regression_data['filter3'])
            or ('yearLowReversal(Confirm)' in regression_data['filter3'])
            or ('month6LowReversal(Confirm)' in regression_data['filter3'])
            or ('year2LowBreak' in regression_data['filter3'])
            or ('yearLowBreak' in regression_data['filter3'])
            or ('month6LowBreak' in regression_data['filter3'])
            )
            and regression_data['SMA200'] < regression_data['SMA100'] < regression_data['SMA50'] < regression_data['SMA25'] < regression_data['SMA9']
            and regression_data['series_trend'] == "upTrend"
            ):
    #             if(((-3 < regression_data['PCT_change'] < 0) and (-3 < regression_data['PCT_day_change'] < 0))
    #                 and regression_data['SMA4'] > 0.5
    #                 and regression_data['SMA25'] > -10
    #                 and ('[') not in regression_data['sellIndia']
    #                 ):
    #                 add_in_csv(regression_data, regressionResult, ws, '##ALL:(Test)buyBottomReversal-0')
            if(((-3 < regression_data['PCT_change'] < 0) and (-3 < regression_data['PCT_day_change'] < 0))
                ):
                if(is_algo_buy(regression_data)):
                    add_in_csv(regression_data, regressionResult, ws, '##ALL:ML:buyBottomReversal-1')
                    return True
                return False
    #             elif(((-3 < regression_data['PCT_change'] < -1.5) and (-3 < regression_data['PCT_day_change'] < -1.5))
    #                 ):
    #                 add_in_csv(regression_data, regressionResult, ws, '##UPTREND:(Test)buyBottomReversal-2')
     
            
    #             elif(regression_data['PCT_day_change_pre2'] < 0 and (regression_data['PCT_day_change'] > 1.5)):
    #                 add_in_csv(regression_data, regressionResult, ws, '##ALL:(Test)buyBottomReversal-1')
        return True

def buy_study_risingMA(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    if(regression_data['SMA200'] < regression_data['SMA100'] < regression_data['SMA50'] < regression_data['SMA25'] < regression_data['SMA9']
    ):
        add_in_csv(regression_data, regressionResult, ws, '$$(Study)$$:RisingMA')
        if(-5 < regression_data['SMA25'] < 0):
            add_in_csv(regression_data, regressionResult, ws, '##LONGTERM:NearSMA25')
        elif(0 < regression_data['SMA25'] < 5):
            add_in_csv(regression_data, regressionResult, ws, '##LONGTERM:CrossoverSMA25')
        elif(-5 < regression_data['SMA50'] < 0):
            add_in_csv(regression_data, regressionResult, ws, '##MEDIUMTERM:NearSMA50')
        elif(0 < regression_data['SMA50'] < 5):
            add_in_csv(regression_data, regressionResult, ws, '##MEDIUMTERM:CrossoverSMA50')
        elif(-5 < regression_data['SMA100'] < 0):
            add_in_csv(regression_data, regressionResult, ws, '##SHORTTERM:NearSMA100')
        elif(0 < regression_data['SMA100'] < 5):
            add_in_csv(regression_data, regressionResult, ws, '##SHORTTERM:CrossoverSMA100')

def buy_test(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    
    if(regression_data['close'] < 50
        ):
        return False
    
    flag = buy_up_trend(regression_data, regressionResult, reg, ws)
    return flag
    return False    

def buy_all_common(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    buy_other_indicator(regression_data, regressionResult, reg, ws)

    if((-5 < regression_data['PCT_day_change'] < -3) and (regression_data['PCT_change'] < -1.5)
        and regression_data['PCT_day_change'] < regression_data['PCT_change']
        and (((mlpValue > 0.3) and (kNeighboursValue > 0.3) and ((mlpValue_other > 0) or (kNeighboursValue_other > 0)))
             or ((mlpValue_other > 0.3) and (kNeighboursValue_other > 0.3) and ((mlpValue > 0) or (kNeighboursValue > 0))))
        ):
        if('P@' not in regression_data['sellIndia']):
            add_in_csv(regression_data, regressionResult, ws, '##Common(Test):buyDayReversalCandidate-0')
        else:
            add_in_csv(regression_data, regressionResult, ws, '##Common(Test):buyDayReversalCandidate-1')
    
    if((((mlpValue > 0.3) and (kNeighboursValue > 0.3) and ((mlpValue_other > 0) or (kNeighboursValue_other > 0)))
             or ((mlpValue_other > 0.3) and (kNeighboursValue_other > 0.3) and ((mlpValue > 0) or (kNeighboursValue > 0))))
        ):
        if((-3 < regression_data['PCT_day_change'] < -1) and (regression_data['forecast_day_PCT10_change'] > 5)
            and low_tail_pct(regression_data) > 2
            and high_tail_pct(regression_data) < 1.5
            ):
                add_in_csv(regression_data, regressionResult, ws, '##Common:MayBuyCheckChart-0')
    
#     if((1 < regression_data['PCT_day_change'] < 4
#         and (regression_data['PCT_day_change'] > 1.5 or regression_data['PCT_change'] > 1.5)
#         and high_tail_pct(regression_data) < 0.3
#         )
#         and mlpValue >= 0 and kNeighboursValue >= 0
#         and (mlpValue_other >= 0 or kNeighboursValue_other >= 0)
#         ):
#         if (regression_data['PCT_day_change_pre1'] < 0):
#             add_in_csv(regression_data, regressionResult, ws, "##Common:buyHighTailLessThan0.3-0(checkHillUp)")
#         elif((regression_data['PCT_day_change_pre1'] < 1) and regression_data['PCT_day_change_pre2'] < 0):
#             add_in_csv(regression_data, regressionResult, ws, "##Common:buyHighTailLessThan0.3-1(checkHillUp)")
#         elif((regression_data['PCT_day_change'] < 2) and low_tail_pct(regression_data) < 0.3):
#             add_in_csv(regression_data, regressionResult, ws, "##Common:buyHighTailLessThan0.3-2(checkHillUp)")
            
    if((mlpValue > 0) 
        and (kNeighboursValue > 0) 
        and (mlpValue_other > 0) 
        and (kNeighboursValue_other > 0)
        and regression_data['PCT_day_change_pre1'] < 0
        and (1 < regression_data['PCT_day_change'] < 3) and (2 < regression_data['PCT_change'] < 2.5)
        and regression_data['month3HighChange'] < -10
        and regression_data['month3LowChange'] > 10
        ):    
        if(regression_data['SMA9'] > 1):
            add_in_csv(regression_data, regressionResult, ws, '##Common:buyNotM3HighLow-0(SMA9GT1)')
        elif(regression_data['SMA25'] > 0):
            add_in_csv(regression_data, regressionResult, ws, '##Common:buyNotM3HighLow-0(SMA25GT0)')  
        else:
            add_in_csv(regression_data, regressionResult, ws, None)
            
    if((((mlpValue > 0.3) and (kNeighboursValue > 0.3) and ((mlpValue_other > 0) or (kNeighboursValue_other > 0)))
             or ((mlpValue_other > 0.3) and (kNeighboursValue_other > 0.3) and ((mlpValue > 0) or (kNeighboursValue > 0))))
        and (regression_data['PCT_day_change_pre1'] < 0 or regression_data['PCT_day_change_pre2'] < 0)
        and (1 < regression_data['PCT_day_change'] < 4.5) and (1 < regression_data['PCT_change'] < 4.5)
        and regression_data['yearHighChange'] < -10
        and regression_data['yearLowChange'] > 10
        and abs_month3High_less_than_month3Low(regression_data)
        ):    
        if(regression_data['SMA9'] > 1):
            add_in_csv(regression_data, regressionResult, ws, '##Common:buyNotM3HighLow-1(SMA9GT1)')
        elif(regression_data['SMA25'] > 0):
            add_in_csv(regression_data, regressionResult, ws, '##Common:buyNotM3HighLow-1(SMA25GT0)')  
        else:
            add_in_csv(regression_data, regressionResult, ws, None)
            
            
                
    if(mlpValue > 0
        and kNeighboursValue > 0
        and ('P@' not in regression_data['sellIndia'])
        and (((2 < regression_data['PCT_change'] < 6) and (2 < regression_data['PCT_day_change'] < 6))
             or ((-4 < regression_data['PCT_day_change'] < 0) 
                 and (-4 < regression_data['PCT_change'] < 0.5)
                 and mlpValue_other > -0.5
                 and kNeighboursValue_other > -0.5
                 and (mlpValue_other > 0.5 or kNeighboursValue_other > 0.5)
                 ))
        #and regression_data['trend'] == 'up'
        ):
        if(('year2LowReversal(Confirm)' in regression_data['filter3']) and (regression_data['year2HighChange'] < -40)):
            add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyYear2LowReversal(Confirm)')
        if(('yearLowReversal(Confirm)' in regression_data['filter3']) and (regression_data['yearHighChange'] < -30)):
            add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyYearLowReversal(Confirm)')
        if(('month6LowReversal(Confirm)' in regression_data['filter3']) and (regression_data['month6HighChange'] < -25)):
            add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyMonth6LowReversal(Confirm)')  
        if(('nearYear2Low' in regression_data['filter3']) and (regression_data['year2HighChange'] < -40)):
            add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyYear2Low')
        if(('nearYearLow' in regression_data['filter3']) and (regression_data['yearHighChange'] < -30)):
            add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyYearLow')
        if(('nearMonth6Low' in regression_data['filter3']) and (regression_data['month6HighChange'] < -25)):
            add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyMonth6Low')
        
#     if(mlpValue > 0
#         and kNeighboursValue > 0
#         and ('P@' not in regression_data['sellIndia'])
#         and (((1 < regression_data['PCT_change'] < 4) and (1 < regression_data['PCT_day_change'] < 4))
#             )
#         ):    
#         if('yearHighBreak' in regression_data['filter3']):
#             add_in_csv(regression_data, regressionResult, ws, '##Common:buyYearHighBreak')
#         if('month6HighBreak' in regression_data['filter3']):
#             add_in_csv(regression_data, regressionResult, ws, '##Common:buyMonth6HighBreak')
#         if('month3HighBreak' in regression_data['filter3']):
#             add_in_csv(regression_data, regressionResult, ws, '##Common:buyMonth3HighBreak')
    return False

def buy_all_filter(regression_data, regressionResult, reg, ws_buyAllFilter):
    flag = False
    if buy_year_high(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws_buyAllFilter, None)
        flag = True
    if buy_year_low(regression_data, regressionResult, reg, None, None):
        add_in_csv(regression_data, regressionResult, ws_buyAllFilter, None)
        flag = True
    if buy_up_trend(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws_buyAllFilter, None)
        flag = True
    if buy_down_trend(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws_buyAllFilter, None)
        flag = True
    if buy_final(regression_data, regressionResult, reg, None, None):
        add_in_csv(regression_data, regressionResult, ws_buyAllFilter, None)
        flag = True
    if buy_high_indicators(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws_buyAllFilter, None)
        flag = True
    if buy_pattern(regression_data, regressionResult, reg, None, None):
        add_in_csv(regression_data, regressionResult, ws_buyAllFilter, None)
        flag = True
    if buy_oi(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws_buyAllFilter, None)
        flag = True
    return flag

def sell_pattern_without_mlalgo(regression_data, regressionResult, ws_buyPattern2, ws_sellPattern2):
    if(regression_data['yearHighChange'] < -10 and regression_data['sellIndia_count'] > 1):
        if(regression_data['sellIndia_avg'] < -1.5 and low_tail_pct(regression_data) < 1.5):
            add_in_csv(regression_data, regressionResult, None, 'sellPatterns')
        elif(regression_data['sellIndia_avg'] < -0.9 and low_tail_pct(regression_data) < 1.5
            and regression_data['PCT_day_change'] > 2
            and (regression_data['PCT_day_change'] > 1 or regression_data['sellIndia_count'] > 5)
            ):
            add_in_csv(regression_data, regressionResult, None, 'sellPatterns-1')
    elif(regression_data['sellIndia_avg'] < -0.9 and low_tail_pct(regression_data) < 1.5):
        add_in_csv(regression_data, regressionResult, None, None)
        #add_in_csv(regression_data, regressionResult, None, 'sellPatterns-1-Risky')
    
    if(regression_data['yearLowChange'] < -10 and regression_data['sellIndia_count'] > 1):
        if(regression_data['sellIndia_avg'] > 1.5 and high_tail_pct(regression_data) < 1.5):
            add_in_csv(regression_data, regressionResult, None, 'buyPatterns')
        elif(regression_data['sellIndia_avg'] > 0.9 and high_tail_pct(regression_data) < 1.5
            and regression_data['PCT_day_change'] < -2
            and (regression_data['PCT_day_change'] < -1 or regression_data['buyIndia_count'] > 5)
            ):
            add_in_csv(regression_data, regressionResult, None, 'buyPatterns-1')
    elif(regression_data['sellIndia_avg'] > 0.9 and high_tail_pct(regression_data) < 1.5):
        add_in_csv(regression_data, regressionResult, None, None)
        #add_in_csv(regression_data, regressionResult, None, 'buyPatterns-1-Risky')
        
    if(regression_data['sellIndia_avg'] < -1.25 and regression_data['sellIndia_count'] > 1
        and low_tail_pct(regression_data) < 1.5
        and regression_data['SMA9'] < -1
        ):
        add_in_csv(regression_data, regressionResult, None, 'sellPatterns-(SMA9LT-1)')
    
    sellPatternsDict=scrip_patterns_to_dict('../../data-import/nselist/all-buy-filter-by-PCT-Change.csv')
    if regression_data['sellIndia'] != '' and regression_data['sellIndia'] in sellPatternsDict:
        if (abs(float(sellPatternsDict[regression_data['sellIndia']]['avg'])) >= .1 and float(sellPatternsDict[regression_data['sellIndia']]['count']) >= 2):
            if(-3 < regression_data['PCT_day_change'] < 0.5 and float(sellPatternsDict[regression_data['sellIndia']]['avg']) < -1):
                avg = sellPatternsDict[regression_data['sellIndia']]['avg']
                count = sellPatternsDict[regression_data['sellIndia']]['count']
                #add_in_csv_hist_pattern(regression_data, regressionResult, ws_sellPattern2, 'wml_sell', avg, count)
            if(-0.5 < regression_data['PCT_day_change'] < 3 and float(sellPatternsDict[regression_data['sellIndia']]['avg']) > 1): 
                avg = sellPatternsDict[regression_data['sellIndia']]['avg']
                count = sellPatternsDict[regression_data['sellIndia']]['count']
                #add_in_csv_hist_pattern(regression_data, regressionResult, ws_buyPattern2, 'wml_sell', avg, count)

def sell_pattern_from_history(regression_data, ws_sellPattern2):
    sellPatternsDict=scrip_patterns_to_dict('../../data-import/nselist/patterns-sell.csv')
    sellIndiaAvg = 0
    regression_data['buyIndia_avg'] = 0
    regression_data['buyIndia_count'] = 0
    regression_data['sellIndia_avg'] = 0
    regression_data['sellIndia_count'] = 0
    flag = False
    if regression_data['sellIndia'] != '' and regression_data['sellIndia'] in sellPatternsDict: 
        regression_data['sellIndia_avg'] = float(sellPatternsDict[regression_data['sellIndia']]['avg'])
        regression_data['sellIndia_count'] = float(sellPatternsDict[regression_data['sellIndia']]['count'])
        if (abs(float(sellPatternsDict[regression_data['sellIndia']]['avg'])) >= .1):
            sellIndiaAvg = float(sellPatternsDict[regression_data['sellIndia']]['avg'])
            if(int(sellPatternsDict[regression_data['sellIndia']]['count']) >= 2):
                if(is_algo_sell(regression_data)
                    and 'P@[' not in str(regression_data['buyIndia'])
                    and regression_data['trend'] != 'down'
                    and -3 < regression_data['PCT_day_change'] < 0.5):
                    avg = sellPatternsDict[regression_data['sellIndia']]['avg']
                    count = sellPatternsDict[regression_data['sellIndia']]['count']
                    if(float(sellPatternsDict[regression_data['sellIndia']]['avg']) < -1 and int(sellPatternsDict[regression_data['sellIndia']]['count']) >= 5):
                        flag = True
                        #add_in_csv_hist_pattern(regression_data, regressionResult, ws_sellPattern2, 'sellPattern2', avg, count) 
                    if(float(sellPatternsDict[regression_data['sellIndia']]['avg']) < -0.5 
                        or (float(sellPatternsDict[regression_data['sellIndia']]['avg']) < -0.3 and (ten_days_more_than_ten(regression_data) or regression_data['yearLowChange'] > 40))):
                        if(regression_data['forecast_day_PCT10_change'] > 0 and regression_data['forecast_day_PCT_change'] <= 0):
                            flag = True
                            #add_in_csv_hist_pattern(regression_data, regressionResult, ws_sellPattern2, 'sellPattern2', avg, count)
                        elif(regression_data['forecast_day_PCT10_change'] < 0):    
                            flag = True
                            #add_in_csv_hist_pattern(regression_data, regressionResult, ws_sellPattern2, 'sellPattern2', avg, count)
    return sellIndiaAvg, flag

def sell_all_rule(regression_data, regressionResult, sellIndiaAvg, ws_sellAll):
    sell_other_indicator(regression_data, regressionResult, True, None)
    if(is_algo_sell(regression_data)
        and ((regression_data['PCT_day_change'] < -1 
                and low_tail_pct(regression_data) < 2
                and ('P@[' not in str(regression_data['buyIndia']))
                ) 
             or (high_tail_pct(regression_data) > 1.5 
                and (low_tail_pct(regression_data) < high_tail_pct(regression_data))
                )
             or (regression_data['PCT_day_change'] > 2
                and regression_data['forecast_day_PCT_change'] < -0.3
                )
            )
        and (SELL_VERY_LESS_DATA or regression_data['PCT_change'] < 1)
        and (SELL_VERY_LESS_DATA or ((regression_data['PCT_day_change_pre1'] > 0) or (regression_data['forecast_day_VOL_change'] > 0))) #Uncomment1 If very less data
        and (SELL_VERY_LESS_DATA or (regression_data['bar_low']-regression_data['low']) < (regression_data['bar_high']-regression_data['bar_low']))
        and sellIndiaAvg <= 0.70
        and ((last_7_day_all_down(regression_data) == False) or (regression_data['forecast_day_PCT10_change'] > -10))
        and (MARKET_IN_DOWNTREND or (last_4_day_all_down(regression_data) == False)) #Uncomment0 If very less data
        and breakout_or_no_consolidation(regression_data) == True
        and regression_data['close'] > 50
        ):
        if((7.5 < regression_data['month3LowChange'] < 25)
            and (-25 < regression_data['month3HighChange'] < -7.5)
            and regression_data['PCT_day_change'] > -1
            and 2 > regression_data['PCT_day_change'] > -1
            and 2 > regression_data['PCT_change'] > -1
            and (-10 < regression_data['forecast_day_PCT3_change'] < 0)
            and (-10 < regression_data['forecast_day_PCT4_change'] < 0)
            and (-10 < regression_data['forecast_day_PCT5_change'] < 0)
            and (-10 < regression_data['forecast_day_PCT7_change'] < 0)
            and (-15 < regression_data['forecast_day_PCT10_change'] < 0)
            and high_tail_pct(regression_data) > 1.5
            and low_tail_pct(regression_data) < 1
            ):
            add_in_csv(regression_data, regressionResult, None, '##ALL(Test):upLastDay-DownTrend')
        if(high_tail_pct(regression_data) < 2.5
           and regression_data['low'] < regression_data['low_pre1']
           ):
            if(regression_data['PCT_day_change'] > 0 and regression_data['PCT_change'] > 0
                and regression_data['month3LowChange'] > 15  
                ):
                add_in_csv(regression_data, regressionResult, None, 'MLSell-0')
#             elif(regression_data['PCT_day_change'] > -2.5 and regression_data['PCT_change'] > -0.5
#                 and (regression_data['PCT_day_change'] > 0 or regression_data['PCT_day_change_pre1'] > 0)
#                 and regression_data['month3LowChange'] > 5
#                 ):
#                 add_in_csv(regression_data, regressionResult, None, 'DOWNTREND:MLSell-1')
#             elif(regression_data['PCT_day_change'] > -2.5 and regression_data['PCT_change'] > -1
#                 and (regression_data['PCT_day_change'] > 0 or regression_data['PCT_day_change_pre1'] > 0)
#                 and regression_data['month3LowChange'] > 5
#                 ):
#                 add_in_csv(regression_data, regressionResult, None, 'DOWNTREND:MLSell-2')
        add_in_csv(regression_data, regressionResult, ws_sellAll, None)
        return True
    elif(is_algo_buy(regression_data)
        and ((regression_data['PCT_day_change'] > 1 
                and high_tail_pct(regression_data) < 2 
                and ('P@[' not in str(regression_data['sellIndia']))
                )
             or (low_tail_pct(regression_data) > 1.5 
                and (high_tail_pct(regression_data) < low_tail_pct(regression_data))
                )
             or (regression_data['PCT_day_change'] < -2
                and regression_data['forecast_day_PCT_change'] > 0.3
                )
            )
        and (BUY_VERY_LESS_DATA or regression_data['PCT_change'] > -1)
        and (BUY_VERY_LESS_DATA or ((regression_data['PCT_day_change_pre1'] < 0) or (regression_data['forecast_day_VOL_change'] > 0))) #Uncomment1 If very less data
        and (BUY_VERY_LESS_DATA or (regression_data['high']-regression_data['bar_high']) < (regression_data['bar_high']-regression_data['bar_low']))
        and sellIndiaAvg >= -.70
        and ((last_7_day_all_up(regression_data) == False) or (regression_data['forecast_day_PCT10_change'] < 10))
        and (MARKET_IN_UPTREND or (last_4_day_all_up(regression_data) == False)) #Uncomment0 If very less data
        and breakout_or_no_consolidation(regression_data) == True
        and regression_data['close'] > 50
        ):
        if(-5 < regression_data['PCT_day_change'] < -2
            and -5 < regression_data['PCT_change'] < -2
            and low_tail_pct(regression_data) > 1.5
            and high_tail_pct(regression_data) < 1):
            add_in_csv(regression_data, regressionResult, None, 'Test:MLBuyFromLowData')
    return False

def sell_all_rule_classifier(regression_data, regressionResult, sellIndiaAvg, ws_sellAll):
    sell_other_indicator(regression_data, regressionResult, False, None)
    if(is_algo_sell_classifier(regression_data)
        and ((regression_data['PCT_day_change'] < -1 
                and low_tail_pct(regression_data) < 2
                and ('P@[' not in str(regression_data['buyIndia']))
                ) 
             or (high_tail_pct(regression_data) > 1.5 
                and (low_tail_pct(regression_data) < high_tail_pct(regression_data))
                )
             or (regression_data['PCT_day_change'] > 2
                and regression_data['forecast_day_PCT_change'] < -0.3
                )
            )
        and (SELL_VERY_LESS_DATA or regression_data['PCT_change'] < 1)
        and (SELL_VERY_LESS_DATA or ((regression_data['PCT_day_change_pre1'] > 0) or (regression_data['forecast_day_VOL_change'] > 0))) #Uncomment1 If very less data
        and (SELL_VERY_LESS_DATA or (regression_data['bar_low']-regression_data['low']) < (regression_data['bar_high']-regression_data['bar_low']))
        and sellIndiaAvg <= 0.70
        and ((last_7_day_all_down(regression_data) == False) or (regression_data['forecast_day_PCT10_change'] > -10))
        and (MARKET_IN_DOWNTREND or (last_4_day_all_down(regression_data) == False)) #Uncomment0 If very less data
        and breakout_or_no_consolidation(regression_data) == True
        and regression_data['close'] > 50
        ):
        add_in_csv(regression_data, regressionResult, ws_sellAll, None)
        return True
    return False
      
def sell_year_high(regression_data, regressionResult, reg, ws_sellYearHigh, ws_sellYearHigh1):
    return False
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(-10 < regression_data['yearHighChange'] < -1 and regression_data['yearLowChange'] > 30 and -5 < regression_data['PCT_day_change'] < -0.75 
        and ten_days_more_than_ten(regression_data) and regression_data['forecast_day_PCT7_change'] > 5 and regression_data['forecast_day_PCT5_change'] > -0.5 and regression_data['forecast_day_PCT4_change'] > -0.5
        and regression_data['forecast_day_PCT2_change'] < 0 and regression_data['forecast_day_PCT_change'] < 0
        and float(regression_data['forecast_day_VOL_change']) > 0
        ):
        add_in_csv(regression_data, regressionResult, ws_sellYearHigh, 'sellYearHigh')
        return True
    elif(-10 < regression_data['yearHighChange'] < 0 and regression_data['yearLowChange'] > 30 
        and (regression_data['PCT_day_change'] < 0 and regression_data['PCT_change'] < 0.5)
        and regression_data['forecast_day_PCT10_change'] > 5 and regression_data['forecast_day_PCT7_change'] > 3 and regression_data['forecast_day_PCT5_change'] > -0.5
        and regression_data['forecast_day_PCT2_change'] < 0 and regression_data['forecast_day_PCT_change'] < 0
        and float(regression_data['forecast_day_VOL_change']) > 0
        ):
        add_in_csv(regression_data, regressionResult, ws_sellYearHigh1, 'sellYearHigh1')
        return True
    elif(-10 < regression_data['yearHighChange'] < 0 and regression_data['yearLowChange'] > 30 
        and (regression_data['PCT_day_change'] < 0 and regression_data['PCT_change'] < 0.5)
        and regression_data['forecast_day_PCT10_change'] > 0 and regression_data['forecast_day_PCT7_change'] > 0 and regression_data['forecast_day_PCT5_change'] > 0
        and regression_data['forecast_day_PCT2_change'] < 0 and regression_data['forecast_day_PCT_change'] < 0
        and float(regression_data['forecast_day_VOL_change']) > 0
        ):
        add_in_csv(regression_data, regressionResult, ws_sellYearHigh1, 'sellYearHigh1')
        return True   
    return False

def sell_year_low(regression_data, regressionResult, reg, ws_sellYearLow):
    return False
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(0 < regression_data['yearLowChange'] < 2 and regression_data['yearHighChange'] < -30 
        and -2 < regression_data['PCT_day_change'] < 0 and regression_data['forecast_day_PCT_change'] < 0
        and (str(regression_data['score']) != '1-1' or str(regression_data['score']) != '10')
        and all_day_pct_change_negative(regression_data) and no_doji_or_spinning_sell_india(regression_data)
        and float(regression_data['forecast_day_VOL_change']) > 30
        and regression_data['PCT_day_change_pre1'] < 0.5
        ):
        add_in_csv(regression_data, regressionResult, ws_sellYearLow, 'sellYearLow')
        return True
    return False

def sell_up_trend(regression_data, regressionResult, reg, ws_sellUpTrend):
    return False
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(all_day_pct_change_positive_except_today(regression_data)
       and regression_data['forecast_day_PCT_change'] < 0 
       and -4 < regression_data['PCT_day_change'] < 0 and regression_data['PCT_change'] < 0
       and regression_data['yearLowChange'] > 30
       and low_tail_pct(regression_data) < 0.5
       ):
        if (last_5_day_all_up_except_today(regression_data)
            and ten_days_more_than_ten(regression_data)
            and regression_data['forecast_day_PCT7_change'] > 5
            and regression_data['forecast_day_PCT10_change'] > 10
            ):
            add_in_csv(regression_data, regressionResult, ws_sellUpTrend, 'sellUpTrend-0(Risky)')
            return True
        elif(last_5_day_all_up_except_today(regression_data)
            and ten_days_more_than_seven(regression_data)
            and regression_data['forecast_day_PCT7_change'] > 4
            and regression_data['forecast_day_PCT10_change'] > 4
            ):
            add_in_csv(regression_data, regressionResult, ws_sellUpTrend, 'sellUpTrend-1')
            return True
        elif(regression_data['forecast_day_PCT7_change'] > 4
            and regression_data['forecast_day_PCT10_change'] > 4
            ):
            add_in_csv(regression_data, regressionResult, ws_sellUpTrend, 'sellUpTrend-2(Risky)')
            return True
    return False

def sell_down_trend(regression_data, regressionResult, reg, ws_sellDownTrend):
    return False
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if((regression_data['yearHighChange'] < -20 and regression_data['month3HighChange'] < -15)
       and (regression_data['yearLowChange'] > 15 or regression_data['month3LowChange'] > 10)
       and regression_data['forecast_day_PCT_change'] < 0
       and regression_data['forecast_day_PCT2_change'] < 0
       and regression_data['forecast_day_PCT3_change'] < 0
       and (regression_data['PCT_day_change_pre1'] > 0 or regression_data['PCT_day_change_pre2'] > 0)
       ):
        if(abs_yearHigh_less_than_yearLow(regression_data)
           and -4 < regression_data['PCT_day_change'] < -2 and -4 < regression_data['forecast_day_PCT_change'] < -2
           and regression_data['PCT_change'] < regression_data['PCT_day_change'] - 0.2
           and regression_data['forecast_day_PCT_change'] < regression_data['PCT_day_change'] - 0.2
           and regression_data['series_trend'] != 'upTrend'
           and str(regression_data['score']) != '10' 
           and ten_days_more_than_ten(regression_data)
           ):
            add_in_csv(regression_data, regressionResult, None, 'sellDownTrend-0')
            return True
        if(abs_yearHigh_less_than_yearLow(regression_data)
           and -4 < regression_data['PCT_day_change'] < -2 and -4 < regression_data['forecast_day_PCT_change'] < -2
           and regression_data['PCT_change'] < regression_data['PCT_day_change'] - 0.2
           and regression_data['forecast_day_PCT_change'] < regression_data['PCT_day_change'] - 0.2
           and regression_data['series_trend'] != 'upTrend'
           and str(regression_data['score']) != '10' 
           and (regression_data['forecast_day_PCT7_change'] > 0 and regression_data['forecast_day_PCT10_change'] > 0)
           ):
            add_in_csv(regression_data, regressionResult, None, 'sellDownTrend-00')
            return True
        if(abs_yearHigh_less_than_yearLow(regression_data)
           and regression_data['yearLowChange'] > 10 
           and -4 < regression_data['PCT_day_change'] < -2 and -4 < regression_data['forecast_day_PCT_change'] < -2
           and regression_data['forecast_day_PCT_change'] > regression_data['PCT_change']
           and regression_data['PCT_day_change_pre1'] > 0
           and regression_data['series_trend'] != 'upTrend'
           and str(regression_data['score']) != '10'
           and regression_data['forecast_day_PCT5_change'] > -3
           and (regression_data['forecast_day_PCT7_change'] > -5 and regression_data['forecast_day_PCT10_change'] > -7) 
           ):
            add_in_csv(regression_data, regressionResult, None, '##Test:longDownTrend-0-IndexNotDownLastDay(checkBase)')
            return True
        if(abs_yearHigh_less_than_yearLow(regression_data)
           and regression_data['yearLowChange'] > 10 
           and -4 < regression_data['PCT_day_change'] < -2 and -4 < regression_data['forecast_day_PCT_change'] 
           and regression_data['forecast_day_PCT_change'] > regression_data['PCT_change']
           and regression_data['series_trend'] != 'upTrend'
           and str(regression_data['score']) != '10'
           and (regression_data['forecast_day_PCT7_change'] > -5 and regression_data['forecast_day_PCT10_change'] > -7) 
           ):
            add_in_csv(regression_data, regressionResult, None, '##Test:longDownTrend-1-IndexNotDownLastDay(checkBase)')
            return True
        if(-4 < regression_data['PCT_day_change'] < -2 and -4 < regression_data['forecast_day_PCT_change'] 
           and regression_data['forecast_day_PCT_change'] > regression_data['PCT_change']
           and regression_data['series_trend'] != 'upTrend'
           and str(regression_data['score']) != '10'
           and (regression_data['forecast_day_PCT7_change'] > -5 and regression_data['forecast_day_PCT10_change'] > -7) 
           ):
            add_in_csv(regression_data, regressionResult, None, '##Test:longDownTrend-2-IndexNotDownLastDay(checkBase)')
            return True
        if(-4 < regression_data['PCT_day_change'] < -2 and -4 < regression_data['forecast_day_PCT_change'] 
           and regression_data['forecast_day_PCT_change'] > regression_data['PCT_change']
           and regression_data['series_trend'] != 'upTrend'
           and str(regression_data['score']) != '10'
           and (regression_data['forecast_day_PCT7_change'] > -10 and regression_data['forecast_day_PCT10_change'] > -10) 
           ):
            #add_in_csv(regression_data, regressionResult, None, 'sellDownTrend-2-onlyNews')
            return False
    if(all_day_pct_change_negative(regression_data) and -4 < regression_data['PCT_day_change'] < -2 and regression_data['yearLowChange'] > 30
        and regression_data['forecast_day_PCT10_change'] <= regression_data['PCT_change'] - 2
        and regression_data['forecast_day_PCT10_change'] <= regression_data['PCT_day_change'] - 2
        and float(regression_data['forecast_day_VOL_change']) > 30
        and regression_data['PCT_day_change_pre1'] < 0.5
        and float(regression_data['contract']) > 10
        and no_doji_or_spinning_sell_india(regression_data)):
        add_in_csv(regression_data, regressionResult, ws_sellDownTrend, '##Test:longDownTrend-Risky-IndexNotDownLastDay(checkBase)')
        return True
    return False

def sell_final(regression_data, regressionResult, reg, ws, ws1):
    return False
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(regression_data['yearLowChange'] > 10
       and regression_data['yearHighChange'] < -5
       and regression_data['month3HighChange'] < -3
       and -4 < regression_data['PCT_day_change'] < -1 and -4 < regression_data['PCT_change'] < -1
       and regression_data['forecast_day_VOL_change'] > 0
       and abs(regression_data['PCT_day_LC']) < 0.3
       and low_tail_pct(regression_data) < 1
       and str(regression_data['score']) != '10'
       ):
        if(str(regression_data['buyIndia']) == '' and -90 < regression_data['yearHighChange'] < -10
            and (ten_days_more_than_ten(regression_data)
                 or (last_5_day_all_up_except_today(regression_data)
                     and ten_days_more_than_seven(regression_data)
                    )
            ) 
            and regression_data['forecast_day_PCT7_change'] > 5 
            and regression_data['forecast_day_PCT5_change'] > -0.5 
            and regression_data['forecast_day_PCT4_change'] > -0.5
            and regression_data['forecast_day_PCT2_change'] < 0 
            and regression_data['forecast_day_PCT_change'] < 0):
            add_in_csv(regression_data, regressionResult, ws, 'sellFinal')
        elif(str(regression_data['buyIndia']) == '' and -90 < regression_data['yearHighChange'] < -10
            and (ten_days_more_than_ten(regression_data)
                 or (last_5_day_all_up_except_today(regression_data)
                     and ten_days_more_than_seven(regression_data)
                    )
            ) 
            and regression_data['forecast_day_PCT7_change'] >= 1 
            and regression_data['forecast_day_PCT5_change'] >= -1
            and regression_data['forecast_day_PCT2_change'] < 0 
            and regression_data['forecast_day_PCT_change'] < 0
            and regression_data['trend'] != 'down'
            ):
            add_in_csv(regression_data, regressionResult, ws1, 'sellFinal1')
    if(regression_data['forecast_day_PCT4_change'] >= -0.5
        and regression_data['forecast_day_PCT5_change'] >= -0.5
        and regression_data['forecast_day_PCT7_change'] >= -0.5
        and regression_data['yearLowChange'] > 5 and regression_data['yearHighChange'] < -5
        and regression_data['month3HighChange'] < -3
        and (ten_days_more_than_ten(regression_data)
             or (last_5_day_all_up_except_today(regression_data)
                 and ten_days_more_than_seven(regression_data)
                )
             )
        and low_tail_pct(regression_data) < 1
        and regression_data['SMA50'] > 0
        ):  
        if(regression_data['forecast_day_PCT_change'] < 0
            and regression_data['bar_low'] < regression_data['bar_low_pre1']
            and regression_data['forecast_day_VOL_change'] > 0
            ):
            if(-4 < regression_data['PCT_day_change'] < -2 and -4 < regression_data['PCT_change'] < -2
               and regression_data['PCT_day_change_pre1'] > 0
                ):
                #add_in_csv(regression_data, regressionResult, ws, 'sellFinalCandidate-0')
                add_in_csv(regression_data, regressionResult, ws, None)
                return True
            if(-5 < regression_data['PCT_day_change'] < -2 and -5 < regression_data['PCT_change'] < -2
               and regression_data['PCT_day_change_pre1'] > 0
               and (regression_data['yearHighChange'] > -30 or regression_data['yearLowChange'] > 30)
                ):
                add_in_csv(regression_data, regressionResult, ws, 'sellFinalCandidate-00')
                return True
            if(-6.5 < regression_data['PCT_day_change'] < -2 and -6.5 < regression_data['PCT_change'] < -2
               and regression_data['PCT_day_change_pre1'] > 0
               and (regression_data['yearHighChange'] > -30 or regression_data['yearLowChange'] > 30)
                ):
                add_in_csv(regression_data, regressionResult, ws, 'sellFinalCandidate-00HighChange')
                return True
            if(-2.5 < regression_data['PCT_day_change'] < -1 and -2.5 < regression_data['PCT_change'] < -1
                and regression_data['PCT_day_change_pre1'] < 0
                and (mlpValue <= -1 or kNeighboursValue <= -1)
                ):
                add_in_csv(regression_data, regressionResult, ws, 'sellFinalCandidate-1')
                return True
            if(-4 < regression_data['PCT_day_change'] < -1 and -4 < regression_data['PCT_change'] < -1 
                and no_doji_or_spinning_sell_india(regression_data)
                and regression_data['PCT_day_change_pre1'] < 0
                and (mlpValue <= -1 or kNeighboursValue <= -1)
                ):   
                add_in_csv(regression_data, regressionResult, ws, 'sellFinalCandidate-2')
                return True
            if(-2.5 < regression_data['PCT_day_change'] < -0.5 and -2.5 < regression_data['PCT_change'] < -0.5
                and regression_data['PCT_day_change_pre1'] < 0
                and (mlpValue <= -1 or kNeighboursValue <= -1)
                ):
                add_in_csv(regression_data, regressionResult, ws, '##sellFinalCandidate-2-test')
                return True
        if((((regression_data['open'] - regression_data['close']) * 1.5 > regression_data['high'] - regression_data['low']) or (regression_data['forecast_day_PCT_change'] < 0 and regression_data['PCT_day_change'] < -1))
            and (regression_data['yearHighChange'] > -30 or regression_data['yearLowChange'] > 30)
            ):
            if(-2.5 < regression_data['PCT_day_change'] < -1 and -2.5 < regression_data['PCT_change'] < -1 
                and no_doji_or_spinning_sell_india(regression_data) and no_doji_or_spinning_buy_india(regression_data)
                ):
                if(regression_data['forecast_day_VOL_change'] > -20):
                    if(((mlpValue <= -0.5 and kNeighboursValue <= -0.5) or is_algo_sell(regression_data))
                        ):    
                        add_in_csv(regression_data, regressionResult, ws, 'ML:sellFinalCandidate-3')
                        return True
                    return False
            if(-5 < regression_data['PCT_day_change'] < -1 and -5 < regression_data['PCT_change'] < -1 
                and no_doji_or_spinning_sell_india(regression_data) and no_doji_or_spinning_buy_india(regression_data)
                ):
                if(regression_data['forecast_day_VOL_change'] > 0):
                    if(((mlpValue <= -0.5 and kNeighboursValue <= -0.5) or is_algo_sell(regression_data))
                        ):    
                        add_in_csv(regression_data, regressionResult, ws, '##ML:sellFinalCandidate-4')
                        return True
                    return False
#         if(-1 < regression_data['PCT_day_change'] < 0 and -1 < regression_data['PCT_change'] < 0 
#             and no_doji_or_spinning_sell_india(regression_data) and no_doji_or_spinning_buy_india(regression_data)
#             and (mlpValue <= -1 or kNeighboursValue <= -1)
#             ):   
#             add_in_csv(regression_data, regressionResult, ws, '##sellFinalCandidate-5-(upLastDayOrDown2to3)')
#             return True
    return False

def sell_high_indicators(regression_data, regressionResult, reg, ws_sellHighIndicators):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    if(mlpValue < -3 and mlpValue_other < -3
        and regression_data['PCT_day_change'] < -5
        and regression_data['PCT_change'] < -5
        ):
        if(-35 < regression_data['forecast_day_PCT10_change'] < -10):
            add_in_csv(regression_data, regressionResult, ws, '##ALL:sellHighMLP-StockDowntrend(Risky)')
        elif(regression_data['forecast_day_PCT10_change'] > -10
            and -10 < regression_data['PCT_day_change'] < -5
            and -10 < regression_data['PCT_day_change'] < -5
            ):
            add_in_csv(regression_data, regressionResult, ws, '##ALL:sellHighMLP(Risky)')
    if(kNeighboursValue < -3 and kNeighboursValue_other < -3
        and mlpValue < -2 and mlpValue_other < -2
        and regression_data['PCT_day_change'] < -5
        and regression_data['PCT_change'] < -5
        ):
        if (-35 < regression_data['forecast_day_PCT10_change'] < -10):
            add_in_csv(regression_data, regressionResult, ws, '##ALL:sellHighKNeighbours-StockDowntrend(Risky)')
        elif(regression_data['forecast_day_PCT10_change'] > -10
            and -10 < regression_data['PCT_day_change'] < -5
            and -10 < regression_data['PCT_day_change'] < -5
            ):
            add_in_csv(regression_data, regressionResult, ws, '##ALL:sellHighKNeighbours(Risky)')
    return False
    if(mlpValue <= -2.0 and kNeighboursValue <= -1.0 
       and regression_data['yearHighChange'] < -10 
       and regression_data['yearLowChange'] > 10
       and (low_tail_pct(regression_data) < 1.5 and (low_tail_pct(regression_data) < high_tail_pct(regression_data)))
       ):
        if(-4 < regression_data['PCT_day_change'] < -1.5 and -4 < regression_data['PCT_change'] < 0.5
           and regression_data['forecast_day_PCT_change'] < 0
           and low_tail_pct(regression_data) < 1
           ):
            add_in_csv(regression_data, regressionResult, ws_sellHighIndicators, 'sellHighIndicators')
            return True
        if(-1 < regression_data['PCT_day_change'] < 0.5 and -2.5 < regression_data['PCT_change'] < 0.5):
            add_in_csv(regression_data, regressionResult, ws_sellHighIndicators, '(longUpTrend)sellHighIndicators')
            return True         
    return False

def sell_pattern(regression_data, regressionResult, reg, ws_sellPattern, ws_sellPattern1):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(regression_data['yearHighChange'] < -10):
        if(is_algo_sell(regression_data)
            and regression_data['sellIndia_avg'] < -1.5 
            and low_tail_pct(regression_data) < 1.5
            ):
            add_in_csv(regression_data, regressionResult, ws_sellPattern, 'sellPatternsML')
            return True

def sell_base_line_sell(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    if((-5 < regression_data['year2LowChange'] < 0 ) 
        and (regression_data['year2HighChange'] < -40)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Year2LowBreak')
    elif((-5 < regression_data['yearLowChange'] < 0) 
        and (regression_data['year2LowChange'] > 7.5)
        and (regression_data['yearHighChange'] < -30)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'YearLowBreak')
    elif((-5 < regression_data['month6LowChange'] < 0)
        and (regression_data['yearLowChange'] > 7.5)
        and (regression_data['month6HighChange'] < -25)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'month6LowBreak')
    elif((-5 < regression_data['month3LowChange'] < 0)
        and (regression_data['month6LowChange'] > 7.5)
        and (regression_data['month3HighChange'] < -15)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'month3LowBreak')
        
    if((0 < regression_data['year2LowChange'] < 7.5) 
       and (regression_data['year2HighChange'] < -40)
       ):
        if(regression_data['weekLow'] < regression_data['year2Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'year2LowReversal(Confirm)')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'nearYear2Low')
    elif((0 < regression_data['yearLowChange'] < 7.5)
        and (regression_data['year2LowChange'] > 7.5)
        and (regression_data['yearHighChange'] < -30)
        ):
        if(regression_data['weekLow'] < regression_data['yearLow']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'yearLowReversal(Confirm)')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'nearYearLow')
    elif((0 < regression_data['month6LowChange'] < 7.5)
        and (regression_data['yearLowChange'] > 7.5)
        and (regression_data['month6HighChange'] < -25)
        ):
        if(regression_data['weekLow'] < regression_data['month6Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'month6LowReversal(Confirm)')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'nearMonth6Low')
    elif((0 < regression_data['month3LowChange'] < 7.5)
        and (regression_data['month6LowChange'] > 7.5)
        and (regression_data['month3HighChange'] < -15)
        ):
        if(regression_data['weekLow'] < regression_data['month3Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'month3LowReversal(Confirm)')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'nearMonth3Low')  
            
    if((0 < regression_data['year2HighChange'] < 5) 
        and (regression_data['year2LowChange'] > 40)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Year2HighBreak')
    elif((0 < regression_data['yearHighChange'] < 5) 
        and (regression_data['yearLowChange'] > 30)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'YearHighBreak')
    elif((0 < regression_data['month6HighChange'] < 5)
        and (regression_data['month6LowChange'] > 25)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'month6HighBreak')
    elif((0 < regression_data['month3HighChange'] < 5) 
        and (regression_data['month3LowChange'] > 15)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'month3HighBreak')  
    
    if((-7.5 < regression_data['year2HighChange'] < 0) 
        and (regression_data['year2LowChange'] > 40)
        ):
        if(regression_data['weekHigh'] >= regression_data['year2High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'year2HighReversal(Confirm)')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'nearYear2High')
    elif((-7.5 < regression_data['yearHighChange'] < 0) 
        and (regression_data['yearLowChange'] > 30)
        ):
        if(regression_data['weekHigh'] >= regression_data['yearHigh']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'yearHighReversal(Confirm)')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'nearYearHigh')
    elif((-7.5 < regression_data['month6HighChange'] < 0) 
        and (regression_data['month6LowChange'] > 25)
        ):
        if(regression_data['weekHigh'] >= regression_data['month6High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'month6HighReversal(Confirm)')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'nearMonth6High')
    elif((-7.5 < regression_data['month3HighChange'] < 0) 
        and (regression_data['month3LowChange'] > 15)
        ):
        if(regression_data['weekHigh'] >= regression_data['month3High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'month3HighReversal(Confirm)')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'nearMonth3High')
    elif(regression_data['year2HighChange'] > 0):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, '**year2High')
    elif(regression_data['yearHighChange'] > 0):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, '**YearHigh')
    elif(regression_data['month6HighChange'] > 0):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, '**Month6High')
    elif(regression_data['month3HighChange'] > 0):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, '**Month3High')
    elif(regression_data['year2LowChange'] < -5):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, '**2YearLow')
    elif(regression_data['yearLowChange'] < -5):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, '**YearLow')
    elif(regression_data['month6LowChange'] < -5):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, '**Month6Low')
    elif(regression_data['month3LowChange'] < -5):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, '**Month3Low')
    
    
#     if(is_algo_sell(regression_data)
#         and mlpValue_other < 0.5
#         and kNeighboursValue_other < 0.5
#         and (mlpValue_other < -0.5 or kNeighboursValue_other < -0.5)
#         and regression_data['buyIndia'] == ''
#         and low_tail_pct(regression_data) < 2
#         ):
#         if(-4.5 < regression_data['PCT_day_change'] < -1 and -4.5 < regression_data['PCT_change'] < -1
#             and regression_data['forecast_day_PCT_change'] < 0
#             and regression_data['forecast_day_PCT2_change'] <= 0
#             and regression_data['forecast_day_PCT3_change'] <= 0
#             ):
#             if(-5 < regression_data['year2LowChange'] < 0
#                 and (regression_data['year2HighChange'] < -40)
#                 ):
#                 return False
#             if(-5 < regression_data['yearLowChange'] < 0
#                 and (regression_data['yearHighChange'] < -30)
#                 ):
#                 return False
#             if(-5 < regression_data['month6LowChange'] < 0
#                 and (regression_data['month6HighChange'] < -20)
#                 and regression_data['buyIndia'] == ""
#                 and regression_data['sellIndia'] != ""
#                 ):
#                 if('month6LowBreak' in regression_data['filter3']):
#                     add_in_csv(regression_data, regressionResult, ws, 'Test:sellMonth6LowBreakML(Check2-3Down)')
#                     return True
#             if(-10 < regression_data['month6LowChange'] < 0
#                 and (regression_data['month6HighChange'] < -20)
#                 ):
#                 return False
#             if(-10 < regression_data['month3LowChange'] < 0
#                 and (regression_data['month3HighChange'] < -15)
#                 ):
#                 if('month3LowBreak' in regression_data['filter3']):
#                     add_in_csv(regression_data, regressionResult, ws, 'Test:sellMonth3LowBreakML(Check2-3Down)')
#                     return True
#         if(-5 < regression_data['PCT_day_change'] < 0 and -5 < regression_data['PCT_change'] < 0
#             ):
#             if(-6.5 < regression_data['year2HighChange'] < 0
#                 and (regression_data['year2LowChange'] > 40)
#                 ):
#                 if('year2HighReversal(Confirm)' in regression_data['filter3']):
#                     add_in_csv(regression_data, regressionResult, ws, None)
#                     return False
#                 if('nearYear2High' in regression_data['filter3']):
#                     add_in_csv(regression_data, regressionResult, ws, None)
#                     return False
#             if(-6.5 < regression_data['yearHighChange'] < 0
#                 and (regression_data['yearLowChange'] > 30)
#                 ):
#                 if('yearHighReversal(Confirm)' in regression_data['filter3']):
#                     add_in_csv(regression_data, regressionResult, ws, 'Test:sellYearHighReversalML-(downTrend)(checkBase)')
#                     return True
#                 if('nearYearHigh' in regression_data['filter3']):
#                     add_in_csv(regression_data, regressionResult, ws, 'Test:sellYearHighML-(downTrend)(checkBase)')
#                     return True
#             if(-6.5 < regression_data['month6HighChange'] < 0
#                 and (regression_data['month6LowChange'] > 20)
#                 ):
#                 if('month6HighReversal(Confirm)' in regression_data['filter3']):
#                     add_in_csv(regression_data, regressionResult, ws, 'Test:sellMonth6HighReversalML-(downTrend)(checkBase)')
#                     return True
#                 if('nearMonth6High' in regression_data['filter3']):
#                     add_in_csv(regression_data, regressionResult, ws, 'Test:sellMonth6HighML-(downTrend)(checkBase)')
#                     return True
# #             if(-6.5 < regression_data['month3HighChange'] < 0
# #                 and (regression_data['month3LowChange'] > 15)
# #                 ):
# #                 if('month3HighReversal(Confirm)' in regression_data['filter3']):
# #                     add_in_csv(regression_data, regressionResult, ws, 'Test:sellMonth3HighReversalML-(downTrend)(checkBase)')
# #                     return True
#                 
#     if((regression_data['PCT_day_change_pre1'] > 0) or (regression_data['forecast_day_VOL_change'] > 0)
#         and low_tail_pct(regression_data) < 2
#         ):
#         if(-4.5 < regression_data['PCT_day_change'] < -1 and -4.5 < regression_data['PCT_change'] < -1
#             and low_tail_pct(regression_data) < 2
#             and regression_data['forecast_day_PCT_change'] < 0
#             and regression_data['forecast_day_PCT2_change'] <= 0
#             and regression_data['forecast_day_PCT3_change'] <= 0
#             ):
#             if(-5 < regression_data['year2LowChange'] < 0
#                 and (regression_data['year2HighChange'] < -40)
#                 ):
#                 return False
#             if(-5 < regression_data['yearLowChange'] < 0
#                 and (regression_data['yearHighChange'] < -30)
#                 ):
#                 return False
#             if(-5 < regression_data['month6LowChange'] < 0
#                 and (regression_data['month6HighChange'] < -20)
#                 ):
#                 return False
#             if(-5 < regression_data['month3LowChange'] < 0
#                 and (regression_data['month3HighChange'] < -15)
#                 ):
#                 if('month3LowBreak' in regression_data['filter3']):
#                     add_in_csv(regression_data, regressionResult, ws, 'Test:sellMonth3LowBreak-1(Check2-3Down)')
#                     return True
#         if(-5 < regression_data['PCT_day_change'] < -1.5 and -5 < regression_data['PCT_change'] < -1.5
#             ):
#             if(-6.5 < regression_data['year2HighChange'] < 0
#                 and (regression_data['year2LowChange'] > 40)
#                 ):
#                 if('year2HighReversal(Confirm)' in regression_data['filter3']):
#                     add_in_csv(regression_data, regressionResult, ws, None)
#                     return False
#             if(-6.5 < regression_data['yearHighChange'] < 0
#                 and (regression_data['yearLowChange'] > 30)
#                 ):
#                 if('yearHighReversal(Confirm)' in regression_data['filter3']):
#                     add_in_csv(regression_data, regressionResult, ws, 'Test:sellYearHighReversal-1(HighDownTrend)(checkBase)')
#                     return True
#             if(-6.5 < regression_data['month6HighChange'] < 0
#                 and (regression_data['month6LowChange'] > 20)
#                 ):
#                 if('month6HighReversal(Confirm)' in regression_data['filter3']):
#                     add_in_csv(regression_data, regressionResult, ws, 'Test:sellMonth6HighReversal-1(HighDownTrend)(checkBase)')
#                     return True
#             if(-6.5 < regression_data['month3HighChange'] < 0
#                 and (regression_data['month3LowChange'] > 15)
#                 ):
#                 if('month3HighReversal(Confirm)' in regression_data['filter3']):
#                     add_in_csv(regression_data, regressionResult, ws, 'Test:sellMonth3HighReversal-1(HighDownTrend)(checkBase)')
#                     return True
    return False

def sell_base_line_buy(regression_data, regressionResult, reg, ws):
    return False
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    if(low_tail_pct(regression_data) > 2
        and (mlpValue > 0 and kNeighboursValue > 0
             and (mlpValue_other > 0 or kNeighboursValue_other > 0)
            )
        ):
        if(-4 < regression_data['PCT_day_change'] < 0 and -4 < regression_data['PCT_change'] < 0
            ):
            if(-10 < regression_data['year2LowChange'] < 5):
                add_in_csv(regression_data, regressionResult, ws, 'Test:buyYear2LowBreak-0')
                return True
            if(-10 < regression_data['yearLowChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, 'Test:buyYearLowBreak-0')
                return True
            if(-10 < regression_data['month6LowChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, 'Test:buyMonth6LowBreak-0')
                return True
            if(-6.5 < regression_data['yearHighChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, 'Test:buyYearHighReversal-0-(downTrend)(checkBase)')
                return True
            if(-6.5 < regression_data['month6HighChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, 'Test:buyMonth6HighReversal-0-(downTrend)(checkBase)')
                return True
            if(-6.5 < regression_data['month3HighChange'] < 0
                and low_tail_pct(regression_data) > 2
                ):
                add_in_csv(regression_data, regressionResult, ws, 'Test:buyMonth3HighReversal-0-(downTrend)(checkBase)')
                return True
    
    if(low_tail_pct(regression_data) > 2
        and (regression_data['close'] - regression_data['low']) > (regression_data['open'] - regression_data['close'])
        and (regression_data['close'] - regression_data['low']) >= ((regression_data['high'] - regression_data['open']) * 3)
        and (mlpValue > 0 and kNeighboursValue > 0)
        ):
        if(-4 < regression_data['PCT_day_change'] < 0 and -4 < regression_data['PCT_change'] < 0
            and -4 < regression_data['forecast_day_PCT_change'] < 0
            ):
            if(-10 < regression_data['year2LowChange'] < 5):
                add_in_csv(regression_data, regressionResult, ws, 'Test:buyYear2LowBreak-1')
                return True
            if(-10 < regression_data['yearLowChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, 'Test:buyYearLowBreak-1')
                return True
            if(-10 < regression_data['month6LowChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, 'Test:buyMonth6LowBreak-1')
                return True
            if(-6.5 < regression_data['yearHighChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, 'Test:buyYearHighReversal-1-(downTrend)(checkBase)')
                return True
            if(-6.5 < regression_data['month6HighChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, 'Test:buyMonth6HighReversal-1-(downTrend)(checkBase)')
                return True
            if(-6.5 < regression_data['month3HighChange'] < 0
                and low_tail_pct(regression_data) > 2
                ):
                add_in_csv(regression_data, regressionResult, ws, 'Test:buyMonth3HighReversal-1-(downTrend)(checkBase)')
                return True
    
    if(('M@[,RSI]' in regression_data['buyIndia'])
        and (mlpValue > 0 and kNeighboursValue > 0)
        ):
        if(-4 < regression_data['PCT_day_change'] < 0 and -4 < regression_data['PCT_change'] < 0
            and -4 < regression_data['forecast_day_PCT_change'] < 0
            ):
            if(-5 < regression_data['year2LowChange'] < 5):
                add_in_csv(regression_data, regressionResult, ws, 'Test:buyYear2LowBreak-2')
                return True
            if(-5 < regression_data['yearLowChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, 'Test:buyYearLowBreak-2')
                return True
            if(-5 < regression_data['month6LowChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, 'Test:buyMonth6LowBreak-2')
                return True
            
#     if(regression_data['forecast_day_PCT_change'] > 0
#         and regression_data['forecast_day_PCT2_change'] >= 0
#         and (mlpValue > 0 and kNeighboursValue > 0)
#         ):
#         if(-4 < regression_data['PCT_day_change'] < 0 and -4 < regression_data['PCT_change'] < 0
#             ):
#             if(-5 < regression_data['year2LowChange'] < 5):
#                 add_in_csv(regression_data, regressionResult, ws, 'Test:buyYear2LowBreak-3')
#                 return True
#             if(-5 < regression_data['yearLowChange'] < 0):
#                 add_in_csv(regression_data, regressionResult, ws, 'Test:buyYearLowBreak-3')
#                 return True
#             if(-5 < regression_data['month6LowChange'] < 0):
#                 add_in_csv(regression_data, regressionResult, ws, 'Test:buyMonth6LowBreak-3')
#                 return True
    
    return False
    
def sell_morning_star_buy(regression_data, regressionResult, reg, ws):
    return False
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(-8 < regression_data['forecast_day_PCT_change'] < -3
        and ((regression_data['yearLowChange'] > 15) or (regression_data['yearLowChange'] < 2))
        and high_tail_pct(regression_data) < 0.5
        and low_tail_pct(regression_data) > 3
        and regression_data['forecast_day_PCT10_change'] < -10
        ):
        if(-6 < regression_data['PCT_day_change'] < -2 and -6 < regression_data['PCT_change'] < -1
            and (regression_data['close'] - regression_data['low']) >= ((regression_data['open'] - regression_data['close']) * 3)
            and (regression_data['close'] - regression_data['low']) >= ((regression_data['high'] - regression_data['open']) * 3)
            and regression_data['forecast_day_PCT10_change'] < -10
            and regression_data['SMA25'] < -8.5
            ):
            add_in_csv(regression_data, regressionResult, ws, None)
            return True
    if(-10 < regression_data['forecast_day_PCT_change'] < -2
        and regression_data['PCT_day_change_pre1'] < 0
        and (ten_days_less_than_minus_seven(regression_data))
        and high_tail_pct(regression_data) < 0.5
        and 1.5 < low_tail_pct(regression_data) < 4
        ):
        if(-3 < regression_data['PCT_day_change'] < 0 and -3 < regression_data['PCT_change'] < 0
            and (regression_data['close'] - regression_data['low']) >= ((regression_data['open'] - regression_data['close']) * 3)
            and (regression_data['close'] - regression_data['low']) >= ((regression_data['high'] - regression_data['open']) * 3)
            and regression_data['forecast_day_PCT10_change'] < -10
            and regression_data['SMA25'] < -8.5
            ):
            add_in_csv(regression_data, regressionResult, ws, 'morningStarBuy-dayDown')
            return True
        if(0.3 < regression_data['PCT_day_change'] < 1
            and (regression_data['open'] - regression_data['low']) >= ((regression_data['open'] - regression_data['close']) * 3)
            and (regression_data['open'] - regression_data['low']) >= ((regression_data['high'] - regression_data['close']) * 3)
            and 2 < low_tail_pct(regression_data) < 3.5
            ):
            if(is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, 'ML:morningStarBuy-Risky-dayUp')
                return True
            return False
    if(-10 < regression_data['forecast_day_PCT_change'] < -2
        and regression_data['PCT_day_change_pre1'] < 0
        and (ten_days_less_than_minus_seven(regression_data))
        and high_tail_pct(regression_data) < 0.5
        and 1.5 < low_tail_pct(regression_data) < 7
        ):
        if(0.3 < regression_data['PCT_day_change'] < 1
            and (regression_data['open'] - regression_data['low']) >= ((regression_data['open'] - regression_data['close']) * 3)
            and (regression_data['open'] - regression_data['low']) >= ((regression_data['high'] - regression_data['close']) * 3)
            and regression_data['year2HighChange'] > -50
            ):
            add_in_csv(regression_data, regressionResult, ws, 'morningStarSell-dayUp')
            return True
#         if(high_tail_pct(regression_data) < 1.5
#            and low_tail_pct(regression_data) > 1.5
#            ):
#             if(0 < regression_data['PCT_day_change'] < 1 and 0 < regression_data['PCT_change'] < 1 
#                 and kNeighboursValue >= 0
#                 ):
#                 add_in_csv(regression_data, regressionResult, ws, '##morningStarBuy-0-NotUpSecondHalfAndUp2to3')
#                 return True
#             if(-1.5 < regression_data['PCT_day_change'] < 0 and -1.5 < regression_data['PCT_change'] < 0
#                 and (regression_data['close'] - regression_data['low']) >= ((regression_data['open'] - regression_data['close']) * 3)
#                 and (regression_data['close'] - regression_data['low']) >= ((regression_data['high'] - regression_data['open']) * 3)
#                 ):
#                 add_in_csv(regression_data, regressionResult, ws, '##morningStarBuy-1-NotUpSecondHalfAndUp2to3')
#                 return True
    return False

def sell_evening_star_sell(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(8 > regression_data['forecast_day_PCT_change'] > 4
        and regression_data['month3HighChange'] > -50
        and low_tail_pct(regression_data) < 0.8
        and high_tail_pct(regression_data) > 2.5
        and regression_data['yearHighChange'] < -4
        ):
        if(6 > regression_data['PCT_day_change'] > 1.5 and 6 > regression_data['PCT_change'] > 1
            and (regression_data['high']-regression_data['close']) > ((regression_data['close']-regression_data['open']))
            and (regression_data['high']-regression_data['close']) >= ((regression_data['open']-regression_data['low'])*3)
            #and ((regression_data['yearHighChange'] < -15) or (regression_data['yearHighChange'] > -2))
            #and regression_data['forecast_day_PCT5_change'] < 10
            ):
            if(regression_data['year2HighChange'] < -80
            ):
                add_in_csv(regression_data, regressionResult, ws, 'eveningStarBuy-0(Buy-After-1pc-down)')
                return True
            else:
                add_in_csv(regression_data, regressionResult, ws, 'eveningStarSell-0')
                return True
    elif(
        regression_data['PCT_day_change_pre1'] > 0
        and (ten_days_more_than_seven(regression_data))
        ):
        if(low_tail_pct(regression_data) < 1.5
            and high_tail_pct(regression_data) > 1.5
            ):
            if(1.5 > regression_data['PCT_day_change'] > 0.5 and 1.5 > regression_data['PCT_change'] > 0
                and (regression_data['high']-regression_data['close']) >= ((regression_data['close']-regression_data['open']) * 3)
                and (regression_data['high']-regression_data['close']) >= ((regression_data['open']-regression_data['low'])*3)
                ):
                if(is_algo_sell(regression_data)):
                    add_in_csv(regression_data, regressionResult, ws, 'ML:eveningStarSell-2(Check2-3MidCapCross)')
                    return True
                return False
        elif((low_tail_pct(regression_data) < 0.5 or (regression_data['forecast_day_PCT_change'] > 6 and low_tail_pct(regression_data) < 1))
            and 2 < high_tail_pct(regression_data) < 3.5
            and low_tail_pct(regression_data) < 0.5
            ):
            if(2 > regression_data['PCT_day_change'] > 0.5 and 2 > regression_data['PCT_change'] > 0
                ):
                if(is_algo_sell(regression_data)):
                    add_in_csv(regression_data, regressionResult, ws, 'ML:eveningStarSell-Risky-3(Check2-3MidCapCross)')
                    return True
                return False
#         if(low_tail_pct(regression_data) < 1.5
#             and high_tail_pct(regression_data) > 2
#             ):
#             if(1.5 > regression_data['PCT_day_change'] > 0 and 1.5 > regression_data['PCT_change'] > 0
#                 and (regression_data['high']-regression_data['close']) >= ((regression_data['close']-regression_data['open'])*3)
#                 and (regression_data['high']-regression_data['close']) >= ((regression_data['open']-regression_data['low'])*3)
#                 ):
#                 add_in_csv(regression_data, regressionResult, ws, '##TEST:eveningStarSell-3(Check2-3MidCapCross)')
#                 return True
#             if(0 > regression_data['PCT_day_change'] > -1
#                 and (regression_data['high']-regression_data['open']) >= ((regression_data['open']-regression_data['close'])*3)
#                 and (regression_data['high']-regression_data['open']) >= ((regression_data['close']-regression_data['low'])*3)
#                 ):
#                 add_in_csv(regression_data, regressionResult, ws, '##TEST:eveningStarSell-4(Check2-3MidCapCross)')
#                 return True   
    return False

def sell_oi_negative(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(regression_data['greentrend'] == 1
        and regression_data['forecast_day_PCT_change'] > 0.5
        and regression_data['forecast_day_PCT2_change'] > 0.5
        and regression_data['forecast_day_PCT3_change'] > 0.5
        and regression_data['forecast_day_PCT4_change'] > 0.5
        and regression_data['forecast_day_PCT5_change'] > 0.5
        and regression_data['forecast_day_PCT7_change'] > 0.5
        and ten_days_more_than_ten(regression_data)
        and float(regression_data['forecast_day_VOL_change']) < -40 
        and regression_data['PCT_day_change_pre1'] > regression_data['PCT_day_change']
        and float(regression_data['contract']) < 0
        and float(regression_data['oi']) < 5
        and (regression_data['yearLowChange'] > 15 or regression_data['yearHighChange'] > -15)
        ):
        if(is_algo_sell(regression_data)):
            if(((0 < regression_data['PCT_day_change'] < 1 and 0.5 < regression_data['PCT_change'] < 1)
                or (0.5 < regression_data['PCT_day_change'] < 1 and 0 < regression_data['PCT_change'] < 1))
               ):
                add_in_csv(regression_data, regressionResult, ws, 'ML:sellNegativeOI-0-checkBase(1%up)')
                return True
            if(0 < regression_data['PCT_day_change'] < 2 and 0 < regression_data['PCT_change'] < 2 
                ):
                add_in_csv(regression_data, regressionResult, ws, 'ML:sellNegativeOI-1-checkBase(1%up)')
                return True
        return False
    return False

def sell_day_high(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(regression_data['PCT_day_change_pre1'] > 1.5
       and regression_data['high'] > regression_data['high_pre1']
       and regression_data['bar_high'] > regression_data['bar_high_pre1']
       ):
        if((regression_data['PCT_day_change'] > 5 or regression_data['PCT_change'] > 5)
           and float(regression_data['forecast_day_VOL_change']) < -50
           and regression_data['PCT_day_change'] > regression_data['PCT_day_change_pre1'] > 0
           and regression_data['PCT_day_change_pre1'] > 2
           and regression_data['forecast_day_PCT_change'] > 5
           and regression_data['forecast_day_PCT10_change'] < -5
           ):
            add_in_csv(regression_data, regressionResult, ws, 'dayHighVolLowSell-0')
            return True
        elif((regression_data['PCT_day_change'] > 5 or regression_data['PCT_change'] > 5)
           and float(regression_data['forecast_day_VOL_change']) < -20
           and regression_data['PCT_day_change'] > regression_data['PCT_day_change_pre1'] > 0
           and regression_data['PCT_day_change_pre1'] > 1
           and regression_data['forecast_day_PCT_change'] > 4
           and regression_data['yearLowChange'] < 80
           ):
            add_in_csv(regression_data, regressionResult, ws, 'dayHighVolLowBuy-0')
            return True
        elif((regression_data['PCT_day_change'] > 5 and regression_data['PCT_change'] > 4)
           and float(regression_data['forecast_day_VOL_change']) < -20
           and regression_data['PCT_day_change'] > regression_data['PCT_day_change_pre1'] > 0
           and regression_data['PCT_day_change_pre1'] > 1.5
           and regression_data['month3LowChange'] < 30
           ):
            add_in_csv(regression_data, regressionResult, ws, 'dayHighVolLowSell-01-checkMorningTrend(.5SL)')
            return True
#         elif((regression_data['PCT_day_change'] > 3 and regression_data['PCT_change'] > 3) 
#            and abs_yearHigh_more_than_yearLow(regression_data)
#            and float(regression_data['forecast_day_VOL_change']) < -50  
#            and regression_data['PCT_day_change'] > regression_data['PCT_day_change_pre1'] > 0
#            and regression_data['PCT_day_change_pre2'] < -1
#            ):
#             add_in_csv(regression_data, regressionResult, ws, 'dayHighVolLowSell-1-checkMorningTrend(.5SL)-NotYearHigh')
#             return True
#     if((regression_data['PCT_day_change'] > 2 and regression_data['PCT_change'] > 2) 
#        and float(regression_data['forecast_day_VOL_change']) < -50  
#        and regression_data['PCT_day_change_pre1'] > 0
#        ):
#         add_in_csv(regression_data, regressionResult, ws, '##dayHighVolLowSell-2')
#         return True
    return False

def sell_vol_contract(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if((ten_days_less_than_minus_ten(regression_data) == False
        or ten_days_less_than_minus_fifteen(regression_data) == True
        or (regression_data['forecast_day_PCT5_change'] > -5 and regression_data['forecast_day_PCT7_change'] > -5))
        #and ((mlpValue <= -0.3 and kNeighboursValue <= -0.3) or is_algo_sell(regression_data))
        and (float(regression_data['contract']) != 0 or float(regression_data['oi']) != 0)
        and float(regression_data['contract']) > 10
        and ((regression_data['PCT_day_change'] < -1 or regression_data['PCT_change'] < -1)
             or
             (regression_data['PCT_day_change'] < -0.75 and regression_data['PCT_change'] < -0.75)
             and regression_data['forecast_day_PCT_change'] > -2
             and regression_data['forecast_day_PCT2_change'] > -2
             and regression_data['forecast_day_PCT3_change'] > -2
             and regression_data['forecast_day_PCT4_change'] > -2
             and regression_data['forecast_day_PCT5_change'] > -2
             and regression_data['forecast_day_PCT7_change'] > -2
             and regression_data['forecast_day_PCT10_change'] > -2
            )
        and regression_data['forecast_day_PCT_change'] < 0
        and regression_data['forecast_day_PCT2_change'] < 0
        and regression_data['forecast_day_PCT3_change'] < 0
        and -5 < regression_data['forecast_day_PCT4_change'] < 0
        and regression_data['forecast_day_PCT5_change'] > -5
        and regression_data['forecast_day_PCT7_change'] > -5
        and regression_data['forecast_day_PCT10_change'] > -5
        and (regression_data['PCT_day_change'] > 0
            or regression_data['PCT_day_change_pre1'] > 0
            or regression_data['PCT_day_change_pre2'] > 0
            or regression_data['PCT_day_change_pre3'] > 0
            or regression_data['PCT_day_change_pre4'] > 0
            )
        and preDayPctChangeDown_orVolHigh(regression_data)
        and regression_data['open'] > 50
        and last_4_day_all_down(regression_data) == False
        and low_tail_pct(regression_data) < 1.5
        and regression_data['month3LowChange'] > 7.5
        and (regression_data['forecast_day_VOL_change'] > 150
            or (regression_data['PCT_day_change_pre2'] > 0
                and (((regression_data['volume'] - regression_data['volume_pre2'])*100)/regression_data['volume_pre2']) > 100
                and (((regression_data['volume'] - regression_data['volume_pre3'])*100)/regression_data['volume_pre3']) > 100
               )
           )
        ):
        if((regression_data['forecast_day_VOL_change'] > 70 and -2 < regression_data['PCT_day_change'] < -0.5 and -2 < regression_data['PCT_change'] < -1)
            and float(regression_data['contract']) > 10
            ):
            if((mlpValue <= -0.3 and kNeighboursValue <= -0.3) or is_algo_sell(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, 'ML:oiSell-0')
                return True
            return False
        elif((regression_data['forecast_day_VOL_change'] > 35 and -2 < regression_data['PCT_day_change'] < -0.5 and -2 < regression_data['PCT_change'] < -1)
            and float(regression_data['contract']) > 20
            ):
            if((mlpValue <= -0.3 and kNeighboursValue <= -0.3) or is_algo_sell(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, 'ML:oiSell-1')
                return True
            return False
        elif((regression_data['forecast_day_VOL_change'] > 150 and -3 < regression_data['PCT_day_change'] < -1 and -3 < regression_data['PCT_change'] < -1)
            ):
            if((mlpValue <= -0.3 and kNeighboursValue <= -0.3) or is_algo_sell(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, 'ML:oiSell-2-checkBase')
                return True
            return False
        elif(((regression_data['forecast_day_VOL_change'] > 400 and -3.5 < regression_data['PCT_day_change'] < -1 and -3.5 < regression_data['PCT_change'] < -1)
            or (regression_data['forecast_day_VOL_change'] > 500 and -4.5 < regression_data['PCT_day_change'] < -1 and -4.5 < regression_data['PCT_change'] < -1)
            )
            ):
            if((mlpValue <= -0.3 and kNeighboursValue <= -0.3) or is_algo_sell(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, 'oiSell-3-checkBase')
                return True
            return False
        elif((regression_data['forecast_day_VOL_change'] > 500 and -5 < regression_data['PCT_day_change'] < -1 and -5 < regression_data['PCT_change'] < -1)
            and float(regression_data['contract']) > 50
            and (regression_data['forecast_day_PCT10_change'] > 8 or regression_data['forecast_day_PCT7_change'] > 8)
            ):
            if((mlpValue <= -0.3 and kNeighboursValue <= -0.3) or is_algo_sell(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, 'oiSell-4-checkBase')
                return True
            return False
    return False

def sell_vol_contract_contrarian(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(
        #(float(regression_data['contract']) != 0 or float(regression_data['oi']) != 0)
        (ten_days_less_than_minus_ten(regression_data) == True and ten_days_less_than_minus_fifteen(regression_data) == False
             and (regression_data['forecast_day_PCT5_change'] < -5 and regression_data['forecast_day_PCT7_change'] < -5))
        #and float(regression_data['contract']) > 10
        #and (regression_data['PCT_day_change'] < -1 or regression_data['PCT_change'] < -1)
        #and regression_data['forecast_day_PCT_change'] < -0.5
        #and regression_data['forecast_day_PCT2_change'] < -0.5
        #and regression_data['forecast_day_PCT3_change'] < 0
        #and regression_data['forecast_day_PCT4_change'] < 0
        #and preDayPctChangeDown_orVolHigh(regression_data)
        and regression_data['open'] > 50
        #and last_7_day_all_down(regression_data) == False
        ):
        if((regression_data['forecast_day_VOL_change'] > 70 and -2 < regression_data['PCT_day_change'] < -0.75 and -2 < regression_data['PCT_change'] < -0.5)
            and float(regression_data['contract']) > 10
            ):
            if(('P@[') not in regression_data['sellIndia']):
                add_in_csv(regression_data, regressionResult, ws, 'Reversal(Test):buyReversalOI-0')
                return True
            return False
        elif((regression_data['forecast_day_VOL_change'] > 35 and -2 < regression_data['PCT_day_change'] < -0.75 and -2 < regression_data['PCT_change'] < -0.5)
            and float(regression_data['contract']) > 20
            ):
            if(('P@[') not in regression_data['sellIndia']):
                add_in_csv(regression_data, regressionResult, ws, 'Reversal(Test):buyReversalOI-1')
                return True
            return False
        elif((regression_data['forecast_day_VOL_change'] > 150 and -3 < regression_data['PCT_day_change'] < -0.75 and -3 < regression_data['PCT_change'] < -0.5)
            ):
            add_in_csv(regression_data, regressionResult, ws, 'Reversal(Test):buyReversalOI-2')
            return True
#             elif(((regression_data['forecast_day_VOL_change'] > 300 and -3.5 < regression_data['PCT_day_change'] < -0.75 and -3.5 < regression_data['PCT_change'] < -0.5)
#                 or (regression_data['forecast_day_VOL_change'] > 400 and -4.5 < regression_data['PCT_day_change'] < -0.75 and -4.5 < regression_data['PCT_change'] < -0.5)
#                 )
#                 and regression_data['forecast_day_PCT10_change'] > -10
#                 ):
#                 add_in_csv(regression_data, regressionResult, ws, 'Reversal(Test):buyReversalOI-3-checkBase-(openAroundLastCloseAnd5MinuteChart)')
#                 return True
#             elif((regression_data['forecast_day_VOL_change'] > 500 and -5 < regression_data['PCT_day_change'] < -0.75 and -5 < regression_data['PCT_change'] < -0.5)
#                 #and float(regression_data['contract']) > 50
#                 and regression_data['forecast_day_PCT10_change'] > -10
#                 ):
#                 add_in_csv(regression_data, regressionResult, ws, 'Reversal(Test):buyReversalOI-4-checkBase-(openAroundLastCloseAnd5MinuteChart)')
#                 return True
        
#     if((('P@[' not in str(regression_data['buyIndia'])) and ('P@[' not in str(regression_data['sellIndia'])))
#         and (0 < regression_data['PCT_day_change'] < 1.5 and 0 < regression_data['PCT_change'] < 1.5)
#         and kNeighboursValue <= -1
#         and mlpValue <= 0
#         and is_recent_consolidation(regression_data) == False
#         and str(regression_data['score']) != '10'
#         and (low_tail_pct(regression_data) < 1.5 or (low_tail_pct(regression_data) < high_tail_pct(regression_data)))
#         ):
#             add_in_csv(regression_data, regressionResult, ws, 'Reversal(Test):sellReversalKNeighbours(upTrend)(upLastDay)')
#             return True        
    return False

def sell_trend_reversal(regression_data, regressionResult, reg, ws):    
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(regression_data['yearLowChange'] > 5 and regression_data['yearHighChange'] < -5
        and (ten_days_more_than_ten(regression_data)
             or (last_5_day_all_up_except_today(regression_data)
                 and ten_days_more_than_seven(regression_data)
                )
             )
        ):  
        if((((regression_data['open'] - regression_data['close']) * 1.5 > regression_data['high'] - regression_data['low']) or (regression_data['forecast_day_PCT_change'] < 0 and regression_data['PCT_day_change'] < -1))
            and (regression_data['yearHighChange'] > -30 or regression_data['yearLowChange'] > 30)
            ):
            if(-2.5 < regression_data['PCT_day_change'] < -1 and -2.5 < regression_data['PCT_change'] < -1 
                and no_doji_or_spinning_sell_india(regression_data) and no_doji_or_spinning_buy_india(regression_data)
                ):
                if(regression_data['forecast_day_VOL_change'] <= -30
                    and ('P@[' not in regression_data['buyIndia'])
                    and (regression_data['PCT_day_change_pre1'] < -1)
                    and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None)
                    return True
            if(-5 < regression_data['PCT_day_change'] < -1 and -5 < regression_data['PCT_change'] < -1 
                and no_doji_or_spinning_sell_india(regression_data) and no_doji_or_spinning_buy_india(regression_data)
                ):
                if(regression_data['forecast_day_VOL_change'] <= -30
                    and (regression_data['PCT_day_change_pre1'] < -1)
                    and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
                    and regression_data['weekLowChange'] > 2
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None)
                    return False
                elif(regression_data['forecast_day_VOL_change'] <= -10
                    and (regression_data['PCT_day_change_pre1'] < -1)
                    and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
                    and regression_data['weekLowChange'] > 2
                    ):
                    add_in_csv(regression_data, regressionResult, ws, '##finalBuyContinue-2')
                    return True
    if(regression_data['yearLowChange'] > 5 and regression_data['yearHighChange'] < -5
        and ten_days_more_than_five(regression_data)
        ):
        if(regression_data['forecast_day_PCT_change'] < 0 and regression_data['PCT_day_change'] < 0 
            and (regression_data['PCT_day_change_pre1'] < -1)
            and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
            and regression_data['forecast_day_VOL_change'] <= -20
            ):
            if(-5 < regression_data['PCT_day_change'] < -2 and -5 < regression_data['PCT_change'] < -2):
                if(is_algo_buy(regression_data)):
                    add_in_csv(regression_data, regressionResult, ws, 'ML:finalBuyContinue-3')
                    return True 
                return False
    
    if((1 < regression_data['PCT_day_change'] < 3) 
        and (0.75 < regression_data['PCT_change'] < 3)
        and -75 < regression_data['year2HighChange'] < -25
        and regression_data['year2LowChange'] > 10
        and low_tail_pct(regression_data) < 1
        and ('MaySellCheckChart' in regression_data['filter1']) 
        and ('Reversal' not in regression_data['filter3'])
        and 3 > high_tail_pct(regression_data) > 2
        ):
        if(regression_data['PCT_day_change'] >= 1
            ):
            if(is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, "ML:(check-chart-2-3MidCapCross)MaySellCheckChart-0")
                return True
            return False
        elif(regression_data['PCT_day_change'] >= 1):
            add_in_csv(regression_data, regressionResult, ws, "(check-chart-2-3MidCapCross)MaySellCheckChart-0")
            return True
    
    if(('MaySellCheckChart' in regression_data['filter1'])
        and ('Reversal' not in regression_data['filter3'])
        and regression_data['year2LowChange'] > 10
        and low_tail_pct(regression_data) < 0.5
        and ((((1 < regression_data['PCT_day_change'] <= 2) and (0 < regression_data['PCT_change'] <= 2))
                and 3 > high_tail_pct(regression_data) > 1.8
                )
             or
             (((1.5 < regression_data['PCT_day_change'] <= 4) and (1 < regression_data['PCT_change'] <= 4))
                and 5 > high_tail_pct(regression_data) > 2.8
                )
            )
        ):
        if(is_algo_sell(regression_data)):
            add_in_csv(regression_data, regressionResult, ws, "ML:(check-chart-2-3MidCapCross)MaySellCheckChart-1")
            return True
        return False

#     if((-0.5 < regression_data['PCT_day_change'] < 0.5)
#         and (-0.5 < regression_data['PCT_change'] < 0.5)
#         and low_tail_pct(regression_data) < 0.3
#         and (0.6 < high_tail_pct(regression_data) < 0.9)
#         ):
#         add_in_csv(regression_data, regressionResult, ws, "Test:sellLowTailLessThan0.3-3(checkHillUp)")
    return False   

def sell_trend_break(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
#     if(regression_data['SMA200'] == 1
#        and regression_data['PCT_day_change'] < -2 and regression_data['PCT_change'] < -2
#        ):
#         add_in_csv(regression_data, regressionResult, ws, '##TestBreakOutSellConsolidate-0')
#         return True
    
    flag = False
    if(NIFTY_HIGH and high_tail_pct(regression_data) > 1.5
        and -1 < regression_data['PCT_change'] < 1 and -1 < regression_data['PCT_day_change'] < 1
        and regression_data['forecast_day_PCT10_change'] > -10
        #and ((mlpValue <= -0.5 and kNeighboursValue <= -0.5) or is_algo_sell(regression_data))
        ):
        add_in_csv(regression_data, regressionResult, ws, None, '##TEST:sellCheckLastHourDown')
        flag = True
    
    if(regression_data['yearLowChange'] < 5
       and 'M@[,RSI' in str(regression_data['buyIndia'])
       and 'P@[' not in str(regression_data['sellIndia'])
       and (regression_data['PCT_day_change'] < -5 and regression_data['PCT_change'] < 0)
       #and mlpValue >= 1
       ):
        add_in_csv(regression_data, regressionResult, ws, 'RSISellCandidate(yearLow)-lessThanMinus5')
        flag = True
    
    if(ten_days_more_than_five(regression_data)
        and regression_data['yearLowChange'] > 15
        and regression_data['weekLowChange'] > 5
        and -2 > regression_data['month3HighChange'] > -10
        ):
        if(regression_data['forecast_day_PCT_change'] < -1.5 and regression_data['PCT_day_change'] < 0 and regression_data['PCT_day_change_pre1'] > 0
            and abs(regression_data['PCT_day_change']) > abs(regression_data['PCT_day_change_pre1'])
            #and regression_data['open'] == regression_data['high']
            and regression_data['forecast_day_VOL_change'] >= -20
            ):
                add_in_csv(regression_data, regressionResult, ws, 'finalBreakOutSell-0')
                flag = True
    return flag
    
def sell_final_candidate(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(regression_data['forecast_day_PCT4_change'] >= -0.5
        and regression_data['forecast_day_PCT5_change'] >= -0.5
        and regression_data['forecast_day_PCT7_change'] >= -0.5
        and regression_data['yearLowChange'] > 15 and regression_data['yearHighChange'] < -15
        and regression_data['month3HighChange'] < -3
        and (ten_days_more_than_ten(regression_data)
             or (last_5_day_all_up_except_today(regression_data)
                and ten_days_more_than_seven(regression_data)
                )
             )
        ):  
        if(regression_data['forecast_day_PCT_change'] < 0
            #and regression_data['bar_low'] < regression_data['bar_low_pre1']
            #and regression_data['forecast_day_VOL_change'] > 0
            ):
            if(-4 < regression_data['PCT_day_change'] < -2 and -4 < regression_data['PCT_change'] < -2
                and regression_data['PCT_day_change_pre1'] > 0
                ):
                if(regression_data['SMA25'] > 0 and regression_data['SMA50'] > 0
                    and is_algo_sell(regression_data)
                    ):
                    add_in_csv(regression_data, regressionResult, ws, 'ML:sellFinalCandidate-(lastDayUp)')
                    return True
                elif(regression_data['SMA25'] < 0 and regression_data['SMA50'] < 0
                    and is_algo_buy(regression_data)):
                    add_in_csv(regression_data, regressionResult, ws, 'ML:buyFinalContinue-(lastDayUp)')
                    return True
                elif(is_algo_sell(regression_data)):
                    add_in_csv(regression_data, regressionResult, ws, 'ML:sellFinalCandidate-1-(lastDayUp)')
                    return True
                return False
            if(-5 < regression_data['PCT_day_change'] < -2 and -5 < regression_data['PCT_change'] < -2
                and regression_data['PCT_day_change_pre1'] > 0
                and (regression_data['yearHighChange'] > -30 or regression_data['yearLowChange'] > 30)
                and regression_data['forecast_day_PCT7_change'] > 5
                and regression_data['forecast_day_PCT10_change'] > 10
                ):
                add_in_csv(regression_data, regressionResult, ws, 'sellFinalCandidate-(lastDayUp)-(highChange)')
                return True
            elif(regression_data['PCT_day_change'] < -2 and regression_data['PCT_change'] < -2
                and regression_data['PCT_day_change_pre1'] > 0
                and (regression_data['yearHighChange'] > -30 or regression_data['yearLowChange'] > 30)
                and (regression_data['forecast_day_PCT7_change'] < 5 or regression_data['forecast_day_PCT10_change'] < 10)
                ):
                if(('P@[' not in regression_data['sellIndia'])):
                    add_in_csv(regression_data, regressionResult, ws, 'buyFinalContinue-(lastDayUp)-(highChange)')
                    return True
                else:
                    add_in_csv(regression_data, regressionResult, ws, 'sellFinalCandidate-(lastDayUp)-(highChange)')
                    return True
            if(-4 < regression_data['PCT_day_change'] < -0.5 and -4 < regression_data['PCT_change'] < -0.5
                and regression_data['PCT_day_change_pre1'] < 0
                and 'P@[' in regression_data['buyIndia']
                ):
                add_in_csv(regression_data, regressionResult, ws, 'sellFinalCandidate-(lastDayDown)-(buyPattern)')
                return True
        if((((regression_data['open'] - regression_data['close']) * 1.5 > regression_data['high'] - regression_data['low']) or (regression_data['forecast_day_PCT_change'] < 0 and regression_data['PCT_day_change'] < -1))
            and (regression_data['yearHighChange'] > -30 or regression_data['yearLowChange'] > 30)
            ):
            if(-2.5 < regression_data['PCT_day_change'] < -1 and -2.5 < regression_data['PCT_change'] < -1 
                and no_doji_or_spinning_sell_india(regression_data) and no_doji_or_spinning_buy_india(regression_data)
                ):
                if(regression_data['forecast_day_VOL_change'] > -20
                    and is_algo_sell(regression_data)
                    ):    
                    add_in_csv(regression_data, regressionResult, ws, 'ML:sellFinalCandidate-3')
                    return True
                elif(regression_data['forecast_day_VOL_change'] < -30
                    and is_algo_buy(regression_data)
                    and ('[' in regression_data['sellIndia'])
                    ):
                    add_in_csv(regression_data, regressionResult, ws, 'ML:buyFinalContinue-3')
                    return True
                return False
            if(-5 < regression_data['PCT_day_change'] < -1 and -5 < regression_data['PCT_change'] < -1 
                and no_doji_or_spinning_sell_india(regression_data) and no_doji_or_spinning_buy_india(regression_data)
                ):
                if(regression_data['forecast_day_VOL_change'] < -30
                    and is_algo_sell(regression_data)
                    ):    
                    add_in_csv(regression_data, regressionResult, ws, 'ML:sellFinalCandidate-4')
                    return True
                elif(regression_data['forecast_day_VOL_change'] > -20
                    and is_algo_buy(regression_data)
                    and ('[' in regression_data['sellIndia'])
                    ):    
                    add_in_csv(regression_data, regressionResult, ws, 'ML:buyFinalContinue-4')
                    return True
                return False
    return False            
    
def sell_oi_candidate(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    tail_pct_filter(regression_data, regressionResult)
    tail_reversal_filter(regression_data, regressionResult)
    flag = False
    if(regression_data['close'] > 50
        and ((regression_data['PCT_change'] > -4 and low_tail_pct(regression_data) < 2)
             or (regression_data['PCT_change'] < -4 and low_tail_pct(regression_data) < 3)
             or (low_tail_pct(regression_data) < high_tail_pct(regression_data)))
        ):
        if sell_base_line_sell(regression_data, regressionResult, reg, ws):
            flag = True
    if(regression_data['close'] > 50):
        if sell_base_line_buy(regression_data, regressionResult, reg, ws):
            flag = True
    if(sell_trend_reversal(regression_data, regressionResult, reg, ws)
        and regression_data['close'] > 50
        ):
        flag = True
    if(breakout_or_no_consolidation(regression_data) == True):
        if sell_morning_star_buy(regression_data, regressionResult, reg, ws): 
            flag = True
        if sell_evening_star_sell(regression_data, regressionResult, reg, ws): 
            flag = True
        if sell_oi_negative(regression_data, regressionResult, reg, ws):
            flag = True
        if sell_day_high(regression_data, regressionResult, reg, ws):
            flag = True
        if sell_vol_contract(regression_data, regressionResult, reg, ws):
            flag = True
        if sell_vol_contract_contrarian(regression_data, regressionResult, reg, ws):
            flag = True
        if sell_trend_break(regression_data, regressionResult, reg, ws):
            flag = True
        if sell_final_candidate(regression_data, regressionResult, reg, ws):
            flag = True
    return flag

def sell_oi(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(((regression_data['PCT_day_change'] < -1 or regression_data['PCT_change'] < -1)
             or
             (regression_data['PCT_day_change'] < -0.75 and regression_data['PCT_change'] < -0.75)
             and regression_data['forecast_day_PCT_change'] > -2
             and regression_data['forecast_day_PCT2_change'] > -2
             and regression_data['forecast_day_PCT3_change'] > -2
             and regression_data['forecast_day_PCT4_change'] > -2
             and regression_data['forecast_day_PCT5_change'] > -2
             and regression_data['forecast_day_PCT7_change'] > -2
             and regression_data['forecast_day_PCT10_change'] > -2
            )
        and regression_data['forecast_day_PCT_change'] < 0
        and regression_data['forecast_day_PCT2_change'] < 0
        and regression_data['forecast_day_PCT3_change'] < 0
        and -5 < regression_data['forecast_day_PCT4_change'] < 0
        and regression_data['forecast_day_PCT5_change'] > -5
        and regression_data['forecast_day_PCT7_change'] > -5
        and regression_data['forecast_day_PCT10_change'] > -5
        and (regression_data['PCT_day_change'] > 0
            or regression_data['PCT_day_change_pre1'] > 0
            or regression_data['PCT_day_change_pre2'] > 0
            or regression_data['PCT_day_change_pre3'] > 0
            or regression_data['PCT_day_change_pre4'] > 0
            )
        and (regression_data['forecast_day_VOL_change'] > 150
            or (regression_data['PCT_day_change_pre2'] < 0
                and (((regression_data['volume'] - regression_data['volume_pre2'])*100)/regression_data['volume_pre2']) > 100
                and (((regression_data['volume'] - regression_data['volume_pre3'])*100)/regression_data['volume_pre3']) > 100
               )
           )
        and float(regression_data['contract']) > 100
        and(regression_data['PCT_day_change_pre1'] < 0 
               or (regression_data['volume'] > regression_data['volume_pre2'] and regression_data['volume'] > regression_data['volume_pre3'])
            )
        and regression_data['open'] > 50
        and (last_4_day_all_down(regression_data) == False) #Uncomment0 If very less data
        and (low_tail_pct(regression_data) < 1)
        and (low_tail_pct(regression_data) < 1.5 or (low_tail_pct(regression_data) < high_tail_pct(regression_data)))
        and regression_data['month3LowChange'] > 7.5
        ):
        if(-3 < regression_data['PCT_day_change'] < -1 and -3 < regression_data['PCT_change'] < -1 
            ):
            if(regression_data['forecast_day_PCT10_change'] > 0 or regression_data['forecast_day_PCT7_change'] > 0):
                add_in_csv(regression_data, regressionResult, ws, 'openInterest-0')
                return True
            elif(regression_data['forecast_day_PCT10_change'] > -10 or (regression_data['forecast_day_PCT5_change'] > -5 and regression_data['forecast_day_PCT7_change'] > -5)):
                add_in_csv(regression_data, regressionResult, ws, 'openInterest-1')
                return True
            else:
                add_in_csv(regression_data, regressionResult, ws, 'openInterest-1-Risky')
                return True
        if(-6 < regression_data['PCT_day_change'] < -1 and -6 < regression_data['PCT_change'] < -1 
            and float(regression_data['forecast_day_VOL_change']) > 300 
            ):
            if(regression_data['forecast_day_PCT10_change'] > 0 or regression_data['forecast_day_PCT7_change'] > 0
               ):
                add_in_csv(regression_data, regressionResult, ws, 'openInterest-0-checkConsolidation')
                return True
            elif(regression_data['forecast_day_PCT10_change'] > -10 or (regression_data['forecast_day_PCT5_change'] > -5 and regression_data['forecast_day_PCT7_change'] > -5)
                -4 < regression_data['PCT_day_change'] < -1 and -4 < regression_data['PCT_change'] < -1
                ):
                add_in_csv(regression_data, regressionResult, ws, 'openInterest-1-checkConsolidation')
                return True
            else:
                add_in_csv(regression_data, regressionResult, ws, 'openInterest-1-Risky')
                return True 
    return False

def sell_other_indicator(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    
    if(regression_data['close'] > 50
        ):
        sell_downingMA(regression_data, regressionResult, reg, ws)
        sell_study_downingMA(regression_data, regressionResult, reg, ws)
        sell_market_downtrend(regression_data, regressionResult, reg, ws)
        sell_supertrend(regression_data, regressionResult, reg, ws)
        sell_heavy_downtrend(regression_data, regressionResult, reg, ws)
        sell_check_chart(regression_data, regressionResult, reg, ws)
        return True
    return False

def sell_downingMA(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    return False
    #         if(-10 < regression_data['SMA50'] < 0
#             and 0 < regression_data['SMA100'] < regression_data['SMA200']
#             and 25 < regression_data['SMA200'] < 70
#             and regression_data['PCT_day_change'] > 1
#             and regression_data['PCT_change'] > 1
#             and ('[') not in regression_data['buyIndia']
#             and regression_data['series_trend'] != "upTrend"
#             and all_day_pct_change_positive_except_today(regression_data) == False
#             ):
#             add_in_csv(regression_data, regressionResult, ws, '##ALL:sellDowningMA')
#         elif(-10 < regression_data['SMA50'] < 0
#             and 0 < regression_data['SMA100'] < regression_data['SMA200']
#             and 10 < regression_data['SMA200'] < 70
#             and regression_data['PCT_day_change'] > 1
#             and regression_data['PCT_change'] > 1
#             and ('[') not in regression_data['buyIndia']
#             and regression_data['series_trend'] != "upTrend"
#             and all_day_pct_change_positive_except_today(regression_data) == False
#             ):
#             add_in_csv(regression_data, regressionResult, ws, '##ALL:sellDowningMA-Risky')
#         elif(regression_data['SMA25'] < 0
#             and -3 < regression_data['SMA50'] < 1
#             and 1 < regression_data['SMA100'] < regression_data['SMA200']
#             and 15 < regression_data['SMA200'] < 70
#             and regression_data['PCT_day_change'] > 0.5
#             and regression_data['PCT_change'] > 0
#             and ('[') not in regression_data['buyIndia']
#             and regression_data['series_trend'] != "upTrend"
#             and all_day_pct_change_positive_except_today(regression_data) == False
#             ):
#             add_in_csv(regression_data, regressionResult, ws, '##ALL:sellDowningMA-Risky-1')
#         elif(regression_data['SMA9'] < 0
#             and regression_data['SMA25'] < 0
#             and regression_data['SMA50'] > 0
#             and regression_data['SMA50'] < regression_data['SMA100'] < regression_data['SMA200']
#             and regression_data['SMA200'] > 10
#             and -2 < regression_data['PCT_day_change'] < -4
#             and -2 < regression_data['PCT_change'] < -4
#             and regression_data['series_trend'] != "upTrend"
#             and all_day_pct_change_positive_except_today(regression_data) == False
#             ):
#             add_in_csv(regression_data, regressionResult, ws, '##ALL:sellDowningMA-downTrend'
#             if(1.5 < regression_data['PCT_change'] < 3
#                 and regression_data['SMA9'] > -2
#                 and regression_data['SMA25'] > 0
#                 ):
#                 add_in_csv(regression_data, regressionResult, ws, 'ALL(Test):sellDowningMA-Downtrend')

def sell_study_downingMA(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    if(regression_data['SMA200'] > regression_data['SMA100'] > regression_data['SMA50'] > regression_data['SMA25'] > regression_data['SMA9']
        and regression_data['series_trend'] != "upTrend"
        and all_day_pct_change_positive_except_today(regression_data) == False
        ):
        add_in_csv(regression_data, regressionResult, ws, '$$(Study)$$:DowningMA-Downtrend-1')

def sell_market_downtrend(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    if(('P@' not in regression_data['buyIndia'])
        and ((-6 < regression_data['PCT_change'] < -2) 
            and (-6 < regression_data['PCT_day_change'] < -2)
            and regression_data['close'] < regression_data['bar_low_pre1']
            )
        #and regression_data['trend'] == 'down'
        ):
        if(regression_data['trend'] == 'down'):
            if(('year2HighReversal(Confirm)' in regression_data['filter3'])):
                add_in_csv(regression_data, regressionResult, ws, "##DOWNTREND:sellYear2HighReversal(InDownTrend)")
            if(('yearHighReversal(Confirm)' in regression_data['filter3'])):
                add_in_csv(regression_data, regressionResult, ws, '##DOWNTREND:sellYearHighReversal(InDownTrend)')
            if(('month6HighReversal(Confirm)' in regression_data['filter3'])):
                add_in_csv(regression_data, regressionResult, ws, '##DOWNTREND:sellMonth6HighReversal(InDownTrend)')
#             if(('month3HighReversal(Confirm)' in regression_data['filter3'])):
#                 add_in_csv(regression_data, regressionResult, ws, '##DOWNTREND:sellMonth3HighReversal(InDownTrend)')
#             if(regression_data['month3LowChange'] > 15 and (regression_data['month6LowChange'] > 20 or regression_data['yearLowChange'] > 30)
#                 ):
#                 if(('nearYear2High' in regression_data['filter3'])):
#                     add_in_csv(regression_data, regressionResult, ws, None)
#                 if(('nearYearHigh' in regression_data['filter3'])):
#                     add_in_csv(regression_data, regressionResult, ws, '##DOWNTREND:sellYearHigh(InDownTrend)')
#                 if(('nearMonth6High' in regression_data['filter3'])):
#                     add_in_csv(regression_data, regressionResult, ws, '##DOWNTREND:sellMonth6High(InDownTrend)')
#                 if(('nearMonth3High' in regression_data['filter3'])):
#                     add_in_csv(regression_data, regressionResult, ws, '##DOWNTREND:sellMonth3High(InDownTrend)')
        if(((regression_data['PCT_day_change'] < -2) or (regression_data['PCT_change'] < -2) or ('MaySellCheckChart' in regression_data['filter1']))):
            if('yearLowBreak' in regression_data['filter3']
                and regression_data['year2LowChange'] > 5
                ):
                add_in_csv(regression_data, regressionResult, ws, '##DOWNTREND:sellYearLowBreak')
            if('month6LowBreak' in regression_data['filter3']
                and regression_data['yearLowChange'] > 5
                ):
                add_in_csv(regression_data, regressionResult, ws, '##DOWNTREND:sellMonth6LowBreak')
            if('month3LowBreak' in regression_data['filter3']
                and regression_data['month6LowChange'] > 0
                ):
                add_in_csv(regression_data, regressionResult, ws, '##DOWNTREND:sellMonth3LowBreak')

def sell_supertrend(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    
    if(regression_data['close'] > 50
        ):
        if(0 > regression_data['forecast_day_PCT2_change'] > regression_data['forecast_day_PCT3_change'] > regression_data['forecast_day_PCT4_change'] > regression_data['forecast_day_PCT5_change']
            and regression_data['forecast_day_PCT5_change'] < -5
            and -1.5 < regression_data['PCT_day_change_pre1'] < 0.5
            and -0.5 < regression_data['PCT_day_change'] < 0.5
            and regression_data['yearHighChange'] < -5
            and regression_data['yearLowChange'] > 5
            and regression_data['month3LowChange'] > 5
            #and regression_data['high'] < regression_data['high_pre1']
            ):
            if(abs_month3High_more_than_month3Low(regression_data)
#                 and regression_data['yearHighChange'] < -10
#                 and regression_data['yearLowChange'] > 10
#                 and regression_data['month3LowChange'] > 10
                ):
                if(regression_data['PCT_day_change'] > 0
                    and -1 < regression_data['PCT_day_change_pre1'] < 0
                    and ('[' in regression_data['buyIndia'])
                    and low_tail_pct(regression_data) < 2
                    ):
                    add_in_csv(regression_data, regressionResult, ws, '##ALL(Test):sellSuperTrend-(Risky)')
                elif((regression_data['PCT_day_change'] > 0
                    or regression_data['forecast_day_PCT_change'] > 0)
                    and (('[' not in regression_data['sellIndia']) and ('[' in regression_data['buyIndia']))
                    ):
                    add_in_csv(regression_data, regressionResult, ws, '##ALL(Test):buySuperTrend-0')
            elif(abs_month3High_less_than_month3Low(regression_data)):
                if(regression_data['PCT_day_change'] > 0
                    and -1 < regression_data['PCT_day_change_pre1'] < 0
                    and low_tail_pct(regression_data) < 2.5
                    ):
                    add_in_csv(regression_data, regressionResult, ws, '##ALL(Test):sellSuperTrend-0')
            return True
        return False

def sell_heavy_downtrend(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    return False
#         if((('nearYear2High' in regression_data['filter3']) 
#                 or ('nearYearHigh' in regression_data['filter3'])
#                 or ('nearMonth6High' in regression_data['filter3'])
#                 or ('year2HighReversal(Confirm)' in regression_data['filter3'])
#                 or ('yearHighReversal(Confirm)' in regression_data['filter3'])
#                 or ('month6HighReversal(Confirm)' in regression_data['filter3'])
#                 or ('year2HighBreak' in regression_data['filter3'])
#                 or ('yearHighBreak' in regression_data['filter3'])
#                 or ('month6HighBreak' in regression_data['filter3'])
#             )
#             and regression_data['SMA200'] > regression_data['SMA100'] > regression_data['SMA50'] > regression_data['SMA25'] > regression_data['SMA9']
#             and regression_data['series_trend'] == "downTrend"
#             and ((abs(regression_data['PCT_day_change']) > abs(regression_data['PCT_day_change_pre1']))
#                 or regression_data['PCT_change'] > 2
#                 )
#             ):
#             if(((0 < regression_data['PCT_change'] < 3) and (0 < regression_data['PCT_day_change'] < 3))
#             ):
#                 add_in_csv(regression_data, regressionResult, ws, '##ALL:(Test)sellSeilingReversal-0')
#             elif(regression_data['PCT_day_change_pre2'] > 0 and regression_data['PCT_day_change'] < -1.5):
#                 add_in_csv(regression_data, regressionResult, ws, '##ALL:(Test)sellSeilingReversal-1')
                
#To-Do        
#         if(regression_data['series_trend'] == "downTrend"
#             and (-15 < regression_data['forecast_day_PCT4_change'] < 0)
#             and (-15 < regression_data['forecast_day_PCT5_change'] < 0)
#             and (-15 < regression_data['forecast_day_PCT7_change'] < 0)
#             and (-15 < regression_data['forecast_day_PCT10_change'])
#             ):
#             if((regression_data['month3LowChange'] > 5)
#                 and ((-5 < regression_data['PCT_change'] < 0) and (-5 < regression_data['PCT_day_change'] < 0))
#                 and ('[') not in regression_data['buyIndia']
#                 and regression_data['close_pre1'] < regression_data['close_pre2']
#                 ):
#                 if((-5 < regression_data['PCT_change'] < -4) and (-5 < regression_data['PCT_day_change'] < -4)
#                 ):
#                     add_in_csv(regression_data, regressionResult, ws, '##ALL:sellHeavyDownTrend-0-Continue')
#                 elif(ten_days_less_than_minus_seven(regression_data)
#                      and(('nearMonth3Low' in regression_data['filter3'])
#                         or ('nearMonth6Low' in regression_data['filter3'])
#                         )
#                 ):
#                     add_in_csv(regression_data, regressionResult, ws, '##ALL:sellHeavyDownTrend-1-Continue')
#             if((regression_data['month3LowChange'] < 4)
#                 and ((-5 < regression_data['PCT_change'] < 0) and (-5 < regression_data['PCT_day_change'] < 0))
#                 ):
#                 if((-5 < regression_data['PCT_change'] < -2) and (-5 < regression_data['PCT_day_change'] < -1)
#                     and ten_days_less_than_minus_seven(regression_data)
#                     and(('nearMonth3Low' in regression_data['filter3'])
#                         or ('month3LowBreak' in regression_data['filter3'])
#                         or ('nearMonth6Low' in regression_data['filter3'])
#                         )
#                 ):
#                     add_in_csv(regression_data, regressionResult, ws, '##ALL:buyHeavyDownTrend-0-Reversal')

def sell_check_chart(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    if(('nearMonth3Low' in regression_data['filter3']) 
            or ('month3LowBreak' in regression_data['filter3'])
            or ('month3LowReversal(Confirm)' in regression_data['filter3'])
        ):
        if((regression_data['forecast_day_PCT4_change'] > 0)
            and (regression_data['forecast_day_PCT5_change'] > 0)
            and (regression_data['forecast_day_PCT7_change'] > 0)
            and ((regression_data['forecast_day_PCT_change'] < 0 and (-4 < regression_data['PCT_change'] < -2) and (-4 < regression_data['PCT_day_change'] < -2))
                 or (regression_data['series_trend'] == "upTrend" and (-4 < regression_data['PCT_change'] < -1) and (-4 < regression_data['PCT_day_change'] < 1)))
            and ('[') not in regression_data['buyIndia']
            and regression_data['low'] < regression_data['low_pre1']
            and regression_data['bar_low'] < regression_data['bar_low_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, '##ALL:(Check-chart)sellMonth3Low-Continue(InUpTrend)')
            
    #Check for last 5 from latest down should crossover
    if(('nearMonth3Low' in regression_data['filter3']) 
        or ('month3LowBreak' in regression_data['filter3'])
        or ('month3LowReversal(Confirm)' in regression_data['filter3'])
        ):
        if(regression_data['month3HighChange'] < -15
            and ((1 < regression_data['PCT_change'] < 5) and (2 < regression_data['PCT_day_change'] < 5))
            and regression_data['close'] > regression_data['bar_high_pre1']
            and regression_data['close'] > regression_data['bar_high_pre2']
            ):
            if(regression_data['forecast_day_PCT5_change'] > 0):
                add_in_csv(regression_data, regressionResult, ws, '##(Test)(Check-chart-sell):month3Low-InPlus')
            else:
                add_in_csv(regression_data, regressionResult, ws, '##(Test)(Check-chart-buy):month3Low-InPlus')
    elif(('nearMonth6Low' in regression_data['filter3']) 
        or ('month6LowReversal(Confirm)' in regression_data['filter3'])
        ):
        if(regression_data['month6LowChange'] < -20
            and ((1 < regression_data['PCT_change'] < 5) and (2 < regression_data['PCT_day_change'] < 5))
            and regression_data['close'] > regression_data['bar_high_pre1']
            and regression_data['close'] > regression_data['bar_high_pre2']
            ):
            if(regression_data['forecast_day_PCT5_change'] > 0):
                add_in_csv(regression_data, regressionResult, ws, '##(Test)(Check-chart-sell):month6Low-InPlus')
            else:
                add_in_csv(regression_data, regressionResult, ws, '##(Test)(Check-chart-buy):month6Low-InPlus')
                
    elif(('nearYearLow' in regression_data['filter3']) 
        or ('yearLowReversal(Confirm)' in regression_data['filter3'])
        ):
        if(regression_data['month6LowChange'] < -20
            and ((1 < regression_data['PCT_change'] < 5) and (2 < regression_data['PCT_day_change'] < 5))
            and regression_data['close'] > regression_data['bar_high_pre1']
            and regression_data['close'] > regression_data['bar_high_pre2']
            ):
            if(regression_data['forecast_day_PCT5_change'] > 0):
                add_in_csv(regression_data, regressionResult, ws, '##(Test)(Check-chart-sell):yearLow-InPlus')
            else:
                add_in_csv(regression_data, regressionResult, ws, '##(Test)(Check-chart-buy):yearLow-InPlus')
            
    if(('nearMonth3Low' in regression_data['filter3']) 
        or ('month3LowBreak' in regression_data['filter3'])
        #or ('month3LowReversal(Confirm)' in regression_data['filter3'])
        ):
        if(regression_data['month3HighChange'] < -15
            and ((regression_data['PCT_change'] < 2) and (1 < regression_data['PCT_day_change'] < 2))
            and regression_data['PCT_day_change_pre1'] < -1.5
            and regression_data['PCT_change_pre1'] < -0.5
            and regression_data['close'] < regression_data['bar_high_pre1']
            and (abs(regression_data['PCT_day_change']) * 2 < abs(regression_data['PCT_day_change_pre1']))
            ):
            add_in_csv(regression_data, regressionResult, ws, '##(Test)(Check-chart-buy):month3Low-InPlus-PCTChangeLessThan2')
    elif(('nearMonth6Low' in regression_data['filter3'])
        or ('month6LowBreak' in regression_data['filter3'])
        #or ('month6LowReversal(Confirm)' in regression_data['filter3'])
        ):
        if(regression_data['month6LowChange'] < -20
            and ((regression_data['PCT_change'] < 2) and (1 < regression_data['PCT_day_change'] < 2))
            and regression_data['PCT_day_change_pre1'] < -1.5
            and regression_data['PCT_change_pre1'] < -0.5
            and regression_data['close'] < regression_data['bar_high_pre1']
            and (abs(regression_data['PCT_day_change']) * 2 < abs(regression_data['PCT_day_change_pre1']))
            ):
            add_in_csv(regression_data, regressionResult, ws, '##(Test)(Check-chart-buy):month6Low-InPlus-PCTChangeLessThan2')        
            
#         if((('nearYear2Low' in regression_data['filter3']) 
#             or ('year2LowReversal(Confirm)' in regression_data['filter3'])
#             or ('year2LowBreak' in regression_data['filter3'])
#             )):    
#             if(regression_data['year2HighChange'] < -50
#                 and regression_data['year2LowChange'] < 1
#                 and ((regression_data['PCT_change'] < -1) and (regression_data['PCT_day_change'] < -1))
#                 and regression_data['close'] < regression_data['bar_low_pre1']
#                 ):
#                 if(regression_data['PCT_change'] < -4
#                     and ('year2LowBreak' in regression_data['filter3'])
#                     ):
#                     add_in_csv(regression_data, regressionResult, ws, '##(Test)(Check-chart-buy):year2Low-InMinus')
#                 elif(regression_data['PCT_change'] < -2.5 and regression_data['PCT_day_change'] < -2.5
#                     and ('nearYear2Low' in regression_data['filter3'])
#                     ):
#                     add_in_csv(regression_data, regressionResult, ws, '##(Test)(Check-chart-sell):year2Low-InMinus')
#                 else:
#                     add_in_csv(regression_data, regressionResult, ws, '##(Test)(Check-chart):year2Low-InMinus')
#         elif((('nearYearLow' in regression_data['filter3'])
#             or ('yearLowReversal(Confirm)' in regression_data['filter3'])
#             or ('yearLowBreak' in regression_data['filter3'])
#             )):
#             if(regression_data['yearHighChange'] < -40
#                 and regression_data['yearLowChange'] < 1
#                 and ((regression_data['PCT_change'] < -1) and (regression_data['PCT_day_change'] < -1))
#                 and regression_data['close'] < regression_data['bar_low_pre1']
#                 ):
#                 if(regression_data['PCT_change'] < -4
#                     and ('yearLowBreak' in regression_data['filter3'])
#                     ):
#                     add_in_csv(regression_data, regressionResult, ws, '##(Test)(Check-chart-buy):yearLow-InMinus')
#                 elif(regression_data['PCT_change'] < -2.5 and regression_data['PCT_day_change'] < -2.5
#                     and ('nearYearLow' in regression_data['filter3'])
#                     ):
#                     add_in_csv(regression_data, regressionResult, ws, '##(Test)(Check-chart-sell):yearLow-InMinus')
#                 else:
#                     add_in_csv(regression_data, regressionResult, ws, '##(Test)(Check-chart):yearLow-InMinus')
    
    if((-0.5 < regression_data['PCT_change'] < 0.5)
        and (0 < regression_data['PCT_day_change'] < 1)
        and abs(regression_data['PCT_change'] - regression_data['PCT_day_change']) < 0.8
        and low_tail_pct(regression_data) < 0.5
        and (0.6 < high_tail_pct(regression_data) < 1.5)
        and (high_tail_pct(regression_data) - low_tail_pct(regression_data)) > 0.6
        and regression_data['PCT_day_change_pre1'] < -1.8
        ):
        if(abs_month3High_less_than_month3Low(regression_data)
            ):
            add_in_csv(regression_data, regressionResult, ws, '##ALL(Check-chart):MaySellCheckChart-(|_|`|)')
        else:
            add_in_csv(regression_data, regressionResult, ws, '##ALL(Check-chart):MaySellCheckChart-(Risky)-(|_|`|)')
    elif(
        (((mlpValue < -0.3) and (kNeighboursValue < -0.3) and ((mlpValue_other < 0) or (kNeighboursValue_other < 0)))
             or ((mlpValue_other < -0.3) and (kNeighboursValue_other < -0.3) and ((mlpValue < 0) or (kNeighboursValue < 0))))
        and (1 <= regression_data['PCT_day_change'] < 2.5)
        and (1 <= regression_data['PCT_change'] < 4)
        ):
        if(('MaySellCheckChart' in regression_data['filter1'])
            and low_tail_pct(regression_data) < 0.8
            and (1 < regression_data['forecast_day_PCT5_change'] < 15)
            and (1 < regression_data['forecast_day_PCT7_change'] < 15)
            and (1 < regression_data['forecast_day_PCT10_change'] < 15)
            ):
            if(1.8 < high_tail_pct(regression_data) < 2.5):
                add_in_csv(regression_data, regressionResult, ws, '##ALL(Check-chart):MaySellCheckChart-(IndexNotDownInSecondHalf)')
        
def sell_test(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
#     flag = sell_other_indicator(regression_data, regressionResult, reg, ws)
#     return flag
    if(regression_data['close'] < 50
        ):
        return False
    #flag = sell_final_candidate(regression_data, regressionResult, reg, ws)
    #return flag
    
    if((regression_data['yearHighChange'] < -20 and regression_data['month3HighChange'] < -15)
       and (regression_data['yearLowChange'] > 15 or regression_data['month3LowChange'] > 10)
       and regression_data['forecast_day_PCT_change'] < 0
       and regression_data['forecast_day_PCT2_change'] < 0
       and regression_data['forecast_day_PCT3_change'] < 0
       and (regression_data['PCT_day_change_pre1'] > 0 or regression_data['PCT_day_change_pre2'] > 0)
       ):
        if(#abs_yearHigh_less_than_yearLow(regression_data)
           -4 < regression_data['PCT_day_change'] < -2 and -4 < regression_data['forecast_day_PCT_change'] < -2
           and regression_data['series_trend'] != 'uptrend'
           and str(regression_data['score']) != '10' 
           and (regression_data['forecast_day_PCT10_change'] > 5)
           ):
            add_in_csv(regression_data, regressionResult, None, 'sellDownTrend-0')
            return True
        if(#abs_yearHigh_less_than_yearLow(regression_data)
           -4 < regression_data['PCT_day_change'] < -2 and -4 < regression_data['forecast_day_PCT_change'] < -2
           and regression_data['series_trend'] != 'upTrend'
           and str(regression_data['score']) != '10' 
           and (regression_data['forecast_day_PCT7_change'] > 0 and regression_data['forecast_day_PCT10_change'] > 0)
           ):
            add_in_csv(regression_data, regressionResult, None, 'sellDownTrend-00')
            return True
        if(#abs_yearHigh_less_than_yearLow(regression_data)
           regression_data['yearLowChange'] > 10 
           and -4 < regression_data['PCT_day_change'] < -2 and -4 < regression_data['forecast_day_PCT_change'] < -2
           and regression_data['forecast_day_PCT_change'] > regression_data['PCT_change']
           and regression_data['PCT_day_change_pre1'] > 0
           and regression_data['series_trend'] != 'upTrend'
           and str(regression_data['score']) != '10'
           and regression_data['forecast_day_PCT5_change'] > -3
           and (regression_data['forecast_day_PCT7_change'] > -5 and regression_data['forecast_day_PCT10_change'] > -7) 
           ):
            add_in_csv(regression_data, regressionResult, None, '##Test:longDownTrend-0-IndexNotDownLastDay(checkBase)')
            return True
        if(#abs_yearHigh_less_than_yearLow(regression_data)
           regression_data['yearLowChange'] > 10 
           and -4 < regression_data['PCT_day_change'] < -2 and -4 < regression_data['forecast_day_PCT_change'] 
           and regression_data['forecast_day_PCT_change'] > regression_data['PCT_change']
           and regression_data['series_trend'] != 'upTrend'
           and str(regression_data['score']) != '10'
           and (regression_data['forecast_day_PCT7_change'] > -5 and regression_data['forecast_day_PCT10_change'] > -7) 
           ):
            add_in_csv(regression_data, regressionResult, None, '##Test:longDownTrend-1-IndexNotDownLastDay(checkBase)')
            return True
        if(-4 < regression_data['PCT_day_change'] < -2 and -4 < regression_data['forecast_day_PCT_change'] 
           and regression_data['forecast_day_PCT_change'] > regression_data['PCT_change']
           and regression_data['series_trend'] != 'upTrend'
           and str(regression_data['score']) != '10'
           and (regression_data['forecast_day_PCT7_change'] > -5 and regression_data['forecast_day_PCT10_change'] > -7) 
           ):
            add_in_csv(regression_data, regressionResult, None, '##Test:longDownTrend-2-IndexNotDownLastDay(checkBase)')
            return True
        if(-4 < regression_data['PCT_day_change'] < -2 and -4 < regression_data['forecast_day_PCT_change'] 
           and regression_data['forecast_day_PCT_change'] > regression_data['PCT_change']
           and regression_data['series_trend'] != 'upTrend'
           and str(regression_data['score']) != '10'
           and (regression_data['forecast_day_PCT7_change'] > -10 and regression_data['forecast_day_PCT10_change'] > -10) 
           ):
            #add_in_csv(regression_data, regressionResult, None, 'sellDownTrend-2-onlyNews')
            return False
    if(all_day_pct_change_negative(regression_data) and -4 < regression_data['PCT_day_change'] < -2 and regression_data['yearLowChange'] > 30
        and regression_data['forecast_day_PCT10_change'] <= regression_data['PCT_change'] - 2
        and regression_data['forecast_day_PCT10_change'] <= regression_data['PCT_day_change'] - 2
        and float(regression_data['forecast_day_VOL_change']) > 30
        and regression_data['PCT_day_change_pre1'] < 0.5
        and float(regression_data['contract']) > 10
        and no_doji_or_spinning_sell_india(regression_data)):
        add_in_csv(regression_data, regressionResult, ws_sellDownTrend, '##Test:longDownTrend-Risky-IndexNotDownLastDay(checkBase)')
        return True
    return False

def sell_all_common(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    sell_other_indicator(regression_data, regressionResult, reg, ws)
    
    if((5 > regression_data['PCT_day_change'] > 3) and (regression_data['PCT_change'] > 1.5)
        and (((mlpValue < -0.3) and (kNeighboursValue < -0.3) and ((mlpValue_other < 0.2) and (kNeighboursValue_other < 0)))
             or ((mlpValue_other < -0.3) and (kNeighboursValue_other < -0.3) and ((mlpValue < 0.2) and (kNeighboursValue < 0))))
        ):
        if('P@' not in regression_data['buyIndia']):
            add_in_csv(regression_data, regressionResult, ws, '##Common:sellDayReversalCandidate-0')
        else:
            add_in_csv(regression_data, regressionResult, ws, '##Common:sellDayReversalCandidate-1')
    
    if((((mlpValue < -0.3) and (kNeighboursValue < -0.3) and ((mlpValue_other < 0) or (kNeighboursValue_other < 0)))
             or ((mlpValue_other < -0.3) and (kNeighboursValue_other < -0.3) and ((mlpValue < 0) or (kNeighboursValue < 0))))
        ):
        if((1 < regression_data['PCT_day_change'] < 3) and (regression_data['forecast_day_PCT10_change'] < -5)
            and low_tail_pct(regression_data) < 1.5
            and high_tail_pct(regression_data) > 2
            ):
                add_in_csv(regression_data, regressionResult, ws, '##Common:MaySellCheckChart-0')
    
    if((mlpValue < 0) 
        and (kNeighboursValue < 0) 
        and (mlpValue_other < 0) 
        and (kNeighboursValue_other < 0)
        and regression_data['PCT_day_change_pre1'] > 0
        and (-5 < regression_data['PCT_day_change'] < -1) and (-4 < regression_data['PCT_change'] < -1)
        and regression_data['month3HighChange'] < -10
        and regression_data['month3LowChange'] > 10
        and regression_data['trend'] != 'down'
        ):    
        if(regression_data['SMA9'] < -1):
            add_in_csv(regression_data, regressionResult, ws, '##Common:sellNotM3HighLow-0(SMA9LT-1)') 
        elif(regression_data['SMA25'] < 0):
            add_in_csv(regression_data, regressionResult, ws, '##Common:sellNotM3HighLow-0(SMA25LT0)') 
        else:
            add_in_csv(regression_data, regressionResult, ws, None) 
    
    if((((mlpValue < -0.3) and (kNeighboursValue < -0.3) and ((mlpValue_other < 0) or (kNeighboursValue_other < 0)))
            or ((mlpValue_other < -0.3) and (kNeighboursValue_other < -0.3) and ((mlpValue < 0) or (kNeighboursValue < 0))))
        and (regression_data['PCT_day_change_pre1'] > 0 or regression_data['PCT_day_change_pre2'] > 0)
        and (-5 < regression_data['PCT_day_change'] < -1) and (-4 < regression_data['PCT_change'] < -1)
        and regression_data['yearHighChange'] < -10
        and regression_data['yearLowChange'] > 10
        and regression_data['trend'] != 'down'
        and abs_month3High_more_than_month3Low(regression_data)
        ):    
        if(regression_data['SMA9'] < -1):
            add_in_csv(regression_data, regressionResult, ws, '##Common:sellNotM3HighLow-1(SMA9LT-1)') 
        elif(regression_data['SMA25'] < 0):
            add_in_csv(regression_data, regressionResult, ws, '##Common:sellNotM3HighLow-1(SMA25LT0)') 
        else:
            add_in_csv(regression_data, regressionResult, ws, None)
            
    if(is_algo_sell(regression_data)
        and mlpValue_other < 0.5
        and kNeighboursValue_other < 0.5
        and (mlpValue_other < -0.5 or kNeighboursValue_other < -0.5)
        and ('P@' not in regression_data['buyIndia'])
        #and (((-5 < regression_data['PCT_change'] < -2) and (-5 < regression_data['PCT_day_change'] < -2)) or ((-0.5 < regression_data['PCT_day_change'] < 4) and (-0.5 < regression_data['PCT_change'] < 4)))
        #and regression_data['trend'] == 'down'
        ):
        if(regression_data['trend'] == 'down'):
            if(('year2HighReversal(Confirm)' in regression_data['filter3'])):
                add_in_csv(regression_data, regressionResult, ws, '##DOWNTREND:sellYear2HighReversal(Confirm)')
            if(('yearHighReversal(Confirm)' in regression_data['filter3'])):
                add_in_csv(regression_data, regressionResult, ws, '##DOWNTREND:sellYearHighReversal(Confirm)')
            if(('month6HighReversal(Confirm)' in regression_data['filter3'])):
                add_in_csv(regression_data, regressionResult, ws, '##DOWNTREND:sellMonth6HighReversal(Confirm)')
        if('yearLowBreak' in regression_data['filter3']):
            add_in_csv(regression_data, regressionResult, ws, '##DOWNTREND:sellYearLowBreak')
        if('month6LowBreak' in regression_data['filter3']):
            add_in_csv(regression_data, regressionResult, ws, '##DOWNTREND:sellMonth6LowBreak')
        if('month3LowBreak' in regression_data['filter3']):
            add_in_csv(regression_data, regressionResult, ws, '##DOWNTREND:sellMonth3LowBreak')  
                      
    if(-4 < regression_data['PCT_change'] < 1
        and (last_7_day_all_down(regression_data) == False)
        and (MARKET_IN_DOWNTREND or (last_4_day_all_down(regression_data) == False)) #Uncomment0 If very less data
        and low_tail_pct(regression_data) < 1
        ):
        return True
    
#     if((-4 < regression_data['PCT_day_change'] < -1 
#         and (regression_data['PCT_day_change'] < -1.5 or regression_data['PCT_change'] < -1.5) 
#         and low_tail_pct(regression_data) < 0.3
#         )
#         and mlpValue <= 0 and kNeighboursValue <= 0
#         and (mlpValue_other <= 0 or kNeighboursValue_other <= 0)
#         ):
#         if (regression_data['PCT_day_change_pre1'] > 0):
#             add_in_csv(regression_data, regressionResult, ws, "##Common:sellLowTailLessThan0.3-0(checkHillDown)")
#         elif ((regression_data['PCT_day_change_pre1'] > -1) and regression_data['PCT_day_change_pre2'] > 0):
#             add_in_csv(regression_data, regressionResult, ws, "##Common:sellLowTailLessThan0.3-1(checkHillDown)")
#         elif ((-2 < regression_data['PCT_day_change']) and high_tail_pct(regression_data) < 0.3):
#             add_in_csv(regression_data, regressionResult, ws, "##Common:sellLowTailLessThan0.3-2(checkHillDown)")
    
    return False

def sell_all_filter(regression_data, regressionResult, reg, ws_sellAllFilter):
    flag = False
    if sell_year_high(regression_data, regressionResult, reg, None, None):
        add_in_csv(regression_data, regressionResult, ws_sellAllFilter, None)
        flag = True
    if sell_year_low(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws_sellAllFilter, None)
        flag = True
    if sell_up_trend(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws_sellAllFilter, None)
        flag = True
    if sell_down_trend(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws_sellAllFilter, None)
        flag = True
    if sell_final(regression_data, regressionResult, reg, None, None):
        add_in_csv(regression_data, regressionResult, ws_sellAllFilter, None)
        flag = True
    if sell_high_indicators(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws_sellAllFilter, None)
        flag = True
    if sell_pattern(regression_data, regressionResult, reg, None, None):
        add_in_csv(regression_data, regressionResult, ws_sellAllFilter, None)
        flag = True
    if sell_oi(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws_sellAllFilter, None)
        flag = True
    return flag
