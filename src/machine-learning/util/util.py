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

def add_in_csv(regression_data, regressionResult, ws=None, filter=None, filter1=None, filter2=None, filter3=None, filter4=None, filter5=None, filter6=None):
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
        if ((filter5 is not None) and (filter5 not in regression_data['filter5'])):
            regression_data['filter5'] = regression_data['filter5'] + filter5 + ','  
        tempRegressionResult = regressionResult.copy() 
        tempRegressionResult.append(regression_data['filter1'])
        tempRegressionResult.append(regression_data['filter2'])
        tempRegressionResult.append(regression_data['filter3'])
        tempRegressionResult.append(regression_data['filter4'])
        tempRegressionResult.append(regression_data['filter5'])
        tempRegressionResult.append(regression_data['filter'])
        tempRegressionResult.append(regression_data['filter_avg'])
        tempRegressionResult.append(regression_data['filter_count'])
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
        if ((filter5 is not None) and (filter5 not in regression_data['filter5'])):
            regression_data['filter5'] = regression_data['filter5'] + filter5 + ','   
        if ((filter6 is not None) and (filter6 not in regression_data['filter6'])):
            regression_data['filter6'] = regression_data['filter6'] + filter6 + ','   
        
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

def is_algo_buy(regression_data, resticted=False):
    if TEST:
        return True
#     if not_from_rule == False:
#         return True
    REG_MIN = -1.5
    CLA_MIN = -1
    if resticted:
        REG_MIN = -0.5
        CLA_MIN = 0
    if((regression_data['mlpValue_reg'] >= REG_MIN) and (regression_data['kNeighboursValue_reg'] >= REG_MIN)
        and (regression_data['mlpValue_reg_other'] >= REG_MIN) and (regression_data['kNeighboursValue_reg_other'] >= REG_MIN)
        and (regression_data['mlpValue_cla'] >= CLA_MIN) and (regression_data['kNeighboursValue_cla'] >= CLA_MIN)
        and (regression_data['mlpValue_cla_other'] >= CLA_MIN) and (regression_data['kNeighboursValue_cla_other'] >= CLA_MIN)
        ):
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
    
def is_algo_sell(regression_data, resticted=False):
    if TEST:
        return True
#     if not_from_rule == False:
#         return True
    REG_MAX = 1.5
    CLA_MAX = 1
    if resticted:
        REG_MAX = 0.5
        CLA_MAX = 0
    if((regression_data['mlpValue_reg'] <= REG_MAX) and (regression_data['kNeighboursValue_reg'] <= REG_MAX)
        and (regression_data['mlpValue_reg_other'] <= REG_MAX) and (regression_data['kNeighboursValue_reg_other'] <= REG_MAX)
        and (regression_data['mlpValue_cla'] <= CLA_MAX) and (regression_data['kNeighboursValue_cla'] <= CLA_MAX)
        and (regression_data['mlpValue_cla_other'] <= CLA_MAX) and (regression_data['kNeighboursValue_cla_other'] <= CLA_MAX)
        ):
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

def is_algo_buy_classifier(regression_data, resticted=False):
    REG_MIN = -1.5
    CLA_MIN = -1
    if resticted:
        REG_MIN = -0.5
        CLA_MIN = 0
    if((regression_data['mlpValue_reg'] >= REG_MIN) and (regression_data['kNeighboursValue_reg'] >= REG_MIN)
        and (regression_data['mlpValue_reg_other'] >= REG_MIN) and (regression_data['kNeighboursValue_reg_other'] >= REG_MIN)
        and (regression_data['mlpValue_cla'] >= CLA_MIN) and (regression_data['kNeighboursValue_cla'] >= CLA_MIN)
        and (regression_data['mlpValue_cla_other'] >= CLA_MIN) and (regression_data['kNeighboursValue_cla_other'] >= CLA_MIN)
        ):
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
    
def is_algo_sell_classifier(regression_data, resticted=False):
    REG_MAX = 1.5
    CLA_MAX = 1
    if resticted:
        REG_MAX = 0.5
        CLA_MAX = 0
    if((regression_data['mlpValue_reg'] <= REG_MAX) and (regression_data['kNeighboursValue_reg'] <= REG_MAX)
        and (regression_data['mlpValue_reg_other'] <= REG_MAX) and (regression_data['kNeighboursValue_reg_other'] <= REG_MAX)
        and (regression_data['mlpValue_cla'] <= CLA_MAX) and (regression_data['kNeighboursValue_cla'] <= CLA_MAX)
        and (regression_data['mlpValue_cla_other'] <= CLA_MAX) and (regression_data['kNeighboursValue_cla_other'] <= CLA_MAX)
        ):
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

def high_tail_pct_pre1(regression_data):
    if(regression_data['high_pre1'] - regression_data['bar_high_pre1'] == 0):
        return 0
    else:
        return (((regression_data['high_pre1'] - regression_data['bar_high_pre1'])/regression_data['bar_high_pre1'])*100)
    
def low_tail_pct_pre1(regression_data):
    if((regression_data['bar_low_pre1'] - regression_data['low_pre1']) == 0):
        return 0
    else:
        return (((regression_data['bar_low_pre1'] - regression_data['low_pre1'])/regression_data['bar_low_pre1'])*100)

def high_tail_pct_pre2(regression_data):
    if(regression_data['high_pre2'] - regression_data['bar_high_pre2'] == 0):
        return 0
    else:
        return (((regression_data['high_pre2'] - regression_data['bar_high_pre2'])/regression_data['bar_high_pre2'])*100)
    
def low_tail_pct_pre2(regression_data):
    if((regression_data['bar_low_pre2'] - regression_data['low_pre2']) == 0):
        return 0
    else:
        return (((regression_data['bar_low_pre2'] - regression_data['low_pre2'])/regression_data['bar_low_pre2'])*100)

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

def is_ema6_sliding_up(regression_data):
    if((regression_data['EMA6'] > regression_data['EMA6_1daysBack'])
        and (regression_data['EMA6'] > regression_data['EMA6_2daysBack'])):
        return True
    else:
        return False
  
def is_ema14_sliding_up(regression_data):
    if((regression_data['EMA14'] > regression_data['EMA14_1daysBack'])
        and (regression_data['EMA14'] > regression_data['EMA14_2daysBack'])):
        return True
    else:
        return False 
    
def is_ema6_sliding_down(regression_data):
    if((regression_data['EMA6'] < regression_data['EMA6_1daysBack'])
        and (regression_data['EMA6'] < regression_data['EMA6_2daysBack'])):
        return True
    else:
        return False
  
def is_ema14_sliding_down(regression_data):
    if((regression_data['EMA14'] < regression_data['EMA14_1daysBack'])
        and (regression_data['EMA14'] < regression_data['EMA14_2daysBack'])):
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
#     if(regression_data['PCT_day_change'] > 0):
#         if(high_tail_pct(regression_data) < 0.1):
#             add_in_csv(regression_data, regressionResult, None, None, None, 'HighTailLessThan-0.1pc')
#         if(high_tail_pct(regression_data) < 0.3):
#             add_in_csv(regression_data, regressionResult, None, None, None, 'HighTailLessThan-0.3pc')
#             if(low_tail_pct(regression_data) < 0.1):
#                 add_in_csv(regression_data, regressionResult, None, None, None, 'LowTailLessThan-0.1pc')
#             if(low_tail_pct(regression_data) < 0.3):
#                 add_in_csv(regression_data, regressionResult, None, None, None, 'LowTailLessThan-0.3pc')
#     if(regression_data['PCT_day_change'] < 0):
#         if(low_tail_pct(regression_data) < 0.1):
#             add_in_csv(regression_data, regressionResult, None, None, None, 'LowTailLessThan-0.1pc')
#         if(low_tail_pct(regression_data) < 0.3):
#             add_in_csv(regression_data, regressionResult, None, None, None, 'LowTailLessThan-0.3pc')
#             if(high_tail_pct(regression_data) < 0.1):
#                 add_in_csv(regression_data, regressionResult, None, None, None, 'HighTailLessThan-0.1pc')
#             if(high_tail_pct(regression_data) < 0.3):
#                 add_in_csv(regression_data, regressionResult, None, None, None, 'HighTailLessThan-0.3pc')
#    high_tail_pct_filter(regression_data, regressionResult)
    return False

def tail_reversal_filter(regression_data, regressionResult):
#     if(3 > low_tail_pct(regression_data) > 2
#             and high_tail_pct(regression_data) < 1
#             and low_tail_pct_pre1(regression_data) < 1.5
#             #and regression_data['SMA9'] < 0
#             #and 'MayBuyCheckChart' in regression_data['filter1'] 
#             and -3 < regression_data['PCT_day_change_pre1'] < -1
#             and -3 < regression_data['PCT_day_change'] < -1
#             and (regression_data['PCT_day_change_pre2'] > 0
#                 or regression_data['PCT_day_change_pre3'] > 0
#                 )
#             ):
#             add_in_csv(regression_data, regressionResult, None, '(Check-chart-market2to3down)MayBuy-LastDayDown', None)
#     elif(3 > low_tail_pct(regression_data) > 1.8
#             and high_tail_pct(regression_data) < 1
#             and low_tail_pct_pre1(regression_data) < 1.5
#             #and regression_data['SMA9'] < 0
#             #and 'MayBuyCheckChart' in regression_data['filter1'] 
#             and -3 < regression_data['PCT_day_change_pre1'] < -1
#             and -3 < regression_data['PCT_day_change'] < -1
#             and regression_data['PCT_day_change_pre2'] < 0
#             and regression_data['PCT_day_change_pre3'] < 0
#             ):
#             add_in_csv(regression_data, regressionResult, None, 'MaySell-downTrend', None)
#     if(3 > high_tail_pct(regression_data) > 2
#             and low_tail_pct(regression_data) < 1
#             and high_tail_pct_pre1(regression_data) < 1.5
#             #and regression_data['SMA9'] > 0
#             #and 'MaySellCheckChart' in regression_data['filter1'] 
#             and 3 > regression_data['PCT_day_change_pre1'] > 1
#             and 3 > regression_data['PCT_day_change'] > 1
#             and (regression_data['PCT_day_change_pre2'] < 0
#                 or regression_data['PCT_day_change_pre3'] < 0
#                 )
#             ):
#             add_in_csv(regression_data, regressionResult, None, '(Check-chart-market2to3up)MaySell-LastDayUp', None)
#     elif(3 > high_tail_pct(regression_data) > 1.8
#             and low_tail_pct(regression_data) < 1
#             and high_tail_pct_pre1(regression_data) < 1.5
#             #and regression_data['SMA9'] > 0
#             #and 'MaySellCheckChart' in regression_data['filter1'] 
#             and 3 > regression_data['PCT_day_change_pre1'] > 1
#             and 3 > regression_data['PCT_day_change'] > 1
#             and regression_data['PCT_day_change_pre2'] > 0
#             and regression_data['PCT_day_change_pre3'] > 0
#             ):
#             add_in_csv(regression_data, regressionResult, None, 'MayBuy-upTrend', None)
    
    if(-5 < regression_data['PCT_day_change'] < -1.5
        and 4 > low_tail_pct(regression_data) >= 1.49 and high_tail_pct(regression_data) <= 0.8):
            add_in_csv(regression_data, regressionResult, None, None, '(MayBuy-CheckChart)-1', None)
    elif(-5 < regression_data['PCT_day_change'] < -1
        and 4 > low_tail_pct(regression_data) >= 1.49 and high_tail_pct(regression_data) <= 0.8):
            add_in_csv(regression_data, regressionResult, None, None, '(MayBuy-CheckChart)-1-Risky', None)
    elif(-6 < regression_data['PCT_day_change'] < -1.5
        and 3 > low_tail_pct(regression_data) >= 0.99 and high_tail_pct(regression_data) <= 0.6):
            add_in_csv(regression_data, regressionResult, None, None, '(MayBuy-CheckChart)-2', None)
    elif(-6 < regression_data['PCT_day_change'] < -1
        and 3 > low_tail_pct(regression_data) >= 0.99 and high_tail_pct(regression_data) <= 0.6):
            add_in_csv(regression_data, regressionResult, None, None, '(MayBuy-CheckChart)-2-Risky', None)
            
    if(1.5 < regression_data['PCT_day_change'] < 5
        and 4 > high_tail_pct(regression_data) >= 1.49 and low_tail_pct(regression_data) <= 0.8):
            add_in_csv(regression_data, regressionResult, None, None, '(MaySell-CheckChart)-1', None) 
    elif(1 < regression_data['PCT_day_change'] < 5
        and 4 > high_tail_pct(regression_data) >= 1.49 and low_tail_pct(regression_data) <= 0.8):
            add_in_csv(regression_data, regressionResult, None, None, '(MaySell-CheckChart)-1-Risky', None)   
    elif(1.5 < regression_data['PCT_day_change'] < 6
        and 3 > high_tail_pct(regression_data) >= 0.99 and low_tail_pct(regression_data) <= 0.6):
            add_in_csv(regression_data, regressionResult, None, None, '(MaySell-CheckChart)-2', None)
    elif(1 < regression_data['PCT_day_change'] < 6
        and 3 > high_tail_pct(regression_data) >= 0.99 and low_tail_pct(regression_data) <= 0.6):
            add_in_csv(regression_data, regressionResult, None, None, '(MaySell-CheckChart)-2-Risky', None)
    
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
        
    if(('MayBuy-CheckChart' in regression_data['filter1']) 
        or ('MayBuyCheckChart' in regression_data['filter1'])
        ):
        if(
            (low_tail_pct(regression_data) > 1.8)
            and low_tail_pct(regression_data) < abs(regression_data['PCT_change'])
            ):
            add_in_csv(regression_data, regressionResult, None, None, 'Strong', None)
    if(('MaySell-CheckChart' in regression_data['filter1']) 
        or ('MaySellCheckChart' in regression_data['filter1'])
        ):
        if(
            (high_tail_pct(regression_data) > 1.8)
            and high_tail_pct(regression_data) < abs(regression_data['PCT_change'])
            ):
            add_in_csv(regression_data, regressionResult, None, None, 'Strong', None)

