import csv
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import Color, PatternFill, Font, Border
from pymongo import MongoClient
from multiprocessing.dummy import Pool as ThreadPool

import quandl, math, time
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np

soft=False

buyMLP = 1
buyMLP_MIN = 1
buyKN = 0.5
buyKN_MIN = 0
sellMLP = -1
sellMLP_MIN = -1
sellKN = -0.5
sellKN_MIN = 0

def is_algo_buy(regression_data):
    if((regression_data['mlpValue'] >= buyMLP and regression_data['kNeighboursValue'] >= buyKN_MIN) 
        or (regression_data['mlpValue'] >= buyMLP_MIN and regression_data['kNeighboursValue'] >= buyKN)):
        return True
    else:
        return False   
    
def is_algo_sell(regression_data):
    if((regression_data['mlpValue'] <= sellMLP and regression_data['kNeighboursValue'] <= sellKN_MIN)
       or (regression_data['mlpValue'] <= sellMLP_MIN and regression_data['kNeighboursValue'] <= sellKN)):   
        return True
    else:
        return False

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
    
def all_day_pct_change_positive(regression_data):
    if(regression_data['forecast_day_PCT_change'] > 0
        and regression_data['forecast_day_PCT2_change'] > -0.5
        and regression_data['forecast_day_PCT3_change'] > -0.5
        and regression_data['forecast_day_PCT4_change'] > -0.5
        and regression_data['forecast_day_PCT5_change'] > -0.5
        and regression_data['forecast_day_PCT7_change'] > -0.5
        and regression_data['forecast_day_PCT10_change'] > -0.5):
        return True;    
        
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

buyPatternsDict=scrip_patterns_to_dict('../../data-import/nselist/patterns-buy.csv')
sellPatternsDict=scrip_patterns_to_dict('../../data-import/nselist/patterns-sell.csv')

def get_regressionResult(regression_data, scrip, db):
    resultDeclared = ""
    resultDate = ""
    resultSentiment = ""
    resultComment = ""
    result_data = db.scrip_result.find_one({'scrip':scrip.replace('&','').replace('-','_')})
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
    regressionResult.append(regression_data['scrip'])
    regressionResult.append(regression_data['forecast_day_VOL_change'])
    regressionResult.append(regression_data['forecast_day_PCT_change'])
    regressionResult.append(regression_data['forecast_day_PCT2_change'])
    regressionResult.append(regression_data['forecast_day_PCT3_change'])
    regressionResult.append(regression_data['forecast_day_PCT4_change'])
    regressionResult.append(regression_data['forecast_day_PCT5_change'])
    regressionResult.append(regression_data['forecast_day_PCT7_change'])
    regressionResult.append(regression_data['forecast_day_PCT10_change'])
    regressionResult.append(regression_data['PCT_day_change'])
    regressionResult.append(regression_data['PCT_change'])
    regressionResult.append(regression_data['score'])
    regressionResult.append(regression_data['mlpValue'])
    regressionResult.append(regression_data['kNeighboursValue'])
    regressionResult.append(regression_data['trend'])
    regressionResult.append(regression_data['yearHighChange'])
    regressionResult.append(regression_data['yearLowChange'])
    regressionResult.append(resultDate)
    regressionResult.append(resultDeclared)
    regressionResult.append(resultSentiment)
    regressionResult.append(resultComment)
    return regressionResult

