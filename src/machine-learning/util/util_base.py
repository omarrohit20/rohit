import csv
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import Color, PatternFill, Font, Border
from pymongo import MongoClient
from multiprocessing.dummy import Pool as ThreadPool

import quandl, math, time
from datetime import date
import datetime   
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np

soft=False
NIFTY_HIGH = False
NIFTY_LOW = False
BUY_VERY_LESS_DATA=True
SELL_VERY_LESS_DATA=True
MARKET_IN_UPTREND=False
MARKET_IN_DOWNTREND=False
CLOSEPRICE = 40
TEST = False

buyMLP = 0.1
buyMLP_MIN = 0
buyKN = 0.1
buyKN_MIN = 0
sellMLP = -0.1
sellMLP_MIN = 0
sellKN = -0.1
sellKN_MIN = 0

connection = MongoClient('localhost',27017)
db = connection.Nsedata

def patterns_to_dict(filename):  
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
                    dictValue['countgt'] = row[3]
                    dictValue['countlt'] = row[4]
                    tempDict[row[0]] = dictValue
                count = count + 1
            except:
                pass
    return tempDict

def all_withoutml(regression_data, regressionResult, ws):
    tempRegressionResult = regressionResult.copy() 
    tempRegressionResult.append(regression_data['filter1'])
    tempRegressionResult.append(regression_data['filter2'])
    tempRegressionResult.append(regression_data['filter3'])
    tempRegressionResult.append(regression_data['filter4'])
    tempRegressionResult.append(regression_data['filter5'])
    tempRegressionResult.append(regression_data['filter'])
    tempRegressionResult.append(regression_data['filterbuy'])
    tempRegressionResult.append(regression_data['filtersell'])
    tempRegressionResult.append(regression_data['filter_345_avg'])
    tempRegressionResult.append(regression_data['filter_345_count'])
    tempRegressionResult.append(regression_data['filter_345_pct'])
    tempRegressionResult.append(regression_data['filter_avg'])
    tempRegressionResult.append(regression_data['filter_count'])
    tempRegressionResult.append(regression_data['filter_pct'])
    tempRegressionResult.append(regression_data['filter_pct_change_avg'])
    tempRegressionResult.append(regression_data['filter_pct_change_count'])
    tempRegressionResult.append(regression_data['filter_pct_change_pct'])
    tempRegressionResult.append(regression_data['filter_all_avg'])
    tempRegressionResult.append(regression_data['filter_all_count'])
    tempRegressionResult.append(regression_data['filter_all_pct'])
    tempRegressionResult.append(regression_data['filter_tech_avg'])
    tempRegressionResult.append(regression_data['filter_tech_count'])
    tempRegressionResult.append(regression_data['filter_tech_pct'])
    tempRegressionResult.append(regression_data['filter_tech_all_avg'])
    tempRegressionResult.append(regression_data['filter_tech_all_count'])
    tempRegressionResult.append(regression_data['filter_tech_all_pct'])
    tempRegressionResult.append(regression_data['filter_tech_all_pct_change_avg'])
    tempRegressionResult.append(regression_data['filter_tech_all_pct_change_count'])
    tempRegressionResult.append(regression_data['filter_tech_all_pct_change_pct'])
    ws.append(tempRegressionResult) if (ws is not None) else False
    if(db.resultScripFutures.find_one({'scrip':regression_data['scrip']}) is None):
        db.resultScripFutures.insert_one({
            "scrip": regression_data['scrip'],
            "date": regression_data['date']
            })

def withoutml(regression_data, ws):
    ws.append(regression_data) if (ws is not None) else False


def add_in_csv(regression_data, regressionResult, ws=None, filterbuy=None, filtersell=None, filter=None, filter1=None, filter2=None, filter3=None, filter4=None, filter5=None, filter6=None):
    if(TEST != True):
        if(is_algo_buy(regression_data) and (filter is None)):
            if '[MLBuy]' not in regression_data['filter']:
                #regression_data['filterbuy'] ='[MLBuy]' + ':'
                #regression_data['filtersell'] ='[MLBuy]' + ':'
                regression_data['filter'] ='[MLBuy]' + ':'
        if(is_algo_sell(regression_data) and (filter is None)):
            if '[MLSell]' not in regression_data['filter']:
                #regression_data['filterbuy'] ='[MLSell]' + ':'
                #regression_data['filtersell'] ='[MLSell]' + ':'
                regression_data['filter'] ='[MLSell]' + ':'
        if ((filterbuy is not None) and (filterbuy not in regression_data['filterbuy'])):
            list = regression_data['filterbuy'].partition(']:')
            if(list[1] == ']:'):
                regression_data['filterbuy'] = list[0] + list[1] + filterbuy + ','  + list[2]
            else:
                regression_data['filterbuy'] = filterbuy + ','  + regression_data['filterbuy']
        if ((filtersell is not None) and (filtersell not in regression_data['filtersell'])):
            list = regression_data['filtersell'].partition(']:')
            if(list[1] == ']:'):
                regression_data['filtersell'] = list[0] + list[1] + filtersell + ','  + list[2]
            else:
                regression_data['filtersell'] = filtersell + ','  + regression_data['filtersell']  
        if ((filter is not None) and (filter not in regression_data['filter'])):
            list = regression_data['filter'].partition(']:')
            if(list[1] == ']:'):
                regression_data['filter'] = list[0] + list[1] + filter + ','  + list[2]
            else:
                regression_data['filter'] = filter + ','  + regression_data['filter']    
        if ((filter1 is not None) and (filter1 not in regression_data['filter1'])):
            regression_data['filter1'] = filter1 + ',' + regression_data['filter1']
        if ((filter2 is not None) and (filter2 not in regression_data['filter2'])):
            regression_data['filter2'] = filter2 + ',' + regression_data['filter2']
        if ((filter3 is not None) and (filter3 not in regression_data['filter3'])):
            regression_data['filter3'] = filter3 + ',' + regression_data['filter3']
        if ((filter4 is not None) and (filter4 not in regression_data['filter4'])):
            regression_data['filter4'] = filter4 + ',' + regression_data['filter4']  
        if ((filter5 is not None) and (filter5 not in regression_data['filter5'])):
            regression_data['filter5'] = filter5 + ',' + regression_data['filter5']
    else:
        if ((filterbuy is not None) and (filterbuy not in regression_data['filterbuy'])):
            regression_data['filterbuy'] = filterbuy + ','  + regression_data['filterbuy']
        if ((filtersell is not None) and (filtersell not in regression_data['filtersell'])):
            regression_data['filtersell'] = filtersell + ','  + regression_data['filtersell']
        if ((filter is not None) and (filter not in regression_data['filter'])):
            regression_data['filter'] = filter + ','  + regression_data['filter']
        if ((filter1 is not None) and (filter1 not in regression_data['filter1'])):
            regression_data['filter1'] = filter1 + ',' + regression_data['filter1']
        if ((filter2 is not None) and (filter2 not in regression_data['filter2'])):
            regression_data['filter2'] = filter2 + ',' + regression_data['filter2']
        if ((filter3 is not None) and (filter3 not in regression_data['filter3'])):
            regression_data['filter3'] = filter3 + ',' + regression_data['filter3']
        if ((filter4 is not None) and (filter4 not in regression_data['filter4'])):
            regression_data['filter4'] = filter4 + ',' + regression_data['filter4']  
        if ((filter5 is not None) and (filter5 not in regression_data['filter5'])):
            regression_data['filter5'] = filter5 + ',' + regression_data['filter5']
        if ((filter6 is not None) and (filter6 not in regression_data['filter6'])):
            regression_data['filter6'] = filter6 + ',' + regression_data['filter6']
        
# def add_in_csv_hist_pattern(regression_data, regressionResult, ws, filter, avg, count):
#     if(TEST != True):
#         if ((filter is not None) and (filter not in regression_data['filter'])):
#             regression_data['filter'] = regression_data['filter'] + filter + ','
#         tempRegressionResult = regressionResult.copy() 
#         tempRegressionResult.append(regression_data['filter'])
#         tempRegressionResult.append(avg)
#         tempRegressionResult.append(count)
#         ws.append(tempRegressionResult) if (ws is not None) else False
#     else:
#         if ((filter is not None) and (filter not in regression_data['filterTest'])):
#             regression_data['filterTest'] = regression_data['filterTest'] + filter + ','
#         tempRegressionResult = regressionResult.copy() 
#         tempRegressionResult.append(regression_data['filterTest'])
#         tempRegressionResult.append(avg)
#         tempRegressionResult.append(count)
#         ws.append(tempRegressionResult) if (ws is not None) else False

def is_any_reg_algo_gt1(regression_data):
    if((regression_data['mlpValue_reg'] >= 1) 
        or (regression_data['kNeighboursValue_reg'] >= 1)
        or (regression_data['mlpValue_reg_other'] >= 1) 
        or (regression_data['kNeighboursValue_reg_other'] >= 1)
        ):
        return True
    else:
        return False
    
def is_any_reg_algo_lt_minus1(regression_data):
    if((regression_data['mlpValue_reg'] <= -1) 
        or (regression_data['kNeighboursValue_reg'] <= -1)
        or (regression_data['mlpValue_reg_other'] <= -1) 
        or (regression_data['kNeighboursValue_reg_other'] <= -1)
        ):
        return True
    else:
        return False

def is_any_reg_algo_gt1dot5(regression_data):
    if((regression_data['mlpValue_reg'] >= 1.5) 
        or (regression_data['kNeighboursValue_reg'] >= 1.5)
        or (regression_data['mlpValue_reg_other'] >= 1.5) 
        or (regression_data['kNeighboursValue_reg_other'] >= 1.5)
        ):
        return True
    else:
        return False
    
def is_any_reg_algo_lt_minus1dot5(regression_data):
    if((regression_data['mlpValue_reg'] <= -1.5) 
        or (regression_data['kNeighboursValue_reg'] <= -1.5)
        or (regression_data['mlpValue_reg_other'] <= -1.5) 
        or (regression_data['kNeighboursValue_reg_other'] <= -1.5)
        ):
        return True
    else:
        return False

def is_any_reg_algo_gt1_not_other(regression_data):
    if((regression_data['mlpValue_reg'] >= 1) 
        or (regression_data['kNeighboursValue_reg'] >= 1)
        ):
        return True
    else:
        return False
    
def is_any_reg_algo_lt_minus1_not_other(regression_data):
    if((regression_data['mlpValue_reg'] <= -1) 
        or (regression_data['kNeighboursValue_reg'] <= -1)
        ):
        return True
    else:
        return False

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
            or ((regression_data['mlpValue_reg'] + regression_data['kNeighboursValue_reg'] + regression_data['mlpValue_reg_other'] + regression_data['kNeighboursValue_reg_other']) > 4
                and regression_data['mlpValue_reg'] + regression_data['kNeighboursValue_reg'] > 2
                )
            ):
            if((regression_data['mlpValue_cla'] < 0) or (regression_data['kNeighboursValue_cla'] < 0)
                or (regression_data['mlpValue_cla_other'] < 0) or (regression_data['kNeighboursValue_cla_other'] < 0)
                ):
                if((regression_data['mlpValue_reg'] < 0) or (regression_data['kNeighboursValue_reg'] < 0)
                    or (regression_data['mlpValue_reg_other'] < 0) or (regression_data['kNeighboursValue_reg_other'] < 0)
                    ):
                    return False
            if((regression_data['mlpValue_reg'] + regression_data['kNeighboursValue_reg']) < 1.5
                and (regression_data['mlpValue_reg_other'] + regression_data['kNeighboursValue_reg_other']) < 1.5
                and regression_data['PCT_day_change'] > 0
                #and regression_data['PCT_change'] > 0
                ):
                return False
            if((regression_data['mlpValue_cla'] <= 0) and (regression_data['kNeighboursValue_cla'] <= 0)
                and (regression_data['mlpValue_cla_other'] <= 0) and (regression_data['kNeighboursValue_cla_other'] <= 0)
                and (regression_data['mlpValue_reg'] <= 2.5) and (regression_data['kNeighboursValue_reg'] <= 2.5)
                and (regression_data['mlpValue_reg_other'] <= 2.5) and (regression_data['kNeighboursValue_reg_other'] <= 2.5)
                ):
                return False
            if resticted:
                if((regression_data['mlpValue_reg_other'] >= 0 or regression_data['kNeighboursValue_reg_other'] >= 0)):
                    return True
            else:
                return True
    elif(regression_data['PCT_day_change'] < -3
#          and ((regression_data['mlpValue_reg'] + regression_data['kNeighboursValue_reg']) > 1.5
#                 or (regression_data['mlpValue_reg_other'] + regression_data['kNeighboursValue_reg_other']) > 1.5
#              )
         and ((regression_data['mlpValue_reg_other'] > -1 and regression_data['mlpValue_reg'] > -1 and regression_data['forecast_mlpValue_reg'] > 5)
              or (regression_data['kNeighboursValue_reg_other'] > -1 and regression_data['kNeighboursValue_reg'] > -1 and regression_data['forecast_kNeighboursValue_reg'] > 5)
              or (regression_data['mlpValue_reg'] > -1.5
                  and regression_data['kNeighboursValue_reg'] > -1.5
                  and regression_data['mlpValue_reg_other'] > -1
                  and regression_data['kNeighboursValue_reg_other'] > -1
                 )
              )
        ):
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
            or ((regression_data['mlpValue_reg'] + regression_data['kNeighboursValue_reg'] + regression_data['mlpValue_reg_other'] + regression_data['kNeighboursValue_reg_other']) < -4
               and regression_data['mlpValue_reg'] + regression_data['kNeighboursValue_reg'] < -2
               )
            ):
            if((regression_data['mlpValue_cla'] > 0) or (regression_data['kNeighboursValue_cla'] > 0)
                or (regression_data['mlpValue_cla_other'] > 0) or (regression_data['kNeighboursValue_cla_other'] > 0)
                ):
                if((regression_data['mlpValue_reg'] > 0) or (regression_data['kNeighboursValue_reg'] > 0)
                    or (regression_data['mlpValue_reg_other'] > 0) or (regression_data['kNeighboursValue_reg_other'] > 0)
                    ):
                    return False
            if((regression_data['mlpValue_reg'] + regression_data['kNeighboursValue_reg']) > -1.5
                and (regression_data['mlpValue_reg_other'] + regression_data['kNeighboursValue_reg_other']) > -1.5
                and regression_data['PCT_day_change'] < 0
                #and regression_data['PCT_change'] < 0
                ):
                return False
            if((regression_data['mlpValue_cla'] >= 0) and (regression_data['kNeighboursValue_cla'] >= 0)
                and (regression_data['mlpValue_cla_other'] >= 0) and (regression_data['kNeighboursValue_cla_other'] >= 0)
                and (regression_data['mlpValue_reg'] >= -2.5) and (regression_data['kNeighboursValue_reg'] >= -2.5)
                and (regression_data['mlpValue_reg_other'] >= -2.5) and (regression_data['kNeighboursValue_reg_other'] >= -2.5)
                ):
                return False
            if resticted:
                if((-5 < regression_data['PCT_day_change'] < 0) and (regression_data['mlpValue_reg_other'] <= 0 or regression_data['kNeighboursValue_reg_other'] <= 0)):
                    return True
            else:
                return True
    elif(regression_data['PCT_day_change'] > 3
#          and ((regression_data['mlpValue_reg'] + regression_data['kNeighboursValue_reg']) < -1.5
#                 or (regression_data['mlpValue_reg_other'] + regression_data['kNeighboursValue_reg_other']) < -1.5
#              )
         and ((regression_data['mlpValue_reg_other'] < 1 and regression_data['mlpValue_reg'] < 1 and regression_data['forecast_mlpValue_reg'] < -5)
              or (regression_data['kNeighboursValue_reg_other'] < 1 and regression_data['kNeighboursValue_reg'] < 1 and regression_data['forecast_kNeighboursValue_reg'] < -5)
              or (regression_data['mlpValue_reg'] < 1.5
                  and regression_data['kNeighboursValue_reg'] < 1.5
                  and regression_data['mlpValue_reg_other'] < 1
                  and regression_data['kNeighboursValue_reg_other'] < 1
                 )
              )
        ):
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