def filterMA(regression_data, regressionResult):
    ws = None
    if(2 < regression_data['PCT_day_change'] < 4
       and 0 < regression_data['PCT_change'] < 4.5
       and regression_data['forecast_day_PCT_change'] > 0
       and regression_data['PCT_day_change_pre1'] < 0
       #and regression_data['PCT_day_change_pre2'] < 0.75
       and high_tail_pct(regression_data) < 1
       and low_tail_pct(regression_data) < 1
       #and low_tail_pct_pre1(regression_data) < 1.5
       ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, "UP")
    elif(2 < regression_data['PCT_day_change'] < 4
       and 0 < regression_data['PCT_change'] < 4.5
       and regression_data['forecast_day_PCT_change'] > 0
       and regression_data['forecast_day_PCT2_change'] > 0
       and regression_data['PCT_day_change_pre1'] < 0.75
       and regression_data['PCT_day_change_pre2'] < 0.5
       and 0.75 > regression_data['PCT_day_change_pre3'] > 0
       and high_tail_pct(regression_data) < 1
       and low_tail_pct(regression_data) < 1
       and low_tail_pct_pre1(regression_data) < 1
       ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, "UP-1")
    elif(2.5 < regression_data['PCT_day_change'] < 4
       and 0 < regression_data['PCT_change'] < 4.5
       and regression_data['forecast_day_PCT_change'] > 0
       and regression_data['forecast_day_PCT2_change'] > 0
       and regression_data['PCT_day_change_pre1'] < 0.75
       and regression_data['PCT_day_change_pre2'] < 0.5
       and regression_data['PCT_day_change_pre3'] < 0
       and high_tail_pct(regression_data) < 1
       and low_tail_pct(regression_data) < 1
       #and low_tail_pct_pre1(regression_data) < 1
       ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, "UP-2")
    elif(-4 < regression_data['PCT_day_change'] < -2
       and -4.5 < regression_data['PCT_change'] < 0
       and regression_data['forecast_day_PCT_change'] < 0
       and regression_data['PCT_day_change_pre1'] > 0
       #and regression_data['PCT_day_change_pre2'] > -0.75
       and low_tail_pct(regression_data) < 1
       and high_tail_pct(regression_data) < 1
       #and high_tail_pct_pre1(regression_data) < 1.5
       ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, "DOWN")
    elif(-4 < regression_data['PCT_day_change'] < -2
       and -4.5 < regression_data['PCT_change'] < 0
       and regression_data['forecast_day_PCT_change'] < 0
       and regression_data['forecast_day_PCT2_change'] < 0
       and regression_data['PCT_day_change_pre1'] > -0.75
       and regression_data['PCT_day_change_pre2'] > -0.5
       and -0.75 < regression_data['PCT_day_change_pre3'] < 0
       and low_tail_pct(regression_data) < 1
       and high_tail_pct(regression_data) < 1
       and high_tail_pct_pre1(regression_data) < 1
       ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, "DOWN-1")
    elif(-4 < regression_data['PCT_day_change'] < -2
       and -4.5 < regression_data['PCT_change'] < 0
       and regression_data['forecast_day_PCT_change'] < 0
       and regression_data['forecast_day_PCT2_change'] < 0
       and regression_data['PCT_day_change_pre1'] > -0.75
       and regression_data['PCT_day_change_pre2'] > -0.5
       and regression_data['PCT_day_change_pre3'] > 0
       and low_tail_pct(regression_data) < 1
       and high_tail_pct(regression_data) < 1
       #and high_tail_pct_pre1(regression_data) < 1
       ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, "DOWN-2")
    
    if(regression_data['forecast_day_PCT_change'] > 0
        and regression_data['PCT_day_change'] > 2.5
        and -1.5 < regression_data['PCT_day_change_pre1'] < 0
        and -1.5 < regression_data['PCT_day_change_pre2'] < 0
        and -1.5 < regression_data['PCT_day_change_pre3'] < 0 
        and (regression_data['yearHighChange'] < -10 or regression_data['PCT_day_change_pre3'] < 0)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(check-chart)consolidationBreakout-0')
    elif(regression_data['forecast_day_PCT_change'] > 0
        and regression_data['PCT_day_change'] > 2.5
        and -1.5 < regression_data['PCT_day_change_pre1'] < 0
        and -1.5 < regression_data['PCT_day_change_pre2'] < 0
        and -1.5 < regression_data['PCT_day_change_pre3'] < 1.5 
        and (regression_data['yearHighChange'] < -10 or regression_data['PCT_day_change_pre3'] < 0)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(check-chart)consolidationBreakout-1')
    elif(regression_data['forecast_day_PCT_change'] > 0
        and regression_data['PCT_day_change'] > 2.5
        and -1.5 < regression_data['PCT_day_change_pre1'] < 0
        and -1.5 < regression_data['PCT_day_change_pre2'] < 1.5
        and -1.5 < regression_data['PCT_day_change_pre3'] < 1.5 
        and regression_data['yearHighChange'] < -10
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(check-chart)consolidationBreakout-Risky')
    elif(regression_data['forecast_day_PCT_change'] > 0
        and regression_data['PCT_day_change'] > 2.5
        and regression_data['PCT_day_change_pre1'] > 2.5
        and -1.5 < regression_data['PCT_day_change_pre2'] < 0
        and -1.5 < regression_data['PCT_day_change_pre3'] < 0
        and -1.5 < regression_data['PCT_day_change_pre4'] < 0
        and regression_data['yearHighChange'] < -10
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(check-chart)consolidationBreakoutLastDay-Risky')
    
    
    if(regression_data['forecast_day_PCT_change'] < 0
        and regression_data['PCT_day_change'] < -2.5
        and 0 < regression_data['PCT_day_change_pre1'] < 1.5
        and 0 < regression_data['PCT_day_change_pre2'] < 1.5
        and 0 < regression_data['PCT_day_change_pre3'] < 1.5 
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(check-chart)consolidationBreakdown-0')
    elif(regression_data['forecast_day_PCT_change'] < 0
        and regression_data['PCT_day_change'] < -2.5
        and 0 < regression_data['PCT_day_change_pre1'] < 1.5
        and 0 < regression_data['PCT_day_change_pre2'] < 1.5
        and -1.5 < regression_data['PCT_day_change_pre3'] < 1.5 
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(check-chart)consolidationBreakdown-1')
    elif(regression_data['forecast_day_PCT_change'] < 0
        and regression_data['PCT_day_change'] < -2.5
        and 0 < regression_data['PCT_day_change_pre1'] < 1.5
        and -1.5 < regression_data['PCT_day_change_pre2'] < 1.5
        and -1.5 < regression_data['PCT_day_change_pre3'] < 1.5 
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(check-chart)consolidationBreakdown-Risky')
    elif(regression_data['forecast_day_PCT_change'] < 0
        and regression_data['PCT_day_change'] < -2.5
        and regression_data['PCT_day_change_pre1'] < -2.5
        and 0 < regression_data['PCT_day_change_pre2'] < 1.5
        and 0 < regression_data['PCT_day_change_pre3'] < 1.5
        and 0 < regression_data['PCT_day_change_pre4'] < 1.5 
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(check-chart)consolidationBreakdownLastDay-Risky')
    
    
    ema_diff = regression_data['ema6-14']
    ema_diff_pre1 = regression_data['ema6-14_pre1']
    ema_diff_pre2 = regression_data['ema6-14_pre2']
    
    if(ema_diff > 0
       and ema_diff_pre1 < 0
       and ema_diff_pre2 < 0
       and ema_diff_pre2 < ema_diff_pre1
       ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, '$$(Confirmed)$$:EMA6>EMA14')
        
    if(ema_diff < 0
       and ema_diff_pre1 > 0
       and ema_diff_pre2 > 0
       and ema_diff_pre2 > ema_diff_pre1
       ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, '$$(Confirmed)$$:EMA6<EMA14')
        
        
    if(((regression_data['EMA6'] < regression_data['EMA6_1daysBack'] < regression_data['EMA6_2daysBack'])
       or (regression_data['EMA14'] < regression_data['EMA14_1daysBack'] < regression_data['EMA14_2daysBack']))
       and ema_diff < ema_diff_pre1 < ema_diff_pre2
       and 0 < ema_diff < 1 and ema_diff_pre2 > 2*ema_diff
       and (regression_data['PCT_day_change'] > 0
             or regression_data['PCT_day_change_pre1'] > 0
             or regression_data['PCT_day_change_pre2'] > 0
             or regression_data['PCT_day_change_pre3'] > 0
            )
       ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, '$$(May)$$:EMA6-MT-May-LT-EMA14')
        
    if(((regression_data['EMA6'] > regression_data['EMA6_1daysBack'] > regression_data['EMA6_2daysBack'])
       or (regression_data['EMA14'] > regression_data['EMA14_1daysBack'] > regression_data['EMA14_2daysBack']))
       and ema_diff_pre2 < ema_diff_pre1 < ema_diff
       and -1 < ema_diff < 0 and ema_diff_pre2 < 2*ema_diff
       and (regression_data['PCT_day_change'] < 0
             or regression_data['PCT_day_change_pre1'] < 0
             or regression_data['PCT_day_change_pre2'] < 0
             or regression_data['PCT_day_change_pre3'] < 0
            )
       ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, '$$(May)$$:EMA6-LT-May-MT-EMA14')
            
    if((regression_data['SMA200'] < regression_data['SMA100'] < regression_data['SMA50'] < regression_data['SMA25']
        or(
            regression_data['SMA200'] < 0
            and regression_data['SMA100'] < 0
            and regression_data['SMA50'] < 0
            and regression_data['SMA50'] < regression_data['SMA25']
        )
        )
       and regression_data['SMA100'] < -5
       and (regression_data['SMA100'] < -10 or regression_data['SMA200'] < -10)
       and (regression_data['SMA9'] > -1 and regression_data['SMA4'] > -1)
       and (
            (regression_data['SMA9'] > 1 or regression_data['SMA4'] > 1)
            or (regression_data['SMA9'] > 0 and regression_data['SMA4'] > 0)
            )
       #and (regression_data['SMA9'] > 0 and regression_data['SMA4'] > 0)
    ):
        if(is_ema14_sliding_up(regression_data)):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, '$$(Study)$$:RisingMA-Confirm')
        elif((regression_data['SMA9'] > 1 or regression_data['SMA4'] > 1)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, '$$(Study)$$:RisingMA')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, '$$(Study)$$:RisingMA-Risky')
        if(-5 < regression_data['SMA25'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, '##LONGTERM:NearSMA25')
        elif(0 < regression_data['SMA25'] < 5):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, '##LONGTERM:CrossoverSMA25')
        elif(-5 < regression_data['SMA50'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, '##MEDIUMTERM:NearSMA50')
        elif(0 < regression_data['SMA50'] < 5):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, '##MEDIUMTERM:CrossoverSMA50')
        elif(-5 < regression_data['SMA100'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, '##SHORTTERM:NearSMA100')
        elif(0 < regression_data['SMA100'] < 5):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, '##SHORTTERM:CrossoverSMA100')
        
    elif(regression_data['SMA200'] < regression_data['SMA100'] < regression_data['SMA50'] < regression_data['SMA25'] < 0
         and regression_data['SMA9'] < 0
         and regression_data['SMA4'] < 0
    ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, '$$(Study)$$:AllNegativeMA')
    elif(regression_data['SMA200'] > 0
         and regression_data['SMA100'] > 0 
         and regression_data['SMA50'] > 0
         and (regression_data['SMA9'] < 1 and regression_data['SMA4'] < 1)
         and (regression_data['SMA9'] < -1 or regression_data['SMA4'] < -1
              or (regression_data['SMA9'] < 0 or regression_data['SMA4'] < 0))
         ):
        if(is_ema14_sliding_down(regression_data)):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, '$$(Study)$$:DowningMA-Confirm')
        elif((regression_data['SMA9'] < -1 or regression_data['SMA4'] < -1)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, '$$(Study)$$:DowningMA')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, '$$(Study)$$:DowningMA-Risky')
#     elif(regression_data['SMA200'] > 0 
#          and regression_data['SMA100'] > 0
#          and regression_data['SMA50'] > 0
#          and regression_data['SMA25'] > 0
#          and regression_data['SMA9'] > 0
#          and regression_data['SMA4'] > 0
#          ):
#         add_in_csv(regression_data, regressionResult, ws, None, None, None, None, '$$(Study)$$:AllPositiveMA')

def base_line(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    if((0 < regression_data['year2HighChange'] < 5) 
        and (regression_data['year2LowChange'] > 40)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'BreakHighYear2')
        if(regression_data['year2High'] != regression_data['high_year2']
            #and regression_data['monthHighChange'] == regression_data['weekHighChange']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(Confirm)')
    elif((0 < regression_data['yearHighChange'] < 5) 
        and (regression_data['yearLowChange'] > 30)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'BreakHighYear')
        if(regression_data['yearHigh'] != regression_data['high_year']
            #and regression_data['monthHighChange'] == regression_data['weekHighChange']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(Confirm)')
    elif((0 < regression_data['month6HighChange'] < 5)
        and (regression_data['month6LowChange'] > 20)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'BreakHighMonth6')
        if(regression_data['month6High'] != regression_data['high_month6']
            #and regression_data['monthHighChange'] == regression_data['weekHighChange']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(Confirm)')
    elif((0 < regression_data['month3HighChange'] < 5) 
        and (regression_data['month3LowChange'] > 15)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'BreakHighMonth3')
        if(regression_data['month3High'] != regression_data['high_month3']
            ##and regression_data['monthHighChange'] == regression_data['weekHighChange']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(Confirm)')
    elif((0 < regression_data['monthHighChange'] < 5) 
        and (regression_data['monthLowChange'] > 10)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'BreakHighMonth')
    
    if((-7.5 < regression_data['year2HighChange'] < 0) 
        and (regression_data['year2LowChange'] > 40)
        ):
        if(regression_data['weekHigh'] >= regression_data['year2High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'ReversalHighYear2')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'NearHighYear2')
        if(regression_data['year2High'] != regression_data['high_year2']
            ##and regression_data['monthHighChange'] == regression_data['weekHighChange']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(Confirm)')
    elif((-7.5 < regression_data['yearHighChange'] < 0) 
        and (regression_data['yearLowChange'] > 30)
        ):
        if(regression_data['weekHigh'] >= regression_data['yearHigh']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'ReversalHighYear')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'NearHighYear')
        if(regression_data['yearHigh'] != regression_data['high_year']
            ##and regression_data['monthHighChange'] == regression_data['weekHighChange']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(Confirm)')
    elif((-7.5 < regression_data['month6HighChange'] < 0) 
        and (regression_data['month6LowChange'] > 20)
        ):
        if(regression_data['weekHigh'] >= regression_data['month6High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'ReversalHighMonth6')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'NearHighMonth6')
        if(regression_data['month6High'] != regression_data['high_month6']
            #and regression_data['monthHighChange'] == regression_data['weekHighChange']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(Confirm)')
    elif((-7.5 < regression_data['month3HighChange'] < 0) 
        and (regression_data['month3LowChange'] > 15)
        ):
        if(regression_data['weekHigh'] >= regression_data['month3High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'ReversalHighMonth3')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'NearHighMonth3')
        if(regression_data['month3High'] != regression_data['high_month3']
            #and regression_data['monthHighChange'] == regression_data['weekHighChange']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(Confirm)')
    elif((-7.5 < regression_data['monthHighChange'] < 0) 
        and (regression_data['monthLowChange'] > 10)
        ):
        if(regression_data['weekHigh'] >= regression_data['month3High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None)
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'NearHighMonth')
        
    if((-5 < regression_data['year2LowChange'] < 0 ) 
        and (regression_data['year2HighChange'] < -40)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'BreakLowYear2')
        if(regression_data['year2Low'] != regression_data['low_year2']
            #and regression_data['monthLowChange'] == regression_data['weekLowChange']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(Confirm)')
    elif((-5 < regression_data['yearLowChange'] < 0) 
        and (regression_data['year2LowChange'] > 20)
        and (regression_data['yearHighChange'] < -30)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'BreakLowYear')
        if(regression_data['yearLow'] != regression_data['low_year']
            #and regression_data['monthLowChange'] == regression_data['weekLowChange']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(Confirm)')
    elif((-5 < regression_data['month6LowChange'] < 0)
        and (regression_data['yearLowChange'] > 20)
        and (regression_data['month6HighChange'] < -20)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'BreakLowMonth6')
        if(regression_data['month6Low'] != regression_data['low_month6']
            #and regression_data['monthLowChange'] == regression_data['weekLowChange']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(Confirm)')
    elif((-5 < regression_data['month3LowChange'] < 0)
        and (regression_data['month6LowChange'] > 10)
        and (regression_data['yearLowChange'] > 20)
        and (regression_data['month3HighChange'] < -15)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'BreakLowMonth3')
        if(regression_data['month3Low'] != regression_data['low_month3']
            #and regression_data['monthLowChange'] == regression_data['weekLowChange']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(Confirm)')
    elif((-5 < regression_data['monthLowChange'] < 0)
        and (regression_data['month3LowChange'] > 10)
        and (regression_data['yearLowChange'] > 20)
        and (regression_data['monthHighChange'] < -10)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'BreakLowMonth')
    
    if((0 < regression_data['year2LowChange'] < 7.5) 
       and (regression_data['year2HighChange'] < -40)
       ):
        if(regression_data['weekLow'] < regression_data['year2Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'ReversalLowYear2')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'NearLowYear2')
        if(regression_data['year2Low'] != regression_data['low_year2']
            #and regression_data['monthLowChange'] == regression_data['weekLowChange']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(Confirm)')
    elif((0 < regression_data['yearLowChange'] < 7.5)
        and (regression_data['year2LowChange'] > 7.5)
        and (regression_data['yearHighChange'] < -30)
        ):
        if(regression_data['weekLow'] < regression_data['yearLow']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'ReversalLowYear')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'NearLowYear')
        if(regression_data['yearLow'] != regression_data['low_year']
            #and regression_data['monthLowChange'] == regression_data['weekLowChange']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(Confirm)')
    elif((0 < regression_data['month6LowChange'] < 7.5)
        and (regression_data['yearLowChange'] > 7.5)
        and (regression_data['month6HighChange'] < -20)
        ):
        if(regression_data['weekLow'] < regression_data['month6Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'ReversalLowMonth6')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'NearLowMonth6')
        if(regression_data['month6Low'] != regression_data['low_month6']
            #and regression_data['monthLowChange'] == regression_data['weekLowChange']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(Confirm)')
    elif((0 < regression_data['month3LowChange'] < 7.5)
        and (regression_data['month6LowChange'] > 7.5)
        and (regression_data['month3HighChange'] < -15)
        ):
        if(regression_data['weekLow'] < regression_data['month3Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'ReversalLowMonth3')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'NearLowMonth3')
        if(regression_data['month3Low'] != regression_data['low_month3']
            #and regression_data['monthLowChange'] == regression_data['weekLowChange']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(Confirm)')
    elif((0 < regression_data['monthLowChange'] < 7.5)
        and (regression_data['month3LowChange'] > 7.5)
        and (regression_data['monthHighChange'] < -10)
        ):
        if(regression_data['weekLow'] < regression_data['month3Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None)
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'NearLowMonth')                 
    elif(regression_data['year2LowChange'] < 0):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, '**LowYear2')
    elif(regression_data['yearLowChange'] < 0):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, '**LowYear')
    elif(regression_data['month6LowChange'] < 0):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, '**LowMonth6')
    elif(regression_data['month3LowChange'] < 0):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, '**LowMonth3')
    elif(regression_data['year2HighChange'] > 5):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, '**HighYear2')
    elif(regression_data['yearHighChange'] > 5):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, '**HighYear')
    elif(regression_data['month6HighChange'] > 5):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, '**HighMonth6')
    elif(regression_data['month3HighChange'] > 5):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, '**HighMonth3')
    
    if(-1 < regression_data['monthHighChange'] < 3
        and regression_data['month3HighChange'] < -5
        and regression_data['PCT_day_change'] > 1
        and (regression_data['PCT_day_change_pre2'] < 0.5
             or regression_data['PCT_day_change_pre3'] < 0.5
            )
        ):
        if(abs(regression_data['year2HighChange']) > abs(regression_data['year2LowChange'])
            and regression_data['year2LowChange'] < 25  
            and regression_data['yearLowChange'] < 15
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '(check-chart):buyMonthHighBreak-atNearYearLow')
        elif(abs(regression_data['year2HighChange']) < abs(regression_data['year2LowChange'])
            and regression_data['high'] > regression_data['high_pre1']
            and regression_data['bar_high'] > regression_data['bar_high_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '(check-chart):buyMonthHighBreak-checkATRSellBreak')
        elif(regression_data['high'] > regression_data['high_pre1']
            and regression_data['bar_high'] > regression_data['bar_high_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '(check-chart):buyMonthHighBreak-checkATRSellBreak-Risky') 
    
    if(-3 < regression_data['monthLowChange'] < 1
        and regression_data['month3LowChange'] > 5
        and regression_data['PCT_day_change'] < -1
        and (regression_data['PCT_day_change_pre2'] > -0.5
             or regression_data['PCT_day_change_pre3'] > -0.5
            )
        ):
        if(abs(regression_data['year2HighChange']) < abs(regression_data['year2LowChange'])
            and regression_data['year2HighChange'] > -25  
            and regression_data['yearHighChange'] > -15  
            and (regression_data['PCT_day_change_pre2'] > 0
                 or regression_data['PCT_day_change_pre1'] > 0
                )                                      
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '(check-chart):sellMonthLowBreak-atNearYearHigh')
        elif(abs(regression_data['year2HighChange']) > abs(regression_data['year2LowChange'])
            and regression_data['low'] < regression_data['low_pre1']
            and regression_data['bar_low'] < regression_data['bar_low_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '(check-chart):sellMonthLowBreak-checkATRBuyBreak')
        elif(regression_data['low'] < regression_data['low_pre1']
            and regression_data['bar_low'] < regression_data['bar_low_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '(check-chart):sellMonthLowBreak-checkATRBuyBreak-Risky')   
                   
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
    regression_data['filter5'] = " "
    regression_data['filter6'] = " "
    regression_data['filter_avg'] = 0
    regression_data['filter_count'] = 0
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

def buy_pattern_without_mlalgo(regression_data, regressionResult):
    if(regression_data['PCT_day_change'] < 3.5
        and regression_data['year2LowChange'] > 5):
        if(regression_data['buyIndia_avg'] > 1.8):
            add_in_csv(regression_data, regressionResult, None, 'mayBuyFromBuyPattern-GT1.8')
        if(regression_data['buyIndia_avg'] > 0.9 and regression_data['buyIndia_count'] > 1
            and (regression_data['SMA9'] > 0 or regression_data['SMA4'] > 1.5)
            ):
            if(regression_data['SMA9'] > 0):
                add_in_csv(regression_data, regressionResult, None, '(SMA9GT0)')
            elif(regression_data['SMA4'] > 1.5):
                add_in_csv(regression_data, regressionResult, None, '(SMA4GT(1.5))')
            if(regression_data['yearLowChange'] > 10 and regression_data['buyIndia_count'] > 1):
                if(regression_data['buyIndia_avg'] > 1.5):
                    add_in_csv(regression_data, regressionResult, None, 'buyPattern-GT1.5-SMAGT0')
                elif(regression_data['buyIndia_avg'] > 0.9
                    ):
                    add_in_csv(regression_data, regressionResult, None, 'buyPattern-Risky-GT0.9-SMAGT0')
                #add_in_csv(regression_data, regressionResult, None, 'buyPatterns-1-Risky')

    if(regression_data['PCT_day_change'] < 3.5
        and regression_data['year2LowChange'] > 5
        and regression_data['year2HighChange'] < -5):
        if(regression_data['buyIndia_avg'] < -1.8):
            add_in_csv(regression_data, regressionResult, None, 'maySellFromBuyPattern-LT-1.8')
        if(regression_data['buyIndia_avg'] < -0.9 and regression_data['buyIndia_count'] > 1
            and (regression_data['SMA9'] < 0 or regression_data['SMA4'] < -1.5)
            ):
            if(regression_data['SMA9'] < 0):
                add_in_csv(regression_data, regressionResult, None, '(SMA9LT0)')
            elif(regression_data['SMA4'] < -1.5):
                add_in_csv(regression_data, regressionResult, None, '(SMA4LT(-1.5))')
            if(regression_data['yearLowChange'] > 10 and regression_data['buyIndia_count'] > 1):
                if(regression_data['buyIndia_avg'] < -1.5):
                    add_in_csv(regression_data, regressionResult, None, 'sellPattern-LT-1.5-SMALT0')
                elif(regression_data['buyIndia_avg'] < -0.9
                    ):
                    add_in_csv(regression_data, regressionResult, None, 'sellPattern-Risky-LT-0.9-SMALT0')
            #add_in_csv(regression_data, regressionResult, None, 'sellPatterns-1-Risky')
#     buyPatternsDict=scrip_patterns_to_dict('../../data-import/nselist/all-buy-filter-by-PCT-Change.csv')
#     if regression_data['buyIndia'] != '' and regression_data['buyIndia'] in buyPatternsDict:
#         if (abs(float(buyPatternsDict[regression_data['buyIndia']]['avg'])) >= .1 and float(buyPatternsDict[regression_data['buyIndia']]['count']) >= 2):
#             if(-0.5 < regression_data['PCT_day_change'] < 3 and float(buyPatternsDict[regression_data['buyIndia']]['avg']) > 1):
#                 avg = buyPatternsDict[regression_data['buyIndia']]['avg']
#                 count = buyPatternsDict[regression_data['buyIndia']]['count']
#                 #add_in_csv_hist_pattern(regression_data, regressionResult, ws2, 'wml_buy', avg, count)
#             elif(-3 < regression_data['PCT_day_change'] < 0.5 and float(buyPatternsDict[regression_data['buyIndia']]['avg']) < -1):
#                 avg = buyPatternsDict[regression_data['buyIndia']]['avg']
#                 count = buyPatternsDict[regression_data['buyIndia']]['count']
#                 #add_in_csv_hist_pattern(regression_data, regressionResult, ws, 'wml_buy', avg, count)

def buy_pattern_from_history(regression_data, ws):
    buyPatternsDict=scrip_patterns_to_dict('../../data-import/nselist/patterns-buy.csv')
    buyIndiaAvg = 0
    regression_data['buyIndia_avg'] = 0
    regression_data['buyIndia_count'] = 0
    regression_data['sellIndia_avg'] = 0
    regression_data['sellIndia_count'] = 0
    regression_data['filter_avg'] = 0
    regression_data['filter_count'] = 0
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
                       #add_in_csv_hist_pattern(regression_data, regressionResult, ws, 'buyPattern2', avg, count)
                    elif(float(buyPatternsDict[regression_data['buyIndia']]['avg']) > 0.5 
                       or (float(buyPatternsDict[regression_data['buyIndia']]['avg']) > 0.3 and (ten_days_less_than_minus_ten(regression_data) or regression_data['yearHighChange'] < -40))):
                        if(regression_data['forecast_day_PCT10_change'] < 0 and regression_data['forecast_day_PCT_change'] >= 0):
                            flag = True
                            #add_in_csv_hist_pattern(regression_data, regressionResult, ws, 'buyPattern2', avg, count)
                        elif(regression_data['forecast_day_PCT10_change'] > 0):    
                            flag = True
                            #add_in_csv_hist_pattern(regression_data, regressionResult, ws, 'buyPattern2', avg, count)     
    return buyIndiaAvg, flag

def buy_all_rule(regression_data, regressionResult, buyIndiaAvg, ws):
    if(is_algo_buy(regression_data)
        and buyIndiaAvg >= -.70
        and ((last_7_day_all_up(regression_data) == False) or (regression_data['forecast_day_PCT10_change'] < 10))
        and (MARKET_IN_UPTREND or (last_4_day_all_up(regression_data) == False)) #Uncomment0 If very less data
        and breakout_or_no_consolidation(regression_data) == True
        and '$$(Confirmed)$$:EMA6>EMA14' not in regression_data['filter4']
        and regression_data['close'] > 50
        and high_tail_pct(regression_data) < 1
        and low_tail_pct(regression_data) > 1.2
        and regression_data['low'] > regression_data['low_pre1']
        ):
        if(regression_data['PCT_day_change'] < -0.75 and regression_data['PCT_change'] < 0
            and regression_data['month3HighChange'] < -15  
            ):
            add_in_csv(regression_data, regressionResult, None, 'ML:buy-0')
    elif(is_algo_sell(regression_data)):
        if(2 < regression_data['PCT_day_change'] < 5
            and  2 < regression_data['PCT_change'] < 5
            and high_tail_pct(regression_data) > 1.5
            and low_tail_pct(regression_data) < 1
            ):
            add_in_csv(regression_data, regressionResult, None, 'ML:sell-1')
    
    if(is_algo_buy(regression_data, True)
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
        and '$$(Confirmed)$$:EMA6>EMA14' not in regression_data['filter4']
        and regression_data['close'] > 50
        ):
        add_in_csv(regression_data, regressionResult, ws, None)
        return True
    return False

def buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvg, ws):
    if(is_algo_buy_classifier(regression_data, True)
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
        and '$$(Confirmed)$$:EMA6>EMA14' not in regression_data['filter4']
        and regression_data['close'] > 50
        ):
        add_in_csv(regression_data, regressionResult, ws, None)
        return True
    return False

def buy_all_common(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, True)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, True)
    mlpValue_cla, kNeighboursValue_cla = get_reg_or_cla(regression_data, False)
    mlpValue_other_cla, kNeighboursValue_other_cla = get_reg_or_cla_other(regression_data, False)
    
    if((regression_data['PCT_day_change'] < 3)
       and ((regression_data['PCT_day_change'] > 1
           and 6 > mlpValue_other >= 2
           and 6 > kNeighboursValue_other >= 2
           and 6 > mlpValue_other_cla >= 2
           and 6 > kNeighboursValue_other_cla >= 2
           and 6 > mlpValue_cla >= 0
           and 6 > kNeighboursValue_cla >= 0)
       )):
        add_in_csv(regression_data, regressionResult, ws, '##Common:(Test)HighIndicators-0')
    elif((regression_data['PCT_day_change'] < 3)
       and ((regression_data['PCT_day_change'] > 2
           and 6 > mlpValue_other >= 1 
           and 6 > kNeighboursValue_other >= 1
           and 6 > mlpValue_other_cla >= 2
           and 6 > kNeighboursValue_other_cla >= 2
           and 6 > mlpValue_cla >= 2
           and 6 > kNeighboursValue_cla >= 2)
       )):
        add_in_csv(regression_data, regressionResult, ws, '##Common:(Test)HighIndicators-1')
    
#     if(is_algo_buy(regression_data)):
#         if('P@' not in regression_data['sellIndia']):
#             add_in_csv(regression_data, regressionResult, ws, '##Common(Test):buyDayReversalCandidate-0')
#         else:
#             add_in_csv(regression_data, regressionResult, ws, '##Common(Test):buyDayReversalCandidate-1')
    
            
    if(is_algo_buy(regression_data)
        and (2 < regression_data['PCT_day_change'] < 4) and (1 < regression_data['PCT_change'] < 4)
        and ((regression_data['PCT_day_change_pre1'] < 0 and regression_data['forecast_day_PCT_change'] > 0)
             )
        and regression_data['forecast_day_PCT2_change'] > 0
        and regression_data['forecast_day_PCT3_change'] > 0
        and regression_data['forecast_day_PCT4_change'] > 1
        #and regression_data['forecast_day_PCT10_change'] < 15
        and regression_data['month3HighChange'] < -10
        and regression_data['month3LowChange'] > 10
        ):    
        if(regression_data['SMA9'] > 1):
            add_in_csv(regression_data, regressionResult, ws, '##Common:buyNotM3HighLow-0(SMA9GT1)')
        elif(regression_data['SMA25'] > 0):
            add_in_csv(regression_data, regressionResult, ws, '##(Test):buyNotM3HighLow-0(SMA25GT0)')  
        else:
            add_in_csv(regression_data, regressionResult, ws, None)
            
    if(is_algo_buy(regression_data)
        and (2 < regression_data['PCT_day_change'] < 4) and (1 < regression_data['PCT_change'] < 4)
        and ((regression_data['PCT_day_change_pre1'] < 0 and regression_data['forecast_day_PCT_change'] > 0)
             or regression_data['PCT_day_change_pre2'] < 0
            )
        and regression_data['forecast_day_PCT2_change'] > 0
        and regression_data['forecast_day_PCT3_change'] > 0
        #and regression_data['forecast_day_PCT10_change'] < 15
        and regression_data['month3HighChange'] < -3
        and regression_data['month3LowChange'] > 3
        and regression_data['yearHighChange'] < -10
        and regression_data['yearLowChange'] > 10
        and abs_month3High_less_than_month3Low(regression_data)
        ):    
        if(regression_data['SMA9'] > 1):
            add_in_csv(regression_data, regressionResult, ws, '##Common:buyNotM3HighLow-1(SMA9GT1)')
        elif(regression_data['SMA25'] > 0):
            add_in_csv(regression_data, regressionResult, ws, '##(Test):buyNotM3HighLow-1(SMA25GT0)')  
        else:
            add_in_csv(regression_data, regressionResult, ws, None)
            
    if(ten_days_less_than_minus_ten(regression_data)
        and regression_data['forecast_day_PCT2_change'] < 0
        and regression_data['forecast_day_PCT3_change'] < 0
        and regression_data['forecast_day_PCT5_change'] < 0
        and regression_data['forecast_day_PCT7_change'] < 0
        and regression_data['forecast_day_PCT7_change'] < 0
        and regression_data['PCT_day_change'] > 2
        and regression_data['PCT_change'] > 2
        and regression_data['PCT_day_change_pre2'] < 0
        and regression_data['PCT_day_change_pre3'] < 0
        ):
        add_in_csv(regression_data, regressionResult, ws, '##Common:Breakout-tenDaysLessThanMinusTen')
            
    return False

def buy_other_indicator(regression_data, regressionResult, reg, ws):
    tail_pct_filter(regression_data, regressionResult)
    base_line(regression_data, regressionResult, reg, ws)
    filterMA(regression_data, regressionResult)
    tail_reversal_filter(regression_data, regressionResult)
    if(regression_data['close'] > 50
        ):
        buy_tail_reversal_filter(regression_data, regressionResult, reg, ws)
        buy_year_high(regression_data, regressionResult, reg, ws)
        buy_year_low(regression_data, regressionResult, reg, ws, ws)
        buy_down_trend(regression_data, regressionResult, reg, ws)
        buy_final(regression_data, regressionResult, reg, ws, ws)
        buy_high_indicators(regression_data, regressionResult, reg, ws)
        buy_pattern(regression_data, regressionResult, reg, ws, ws)
        buy_morning_star_buy(regression_data, regressionResult, reg, ws)
        buy_evening_star_sell(regression_data, regressionResult, reg, ws)
        buy_oi_negative(regression_data, regressionResult, reg, ws)
        buy_day_low(regression_data, regressionResult, reg, ws)
        buy_vol_contract(regression_data, regressionResult, reg, ws)
        buy_vol_contract_contrarian(regression_data, regressionResult, reg, ws)
        buy_trend_reversal(regression_data, regressionResult, reg, ws)
        buy_trend_break(regression_data, regressionResult, reg, ws)
        buy_consolidation_breakout(regression_data, regressionResult, reg, ws)
        buy_final_candidate(regression_data, regressionResult, reg, ws)
        buy_oi(regression_data, regressionResult, reg, ws)
        buy_up_trend(regression_data, regressionResult, reg, ws)
        buy_market_uptrend(regression_data, regressionResult, reg, ws)
        buy_check_chart(regression_data, regressionResult, reg, ws)
        buy_month3_high_continue(regression_data, regressionResult, reg, ws)
        buy_heavy_uptrend_reversal(regression_data, regressionResult, reg, ws)
        buy_supertrend(regression_data, regressionResult, reg, ws)
        buy_risingMA(regression_data, regressionResult, reg, ws)
        buy_study_risingMA(regression_data, regressionResult, reg, ws)
        buy_random_filters(regression_data, regressionResult, reg, ws)
        return True
    return False

def buy_tail_reversal_filter(regression_data, regressionResult, reg, ws):
    if('MayBuy-CheckChart' in regression_data['filter1']):
        if(regression_data['PCT_day_change_pre1'] > 2
            and regression_data['PCT_day_change_pre2'] < 0
            and is_ema14_sliding_up(regression_data)
            and (last_5_day_all_up_except_today(regression_data) != True)
            and regression_data['bar_low'] >  regression_data['bar_low_pre1']
            and regression_data['low'] >  regression_data['low_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, 'MayBuy-CheckChart(upTrend-lastDayDown)')
    
    if(('MayBuy-CheckChart' in regression_data['filter1']) or ('MayBuyCheckChart' in regression_data['filter1'])):
#         if(-3 < regression_data['PCT_day_change'] < -1
#             and -3 < regression_data['PCT_change'] < 0
#             and regression_data['forecast_day_PCT_change'] < 0
#             and regression_data['month3HighChange'] > -5
#             and regression_data['month6HighChange'] > -5
#             and regression_data['yearHighChange'] > -5
#             and regression_data['year2HighChange'] > -5
#             ):
#             add_in_csv(regression_data, regressionResult, ws, 'sell(MayBuy-CheckChart)(downTrendstart-yearHigh)')
        if(-1 < regression_data['PCT_day_change'] < 0
            and -1 < regression_data['PCT_change'] < 0
            and regression_data['PCT_day_change_pre1'] < 0
            and regression_data['PCT_day_change_pre2'] < regression_data['PCT_day_change']
            and (regression_data['PCT_day_change_pre2'] < -1.5 or regression_data['PCT_day_change_pre3'] < -1)
            and regression_data['month3HighChange'] > -10
            and abs(regression_data['year2HighChange']) < abs(regression_data['year2LowChange'])
            #and regression_data['PCT_day_change_pre3'] < regression_data['PCT_day_change']
            ):
            add_in_csv(regression_data, regressionResult, ws, 'MayBuy-CheckChart(downTrend-mayReverseAtMonth3High)-0')
        elif(-2 < regression_data['PCT_day_change'] < -1
            and -2 < regression_data['PCT_change'] < -1
            and regression_data['PCT_day_change_pre1'] < -1
            and regression_data['PCT_day_change_pre2'] < 0
            and regression_data['PCT_day_change_pre3'] < 0
            #and regression_data['PCT_day_change_pre3'] < regression_data['PCT_day_change']
            ):
            add_in_csv(regression_data, regressionResult, ws, 'MayBuy-CheckChart(downTrend-mayReverseLast4DaysDown)-1')
        elif(-3.5 < regression_data['PCT_day_change'] < -1
            and -3.5 < regression_data['PCT_change'] < -1
            and regression_data['PCT_day_change_pre1'] < -1
            and regression_data['monthLowChange'] < 1
            and regression_data['month3LowChange'] > 1
            and regression_data['yearLowChange'] > 10
            and low_tail_pct(regression_data) < 2.5
            #and regression_data['PCT_day_change_pre3'] < regression_data['PCT_day_change']
            ):
            add_in_csv(regression_data, regressionResult, ws, 'MayBuy-CheckChart(monthLow-minimumLast2DayDown)')
    
    if(is_algo_buy(regression_data)):        
        if(('MayBuyCheckChart' in regression_data['filter1'])
            and ('Reversal' not in regression_data['filter3'])
            and high_tail_pct(regression_data) < 0.5
            ):
            if((-2 <= regression_data['PCT_day_change'] < -1) and (-2 <= regression_data['PCT_change'] < 0)
                and 3 > low_tail_pct(regression_data) > 1.8
                and regression_data['PCT_day_change_pre1'] < 0
                and regression_data['PCT_day_change_pre2'] < 0
                and regression_data['PCT_day_change_pre3'] < 0
                ):
                add_in_csv(regression_data, regressionResult, ws, "##ML:MayBuyCheckChart-last3DayDown")
            elif((-2 <= regression_data['PCT_day_change'] < -1) and (-2 <= regression_data['PCT_change'] < 0)
                and 3 > low_tail_pct(regression_data) > 1.8
                ):
                add_in_csv(regression_data, regressionResult, ws, "##ML:(check-chart-2-3MidCapCross)MayBuyCheckChart-1") 
    elif(('MayBuyCheckChart' in regression_data['filter1'])
        and ('Reversal' not in regression_data['filter3'])
        and high_tail_pct(regression_data) < 0.5
        ):
        if((-5 <= regression_data['PCT_day_change'] < -3) and (-6 <= regression_data['PCT_change'] < -2)
            and 5 > low_tail_pct(regression_data) > 2.8
            ):
            add_in_csv(regression_data, regressionResult, ws, "##ML:(Test)MayBuyCheckChart-PCTDayChangeLT(-3)BigHighTail")        
                
def buy_year_high(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(is_algo_buy(regression_data, True)
        and last_4_day_all_up(regression_data) == False
        and regression_data['year2HighChange'] > -10
        and regression_data['yearLowChange'] > 20
        and ((0 < regression_data['PCT_day_change'] < 1.5)
             or (-1 < regression_data['PCT_day_change'] < 0 and regression_data['forecast_day_PCT_change'] > 0)
            )
        and -1 < regression_data['PCT_change'] < 1.75
        ):
            add_in_csv(regression_data, regressionResult, ws, 'ML:buyYear2High')
            return True
    return False
    if(float(regression_data['forecast_day_VOL_change']) > 70
       and regression_data['PCT_day_change_pre1'] > -0.5
       and no_doji_or_spinning_buy_india(regression_data)
       ):
        if(-15 < regression_data['yearHighChange'] < -5 and regression_data['yearLowChange'] > 30
            and -0.5 < regression_data['PCT_day_change'] < 2 and regression_data['forecast_day_PCT2_change'] <= 2
            ):
            add_in_csv(regression_data, regressionResult, ws, 'buyYearHigh-0')
            return True
    if(float(regression_data['forecast_day_VOL_change']) > 35
       and regression_data['PCT_day_change_pre1'] > -0.5
       and no_doji_or_spinning_buy_india(regression_data)
       ):
        if(-15 < regression_data['yearHighChange'] < -5 and regression_data['yearLowChange'] > 30
            and -0.5 < regression_data['PCT_day_change'] < 2 and regression_data['forecast_day_PCT2_change'] <= 2
            ):
            add_in_csv(regression_data, regressionResult, ws, 'buyYearHigh-1')
            return True
    if(float(regression_data['forecast_day_VOL_change']) > 50
       and regression_data['PCT_day_change_pre1'] > -0.5
       and no_doji_or_spinning_buy_india(regression_data)
       ):
        if(-5 <= regression_data['yearHighChange'] < -1 and regression_data['yearLowChange'] > 15 
            and -0.5 < regression_data['PCT_day_change'] < 2 and regression_data['forecast_day_PCT2_change'] <= 2
            ):
            add_in_csv(regression_data, regressionResult, ws, 'buyYearHigh-2')
            return True
    
    return False

def buy_year_low(regression_data, regressionResult, reg, ws, ws1):
    return False
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(1 < regression_data['yearLowChange'] < 5 and regression_data['yearHighChange'] < -30 
        and 2 < regression_data['PCT_day_change'] < 6 and 2 < regression_data['PCT_day_change'] < 6
        and regression_data['forecast_day_PCT2_change'] > 0 and regression_data['forecast_day_PCT_change'] > 0
        and float(regression_data['forecast_day_VOL_change']) > 35
        ):
        add_in_csv(regression_data, regressionResult, ws, 'buyYearLow')
        return True
    elif(5 < regression_data['yearLowChange'] < 15 and regression_data['yearHighChange'] < -75 
        and 2 < regression_data['PCT_day_change'] < 5 and 2 < regression_data['PCT_day_change'] < 5
        and 5 > regression_data['forecast_day_PCT2_change'] > -0.5 and regression_data['forecast_day_PCT_change'] > 0
        and float(regression_data['forecast_day_VOL_change']) > 35
        ):
        add_in_csv(regression_data, regressionResult, ws1, 'buyYearLow1')
        return True
    return False

def buy_down_trend(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if((('NearLowYear2' in regression_data['filter3'])
        or ('BreakLowYear2' in regression_data['filter3'])
        or (regression_data['year2HighChange'] < -50 and regression_data['month3LowChange'] < 10)
        ) 
        and (regression_data['year2HighChange'] < -40)
        and high_tail_pct(regression_data) < 1
        and low_tail_pct(regression_data) > 1.1
        and regression_data['PCT_day_change'] < -1
        and regression_data['PCT_day_change_pre1'] < -2
        and regression_data['PCT_day_change_pre2'] < -2
        ):
        add_in_csv(regression_data, regressionResult, ws, 'buyYear2Low')
        return True
    if(regression_data['forecast_day_PCT10_change'] < -10
        and regression_data['year2HighChange'] < -60
        and regression_data['month3LowChange'] < 10
        and -1.5 < regression_data['forecast_day_PCT_change']
        and 3 < regression_data['PCT_day_change'] < 7
        and 2 < regression_data['PCT_change'] < 8
        and (regression_data['PCT_day_change_pre1'] < -4 or regression_data['PCT_day_change_pre2'] < -4)
        ):
        add_in_csv(regression_data, regressionResult, ws, 'sellYear2LowContinue')
        return True
    return False
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
            add_in_csv(regression_data, regressionResult, ws, 'buyDownTrend-0(Risky)')
            return True
        elif(last_5_day_all_down_except_today(regression_data)
            and ten_days_less_than_minus_seven(regression_data)
            and regression_data['forecast_day_PCT7_change'] < -4
            and regression_data['forecast_day_PCT10_change'] < -4
            ):
            add_in_csv(regression_data, regressionResult, ws, 'buyDownTrend-1')
            return True
        elif(regression_data['forecast_day_PCT7_change'] < -4
            and regression_data['forecast_day_PCT10_change'] < -4
            ):
            add_in_csv(regression_data, regressionResult, ws, 'buyDownTrend-2(Risky)')
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

def buy_high_indicators(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    if(kNeighboursValue > 3 and kNeighboursValue_other > 3
            and mlpValue > 2 and mlpValue_other > 2
            and regression_data['PCT_day_change'] > 5
            and regression_data['PCT_change'] > 5
            ):
            if(10 < regression_data['forecast_day_PCT10_change'] < 35):
                add_in_csv(regression_data, regressionResult, ws, 'buyHighKNeighbours-StockUptrend(Risky)')
            elif(regression_data['forecast_day_PCT10_change'] < 10
                and 5 < regression_data['PCT_day_change'] < 10
                and 5 < regression_data['PCT_change'] < 10
                ):
                add_in_csv(regression_data, regressionResult, ws, 'buyHighKNeighbours(Risky)') 
    elif(mlpValue >= 2.0 and kNeighboursValue >= 1.0
       and regression_data['month3HighChange'] < -3
       and regression_data['month3LowChange'] > 3
       and regression_data['yearHighChange'] < -10
       and regression_data['yearLowChange'] > 10
       #and regression_data['forecast_day_PCT10_change'] < 15
       and (high_tail_pct(regression_data) < 1.5 and (high_tail_pct(regression_data) < low_tail_pct(regression_data)))
       ):
        if(3 > regression_data['PCT_day_change'] > 1.5 and 3 > regression_data['PCT_change'] > -0.5
           and regression_data['forecast_day_PCT_change'] > 0
           and high_tail_pct(regression_data) < 1
           ):
            add_in_csv(regression_data, regressionResult, ws, 'buyHighIndicators(shouldNotOpenInMinus)')
            return True
        if(1 > regression_data['PCT_day_change'] > 0 and 2.5 > regression_data['PCT_change'] > -0.5):
            #add_in_csv(regression_data, regressionResult, ws, '(longDownTrend)buyHighIndicators')
            add_in_csv(regression_data, regressionResult, ws, None)
            return True 
    return False
              
def buy_pattern(regression_data, regressionResult, reg, ws, ws1):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    score = ''
    buy_pattern_without_mlalgo(regression_data, regressionResult)
    if(regression_data['yearLowChange'] > 10):
        if(is_algo_buy(regression_data)
            and regression_data['buyIndia_avg'] > 1.5 
            and high_tail_pct(regression_data) < 1.5
            ):
            add_in_csv(regression_data, regressionResult, ws, 'buyPatternsML')
            return True   
    
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
            add_in_csv(regression_data, regressionResult, ws, 'buyMorningStar-HighLowerTail')
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
            add_in_csv(regression_data, regressionResult, ws, 'buyMorningStar-dayDown')
            return True
        if(0.3 < regression_data['PCT_day_change'] < 1
            and (regression_data['open'] - regression_data['low']) >= ((regression_data['open'] - regression_data['close']) * 3)
            and (regression_data['open'] - regression_data['low']) >= ((regression_data['high'] - regression_data['close']) * 3)
            and regression_data['year2HighChange'] > -50
            ):
            add_in_csv(regression_data, regressionResult, ws, 'buyMorningStar-dayUp')
            return True
#         if(high_tail_pct(regression_data) < 1.5
#            and low_tail_pct(regression_data) > 2
#            ):
#             if(-1.5 < regression_data['PCT_day_change'] < 0 and -1.5 < regression_data['PCT_change'] < 0
#                 and (regression_data['close'] - regression_data['low']) >= ((regression_data['open'] - regression_data['close']) * 3)
#                 and (regression_data['close'] - regression_data['low']) >= ((regression_data['high'] - regression_data['open']) * 3)
#                 ):
#                 add_in_csv(regression_data, regressionResult, ws, '##TEST:buyMorningStar-3(Check2-3MidCapCross)')
#                 return True
#             if(0 < regression_data['PCT_day_change'] < 1
#                 and (regression_data['open'] - regression_data['low']) >= ((regression_data['open'] - regression_data['close']) * 3)
#                 and (regression_data['open'] - regression_data['low']) >= ((regression_data['high'] - regression_data['close']) * 3)
#                 ):
#                 add_in_csv(regression_data, regressionResult, ws, '##TEST:buyMorningStar-4(Check2-3MidCapCross)')
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
            add_in_csv(regression_data, regressionResult, ws, 'buyEveningStar-0')
            return True
        elif(4 > regression_data['PCT_day_change'] > 2 and 4 > regression_data['PCT_change'] > 2
            and -15 < regression_data['yearHighChange'] 
            and regression_data['PCT_day_change_pre3'] > -1
            and regression_data['PCT_day_change_pre1'] > -1
            and regression_data['PCT_change_pre1'] > -1
            and regression_data['PCT_change_pre2'] > -1
            ):
            add_in_csv(regression_data, regressionResult, ws, 'sellEveningStar-0')
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
                    add_in_csv(regression_data, regressionResult, ws, 'ML:sellEveningStar-2(Check2-3MidCapCross)')
                    return True
                return False
        elif((low_tail_pct(regression_data) < 0.5 or (regression_data['forecast_day_PCT_change'] > 6 and low_tail_pct(regression_data) < 1))
            and 2 < high_tail_pct(regression_data) < 3.5
            and low_tail_pct(regression_data) < 0.5
            ):
            if(2 > regression_data['PCT_day_change'] > 0.5 and 2 > regression_data['PCT_change'] > 0
                ):
                if(is_algo_sell(regression_data)):
                    add_in_csv(regression_data, regressionResult, ws, 'ML:sellEveningStar-Risky-3(Check2-3MidCapCross)')
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
            add_in_csv(regression_data, regressionResult, ws, 'buyDayLowVolLow-0')
            return True
        elif((regression_data['PCT_day_change'] < -5 or regression_data['PCT_change'] < -5)
           and float(regression_data['forecast_day_VOL_change']) < -20
           and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
           and regression_data['PCT_day_change_pre1'] < -1.5
           and regression_data['forecast_day_PCT_change'] < -5
           #and regression_data['forecast_day_PCT10_change'] < -5
           ):
            add_in_csv(regression_data, regressionResult, ws, 'sellDayLowVolLow-0')
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
                add_in_csv(regression_data, regressionResult, ws, 'buyDayLowVolLow-01')
                return True
            elif(regression_data['month6LowChange'] > 10
                and regression_data['yearLowChange'] > 20
                ):
                add_in_csv(regression_data, regressionResult, ws, 'sellDayLowVolLow-01')
                return True
        elif((regression_data['PCT_day_change'] < -5 and regression_data['PCT_change'] < -4)
           and float(regression_data['forecast_day_VOL_change']) < -30
           and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
           and regression_data['PCT_day_change_pre1'] < -1.5
           and -20 < regression_data['SMA50'] < 10
           and regression_data['SMA9'] > -7
           #and regression_data['PCT_day_change_pre2'] < -1.5
           ):
            add_in_csv(regression_data, regressionResult, ws, 'buyDayLowVolLow-02-checkMorningTrend(.5SL)')
            return True
        elif((regression_data['PCT_day_change'] < -5 and regression_data['PCT_change'] < -4)
           and float(regression_data['forecast_day_VOL_change']) < 0
           and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
           and -5 < regression_data['PCT_day_change_pre1'] < -1.5
           and regression_data['PCT_day_change_pre2'] > 1.5
           and regression_data['year2LowChange'] > 10
           ):
            add_in_csv(regression_data, regressionResult, ws, 'sellDayLowVolLow-02-checkMorningTrend(.5SL)')
            return True
        elif((regression_data['PCT_day_change'] < -4 and regression_data['PCT_change'] < -2)
           and float(regression_data['forecast_day_VOL_change']) < 0
           and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
           and regression_data['PCT_day_change_pre1'] < -1.5
           and regression_data['PCT_day_change_pre2'] < -1.5
           and -20 < regression_data['SMA50']
           and regression_data['SMA9'] > -7
           ):
            add_in_csv(regression_data, regressionResult, ws, 'sellDayLowVolLow-03-checkMorningTrend(.5SL)')
            return True
        elif((regression_data['PCT_day_change'] < -4 and regression_data['PCT_change'] < -2)
           and float(regression_data['forecast_day_VOL_change']) < 0
           and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
           and regression_data['PCT_day_change_pre1'] < -1.5
           and regression_data['PCT_day_change_pre2'] < -1.5
           ):
            if(is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, 'ML:buyDayLowVolLow-03-checkMorningTrend(.5SL)-after10:30')
                return True
            return False
        elif((regression_data['PCT_day_change'] < -4 and regression_data['PCT_change'] < -2)
           and float(regression_data['forecast_day_VOL_change']) < 0
           and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
           and regression_data['PCT_day_change_pre1'] < -1.5
           and regression_data['PCT_day_change_pre2'] < -1.5
           ):
            if(is_algo_sell(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, 'ML:sellDayLowVolLow-03-checkMorningTrend(.5SL)')
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
#         add_in_csv(regression_data, regressionResult, ws, '##buyDayLowVolLow-2')
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
                add_in_csv(regression_data, regressionResult, ws, 'ML:buyOI-2-checkBase-Risky')
                return True
            return False
        elif(((regression_data['forecast_day_VOL_change'] > 400 and 1 < regression_data['PCT_day_change'] < 3.5 and 1 < regression_data['PCT_change'] < 3.5)
            or (regression_data['forecast_day_VOL_change'] > 500 and 1 < regression_data['PCT_day_change'] < 4.5 and 1 < regression_data['PCT_change'] < 4.5)
            )
            #and regression_data['PCT_day_change_pre1'] > -0.5
            ):
            if((mlpValue >= 0.3 and kNeighboursValue >= 0.3) or is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, 'ML:buyOI-3-checkBase-Risky')
                return True
            return False    
        elif((regression_data['forecast_day_VOL_change'] > 500 and 1 < regression_data['PCT_day_change'] < 5 and 1 < regression_data['PCT_change'] < 5)
            and float(regression_data['contract']) > 50 
            and (regression_data['forecast_day_PCT10_change'] < -8 or regression_data['forecast_day_PCT7_change'] < -8)
            ):
            if((mlpValue >= 0.3 and kNeighboursValue >= 0.3) or is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, 'ML:buyOI-4-checkBase-Risky')
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
        and (regression_data['PCT_day_change'] > 1 or regression_data['PCT_change'] > 1)
        and regression_data['forecast_day_PCT_change'] > 0.5
        and regression_data['forecast_day_PCT2_change'] > 0.5
        and regression_data['forecast_day_PCT3_change'] > 0
        and regression_data['forecast_day_PCT4_change'] > 0
        and preDayPctChangeUp_orVolHigh(regression_data)
        and regression_data['open'] > 50
        and last_7_day_all_up(regression_data) == False
        ):
        if((regression_data['forecast_day_VOL_change'] > 70 and 0.75 < regression_data['PCT_day_change'] < 2 and 0.5 < regression_data['PCT_change'] < 2)
            and float(regression_data['contract']) > 10
            ):
            add_in_csv(regression_data, regressionResult, ws, 'Reversal(Test):sellReversalOI-0(openAroundLastCloseAnd5MinuteChart)')
            return True
#         elif((regression_data['forecast_day_VOL_change'] > 35 and 0.75 < regression_data['PCT_day_change'] < 2 and 0.5 < regression_data['PCT_change'] < 2)
#             and float(regression_data['contract']) > 20
#             ):
#             add_in_csv(regression_data, regressionResult, ws, 'Reversal(Test):sellReversalOI-1(openAroundLastCloseAnd5MinuteChart)')
#             return True
#         elif((regression_data['forecast_day_VOL_change'] > 150 and 0.75 < regression_data['PCT_day_change'] < 3 and 0.5 < regression_data['PCT_change'] < 3)
#             and regression_data['PCT_day_change_pre1'] > -0.5
#             ):
#             add_in_csv(regression_data, regressionResult, ws, 'Reversal(Test):sellReversalOI-2(openAroundLastCloseAnd5MinuteChart)')
#             return True
#         elif(((regression_data['forecast_day_VOL_change'] > 400 and 0.75 < regression_data['PCT_day_change'] < 3.5 and 0.5 < regression_data['PCT_change'] < 3.5)
#             or (regression_data['forecast_day_VOL_change'] > 500 and 0.75 < regression_data['PCT_day_change'] < 4.5 and 0.5 < regression_data['PCT_change'] < 4.5)
#             )
#             and regression_data['forecast_day_PCT10_change'] > 10
#             ):
#             if(('P@[') in regression_data['buyIndia']):
#                 add_in_csv(regression_data, regressionResult, ws, 'Reversal(Test):sellReversalOI-3-checkBase-(openAroundLastCloseAnd5MinuteChart)')
#                 return True
#             elif(preDayPctChangeUp_orVolHigh(regression_data)):
#                 add_in_csv(regression_data, regressionResult, ws, 'Reversal(Test):buyContinueOI-3-checkBase-(openAroundLastCloseAnd5MinuteChart)')
#                 return True
#         elif((regression_data['forecast_day_VOL_change'] > 500 and 0.75 < regression_data['PCT_day_change'] < 5 and 0.5 < regression_data['PCT_change'] < 5)
#             and float(regression_data['contract']) > 50 
#             and regression_data['forecast_day_PCT10_change'] > 10
#             ):
#             add_in_csv(regression_data, regressionResult, ws, 'Reversal(Test):sellReversalOI-4-checkBase-(openAroundLastCloseAnd5MinuteChart)')
#             return True
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
                add_in_csv(regression_data, regressionResult, ws, 'sellFinalContinue-00')
                return True
            elif(3 < regression_data['PCT_day_change'] < 5 and 3 < regression_data['PCT_change'] < 5
                ):
                if(is_algo_buy(regression_data)):
                    add_in_csv(regression_data, regressionResult, ws, 'ML:buyFinalContinue-00')
                    return True
                return False
            elif(regression_data['forecast_day_PCT_change'] > 0
                and regression_data['forecast_day_VOL_change'] <= 0
                ):
                add_in_csv(regression_data, regressionResult, ws, 'buyFinalContinue-00')
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
        
#     if(0.5 < regression_data['forecast_day_PCT10_change'] < 2
#         and regression_data['forecast_day_PCT_change'] > 1
#         and 2 < regression_data['PCT_day_change'] < 5.5
#         and 2 < regression_data['PCT_change'] < 5.5
#         and regression_data['PCT_day_change_pre1'] > -0.5
#         and 0.5 < high_tail_pct(regression_data) < 2
#         and regression_data['buyIndia_avg'] > -0.75
#         and regression_data['sellIndia_avg'] > -0.75
#         and regression_data['month3LowChange'] > 4
#         and ('P@[' not in regression_data['sellIndia'])
#         and abs_month3High_more_than_month3Low(regression_data)
#         and (abs(regression_data['month6HighChange']) > abs(regression_data['month6LowChange']))
#         ):
#         add_in_csv(regression_data, regressionResult, ws, 'buy-2week-breakoutup')
#     elif(0.5 < regression_data['forecast_day_PCT10_change'] < 3
#         #and regression_data['forecast_day_PCT_change'] > 1
#         and 2 < regression_data['PCT_day_change']
#         and 2 < regression_data['PCT_change']
#         and regression_data['PCT_day_change_pre1'] > -0.5
#         and 0.5 < high_tail_pct(regression_data) < 2
#         #and regression_data['buyIndia_avg'] > -0.75
#         #and regression_data['sellIndia_avg'] > -0.75
#         #and regression_data['month3LowChange'] > 4
#         #and ('P@[' not in regression_data['sellIndia'])
#         and abs_month3High_more_than_month3Low(regression_data)
#         and (abs(regression_data['month6HighChange']) > abs(regression_data['month6LowChange']))
#         ):
#         add_in_csv(regression_data, regressionResult, ws, 'sell-2week-breakoutup')
    if(0.5 < regression_data['forecast_day_PCT10_change'] < 3
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
            add_in_csv(regression_data, regressionResult, ws, '(check-chart):ML:buy-2week-breakoutup')
            return True
        elif(is_algo_sell(regression_data)):
            add_in_csv(regression_data, regressionResult, ws, '(check-chart):ML:sell-2week-breakoutup')
            return True
    elif(0.5 < regression_data['forecast_day_PCT10_change'] < 3
        and regression_data['forecast_day_PCT_change'] > 1
        and 2 < regression_data['PCT_day_change'] < 5.5
        and 2 < regression_data['PCT_change'] < 5.5
        and high_tail_pct(regression_data) < 1
        #and regression_data['buyIndia_avg'] > -0.75
        #and regression_data['sellIndia_avg'] > -0.75
        and regression_data['month3LowChange'] > 4
        and regression_data['month3HighChange'] < -4
        ):
        add_in_csv(regression_data, regressionResult, ws, '(check-chart)buy-2week-breakoutup(|-|-| or --|)')
        return True
            
    
          
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

def buy_consolidation_breakout(regression_data, regressionResult, reg, ws):
    return False
     
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
           
def buy_oi(regression_data, regressionResult, reg, ws):
    return False
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

def buy_up_trend(regression_data, regressionResult, reg, ws):
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
        if(('ReversalLowYear2' in regression_data['filter3']) and (regression_data['year2HighChange'] < -40)):
            add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyYear2LowReversal(Confirm)')
        if(('ReversalLowYear' in regression_data['filter3']) and (regression_data['yearHighChange'] < -30)):
            add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyYearLowReversal(Confirm)')
        if(('ReversalLowMonth6' in regression_data['filter3']) and (regression_data['month6HighChange'] < -25)):
            add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyMonth6LowReversal(Confirm)')
        if(('ReversalLowMonth3' in regression_data['filter3']) and (regression_data['month3HighChange'] < -15)):
            add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyMonth3LowReversal(Confirm)')
        if(regression_data['month3HighChange'] < -20 and (regression_data['month6HighChange'] < -20 or regression_data['yearHighChange'] < -30)
            ):
            if(('NearLowYear2' in regression_data['filter3']) and (regression_data['year2HighChange'] < -40)):
                add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyYear2Low')
            if(('NearLowYear' in regression_data['filter3']) and (regression_data['yearHighChange'] < -30)):
                add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyYearLow')
            if(('NearLowMonth6' in regression_data['filter3']) and (regression_data['month6HighChange'] < -25)):
                add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyMonth6Low')
            if(('NearLowMonth3' in regression_data['filter3']) and (regression_data['month3HighChange'] < -20)):
                add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyMonth3Low')

def buy_check_chart(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    #Check for last 5 from latest up should crossover
    if(('NearHighMonth3' in regression_data['filter3']) 
        or ('BreakHighMonth3' in regression_data['filter3'])
        or ('ReversalHighMonth3' in regression_data['filter3'])
        ):
        if(regression_data['month3LowChange'] > 15
            and ((-5 < regression_data['PCT_change'] < -1) and (-5 < regression_data['PCT_day_change'] < -2))
            and regression_data['close'] < regression_data['bar_low_pre1']
            and regression_data['close'] < regression_data['bar_low_pre2']
            ):
            add_in_csv(regression_data, regressionResult, ws, '##(Check-chart-buy):month3High-InMinus')
            
    elif(('NearHighMonth6' in regression_data['filter3']) 
        or ('ReversalHighMonth6' in regression_data['filter3'])
        ):
        if(regression_data['month6LowChange'] > 20
            and ((-5 < regression_data['PCT_change'] < -1) and (-5 < regression_data['PCT_day_change'] < -2))
            and regression_data['close'] < regression_data['bar_low_pre1']
            and regression_data['close'] < regression_data['bar_low_pre2']
            ):
            add_in_csv(regression_data, regressionResult, ws, '##(Check-chart-buy):month6High-InMinus')
            
    elif(('NearHighYear' in regression_data['filter3']) 
        or ('ReversalHighYear' in regression_data['filter3'])
        ):
        if(regression_data['month6LowChange'] > 20
            and ((-5 < regression_data['PCT_change'] < -1) and (-5 < regression_data['PCT_day_change'] < -2))
            and regression_data['close'] < regression_data['bar_low_pre1']
            and regression_data['close'] < regression_data['bar_low_pre2']
            ):
            add_in_csv(regression_data, regressionResult, ws, '##(Check-chart-buy):YearHigh-InMinus')
                
    
    if(('NearHighMonth3' in regression_data['filter3']) 
        or ('BreakHighMonth3' in regression_data['filter3'])
        #or ('ReversalHighMonth3' in regression_data['filter3'])
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
    elif(('NearHighMonth6' in regression_data['filter3']) 
        or ('BreakHighMonth6' in regression_data['filter3'])
        #or ('ReversalHighMonth6' in regression_data['filter3'])
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
    
#         if((('NearHighYear2' in regression_data['filter3']) 
#             or ('ReversalHighYear2' in regression_data['filter3'])
#             or ('BreakHighYear2' in regression_data['filter3'])
#             )):    
#             if(regression_data['year2LowChange'] > 50
#                 and regression_data['year2HighChange'] > -1
#                 and ((regression_data['PCT_change'] > 1) and (regression_data['PCT_day_change'] > 1))
#                 and regression_data['close'] > regression_data['bar_high_pre1']
#                 ):
#                 if(regression_data['PCT_change'] > 4
#                     and ('BreakHighYear2' in regression_data['filter3'])
#                     ):
#                     add_in_csv(regression_data, regressionResult, ws, '##(Check-chart-sell):year2High-InPlus')
#                 else:
#                     add_in_csv(regression_data, regressionResult, ws, '##(Check-chart):year2High-InPlus')
#                     
#         elif((('NearHighYear' in regression_data['filter3'])
#             or ('ReversalHighYear' in regression_data['filter3'])
#             or ('BreakHighYear' in regression_data['filter3'])
#             )):
#             if(regression_data['yearLowChange'] > 40
#                 and regression_data['yearHighChange'] > -1
#                 and ((regression_data['PCT_change'] > 1) and (regression_data['PCT_day_change'] > 1))
#                 and regression_data['close'] > regression_data['bar_high_pre1']
#                 ):
#                 if(regression_data['PCT_change'] > 4
#                     and ('BreakHighYear' in regression_data['filter3'])
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
            add_in_csv(regression_data, regressionResult, ws, '##(Check-chart):MayBuyCheckChart-(|`|_|)')
    elif(is_algo_buy(regression_data)
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
                add_in_csv(regression_data, regressionResult, ws, '##(Check-chart):MayBuyCheckChart-(IndexNotUpInSecondHalf)')

def buy_month3_high_continue(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    if(('NearHighMonth3' in regression_data['filter3']) 
        or ('BreakHighMonth3' in regression_data['filter3'])
        or ('ReversalHighMonth3' in regression_data['filter3'])
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
                add_in_csv(regression_data, regressionResult, ws, '##(Check-chart)buyMonth3High-Continue')
                return True
            elif(regression_data['SMA4_2daysBack'] < -0.5 and regression_data['SMA9_2daysBack'] < -0.5
                ):
                add_in_csv(regression_data, regressionResult, ws, '##(Check-chart)sellMonth3High-Continue')
                return True
            elif(is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, '##(Check-chart)ML:buyMonth3High-Continue')
                return True
            elif(is_algo_sell(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, '##(Check-chart)ML:sellMonth3High-Continue')
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
#                     add_in_csv(regression_data, regressionResult, ws, '##buyHeavyUpTrend-0-Continue')
#                 elif(ten_days_more_than_seven(regression_data)
#                      and (('NearHighMonth3' in regression_data['filter3']) 
#                           or ('NearHighMonth6' in regression_data['filter3'])
#                          )
#                 ):
#                     add_in_csv(regression_data, regressionResult, ws, '##buyHeavyUpTrend-1-Continue')
        if((regression_data['month3HighChange'] > -5)
            and ((0 < regression_data['PCT_change'] < 5) and (0 < regression_data['PCT_day_change'] < 5))
            and regression_data['PCT_day_change_pre1'] > 1
            ):
            if((2 < regression_data['PCT_change'] < 7) and (3 < regression_data['PCT_day_change'] < 7)
                and ten_days_more_than_seven(regression_data)
                and (('NearHighMonth3' in regression_data['filter3']) 
                      or ('BreakHighMonth3' in regression_data['filter3'])
                      or ('NearHighMonth6' in regression_data['filter3'])
                      or ('BreakHighMonth6' in regression_data['filter3'])
                    )
            ):
                if(regression_data['month6HighChange'] > -5
                    and (3 < regression_data['PCT_change'] or 3 < regression_data['PCT_day_change'])
                    and('BELTHOLD' and 'LONGLINE' not in regression_data['buyIndia'])
                    and regression_data['year2HighChange'] > -20
                    ):
                    add_in_csv(regression_data, regressionResult, ws, 'sellHeavyUpTrend-Reversal')
                else:
                    if(regression_data['forecast_day_VOL_change'] < 0):
                        add_in_csv(regression_data, regressionResult, ws, 'buyHeavyUpTrend-Reversal-(Risky)')
                    elif('P@' in regression_data['buyIndia']
                        and regression_data['year2HighChange'] > -20
                        ):
                        add_in_csv(regression_data, regressionResult, ws, 'sellHeavyUpTrend-Reversal-(Risky)')
            elif((2 < regression_data['PCT_change'] < 7) and (3 < regression_data['PCT_day_change'] < 7)
                #and ten_days_more_than_seven(regression_data)
                and (('NearHighMonth3' in regression_data['filter3']) 
                      or ('BreakHighMonth3' in regression_data['filter3'])
                      or ('NearHighMonth6' in regression_data['filter3'])
                      or ('BreakHighMonth6' in regression_data['filter3'])
                    )
                and regression_data['year2HighChange'] < -20
                and regression_data['yearHighChange'] > -50
                ):
                add_in_csv(regression_data, regressionResult, ws, '(Test)sellHeavyUpTrend-Reversal-1')
                   
def buy_supertrend(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    
    if(regression_data['close'] > 50
        ):
        if(0 < regression_data['forecast_day_PCT2_change'] < regression_data['forecast_day_PCT3_change'] < regression_data['forecast_day_PCT4_change'] < regression_data['forecast_day_PCT5_change']
            and regression_data['forecast_day_PCT5_change'] > 5
            and regression_data['forecast_day_PCT10_change'] < regression_data['forecast_day_PCT5_change']
            and regression_data['forecast_day_PCT10_change'] < regression_data['forecast_day_PCT7_change']
            and -0.75 < regression_data['PCT_day_change_pre1'] < 2.5
            and -0.75 < regression_data['PCT_day_change'] < 0.5
            and regression_data['yearHighChange'] < -5
            and regression_data['yearLowChange'] > 15
            and regression_data['month3LowChange'] > 10 
            #and regression_data['low'] > regression_data['low_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, 'set1')
            if(regression_data['PCT_day_change_pre1'] < 0
                and -0.75 < regression_data['PCT_day_change'] < 0):
                add_in_csv(regression_data, regressionResult, ws, '--')
            elif(regression_data['PCT_day_change_pre1'] > 0
                and 0 < regression_data['PCT_day_change'] < 0.75):
                add_in_csv(regression_data, regressionResult, ws, '++')
            elif(regression_data['PCT_day_change_pre1'] < 0
                and 0 < regression_data['PCT_day_change'] < 0.75):
                add_in_csv(regression_data, regressionResult, ws, '-+')
            elif(regression_data['PCT_day_change_pre1'] > 0
                and -0.75 < regression_data['PCT_day_change'] < 0):
                add_in_csv(regression_data, regressionResult, ws, '+-')
            if((regression_data['PCT_day_change_pre1'] < 0 and regression_data['PCT_day_change'] < 0)
                or (regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change'] > 0)):    
                if((regression_data['forecast_day_PCT_change'] < 0
                        and regression_data['PCT_day_change'] < 0
                        and regression_data['SMA4'] < 1.5
                        and high_tail_pct(regression_data) < 1.5
                        and regression_data['low'] > regression_data['low_pre1']
                    )
                    ):
                    add_in_csv(regression_data, regressionResult, ws, 'buySuperTrend-0')
                elif('SPINNINGTOP' in regression_data['sellIndia']
                    and regression_data['low'] > regression_data['low_pre1']
                    ):
                    add_in_csv(regression_data, regressionResult, ws, 'sellSuperTrend-0')
                elif(regression_data['PCT_day_change_pre2'] > 2
                    and regression_data['PCT_change_pre2'] > 2
                    and regression_data['low'] < regression_data['low_pre1']
                    ):
                    if(is_algo_buy(regression_data)):
                       add_in_csv(regression_data, regressionResult, ws, 'ML:buySuperTrend-2')
                       return True
                    return False
                elif(regression_data['PCT_day_change_pre2'] < 0.5
                    and regression_data['PCT_change_pre2'] < 0.5
                    and regression_data['low'] < regression_data['low_pre1']
                    ):
                    add_in_csv(regression_data, regressionResult, ws, 'sellSuperTrend-1')
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
                    add_in_csv(regression_data, regressionResult, ws, 'sellSuperTrend-2')
                elif(5 > regression_data['month3HighChange'] > 0.45
                    or (regression_data['PCT_day_change'] < 0
                       and regression_data['month3LowChange'] < 25
                       and regression_data['year2HighChange'] < -10
                       and regression_data['year2HighChange'] < -30
                       )
                    ):
                    add_in_csv(regression_data, regressionResult, ws, 'buySuperTrend-1')
        elif(0 < regression_data['forecast_day_PCT2_change'] < regression_data['forecast_day_PCT3_change'] < regression_data['forecast_day_PCT4_change'] < regression_data['forecast_day_PCT5_change']
            and regression_data['forecast_day_PCT5_change'] > 5
            and -0.75 < regression_data['PCT_day_change_pre1'] < 2.5
            and -0.75 < regression_data['PCT_day_change'] < 0.5
            and regression_data['yearHighChange'] < -5
            and regression_data['yearLowChange'] > 15
            and regression_data['month3LowChange'] > 10   
            #and regression_data['low'] > regression_data['low_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, 'set2')
            if(regression_data['PCT_day_change_pre1'] < 0
                and -0.75 < regression_data['PCT_day_change'] < 0):
                add_in_csv(regression_data, regressionResult, ws, '--')
            elif(regression_data['PCT_day_change_pre1'] > 0
                and 0 < regression_data['PCT_day_change'] < 0.75):
                add_in_csv(regression_data, regressionResult, ws, '++')
            elif(regression_data['PCT_day_change_pre1'] < 0
                and 0 < regression_data['PCT_day_change'] < 0.75):
                add_in_csv(regression_data, regressionResult, ws, '-+')
            elif(regression_data['PCT_day_change_pre1'] > 0
                and -0.75 < regression_data['PCT_day_change'] < 0):
                add_in_csv(regression_data, regressionResult, ws, '+-')
            if((regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change'] > 0)
                 or (regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change'] < 0)
                ):
                if('SPINNINGTOP' in regression_data['sellIndia']
                    and regression_data['year2LowChange'] > 50
                    and regression_data['low'] > regression_data['low_pre1']
                    ):
                    add_in_csv(regression_data, regressionResult, ws, 'buySuperTrend-0')
                elif(regression_data['PCT_day_change_pre2'] > 2
                    and regression_data['PCT_change_pre2'] > 2
                    and regression_data['yearHighChange'] < -20
                    and regression_data['low'] < regression_data['low_pre1']
                    ):
                    add_in_csv(regression_data, regressionResult, ws, 'buySuperTrend-1')
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
                    add_in_csv(regression_data, regressionResult, ws, 'sellSuperTrend-0')
                elif((regression_data['PCT_day_change'] < 0
                       and regression_data['PCT_change_pre1'] > 1
                       and regression_data['month3LowChange'] < 25
                       and regression_data['year2HighChange'] < -10
                       and regression_data['year2HighChange'] < -30
                       )
                    ):
                    add_in_csv(regression_data, regressionResult, ws, 'sellSuperTrend-1')  
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
                        add_in_csv(regression_data, regressionResult, ws, 'sellSuperTrend-1')
                    elif(regression_data['PCT_day_change'] < 0
                        and regression_data['low'] < regression_data['low_pre1']
                        ):
                        add_in_csv(regression_data, regressionResult, ws, None)
                    elif(regression_data['PCT_day_change'] < 0
                        ):
                        add_in_csv(regression_data, regressionResult, ws, None)
                    elif(('[') not in regression_data['buyIndia']):
                        add_in_csv(regression_data, regressionResult, ws, 'sellSuperTrend-1')
        return True
    return False

def buy_risingMA(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    
    if(is_algo_buy(regression_data)
        and regression_data['SMA4'] > 0
        and regression_data['SMA9'] > 0
        and regression_data['SMA25'] > 0
        and regression_data['SMA100'] > 10
        and regression_data['SMA200'] > 10
        and regression_data['year2HighChange'] < -5
        and regression_data['yearHighChange'] < -5
        and (regression_data['PCT_day_change_pre1'] < 0.5
             or -0.5 < regression_data['PCT_day_change'] < 0.5)
        ):
        if(regression_data['PCT_change'] < -4.5
            and regression_data['PCT_day_change'] < -4.5):
            add_in_csv(regression_data, regressionResult, ws, '(Test)ML:AllMAPositive_Uptrend_(LT-4.5)')
        elif(-5 < regression_data['PCT_change'] < -2
            and -5 < regression_data['PCT_day_change'] < -2):
            add_in_csv(regression_data, regressionResult, ws, '(Test)ML:AllMAPositive_Uptrend_(LT-2)')
        elif(-5 < regression_data['PCT_change'] < 0
            and -5 < regression_data['PCT_day_change'] < 0):
            add_in_csv(regression_data, regressionResult, ws, '(Test)ML:AllMAPositive_Uptrend_(LT0)')
        elif(-1 < regression_data['PCT_change'] < 1
            and -1 < regression_data['PCT_day_change'] < 1):
            add_in_csv(regression_data, regressionResult, ws, '(Test)ML:AllMAPositive_Uptrend_(BT+1-1)')
        elif(0 < regression_data['PCT_change'] < 2
            and 0 < regression_data['PCT_day_change'] < 2):
            add_in_csv(regression_data, regressionResult, ws, '(Test)ML:AllMAPositive_Uptrend_(GT0)')
        elif(0 < regression_data['PCT_change'] < 5
            and 0 < regression_data['PCT_day_change'] < 5):
            add_in_csv(regression_data, regressionResult, ws, '(Test)ML:AllMAPositive_Uptrend_(GT+2)')
        elif(regression_data['PCT_change'] > 4.5
            and regression_data['PCT_day_change'] > 4.5):
            add_in_csv(regression_data, regressionResult, ws, '(Test)ML:AllMAPositive_Uptrend_(GT+4.5)')
        else:
            add_in_csv(regression_data, regressionResult, ws, '(Test)ML:AllMAPositive_Uptrend')
    
    if(regression_data['year2HighChange'] < -50
        ):
        if(regression_data['yearHighChange'] < -30
            and 2 < regression_data['PCT_day_change'] < 4
            #and regression_data['forecast_day_PCT_change'] < 1
            and regression_data['forecast_day_PCT_change'] < regression_data['forecast_day_PCT4_change']
            and regression_data['forecast_day_PCT2_change'] < 1
            and regression_data['forecast_day_PCT3_change'] < 1
            and regression_data['forecast_day_PCT4_change'] < 0
            and regression_data['forecast_day_PCT5_change'] < 0
            and regression_data['forecast_day_PCT7_change'] < 0
            and regression_data['forecast_day_PCT10_change'] < 0
            and high_tail_pct(regression_data) < 1
            ):
            add_in_csv(regression_data, regressionResult, ws, 'buyYear2LowBreakingUp')
        elif(regression_data['yearHighChange'] < -20
            and -1.5 < regression_data['PCT_day_change'] < -0.3
            and -2 < regression_data['PCT_change'] < 1 
            and regression_data['PCT_day_change_pre1'] < 0
            and regression_data['EMA14_2daysBack'] < regression_data['EMA14_1daysBack'] < regression_data['EMA14']
            and (((regression_data['bar_low'] - regression_data['bar_low_pre1'])/regression_data['bar_low'])*100) > 0
            and regression_data['low'] > regression_data['low_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, 'buyMayYear2LowBreakingUp')
            
            
    
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
                add_in_csv(regression_data, regressionResult, ws, None)
                return True
            elif(regression_data['PCT_day_change_pre1'] < -1
                and -5 < regression_data['PCT_day_change'] < -1
                and all_day_pct_change_negative_except_today(regression_data) != True
                ):
                add_in_csv(regression_data, regressionResult, ws, 'sellRisingMA')
                return True
            elif(regression_data['PCT_day_change_pre1'] > 1
                and regression_data['SMA50'] < 1
                ):
                add_in_csv(regression_data, regressionResult, ws, 'sellRisingMA')
                return True
            elif(is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, 'ML:BuyRisingMA-Risky-0')
                return True
            elif(is_algo_sell(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, 'ML:SellRisingMA-Risky-0')
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
                add_in_csv(regression_data, regressionResult, ws, 'buyRisingMA-1')
                return True
            elif(('P@' or 'M@') in regression_data['buyIndia']):
                add_in_csv(regression_data, regressionResult, ws, 'sellRisingMA-1')
                return True
            elif(is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, 'ML:BuyRisingMA-Risky-1')
                return True
            elif(is_algo_sell(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, 'ML:SellRisingMA-Risky-1')
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
                add_in_csv(regression_data, regressionResult, ws, 'ML:BuyRisingMA-Risky-2')
                return True
            elif(is_algo_sell(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, 'ML:SellRisingMA-Risky-2')
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
                add_in_csv(regression_data, regressionResult, ws, 'sellRisingMAuptrend-0')
                return True
            elif(regression_data['month3LowChange'] < 10
                and ('P@[' or 'M@[') in regression_data['buyIndia']
                
                ):
                if(is_algo_sell(regression_data)):
                    add_in_csv(regression_data, regressionResult, ws, 'ML:sellRisingMAuptrend-1')
                    return True
                return False
            elif(high_tail_pct(regression_data) > 1.5
                and regression_data['month6HighChange'] > -80
                and ('P@[' or 'M@[') not in regression_data['buyIndia']
                ):
                add_in_csv(regression_data, regressionResult, ws, 'sellRisingMAuptrend-2')
                return True
            elif(2 < regression_data['PCT_day_change'] < 4
                and 1.5 < regression_data['PCT_change'] < 4
                and regression_data['forecast_day_PCT7_change'] > 0
                and regression_data['forecast_day_PCT10_change'] > 0
                and (regression_data['month6HighChange'] > -80 and regression_data['month3HighChange'] > -80)
                and ('P@[' or 'M@[') in regression_data['buyIndia']
                #and is_algo_buy(regression_data)
                ):
                add_in_csv(regression_data, regressionResult, ws, 'buyRisingMAuptrend-(Risky)')
                return True
            elif(2 < regression_data['PCT_day_change'] < 4
                and 1.5 < regression_data['PCT_change'] < 4
                and regression_data['forecast_day_PCT7_change'] > 0
                and regression_data['forecast_day_PCT10_change'] > 0
                and (regression_data['month6HighChange'] < -80 or regression_data['month3HighChange'] < -80)
                ):
                if(is_algo_buy(regression_data)):
                    add_in_csv(regression_data, regressionResult, ws, 'ML:buyRisingMAuptrend-Risky')
                    return True
                elif(is_algo_sell(regression_data)):
                    add_in_csv(regression_data, regressionResult, ws, 'ML:sellRisingMAuptrend-Risky')
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
                and is_algo_buy(regression_data)
                ):
                add_in_csv(regression_data, regressionResult, ws, 'ML:buyRisingMA-down-0')
                return True
            elif((((regression_data['PCT_change'] + regression_data['PCT_change_pre1'])  < -4
                and (regression_data['PCT_change'] < -3.5 or regression_data['PCT_change_pre1'] < -3.5)
                )
                )
                and regression_data['PCT_change'] < 0
                and regression_data['year2HighChange'] < -40
                and -5 < regression_data['SMA25'] < 0
                and is_algo_sell(regression_data)
                ):
                add_in_csv(regression_data, regressionResult, ws, 'ML:sellRisingMA-down-(Risky)')
                return True
            elif((
                -4 < regression_data['PCT_change'] < -2
                )
                and regression_data['year2HighChange'] < -30
                and -2.5 < regression_data['SMA9'] < 2
                and -5 < regression_data['SMA25'] < 0
                ):
                if(is_algo_buy(regression_data)):
                    add_in_csv(regression_data, regressionResult, ws, 'ML:buyRisingMA-down-Risky')
                    return True
                elif(is_algo_sell(regression_data)):
                    add_in_csv(regression_data, regressionResult, ws, 'ML:sellRisingMA-down-Risky')
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
#                 add_in_csv(regression_data, regressionResult, ws, '(Test):buyRisingMA-uptrend-SMA25gt0')
                #add_in_csv(regression_data, regressionResult, ws, None)
        
        if((('NearLowYear2' in regression_data['filter3']) 
            or ('NearLowYear' in regression_data['filter3'])
            or ('NearLowMonth6' in regression_data['filter3'])
            or ('ReversalLowYear2' in regression_data['filter3'])
            or ('ReversalLowYear' in regression_data['filter3'])
            or ('ReversalLowMonth6' in regression_data['filter3'])
            or ('BreakLowYear2' in regression_data['filter3'])
            or ('BreakLowYear' in regression_data['filter3'])
            or ('BreakLowMonth6' in regression_data['filter3'])
            )
            and regression_data['SMA200'] < regression_data['SMA100'] < regression_data['SMA50'] < regression_data['SMA25'] < regression_data['SMA9']
            and regression_data['series_trend'] == "upTrend"
            ):
    #             if(((-3 < regression_data['PCT_change'] < 0) and (-3 < regression_data['PCT_day_change'] < 0))
    #                 and regression_data['SMA4'] > 0.5
    #                 and regression_data['SMA25'] > -10
    #                 and ('[') not in regression_data['sellIndia']
    #                 ):
    #                 add_in_csv(regression_data, regressionResult, ws, '(Test)buyBottomReversal-0')
            if(((-3 < regression_data['PCT_change'] < 0) and (-3 < regression_data['PCT_day_change'] < 0))
                ):
                if(is_algo_buy(regression_data)):
                    add_in_csv(regression_data, regressionResult, ws, None)
                    return True
                return False
    #             elif(((-3 < regression_data['PCT_change'] < -1.5) and (-3 < regression_data['PCT_day_change'] < -1.5))
    #                 ):
    #                 add_in_csv(regression_data, regressionResult, ws, '##UPTREND:(Test)buyBottomReversal-2')
     
            
    #             elif(regression_data['PCT_day_change_pre2'] < 0 and (regression_data['PCT_day_change'] > 1.5)):
    #                 add_in_csv(regression_data, regressionResult, ws, '(Test)buyBottomReversal-1')
        return True

def buy_study_risingMA(regression_data, regressionResult, reg, ws):
    if(('UP-1' in regression_data['filter5'])
       ):
        add_in_csv(regression_data, regressionResult, ws,"buy-1-UP")
        return True
    elif(('UP-2' in regression_data['filter5'])
       ):
        add_in_csv(regression_data, regressionResult, ws, None)
        return True
    elif(('UP' in regression_data['filter5'])
       ):
        if((-2 < regression_data['SMA9'] < 0 or -2 < regression_data['SMA25'] < 0)
            and regression_data['SMA100'] < -10
            and regression_data['SMA200'] < -10
            and regression_data['year2HighChange'] < -50
            and regression_data['year2LowChange'] > 8
            ):
            add_in_csv(regression_data, regressionResult, ws, '(Test)sell-UP')
        elif((1 < regression_data['SMA9'] < 3 or 1 < regression_data['SMA25'] < 3)
            and regression_data['SMA100'] < -10
            and regression_data['SMA200'] < -10
            and regression_data['year2LowChange'] > 8
            ):
            add_in_csv(regression_data, regressionResult, ws, '(Test)sell-UP')
        elif((1 < regression_data['SMA9'] < 3 or 1 < regression_data['SMA25'] < 3)
            and regression_data['SMA100'] < -10
            and regression_data['SMA200'] < -10
            and regression_data['year2LowChange'] < 8
            ):
            add_in_csv(regression_data, regressionResult, ws, '(Test)buy-UP')
        return True
    elif(2.5 < regression_data['PCT_day_change'] < 7
       and 3 < regression_data['PCT_change'] < 7
       and regression_data['forecast_day_PCT_change'] > 0
       and regression_data['forecast_day_PCT2_change'] > 0
       and regression_data['PCT_day_change_pre1'] < 0.75
       and regression_data['PCT_day_change_pre2'] < 0.5
       and regression_data['PCT_day_change_pre3'] < 0
       and high_tail_pct(regression_data) < 1
       and low_tail_pct(regression_data) < 1
       #and low_tail_pct_pre1(regression_data) < 1
       and regression_data['year2HighChange'] < -5
       and regression_data['year2LowChange'] > 15
       and (('P@' not in regression_data['buyIndia']) or (regression_data['forecast_day_PCT10_change'] > 4))
       ):
        add_in_csv(regression_data, regressionResult, ws, "sell-UP")
        return True
    elif(('DOWN-2' in regression_data['filter5'])
       ):
        add_in_csv(regression_data, regressionResult, ws, None)
    elif(('DOWN-1' in regression_data['filter5'])
       ):
        add_in_csv(regression_data, regressionResult, ws, None)
    elif(('DOWN' in regression_data['filter5'])
       ):
        add_in_csv(regression_data, regressionResult, ws, None)
        
    
    
    if(('EMA6-LT-May-MT-EMA14' in regression_data['filter4'])
        and 2.5 < regression_data['PCT_day_change'] < 4
        and 0 < regression_data['PCT_change'] < 4.5
        and (regression_data['PCT_day_change'] > 3 or regression_data['PCT_change'] > 3)
        and high_tail_pct(regression_data) < 1
        ):
        add_in_csv(regression_data, regressionResult, ws, '(check-chart)mayBuy-EMA6-LT-May-MT-EMA14')
    elif(('EMA6-MT-May-LT-EMA14' in regression_data['filter4'])
        and -4 < regression_data['PCT_day_change'] < -2.5
        and -4.5 < regression_data['PCT_change'] < 0
        and (regression_data['PCT_day_change'] < -3 or regression_data['PCT_change'] < -3)
        and low_tail_pct(regression_data) < 1
        ):
        add_in_csv(regression_data, regressionResult, ws, '(check-chart)maySell-EMA6-MT-May-LT-EMA14')
        
        
    if(('$$(Confirmed)$$:EMA6>EMA14' in regression_data['filter4'])
        and 2.5 < regression_data['PCT_day_change'] 
        and 0 < regression_data['PCT_change']
        and (regression_data['PCT_day_change'] > 3 or regression_data['PCT_change'] > 3)
        and ((regression_data['PCT_day_change_pre1'] > 1 and regression_data['PCT_day_change_pre2'] > 1)
             or (regression_data['PCT_day_change_pre1'] > 2 and regression_data['PCT_day_change_pre3'] > 1)
             or (regression_data['PCT_day_change_pre1'] > 1 and regression_data['PCT_day_change_pre2'] > 1 and regression_data['PCT_day_change_pre3'] > 1)
             )
        ):
        add_in_csv(regression_data, regressionResult, ws, '(check-chart)EMA6>EMA14:maySell-HighUpside')
        return True
    elif(('$$(Confirmed)$$:EMA6>EMA14' in regression_data['filter4'])
        and 2.5 < regression_data['PCT_day_change'] < 6
        and 0 < regression_data['PCT_change']
        and (regression_data['PCT_day_change'] > 3 or regression_data['PCT_change'] > 3)
        and ((regression_data['PCT_day_change_pre1'] < 0 and regression_data['PCT_day_change_pre2'] < 0)
             )
        ):
        add_in_csv(regression_data, regressionResult, ws, '(check-chart)EMA6>EMA14:maySell-LowUpside')
        return True
    elif(('$$(Confirmed)$$:EMA6>EMA14' in regression_data['filter4'])
        and 2.5 < regression_data['PCT_day_change'] < 6
        and 0 < regression_data['PCT_change']
        and (regression_data['PCT_day_change'] > 3 or regression_data['PCT_change'] > 3)
        and (regression_data['PCT_day_change_pre1'] < 1 and regression_data['PCT_day_change_pre2'] < 1)
        and regression_data['forecast_day_PCT10_change'] < 5
        ):
        add_in_csv(regression_data, regressionResult, ws, '(check-chart)EMA6>EMA14:mayBuy-LowUpside')
        return True
    elif(('$$(Confirmed)$$:EMA6>EMA14' in regression_data['filter4'])
        and 2.5 < regression_data['PCT_day_change'] 
        and 0 < regression_data['PCT_change']
        and (regression_data['PCT_day_change'] > 3 or regression_data['PCT_change'] > 3)
        ):
        add_in_csv(regression_data, regressionResult, ws, '(check-chart)EMA6>EMA14')
        return True
    
    if('$$(Study)$$:RisingMA' in regression_data['filter4']
        ):
        if(-2.5 < regression_data['PCT_day_change'] < 0 and -2.5 < regression_data['PCT_change'] < 0
            and (regression_data['SMA50'] < 0 and regression_data['SMA25'] > 10 and regression_data['SMA4'] > 0)
            ):
            add_in_csv(regression_data, regressionResult, ws, "sellSMA25GT10")
        if(-4 < regression_data['PCT_day_change'] < -0.5
           and -4 < regression_data['PCT_change']
           and 5 > low_tail_pct(regression_data) > 2.5
           and high_tail_pct(regression_data) < 0.6
           and (low_tail_pct(regression_data) - high_tail_pct(regression_data)) > 1
           ):
            add_in_csv(regression_data, regressionResult, ws, None)
            return True
        elif(-4 < regression_data['PCT_day_change'] < -0.5
           and -4 < regression_data['PCT_change']
           and 5 > low_tail_pct(regression_data) > 2.5
           and high_tail_pct(regression_data) < 2
           and (low_tail_pct(regression_data) - high_tail_pct(regression_data)) > 0.8
           ):
            add_in_csv(regression_data, regressionResult, ws, "##RisingMA(check-chart-buy)-MayBuyCheckChart")
            return True
        elif(0.5 < regression_data['PCT_day_change'] < 4
           and regression_data['PCT_change'] < 4
           and low_tail_pct(regression_data) < 0.6
           and 5 > high_tail_pct(regression_data) > 2.5
           and (high_tail_pct(regression_data) - low_tail_pct(regression_data)) > 0.8
           ):
            add_in_csv(regression_data, regressionResult, ws, "##RisingMA(check-chart-sell)-MaySellCheckChart")
            return True
        elif(0.5 < regression_data['PCT_day_change'] < 4
           and regression_data['PCT_change'] < 4
           and low_tail_pct(regression_data) < 2
           and 5 > high_tail_pct(regression_data) > 2.5
           and (high_tail_pct(regression_data) - low_tail_pct(regression_data)) > 0.8
           ):
            add_in_csv(regression_data, regressionResult, ws, None)
            return True
        elif(0.5 < regression_data['PCT_day_change'] < 4
           and regression_data['PCT_day_change_pre1'] < 0
           and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change'])
           and ((regression_data['forecast_day_PCT_change'] < 0)
                #or (regression_data['open'] > regression_data['close_pre'])
                )
           and high_tail_pct(regression_data) < 1
           ):
            add_in_csv(regression_data, regressionResult, ws, "##RisingMA(Test)(check-chart-buy)-1DayUp")
            return True
        elif(0.5 < regression_data['PCT_day_change'] < 4
           and 0.5 < regression_data['PCT_day_change_pre1'] < 4
           and regression_data['PCT_day_change_pre2'] < 0
           and regression_data['PCT_day_change_pre3'] < 0
           and abs(regression_data['PCT_day_change_pre2']) > abs(regression_data['PCT_day_change_pre1'])
           and regression_data['forecast_day_PCT_change'] > 0
           and high_tail_pct(regression_data) < 1
           ):
            add_in_csv(regression_data, regressionResult, ws, "##RisingMA(Test)(check-chart-buy)-2DayUp")
            return True
        elif(0 < regression_data['PCT_day_change'] < 1.5
           and regression_data['PCT_day_change_pre1'] < -2
           and (regression_data['PCT_day_change_pre2'] < 0 
                or (regression_data['PCT_day_change_pre2'] < 1 and high_tail_pct_pre2(regression_data) > 1.5)
                )
           and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change'])
           and regression_data['forecast_day_PCT_change'] < 0
           and regression_data['forecast_day_PCT2_change'] < 0
           and regression_data['forecast_day_PCT3_change'] < 0
           and regression_data['forecast_day_PCT4_change'] < 0
           and regression_data['forecast_day_PCT5_change'] < 0
           ):
            add_in_csv(regression_data, regressionResult, ws, "##RisingMA(Test)(check-chart-sell)-1DayUp")
            return True
        
    if(regression_data['SMA9'] < 0 
       and regression_data['SMA4'] < 0
       and regression_data['forecast_day_PCT_change'] < -0.5
       and regression_data['forecast_day_PCT2_change'] < -0.5
       and regression_data['forecast_day_PCT5_change'] < -0.5
       and regression_data['forecast_day_PCT7_change'] > -10
       and abs(regression_data['PCT_day_change_pre1']) > 2* (regression_data['PCT_day_change'])
       and ((0 < regression_data['PCT_day_change'] < 1.5
               and regression_data['PCT_day_change_pre1'] < -2
               and regression_data['PCT_day_change_pre2'] < 1.5
               and regression_data['PCT_day_change_pre3'] < 1.5
               and (
                   regression_data['PCT_day_change_pre2'] < -1
                   or regression_data['PCT_day_change_pre3'] < -1
                   )
               and regression_data['forecast_day_PCT5_change'] > -5
               and high_tail_pct(regression_data) > 1
            )
            or(-1.5 < regression_data['PCT_day_change'] < 0 
                and regression_data['PCT_day_change_pre1'] < -1.5
                and (regression_data['month3LowChange'] < 0 or regression_data['month3LowChange'] > 5)
                and regression_data['yearLowChange'] > 5
                and regression_data['year2LowChange'] > 5
                and regression_data['month3HighChange'] < -15
                and (high_tail_pct(regression_data) < 1)
            )
        )
       and (low_tail_pct(regression_data) < 1.5)
       ):  
        add_in_csv(regression_data, regressionResult, ws, "##(Test)(check-chart)-SMADownTrend")
        if(0 < regression_data['PCT_day_change'] < 2
           and regression_data['PCT_day_change_pre1'] < 0
           and (regression_data['PCT_day_change_pre2'] < 0 or regression_data['PCT_day_change_pre3'] < 0)
           and (regression_data['PCT_day_change_pre2'] > 0 or regression_data['PCT_day_change_pre3'] > 0)
           and (low_tail_pct(regression_data) < 1.5)  
           ):
           add_in_csv(regression_data, regressionResult, ws, None)
        elif('P@' in regression_data['buyIndia']
           and is_algo_buy(regression_data)):
           add_in_csv(regression_data, regressionResult, ws, "##(Test)ML:buySMADownTrend")
           
        return True

def buy_random_filters(regression_data, regressionResult, reg, ws):
    if(is_algo_buy(regression_data)):
        if(2 < regression_data['PCT_day_change'] < 3
            and 1.5 < regression_data['PCT_change'] < 3.5
            and (regression_data['forecast_day_PCT7_change'] < 1)
            and (regression_data['forecast_day_PCT10_change'] < 1)
            and (regression_data['forecast_day_PCT7_change'] < 0
                or regression_data['forecast_day_PCT10_change'] < 0
                )
            and (regression_data['forecast_day_PCT_change'] > 0
                or regression_data['forecast_day_PCT2_change'] > 0
                or regression_data['forecast_day_PCT3_change'] > 0
                )
            and (((regression_data['low'] - regression_data['low_pre1'])/regression_data['low_pre1'])*100) > 0
            ):
            if(regression_data['forecast_day_PCT2_change'] > 1
                and regression_data['forecast_day_PCT3_change'] > 1
                ):
                add_in_csv(regression_data, regressionResult, ws, '(Test)checkCupUp')
            else:
                add_in_csv(regression_data, regressionResult, ws, '(Test)checkCupUp-inUpTrend')
    if(-2.5 < regression_data['PCT_day_change'] < -1
        and -3.5 < regression_data['PCT_change'] < -1
        and regression_data['PCT_day_change_pre1'] > 1.5
        and (regression_data['forecast_day_PCT5_change'] < 2)
        and (regression_data['forecast_day_PCT7_change'] < 2)
        and (regression_data['forecast_day_PCT10_change'] < 2)
        and (regression_data['forecast_day_PCT5_change'] < 0
            or regression_data['forecast_day_PCT7_change'] < 0
            or regression_data['forecast_day_PCT10_change'] < 0
            )
        and (regression_data['forecast_day_PCT2_change'] > 0
            and regression_data['forecast_day_PCT3_change'] > 0
            )
        and (((regression_data['low'] - regression_data['low_pre1'])/regression_data['low_pre1'])*100) > 0
        ):
        add_in_csv(regression_data, regressionResult, ws, '(Test)checkCupUp-lastDayDown')  
        
    if((-0.5 < regression_data['forecast_day_PCT4_change'] < 0.5
        or -0.5 < regression_data['forecast_day_PCT5_change'] < 0.5
        )
        and 
        (regression_data['forecast_day_PCT4_change'] > 1
        or regression_data['forecast_day_PCT5_change'] > 1
        )
        and regression_data['forecast_day_PCT_change'] > 1
        and regression_data['forecast_day_PCT2_change'] > 2
        and regression_data['forecast_day_PCT3_change'] > 3
#         and regression_data['forecast_day_PCT7_change'] > 3
#         and regression_data['forecast_day_PCT10_change'] > 3
        and regression_data['PCT_day_change'] > 1
        and regression_data['PCT_day_change_pre1'] > 1
        and regression_data['PCT_day_change_pre2'] > 1
        ):
        add_in_csv(regression_data, regressionResult, ws, '(Test)buyMay5DayCeilReversal')

def buy_test(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    flag = buy_other_indicator(regression_data, regressionResult, reg, ws)
    return flag
    
    
    return False    

def buy_oi_candidate(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    tail_pct_filter(regression_data, regressionResult)
    tail_reversal_filter(regression_data, regressionResult)
    flag = False
    
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

def buy_all_filter(regression_data, regressionResult, reg, ws):
    flag = False
    if buy_year_high(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws, None)
        flag = True
    if buy_year_low(regression_data, regressionResult, reg, None, None):
        add_in_csv(regression_data, regressionResult, ws, None)
        flag = True
    if buy_up_trend(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws, None)
        flag = True
    if buy_down_trend(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws, None)
        flag = True
    if buy_final(regression_data, regressionResult, reg, None, None):
        add_in_csv(regression_data, regressionResult, ws, None)
        flag = True
    if buy_high_indicators(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws, None)
        flag = True
    if buy_pattern(regression_data, regressionResult, reg, None, None):
        add_in_csv(regression_data, regressionResult, ws, None)
        flag = True
    if buy_oi(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws, None)
        flag = True
    return flag

def buy_filter_accuracy(regression_data, regressionResult, reg, ws):
    filtersDict=scrip_patterns_to_dict('../../data-import/nselist/filter-buy.csv')
    if regression_data['filter'] != '':
        filter = regression_data['filter'].replace("[MLBuy]:", "").replace("[MLSell]:", "").strip()
        if filter != '' and filter in filtersDict:
            regression_data['filter_avg'] = float(filtersDict[filter]['avg'])
            regression_data['filter_count'] = float(filtersDict[filter]['count'])
            
def sell_pattern_without_mlalgo(regression_data, regressionResult):
    if(regression_data['PCT_day_change'] > -3.5
        and regression_data['year2HighChange'] < -5):
        if(regression_data['sellIndia_avg'] < -1.8):
            add_in_csv(regression_data, regressionResult, None, 'maySellFromSellPattern-LT-1.8')
        if(regression_data['sellIndia_avg'] < -0.9 and regression_data['sellIndia_count'] > 1
            and (regression_data['SMA9'] < 0 or regression_data['SMA4'] < -1.5)
            ):
            if(regression_data['SMA9'] < 0):
                add_in_csv(regression_data, regressionResult, None, '(SMA9LT0)')
            elif(regression_data['SMA4'] < -1.5):
                add_in_csv(regression_data, regressionResult, None, '(SMA4LT(-1.5))')
            if(regression_data['yearHighChange'] < -10 and regression_data['sellIndia_count'] > 1):
                if(regression_data['sellIndia_avg'] < -1.5):
                    add_in_csv(regression_data, regressionResult, None, 'sellPatterns-LT-1.5-SMALT0')
                elif(regression_data['sellIndia_avg'] < -0.9
                    ):
                    add_in_csv(regression_data, regressionResult, None, 'sellPatterns-Risky-LT-0.9-SMALT0')   
                    
    if(regression_data['PCT_day_change'] > -3.5
        and regression_data['year2HighChange'] < -5
        and regression_data['year2LowChange'] > 5):
        if(regression_data['sellIndia_avg'] > 1.8):
            add_in_csv(regression_data, regressionResult, None, 'mayBuyFromSellPattern-GT1.8')
        if(regression_data['sellIndia_avg'] > 0.9 and regression_data['sellIndia_count'] > 1
            and (regression_data['SMA9'] > 0 or regression_data['SMA4'] > 1.5)
            ):
            if(regression_data['SMA9'] > 0):
                add_in_csv(regression_data, regressionResult, None, '(SMA9GT0)')
            elif(regression_data['SMA4'] > 1.5):
                add_in_csv(regression_data, regressionResult, None, '(SMA4GT(1.5))')
            if(regression_data['yearLowChange'] < -10 and regression_data['sellIndia_count'] > 1):
                if(regression_data['sellIndia_avg'] > 1.5):
                    add_in_csv(regression_data, regressionResult, None, 'buyPatterns-GT1.5-SMAGT0')
                elif(regression_data['sellIndia_avg'] > 0.9
                    ):
                    add_in_csv(regression_data, regressionResult, None, 'buyPatterns-Risky-GT0.9-SMAGT0')                          
            #add_in_csv(regression_data, regressionResult, None, 'buyPatterns-1-Risky')   
#     sellPatternsDict=scrip_patterns_to_dict('../../data-import/nselist/all-buy-filter-by-PCT-Change.csv')
#     if regression_data['sellIndia'] != '' and regression_data['sellIndia'] in sellPatternsDict:
#         if (abs(float(sellPatternsDict[regression_data['sellIndia']]['avg'])) >= .1 and float(sellPatternsDict[regression_data['sellIndia']]['count']) >= 2):
#             if(-3 < regression_data['PCT_day_change'] < 0.5 and float(sellPatternsDict[regression_data['sellIndia']]['avg']) < -1):
#                 avg = sellPatternsDict[regression_data['sellIndia']]['avg']
#                 count = sellPatternsDict[regression_data['sellIndia']]['count']
#                 #add_in_csv_hist_pattern(regression_data, regressionResult, ws, 'wml_sell', avg, count)
#             if(-0.5 < regression_data['PCT_day_change'] < 3 and float(sellPatternsDict[regression_data['sellIndia']]['avg']) > 1): 
#                 avg = sellPatternsDict[regression_data['sellIndia']]['avg']
#                 count = sellPatternsDict[regression_data['sellIndia']]['count']
#                 #add_in_csv_hist_pattern(regression_data, regressionResult, ws2, 'wml_sell', avg, count)

def sell_study_downingMA(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
        
    if(regression_data['SMA9'] > 0 
       and regression_data['SMA4'] > 0
       and regression_data['forecast_day_PCT_change'] > 0.5
       and regression_data['forecast_day_PCT2_change'] > 0.5
       and regression_data['forecast_day_PCT5_change'] > 0.5
       and regression_data['forecast_day_PCT7_change'] < 10
       and abs(regression_data['PCT_day_change_pre1']) > 2* (regression_data['PCT_day_change'])
       and ((-1.5 < regression_data['PCT_day_change'] < 0
               and regression_data['PCT_day_change_pre1'] > 2
               and regression_data['PCT_day_change_pre2'] > -1.5
               and regression_data['PCT_day_change_pre3'] > -1.5
               and (
                   regression_data['PCT_day_change_pre2'] > 1
                   or regression_data['PCT_day_change_pre3'] > 1
                   )
               and regression_data['forecast_day_PCT5_change'] < 5
               and low_tail_pct(regression_data) > 1
            )
            or (0 < regression_data['PCT_day_change'] < 1.5
                and regression_data['PCT_day_change_pre1'] > 1.5
                and regression_data['yearHighChange'] < -5
                and regression_data['year2HighChange'] < -5
                and (regression_data['month3HighChange'] > 0 or regression_data['month3HighChange'] < -5)
                and regression_data['month3LowChange'] > 15
                and low_tail_pct(regression_data) < 1
            )
        )
       and (high_tail_pct(regression_data) < 1.5)
       ):  
       add_in_csv(regression_data, regressionResult, ws, "##(Test)(check-chart)-SMAUpTrend")
       if('P@' in regression_data['sellIndia']
           and is_algo_sell(regression_data)):
           add_in_csv(regression_data, regressionResult, ws, "##(Test)ML:sellSMAUpTrend")
       return True

def sell_pattern_from_history(regression_data, ws):
    sellPatternsDict=scrip_patterns_to_dict('../../data-import/nselist/patterns-sell.csv')
    sellIndiaAvg = 0
    regression_data['buyIndia_avg'] = 0
    regression_data['buyIndia_count'] = 0
    regression_data['sellIndia_avg'] = 0
    regression_data['sellIndia_count'] = 0
    regression_data['filter_avg'] = 0
    regression_data['filter_count'] = 0
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
                        #add_in_csv_hist_pattern(regression_data, regressionResult, ws, 'sellPattern2', avg, count) 
                    if(float(sellPatternsDict[regression_data['sellIndia']]['avg']) < -0.5 
                        or (float(sellPatternsDict[regression_data['sellIndia']]['avg']) < -0.3 and (ten_days_more_than_ten(regression_data) or regression_data['yearLowChange'] > 40))):
                        if(regression_data['forecast_day_PCT10_change'] > 0 and regression_data['forecast_day_PCT_change'] <= 0):
                            flag = True
                            #add_in_csv_hist_pattern(regression_data, regressionResult, ws, 'sellPattern2', avg, count)
                        elif(regression_data['forecast_day_PCT10_change'] < 0):    
                            flag = True
                            #add_in_csv_hist_pattern(regression_data, regressionResult, ws, 'sellPattern2', avg, count)
    return sellIndiaAvg, flag

def sell_all_rule(regression_data, regressionResult, sellIndiaAvg, ws):
    if(is_algo_sell(regression_data)
        and sellIndiaAvg <= 0.70
        and ((last_7_day_all_down(regression_data) == False) or (regression_data['forecast_day_PCT10_change'] > -10))
        and (MARKET_IN_DOWNTREND or (last_4_day_all_down(regression_data) == False)) #Uncomment0 If very less data
        and breakout_or_no_consolidation(regression_data) == True
        and '$$(Confirmed)$$:EMA6<EMA14' not in regression_data['filter4']
        and regression_data['close'] > 50
        and low_tail_pct(regression_data) < 1
        and high_tail_pct(regression_data) > 1.2
        and regression_data['low'] < regression_data['low_pre1']
        ):
        if(regression_data['PCT_day_change'] > 0.75 and regression_data['PCT_change'] > 0
            and regression_data['month3LowChange'] > 15  
            ):
            add_in_csv(regression_data, regressionResult, None, 'ML:sell-0')
    elif(is_algo_buy(regression_data)):
        if(-5 < regression_data['PCT_day_change'] < -2
            and -5 < regression_data['PCT_change'] < -2
            and low_tail_pct(regression_data) > 1.5
            and high_tail_pct(regression_data) < 1
            ):
            add_in_csv(regression_data, regressionResult, None, 'ML:buy-1')
    
    if(is_algo_sell(regression_data, True)
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
        and '$$(Confirmed)$$:EMA6<EMA14' not in regression_data['filter4']
        and regression_data['close'] > 50
        ):
        add_in_csv(regression_data, regressionResult, ws, None)
        return True
    return False

def sell_all_rule_classifier(regression_data, regressionResult, sellIndiaAvg, ws):
    if(is_algo_sell_classifier(regression_data, True)
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
        and '$$(Confirmed)$$:EMA6<EMA14' not in regression_data['filter4']
        and regression_data['close'] > 50
        ):
        add_in_csv(regression_data, regressionResult, ws, None)
        return True
    return False

def sell_all_common(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, True)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, True)
    mlpValue_cla, kNeighboursValue_cla = get_reg_or_cla(regression_data, False)
    mlpValue_other_cla, kNeighboursValue_other_cla = get_reg_or_cla_other(regression_data, False)
    
    if((regression_data['PCT_day_change'] > -3)
       and ((regression_data['PCT_day_change'] < -1
           and -6 < mlpValue_other <= -2
           and -6 < kNeighboursValue_other <= -2
           and -6 < mlpValue_other_cla <= -2
           and -6 < kNeighboursValue_other_cla <= -2
           and -6 < mlpValue_cla <= 0
           and -6 < kNeighboursValue_cla <= 0)
       )):
        add_in_csv(regression_data, regressionResult, ws, '##Common:(Test)HighIndicators-0')
    elif((regression_data['PCT_day_change'] > -3)
       and ((regression_data['PCT_day_change'] < -2
           and -6 < mlpValue_other < -1 
           and -6 < kNeighboursValue_other <= -1
           and -6 < mlpValue_other_cla <= -2
           and -6 < kNeighboursValue_other_cla <= -2
           and -6 < mlpValue_cla <= -2
           and -6 < kNeighboursValue_cla <= -2)
       )):
        add_in_csv(regression_data, regressionResult, ws, '##Common:(Test)HighIndicators-1')
    
#     if(is_algo_sell(regression_data)):
#         if('P@' not in regression_data['buyIndia']):
#             add_in_csv(regression_data, regressionResult, ws, '##Common:sellDayReversalCandidate-0')
#         else:
#             add_in_csv(regression_data, regressionResult, ws, '##Common:sellDayReversalCandidate-1')
    
    if(is_algo_sell(regression_data)
        and (-4 < regression_data['PCT_day_change'] < -2) and (-4 < regression_data['PCT_change'] < -2)
        and ((regression_data['PCT_day_change_pre1'] > 0 and regression_data['forecast_day_PCT_change'] < 0)
            )
        and regression_data['forecast_day_PCT2_change'] < 0
        and regression_data['forecast_day_PCT3_change'] < 0
        #and regression_data['forecast_day_PCT10_change'] > -15
        and regression_data['month3HighChange'] < -10
        and regression_data['month3LowChange'] > 10
        #and regression_data['trend'] != 'down'
        ):    
        if(regression_data['SMA9'] < -1):
            add_in_csv(regression_data, regressionResult, ws, '##Common:sellNotM3HighLow-0(SMA9LT-1)') 
        elif(regression_data['SMA25'] < 0):
            add_in_csv(regression_data, regressionResult, ws, '##(Test):sellNotM3HighLow-0(SMA25LT0)') 
        else:
            add_in_csv(regression_data, regressionResult, ws, None) 
    
    if(is_algo_sell(regression_data)
        and (-3 < regression_data['PCT_day_change'] < -2) and (-4 < regression_data['PCT_change'] < -2)
        and ((regression_data['PCT_day_change_pre1'] > 0 and regression_data['forecast_day_PCT_change'] < 0)
             or regression_data['PCT_day_change_pre2'] > 0
            )
        and regression_data['forecast_day_PCT2_change'] < 0
        and regression_data['forecast_day_PCT3_change'] < 0
        and regression_data['forecast_day_PCT4_change'] < -1
        #and regression_data['forecast_day_PCT10_change'] > -15
        and regression_data['month3HighChange'] < -3
        and regression_data['month3LowChange'] > 3
        and regression_data['yearHighChange'] < -10
        and regression_data['yearLowChange'] > 10
        #and regression_data['trend'] != 'down'
        and abs_month3High_more_than_month3Low(regression_data)
        ):    
        if(regression_data['SMA9'] < -1):
            add_in_csv(regression_data, regressionResult, ws, '##Common:sellNotM3HighLow-1(SMA9LT-1)') 
        elif(regression_data['SMA25'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None) 
        else:
            add_in_csv(regression_data, regressionResult, ws, None)
            
    if(ten_days_more_than_ten(regression_data)
        and regression_data['forecast_day_PCT2_change'] > 0
        and regression_data['forecast_day_PCT3_change'] > 0
        and regression_data['forecast_day_PCT5_change'] > 0
        and regression_data['forecast_day_PCT7_change'] > 0
        and regression_data['forecast_day_PCT7_change'] > 0
        and regression_data['PCT_day_change'] < -2
        and regression_data['PCT_change'] < -2
        and regression_data['PCT_day_change_pre2'] > 0
        and regression_data['PCT_day_change_pre3'] > 0
        ):
        add_in_csv(regression_data, regressionResult, ws, '##Common:Breakdown-tenDaysMoreThanTen')
                         
#     if(-4 < regression_data['PCT_change'] < 1
#         and (last_7_day_all_down(regression_data) == False)
#         and (MARKET_IN_DOWNTREND or (last_4_day_all_down(regression_data) == False)) #Uncomment0 If very less data
#         and low_tail_pct(regression_data) < 1
#         ):
#         return True
    
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

def sell_other_indicator(regression_data, regressionResult, reg, ws):
    tail_pct_filter(regression_data, regressionResult)
    base_line(regression_data, regressionResult, reg, ws)
    filterMA(regression_data, regressionResult)
    tail_reversal_filter(regression_data, regressionResult)
    if(regression_data['close'] > 50
        ):
        sell_tail_reversal_filter(regression_data, regressionResult, reg, ws)
        sell_up_trend(regression_data, regressionResult, reg, ws)
        sell_down_trend(regression_data, regressionResult, reg, ws)
        sell_final(regression_data, regressionResult, reg, ws, ws)
        sell_high_indicators(regression_data, regressionResult, reg, ws)
        sell_pattern(regression_data, regressionResult, reg, ws, ws)
        sell_base_line_buy(regression_data, regressionResult, reg, ws)
        sell_morning_star_buy(regression_data, regressionResult, reg, ws)
        sell_evening_star_sell(regression_data, regressionResult, reg, ws)
        sell_oi_negative(regression_data, regressionResult, reg, ws)
        sell_day_high(regression_data, regressionResult, reg, ws)
        sell_vol_contract(regression_data, regressionResult, reg, ws)
        sell_vol_contract_contrarian(regression_data, regressionResult, reg, ws)
        sell_trend_reversal(regression_data, regressionResult, reg, ws)
        sell_trend_break(regression_data, regressionResult, reg, ws)
        sell_consolidation_breakdown(regression_data, regressionResult, reg, ws)
        sell_final_candidate(regression_data, regressionResult, reg, ws)
        sell_oi(regression_data, regressionResult, reg, ws)
        sell_downingMA(regression_data, regressionResult, reg, ws)
        sell_study_downingMA(regression_data, regressionResult, reg, ws)
        sell_market_downtrend(regression_data, regressionResult, reg, ws)
        sell_supertrend(regression_data, regressionResult, reg, ws)
        sell_heavy_downtrend(regression_data, regressionResult, reg, ws)
        sell_check_chart(regression_data, regressionResult, reg, ws)
        sell_random_filter(regression_data, regressionResult, reg, ws)
        return True
    return False

def sell_tail_reversal_filter(regression_data, regressionResult, reg, ws):
    if('MaySell-CheckChart' in regression_data['filter1']):
        if(regression_data['PCT_day_change_pre1'] < -2
            and regression_data['PCT_day_change_pre2'] > 0
            and is_ema14_sliding_down(regression_data)
            and (last_5_day_all_down_except_today(regression_data) != True)
            and regression_data['bar_high'] <  regression_data['bar_high_pre1']
            and regression_data['high'] <  regression_data['high_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, 'MaySell-CheckChart(downTrend-lastDayUp)')
    if(('MaySell-CheckChart' in regression_data['filter1']) or ('MaySellCheckChart' in regression_data['filter1'])):
        if(1 < regression_data['PCT_day_change'] < 3.5
            and 1 < regression_data['PCT_change'] < 3.5
            and 1 < regression_data['PCT_day_change_pre1'] 
            and regression_data['monthHighChange'] > -1
            and high_tail_pct(regression_data) < 2.5
            #and regression_data['PCT_day_change_pre3'] < regression_data['PCT_day_change']
            ):
            add_in_csv(regression_data, regressionResult, ws, 'MaySell-CheckChart(monthHigh-minimumLast2DayUp)')
    
    if(is_algo_buy(regression_data)):        
        if(('MaySellCheckChart' in regression_data['filter1'])
            and ('Reversal' not in regression_data['filter3'])
            and regression_data['year2LowChange'] > 10
            and low_tail_pct(regression_data) < 0.5
            ):
            if(((1 < regression_data['PCT_day_change'] <= 2) and (0 < regression_data['PCT_change'] <= 2))
                and 3 > high_tail_pct(regression_data) > 1.8
                and regression_data['PCT_day_change_pre1'] > 0
                and regression_data['PCT_day_change_pre2'] > 0
                and regression_data['PCT_day_change_pre3'] > 0
                ):
                add_in_csv(regression_data, regressionResult, ws, "##ML:MaySellCheckChart-last3DayUp")
            elif(((1 < regression_data['PCT_day_change'] <= 2) and (0 < regression_data['PCT_change'] <= 2))
                and 3 > high_tail_pct(regression_data) > 1.8):
                add_in_csv(regression_data, regressionResult, ws, "##ML:(check-chart-2-3MidCapCross)MaySellCheckChart-1")
    elif(('MaySellCheckChart' in regression_data['filter1'])
        and ('Reversal' not in regression_data['filter3'])
        and regression_data['year2LowChange'] > 10
        and low_tail_pct(regression_data) < 0.5
        ):
        if((3 < regression_data['PCT_day_change'] <= 5) and (2 < regression_data['PCT_change'] <= 6)
            and 5 > high_tail_pct(regression_data) > 2.8
            ):
            add_in_csv(regression_data, regressionResult, ws, "##ML:(Test)MaySellCheckChart--PCTDayChangeGT(3)BigLowTail")

def sell_year_high(regression_data, regressionResult, reg, ws, ws1):
    return False
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(-10 < regression_data['yearHighChange'] < -1 and regression_data['yearLowChange'] > 30 and -5 < regression_data['PCT_day_change'] < -0.75 
        and ten_days_more_than_ten(regression_data) and regression_data['forecast_day_PCT7_change'] > 5 and regression_data['forecast_day_PCT5_change'] > -0.5 and regression_data['forecast_day_PCT4_change'] > -0.5
        and regression_data['forecast_day_PCT2_change'] < 0 and regression_data['forecast_day_PCT_change'] < 0
        and float(regression_data['forecast_day_VOL_change']) > 0
        ):
        add_in_csv(regression_data, regressionResult, ws, 'sellYearHigh')
        return True
    elif(-10 < regression_data['yearHighChange'] < 0 and regression_data['yearLowChange'] > 30 
        and (regression_data['PCT_day_change'] < 0 and regression_data['PCT_change'] < 0.5)
        and regression_data['forecast_day_PCT10_change'] > 5 and regression_data['forecast_day_PCT7_change'] > 3 and regression_data['forecast_day_PCT5_change'] > -0.5
        and regression_data['forecast_day_PCT2_change'] < 0 and regression_data['forecast_day_PCT_change'] < 0
        and float(regression_data['forecast_day_VOL_change']) > 0
        ):
        add_in_csv(regression_data, regressionResult, ws1, 'sellYearHigh1')
        return True
    elif(-10 < regression_data['yearHighChange'] < 0 and regression_data['yearLowChange'] > 30 
        and (regression_data['PCT_day_change'] < 0 and regression_data['PCT_change'] < 0.5)
        and regression_data['forecast_day_PCT10_change'] > 0 and regression_data['forecast_day_PCT7_change'] > 0 and regression_data['forecast_day_PCT5_change'] > 0
        and regression_data['forecast_day_PCT2_change'] < 0 and regression_data['forecast_day_PCT_change'] < 0
        and float(regression_data['forecast_day_VOL_change']) > 0
        ):
        add_in_csv(regression_data, regressionResult, ws1, 'sellYearHigh1')
        return True   
    return False

def sell_year_low(regression_data, regressionResult, reg, ws):
    return False
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(0 < regression_data['yearLowChange'] < 2 and regression_data['yearHighChange'] < -30 
        and -2 < regression_data['PCT_day_change'] < 0 and regression_data['forecast_day_PCT_change'] < 0
        and (str(regression_data['score']) != '1-1' or str(regression_data['score']) != '10')
        and all_day_pct_change_negative(regression_data) and no_doji_or_spinning_sell_india(regression_data)
        and float(regression_data['forecast_day_VOL_change']) > 30
        and regression_data['PCT_day_change_pre1'] < 0.5
        ):
        add_in_csv(regression_data, regressionResult, ws, 'sellYearLow')
        return True
    return False

def sell_up_trend(regression_data, regressionResult, reg, ws):
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
            add_in_csv(regression_data, regressionResult, ws, 'sellUpTrend-0(Risky)')
            return True
        elif(last_5_day_all_up_except_today(regression_data)
            and ten_days_more_than_seven(regression_data)
            and regression_data['forecast_day_PCT7_change'] > 4
            and regression_data['forecast_day_PCT10_change'] > 4
            ):
            add_in_csv(regression_data, regressionResult, ws, 'sellUpTrend-1')
            return True
        elif(regression_data['forecast_day_PCT7_change'] > 4
            and regression_data['forecast_day_PCT10_change'] > 4
            ):
            add_in_csv(regression_data, regressionResult, ws, 'sellUpTrend-2(Risky)')
            return True
    return False

def sell_down_trend(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(regression_data['forecast_day_PCT10_change'] < -10
        and regression_data['year2HighChange'] < -60
        and regression_data['month3LowChange'] < 10
        and (regression_data['forecast_day_PCT_change'] >= -1.5)
        and 3 < regression_data['PCT_day_change'] < 7
        and 2 < regression_data['PCT_change'] < 8
        and (regression_data['PCT_day_change_pre1'] < -4 or regression_data['PCT_day_change_pre2'] < -4)
        ):
        add_in_csv(regression_data, regressionResult, ws, 'sellYear2LowContinue')
        return True
    return False
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
        add_in_csv(regression_data, regressionResult, ws, '##Test:longDownTrend-Risky-IndexNotDownLastDay(checkBase)')
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

def sell_high_indicators(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    if(mlpValue < -3 and mlpValue_other < -3
        and regression_data['PCT_day_change'] < -5
        and regression_data['PCT_change'] < -5
        ):
        if(-35 < regression_data['forecast_day_PCT10_change'] < -10):
            add_in_csv(regression_data, regressionResult, ws, '##sellHighMLP-StockDowntrend(Risky)')
        elif(regression_data['forecast_day_PCT10_change'] > -10
            and -10 < regression_data['PCT_day_change'] < -5
            and -10 < regression_data['PCT_day_change'] < -5
            ):
            add_in_csv(regression_data, regressionResult, ws, '##sellHighMLP(Risky)')
    if(kNeighboursValue < -3 and kNeighboursValue_other < -3
        and mlpValue < -2 and mlpValue_other < -2
        and regression_data['PCT_day_change'] < -5
        and regression_data['PCT_change'] < -5
        ):
        if (-35 < regression_data['forecast_day_PCT10_change'] < -10):
            add_in_csv(regression_data, regressionResult, ws, '##sellHighKNeighbours-StockDowntrend(Risky)')
        elif(regression_data['forecast_day_PCT10_change'] > -10
            and -10 < regression_data['PCT_day_change'] < -5
            and -10 < regression_data['PCT_day_change'] < -5
            ):
            add_in_csv(regression_data, regressionResult, ws, '##sellHighKNeighbours(Risky)')
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
            add_in_csv(regression_data, regressionResult, ws, 'sellHighIndicators')
            return True
        if(-1 < regression_data['PCT_day_change'] < 0.5 and -2.5 < regression_data['PCT_change'] < 0.5):
            #add_in_csv(regression_data, regressionResult, ws, '(longUpTrend)sellHighIndicators')
            add_in_csv(regression_data, regressionResult, ws, None)
            return True         
    return False

def sell_pattern(regression_data, regressionResult, reg, ws, ws1):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    sell_pattern_without_mlalgo(regression_data, regressionResult)
    if(regression_data['yearHighChange'] < -10):
        if(is_algo_sell(regression_data)
            and regression_data['sellIndia_avg'] < -1.5 
            and low_tail_pct(regression_data) < 1.5
            ):
            add_in_csv(regression_data, regressionResult, ws, 'sellPatternsML')
            return True
    
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
            add_in_csv(regression_data, regressionResult, ws, 'buyMorningStar-dayDown')
            return True
        if(0.3 < regression_data['PCT_day_change'] < 1
            and (regression_data['open'] - regression_data['low']) >= ((regression_data['open'] - regression_data['close']) * 3)
            and (regression_data['open'] - regression_data['low']) >= ((regression_data['high'] - regression_data['close']) * 3)
            and 2 < low_tail_pct(regression_data) < 3.5
            ):
            if(is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, 'ML:buyMorningStar-Risky-dayUp')
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
            add_in_csv(regression_data, regressionResult, ws, 'sellMorningStar-dayUp')
            return True
#         if(high_tail_pct(regression_data) < 1.5
#            and low_tail_pct(regression_data) > 1.5
#            ):
#             if(0 < regression_data['PCT_day_change'] < 1 and 0 < regression_data['PCT_change'] < 1 
#                 and kNeighboursValue >= 0
#                 ):
#                 add_in_csv(regression_data, regressionResult, ws, '##buyMorningStar-0-NotUpSecondHalfAndUp2to3')
#                 return True
#             if(-1.5 < regression_data['PCT_day_change'] < 0 and -1.5 < regression_data['PCT_change'] < 0
#                 and (regression_data['close'] - regression_data['low']) >= ((regression_data['open'] - regression_data['close']) * 3)
#                 and (regression_data['close'] - regression_data['low']) >= ((regression_data['high'] - regression_data['open']) * 3)
#                 ):
#                 add_in_csv(regression_data, regressionResult, ws, '##buyMorningStar-1-NotUpSecondHalfAndUp2to3')
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
                add_in_csv(regression_data, regressionResult, ws, 'buyEveningStar-0(Buy-After-1pc-down)')
                return True
            else:
                add_in_csv(regression_data, regressionResult, ws, 'sellEveningStar-0')
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
                    add_in_csv(regression_data, regressionResult, ws, 'ML:sellEveningStar-2(Check2-3MidCapCross)')
                    return True
                return False
        elif((low_tail_pct(regression_data) < 0.5 or (regression_data['forecast_day_PCT_change'] > 6 and low_tail_pct(regression_data) < 1))
            and 2 < high_tail_pct(regression_data) < 3.5
            and low_tail_pct(regression_data) < 0.5
            ):
            if(2 > regression_data['PCT_day_change'] > 0.5 and 2 > regression_data['PCT_change'] > 0
                ):
                if(is_algo_sell(regression_data)):
                    add_in_csv(regression_data, regressionResult, ws, 'ML:sellEveningStar-Risky-3(Check2-3MidCapCross)')
                    return True
                return False
#         if(low_tail_pct(regression_data) < 1.5
#             and high_tail_pct(regression_data) > 2
#             ):
#             if(1.5 > regression_data['PCT_day_change'] > 0 and 1.5 > regression_data['PCT_change'] > 0
#                 and (regression_data['high']-regression_data['close']) >= ((regression_data['close']-regression_data['open'])*3)
#                 and (regression_data['high']-regression_data['close']) >= ((regression_data['open']-regression_data['low'])*3)
#                 ):
#                 add_in_csv(regression_data, regressionResult, ws, '##TEST:sellEveningStar-3(Check2-3MidCapCross)')
#                 return True
#             if(0 > regression_data['PCT_day_change'] > -1
#                 and (regression_data['high']-regression_data['open']) >= ((regression_data['open']-regression_data['close'])*3)
#                 and (regression_data['high']-regression_data['open']) >= ((regression_data['close']-regression_data['low'])*3)
#                 ):
#                 add_in_csv(regression_data, regressionResult, ws, '##TEST:sellEveningStar-4(Check2-3MidCapCross)')
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
            add_in_csv(regression_data, regressionResult, ws, 'sellDayHighVolLow-0')
            return True
        elif((regression_data['PCT_day_change'] > 5 or regression_data['PCT_change'] > 5)
           and float(regression_data['forecast_day_VOL_change']) < -20
           and regression_data['PCT_day_change'] > regression_data['PCT_day_change_pre1'] > 0
           and regression_data['PCT_day_change_pre1'] > 1
           and regression_data['forecast_day_PCT_change'] > 4
           and regression_data['yearLowChange'] < 80
           ):
            add_in_csv(regression_data, regressionResult, ws, 'buyDayHighVolLow-0')
            return True
        elif((regression_data['PCT_day_change'] > 5 and regression_data['PCT_change'] > 4)
           and float(regression_data['forecast_day_VOL_change']) < -20
           and regression_data['PCT_day_change'] > regression_data['PCT_day_change_pre1'] > 0
           and regression_data['PCT_day_change_pre1'] > 1.5
           and regression_data['month3LowChange'] < 30
           ):
            add_in_csv(regression_data, regressionResult, ws, 'sellDayHighVolLow-01-checkMorningTrend(.5SL)')
            return True
#         elif((regression_data['PCT_day_change'] > 3 and regression_data['PCT_change'] > 3) 
#            and abs_yearHigh_more_than_yearLow(regression_data)
#            and float(regression_data['forecast_day_VOL_change']) < -50  
#            and regression_data['PCT_day_change'] > regression_data['PCT_day_change_pre1'] > 0
#            and regression_data['PCT_day_change_pre2'] < -1
#            ):
#             add_in_csv(regression_data, regressionResult, ws, 'sellDayHighVolLow-1-checkMorningTrend(.5SL)-NotYearHigh')
#             return True
#     if((regression_data['PCT_day_change'] > 2 and regression_data['PCT_change'] > 2) 
#        and float(regression_data['forecast_day_VOL_change']) < -50  
#        and regression_data['PCT_day_change_pre1'] > 0
#        ):
#         add_in_csv(regression_data, regressionResult, ws, '##sellDayHighVolLow-2')
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
        and float(regression_data['contract']) > 10
        and (regression_data['PCT_day_change'] < -1 or regression_data['PCT_change'] < -1)
        and regression_data['forecast_day_PCT_change'] < -0.5
        and regression_data['forecast_day_PCT2_change'] < -0.5
        and regression_data['forecast_day_PCT3_change'] < 0
        and regression_data['forecast_day_PCT4_change'] < 0
        and preDayPctChangeDown_orVolHigh(regression_data)
        and regression_data['open'] > 50
        and last_7_day_all_down(regression_data) == False
        ):
        if((regression_data['forecast_day_VOL_change'] > 70 and -2 < regression_data['PCT_day_change'] < -0.75 and -2 < regression_data['PCT_change'] < -0.5)
            and float(regression_data['contract']) > 10
            ):
            if(('P@[') not in regression_data['sellIndia']):
                add_in_csv(regression_data, regressionResult, ws, 'Reversal(Test):buyReversalOI-0')
                return True
            return False
#         elif((regression_data['forecast_day_VOL_change'] > 35 and -2 < regression_data['PCT_day_change'] < -0.75 and -2 < regression_data['PCT_change'] < -0.5)
#             and float(regression_data['contract']) > 20
#             ):
#             if(('P@[') not in regression_data['sellIndia']):
#                 add_in_csv(regression_data, regressionResult, ws, 'Reversal(Test):buyReversalOI-1')
#                 return True
#             return False
#         elif((regression_data['forecast_day_VOL_change'] > 150 and -3 < regression_data['PCT_day_change'] < -0.75 and -3 < regression_data['PCT_change'] < -0.5)
#             ):
#             add_in_csv(regression_data, regressionResult, ws, 'Reversal(Test):buyReversalOI-2')
#             return True
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
                    add_in_csv(regression_data, regressionResult, ws, '##buyFinalContinue-2')
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
                    add_in_csv(regression_data, regressionResult, ws, 'ML:buyFinalContinue-3')
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

def sell_consolidation_breakdown(regression_data, regressionResult, reg, ws):
    return False
  
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

def sell_oi(regression_data, regressionResult, reg, ws):
    return False
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

def sell_downingMA(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    
    if(is_algo_sell(regression_data)
        and regression_data['SMA4'] < 0
        and regression_data['SMA9'] < 0
        and regression_data['SMA25'] < 0
        and regression_data['SMA100'] < -10
        and regression_data['SMA200'] < -10
        and regression_data['year2HighChange'] > 5
        and regression_data['yearHighChange'] > 5
        ):
        add_in_csv(regression_data, regressionResult, ws, '(Test)ML:AllMANegative-Downtrend')
        return True
    
    if(('$$(Confirmed)$$:EMA6<EMA14' in regression_data['filter4'])
        and -6 < regression_data['PCT_day_change'] < -2.5
        and 0 > regression_data['PCT_change']
        and (regression_data['PCT_day_change'] < -3 or regression_data['PCT_change'] < -3)
        and ((regression_data['PCT_day_change_pre1'] < -1 and regression_data['PCT_day_change_pre2'] < -1 and regression_data['PCT_day_change_pre3'] < -1)
            )
        ):
        add_in_csv(regression_data, regressionResult, ws, '(check-chart)EMA6<EMA14:mayBuy-HighDownSide')
        return True
    elif(('$$(Confirmed)$$:EMA6<EMA14' in regression_data['filter4'])
        and -6 < regression_data['PCT_day_change'] < -2.5
        and 0 > regression_data['PCT_change']
        and (regression_data['PCT_day_change'] < -3 or regression_data['PCT_change'] < -3)
        and (regression_data['PCT_day_change_pre1'] > -1 and regression_data['PCT_day_change_pre2'] > -1)
        ):
        add_in_csv(regression_data, regressionResult, ws, '(check-chart)EMA6<EMA14:mayBuy-LowDownside')
        return True    
    elif(('$$(Confirmed)$$:EMA6<EMA14' in regression_data['filter4'])
        and -2.5 > regression_data['PCT_day_change'] 
        and 0 > regression_data['PCT_change']
        and (regression_data['PCT_day_change'] < -3 or regression_data['PCT_change'] < -3)
        ):
        add_in_csv(regression_data, regressionResult, ws, '(check-chart)EMA6<EMA14')
        return True
    
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
            if(('ReversalHighYear2' in regression_data['filter3'])):
                add_in_csv(regression_data, regressionResult, ws, "##DOWNTREND:sellYear2HighReversal(InDownTrend)")
            if(('ReversalHighYear' in regression_data['filter3'])):
                add_in_csv(regression_data, regressionResult, ws, '##DOWNTREND:sellYearHighReversal(InDownTrend)')
            if(('ReversalHighMonth6' in regression_data['filter3'])):
                add_in_csv(regression_data, regressionResult, ws, '##DOWNTREND:sellMonth6HighReversal(InDownTrend)')
#             if(('ReversalHighMonth3' in regression_data['filter3'])):
#                 add_in_csv(regression_data, regressionResult, ws, '##DOWNTREND:sellMonth3HighReversal(InDownTrend)')
#             if(regression_data['month3LowChange'] > 15 and (regression_data['month6LowChange'] > 20 or regression_data['yearLowChange'] > 30)
#                 ):
#                 if(('NearHighYear2' in regression_data['filter3'])):
#                     add_in_csv(regression_data, regressionResult, ws, None)
#                 if(('NearHighYear' in regression_data['filter3'])):
#                     add_in_csv(regression_data, regressionResult, ws, '##DOWNTREND:sellYearHigh(InDownTrend)')
#                 if(('NearHighMonth6' in regression_data['filter3'])):
#                     add_in_csv(regression_data, regressionResult, ws, '##DOWNTREND:sellMonth6High(InDownTrend)')
#                 if(('NearHighMonth3' in regression_data['filter3'])):
#                     add_in_csv(regression_data, regressionResult, ws, '##DOWNTREND:sellMonth3High(InDownTrend)')
        if(((regression_data['PCT_day_change'] < -2) or (regression_data['PCT_change'] < -2) or ('MaySellCheckChart' in regression_data['filter1']))):
            if('BreakLowYear' in regression_data['filter3']
                and regression_data['year2LowChange'] > 5
                ):
                add_in_csv(regression_data, regressionResult, ws, '##DOWNTREND:sellYearLowBreak')
            if('BreakLowMonth6' in regression_data['filter3']
                and regression_data['yearLowChange'] > 5
                ):
                add_in_csv(regression_data, regressionResult, ws, '##DOWNTREND:sellMonth6LowBreak')
            if('BreakLowMonth3' in regression_data['filter3']
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
            if(regression_data['PCT_day_change_pre1'] < 0
                and -0.75 < regression_data['PCT_day_change'] < 0):
                add_in_csv(regression_data, regressionResult, ws, '--')
            elif(regression_data['PCT_day_change_pre1'] > 0
                and 0 < regression_data['PCT_day_change'] < 0.75):
                add_in_csv(regression_data, regressionResult, ws, '++')
            elif(regression_data['PCT_day_change_pre1'] < 0
                and 0 < regression_data['PCT_day_change'] < 0.75):
                add_in_csv(regression_data, regressionResult, ws, '-+')
            elif(regression_data['PCT_day_change_pre1'] > 0
                and -0.75 < regression_data['PCT_day_change'] < 0):
                add_in_csv(regression_data, regressionResult, ws, '+-')
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
                    add_in_csv(regression_data, regressionResult, ws, 'sellSuperTrend-(Risky)')
                elif((regression_data['PCT_day_change'] > 0
                    or regression_data['forecast_day_PCT_change'] > 0)
                    and (('[' not in regression_data['sellIndia']) and ('[' in regression_data['buyIndia']))
                    ):
                    if(is_algo_buy(regression_data)):
                        add_in_csv(regression_data, regressionResult, ws, 'ML:buySuperTrend-0')
                        return True
                    return False
            elif(abs_month3High_less_than_month3Low(regression_data)):
                if(regression_data['PCT_day_change'] > 0
                    and -1 < regression_data['PCT_day_change_pre1'] < 0
                    and low_tail_pct(regression_data) < 2.5
                    ):
                    add_in_csv(regression_data, regressionResult, ws, 'sellSuperTrend-0')
            return True
        return False

def sell_heavy_downtrend(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    return False
#         if((('NearHighYear2' in regression_data['filter3']) 
#                 or ('NearHighYear' in regression_data['filter3'])
#                 or ('NearHighMonth6' in regression_data['filter3'])
#                 or ('ReversalHighYear2' in regression_data['filter3'])
#                 or ('ReversalHighYear' in regression_data['filter3'])
#                 or ('ReversalHighMonth6' in regression_data['filter3'])
#                 or ('BreakHighYear2' in regression_data['filter3'])
#                 or ('BreakHighYear' in regression_data['filter3'])
#                 or ('BreakHighMonth6' in regression_data['filter3'])
#             )
#             and regression_data['SMA200'] > regression_data['SMA100'] > regression_data['SMA50'] > regression_data['SMA25'] > regression_data['SMA9']
#             and regression_data['series_trend'] == "downTrend"
#             and ((abs(regression_data['PCT_day_change']) > abs(regression_data['PCT_day_change_pre1']))
#                 or regression_data['PCT_change'] > 2
#                 )
#             ):
#             if(((0 < regression_data['PCT_change'] < 3) and (0 < regression_data['PCT_day_change'] < 3))
#             ):
#                 add_in_csv(regression_data, regressionResult, ws, '##(Test)sellSeilingReversal-0')
#             elif(regression_data['PCT_day_change_pre2'] > 0 and regression_data['PCT_day_change'] < -1.5):
#                 add_in_csv(regression_data, regressionResult, ws, '##(Test)sellSeilingReversal-1')
                
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
#                     add_in_csv(regression_data, regressionResult, ws, '##sellHeavyDownTrend-0-Continue')
#                 elif(ten_days_less_than_minus_seven(regression_data)
#                      and(('NearLowMonth3' in regression_data['filter3'])
#                         or ('NearLowMonth6' in regression_data['filter3'])
#                         )
#                 ):
#                     add_in_csv(regression_data, regressionResult, ws, '##sellHeavyDownTrend-1-Continue')
#             if((regression_data['month3LowChange'] < 4)
#                 and ((-5 < regression_data['PCT_change'] < 0) and (-5 < regression_data['PCT_day_change'] < 0))
#                 ):
#                 if((-5 < regression_data['PCT_change'] < -2) and (-5 < regression_data['PCT_day_change'] < -1)
#                     and ten_days_less_than_minus_seven(regression_data)
#                     and(('NearLowMonth3' in regression_data['filter3'])
#                         or ('BreakLowMonth3' in regression_data['filter3'])
#                         or ('NearLowMonth6' in regression_data['filter3'])
#                         )
#                 ):
#                     add_in_csv(regression_data, regressionResult, ws, '##buyHeavyDownTrend-0-Reversal')

def sell_check_chart(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    if(('NearLowMonth3' in regression_data['filter3']) 
            or ('BreakLowMonth3' in regression_data['filter3'])
            or ('ReversalLowMonth3' in regression_data['filter3'])
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
            add_in_csv(regression_data, regressionResult, ws, '##(Check-chart-sell)Month3Low-Continue(InUpTrend)')
            
    #Check for last 5 from latest down should crossover
    if(('NearLowMonth3' in regression_data['filter3']) 
        or ('BreakLowMonth3' in regression_data['filter3'])
        or ('ReversalLowMonth3' in regression_data['filter3'])
        ):
        if(regression_data['month3HighChange'] < -15
            and ((1 < regression_data['PCT_change'] < 5) and (2 < regression_data['PCT_day_change'] < 5))
            and regression_data['close'] > regression_data['bar_high_pre1']
            and regression_data['close'] > regression_data['bar_high_pre2']
            ):
                add_in_csv(regression_data, regressionResult, ws, '##(Test)(Check-chart-sell):month3Low-InPlus')
            
    elif(('NearLowMonth6' in regression_data['filter3']) 
        or ('ReversalLowMonth6' in regression_data['filter3'])
        ):
        if(regression_data['month6LowChange'] < -20
            and ((1 < regression_data['PCT_change'] < 5) and (2 < regression_data['PCT_day_change'] < 5))
            and regression_data['close'] > regression_data['bar_high_pre1']
            and regression_data['close'] > regression_data['bar_high_pre2']
            ):
                add_in_csv(regression_data, regressionResult, ws, '##(Test)(Check-chart-sell):month6Low-InPlus')
                
    elif(('NearLowYear' in regression_data['filter3']) 
        or ('ReversalLowYear' in regression_data['filter3'])
        ):
        if(regression_data['month6LowChange'] < -20
            and ((1 < regression_data['PCT_change'] < 5) and (2 < regression_data['PCT_day_change'] < 5))
            and regression_data['close'] > regression_data['bar_high_pre1']
            and regression_data['close'] > regression_data['bar_high_pre2']
            ):
                add_in_csv(regression_data, regressionResult, ws, '##(Test)(Check-chart-sell):yearLow-InPlus')
            
    if(('NearLowMonth3' in regression_data['filter3']) 
        or ('BreakLowMonth3' in regression_data['filter3'])
        #or ('ReversalLowMonth3' in regression_data['filter3'])
        ):
        if(regression_data['month3HighChange'] < -15
            and ((regression_data['PCT_change'] < 2) and (1 < regression_data['PCT_day_change'] < 2))
            and regression_data['PCT_day_change_pre1'] < -1.5
            and regression_data['PCT_change_pre1'] < -0.5
            and regression_data['close'] < regression_data['bar_high_pre1']
            and (abs(regression_data['PCT_day_change']) * 2 < abs(regression_data['PCT_day_change_pre1']))
            ):
            add_in_csv(regression_data, regressionResult, ws, '##(Test)(Check-chart-buy):month3Low-InPlus-PCTChangeLessThan2')
    elif(('NearLowMonth6' in regression_data['filter3'])
        or ('BreakLowMonth6' in regression_data['filter3'])
        #or ('ReversalLowMonth6' in regression_data['filter3'])
        ):
        if(regression_data['month6LowChange'] < -20
            and ((regression_data['PCT_change'] < 2) and (1 < regression_data['PCT_day_change'] < 2))
            and regression_data['PCT_day_change_pre1'] < -1.5
            and regression_data['PCT_change_pre1'] < -0.5
            and regression_data['close'] < regression_data['bar_high_pre1']
            and (abs(regression_data['PCT_day_change']) * 2 < abs(regression_data['PCT_day_change_pre1']))
            ):
            add_in_csv(regression_data, regressionResult, ws, '##(Test)(Check-chart-buy):month6Low-InPlus-PCTChangeLessThan2')        
            
#         if((('NearLowYear2' in regression_data['filter3']) 
#             or ('ReversalLowYear2' in regression_data['filter3'])
#             or ('BreakLowYear2' in regression_data['filter3'])
#             )):    
#             if(regression_data['year2HighChange'] < -50
#                 and regression_data['year2LowChange'] < 1
#                 and ((regression_data['PCT_change'] < -1) and (regression_data['PCT_day_change'] < -1))
#                 and regression_data['close'] < regression_data['bar_low_pre1']
#                 ):
#                 if(regression_data['PCT_change'] < -4
#                     and ('BreakLowYear2' in regression_data['filter3'])
#                     ):
#                     add_in_csv(regression_data, regressionResult, ws, '##(Test)(Check-chart-buy):year2Low-InMinus')
#                 elif(regression_data['PCT_change'] < -2.5 and regression_data['PCT_day_change'] < -2.5
#                     and ('NearLowYear2' in regression_data['filter3'])
#                     ):
#                     add_in_csv(regression_data, regressionResult, ws, '##(Test)(Check-chart-sell):year2Low-InMinus')
#                 else:
#                     add_in_csv(regression_data, regressionResult, ws, '##(Test)(Check-chart):year2Low-InMinus')
#         elif((('NearLowYear' in regression_data['filter3'])
#             or ('ReversalLowYear' in regression_data['filter3'])
#             or ('BreakLowYear' in regression_data['filter3'])
#             )):
#             if(regression_data['yearHighChange'] < -40
#                 and regression_data['yearLowChange'] < 1
#                 and ((regression_data['PCT_change'] < -1) and (regression_data['PCT_day_change'] < -1))
#                 and regression_data['close'] < regression_data['bar_low_pre1']
#                 ):
#                 if(regression_data['PCT_change'] < -4
#                     and ('BreakLowYear' in regression_data['filter3'])
#                     ):
#                     add_in_csv(regression_data, regressionResult, ws, '##(Test)(Check-chart-buy):yearLow-InMinus')
#                 elif(regression_data['PCT_change'] < -2.5 and regression_data['PCT_day_change'] < -2.5
#                     and ('NearLowYear' in regression_data['filter3'])
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
            add_in_csv(regression_data, regressionResult, ws, '##(Check-chart):MaySellCheckChart-(|_|`|)')
        else:
            add_in_csv(regression_data, regressionResult, ws, '##(Check-chart):MaySellCheckChart-(Risky)-(|_|`|)')
    elif(is_algo_sell(regression_data)
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
                add_in_csv(regression_data, regressionResult, ws, '##(Check-chart):MaySellCheckChart-(IndexNotDownInSecondHalf)')

def sell_random_filter(regression_data, regressionResult, reg, ws):
    if(is_algo_sell(regression_data)):
        if(-3 < regression_data['PCT_day_change'] < -2
            and -3.5 < regression_data['PCT_change'] < -1.5
            and (regression_data['forecast_day_PCT7_change'] > -1)
            and (regression_data['forecast_day_PCT10_change'] > -1)
            and (regression_data['forecast_day_PCT7_change'] > 0
                or regression_data['forecast_day_PCT10_change'] > 0
                )
            and (regression_data['forecast_day_PCT_change'] < 0
                or regression_data['forecast_day_PCT2_change'] < 0
                or regression_data['forecast_day_PCT3_change'] < 0
                )
            and (((regression_data['high'] - regression_data['high_pre1'])/regression_data['high_pre1'])*100) < 0
            ):
            if(regression_data['forecast_day_PCT2_change'] < -1
                and regression_data['forecast_day_PCT3_change'] < -1
                ):
                add_in_csv(regression_data, regressionResult, ws, '(Test)checkCupDown')
            else:
                add_in_csv(regression_data, regressionResult, ws, '(Test)checkCupDown-inDownTrend')      
    if(1 < regression_data['PCT_day_change'] < 2.5
        and 1 < regression_data['PCT_change'] < 3.5
        and regression_data['PCT_day_change'] < -1.5
        and (regression_data['forecast_day_PCT5_change'] > -2)
        and (regression_data['forecast_day_PCT7_change'] > -2)
        and (regression_data['forecast_day_PCT10_change'] > -2)
        and (regression_data['forecast_day_PCT5_change'] > 0
            and regression_data['forecast_day_PCT7_change'] > 0
            and regression_data['forecast_day_PCT10_change'] > 0
            )
        and (regression_data['forecast_day_PCT2_change'] < 0
            and regression_data['forecast_day_PCT3_change'] < 0
            )
        and (((regression_data['high'] - regression_data['high_pre1'])/regression_data['high_pre1'])*100) < 0
        ):
        add_in_csv(regression_data, regressionResult, ws, '(Test)checkCupDown-lastDayUp')
        
    if((-0.5 < regression_data['forecast_day_PCT4_change'] < 0.5
        or -0.5 < regression_data['forecast_day_PCT5_change'] < 0.5
        )
        and 
        (regression_data['forecast_day_PCT4_change'] < -1
        or regression_data['forecast_day_PCT5_change'] < -1
        )
        and regression_data['forecast_day_PCT_change'] < -1
        and regression_data['forecast_day_PCT2_change'] < -2
        and regression_data['forecast_day_PCT3_change'] < -3
#         and regression_data['forecast_day_PCT7_change'] < -3
#         and regression_data['forecast_day_PCT10_change'] < -3
        and regression_data['PCT_day_change'] < -1
        and regression_data['PCT_day_change_pre1'] < -1
        and regression_data['PCT_day_change_pre2'] < -1
        ):
        add_in_csv(regression_data, regressionResult, ws, '(Test)buyMay5DayFloorReversal')
        
def sell_test(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    flag = sell_other_indicator(regression_data, regressionResult, reg, ws)
    return flag
        
    return False
      
def sell_oi_candidate(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    tail_pct_filter(regression_data, regressionResult)
    tail_reversal_filter(regression_data, regressionResult)
    flag = False
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

def sell_all_filter(regression_data, regressionResult, reg, ws):
    flag = False
    if sell_year_high(regression_data, regressionResult, reg, None, None):
        add_in_csv(regression_data, regressionResult, ws, None)
        flag = True
    if sell_year_low(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws, None)
        flag = True
    if sell_up_trend(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws, None)
        flag = True
    if sell_down_trend(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws, None)
        flag = True
    if sell_final(regression_data, regressionResult, reg, None, None):
        add_in_csv(regression_data, regressionResult, ws, None)
        flag = True
    if sell_high_indicators(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws, None)
        flag = True
    if sell_pattern(regression_data, regressionResult, reg, None, None):
        add_in_csv(regression_data, regressionResult, ws, None)
        flag = True
    if sell_oi(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws, None)
        flag = True
    return flag

def sell_filter_accuracy(regression_data, regressionResult, reg, ws):
    filtersDict=scrip_patterns_to_dict('../../data-import/nselist/filter-sell.csv')
    if regression_data['filter'] != '':
        filter = regression_data['filter'].replace("[MLBuy]:", "").replace("[MLSell]:", "").strip()
        if filter != '' and filter in filtersDict:
            regression_data['filter_avg'] = float(filtersDict[filter]['avg'])
            regression_data['filter_count'] = float(filtersDict[filter]['count'])