def buy_pattern_from_history(regression_data, regressionResult, ws_buyPattern2):
    buyIndiaAvg = 0
    if regression_data['buyIndia'] != '' and regression_data['buyIndia'] in buyPatternsDict:
        if (abs(float(buyPatternsDict[regression_data['buyIndia']]['avg'])) >= .1):
            buyIndiaAvg = float(buyPatternsDict[regression_data['buyIndia']]['avg'])
            regressionResult.append(buyPatternsDict[regression_data['buyIndia']]['avg'])
            regressionResult.append(buyPatternsDict[regression_data['buyIndia']]['count'])
            if(int(buyPatternsDict[regression_data['buyIndia']]['count']) >= 2):
                if(is_algo_buy(regression_data)
                    and 'P@[' not in str(regression_data['sellIndia'])
                    and -1 < regression_data['PCT_day_change'] < 3):
                    if(float(buyPatternsDict[regression_data['buyIndia']]['avg']) > 0.8 and int(buyPatternsDict[regression_data['buyIndia']]['count']) >= 5):
                       ws_buyPattern2.append(regressionResult)
                    elif(float(buyPatternsDict[regression_data['buyIndia']]['avg']) > 0.5 
                       or (float(buyPatternsDict[regression_data['buyIndia']]['avg']) > 0.3 and (regression_data['forecast_day_PCT10_change'] < -10 or regression_data['yearHighChange'] < -40))):
                        if(regression_data['forecast_day_PCT10_change'] < 0 and regression_data['forecast_day_PCT_change'] >= 0):
                            ws_buyPattern2.append(regressionResult)
                        elif(regression_data['forecast_day_PCT10_change'] > 0):    
                            ws_buyPattern2.append(regressionResult)      
    return buyIndiaAvg

def buy_all_rule(regression_data, regressionResult, buyIndiaAvg, ws_buyAll):
    if(is_algo_buy(regression_data)
        and (regression_data['high']-regression_data['bar_high']) < (regression_data['bar_high']-regression_data['bar_low'])
        and 'P@[' not in str(regression_data['sellIndia'])
        and buyIndiaAvg >= -.5):
        ws_buyAll.append(regressionResult)
        if(0 < regression_data['yearLowChange'] < 10):
            if(regression_data['PCT_day_change'] < -1):
                return True
        else:
            return True
    return False

def buy_year_high(regression_data, regressionResult, ws_buyYearHigh):
    if(-10 <= regression_data['yearHighChange'] < -1 and regression_data['yearLowChange'] > 30 and no_doji_or_spinning_buy_india(regression_data)
        and -0.5 < regression_data['PCT_day_change'] < 5 and regression_data['forecast_day_PCT2_change'] <= 5):
        ws_buyYearHigh.append(regressionResult)
    elif(-15 < regression_data['yearHighChange'] < -5 and regression_data['yearLowChange'] > 30 and no_doji_or_spinning_buy_india(regression_data)
        and -0.5 < regression_data['PCT_day_change'] < 5):
        if(regression_data['forecast_day_PCT2_change'] > 0 and regression_data['forecast_day_VOL_change'] > 0):
            ws_buyYearHigh.append(regressionResult)

def buy_year_low(regression_data, regressionResult, ws_buyYearLow, ws_buyYearLow1):
    if(1 < regression_data['yearLowChange'] < 10 and regression_data['yearHighChange'] < -30 
        and 0.75 < regression_data['PCT_day_change'] < 5
        and regression_data['forecast_day_PCT10_change'] <= -10 and regression_data['forecast_day_PCT7_change'] < -5 and regression_data['forecast_day_PCT5_change'] < 0.5 and regression_data['forecast_day_PCT4_change'] < 0.5 
        and regression_data['forecast_day_PCT2_change'] > -0.5 and regression_data['forecast_day_PCT_change'] > 0):
        ws_buyYearLow.append(regressionResult) 
    elif(0 < regression_data['yearLowChange'] < 15 and regression_data['yearHighChange'] < -25 
        and (5 > regression_data['PCT_day_change'] > 0.75 and regression_data['PCT_change'] > -0.5)
        and regression_data['forecast_day_PCT10_change'] <= -5 and regression_data['forecast_day_PCT7_change'] < -3 and regression_data['forecast_day_PCT5_change'] < 0.5):
        ws_buyYearLow1.append(regressionResult)
    elif(0 < regression_data['yearLowChange'] < 15 and regression_data['yearHighChange'] < -25 
        and (5 > regression_data['PCT_day_change'] > 0.75 and regression_data['PCT_change'] > -0.5 and regression_data['PCT_day_change'] >= regression_data['PCT_change'])
        and regression_data['forecast_day_PCT10_change'] < -5 and regression_data['forecast_day_PCT7_change'] < 0 and regression_data['forecast_day_PCT5_change'] < 0
        and regression_data['forecast_day_PCT2_change'] > 0 and regression_data['forecast_day_PCT_change'] > 0):
        ws_buyYearLow1.append(regressionResult)