def high_counter(regression_data):
    count = 0
    if(regression_data['high'] > regression_data['high_pre1']):
        count = count + 1;
    if(regression_data['high_pre1'] > regression_data['high_pre2']):
        count = count + 1;
    if(regression_data['high_pre2'] > regression_data['high_pre3']):
        count = count + 1;
    if(regression_data['high_pre3'] > regression_data['high_pre4']):
        count = count + 1;
    return count

def low_counter(regression_data):
    count = 0
    if(regression_data['low'] < regression_data['low_pre1']):
        count = count + 1;
    if(regression_data['low_pre1'] < regression_data['low_pre2']):
        count = count + 1;
    if(regression_data['low_pre2'] < regression_data['low_pre3']):
        count = count + 1;
    if(regression_data['low_pre3'] < regression_data['low_pre4']):
        count = count + 1;
    return count

def pct_day_change_counter(regression_data):
    countGt = 0
    countLt = 0
    if(regression_data['PCT_day_change'] > 0):
        countGt = countGt + 1
    if(regression_data['PCT_day_change'] < 0):
        countLt = countLt + 1
        
    if(regression_data['PCT_day_change_pre1'] > 0):
        countGt = countGt + 1
    if(regression_data['PCT_day_change_pre1'] < 0):
        countLt = countLt + 1
        
    if(regression_data['PCT_day_change_pre2'] > 0):
        countGt = countGt + 1
    if(regression_data['PCT_day_change_pre2'] < 0):
        countLt = countLt + 1
        
    if(regression_data['PCT_day_change_pre3'] > 0):
        countGt = countGt + 1
    if(regression_data['PCT_day_change_pre3'] < 0):
        countLt = countLt + 1
    
    return countGt, countLt

def pct_day_change_counter_gt1dot5(regression_data):
    countGt = 0
    countLt = 0
    if(regression_data['PCT_day_change'] > 1):
        countGt = countGt + 1
    if(regression_data['PCT_day_change'] < -1):
        countLt = countLt + 1
        
    if(regression_data['PCT_day_change_pre1'] > 1):
        countGt = countGt + 1
    if(regression_data['PCT_day_change_pre1'] < -1):
        countLt = countLt + 1
        
    if(regression_data['PCT_day_change_pre2'] > 1):
        countGt = countGt + 1
    if(regression_data['PCT_day_change_pre2'] < -1):
        countLt = countLt + 1
        
    if(regression_data['PCT_day_change_pre3'] > 1):
        countGt = countGt + 1
    if(regression_data['PCT_day_change_pre3'] < -1):
        countLt = countLt + 1
    
    return countGt, countLt

def pct_day_change_trend(regression_data):
    countGt = 0
    countLt = 0
    if(regression_data['PCT_day_change'] > 0):
        countGt = countGt + 1
    else:
        countLt = countLt - 1
        
    if(regression_data['PCT_day_change_pre1'] > 0):
        countGt = countGt + 1
    else:
        countLt = countLt - 1
        
    if(regression_data['PCT_day_change_pre2'] > 0):
        countGt = countGt + 1
    else:
        countLt = countLt - 1
        
    if(regression_data['PCT_day_change_pre3'] > 0):
        countGt = countGt + 1
    else:
        countLt = countLt - 1
        
    if(regression_data['PCT_day_change_pre4'] > 0):
        countGt = countGt + 1
    else:
        countLt = countLt - 1
        
    if (high_counter(regression_data) >= 2 and countGt >= 4
        and regression_data['PCT_day_change_pre1'] > -1
        and regression_data['PCT_day_change_pre2'] > -1
        ):
        return countGt
    elif(low_counter(regression_data) >= 2 and countLt <= -4
        and regression_data['PCT_day_change_pre1'] < 1
        and regression_data['PCT_day_change_pre2'] < 1
        ):
        return countLt
    else:
        return 0
    
    return count
    
