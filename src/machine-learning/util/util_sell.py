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

from util.util_base import *

connection = MongoClient('localhost',27017)
db = connection.Nsedata

def sell_pattern_without_mlalgo(regression_data, regressionResult):
    ws=None
    if(regression_data['PCT_day_change'] > -3.5
        and regression_data['year2HighChange'] < -5):
        if(regression_data['sellIndia_avg'] < -0.9 and regression_data['sellIndia_count'] > 1
            and (regression_data['SMA9'] < 0 or regression_data['SMA4'] < -1.5)
            ):
            if(regression_data['SMA9'] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, '(SMA9LT0)')
            elif(regression_data['SMA4'] < -1.5):
                add_in_csv(regression_data, regressionResult, ws, None, None, '(SMA4LT(-1.5))')
            if(regression_data['yearHighChange'] < -10 and regression_data['sellIndia_count'] > 1):
                if(regression_data['sellIndia_avg'] < -1.5):
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'sellPatterns-LT-1.5-SMALT0')  
                    
    if(regression_data['PCT_day_change'] > -3.5
        and regression_data['year2HighChange'] < -5
        and regression_data['year2LowChange'] > 5):
        if(regression_data['sellIndia_avg'] > 1.8):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'mayBuyFromSellPattern-GT1.8')
        if(regression_data['sellIndia_avg'] > 0.9 and regression_data['sellIndia_count'] > 1
            and (regression_data['SMA9'] > 0 or regression_data['SMA4'] > 1.5)
            ):
            if(regression_data['SMA9'] > 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, '(SMA9GT0)')
            elif(regression_data['SMA4'] > 1.5):
                add_in_csv(regression_data, regressionResult, ws, None, None, '(SMA4GT(1.5))')
            if(regression_data['yearLowChange'] < -10 and regression_data['sellIndia_count'] > 1):
                if(regression_data['sellIndia_avg'] > 1.5):
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'buyPatterns-GT1.5-SMAGT0')
                
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
                    and -3 < regression_data['PCT_day_change']):
                    avg = sellPatternsDict[regression_data['sellIndia']]['avg']
                    count = sellPatternsDict[regression_data['sellIndia']]['count']
                    if(float(sellPatternsDict[regression_data['sellIndia']]['avg']) < -2 and int(sellPatternsDict[regression_data['sellIndia']]['count']) >= 3):
                        flag = True
                    
    return sellIndiaAvg, flag

def sell_high_volatility(regression_data, regressionResult):
    flag = False
    ws = None
    
    if('checkSellConsolidationBreakDown-2week' in regression_data['filter']
        and -4 < regression_data['PCT_day_change'] < -1
        and -4 < regression_data['PCT_change'] < -1
        and (regression_data['PCT_day_change_pre1'] > regression_data['PCT_day_change']/2
             #or 'MLSell' in regression_data['filter']
             #or 'brokenToday' in regression_data['filter']
            )
        and (regression_data['PCT_day_change'] < -2
             #or 'MLSell' in regression_data['filter']
             or 'brokenToday' in regression_data['filter']
            )
        and (regression_data['month3LowChange'] > 5 or abs_month3High_less_than_month3Low(regression_data))
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'checkSellConsolidationBreakDown(NotShapeA)-2week')
        flag = True
#     elif('checkSellConsolidationBreakDown-2week' in regression_data['filter']
#         and -5 < regression_data['PCT_day_change'] < 0
#         and -5 < regression_data['PCT_change'] < 0
#         and regression_data['PCT_day_change_pre1'] > -1.5 and regression_data['PCT_change_pre1'] > -1.5
#         and 'brokenToday' in regression_data['filter']
#         and 'MLSell' in regression_data['filter']
#         ):
#         add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'RISKY:checkSellConsolidationBreakDown(NotShapeA)-2week')
#         flag = True
    
    if(regression_data['PCT_day_change'] < 0
        and regression_data['PCT_day_change_pre1'] < 0
        and regression_data['PCT_day_change_pre2'] < 0
        and regression_data['PCT_day_change_pre3'] < 0
        and -7 > regression_data['forecast_day_PCT5_change'] > -15
        and -7 > regression_data['forecast_day_PCT7_change'] > -15
        and -7 > regression_data['forecast_day_PCT10_change'] > -15
        and (regression_data['forecast_day_PCT5_change'] < -10
            or regression_data['forecast_day_PCT7_change'] < -10
            or regression_data['forecast_day_PCT10_change'] < -10
            )
        and regression_data['year2HighChange'] < -2
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'UPTRENDMARKET:buyStockHeavyDowntrend')
        flag = True
    
    if((('NA$(shortDownTrend)' in regression_data['series_trend']) 
            or
            (regression_data['PCT_day_change'] < 0 
             and regression_data['PCT_day_change_pre1'] < 0
             and regression_data['PCT_day_change_pre2'] < 0
             and regression_data['PCT_day_change_pre3'] < 0
            )
        ) 
        and (regression_data['yearHighChange'] > -10
             or (regression_data['yearHighChange'] > -20
                 and abs_yearHigh_less_than_yearLow(regression_data)
                 and abs(regression_data['PCT_day_change']) < low_tail_pct(regression_data)
                 and low_tail_pct(regression_data) > 1
                )
            )
        and ((regression_data['PCT_day_change'] < 0 and regression_data['PCT_change'] < 0)
             or (regression_data['PCT_day_change'] > 1.5 and regression_data['PCT_change'] > 1.5)
            )
        ):
        if(low_tail_pct(regression_data) > 1.5
            and regression_data['PCT_day_change'] < 0
            and abs(regression_data['PCT_day_change']) > low_tail_pct(regression_data)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'checkForBuyATRReversal')
        elif(regression_data['PCT_day_change'] < -2
            and ((regression_data['forecast_day_PCT7_change'] < -10 and regression_data['forecast_day_PCT10_change'] < -10)
                 or regression_data['forecast_day_PCT2_change'] < -8
                 or regression_data['forecast_day_PCT3_change'] < -8
                 or (regression_data['PCT_day_change'] < -1.5 and regression_data['PCT_day_change_pre1'] < -1.5 and regression_data['PCT_day_change_pre2'] < -1.5)
                 )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'checkBuyATRCrossForReversal')
        
        if(regression_data['PCT_day_change'] > 0
            and regression_data['PCT_change'] > 0
            and -4 < regression_data['PCT_day_change_pre1'] < -0.5
            and regression_data['PCT_day_change_pre2'] < -0.5
            and (regression_data['PCT_day_change_pre1'] < -1 or regression_data['PCT_day_change_pre2'] < -1)
            and (regression_data['forecast_day_PCT3_change'] < regression_data['forecast_day_PCT2_change']
                or regression_data['forecast_day_PCT4_change'] < regression_data['forecast_day_PCT3_change']
                )
            and regression_data['close'] > regression_data['low_pre1']
            and (regression_data['close'] < regression_data['low_pre2'] 
                or regression_data['close'] < regression_data['low_pre3']
                )
            ):
            #add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'checkForDownTrendContinueLastDayUp')
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None)
        elif(regression_data['PCT_day_change'] < -1
            and regression_data['PCT_day_change_pre1'] < -1
            and regression_data['PCT_day_change_pre2'] < -1
            and regression_data['week2LowChange'] > 3
            and (regression_data['PCT_day_change_pre1'] > 0 or regression_data['PCT_day_change_pre2'] > 0 or regression_data['PCT_day_change_pre3'] > 0)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'checkForDownTrendContinueWeek2LowNotReached')
        elif(regression_data['PCT_day_change'] < -1
            and regression_data['PCT_day_change_pre1'] < -0.75
            and regression_data['PCT_day_change_pre2'] < -0.75
            and (regression_data['PCT_day_change_pre1'] < -1 or regression_data['PCT_day_change_pre2'] < -1)
            #and regression_data['monthLowChange'] < 2
            #and regression_data['monthHighChange'] < -10
            and regression_data['year2HighChange'] < -10
            and regression_data['monthLowChange'] < regression_data['month3LowChange']
            and regression_data['month3LowChange'] < regression_data['month6LowChange']
            ):
            if(regression_data['PCT_day_change_pre1'] > 0 or regression_data['PCT_day_change_pre2'] > 0 or regression_data['PCT_day_change_pre3'] > 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'DOWNTRENDMARKET:checkForDowntrendContinueMonthLow(NotMonth3LowMonth6Low)')
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'HEAVYDOWNTRENDMARKET:RISKY-Last4DayDown:checkForDowntrendContinueMonthLow(NotMonth3LowMonth6Low)')
        elif(regression_data['PCT_day_change'] < -1
            and regression_data['PCT_day_change_pre1'] < -0.75
            and regression_data['PCT_day_change_pre2'] < -0.75
            and (regression_data['PCT_day_change_pre1'] < -1 or regression_data['PCT_day_change_pre2'] < -1)
            and regression_data['monthLowChange'] < 2
            and regression_data['monthHighChange'] < -10
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'checkForDowntrendReversalMonthLow(5to10-minute-baseline-if-downtrend)')
        elif(regression_data['PCT_day_change'] < 0
            and regression_data['PCT_day_change_pre1'] < 0
            and regression_data['PCT_day_change_pre2'] < 0
            and regression_data['year2HighChange'] > -5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'checkForDowntrendReversalMA25')
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'TEST:yearHighCheckDownTrendATRBuyOrSell')
        flag = True
    elif((('NA$(shortDownTrend)' in regression_data['series_trend'])
            or ('NA$(shortDownTrend-Risky)' in regression_data['series_trend']) 
            or
            (regression_data['PCT_day_change'] < 0 
             and regression_data['PCT_day_change_pre1'] < 0
             and regression_data['PCT_day_change_pre2'] < 0
             and regression_data['PCT_day_change_pre3'] < 0
            )
        ) 
        and (regression_data['yearLowChange'] > 5)
        ):
        if(low_tail_pct(regression_data) > 1.5
            and regression_data['PCT_day_change'] < 0
            and regression_data['PCT_day_change_pre1'] < -1
            and abs(regression_data['PCT_day_change']) > low_tail_pct(regression_data)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'checkForBuyATRReversal') 
        elif(low_tail_pct(regression_data) > 3
            and regression_data['PCT_day_change'] < 1
            and regression_data['PCT_day_change_pre1'] < -1
            and regression_data['PCT_day_change_pre2'] < -1
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'checkForBuyATRReversalLowTail')
        elif(regression_data['PCT_day_change'] < -2
            and regression_data['forecast_day_PCT7_change'] < -10
            and regression_data['forecast_day_PCT10_change'] < -10
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'checkBuyATRCrossForReversal')
        if(regression_data['PCT_day_change'] > 0
            and regression_data['PCT_change'] > 0
            and -4 < regression_data['PCT_day_change_pre1'] < -0.5
            and regression_data['PCT_day_change_pre2'] < -0.5
            and (regression_data['PCT_day_change_pre1'] < -1 or regression_data['PCT_day_change_pre2'] < -1)
            and (regression_data['forecast_day_PCT3_change'] < regression_data['forecast_day_PCT2_change']
                or regression_data['forecast_day_PCT4_change'] < regression_data['forecast_day_PCT3_change']
                )
            and regression_data['close'] > regression_data['low_pre1']
            and (regression_data['close'] < regression_data['low_pre2'] 
                or regression_data['close'] < regression_data['low_pre3']
                )
            ):
            #add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'checkForDownTrendContinueLastDayUp')
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None)
        elif(regression_data['PCT_day_change'] < -1
            and regression_data['PCT_day_change_pre1'] < -1
            and regression_data['PCT_day_change_pre2'] < -1
            and regression_data['yearHighChange'] < -10
            and regression_data['week2LowChange'] > 3
            and (regression_data['PCT_day_change_pre1'] > 0 or regression_data['PCT_day_change_pre2'] > 0 or regression_data['PCT_day_change_pre3'] > 0)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'checkForDownTrendContinueWeek2LowNotReached')
        elif(regression_data['PCT_day_change'] < -1
            and regression_data['PCT_day_change_pre1'] < -0.75
            and regression_data['PCT_day_change_pre2'] < -0.75
            and (regression_data['PCT_day_change_pre1'] < -1 or regression_data['PCT_day_change_pre2'] < -1)
            #and regression_data['monthLowChange'] < 2
            #and regression_data['monthHighChange'] < -10
            and regression_data['monthLowChange'] < regression_data['month3LowChange']
            and regression_data['month3LowChange'] < regression_data['month6LowChange']
            ):
            if(regression_data['PCT_day_change_pre1'] > 0 or regression_data['PCT_day_change_pre2'] > 0 or regression_data['PCT_day_change_pre3'] > 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'DOWNTRENDMARKET:checkForDowntrendContinueMonthLow(NotMonth3LowMonth6Low)')
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'HEAVYDOWNTRENDMARKET:RISKY-Last4DayDown:checkForDowntrendContinueMonthLow(NotMonth3LowMonth6Low)')
        elif(regression_data['PCT_day_change'] < -1
            and regression_data['PCT_day_change_pre1'] < -0.75
            and regression_data['PCT_day_change_pre2'] < -0.75
            and (regression_data['PCT_day_change_pre1'] < -1 or regression_data['PCT_day_change_pre2'] < -1)
            and regression_data['monthLowChange'] < 2
            and regression_data['monthHighChange'] < -10
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'checkForDowntrendReversalMonthLow(5to10-minute-baseline-if-downtrend)')
        
#         if(regression_data['PCT_day_change'] < -5
#             and regression_data['PCT_change'] < -3
#             and regression_data['PCT_day_change_pre1'] < -1.5
#             and regression_data['PCT_day_change_pre2'] < -1.5
#             #and (regression_data['PCT_day_change_pre1'] < -2 or regression_data['PCT_day_change_pre2'] < -2)
#             ):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'TestmayBuyShortDownTrend') 
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'TEST:checkDownTrendATRBuyOrSell')
        flag = True
    elif('shortDownTrend' in regression_data['series_trend']):
        if(low_tail_pct(regression_data) > 1.5
            and regression_data['PCT_day_change'] < 0
            and regression_data['PCT_day_change_pre1'] < -1
            and abs(regression_data['PCT_day_change']) > low_tail_pct(regression_data)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'checkForBuyATRReversal') 
        elif(low_tail_pct(regression_data) > 3
            and regression_data['PCT_day_change'] < 1
            and regression_data['PCT_day_change_pre1'] < -1
            and regression_data['PCT_day_change_pre2'] < -1
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'checkForBuyATRReversalLowTail')   
        elif(regression_data['PCT_day_change'] < -2
            and (regression_data['forecast_day_PCT7_change'] < -10 or regression_data['forecast_day_PCT10_change'] < -10)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'UPTRENDMARKET:checkBuyATRCrossForReversal')
            flag = True
    
    if(regression_data['PCT_day_change'] > 0
        and regression_data['PCT_day_change_pre1'] < 0
        and regression_data['PCT_day_change_pre2'] < 0
        and (regression_data['PCT_day_change_pre1'] < -1 
             or regression_data['PCT_day_change_pre2'] < -1
             or regression_data['PCT_day_change_pre3'] < -1
             )
        and regression_data['close'] > regression_data['low_pre1']
        and (regression_data['close'] < regression_data['low_pre2'] 
             or regression_data['close'] < regression_data['low_pre3']
             or (regression_data['close'] < regression_data['high_pre2'] and regression_data['close'] < regression_data['high_pre3'])
             )
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'RISKY-DOWNTREND-BUY') 
        flag = True
        if(0 < regression_data['PCT_change'] < 1.5
           and 0 < regression_data['PCT_day_change'] < 1
           and (regression_data['PCT_change'] > 0.75 or regression_data['PCT_day_change'] > 0.75)
           and (regression_data['PCT_day_change_pre1'] < -1 or regression_data['PCT_day_change_pre2'] < -1 or regression_data['PCT_day_change_pre3'] < -1)
           and (abs_week2High_less_than_week2Low(regression_data) 
                or abs_monthHigh_less_than_monthLow(regression_data)
                )
           and (10 > regression_data['forecast_day_PCT7_change'] > 3 or 10 > regression_data['forecast_day_PCT10_change'] > 3)
           and (high_tail_pct(regression_data) < 1.5 or high_tail_pct(regression_data) < low_tail_pct(regression_data))
           and regression_data['year2HighChange'] < -5
           and regression_data['year2LowChange'] > 5
           ):
           add_in_csv(regression_data, regressionResult, ws, None, None, None, None,'[DOWNTRENDMARKET-Sell]')
        elif(0 < regression_data['PCT_change'] < 2 and 0 < regression_data['PCT_day_change'] < 2
           and (0 < regression_data['PCT_change'] < 1 or 0 < regression_data['PCT_day_change'] < 1 or regression_data['forecast_day_PCT4_change'] < 0)
           #and (regression_data['PCT_change'] > 0.75 or regression_data['PCT_day_change'] > 0.75)
           and (regression_data['PCT_day_change_pre1'] < -1 or regression_data['PCT_day_change_pre2'] < -1 or regression_data['PCT_day_change_pre3'] < -1)
           and (abs_week2High_less_than_week2Low(regression_data) 
                or abs_monthHigh_less_than_monthLow(regression_data)
                )
           and (10 > regression_data['forecast_day_PCT7_change'] > 2 
                or 10 > regression_data['forecast_day_PCT10_change'] > 2
                or (5 > regression_data['forecast_day_PCT7_change'] > 0 and 5 > regression_data['forecast_day_PCT10_change'] > 0)
                )
           and regression_data['year2HighChange'] < -5
           and regression_data['year2LowChange'] > 5
           ):
            if((regression_data['PCT_day_change_pre1'] > -1 and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change']))
                or (regression_data['SMA9'] < 0 and regression_data['SMA25'] < 0)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None,None)
            elif((high_tail_pct(regression_data) < 1.5 or high_tail_pct(regression_data) < low_tail_pct(regression_data))
                 and low_tail_pct(regression_data) > 1
                #and regression_data['SMA9'] > 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None,'[DOWNTRENDMARKET-Sell,UPTRENDMARKET:checkForUptrendContinueInGLOBALMARKETUP]')
        elif(-2 < regression_data['PCT_change'] < 3
           and 0 < regression_data['PCT_day_change'] < 1
           and regression_data['PCT_day_change_pre1'] < 0
           and regression_data['PCT_day_change_pre2'] < 0
           and regression_data['year2HighChange'] < -5
           and regression_data['year2LowChange'] > 5
           ):
            if(4 > low_tail_pct(regression_data) > 1
                and high_tail_pct(regression_data) < 1 
                and low_tail_pct(regression_data) > high_tail_pct(regression_data)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None,'LowTail-GT-HighTail')
            elif(4 > high_tail_pct(regression_data) > 1
                and low_tail_pct(regression_data) < 1
                and high_tail_pct(regression_data) > low_tail_pct(regression_data)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None,'HighTail-GT-LowTail')
            if(regression_data['PCT_day_change_pre1'] < -1
                and regression_data['PCT_day_change_pre2'] < -1
                and regression_data['PCT_day_change'] > 0
                and regression_data['high'] < regression_data['high_pre1']
                and high_tail_pct(regression_data) < low_tail_pct(regression_data)
                and (regression_data['forecast_day_PCT4_change'] > 0 or regression_data['forecast_day_PCT5_change'] > 0 or regression_data['forecast_day_PCT7_change'] > 0)
                ): 
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None,'[STRONG-UPTRENDMARKET:followMarketTrend]')
            
        elif(-2 < regression_data['PCT_change'] < 3 
           and regression_data['PCT_day_change_pre1'] < 0
           and regression_data['PCT_day_change_pre2'] < 0
           and regression_data['year2HighChange'] < -5
           and regression_data['year2LowChange'] > 5
           ):
            if(4 > low_tail_pct(regression_data) > 1
                and high_tail_pct(regression_data) < 1 
                and low_tail_pct(regression_data) > high_tail_pct(regression_data)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None,'LowTail-GT-HighTail')
            elif(4 > high_tail_pct(regression_data) > 1
                and low_tail_pct(regression_data) < 1
                and high_tail_pct(regression_data) > low_tail_pct(regression_data)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None,'HighTail-GT-LowTail')
            if(regression_data['PCT_day_change_pre1'] < 0
                and regression_data['PCT_day_change_pre2'] < 0
                and regression_data['PCT_day_change'] > 1 
                and regression_data['bar_high'] > regression_data['bar_high_pre1']
                and regression_data['high'] < regression_data['high_pre2']
                and high_tail_pct(regression_data) < low_tail_pct(regression_data) + 0.5
                ): 
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None,'[UPTREND-BUY-RISKY,DOWNTREND-SELL-RISKY]')
            elif(regression_data['PCT_day_change_pre1'] < 0
                and regression_data['PCT_day_change_pre2'] < 0
                and regression_data['PCT_day_change'] > 0
                and regression_data['high'] > regression_data['high_pre1']
                and regression_data['high'] < regression_data['high_pre2']
                ): 
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None,'[DOWNTREND-SELL-RISKY]')   
        
        if(((regression_data['weekHighChange'] < -2 and regression_data['weekLowChange'] > 1.5)
            #or regression_data['week2HighChange'] < -3 and regression_data['week2LowChange'] > 5
            )
            and regression_data['forecast_day_PCT5_change'] > 0
            #and regression_data['low_pre4'] > regression_data['low']
            and regression_data['PCT_day_change'] > 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None,'DOWNTREND-GLOBALDOWN:checkForDowntrendContinueLastDayUp')
                  
        if(regression_data['PCT_change'] > 0
            and -5 < regression_data['PCT_day_change_pre1']
            and (regression_data['PCT_day_change_pre3'] > -1 
                 or high_tail_pct(regression_data) > 1
                 or high_tail_pct(regression_data) > low_tail_pct(regression_data)
                 )
            and (regression_data['forecast_day_PCT3_change'] < regression_data['forecast_day_PCT2_change']
                or regression_data['forecast_day_PCT4_change'] < regression_data['forecast_day_PCT3_change']
                )
            and regression_data['year2HighChange'] < -10
            and regression_data['year2LowChange'] > 10
            and regression_data['week2HighChange'] == regression_data['month3HighChange']
            and regression_data['week2HighChange'] > -5
            and (abs_monthHigh_more_than_monthLow(regression_data)
                or regression_data['monthLowChange'] < 0
                or regression_data['week2LowChange'] < 0
                )
            
            ):
            if(regression_data['PCT_day_change'] > 4 and regression_data['PCT_change'] > 4):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'DOWNTRENDMARKET:checkForDowntrendContinueLastDayUp')
            elif(high_tail_pct(regression_data) > low_tail_pct(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'DOWNTRENDMARKET:checkForDowntrendContinueLastDayUp')
        if(regression_data['PCT_change'] > -1
            and 0 < regression_data['PCT_day_change'] < 1
            and regression_data['forecast_day_PCT10_change'] > -0.5
            and regression_data['monthHighChange'] < -5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'DOWNTRENDMARKET:checkForDowntrendContinueLastDayDownPCT10GT-0.5') 
    
    if((regression_data['forecast_day_PCT5_change'] < -10 or regression_data['forecast_day_PCT4_change'] < -10 or regression_data['forecast_day_PCT3_change'] < -10)
        and regression_data['PCT_day_change'] < -15
        and regression_data['close'] > 50
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'HEAVYDOWNTRENDMARKET:SellIfOpenHigh-BuyReversalIfOpenInLow(no-news-on-stock)(Nifty-down-last-3-days)')
        flag = True
    elif((regression_data['forecast_day_PCT5_change'] < -15 or regression_data['forecast_day_PCT4_change'] < -15 or regression_data['forecast_day_PCT3_change'] < -10)
        and regression_data['PCT_day_change'] < -5
        and (regression_data['PCT_day_change'] < -9 or "MLBuy" in regression_data['filter'])
        and regression_data['close'] > 50
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'HEAVYDOWNTRENDMARKET:BuyReversal(no-news-on-stock)(Nifty-down-last-3-days)')
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
    elif(low_tail_pct(regression_data) < 2):
        if(-10 < regression_data['PCT_day_change'] < -5
            and -10 < regression_data['PCT_change'] < -2
            and (regression_data['forecast_day_PCT3_change'] > 0 or regression_data['forecast_day_PCT5_change'] > 0 or regression_data['forecast_day_PCT7_change'] > 0)
            ):
            #add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'TEST:%%maySellHighVolatileDownContinueLT-5')
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None)
            flag = True
        