def buy_up_trend(regression_data, regressionResult, ws_buyUpTrend):
    if(all_day_pct_change_positive(regression_data) and 0 < regression_data['PCT_day_change'] < 5 and regression_data['yearHighChange'] < -10
        and regression_data['forecast_day_PCT10_change'] >= regression_data['PCT_change'] + 2
        and regression_data['forecast_day_PCT10_change'] >= regression_data['PCT_day_change'] + 2
        and regression_data['forecast_day_PCT10_change'] < 10
        and no_doji_or_spinning_buy_india(regression_data)):
        ws_buyUpTrend.append(regressionResult)  

def buy_down_trend(regression_data, regressionResult, ws_buyDownTrend):
    if(all_day_pct_change_negative(regression_data) and 0 < regression_data['PCT_day_change'] < 5 and regression_data['yearHighChange'] < -10):
        ws_buyDownTrend.append(regressionResult)

def buy_final(regression_data, regressionResult, ws_buyFinal, ws_buyFinal1):
    if(regression_data['yearHighChange'] < -10 and regression_data['score'] != '0-1'
        and 3 > regression_data['PCT_day_change'] > 0.50 and 3 > regression_data['PCT_change'] > 0.75):   
        if( str(regression_data['sellIndia']) == '' and -90 < regression_data['yearHighChange'] < -10
            and regression_data['forecast_day_PCT10_change'] <= -10 and regression_data['forecast_day_PCT7_change'] < -5 and regression_data['forecast_day_PCT5_change'] < 0.5 and regression_data['forecast_day_PCT4_change'] < 0.5 
            and regression_data['forecast_day_PCT2_change'] > -0.5 and regression_data['forecast_day_PCT_change'] > 0):
            ws_buyFinal.append(regressionResult) 
        elif(regression_data['forecast_day_PCT5_change'] <= 1 and regression_data['forecast_day_PCT7_change'] <= -1 and regression_data['forecast_day_PCT10_change'] <= -7):
            ws_buyFinal1.append(regressionResult) 
 
def buy_high_indicators(regression_data, regressionResult, ws_buyHighIndicators):
    if(regression_data['kNeighboursValue'] > 1.0 and regression_data['yearLowChange'] < 16 and regression_data['yearHighChange'] < -35
        and (5 > regression_data['PCT_day_change'] > 0 and regression_data['PCT_change'] > -0.5)):
        ws_buyHighIndicators.append(regressionResult)   
                           