def pct_change_negative_trend(regression_data):
    countGt1, countLt1 = pct_day_change_counter_gt1dot5(regression_data)
    if (#regression_data['forecast_day_PCT_change'] < 0
        regression_data['forecast_day_PCT2_change'] < 0
        and regression_data['forecast_day_PCT3_change'] < 0
#         and ((regression_data['low'] < regression_data['low_pre1'] and regression_data['low_pre1'] < regression_data['low_pre2'])
#             or (regression_data['bar_low'] < regression_data['bar_low_pre1'] and regression_data['bar_low_pre1'] < regression_data['bar_low_pre2'])
#             )
        and regression_data['forecast_day_PCT3_change'] < regression_data['forecast_day_PCT2_change']
        and low_counter(regression_data) >= 2
#         and (regression_data['high'] < regression_data['high_pre1']
#              or regression_data['high'] < regression_data['high_pre2']
#              or regression_data['high'] < regression_data['high_pre3']
#              or regression_data['high'] < regression_data['high_pre4']
#              )
        #and countLt1 >= 2
        ):
        pct_change_list = [#regression_data['forecast_day_PCT_change']
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
        if trend:
            if (regression_data['forecast_day_PCT10_change'] < regression_data['forecast_day_PCT5_change']
                or regression_data['forecast_day_PCT7_change'] < regression_data['forecast_day_PCT5_change']
                ):
                if(regression_data['bar_low'] < regression_data['bar_low_pre1']
                    and regression_data['bar_low_pre1'] < regression_data['bar_low_pre2']
                    and low_counter(regression_data) >= 3
                    ):
                    return '(downTrend)'
                else:
                    return '(downTrend-Risky)'
            if (regression_data['forecast_day_PCT5_change'] < regression_data['forecast_day_PCT4_change']
                ):
                if(regression_data['bar_low'] < regression_data['bar_low_pre1']
                    and regression_data['bar_low_pre1'] < regression_data['bar_low_pre2']
                    and low_counter(regression_data) >= 3
                    ):
                    return '(downTrend5Day)'
                else:
                    return '(downTrend5Day-Risky)'
    if(regression_data['forecast_day_PCT10_change'] < regression_data['forecast_day_PCT7_change'] < regression_data['forecast_day_PCT4_change'] < 0
        and regression_data['high'] < regression_data['bar_low_pre1']
        and regression_data['high'] < regression_data['bar_low_pre2']
        and regression_data['forecast_day_PCT2_change'] < 0
        and regression_data['forecast_day_PCT3_change'] < 0
        ):
        return '(trendDown10<7<4)'
    if(regression_data['forecast_day_PCT10_change'] < regression_data['forecast_day_PCT5_change'] < regression_data['forecast_day_PCT4_change'] < 0
        and regression_data['high'] < regression_data['bar_low_pre1']
        and regression_data['high'] < regression_data['bar_low_pre2']
        and regression_data['forecast_day_PCT2_change'] < 0
        and regression_data['forecast_day_PCT3_change'] < 0
        ):
        return '(trendDown10<5<4)'
#     elif(
#         regression_data['forecast_day_PCT2_change'] < 0
#         and regression_data['forecast_day_PCT3_change'] < 0
#         and regression_data['forecast_day_PCT4_change'] < 0
#         and regression_data['forecast_day_PCT5_change'] < 0
#         and regression_data['forecast_day_PCT7_change'] < 0
#         and regression_data['forecast_day_PCT10_change'] < 0
#         ):
#         return '(trendDownAll)'    
    if(regression_data['forecast_day_PCT10_change'] < regression_data['forecast_day_PCT7_change'] < regression_data['forecast_day_PCT3_change'] < 0
        ):
        return '(trendDown10<7<3)'
    if(regression_data['forecast_day_PCT10_change'] < regression_data['forecast_day_PCT5_change'] < regression_data['forecast_day_PCT3_change'] < 0
        ):
        return '(trendDown10<5<3)'
    if(regression_data['forecast_day_PCT2_change'] < 0
        and regression_data['forecast_day_PCT3_change'] < 0
        and (regression_data['forecast_day_PCT3_change'] < regression_data['forecast_day_PCT2_change']
            or regression_data['forecast_day_PCT4_change'] < regression_data['forecast_day_PCT3_change']
            or regression_data['forecast_day_PCT5_change'] < regression_data['forecast_day_PCT4_change']
            )
        and low_counter(regression_data) >= 2
        and (regression_data['high'] < regression_data['high_pre1']
             or regression_data['high'] < regression_data['high_pre2']
             or regression_data['high'] < regression_data['high_pre3']
             or regression_data['high'] < regression_data['high_pre4']
             )
        and regression_data['month3LowChange'] < 0
        and abs(regression_data['monthHighChange']) > abs(regression_data['monthLowChange'])
        ):
        return '(shortUpTrend-month3LowChangeLT0)' 
    if(pct_day_change_trend(regression_data) <= -3
        and abs_monthHigh_more_than_monthLow(regression_data)
        and regression_data['forecast_day_PCT5_change'] < 0
        and regression_data['forecast_day_PCT7_change'] < 0
        ):
        return '(trendDown-MLowLTMHigh)'
    if (regression_data['forecast_day_PCT_change'] > 0  
        and regression_data['forecast_day_PCT_change'] < regression_data['forecast_day_PCT2_change'] < regression_data['forecast_day_PCT3_change']
        and high_counter(regression_data) >= 3
        and ((regression_data['forecast_day_PCT3_change'] > regression_data['forecast_day_PCT4_change'] > regression_data['forecast_day_PCT5_change'] > regression_data['forecast_day_PCT7_change'] > regression_data['forecast_day_PCT10_change'])
             or (regression_data['forecast_day_PCT4_change'] > regression_data['forecast_day_PCT5_change'] > regression_data['forecast_day_PCT7_change'] > regression_data['forecast_day_PCT10_change'])
            )
        ):
        if(abs_monthHigh_more_than_monthLow(regression_data)):
            if(regression_data['forecast_day_PCT10_change'] < 0):
                return '(mediumDownTrend)'  
            elif(regression_data['forecast_day_PCT10_change'] > 0):
                return '(mediumDownTrend-crossed10Days)'
        if(abs_monthHigh_less_than_monthLow(regression_data)): 
            if(regression_data['forecast_day_PCT10_change'] < 0):
                return '(mediumDownTrend-monthLowGTmonthHigh)'  
            elif(regression_data['forecast_day_PCT10_change'] > 0):
                return '(mediumDownTrend-monthLowGTmonthHigh-crossed10Days)' 
    
    if(regression_data['SMA9'] < -1.5):
        return 'SMA9LT-1.5'
            
    return 'NA'           
    
def pct_change_positive_trend(regression_data):
    countGt1, countLt1 = pct_day_change_counter_gt1dot5(regression_data)
    
    if(regression_data['forecast_day_PCT2_change'] > 0
        and regression_data['forecast_day_PCT3_change'] > 0
        and regression_data['forecast_day_PCT3_change'] > regression_data['forecast_day_PCT2_change']
        and high_counter(regression_data) >= 2
#         and (regression_data['low'] > regression_data['low_pre1']
#              or regression_data['low'] > regression_data['low_pre2']
#              or regression_data['low'] > regression_data['low_pre3']
#              or regression_data['low'] > regression_data['low_pre4']
#              )
        #and countGt1 >= 2
        ):
        pct_change_list = [#regression_data['forecast_day_PCT_change'],
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
        if trend:
            if (regression_data['forecast_day_PCT10_change'] > regression_data['forecast_day_PCT5_change']
                or regression_data['forecast_day_PCT7_change'] > regression_data['forecast_day_PCT5_change']
                ):
                if(regression_data['bar_high'] > regression_data['bar_high_pre1']
                    and regression_data['bar_high_pre1'] > regression_data['bar_high_pre2']
                    and high_counter(regression_data) >= 3
                    ):
                    return '(upTrend)' 
                else:
                    return '(upTrend-Risky)'
            elif (regression_data['forecast_day_PCT5_change'] > regression_data['forecast_day_PCT4_change']
                ):
                if(regression_data['bar_high'] > regression_data['bar_high_pre1']
                    and regression_data['bar_high_pre1'] > regression_data['bar_high_pre2']
                    and high_counter(regression_data) >= 3
                    ):
                    return '(upTrend5Day)' 
                else:
                    return '(upTrend5Day-Risky)' 
    if(regression_data['forecast_day_PCT10_change'] > regression_data['forecast_day_PCT7_change'] > regression_data['forecast_day_PCT4_change'] > 0
        and regression_data['low'] > regression_data['bar_high_pre1']
        and regression_data['low'] > regression_data['bar_high_pre2']
        and regression_data['forecast_day_PCT2_change'] > 0
        and regression_data['forecast_day_PCT3_change'] > 0
        ):
        return '(trendUp10>7>4)'
    if(regression_data['forecast_day_PCT10_change'] > regression_data['forecast_day_PCT5_change'] > regression_data['forecast_day_PCT4_change'] > 0
        and regression_data['low'] > regression_data['bar_high_pre1']
        and regression_data['low'] > regression_data['bar_high_pre2']
        and regression_data['forecast_day_PCT2_change'] > 0
        and regression_data['forecast_day_PCT3_change'] > 0
        ):
        return '(trendUp10>5>4)' 
#     elif(
#         regression_data['forecast_day_PCT2_change'] > 0
#         and regression_data['forecast_day_PCT3_change'] > 0
#         and regression_data['forecast_day_PCT4_change'] > 0
#         and regression_data['forecast_day_PCT5_change'] > 0
#         and regression_data['forecast_day_PCT7_change'] > 0
#         and regression_data['forecast_day_PCT10_change'] > 0
#         ):
#         return '(trendUpAll)' 
    if(regression_data['forecast_day_PCT10_change'] > regression_data['forecast_day_PCT7_change'] > regression_data['forecast_day_PCT3_change'] > 0
        ):
        return '(trendUp10>7>3)'
    if(regression_data['forecast_day_PCT10_change'] > regression_data['forecast_day_PCT5_change'] > regression_data['forecast_day_PCT3_change'] > 0
        ):
        return '(trendUp10>5>3)'
    if(regression_data['forecast_day_PCT2_change'] > 0
        and regression_data['forecast_day_PCT3_change'] > 0
        and (regression_data['forecast_day_PCT3_change'] > regression_data['forecast_day_PCT2_change']
             or regression_data['forecast_day_PCT4_change'] > regression_data['forecast_day_PCT3_change']
             or regression_data['forecast_day_PCT5_change'] > regression_data['forecast_day_PCT4_change']
            )
        and high_counter(regression_data) >= 2
        and (regression_data['low'] > regression_data['low_pre1']
             or regression_data['low'] > regression_data['low_pre2']
             or regression_data['low'] > regression_data['low_pre3']
             or regression_data['low'] > regression_data['low_pre4']
             )
        and regression_data['month3HighChange'] > 0
        and abs(regression_data['monthHighChange']) < abs(regression_data['monthLowChange'])
        ):
        return '(shortUpTrend-month3HighChangeGT0)'
    if(pct_day_change_trend(regression_data) >= 3
        and abs_monthHigh_less_than_monthLow(regression_data)
        and regression_data['forecast_day_PCT5_change'] > 0
        and regression_data['forecast_day_PCT7_change'] > 0
        ):
        return '(trendDown-MLowLTMHigh)'    
    if(regression_data['forecast_day_PCT_change'] < 0  
        and regression_data['forecast_day_PCT_change'] > regression_data['forecast_day_PCT2_change'] > regression_data['forecast_day_PCT3_change'] > 0
        and low_counter(regression_data) >= 3
        and ((regression_data['forecast_day_PCT3_change'] < regression_data['forecast_day_PCT4_change'] < regression_data['forecast_day_PCT5_change'] < regression_data['forecast_day_PCT7_change'] < regression_data['forecast_day_PCT10_change'])
             or (regression_data['forecast_day_PCT4_change'] < regression_data['forecast_day_PCT5_change'] < regression_data['forecast_day_PCT7_change'] < regression_data['forecast_day_PCT10_change'])
             )
        ):
        if(abs_monthHigh_less_than_monthLow(regression_data)):
            if(regression_data['forecast_day_PCT10_change'] > 0):
                return '(mediumUpTrend)'
            elif(regression_data['forecast_day_PCT10_change'] < 0):
                return '(mediumUpTrend-crossed10Days)'
        if(abs_monthHigh_more_than_monthLow(regression_data)):
            if(regression_data['forecast_day_PCT10_change'] > 0):
                return '(mediumUpTrend-monthHighGTmonthLow)'
            elif(regression_data['forecast_day_PCT10_change'] < 0):
                return '(mediumUpTrend-monthHighGTmonthLow-crossed10Days)'
    
    if(regression_data['SMA9'] > 1.5):
        return 'SMA9GT1.5'
     
    return 'NA' 

def pct_change_negative_trend_medium(regression_data):
    if (#regression_data['forecast_day_PCT_change'] < 0
        #and regression_data['forecast_day_PCT2_change'] < 0
        regression_data['forecast_day_PCT3_change'] < 0
        and low_counter(regression_data) >= 3
        and ((regression_data['forecast_day_PCT3_change'] > regression_data['forecast_day_PCT4_change'] > regression_data['forecast_day_PCT5_change'])
             or (regression_data['forecast_day_PCT4_change'] > regression_data['forecast_day_PCT5_change'] > regression_data['forecast_day_PCT7_change'])
             or (regression_data['forecast_day_PCT3_change'] > regression_data['forecast_day_PCT5_change'] > regression_data['forecast_day_PCT7_change'])
            )
        ):
        return 'mediumDownTrend' 
    
    if(regression_data['SMA9'] < -1.5):
        return 'SMA9LT-1.5'          
    
    return 'NA'           
    
def pct_change_positive_trend_medium(regression_data):
    if (#regression_data['forecast_day_PCT_change'] > 0
        #and regression_data['forecast_day_PCT2_change'] > 0
        regression_data['forecast_day_PCT3_change'] > 0
        and high_counter(regression_data) >= 3
        and ((regression_data['forecast_day_PCT3_change'] < regression_data['forecast_day_PCT4_change'] < regression_data['forecast_day_PCT5_change'])
             or (regression_data['forecast_day_PCT4_change'] < regression_data['forecast_day_PCT5_change'] < regression_data['forecast_day_PCT7_change'])
             or (regression_data['forecast_day_PCT3_change'] < regression_data['forecast_day_PCT5_change'] < regression_data['forecast_day_PCT7_change'])
            )
        ):
        return 'mediumUpTrend'
    
    
    if(1.5 < regression_data['SMA9']):
        return 'SMA9GT1.5'
    
    return 'NA'          

def pct_change_negative_trend_short(regression_data):
    countGt1, countLt1 = pct_day_change_counter_gt1dot5(regression_data)
    if(regression_data['forecast_day_PCT2_change'] < 0
        and regression_data['forecast_day_PCT3_change'] < 0
        and regression_data['forecast_day_PCT3_change'] < regression_data['forecast_day_PCT2_change']
        and low_counter(regression_data) >= 2
        and (regression_data['high'] < regression_data['high_pre1']
             or regression_data['high'] < regression_data['high_pre2']
             or regression_data['high'] < regression_data['high_pre3']
             or regression_data['high'] < regression_data['high_pre4']
             )
        and countLt1 >= 2
        ):
        if(regression_data['low'] < regression_data['low_pre2']):
            if(regression_data['bar_low'] < regression_data['bar_low_pre1']
                and regression_data['bar_low_pre1'] < regression_data['bar_low_pre2']
                and low_counter(regression_data) >= 3
                ):
                return '(shortDownTrend)'
            else:
                return '(shortDownTrend-Risky)'
        if(regression_data['low'] > regression_data['low_pre2']):
            return '(shortDownTrend-MayReversal)'
    if(regression_data['forecast_day_PCT2_change'] < 0
        and regression_data['forecast_day_PCT3_change'] < 0
        and (regression_data['forecast_day_PCT3_change'] < regression_data['forecast_day_PCT2_change']
            or regression_data['forecast_day_PCT4_change'] < regression_data['forecast_day_PCT3_change']
            or regression_data['forecast_day_PCT5_change'] < regression_data['forecast_day_PCT4_change']
            )
        and low_counter(regression_data) >= 2
        and (regression_data['high'] < regression_data['high_pre1']
             or regression_data['high'] < regression_data['high_pre2']
             or regression_data['high'] < regression_data['high_pre3']
             or regression_data['high'] < regression_data['high_pre4']
             )
        and regression_data['month3LowChange'] > 0
        and abs(regression_data['monthHighChange']) > abs(regression_data['monthLowChange'])
        ):
        if(regression_data['monthLowChange'] < 0):
            return '(shortUpTrend-monthLowChangeLT0)' 
        else:
            return '(shortUpTrend-monthLowChangeGT0)'        
    if(pct_day_change_trend(regression_data) <= -3
        ):
        return '(shortDownTrend-Mini)'
    if(regression_data['high'] < regression_data['bar_low_pre1']
        and regression_data['high'] < regression_data['bar_low_pre2']
        #and regression_data['forecast_day_PCT_change'] < 0
        and regression_data['forecast_day_PCT2_change'] < 0
        and regression_data['forecast_day_PCT3_change'] < regression_data['forecast_day_PCT2_change']
        ):
        return '(shortTrendDown)'

    if(regression_data['SMA4'] < -1.5):
        return 'SMA4LT-1.5'
    
    return 'NA'           
    
def pct_change_positive_trend_short(regression_data):
    countGt1, countLt1 = pct_day_change_counter_gt1dot5(regression_data)
    if(regression_data['forecast_day_PCT2_change'] > 0
        and regression_data['forecast_day_PCT3_change'] > 0
        and regression_data['forecast_day_PCT3_change'] > regression_data['forecast_day_PCT2_change']
        and high_counter(regression_data) >= 2
        and (regression_data['low'] > regression_data['low_pre1']
             or regression_data['low'] > regression_data['low_pre2']
             or regression_data['low'] > regression_data['low_pre3']
             or regression_data['low'] > regression_data['low_pre4']
             )
        and countGt1 >= 2
        ):
        if(regression_data['high'] > regression_data['high_pre2']):
            if(regression_data['bar_high'] > regression_data['bar_high_pre1']
                and regression_data['bar_high_pre1'] > regression_data['bar_high_pre2']
                and high_counter(regression_data) >= 3
                ):
                return '(shortUpTrend)'
            else:
                return '(shortUpTrend-Risky)'
        if(regression_data['high'] < regression_data['high_pre2']):
            return '(shortUpTrend-MayReversal)'
    if(regression_data['forecast_day_PCT2_change'] > 0
        and regression_data['forecast_day_PCT3_change'] > 0
        and (regression_data['forecast_day_PCT3_change'] > regression_data['forecast_day_PCT2_change']
             or regression_data['forecast_day_PCT4_change'] > regression_data['forecast_day_PCT3_change']
             or regression_data['forecast_day_PCT5_change'] > regression_data['forecast_day_PCT4_change']
            )
        and high_counter(regression_data) >= 2
        and (regression_data['low'] > regression_data['low_pre1']
             or regression_data['low'] > regression_data['low_pre2']
             or regression_data['low'] > regression_data['low_pre3']
             or regression_data['low'] > regression_data['low_pre4']
             )
        and regression_data['month3HighChange'] < 0
        and abs(regression_data['monthHighChange']) < abs(regression_data['monthLowChange'])
        ):
        if(regression_data['monthHighChange'] < 0):
            return '(shortUpTrend-monthHighChangeLT0)' 
        else:
            return '(shortUpTrend-monthHighChangeGT0)'     
    if(pct_day_change_trend(regression_data) >= 3):
        return '(shortUpTrend-Mini)'
    if(regression_data['low'] > regression_data['bar_high_pre1']
        and regression_data['low'] > regression_data['bar_high_pre2']
        #and regression_data['forecast_day_PCT_change'] > 0
        and regression_data['forecast_day_PCT2_change'] > 0
        and regression_data['forecast_day_PCT3_change'] > regression_data['forecast_day_PCT2_change']
        ):
        return '(shortTrendUp)' 
    
    if(regression_data['SMA4'] > 1.5):
        return 'SMA4GT1.5'
    return 'NA'       

def trend_calculator(regression_data):
    trend = pct_change_positive_trend(regression_data) + '$' + pct_change_negative_trend(regression_data)
    shortTrend = pct_change_positive_trend_short(regression_data) + '$' +  pct_change_negative_trend_short(regression_data)
    #mediumTrend = pct_change_positive_trend_medium(regression_data) + '$' +  pct_change_negative_trend_medium(regression_data)
    
    ser_trend = trend + ':' + shortTrend
    if('(' not in ser_trend):
        ser_trend = ''
        if(regression_data['SMA9'] > 5):
            ser_trend = 'SMA9GT5'
        elif(regression_data['SMA9'] > 1):
            ser_trend = 'SMA9GT1'
        else:
            ser_trend = 'NA'
        
        if(regression_data['SMA9'] < -5):
            ser_trend = ser_trend + '$' + 'SMA9LT-5'
        elif(regression_data['SMA9'] < -1):
            ser_trend = ser_trend + '$' + 'SMA9LT-1'
        else:
            ser_trend = ser_trend + '$' + 'NA'
        
        if(regression_data['SMA4'] > 5):
            ser_trend = ser_trend + ':' + 'SMA4GT5'
        elif(regression_data['SMA4'] > 1):
            ser_trend = ser_trend + ':' + 'SMA4GT1'
        else:
            ser_trend = ser_trend + ':' + 'NA'
        
        if(regression_data['SMA4'] < -5):
            ser_trend = ser_trend + '$' + 'SMA4LT-5'
        elif(regression_data['SMA4'] < -1):
            ser_trend = ser_trend + '$' + 'SMA4LT-1'
        else:
            ser_trend = ser_trend + '$' + 'NA'
        
    return ser_trend 

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

def abs_year2High_more_than_year2Low(regression_data):
    if(regression_data['year2LowChange'] < 0
        or (abs(regression_data['year2HighChange']) - 1 > abs(regression_data['year2LowChange'])
            and regression_data['year2HighChange'] < 0
            )
        ):
        return True;
    else:
        return False;

def abs_year2High_less_than_year2Low(regression_data):
    if(regression_data['year2HighChange'] > 0
        or (abs(regression_data['year2HighChange']) + 1 < abs(regression_data['year2LowChange'])
            and regression_data['year2LowChange'] > 0
            )
        ):
        return True;
    else:
        return False;

def abs_yearHigh_more_than_yearLow(regression_data):
    if(regression_data['yearLowChange'] < 0
        or (abs(regression_data['yearHighChange']) - 1 > abs(regression_data['yearLowChange'])
            and regression_data['yearHighChange'] < 0
            )
        ):
        return True;
    else:
        return False;

def abs_yearHigh_less_than_yearLow(regression_data):
    if(regression_data['yearHighChange'] > 0
        or (abs(regression_data['yearHighChange']) + 1 < abs(regression_data['yearLowChange'])
            and regression_data['yearLowChange'] > 0
            )
        ):
        return True;
    else:
        return False;

def abs_month6High_more_than_month6Low(regression_data):
    if(regression_data['month6LowChange'] < 0
        or (abs(regression_data['month6HighChange']) - 1 > abs(regression_data['month6LowChange'])
            and regression_data['month6HighChange'] < 0
            )
        ):
        return True;
    else:
        return False;

def abs_month6High_less_than_month6Low(regression_data):
    if(regression_data['month6HighChange'] > 0
        or (abs(regression_data['month6HighChange']) + 1 < abs(regression_data['month6LowChange'])
            and regression_data['month6LowChange'] > 0
            )
        ):
        return True;
    else:
        return False;

def abs_month3High_more_than_month3Low(regression_data):
    if(regression_data['month3LowChange'] < 0
        or (abs(regression_data['month3HighChange']) - 1 > abs(regression_data['month3LowChange'])
            and regression_data['month3HighChange'] < 0
            )
        ):
        return True;
    else:
        return False;

def abs_month3High_less_than_month3Low(regression_data):
    if(regression_data['month3HighChange'] > 0
        or (abs(regression_data['month3HighChange']) + 1 < abs(regression_data['month3LowChange'])
            and regression_data['month3LowChange'] > 0
            )
        ):
        return True;
    else:
        return False;

def abs_monthHigh_more_than_monthLow(regression_data):
    if(regression_data['monthLowChange'] < 0
        or (abs(regression_data['monthHighChange']) - 1 > abs(regression_data['monthLowChange'])
            and regression_data['monthHighChange'] < 0
            )
        ):
        return True;
    else:
        return False;

def abs_monthHigh_less_than_monthLow(regression_data):
    if(regression_data['monthHighChange'] > 0
        or (abs(regression_data['monthHighChange']) + 1 < abs(regression_data['monthLowChange'])
            and regression_data['monthLowChange'] > 0
            )
        ):
        return True;
    else:
        return False;
    
def abs_week2High_more_than_week2Low(regression_data):
    if((regression_data['week2LowChange'] < 0 and regression_data['week2HighChange'] > -5)
        or regression_data['week2HighChange'] > -2
        ):
        return False
    elif(regression_data['week2LowChange'] < 0
        or (abs(regression_data['week2HighChange']) - 1 > abs(regression_data['week2LowChange']) 
            and regression_data['week2HighChange'] < 0
            )
        ):
        return True;
    else:
        return False;

def abs_week2High_less_than_week2Low(regression_data):
    if((regression_data['week2HighChange'] > 0 and regression_data['week2LowChange'] < 5)
        or regression_data['week2LowChange'] < 2
        ):
        return False
    
    elif(regression_data['week2HighChange'] > 0
        or (abs(regression_data['week2HighChange']) + 1 < abs(regression_data['week2LowChange'])
            and regression_data['week2LowChange'] > 0
            )
        ):
        return True;
    else:
        return False;

def abs_weekHigh_more_than_weekLow(regression_data):
    if(regression_data['weekLowChange'] < 0
        or (abs(regression_data['weekHighChange']) - 1 > abs(regression_data['weekLowChange']) 
            and regression_data['weekHighChange'] < 0
            )
        ):
        return True;
    else:
        return False;

def abs_weekHigh_less_than_weekLow(regression_data):
    if(regression_data['weekHighChange'] > 0
        or (abs(regression_data['weekHighChange']) + 1 < abs(regression_data['weekLowChange'])
            and regression_data['weekLowChange'] > 0
            )
        ):
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

def bar_low_change_month(regression_data):
    return (regression_data['monthLow'] - regression_data['bar_low'])*100/regression_data['monthLow']
    
def bar_low_change_month3(regression_data):
    return (regression_data['month3Low'] - regression_data['bar_low'])*100/regression_data['month3Low']
    
def bar_high_change_month(regression_data):
    return (regression_data['monthHigh'] - regression_data['bar_high'])*100/regression_data['monthHigh']
    
def bar_high_change_month3(regression_data):
    return (regression_data['month3High'] - regression_data['bar_high'])*100/regression_data['month3High']
    


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
    ws = None
    if((-0.5 < regression_data['PCT_day_change'] < 0.5 and -0.5 < regression_data['PCT_change'] < 0.5)
       or (0 < regression_data['PCT_day_change'] < 1)
       ):
        if(low_tail_pct(regression_data) > 3):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'GLowTail-3pc')
        elif(low_tail_pct(regression_data) > 2):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'GLowTail-2pc')
        elif(low_tail_pct(regression_data) > 1):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'GLowTail-1pc')
    
    if((-0.5 < regression_data['PCT_day_change'] < 0.5 and -0.5 < regression_data['PCT_change'] < 0.5)
       or (-1 < regression_data['PCT_day_change'] < 0)
        ):
        if(high_tail_pct(regression_data) > 3):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'GHighTail-3pc')
        elif(high_tail_pct(regression_data) > 2):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'GHighTail-2pc')
        elif(high_tail_pct(regression_data) > 1):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'GHighTail-1pc')
            
    if(0.75 < regression_data['PCT_day_change'] < 4):
        if(high_tail_pct(regression_data) > 3):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'GHighTail-3pc')
        elif(high_tail_pct(regression_data) > 2):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'GHighTail-2pc')
        elif(high_tail_pct(regression_data) > 1.5):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'GHighTail-1.5pc')
    if(-4 < regression_data['PCT_day_change'] < -0.75):
        if(low_tail_pct(regression_data) > 3):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'GLowTail-3pc')
        elif(low_tail_pct(regression_data) > 2):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'GLowTail-2pc')
        elif(low_tail_pct(regression_data) > 1.5):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'GLowTail-1.5pc')