#     if('%%mayBuyTail' in regression_data['filter']
#         and (('downTrend' in regression_data['series_trend'])
#              or ('DownTrend' in regression_data['series_trend'])
#              or pct_day_change_trend(regression_data) <= -3
#             )
#         and ('shortDownTrend-Mini' not in regression_data['series_trend'])
#         ):
#         countGt, countLt = pct_day_change_counter(regression_data)
#         if(countGt < countLt
#             and regression_data['PCT_day_change'] > -3
#             and regression_data['PCT_change'] > -3
#             and regression_data['forecast_day_PCT10_change'] > -10
#             and (-2 > regression_data['month3LowChange'] or regression_data['month3LowChange'] > 5)
#             ):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, '%%SellDownTrend-lowTail')
#         elif(countGt == countLt
#             and regression_data['PCT_day_change'] < 0.5
#             and regression_data['PCT_change'] < 0.5
#             and -2 < regression_data['month3LowChange'] < 2
#             ):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, '%%BuyDownTrend-lowTail-nearMonth3Low')
#         flag = True
        
#     if((('NA$(shortDownTrend-Risky)' in regression_data['series_trend']) 
#             or ('NA$(shortDownTrend)' in regression_data['series_trend']) 
#             or
#             (regression_data['PCT_day_change_pre1'] < -3
#              and regression_data['PCT_day_change_pre2'] < -2
#              and regression_data['PCT_day_change_pre3'] < -2
#             )
#         ) 
#         and (regression_data['PCT_day_change'] > 2.5 and regression_data['PCT_change'] > 2)
#         and abs_month3High_less_than_month3Low(regression_data)
#         and regression_data['high'] < regression_data['high_pre2']  
#         ):
#         if(regression_data['PCT_day_change'] > 4 and regression_data['PCT_change'] > 4):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'downtrendReversalMayFail')
#         else:
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'DOWNTRENDMARKET:RISKYdowntrendReversalMayFail(marketUpLast2-3Days)')
#         flag = True
#     
#     if(('NA$(shortDownTrend-MayReversal' in regression_data['series_trend']
#         #or 'shortDownTrend' in regression_data['series_trend']
#         #or 'trendDown' in regression_data['series_trend']
#         ) 
#         and regression_data['PCT_day_change'] < 0
#         and regression_data['PCT_change'] < 0
#         and regression_data['PCT_day_change_pre1'] > 2.5
#         and (regression_data['low'] > regression_data['low_pre1'] 
#              or ( regression_data['PCT_day_change'] > -3
#                   and regression_data['PCT_change'] > -3
#                 )
#             )
#         ):
#         add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'maySellshortDownTrendContinue')
#         flag = True
    
    if(high_volatility(regression_data, regressionResult, False)):
        flag = True
        
    return flag

