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

def buy_pattern_without_mlalgo(regression_data, regressionResult):
    if(regression_data['PCT_day_change'] < 3.5
        and regression_data['year2LowChange'] > 5):
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

def buy_high_volatility(regression_data, regressionResult):
    flag = False
    ws = None

    if('checkConsolidationBreakUp-2week' in regression_data['filter']
        and 1 < regression_data['PCT_day_change'] < 4
        and 1 < regression_data['PCT_change'] < 4
        and (regression_data['PCT_day_change_pre1'] < regression_data['PCT_day_change']/2
            #or 'MLBuy' in regression_data['filter']
            #or 'brokenToday' in regression_data['filter']
            )
        and (regression_data['PCT_day_change'] > 2 
            #or 'MLBuy' in regression_data['filter']
            or 'brokenToday' in regression_data['filter']
            )
        and (regression_data['month3HighChange'] < -5 or abs_month3High_more_than_month3Low(regression_data))
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'checkConsolidationBreakUp(NotShapeV)-2week')
        flag = True
    elif('checkConsolidationBreakUp-2week' in regression_data['filter']
        and 0 < regression_data['PCT_day_change'] < 5
        and 0 < regression_data['PCT_change'] < 5
        and regression_data['PCT_day_change_pre1'] < 1.5  and regression_data['PCT_change_pre1'] < 1.5
        and 'brokenToday' in regression_data['filter']
        and 'MLBuy' in regression_data['filter']
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'RISKY:checkConsolidationBreakUp(NotShapeV)-2week')
        flag = True
        
    if(regression_data['PCT_day_change'] > 0
        and regression_data['PCT_day_change_pre1'] > 0
        and regression_data['PCT_day_change_pre2'] > 0
        and regression_data['PCT_day_change_pre3'] > 0
        and 7 < regression_data['forecast_day_PCT5_change'] < 15
        and 7 < regression_data['forecast_day_PCT7_change'] < 15
        and 7 < regression_data['forecast_day_PCT10_change'] < 15
        and (regression_data['forecast_day_PCT5_change'] > 10
            or regression_data['forecast_day_PCT7_change'] > 10
            or regression_data['forecast_day_PCT10_change'] > 10
            )
        and regression_data['year2HighChange'] < -2
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'DOWNTRENDMARKET:sellStockHeavyUptrend')
        flag = True

    if((('(shortUpTrend)$NA' in regression_data['series_trend']) 
            or
            (regression_data['PCT_day_change'] > 0 
             and regression_data['PCT_day_change_pre1'] > 0
             and regression_data['PCT_day_change_pre2'] > 0
             and regression_data['PCT_day_change_pre3'] > 0
            )
        ) 
        and (regression_data['yearLowChange'] < 10
             or (regression_data['yearLowChange'] < 20
                 and abs_yearHigh_more_than_yearLow(regression_data)
                 and abs(regression_data['PCT_day_change']) < high_tail_pct(regression_data)
                 and low_tail_pct(regression_data) > 1
                )
            )
        and ((regression_data['PCT_day_change'] < 0 and regression_data['PCT_change'] < 0)
             or (regression_data['PCT_day_change'] > 1.5 and regression_data['PCT_change'] > 1.5)
            )
        ):  
        if(high_tail_pct(regression_data) > 1.5
            and regression_data['PCT_day_change'] > 0
            and regression_data['PCT_day_change_pre1'] > 0
            and abs(regression_data['PCT_day_change']) > high_tail_pct(regression_data)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkForSellATRReversal')
        elif(regression_data['PCT_day_change'] > 2
            and regression_data['forecast_day_PCT7_change'] > 10
            and regression_data['forecast_day_PCT10_change'] > 10
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkSellATRCrossForReversal')
        if(regression_data['PCT_day_change'] < 0
            and regression_data['PCT_change'] < 0
            and 4 > regression_data['PCT_day_change_pre1'] > 0.5
            and regression_data['PCT_day_change_pre2'] > 0.5
            and (regression_data['PCT_day_change_pre1'] > 1 or regression_data['PCT_day_change_pre2'] > 1)
            and (regression_data['forecast_day_PCT3_change'] > regression_data['forecast_day_PCT2_change']
                or regression_data['forecast_day_PCT4_change'] > regression_data['forecast_day_PCT3_change']
                )
            and regression_data['close'] < regression_data['high_pre1']
            and (regression_data['close'] > regression_data['high_pre2'] 
                 or regression_data['close'] > regression_data['high_pre3']
                )
            ):
            #add_in_csv(regression_data, regressionResult, ws, None, None, 'checkForUptrendContinueLastDayDown')
            add_in_csv(regression_data, regressionResult, ws, None, None, None)
        elif(regression_data['PCT_day_change'] > 1
            and regression_data['PCT_day_change_pre1'] > 1
            and regression_data['PCT_day_change_pre2'] > 1
            and regression_data['week2HighChange'] < -3
            and (regression_data['PCT_day_change_pre1'] < 0 or regression_data['PCT_day_change_pre2'] < 0 or regression_data['PCT_day_change_pre3'] < 0)
            ):
            #add_in_csv(regression_data, regressionResult, ws, None, None, 'checkForUptrendContinueWeek2HighNotReached')
            add_in_csv(regression_data, regressionResult, ws, None, None, None)
        elif(regression_data['PCT_day_change'] > 1
            and regression_data['PCT_day_change_pre1'] > 0.75
            and regression_data['PCT_day_change_pre2'] > 0.75
            and (regression_data['PCT_day_change_pre1'] > 1 or regression_data['PCT_day_change_pre2'] > 1)
#             and regression_data['monthHighChange'] > -2
#             and regression_data['monthLowChange'] > 10
            and regression_data['year2LowChange'] > 10
            and regression_data['month3HighChange'] < regression_data['monthHighChange']
            and regression_data['month6HighChange'] < regression_data['month3HighChange']
            ):
            if((regression_data['PCT_day_change_pre1'] < 0 or regression_data['PCT_day_change_pre2'] < 0 or regression_data['PCT_day_change_pre3'] < 0)
               ):
               add_in_csv(regression_data, regressionResult, ws, None, None, 'UPTRENDMARKET:checkForUptrendContinueMonthHigh(NotMonth3HighMonth6High)')
            else:
               add_in_csv(regression_data, regressionResult, ws, None, None, 'HEAVYUPTRENDMARKET:RISKY-Last4DayUp:checkForUptrendContinueMonthHigh(NotMonth3HighMonth6High)')
        elif(regression_data['PCT_day_change'] > 1
            and regression_data['PCT_day_change_pre1'] > 0.75
            and regression_data['PCT_day_change_pre2'] > 0.75
            and (regression_data['PCT_day_change_pre1'] > 1 or regression_data['PCT_day_change_pre2'] > 1)
            and regression_data['monthHighChange'] > -2
            and regression_data['monthLowChange'] > 10
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkForUptrendReversalMonthHigh(5to10-minute-baseline-if-uptrend)') 
        add_in_csv(regression_data, regressionResult, ws, None, 'TEST:yearLowCheckUpTrendATRBuyOrSell')
        flag = True
    elif((('(shortUpTrend)$NA' in regression_data['series_trend']) 
            or ('(shortUpTrend-Risky)$NA' in regression_data['series_trend'])
            or
            (regression_data['PCT_day_change'] > 0 
             and regression_data['PCT_day_change_pre1'] > 0
             and regression_data['PCT_day_change_pre2'] > 0
             and regression_data['PCT_day_change_pre3'] > 0
            )
        ) 
        and (regression_data['yearHighChange'] < -5)
        ):
        if(high_tail_pct(regression_data) > 1.5
            and regression_data['PCT_day_change'] > 0
            and regression_data['PCT_day_change_pre1'] > 0
            and abs(regression_data['PCT_day_change']) > high_tail_pct(regression_data)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkForSellATRReversal')
        elif(high_tail_pct(regression_data) > 3
            and regression_data['PCT_day_change'] > -1
            and regression_data['PCT_day_change_pre1'] > 1
            and regression_data['PCT_day_change_pre2'] > 1
            and abs(regression_data['PCT_day_change']) > high_tail_pct(regression_data)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkForSellATRReversalHighTail')
        elif(regression_data['PCT_day_change'] > 2
            and regression_data['forecast_day_PCT7_change'] > 10
            and regression_data['forecast_day_PCT10_change'] > 10
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkSellATRCrossForReversal')
        if(regression_data['PCT_day_change'] < 0
            and regression_data['PCT_change'] < 0
            and 4 > regression_data['PCT_day_change_pre1'] > 0.5
            and regression_data['PCT_day_change_pre2'] > 0.5
            and (regression_data['PCT_day_change_pre1'] > 1 or regression_data['PCT_day_change_pre2'] > 1)
            and (regression_data['forecast_day_PCT3_change'] > regression_data['forecast_day_PCT2_change']
                or regression_data['forecast_day_PCT4_change'] > regression_data['forecast_day_PCT3_change']
                )
            and regression_data['close'] < regression_data['high_pre1']
            and (regression_data['close'] > regression_data['high_pre2'] 
                 or regression_data['close'] > regression_data['high_pre3']
                )
            ):
            #add_in_csv(regression_data, regressionResult, ws, None, None, 'checkForUptrendContinueLastDayDown')
            add_in_csv(regression_data, regressionResult, ws, None, None, None)
        elif(regression_data['PCT_day_change'] > 1
            and regression_data['PCT_day_change_pre1'] > 1
            and regression_data['PCT_day_change_pre2'] > 1
            and regression_data['week2HighChange'] < -3
            and (regression_data['PCT_day_change_pre1'] < 0 or regression_data['PCT_day_change_pre2'] < 0 or regression_data['PCT_day_change_pre3'] < 0)
            ):
            #add_in_csv(regression_data, regressionResult, ws, None, None, 'checkForUptrendContinueWeek2HighNotReached')
            add_in_csv(regression_data, regressionResult, ws, None, None, None)
        elif(regression_data['PCT_day_change'] > 1
            and regression_data['PCT_day_change_pre1'] > 0.75
            and regression_data['PCT_day_change_pre2'] > 0.75
            and (regression_data['PCT_day_change_pre1'] > 1 or regression_data['PCT_day_change_pre2'] > 1)
#             and regression_data['monthHighChange'] > -2
#             and regression_data['monthLowChange'] > 10
            and regression_data['month3HighChange'] < regression_data['monthHighChange']
            and regression_data['month6HighChange'] < regression_data['month3HighChange']
            ):
            if((regression_data['PCT_day_change_pre1'] < 0 or regression_data['PCT_day_change_pre2'] < 0 or regression_data['PCT_day_change_pre3'] < 0)
               ):
               add_in_csv(regression_data, regressionResult, ws, None, None, 'UPTRENDMARKET:checkForUptrendContinueMonthHigh(NotMonth3HighMonth6High)')
            else:
               add_in_csv(regression_data, regressionResult, ws, None, None, 'HEAVYUPTRENDMARKET:RISKY-Last4DayUp:checkForUptrendContinueMonthHigh(NotMonth3HighMonth6High)')
        elif(regression_data['PCT_day_change'] > 1
            and regression_data['PCT_day_change_pre1'] > 0.75
            and regression_data['PCT_day_change_pre2'] > 0.75
            and (regression_data['PCT_day_change_pre1'] > 1 or regression_data['PCT_day_change_pre2'] > 1)
            and regression_data['monthHighChange'] > -2
            and regression_data['monthLowChange'] > 10
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkForUptrendReversalMonthHigh(5to10-minute-baseline-if-uptrend)')
        if(high_tail_pct(regression_data) > 1.5 
           and 0 < regression_data['PCT_day_change'] < 1
           and 0 < regression_data['PCT_day_change_pre1'] < 1.5
           and (regression_data['PCT_day_change_pre2'] > 2.5 or regression_data['PCT_day_change_pre3'] > 2.5)
           and regression_data['forecast_day_PCT2_change'] > 0
           and regression_data['forecast_day_PCT3_change'] > 0
           and regression_data['forecast_day_PCT4_change'] > 0
           ):
           add_in_csv(regression_data, regressionResult, ws, None, None, 'maySellShortUpTrendDoji')
        elif(high_tail_pct(regression_data) < 1.5 
           and 2 < regression_data['PCT_day_change'] < 4.5
           and 2 < regression_data['PCT_change'] < 5
           and regression_data['PCT_day_change_pre1'] < 0
           and regression_data['PCT_day_change_pre2'] > 0.5
           ):
           add_in_csv(regression_data, regressionResult, ws, None, None, 'mayBuyShortUpTrend(after10:20orlessThan1%)')
        elif(high_tail_pct(regression_data) < 1.5 
           and low_tail_pct(regression_data) > 1.5
           and -1.5 < regression_data['PCT_day_change'] < 0
           and (regression_data['PCT_day_change_pre1'] < 0 or regression_data['PCT_day_change_pre2'] < 0)
           and (regression_data['PCT_day_change_pre1'] > 2 or regression_data['PCT_day_change_pre2'] > 2)
           ):
           add_in_csv(regression_data, regressionResult, ws, None, None, 'mayBuyShortUpTrendDojiNegative')
#         elif(high_tail_pct(regression_data) < 1.5 
#            and low_tail_pct(regression_data) > 1.5
#            and 0 < regression_data['PCT_day_change'] < 1.5
#            and (regression_data['PCT_day_change_pre1'] > 2 and regression_data['PCT_day_change_pre2'] > 0)
#            ):
#            add_in_csv(regression_data, regressionResult, ws, None, None, 'mayBuyShortUpTrendDojiPositive')
        elif(regression_data['PCT_day_change_pre1'] > 1.5
           ):
           if(high_tail_pct(regression_data) < 1.5
              and 4 < regression_data['PCT_day_change'] < 7
              and 4 < regression_data['PCT_change'] < 7
              and regression_data['PCT_day_change_pre2'] < 0
              ): 
              add_in_csv(regression_data, regressionResult, ws, None, None, 'TestmayBuyShortUpTrend')
           elif(3 < regression_data['PCT_day_change'] < 5
              and 3 < regression_data['PCT_change'] < 5
              ):
              add_in_csv(regression_data, regressionResult, ws, None, None, 'TestmaySellShortUpTrend')
        add_in_csv(regression_data, regressionResult, ws, None, 'TEST:checkUpTrendATRBuyOrSell')
        flag = True
    elif('shortUpTrend' in regression_data['series_trend']):
        if(high_tail_pct(regression_data) > 1.5
            and regression_data['PCT_day_change'] > 0
            and regression_data['PCT_day_change_pre1'] > 0
            and abs(regression_data['PCT_day_change']) > high_tail_pct(regression_data)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkForSellATRReversal')
        elif(high_tail_pct(regression_data) > 3
            and regression_data['PCT_day_change'] > -1
            and regression_data['PCT_day_change_pre1'] > 1
            and regression_data['PCT_day_change_pre2'] > 1
            and abs(regression_data['PCT_day_change']) > high_tail_pct(regression_data)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkForSellATRReversalHighTail')
        elif(regression_data['PCT_day_change'] > 2
            and (regression_data['forecast_day_PCT7_change'] > 10 or regression_data['forecast_day_PCT10_change'] > 10)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'DOWNTREND:checkSellATRCrossForReversal')
            flag = True   
            
    if(regression_data['PCT_day_change'] < 0
        and regression_data['PCT_day_change_pre1'] > 0
        and regression_data['PCT_day_change_pre2'] > 0
        and (regression_data['PCT_day_change_pre1'] > 1 
             or regression_data['PCT_day_change_pre2'] > 1 
             or regression_data['PCT_day_change_pre3'] > 1
             )
        and regression_data['close'] < regression_data['high_pre1']
        and (regression_data['close'] > regression_data['high_pre2'] 
             or regression_data['close'] > regression_data['high_pre3']
             or (regression_data['close'] > regression_data['low_pre2'] and regression_data['close'] > regression_data['low_pre3'])
             )
        ):
        add_in_csv(regression_data, regressionResult, ws, None, 'RISKY-UPTREND-SELL') 
        flag = True
        if(-1.5 < regression_data['PCT_change'] < 0
           and -1 < regression_data['PCT_day_change'] < 0
           and (regression_data['PCT_change'] < -0.75 or regression_data['PCT_day_change'] < -0.75)
           and (regression_data['PCT_day_change_pre1'] > 1 or regression_data['PCT_day_change_pre2'] > 1 or regression_data['PCT_day_change_pre3'] > 1)
           and (abs_week2High_more_than_week2Low(regression_data)
                or abs_monthHigh_more_than_monthLow(regression_data)
                )
           and (-10 < regression_data['forecast_day_PCT7_change'] < -3 or -10 < regression_data['forecast_day_PCT10_change'] < -3)
           and (low_tail_pct(regression_data) < 1.5 or low_tail_pct(regression_data) < high_tail_pct(regression_data))
           and regression_data['year2HighChange'] < -5
           and regression_data['year2LowChange'] > 5
           ):
           add_in_csv(regression_data, regressionResult, ws, None, None, '[UPTRENDMARKET-BUY,DOWNTRENDMARKET:checkForDowntrendContinueInDOWNTRENDMARKET]')
        elif(-2 < regression_data['PCT_change'] < 0 and -2 < regression_data['PCT_day_change'] < 0
           and (-1 < regression_data['PCT_change'] or -1 < regression_data['PCT_day_change'] or regression_data['forecast_day_PCT4_change'] > 0)
           #and (regression_data['PCT_change'] < -0.75 or regression_data['PCT_day_change'] < -0.75)
           and (regression_data['PCT_day_change_pre1'] > 1 or regression_data['PCT_day_change_pre2'] > 1 or regression_data['PCT_day_change_pre3'] > 1)
           and (abs_week2High_more_than_week2Low(regression_data)
                or abs_monthHigh_more_than_monthLow(regression_data)
                )
           and (-10 < regression_data['forecast_day_PCT7_change'] < -2 
                or -10 < regression_data['forecast_day_PCT10_change'] < -2
                or (-10 < regression_data['forecast_day_PCT7_change'] < 0 and -10 < regression_data['forecast_day_PCT10_change'] < 0)
                )
           and regression_data['year2HighChange'] < -5
           and regression_data['year2LowChange'] > 5
           ):
           if((0 < regression_data['PCT_day_change_pre1'] < 1 and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change']))
               or (regression_data['SMA9'] > 0 and regression_data['SMA25'] > 0)
               ):
               add_in_csv(regression_data, regressionResult, ws, None, None,'[UPTRENDMARKET-BUY,DOWNTRENDMARKET:RISKYcheckForUptrendContinueInGLOBALMARKETUP]')
           elif((low_tail_pct(regression_data) < 1.5 or low_tail_pct(regression_data) < high_tail_pct(regression_data))
               #and regression_data['SMA9'] < 0
               ):
               add_in_csv(regression_data, regressionResult, ws, None, None, '[UPTRENDMARKET-BUY,DOWNTRENDMARKET:RISKYcheckForDowntrendContinueInGLOBALMARKETDOWN]')
        
        elif(-3 < regression_data['PCT_change'] < 2
           and -1 < regression_data['PCT_day_change'] < 0
           and regression_data['PCT_day_change_pre1'] > 0
           and regression_data['PCT_day_change_pre2'] > 0
           and regression_data['year2HighChange'] < -5
           and regression_data['year2LowChange'] > 5
           ):
            if(4 > low_tail_pct(regression_data) > 1
                and high_tail_pct(regression_data) < 1 
                and low_tail_pct(regression_data) > high_tail_pct(regression_data)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None,'LowTail-GT-HighTail')
            elif(4 > high_tail_pct(regression_data) > 1
                and low_tail_pct(regression_data) < 1
                and high_tail_pct(regression_data) > low_tail_pct(regression_data)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None,'HighTail-GT-LowTail')
            if(regression_data['PCT_day_change_pre1'] > 1
                and regression_data['PCT_day_change_pre2'] > 1
                and regression_data['PCT_day_change'] < 0
                and regression_data['low'] > regression_data['low_pre1']
                and low_tail_pct(regression_data) < high_tail_pct(regression_data)
                and (regression_data['forecast_day_PCT4_change'] < 0 or regression_data['forecast_day_PCT5_change'] < 0 or regression_data['forecast_day_PCT7_change'] < 0)
                ): 
                add_in_csv(regression_data, regressionResult, ws, None, None,'STRONG-DOWNTRENDMARKET:followMarketTrend')
            elif(regression_data['PCT_day_change_pre1'] > 0.5
                and regression_data['PCT_day_change_pre2'] > 0.5
                and regression_data['PCT_day_change'] < 0
                and regression_data['low'] > regression_data['low_pre1']
                and low_tail_pct(regression_data) < high_tail_pct(regression_data)
                ): 
                add_in_csv(regression_data, regressionResult, ws, None, None,'[UPTREND-BUY,DOWNTREND-SELL]')
            elif(regression_data['PCT_day_change_pre1'] > 0.5
                and regression_data['PCT_day_change_pre2'] > 0.5
                and regression_data['PCT_day_change'] < 0
                and regression_data['low'] > regression_data['low_pre1']
                ): 
                add_in_csv(regression_data, regressionResult, ws, None, None,'[UPTREND-BUY]')
        elif(-3 < regression_data['PCT_change'] < 2
           and regression_data['PCT_day_change_pre1'] > 0
           and regression_data['PCT_day_change_pre2'] > 0
           and regression_data['year2HighChange'] < -5
           and regression_data['year2LowChange'] > 5
           ):
            if(4 > low_tail_pct(regression_data) > 1
                and high_tail_pct(regression_data) < 1 
                and low_tail_pct(regression_data) > high_tail_pct(regression_data)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None,'LowTail-GT-HighTail')
            elif(4 > high_tail_pct(regression_data) > 1
                and low_tail_pct(regression_data) < 1
                and high_tail_pct(regression_data) > low_tail_pct(regression_data)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None,'HighTail-GT-LowTail')
            if(regression_data['PCT_day_change_pre1'] > 0
                and regression_data['PCT_day_change_pre2'] > 0
                and regression_data['PCT_day_change'] < 0
                and regression_data['low'] < regression_data['low_pre1']
                and regression_data['low'] > regression_data['low_pre2']
                and low_tail_pct(regression_data) < high_tail_pct(regression_data)
                ): 
                add_in_csv(regression_data, regressionResult, ws, None, None,'[UPTREND-BUY-RISKY,DOWNTREND-SELL-RISKY]')
            elif(regression_data['PCT_day_change_pre1'] > 0
                and regression_data['PCT_day_change_pre2'] > 0
                and regression_data['PCT_day_change'] < 0
                and regression_data['low'] < regression_data['low_pre2']
                and regression_data['low'] > regression_data['low_pre2']
                ): 
                add_in_csv(regression_data, regressionResult, ws, None, None,'[UPTREND-BUY-RISKY]')     
        elif(-1.5 < regression_data['PCT_change'] < 0
            and -1 < regression_data['PCT_day_change'] < 0
            and (regression_data['PCT_change'] < -0.75 or regression_data['PCT_day_change'] < -0.75)
            and (regression_data['PCT_day_change_pre1'] > 1 or regression_data['PCT_day_change_pre2'] > 1 or regression_data['PCT_day_change_pre3'] > 1)
            and abs_monthHigh_less_than_monthLow(regression_data)
            and (regression_data['forecast_day_PCT7_change'] > 3 or regression_data['forecast_day_PCT10_change'] > 3)
            and regression_data['year2HighChange'] < -5
            and regression_data['year2LowChange'] > 5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'STOCK-IN-UPTREND')       
           
        if(-1.5 < regression_data['PCT_change'] < 0
           and -1 < regression_data['PCT_day_change'] < 0
           and regression_data['year2HighChange'] < -5
           and regression_data['year2LowChange'] > 5
            ):
            if(regression_data['PCT_day_change_pre1'] > 0 
                and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change']) * 2
                and high_tail_pct(regression_data) + 0.5 < low_tail_pct(regression_data) 
                and regression_data['month3HighChange'] < -2
                and low_tail_pct(regression_data) < 3.5
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'STOCK-IN-UPTREND-BUY')
            elif(regression_data['PCT_day_change_pre1'] > 0 
                and abs(regression_data['PCT_day_change_pre1']) < abs(regression_data['PCT_day_change'])
                and high_tail_pct(regression_data) > low_tail_pct(regression_data) + 0.5
                and high_tail_pct(regression_data) < 3.5
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'STOCK-IN-UPTREND-SELL')           
        if(regression_data['PCT_change'] < 0
            and 4 > regression_data['PCT_day_change_pre1']
            and (regression_data['PCT_day_change_pre3'] < 1 
                 or low_tail_pct(regression_data) > 1
                 or low_tail_pct(regression_data) > high_tail_pct(regression_data)
                 )
            and (regression_data['forecast_day_PCT3_change'] > regression_data['forecast_day_PCT2_change']
                 or regression_data['forecast_day_PCT4_change'] > regression_data['forecast_day_PCT3_change']
                 )
            #and regression_data['year2HighChange'] < -10
            and regression_data['year2LowChange'] > 10
            and regression_data['week2LowChange'] == regression_data['month3LowChange']
            and regression_data['week2LowChange'] < 5
            and (abs_monthHigh_less_than_monthLow(regression_data)
                 or regression_data['monthHighChange'] > 0
                 or regression_data['week2HighChange'] > 0
                )
            ):
            if(regression_data['PCT_day_change'] < -4 and regression_data['PCT_change'] < -4):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'UPTRENDMARKET:checkForUptrendContinueLastDayDown')
            elif(low_tail_pct(regression_data) > high_tail_pct(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'UPTRENDMARKET:checkForUptrendContinueLastDayDown')
        if(regression_data['PCT_change'] < 1
            and -1 < regression_data['PCT_day_change'] < 0
            and regression_data['forecast_day_PCT10_change'] < 0.5
            and regression_data['monthLowChange'] > 5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'UPTRENDMARKET:checkForUptrendContinueLastDayDownPCT10LT0.5') 
    
    if('%%maySellTail' in regression_data['filter']
        and (('upTrend' in regression_data['series_trend'])
             or ('UpTrend' in regression_data['series_trend'])
             or pct_day_change_trend(regression_data) >= 3
             )
        and ('shortUpTrend-Mini' not in regression_data['series_trend'])
        ):
        countGt, countLt = pct_day_change_counter(regression_data)
        if(countGt > countLt 
            and regression_data['PCT_day_change'] < 3
            and regression_data['PCT_change'] < 3
            and regression_data['forecast_day_PCT10_change'] < 10
            and (-5 > regression_data['month3HighChange'] or regression_data['month3HighChange'] > 2)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, '%%BuyUpTrend-highTail')
        elif(regression_data['PCT_day_change'] > -0.5
            and regression_data['PCT_change'] > -0.5
            and -2 < regression_data['month3HighChange'] < 2
            ):
            add_in_csv(regression_data, regressionResult, ws, None, '%%SellUpTrend-highTail-nearMonth3High')
        flag = True
        
    if('NA$NA:NA$(shortDownTrend-MayReversal)' in regression_data['series_trend']
        and regression_data['PCT_day_change'] < -0.5
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'TEST:shortDownTrend-MayReversalBuy')
        flag = True 
        
    if(high_volatility(regression_data, regressionResult, True)):
        flag = True    
    return flag

def buy_common_up_continued(regression_data, regressionResult, reg, ws):
    if(high_tail_pct(regression_data) < 1.1 and low_tail_pct(regression_data) < 2
        and regression_data['monthHighChange'] > 0 and regression_data['month3LowChange'] < 40
        and (regression_data['month3LowChange'] > 10 or regression_data['month6LowChange'] > 15)
        and (regression_data['forecast_day_PCT10_change'] < 15)
        and (regression_data['forecast_day_PCT5_change'] < 10 or regression_data['forecast_day_PCT10_change'] < 10)
        
        and ((regression_data['PCT_day_change_pre1'] > 0
                and (regression_data['PCT_day_change_pre2'] < 0 or regression_data['PCT_day_change_pre3'] < 0)
                and (regression_data['forecast_day_PCT5_change'] > 10 or regression_data['forecast_day_PCT7_change'] > 10 or regression_data['forecast_day_PCT10_change'] > 10)
                )
             or (regression_data['PCT_day_change_pre1'] > 0 
                and regression_data['PCT_day_change_pre2'] < 0 
                and (regression_data['forecast_day_PCT5_change'] < 5)
                )
             or ((regression_data['monthHighChange'] > 0 or regression_data['month3HighChange'] > 0)
                and regression_data['yearHighChange'] > -10
                )
            )
        and (regression_data['PCT_day_change_pre1'] < 0 or regression_data['PCT_day_change_pre2'] < 0 or regression_data['PCT_day_change_pre3'] < 0)
        ):
        if(2.5 < regression_data['PCT_day_change'] < 4.0 and 2.5 < regression_data['PCT_change'] < 5):
            if(regression_data['monthLowChange'] < 5):
                add_in_csv(regression_data, regressionResult, ws, 'CommonHL:mayBuyUpContinueGT3')
            elif(regression_data['forecast_day_PCT5_change'] < 10 
                and regression_data['forecast_day_PCT10_change'] < 10
                and regression_data['yearHighChange'] < -5
                ):
                add_in_csv(regression_data, regressionResult, ws, 'CommonHL:mayBuyUpContinueGT3-Risky')
        elif(2 < regression_data['PCT_day_change'] < 4 and 1 < regression_data['PCT_change'] < 5):
            if(regression_data['monthLowChange'] < 5):
                add_in_csv(regression_data, regressionResult, ws, 'CommonHL:mayBuyUpContinueLT3')  
            else:
                add_in_csv(regression_data, regressionResult, ws, 'CommonHL:mayBuyUpContinueLT3-Risky')
                
    elif(high_tail_pct(regression_data) < 2 and low_tail_pct(regression_data) < 2
        and (regression_data['monthLowChange'] < 5 and regression_data['month3LowChange'] < 5 
             and regression_data['month3HighChange'] < 0 and regression_data['month6HighChange'] < -5)
        and (regression_data['forecast_day_PCT10_change'] < 15)
        and (regression_data['forecast_day_PCT5_change'] < 10 or regression_data['forecast_day_PCT10_change'] < 10)  
        and (regression_data['PCT_day_change_pre1'] < 0 or regression_data['PCT_day_change_pre2'] < 0 or regression_data['PCT_day_change_pre3'] < 0)
        ):
        if(3.5 < regression_data['PCT_day_change'] < 6.0 and 3.5 < regression_data['PCT_change'] < 7):
                add_in_csv(regression_data, regressionResult, ws, 'CommonHL:mayBuyUpContinueGT3AfterSomeDownCheckBase')

def buy_af_high_indicators(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_cla, kNeighboursValue_cla = get_reg_or_cla(regression_data, False)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    if(regression_data['PCT_day_change'] == 0):
        return False
    flag = False
    if(regression_data['PCT_day_change'] < 1.5 and regression_data['PCT_change'] < 1.5):
        if(is_algo_buy(regression_data, True)
            and (mlpValue >= 2.5 or kNeighboursValue >= 2.5)
            and (mlpValue_other >= 0 and kNeighboursValue_other >= 0)
            and (regression_data['PCT_day_change'] < 5)
            ):
            if(((4.0 <= mlpValue < 10.0 and 2.0 <= kNeighboursValue < 10.0) or (2.0 <= mlpValue < 10.0 and 4.0 <= kNeighboursValue < 10.0))
                ):
                if(mlpValue_cla > 0 or kNeighboursValue_cla > 0):
                    add_in_csv(regression_data, regressionResult, ws, 'buyHighIndicators')
                    flag = True
            elif((2 <= mlpValue < 10.0 and 0 <= kNeighboursValue < 10.0)
                and (2 <= mlpValue_other or regression_data['PCT_day_change'] < -2) 
                and (0 <= mlpValue_cla )
                ):
                add_in_csv(regression_data, regressionResult, ws, 'buyHighMLPClaIndicators')
                flag = True
            elif((0 <= mlpValue < 10.0 and 4 <= kNeighboursValue < 10.0)
                and (2 <= kNeighboursValue_other or regression_data['PCT_day_change'] < -2)
                and (0 <= kNeighboursValue_cla )
                ):
                add_in_csv(regression_data, regressionResult, ws, 'buyHighKNClaIndicators')
                flag = True
        elif((mlpValue_other >= 0 and kNeighboursValue_other >= 0)
            #and (mlpValue_cla > 0 or kNeighboursValue_cla > 0)
            and (2.0 <= mlpValue < 10.0 and 2.0 <= kNeighboursValue < 10.0)
            and ((mlpValue + kNeighboursValue) > 5)
            ):
            add_in_csv(regression_data, regressionResult, ws, 'buyHighIndicators-Risky')
            flag = True
        elif((mlpValue_other >= 0 and kNeighboursValue_other >= 0)
            and (2 <= mlpValue < 10.0 and 0 <= kNeighboursValue < 10.0)
            and (2 <= mlpValue_other or regression_data['PCT_day_change'] < -2)
            ):
            add_in_csv(regression_data, regressionResult, ws, 'buyHighMLPClaIndicators-risky')
            flag = True
        elif((mlpValue_other >= 0 and kNeighboursValue_other >= 0)
            and (0 <= mlpValue < 10.0 and 2 <= kNeighboursValue < 10.0)
            and (2 <= kNeighboursValue_other or regression_data['PCT_day_change'] < -2)
            ):
            add_in_csv(regression_data, regressionResult, ws, 'buyHighKNClaIndicators-risky')
            flag = True
    return flag
    
def buy_af_low_tail(regression_data, regressionResult, reg, ws):
    if(high_tail_pct(regression_data) <= 2 and 2 <= low_tail_pct(regression_data) <= 5.5
        and -5 < regression_data['PCT_day_change'] < 5
        and -7 < regression_data['PCT_day_change_pre1'] 
        and regression_data['forecast_day_PCT7_change'] < -5
        and regression_data['forecast_day_PCT10_change'] < -5
        and (regression_data['forecast_day_PCT7_change'] < -15
             or regression_data['forecast_day_PCT10_change'] < -15)
        ):
        if(regression_data['PCT_day_change'] < 3
            and (regression_data['forecast_day_PCT7_change'] < -20
                 or regression_data['forecast_day_PCT10_change'] < -20)
            ):
            add_in_csv(regression_data, regressionResult, ws, '%%AF:mayBuyTail-tailGT2-7,10thDayLT(-20)')
        elif(regression_data['PCT_day_change'] < 3):
            add_in_csv(regression_data, regressionResult, ws, '%%AF-Risky9:30:mayBuyTail-tailGT2-7,10thDayLT(-15)')
        else:
            add_in_csv(regression_data, regressionResult, ws, None)
    elif(high_tail_pct(regression_data) <= 2 and 3 <= low_tail_pct(regression_data) <= 5
        and 0 < regression_data['PCT_day_change'] < 5 and -5 < regression_data['PCT_change'] < 5
        and regression_data['PCT_day_change_pre1'] < 0
        and regression_data['PCT_day_change_pre2'] < 0
        and regression_data['forecast_day_PCT3_change'] < 0
        and regression_data['forecast_day_PCT4_change'] < 0
        and regression_data['forecast_day_PCT5_change'] < 0
        and regression_data['forecast_day_PCT7_change'] < 0
        and regression_data['forecast_day_PCT10_change'] < 0
        and (regression_data['forecast_day_PCT7_change'] < -15 
             or regression_data['forecast_day_PCT10_change'] < -15
             or (regression_data['forecast_day_PCT7_change'] < -10 and regression_data['forecast_day_PCT10_change'] < -10)
             or ((regression_data['forecast_day_PCT7_change'] < -5 or regression_data['forecast_day_PCT10_change'] < -5) and regression_data['PCT_day_change'] > 2)
             )
        ):
        add_in_csv(regression_data, regressionResult, ws, '%%AF:mayBuyTail-tailGT2-allDayLT0')
    elif(high_tail_pct(regression_data) <= 1 and 2 <= low_tail_pct(regression_data) <= 4
        and -5 < regression_data['PCT_day_change'] < -1 and -5 < regression_data['PCT_change'] < -1
        and regression_data['forecast_day_PCT2_change'] < 0
        and regression_data['forecast_day_PCT3_change'] < 0
        and regression_data['forecast_day_PCT4_change'] < 0
        and regression_data['forecast_day_PCT5_change'] < 5
        and regression_data['forecast_day_PCT7_change'] < 10
        and regression_data['forecast_day_PCT10_change'] < 10
        and (regression_data['forecast_day_PCT7_change'] < 5 or regression_data['forecast_day_PCT10_change'] < 5)
        and (regression_data['forecast_day_PCT7_change'] > 0 or regression_data['forecast_day_PCT10_change'] > 0)
        ):
#            if(regression_data['forecast_day_PCT7_change'] > -5
#                or regression_data['forecast_day_PCT10_change'] > -5
#                ): 
#                add_in_csv(regression_data, regressionResult, ws, '%%AF:mayBuyTail-tailGT2-2,3,4thDayLT0')
#            else:
        add_in_csv(regression_data, regressionResult, ws, '%%AF:(GLOBAL-UP)mayBuyTail-tailGT2-2,3,4thDayLT0')
    elif(high_tail_pct(regression_data) < 2 and 1.5 < low_tail_pct(regression_data) < 2.1
        and (('MayBuy-CheckChart' in regression_data['filter1']) or ('MayBuyCheckChart' in regression_data['filter1']))
        and (-0.75 < regression_data['PCT_day_change'] < 0.75) and (-2.5 < regression_data['PCT_change'] < 2.5)
        and (regression_data['PCT_day_change'] > 0 or regression_data['PCT_change_pre1'] > 0)
        and (is_algo_buy(regression_data) or regression_data['PCT_change_pre2'] < 0 or regression_data['PCT_change_pre3'] < 0)
        and low_tail_pct(regression_data) > high_tail_pct(regression_data)
        ): 
        add_in_csv(regression_data, regressionResult, ws, '%%AF-LastDayDown:(GLOBAL-UP)MayBuyLowTail-LastDayMarketDown')
    elif(high_tail_pct(regression_data) <= 1 and 1.3 <= low_tail_pct(regression_data) <= 2
        and low_tail_pct(regression_data) > (high_tail_pct(regression_data) + 0.5)
        ):
        if(-3 < regression_data['PCT_day_change'] < -0.5 and -3 < regression_data['PCT_change'] < -0.5
            and (regression_data['PCT_day_change'] < -1 or regression_data['PCT_change'] < -1)
            and regression_data['forecast_day_PCT2_change'] < 0
            and regression_data['forecast_day_PCT3_change'] < 0
            and regression_data['forecast_day_PCT4_change'] < 0
            and regression_data['forecast_day_PCT5_change'] < 5
            and regression_data['forecast_day_PCT7_change'] < 10
            and regression_data['forecast_day_PCT10_change'] < 10
            and (regression_data['forecast_day_PCT7_change'] < 5 or regression_data['forecast_day_PCT10_change'] < 5)
            ):
            if(regression_data['forecast_day_PCT7_change'] > -5
                or regression_data['forecast_day_PCT10_change'] > -5
                ): 
                add_in_csv(regression_data, regressionResult, ws, '%%AF:mayBuyTail-2,3,4thDayLT0')
            else:
                add_in_csv(regression_data, regressionResult, ws, '%%AF:(GLOBAL-UP)mayBuyTail-2,3,4thDayLT0')   
#         elif(-3 < regression_data['PCT_day_change'] < 1 
#            and -3 < regression_data['PCT_change'] < 1 
#            and 1.4 <= low_tail_pct(regression_data)
#            and is_algo_buy(regression_data)
#            ):
#            if(regression_data['high'] < regression_data['high_pre1']
#                 and regression_data['PCT_day_change'] > 0 and regression_data['PCT_change'] > 0
#                 and regression_data['PCT_day_change_pre1'] > 0
#                 and regression_data['PCT_day_change_pre2'] > 0
#                 and abs(regression_data['PCT_day_change']) < abs(regression_data['PCT_day_change_pre1'])
#                 and abs(regression_data['PCT_day_change']) < abs(regression_data['PCT_day_change_pre2'])
#                 and (regression_data['weekHighChange'] < 0 or regression_data['week2HighChange'] or regression_data['week3HighChange'])
#                 ):
#                 add_in_csv(regression_data, regressionResult, ws, None)
#            elif((regression_data['high'] > regression_data['high_pre1']
#                 and regression_data['PCT_day_change'] > 0 and regression_data['PCT_change'] > 0
#                 )
#                 or
#                 (regression_data['PCT_day_change'] < 0 and regression_data['PCT_change'] < 0)
#                 ):
#                 add_in_csv(regression_data, regressionResult, ws, '%%AF:mayBuyTail-Risky')
    
    
    if(low_tail_pct(regression_data) <= 2 and 2 <= high_tail_pct(regression_data) <= 5.5
        and -5 < regression_data['PCT_day_change'] < 5
        and regression_data['PCT_day_change_pre1'] < 7
        and regression_data['forecast_day_PCT7_change'] > 5
        and regression_data['forecast_day_PCT10_change'] > 5
        and (regression_data['forecast_day_PCT7_change'] > 15
             or regression_data['forecast_day_PCT10_change'] > 15)
        ):
        if(-3 < regression_data['PCT_day_change'] 
            and(regression_data['forecast_day_PCT7_change'] > 20
                or regression_data['forecast_day_PCT10_change'] > 20)
            ):
            add_in_csv(regression_data, regressionResult, ws, '%%AF:maySellTail-tailGT2-7,10thDayGT20') 
        elif(-3 < regression_data['PCT_day_change']):
            add_in_csv(regression_data, regressionResult, ws, '%%AF-Risky9:30:maySellTail-tailGT2-7,10thDayGT15')
        else:
            add_in_csv(regression_data, regressionResult, ws, None) 
#     elif(-3 < regression_data['PCT_day_change'] < 0 and -3 < regression_data['PCT_day_change'] < 1
#         and 1.3 < low_tail_pct(regression_data) < 2
#         and high_tail_pct(regression_data) < 5
#         ):
#         if(high_tail_pct(regression_data) < low_tail_pct(regression_data)):
#             add_in_csv(regression_data, regressionResult, ws, None)
#         else:
#             add_in_csv(regression_data, regressionResult, ws, None)
    elif(low_tail_pct(regression_data) <= 2 and 3 <= high_tail_pct(regression_data) <= 5
        and -5 < regression_data['PCT_day_change'] < 5 and -5 < regression_data['PCT_change'] < 5
        and regression_data['PCT_day_change_pre1'] > 0
        and regression_data['PCT_day_change_pre2'] > 0
        and regression_data['forecast_day_PCT3_change'] > 0
        and regression_data['forecast_day_PCT4_change'] > 0
        and regression_data['forecast_day_PCT5_change'] > 0
        and regression_data['forecast_day_PCT7_change'] > 0
        and regression_data['forecast_day_PCT10_change'] > 0
        and (regression_data['forecast_day_PCT7_change'] > 5 or regression_data['forecast_day_PCT10_change'] > 5)
        ):
        add_in_csv(regression_data, regressionResult, ws, None)
    elif(low_tail_pct(regression_data) <= 2 and 3 <= high_tail_pct(regression_data) <= 5
        and -6 < regression_data['PCT_day_change'] < 0 and -6 < regression_data['PCT_change'] < 0
        and regression_data['PCT_day_change_pre1'] < 0
        and regression_data['PCT_day_change_pre2'] < 0
        and regression_data['PCT_day_change_pre3'] < 0
        and regression_data['forecast_day_PCT3_change'] < 0
        and regression_data['forecast_day_PCT4_change'] < 0
        and regression_data['forecast_day_PCT5_change'] < 0
        and regression_data['forecast_day_PCT7_change'] < 0
        and regression_data['forecast_day_PCT10_change'] < 0
        and (-10 < regression_data['forecast_day_PCT7_change'] < -5
             or -10 < regression_data['forecast_day_PCT10_change'] < -5)
        and (abs(regression_data['month3HighChange']) < abs(regression_data['month3LowChange'])) 
        ):
        add_in_csv(regression_data, regressionResult, ws, '%%AF:sellStockInDowntrend')
    elif(low_tail_pct(regression_data) <= 1 and 2 <= high_tail_pct(regression_data) <= 5
        and -2 < regression_data['PCT_day_change'] < 2 
        and regression_data['PCT_day_change_pre1'] < 0
        and regression_data['PCT_day_change_pre2'] < 0
        and regression_data['PCT_day_change_pre3'] < 0
        and regression_data['forecast_day_PCT3_change'] < 0
        and regression_data['forecast_day_PCT4_change'] < 0
        and regression_data['forecast_day_PCT5_change'] < 0
        and (regression_data['forecast_day_PCT7_change'] > 0
             and regression_data['forecast_day_PCT10_change'] > 0)
        ):
        add_in_csv(regression_data, regressionResult, ws, '%%AF:buyStockInDowntrendReversal')  
    elif((3.5 < high_tail_pct(regression_data) < 6 or (2.5 < high_tail_pct(regression_data) < 5.5 and low_tail_pct(regression_data) < 1.5)) 
        and low_tail_pct(regression_data) < 3.5
        and (regression_data['PCT_day_change'] < (high_tail_pct(regression_data)*2))
        ):
        if(regression_data['PCT_day_change'] > 1 and regression_data['PCT_change'] > 1
            and regression_data['PCT_day_change'] < high_tail_pct(regression_data)
            ):
            if(regression_data['forecast_day_PCT7_change'] < 0 or regression_data['forecast_day_PCT10_change'] < 0
                #or (is_algo_buy(regression_data) and regression_data['PCT_day_change'] < 4 and abs(regression_data['PCT_day_change']) < low_tail_pct(regression_data))
                ):
                add_in_csv(regression_data, regressionResult, ws, '%%AF:buyHighUpperTail-Reversal-LastDayMarketDown')
            else:
                add_in_csv(regression_data, regressionResult, ws, None)
        elif((regression_data['forecast_day_PCT7_change'] < 5 and regression_data['forecast_day_PCT10_change'] < 5
            and (regression_data['forecast_day_PCT7_change'] < 0 or regression_data['forecast_day_PCT10_change'] < 0))
            or regression_data['forecast_day_PCT10_change'] < 0
            ):
            if(regression_data['forecast_day_PCT_change'] > 0
                and regression_data['forecast_day_PCT2_change'] > 0
                and regression_data['forecast_day_PCT3_change'] > 0
                #and is_algo_sell(regression_data) 
                and regression_data['forecast_day_PCT7_change'] < 0
                and regression_data['forecast_day_PCT10_change'] < 0
                and is_algo_buy(regression_data) == False
                ):
                add_in_csv(regression_data, regressionResult, ws, '%%AF:(Not-GLOBAL-UP)maySellTail-tailGT2')
            elif(regression_data['forecast_day_PCT7_change'] < 0 and regression_data['forecast_day_PCT10_change'] < 0):
                add_in_csv(regression_data, regressionResult, ws, '%%AF:(GLOBAL-UP)buyHighUpperTail-Reversal-LastDayMarketDown')
            elif(is_algo_sell(regression_data) == False):
                add_in_csv(regression_data, regressionResult, ws, '%%AF:(GLOBAL-UP)buyHighUpperTail-Reversal-LastDayMarketDown')
        elif(regression_data['PCT_day_change'] < 1
            and is_algo_buy(regression_data)
            ):
            add_in_csv(regression_data, regressionResult, ws, '%%AF-Risky:(GLOBAL-UP)buyHighUpperTail-Reversal-LastDayMarketDown')
        elif(3.5 < high_tail_pct(regression_data) < 6):
            add_in_csv(regression_data, regressionResult, ws, '%%AF-Last2DayMarketDown:(GLOBAL-UP)buyHighUpperTail-Reversal-LastDayMarketDown')
    elif(2 < low_tail_pct_pre1(regression_data) < 6
        and 2.9 < regression_data['PCT_day_change'] < 4.1
        and abs(regression_data['PCT_day_change_pre1']) < 1.5
        and regression_data['PCT_day_change_pre2'] < -1
        and abs(regression_data['PCT_day_change_pre2']) > abs(regression_data['PCT_day_change_pre1'])
        #and regression_data['high'] >= regression_data['bar_high_pre2']
        #and abs(regression_data['month6HighChange']) < abs(regression_data['month6LowChange'])
        and low_tail_pct(regression_data) < 1.5
        and high_tail_pct(regression_data) < 1.5
        ):
        add_in_csv(regression_data, regressionResult, ws, '%%AF-Last2DayMarketUp:(GLOBAL-DOWN)sellHighLowerTailPre1-Reversal-LastDayMarketUp')
 
def buy_af_up_continued(regression_data, regressionResult, reg, ws):
    if(high_tail_pct(regression_data) < 1.1 and low_tail_pct(regression_data) < 2
        and regression_data['monthLowChange'] < 5
        and (regression_data['month3LowChange'] > 10 or regression_data['month6LowChange'] > 15)
        and (regression_data['forecast_day_PCT10_change'] < 15)
        and (regression_data['forecast_day_PCT5_change'] < 10 or regression_data['forecast_day_PCT10_change'] < 10)
        
        and ((regression_data['PCT_day_change_pre1'] > 0
                and (regression_data['PCT_day_change_pre2'] < 0 or regression_data['PCT_day_change_pre3'] < 0)
                and (regression_data['forecast_day_PCT5_change'] > 10 or regression_data['forecast_day_PCT7_change'] > 10 or regression_data['forecast_day_PCT10_change'] > 10)
                )
             or (regression_data['PCT_day_change_pre1'] > 0 
                and regression_data['PCT_day_change_pre2'] < 0 
                and (regression_data['forecast_day_PCT5_change'] < 5)
                )
             or ((regression_data['monthHighChange'] > 0 or regression_data['month3HighChange'] > 0)
                and regression_data['yearHighChange'] > -10
                )
            )
        and (regression_data['PCT_day_change_pre1'] < 0 or regression_data['PCT_day_change_pre2'] < 0 or regression_data['PCT_day_change_pre3'] < 0)
        ):
        if(2.5 < regression_data['PCT_day_change'] < 4.0 and 2.5 < regression_data['PCT_change'] < 5):
            if(regression_data['monthLowChange'] < 5):
                add_in_csv(regression_data, regressionResult, ws, '%%AF:mayBuyUpContinueGT3')
            elif(regression_data['forecast_day_PCT5_change'] < 10 
                and regression_data['forecast_day_PCT10_change'] < 10
                and regression_data['yearHighChange'] < -5
                ):
                add_in_csv(regression_data, regressionResult, ws, '%%AF:mayBuyUpContinueGT3-Risky')
        elif(2 < regression_data['PCT_day_change'] < 4 and 1 < regression_data['PCT_change'] < 5):
            if(regression_data['monthLowChange'] < 5):
                add_in_csv(regression_data, regressionResult, ws, '%%AF:mayBuyUpContinueLT3')  
            else:
                add_in_csv(regression_data, regressionResult, ws, '%%AF:mayBuyUpContinueLT3-Risky')

def buy_af_oi_negative(regression_data, regressionResult, reg, ws):
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
                add_in_csv(regression_data, regressionResult, ws, '%%AF:buyNegativeOI-0-checkBase(1%down)')
                return True
            if(-2 < regression_data['PCT_day_change'] < 0 and -2 < regression_data['PCT_change'] < 0
                ):
                add_in_csv(regression_data, regressionResult, ws, '%%AF:buyNegativeOI-1-checkBase(1%down)')
                return True
        return False
    return False

def buy_af_vol_contract(regression_data, regressionResult, reg, ws):
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
            if((mlpValue >= 0.3 and kNeighboursValue >= 0.3) and is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, '%%AF:buyOI-0-checkBase-Risky')
                return True
            return False
        elif((regression_data['forecast_day_VOL_change'] > 35 and 0.5 < regression_data['PCT_day_change'] < 2 and 1 < regression_data['PCT_change'] < 2)
            and float(regression_data['contract']) > 20
            #and regression_data['PCT_day_change_pre1'] > -0.5
            ):
            if((mlpValue >= 0.3 and kNeighboursValue >= 0.3) and is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, '%%AF:buyOI-1-checkBase-Risky')
                return True
            return False
        elif((regression_data['forecast_day_VOL_change'] > 150 and 1 < regression_data['PCT_day_change'] < 3 and 1 < regression_data['PCT_change'] < 3)
            #and regression_data['PCT_day_change_pre1'] > -0.5
            ):
            if((mlpValue >= 0.3 and kNeighboursValue >= 0.3) or is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, '%%AF:buyOI-2-checkBase-Risky')
                return True
            return False
        elif((regression_data['forecast_day_VOL_change'] > 500 and 1 < regression_data['PCT_day_change'] < 5 and 1 < regression_data['PCT_change'] < 5)
            and float(regression_data['contract']) > 50 
            and (regression_data['forecast_day_PCT10_change'] < -8 or regression_data['forecast_day_PCT7_change'] < -8)
            ):
            if((mlpValue >= 0.3 and kNeighboursValue >= 0.3) or is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, '%%AF:buyOI-4-checkBase-Risky')
                return True
            return False    
    return False

def buy_af_vol_contract_contrarian(regression_data, regressionResult, reg, ws):
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
        and high_tail_pct(regression_data) > 1.5
        and low_tail_pct(regression_data) < 1
        ):
        if((regression_data['forecast_day_VOL_change'] > 70 and 0.75 < regression_data['PCT_day_change'] < 2 and 0.5 < regression_data['PCT_change'] < 2)
            and float(regression_data['contract']) > 10
            ):
            add_in_csv(regression_data, regressionResult, ws, '%%AF:Reversal(Test):sellReversalOI-0(openAroundLastCloseAnd5MinuteChart)')
            return True
        elif((regression_data['forecast_day_VOL_change'] > 35 and 0.75 < regression_data['PCT_day_change'] < 2 and 0.5 < regression_data['PCT_change'] < 2)
            and float(regression_data['contract']) > 20
            ):
            add_in_csv(regression_data, regressionResult, ws, '%%AF:Reversal(Test):sellReversalOI-1(openAroundLastCloseAnd5MinuteChart)')
            return True
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

def buy_af_others(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, True)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, True)
    mlpValue_cla, kNeighboursValue_cla = get_reg_or_cla(regression_data, False)
    mlpValue_other_cla, kNeighboursValue_other_cla = get_reg_or_cla_other(regression_data, False)
    
    if(-1 < regression_data['PCT_day_change'] < 1 and -1.5 < regression_data['PCT_change'] < 1.5
        and (1 < regression_data['PCT_day_change_pre1'] < 5 and 1 < regression_data['PCT_day_change_pre2'] < 5)
        and (regression_data['PCT_day_change_pre1'] > 3
             or (regression_data['PCT_day_change_pre1'] > 2 and regression_data['PCT_day_change_pre2'] > 2)
            )
        #and (regression_data['monthHighChange'] < -10 or regression_data['month3HighChange'] < -15)
        and 0.9 < low_tail_pct(regression_data) <= 2.5 
        and 0.9 < high_tail_pct(regression_data) <= 2.5
        ):
        add_in_csv(regression_data, regressionResult, ws, '%%AF:(Last-Day-Down)buyUptrendContinue(Last-Day-Up)buyDowntrendReverse')
    elif(0 < regression_data['PCT_day_change'] < 1 and -1.5 < regression_data['PCT_change'] < 1.5
        and 2.5 < regression_data['PCT_day_change_pre1'] < 5
        and -5 < regression_data['PCT_day_change_pre2'] < -2.5
        and regression_data['high'] < regression_data['high_pre1']
        and abs(regression_data['monthHighChange']) > abs(regression_data['monthLowChange'])
        and abs(regression_data['week2HighChange']) > abs(regression_data['week2LowChange'])
        and low_tail_pct(regression_data) <= 2.5 
        and high_tail_pct(regression_data) <= 2.5
        ):
        add_in_csv(regression_data, regressionResult, ws, '%%AF:mayBuyStock-DowntrendStart')
                       
#     if(len(regression_data['filter']) > 9
#         and 2 < regression_data['PCT_day_change'] < 4
#         and 2 < regression_data['PCT_change'] < 4
#         and high_tail_pct(regression_data) < 1.3
#         and is_buy_from_filter_all_filter_relaxed(regression_data)
#         and regression_data['SMA25'] > 0
#         ):
#         if(regression_data['PCT_day_change_pre1'] < -1
#             and regression_data['PCT_day_change_pre2'] > 1
#             ):
#             add_in_csv(regression_data, regressionResult, ws, None, 'Filter-Buy-Relaxed-01')
#         elif(-1 < regression_data['PCT_day_change_pre1'] < 1
#             and regression_data['PCT_day_change_pre2'] < -1
#             and regression_data['PCT_day_change_pre3'] < -1
#             ):
#             add_in_csv(regression_data, regressionResult, ws, None, 'Filter-Buy-Relaxed-02')
#         elif(regression_data['PCT_day_change_pre1'] > 1
#             and regression_data['PCT_day_change_pre2'] > 1
#             ):
#             add_in_csv(regression_data, regressionResult, ws, None, None)
#         else:
#             add_in_csv(regression_data, regressionResult, ws, None, None)
#     
#     if('NA$NA:(shortUpTrend)$NA' in regression_data['series_trend']):
#         add_in_csv(regression_data, regressionResult, ws, None, 'shortUpTrend')
                   
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
            and regression_data['PCT_day_change_pre3'] < regression_data['PCT_day_change']
            and (regression_data['PCT_day_change_pre2'] < -1.5 or regression_data['PCT_day_change_pre3'] < -1)
            and regression_data['month3HighChange'] > -10
            and abs(regression_data['year2HighChange']) < abs(regression_data['year2LowChange'])
            ):
            add_in_csv(regression_data, regressionResult, ws, '$$MayBuy-CheckChart(downTrend-mayReverseAtMonth3High)-0')
        elif(-2 < regression_data['PCT_day_change'] < -1
            and -2 < regression_data['PCT_change'] < -1
            and regression_data['PCT_day_change_pre1'] < -1
            and regression_data['PCT_day_change_pre2'] < 0
            and regression_data['PCT_day_change_pre3'] < 0
            and regression_data['monthLow'] >= regression_data['low']
            and (regression_data['forecast_day_PCT7_change'] < -10 or regression_data['forecast_day_PCT10_change'] < -10)
            #and regression_data['PCT_day_change_pre3'] < regression_data['PCT_day_change']
            ):
            add_in_csv(regression_data, regressionResult, ws, '$$MayBuy-CheckChart(downTrend-mayReverseLast4DaysDown)')
        elif(-2 < regression_data['PCT_day_change'] < -1
            and -2 < regression_data['PCT_change'] < -1
            and regression_data['PCT_day_change_pre1'] < -1
            and regression_data['PCT_day_change_pre2'] < 0
            and regression_data['PCT_day_change_pre3'] < 0
            and regression_data['monthLow'] >= regression_data['low']
            #and regression_data['PCT_day_change_pre3'] < regression_data['PCT_day_change']
            ):
            add_in_csv(regression_data, regressionResult, ws, '$$MayBuy-CheckChart(downTrend-mayReverseLast4DaysDown)-Risky')
        elif(-3.5 < regression_data['PCT_day_change'] < -1
            and -3.5 < regression_data['PCT_change'] < -1
            and regression_data['PCT_day_change_pre1'] < -1
            and regression_data['monthLowChange'] < 1
            and regression_data['month3LowChange'] > 1
            and regression_data['yearLowChange'] > 10
            and low_tail_pct(regression_data) < 2.5
            #and regression_data['PCT_day_change_pre3'] < regression_data['PCT_day_change']
            ):
            add_in_csv(regression_data, regressionResult, ws, '$$MayBuy-CheckChart(monthLow-minimumLast2DayDown)')
    
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
            add_in_csv(regression_data, regressionResult, ws, 'MayBuyCheckChart-(|`|_|)')
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
                add_in_csv(regression_data, regressionResult, ws, 'MayBuyCheckChart-(IndexNotUpInSecondHalf)')
                
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
                add_in_csv(regression_data, regressionResult, ws, "ML:MayBuyCheckChart-last3DayDown")
            elif((-2 <= regression_data['PCT_day_change'] < -1) and (-2 <= regression_data['PCT_change'] < 0)
                and 3 > low_tail_pct(regression_data) > 1.8
                ):
                add_in_csv(regression_data, regressionResult, ws, "ML:(check-chart-2-3MidCapCross)MayBuyCheckChart-Risky") 
    elif(('MayBuyCheckChart' in regression_data['filter1'])
        and ('Reversal' not in regression_data['filter3'])
        and high_tail_pct(regression_data) < 0.5
        ):
        if((-5 <= regression_data['PCT_day_change'] < -3) and (-6 <= regression_data['PCT_change'] < -2)
            and 5 > low_tail_pct(regression_data) > 2.8
            ):
            add_in_csv(regression_data, regressionResult, ws, "ML:(Test)MayBuyCheckChart-PCTDayChangeLT(-3)BigHighTail")
            
    if(regression_data['year2LowChange'] > 3
        and regression_data['low'] == regression_data['weekLow']
        and low_tail_pct(regression_data) > 1.5
        and (regression_data['PCT_day_change'] < 2 or is_algo_buy(regression_data))
        ):
        if(regression_data['weekLow'] < regression_data['week2Low']):
            add_in_csv(regression_data, regressionResult, ws, "weekLowLTweek2")
        if(regression_data['monthLowChange'] < 3
            and regression_data['monthLow'] != regression_data['weekLow']
            and regression_data['monthLow'] == regression_data['month2Low']
            #and (is_algo_buy(regression_data)
                #or ((regression_data['bar_low'] - regression_data['month2BarLow'])/regression_data['month2BarLow'])*100 < 1.5
                #or regression_data['PCT_day_change'] > 0
                #)
            ):
            if(regression_data['monthLowChange'] < -5):
                add_in_csv(regression_data, regressionResult, ws, "monthLowChangeLT-5")
            elif(regression_data['monthLowChange'] < -4):
                add_in_csv(regression_data, regressionResult, ws, "monthLowChangeLT-4")
            elif(regression_data['monthLowChange'] < -3):
                add_in_csv(regression_data, regressionResult, ws, "monthLowChangeLT-3")
            elif(regression_data['monthLowChange'] < -2):
                add_in_csv(regression_data, regressionResult, ws, "monthLowChangeLT-2")
            elif(regression_data['monthLowChange'] < -1):
                add_in_csv(regression_data, regressionResult, ws, "monthLowChangeLT-1")
            elif(regression_data['monthLowChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, "monthLowChangeLT0")
            elif(regression_data['monthLowChange'] < 1):
                add_in_csv(regression_data, regressionResult, ws, "monthLowChangeLT1")     
            elif(regression_data['monthLowChange'] < 2):
                add_in_csv(regression_data, regressionResult, ws, "monthLowChangeLT2")
            elif(regression_data['monthLowChange'] < 3):
                add_in_csv(regression_data, regressionResult, ws, "monthLowChangeLT3")     
            add_in_csv(regression_data, regressionResult, ws, "(Test)MayBuyCheckChart-monthLowReversal")
        elif(regression_data['monthLowChange'] < 3
            and regression_data['monthLow'] != regression_data['weekLow']
            ):
            if(regression_data['monthLowChange'] < -5):
                add_in_csv(regression_data, regressionResult, ws, "monthLowChangeLT-5")
            elif(regression_data['monthLowChange'] < -4):
                add_in_csv(regression_data, regressionResult, ws, "monthLowChangeLT-4")
            elif(regression_data['monthLowChange'] < -3):
                add_in_csv(regression_data, regressionResult, ws, "monthLowChangeLT-3")
            elif(regression_data['monthLowChange'] < -2):
                add_in_csv(regression_data, regressionResult, ws, "monthLowChangeLT-2")
            elif(regression_data['monthLowChange'] < -1):
                add_in_csv(regression_data, regressionResult, ws, "monthLowChangeLT-1")
            elif(regression_data['monthLowChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, "monthLowChangeLT0")
            elif(regression_data['monthLowChange'] < 1):
                add_in_csv(regression_data, regressionResult, ws, "monthLowChangeLT1")     
            elif(regression_data['monthLowChange'] < 2):
                add_in_csv(regression_data, regressionResult, ws, "monthLowChangeLT2")
            elif(regression_data['monthLowChange'] < 3):
                add_in_csv(regression_data, regressionResult, ws, "monthLowChangeLT3") 
            add_in_csv(regression_data, regressionResult, ws, "(Test)MayBuyCheckChart-monthLowReversal-risky")
        elif((regression_data['monthLowChange'] < 5 and regression_data['SMA9'] > 0)
            and regression_data['monthLow'] != regression_data['weekLow']
            and regression_data['monthLow'] == regression_data['month2Low']
            ):
            if(regression_data['monthLowChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, "monthLowChangeLT0")
            elif(regression_data['monthLowChange'] < 1):
                add_in_csv(regression_data, regressionResult, ws, "monthLowChangeLT1")     
            elif(regression_data['monthLowChange'] < 2):
                add_in_csv(regression_data, regressionResult, ws, "monthLowChangeLT2")
            elif(regression_data['monthLowChange'] < 3):
                add_in_csv(regression_data, regressionResult, ws, "monthLowChangeLT3")
            elif(regression_data['monthLowChange'] < 4):
                add_in_csv(regression_data, regressionResult, ws, "monthLowChangeLT4")
            elif(regression_data['monthLowChange'] < 5):
                add_in_csv(regression_data, regressionResult, ws, "monthLowChangeLT5") 
            add_in_csv(regression_data, regressionResult, ws, "(Test)MayBuyCheckChart-monthLowReversal-SMA9GT0")
        elif(regression_data['month2LowChange'] < 3
            and regression_data['month2Low'] != regression_data['weekLow']
            and regression_data['month2Low'] == regression_data['month3Low']
            #and (is_algo_buy(regression_data)
                #or ((regression_data['bar_low'] - regression_data['month3BarLow'])/regression_data['month3BarLow'])*100 < 1.5
                #or regression_data['PCT_day_change'] > 0
                #)
            ):
            if(regression_data['month2LowChange'] < -5):
                add_in_csv(regression_data, regressionResult, ws, "month2LowChangeLT-5")
            elif(regression_data['month2LowChange'] < -4):
                add_in_csv(regression_data, regressionResult, ws, "month2LowChangeLT-4")
            elif(regression_data['month2LowChange'] < -3):
                add_in_csv(regression_data, regressionResult, ws, "month2LowChangeLT-3")
            elif(regression_data['month2LowChange'] < -2):
                add_in_csv(regression_data, regressionResult, ws, "month2LowChangeLT-2")
            elif(regression_data['month2LowChange'] < -1):
                add_in_csv(regression_data, regressionResult, ws, "month2LowChangeLT-1")
            elif(regression_data['month2LowChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, "month2LowChangeLT0")
            elif(regression_data['month2LowChange'] < 1):
                add_in_csv(regression_data, regressionResult, ws, "month2LowChangeLT1")     
            elif(regression_data['month2LowChange'] < 2):
                add_in_csv(regression_data, regressionResult, ws, "month2LowChangeLT2")
            elif(regression_data['month2LowChange'] < 3):
                add_in_csv(regression_data, regressionResult, ws, "month2LowChangeLT3") 
            add_in_csv(regression_data, regressionResult, ws, "(Test)MayBuyCheckChart-month2LowReversal")
        elif(regression_data['month2LowChange'] < 3
            and regression_data['month2Low'] != regression_data['weekLow']
            ):
            if(regression_data['month2LowChange'] < -5):
                add_in_csv(regression_data, regressionResult, ws, "month2LowChangeLT-5")
            elif(regression_data['month2LowChange'] < -4):
                add_in_csv(regression_data, regressionResult, ws, "month2LowChangeLT-4")
            elif(regression_data['month2LowChange'] < -3):
                add_in_csv(regression_data, regressionResult, ws, "month2LowChangeLT-3")
            elif(regression_data['month2LowChange'] < -2):
                add_in_csv(regression_data, regressionResult, ws, "month2LowChangeLT-2")
            elif(regression_data['month2LowChange'] < -1):
                add_in_csv(regression_data, regressionResult, ws, "month2LowChangeLT-1")
            elif(regression_data['month2LowChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, "month2LowChangeLT0")
            elif(regression_data['month2LowChange'] < 1):
                add_in_csv(regression_data, regressionResult, ws, "month2LowChangeLT1")     
            elif(regression_data['month2LowChange'] < 2):
                add_in_csv(regression_data, regressionResult, ws, "month2LowChangeLT2")
            elif(regression_data['month2LowChange'] < 3):
                add_in_csv(regression_data, regressionResult, ws, "month2LowChangeLT3") 
            add_in_csv(regression_data, regressionResult, ws, "(Test)MayBuyCheckChart-month2LowReversal-risky")
        elif((regression_data['month2LowChange'] < 5 and regression_data['SMA9'] > 0)
            and regression_data['month2Low'] != regression_data['weekLow']
            and regression_data['month2Low'] == regression_data['month3Low']
            ):
            if(regression_data['month2LowChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, "month2LowChangeLT0")
            elif(regression_data['month2LowChange'] < 1):
                add_in_csv(regression_data, regressionResult, ws, "month2LowChangeLT1")     
            elif(regression_data['month2LowChange'] < 2):
                add_in_csv(regression_data, regressionResult, ws, "month2LowChangeLT2")
            elif(regression_data['month2LowChange'] < 3):
                add_in_csv(regression_data, regressionResult, ws, "month2LowChangeLT3")
            elif(regression_data['month2LowChange'] < 4):
                add_in_csv(regression_data, regressionResult, ws, "month2LowChangeLT4")
            elif(regression_data['month2LowChange'] < 5):
                add_in_csv(regression_data, regressionResult, ws, "month2LowChangeLT5")
            add_in_csv(regression_data, regressionResult, ws, "(Test)MayBuyCheckChart-month2LowReversal-SMA9GT0")
        elif(regression_data['month3LowChange'] < 3
            and regression_data['month3Low'] != regression_data['weekLow']
            #and regression_data['month3Low'] != regression_data['low_month3']
            and regression_data['month6Low'] == regression_data['yearLow']
            ):
            if(regression_data['month3LowChange'] < -5):
                add_in_csv(regression_data, regressionResult, ws, "monthLow3ChangeLT-5")
            elif(regression_data['month3LowChange'] < -4):
                add_in_csv(regression_data, regressionResult, ws, "monthLow3ChangeLT-4")
            elif(regression_data['month3LowChange'] < -3):
                add_in_csv(regression_data, regressionResult, ws, "monthLow3ChangeLT-3")
            elif(regression_data['month3LowChange'] < -2):
                add_in_csv(regression_data, regressionResult, ws, "monthLow3ChangeLT-2")
            elif(regression_data['month3LowChange'] < -1):
                add_in_csv(regression_data, regressionResult, ws, "monthLow3ChangeLT-1")
            elif(regression_data['month3LowChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, "monthLow3ChangeLT0")
            elif(regression_data['month3LowChange'] < 1):
                add_in_csv(regression_data, regressionResult, ws, "monthLow3ChangeLT1")     
            elif(regression_data['month3LowChange'] < 2):
                add_in_csv(regression_data, regressionResult, ws, "monthLow3ChangeLT2")
            elif(regression_data['month3LowChange'] < 3):
                add_in_csv(regression_data, regressionResult, ws, "monthLow3ChangeLT3") 
            add_in_csv(regression_data, regressionResult, ws, "(Test)MayBuyCheckChart-month3LowReversal")
        elif(regression_data['month3LowChange'] < 0
            and regression_data['month3Low'] != regression_data['weekLow']
            and regression_data['month3Low'] == regression_data['month6Low']
            ):
            add_in_csv(regression_data, regressionResult, ws, "(Test)MayBuyCheckChart-month3LowBreakReversal")
        elif(regression_data['month6LowChange'] < 3
            and regression_data['month6Low'] != regression_data['weekLow']
            #and regression_data['month3Low'] != regression_data['low_month6']
            and regression_data['yearLow'] == regression_data['year2Low']
            ):
            if(regression_data['month6LowChange'] < -5):
                add_in_csv(regression_data, regressionResult, ws, "monthLow6ChangeLT-5")
            elif(regression_data['month6LowChange'] < -4):
                add_in_csv(regression_data, regressionResult, ws, "monthLow6ChangeLT-4")
            elif(regression_data['month6LowChange'] < -3):
                add_in_csv(regression_data, regressionResult, ws, "monthLow6ChangeLT-3")
            elif(regression_data['month6LowChange'] < -2):
                add_in_csv(regression_data, regressionResult, ws, "monthLow6ChangeLT-2")
            elif(regression_data['month6LowChange'] < -1):
                add_in_csv(regression_data, regressionResult, ws, "monthLow6ChangeLT-1")
            elif(regression_data['month6LowChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, "monthLow6ChangeLT0")
            elif(regression_data['month6LowChange'] < 1):
                add_in_csv(regression_data, regressionResult, ws, "monthLow6ChangeLT1")     
            elif(regression_data['month6LowChange'] < 2):
                add_in_csv(regression_data, regressionResult, ws, "monthLow6ChangeLT2")
            elif(regression_data['month6LowChange'] < 3):
                add_in_csv(regression_data, regressionResult, ws, "monthLow6ChangeLT3") 
            add_in_csv(regression_data, regressionResult, ws, "(Test)MayBuyCheckChart-month6LowReversal")
        elif(regression_data['month6LowChange'] < 0
            and regression_data['month6Low'] != regression_data['weekLow']
            and regression_data['month6Low'] == regression_data['yearLow']
            ):
            add_in_csv(regression_data, regressionResult, ws, "(Test)MayBuyCheckChart-month6LowBreakReversal")
                          
def buy_year_high(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(float(regression_data['forecast_day_VOL_change']) > 70
       and regression_data['PCT_day_change_pre1'] > -0.5
       and no_doji_or_spinning_buy_india(regression_data)
       ):
        if(-15 < regression_data['yearHighChange'] < -5 and regression_data['yearLowChange'] > 30
            and -0.5 < regression_data['PCT_day_change'] < 2 and regression_data['forecast_day_PCT2_change'] <= 2
            ):
            add_in_csv(regression_data, regressionResult, ws, 'buyYearHigh-0')
            return True
    elif(float(regression_data['forecast_day_VOL_change']) > 35
       and regression_data['PCT_day_change_pre1'] > -0.5
       and no_doji_or_spinning_buy_india(regression_data)
       ):
        if(-15 < regression_data['yearHighChange'] < -5 and regression_data['yearLowChange'] > 30
            and -0.5 < regression_data['PCT_day_change'] < 2 and regression_data['forecast_day_PCT2_change'] <= 2
            ):
            add_in_csv(regression_data, regressionResult, ws, 'buyYearHigh-1')
            return True
    elif(float(regression_data['forecast_day_VOL_change']) > 50
       and regression_data['PCT_day_change_pre1'] > -0.5
       and no_doji_or_spinning_buy_india(regression_data)
       ):
        if(-5 <= regression_data['yearHighChange'] < -1 and regression_data['yearLowChange'] > 15 
            and -0.5 < regression_data['PCT_day_change'] < 2 and regression_data['forecast_day_PCT2_change'] <= 2
            ):
            add_in_csv(regression_data, regressionResult, ws, 'buyYearHigh-2')
            return True
    elif(regression_data['PCT_day_change_pre1'] > -0.5):
        if(-5 <= regression_data['yearHighChange'] < -1 and regression_data['yearLowChange'] > 15 
            and -0.5 < regression_data['PCT_day_change'] < 2 and regression_data['forecast_day_PCT2_change'] <= 2
            ):
            add_in_csv(regression_data, regressionResult, ws, 'buyYearHigh-3')
            return True
    return False

def buy_year_low(regression_data, regressionResult, reg, ws, ws1):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if((-1.5 < regression_data['PCT_day_change'] < 0) and (-2 < regression_data['PCT_change'] < 0)
        and regression_data['year2HighChange'] < -50
        and regression_data['yearHighChange'] < -30
        and regression_data['month3LowChange'] > 10
        and regression_data['monthLowChange'] > 10
        and 0 < regression_data['SMA4'] < 10
        and 2 < regression_data['SMA9'] < 10
        ):   
        add_in_csv(regression_data, regressionResult, ws, 'buyYear2LowMovingSMA')
        return True
    elif(1 < regression_data['yearLowChange'] < 5 and regression_data['yearHighChange'] < -30 
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
        if('NearLowYear2' in regression_data['filter3']):
            add_in_csv(regression_data, regressionResult, ws, 'NearLowYear2')
        elif('BreakLowYear2' in regression_data['filter3']):
            add_in_csv(regression_data, regressionResult, ws, 'BreakLowYear2')
        add_in_csv(regression_data, regressionResult, ws, 'buyYear2Low')
        return True
    elif(regression_data['forecast_day_PCT10_change'] < -10
        and regression_data['year2HighChange'] < -60
        and regression_data['month3LowChange'] < 10
        and -1.5 < regression_data['forecast_day_PCT_change']
        and 3 < regression_data['PCT_day_change'] < 7
        and 2 < regression_data['PCT_change'] < 8
        and (regression_data['PCT_day_change_pre1'] < -4 or regression_data['PCT_day_change_pre2'] < -4)
        ):
        add_in_csv(regression_data, regressionResult, ws, 'sellYear2LowContinue')
        return True
    if(all_day_pct_change_negative_except_today(regression_data) 
        and (regression_data['high'] > regression_data['high_pre1'])
        and 0 < regression_data['PCT_day_change'] < 4.5 and 0 < regression_data['PCT_change']
        and ( 2 < regression_data['PCT_day_change'] or 2 < regression_data['PCT_change'])
        and regression_data['yearHighChange'] < -15 
        and (high_tail_pct(regression_data) < 0.5 
             or (low_tail_pct(regression_data) > high_tail_pct(regression_data) and low_tail_pct(regression_data) > 1 
                 and -2 < regression_data['PCT_day_change'] < 2 and -2 < regression_data['PCT_day_change_pre1'] < 2)
             or (high_tail_pct(regression_data) > 2.5 and regression_data['PCT_day_change'] > high_tail_pct(regression_data))
             )
        ):
        if(ten_days_less_than_minus_ten(regression_data)
            and regression_data['forecast_day_PCT7_change'] < -5
            and regression_data['forecast_day_PCT10_change'] < -10
            and (low_tail_pct(regression_data) > high_tail_pct(regression_data) and low_tail_pct(regression_data) > 1)
            ):
            add_in_csv(regression_data, regressionResult, ws, 'buyDownTrend-lowTail')
            return True
        elif(ten_days_less_than_minus_ten(regression_data)
            and regression_data['forecast_day_PCT7_change'] < -5
            and regression_data['forecast_day_PCT10_change'] < -10
            and (high_tail_pct(regression_data) > 2.5)
            ):
            add_in_csv(regression_data, regressionResult, ws, 'buyDownTrend-highTail')
            return True
        elif(last_5_day_all_down_except_today(regression_data)
            and ten_days_less_than_minus_ten(regression_data)
            and regression_data['forecast_day_PCT7_change'] < -5
            and regression_data['forecast_day_PCT10_change'] < -10
            ):
            add_in_csv(regression_data, regressionResult, ws, 'buyDownTrend-Risky-0')
            return True
        elif(last_5_day_all_down_except_today(regression_data)
            and ten_days_less_than_minus_seven(regression_data)
            and regression_data['forecast_day_PCT7_change'] < -4
            and regression_data['forecast_day_PCT10_change'] < -4
            ):
            add_in_csv(regression_data, regressionResult, ws, 'buyDownTrend-Risky-1')
            return True
        elif(regression_data['forecast_day_PCT7_change'] < -4
            and regression_data['forecast_day_PCT10_change'] < -4
            ):
            add_in_csv(regression_data, regressionResult, ws, 'buyDownTrend-Risky-2')
            return True
    
    if(ten_days_less_than_minus_ten(regression_data)
        and regression_data['forecast_day_PCT2_change'] < 0
        and regression_data['forecast_day_PCT3_change'] < 0
        and regression_data['forecast_day_PCT5_change'] < 0
        and regression_data['forecast_day_PCT7_change'] < 0
        and regression_data['forecast_day_PCT7_change'] < 0
        and 2 < regression_data['PCT_day_change'] < 5
        and 2 < regression_data['PCT_change'] < 5
        and regression_data['PCT_day_change_pre2'] < 0
        and regression_data['PCT_day_change_pre3'] < 0
        ):
        add_in_csv(regression_data, regressionResult, ws, '##buyTenDaysLessThanMinusTen')
        return True
        
    return False

def buy_up_trend(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    if(('NearLow' in regression_data['filter3'] or 'ReversalLow' in regression_data['filter3'])
        and 'GT0' not in regression_data['filter3']
        and regression_data['SMA4'] > 0
        and regression_data['SMA4_2daysBack'] > 0
        and regression_data['PCT_day_change'] > 0.5 and regression_data['PCT_change'] > 0
        #and (regression_data['PCT_day_change_pre2'] > 0 or regression_data['PCT_day_change_pre3'] > 0)
        and (regression_data['PCT_day_change_pre1'] < 0 or regression_data['PCT_day_change_pre2'] < 0)
        ):
        if(regression_data['SMA4'] > regression_data['SMA4_2daysBack']
            and regression_data['SMA9'] > regression_data['SMA9_2daysBack']
            ):
            add_in_csv(regression_data, regressionResult, None, 'buyUpTrend-nearLow')
            return True
        else:
            add_in_csv(regression_data, regressionResult, None, 'buyUpTrend-Risky-nearLow')
            return True
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

def buy_final(regression_data, regressionResult, reg, ws, ws1):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(regression_data['yearHighChange'] < -10 
        and regression_data['yearLowChange'] > 5
        and regression_data['month3LowChange'] > 3
        and 4 > regression_data['PCT_day_change'] > 1 and 4 > regression_data['PCT_change'] > 1
        #and abs(regression_data['PCT_day_CH']) < 0.3
        #and regression_data['forecast_day_VOL_change'] > 0
        and high_tail_pct(regression_data) < 1
        #and str(regression_data['score']) != '0-1'
        ):   
        if(-90 < regression_data['yearHighChange'] < -10
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
            return True
        elif(-90 < regression_data['yearHighChange'] < -10
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
            add_in_csv(regression_data, regressionResult, ws, 'buyMorningStar-HighLowerTail')
            return True
        elif(-6 < regression_data['PCT_day_change'] < 0 and -6 < regression_data['PCT_change'] < 0
            and (regression_data['bar_low'] - regression_data['low']) >= ((regression_data['bar_high'] - regression_data['bar_low']) * 3)
            ):
            add_in_csv(regression_data, regressionResult, ws, 'buyMorningStar-HighLowerTail-(checkChart)')
        elif(-6 < regression_data['PCT_day_change'] < 2 and -6 < regression_data['PCT_change'] < 2
            and regression_data['PCT_day_change_pre1'] < 0
            and regression_data['PCT_day_change_pre2'] < 0
            and regression_data['PCT_day_change_pre3'] < 0
            and (regression_data['bar_low'] - regression_data['low']) >= ((regression_data['bar_high'] - regression_data['bar_low']) * 2)
            ):
            add_in_csv(regression_data, regressionResult, ws, 'buyMorningStar-(checkChart)')
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
        if(high_tail_pct(regression_data) < 1.5
           and low_tail_pct(regression_data) > 2
           ):
            if(-1.5 < regression_data['PCT_day_change'] < 0 and -1.5 < regression_data['PCT_change'] < 0
                and (regression_data['close'] - regression_data['low']) >= ((regression_data['open'] - regression_data['close']) * 3)
                and (regression_data['close'] - regression_data['low']) >= ((regression_data['high'] - regression_data['open']) * 3)
                ):
                add_in_csv(regression_data, regressionResult, ws, '##TEST:buyMorningStar-3(Check2-3MidCapCross)')
                return True
            if(0 < regression_data['PCT_day_change'] < 1
                and (regression_data['open'] - regression_data['low']) >= ((regression_data['open'] - regression_data['close']) * 3)
                and (regression_data['open'] - regression_data['low']) >= ((regression_data['high'] - regression_data['close']) * 3)
                ):
                add_in_csv(regression_data, regressionResult, ws, '##TEST:buyMorningStar-4(Check2-3MidCapCross)')
                return True
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
    
    if((regression_data['PCT_day_change'] < 2 and low_tail_pct(regression_data) > 4)
        #and regression_data['PCT_change'] <= 0
        and -75 < regression_data['year2HighChange'] < -25
        and low_tail_pct(regression_data) < 1
        and ('MayBuyCheckChart' in regression_data['filter1']) 
        and ('Reversal' not in regression_data['filter3'])
        ):
        add_in_csv(regression_data, regressionResult, ws, "Test:MayBuyCheckChart-HighTail(Check2-3MidCapCross)")
        return True
     
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
    flag = False
    if(NIFTY_LOW and low_tail_pct(regression_data) > 1.5
       and -1 < regression_data['PCT_change'] < 1 and -1 < regression_data['PCT_day_change'] < 1
       and regression_data['forecast_day_PCT10_change'] < 10
       ):
        add_in_csv(regression_data, regressionResult, ws, None, '##TEST:buyCheckLastHourUp')
        flag = True
        if(2 < regression_data['month3LowChange'] < 10):
            if(ten_days_less_than_minus_ten(regression_data)
               and regression_data['forecast_day_PCT10_change'] < -15
               and 5 > regression_data['PCT_day_change'] > 1 and 5 > regression_data['PCT_day_change'] > 1
               #and regression_data['forecast_day_VOL_change'] > 50
               and abs_yearHigh_more_than_yearLow(regression_data) == True
               ):
                add_in_csv(regression_data, regressionResult, ws, '##BreakOutBuyCandidate(notUpLastDay)-1')
                flag = True
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
        and (abs_month6High_more_than_month6Low(regression_data))
        ):
        add_in_csv(regression_data, regressionResult, ws, 'buy-2week-breakoutup')
        flag = True
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
        and (abs_month6High_more_than_month6Low(regression_data))
        ):
        add_in_csv(regression_data, regressionResult, ws, 'sell-2week-breakoutup')
        flag = True
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
            flag = True
        elif(is_algo_sell(regression_data)):
            add_in_csv(regression_data, regressionResult, ws, '(check-chart):ML:sell-2week-breakoutup')
            flag = True
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
        flag = True
            
    if(regression_data['yearLowChange'] < 5):
       if(regression_data['forecast_day_PCT_change'] > 3 and regression_data['PCT_day_change'] > 3
           and abs(regression_data['PCT_day_change']) > abs(regression_data['PCT_day_change_pre1'])
           #and regression_data['open'] == regression_data['low']
           and regression_data['forecast_day_VOL_change'] >= -20
           and high_tail_pct(regression_data) < 0.5
           ):
               add_in_csv(regression_data, regressionResult, ws, '##finalBreakOutBuy-1test-atYearLow')
               flag = True
    if(5 < regression_data['yearLowChange'] < 10 and abs_yearHigh_more_than_yearLow(regression_data)
       and regression_data['forecast_day_PCT10_change'] < 10
       and last_7_day_all_up(regression_data) == False
       and high_tail_pct(regression_data) < 0.7
       ):
       if(3 > regression_data['forecast_day_PCT_change'] > 2 and 3 > regression_data['PCT_day_change'] > 2
           and regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change_pre2'] > 0 and regression_data['PCT_day_change_pre3'] > 0
           and (regression_data['open'] == regression_data['low'] or regression_data['forecast_day_VOL_change'] >= 0)
           and regression_data['forecast_day_VOL_change'] >= -50
           ):
               add_in_csv(regression_data, regressionResult, ws, '##finalBreakOutBuyContinue-00-test-atYearLow')
               flag = True
       if(2 > regression_data['forecast_day_PCT_change'] > 0 and 2 > regression_data['PCT_day_change'] > 0
           and regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change_pre2'] > 0 and regression_data['PCT_day_change_pre3'] > 0
           and (regression_data['forecast_day_PCT_change'] > 0.75 or regression_data['PCT_day_change_pre1'] > 0.75 or regression_data['PCT_day_change_pre2'] > 0.75 or regression_data['PCT_day_change_pre3'] > 0.75)
           and (regression_data['open'] == regression_data['low'] or regression_data['forecast_day_VOL_change'] >= 0)
           and regression_data['forecast_day_VOL_change'] >= -50
           ):
               add_in_csv(regression_data, regressionResult, ws, '##finalBreakOutBuyContinue-0-test-atYearLow')
               flag = True
    if(5 < regression_data['yearLowChange'] < 12 and abs_yearHigh_more_than_yearLow(regression_data)
       and regression_data['forecast_day_PCT10_change'] < 10
       and last_7_day_all_up(regression_data) == False
       and high_tail_pct(regression_data) < 0.7
       ):
       if(3 > regression_data['forecast_day_PCT_change'] > 2 and 3 > regression_data['PCT_day_change'] > 2
           and regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change_pre2'] > 0 and regression_data['PCT_day_change_pre3'] > 0
           #and regression_data['open'] == regression_data['low']
           and regression_data['forecast_day_VOL_change'] >= 0
           ):
               add_in_csv(regression_data, regressionResult, ws, '##finalBreakOutBuyContinue-11-test-atYearLow')
               flag = True
       if(2 > regression_data['forecast_day_PCT_change'] > 0 and 2 > regression_data['PCT_day_change'] > 0
           and regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change_pre2'] > 0 and regression_data['PCT_day_change_pre3'] > 0
           and (regression_data['forecast_day_PCT_change'] > 0.75 or regression_data['PCT_day_change_pre1'] > 0.75 or regression_data['PCT_day_change_pre2'] > 0.75 or regression_data['PCT_day_change_pre3'] > 0.75)
           #and regression_data['open'] == regression_data['low']
           and regression_data['forecast_day_VOL_change'] >= 0
           ):
               add_in_csv(regression_data, regressionResult, ws, '##finalBreakOutBuyContinue-1-test-atYearLow')
               flag = True
    if(regression_data['SMA200'] == 1
       and regression_data['PCT_day_change'] > 2 and regression_data['PCT_change'] > 2
       ):
        add_in_csv(regression_data, regressionResult, ws, '##TestBreakOutBuyConsolidate-0')
        flag = True
    return flag   

def buy_consolidation_breakout(regression_data, regressionResult, reg, ws):
    week2BarHighChange = ((regression_data['bar_high'] - regression_data['week2BarHigh'])/regression_data['bar_high'])*100
    if(0 < regression_data['PCT_day_change'] < 6
        and regression_data['PCT_change'] < 6
        and (regression_data['PCT_day_change_pre1'] < 2 
             or regression_data['PCT_day_change_pre1'] < regression_data['PCT_day_change']
            )
        and (regression_data['PCT_day_change_pre1'] < 0 
             or regression_data['PCT_day_change_pre2'] < 0
             or regression_data['PCT_day_change_pre3'] < 0
            )
        #and regression_data['high'] > regression_data['high_pre3']
        and regression_data['high'] > regression_data['high_pre2']
        and regression_data['high'] > regression_data['high_pre1']
        and 0.5 < regression_data['forecast_day_PCT4_change'] < 3
        and 0 < regression_data['forecast_day_PCT3_change'] < 4
        and 0 < regression_data['forecast_day_PCT2_change'] < 4
        and 0 < regression_data['forecast_day_PCT_change'] < 3
        and 0 <= regression_data['forecast_day_PCT10_change'] <= 3
        and regression_data['bar_high'] >= regression_data['week2BarHigh']
        ):
        if(regression_data['weekBarHigh'] > regression_data['bar_high_pre1'] 
            and regression_data['week2BarHigh'] > regression_data['bar_high_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, 'brokenToday')
        if(regression_data['weekHigh'] > regression_data['week2High']):
            add_in_csv(regression_data, regressionResult, ws, 'weekHighGTweek2High')
        if(week2BarHighChange > 5):
            add_in_csv(regression_data, regressionResult, ws, 'week2BarHighChangeGT5')
        elif(week2BarHighChange > 4):
            add_in_csv(regression_data, regressionResult, ws, 'week2BarHighChangeGT4')
        elif(week2BarHighChange > 3):
            add_in_csv(regression_data, regressionResult, ws, 'week2BarHighChangeGT3')
        elif(week2BarHighChange > 2):
            add_in_csv(regression_data, regressionResult, ws, 'week2BarHighChangeGT2')
        elif(week2BarHighChange > 1):
            add_in_csv(regression_data, regressionResult, ws, 'week2BarHighChangeGT1')
        elif(week2BarHighChange > 0):
            add_in_csv(regression_data, regressionResult, ws, 'week2BarHighChangeGT0')
        if(regression_data['PCT_day_change'] > 1
            and regression_data['year2HighChange'] < -5
            ):
            add_in_csv(regression_data, regressionResult, ws, '(Test)checkConsolidationBreakUp-2week')
        elif(regression_data['PCT_day_change'] < 1
            and regression_data['year2HighChange'] < -5
            ):
            add_in_csv(regression_data, regressionResult, ws, '(Test)checkConsolidationBreakUp-2week-(Risky)-PCTDayChangeLT1')
        elif(regression_data['year2HighChange'] >= -5):
            add_in_csv(regression_data, regressionResult, ws, '(Test)checkConsolidationBreakUp-2week-(Risky)-year2High')
            
    elif(1.5 < regression_data['PCT_day_change'] < 6
        and regression_data['PCT_change'] < 6
        and (regression_data['PCT_day_change_pre1'] < 0 or regression_data['PCT_day_change_pre2'] < 0)
        #and regression_data['high'] > regression_data['high_pre3']
        and regression_data['high'] > regression_data['high_pre2']
        and regression_data['high'] > regression_data['high_pre1']
        and 0.5 < regression_data['forecast_day_PCT4_change'] < 3
        and 0 < regression_data['forecast_day_PCT3_change'] < 4
        and 0 < regression_data['forecast_day_PCT2_change'] < 4
        and 0 < regression_data['forecast_day_PCT_change'] < 3
        and ((abs_monthHigh_less_than_monthLow(regression_data))
            )
        and regression_data['SMA4'] > regression_data['SMA4_2daysBack']
        ):
        add_in_csv(regression_data, regressionResult, ws, '(Test)checkConsolidationBreakUp-month3HighLTMonth3Low')
    elif(1.5 < regression_data['PCT_day_change'] < 6
        and regression_data['PCT_change'] < 6
        and (regression_data['PCT_day_change_pre1'] < 0 or regression_data['PCT_day_change_pre2'] < 0)
        #and regression_data['high'] > regression_data['high_pre3']
        and regression_data['high'] > regression_data['high_pre2']
        and regression_data['high'] > regression_data['high_pre1']
        and 0.5 < regression_data['forecast_day_PCT4_change'] < 3
        and 0 < regression_data['forecast_day_PCT3_change'] < 4
        and 0 < regression_data['forecast_day_PCT2_change'] < 4
        and 0 < regression_data['forecast_day_PCT_change'] < 3
        and ((0 < regression_data['forecast_day_PCT5_change'] < 4
                and 0 < regression_data['forecast_day_PCT7_change'] < 4
               )
            )
        and regression_data['SMA4'] > regression_data['SMA4_2daysBack']
        ):
        add_in_csv(regression_data, regressionResult, ws, '(Test)checkConsolidationBreakUp-forecastDayPCT7changeGT0')
     
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

def buy_market_uptrend(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
#    return False
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
            return True
        if(('ReversalLowYear' in regression_data['filter3']) and (regression_data['yearHighChange'] < -30)):
            add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyYearLowReversal(Confirm)')
            return True
        if(('ReversalLowMonth6' in regression_data['filter3']) and (regression_data['month6HighChange'] < -25)):
            add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyMonth6LowReversal(Confirm)')
            return True
        if(('ReversalLowMonth3' in regression_data['filter3']) and (regression_data['month3HighChange'] < -15)):
            add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyMonth3LowReversal(Confirm)')
            return True
        if(regression_data['month3HighChange'] < -20 and (regression_data['month6HighChange'] < -20 or regression_data['yearHighChange'] < -30)
            ):
            if(('NearLowYear2' in regression_data['filter3']) and (regression_data['year2HighChange'] < -40)):
                add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyYear2Low')
                return True
            if(('NearLowYear' in regression_data['filter3']) and (regression_data['yearHighChange'] < -30)):
                add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyYearLow')
                return True
            if(('NearLowMonth6' in regression_data['filter3']) and (regression_data['month6HighChange'] < -25)):
                add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyMonth6Low')
                return True
            if(('NearLowMonth3' in regression_data['filter3']) and (regression_data['month3HighChange'] < -20)):
                add_in_csv(regression_data, regressionResult, ws, '##UPTREND:buyMonth3Low')
                return True

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
            if('NearHighMonth3' in regression_data['filter3']):
                add_in_csv(regression_data, regressionResult, ws, 'NearHighMonth3')
            elif('ReversalHighMonth3' in regression_data['filter3']):
                add_in_csv(regression_data, regressionResult, ws, 'ReversalHighMonth3')
            elif('BreakHighMonth3' in regression_data['filter3']):
                add_in_csv(regression_data, regressionResult, ws, 'BreakHighMonth3')
            add_in_csv(regression_data, regressionResult, ws, '##(Check-chart-buy):month3High-InMinus')
            
    elif(('NearHighMonth6' in regression_data['filter3']) 
        or ('ReversalHighMonth6' in regression_data['filter3'])
        ):
        if(regression_data['month6LowChange'] > 20
            and ((-5 < regression_data['PCT_change'] < -1) and (-5 < regression_data['PCT_day_change'] < -2))
            and regression_data['close'] < regression_data['bar_low_pre1']
            and regression_data['close'] < regression_data['bar_low_pre2']
            ):
            if('NearHighMonth6' in regression_data['filter3']):
                add_in_csv(regression_data, regressionResult, ws, 'NearHighMonth6')
            elif('ReversalHighMonth6' in regression_data['filter3']):
                add_in_csv(regression_data, regressionResult, ws, 'ReversalHighMonth6')
            add_in_csv(regression_data, regressionResult, ws, '##(Check-chart-buy):month6High-InMinus')
            
    elif(('NearHighYear' in regression_data['filter3']) 
        or ('ReversalHighYear' in regression_data['filter3'])
        ):
        if(regression_data['month6LowChange'] > 20
            and ((-5 < regression_data['PCT_change'] < -1) and (-5 < regression_data['PCT_day_change'] < -2))
            and regression_data['close'] < regression_data['bar_low_pre1']
            and regression_data['close'] < regression_data['bar_low_pre2']
            ):
            if('NearHighYear' in regression_data['filter3']):
                add_in_csv(regression_data, regressionResult, ws, 'NearHighYear')
            elif('ReversalHighYear' in regression_data['filter3']):
                add_in_csv(regression_data, regressionResult, ws, 'ReversalHighYear')
            add_in_csv(regression_data, regressionResult, ws, '##(Check-chart-buy):YearHigh-InMinus')
        
        if((('NearHighYear2' in regression_data['filter3']) 
            or ('ReversalHighYear2' in regression_data['filter3'])
            or ('BreakHighYear2' in regression_data['filter3'])
            )):    
            if(regression_data['year2LowChange'] > 50
                and regression_data['year2HighChange'] > -1
                and ((regression_data['PCT_change'] > 1) and (regression_data['PCT_day_change'] > 1))
                and regression_data['close'] > regression_data['bar_high_pre1']
                ):
                if(regression_data['PCT_change'] > 4
                    and ('BreakHighYear2' in regression_data['filter3'])
                    ):
                    add_in_csv(regression_data, regressionResult, ws, '##(Check-chart-sell):year2High-InPlus')
                else:
                    add_in_csv(regression_data, regressionResult, ws, '##(Check-chart):year2High-InPlus')
                     
        elif((('NearHighYear' in regression_data['filter3'])
            or ('ReversalHighYear' in regression_data['filter3'])
            or ('BreakHighYear' in regression_data['filter3'])
            )):
            if(regression_data['yearLowChange'] > 40
                and regression_data['yearHighChange'] > -1
                and ((regression_data['PCT_change'] > 1) and (regression_data['PCT_day_change'] > 1))
                and regression_data['close'] > regression_data['bar_high_pre1']
                ):
                if(regression_data['PCT_change'] > 4
                    and ('BreakHighYear' in regression_data['filter3'])
                    ):
                    add_in_csv(regression_data, regressionResult, ws, '##(Check-chart-sell):yearHigh-InPlus')
                else:
                    add_in_csv(regression_data, regressionResult, ws, '##(Check-chart):yearHigh-InPlus')
    
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
                 or ( ("downTrend" in regression_data['series_trend']) and (1.5 < regression_data['PCT_change'] < 3) and (1.5 < regression_data['PCT_day_change'] < 3)))
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
    if( ("upTrend" in regression_data['series_trend'])
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
            and -0.75 < regression_data['PCT_day_change_pre1'] < 5
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
#             if(regression_data['high_month6'] >= regression_data['high']):
#                 add_in_csv(regression_data, regressionResult, ws, 'MoreThanM6High')
#             else:
#                 add_in_csv(regression_data, regressionResult, ws, 'LessThanM6High')
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
            and -0.75 < regression_data['PCT_day_change_pre1'] < 5
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
    
#     if(is_algo_buy(regression_data)
#         and regression_data['SMA4'] > 0
#         and regression_data['SMA9'] > 0
#         and regression_data['SMA25'] > 0
#         and regression_data['SMA100'] > 10
#         and regression_data['SMA200'] > 10
#         and regression_data['year2HighChange'] < -5
#         and regression_data['yearHighChange'] < -5
#         and (regression_data['PCT_day_change_pre1'] < 0.5
#              or -0.5 < regression_data['PCT_day_change'] < 0.5)
#         ):
#         if(regression_data['PCT_change'] < -4.5
#             and regression_data['PCT_day_change'] < -4.5):
#             add_in_csv(regression_data, regressionResult, ws, '(Test)ML:AllMAPositive_Uptrend_(LT-4.5)')
#         elif(-5 < regression_data['PCT_change'] < -2
#             and -5 < regression_data['PCT_day_change'] < -2):
#             add_in_csv(regression_data, regressionResult, ws, '(Test)ML:AllMAPositive_Uptrend_(LT-2)')
#         elif(-5 < regression_data['PCT_change'] < 0
#             and -5 < regression_data['PCT_day_change'] < 0):
#             add_in_csv(regression_data, regressionResult, ws, '(Test)ML:AllMAPositive_Uptrend_(LT0)')
#         elif(-1 < regression_data['PCT_change'] < 1
#             and -1 < regression_data['PCT_day_change'] < 1):
#             add_in_csv(regression_data, regressionResult, ws, '(Test)ML:AllMAPositive_Uptrend_(BT+1-1)')
#         elif(0 < regression_data['PCT_change'] < 2
#             and 0 < regression_data['PCT_day_change'] < 2):
#             add_in_csv(regression_data, regressionResult, ws, '(Test)ML:AllMAPositive_Uptrend_(GT0)')
#         elif(0 < regression_data['PCT_change'] < 5
#             and 0 < regression_data['PCT_day_change'] < 5):
#             add_in_csv(regression_data, regressionResult, ws, '(Test)ML:AllMAPositive_Uptrend_(GT+2)')
#         elif(regression_data['PCT_change'] > 4.5
#             and regression_data['PCT_day_change'] > 4.5):
#             add_in_csv(regression_data, regressionResult, ws, '(Test)ML:AllMAPositive_Uptrend_(GT+4.5)')
#         else:
#             add_in_csv(regression_data, regressionResult, ws, '(Test)ML:AllMAPositive_Uptrend')
    
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
            and  ("upTrend" in regression_data['series_trend'])
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
#     if(('UP-1' in regression_data['filter5'])
#        ):
#         add_in_csv(regression_data, regressionResult, ws,"buy-1-UP")
#         return True
#     elif(('UP-2' in regression_data['filter5'])
#        ):
#         add_in_csv(regression_data, regressionResult, ws, None)
#         return True
#     elif(('UP' in regression_data['filter5'])
#        ):
#         if((-2 < regression_data['SMA9'] < 0 or -2 < regression_data['SMA25'] < 0)
#             and regression_data['SMA100'] < -10
#             and regression_data['SMA200'] < -10
#             and regression_data['year2HighChange'] < -50
#             and regression_data['year2LowChange'] > 8
#             ):
#             add_in_csv(regression_data, regressionResult, ws, '(Test)sell-UP')
#         elif((1 < regression_data['SMA9'] < 3 or 1 < regression_data['SMA25'] < 3)
#             and regression_data['SMA100'] < -10
#             and regression_data['SMA200'] < -10
#             and regression_data['year2LowChange'] > 8
#             ):
#             add_in_csv(regression_data, regressionResult, ws, '(Test)sell-UP')
#         elif((1 < regression_data['SMA9'] < 3 or 1 < regression_data['SMA25'] < 3)
#             and regression_data['SMA100'] < -10
#             and regression_data['SMA200'] < -10
#             and regression_data['year2LowChange'] < 8
#             ):
#             add_in_csv(regression_data, regressionResult, ws, '(Test)buy-UP')
#         return True
#     elif(2.5 < regression_data['PCT_day_change'] < 7
#        and 3 < regression_data['PCT_change'] < 7
#        and regression_data['forecast_day_PCT_change'] > 0
#        and regression_data['forecast_day_PCT2_change'] > 0
#        and regression_data['PCT_day_change_pre1'] < 0.75
#        and regression_data['PCT_day_change_pre2'] < 0.5
#        and regression_data['PCT_day_change_pre3'] < 0
#        and high_tail_pct(regression_data) < 1
#        and low_tail_pct(regression_data) < 1
#        #and low_tail_pct_pre1(regression_data) < 1
#        and regression_data['year2HighChange'] < -5
#        and regression_data['year2LowChange'] > 15
#        and (('P@' not in regression_data['buyIndia']) or (regression_data['forecast_day_PCT10_change'] > 4))
#        ):
#         add_in_csv(regression_data, regressionResult, ws, "sell-UP")
#         return True
#     elif(('DOWN-2' in regression_data['filter5'])
#        ):
#         add_in_csv(regression_data, regressionResult, ws, None)
#     elif(('DOWN-1' in regression_data['filter5'])
#        ):
#         add_in_csv(regression_data, regressionResult, ws, None)
#     elif(('DOWN' in regression_data['filter5'])
#        ):
#         add_in_csv(regression_data, regressionResult, ws, None)
#         
#     
#     
    if(('EMA6-LT-May-MT-EMA14' in regression_data['filter4'])
        and 2.5 < regression_data['PCT_day_change'] < 4
        and 0 < regression_data['PCT_change'] < 4.5
        and regression_data['PCT_day_change_pre1'] > 0
        and (regression_data['PCT_day_change'] > 3 or regression_data['PCT_change'] > 3)
        and high_tail_pct(regression_data) < 1
        ):
        add_in_csv(regression_data, regressionResult, ws, '(check-chart)mayBuy-EMA6-LT-May-MT-EMA14')
    elif(('EMA6-MT-May-LT-EMA14' in regression_data['filter4'])
        and -4 < regression_data['PCT_day_change'] < -2.5
        and -4.5 < regression_data['PCT_change'] < 0
        and regression_data['PCT_day_change_pre1'] < 0
        and (regression_data['PCT_day_change'] < -3 or regression_data['PCT_change'] < -3)
        and low_tail_pct(regression_data) < 1
        ):
        add_in_csv(regression_data, regressionResult, ws, '(check-chart)maySell-EMA6-MT-May-LT-EMA14')
        
        
    if(('(Confirmed)EMA6>EMA14' in regression_data['filter4'])
        and 3 < regression_data['PCT_day_change'] 
        and 0 < regression_data['PCT_change']
        and regression_data['PCT_day_change_pre1'] < -1
        and (regression_data['PCT_day_change'] > 3 or regression_data['PCT_change'] > 3)
        ):
        if(regression_data['month3HighChange'] < 10):
            add_in_csv(regression_data, regressionResult, ws, '(check-chart)sellEMA6>EMA14')
        elif(regression_data['PCT_day_change'] > 3.5 or regression_data['PCT_change'] > 3.5):
            add_in_csv(regression_data, regressionResult, ws, '(check-chart)sellEMA6>EMA14-Risky')
    
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
        and regression_data['forecast_day_PCT5_change'] > -5
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
            )
        )
        and high_tail_pct(regression_data) > 1
        and (low_tail_pct(regression_data) < 1.5)
        ):  
        add_in_csv(regression_data, regressionResult, ws, "##(Test)(check-chart)-sellSMADownTrend") 
    elif((regression_data['SMA9'] < 0 or regression_data['SMA25'] < 0)
        and 0 < regression_data['weekHighChange'] < 0.5
        and regression_data['close'] < regression_data['high_week']
        and regression_data['forecast_day_PCT_change'] > 0
        and regression_data['forecast_day_PCT2_change'] > 0
        and (regression_data['forecast_day_PCT5_change'] < 0
            or regression_data['forecast_day_PCT7_change'] < 0
            ) 
        and regression_data['forecast_day_PCT10_change'] < 0
        and ((0 < regression_data['PCT_day_change'] > 1
            and regression_data['PCT_day_change_pre1'] > 1
            and (
                regression_data['PCT_day_change_pre2'] < 0
                or regression_data['PCT_day_change_pre3'] < 0
                )
            )
        )
        and high_tail_pct(regression_data) > 1 
        and (low_tail_pct(regression_data) < 1.5)
        ):  
        add_in_csv(regression_data, regressionResult, ws, "##(Test)(check-chart)-sellSMADownTrend-2DayUp-weekHighTouch")
           
        return True

def buy_random_filters(regression_data, regressionResult, reg, ws):
    if(1 < regression_data['PCT_day_change'] < 5
        and (regression_data['PCT_day_change']-0.5) < regression_data['PCT_change'] < (regression_data['PCT_day_change'] + 0.5)
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
        if(regression_data['week2HighChange'] > -0.5):
            add_in_csv(regression_data, regressionResult, ws, 'checkCupUp-near2WeekHigh-mayReveresalSell')
        elif(regression_data['PCT_day_change_pre1'] > 2
            and regression_data['PCT_day_change_pre2'] > 2
            and regression_data['forecast_day_PCT5_change'] > 0
            ):
            add_in_csv(regression_data, regressionResult, ws, 'checkCupUp-3dayUp-mayReversalSell')
        elif(regression_data['PCT_day_change'] > 2
            and regression_data['PCT_day_change_pre1'] > 2
            and regression_data['forecast_day_PCT5_change'] > 0
            ):
            add_in_csv(regression_data, regressionResult, ws, 'checkCupUp-2dayUp-mayReversalSell')
        elif(2 < regression_data['PCT_day_change'] < 3
            and regression_data['week2HighChange'] < -3
            ):
            if(is_algo_buy(regression_data)
                and 2 > regression_data['PCT_day_change_pre1'] > 0.5
                and regression_data['PCT_day_change_pre2'] > 0.5
                ):
                add_in_csv(regression_data, regressionResult, ws, 'checkCupUp-3dayUp')
            elif(is_algo_buy(regression_data)
                and 2 > regression_data['PCT_day_change_pre1'] > 0.5
                ):
                add_in_csv(regression_data, regressionResult, ws, 'checkCupUp-2dayUp')
            elif(regression_data['forecast_day_PCT7_change'] < 1
                and regression_data['PCT_day_change_pre1'] < 0 
                and regression_data['PCT_day_change_pre2'] < 0
                and regression_data['PCT_day_change_pre3'] < 0
                and regression_data['forecast_day_PCT_change'] > 0
                and regression_data['forecast_day_PCT2_change'] > 0
                ):
                add_in_csv(regression_data, regressionResult, ws, 'checkCupUp-downTrendLastDayUp-mayReversalSell')
            elif(is_algo_buy(regression_data) 
                and regression_data['forecast_day_PCT7_change'] < 1
                and (regression_data['PCT_day_change_pre2'] < 0
                    or regression_data['bar_high'] > regression_data['bar_high_pre1']
                    )
                and abs_month3High_less_than_month3Low(regression_data)
                ):
                if(regression_data['bar_high'] > regression_data['bar_high_pre1']):
                    add_in_csv(regression_data, regressionResult, ws, 'bar_high')
                if(regression_data['forecast_day_PCT2_change'] > 1
                    and regression_data['forecast_day_PCT3_change'] > 1  
                    ):
                    add_in_csv(regression_data, regressionResult, ws, 'checkCupUp')
                else:
                    add_in_csv(regression_data, regressionResult, ws, 'checkCupUp-inUpTrend')
            elif(is_algo_buy(regression_data) 
                and regression_data['forecast_day_PCT7_change'] < 1
                and (regression_data['PCT_day_change_pre2'] < 0
                    or regression_data['bar_high'] > regression_data['bar_high_pre1']
                    )
                ):
                if(regression_data['bar_high'] > regression_data['bar_high_pre1']):
                    add_in_csv(regression_data, regressionResult, ws, 'bar_high')
                if(regression_data['forecast_day_PCT2_change'] > 1
                    and regression_data['forecast_day_PCT3_change'] > 1  
                    ):
                    add_in_csv(regression_data, regressionResult, ws, 'checkCupUp-month3HighMTmonth3Low')
                else:
                    add_in_csv(regression_data, regressionResult, ws, 'checkCupUp-inUpTrend-month3HighMTmonth3Low')
            elif(regression_data['forecast_day_PCT7_change'] < 1
                and regression_data['PCT_day_change_pre1'] < 0 
                and regression_data['PCT_day_change_pre2'] > 0
                and regression_data['bar_high'] < regression_data['bar_high_pre1']
                ):
                add_in_csv(regression_data, regressionResult, ws, 'checkCupUp-mayReversalSell')
            
    if(-2.5 < regression_data['PCT_day_change'] < -1
        and -3.5 < regression_data['PCT_change'] < -1
        and regression_data['PCT_day_change_pre1'] > 1.5
        and (regression_data['PCT_day_change_pre2'] > 1
            or regression_data['PCT_day_change_pre3'] > 1
            )
        #and (regression_data['forecast_day_PCT5_change'] < 2)
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
        and (((regression_data['low'] - regression_data['bar_low_pre1'])/regression_data['bar_low_pre1'])*100) > 0 
        ):
        if(regression_data['week2HighChange'] > -0.5):
            add_in_csv(regression_data, regressionResult, ws, 'checkCupUp-lastDayDown-near2WeekHigh-mayReveresalSell')
        elif(regression_data['week2HighChange'] < -2):
            add_in_csv(regression_data, regressionResult, ws, 'checkCupUp-lastDayDown')  
        
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
        
    if(1.5 < regression_data['PCT_day_change'] < 6
        and regression_data['PCT_change'] < 6
        and (regression_data['PCT_day_change_pre2'] < 0 or regression_data['PCT_day_change_pre3'] < 0)
        and regression_data['high'] > regression_data['high_pre2']
        and regression_data['forecast_day_PCT3_change'] > 0
        and regression_data['forecast_day_PCT2_change'] > 0
        and regression_data['forecast_day_PCT_change'] > 0
        and regression_data['SMA4'] > regression_data['SMA4_2daysBack']
        and regression_data['forecast_day_PCT10_change'] < 0
        and ((regression_data['forecast_day_PCT4_change'] > 0
              and regression_data['forecast_day_PCT7_change'] < 0
              and (regression_data['forecast_day_PCT7_change'] < -5
                   or regression_data['forecast_day_PCT10_change'] < -5
                   )
            )
            or(regression_data['monthHighChange'] < -15
                and regression_data['monthLowChange'] < 10
                )
            ) 
        ):
        add_in_csv(regression_data, regressionResult, ws, '(Test)check10DayLowReversal')
        
    if('RisingMA-Risky' not in regression_data['filter4'] 
        and 'RisingMA' in regression_data['filter4']
        and (regression_data['low'] > regression_data['low_pre1']) 
        and (-2 < regression_data['PCT_day_change'] < 0) and (-2 < regression_data['PCT_change'] < 0)
        and (regression_data['forecast_day_PCT5_change'] > 3
             or regression_data['forecast_day_PCT7_change'] > 3
             or regression_data['forecast_day_PCT10_change'] > 3
            )
        ):
        if(-0.5 < regression_data['week2HighChange'] < 0.5 
            and regression_data['week2High'] != regression_data['high_pre1']
            and regression_data['week2High'] != regression_data['high_pre2']
            #and (-1 < regression_data['PCT_day_change'] < 0) and (-1 < regression_data['PCT_change'] < 0)
            ):
                add_in_csv(regression_data, regressionResult, ws, None)
        elif(regression_data['week2HighChange'] < -1):
            add_in_csv(regression_data, regressionResult, ws, 'buyRisingMA-(check5MinuteUpTrendAndBuySupertrend)')
        elif(is_algo_buy(regression_data)):
            add_in_csv(regression_data, regressionResult, ws, 'buyRisingMA-(check5MinuteUpTrendAndBuySupertrend)-Already10DayDown')
    
    if((-0.75 < regression_data['PCT_day_change'] < 0) and (-0.75 < regression_data['PCT_change'] < 0)
        and (regression_data['SMA4_2daysBack'] > 0 or regression_data['SMA9_2daysBack'] > 0)
        and regression_data['SMA4'] < 0
        and regression_data['PCT_day_change_pre1'] < -0.5
        and regression_data['PCT_day_change_pre2'] < -0.5
        and (regression_data['PCT_day_change_pre1'] < -1.5 or regression_data['PCT_day_change_pre2'] < -1.5)
        ):   
        add_in_csv(regression_data, regressionResult, ws, 'buySMA4Reversal')
        
    if((-2 < regression_data['PCT_day_change'] < 0) and (-2 < regression_data['PCT_change'] < 0)
        and regression_data['PCT_day_change_pre1'] < -7
        and low_tail_pct(regression_data) > 2
        ):
        add_in_csv(regression_data, regressionResult, ws, 'buyLastDayDownReversal')
        
    if((0.5 < regression_data['PCT_day_change'] < 2) and (-10 < regression_data['PCT_change'] < -4)
        and low_tail_pct(regression_data) > 1
        ):
        add_in_csv(regression_data, regressionResult, ws, 'buyLastDayHighDownReversal')
        
    if('checkConsolidationBreakUp-2week' in regression_data['filter']
        and 1 < regression_data['PCT_day_change'] < 4
        and 1 < regression_data['PCT_change'] < 4
        and (regression_data['PCT_day_change_pre1'] < regression_data['PCT_day_change']/2
            #or 'MLBuy' in regression_data['filter']
            #or 'brokenToday' in regression_data['filter']
            )
        and (regression_data['PCT_day_change'] > 2 
            #or 'MLBuy' in regression_data['filter']
            or 'brokenToday' in regression_data['filter']
            )
        and (regression_data['month3HighChange'] < -5 or abs_month3High_more_than_month3Low(regression_data))
        ):
        add_in_csv(regression_data, regressionResult, ws, 'checkConsolidationBreakUp(NotShapeV)-2week')
        flag = True
    elif('checkConsolidationBreakUp-2week' in regression_data['filter']
        and 0 < regression_data['PCT_day_change'] < 5
        and 0 < regression_data['PCT_change'] < 5
        and regression_data['PCT_day_change_pre1'] < 1.5  and regression_data['PCT_change_pre1'] < 1.5
        and 'brokenToday' in regression_data['filter']
        and 'MLBuy' in regression_data['filter']
        ):
        add_in_csv(regression_data, regressionResult, ws, 'RiskyCheckConsolidationBreakUp(NotShapeV)-2week')
        flag = True