def tail_pct_filter(regression_data, regressionResult):
#     if(regression_data['PCT_day_change'] > 0):
#         if(high_tail_pct(regression_data) < 0.1):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'HighTailLessThan-0.1pc')
#         if(high_tail_pct(regression_data) < 0.3):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'HighTailLessThan-0.3pc')
#             if(low_tail_pct(regression_data) < 0.1):
#                 add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'LowTailLessThan-0.1pc')
#             if(low_tail_pct(regression_data) < 0.3):
#                 add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'LowTailLessThan-0.3pc')
#     if(regression_data['PCT_day_change'] < 0):
#         if(low_tail_pct(regression_data) < 0.1):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'LowTailLessThan-0.1pc')
#         if(low_tail_pct(regression_data) < 0.3):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'LowTailLessThan-0.3pc')
#             if(high_tail_pct(regression_data) < 0.1):
#                 add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'HighTailLessThan-0.1pc')
#             if(high_tail_pct(regression_data) < 0.3):
#                 add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'HighTailLessThan-0.3pc')
#    high_tail_pct_filter(regression_data, regressionResult)
    return False

def tail_reversal_filter(regression_data, regressionResult):
    ws = None
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
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(MayBuy-CheckChart)-1', None)
    elif(-5 < regression_data['PCT_day_change'] < -1
        and 4 > low_tail_pct(regression_data) >= 1.49 and high_tail_pct(regression_data) <= 0.8):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(MayBuy-CheckChart)-1-Risky', None)
    elif(-6 < regression_data['PCT_day_change'] < -1.5
        and 3 > low_tail_pct(regression_data) >= 0.99 and high_tail_pct(regression_data) <= 0.6):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(MayBuy-CheckChart)-2', None)
    elif(-6 < regression_data['PCT_day_change'] < -1
        and 3 > low_tail_pct(regression_data) >= 0.99 and high_tail_pct(regression_data) <= 0.6):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(MayBuy-CheckChart)-2-Risky', None)
            
    if(1.5 < regression_data['PCT_day_change'] < 5
        and 4 > high_tail_pct(regression_data) >= 1.49 and low_tail_pct(regression_data) <= 0.8):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(MaySell-CheckChart)-1', None) 
    elif(1 < regression_data['PCT_day_change'] < 5
        and 4 > high_tail_pct(regression_data) >= 1.49 and low_tail_pct(regression_data) <= 0.8):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(MaySell-CheckChart)-1-Risky', None)   
    elif(1.5 < regression_data['PCT_day_change'] < 6
        and 3 > high_tail_pct(regression_data) >= 0.99 and low_tail_pct(regression_data) <= 0.6):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(MaySell-CheckChart)-2', None)
    elif(1 < regression_data['PCT_day_change'] < 6
        and 3 > high_tail_pct(regression_data) >= 0.99 and low_tail_pct(regression_data) <= 0.6):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(MaySell-CheckChart)-2-Risky', None)
    
    if(-4 < regression_data['PCT_day_change'] < -1.5 and -4 < regression_data['PCT_change'] < -1.5
        ):
        if(3.5 > low_tail_pct(regression_data) > 1.8):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(MayBuyCheckChart-Strong(check-chart-MarketNotUp2-3))', None)
        elif(low_tail_pct(regression_data) > 1.8 and regression_data['PCT_day_change'] < -2):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(MayBuyCheckChart-Strong(check-chart-MarketNotUp2-3))', None)
    elif(-4 < regression_data['PCT_day_change'] < 1 and -4 < regression_data['PCT_change'] < 1
        ):
        if(3.5 > low_tail_pct(regression_data) > 1.8):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(MayBuyCheckChart(check-chart-MarketNotUp2-3))', None)
        elif(low_tail_pct(regression_data) > 1.8 and regression_data['PCT_day_change'] < -2):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(MayBuyCheckChart(check-chart-MarketNotUp2-3))', None)
    
    if(1.5 < regression_data['PCT_day_change'] < 4 and 1.5 < regression_data['PCT_change'] < 4
        ):
        if(3.5 > high_tail_pct(regression_data) > 1.8):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(MaySellCheckChart-Strong(check-chart-MarketNotDown2-3))', None)
        if(high_tail_pct(regression_data) > 1.8 and regression_data['PCT_day_change'] > 2):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(MaySellCheckChart-Strong(check-chart-MarketNotDown2-3))', None)
    elif(-1 < regression_data['PCT_day_change'] < 4 and -1 < regression_data['PCT_change'] < 4
        ):
        if(3.5 > high_tail_pct(regression_data) > 1.8):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(MaySellCheckChart(check-chart-MarketNotDown2-3))', None)
        elif(high_tail_pct(regression_data) > 1.8 and regression_data['PCT_day_change'] > 2):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '(MaySellCheckChart(check-chart-MarketNotDown2-3))', None)
        
    if(('MayBuy-CheckChart' in regression_data['filter1']) 
        or ('MayBuyCheckChart' in regression_data['filter1'])
        ):
        if(
            (low_tail_pct(regression_data) > 1.8)
            and low_tail_pct(regression_data) < abs(regression_data['PCT_change'])
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Strong', None)
    if(('MaySell-CheckChart' in regression_data['filter1']) 
        or ('MaySellCheckChart' in regression_data['filter1'])
        ):
        if(
            (high_tail_pct(regression_data) > 1.8)
            and high_tail_pct(regression_data) < abs(regression_data['PCT_change'])
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Strong', None)

def base_change_filter(regression_data, regressionResult, save=False):
    filterName = ""
    if(regression_data['year2HighChange'] > 0):
        filterName = filterName + ':' + 'AtYear2High'
    elif(regression_data['year2HighChange'] < 0 and regression_data['year2LowChange'] > 0 and abs(regression_data['year2HighChange']) < abs(regression_data['year2LowChange'])):
        filterName = filterName + ':' + 'AtAboveYear2Midline'
    elif(regression_data['year2HighChange'] < 0 and regression_data['year2LowChange'] > 0 and abs(regression_data['year2HighChange']) > abs(regression_data['year2LowChange'])):
        filterName = filterName + ':' + 'AtBelowYear2Midline'
    elif(regression_data['year2LowChange'] < 0):
        filterName = filterName + ':' + 'AtYear2Low'
     
    if(regression_data['yearHighChange'] > 0):
        filterName = filterName + ':' + 'AtYearHigh'        
    elif(regression_data['yearHighChange'] < 0 and regression_data['yearLowChange'] > 0 and abs(regression_data['yearHighChange']) < abs(regression_data['yearLowChange'])):
        filterName = filterName + ':' + 'AtAboveYearMidline'
    elif(regression_data['yearHighChange'] < 0 and regression_data['yearLowChange'] > 0 and abs(regression_data['yearHighChange']) > abs(regression_data['yearLowChange'])):
        filterName = filterName + ':' + 'AtBelowYearMidline'
    elif(regression_data['yearLowChange'] < 0):
        filterName = filterName + ':' + 'AtYearLow'
    
    if(regression_data['month6HighChange'] > 0):
        filterName = filterName + ':' + 'AtMonth6High'     
    elif(regression_data['month6HighChange'] < 0 and regression_data['month6LowChange'] > 0 and abs(regression_data['month6HighChange']) < abs(regression_data['month6LowChange'])):
        filterName = filterName + ':' + 'AtAboveMonth6Midline'
    elif(regression_data['month6HighChange'] < 0 and regression_data['month6LowChange'] > 0 and abs(regression_data['month6HighChange']) > abs(regression_data['month6LowChange'])):
        filterName = filterName + ':' + 'AtBelowMonth6Midline'
    elif(regression_data['month6LowChange'] < 0):
        filterName = filterName + ':' + 'AtMonth6Low'
    
    if(regression_data['month3HighChange'] > 0 ):
        filterName = filterName + ':' + 'AtMonth3High'    
    elif(regression_data['month3HighChange'] < 0 and regression_data['month3LowChange'] > 0 and abs(regression_data['month3HighChange']) < abs(regression_data['month3LowChange'])):
        filterName = filterName + ':' + 'AtAboveMonth3Midline'
    elif(regression_data['month3HighChange'] < 0 and regression_data['month3LowChange'] > 0 and abs(regression_data['month3HighChange']) > abs(regression_data['month3LowChange'])):
        filterName = filterName + ':' + 'AtBelowMonth3Midline'
    elif(regression_data['month3LowChange'] < 0):
        filterName = filterName + ':' + 'AtMonth3Low'
    
    if(regression_data['monthHighChange'] > 0 ):
        filterName = filterName + ':' + 'AtMonthHigh'
    elif(regression_data['monthHighChange'] < 0 and regression_data['monthLowChange'] > 0 and abs(regression_data['monthHighChange']) < abs(regression_data['monthLowChange'])):
        filterName = filterName + ':' + 'AtAboveMonthMidline'
    elif(regression_data['monthHighChange'] < 0 and regression_data['monthLowChange'] > 0 and abs(regression_data['monthHighChange']) > abs(regression_data['monthLowChange'])):
        filterName = filterName + ':' + 'AtBelowMonthMidline'
    elif(regression_data['monthLowChange'] < 0):
        filterName = filterName + ':' + 'AtMonthLow'
    
    return filterName

def pct_change_filter(regression_data, regressionResult, save=False):
    filterName = ''
    if(regression_data['PCT_change'] < 0 and regression_data['PCT_day_change'] <= 0):
        if(regression_data['PCT_change'] < -16):
            filterName = 'PCTChangeLT-16'
        elif(regression_data['PCT_change'] < -12):
            filterName = 'PCTChangeLT-12'
        elif(regression_data['PCT_change'] < -8):
            filterName = 'PCTChangeLT-8'
        elif(regression_data['PCT_change'] < -5):
            filterName = 'PCTChangeLT-5'
        elif(regression_data['PCT_change'] < -3):
            filterName = 'PCTChangeLT-3'
        elif(regression_data['PCT_change'] < -2):
            filterName = 'PCTChangeLT-2'
        elif(regression_data['PCT_change'] < -1):
            filterName = 'PCTChangeLT-1'
        elif(regression_data['PCT_change'] < -0.5):
            filterName = 'PCTChangeLT-0.5'
        else:
            filterName = 'PCTDayChangeLT0'
    elif(regression_data['PCT_change'] > 0 and regression_data['PCT_day_change'] >= 0):
        if(regression_data['PCT_change'] > 16):
            filterName = 'PCTChangeGT16'
        elif(regression_data['PCT_change'] > 12):
            filterName = 'PCTChangeGT12'
        elif(regression_data['PCT_change'] > 8):
            filterName = 'PCTChangeGT8'
        elif(regression_data['PCT_change'] > 5):
            filterName = 'PCTChangeGT5'
        elif(regression_data['PCT_change'] > 3):
            filterName = 'PCTChangeGT3'
        elif(regression_data['PCT_change'] > 2):
            filterName = 'PCTChangeGT2'
        elif(regression_data['PCT_change'] > 1):
            filterName = 'PCTChangeGT1'
        elif(regression_data['PCT_change'] > 0.5):
            filterName = 'PCTChangeGT0.5'
        else:
            filterName = 'PCTChangeGT0'
    elif(regression_data['PCT_change'] == 0):
        filterName = 'PCTChangeEQ0'
    elif(regression_data['PCT_change'] < 0 and regression_data['PCT_day_change'] > 0):
        if(regression_data['PCT_change'] < -16):
            filterName = 'PCDCGT0PCTChangeLT-16'
        elif(regression_data['PCT_change'] < -8):
            filterName = 'PCDCGT0PCTChangeLT-8'
        elif(regression_data['PCT_change'] < -5):
            filterName = 'PCDCGT0PCTChangeLT-5'
        elif(regression_data['PCT_change'] < -3):
            filterName = 'PCDCGT0PCTChangeLT-3'
        elif(regression_data['PCT_change'] < -1):
            filterName = 'PCDCGT0PCTChangeLT-1'
        else:
            filterName = 'PCDCGT0PCTDayChangeLT0'
    elif(regression_data['PCT_change'] > 0 and regression_data['PCT_day_change'] < 0):
        if(regression_data['PCT_change'] > 16):
            filterName = 'PCDCLT0PCTChangeGT16'
        elif(regression_data['PCT_change'] > 8):
            filterName = 'PCDCLT0PCTChangeGT8'
        elif(regression_data['PCT_change'] > 5):
            filterName = 'PCDCLT0PCTChangeGT5'
        elif(regression_data['PCT_change'] > 3):
            filterName = 'PCDCLT0PCTChangeGT3'
        elif(regression_data['PCT_change'] > 1):
            filterName = 'PCDCLT0PCTChangeGT1'
        else:
            filterName = 'PCDCLT0PCTChangeGT0'
            
    if(-0.5 < regression_data['PCT_day_change'] < 0):
        filterName = filterName + ',PCDayChange-0.5to0.5'
    elif(0 < regression_data['PCT_day_change'] < 0.5):
        filterName = filterName + ',PCDayChange-0.5to0.5'
        
#     if(regression_data['SMA4'] > regression_data['SMA4_2daysBack']):
#         filterName = filterName + ',SMA4GT2DaysBack'
#     else:
#         filterName = filterName + ',SMA4LT2DaysBack'
#         
#     if(regression_data['SMA9'] > regression_data['SMA9_2daysBack']):
#         filterName = filterName + ',SMA9GT2DaysBack'
#     else:
#         filterName = filterName + ',SMA9LT2DaysBack'
        
#     if(regression_data['EMA14'] > regression_data['EMA14_2daysBack']):
#         filterName = filterName + ',EMA14GT2DaysBack'
#     else:
#         filterName = filterName + ',EMA14LT2DaysBack'
        
    if(regression_data['year2HighChange'] > 0):
        filterName = filterName + ',year2High'
    elif(regression_data['year2LowChange'] < 0):
        filterName = filterName + ',year2Low'
        
        
    return filterName

def pct_change_filter_days(regression_data, regressionResult, save=False):
    filterName = ''
    if(regression_data['forecast_day_PCT5_change'] < 0):
        if(regression_data['forecast_day_PCT5_change'] < -20):
            filterName = 'PCTDays5ChangeLT-20'
        elif(regression_data['forecast_day_PCT5_change'] < -15):
            filterName = 'PCTDays5ChangeLT-15'
        elif(regression_data['forecast_day_PCT5_change'] < -10):
            filterName = 'PCTDays5ChangeLT-10'
        elif(regression_data['forecast_day_PCT5_change'] < -5):
            filterName = 'PCTDays5ChangeLT-5'
        else:
            filterName = 'PCTDays5ChangeLT0'
    elif(regression_data['forecast_day_PCT5_change'] > 0):
        if(regression_data['forecast_day_PCT5_change'] > 20):
            filterName = 'PCTDays5ChangeGT+20'
        elif(regression_data['forecast_day_PCT5_change'] > 15):
            filterName = 'PCTDays5ChangeGT+15'
        elif(regression_data['forecast_day_PCT5_change'] > 10):
            filterName = 'PCTDays5ChangeGT+10'
        elif(regression_data['forecast_day_PCT5_change'] > 5):
            filterName = 'PCTDays5ChangeGT+5'
        else:
            filterName = 'PCTDays5ChangeGT0'
    elif(regression_data['forecast_day_PCT5_change'] == 0):
        filterName = 'PCTDays5ChangeEq0'
        
    return filterName

def tail_change_filter(regression_data, regressionResult, save=False):
    filterTail = ''
    
    if(high_tail_pct(regression_data) > 3.0):
        filterTail = filterTail + '_HTGT3.0_'
    elif(high_tail_pct(regression_data) > 1.5):
        filterTail = filterTail + '_HTGT1.5_'
#     elif(high_tail_pct(regression_data) > 0.5):
#         filterTail = filterTail + '_HTGT0.5_'
        
#     elif(high_tail_pct(regression_data) > 2.5):
#         filterTail = filterTail + 'HTGT2.5'
#     elif(high_tail_pct(regression_data) > 1.5):
#         filterTail = filterTail + 'HTGT1.5'
#     elif(high_tail_pct(regression_data) < 1):
#         filterTail = filterTail + 'HTLT1'
        
    
    if(low_tail_pct(regression_data) > 3.0):
        filterTail = filterTail + '_LTGT3.0_'
    elif(low_tail_pct(regression_data) > 1.5):
        filterTail = filterTail + '_LTGT1.5_'
#     elif(low_tail_pct(regression_data) > 0.5):
#         filterTail = filterTail + '_LTGT0.5_'
#     elif(low_tail_pct(regression_data) > 2.5):
#         filterTail = filterTail + 'LTGT2.5'
#     elif(low_tail_pct(regression_data) > 1.5):
#         filterTail = filterTail + 'LTGT1.5'
#     elif(low_tail_pct(regression_data) < 1):
#         filterTail = filterTail + 'LTLT1'
    
    if(abs(regression_data['PCT_day_change']) > 1
        and (high_tail_pct(regression_data) > 1.5 or high_tail_pct(regression_data) > 1.5)
        ):
        if(high_tail_pct(regression_data) > abs(regression_data['PCT_day_change'])):
            filterTail = filterTail + '_HTGTPCTDayChange_'    
        if(low_tail_pct(regression_data) > abs(regression_data['PCT_day_change'])):
            filterTail = filterTail + '_LTGTPCTDayChange_'
            
    return filterTail

def tail2_change_filter(regression_data, regressionResult, save):
    filterTail = ''
    
    if(high_tail_pct(regression_data) > 3.5):
        filterTail = filterTail + 'HTGT3.5,'
    elif(high_tail_pct(regression_data) > 2.5):
        filterTail = filterTail + 'HTGT2.5,'
    elif(high_tail_pct(regression_data) > 1.3):
        filterTail = filterTail + 'HTGT1.3,'
    if(high_tail_pct(regression_data) > abs(regression_data['PCT_day_change']) 
        and high_tail_pct(regression_data) > 1.5
        ):
        filterTail = filterTail + 'HTGTPCTDayChange'

    if(low_tail_pct(regression_data) > 3.5):
        filterTail = filterTail + 'LTGT3.5,'
    elif(low_tail_pct(regression_data) > 2.5):
        filterTail = filterTail + 'LTGT2.5,'
    elif(low_tail_pct(regression_data) > 1.3):
        filterTail = filterTail + 'LTGT1.3,'
    if(low_tail_pct(regression_data) > abs(regression_data['PCT_day_change']) 
        and low_tail_pct(regression_data) > 1.5
        ):
        filterTail = filterTail + 'LTGTPCTDayChange'

    return filterTail
        
def filterMA(regression_data, regressionResult):
    ws = None
    ema_diff = regression_data['ema6-14']
    ema_diff_pre1 = regression_data['ema6-14_pre1']
    ema_diff_pre2 = regression_data['ema6-14_pre2']
    
    if(ema_diff > 0
       and ema_diff_pre1 < 0
       and ema_diff_pre2 < 0
       and ema_diff_pre2 < ema_diff_pre1
       ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '(Confirmed)EMA6>EMA14')
        
    if(ema_diff < 0
       and ema_diff_pre1 > 0
       and ema_diff_pre2 > 0
       and ema_diff_pre2 > ema_diff_pre1
       ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '(Confirmed)EMA6<EMA14')
        
        
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
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '(May)EMA6-MT-May-LT-EMA14')
        
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
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '(May)EMA6-LT-May-MT-EMA14')
    
    if(is_ema6_sliding_up(regression_data)):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@EMA6Up@e@')
    elif(is_ema6_sliding_down(regression_data)):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@EMA6Down@e@')
    if(is_ema14_sliding_up(regression_data)):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@EMA14Up@e@')
    elif(is_ema14_sliding_down(regression_data)):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@EMA14Down@e@')
    
    if(regression_data['SMA4_2daysBack']) < -5:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA4BD2LT-5@e@')
    elif(regression_data['SMA4_2daysBack']) < 0:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA4BD2LT0@e@')
    elif(regression_data['SMA4_2daysBack']) > 5:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA4BD2GT5@e@')
    elif(regression_data['SMA4_2daysBack']) > 0:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA4BD2GT0@e@')
    
    if(regression_data['SMA9_2daysBack']) < -5:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA9BD2LT-5@e@')
    elif(regression_data['SMA9_2daysBack']) < 0:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA9BD2LT0@e@')
    elif(regression_data['SMA9_2daysBack']) > 5:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA9BD2GT5@e@')
    elif(regression_data['SMA9_2daysBack']) > 0:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA9BD2GT0@e@')
    
    if(regression_data['SMA4']) < -5:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA4LT-5@e@')
    elif(regression_data['SMA4']) < 0:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA4LT0@e@')
    elif(regression_data['SMA4']) > 5:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA4GT5@e@')
    elif(regression_data['SMA4']) > 0:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA4GT0@e@')
    
    if(regression_data['SMA9']) < -5:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA9LT-5@e@')
    elif(regression_data['SMA9']) < 0:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA9LT0@e@')
    elif(regression_data['SMA9']) > 5:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA9GT5@e@')
    elif(regression_data['SMA9']) > 0:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA9GT0@e@')
    
    if(regression_data['SMA25']) < -10:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA25LT-10@e@')
    elif(regression_data['SMA25']) < 0:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA25LT0@e@')
    elif(regression_data['SMA25']) > 10:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA25GT10@e@')
    elif(regression_data['SMA25']) > 0:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA25GT0@e@')
    
    if(regression_data['SMA50']) < -10:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA50LT-10@e@')
    elif(regression_data['SMA50']) < 0:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA50LT0@e@')
    elif(regression_data['SMA50']) > 10:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA50GT10@e@')
    elif(regression_data['SMA50']) > 0:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA50GT0@e@')
    
    if(regression_data['SMA100']) < -20:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA100LT-20@e@')
    elif(regression_data['SMA100']) < 0:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA100LT0@e@')
    elif(regression_data['SMA100']) > 20:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA100GT20@e@')
    elif(regression_data['SMA100']) > 0:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA100GT0@e@')
    
    if(regression_data['SMA200']) < -20:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA200LT-20@e@')
    elif(regression_data['SMA200']) < 0:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA200LT0@e@')
    elif(regression_data['SMA200']) > 20:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA200GT20@e@')
    elif(regression_data['SMA200']) > 0:
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '@s@SMA200GT0@e@')
            
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
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '$$(Study)$$:RisingMA-Confirm')
        elif((regression_data['SMA9'] > 1 or regression_data['SMA4'] > 1)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '$$(Study)$$:RisingMA')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '$$(Study)$$:RisingMA-Risky')
        