def buy_pattern(regression_data, regressionResult, ws_buyPattern, ws_buyPattern1):
    score = ''
    if(regression_data['score'] == '10' or regression_data['score'] == '1-1'):
        score = 'up'
    if(-1 < regression_data['PCT_day_change'] < 4 and regression_data['yearLowChange'] > 5 and regression_data['score'] != '0-1'):
        if(('MARUBOZU' in str(regression_data['buyIndia']) and regression_data['forecast_day_PCT5_change'] <= 0 and regression_data['forecast_day_PCT10_change'] <= -5)
           or ('HAMMER' in str(regression_data['buyIndia']) and regression_data['PCT_day_change'] > 0)
           #or 'ENGULFING' in str(regression_data['buyIndia'])
           #or 'PIERCING' in str(regression_data['buyIndia'])
           or ('MORNINGSTAR' in str(regression_data['buyIndia']) and regression_data['forecast_day_PCT5_change'] <= 0 and regression_data['forecast_day_PCT10_change'] <= -5)
           #or ':DOJISTAR' in str(regression_data['buyIndia'])
           #or 'MORNINGDOJISTAR' in str(regression_data['buyIndia'])
           or 'ABANDONEDBABY' in str(regression_data['buyIndia'])
           or 'COUNTERATTACK' in str(regression_data['buyIndia'])
           or 'KICKING' in str(regression_data['buyIndia'])
           or 'BREAKAWAY' in str(regression_data['buyIndia'])
           #or 'TRISTAR' in str(regression_data['buyIndia'])
           #or '3WHITESOLDIERS' in str(regression_data['buyIndia'])
           #or '3INSIDE' in str(regression_data['buyIndia'])
           ):
            ws_buyPattern.append(regressionResult) 
        elif(
           ('CCI:BOP' in str(regression_data['buyIndia']) and 'BELTHOLD' in str(regression_data['buyIndia']))
           or ('AROON:BOP' in str(regression_data['buyIndia']) and 'BELTHOLD' in str(regression_data['buyIndia']) and 'ENGULFING' in str(regression_data['buyIndia']))
           or ('BELTHOLD' == str(regression_data['buyIndia']) and score == 'up')
           #or ('3OUTSIDE' in str(regression_data['buyIndia']) and regression_data['forecast_day_PCT5_change'] <= 0 and score == 'up')
           #or ('HARAMI' in str(regression_data['buyIndia']) and regression_data['forecast_day_PCT5_change'] <= 0 and score == 'up')
           #or (regression_data['yearHighChange'] <= -35 and 'HARAMI' in str(regression_data['buyIndia']) and 'SHORTLINE' in str(regression_data['buyIndia']) and regression_data['PCT_day_change'] > 0)
           or ('DOJI' in str(regression_data['buyIndia']) and 'GRAVESTONEDOJI' in str(regression_data['buyIndia']) and 'LONGLEGGEDDOJI' in str(regression_data['buyIndia']) and regression_data['PCT_day_change'] > 0)
           #or ('P@[,HIKKAKE]' == str(regression_data['buyIndia']) and regression_data['PCT_day_change'] < 0)
           #or (regression_data['yearHighChange'] <= -35 and 'BELTHOLD' in str(regression_data['buyIndia']) and 'LONGLINE' in str(regression_data['buyIndia']))
           #or (regression_data['yearHighChange'] <= -35 and ',CCI:BOP' in str(regression_data['buyIndia']) and 'LONGLINE' in str(regression_data['buyIndia']))
           ) and ((regression_data['forecast_day_PCT5_change'] <= -5) or regression_data['yearHighChange'] < -50):
            ws_buyPattern1.append(regressionResult)
        elif(
           ('MARUBOZU' in str(regression_data['buyIndia']) and regression_data['forecast_day_PCT5_change'] <= 0 and regression_data['forecast_day_PCT10_change'] <= 1)
           or ('HAMMER' in str(regression_data['buyIndia']) and regression_data['PCT_day_change'] > 0)
           or 'ENGULFING' in str(regression_data['buyIndia'])
           or 'PIERCING' in str(regression_data['buyIndia'])
           or ('MORNINGSTAR' in str(regression_data['buyIndia']) and regression_data['forecast_day_PCT5_change'] <= 0 and regression_data['forecast_day_PCT10_change'] <= 1)
           #or ':DOJISTAR' in str(regression_data['buyIndia'])
           or 'MORNINGDOJISTAR' in str(regression_data['buyIndia'])
           or 'ABANDONEDBABY' in str(regression_data['buyIndia'])
           or 'COUNTERATTACK' in str(regression_data['buyIndia'])
           or 'KICKING' in str(regression_data['buyIndia'])
           or 'BREAKAWAY' in str(regression_data['buyIndia'])
           or 'TRISTAR' in str(regression_data['buyIndia'])
           or '3WHITESOLDIERS' in str(regression_data['buyIndia'])
           or '3INSIDE' in str(regression_data['buyIndia'])
           ) and 'DOJI' not in str(regression_data['buyIndia']) and ((regression_data['forecast_day_PCT5_change'] <= -5) or regression_data['yearHighChange'] < -50): 
            ws_buyPattern1.append(regressionResult)