def sell_common_down_continued(regression_data, regressionResult, reg, ws):
    if(high_tail_pct(regression_data) < 2 and low_tail_pct(regression_data) < 1.1
        and (regression_data['monthLowChange'] < 0 and regression_data['month3HighChange'] > -40)
        and (regression_data['month3HighChange'] < -10 or regression_data['month6HighChange'] < -15)
        and (regression_data['forecast_day_PCT10_change'] > -15)
        and (regression_data['forecast_day_PCT5_change'] > -10 or regression_data['forecast_day_PCT10_change'] > -10)
        and ((regression_data['PCT_day_change_pre1'] < 0
                and (regression_data['PCT_day_change_pre2'] > 0 or regression_data['PCT_day_change_pre3'] > 0)
                and (regression_data['forecast_day_PCT5_change'] < -10 or regression_data['forecast_day_PCT7_change'] < -10 or regression_data['forecast_day_PCT10_change'] < -10)
                )
            or (regression_data['PCT_day_change_pre1'] < 0
                and regression_data['PCT_day_change_pre2'] > 0 
                and (regression_data['forecast_day_PCT5_change'] > -5)
                )
            or ((regression_data['monthLowChange'] < 0 or regression_data['month3LowChange'] < 0)
                and regression_data['yearLowChange'] < 10
                )
            )
        and (regression_data['PCT_day_change_pre1'] > 0 or regression_data['PCT_day_change_pre2'] > 0 or regression_data['PCT_day_change_pre3'] > 0)
        ):
        if(-4.0 < regression_data['PCT_day_change'] < -2.5 and -5 < regression_data['PCT_change'] < -2.5):
            if(regression_data['monthHighChange'] > -5):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'CommonHL:maySellDownContinueLT-3')
            elif(regression_data['forecast_day_PCT5_change'] > -10 
                and regression_data['forecast_day_PCT10_change'] > -10
                and regression_data['yearLowChange'] > 5
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'CommonHL:maySellDownContinueLT-3-Risky')
        elif(-4 < regression_data['PCT_day_change'] < -2 and -4 < regression_data['PCT_change'] < -1):
            if(regression_data['monthHighChange'] > -5):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'CommonHL:maySellDownContinueGT-3')
            else:
                #add_in_csv(regression_data, regressionResult, ws, None, None, 'CommonHL:maySellDownContinueGT-3-Risky')
                add_in_csv(regression_data, regressionResult, ws, None, None, None)
    elif(high_tail_pct(regression_data) < 2 and low_tail_pct(regression_data) < 2
        and (regression_data['monthHighChange'] > -5 and regression_data['month3HighChange'] > -5 
             and regression_data['month3LowChange'] > 0 and regression_data['month6LowChange'] > 5)
        and (regression_data['forecast_day_PCT10_change'] > -15)
        and (regression_data['forecast_day_PCT5_change'] > -10 or regression_data['forecast_day_PCT10_change'] > -10)  
        and (regression_data['PCT_day_change_pre1'] > 0 or regression_data['PCT_day_change_pre2'] > 0 or regression_data['PCT_day_change_pre3'] > 0)
        ):
        if(-6.0 < regression_data['PCT_day_change'] < -2.5 and -7 < regression_data['PCT_change'] < -2.5):
            if(abs(regression_data['PCT_day_change']) < abs(regression_data['PCT_day_change_pre1'])):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'CommonHL:maySellDownContinueLT-3AfterSomeUpCheckBase')
            elif(-4.5 < regression_data['PCT_day_change'] < -2.5 and -5 < regression_data['PCT_change'] < -2.5):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'CommonHL-(10:00to12:00):maySellDownContinueLT-3AfterSomeUpCheckBase')
    
    if(high_tail_pct(regression_data) < 2 and low_tail_pct(regression_data) < 1.1
        and regression_data['monthHighChange'] > -5
        and (regression_data['month3HighChange'] < -10 or regression_data['month6HighChange'] < -15)
        and (regression_data['forecast_day_PCT10_change'] > -15)
        and (regression_data['forecast_day_PCT5_change'] > -10 or regression_data['forecast_day_PCT10_change'] > -10)
        and ((regression_data['PCT_day_change_pre1'] < 0
                and (regression_data['PCT_day_change_pre2'] > 0 or regression_data['PCT_day_change_pre3'] > 0)
                and (regression_data['forecast_day_PCT5_change'] < -10 or regression_data['forecast_day_PCT7_change'] < -10 or regression_data['forecast_day_PCT10_change'] < -10)
                )
            or (regression_data['PCT_day_change_pre1'] < 0
                and regression_data['PCT_day_change_pre2'] > 0 
                and (regression_data['forecast_day_PCT5_change'] > -5)
                )
            or ((regression_data['monthLowChange'] < 0 or regression_data['month3LowChange'] < 0)
                and regression_data['yearLowChange'] < 10
                )
            )
        and (regression_data['PCT_day_change_pre1'] > 0 or regression_data['PCT_day_change_pre2'] > 0 or regression_data['PCT_day_change_pre3'] > 0)
        ):
        if(-4 < regression_data['PCT_day_change'] < -2 and -4 < regression_data['PCT_change'] < -1
            and (regression_data['PCT_day_change_pre1'] < -1.5 and regression_data['PCT_day_change_pre2'] > 1.5) 
            and (regression_data['forecast_day_PCT7_change'] > -1 and regression_data['forecast_day_PCT10_change'] > -1)
            ):
            #add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF:mayBuyReversalInSmallDowntrend')
            add_in_csv(regression_data, regressionResult, ws, None, None, None)
        elif(-4.0 < regression_data['PCT_day_change'] < -3 and -5 < regression_data['PCT_change'] < -1
            and ((regression_data['forecast_day_PCT3_change'] < 0 and regression_data['forecast_day_PCT4_change'] < 0)
                or regression_data['forecast_day_PCT5_change'] < 0
                or regression_data['forecast_day_PCT7_change'] < 0
                or regression_data['forecast_day_PCT10_change'] < 0
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF:maySellDownContinueLT-3')
        elif(-4 < regression_data['PCT_day_change'] < -2 and -4 < regression_data['PCT_change'] < -1
            and regression_data['PCT_day_change_pre2'] < 1 
            and regression_data['low'] > regression_data['low_pre2']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF:maySellDownContinueGT-3')
            
def sell_af_high_indicators(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_cla, kNeighboursValue_cla = get_reg_or_cla(regression_data, False)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    if(regression_data['PCT_day_change'] == 0):
        return False
    flag = False
    if(regression_data['PCT_day_change'] > -1.5 and regression_data['PCT_change'] > -1.5):
        if(is_algo_sell(regression_data, True)
            and (mlpValue <= -2.5 or kNeighboursValue <= -2.5)
            and (mlpValue_other <= 0 and kNeighboursValue_other <= 0)
            and regression_data['PCT_day_change'] > -5
            ):
            if(((-10 < mlpValue < -4 and -10 <= kNeighboursValue <= -2) or (-10 < mlpValue <= -2 and -10 < kNeighboursValue <= -4))
                ):
                if(mlpValue_cla < 0 or kNeighboursValue_cla < 0):
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'sellHighIndicators')
                    flag = True
            elif((-10 < mlpValue < -2 and -10 < kNeighboursValue < 0)
                and (mlpValue_other < -2 or regression_data['PCT_day_change'] > 2) 
                and (mlpValue_cla <= 0)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'sellHighMLPClaIndicators')
                flag = True
            elif((-10 < mlpValue < 0 and -10 < kNeighboursValue < -2)
                and (kNeighboursValue_other < -2 or regression_data['PCT_day_change'] > 2) 
                and (kNeighboursValue_cla <= 0)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'sellHighKNClaIndicators')
                flag = True
        elif((mlpValue_other <= 0 and kNeighboursValue_other <= 0)
            #and (mlpValue_cla > 0 or kNeighboursValue_cla > 0)
            and (-10 < mlpValue < -2 and -10 < kNeighboursValue < -2)
            and ((mlpValue + kNeighboursValue) < -5)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'sellHighIndicators-Risky')
            flag = True
        elif((mlpValue_other <= 0 and kNeighboursValue_other <= 0)
            and (-10 < mlpValue < -2 and -10 < kNeighboursValue < 0)
            and (mlpValue_other < -2 or regression_data['PCT_day_change'] > 2)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'sellHighMLPClaIndicators-risky')
            flag = True
        elif((mlpValue_other <= 0 and kNeighboursValue_other <= 0)
            and (-10 < mlpValue < 0 and -10 < kNeighboursValue < -2)
            and (kNeighboursValue_other < -2 or regression_data['PCT_day_change'] > 2)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'sellHighKNClaIndicators-risky')
            flag = True
    return flag

def sell_af_high_tail(regression_data, regressionResult, reg, ws):
    if(sell_uptrend_common(regression_data, regressionResult, reg, ws)):
        add_in_csv(regression_data, regressionResult, ws, None, None, None)
    elif(low_tail_pct(regression_data) <= 2 and 3 <= high_tail_pct(regression_data) <= 5.5
        and -5 < regression_data['PCT_day_change'] < 0 and -5 < regression_data['PCT_change'] < 5
        and regression_data['PCT_day_change_pre1'] > 0
        and regression_data['PCT_day_change_pre2'] > 0
        and regression_data['forecast_day_PCT3_change'] > 0
        and regression_data['forecast_day_PCT4_change'] > 0
        and regression_data['forecast_day_PCT5_change'] > 0
        and regression_data['forecast_day_PCT7_change'] > 0
        and regression_data['forecast_day_PCT10_change'] > 0
        and (regression_data['forecast_day_PCT7_change'] > 15 
             or regression_data['forecast_day_PCT10_change'] > 15
             or (regression_data['forecast_day_PCT7_change'] > 10 and regression_data['forecast_day_PCT10_change'] > 10)
             or ((regression_data['forecast_day_PCT7_change'] > 5 or regression_data['forecast_day_PCT10_change'] > 5) and regression_data['PCT_day_change'] < -2)
            )
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF:maySellTail-tailGT2-allDayGT0')
    elif(low_tail_pct(regression_data) <= 1.5 and 2 <= high_tail_pct(regression_data) <= 5.5
        and -5 < regression_data['PCT_day_change'] < 0 and -5 < regression_data['PCT_change'] < 5
        and regression_data['bar_high'] < regression_data['bar_high_pre1'] < regression_data['bar_high_pre2']
        and regression_data['forecast_day_PCT_change'] < 0
        and regression_data['forecast_day_PCT2_change'] < 0
        and regression_data['forecast_day_PCT7_change'] > 0
        and regression_data['forecast_day_PCT10_change'] > 0
        and regression_data['SMA25'] < 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF:maySellTail-tailGT2-7,10thDayGT0')
    elif(low_tail_pct(regression_data) <= 1 and 2 <= high_tail_pct(regression_data) <= 6
        and 1 < regression_data['PCT_day_change'] < 5 and 1 < regression_data['PCT_change'] < 5
#         and regression_data['forecast_day_PCT2_change'] > 0 and regression_data['low'] > regression_data['high_pre2']
#         and regression_data['forecast_day_PCT3_change'] > 0 and regression_data['low'] > regression_data['high_pre3']
#         and regression_data['forecast_day_PCT4_change'] > 0 and regression_data['low'] > regression_data['high_pre4']
        and regression_data['forecast_day_PCT2_change'] > 0
        and regression_data['forecast_day_PCT3_change'] > 0
        and regression_data['forecast_day_PCT4_change'] > 0
        and regression_data['forecast_day_PCT5_change'] > -5
        #and regression_data['forecast_day_PCT7_change'] > -10
        #and regression_data['forecast_day_PCT10_change'] > -10
        and (regression_data['forecast_day_PCT7_change'] > -5 or regression_data['forecast_day_PCT10_change'] > -5)
        and (regression_data['forecast_day_PCT7_change'] < 0 or regression_data['forecast_day_PCT10_change'] < 0)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF:(DOWNTREND-OR-GLOBALDOWN)maySellTail-tailGT2-2,3,4thDayGT0')
    elif(low_tail_pct(regression_data) < 2 and 1.5 < high_tail_pct(regression_data) < 2.1
        and (('MaySell-CheckChart' in regression_data['filter1']) or ('MaySellCheckChart' in regression_data['filter1']))
        and (-0.75 < regression_data['PCT_day_change'] < 0) and (-2.5 < regression_data['PCT_change'] < 1)
        and (regression_data['PCT_day_change'] < 0 or regression_data['PCT_change_pre1'] < 0)
        and (is_algo_sell(regression_data) 
             or ((regression_data['PCT_change_pre2'] > 0 or regression_data['PCT_change_pre3'] > 0)
                 and (regression_data['PCT_change_pre1'] < 0 or regression_data['PCT_change_pre2'] < 0 or regression_data['PCT_change_pre3'] < 0)
                 and regression_data['PCT_day_change'] < 0
                )
             )
        and high_tail_pct(regression_data) > low_tail_pct(regression_data)
        ): 
        add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF-LastDayUp:(DOWNTREND-OR-GLOBALDOWN)MaySellHighTail-LastDayMarketUp')
    elif(low_tail_pct(regression_data) <= 1 and 1.3 <= high_tail_pct(regression_data) <= 2
        and high_tail_pct(regression_data) > (low_tail_pct(regression_data) + 0.5)
        and high_tail_pct(regression_data) > (abs(regression_data['PCT_day_change']) + 0.5)
        ):
        if(0.5 < regression_data['PCT_day_change'] < 3 and 0.5 < regression_data['PCT_change'] < 3
           and (1 < regression_data['PCT_day_change'] or 1 < regression_data['PCT_change'])
           and abs(regression_data['PCT_day_change']) < high_tail_pct(regression_data)
           and regression_data['forecast_day_PCT2_change'] > 0
           and regression_data['forecast_day_PCT3_change'] > 0
           and regression_data['forecast_day_PCT4_change'] > 0
           and regression_data['forecast_day_PCT5_change'] > -5
           and regression_data['forecast_day_PCT7_change'] > -10
           and regression_data['forecast_day_PCT10_change'] > -10
           and (regression_data['forecast_day_PCT7_change'] > -5 or regression_data['forecast_day_PCT10_change'] > -5)
           and (regression_data['forecast_day_PCT7_change'] < 5 or regression_data['forecast_day_PCT10_change'] < 5)
           ):
           add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF:(GLOBAL-SGX-DOWN)maySellTail-2,3,4thDayGT0')
      
#         elif(-1 < regression_data['PCT_day_change'] < 3 
#            and -1 < regression_data['PCT_change'] < 3 
#            and 1.4 <= high_tail_pct(regression_data)
#            and is_algo_sell(regression_data)
#            ):
#            if(regression_data['low'] > regression_data['low_pre1']
#                 and regression_data['PCT_day_change'] < 0 and regression_data['PCT_change'] < 0
#                 and regression_data['PCT_day_change_pre1'] < 0
#                 and regression_data['PCT_day_change_pre2'] < 0
#                 and abs(regression_data['PCT_day_change']) < abs(regression_data['PCT_day_change_pre1'])
#                 and abs(regression_data['PCT_day_change']) < abs(regression_data['PCT_day_change_pre2'])
#                 and (regression_data['weekLowChange'] > 0 or regression_data['week2LowChange'] > 0 or regression_data['month3LowChange'] > 0)
#                 ):
#                 add_in_csv(regression_data, regressionResult, ws, None, None, None)
#                 #add_in_csv(regression_data, regressionResult, ws, None, None, '%%Reversal-maySellTail-Risky')
#            elif((regression_data['low'] < regression_data['low_pre1']
#                 and regression_data['PCT_day_change'] < 0 and regression_data['PCT_change'] < 0
#                 )
#                 or
#                 (regression_data['PCT_day_change'] > 0 and regression_data['PCT_change'] > 0)
#                 ):
#                 add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF:maySellTail-Risky')
    if((3.5 < low_tail_pct(regression_data) < 5 or (2.5 < low_tail_pct(regression_data) < 5 and high_tail_pct(regression_data) < 1.5))
        and high_tail_pct(regression_data) < 3.5
        and regression_data['SMA4'] > 0 and regression_data['SMA4_2daysBack'] > 0
        and regression_data['SMA9'] > 0 and  regression_data['SMA9_2daysBack'] > 0
        and regression_data['SMA25'] > 1
        and (regression_data['high'] > regression_data['high_pre1'] > regression_data['high_pre2']
            or regression_data['bar_high'] > regression_data['bar_high_pre1'] > regression_data['bar_high_pre2']
            )
        and regression_data['forecast_day_PCT4_change'] > 0
        and regression_data['forecast_day_PCT5_change'] > 0
        and regression_data['forecast_day_PCT7_change'] < 15 and regression_data['forecast_day_PCT10_change'] < 15
        and regression_data['PCT_day_change'] < 3 and regression_data['PCT_change'] < 5
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF:(SGXNIFTYUP)buyHighLowerTail-Continue')
        
    if(buy_downtrend_common(regression_data, regressionResult, reg, ws)):
        add_in_csv(regression_data, regressionResult, ws, None, None, None)
#     elif(0 < regression_data['PCT_day_change'] < 3 and -1 < regression_data['PCT_day_change'] < 3
#         and 1 < high_tail_pct(regression_data) < 2
#         and low_tail_pct(regression_data) < 5
#         ):
#         if(low_tail_pct(regression_data) < high_tail_pct(regression_data)):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None)
#         else:
#             add_in_csv(regression_data, regressionResult, ws, None, None, None)
    elif(high_tail_pct(regression_data) <= 2 and 3 <= low_tail_pct(regression_data) <= 5
        and -5 < regression_data['PCT_day_change'] < 5 and -5 < regression_data['PCT_change'] < 5
        and regression_data['PCT_day_change_pre1'] < 0
        and regression_data['PCT_day_change_pre2'] < 0
        and regression_data['forecast_day_PCT3_change'] < 0
        and regression_data['forecast_day_PCT4_change'] < 0
        and regression_data['forecast_day_PCT5_change'] < 0
        and regression_data['forecast_day_PCT7_change'] < 0
        and regression_data['forecast_day_PCT10_change'] < 0
        and (regression_data['forecast_day_PCT7_change'] < -5 or regression_data['forecast_day_PCT10_change'] < -5)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None) 
    elif(high_tail_pct(regression_data) <= 2 and 3 <= low_tail_pct(regression_data) <= 5
        and 0 < regression_data['PCT_day_change'] < 6 and 0 < regression_data['PCT_change'] < 6
        and regression_data['PCT_day_change_pre1'] > 0
        and regression_data['PCT_day_change_pre2'] > 0
        and regression_data['PCT_day_change_pre3'] > 0
        and regression_data['forecast_day_PCT3_change'] > 0
        and regression_data['forecast_day_PCT4_change'] > 0
        and regression_data['forecast_day_PCT5_change'] > 0
        and regression_data['forecast_day_PCT7_change'] > 0
        and regression_data['forecast_day_PCT10_change'] > 0
        and (5 < regression_data['forecast_day_PCT7_change'] < 10
             or 5 < regression_data['forecast_day_PCT10_change'] < 10)
        and (abs_month3High_more_than_month3Low(regression_data))
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF:buyStockInUptrend')
    elif(high_tail_pct(regression_data) <= 1 and 2 <= low_tail_pct(regression_data) <= 5
        and -2 < regression_data['PCT_day_change'] < 2 
        and regression_data['PCT_day_change_pre1'] > 0
        and regression_data['PCT_day_change_pre2'] > 0
        and regression_data['PCT_day_change_pre3'] > 0
        and regression_data['forecast_day_PCT3_change'] > 0
        and regression_data['forecast_day_PCT4_change'] > 0
        and regression_data['forecast_day_PCT5_change'] > 0

        and (regression_data['forecast_day_PCT7_change'] < 0
             and regression_data['forecast_day_PCT10_change'] < 0)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF:sellStockInUptrendReversal')  
    elif((3.5 < low_tail_pct(regression_data) < 6 or (2.5 < low_tail_pct(regression_data) < 5.5 and high_tail_pct(regression_data) < 1.5))
        and high_tail_pct(regression_data) < 3.5
        and (regression_data['PCT_day_change'] > -(low_tail_pct(regression_data)*2))
        ):
        if(regression_data['PCT_day_change'] < 0 and regression_data['PCT_change'] < 0
            and regression_data['PCT_day_change_pre1'] < -1
            and regression_data['PCT_day_change_pre2'] > 0
            and regression_data['forecast_day_PCT7_change'] > 0 and regression_data['forecast_day_PCT10_change'] > 0
            and abs(regression_data['PCT_day_change']) < low_tail_pct(regression_data)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF:sellHighLowerTail-Reversal-LastDayMarketUp')
        elif(regression_data['PCT_day_change'] < -1 and regression_data['PCT_change'] < -1
            and abs(regression_data['PCT_day_change']) < low_tail_pct(regression_data)
            ):
            if(regression_data['forecast_day_PCT7_change'] > 0 or regression_data['forecast_day_PCT10_change'] > 0
                #or (is_algo_sell(regression_data) and regression_data['PCT_day_change'] > -4 and abs(regression_data['PCT_day_change']) < low_tail_pct(regression_data))
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF:(NOT-UPTREND-LASTWEEK)sellHighLowerTail-Reversal-LastDayMarketUp')
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, None)
        elif(regression_data['forecast_day_PCT_change'] < -1
            and (((regression_data['forecast_day_PCT7_change'] > -5 and regression_data['forecast_day_PCT10_change'] > -5)
                    and (regression_data['forecast_day_PCT7_change'] > 0 or regression_data['forecast_day_PCT10_change'] > 0)
                    )
                or regression_data['forecast_day_PCT10_change'] > 0
                )
            ):
            if(regression_data['forecast_day_PCT_change'] < 0
                and regression_data['forecast_day_PCT2_change'] < 0
                and regression_data['forecast_day_PCT3_change'] < 0
                #and is_algo_buy(regression_data)
                and regression_data['forecast_day_PCT7_change'] > 0
                and regression_data['forecast_day_PCT10_change'] > 0
                and is_algo_sell(regression_data) == False
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF:(NOT-GLOBAL/SGX-DOWN-Last2DayMarketDown)mayBuyTail-tailGT2(*)sellHighLowerTail')
            elif(regression_data['forecast_day_PCT7_change'] > 0 and regression_data['forecast_day_PCT10_change'] > 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF:(GLOBAL-DOWN)sellHighLowerTail-Reversal-LastDayMarketUp')
            elif(is_algo_buy(regression_data) == False):
                add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF:(GLOBAL-DOWN)sellHighLowerTail-Reversal-LastDayMarketUp')
        elif(regression_data['PCT_day_change'] > 1 and regression_data['PCT_change'] > 1
            and is_algo_sell(regression_data)
            and regression_data['forecast_day_PCT7_change'] > 2
            and regression_data['forecast_day_PCT10_change'] > 2
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF-Risky:(GLOBAL-DOWN)sellHighLowerTail-Reversal-LastDayMarketUp')
        elif(3.5 < low_tail_pct(regression_data) < 6
            and (regression_data['PCT_day_change_pre1'] > 1.5 or regression_data['PCT_day_change_pre2'] > 1.5)
            and regression_data['forecast_day_PCT7_change'] > 2
            and regression_data['forecast_day_PCT10_change'] > 2
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF-Last2DayMarketUp:(GLOBAL-DOWN)sellHighLowerTail-Reversal-LastDayMarketUp')
    elif(2 < high_tail_pct_pre1(regression_data) < 6
        and -2.9 > regression_data['PCT_day_change'] > -4.1
        and abs(regression_data['PCT_day_change_pre1']) < 1.5
        and regression_data['PCT_day_change_pre2'] > 1
        and abs(regression_data['PCT_day_change_pre2']) > abs(regression_data['PCT_day_change_pre1'])
        #and regression_data['low'] >= regression_data['bar_low_pre2']
        #and abs_month6High_more_than_month6Low(regression_data)
        and low_tail_pct(regression_data) < 1.5
        and high_tail_pct(regression_data) < 1.5
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF-Last2DayMarketDown:(GLOBAL-UP)buyHighUpperTailPre1-Reversal-LastDayMarketDown')
        
    if((high_tail_pct(regression_data) > 1.5 and low_tail_pct(regression_data) < 1.5 and high_tail_pct(regression_data) > low_tail_pct(regression_data))
        and ((high_tail_pct_pre1(regression_data) > 1.5 and regression_data['high_pre1'] > regression_data['high'] and regression_data['low_pre1'] > regression_data['low'] and high_tail_pct_pre1(regression_data) > low_tail_pct_pre1(regression_data))
             or (high_tail_pct_pre2(regression_data) > 1.5 and regression_data['high_pre2'] > regression_data['high'] and regression_data['low_pre2'] > regression_data['low'] and high_tail_pct_pre2(regression_data) > low_tail_pct_pre2(regression_data))   
             )
        and (-2 < regression_data['PCT_day_change'] < 0)
        #and (regression_data['forecast_day_PCT2_change'] < 0 or regression_data['forecast_day_PCT3_change'] < 0 or regression_data['forecast_day_PCT4_change'] < 0)
        #and (regression_data['forecast_day_PCT5_change'] > 0 or regression_data['forecast_day_PCT7_change'] > 0 or regression_data['forecast_day_PCT10_change'] > 0)
        and (#abs_monthHigh_less_than_monthLow(regression_data)
            abs_week2High_less_than_week2Low(regression_data)
            or regression_data['week2HighChange'] > 0
            )
        ):
        if(regression_data['week2HighChange'] == regression_data['monthHighChange']):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF-Last2HighTail:(DOWNTREND)sellHighUpperTailPre')
        elif(abs_monthHigh_less_than_monthLow(regression_data)):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF-Last2HighTail:(DOWNTREND)sell(UPTREND)buy:HighUpperTailPre')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF-Last2HighTail:(DOWNTREND)sellHighUpperTailPre')
    elif((high_tail_pct(regression_data) > 1.5 and low_tail_pct(regression_data) < 1.5 and high_tail_pct(regression_data) > low_tail_pct(regression_data))
        and ((high_tail_pct_pre1(regression_data) > 1.5 and regression_data['high_pre1'] > regression_data['high'] and regression_data['low_pre1'] > regression_data['low'] and high_tail_pct_pre1(regression_data) > low_tail_pct_pre1(regression_data))
             or (high_tail_pct_pre2(regression_data) > 1.5 and regression_data['high_pre2'] > regression_data['high'] and regression_data['low_pre2'] > regression_data['low'] and high_tail_pct_pre2(regression_data) > low_tail_pct_pre2(regression_data))
             )
        and (-2 < regression_data['PCT_day_change'] < 2)
        and (regression_data['forecast_day_PCT2_change'] > 0 and regression_data['forecast_day_PCT3_change'] > 0)
        and (abs_monthHigh_more_than_monthLow(regression_data)
            or abs_week2High_more_than_week2Low(regression_data)
            )
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF-Last2HighTail:(DOWNTREND)sellHighUpperTailPre-1')
    elif((high_tail_pct(regression_data) > 1.5 and high_tail_pct(regression_data) > low_tail_pct(regression_data))
        and (high_tail_pct_pre1(regression_data) > 1.5 and high_tail_pct_pre1(regression_data) > low_tail_pct_pre1(regression_data))
        and regression_data['high_pre1'] < regression_data['high']
        and regression_data['PCT_day_change'] > 0
        and regression_data['PCT_day_change_pre1'] > 0
        and abs_week2High_less_than_week2Low(regression_data)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF-Last2HighTail:(DOWNTREND)sellHighUpperTailPre-last2DayUp')
        
    if((low_tail_pct(regression_data) > 1.5 and high_tail_pct(regression_data) < low_tail_pct(regression_data))
        and ((low_tail_pct_pre1(regression_data) > 1.5 and regression_data['PCT_day_change'] < 0 and regression_data['low_pre1'] > regression_data['low'] and high_tail_pct_pre1(regression_data) < low_tail_pct_pre1(regression_data))
             or (low_tail_pct_pre2(regression_data) > 1.5 and regression_data['PCT_day_change'] < 0 and regression_data['low_pre2'] > regression_data['low'] and high_tail_pct_pre2(regression_data) < low_tail_pct_pre2(regression_data))
             )
        and (0 < regression_data['PCT_day_change'] < 2)
        and (abs_week2High_more_than_week2Low(regression_data))
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF-Last2LowTail:(DOWNTREND)sellHighLowerTailPre')
    elif((low_tail_pct(regression_data) > 1.5 and high_tail_pct(regression_data) > 1.5)
        and (low_tail_pct_pre1(regression_data) > 1.5 and regression_data['high_pre1'] > regression_data['high'] and high_tail_pct_pre1(regression_data) < low_tail_pct_pre1(regression_data))
        and (0 < regression_data['PCT_day_change'] < 2)
        and (regression_data['forecast_day_PCT2_change'] < 0 and regression_data['forecast_day_PCT3_change'] < 0)
        and (abs_week2High_more_than_week2Low(regression_data)
             or regression_data['week2LowChange'] < 0
            )
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF-Last2LowTail:(DOWNTREND)sellHighLowerTailPre-1')
                             
def sell_af_down_continued(regression_data, regressionResult, reg, ws):
    return False
                  
def sell_af_oi_negative(regression_data, regressionResult, reg, ws):
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
                add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF:sellNegativeOI-0-checkBase(1%up)')
                return True
            if(0 < regression_data['PCT_day_change'] < 2 and 0 < regression_data['PCT_change'] < 2 
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF:sellNegativeOI-1-checkBase(1%up)')
                return True
        return False
    return False

def sell_af_vol_contract(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if((ten_days_less_than_minus_ten(regression_data) == False
            or ten_days_less_than_minus_fifteen(regression_data) == True
            or (regression_data['forecast_day_PCT5_change'] > -5 and regression_data['forecast_day_PCT7_change'] > -5)
        )
        and (float(regression_data['contract']) != 0 or float(regression_data['oi']) != 0)
        and float(regression_data['contract']) > 10
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
        and low_tail_pct(regression_data) < 1.5
        and regression_data['month3LowChange'] > 7.5
        and (regression_data['forecast_day_VOL_change'] > 100
            or (regression_data['PCT_day_change_pre2'] > 0
                and (((regression_data['volume'] - regression_data['volume_pre2'])*100)/regression_data['volume_pre2']) > 100
                and (((regression_data['volume'] - regression_data['volume_pre3'])*100)/regression_data['volume_pre3']) > 100
               )
           )
        and (mlpValue <= -0.3 and kNeighboursValue <= -0.3 or is_algo_sell(regression_data))
        ):
        if((regression_data['forecast_day_VOL_change'] > 400 and -5 < regression_data['PCT_day_change'] < -1 and -5 < regression_data['PCT_change'] < -1)
            and float(regression_data['contract']) > 50
            and (regression_data['forecast_day_PCT10_change'] > 8 or regression_data['forecast_day_PCT7_change'] > 8)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF:oiSell-2-checkBase')
            return True
        elif((regression_data['forecast_day_VOL_change'] > 150 and -3 < regression_data['PCT_day_change'] < -1 and -3 < regression_data['PCT_change'] < -1)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF:oiSell-1-checkBase')
            return True
        elif((regression_data['forecast_day_VOL_change'] > 70 and -3 < regression_data['PCT_day_change'] < -1 and -3 < regression_data['PCT_change'] < -1)
            and float(regression_data['contract']) > 10
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF:oiSell-0-checkBase')
            return True
    return False

def sell_af_vol_contract_contrarian(regression_data, regressionResult, reg, ws):
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
                add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF:Reversal(Test):buyReversalOI-0')
                return True
            return False
#         elif((regression_data['forecast_day_VOL_change'] > 35 and -2 < regression_data['PCT_day_change'] < -0.75 and -2 < regression_data['PCT_change'] < -0.5)
#             and float(regression_data['contract']) > 20
#             ):
#             if(('P@[') not in regression_data['sellIndia']):
#                 add_in_csv(regression_data, regressionResult, ws, None, None, 'Reversal(Test):buyReversalOI-1')
#                 return True
#             return False
#         elif((regression_data['forecast_day_VOL_change'] > 150 and -3 < regression_data['PCT_day_change'] < -0.75 and -3 < regression_data['PCT_change'] < -0.5)
#             ):
#             add_in_csv(regression_data, regressionResult, ws, None, None, 'Reversal(Test):buyReversalOI-2')
#             return True
#             elif(((regression_data['forecast_day_VOL_change'] > 300 and -3.5 < regression_data['PCT_day_change'] < -0.75 and -3.5 < regression_data['PCT_change'] < -0.5)
#                 or (regression_data['forecast_day_VOL_change'] > 400 and -4.5 < regression_data['PCT_day_change'] < -0.75 and -4.5 < regression_data['PCT_change'] < -0.5)
#                 )
#                 and regression_data['forecast_day_PCT10_change'] > -10
#                 ):
#                 add_in_csv(regression_data, regressionResult, ws, None, None, 'Reversal(Test):buyReversalOI-3-checkBase-(openAroundLastCloseAnd5MinuteChart)')
#                 return True
#             elif((regression_data['forecast_day_VOL_change'] > 500 and -5 < regression_data['PCT_day_change'] < -0.75 and -5 < regression_data['PCT_change'] < -0.5)
#                 #and float(regression_data['contract']) > 50
#                 and regression_data['forecast_day_PCT10_change'] > -10
#                 ):
#                 add_in_csv(regression_data, regressionResult, ws, None, None, 'Reversal(Test):buyReversalOI-4-checkBase-(openAroundLastCloseAnd5MinuteChart)')
#                 return True
        
#     if((('P@[' not in str(regression_data['buyIndia'])) and ('P@[' not in str(regression_data['sellIndia'])))
#         and (0 < regression_data['PCT_day_change'] < 1.5 and 0 < regression_data['PCT_change'] < 1.5)
#         and kNeighboursValue <= -1
#         and mlpValue <= 0
#         and is_recent_consolidation(regression_data) == False
#         and str(regression_data['score']) != '10'
#         and (low_tail_pct(regression_data) < 1.5 or (low_tail_pct(regression_data) < high_tail_pct(regression_data)))
#         ):
#             add_in_csv(regression_data, regressionResult, ws, None, None, 'Reversal(Test):sellReversalKNeighbours(upTrend)(upLastDay)')
#             return True        
    return False

def sell_af_others(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, True)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, True)
    mlpValue_cla, kNeighboursValue_cla = get_reg_or_cla(regression_data, False)
    mlpValue_other_cla, kNeighboursValue_other_cla = get_reg_or_cla_other(regression_data, False)
    
    if( -7.5 < regression_data['PCT_day_change_pre1'] < -1.5 and -8 < regression_data['PCT_change_pre1'] < -0.75
        and 0 < regression_data['PCT_day_change'] < 3
        and regression_data['bar_high'] < regression_data['bar_high_pre1']
        and (regression_data['high'] < regression_data['high_pre1'] or regression_data['low'] < regression_data['low_pre1'])
        and ((regression_data['forecast_day_PCT2_change'] < 0 and regression_data['forecast_day_PCT3_change'] < 0)
            or (regression_data['forecast_day_PCT3_change'] < 0 and regression_data['forecast_day_PCT4_change'] < 0)
            )
        and (regression_data['PCT_day_change_pre1'] > 0 or regression_data['PCT_day_change_pre2'] > 0 or regression_data['PCT_day_change_pre3'] > 0 or regression_data['PCT_day_change_pre4'] > 0)
        and regression_data['forecast_day_PCT10_change'] > -15
        and ((regression_data['forecast_day_PCT7_change'] > 0 and regression_data['forecast_day_PCT10_change'] > 0)
            or (regression_data['forecast_day_PCT3_change'] < 0
                and regression_data['forecast_day_PCT4_change'] < 0
                and regression_data['forecast_day_PCT5_change'] < 0
                and regression_data['forecast_day_PCT7_change'] < 0
                and regression_data['forecast_day_PCT10_change'] < 0
                )
            )
        and high_tail_pct(regression_data) > 1
        #and regression_data['year2LowChange'] > 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '%%AF:sellDowntrend-lastDayUp-ReversalHighTail')
        return True      
    return False

def sell_tail_reversal_filter(regression_data, regressionResult, reg, ws):
    if(('MaySell-CheckChart' in regression_data['filter1']) or ('MaySellCheckChart' in regression_data['filter1'])):
        if(1 < regression_data['PCT_day_change'] < 2
            and 1 < regression_data['PCT_change'] < 2
            and regression_data['PCT_day_change_pre1'] > 1
            and regression_data['PCT_day_change_pre2'] > 0
            and regression_data['PCT_day_change_pre3'] > 0
            and regression_data['monthHigh'] <= regression_data['high']
            and (regression_data['forecast_day_PCT7_change'] > 10 or regression_data['forecast_day_PCT10_change'] > 10)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '$$MaySell-CheckChart(downTrend-mayReverseLast4DaysUp)')
        elif(1 < regression_data['PCT_day_change'] < 2
            and 1 < regression_data['PCT_change'] < 2
            and regression_data['PCT_day_change_pre1'] > 1
            and regression_data['PCT_day_change_pre2'] > 0
            and regression_data['PCT_day_change_pre3'] > 0
            and regression_data['monthHigh'] <= regression_data['high']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '$$MaySell-CheckChart(downTrend-mayReverseLast4DaysUp)-Risky')
    
    if(-0.75 < regression_data['monthHighChange'] < 1.3
        and regression_data['monthLowChange'] > 5
        and regression_data['weekHighChange'] > 0
        and abs(regression_data['month3HighChange']) > abs(regression_data['month3LowChange']) and regression_data['month3HighChange'] < -15
        and abs(regression_data['monthHighChange']) < abs(regression_data['monthLowChange'])
        and regression_data['year2HighChange'] < 0
        and (regression_data['PCT_day_change_pre3'] > 1 or regression_data['PCT_day_change_pre4'] > 1)
        and (high_tail_pct(regression_data) >= 1 or (high_tail_pct(regression_data) > (abs(regression_data['PCT_day_change'])/3)))
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '$$MaySell-CheckChart-baseLine(inDownTrend-monthHigh)')
    if(-3 < regression_data['monthHighChange'] < 1.3
        and regression_data['monthLowChange'] > 5
        and regression_data['weekHighChange'] > 0
        and abs(regression_data['month3HighChange']) > abs(regression_data['month3LowChange']) and regression_data['month3HighChange'] < -15
        and abs(regression_data['monthHighChange']) < abs(regression_data['monthLowChange'])
        and regression_data['year2HighChange'] < 0
        and regression_data['PCT_day_change'] < -1
        and (regression_data['PCT_day_change_pre3'] > 1 or regression_data['PCT_day_change_pre4'] > 1)
        and (high_tail_pct(regression_data) >= 1 or (high_tail_pct(regression_data) > (abs(regression_data['PCT_day_change'])/3)))
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '$$(DOWNTREND-OR-GLOBALDOWN)MaySell-CheckChart-baseLine(inDownTrend-monthHigh)')
    elif(('MaySell-CheckChart' in regression_data['filter1']) or ('MaySellCheckChart' in regression_data['filter1'])):
        if(1 < regression_data['PCT_day_change'] < 3.5
            and 1 < regression_data['PCT_change'] < 3.5
            and 0 < regression_data['PCT_day_change_pre1']
            and 0 < regression_data['PCT_day_change_pre2']
            and 0 < regression_data['PCT_day_change_pre3'] 
            and regression_data['monthHighChange'] > -1
            and high_tail_pct(regression_data) < 2.5
            #and regression_data['PCT_day_change_pre3'] < regression_data['PCT_day_change']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '$$MaySell-CheckChart(monthHigh-minimumLast4DayUp)')
    
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
            add_in_csv(regression_data, regressionResult, ws, None, None, 'MaySellCheckChart-(|_|`|)')
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
                add_in_csv(regression_data, regressionResult, ws, None, None, 'MaySellCheckChart-(IndexNotDownInSecondHalf)')
    
    if('MaySell-CheckChart' in regression_data['filter1']):
        if(regression_data['PCT_day_change_pre1'] < -2
            and regression_data['PCT_day_change_pre2'] > 0
            and is_ema14_sliding_down(regression_data)
            and (last_5_day_all_down_except_today(regression_data) != True)
            and regression_data['bar_high'] <  regression_data['bar_high_pre1']
            and regression_data['high'] <  regression_data['high_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '(Test)MaySell-CheckChart(downTrend-lastDayUp)')
    
    if(('MaySellCheckChart' in regression_data['filter1'])
        and ('Reversal' not in regression_data['filter3'])
        and regression_data['year2LowChange'] > 10
        and low_tail_pct(regression_data) < 0.5
        ):
        if((1 < regression_data['PCT_day_change'] <= 2) and (0 < regression_data['PCT_change'] <= 2)
            and 3 > high_tail_pct(regression_data) > 1.8
            and regression_data['PCT_day_change_pre1'] > 0
            and regression_data['PCT_day_change_pre2'] > 0
            and regression_data['PCT_day_change_pre3'] > 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, "(Test)MaySellCheckChart-last3DayUp")
        elif((1 < regression_data['PCT_day_change'] <= 2) and (0 < regression_data['PCT_change'] <= 2)
            and 3 > high_tail_pct(regression_data) > 1.8
            and is_algo_sell(regression_data)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, "(Test)(check-chart-2-3MidCapCross)MaySellCheckChart-Risky")
    elif(('MaySellCheckChart' in regression_data['filter1'])
        and ('Reversal' not in regression_data['filter3'])
        and regression_data['year2LowChange'] > 10
        and low_tail_pct(regression_data) < 0.5
        ):
        if((3 < regression_data['PCT_day_change'] <= 5) and (2 < regression_data['PCT_change'] <= 6)
            and 5 > high_tail_pct(regression_data) > 2.8
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, "(Test)MaySellCheckChart-PCTDayChangeGT(3)BigLowTail-Risky")
    
    if(regression_data['year2HighChange'] < -3
        and regression_data['high'] == regression_data['weekHigh'] 
        and high_tail_pct(regression_data) > 1.5
        and (regression_data['PCT_day_change'] > -2 or is_algo_sell(regression_data))
        ):
        if(regression_data['weekHigh'] > regression_data['week2High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, "weekHighGTweek2")
        if(regression_data['monthHighChange'] > -3
            and regression_data['monthHigh'] != regression_data['weekHigh']
            and regression_data['monthHigh'] == regression_data['month2High']
            #and (is_algo_sell(regression_data)
                #or ((regression_data['bar_high'] - regression_data['month2BarHigh'])/regression_data['month2BarHigh'])*100 > -1.5
                #or regression_data['PCT_day_change'] < 0
                #)
            ):
            if(regression_data['monthHighChange'] > 5):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthHighChangeGT5")
            elif(regression_data['monthHighChange'] > 4):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthHighChangeGT4")
            elif(regression_data['monthHighChange'] > 3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthHighChangeGT3")
            elif(regression_data['monthHighChange'] > 2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthHighChangeGT2")
            elif(regression_data['monthHighChange'] > 1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthHighChangeGT1")
            elif(regression_data['monthHighChange'] > 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthHighChangeGT0")
            elif(regression_data['monthHighChange'] > -1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthHighChangeGT-1")
            elif(regression_data['monthHighChange'] > -2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthHighChangeGT-2")
            elif(regression_data['monthHighChange'] > -3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthHighChangeGT-3")
            add_in_csv(regression_data, regressionResult, ws, None, None, "(Test)MaySellCheckChart-monthHighReversal")
        elif(regression_data['monthHighChange'] > -3
            and regression_data['monthHigh'] != regression_data['weekHigh']
            ):
            if(regression_data['monthHighChange'] > 5):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthHighChangeGT5")
            elif(regression_data['monthHighChange'] > 4):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthHighChangeGT4")
            elif(regression_data['monthHighChange'] > 3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthHighChangeGT3")
            elif(regression_data['monthHighChange'] > 2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthHighChangeGT2")
            elif(regression_data['monthHighChange'] > 1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthHighChangeGT1")
            elif(regression_data['monthHighChange'] > 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthHighChangeGT0")
            elif(regression_data['monthHighChange'] > -1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthHighChangeGT-1")
            elif(regression_data['monthHighChange'] > -2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthHighChangeGT-2")
            elif(regression_data['monthHighChange'] > -3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthHighChangeGT-3")
            add_in_csv(regression_data, regressionResult, ws, None, None, "(Test)MaySellCheckChart-monthHighReversal-risky")
        elif((regression_data['monthHighChange'] > -5 and regression_data['SMA9'] < 0)
            and regression_data['monthHigh'] != regression_data['weekHigh']
            and regression_data['monthHigh'] == regression_data['month2High']
            ):
            if(regression_data['monthHighChange'] > 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthHighChangeGT0")
            elif(regression_data['monthHighChange'] > -1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthHighChangeGT-1")
            elif(regression_data['monthHighChange'] > -2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthHighChangeGT-2")
            elif(regression_data['monthHighChange'] > -3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthHighChangeGT-3")
            elif(regression_data['monthHighChange'] > -4):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthHighChangeGT-4")
            elif(regression_data['monthHighChange'] > -5):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthHighChangeGT-5")
            add_in_csv(regression_data, regressionResult, ws, None, None, "(Test)MaySellCheckChart-month2HighReversal-SMA9LT0")
        elif(regression_data['month2HighChange'] > -3
            and regression_data['month2High'] != regression_data['weekHigh']
            and regression_data['month2High'] == regression_data['month3High']
            #and (is_algo_sell(regression_data)
                #or ((regression_data['bar_high'] - regression_data['month3BarHigh'])/regression_data['month3BarHigh'])*100 > -1.5
                #or regression_data['PCT_day_change'] < 0
                #)
            ):
            if(regression_data['month2HighChange'] > 5):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2HighChangeGT5")
            elif(regression_data['month2HighChange'] > 4):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2HighChangeGT4")
            elif(regression_data['month2HighChange'] > 3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2HighChangeGT3")
            elif(regression_data['month2HighChange'] > 2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2HighChangeGT2")
            elif(regression_data['month2HighChange'] > 1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2HighChangeGT1")
            elif(regression_data['month2HighChange'] > 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2HighChangeGT0")
            elif(regression_data['month2HighChange'] > -1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2HighChangeGT-1")
            elif(regression_data['month2HighChange'] > -2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2HighChangeGT-2")
            elif(regression_data['month2HighChange'] > -3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2HighChangeGT-3")
            add_in_csv(regression_data, regressionResult, ws, None, None, "(Test)MaySellCheckChart-month2HighReversal")
        elif(regression_data['month2HighChange'] > -3
            and regression_data['month2High'] != regression_data['weekHigh']
            ):
            if(regression_data['month2HighChange'] > 5):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2HighChangeGT5")
            elif(regression_data['month2HighChange'] > 4):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2HighChangeGT4")
            elif(regression_data['month2HighChange'] > 3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2HighChangeGT3")
            elif(regression_data['month2HighChange'] > 2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2HighChangeGT2")
            elif(regression_data['month2HighChange'] > 1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2HighChangeGT1")
            elif(regression_data['month2HighChange'] > 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2HighChangeGT0")
            elif(regression_data['month2HighChange'] > -1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2HighChangeGT-1")
            elif(regression_data['month2HighChange'] > -2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2HighChangeGT-2")
            elif(regression_data['month2HighChange'] > -3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2HighChangeGT-3")
            add_in_csv(regression_data, regressionResult, ws, None, None, "(Test)MaySellCheckChart-month2HighReversal-risky")
        elif((regression_data['month2HighChange'] > -5 and regression_data['SMA9'] < 0)
            and regression_data['month2High'] != regression_data['weekHigh']
            and regression_data['month2High'] == regression_data['month3High']
            ):
            if(regression_data['month2HighChange'] > 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2HighChangeGT0")
            elif(regression_data['month2HighChange'] > -1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2HighChangeGT-1")
            elif(regression_data['month2HighChange'] > -2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2HighChangeGT-2")
            elif(regression_data['month2HighChange'] > -3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2HighChangeGT-3")
            elif(regression_data['month2HighChange'] > -4):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2HighChangeGT-4")
            elif(regression_data['month2HighChange'] > -5):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2HighChangeGT-5")
            add_in_csv(regression_data, regressionResult, ws, None, None, "(Test)MaySellCheckChart-month2HighReversal-SMA9LT0")
        elif(regression_data['month3HighChange'] > -3
            and regression_data['month3High'] != regression_data['weekHigh']
            #and regression_data['month3High'] != regression_data['high_month3'] 
            and regression_data['month6High'] == regression_data['yearHigh'] 
            ):
            if(regression_data['month3HighChange'] > 5):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month3HighChangeGT5")
            elif(regression_data['month3HighChange'] > 4):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month3HighChangeGT4")
            elif(regression_data['month3HighChange'] > 3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month3HighChangeGT3")
            elif(regression_data['month3HighChange'] > 2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month3HighChangeGT2")
            elif(regression_data['month3HighChange'] > 1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month3HighChangeGT1")
            elif(regression_data['month3HighChange'] > 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month3HighChangeGT0")
            elif(regression_data['month3HighChange'] > -1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month3HighChangeGT-1")
            elif(regression_data['month3HighChange'] > -2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month3HighChangeGT-2")
            elif(regression_data['month3HighChange'] > -3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month3HighChangeGT-3")
            add_in_csv(regression_data, regressionResult, ws, None, None, "(Test)MaySellCheckChart-month3HighReversal")
        elif(regression_data['month3HighChange'] > 0
            and regression_data['month3High'] != regression_data['weekHigh']
            and regression_data['month3High'] == regression_data['month6High'] 
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, "(Test)MaySellCheckChart-month3HighBreakReversal")
        elif(regression_data['month6HighChange'] > -3
            and regression_data['month6High'] != regression_data['weekHigh']
            #and regression_data['month6High'] != regression_data['high_month6']
            and regression_data['yearHigh'] == regression_data['year2High']
            ):
            if(regression_data['month6HighChange'] > 5):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month6HighChangeGT5")
            elif(regression_data['month6HighChange'] > 4):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month6HighChangeGT4")
            elif(regression_data['month6HighChange'] > 3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month6HighChangeGT3")
            elif(regression_data['month6HighChange'] > 2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month6HighChangeGT2")
            elif(regression_data['month6HighChange'] > 1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month6HighChangeGT1")
            elif(regression_data['month6HighChange'] > 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month6HighChangeGT0")
            elif(regression_data['month6HighChange'] > -1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month6HighChangeGT-1")
            elif(regression_data['month6HighChange'] > -2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month6HighChangeGT-2")
            elif(regression_data['month6HighChange'] > -3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month6HighChangeGT-3")
            add_in_csv(regression_data, regressionResult, ws, None, None, "(Test)MaySellCheckChart-month6HighReversal")
        elif(regression_data['month6HighChange'] > 0
            and regression_data['month6High'] != regression_data['weekHigh']
            and regression_data['month6High'] == regression_data['yearHigh'] 
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, "(Test)MaySellCheckChart-month6HighBreakReversal")
    
def sell_year_high(regression_data, regressionResult, reg, ws, ws1):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(regression_data['yearHighChange'] > -10 and regression_data['yearLowChange'] > 30 and -5 < regression_data['PCT_day_change'] < -0.50 
        and high_tail_pct(regression_data) > 1.5
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellYearHigh-highTail')
        return True
    elif(-10 < regression_data['yearHighChange'] < -1 and regression_data['yearLowChange'] > 30 and -5 < regression_data['PCT_day_change'] < -0.75 
        and ten_days_more_than_ten(regression_data) and regression_data['forecast_day_PCT7_change'] > 5 and regression_data['forecast_day_PCT5_change'] > -0.5 and regression_data['forecast_day_PCT4_change'] > -0.5
        and regression_data['forecast_day_PCT2_change'] < 0 and regression_data['forecast_day_PCT_change'] < 0
        and float(regression_data['forecast_day_VOL_change']) > 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'sellYearHigh')
        return True
    elif(-10 < regression_data['yearHighChange'] < 0 and regression_data['yearLowChange'] > 30 
        and (regression_data['PCT_day_change'] < 0 and regression_data['PCT_change'] < 0.5)
        and regression_data['forecast_day_PCT10_change'] > 5 and regression_data['forecast_day_PCT7_change'] > 3 and regression_data['forecast_day_PCT5_change'] > -0.5
        and regression_data['forecast_day_PCT2_change'] < 0 and regression_data['forecast_day_PCT_change'] < 0
        and float(regression_data['forecast_day_VOL_change']) > 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellYearHigh-1')
        return True
    elif(-10 < regression_data['yearHighChange'] < 0 and regression_data['yearLowChange'] > 30 
        and (regression_data['PCT_day_change'] < 0 and regression_data['PCT_change'] < 0.5)
        and regression_data['forecast_day_PCT10_change'] > 0 and regression_data['forecast_day_PCT7_change'] > 0 and regression_data['forecast_day_PCT5_change'] > 0
        and regression_data['forecast_day_PCT2_change'] < 0 and regression_data['forecast_day_PCT_change'] < 0
        and float(regression_data['forecast_day_VOL_change']) > 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellYearHigh-2')
        return True   
    return False

def sell_year_low(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(0 < regression_data['yearLowChange'] < 2 and regression_data['yearHighChange'] < -30 
        and -2 < regression_data['PCT_day_change'] < 0 and regression_data['forecast_day_PCT_change'] < 0
        and (str(regression_data['score']) != '1-1' or str(regression_data['score']) != '10')
        and all_day_pct_change_negative(regression_data) and no_doji_or_spinning_sell_india(regression_data)
        and float(regression_data['forecast_day_VOL_change']) > 30
        and regression_data['PCT_day_change_pre1'] < 0.5
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'sellYearLow')
        return True
    return False

def sell_up_trend(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(all_day_pct_change_positive_except_today(regression_data)
        and (regression_data['low'] < regression_data['low_pre1'])
        and -4.5 < regression_data['PCT_day_change'] < 0 and regression_data['PCT_change'] < 0
        and (regression_data['PCT_day_change'] < -2 or regression_data['PCT_change'] < -2)
        and regression_data['yearLowChange'] > 30
        and (low_tail_pct(regression_data) < 0.5 
             or (high_tail_pct(regression_data) > low_tail_pct(regression_data) and high_tail_pct(regression_data) > 1
                 and -2 < regression_data['PCT_day_change'] < 2 and -2 < regression_data['PCT_day_change_pre1'] < 2)
             or (low_tail_pct(regression_data) > 2.5 and abs(regression_data['PCT_day_change']) > low_tail_pct(regression_data))
             )
        ):
        if(ten_days_more_than_ten(regression_data)
            and regression_data['forecast_day_PCT7_change'] > 5
            and regression_data['forecast_day_PCT10_change'] > 10
            and (high_tail_pct(regression_data) > low_tail_pct(regression_data) and high_tail_pct(regression_data) > 1)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellUpTrend-highTail')
            return True
        elif(ten_days_more_than_ten(regression_data)
            and regression_data['forecast_day_PCT7_change'] > 5
            and regression_data['forecast_day_PCT10_change'] > 10
            and (low_tail_pct(regression_data) > 2.5)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellTrend-lowTail')
            return True
        elif(last_5_day_all_up_except_today(regression_data)
            and ten_days_more_than_ten(regression_data)
            and regression_data['forecast_day_PCT7_change'] > 5
            and regression_data['forecast_day_PCT10_change'] > 10
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellUpTrend-Risky-0')
            return True
        elif(last_5_day_all_up_except_today(regression_data)
            and ten_days_more_than_seven(regression_data)
            and regression_data['forecast_day_PCT7_change'] > 4
            and regression_data['forecast_day_PCT10_change'] > 4
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellUpTrend-Risky-1')
            return True
        elif(regression_data['forecast_day_PCT7_change'] > 4
            and regression_data['forecast_day_PCT10_change'] > 4
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellUpTrend-Risky-2')
            return True
        
    if(ten_days_more_than_ten(regression_data)
        and regression_data['forecast_day_PCT2_change'] > 0
        and regression_data['forecast_day_PCT3_change'] > 0
        and regression_data['forecast_day_PCT5_change'] > 0
        and regression_data['forecast_day_PCT7_change'] > 0
        and regression_data['forecast_day_PCT7_change'] > 0
        and -5 < regression_data['PCT_day_change'] < -2
        and -5 < regression_data['PCT_change'] < -2
        and regression_data['PCT_day_change_pre2'] > 0
        and regression_data['PCT_day_change_pre3'] > 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '##sellTenDaysMoreThanTen')
            
    return False

def sell_down_trend(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(('NearHigh' in regression_data['filter3'] or 'ReversalHigh' in regression_data['filter3'])
        and 'LT0' not in regression_data['filter3']
        and regression_data['SMA4'] < 0
        and regression_data['SMA4_2daysBack'] < 0
        and regression_data['PCT_day_change'] < -0.5 and regression_data['PCT_change'] < 0
        #and (regression_data['PCT_day_change_pre2'] < 0 or regression_data['PCT_day_change_pre3'] < 0)
        and (regression_data['PCT_day_change_pre1'] > 0 or regression_data['PCT_day_change_pre2'] > 0)
        ):
        if(regression_data['SMA4'] < regression_data['SMA4_2daysBack']
            and regression_data['SMA9'] < regression_data['SMA9_2daysBack']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellDownTrend-nearHigh')
            return True
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellDownTrend-Risky-nearHigh')
            return True
    if(regression_data['forecast_day_PCT10_change'] < -10
        and regression_data['year2HighChange'] < -60
        and regression_data['month3LowChange'] < 10
        and (regression_data['forecast_day_PCT_change'] >= -1.5)
        and 3 < regression_data['PCT_day_change'] < 7
        and 2 < regression_data['PCT_change'] < 8
        and (regression_data['PCT_day_change_pre1'] < -4 or regression_data['PCT_day_change_pre2'] < -4)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellYear2LowContinue')
        return True
    elif((regression_data['yearHighChange'] < -20 and regression_data['month3HighChange'] < -15)
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
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellDownTrend-0')
            return True
        elif(abs_yearHigh_less_than_yearLow(regression_data)
           and -4 < regression_data['PCT_day_change'] < -2 and -4 < regression_data['forecast_day_PCT_change'] < -2
           and regression_data['PCT_change'] < regression_data['PCT_day_change'] - 0.2
           and regression_data['forecast_day_PCT_change'] < regression_data['PCT_day_change'] - 0.2
           and regression_data['series_trend'] != 'upTrend'
           and str(regression_data['score']) != '10' 
           and (regression_data['forecast_day_PCT7_change'] > 0 and regression_data['forecast_day_PCT10_change'] > 0)
           ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellDownTrend-00')
            return True
        elif(abs_yearHigh_less_than_yearLow(regression_data)
           and regression_data['yearLowChange'] > 10 
           and -4 < regression_data['PCT_day_change'] < -2 and -4 < regression_data['forecast_day_PCT_change'] < -2
           and regression_data['forecast_day_PCT_change'] > regression_data['PCT_change']
           and regression_data['PCT_day_change_pre1'] > 0
           and regression_data['series_trend'] != 'upTrend'
           and str(regression_data['score']) != '10'
           and regression_data['forecast_day_PCT5_change'] > -3
           and (regression_data['forecast_day_PCT7_change'] > -5 and regression_data['forecast_day_PCT10_change'] > -7) 
           ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##longDownTrend-0-IndexNotDownLastDay(checkBase)')
            return True
        elif(abs_yearHigh_less_than_yearLow(regression_data)
           and regression_data['yearLowChange'] > 10 
           and -4 < regression_data['PCT_day_change'] < -2 and -4 < regression_data['forecast_day_PCT_change'] 
           and regression_data['forecast_day_PCT_change'] > regression_data['PCT_change']
           and regression_data['series_trend'] != 'upTrend'
           and str(regression_data['score']) != '10'
           and (regression_data['forecast_day_PCT7_change'] > -5 and regression_data['forecast_day_PCT10_change'] > -7) 
           ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##longDownTrend-1-IndexNotDownLastDay(checkBase)')
            return True
        elif(-4 < regression_data['PCT_day_change'] < -2 and -4 < regression_data['forecast_day_PCT_change'] 
           and regression_data['forecast_day_PCT_change'] > regression_data['PCT_change']
           and regression_data['series_trend'] != 'upTrend'
           and str(regression_data['score']) != '10'
           and (regression_data['forecast_day_PCT7_change'] > -5 and regression_data['forecast_day_PCT10_change'] > -7) 
           ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##longDownTrend-2-IndexNotDownLastDay(checkBase)')
            return True
        elif(-4 < regression_data['PCT_day_change'] < -2 and -4 < regression_data['forecast_day_PCT_change'] 
           and regression_data['forecast_day_PCT_change'] > regression_data['PCT_change']
           and regression_data['series_trend'] != 'upTrend'
           and str(regression_data['score']) != '10'
           and (regression_data['forecast_day_PCT7_change'] > -10 and regression_data['forecast_day_PCT10_change'] > -10) 
           ):
            #add_in_csv(regression_data, regressionResult, ws, None, None, 'sellDownTrend-2-onlyNews')
            return False
    elif(all_day_pct_change_negative(regression_data) and -4 < regression_data['PCT_day_change'] < -2 and regression_data['yearLowChange'] > 30
        and regression_data['forecast_day_PCT10_change'] <= regression_data['PCT_change'] - 2
        and regression_data['forecast_day_PCT10_change'] <= regression_data['PCT_day_change'] - 2
        and float(regression_data['forecast_day_VOL_change']) > 30
        and regression_data['PCT_day_change_pre1'] < 0.5
        and float(regression_data['contract']) > 10
        and no_doji_or_spinning_sell_india(regression_data)):
        add_in_csv(regression_data, regressionResult, ws, None, None, '##longDownTrend-Risky-IndexNotDownLastDay(checkBase)')
        return True
    return False

def sell_final(regression_data, regressionResult, reg, ws, ws1):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(regression_data['yearLowChange'] > 10
       and regression_data['yearHighChange'] < -5
       and regression_data['month3HighChange'] < -3
       and -4 < regression_data['PCT_day_change'] < -1 and -4 < regression_data['PCT_change'] < -1
       #and regression_data['forecast_day_VOL_change'] > 0
       #and abs(regression_data['PCT_day_LC']) < 0.3
       and low_tail_pct(regression_data) < 1
       #and str(regression_data['score']) != '10'
       ):
        if(-90 < regression_data['yearHighChange'] < -10
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
            add_in_csv(regression_data, regressionResult, ws, None, None, 'sellFinal')
            return True
        elif(-90 < regression_data['yearHighChange'] < -10
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
            add_in_csv(regression_data, regressionResult, ws, None, None, 'sellFinal1')
            return True
    elif(regression_data['forecast_day_PCT4_change'] >= -0.5
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
                #add_in_csv(regression_data, regressionResult, ws, None, None, 'sellFinalCandidate-0')
                add_in_csv(regression_data, regressionResult, ws, None, None, None)
                return True
            elif(-5 < regression_data['PCT_day_change'] < -2 and -5 < regression_data['PCT_change'] < -2
               and regression_data['PCT_day_change_pre1'] > 0
               and (regression_data['yearHighChange'] > -30 or regression_data['yearLowChange'] > 30)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'sellFinalCandidate-00')
                return True
            elif(-6.5 < regression_data['PCT_day_change'] < -2 and -6.5 < regression_data['PCT_change'] < -2
               and regression_data['PCT_day_change_pre1'] > 0
               and (regression_data['yearHighChange'] > -30 or regression_data['yearLowChange'] > 30)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'sellFinalCandidate-00HighChange')
                return True
            elif(-2.5 < regression_data['PCT_day_change'] < -1 and -2.5 < regression_data['PCT_change'] < -1
                and regression_data['PCT_day_change_pre1'] < 0
                and (mlpValue <= -1 or kNeighboursValue <= -1)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellFinalCandidate-1')
                return True
            elif(-4 < regression_data['PCT_day_change'] < -1 and -4 < regression_data['PCT_change'] < -1 
                and no_doji_or_spinning_sell_india(regression_data)
                and regression_data['PCT_day_change_pre1'] < 0
                and (mlpValue <= -1 or kNeighboursValue <= -1)
                ):   
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellFinalCandidate-2')
                return True
            elif(-2.5 < regression_data['PCT_day_change'] < -0.5 and -2.5 < regression_data['PCT_change'] < -0.5
                and regression_data['PCT_day_change_pre1'] < 0
                and (mlpValue <= -1 or kNeighboursValue <= -1)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '##(Test)sellFinalCandidate-2')
                return True
        elif((((regression_data['open'] - regression_data['close']) * 1.5 > regression_data['high'] - regression_data['low']) or (regression_data['forecast_day_PCT_change'] < 0 and regression_data['PCT_day_change'] < -1))
            and (regression_data['yearHighChange'] > -30 or regression_data['yearLowChange'] > 30)
            ):
            if(-2.5 < regression_data['PCT_day_change'] < -1 and -2.5 < regression_data['PCT_change'] < -1 
                and no_doji_or_spinning_sell_india(regression_data) and no_doji_or_spinning_buy_india(regression_data)
                ):
                if(regression_data['forecast_day_VOL_change'] > -20):
                    add_in_csv(regression_data, regressionResult, ws, None, None, '##(Test)sellFinalCandidate-3')
                    return True
            elif(-5 < regression_data['PCT_day_change'] < -1 and -5 < regression_data['PCT_change'] < -1 
                and no_doji_or_spinning_sell_india(regression_data) and no_doji_or_spinning_buy_india(regression_data)
                ):
                if(regression_data['forecast_day_VOL_change'] > 0):
                    add_in_csv(regression_data, regressionResult, ws, None, None, '##(Test)sellFinalCandidate-4')
                    return True

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
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellFinalCandidate-(lastDayUp)')
                    return True
                elif(regression_data['SMA25'] < 0 and regression_data['SMA50'] < 0
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyFinalContinue-(lastDayUp)')
                    return True
                else:
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellFinalCandidate-1-(lastDayUp)')
                    return True
                return False
            if(-5 < regression_data['PCT_day_change'] < -2 and -5 < regression_data['PCT_change'] < -2
                and regression_data['PCT_day_change_pre1'] > 0
                and (regression_data['yearHighChange'] > -30 or regression_data['yearLowChange'] > 30)
                and regression_data['forecast_day_PCT7_change'] > 5
                and regression_data['forecast_day_PCT10_change'] > 10
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellFinalCandidate-(lastDayUp)-(highChange)')
                return True
            elif(regression_data['PCT_day_change'] < -2 and regression_data['PCT_change'] < -2
                and regression_data['PCT_day_change_pre1'] > 0
                and (regression_data['yearHighChange'] > -30 or regression_data['yearLowChange'] > 30)
                and (regression_data['forecast_day_PCT7_change'] < 5 or regression_data['forecast_day_PCT10_change'] < 10)
                ):
                if(('P@[' not in regression_data['sellIndia'])):
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyFinalContinue-(lastDayUp)-(highChange)')
                    return True
                else:
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellFinalCandidate-(lastDayUp)-(highChange)')
                    return True
            if(-4 < regression_data['PCT_day_change'] < -0.5 and -4 < regression_data['PCT_change'] < -0.5
                and regression_data['PCT_day_change_pre1'] < 0
                and 'P@[' in regression_data['buyIndia']
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellFinalCandidate-(lastDayDown)-(buyPattern)')
                return True
        if((((regression_data['open'] - regression_data['close']) * 1.5 > regression_data['high'] - regression_data['low']) or (regression_data['forecast_day_PCT_change'] < 0 and regression_data['PCT_day_change'] < -1))
            and (regression_data['yearHighChange'] > -30 or regression_data['yearLowChange'] > 30)
            ):
            if(-2.5 < regression_data['PCT_day_change'] < -1 and -2.5 < regression_data['PCT_change'] < -1 
                and no_doji_or_spinning_sell_india(regression_data) and no_doji_or_spinning_buy_india(regression_data)
                ):
                if(regression_data['forecast_day_VOL_change'] > -20
                    ):    
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellFinalCandidate-3')
                    return True
                return False
            if(-5 < regression_data['PCT_day_change'] < -1 and -5 < regression_data['PCT_change'] < -1 
                and no_doji_or_spinning_sell_india(regression_data) and no_doji_or_spinning_buy_india(regression_data)
                ):
                if(regression_data['forecast_day_VOL_change'] > -20
                    ):    
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellFinalCandidate-4')
                    return True
                return False
    return False            
    
def sell_pattern(regression_data, regressionResult, reg, ws, ws1):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    sell_pattern_without_mlalgo(regression_data, regressionResult)
    if(regression_data['yearHighChange'] < -10):
        if(is_algo_sell(regression_data)
            and regression_data['sellIndia_avg'] < -1.5 
            and low_tail_pct(regression_data) < 1.5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'sellPatternsML')
            return True
        
def sell_morning_star_buy(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(-8 < regression_data['forecast_day_PCT_change'] < 0
        and ((regression_data['year2LowChange'] > 15) or (regression_data['year2LowChange'] < 2))
        and high_tail_pct(regression_data) < 1
        and low_tail_pct(regression_data) > 2.5
        and regression_data['forecast_day_PCT10_change'] < (regression_data['forecast_day_PCT_change'] - 5)
        ):
        if(-6 < regression_data['PCT_day_change'] < -2 and -6 < regression_data['PCT_change'] < -2
            and (regression_data['close'] - regression_data['low']) > ((regression_data['open'] - regression_data['close']))
            and (regression_data['close'] - regression_data['low']) >= ((regression_data['high'] - regression_data['open']) * 3)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'buyMorningStar-HighLowerTail')
            return True
        elif(-6 < regression_data['PCT_day_change'] < 0 and -6 < regression_data['PCT_change'] < 0
            and (regression_data['bar_low'] - regression_data['low']) >= ((regression_data['bar_high'] - regression_data['bar_low']) * 3)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'buyMorningStar-HighLowerTail-(checkChart)')
        elif(-6 < regression_data['PCT_day_change'] < 2 and -6 < regression_data['PCT_change'] < 2
            and regression_data['PCT_day_change_pre1'] < 0
            and regression_data['PCT_day_change_pre2'] < 0
            and regression_data['PCT_day_change_pre3'] < 0
            and (regression_data['bar_low'] - regression_data['low']) >= ((regression_data['bar_high'] - regression_data['bar_low']) * 2)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'buyMorningStar-(checkChart)')
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
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyMorningStar-dayDown')
            return True
        if(0.3 < regression_data['PCT_day_change'] < 1
            and (regression_data['open'] - regression_data['low']) >= ((regression_data['open'] - regression_data['close']) * 3)
            and (regression_data['open'] - regression_data['low']) >= ((regression_data['high'] - regression_data['close']) * 3)
            and regression_data['year2HighChange'] > -50
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyMorningStar-dayUp')
            return True
        if(high_tail_pct(regression_data) < 1.5
           and low_tail_pct(regression_data) > 1.5
           ):
            if(0 < regression_data['PCT_day_change'] < 1 and 0 < regression_data['PCT_change'] < 1 
                and kNeighboursValue >= 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyMorningStar-0-NotUpSecondHalfAndUp2to3')
                return True
            if(-1.5 < regression_data['PCT_day_change'] < 0 and -1.5 < regression_data['PCT_change'] < 0
                and (regression_data['close'] - regression_data['low']) >= ((regression_data['open'] - regression_data['close']) * 3)
                and (regression_data['close'] - regression_data['low']) >= ((regression_data['high'] - regression_data['open']) * 3)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyMorningStar-1(NotUpSecondHalfAndUp2to3)')
                return True
            if(0 < regression_data['PCT_day_change'] < 1
                and (regression_data['close'] - regression_data['low']) >= ((regression_data['open'] - regression_data['close']) * 3)
                and (regression_data['close'] - regression_data['low']) >= ((regression_data['high'] - regression_data['open']) * 3)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyMorningStar-2(NotUpSecondHalfAndUp2to3)')
                return True
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
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyEveningStar-0(Buy-After-1pc-down)')
                return True
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, 'sellEveningStar-0')
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
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellEveningStar-2(Check2-3MidCapCross)')
                return True
        elif((low_tail_pct(regression_data) < 0.5 or (regression_data['forecast_day_PCT_change'] > 6 and low_tail_pct(regression_data) < 1))
            and 2 < high_tail_pct(regression_data) < 3.5
            and low_tail_pct(regression_data) < 0.5
            ):
            if(2 > regression_data['PCT_day_change'] > 0.5 and 2 > regression_data['PCT_change'] > 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellEveningStar-Risky-3(Check2-3MidCapCross)')
                return True
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
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellDayHighVolLow-0')
            return True
        elif((regression_data['PCT_day_change'] > 5 or regression_data['PCT_change'] > 5)
           and float(regression_data['forecast_day_VOL_change']) < -20
           and regression_data['PCT_day_change'] > regression_data['PCT_day_change_pre1'] > 0
           and regression_data['PCT_day_change_pre1'] > 1
           and regression_data['forecast_day_PCT_change'] > 4
           and regression_data['yearLowChange'] < 80
           ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyDayHighVolLow-0')
            return True
        elif((regression_data['PCT_day_change'] > 5 and regression_data['PCT_change'] > 4)
           and float(regression_data['forecast_day_VOL_change']) < -20
           and regression_data['PCT_day_change'] > regression_data['PCT_day_change_pre1'] > 0
           and regression_data['PCT_day_change_pre1'] > 1.5
           and regression_data['month3LowChange'] < 30
           ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellDayHighVolLow-01-checkMorningTrend(.5SL)')
            return True
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
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyFinalContinue-0')
                    return True
            if(-5 < regression_data['PCT_day_change'] < -1 and -5 < regression_data['PCT_change'] < -1 
                and no_doji_or_spinning_sell_india(regression_data) and no_doji_or_spinning_buy_india(regression_data)
                ):
                if(regression_data['forecast_day_VOL_change'] <= -30
                    and (regression_data['PCT_day_change_pre1'] < -1)
                    and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
                    and regression_data['weekLowChange'] > 2
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyFinalContinue-1')
                    return True
                elif(regression_data['forecast_day_VOL_change'] <= -10
                    and (regression_data['PCT_day_change_pre1'] < -1)
                    and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
                    and regression_data['weekLowChange'] > 2
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyFinalContinue-2')
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
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyFinalContinue-3')
                return True
    return False   

def sell_trend_break(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
#     if(regression_data['SMA200'] == 1
#        and regression_data['PCT_day_change'] < -2 and regression_data['PCT_change'] < -2
#        ):
#         add_in_csv(regression_data, regressionResult, ws, None, None, '##TestBreakOutSellConsolidate-0')
#         return True
    
    flag = False
    if(regression_data['yearLowChange'] < 5
       and 'M@[,RSI' in str(regression_data['buyIndia'])
       and 'P@[' not in str(regression_data['sellIndia'])
       and (regression_data['PCT_day_change'] < -5 and regression_data['PCT_change'] < 0)
       #and mlpValue >= 1
       ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisRSISellCandidate(yearLow)-lessThanMinus5')
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
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisFinalBreakOutSell-0')
                flag = True
    return flag
      
def sell_oi(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    
    if(regression_data['PCT_day_change'] < -2 and regression_data['PCT_change'] < -2
        and abs(regression_data['PCT_day_change']) > abs(regression_data['PCT_day_change_pre1'])
        and regression_data['PCT_day_change_pre1'] < 0
        and regression_data['PCT_day_change_pre2'] < 0.5
        and regression_data['volume'] > regression_data['volume_pre1']
        and regression_data['volume'] > regression_data['volume_pre2']
        and (regression_data['forecast_day_VOL_change'] > 20
            or regression_data['volume'] > regression_data['volume_pre1'] > regression_data['volume_pre2']
            )
        ):
        if(regression_data['week2HighChange'] < 0
            and abs_week2High_more_than_week2Low(regression_data)
            and abs_monthHigh_more_than_monthLow(regression_data)
            and abs_month3High_more_than_month3Low(regression_data)
            and low_tail_pct(regression_data) > abs(regression_data['PCT_day_change'])/2
            and regression_data['PCT_day_change'] < -5 and regression_data['PCT_change'] < regression_data['PCT_day_change']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:sellAboveTail-BuyAtClose:3dayDownVolCrossedAtWeek2Low-highLowerTail')
        elif(regression_data['week2LowChange'] > 4.0
            and (regression_data['week2HighChange'] > 0
                or abs_week2High_less_than_week2Low(regression_data)
                or abs_weekHigh_less_than_weekLow(regression_data)
                )
            and regression_data['PCT_day_change_pre3'] > 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:sell3dayDownVolCrossedAtWeek2High')
        elif(regression_data['week2HighChange'] < -4.0
            and (regression_data['low']-regression_data['high']) < regression_data['PCT_day_change_pre1']
            and abs_week2High_more_than_week2Low(regression_data)
            and abs_monthHigh_more_than_monthLow(regression_data)
            and abs_month3High_more_than_month3Low(regression_data)
            and low_tail_pct(regression_data) < 2
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:buy3dayDownVolCrossedAtWeek2Low')       
    elif(regression_data['PCT_day_change'] < -2 and regression_data['PCT_change'] < -2
        #and abs(regression_data['PCT_day_change']) > abs(regression_data['PCT_day_change_pre1'])
        and regression_data['PCT_day_change_pre1'] < 0
        #and regression_data['PCT_day_change_pre2'] < 0
        and regression_data['PCT_day_change_pre3'] > 0
        and regression_data['volume'] < regression_data['volume_pre1']
        #and regression_data['volume'] < regression_data['volume_pre2']
        and regression_data['forecast_day_VOL_change'] < 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL(Test):sellContinueVolDown')
             
    if(abs(regression_data['month3HighChange']) > abs(regression_data['month3LowChange'])
        and abs(regression_data['monthHighChange']) > abs(regression_data['monthLowChange'])
        and regression_data['PCT_day_change'] > 0
        and regression_data['PCT_day_change_pre1'] > 0
        and regression_data['PCT_day_change_pre2'] > 0
        and (regression_data['forecast_day_PCT3_change'] > 5 or regression_data['forecast_day_PCT4_change'] > 5)
        ):
        if(regression_data['PCT_day_change'] > 1
            and regression_data['PCT_day_change_pre1'] > 1
            and regression_data['PCT_day_change_pre2'] > 1
            and -1 < regression_data['PCT_day_change_pre3'] < 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkSellRevarsalLast3DayUpAtMonth3Low') 
        if(regression_data['PCT_day_change'] > 1
            and regression_data['PCT_day_change_pre1'] > 1
            and regression_data['PCT_day_change_pre2'] > 1
            and ((abs(regression_data['PCT_day_change']) > abs(regression_data['PCT_day_change_pre1']) and regression_data['forecast_day_VOL_change'] < -10)
                or (abs(regression_data['PCT_day_change']) < abs(regression_data['PCT_day_change_pre1']) and regression_data['forecast_day_VOL_change'] > 10)
                or (abs(regression_data['PCT_day_change']) > (1.5*abs(regression_data['PCT_day_change_pre1'])) and regression_data['volume'] < regression_data['volume_pre1'])
                or ((1.5*abs(regression_data['PCT_day_change'])) < abs(regression_data['PCT_day_change_pre1']) and regression_data['volume'] > regression_data['volume_pre1'])
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:sellRevarsalVolCrossed')
            
    if(regression_data['PCT_day_change'] > 1 and regression_data['PCT_change'] > 1
        and regression_data['PCT_day_change_pre1'] < 0
        and regression_data['PCT_day_change_pre2'] > 1
        and regression_data['volume'] > regression_data['volume_pre1']
        ):
        if(abs(regression_data['PCT_day_change']) > abs(regression_data['PCT_day_change_pre1'])
            and 0 < regression_data['forecast_day_PCT3_change'] < regression_data['forecast_day_PCT4_change'] < regression_data['forecast_day_PCT5_change']
            and 1 < regression_data['PCT_day_change'] < 3
            and regression_data['PCT_day_change_pre3'] > 0
            and 0 < regression_data['forecast_day_VOL_change'] < 150
            and 0 < regression_data['contract'] < 150 
            and 0 < regression_data['oi_next'] < 150
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:buyContinueZigZagVolCrossedUptrend')
        elif(abs(regression_data['PCT_day_change']) > 2*abs(regression_data['PCT_day_change_pre1'])
            and regression_data['PCT_day_change'] > 4
            and regression_data['PCT_day_change_pre1'] < -1
            and 0 < regression_data['forecast_day_VOL_change'] < 150
            and 20 < regression_data['contract'] < 150 
            and 50 < regression_data['oi_next'] < 150
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:buyContinueZigZagVolCrossed')
        elif(abs(regression_data['PCT_day_change']) < 2*abs(regression_data['PCT_day_change_pre1'])
            and regression_data['PCT_day_change'] > 2
            and regression_data['PCT_day_change_pre1'] < -1 
            and regression_data['PCT_day_change_pre3'] < 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:sellZigZagVolCrossed')
        
            
    if(regression_data['PCT_day_change'] < -2 and regression_data['PCT_change'] < -1
        and regression_data['PCT_day_change_pre1'] < 0
        and regression_data['PCT_day_change_pre2'] > 0
        and regression_data['PCT_day_change_pre3'] > 0
        and regression_data['PCT_day_change_pre4'] > 0
        and regression_data['volume'] > regression_data['volume_pre1']
        and regression_data['volume'] > regression_data['volume_pre2']
        and regression_data['volume'] > regression_data['volume_pre3']
        #and regression_data['volume'] > regression_data['volume_pre4']
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:volumeUpsergedLast2n3n4DayUp')
    elif(-5 < regression_data['PCT_day_change'] < -2 and -5 < regression_data['PCT_change'] < -1
        and regression_data['PCT_day_change_pre1'] < -1
        and regression_data['PCT_day_change_pre2'] > 0
        and regression_data['PCT_day_change_pre3'] > 0
        and regression_data['PCT_day_change_pre4'] < 0
        and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change_pre2'])
        and regression_data['volume'] > regression_data['volume_pre1']
        and regression_data['volume'] > regression_data['volume_pre2']
        and regression_data['volume'] > regression_data['volume_pre3']
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:buyVolumeUpsergedLast2n3DayUp')
    elif(-5 < regression_data['PCT_day_change'] < -2 and -5 < regression_data['PCT_change'] < -1
        and -1 < regression_data['PCT_day_change_pre1'] < 0
        and regression_data['PCT_day_change_pre2'] > 0
        and regression_data['PCT_day_change_pre3'] > 0
        and regression_data['PCT_day_change_pre4'] < 0
        and abs(regression_data['PCT_day_change_pre1']) < abs(regression_data['PCT_day_change_pre2'])
        and regression_data['volume'] > regression_data['volume_pre1']
        and regression_data['volume'] > regression_data['volume_pre2']
        and regression_data['volume'] > regression_data['volume_pre3']
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:sellVolumeUpsergedLast2n3DayUp')
    if(regression_data['PCT_day_change'] < -2.5 and regression_data['PCT_change'] < -1
        and regression_data['PCT_day_change_pre1'] > 0
        and regression_data['PCT_day_change_pre2'] > 0
        and regression_data['volume'] > regression_data['volume_pre1']
        and regression_data['volume'] > regression_data['volume_pre2']
        and (regression_data['forecast_day_VOL_change'] > 50 or regression_data['PCT_day_change'] < -3)
        and 50 < regression_data['forecast_day_VOL_change'] < 150
        and 20 < regression_data['contract'] < 150 
        and 50 < regression_data['oi_next'] < 150
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:sellVolumeUpsergedLast1n2DayUp')
        
    return True

#     if(((regression_data['PCT_day_change'] < -1 or regression_data['PCT_change'] < -1)
#              or
#              (regression_data['PCT_day_change'] < -0.75 and regression_data['PCT_change'] < -0.75)
#              and regression_data['forecast_day_PCT_change'] > -2
#              and regression_data['forecast_day_PCT2_change'] > -2
#              and regression_data['forecast_day_PCT3_change'] > -2
#              and regression_data['forecast_day_PCT4_change'] > -2
#              and regression_data['forecast_day_PCT5_change'] > -2
#              and regression_data['forecast_day_PCT7_change'] > -2
#              and regression_data['forecast_day_PCT10_change'] > -2
#             )
#         and regression_data['forecast_day_PCT_change'] < 0
#         and regression_data['forecast_day_PCT2_change'] < 0
#         and regression_data['forecast_day_PCT3_change'] < 0
#         and -5 < regression_data['forecast_day_PCT4_change'] < 0
#         and regression_data['forecast_day_PCT5_change'] > -5
#         and regression_data['forecast_day_PCT7_change'] > -5
#         and regression_data['forecast_day_PCT10_change'] > -5
#         and (regression_data['PCT_day_change'] > 0
#             or regression_data['PCT_day_change_pre1'] > 0
#             or regression_data['PCT_day_change_pre2'] > 0
#             or regression_data['PCT_day_change_pre3'] > 0
#             or regression_data['PCT_day_change_pre4'] > 0
#             )
#         and (regression_data['forecast_day_VOL_change'] > 150
#             or (regression_data['PCT_day_change_pre2'] < 0
#                 and (((regression_data['volume'] - regression_data['volume_pre2'])*100)/regression_data['volume_pre2']) > 100
#                 and (((regression_data['volume'] - regression_data['volume_pre3'])*100)/regression_data['volume_pre3']) > 100
#                )
#            )
#         and float(regression_data['contract']) > 100
#         and(regression_data['PCT_day_change_pre1'] < 0 
#                or (regression_data['volume'] > regression_data['volume_pre2'] and regression_data['volume'] > regression_data['volume_pre3'])
#             )
#         and regression_data['open'] > 50
#         and (last_4_day_all_down(regression_data) == False) #Uncomment0 If very less data
#         and (low_tail_pct(regression_data) < 1)
#         and (low_tail_pct(regression_data) < 1.5 or (low_tail_pct(regression_data) < high_tail_pct(regression_data)))
#         and regression_data['month3LowChange'] > 7.5
#         ):
#         if(-3 < regression_data['PCT_day_change'] < -1 and -3 < regression_data['PCT_change'] < -1 
#             ):
#             if(regression_data['forecast_day_PCT10_change'] > 0 or regression_data['forecast_day_PCT7_change'] > 0):
#                 add_in_csv(regression_data, regressionResult, ws, None, None, 'openInterest-0')
#                 return True
#             elif(regression_data['forecast_day_PCT10_change'] > -10 or (regression_data['forecast_day_PCT5_change'] > -5 and regression_data['forecast_day_PCT7_change'] > -5)):
#                 add_in_csv(regression_data, regressionResult, ws, None, None, 'openInterest-1')
#                 return True
#             else:
#                 add_in_csv(regression_data, regressionResult, ws, None, None, 'openInterest-1-Risky')
#                 return True
#         if(-6 < regression_data['PCT_day_change'] < -1 and -6 < regression_data['PCT_change'] < -1 
#             and float(regression_data['forecast_day_VOL_change']) > 300 
#             ):
#             if(regression_data['forecast_day_PCT10_change'] > 0 or regression_data['forecast_day_PCT7_change'] > 0
#                ):
#                 add_in_csv(regression_data, regressionResult, ws, None, None, 'openInterest-0-checkConsolidation')
#                 return True
#             elif(regression_data['forecast_day_PCT10_change'] > -10 or (regression_data['forecast_day_PCT5_change'] > -5 and regression_data['forecast_day_PCT7_change'] > -5)
#                 -4 < regression_data['PCT_day_change'] < -1 and -4 < regression_data['PCT_change'] < -1
#                 ):
#                 add_in_csv(regression_data, regressionResult, ws, None, None, 'openInterest-1-checkConsolidation')
#                 return True
#             else:
#                 add_in_csv(regression_data, regressionResult, ws, None, None, 'openInterest-1-Risky')
#                 return True 
    
def sell_heavy_downtrend(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    return False

def sell_random_filter(regression_data, regressionResult, reg, ws):        
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
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyMay5DayFloorReversal')
        
#     if(-6 < regression_data['PCT_day_change'] < -1.5
#         and -6 < regression_data['PCT_change'] 
#         and (regression_data['PCT_day_change_pre2'] > 0 or regression_data['PCT_day_change_pre3'] > 0)
#         and regression_data['low'] < regression_data['low_pre2']
#         and regression_data['forecast_day_PCT3_change'] < 0
#         and regression_data['forecast_day_PCT2_change'] < 0
#         and regression_data['forecast_day_PCT_change'] < 0
#         and regression_data['SMA4'] < regression_data['SMA4_2daysBack']
#         and regression_data['forecast_day_PCT10_change'] > 0
#         and ((regression_data['forecast_day_PCT4_change'] < 0
#               and regression_data['forecast_day_PCT7_change'] > 0
#                 and (regression_data['forecast_day_PCT7_change'] > 5
#                     or regression_data['forecast_day_PCT10_change'] > 5
#                     )
#                 )
#             ) 
#         ):
#         add_in_csv(regression_data, regressionResult, ws, None, None, 'check10DayHighReversal')
    
    if('DowningMA-Risky' not in regression_data['filter4'] 
        and 'DowningMA' in regression_data['filter4']
        and (regression_data['high'] < regression_data['high_pre1']) 
        and (0 < regression_data['PCT_day_change'] < 2) and (0 < regression_data['PCT_change'] < 2)
        and (regression_data['forecast_day_PCT5_change'] < -3
             or regression_data['forecast_day_PCT7_change'] < -3
             or regression_data['forecast_day_PCT10_change'] < -3
            )
        ):
        if(-0.5 < regression_data['week2LowChange'] < 0.5 
            and regression_data['week2Low'] != regression_data['low_pre1']
            and regression_data['week2Low'] != regression_data['low_pre2']
            #and (0 < regression_data['PCT_day_change'] < 1) and (0 < regression_data['PCT_change'] < 1)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None)
        elif(regression_data['week2LowChange'] > 1):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellDowningMA-(check5MinuteDownTrendAndSellDowntrend)')
        elif(is_algo_sell(regression_data)):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellDowningMA-(check5MinuteDownTrendAndSellDowntrend)-Already10DayDown')
    
    if((0 < regression_data['PCT_day_change'] < 0.75) and (0 < regression_data['PCT_change'] < 0.75)
        and (regression_data['SMA4_2daysBack'] < 0 or regression_data['SMA9_2daysBack'] < 0)
        and regression_data['SMA4'] > 0
        and regression_data['PCT_day_change_pre1'] > 0.5
        and regression_data['PCT_day_change_pre2'] > 0.5
        and (regression_data['PCT_day_change_pre1'] > 1.5 or regression_data['PCT_day_change_pre2'] > 1.5)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellSMA4Reversal')
        
    if((2 < regression_data['PCT_day_change']) and (1.5 < regression_data['PCT_change'])
        and regression_data['bar_high'] > regression_data['bar_high_pre1']
        ):
        if(regression_data['year2HighChange'] < -40
            and regression_data['yearHighChange'] < -20
            and regression_data['PCT_day_change_pre1'] < 0
            and ((regression_data['bar_low_pre1'] < regression_data['bar_low_pre2'])
                or regression_data['low_pre1'] < regression_data['low_pre2']
                )
            and regression_data['SMA25'] < 0
            and regression_data['SMA50'] < 0
            and regression_data['SMA100'] < 0
            ):
            if(regression_data['high_pre1'] < regression_data['high_pre2'] < regression_data['high_pre3'] < regression_data['high_pre4']): 
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellYear2LowLT-40-last4DayDown(triggerAfter-9:15)')
            elif(regression_data['high_pre1'] < regression_data['high_pre2'] < regression_data['high_pre3']): 
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellYear2LowLT-40-last3DayDown(triggerAfter-9:15)')
                
    if((-2 < regression_data['PCT_day_change'] < -0.5) and (4 < regression_data['PCT_change'] < 10)
        and high_tail_pct(regression_data) > 1
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellLastDayHighUpReversal')
        
    if((('NA$(shortDownTrend-Risky)' in regression_data['series_trend']) 
            or ('NA$(shortDownTrend)' in regression_data['series_trend']) 
            or
            (regression_data['PCT_day_change_pre1'] < -3
             and regression_data['PCT_day_change_pre2'] < -2
             and regression_data['PCT_day_change_pre3'] < -2
            )
        ) 
        and (regression_data['PCT_day_change'] > 2.5 and regression_data['PCT_change'] > 2)
        and abs_month3High_less_than_month3Low(regression_data)
        and regression_data['high'] < regression_data['high_pre2']  
        ):
        if(regression_data['PCT_day_change'] > 4 and regression_data['PCT_change'] > 4):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSelldowntrendReversalMayFail')
            flag = True
    
    if(regression_data['PCT_day_change'] < 0 and regression_data['PCT_day_change_pre1'] > 1 and regression_data['PCT_day_change_pre2'] > 1
        and (regression_data['forecast_day_PCT4_change'] > 5
            or regression_data['forecast_day_PCT7_change'] > 5
            or regression_data['forecast_day_PCT10_change'] > 5
            )
        and regression_data['monthHighChange'] < -5
        and regression_data['monthLowChange'] > 5
        ):
        if(regression_data['forecast_day_PCT3_change'] < 0 and regression_data['forecast_day_PCT4_change'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuy-smallUptrendContinue')
        elif((regression_data['forecast_day_PCT4_change'] > 0 or regression_data['forecast_day_PCT5_change'] > 0)
            and regression_data['PCT_day_change'] < -1
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSell-smallUptrendReversal')
    
    if(('NA$(shortDownTrend-MayReversal' in regression_data['series_trend']
        #or 'shortDownTrend' in regression_data['series_trend']
        #or 'trendDown' in regression_data['series_trend']
        ) 
        and regression_data['PCT_day_change'] < 0
        and regression_data['PCT_change'] < 0
        and regression_data['PCT_day_change_pre1'] > 2.5
        and (regression_data['low'] > regression_data['low_pre1'] 
             or ( regression_data['PCT_day_change'] > -3
                  and regression_data['PCT_change'] > -3
                )
            )
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisMaySellshortDownTrendContinue')
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
                add_in_csv(regression_data, regressionResult, ws, None, None, 'maySellHighVolatileDownContinueLT-8')
                flag = True
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, 'maySellAfter10:30HighVolatileDownContinueLT-8-Risky')
                flag = True
    
    if(regression_data['forecast_day_PCT2_change'] > 0
        and regression_data['forecast_day_PCT3_change'] > 0
        and (regression_data['forecast_day_PCT5_change'] > 0 and regression_data['forecast_day_PCT7_change'] > 0 and regression_data['forecast_day_PCT10_change'] > 0
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
        add_in_csv(regression_data, regressionResult, ws, None, None, '(GLOBAL-DOWN)maySellAfter10:20HighVolatileLastDayUp-GT10')
        flag = True
    elif(regression_data['high'] > regression_data['high_pre1']
        and regression_data['high'] > regression_data['high_pre2']
        and (regression_data['PCT_day_change'] > 15 and regression_data['PCT_change'] > 10
            or regression_data['forecast_day_PCT2_change'] > 20)
        and regression_data['close'] > 50
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '(GLOBAL-DOWN)maySellAfter10:20HighVolatileLastDayUp-GT10')
        flag = True
    elif(
        regression_data['forecast_day_PCT7_change'] < 0
        and regression_data['forecast_day_PCT10_change'] < 0
        and 8 < regression_data['PCT_day_change'] < 20 and 8 < regression_data['PCT_change'] < 20
        ):
        if(8 < regression_data['PCT_day_change'] < 14 and 8 < regression_data['PCT_change'] < 14):
            add_in_csv(regression_data, regressionResult, ws, None, None, '(GLOBAL-UP)mayBuyContinueHighVolatileLastDayUp-GT8')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, '(GLOBAL-UP)RiskyMayBuyContinueHighVolatileLastDayUp-GT8')
        flag = True

def sell_check_cup_filter(regression_data, regressionResult, reg, ws):
    if(2 < regression_data['PCT_day_change'] < 5.5
        and -1 < regression_data['PCT_change'] < 5.5
        and regression_data['PCT_day_change_pre1'] < -2
        
        and (regression_data['PCT_day_change_pre2'] < 0
            or regression_data['PCT_day_change_pre3'] < 0
            )
        #and (regression_data['forecast_day_PCT5_change'] < 2)
        and (regression_data['forecast_day_PCT7_change'] > 0
            and regression_data['forecast_day_PCT10_change'] > 0
            )
        and regression_data['forecast_day_PCT2_change'] < 0
        and regression_data['weekHighChange'] < -3
        ):
        if(regression_data['week2LowChange'] > 5
            and abs_week2High_less_than_week2Low(regression_data)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupDown-lastDayUp')  
        elif(regression_data['week2HighChange'] > -0.5):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupDown-lastDayUp-near2WeekHigh-mayReveresalSell')
    elif(-5 < regression_data['PCT_day_change'] < -2
        and -5.5 < regression_data['PCT_change'] < -1.5
        and (regression_data['forecast_day_PCT10_change'] > -1)
        and (regression_data['forecast_day_PCT7_change'] > 0
            or regression_data['forecast_day_PCT10_change'] > 0
            )
        and (regression_data['forecast_day_PCT_change'] < 0
            or regression_data['forecast_day_PCT2_change'] < 0
            or regression_data['forecast_day_PCT3_change'] < 0
            )
        and (((regression_data['high'] - regression_data['high_pre1'])/regression_data['high_pre1'])*100) < 0
        and regression_data['weekHighChange'] < -3
        ):
        if(regression_data['week2LowChange'] < 0.5):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupDown-near2WeekDown-mayReveresalBuy')
        elif(regression_data['PCT_day_change_pre1'] < -2
            and regression_data['PCT_day_change_pre2'] < -2
            and regression_data['forecast_day_PCT5_change'] < 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupDown-3dayDown-mayReversalBuy')
        elif(regression_data['PCT_day_change'] < -2
            and regression_data['PCT_day_change_pre1'] < -1
            and regression_data['PCT_day_change_pre2'] > 0
            and regression_data['PCT_day_change_pre3'] < -1
            and regression_data['forecast_day_PCT5_change'] < 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%checkCupDown-2dayDown-continue')
        elif(regression_data['PCT_day_change'] < -2
            and regression_data['PCT_day_change_pre1'] < -2
            and regression_data['forecast_day_PCT5_change'] < 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupDown-2dayDown-mayReversalBuy')
        elif(-3 < regression_data['PCT_day_change'] < -2
            and regression_data['week2LowChange'] > 2
            ):
            if(-2 < regression_data['PCT_day_change_pre1'] < -0.5
                and regression_data['PCT_day_change_pre2'] < -0.5
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupDown-3dayDown')
            elif(-2 < regression_data['PCT_day_change_pre1'] < -0.5
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupDown-2dayDown')
            elif(regression_data['forecast_day_PCT7_change'] > -1
                and regression_data['PCT_day_change_pre1'] > 0 
                and regression_data['PCT_day_change_pre2'] > 0
                and regression_data['PCT_day_change_pre3'] > 0
                and regression_data['forecast_day_PCT_change'] < 0
                and regression_data['forecast_day_PCT2_change'] < 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupDown-upTrendLastDayDown-mayReversalBuy') 
            elif(regression_data['forecast_day_PCT7_change'] > -1
                and (regression_data['PCT_day_change_pre2'] > 0 
                    or regression_data['bar_low'] < regression_data['bar_low_pre1']
                    )
                and abs_month3High_more_than_month3Low(regression_data)
                ):
                if(regression_data['bar_low'] < regression_data['bar_low_pre1']):
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'bar_low')
                if(regression_data['forecast_day_PCT2_change'] < -1
                    and regression_data['forecast_day_PCT3_change'] < -1
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupDown')
                else:
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupDown-inDownTrend')
            elif(regression_data['forecast_day_PCT7_change'] > -1
                and (regression_data['PCT_day_change_pre2'] > 0 
                    or regression_data['bar_low'] < regression_data['bar_low_pre1']
                    )
                ):
                if(regression_data['bar_low'] < regression_data['bar_low_pre1']):
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'bar_low')
                if(regression_data['forecast_day_PCT2_change'] < -1
                    and regression_data['forecast_day_PCT3_change'] < -1
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupDown-month3HighLTmonth3Low')
                else:
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupDown-inDownTrend-month3HighLTmonth3Low')
            elif(regression_data['forecast_day_PCT7_change'] > -1
                and regression_data['PCT_day_change_pre1'] > 0 
                and regression_data['PCT_day_change_pre2'] < 0
                and regression_data['bar_low'] > regression_data['bar_low_pre1']
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupDown-mayReversalBuy')

def sell_consolidation_breakdown(regression_data, regressionResult, reg, ws):
    week2BarLowChange = ((regression_data['bar_low'] - regression_data['week2BarLow'])/regression_data['bar_low'])*100
    if(-6 < regression_data['PCT_day_change'] < -2
        and -6 < regression_data['PCT_change']
        and (regression_data['PCT_day_change_pre1'] > -2 
             or regression_data['PCT_day_change_pre1'] > regression_data['PCT_day_change']
             )
        and (regression_data['PCT_day_change_pre1'] > 0 
             or regression_data['PCT_day_change_pre2'] > 0
             or regression_data['PCT_day_change_pre3'] > 0
            )
        #and regression_data['low'] < regression_data['high_pre3']
        and regression_data['low'] < regression_data['high_pre2']
        and regression_data['low'] < regression_data['high_pre1']
        and -3 < regression_data['forecast_day_PCT4_change'] < -0.5
        and -4 < regression_data['forecast_day_PCT3_change'] < 0
        and -4 < regression_data['forecast_day_PCT2_change'] < 0
        and -3 < regression_data['forecast_day_PCT_change'] < 0
        and -3 <= regression_data['forecast_day_PCT10_change'] <= 0
        and regression_data['bar_low'] <= regression_data['week2BarLow']
        ):
        if(regression_data['weekBarLow'] < regression_data['bar_low_pre1'] 
            and regression_data['week2BarLow'] < regression_data['bar_low_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'brokenToday')
        if(regression_data['weekLow'] < regression_data['week2Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'weekLowLTweek2Low')
        if(week2BarLowChange < -5):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'week2BarLowChangeLT-5')
        elif(week2BarLowChange < -4):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'week2BarLowChangeLT-4')
        elif(week2BarLowChange < -3):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'week2BarLowChangeLT-3')
        elif(week2BarLowChange < -2):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'week2BarLowChangeLT-2')
        elif(week2BarLowChange < -1):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'week2BarLowChangeLT-1')
        elif(week2BarLowChange < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'week2BarLowChangeLT0')
        if(regression_data['PCT_day_change'] < -2
            and regression_data['year2LowChange'] > 5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkSellConsolidationBreakDown-2week')
        elif(regression_data['PCT_day_change'] > -2
            and regression_data['year2LowChange'] > 5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellConsolidationBreakDown-2week-(risky)-PCTDayChangeGT-1')
        elif(regression_data['year2LowChange'] <= 5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellSellConsolidationBreakDown-2week-(risky)-year2Low')
    elif(-6 < regression_data['PCT_day_change'] < -2
        and -6 < regression_data['PCT_change']
        and (regression_data['PCT_day_change_pre1'] > 0 or regression_data['PCT_day_change_pre2'] > 0)
        #and regression_data['low'] < regression_data['high_pre3']
        and regression_data['low'] < regression_data['high_pre2']
        and regression_data['low'] < regression_data['high_pre1']
        and -3 < regression_data['forecast_day_PCT4_change'] < -0.5
        and -4 < regression_data['forecast_day_PCT3_change'] < 0
        and -4 < regression_data['forecast_day_PCT2_change'] < 0
        and -3 < regression_data['forecast_day_PCT_change'] < 0
        and ((abs_monthHigh_more_than_monthLow(regression_data))
            )
        and regression_data['SMA4'] < regression_data['SMA4_2daysBack']
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'checkSellConsolidationBreakDown-month3HighGTMonth3Low')
    elif(-6 < regression_data['PCT_day_change'] < -2
        and -6 < regression_data['PCT_change']
        and (regression_data['PCT_day_change_pre1'] > 0 or regression_data['PCT_day_change_pre2'] > 0)
        #and regression_data['low'] < regression_data['high_pre3']
        and regression_data['low'] < regression_data['high_pre2']
        and regression_data['low'] < regression_data['high_pre1']
        and -3 < regression_data['forecast_day_PCT4_change'] < -0.5
        and -4 < regression_data['forecast_day_PCT3_change'] < 0
        and -4 < regression_data['forecast_day_PCT2_change'] < 0
        and -3 < regression_data['forecast_day_PCT_change'] < 0
        and ((-4 < regression_data['forecast_day_PCT5_change'] < 0
                and -4 < regression_data['forecast_day_PCT7_change'] < 0
               )
            )
        and regression_data['SMA4'] < regression_data['SMA4_2daysBack']
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellConsolidationBreakDown-forecastDayPCT7LT0')
        
        
    if(regression_data['low'] > regression_data['low_pre1']
        and regression_data['low'] > regression_data['low_pre2']
        and regression_data['low'] > regression_data['low_pre3']
        and regression_data['low'] > regression_data['low_pre4']
        ):
        if(regression_data['forecast_day_PCT_change'] < 0
            and -7 < regression_data['PCT_day_change'] < -2.5
            and regression_data['bar_low'] < regression_data['bar_low_pre1']
            and regression_data['bar_low'] < regression_data['bar_low_pre2']
            and 0 < regression_data['PCT_day_change_pre1'] < 1.5
            and 0 < regression_data['PCT_day_change_pre2'] < 1.5
            and 0 < regression_data['PCT_day_change_pre3'] < 1.5
            and 0 < regression_data['PCT_day_change_pre4'] < 1.5 
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkSellConsolidationBreakdown-allPreGT0')
        elif(regression_data['forecast_day_PCT_change'] < 0
            and -7 < regression_data['PCT_day_change'] < -2.5
            and regression_data['bar_low'] < regression_data['bar_low_pre1']
            and regression_data['bar_low'] < regression_data['bar_low_pre2']
            and -1.5 < regression_data['PCT_day_change_pre1'] < 1.5
            and -1.5 < regression_data['PCT_day_change_pre2'] < 1.5
            and -1.5 < regression_data['PCT_day_change_pre3'] < 1.5
            and -1.5 < regression_data['PCT_day_change_pre4'] < 1.5 
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkSellConsolidationBreakdown')

def sell_supertrend(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    
    flag = False
    if(regression_data['close'] > 50
        and regression_data['forecast_day_PCT7_change'] < 0
        and regression_data['forecast_day_PCT10_change'] < 0
        and low_tail_pct(regression_data) < 3.5 
        ):
        if(-0.75 < regression_data['PCT_day_change'] < 0.75
            and -0.75 < regression_data['PCT_day_change_pre1'] < 0.75
            and -0.75 < regression_data['PCT_day_change_pre2'] < 0.75
            and -10 < regression_data['PCT_day_change_pre3'] < -3
            and regression_data['forecast_day_PCT7_change'] < -10
            and regression_data['forecast_day_PCT10_change'] < -10
            and 0 > regression_data['forecast_day_PCT_change']
            and 0 > regression_data['forecast_day_PCT2_change']
            and 0 > regression_data['forecast_day_PCT3_change']
            and 0 > regression_data['forecast_day_PCT4_change']
            and regression_data['low'] > regression_data['low_pre1'] 
            and regression_data['low'] > regression_data['low_pre2'] 
            and regression_data['low'] > regression_data['low_pre3']
            and regression_data['yearHighChange'] < -15
            and regression_data['yearLowChange'] > 5
            and regression_data['month3HighChange'] < -10
            #and regression_data['low'] > regression_data['low_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkSell:Super1') 
            flag = True
        elif(0 < regression_data['PCT_day_change'] < 2 and (abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change']))
            and (-5 < regression_data['PCT_day_change_pre1'] < -2 and -5 < regression_data['PCT_day_change_pre2'] < -2)
            and 0 > regression_data['forecast_day_PCT_change'] > regression_data['forecast_day_PCT2_change'] > regression_data['forecast_day_PCT3_change']
            and regression_data['low_pre2'] > regression_data['low_pre1'] > regression_data['low'] 
            and regression_data['forecast_day_PCT7_change'] > -15
            and regression_data['forecast_day_PCT10_change'] > -15
            and (regression_data['month3HighChange'] > 10
                 or regression_data['month6HighChange'] > 10
                 or regression_data['yearHighChange'] > 10
                 or regression_data['year2HighChange'] > 10
                 )
            and regression_data['yearHighChange'] < -10
            and regression_data['yearLowChange'] > 5 
            ):
            if(low_tail_pct(regression_data) < 3.5 
                and high_tail_pct(regression_data) < 2.5
                and regression_data['forecast_day_PCT7_change'] > -13
                and regression_data['forecast_day_PCT10_change'] > -13
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkSell:Super3')
                flag = True
            elif(high_tail_pct(regression_data) > 2.5
                and low_tail_pct(regression_data) > 1.5
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'buyReversal-sellSuper3')
                flag = True
        elif(0 < regression_data['PCT_day_change'] < 2 and (abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change']))
            and (-7 < regression_data['PCT_day_change_pre1'] < -2 and -10 < regression_data['PCT_day_change_pre2'] < -2)
            and (abs(regression_data['PCT_day_change_pre2']) > abs(regression_data['PCT_day_change_pre1']))
            #and 0 > regression_data['forecast_day_PCT_change'] > regression_data['forecast_day_PCT2_change'] > regression_data['forecast_day_PCT3_change']
            #and regression_data['forecast_day_PCT7_change'] > -30
            #and regression_data['forecast_day_PCT10_change'] > -30
            and (regression_data['month3HighChange'] > 10
                 or regression_data['month6HighChange'] > 10
                 or regression_data['yearHighChange'] > 10
                 or regression_data['year2HighChange'] > 10
                 )
            and regression_data['yearHighChange'] < -10
            and regression_data['yearLowChange'] > 5
            #and low_tail_pct_pre1(regression_data) < 2.5
            ):
            if(low_tail_pct(regression_data) < 3.5 
                and high_tail_pct(regression_data) < 2.5
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkSell:Super4')
                flag = True
            elif(high_tail_pct(regression_data) > 2.5
                and low_tail_pct(regression_data) > 1.5
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'buyReversal-sellSuper4')
                flag = True
        
        if(-5 < regression_data['PCT_day_change_pre1'] < 0.75
            and -0.5 < regression_data['PCT_day_change'] < 0.75
            and (regression_data['PCT_day_change'] < 0 or regression_data['PCT_day_change_pre1'] < 0)
            and 0 > regression_data['forecast_day_PCT2_change'] > regression_data['forecast_day_PCT3_change'] > regression_data['forecast_day_PCT4_change']
            and regression_data['low_pre3'] > regression_data['low_pre2'] > regression_data['low_pre1'] 
            and (regression_data['forecast_day_PCT4_change'] < -5
                or regression_data['forecast_day_PCT5_change'] < -5
                )
            and (regression_data['forecast_day_PCT10_change'] > regression_data['forecast_day_PCT5_change']
                or regression_data['forecast_day_PCT10_change'] > regression_data['forecast_day_PCT7_change']
                )
            and (regression_data['PCT_day_change_pre1'] < -3 
                or regression_data['PCT_day_change_pre2'] < -3 
                or regression_data['PCT_day_change_pre3'] < -3
                )
            and (regression_data['PCT_day_change_pre1'] < -3 
                or regression_data['PCT_day_change_pre2'] < -3 
                or (regression_data['PCT_day_change_pre1'] < 0 and regression_data['PCT_day_change_pre2'] < 0)
                )
            and regression_data['yearHighChange'] < -15
            and regression_data['yearLowChange'] > 5
            and regression_data['month3HighChange'] < -10
            #and regression_data['high'] < regression_data['high_pre1']
            ):
            if(regression_data['PCT_day_change_pre1'] < 0
                and -0.75 < regression_data['PCT_day_change'] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, '--')
            elif(regression_data['PCT_day_change_pre1'] > 0
                and 0 < regression_data['PCT_day_change'] < 0.75):
                add_in_csv(regression_data, regressionResult, ws, None, None, '++')
            elif(regression_data['PCT_day_change_pre1'] < 0
                and 0 < regression_data['PCT_day_change'] < 0.75):
                add_in_csv(regression_data, regressionResult, ws, None, None, '-+')
            elif(regression_data['PCT_day_change_pre1'] > 0
                and -0.75 < regression_data['PCT_day_change'] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, '+-')
            if(-0.75 < regression_data['PCT_day_change_pre1']):
                add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkSell:Super-Risky')
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellSuper-Risky')
            flag = True
        elif(-5 < regression_data['PCT_day_change_pre1'] < -1.5 and (abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change']))
            and (regression_data['PCT_day_change_pre2'] < -1.5 or regression_data['PCT_day_change_pre3'] < -1.5)
            and 0 < regression_data['PCT_day_change'] < 1.5
            and (regression_data['PCT_day_change'] < 0 or regression_data['PCT_day_change_pre1'] < 0)
            and 0 > regression_data['forecast_day_PCT2_change'] > regression_data['forecast_day_PCT3_change'] > regression_data['forecast_day_PCT4_change']
            and regression_data['low_pre3'] > regression_data['low_pre2'] > regression_data['low_pre1'] 
            and regression_data['forecast_day_PCT5_change'] < -5
            and (regression_data['forecast_day_PCT7_change'] > -15 or regression_data['forecast_day_PCT10_change'] > -15)
            and (regression_data['forecast_day_PCT7_change'] > -20 and regression_data['forecast_day_PCT10_change'] > -20)
            and regression_data['yearHighChange'] < -10
            and regression_data['yearLowChange'] > 10
            #and regression_data['month3HighChange'] < -10
            #and low_tail_pct(regression_data) < 2.5
            ):
            if(regression_data['PCT_day_change_pre1'] < 0
                and -0.75 < regression_data['PCT_day_change'] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, '--')
            elif(regression_data['PCT_day_change_pre1'] > 0
                and 0 < regression_data['PCT_day_change'] < 0.75):
                add_in_csv(regression_data, regressionResult, ws, None, None, '++')
            elif(regression_data['PCT_day_change_pre1'] < 0
                and 0 < regression_data['PCT_day_change'] < 0.75):
                add_in_csv(regression_data, regressionResult, ws, None, None, '-+')
            elif(regression_data['PCT_day_change_pre1'] > 0
                and -0.75 < regression_data['PCT_day_change'] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, '+-')
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkSell:Super2')
            flag = True
        
    if(abs_monthHigh_more_than_monthLow(regression_data)
        and regression_data['week2HighChange'] != regression_data['weekHighChange']
        and regression_data['week2LowChange'] == regression_data['weekLowChange']
        and regression_data['weekHighChange'] < -2
        and regression_data['weekLowChange'] > 2
        and (regression_data['forecast_day_PCT2_change'] > -0.5
            or regression_data['forecast_day_PCT3_change'] > -0.5
            or regression_data['forecast_day_PCT4_change'] > -0.5
            )
        ):
        if (0 < regression_data['PCT_day_change'] < 0.75
            and(regression_data['PCT_day_change_pre1'] < -2
                or regression_data['PCT_day_change_pre2'] < -2
                or regression_data['PCT_day_change_pre3'] < -2
                or regression_data['PCT_day_change_pre4'] < -2
                or regression_data['PCT_day_change_pre5'] < -2
               )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkSell:FlagWeek-doji')
            flag = True
        elif(regression_data['PCT_day_change'] < -2 and regression_data['PCT_day_change'] < 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkSell:FlagWeek')
            flag = True
    elif(abs_month3High_more_than_month3Low(regression_data)
        and regression_data['monthHighChange'] != regression_data['week2HighChange']
        and regression_data['monthLowChange'] == regression_data['week2LowChange']
        and regression_data['weekHighChange'] < -2
        and regression_data['weekLowChange'] > 2
        and (regression_data['forecast_day_PCT2_change'] > 0
            or regression_data['forecast_day_PCT3_change'] > 0
            or regression_data['forecast_day_PCT4_change'] > 0
            or regression_data['forecast_day_PCT5_change'] > 0
            )
        ):
        if (0 < regression_data['PCT_day_change'] < 0.75
            and regression_data['PCT_day_change_pre1'] > regression_data['PCT_day_change']
            and regression_data['PCT_day_change_pre2'] > 0
            and (regression_data['high'] > regression_data['high_pre1']
                 or regression_data['PCT_day_change_pre1'] > 1
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkSell:Flag2Week-doji')
            flag = True 
        elif(-4 < regression_data['PCT_day_change'] < -2 and regression_data['PCT_change'] < 0
            and regression_data['PCT_day_change_pre1'] < 1.5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkSell:Flag2Week')
            flag = True 
    elif(regression_data['week2HighChange'] != regression_data['weekHighChange']
        and regression_data['week2LowChange'] <= regression_data['weekLowChange']
        and regression_data['weekHighChange'] < -1
        and regression_data['weekLowChange'] > 1
        and (regression_data['forecast_day_PCT2_change'] > -0.5
            or regression_data['forecast_day_PCT3_change'] > -0.5
            or regression_data['forecast_day_PCT4_change'] > -0.5
            )
        ):
        if(0 < regression_data['PCT_day_change'] < 0.75
            and regression_data['PCT_day_change_pre1'] > regression_data['PCT_day_change']
            and regression_data['PCT_day_change_pre2'] > 0
            and (regression_data['high'] > regression_data['high_pre1']
                 or regression_data['PCT_day_change_pre1'] > 1
                )
            and(regression_data['PCT_day_change_pre3'] < -2
                or regression_data['PCT_day_change_pre4'] < -2
                or regression_data['PCT_day_change_pre5'] < -2
               )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellFlagWeek-doji-Risky')
            flag = True
        elif(-4 < regression_data['PCT_day_change'] < -2 and regression_data['PCT_change'] < 0
            and regression_data['PCT_day_change_pre1'] < 1.5
            and regression_data['weekHighChange'] < -2
            and regression_data['week2LowChange'] > 2
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellFlagWeek-Risky')
            flag = True
    elif(regression_data['monthHighChange'] != regression_data['week2HighChange']
        and regression_data['monthLowChange'] <= regression_data['week2LowChange']
        and regression_data['week2HighChange'] < -1
        and regression_data['week2LowChange'] > 1
        and (regression_data['forecast_day_PCT2_change'] > 0
            or regression_data['forecast_day_PCT3_change'] > 0
            or regression_data['forecast_day_PCT4_change'] > 0
            or regression_data['forecast_day_PCT5_change'] > 0
            )
        ):
        if(0 < regression_data['PCT_day_change'] < 0.75
            and regression_data['PCT_day_change_pre1'] > regression_data['PCT_day_change']
            and regression_data['PCT_day_change_pre2'] > 0
            and (regression_data['high'] > regression_data['high_pre1']
                 or regression_data['PCT_day_change_pre1'] > 1
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellFlag2Week-doji-Risky')  
            flag = True
        elif(-4 < regression_data['PCT_day_change'] < -2 and regression_data['PCT_change'] < 0
            and regression_data['PCT_day_change_pre1'] < 1.5
            and regression_data['PCT_day_change_pre1'] > regression_data['PCT_day_change']
            and regression_data['PCT_day_change_pre2'] > regression_data['PCT_day_change']
            and regression_data['weekHighChange'] < -2
            and regression_data['week2LowChange'] > 2
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellFlag2Week-Risky')  
            flag = True
    
    if(regression_data['week2HighChange'] == regression_data['weekHighChange']
        and regression_data['week2LowChange'] == regression_data['weekLowChange']
        and regression_data['weekHighChange'] < -2
        and regression_data['weekLowChange'] > 2
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None)
    elif(regression_data['monthHighChange'] == regression_data['week2HighChange']
        and regression_data['monthLowChange'] == regression_data['week2LowChange']
        and regression_data['week2HighChange'] < -4
        and regression_data['week2LowChange'] > 4
        ):
        if(0 < regression_data['PCT_day_change'] < 0.75
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkSell:FlagMonth-doji')
            flag = True
        elif(regression_data['PCT_day_change'] < -3):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkSell:FlagMonth')
            flag = True 
            
    if('checkSellConsolidationBreakDown-2week' in regression_data['filter']
        and -5 < regression_data['PCT_day_change'] < -1.5
        and -5 < regression_data['PCT_change'] < -1.5
        and (regression_data['PCT_day_change_pre1'] > regression_data['PCT_day_change']/2
             #or 'MLSell' in regression_data['filter']
             #or 'brokenToday' in regression_data['filter']
            )
        and (regression_data['PCT_day_change'] < -2
             #or 'MLSell' in regression_data['filter']
             or 'brokenToday' in regression_data['filter']
            )
        and (regression_data['month3LowChange'] > 5 or abs_month3High_less_than_month3Low(regression_data))
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkSell:ConsolidationBreakDown(NotShapeA)-2week')
        flag = True
    elif('checkSellConsolidationBreakDown-2week' in regression_data['filter']
        and -5 < regression_data['PCT_day_change'] < -2
        and -5 < regression_data['PCT_change'] < -2
        and regression_data['PCT_day_change_pre1'] > -1.5 and regression_data['PCT_change_pre1'] > -1.5
        and 'brokenToday' in regression_data['filter']
        and 'MLSell' in regression_data['filter']
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'RiskycheckSellConsolidationBreakDown(NotShapeA)-2week')
        flag = True
        
    if(-2.5 < regression_data['PCT_day_change'] < 2.5
        and -3.5 < regression_data['PCT_change'] < 3.5
        and regression_data['PCT_day_change_pre1'] < -1
        and abs(regression_data['PCT_day_change_pre1']) > 2*(abs(regression_data['PCT_day_change']))
        and (regression_data['forecast_day_PCT5_change'] > 0
            and regression_data['forecast_day_PCT7_change'] > 0
            )
        and (regression_data['forecast_day_PCT2_change'] < 0 or regression_data['forecast_day_PCT_change'] < 0)
        and regression_data['week2LowChange'] > 5
        and abs_week2High_less_than_week2Low(regression_data)
        ):
        if(regression_data['weekHighChange'] < -3
            and (regression_data['PCT_day_change_pre1'] < -2 or regression_data['PCT_day_change_pre2'] < -2)
            ):
            if(regression_data['PCT_day_change_pre1'] < -2 
                and regression_data['PCT_day_change'] > 0
                ):
                if(regression_data['PCT_day_change_pre2'] < 0 or regression_data['PCT_day_change_pre3'] < 0):
                    add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkSell:CupDownDoji')
                    flag = True
            elif(regression_data['PCT_day_change_pre1'] < -2 
                and -.75 < regression_data['PCT_day_change'] < 0.75
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkSell:CupDownDoji-lastDayLT(-2)TodayDoji')
                flag = True
            elif(regression_data['PCT_day_change_pre2'] < 0 
                or regression_data['PCT_day_change'] > 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkSell:CupDownDoji-last2lastDayLT0orTodayGT0')
                flag = True
            elif(regression_data['weekHighChange'] < -3
                and -2 < regression_data['PCT_day_change_pre1'] < -1 and -2.5 < regression_data['PCT_day_change_pre2'] < -1
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkBuyContinue:CupDownDoji-last2dayUp')
                flag = True
        elif(regression_data['weekHighChange'] > -2.5
            and abs(regression_data['PCT_day_change']) < 1
            and regression_data['week2HighChange'] == regression_data['weekHighChange']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkBuyContinue:CupDownDoji')
            flag = True
        elif(-2 < regression_data['PCT_day_change_pre1'] < -1 and -2 < regression_data['PCT_day_change_pre2'] < -1):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkBuyContinue:CupDownDoji-last2dayUp')
            flag = True
            
    if( -7.5 < regression_data['PCT_day_change_pre1'] < -4.5 and -10 < regression_data['PCT_change_pre1'] < -3
        and (regression_data['PCT_day_change'] > 0 and regression_data['PCT_change'] > 0)  
        and (regression_data['PCT_day_change_pre2'] > 0 or regression_data['PCT_day_change_pre3'] > 0)
        and (regression_data['PCT_day_change_pre3'] > 0 or regression_data['PCT_day_change_pre4'] > 0)
        and (regression_data['PCT_day_change_pre2'] > -3 and regression_data['PCT_day_change_pre3'] > -3)
        and regression_data['forecast_day_PCT3_change'] < 0
        and regression_data['forecast_day_PCT4_change'] < 0
        and regression_data['low'] < regression_data['low_pre1']
        and regression_data['high'] < regression_data['high_pre1']
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkSell:lastDayLT-(-4.5)') 
            
    return flag



def sell_market_downtrend(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    #return False
    if(('P@' not in regression_data['buyIndia'])
        and ((-6 < regression_data['PCT_change'] < -2) 
            and (-6 < regression_data['PCT_day_change'] < -2)
            and regression_data['close'] < regression_data['bar_low_pre1']
            )
        #and regression_data['trend'] == 'down'
        ):
        if(regression_data['trend'] == 'down'):
            if(('ReversalHighYear2' in regression_data['filter3'])):
                add_in_csv(regression_data, regressionResult, ws, None, None, "##DOWNTREND:sellYear2HighReversal(InDownTrend)")
                return True
            if(('ReversalHighYear' in regression_data['filter3'])):
                add_in_csv(regression_data, regressionResult, ws, None, None, '##DOWNTREND:sellYearHighReversal(InDownTrend)')
                return True
            if(('ReversalHighMonth6' in regression_data['filter3'])):
                add_in_csv(regression_data, regressionResult, ws, None, None, '##DOWNTREND:sellMonth6HighReversal(InDownTrend)')
                return True
            if(('ReversalHighMonth3' in regression_data['filter3'])):
                add_in_csv(regression_data, regressionResult, ws, None, None, '##DOWNTREND:sellMonth3HighReversal(InDownTrend)')
                return True
            if(regression_data['month3LowChange'] > 15 and (regression_data['month6LowChange'] > 20 or regression_data['yearLowChange'] > 30)
                ):
                if(('NearHighYear2' in regression_data['filter3'])):
                    add_in_csv(regression_data, regressionResult, ws, None, None, None)
                if(('NearHighYear' in regression_data['filter3'])):
                    add_in_csv(regression_data, regressionResult, ws, None, None, '##DOWNTREND:sellYearHigh(InDownTrend)')
                    return True
                if(('NearHighMonth6' in regression_data['filter3'])):
                    add_in_csv(regression_data, regressionResult, ws, None, None, '##DOWNTREND:sellMonth6High(InDownTrend)')
                    return True
                if(('NearHighMonth3' in regression_data['filter3'])):
                    add_in_csv(regression_data, regressionResult, ws, None, None, '##DOWNTREND:sellMonth3High(InDownTrend)')
                    return True
        if(((regression_data['PCT_day_change'] < -2) or (regression_data['PCT_change'] < -2) or ('MaySellCheckChart' in regression_data['filter1']))):
            if('BreakLowYear' in regression_data['filter3']
                and regression_data['year2LowChange'] > 5
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '##DOWNTREND:sellYearLowBreak')
                return True
            if('BreakLowMonth6' in regression_data['filter3']
                and regression_data['yearLowChange'] > 5
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '##DOWNTREND:sellMonth6LowBreak')
                return True
            if('BreakLowMonth3' in regression_data['filter3']
                and regression_data['month6LowChange'] > 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '##DOWNTREND:sellMonth3LowBreak')
                return True

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
                 or ( ("upTrend" in regression_data['series_trend']) and (-4 < regression_data['PCT_change'] < -1) and (-4 < regression_data['PCT_day_change'] < 1)))
            and ('[') not in regression_data['buyIndia']
            and regression_data['low'] < regression_data['low_pre1']
            and regression_data['bar_low'] < regression_data['bar_low_pre1']
            ):
            if('NearLowMonth3' in regression_data['filter3']):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'NearLowMonth3')
            elif('ReversalLowMonth3' in regression_data['filter3']):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'ReversalLowMonth3')
            elif('BreakLowMonth3' in regression_data['filter3']):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'BreakLowMonth3')
            add_in_csv(regression_data, regressionResult, ws, None, None, '##(Check-chart-sell)Month3Low-Continue(InUpTrend)')
            
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
            if('NearLowMonth3' in regression_data['filter3']):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'NearLowMonth3')
            elif('ReversalLowMonth3' in regression_data['filter3']):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'ReversalLowMonth3')
            elif('BreakLowMonth3' in regression_data['filter3']):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'BreakLowMonth3')
            add_in_csv(regression_data, regressionResult, ws, None, None, '##(Check-chart-sell):month3Low-InPlus')
            
    elif(('NearLowMonth6' in regression_data['filter3']) 
        or ('ReversalLowMonth6' in regression_data['filter3'])
        ):
        if(regression_data['month6LowChange'] < -20
            and ((1 < regression_data['PCT_change'] < 5) and (2 < regression_data['PCT_day_change'] < 5))
            and regression_data['close'] > regression_data['bar_high_pre1']
            and regression_data['close'] > regression_data['bar_high_pre2']
            ):
            if('NearLowMonth6' in regression_data['filter3']):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'NearLowMonth6')
            elif('ReversalLowMonth6' in regression_data['filter3']):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'ReversalLowMonth6')
            add_in_csv(regression_data, regressionResult, ws, None, None, '##(Check-chart-sell):month6Low-InPlus')
                
    elif(('NearLowYear' in regression_data['filter3']) 
        or ('ReversalLowYear' in regression_data['filter3'])
        ):
        if(regression_data['month6LowChange'] < -20
            and ((1 < regression_data['PCT_change'] < 5) and (2 < regression_data['PCT_day_change'] < 5))
            and regression_data['close'] > regression_data['bar_high_pre1']
            and regression_data['close'] > regression_data['bar_high_pre2']
            ):
            if('NearLowYear' in regression_data['filter3']):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'NearLowYear')
            elif('ReversalLowYear' in regression_data['filter3']):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'ReversalLowYear')
            add_in_csv(regression_data, regressionResult, ws, None, None, '##(Check-chart-sell):yearLow-InPlus')
                        
        if((('NearLowYear2' in regression_data['filter3']) 
            or ('ReversalLowYear2' in regression_data['filter3'])
            or ('BreakLowYear2' in regression_data['filter3'])
            )):    
            if(regression_data['year2HighChange'] < -50
                and regression_data['year2LowChange'] < 1
                and ((regression_data['PCT_change'] < -1) and (regression_data['PCT_day_change'] < -1))
                and regression_data['close'] < regression_data['bar_low_pre1']
                ):
                if(regression_data['PCT_change'] < -4
                    and ('BreakLowYear2' in regression_data['filter3'])
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, None, '##(Test)(Check-chart-buy):year2Low-InMinus')
                elif(regression_data['PCT_change'] < -2.5 and regression_data['PCT_day_change'] < -2.5
                    and ('NearLowYear2' in regression_data['filter3'])
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, None, '##(Test)(Check-chart-sell):year2Low-InMinus')
                else:
                    add_in_csv(regression_data, regressionResult, ws, None, None, '##(Test)(Check-chart):year2Low-InMinus')
        elif((('NearLowYear' in regression_data['filter3'])
            or ('ReversalLowYear' in regression_data['filter3'])
            or ('BreakLowYear' in regression_data['filter3'])
            )):
            if(regression_data['yearHighChange'] < -40
                and regression_data['yearLowChange'] < 1
                and ((regression_data['PCT_change'] < -1) and (regression_data['PCT_day_change'] < -1))
                and regression_data['close'] < regression_data['bar_low_pre1']
                ):
                if(regression_data['PCT_change'] < -4
                    and ('BreakLowYear' in regression_data['filter3'])
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, None, '##(Test)(Check-chart-buy):yearLow-InMinus')
                elif(regression_data['PCT_change'] < -2.5 and regression_data['PCT_day_change'] < -2.5
                    and ('NearLowYear' in regression_data['filter3'])
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, None, '##(Test)(Check-chart-sell):yearLow-InMinus')
                else:
                    add_in_csv(regression_data, regressionResult, ws, None, None, '##(Test)(Check-chart):yearLow-InMinus')

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
        add_in_csv(regression_data, regressionResult, ws, None, None, '##(Test)ML:AllMANegative-Downtrend')
        return True
    
def sell_study_downingMA(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    
    if(('(Confirmed)EMA6<EMA14' in regression_data['filter4'])
        and -3 > regression_data['PCT_day_change'] 
        and 0 > regression_data['PCT_change']
        and regression_data['PCT_day_change_pre1'] > 1
        and (regression_data['PCT_day_change'] < -3 or regression_data['PCT_change'] < -3)
        ):
        if(regression_data['month3HighChange'] > -10):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##(check-chart)buyEMA6<EMA14')
        elif(regression_data['PCT_day_change'] < -3.5 or regression_data['PCT_change'] < -3.5):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##(check-chart)buyEMA6<EMA14-Risky')
        
    if(regression_data['SMA9'] > 0 
        and regression_data['SMA4'] > 0
        and regression_data['forecast_day_PCT_change'] > 0.5
        and regression_data['forecast_day_PCT2_change'] > 0.5
        and regression_data['forecast_day_PCT5_change'] > 0.5
        and regression_data['forecast_day_PCT5_change'] < 5
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
            )
        )
        and low_tail_pct(regression_data) > 1
        and (high_tail_pct(regression_data) < 1.5)
        ):  
        add_in_csv(regression_data, regressionResult, ws, None, None, "##(Test)(check-chart)-buySMAUpTrend")
    elif((regression_data['SMA9'] > 0 or regression_data['SMA25'] > 0)
        and -0.5 < regression_data['weekLowChange'] < 0
        and regression_data['close'] > regression_data['low_week']
        and regression_data['forecast_day_PCT_change'] < 0
        and regression_data['forecast_day_PCT2_change'] < 0
        and (regression_data['forecast_day_PCT5_change'] > 0
            or regression_data['forecast_day_PCT7_change'] > 0
            ) 
        and regression_data['forecast_day_PCT10_change'] > 0
        and ((0 < regression_data['PCT_day_change'] < -1
            and regression_data['PCT_day_change_pre1'] < -1
            and (
                regression_data['PCT_day_change_pre2'] > 0
                or regression_data['PCT_day_change_pre3'] > 0
                )
            )
        )
        and low_tail_pct(regression_data) > 1 
        and (high_tail_pct(regression_data) < 1.5)
        ):  
        add_in_csv(regression_data, regressionResult, ws, None, None, "##(Test)(check-chart)-buySMAUpTrend-2DayDown-weekLowTouch")
    return True