#         if(-5 < regression_data['SMA25'] < 0):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '##LONGTERM:NearSMA25')
#         elif(0 < regression_data['SMA25'] < 5):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '##LONGTERM:CrossoverSMA25')
#         elif(-5 < regression_data['SMA50'] < 0):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '##MEDIUMTERM:NearSMA50')
#         elif(0 < regression_data['SMA50'] < 5):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '##MEDIUMTERM:CrossoverSMA50')
#         elif(-5 < regression_data['SMA100'] < 0):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '##SHORTTERM:NearSMA100')
#         elif(0 < regression_data['SMA100'] < 5):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '##SHORTTERM:CrossoverSMA100')  
        
    elif(regression_data['SMA200'] < regression_data['SMA100'] < regression_data['SMA50'] < regression_data['SMA25'] < 0
         and (regression_data['SMA9'] > 0 or regression_data['SMA4'] > 0)
        ):
        if(regression_data['SMA9'] > 0 and regression_data['SMA4'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, 'SMA9&SMA4GT0')
        elif(regression_data['SMA9'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, 'SMA9GT0')
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '$$(Study)$$:NegativeMA')
    elif(regression_data['SMA200'] < regression_data['SMA100'] < regression_data['SMA50'] < regression_data['SMA25'] < 0
         and regression_data['SMA9'] < 0
         and regression_data['SMA4'] < 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '$$(Study)$$:AllNegativeMA')
    elif(regression_data['SMA200'] > 0
         and regression_data['SMA100'] > 0 
         and regression_data['SMA50'] > 0
         and (regression_data['SMA9'] < 1 and regression_data['SMA4'] < 1)
         and (regression_data['SMA9'] < -1 or regression_data['SMA4'] < -1
              or (regression_data['SMA9'] < 0 or regression_data['SMA4'] < 0))
         ):
        if(is_ema14_sliding_down(regression_data)):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '$$(Study)$$:DowningMA-Confirm')
        elif((regression_data['SMA9'] < -1 or regression_data['SMA4'] < -1)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '$$(Study)$$:DowningMA')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '$$(Study)$$:DowningMA-Risky')
        