def sell_pattern_from_history(regression_data, regressionResult, ws_sellPattern2):
    sellIndiaAvg = 0
    if regression_data['sellIndia'] != '' and regression_data['sellIndia'] in sellPatternsDict: 
        if (abs(float(sellPatternsDict[regression_data['sellIndia']]['avg'])) >= .1):
            sellIndiaAvg = float(sellPatternsDict[regression_data['sellIndia']]['avg'])
            regressionResult.append(sellPatternsDict[regression_data['sellIndia']]['avg'])
            regressionResult.append(sellPatternsDict[regression_data['sellIndia']]['count'])
            if(int(sellPatternsDict[regression_data['sellIndia']]['count']) >= 2):
                if(is_algo_sell(regression_data)
                    and 'P@[' not in str(regression_data['buyIndia'])
                    and -3 < regression_data['PCT_day_change'] < 1):
                    if(float(sellPatternsDict[regression_data['sellIndia']]['avg']) < -0.8 and int(sellPatternsDict[regression_data['sellIndia']]['count']) >= 5):
                        ws_sellPattern2.append(regressionResult)    
                    if(float(sellPatternsDict[regression_data['sellIndia']]['avg']) < -0.5 
                        or (float(sellPatternsDict[regression_data['sellIndia']]['avg']) < -0.3 and (regression_data['forecast_day_PCT10_change'] > 10 or regression_data['yearLowChange'] > 40))):
                        if(regression_data['forecast_day_PCT10_change'] > 0 and regression_data['forecast_day_PCT_change'] <= 0):
                            ws_sellPattern2.append(regressionResult)
                        elif(regression_data['forecast_day_PCT10_change'] < 0):    
                            ws_sellPattern2.append(regressionResult) 
    return sellIndiaAvg

def sell_all_rule(regression_data, regressionResult, sellIndiaAvg, ws_sellAll):
    if(is_algo_sell(regression_data)
        and (regression_data['bar_low']-regression_data['low']) < (regression_data['bar_high']-regression_data['bar_low'])
        and 'P@[' not in str(regression_data['buyIndia'])
        and sellIndiaAvg <= 0.5):
        ws_sellAll.append(regressionResult)
        if(-10 < regression_data['yearHighChange'] < 0):
            if(regression_data['PCT_day_change'] > 1):
                return True
        else:
            return True
    return False
        
def sell_year_high(regression_data, regressionResult, ws_sellYearHigh, ws_sellYearHigh1):
    if(-10 < regression_data['yearHighChange'] < -1 and regression_data['yearLowChange'] > 30 and -5 < regression_data['PCT_day_change'] < -0.75 
        and regression_data['forecast_day_PCT10_change'] > 10 and regression_data['forecast_day_PCT7_change'] > 5 and regression_data['forecast_day_PCT5_change'] > -0.5 and regression_data['forecast_day_PCT4_change'] > -0.5
        and regression_data['forecast_day_PCT2_change'] < 0 and regression_data['forecast_day_PCT_change'] < 0):
        ws_sellYearHigh.append(regressionResult)
    elif(-10 < regression_data['yearHighChange'] < 0 and regression_data['yearLowChange'] > 30 
        and (regression_data['PCT_day_change'] < 0 and regression_data['PCT_change'] < 0.5)
        and regression_data['forecast_day_PCT10_change'] > 5 and regression_data['forecast_day_PCT7_change'] > 3 and regression_data['forecast_day_PCT5_change'] > -0.5
        and regression_data['forecast_day_PCT2_change'] < 0 and regression_data['forecast_day_PCT_change'] < 0):
        ws_sellYearHigh1.append(regressionResult)
    elif(-10 < regression_data['yearHighChange'] < 0 and regression_data['yearLowChange'] > 30 
        and (regression_data['PCT_day_change'] < 0 and regression_data['PCT_change'] < 0.5)
        and regression_data['forecast_day_PCT10_change'] > 0 and regression_data['forecast_day_PCT7_change'] > 0 and regression_data['forecast_day_PCT5_change'] > 0
        and regression_data['forecast_day_PCT2_change'] < 0 and regression_data['forecast_day_PCT_change'] < 0):
        ws_sellYearHigh1.append(regressionResult)        
 