#         if(-5 < regression_data['SMA25'] < 0):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '##LONGTERM:NearSMA25')
#         elif(0 < regression_data['SMA25'] < 5):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '##LONGTERM:CrossoverSMA25')
#         elif(-5 < regression_data['SMA50'] < 0):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '##MEDIUMTERM:NearSMA50')
#         elif(0 < regression_data['SMA50'] < 5):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '##MEDIUMTERM:CrossoverSMA50')
#         elif(-5 < regression_data['SMA100'] < 0):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '##SHORTTERM:NearSMA100')
#         elif(0 < regression_data['SMA100'] < 5):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '##SHORTTERM:CrossoverSMA100')
    elif(regression_data['SMA200'] > regression_data['SMA100'] > regression_data['SMA50'] > regression_data['SMA25'] > 0
        and (regression_data['SMA9'] < 0 or regression_data['SMA4'] < 0)
        ):
        if(regression_data['SMA9'] < 0 and regression_data['SMA4'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, 'SMA9&SMA4LT0')
        elif(regression_data['SMA9'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, 'SMA9LT0')
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '$$(Study)$$:PositiveMA')
    elif(regression_data['SMA200'] > regression_data['SMA100'] > regression_data['SMA50'] > regression_data['SMA25'] > 0
         and regression_data['SMA9'] > 0
         and regression_data['SMA4'] > 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '$$(Study)$$:AllPositiveMA')
#    else:
#         if(-5 < regression_data['SMA25'] < 0):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '##LONGTERM:NearSMA25')
#         elif(0 < regression_data['SMA25'] < 5):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '##LONGTERM:CrossoverSMA25')
#         elif(-5 < regression_data['SMA50'] < 0):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '##MEDIUMTERM:NearSMA50')
#         elif(0 < regression_data['SMA50'] < 5):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '##MEDIUMTERM:CrossoverSMA50')
#         elif(-5 < regression_data['SMA100'] < 0):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '##SHORTTERM:NearSMA100')
#         elif(0 < regression_data['SMA100'] < 5):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, '##SHORTTERM:CrossoverSMA100')
         
def base_line(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    
    
    if((-10 < regression_data['month3HighChange'] < 0) 
        and (regression_data['month3LowChange'] > 15)
        ):
        if(regression_data['month3High'] == regression_data['monthHigh']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Recent)')
        if((regression_data['monthHighChange'] == regression_data['week2HighChange']) and regression_data['week2HighChange'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Oldest)')
        if(regression_data['weekHigh'] > regression_data['week2High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(weekHighGTweek2High)')
        
        if(regression_data['month3HighChange'] < -7):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighMonth3LT-7')
        elif(regression_data['month3HighChange'] < -5):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighMonth3LT-5')
        elif(regression_data['month3HighChange'] < -2):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighMonth3LT-2')
        elif(regression_data['month3HighChange'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighMonth3LT0')
        
        if(regression_data['week2HighChange'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'NearHighMonth3')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'ReversalHighMonth3')
    
    elif((-10 < regression_data['monthHighChange'] < 0) 
        and (regression_data['month3HighChange'] < -7.5) 
        and (regression_data['monthLowChange'] > 5)
        and (regression_data['monthLowChange'] > 10 or regression_data['month3LowChange'] > 10)
        and abs_monthHigh_less_than_monthLow(regression_data)
        ):
        if(regression_data['monthHigh'] == regression_data['week2High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Recent)')
        if(regression_data['week2HighChange'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Oldest)')
        if(regression_data['weekHigh'] > regression_data['week2High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(weekHighGTweek2High)')
        
        if(regression_data['monthHighChange'] < -7):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighMonthLT-7')
        elif(regression_data['monthHighChange'] < -5):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighMonthLT-5')
        elif(regression_data['monthHighChange'] < -2):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighMonthLT-2')
        elif(regression_data['monthHighChange'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighMonthLT0')
        
        if(regression_data['week2HighChange'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'NearHighMonth')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'ReversalHighMonth')
    
    if((0 < regression_data['month3LowChange'] < 10)
        and (regression_data['month6LowChange'] > 7.5)
        and (regression_data['month3HighChange'] < -15)
        ):
        if(regression_data['month3Low'] == regression_data['monthLow']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Recent)')
        if((regression_data['monthLowChange'] == regression_data['week2LowChange']) and regression_data['week2LowChange'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Oldest)')
        if(regression_data['weekLow'] < regression_data['week2Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(weekLowLTweek2Low)')
        
        if(regression_data['month3LowChange'] > 7):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowMonth3GT7')
        elif(regression_data['month3LowChange'] > 5):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowMonth3GT5')
        elif(regression_data['month3LowChange'] > 2):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowMonth3GT2')
        elif(regression_data['month3LowChange'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowMonth3GT0')
        
        if(regression_data['week2LowChange'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'NearLowMonth3')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'ReversalLowMonth3')
    elif((0 < regression_data['monthLowChange'] < 10)
        and (regression_data['month3LowChange'] > 7.5)
        and (regression_data['monthHighChange'] < -5)
        and (regression_data['monthHighChange'] < -10 or regression_data['month3HighChange'] < -10)
        and abs_monthHigh_more_than_monthLow(regression_data)
        ):
        if(regression_data['monthLow'] == regression_data['week2Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Recent)')
        if(regression_data['week2LowChange'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Oldest)')
        if(regression_data['weekLow'] < regression_data['week2Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(weekLowLTweek2Low)')
        
        if(regression_data['monthLowChange'] > 7):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowMonthGT7')
        elif(regression_data['monthLowChange'] > 5):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowMonthGT5')
        elif(regression_data['monthLowChange'] > 2):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowMonthGT2')
        elif(regression_data['monthLowChange'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowMonthGT0')
            
        if(regression_data['week2LowChange'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'NearLowMonth')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'ReversalLowMonth')
    
    
    
    if((0 < regression_data['year2HighChange']) 
        and (regression_data['year2LowChange'] > 40)
        ):
        if(regression_data['year2High'] == regression_data['month6High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Recent)')
        if(regression_data['weekHigh'] > regression_data['week2High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(weekHighGTweek2High)')
        
        if(regression_data['year2HighChange'] > 10):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighYear2GT10')
        elif(regression_data['year2HighChange'] > 7):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighYear2GT7')
        elif(regression_data['year2HighChange'] > 5):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighYear2GT5')
        elif(regression_data['year2HighChange'] > 2):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighYear2GT2')
        elif(regression_data['year2HighChange'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighYear2GT0')
            
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'BreakHighYear2')
        
    elif((0 < regression_data['yearHighChange']) 
        and (regression_data['yearLowChange'] > 30)
        ):
        if(regression_data['yearHigh'] == regression_data['month3High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Recent)')
        if(regression_data['weekHigh'] > regression_data['week2High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(weekHighGTweek2High)')
        
        if(regression_data['yearHighChange'] > 10):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighYearGT10')
        elif(regression_data['yearHighChange'] > 7):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighYearGT7')
        elif(regression_data['yearHighChange'] > 5):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighYearGT5')
        elif(regression_data['yearHighChange'] > 2):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighYearGT2')
        elif(regression_data['yearHighChange'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighYearGT0')
            
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'BreakHighYear')
            
    elif((0 < regression_data['month6HighChange'])
        and (regression_data['month6LowChange'] > 20)
        ):
        if(regression_data['month6High'] == regression_data['month3High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Recent)')
        if(regression_data['weekHigh'] > regression_data['week2High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(weekHighGTweek2High)')
        
        if(regression_data['month6HighChange'] > 10):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighMonth6GT10')
        elif(regression_data['month6HighChange'] > 7):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighMonth6GT7')
        elif(regression_data['month6HighChange'] > 5):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighMonth6GT5')
        elif(regression_data['month6HighChange'] > 2):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighMonth6GT2')
        elif(regression_data['month6HighChange'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighMonth6GT0')
            
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'BreakHighMonth6')
                
    elif((0 < regression_data['month3HighChange']) 
        and (regression_data['month3LowChange'] > 15)
        ):
        if(regression_data['month3High'] == regression_data['monthHigh']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Recent)')
        if(regression_data['weekHigh'] > regression_data['week2High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(weekHighGTweek2High)')
        
        if(regression_data['month3HighChange'] > 10):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighMonth3GT10')
        elif(regression_data['month3HighChange'] > 7):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighMonth3GT7')
        elif(regression_data['month3HighChange'] > 5):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighMonth3GT5')
        elif(regression_data['month3HighChange'] > 2):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighMonth3GT2')
        elif(regression_data['month3HighChange'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighMonth3GT0')
           
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'BreakHighMonth3')
    elif((0 < regression_data['monthHighChange'] < 10)
        and (regression_data['month3HighChange'] < -7.5)   
        and (regression_data['monthLowChange'] > 5)
        and (regression_data['monthLowChange'] > 10 or regression_data['month3LowChange'] > 10)
        and abs_monthHigh_less_than_monthLow(regression_data)
        ):
        if(regression_data['monthHigh'] == regression_data['week2High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Recent)')
        if(regression_data['weekHigh'] > regression_data['week2High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(weekHighGTweek2High)')
        
        if(regression_data['monthHighChange'] > 7):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighMonthGT7')
        elif(regression_data['monthHighChange'] > 5):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighMonthGT5')
        elif(regression_data['monthHighChange'] > 2):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighMonthGT2')
        elif(regression_data['monthHighChange'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighMonthGT0')
            
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'BreakHighMonth')     
    
    
    
    if((regression_data['year2LowChange'] < 0) 
        and (regression_data['year2HighChange'] < -40)
        ):
        if(regression_data['year2Low'] == regression_data['month6Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Recent)')
        if(regression_data['weekLow'] < regression_data['week2Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(weekLowLTweek2Low)')
            
        if(regression_data['year2LowChange'] < -10):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowYear2LT-10')
        elif(regression_data['year2LowChange'] < -7):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowYear2LT-7')
        elif(regression_data['year2LowChange'] < -5):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowYear2LT-5')
        elif(regression_data['year2LowChange'] < -2):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowYear2LT-2')
        elif(regression_data['year2LowChange'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowYear2LT0')    
            
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'BreakLowYear2')
        
    elif((regression_data['yearLowChange'] < 0) 
        and (regression_data['year2LowChange'] > 20)
        and (regression_data['yearHighChange'] < -30)
        ):
        if(regression_data['yearLow'] == regression_data['month3Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Recent)')
        if(regression_data['weekLow'] < regression_data['week2Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(weekLowLTweek2Low)')
            
        if(regression_data['yearLowChange'] < -10):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowYearLT-10')
        elif(regression_data['yearLowChange'] < -7):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowYearLT-7')
        elif(regression_data['yearLowChange'] < -5):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowYearLT-5')
        elif(regression_data['yearLowChange'] < -2):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowYearLT-2')
        elif(regression_data['yearLowChange'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowYearLT0')
            
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'BreakLowYear')
        
    elif((regression_data['month6LowChange'] < 0)
        and (regression_data['yearLowChange'] > 20)
        and (regression_data['month6HighChange'] < -20)
        ):
        if(regression_data['month6Low'] == regression_data['month3Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Recent)')
        if(regression_data['weekLow'] < regression_data['week2Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(weekLowLTweek2Low)')
            
        if(regression_data['month6LowChange'] < -10):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowMonth6LT-10')
        elif(regression_data['month6LowChange'] < -7):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowMonth6LT-7')
        elif(regression_data['month6LowChange'] < -5):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowMonth6LT-5')
        elif(regression_data['month6LowChange'] < -2):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowMonth6LT-2')
        elif(regression_data['month6LowChange'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowMonth6LT0')
            
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'BreakLowMonth6')
        
    elif((regression_data['month3LowChange'] < 0)
        and (regression_data['month6LowChange'] > 10)
        and (regression_data['yearLowChange'] > 20)
        and (regression_data['month3HighChange'] < -15)
        ):
        if(regression_data['month3Low'] == regression_data['monthLow']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Recent)')
        if(regression_data['weekLow'] < regression_data['week2Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(weekLowLTweek2Low)')
            
        if(regression_data['month3LowChange'] < -10):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowMonth3LT-10')
        elif(regression_data['month3LowChange'] < -7):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowMonth3LT-7')
        elif(regression_data['month3LowChange'] < -5):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowMonth3LT-5')
        elif(regression_data['month3LowChange'] < -2):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowMonth3LT-2')
        elif(regression_data['month3LowChange'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowMonth3LT0')
            
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'BreakLowMonth3')
        
    elif((-10 < regression_data['monthLowChange'] < 0)
        and (regression_data['month3LowChange'] > 7.5)
        #and (regression_data['yearLowChange'] > 20)
        and (regression_data['monthHighChange'] < -5)
        and (regression_data['monthHighChange'] < -10 or regression_data['month3HighChange'] < -10)
        and abs_monthHigh_more_than_monthLow(regression_data)
        ):
        if(regression_data['monthLow'] == regression_data['week2Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Recent)')
        if(regression_data['weekLow'] < regression_data['week2Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(weekLowLTweek2Low)')
            
        if(regression_data['monthLowChange'] < -7):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowMonthLT-7')
        elif(regression_data['monthLowChange'] < -5):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowMonthLT-5')
        elif(regression_data['monthLowChange'] < -2):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowMonthLT-2')
        elif(regression_data['monthLowChange'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowMonthLT0')
            
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'BreakLowMonth')
        
    
    if((-10 < regression_data['year2HighChange'] < 0) 
        and (regression_data['year2LowChange'] > 40)
        and (regression_data['year2High'] == regression_data['month6High']
            or ((regression_data['month3HighChange'] == regression_data['monthHighChange']) and (regression_data['monthHighChange'] == regression_data['week2HighChange']) and regression_data['week2HighChange'] > 0)
            )
        ):
        if(regression_data['year2High'] == regression_data['month6High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Recent)')
        if((regression_data['month3HighChange'] == regression_data['monthHighChange']) and (regression_data['monthHighChange'] == regression_data['week2HighChange']) and regression_data['week2HighChange'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Oldest)')
        if(regression_data['weekHigh'] > regression_data['week2High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(weekHighGTweek2High)')
            
        if('Break' not in regression_data['filter3']):
            if(regression_data['year2HighChange'] < -7):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighYear2LT-7')
            elif(regression_data['year2HighChange'] < -5):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighYear2LT-5')
            elif(regression_data['year2HighChange'] < -2):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighYear2LT-2')
            elif(regression_data['year2HighChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighYear2LT0')
            
        if(regression_data['week2HighChange'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'NearHighYear2')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'ReversalHighYear2')  
    elif((-10 < regression_data['yearHighChange'] < 0) 
        and (regression_data['yearLowChange'] > 30)
        and (regression_data['yearHigh'] == regression_data['month3High']
             or ((regression_data['month3HighChange'] == regression_data['monthHighChange']) and (regression_data['monthHighChange'] == regression_data['week2HighChange']) and regression_data['week2HighChange'] > 0)
            )
        ):
        if(regression_data['yearHigh'] == regression_data['month3High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Recent)')
        if((regression_data['month3HighChange'] == regression_data['monthHighChange']) and (regression_data['monthHighChange'] == regression_data['week2HighChange']) and regression_data['week2HighChange'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Oldest)')
        if(regression_data['weekHigh'] > regression_data['week2High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(weekHighGTweek2High)')
        
        if('Break' not in regression_data['filter3'] ):
            if(regression_data['yearHighChange'] < -7):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighYearLT-7')
            elif(regression_data['yearHighChange'] < -5):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighYearLT-5')
            elif(regression_data['yearHighChange'] < -2):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighYearLT-2')
            elif(regression_data['yearHighChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighYearLT0')
        
        if(regression_data['week2HighChange'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'NearHighYear')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'ReversalHighYear')
    elif((-10 < regression_data['month6HighChange'] < 0) 
        and (regression_data['month6LowChange'] > 20)
        and (regression_data['month6High'] == regression_data['month3High']
             or ((regression_data['month3HighChange'] == regression_data['monthHighChange']) and (regression_data['monthHighChange'] == regression_data['week2HighChange']) and regression_data['week2HighChange'] > 0)
            )
        
        ):
        if(regression_data['month6High'] == regression_data['month3High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Recent)')
        if((regression_data['month3HighChange'] == regression_data['monthHighChange']) and (regression_data['monthHighChange'] == regression_data['week2HighChange']) and regression_data['week2HighChange'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Oldest)')
        if(regression_data['weekHigh'] > regression_data['week2High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(weekHighGTweek2High)')
        
        if('Break' not in regression_data['filter3'] ):
            if(regression_data['month6HighChange'] < -7):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighMonth6LT-7')
            elif(regression_data['month6HighChange'] < -5):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighMonth6LT-5')
            elif(regression_data['month6HighChange'] < -2):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighMonth6LT-2')
            elif(regression_data['month6HighChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'HighMonth6LT0')
           
        if(regression_data['week2HighChange'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'NearHighMonth6')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'ReversalHighMonth6')
            

    if((0 < regression_data['year2LowChange'] < 10) 
        and (regression_data['year2HighChange'] < -40)
        and (regression_data['year2Low'] == regression_data['month6Low']
            or ((regression_data['month3LowChange'] == regression_data['monthLowChange']) and (regression_data['monthLowChange'] == regression_data['week2LowChange']) and regression_data['week2LowChange'] < 0)
            )
        ):
        if(regression_data['year2Low'] == regression_data['month6Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Recent)')
        if((regression_data['month3LowChange'] == regression_data['monthLowChange']) and (regression_data['monthLowChange'] == regression_data['week2LowChange']) and regression_data['week2LowChange'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Oldest)')
        if(regression_data['weekLow'] < regression_data['week2Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(weekLowLTweek2Low)')
        
        if('Break' not in regression_data['filter3'] ):
            if(regression_data['year2LowChange'] > 7):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowYear2GT7')
            elif(regression_data['year2LowChange'] > 5):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowYear2GT5')
            elif(regression_data['year2LowChange'] > 2):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowYear2GT2')
            elif(regression_data['year2LowChange'] > 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowYear2GT0')
           
        if(regression_data['week2LowChange'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'NearLowYear2')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'ReversalLowYear2')
    elif((0 < regression_data['yearLowChange'] < 10)
        and (regression_data['year2LowChange'] > 7.5)
        and (regression_data['yearHighChange'] < -30)
        and (regression_data['yearLow'] == regression_data['month3Low']
            or ((regression_data['month3LowChange'] == regression_data['monthLowChange']) and (regression_data['monthLowChange'] == regression_data['week2LowChange']) and regression_data['week2LowChange'] < 0)
            )
        ):
        if(regression_data['yearLow'] == regression_data['month3Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Recent)')
        if((regression_data['month3LowChange'] == regression_data['monthLowChange']) and (regression_data['monthLowChange'] == regression_data['week2LowChange']) and regression_data['week2LowChange'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Oldest)')
        if(regression_data['weekLow'] < regression_data['week2Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(weekLowLTweek2Low)')
        
        if('Break' not in regression_data['filter3'] ):
            if(regression_data['yearLowChange'] > 7):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowYearGT7')
            elif(regression_data['yearLowChange'] > 5):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowYearGT5')
            elif(regression_data['yearLowChange'] > 2):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowYearGT2')
            elif(regression_data['yearLowChange'] > 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowYearGT0')
        
        if(regression_data['week2LowChange'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'NearLowYear')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'ReversalLowYear')
    elif((0 < regression_data['month6LowChange'] < 10)
        and (regression_data['yearLowChange'] > 7.5)
        and (regression_data['month6HighChange'] < -20)
        and (regression_data['month6Low'] == regression_data['month3Low']
             or ((regression_data['month3LowChange'] == regression_data['monthLowChange']) and (regression_data['monthLowChange'] == regression_data['week2LowChange']) and regression_data['week2LowChange'] < 0)
            )
        ):
        if(regression_data['month6Low'] == regression_data['month3Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Recent)')
        if((regression_data['month3LowChange'] == regression_data['monthLowChange']) and (regression_data['monthLowChange'] == regression_data['week2LowChange']) and regression_data['week2LowChange'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(Oldest)')
        if(regression_data['weekLow'] < regression_data['week2Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '(weekLowLTweek2Low)')
        
        if('Break' not in regression_data['filter3'] ):    
            if(regression_data['month6LowChange'] > 7):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowMonth6GT7')
            elif(regression_data['month6LowChange'] > 5):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowMonth6GT5')
            elif(regression_data['month6LowChange'] > 2):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowMonth6GT2')
            elif(regression_data['month6LowChange'] > 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'LowMonth6GT0')
            
        if(regression_data['week2LowChange'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'NearLowMonth6')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'ReversalLowMonth6')
        
    
                   
#     elif(regression_data['year2LowChange'] < 0):
#         add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '**LowYear2')
#     elif(regression_data['yearLowChange'] < 0):
#         add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '**LowYear')
#     elif(regression_data['month6LowChange'] < 0):
#         add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '**LowMonth6')
#     elif(regression_data['month3LowChange'] < 0):
#         add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '**LowMonth3')
#     elif(regression_data['year2HighChange'] > 5):
#         add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '**HighYear2')
#     elif(regression_data['yearHighChange'] > 5):
#         add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '**HighYear')
#     elif(regression_data['month6HighChange'] > 5):
#         add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '**HighMonth6')
#     elif(regression_data['month3HighChange'] > 5):
#         add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, '**HighMonth3')
    
#     if(-1 < regression_data['monthHighChange'] < 3
#         and regression_data['month3HighChange'] < -5
#         and regression_data['PCT_day_change'] > 1
#         and (regression_data['PCT_day_change_pre2'] < 0.5
#              or regression_data['PCT_day_change_pre3'] < 0.5
#             )
#         ):
#         if(abs(regression_data['year2HighChange']) > abs(regression_data['year2LowChange'])
#             and regression_data['year2LowChange'] < 25  
#             and regression_data['yearLowChange'] < 15
#             ):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, '(check-chart):buyMonthHighBreak-atNearYearLow')
#         elif(abs(regression_data['year2HighChange']) < abs(regression_data['year2LowChange'])
#             and regression_data['high'] > regression_data['high_pre1']
#             and regression_data['bar_high'] > regression_data['bar_high_pre1']
#             ):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, '(check-chart):buyMonthHighBreak-checkATRSellBreak')
#         elif(regression_data['high'] > regression_data['high_pre1']
#             and regression_data['bar_high'] > regression_data['bar_high_pre1']
#             ):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, '(check-chart):buyMonthHighBreak-checkATRSellBreak-Risky') 
#     
#     if(-3 < regression_data['monthLowChange'] < 1
#         and regression_data['month3LowChange'] > 5
#         and regression_data['PCT_day_change'] < -1
#         and (regression_data['PCT_day_change_pre2'] > -0.5
#              or regression_data['PCT_day_change_pre3'] > -0.5
#             )
#         ):
#         if(abs(regression_data['year2HighChange']) < abs(regression_data['year2LowChange'])
#             and regression_data['year2HighChange'] > -25  
#             and regression_data['yearHighChange'] > -15  
#             and (regression_data['PCT_day_change_pre2'] > 0
#                  or regression_data['PCT_day_change_pre1'] > 0
#                 )                                      
#             ):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, '(check-chart):sellMonthLowBreak-atNearYearHigh')
#         elif(abs(regression_data['year2HighChange']) > abs(regression_data['year2LowChange'])
#             and regression_data['low'] < regression_data['low_pre1']
#             and regression_data['bar_low'] < regression_data['bar_low_pre1']
#             ):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, '(check-chart):sellMonthLowBreak-checkATRBuyBreak')
#         elif(regression_data['low'] < regression_data['low_pre1']
#             and regression_data['bar_low'] < regression_data['bar_low_pre1']
#             ):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, '(check-chart):sellMonthLowBreak-checkATRBuyBreak-Risky')                    

def historical_data(data):
    ardate = np.array([str(x) for x in (np.array(data['data'])[:,0][::-1]).tolist()])
    aropen = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,1][::-1]).tolist()])
    arhigh = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,2][::-1]).tolist()])
    arlow  = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,3][::-1]).tolist()])
    arclose= np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,4][::-1]).tolist()])
    arquantity = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,5][::-1]).tolist()])
    return ardate, aropen, arhigh, arlow, arclose, arquantity,

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

def get_regressionResult(regression_data, scrip, db, mlp_r_o, kneighbours_r_o, mlp_c_o, kneighbours_c_o, high=True):
    regression_data['mlpValue_reg_other'] = float(mlp_r_o)
    regression_data['kNeighboursValue_reg_other'] = float(kneighbours_r_o)
    regression_data['mlpValue_cla_other'] = float(mlp_c_o)
    regression_data['kNeighboursValue_cla_other'] = float(kneighbours_c_o)
    
    kNeighboursValue_reg = regression_data['kNeighboursValue_reg']
    mlpValue_reg = regression_data['mlpValue_reg']
    kNeighboursValue_cla = regression_data['kNeighboursValue_cla']
    mlpValue_cla = regression_data['mlpValue_cla']
    
    kNeighboursValue_reg_other = regression_data['kNeighboursValue_reg_other']
    mlpValue_reg_other = regression_data['mlpValue_reg_other']
    kNeighboursValue_cla_other = regression_data['kNeighboursValue_cla_other']
    mlpValue_cla_other = regression_data['mlpValue_cla_other']
    
    if(high==False):
        kNeighboursValue_reg_other = regression_data['kNeighboursValue_reg']
        mlpValue_reg_other = regression_data['mlpValue_reg']
        kNeighboursValue_cla_other = regression_data['kNeighboursValue_cla']
        mlpValue_cla_other = regression_data['mlpValue_cla']
        
        kNeighboursValue_reg = regression_data['kNeighboursValue_reg_other']
        mlpValue_reg = regression_data['mlpValue_reg_other']
        kNeighboursValue_cla = regression_data['kNeighboursValue_cla_other']
        mlpValue_cla = regression_data['mlpValue_cla_other']
    
    regression_data['forecast_kNeighboursValue_reg'] = 0
    regression_data['forecast_mlpValue_reg'] = 0
    regression_data['forecast_kNeighboursValue_cla'] = 0
    regression_data['forecast_mlpValue_cla'] = 0        
    
    if(high_tail_pct(regression_data) < 1.5 and low_tail_pct(regression_data) < 1.5):
        if((kNeighboursValue_reg > -1 and kNeighboursValue_reg_other > -1)
            or (kNeighboursValue_reg < 1 and kNeighboursValue_reg_other < 1)
            ):      
            regression_data['forecast_kNeighboursValue_reg'] = (regression_data['high'] + (kNeighboursValue_reg*regression_data['high']/100)) - (regression_data['low'] + (kNeighboursValue_reg_other*regression_data['low']/100))
            regression_data['forecast_kNeighboursValue_reg'] = (regression_data['forecast_kNeighboursValue_reg'])*100/regression_data['close']
        
        if((mlpValue_reg > -1 and mlpValue_reg_other > -1)
            or (mlpValue_reg < 1 and mlpValue_reg_other < 1)
            ):    
            regression_data['forecast_mlpValue_reg'] = (regression_data['high'] + (mlpValue_reg*regression_data['high']/100)) - (regression_data['low'] + (mlpValue_reg_other*regression_data['low']/100))
            regression_data['forecast_mlpValue_reg'] = (regression_data['forecast_mlpValue_reg'])*100/regression_data['close']
        
        if((kNeighboursValue_cla > -1 and kNeighboursValue_cla_other > -1)
            or (kNeighboursValue_cla < 1 and kNeighboursValue_cla_other < 1)
            ):    
            regression_data['forecast_kNeighboursValue_cla'] = (regression_data['high'] + (kNeighboursValue_cla*regression_data['high']/100)) - (regression_data['low'] + (kNeighboursValue_cla_other*regression_data['low']/100))
            regression_data['forecast_kNeighboursValue_cla'] = (regression_data['forecast_kNeighboursValue_cla'])*100/regression_data['close']
        
        if((mlpValue_cla > -1 and mlpValue_cla_other > -1)
            or (mlpValue_cla < 1 and mlpValue_cla_other < 1)
            ):    
            regression_data['forecast_mlpValue_cla'] = (regression_data['high'] + (mlpValue_cla*regression_data['high']/100)) - (regression_data['low'] + (mlpValue_cla_other*regression_data['low']/100))
            regression_data['forecast_mlpValue_cla'] = (regression_data['forecast_mlpValue_cla'])*100/regression_data['close']
    
    regression_data['filterbuy'] = " "
    regression_data['filtersell'] = " "
    regression_data['filter'] = " "
    regression_data['filter1'] = " "
    regression_data['filter2'] = " "
    regression_data['filter3'] = " "
    regression_data['filter4'] = " "
    regression_data['filter5'] = " "
    regression_data['filter6'] = " "
    regression_data['filter_345_avg'] = 0
    regression_data['filter_345_count'] = 0
    regression_data['filter_345_pct'] = 0
    regression_data['filter_avg'] = 0
    regression_data['filter_count'] = 0
    regression_data['filter_pct'] = 0
    regression_data['filter_pct_change_avg']  = 0
    regression_data['filter_pct_change_count'] = 0
    regression_data['filter_pct_change_pct'] = 0
    regression_data['filter_all_avg']  = 0
    regression_data['filter_all_count'] = 0
    regression_data['filter_all_pct'] = 0
    regression_data['filter_tech_avg'] = 0
    regression_data['filter_tech_count'] = 0
    regression_data['filter_tech_pct'] = 0
    regression_data['filter_tech_all_avg'] = 0
    regression_data['filter_tech_all_count'] = 0
    regression_data['filter_tech_all_pct'] = 0
    regression_data['filter_tech_all_pct_change_avg'] = 0
    regression_data['filter_tech_all_pct_change_count'] = 0
    regression_data['filter_tech_all_pct_change_pct'] = 0
    regression_data['series_trend'] = trend_calculator(regression_data)
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
    regressionResult.append(regression_data['forecast_mlpValue_reg'])
    regressionResult.append(regression_data['forecast_kNeighboursValue_reg'])
    regressionResult.append(regression_data['forecast_mlpValue_reg'])
    regressionResult.append(regression_data['forecast_kNeighboursValue_cla'])
    regressionResult.append(regression_data['year2HighChange'])
    regressionResult.append(regression_data['year2LowChange'])
    regressionResult.append(regression_data['yearHighChange'])
    regressionResult.append(regression_data['yearLowChange'])
    regressionResult.append(regression_data['month6HighChange'])
    regressionResult.append(regression_data['month6LowChange'])
    regressionResult.append(regression_data['month3HighChange'])
    regressionResult.append(regression_data['month3LowChange'])
    regressionResult.append(regression_data['monthHighChange'])
    regressionResult.append(regression_data['monthLowChange'])
    regressionResult.append(regression_data['week2HighChange'])
    regressionResult.append(regression_data['week2LowChange'])
    regressionResult.append(regression_data['weekHighChange'])
    regressionResult.append(regression_data['weekLowChange'])
    regressionResult.append(regression_data['trend'])
    regressionResult.append(regression_data['score'])
    regressionResult.append(str(round(high_tail_pct(regression_data), 1))) 
    regressionResult.append(str(round(low_tail_pct(regression_data), 1)))
    regressionResult.append(regression_data['close'])
    regressionResult.append(regression_data['PCT_day_change'])
    regressionResult.append(regression_data['PCT_change'])
    regressionResult.append(regression_data['scrip'])
    regressionResult.append(regression_data['industry'])
    return regressionResult

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

def high_volatility(regression_data, regressionResult, buy=True):
    flag = False
    ws = None

    if(buy == True
        and is_algo_buy(regression_data) == False
        ):
        if(regression_data['week2LowChange'] > 20 and regression_data['weekLowChange'] > 20
            and abs(regression_data['PCT_day_change']) > 2
            and buy == True
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'TEST:2-(GLOBALDOWN-LT(-2.0))%%maySellWeek2LowWeekLowGT20')
            flag = True
        elif(regression_data['week2LowChange'] > 20 and regression_data['weekLowChange'] > 0
            and regression_data['PCT_day_change'] < -3 and regression_data['PCT_change'] < -3
            and buy == True
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'TEST:3-(GLOBALDOWN-Continue-LT(-2.0))%%maySellWeek2LowWeekLowGT20')
            flag = True
        elif(regression_data['week2LowChange'] > 10 and regression_data['weekLowChange'] > -5
            and regression_data['PCT_day_change'] < -3 and regression_data['PCT_change'] < -3
            and buy == True
            and is_algo_sell(regression_data)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'TEST:4-(GLOBALDOWN-Continue-LT(-2.0))%%maySellWeek2LowWeekLowGT10')
            flag = True
    elif(buy == False
        and is_algo_sell(regression_data) == False
        ):
        if(regression_data['week2HighChange'] < -20 and regression_data['weekHighChange'] < -20
            and abs(regression_data['PCT_day_change']) > 2
            and buy == False
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'TEST:2-(GLOBALUP-GT(2.0))%%mayBuyWeek2HighWeekHighLT-20')
            flag = True
        elif(regression_data['week2HighChange'] < -20 and regression_data['weekHighChange'] < 0
            and regression_data['PCT_day_change'] > 3 and regression_data['PCT_change'] > 3
            and buy == False
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'TEST:3-(GLOBALUP-Continue-GT(2.0))%%mayBuyWeek2HighWeekHighLT-20')
            flag = True
        elif(regression_data['week2HighChange'] < -10 and regression_data['weekHighChange'] < 5
            and regression_data['PCT_day_change'] > 3 and regression_data['PCT_change'] > 3
            and buy == False
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'TEST:4-(GLOBALUP-Continue-GT(2.0))%%mayBuyWeek2HighWeekHighLT-10')
            flag = True
    
    if(buy == True
        and regression_data['PCT_day_change'] < -7
        and regression_data['PCT_change'] < -5
        ):
        if(regression_data['weekLowChange'] > 5):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'TEST:(UPTREND-LastDayMarketDown):%%mayBuyMorningHighVolatileLastDayDown-LT(-8)')
            flag = True
        elif(regression_data['month3LowChange'] > 10 and regression_data['monthLowChange'] < 0 and regression_data['week2LowChange'] < 0 and regression_data['weekLowChange'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'TEST(9:30):(UPTREND-LastDayMarketDown):%%maySellContinueMorningHighVolatileLastDayDown-LT(-8)')
            flag = True
    
        
    if(buy == False
        and regression_data['PCT_day_change'] > 7
        and regression_data['PCT_change'] > 5
        ):
        if(regression_data['weekHighChange'] < -5):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'TEST:(DOWNTREND-LastDayMarketUp)%%maySellMorningHighVolatileLastDayUp-GT8')
            flag = True
        elif(regression_data['month3HighChange'] < -10 and regression_data['monthHighChange'] > 0 and regression_data['week2HighChange'] > 0 and regression_data['weekHighChange'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'TEST:(DOWNTREND-LastDayMarketUp)%%mayBuyContinueMorningHighVolatileLastDayUp-GT8')
            flag = True
    
    
        
    if(buy == True
        and regression_data['forecast_day_PCT7_change'] < 0
        and regression_data['forecast_day_PCT10_change'] < 0
        and 8 < regression_data['PCT_day_change'] < 20 and 8 < regression_data['PCT_change'] < 20
        ):
        if(8 < regression_data['PCT_day_change'] < 14 and 8 < regression_data['PCT_change'] < 14):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'TEST:0-(GLOBAL-UP)%%mayBuyContinueHighVolatileLastDayUp-GT8')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'TEST:1-(GLOBAL-UP)%%RiskyMayBuyContinueHighVolatileLastDayUp-GT8')
        flag = True
    elif(buy == False
        and regression_data['forecast_day_PCT2_change'] > 0
        and regression_data['forecast_day_PCT3_change'] > 0
        and regression_data['PCT_day_change_pre1'] > 0
        and regression_data['PCT_day_change_pre2'] > 0
        and ((regression_data['forecast_day_PCT5_change'] > 0 and regression_data['forecast_day_PCT7_change'] > 0 and regression_data['forecast_day_PCT10_change'] > 0)
            or (regression_data['PCT_day_change_pre1'] > 8 and regression_data['forecast_day_PCT2_change'] > 8
                and (regression_data['PCT_day_change_pre1'] > 15 or regression_data['forecast_day_PCT2_change'] > 15)
                and (-10 < regression_data['forecast_day_PCT5_change'] or -10 < regression_data['forecast_day_PCT7_change'] or -10 < regression_data['forecast_day_PCT10_change'] > 0)
               )
            )
        and (regression_data['PCT_day_change'] > 15 and regression_data['PCT_change'] > 10
            or (regression_data['PCT_change'] > -8 and regression_data['PCT_day_change'] > -8 and regression_data['PCT_day_change_pre1'] > regression_data['PCT_day_change_pre1'] > 5 and regression_data['forecast_day_PCT2_change'] > 20)
            )
        and regression_data['close'] > 50
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'TEST:0-(GLOBAL-DOWN)%%maySellAfter10:20HighVolatileLastDayUp-GT10')
        flag = True
    elif(regression_data['high'] > regression_data['high_pre1']
        and regression_data['high'] > regression_data['high_pre2']
        and ((regression_data['PCT_day_change'] > 10 and regression_data['PCT_change'] > 10 and (regression_data['PCT_day_change'] > 15 or regression_data['PCT_change'] > 15))
            or regression_data['forecast_day_PCT2_change'] > 20
            )
        and regression_data['close'] > 50
        ):
        if(buy == False
            and regression_data['PCT_day_change_pre1'] > 0
            and regression_data['PCT_day_change_pre2'] > 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'TEST:1-(GLOBAL-DOWN)%%maySellAfter10:20HighVolatileLastDayUp-GT10')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'TEST:2-(GLOBAL-DOWN)%%maySell(GLOBAL-Up)mayBuy-HighVolatileLastDayUp-GT10')
        flag = True
    
    if(high_tail_pct(regression_data) < 2 and low_tail_pct(regression_data) < 1.5):
        if(regression_data['PCT_day_change_pre1'] > -5
            and regression_data['PCT_change_pre1'] > -5
            and -20 < regression_data['PCT_day_change'] < -8
            and -20 < regression_data['PCT_change'] < -5
            and regression_data['forecast_day_PCT4_change'] > -20
            ):
            if(regression_data['PCT_day_change_pre1'] > -3 
                and regression_data['PCT_change_pre1'] > -3
                and -15 < regression_data['PCT_day_change']
                and -15 < regression_data['PCT_change']
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'TEST:%%maySellHighVolatileDownContinueLT-8')
                flag = True
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'TEST:%%maySellAfter10:30HighVolatileDownContinueLT-8-Risky')
                flag = True
        
    if(regression_data['PCT_day_change'] < -8
        and regression_data['PCT_change'] < -8
        and regression_data['forecast_day_PCT2_change'] < -20
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'TEST:%%mayBuyHighVolatileAfter10:20DownLast2Days-20')
        flag = True
    
    return flag
        
def sell_uptrend_common(regression_data, regressionResult, reg, ws):
    if(((low_tail_pct(regression_data) <= 2 and 2 <= high_tail_pct(regression_data) <= 5.5)
        or (2 <= high_tail_pct(regression_data) <= 10 and regression_data['PCT_day_change'] > 3)
        )
        and regression_data['PCT_day_change'] < high_tail_pct(regression_data)
        and regression_data['PCT_day_change'] < 6
        #and (regression_data['PCT_day_change'] > 0 or regression_data['PCT_day_change'] < -1)
        and -0.5 < regression_data['PCT_day_change_pre1'] < 7
        and regression_data['forecast_day_PCT7_change'] > 5
        and regression_data['forecast_day_PCT10_change'] > 5
        and (regression_data['forecast_day_PCT7_change'] > 15
             or regression_data['forecast_day_PCT10_change'] > 15)
        ):
        if(high_tail_pct(regression_data) > 3 and regression_data['PCT_day_change'] > -0.5
            and regression_data['year2HighChange'] < -5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%HLTF:(UPTREND-GLOBAL/SGX-UP)BuyHighUpperTail-Reversal-7,10thDayGT15-LastDayMarketDown') 
    
    if(low_tail_pct(regression_data) <= 2 and 2 <= high_tail_pct(regression_data) <= 5.5
        and -5 < regression_data['PCT_day_change'] < 3
        and (regression_data['PCT_day_change'] > 0 or regression_data['PCT_day_change'] < -1)
        and -0.5 < regression_data['PCT_day_change_pre1'] < 7
        and regression_data['forecast_day_PCT7_change'] > 5
        and regression_data['forecast_day_PCT10_change'] > 5
        and (regression_data['forecast_day_PCT7_change'] > 15
             or regression_data['forecast_day_PCT10_change'] > 15)
        ):
        if((regression_data['PCT_day_change_pre1'] > 1.5 and regression_data['PCT_day_change_pre2'] > 1.5)
            or (regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change_pre2'] > 0 and regression_data['PCT_day_change_pre3'] > 0)
            or (regression_data['forecast_day_PCT_change'] > regression_data['forecast_day_PCT2_change']
                and regression_data['forecast_day_PCT_change'] > regression_data['forecast_day_PCT3_change']
                and regression_data['forecast_day_PCT2_change'] > regression_data['forecast_day_PCT4_change']
                )
            or regression_data['PCT_day_change_pre1'] > 3 
            ):
            if(high_tail_pct(regression_data) > 3.5
                or (high_tail_pct(regression_data) > 2.5 and is_algo_sell(regression_data))
                ):
                if(-3 < regression_data['PCT_day_change'] 
                    and(regression_data['forecast_day_PCT7_change'] > 20
                        or regression_data['forecast_day_PCT10_change'] > 20)
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, None, '%%HLTF:maySellTail-tailGT2-7,10thDayGT20') 
                    return True
                elif(-3 < regression_data['PCT_day_change']):
                    add_in_csv(regression_data, regressionResult, ws, None, None, '%%HLTF-Risky9:30:maySellTail-tailGT2-7,10thDayGT15')
                    return True
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, None)
                return True
        elif(-3 < regression_data['PCT_day_change'] 
            and(regression_data['forecast_day_PCT7_change'] > 20
                or regression_data['forecast_day_PCT10_change'] > 20)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%HLTF:maySellTail-tailGT2-7,10thDayGT20') 
            return True
        elif(-3 < regression_data['PCT_day_change']):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%HLTF-Risky9:30:maySellTail-tailGT2-7,10thDayGT15')
            return True
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None)
            return True
    if(low_tail_pct(regression_data) <= 2 and 1.7 <= high_tail_pct(regression_data) <= 5.5
        #and 1 <= high_tail_pct(regression_data)
        and -5 < regression_data['PCT_day_change'] < 0.75
        and  regression_data['PCT_day_change_pre1'] < 0
        and 0 < regression_data['PCT_day_change_pre2']
        and 0 < regression_data['PCT_day_change_pre3'] 
        and 0 < regression_data['PCT_day_change_pre4'] 
        and (0 < regression_data['PCT_day_change_pre2'] < 1.5
            or 0 < regression_data['PCT_day_change_pre3'] < 1.5
            or regression_data['PCT_day_change'] < 0
            )
        and (2 < regression_data['PCT_day_change_pre2']
            or 2 < regression_data['PCT_day_change_pre2'] 
            or 2 < regression_data['PCT_day_change_pre3'] 
            or 2 < regression_data['PCT_day_change_pre4']
            )
        and regression_data['low'] > regression_data['low_pre4']
        and regression_data['forecast_day_PCT7_change'] > 5
        and regression_data['forecast_day_PCT10_change'] > 5
        and (regression_data['forecast_day_PCT7_change'] > 10
            or regression_data['forecast_day_PCT10_change'] > 10
            )
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '%%HLTF:(UPTREND-MorningTrend-UP)mayBuyTail-highTailGT2-7,10thDayGT10-Last2DayStockDown')
            
def buy_downtrend_common(regression_data, regressionResult, reg, ws):
    if(((high_tail_pct(regression_data) <= 2 and 2 <= low_tail_pct(regression_data) <= 5.5)
        or (2 <= low_tail_pct(regression_data) <= 10 and regression_data['PCT_day_change'] < -3)
        )
        and regression_data['PCT_day_change'] < low_tail_pct(regression_data)
        and -6 < regression_data['PCT_day_change']
        #and (regression_data['PCT_day_change'] < 0 or regression_data['PCT_day_change'] > 1)
        and -7 < regression_data['PCT_day_change_pre1'] < 0.5
        and regression_data['forecast_day_PCT7_change'] < -5
        and regression_data['forecast_day_PCT10_change'] < -5
        and (regression_data['forecast_day_PCT7_change'] < -15
             or regression_data['forecast_day_PCT10_change'] < -15)
        and regression_data['year2HighChange'] < -5
        ):
        if(low_tail_pct(regression_data) > 3 and regression_data['PCT_day_change'] < 0.5
            and regression_data['yearLowChange'] > 5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%HLTF:(DOWNTREND-GLOBAL/SGX-DOWN)SellHighLowerTail-Reversal-7,10thDayLT(-15)-LastDayMarketUp')
    if(high_tail_pct(regression_data) <= 2 and 2 <= low_tail_pct(regression_data) <= 5.5
        and -3 < regression_data['PCT_day_change'] < 5
        and (regression_data['PCT_day_change'] < 0 or regression_data['PCT_day_change'] > 1)
        and -7 < regression_data['PCT_day_change_pre1'] < 0.5
        and regression_data['forecast_day_PCT7_change'] < -5
        and regression_data['forecast_day_PCT10_change'] < -5
        and (regression_data['forecast_day_PCT7_change'] < -15
             or regression_data['forecast_day_PCT10_change'] < -15)
        and regression_data['year2HighChange'] < -5
        ):
        if((regression_data['PCT_day_change_pre1'] < -1.5 and regression_data['PCT_day_change_pre2'] < -1.5)
            or (regression_data['PCT_day_change_pre1'] < 0 and regression_data['PCT_day_change_pre2'] < 0 and regression_data['PCT_day_change_pre3'] < 0)
            or (regression_data['forecast_day_PCT_change'] < regression_data['forecast_day_PCT2_change']
                and regression_data['forecast_day_PCT_change'] < regression_data['forecast_day_PCT3_change']
                and regression_data['forecast_day_PCT2_change'] < regression_data['forecast_day_PCT4_change']
                )
            or regression_data['PCT_day_change_pre1'] < -3
            ):
            if(low_tail_pct(regression_data) > 3.5
                or (low_tail_pct(regression_data) > 2.5 and is_algo_buy(regression_data))
                ):
                if(regression_data['PCT_day_change'] < 3
                    and (regression_data['forecast_day_PCT7_change'] < -20
                         or regression_data['forecast_day_PCT10_change'] < -20)
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, None, '%%HLTF:mayBuyTail-tailGT2-7,10thDayLT(-20)')
                    return True
                elif(regression_data['PCT_day_change'] < 3):
                    add_in_csv(regression_data, regressionResult, ws, None, None, '%%HLTF-Risky9:30:mayBuyTail-tailGT2-7,10thDayLT(-15)')
                    return True
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, None)
                return True
        elif(regression_data['PCT_day_change'] < 3
            and (regression_data['forecast_day_PCT7_change'] < -20
                 or regression_data['forecast_day_PCT10_change'] < -20)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%HLTF:mayBuyTail-tailGT2-7,10thDayLT(-20)')
            return True
        elif(regression_data['PCT_day_change'] < 3):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%HLTF-Risky9:30:mayBuyTail-tailGT2-7,10thDayLT(-15)')
            return True
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None)
            return True
    if(low_tail_pct(regression_data) <= 2 and 2 <= high_tail_pct(regression_data) <= 5.5
        and -0.75 < regression_data['PCT_day_change'] < 5
        and 0 < regression_data['PCT_day_change_pre1'] < 5
        and -7 < regression_data['PCT_day_change_pre2'] < 0
        and -7 < regression_data['PCT_day_change_pre3'] < 0
        and (-2 < regression_data['PCT_day_change_pre2'] < 0
             or -2 < regression_data['PCT_day_change_pre3'] < 0)
        and regression_data['forecast_day_PCT7_change'] < -5
        and regression_data['forecast_day_PCT10_change'] < -5
        and (regression_data['forecast_day_PCT7_change'] < -10
             or regression_data['forecast_day_PCT10_change'] < -10)
        and regression_data['year2LowChange'] > 5
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '%%HLTF:(DOWNTREND-MT-DOWN)maySellTail-LowTailGT2-7,10thDayLT(-15)-Last2DayUP')  
     

   
        
        