def sell_year_low(regression_data, regressionResult, ws_sellYearLow):
    if(0 < regression_data['yearLowChange'] < 15 and regression_data['yearHighChange'] < -30 
        and -2 < regression_data['PCT_day_change'] < 0 and regression_data['forecast_day_PCT_change'] < 0
        and (regression_data['score'] != '1-1' or regression_data['score'] != '10')
        and all_day_pct_change_negative(regression_data) and no_doji_or_spinning_sell_india(regression_data)):
        ws_sellYearLow.append(regressionResult)

def sell_up_trend(regression_data, regressionResult, ws_sellUpTrend):
    if(all_day_pct_change_positive(regression_data) and -5 < regression_data['PCT_day_change'] < 0 and regression_data['yearLowChange'] > 30):
        ws_sellUpTrend.append(regressionResult)

def sell_down_trend(regression_data, regressionResult, ws_sellDownTrend):
    if(all_day_pct_change_negative(regression_data) and -5 < regression_data['PCT_day_change'] < 0 and regression_data['yearLowChange'] > 30
        and regression_data['forecast_day_PCT10_change'] <= regression_data['PCT_change'] - 2
        and regression_data['forecast_day_PCT10_change'] <= regression_data['PCT_day_change'] - 2
        and no_doji_or_spinning_sell_india(regression_data)):
        ws_sellDownTrend.append(regressionResult) 
 
def sell_final(regression_data, regressionResult, ws_sellFinal, ws_sellFinal1):
    if(regression_data['yearLowChange'] > 10 and regression_data['score'] != '10'
       and -3 < regression_data['PCT_day_change'] < -0.50 and -3 < regression_data['PCT_change'] < -0.75):
        if(str(regression_data['buyIndia']) == '' and -90 < regression_data['yearHighChange'] < -10
            and regression_data['forecast_day_PCT10_change'] > 10 and regression_data['forecast_day_PCT7_change'] > 5 and regression_data['forecast_day_PCT5_change'] > -0.5 and regression_data['forecast_day_PCT4_change'] > -0.5
            and regression_data['forecast_day_PCT2_change'] < 0 and regression_data['forecast_day_PCT_change'] < 0):
            ws_sellFinal.append(regressionResult)
        elif(regression_data['forecast_day_PCT10_change'] >= 7 and regression_data['forecast_day_PCT7_change'] >= 1 and regression_data['forecast_day_PCT5_change'] >= -1
        and regression_data['forecast_day_PCT2_change'] < 0 and regression_data['forecast_day_PCT_change'] < 0):
            ws_sellFinal1.append(regressionResult)    
           
def sell_high_indicators(regression_data, regressionResult, ws_sellHighIndicators):
    if(regression_data['kNeighboursValue'] < -1.0 and regression_data['yearHighChange'] > -10 and regression_data['yearLowChange'] > 30
        and (-5 < regression_data['PCT_day_change'] < 0 and regression_data['PCT_change'] < 0.5)):
        ws_sellHighIndicators.append(regressionResult)           

def sell_pattern(regression_data, regressionResult, ws_sellPattern, ws_sellPattern1):
    score = ''
    if(regression_data['score'] == '1-1' or regression_data['score'] == '0-1'):
        score = 'down'
    if(-4 < regression_data['PCT_day_change'] < 1 and regression_data['yearHighChange'] < -5 and regression_data['score'] != '10'):
        if(('HANGINGMAN' in str(regression_data['sellIndia'])
           #or 'MARUBOZU' in str(regression_data['sellIndia'])
           #or 'ENGULFING' in str(regression_data['sellIndia'])
           or 'EVENINGSTAR' in str(regression_data['sellIndia'])
           #or ':DOJISTAR' in str(regression_data['sellIndia'])
           #or 'EVENINGDOJISTAR' in str(regression_data['sellIndia'])
           or 'ABANDONEDBABY' in str(regression_data['sellIndia'])
           or 'COUNTERATTACK' in str(regression_data['sellIndia'])
           or 'KICKING' in str(regression_data['sellIndia'])
           or 'BREAKAWAY' in str(regression_data['sellIndia'])
           #or 'TRISTAR' in str(regression_data['sellIndia'])
           or ('SHOOTINGSTAR' in str(regression_data['sellIndia']) and regression_data['PCT_day_change'] < 0)
           or 'DARKCLOUDCOVER' in str(regression_data['sellIndia'])
           #or '3INSIDE' in str(regression_data['sellIndia'])
           #or '3OUTSIDE' in str(regression_data['sellIndia'])
           #or '2CROWS' in str(regression_data['sellIndia'])
           #or '3BLACKCROWS' in str(regression_data['sellIndia'])
           ) and (regression_data['forecast_day_PCT5_change'] >= 0)):
            ws_sellPattern.append(regressionResult)
        elif(
           ('HARAMI' in str(regression_data['sellIndia']) and regression_data['forecast_day_PCT5_change'] >= 0 and score == 'down')
           or ('ENGULFING' in str(regression_data['sellIndia']) and 'LONGLINE' in str(regression_data['sellIndia']) and score == 'down')
           ) and ((regression_data['forecast_day_PCT5_change'] >= 5) or regression_data['yearLowChange'] > 50):
            ws_sellPattern1.append(regressionResult)
        elif(
           'HANGINGMAN' in str(regression_data['sellIndia'])
           or 'MARUBOZU' in str(regression_data['sellIndia'])
           #or 'ENGULFING' in str(regression_data['sellIndia'])
           or 'EVENINGSTAR' in str(regression_data['sellIndia'])
           #or ':DOJISTAR' in str(regression_data['sellIndia'])
           #or 'EVENINGDOJISTAR' in str(regression_data['sellIndia'])
           or 'ABANDONEDBABY' in str(regression_data['sellIndia'])
           or 'COUNTERATTACK' in str(regression_data['sellIndia'])
           or 'KICKING' in str(regression_data['sellIndia'])
           or 'BREAKAWAY' in str(regression_data['sellIndia'])
           or 'TRISTAR' in str(regression_data['sellIndia'])
           or ('SHOOTINGSTAR' in str(regression_data['sellIndia']) and regression_data['PCT_day_change'] < 0)
           or 'DARKCLOUDCOVER' in str(regression_data['sellIndia'])
           #or '3INSIDE' in str(regression_data['sellIndia'])
           #or '3OUTSIDE' in str(regression_data['sellIndia'])
           or '2CROWS' in str(regression_data['sellIndia'])
           or '3BLACKCROWS' in str(regression_data['sellIndia'])
           or ('CLOSINGMARUBOZU' in str(regression_data['sellIndia']) and 'LONGLINE' in str(regression_data['sellIndia']))
           or ('M@[,CROSSOVER-MACD]' in str(regression_data['sellIndia']) and 'LONGLINE' in str(regression_data['sellIndia']))
           or ('3OUTSIDE' in str(regression_data['sellIndia']) and 'SPINNINGTOP' not in str(regression_data['sellIndia']) and 'LONGLINE' not in str(regression_data['sellIndia']))
           ) and ((regression_data['forecast_day_PCT5_change'] >= 5) or regression_data['yearLowChange'] > 50):
            ws_sellPattern1.append(regressionResult)
    