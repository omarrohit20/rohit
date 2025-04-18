import csv
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import Color, PatternFill, Font, Border
from pymongo import MongoClient
from multiprocessing.dummy import Pool as ThreadPool

import math, time
from datetime import date
import datetime   
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np

from util.util_base import *

connection = MongoClient('localhost', 27017)
db = connection.Nsedata


def buy_high_volatility_boundary(regression_data, regressionResult):
    flag = False
    ws = None
    
    if(0.5 < regression_data['PCT_day_change'] < 1.5
        and regression_data['PCT_change'] < 3
        and 0 < regression_data['PCT_day_change_pre1'] < 5
        and 0 < regression_data['PCT_day_change_pre2'] < 2
        and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1']
        and 5 < regression_data['forecast_day_PCT10_change'] < 20
        and regression_data['year2HighChange'] < -3
        and high_tail_pct(regression_data) < 2
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'X_:UptrendDojiPlus')
        flag = True
    if(regression_data['monthHighChange'] > 2
        and regression_data['week2LowChange'] > 7
        and regression_data['year2HighChange'] < -3
        and 5 < regression_data['forecast_day_PCT10_change'] < 25
        ):
        if (0.5 < regression_data['PCT_day_change'] < 1.5
            and regression_data['PCT_change'] < 3
            and 0 < regression_data['PCT_day_change_pre1'] < 5
            and 0 < regression_data['PCT_day_change_pre2'] < 2
            and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1']
            and 5 < regression_data['forecast_day_PCT10_change'] < 20
            and high_tail_pct(regression_data) < 2
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'X_:MonthHighUptrendDojiPlus')
            flag = True
        elif (1.5 < regression_data['PCT_day_change'] < 4 
            and regression_data['PCT_change'] < 7
            and 0 < regression_data['PCT_day_change_pre1'] < 5
            and 0 < regression_data['PCT_day_change_pre2'] < 5
            and 0 < regression_data['PCT_day_change_pre3'] < 5
            and regression_data['PCT_day_change_pre4'] < 0
            and 5 < regression_data['forecast_day_PCT10_change'] < 20
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'X_:MonthHighUptrend4Days')
            flag = True
        elif (1 < regression_data['PCT_day_change'] < 4 
            and regression_data['PCT_change'] < 7
            and 0 < regression_data['PCT_day_change_pre1']
            and regression_data['PCT_day_change_pre2'] < 5
            and regression_data['PCT_day_change_pre3'] < 5
            and high_tail_pct(regression_data) < 1.9
            and 10 < regression_data['forecast_day_PCT10_change'] < 20
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'X_:MonthHighUptrendDays-continueUptrendNifty/GlobalUp')
            flag = True
    if(regression_data['monthHighChange'] > 2
        and regression_data['week2LowChange'] > 5
        and 8 < regression_data['forecast_day_PCT10_change'] < 20
        ):
        if (1.5 < regression_data['PCT_day_change'] < 4
            and regression_data['PCT_change'] < 7
            and regression_data['PCT_day_change_pre1'] > 0
            and regression_data['PCT_day_change_pre2'] > 0
            and regression_data['PCT_day_change_pre3'] < 0
            and (regression_data['PCT_day_change_pre1'] < 1.5
                or regression_data['PCT_day_change_pre2'] < 1.5
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'X_:MonthHighUptrend3Days')
            flag = True
    if(regression_data['monthHighChange'] > 2
        and regression_data['week2LowChange'] > 5
        and 8 < regression_data['forecast_day_PCT10_change'] < 20
        ):
        if (1.5 < regression_data['PCT_day_change'] < 4
            and regression_data['PCT_change'] < 7
            and regression_data['PCT_day_change_pre1'] > 0
            and regression_data['PCT_day_change_pre2'] < 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'X_:MonthHighUptrend2Days')
            flag = True
    
    if(1.9 < regression_data['PCT_day_change'] < 2.6
        and 1.9 < regression_data['PCT_change'] < 4
        and regression_data['monthHighChange'] < 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'X_SGXNIFTYUPGT.5PC-GLOBALFUTUP-AfterDownTrend:PCTDayChangeBT2and2.5')
        flag = True
    if(3 < regression_data['PCT_day_change'] < 4
        and 2.5 < regression_data['PCT_change'] < 4.5
        and regression_data['monthHighChange'] < 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'X_LASTDAYNIFYDOWNLT(-2):PCTDayChangeBT3and4')
        flag = True
    if(regression_data['monthHighChange'] > 2
        and regression_data['week2LowChange'] > 7
        and regression_data['close'] < 70
        ):
        if (regression_data['PCT_day_change'] > 2
            and regression_data['PCT_change'] > 2
            and regression_data['PCT_day_change_pre1'] > 2
            and regression_data['PCT_day_change_pre2'] > 2
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'X_:MonthHighUptrend3Days-risky-closelt70')
            flag = True
        elif (regression_data['PCT_day_change'] > 4
            and regression_data['PCT_change'] > 4
            and regression_data['PCT_day_change_pre1'] > 4
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'X_:MonthHighUptrend3Days-risky-closelt70')
            flag = True
    elif(regression_data['monthHighChange'] > 2
        and regression_data['week2LowChange'] > 7
        and regression_data['close'] < 150
        ):
        if (regression_data['PCT_day_change'] > 0
            and regression_data['PCT_change'] > 0
            and regression_data['PCT_day_change_pre1'] > 0
            and regression_data['PCT_day_change_pre2'] > 0
            and regression_data['PCT_day_change_pre3'] > 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'X_:MonthHighUptrend4Days-risky-closelt150')
            flag = True
    if(regression_data['PCT_day_change'] < -2
        and regression_data['PCT_change'] < 0
        and regression_data['monthLowChange'] < 1
        and regression_data['month3HighChange'] < -10
        ):
        if(regression_data['PCT_day_change_pre1'] > -0.7
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'PCTDayChangePre1GT0')
        elif(regression_data['PCT_day_change_pre2'] > -0.7
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'PCTDayChangePre2GT0')
            
        if(regression_data['PCT_day_change'] < -2 and regression_data['PCT_day_change_pre1'] < -2 and regression_data['PCT_day_change_pre2'] < -2
            and regression_data['monthLowChange'] < 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'PCTDayChangeLast3DaysLT(-2)')
        elif(regression_data['PCT_day_change'] < -2 and regression_data['PCT_day_change_pre1'] < -2
            and regression_data['monthLowChange'] < 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'PCTDayChangeLast2DaysLT(-2)')
            
        if(1.5 < low_tail_pct(regression_data)):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'AvoidSellingLowTail-mayBuy')
        
       
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Z_:NearOrBelowMonthLow')
        flag = True
    if(regression_data['PCT_day_change'] < -2
        and regression_data['PCT_change'] < 0
        and regression_data['month3LowChange'] < 1
        and regression_data['month3HighChange'] < -15
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Z_:NearOrBelowMonth3Low')
        flag = True
    if(regression_data['PCT_day_change'] < -2
        and regression_data['PCT_change'] < 0
        and regression_data['year2LowChange'] < 1
        and regression_data['month3HighChange'] < -15
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Z_:NearOrBelowYear2Low')
        flag = True 
    if(-1 < regression_data['PCT_day_change'] < 0
        and regression_data['PCT_day_change_pre1'] > 1
        and regression_data['PCT_day_change_pre2'] < 0
        and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change'])
        and abs(regression_data['PCT_day_change_pre1']) < abs(regression_data['PCT_day_change_pre2'])
        and regression_data['bar_high'] > regression_data['bar_high_pre1']
        and regression_data['bar_high_pre2'] > regression_data['bar_high_pre1']
        and regression_data['weekHighChange'] < -1
        ):
        #add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Y_:AlternateUpDownBuy-Risky-ConNextDayIfWeekHighChangeLT0AfterToday')
        flag = True
    if(-1 < regression_data['PCT_day_change'] < 0
        and regression_data['PCT_day_change_pre1'] > 1.5 
        and regression_data['PCT_day_change_pre2'] < 0
        and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change'])
        and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change_pre2'])
        and regression_data['bar_high'] > regression_data['bar_high_pre1'] > regression_data['bar_high_pre2']
        and regression_data['weekHighChange'] < -1
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Y_:AlternateUpDownBuy-ConNextDayIfWeekHighChangeLT0AfterToday')
        flag = True
    if(-2 < regression_data['PCT_day_change'] < 4
        and -2 < regression_data['PCT_change'] < 6
        and regression_data['month3HighChange'] < -5
        and -2 < regression_data['monthHighChange'] < 3
        and regression_data['monthLowChange'] > 3
        and regression_data['forecast_day_PCT_change'] > 0
#         and regression_data['forecast_day_PCT2_change'] > 1
        # and regression_data['forecast_day_PCT3_change'] > 1
        # and regression_data['forecast_day_PCT4_change'] > 1
        and (regression_data['PCT_day_change'] < 0
             or regression_data['PCT_day_change_pre1'] < 0
             or regression_data['PCT_day_change_pre2'] < 0
             )
        and (regression_data['PCT_day_change_pre1'] > 1.5
             or regression_data['PCT_day_change_pre2'] > 1.5
             or regression_data['PCT_day_change_pre3'] > 1.5
             )
        and (regression_data['PCT_day_change_pre1'] < 0
             or regression_data['PCT_day_change_pre2'] < 0
             or regression_data['PCT_day_change_pre3'] < 0
             or regression_data['PCT_day_change_pre4'] < 0
             )
        ):
        if (((regression_data['PCT_day_change'] > 0 and regression_data['PCT_day_change_pre1'] > 0
                and (regression_data['PCT_day_change_pre2'] > 0 or regression_data['PCT_day_change_pre3'] > 0)
                )
             or (regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change_pre2'] > 0
                and (regression_data['PCT_day_change'] > 0 or regression_data['PCT_day_change_pre3'] > 0)
                )
             or (regression_data['PCT_day_change'] > 0 and regression_data['PCT_day_change_pre2'] > 0 
                and (regression_data['PCT_day_change_pre1'] > 0 or regression_data['PCT_day_change_pre3'] > 0)
                ))
            and regression_data['forecast_day_PCT_change'] > 1
            and (-2 < regression_data['PCT_day_change'] < 0
                or regression_data['PCT_day_change'] > 1
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Y_:MonthLowReversalContinue')
            flag = True
        elif(regression_data['PCT_day_change'] < 0
            and regression_data['PCT_day_change_pre1'] > 0 
            and regression_data['PCT_day_change_pre2'] < 0
            and regression_data['PCT_day_change_pre3'] > 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Y_:MonthLowReversalContinue-AlternateUpDown')
            flag = True
    
    if(1.9 < regression_data['PCT_day_change'] < 4
        and 1.9 < regression_data['PCT_change'] < 6
        and regression_data['monthHighChange'] < -5
        and regression_data['monthLowChange'] < 5
        and (regression_data['monthLowChange'] < 0
            or abs(regression_data['monthHighChange']) > 3 * abs(regression_data['monthLowChange'])
            )
        and high_tail_pct(regression_data) < 1.5
        and regression_data['PCT_day_change_pre1'] < 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Y_:MonthLowReversal-followNiftyDayTrend')
        flag = True
    if((regression_data['month3HighChange'] < -15
            and regression_data['month3LowChange'] < 5
            and regression_data['month6LowChange'] > 7.5
            # and regression_data['monthHighChange'] < -5
            and (regression_data['monthLowChange'] < 5
                or abs(regression_data['monthHighChange']) > 2 * abs(regression_data['monthLowChange'])
                )
            and high_tail_pct(regression_data) < 1.5
        # and regression_data['PCT_day_change_pre1'] < 0
        )
        or ('ReversalLowMonth3' in regression_data['filter3']
            and regression_data['monthLowChange'] < 7
            and high_tail_pct(regression_data) < 1.5
            )
        ):
        if(1.5 < regression_data['PCT_day_change'] < 6
            and 1.5 < regression_data['PCT_change'] < 7
            and regression_data['PCT_day_change_pre1'] < 0
            and regression_data['high'] > regression_data['high_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Y_:Month3LowReversal-followNiftyDayTrend')
            flag = True
        elif(1 < regression_data['PCT_day_change'] < 2
            and 0.5 < regression_data['PCT_change'] < 3
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Y_:Month3LowReversal-followNiftyDayTrend')
            flag = True
        elif(-1 < regression_data['PCT_day_change'] < 1
            and -2 < regression_data['PCT_change'] < 2
            and regression_data['PCT_day_change_pre1'] > 0
            and regression_data['PCT_day_change_pre2'] > 0
            and (regression_data['PCT_day_change_pre1'] > 1 or regression_data['PCT_day_change_pre2'] > 1)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Y_:Month3LowReversal-followNiftyDayTrend')
            flag = True
    if((regression_data['yearLowChange'] < 7
            and (regression_data['month3LowChange'] < 5
                or abs(regression_data['month3HighChange']) > 2 * abs(regression_data['month3LowChange'])
                )
            and high_tail_pct(regression_data) < 1.5
            )
        or (('ReversalLowYear' in regression_data['filter3'] or 'ReversalLowYear2' in regression_data['filter3'])
            and regression_data['monthLowChange'] < 7
            and high_tail_pct(regression_data) < 1.5
            )
        ):
        if(1.5 < regression_data['PCT_day_change'] < 6
            and 1.5 < regression_data['PCT_change'] < 7
            and regression_data['PCT_day_change_pre1'] > 0
            and regression_data['high'] > regression_data['high_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Y_:YearLowReversal-followNiftyDayTrend(greenbarstart-low-month-lowest)')
            flag = True
        elif(1 < regression_data['PCT_day_change'] < 2
            and 0.5 < regression_data['PCT_change'] < 3
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Y_:YearLowReversal-followNiftyDayTrend(greenbarstart-low-month-lowest)')
            flag = True
        elif(-1 < regression_data['PCT_day_change'] < 1
            and -2 < regression_data['PCT_change'] < 2
            and regression_data['PCT_day_change_pre1'] > 0
            and regression_data['PCT_day_change_pre2'] > 0
            and (regression_data['PCT_day_change_pre1'] > 1 or regression_data['PCT_day_change_pre2'] > 1)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Y_:YearLowReversal-followNiftyDayTrend(greenbarstart-low-month-lowest)')
            flag = True
            
    return flag


def buy_high_volatility_monthHighNotReached(regression_data, regressionResult):
    flag = False
    ws = None
    
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
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'DOWNTRENDMARKET:sellStockHeavyUptrend')
        flag = True
    elif((('(shortUpTrend)$NA' in regression_data['series_trend']) 
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
            # add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'checkForUptrendContinueLastDayDown')
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None)
        elif(regression_data['PCT_day_change'] > 1
            and regression_data['PCT_day_change_pre1'] > 1
            and regression_data['PCT_day_change_pre2'] > 1
            and regression_data['week2HighChange'] < -3
            and (regression_data['PCT_day_change_pre1'] < 0 or regression_data['PCT_day_change_pre2'] < 0 or regression_data['PCT_day_change_pre3'] < 0)
            ):
            # add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'checkForUptrendContinueWeek2HighNotReached')
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None)
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
               add_in_csv(regression_data, regressionResult, ws, None, None, None, 'UPTRENDMARKET:checkForUptrendContinueMonthHigh(NotMonth3HighMonth6High)')
            else:
               add_in_csv(regression_data, regressionResult, ws, None, None, None, 'UPTRENDMARKETHEAVY:RISKY-Last4DayUp:checkForUptrendContinueMonthHigh(NotMonth3HighMonth6High)')
        elif(regression_data['PCT_day_change'] > 1
            and regression_data['PCT_day_change_pre1'] > 0.75
            and regression_data['PCT_day_change_pre2'] > 0.75
            and (regression_data['PCT_day_change_pre1'] > 1 or regression_data['PCT_day_change_pre2'] > 1)
            and regression_data['monthHighChange'] > -2
            and regression_data['monthLowChange'] > 10
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'checkForUptrendReversalMonthHigh(5to10-minute-baseline-if-uptrend)') 
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
            # add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'checkForUptrendContinueLastDayDown')
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None)
        elif(regression_data['PCT_day_change'] > 1
            and regression_data['PCT_day_change_pre1'] > 1
            and regression_data['PCT_day_change_pre2'] > 1
            and regression_data['week2HighChange'] < -3
            and (regression_data['PCT_day_change_pre1'] < 0 or regression_data['PCT_day_change_pre2'] < 0 or regression_data['PCT_day_change_pre3'] < 0)
            ):
            # add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'checkForUptrendContinueWeek2HighNotReached')
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None)
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
               add_in_csv(regression_data, regressionResult, ws, None, None, None, 'UPTRENDMARKET:checkForUptrendContinueMonthHigh(NotMonth3HighMonth6High)')
            else:
               add_in_csv(regression_data, regressionResult, ws, None, None, None, 'UPTRENDMARKETHEAVY:RISKY-Last4DayUp:checkForUptrendContinueMonthHigh(NotMonth3HighMonth6High)')
        elif(regression_data['PCT_day_change'] > 1
            and regression_data['PCT_day_change_pre1'] > 0.75
            and regression_data['PCT_day_change_pre2'] > 0.75
            and (regression_data['PCT_day_change_pre1'] > 1 or regression_data['PCT_day_change_pre2'] > 1)
            and regression_data['monthHighChange'] > -2
            and regression_data['monthLowChange'] > 10
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'checkForUptrendReversalMonthHigh(5to10-minute-baseline-if-uptrend)')
        flag = True
    
    if(('upTrend' in regression_data['series_trend'] or 'UpTrend' in regression_data['series_trend'] or 'trendUp' in regression_data['series_trend'])
        and regression_data['monthHighChange'] < 0
        and 1 < regression_data['PCT_day_change'] < 6
        and 1 < regression_data['PCT_change'] < 6
        and (regression_data['PCT_day_change'] > 1.5
            or regression_data['PCT_change'] > 1.5)
        and ((regression_data['bar_high'] > regression_data['weekBarHigh'])
            or regression_data['weekHighChange'] > 0.5
            )
        and (regression_data['PCT_day_change_pre1'] < 0.5
             or regression_data['PCT_day_change_pre2'] < 0.5
             or regression_data['PCT_day_change_pre3'] < 0.5
             or regression_data['PCT_day_change_pre4'] < 0.5
            )
        and ('IT' not in regression_data['industry']
             and 'PHARMA' not in regression_data['industry']
             and 'HEALTH' not in regression_data['industry']
             )
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'GLOBALFUTUP-GLOBALMARKETUP-LASTDAYUP:mayContinueShortUpTrend-monthHighNotReached') 
        flag = True
    return flag


def buy_high_volatility_pre1pre2doji(regression_data, regressionResult):
    flag = False
    ws = None
    
    if(regression_data['week2HighChange'] > 0
        and regression_data['week2LowChange'] > 5
        and regression_data['monthHighChange'] > 0
        # and regression_data['month3HighChange'] > 0
        and 3 < regression_data['PCT_day_change'] < 8
        and 1 < regression_data['PCT_change'] < 8
        and 0 < regression_data['PCT_day_change_pre1'] < 1
        and (regression_data['forecast_day_PCT5_change'] > 5 or  regression_data['forecast_day_PCT10_change'] > 5)
        ):
        if(regression_data['bar_high'] > regression_data['bar_high_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'GLOBALFUTUP-GLOBALMARKETUP:mayContinueShortUpTrend-PCTDayChangePre1GT0-todayGT3')
            flag = True
    elif(regression_data['week2HighChange'] > 0
        and regression_data['week2LowChange'] > 5
        and 3 < regression_data['PCT_day_change'] < 8
        and -1 < regression_data['PCT_day_change_pre1'] < 0
        and regression_data['PCT_day_change_pre2'] > 0 
        and (regression_data['PCT_day_change_pre3'] > 0 or regression_data['PCT_day_change_pre4'] > 0)
        and (regression_data['forecast_day_PCT5_change'] > 5 or  regression_data['forecast_day_PCT10_change'] > 5)
        ):
        if(regression_data['bar_high'] > regression_data['bar_high_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'GLOBALFUTUP-GLOBALMARKETUP:mayContinueShortUpTrend-PCTDayChangePre1LT0-todayGT4')
            flag = True     
    elif(regression_data['week2HighChange'] > 0
        and regression_data['PCT_day_change_pre1'] < 0
        and (0 < regression_data['PCT_day_change'] < 1
            # or (0 < regression_data['PCT_day_change'] < 1.5 and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change']))
            ) 
        ):
        if(regression_data['year2HighChange'] > 0
            and regression_data['weekHighChange'] > -2
            and (regression_data['PCT_day_change_pre1'] < -1 or regression_data['bar_high'] > regression_data['bar_high_pre1'])
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'GLOBALFUTUP-GLOBALMARKETUP:mayContinueShortUpTrend-PCTDayChangePre1LT0-year2High')
            flag = True
        elif(regression_data['month3HighChange'] > 0
            and regression_data['weekHighChange'] > -2
            and ((regression_data['PCT_day_change_pre1'] < -1 and regression_data['PCT_day_change_pre3'] > -0.75)
                 or (regression_data['bar_high'] > regression_data['bar_high_pre1']
                     and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change'])
                     and regression_data['PCT_day_change_pre2'] < -1
                    )
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'GLOBALFUTUP-GLOBALMARKETUP:mayContinueShortUpTrend-PCTDayChangePre1LT0-month3High')
            flag = True
#         elif(regression_data['month3HighChange'] > 0
#             and (regression_data['PCT_day_change_pre1'] > -1 and regression_data['bar_high'] < regression_data['bar_high_pre1'])
#             ):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'GLOBALFUTUP-GLOBALMARKETUP:mayReversalShortUpTrend-PCTDayChangePre1LT0-month3High')
#             flag = True
    elif(regression_data['month3HighChange'] > 0
        and regression_data['week2HighChange'] > -2
        and 0 < regression_data['PCT_day_change_pre1'] < 0.5 and regression_data['bar_high'] < regression_data['bar_high_pre1']
        and -0.5 < regression_data['PCT_day_change'] < 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'GLOBALFUTUP-GLOBALMARKETUP:mayReversalShortUpTrend-PCTDayChangePre1LT0-month3High')
        flag = True
    elif('shortUpTrend' in regression_data['series_trend']
        and (regression_data['forecast_day_PCT5_change'] > 2 or regression_data['forecast_day_PCT7_change'] > 2
            or (regression_data['forecast_day_PCT5_change'] > -1 and regression_data['forecast_day_PCT7_change'] > -1
               and regression_data['PCT_day_change'] > 0)
            )
        ):
        if(-2 < regression_data['PCT_day_change_pre1'] < 0
            and 0 < regression_data['PCT_day_change'] < 2
            ):
            if(regression_data['forecast_day_PCT_change'] > 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'GLOBALFUTUP-GLOBALMARKETUP:mayContinueShortUpTrend-PCTDayChangePre1LT0')
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'GLOBALFUTUP-GLOBALMARKETUP:mayUPTREND(Buy)DOWNTREND(Sell)ShortUpTrend-PCTDayChangePre1LT0')
            flag = True
        elif(-2 < regression_data['PCT_day_change_pre2'] < 0
            and 0 < regression_data['PCT_day_change_pre1'] < 2
            and -1 < regression_data['PCT_day_change'] < 2
            and (regression_data['PCT_day_change'] < 0 or ((regression_data['forecast_day_PCT5_change'] < 0 or regression_data['forecast_day_PCT5_change'] < 0)
                                                           and (regression_data['bar_high'] < regression_data['bar_high_pre4'] or regression_data['bar_high'] < regression_data['bar_high_pre5'])
                                                        )
                )
            ):
            if(regression_data['PCT_day_change'] < 0
                and regression_data['forecast_day_PCT_change'] > 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'GLOBALFUTUP-GLOBALMARKETUP:HEAVY:mayContinueShortUpTrend-PCTDayChangePre2LT0')
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'GLOBALFUTUP-GLOBALMARKETUP:HEAVY:mayUPTREND(Buy)DOWNTREND(Sell)ShortUpTrend-PCTDayChangePre2LT0')
                
            flag = True
    elif('shortUpTrend' in regression_data['series_trend']
        ):
        if(-2 < regression_data['PCT_day_change_pre2'] < 0
            and 0 < regression_data['PCT_day_change_pre1'] < 2
            and (regression_data['PCT_day_change'] < -1.5
                or (regression_data['forecast_day_PCT5_change'] < -1 and regression_data['forecast_day_PCT7_change'] < -1)
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'GLOBALFUTUP-GLOBALMARKETUP:HEAVY:mayReversalShortUpTrend-PCTDayChangePre2LT0')
            flag = True
            
    return flag


def buy_high_volatility_shortUpTrend(regression_data, regressionResult):
    flag = False
    ws = None
    
    if('shortUpTrend' in regression_data['series_trend']): 
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'shortUpTrend')
        if(0 < regression_data['PCT_day_change'] < 1.3 and 0 < regression_data['PCT_change'] < 2
            and 1.5 < regression_data['PCT_day_change_pre1'] > regression_data['PCT_day_change']
            and 1.5 < regression_data['PCT_day_change_pre2'] > regression_data['PCT_day_change']
            and regression_data['forecast_day_PCT_change'] > 0
            and (-1 < regression_data['month3HighChange'] < 2
                or (abs(bar_high_change_month3(regression_data)) < 1 and high_tail_pct(regression_data) > 1)
                )
            and (low_tail_pct(regression_data) < 0.5 or low_tail_pct(regression_data) < high_tail_pct(regression_data)
                or abs(high_tail_pct(regression_data) - low_tail_pct(regression_data)) <= 0.2
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'shortUpTrendSellReversal-Month3High-Doji-Last2DayGTToday')
        elif(0 < regression_data['PCT_day_change'] < 1.3 and 0 < regression_data['PCT_change'] < 2
            and 1.5 < regression_data['PCT_day_change_pre1'] > regression_data['PCT_day_change']
            and 1.5 < regression_data['PCT_day_change_pre2'] > regression_data['PCT_day_change']
            and regression_data['forecast_day_PCT_change'] > 0
            and ((-1.5 < regression_data['monthHighChange'] < 0.5 and regression_data['month3HighChange'] < -20)
                or (abs(bar_high_change_month(regression_data)) < 1 and high_tail_pct(regression_data) > 1)
                )
            and (low_tail_pct(regression_data) < 0.5 or low_tail_pct(regression_data) < high_tail_pct(regression_data)
                or abs(high_tail_pct(regression_data) - low_tail_pct(regression_data)) <= 0.2
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'shortUpTrendSellReversal-MonthHigh-Doji-Last2DayGTToday')
        elif(0 < regression_data['PCT_day_change'] < 1.3 and 0 < regression_data['PCT_change'] < 2
            and 2 < regression_data['PCT_day_change_pre1'] > regression_data['PCT_day_change']
            and 1.5 < regression_data['PCT_day_change_pre2'] > regression_data['PCT_day_change']
            and regression_data['forecast_day_PCT_change'] > 0
            and regression_data['month3HighChange'] < -5
            and regression_data['monthLowChange'] > 5
            and abs(regression_data['monthHighChange']) > 1.5
            and abs(regression_data['monthHighChange']) < abs(regression_data['monthLowChange'])
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'shortUpTrendBuyContinue-Doji-Last2DayGTToday')
        elif(0 < regression_data['PCT_day_change'] < 1.3 and 0 < regression_data['PCT_change'] < 2
            and 2 < regression_data['PCT_day_change_pre1'] > regression_data['PCT_day_change']
            and 2 < regression_data['PCT_day_change_pre2'] > regression_data['PCT_day_change']
            and regression_data['PCT_day_change_pre3'] < 1
            and regression_data['forecast_day_PCT_change'] > 0
            # and regression_data['month3HighChange'] < -5
            and regression_data['monthLowChange'] > 5
            and abs(regression_data['monthHighChange']) > 1.5
            and abs(regression_data['monthHighChange']) < abs(regression_data['monthLowChange'])
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'HEAVY:GLOBALFUTUP-GLOBALMARKETUP:shortUpTrendBuyContinue-Doji-Last2DayGTToday')
            
        if(regression_data['PCT_day_change'] > 0 and regression_data['PCT_change'] > 0
            and regression_data['forecast_day_PCT_change'] > 0
            and ((-1.5 < regression_data['monthHighChange'] < 1.5 and regression_data['monthHighChange'] == regression_data['month2HighChange'])
                and abs(bar_high_change_month(regression_data)) < 1
                )
            and high_tail_pct(regression_data) > 1 and low_tail_pct(regression_data) < high_tail_pct(regression_data)
            and (low_tail_pct(regression_data) < 1 or (high_tail_pct(regression_data) - low_tail_pct(regression_data)) > 0.5)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'shortUpTrendSellReversal-MonthHigh')
        flag = True
    
    if(0 < regression_data['PCT_day_change'] < 5.5
        and -3 < regression_data['PCT_change'] < 5.5
        and regression_data['high'] < regression_data['high_pre1']
        and regression_data['bar_high'] < (regression_data['bar_high_pre1'] - ((regression_data['bar_high_pre1'] - regression_data['bar_low_pre1'])/2))
        and ((regression_data['PCT_day_change_pre1'] < -1.5)
            or (regression_data['PCT_day_change_pre1'] < -1 and 0 < regression_data['PCT_day_change_pre2'] < 2)
            or (regression_data['PCT_day_change_pre1'] < 0 and 0 < regression_data['PCT_day_change_pre2'] < 1)
            )
        and (regression_data['forecast_day_PCT7_change'] > 0
            and regression_data['forecast_day_PCT10_change'] > 0
            )
        and regression_data['forecast_day_PCT_change'] < 0
        and regression_data['weekHighChange'] < 0
        and regression_data['month3HighChange'] < 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'RISKY-DOWNTREND-BUY')
    
    if(-5.5 < regression_data['PCT_day_change'] < 0
        and -5.5 < regression_data['PCT_change'] < 3
        and regression_data['low'] > regression_data['low_pre1']
        and regression_data['bar_low'] > (regression_data['bar_high_pre1'] - ((regression_data['bar_high_pre1'] - regression_data['bar_low_pre1'])/2))
        and ((regression_data['PCT_day_change_pre1'] > 1.5)
            or (regression_data['PCT_day_change_pre1'] > 1 and 0 > regression_data['PCT_day_change_pre2'] > -2)
            or (regression_data['PCT_day_change_pre1'] > 0 and 0 > regression_data['PCT_day_change_pre2'] > -1)
            )
        and (regression_data['forecast_day_PCT7_change'] < 0
            and regression_data['forecast_day_PCT10_change'] < 0
            )
        and regression_data['forecast_day_PCT_change'] > 0
        and regression_data['weekLowChange'] > 0
        and regression_data['month3LowChange'] > 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'RISKY-UPTREND-SELL')
    
    if(('shortUpTrend' in regression_data['series_trend'] or 'RISKY-UPTREND-SELL' in regression_data['filter1'])
        and regression_data['PCT_day_change_pre1'] > 0
        and regression_data['PCT_day_change'] > 0
        and regression_data['PCT_day_change_pre2'] > 0
        and regression_data['PCT_day_change_pre3'] < -2
        and high_tail_pct(regression_data) > 0.9
        ):
        if('shortUpTrend' in regression_data['series_trend']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'shortUpTrend-1')
            
        elif('RISKY-UPTREND-SELL' in regression_data['filter1']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'RISKY-UPTREND-SELL-1')
        
    elif(('shortUpTrend' in regression_data['series_trend'] or 'RISKY-UPTREND-SELL' in regression_data['filter1'])
        and ((regression_data['PCT_day_change_pre1'] > 1.5 and 0 < regression_data['PCT_day_change'] < 1.3)
             or (regression_data['PCT_day_change_pre1'] > 3 and 0 < regression_data['PCT_day_change'] < 1.5)
            )
        and regression_data['PCT_day_change_pre1'] > regression_data['PCT_day_change'] + 0.5
        and regression_data['PCT_day_change_pre2'] > 0 
        and high_tail_pct(regression_data) > 0.9
        ):
        if('shortUpTrend' in regression_data['series_trend']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'shortUpTrend-1')
            flag = True
            if((high_tail_pct(regression_data) > 2 or high_tail_pct_pre1(regression_data) > 2)
                and regression_data['PCT_day_change'] < 0.75
                and regression_data['PCT_change'] < 0
                and regression_data['PCT_day_change_pre1'] > 0
                and regression_data['PCT_day_change_pre2'] > 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'mayReversalSell-doji-shortUpTrend')
            elif(regression_data['month6HighChange'] < 0
                and (regression_data['PCT_day_change_pre1'] < -1
                    or regression_data['PCT_day_change_pre2'] < -1
                    or regression_data['PCT_day_change_pre3'] < -1
                    or regression_data['PCT_day_change_pre4'] < -1
                    )
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'mayContinueBuy-doji-shortUpTrend')
            elif(regression_data['PCT_day_change_pre1'] > 0
                and regression_data['PCT_day_change_pre2'] > 0
                and regression_data['PCT_day_change_pre3'] > 0
                and regression_data['PCT_day_change_pre4'] > 0
                and regression_data['PCT_day_change_pre5'] > 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'mayReversalSell-doji-upTrend')
    
    if('shortUpTrend' in regression_data['filter1']
        and 0 < regression_data['PCT_day_change'] < 1.3
        and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change']) * 2
        and regression_data['PCT_day_change_pre1'] > 1
        and (regression_data['PCT_day_change_pre1'] > -0.5 and regression_data['PCT_day_change_pre2'] > -0.5)
        and (regression_data['PCT_day_change_pre1'] > 1 or regression_data['PCT_day_change_pre2'] > 1)
        and (regression_data['PCT_day_change_pre3'] < -1 or regression_data['PCT_day_change_pre4'] < -1)
        and (regression_data['PCT_day_change_pre3'] < 0.5 and regression_data['PCT_day_change_pre4'] < 0.5)
        and regression_data['year5HighChange'] < -5
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'TEST-UPTREND:mayContinueBuy-(shortUpTrend)')
    
    return flag


def buy_high_volatility_riskyUptrendSell(regression_data, regressionResult):
    flag = False
    ws = None
    
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
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'RISKY-UPTREND-SELL') 
        flag = True
        if(low_tail_pct(regression_data) <= 1.8
            and (0.6 <= low_tail_pct(regression_data) or regression_data['bar_low'] > regression_data['bar_low_pre1'])
            and -1.7 < regression_data['PCT_day_change'] < 0
            and (((regression_data['high'] > regression_data['high_pre1'] or regression_data['bar_low'] > regression_data['bar_low_pre1'])
                  and (regression_data['low'] > regression_data['low_pre1'])
                  and abs(regression_data['PCT_day_change']) < abs(regression_data['PCT_day_change_pre1'])
                  )
                )
            and abs(regression_data['month3HighChange']) > 2
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'RISKY-UPTREND-SELL-0')
            if(regression_data['high'] > regression_data['high_pre1']
                and regression_data['low'] > regression_data['low_pre1']
                and high_tail_pct(regression_data) > abs(regression_data['PCT_day_change'])    
                and low_tail_pct(regression_data) > abs(regression_data['PCT_day_change'])  
                and regression_data['bar_high'] < regression_data['bar_high_pre1']
                and regression_data['bar_low'] > regression_data['bar_low_pre1']
                and regression_data['forecast_day_PCT_change'] < regression_data['forecast_day_PCT2_change'] < regression_data['forecast_day_PCT3_change']
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'mayContinueBuy-doji-RISKY-UPTREND-SELL')
        elif(0.6 <= low_tail_pct(regression_data) <= 1.8
            and -1.7 < regression_data['PCT_day_change'] < 0
            and (((regression_data['high'] > regression_data['high_pre1'] or regression_data['bar_high'] > regression_data['bar_high_pre1'])
                  and abs(regression_data['PCT_day_change']) < abs(regression_data['PCT_day_change_pre1']))
                or (regression_data['low'] > regression_data['low_pre1'] and regression_data['forecast_day_PCT_change'] > 0.5)
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'RISKY-UPTREND-SELL-1')   
    if(-5.5 < regression_data['PCT_day_change'] < 0
        and -5.5 < regression_data['PCT_change'] < 3
        and regression_data['low'] > regression_data['low_pre1']
        and regression_data['bar_low'] > (regression_data['bar_high_pre1'] - ((regression_data['bar_high_pre1'] - regression_data['bar_low_pre1']) / 2))
        and ((regression_data['PCT_day_change_pre1'] > 1.5)
            or (regression_data['PCT_day_change_pre1'] > 1 and 0 > regression_data['PCT_day_change_pre2'] > -2)
            or (regression_data['PCT_day_change_pre1'] > 0 and 0 > regression_data['PCT_day_change_pre2'] > -1)
            )
        and (regression_data['forecast_day_PCT7_change'] < 0
            and regression_data['forecast_day_PCT10_change'] < 0
            )
        and regression_data['forecast_day_PCT_change'] > 0
        and regression_data['weekLowChange'] > 0
        and regression_data['month3LowChange'] > 0
        and abs(regression_data['month3HighChange']) > 2
        and 0.5 < low_tail_pct(regression_data)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'RISKY-UPTREND-SELL-2')
        flag = True
    if('RISKY-UPTREND-SELL' in regression_data['filter5']
        and 'DOJI' in regression_data['filter5']
        and regression_data['PCT_day_change'] < 0
        and regression_data['PCT_day_change_pre1'] > 0
        and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change'])
        and (regression_data['PCT_day_change_pre1'] > 1 or abs(regression_data['PCT_day_change_pre1']) > 2 * abs(regression_data['PCT_day_change']))
        and regression_data['week2HighChange'] > 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'RISKY-UPTREND-SELL-3')
        flag = True
    
    if('DOJI' in regression_data['filter5']
        and regression_data['PCT_day_change'] > 0
        and regression_data['PCT_day_change_pre1'] > 0.5
        and regression_data['PCT_day_change_pre2'] > 0.5
        and abs(regression_data['PCT_day_change']) < abs(regression_data['PCT_day_change_pre1'])
        and abs(regression_data['PCT_day_change']) < abs(regression_data['PCT_day_change_pre2'])
        and (abs(regression_data['PCT_day_change_pre1']) - abs(regression_data['PCT_day_change'])) * 100 / abs(regression_data['PCT_day_change']) > 30
        ):
        if(regression_data['PCT_day_change_pre3'] < 0
            and (regression_data['week2HighChange'] < -3
                 or regression_data['week2HighChange'] < -3
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'RISKY-UPTREND-SELL-4-Buy')
        elif(regression_data['PCT_day_change_pre3'] > 0
            and regression_data['month3HighChange'] < -5
            and regression_data['high'] > regression_data['high_pre1']
            and regression_data['close'] > regression_data['close_pre1']
            and (regression_data['week2HighChange'] > 0.5)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'RISKY-UPTREND-SELL-4-Sell')
        if(regression_data['PCT_day_change_pre3'] < 0.5
            and regression_data['month3HighChange'] > 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'RISKY-UPTREND-SELL-4-month3HighBuy')
        
        flag = True
    
    if('RISKY-UPTREND-SELL' in regression_data['filter1']
       and -1.3 < regression_data['PCT_day_change'] < 0
       and 1.5 < regression_data['PCT_day_change_pre1'] < 6
       and (regression_data['PCT_day_change_pre1'] > 1.5 or regression_data['PCT_day_change_pre3'] < 0)
       and regression_data['PCT_day_change_pre2'] > 0
       and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change'])
       and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change_pre2'])
       and regression_data['forecast_day_PCT_change'] < regression_data['forecast_day_PCT2_change'] < regression_data['forecast_day_PCT3_change']
       and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change']) * 2
       ):
       if(regression_data['PCT_day_change_pre3'] > 1 or regression_data['PCT_day_change_pre4'] > 1):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'mayContinueBuy-(RISKY-UPTREND-SELL)') 
       elif(regression_data['PCT_day_change_pre3'] < -1 or regression_data['PCT_day_change_pre4'] < -1):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'mayReversalSellInDowntrend-ContinueBuyInUptrend(RISKY-UPTREND-SELL)') 
    
    if('RISKY-UPTREND-SELL' in regression_data['filter1']
        and -1.3 < regression_data['PCT_day_change'] < 0
        and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change']) * 2
        and regression_data['PCT_day_change_pre1'] > 1
        and (regression_data['PCT_day_change_pre1'] > -0.5 and regression_data['PCT_day_change_pre2'] > -0.5)
        and (regression_data['PCT_day_change_pre1'] > 1 or regression_data['PCT_day_change_pre2'] > 1)
        and (regression_data['PCT_day_change_pre3'] < -1 or regression_data['PCT_day_change_pre4'] < -1)
        and (regression_data['PCT_day_change_pre3'] < 0.5 and regression_data['PCT_day_change_pre4'] < 0.5)
        # and regression_data['year5HighChange'] < -5
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'mayContinueBuy-(RISKY-UPTREND-SELL)')
    elif(regression_data['PCT_day_change_pre1'] > 7
        and regression_data['PCT_day_change'] < -2
        and regression_data['bar_low_pre1'] < regression_data['bar_low'] < regression_data['bar_high_pre1']
        and low_tail_pct(regression_data) < 3
        and (regression_data['forecast_day_PCT7_change'] < 0 or regression_data['forecast_day_PCT10_change'] < 0)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'mayUpperCircuitContinueUptrend')
        flag = True
    elif('RISKY-UPTREND-SELL' in regression_data['filter1']
        and -1.3 < regression_data['PCT_day_change'] < 0
        and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change']) * 2
        and (high_tail_pct(regression_data) > 1.5 or low_tail_pct(regression_data) > 1.5)
        and regression_data['PCT_day_change_pre1'] > 0
        and regression_data['PCT_day_change_pre2'] > 0
        and regression_data['PCT_day_change_pre3'] > 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'mayContinueSell-(RISKY-UPTREND-SELL)')
    
    return flag


def buy_high_volatility_lastDayDown(regression_data, regressionResult):
    flag = False
    ws = None
    
    if(regression_data['monthHighChange'] > -4 and regression_data['week2HighChange'] > -4 
        and (regression_data['weekHighChange'] > -4 or regression_data['week2HighChange'] > 0)
        and (regression_data['monthHighChange'] == regression_data['week2HighChange']
             or regression_data['week2HighChange'] == regression_data['weekHighChange']
             or regression_data['monthHighChange'] == regression_data['weekHighChange']
            )
        and abs(regression_data['monthLowChange']) > abs(regression_data['monthHighChange'])
        and abs(regression_data['week2LowChange']) > abs(regression_data['week2HighChange'])
        and -7 < regression_data['PCT_day_change'] < -2
        and -7 < regression_data['PCT_change'] < -2
        and regression_data['forecast_day_PCT7_change'] > 3 
        and regression_data['forecast_day_PCT10_change'] > 3
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'morningBuy-LastDayDown-UpTrend')
        if((regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change_pre2'] > 0)
            ):
            if(regression_data['bar_low'] < regression_data['bar_low_pre2']):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'mayFollowLast3DayTrendSellOrBuy-BrokenLast2DaySupport')
            elif(regression_data['bar_low'] > regression_data['bar_low_pre2']
                and regression_data['bar_low'] < regression_data['bar_low_pre1']
                and regression_data['PCT_day_change_pre1'] > 1 and regression_data['PCT_day_change_pre2'] > 1
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'mayMorning-BuyOrSell-5minutesMidcapTrend-last2DayUp')
        elif((regression_data['PCT_day_change_pre2'] > 0 and regression_data['PCT_day_change_pre3'] > 0)
            and regression_data['PCT_day_change_pre1'] < 0
            ):
            if(regression_data['bar_low'] < regression_data['bar_low_pre4']):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'mayFollowLast3DayTrendSellOrBuy-BrokenLast3DaySupport')
            elif(regression_data['bar_low'] > regression_data['bar_low_pre4']
                and regression_data['bar_low'] < regression_data['bar_low_pre3']
                and regression_data['PCT_day_change_pre2'] > 1 and regression_data['PCT_day_change_pre3'] > 1
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'mayMorning-BuyOrSell-5minutesMidcapTrend-lastDayDown')
        elif((regression_data['PCT_day_change'] > 1.5
                and regression_data['PCT_day_change_pre1'] > 0
                and regression_data['PCT_day_change_pre2'] > 0
                )
            ):
            if(regression_data['PCT_day_change_pre1'] > 1.5):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'mayBuy-Last3DayUp')
            elif(regression_data['PCT_day_change_pre1'] < 1):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'mayFollowMarketTrend')        
        elif(regression_data['PCT_day_change_pre2'] > 0
            and (regression_data['low'] < regression_data['low_pre3']
                or regression_data['bar_low'] < regression_data['bar_low_pre2']
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'mayMorning(DOWNTRENDTREND-DOWNMARKET)Sell(UPTREND-UPMARKET)Buy')
        flag = True
    elif(regression_data['monthHighChange'] > -4 and regression_data['week2HighChange'] > -4 and regression_data['weekHighChange'] > -4
        and abs(regression_data['monthLowChange']) > abs(regression_data['monthHighChange'])
        and abs(regression_data['week2LowChange']) > abs(regression_data['week2HighChange'])
        and -7 < regression_data['PCT_day_change'] < -2
        and -7 < regression_data['PCT_change'] < -2
        and regression_data['PCT_day_change_pre1'] > 0 
        and regression_data['PCT_day_change_pre2'] > 0
        and regression_data['forecast_day_PCT7_change'] > 3 
        and regression_data['forecast_day_PCT10_change'] > 3
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'morningBuy-LastDayDown-UpTrend')
        if((regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change_pre2'] > 0)
            ):
            if(regression_data['bar_low'] < regression_data['bar_low_pre2']):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'mayFollowLast3DayTrendSellOrBuy-BrokenLast2DaySupport')
            elif(regression_data['bar_low'] > regression_data['bar_low_pre2']
                and regression_data['bar_low'] < regression_data['bar_low_pre1']
                and regression_data['PCT_day_change_pre1'] > 1 and regression_data['PCT_day_change_pre2'] > 1
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'mayMorning-BuyOrSell-5minutesMidcapTrend-last2DayUp')
        elif((regression_data['PCT_day_change_pre2'] > 0 and regression_data['PCT_day_change_pre3'] > 0)
            and regression_data['PCT_day_change_pre1'] < 0
            ):
            if(regression_data['bar_low'] < regression_data['bar_low_pre4']):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'mayFollowLast3DayTrendSellOrBuy-BrokenLast3DaySupport')
            elif(regression_data['bar_low'] > regression_data['bar_low_pre4']
                and regression_data['bar_low'] < regression_data['bar_low_pre3']
                and regression_data['PCT_day_change_pre2'] > 1 and regression_data['PCT_day_change_pre3'] > 1
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'mayMorning-BuyOrSell-5minutesMidcapTrend-lastDayDown')
        elif((regression_data['PCT_day_change'] > 1.5
                and regression_data['PCT_day_change_pre1'] > 0
                and regression_data['PCT_day_change_pre2'] > 0
                )
            ):
            if(regression_data['PCT_day_change_pre1'] > 1.5):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'mayBuy-Last3DayUp')
            elif(regression_data['PCT_day_change_pre1'] < 1):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'mayFollowMarketTrend')         
        elif(regression_data['PCT_day_change_pre2'] > 0
            and (regression_data['low'] < regression_data['low_pre3']
                or regression_data['bar_low'] < regression_data['bar_low_pre2']
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'mayMorning(DOWNTRENDTREND-DOWNMARKET)Sell(UPTREND-UPMARKET)Buy')
        flag = True
    return flag


def buy_high_volatility(regression_data, regressionResult):
    flag = False
    ws = None
    
    if(regression_data['year2HighChange'] > -5):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'year2HighChangeGT-5')
    elif(regression_data['year2LowChange'] < 5):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'year2LowLT5')

    if (buy_high_volatility_shortUpTrend(regression_data, regressionResult)):
        flag = True

    if(buy_high_volatility_boundary(regression_data, regressionResult)):
        flag = True 
        
    if(buy_high_volatility_monthHighNotReached(regression_data, regressionResult)):
        flag = True
        
    if(buy_high_volatility_pre1pre2doji(regression_data, regressionResult)):
        flag = True
        
    if(buy_high_volatility_riskyUptrendSell(regression_data, regressionResult)):
        flag = True
        
    if(buy_high_volatility_lastDayDown(regression_data, regressionResult)):
        flag = True
        
    if('checkBuyConsolidationBreakUp-2week' in regression_data['filter']
        and 1 < regression_data['PCT_day_change'] < 4
        and 1 < regression_data['PCT_change'] < 4
        and (regression_data['PCT_day_change_pre1'] < regression_data['PCT_day_change'] / 2
            # or 'MLBuy' in regression_data['filter']
            # or 'brokenToday' in regression_data['filter']
            )
        and (regression_data['PCT_day_change'] > 2 
            # or 'MLBuy' in regression_data['filter']
            or 'brokenToday' in regression_data['filter']
            )
        and (regression_data['month3HighChange'] < -5 or abs_month3High_more_than_month3Low(regression_data))
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'checkBuyConsolidationBreakUp(NotShapeV)-2week')
        flag = True
    elif(-1.5 < regression_data['PCT_day_change'] < 1.5 and -1.5 < regression_data['PCT_change'] < 1.5
        and -1.5 < regression_data['PCT_day_change_pre1'] < 1.5 and -1.5 < regression_data['PCT_change_pre1'] < 1.5
        and -1.5 < regression_data['PCT_day_change_pre2'] < 1.5 and -1.5 < regression_data['PCT_change_pre2'] < 1.5
        and -2.5 < regression_data['PCT_day_change_pre3'] < 2.5 and -2.5 < regression_data['PCT_change_pre3'] < 2.5
        and -2.5 < regression_data['PCT_day_change_pre4'] < 2.5 and -2.5 < regression_data['PCT_change_pre4'] < 2.5
        and -1.5 < regression_data['forecast_day_PCT_change'] < 1.5
        and -1.5 < regression_data['forecast_day_PCT2_change'] < 1.5
        and -1.5 < regression_data['forecast_day_PCT3_change'] < 1.5
        and -1.5 < regression_data['forecast_day_PCT4_change'] < 1.5
        and -1.5 < regression_data['forecast_day_PCT5_change'] < 1.5
        and (regression_data['forecast_day_PCT7_change'] < -2 or regression_data['forecast_day_PCT10_change'] < -2)
        and regression_data['monthLowChange'] > 4
        and abs(regression_data['monthHighChange']) < abs(regression_data['monthLowChange'])
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'consolidationBuyCandidate')
        flag = True
              
    if('upTrend' in regression_data['series_trend'] 
        or 'UpTrend' in regression_data['series_trend'] 
        or 'trendUp' in regression_data['series_trend']
        or 'SMA9GT' in regression_data['series_trend']
        ):
        if(regression_data['PCT_day_change_pre1'] < -0.75 
            and regression_data['PCT_day_change'] < 0
            and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change'])
            and regression_data['low'] > regression_data['low_pre1']
            and 'DOJI' in regression_data['filter5']
            and regression_data['forecast_day_PCT5_change'] > 3
            and regression_data['forecast_day_PCT7_change'] > 3
            and regression_data['forecast_day_PCT10_change'] > 3
            and high_tail_pct(regression_data) < 2.5
            and low_tail_pct(regression_data) < 1.5
            ):
            # print(regression_data['scrip'])
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'UPTREND:mayContinueUpTrend-DOJI')
            flag = True
        elif(regression_data['PCT_day_change_pre1'] < 0 
            and regression_data['PCT_day_change'] < 0
            # and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change'])
            and regression_data['bar_low_pre1'] > regression_data['bar_low']
            # and regression_data['bar_low_pre1'] > regression_data['bar_low_pre2']
            and (regression_data['low'] > regression_data['low_pre2']
                 or regression_data['low'] > regression_data['low_pre3']
                )
            and 'DOJI' in regression_data['filter5']
            and regression_data['forecast_day_PCT5_change'] > 3
            and regression_data['forecast_day_PCT7_change'] > 3
            and regression_data['forecast_day_PCT10_change'] > 3
            and high_tail_pct(regression_data) < 2.5
            and low_tail_pct(regression_data) < 3.5
            ):
            # print(regression_data['scrip'])
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'UPTREND:mayContinueUpTrend-DOJI-Risky')
            flag = True
        elif(regression_data['PCT_day_change_pre2'] > 0.5
            and regression_data['PCT_day_change_pre1'] < -0.5 
            and regression_data['PCT_day_change'] < -0.5
            and abs(regression_data['PCT_day_change_pre1']) < abs(regression_data['PCT_day_change'])
            and regression_data['bar_low_pre1'] > regression_data['bar_low']
            and regression_data['low'] > regression_data['low_pre3']
            and regression_data['forecast_day_PCT5_change'] > 3
            and regression_data['forecast_day_PCT7_change'] > 3
            and regression_data['forecast_day_PCT10_change'] > 5
            and (regression_data['forecast_day_PCT10_change'] > regression_data['forecast_day_PCT7_change'] > regression_data['forecast_day_PCT5_change']
                or (regression_data['forecast_day_PCT4_change'] > regression_data['forecast_day_PCT3_change'] + 2
                    and regression_data['forecast_day_PCT3_change'] > regression_data['forecast_day_PCT2_change'] + 2
                    )
               )
            and high_tail_pct(regression_data) < 2.5
            and low_tail_pct(regression_data) < 2.5
            ):
            # print(regression_data['scrip'])
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'UPTREND:mayContinueUpTrend-Last2DayDown')
            flag = True

    if (regression_data['forecast_day_PCT5_change'] > regression_data['forecast_day_PCT4_change'] > regression_data[
        'forecast_day_PCT3_change'] > regression_data['forecast_day_PCT2_change'] > regression_data[
        'forecast_day_PCT_change'] > -1
        and regression_data['year2HighChange'] < 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'CheckChartDown-UptrendLast5Day')
        flag = True

    if('%%' in regression_data['filter']
        or '$$' in regression_data['filter']
        or 'VOL:' in regression_data['filter']):
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
                add_in_csv(regression_data, regressionResult, ws, None, None, 'CommonHL:mayBuyUpContinueGT3')
            elif(regression_data['forecast_day_PCT5_change'] < 10 
                and regression_data['forecast_day_PCT10_change'] < 10
                and regression_data['yearHighChange'] < -5
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'CommonHL:mayBuyUpContinueGT3-Risky')
        elif(2 < regression_data['PCT_day_change'] < 4 and 1 < regression_data['PCT_change'] < 5):
            if(regression_data['monthLowChange'] < 5):
                # add_in_csv(regression_data, regressionResult, ws, None, None, 'CommonHL:mayBuyUpContinueLT3')
                add_in_csv(regression_data, regressionResult, ws, None, None, None) 
            else:
                # add_in_csv(regression_data, regressionResult, ws, None, None, 'CommonHL:mayBuyUpContinueLT3-Risky')
                add_in_csv(regression_data, regressionResult, ws, None, None, None)
                
    elif(high_tail_pct(regression_data) < 2 and low_tail_pct(regression_data) < 2
        and (regression_data['monthLowChange'] < 5 and regression_data['month3LowChange'] < 5 
             and regression_data['month3HighChange'] < 0 and regression_data['month6HighChange'] < -5)
        and (regression_data['forecast_day_PCT10_change'] < 15)
        and (regression_data['forecast_day_PCT5_change'] < 10 or regression_data['forecast_day_PCT10_change'] < 10)  
        and (regression_data['PCT_day_change_pre1'] < 0 or regression_data['PCT_day_change_pre2'] < 0 or regression_data['PCT_day_change_pre3'] < 0)
        ):
        if(3.5 < regression_data['PCT_day_change'] < 6.0 and 2.5 < regression_data['PCT_change'] < 7):
            if(abs(regression_data['PCT_day_change']) < abs(regression_data['PCT_day_change_pre1'])):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'CommonHL:mayBuyUpContinueGT3-AfterSomeDownCheckBase')
            elif(2.5 < regression_data['PCT_day_change'] < 4.5 and 2.5 < regression_data['PCT_change'] < 5):
                # add_in_csv(regression_data, regressionResult, ws, None, None, 'CommonHL-(10:00to12:00):mayBuyUpContinueGT3-AfterSomeDownCheckBase')
                add_in_csv(regression_data, regressionResult, ws, None, None, None)
                
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
        if(2 < regression_data['PCT_day_change'] < 4 and 2 < regression_data['PCT_change'] < 4
            and (regression_data['PCT_day_change_pre1'] > 1.5 and regression_data['PCT_day_change_pre2'] < -1.5)
            and (regression_data['forecast_day_PCT7_change'] < 1 and regression_data['forecast_day_PCT10_change'] < 1)
            ):
            # add_in_csv(regression_data, regressionResult, ws, None, None, 'AF:maySellReversalInSmallUptrend')
            add_in_csv(regression_data, regressionResult, ws, None, None, None)
        elif(3 < regression_data['PCT_day_change'] < 4.0 and 1 < regression_data['PCT_change'] < 5
            and ((regression_data['forecast_day_PCT3_change'] > 0 and regression_data['forecast_day_PCT4_change'] > 0)
                or regression_data['forecast_day_PCT5_change'] > 0
                or regression_data['forecast_day_PCT7_change'] > 0
                or regression_data['forecast_day_PCT10_change'] > 0
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'mayBuyUpContinueGT3')
        elif(2 < regression_data['PCT_day_change'] < 4 and 1 < regression_data['PCT_change'] < 4
            and regression_data['PCT_day_change_pre2'] > -1 
            and regression_data['high'] < regression_data['high_pre2']
            ):
            # add_in_csv(regression_data, regressionResult, ws, None, None, 'AF:mayBuyUpContinueLT3')
            add_in_csv(regression_data, regressionResult, ws, None, None, None)

            
def buy_hltf_low_tail(regression_data, regressionResult, reg, ws):
    if(high_tail_pct(regression_data) <= 2 and 3 <= low_tail_pct(regression_data) <= 5.5
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
        add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:mayBuyTail-tailGT2-allDayLT0')
    elif(high_tail_pct(regression_data) <= 1.5 and 2 <= low_tail_pct(regression_data) <= 5.5
        and 0 < regression_data['PCT_day_change'] < 5 and -5 < regression_data['PCT_change'] < 5
        and regression_data['bar_high'] > regression_data['bar_high_pre1'] > regression_data['bar_high_pre2']
        and regression_data['forecast_day_PCT_change'] > 0
        and regression_data['forecast_day_PCT2_change'] > 0
        and regression_data['forecast_day_PCT7_change'] < 0
        and regression_data['forecast_day_PCT10_change'] < 0
        and regression_data['SMA25'] > 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:mayBuyTail-tailGT2-7,10thDayLT0')
    elif(high_tail_pct(regression_data) <= 1 and 2 <= low_tail_pct(regression_data) <= 6
        and -5 < regression_data['PCT_day_change'] < -1 and -5 < regression_data['PCT_change'] < -1  
#         and regression_data['forecast_day_PCT2_change'] < 0 and regression_data['high'] < regression_data['high_pre2']
#         and regression_data['forecast_day_PCT3_change'] < 0 and regression_data['high'] < regression_data['high_pre3']
#         and regression_data['forecast_day_PCT4_change'] < 0 and regression_data['high'] < regression_data['high_pre4']
        and regression_data['forecast_day_PCT2_change'] < 0
        and regression_data['forecast_day_PCT3_change'] < 0
        and regression_data['forecast_day_PCT4_change'] < 0
        and regression_data['forecast_day_PCT5_change'] < 5
        # and regression_data['forecast_day_PCT7_change'] < 10
        # and regression_data['forecast_day_PCT10_change'] < 10
        and (regression_data['forecast_day_PCT7_change'] < 5 or regression_data['forecast_day_PCT10_change'] < 5)
        and (regression_data['forecast_day_PCT7_change'] > 0 or regression_data['forecast_day_PCT10_change'] > 0)
        ):
#            if(regression_data['forecast_day_PCT7_change'] > -5
#                or regression_data['forecast_day_PCT10_change'] > -5
#                ): 
#                add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:mayBuyTail-tailGT2-2,3,4thDayLT0')
#            else:
        add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:mayBuyTail-tailGT2-2,3,4thDayLT0')
    elif(high_tail_pct(regression_data) < 2 and 1.5 < low_tail_pct(regression_data) < 2.1
        and (('MayBuy-CheckChart' in regression_data['filter1']) or ('MayBuyCheckChart' in regression_data['filter1']))
        and (0 < regression_data['PCT_day_change'] < 0.75) and (-1 < regression_data['PCT_change'] < 2.5)
        and (regression_data['PCT_day_change'] > 0 or regression_data['PCT_change_pre1'] > 0)
        and (((regression_data['PCT_change_pre2'] < 0 or regression_data['PCT_change_pre3'] < 0)
                 and (regression_data['PCT_change_pre1'] > 0 or regression_data['PCT_change_pre2'] > 0 or regression_data['PCT_change_pre3'] > 0)
                 and regression_data['PCT_day_change'] > 0
                 )
            )
        and low_tail_pct(regression_data) > high_tail_pct(regression_data)
        ): 
        add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:mayBuyLowTail-LastDayMarketDown')
    elif(high_tail_pct(regression_data) <= 1 and 1.3 <= low_tail_pct(regression_data) <= 2
        and low_tail_pct(regression_data) > (high_tail_pct(regression_data) + 0.5)
        and low_tail_pct(regression_data) > (abs(regression_data['PCT_day_change']) + 0.5)
        ):
        if(-3 < regression_data['PCT_day_change'] < -0.5 and -3 < regression_data['PCT_change'] < -0.5
            and (regression_data['PCT_day_change'] < -1 or regression_data['PCT_change'] < -1)
            and abs(regression_data['PCT_day_change']) < low_tail_pct(regression_data)
            and regression_data['forecast_day_PCT2_change'] < 0
            and regression_data['forecast_day_PCT3_change'] < 0
            and regression_data['forecast_day_PCT4_change'] < 0
            and regression_data['forecast_day_PCT5_change'] < 5
            and regression_data['forecast_day_PCT7_change'] < 10
            and regression_data['forecast_day_PCT10_change'] < 10
            and (regression_data['forecast_day_PCT7_change'] > -5 or regression_data['forecast_day_PCT10_change'] > -5)
            and (regression_data['forecast_day_PCT7_change'] < 5 or regression_data['forecast_day_PCT10_change'] < 5)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:mayBuyTail-2,3,4thDayLT0')   
    
    if((3.5 < high_tail_pct(regression_data) < 5 or (2.5 < high_tail_pct(regression_data) < 5 and low_tail_pct(regression_data) < 1.5))
        and low_tail_pct(regression_data) < 3.5
        and regression_data['SMA4'] < 0 and regression_data['SMA4_2daysBack'] < 0
        and regression_data['SMA9'] < 0 and regression_data['SMA9_2daysBack'] < 0
        and regression_data['SMA25'] < -1
        and (regression_data['low'] < regression_data['low_pre1'] > regression_data['low_pre2']
             or regression_data['bar_low'] < regression_data['bar_low_pre1'] < regression_data['bar_low_pre2'])
        and regression_data['forecast_day_PCT4_change'] < 0
        and regression_data['forecast_day_PCT5_change'] < 0
        and regression_data['forecast_day_PCT7_change'] > -15 and regression_data['forecast_day_PCT10_change'] > -15
        and regression_data['PCT_day_change'] > -3 and regression_data['PCT_change'] > -5
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:sellHighUpperTail-Continue')
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
        add_in_csv(regression_data, regressionResult, ws, None, None, None)
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
        and (abs_month3High_less_than_month3Low(regression_data)) 
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:sellStockInDowntrend')
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
        add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:buyStockInDowntrendReversal')  
    elif((3.5 < high_tail_pct(regression_data) < 6 or (2.5 < high_tail_pct(regression_data) < 5.5 and low_tail_pct(regression_data) < 1.5)) 
        and low_tail_pct(regression_data) < 3.5
        and (regression_data['PCT_day_change'] < (high_tail_pct(regression_data) * 2))
        ):
        if(regression_data['PCT_day_change'] > 0 and regression_data['PCT_change'] > 0
            and regression_data['PCT_day_change_pre1'] > 1
            and regression_data['PCT_day_change_pre2'] < 0
            and regression_data['forecast_day_PCT7_change'] < 0 and regression_data['forecast_day_PCT10_change'] < 0
            and regression_data['PCT_day_change'] < high_tail_pct(regression_data)
            ):
            if(regression_data['forecast_day_PCT7_change'] < -10 or regression_data['forecast_day_PCT10_change'] < -10):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:sellHighUpperTail-StockInDowntrend')
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:sellHighUpperTail-LastDayMarketUp')
        elif(regression_data['forecast_day_PCT_change'] > 1
            and (((regression_data['forecast_day_PCT7_change'] < 5 and regression_data['forecast_day_PCT10_change'] < 5
                    and (regression_data['forecast_day_PCT7_change'] < 0 or regression_data['forecast_day_PCT10_change'] < 0)
                    )
                  or regression_data['forecast_day_PCT10_change'] < 0)
                )
            ):
            if(regression_data['forecast_day_PCT_change'] > 0
                and regression_data['forecast_day_PCT2_change'] > 0
                and regression_data['forecast_day_PCT3_change'] > 0
                # and is_algo_sell(regression_data) 
                and regression_data['forecast_day_PCT7_change'] < 0
                and regression_data['forecast_day_PCT10_change'] < 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None)
            elif(regression_data['forecast_day_PCT7_change'] < 0 and regression_data['forecast_day_PCT10_change'] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:buyHighUpperTail-Reversal-LastDayMarketDown')
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:buyHighUpperTail-Reversal-LastDayMarketDown')
        elif(regression_data['PCT_day_change'] < -1 and regression_data['PCT_change'] < -1
            and regression_data['forecast_day_PCT7_change'] < -2
            and regression_data['forecast_day_PCT10_change'] < -2
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:buyHighUpperTail-Reversal-LastDayMarketDown')
        elif(3.5 < high_tail_pct(regression_data) < 6
            and (regression_data['PCT_day_change_pre1'] < -1.5 or regression_data['PCT_day_change_pre2'] < -1.5)
            and regression_data['forecast_day_PCT7_change'] < -2
            and regression_data['forecast_day_PCT10_change'] < -2
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:buyHighUpperTail-Reversal-LastDayMarketDown')
    elif(2 < low_tail_pct_pre1(regression_data) < 6
        and 2.9 < regression_data['PCT_day_change'] < 4.1
        and abs(regression_data['PCT_day_change_pre1']) < 1.5
        and regression_data['PCT_day_change_pre2'] < -1
        and abs(regression_data['PCT_day_change_pre2']) > abs(regression_data['PCT_day_change_pre1'])
        # and regression_data['high'] >= regression_data['bar_high_pre2']
        # and abs_month6High_less_than_month6Low(regression_data)
        and low_tail_pct(regression_data) < 1.5
        and high_tail_pct(regression_data) < 1.5
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:sellHighLowerTailPre1-Reversal-LastDayMarketUp')
        
    if((low_tail_pct(regression_data) > 1.5 and high_tail_pct(regression_data) < 1.5 and high_tail_pct(regression_data) < low_tail_pct(regression_data))
        and ((low_tail_pct_pre1(regression_data) > 1.5 and regression_data['low_pre1'] < regression_data['low'] and regression_data['high_pre1'] < regression_data['high'] and high_tail_pct_pre1(regression_data) < low_tail_pct_pre1(regression_data))
             or (low_tail_pct_pre2(regression_data) > 1.5 and regression_data['low_pre2'] < regression_data['low'] and regression_data['high_pre2'] < regression_data['high'] and high_tail_pct_pre2(regression_data) < low_tail_pct_pre2(regression_data))
             )
        and (0 < regression_data['PCT_day_change'] < 2)
        # and (regression_data['forecast_day_PCT2_change'] < 0 or regression_data['forecast_day_PCT3_change'] < 0 or regression_data['forecast_day_PCT4_change'] < 0)
        # and (regression_data['forecast_day_PCT5_change'] > 0 or regression_data['forecast_day_PCT7_change'] > 0 or regression_data['forecast_day_PCT10_change'] > 0)
        and (# abs_monthHigh_more_than_monthLow(regression_data)
            abs_week2High_more_than_week2Low(regression_data)
            or regression_data['week2LowChange'] < 0
            ) 
        ):
        if(regression_data['week2LowChange'] == regression_data['monthLowChange']):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:buyHighLowerTailPre')
        elif(abs_monthHigh_more_than_monthLow(regression_data)):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:buy(DOWNTREND)sell:HighLowerTailPre')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:buyHighLowerTailPre')
    elif((low_tail_pct(regression_data) > 1.5 and high_tail_pct(regression_data) < 1.5 and high_tail_pct(regression_data) < low_tail_pct(regression_data))
        and ((low_tail_pct_pre1(regression_data) > 1.5 and regression_data['low_pre1'] < regression_data['low'] and regression_data['high_pre1'] < regression_data['high'] and high_tail_pct_pre1(regression_data) < low_tail_pct_pre1(regression_data))
             or (low_tail_pct_pre2(regression_data) > 1.5 and regression_data['low_pre2'] < regression_data['low'] and regression_data['high_pre2'] < regression_data['high'] and high_tail_pct_pre2(regression_data) < low_tail_pct_pre2(regression_data))
             )
        and (-2 < regression_data['PCT_day_change'] < 2)
        and (regression_data['forecast_day_PCT2_change'] < 0 and regression_data['forecast_day_PCT3_change'] < 0)
        and (abs_monthHigh_less_than_monthLow(regression_data)
            or abs_week2High_less_than_week2Low(regression_data)
            )
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:buyHighLowerTailPre-1')
    elif((low_tail_pct(regression_data) > 1.5 and high_tail_pct(regression_data) < low_tail_pct(regression_data))
        and (low_tail_pct_pre1(regression_data) > 1.5 and high_tail_pct_pre1(regression_data) < low_tail_pct_pre1(regression_data))
        and regression_data['low_pre1'] > regression_data['low']
        and regression_data['PCT_day_change'] < 0
        and regression_data['PCT_day_change_pre1'] < 0 
        and abs_week2High_more_than_week2Low(regression_data)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:buyHighLowerTailPre-last2DayDown')
    
    if((high_tail_pct(regression_data) > 1.5 and high_tail_pct(regression_data) > low_tail_pct(regression_data))
        and ((high_tail_pct_pre1(regression_data) > 1.5 and regression_data['PCT_day_change'] > 0 and regression_data['high_pre1'] < regression_data['high'] and high_tail_pct_pre1(regression_data) > low_tail_pct_pre1(regression_data))
             or (high_tail_pct_pre2(regression_data) > 1.5 and regression_data['PCT_day_change'] > 0 and regression_data['high_pre2'] < regression_data['high'] and high_tail_pct_pre2(regression_data) > low_tail_pct_pre2(regression_data))
             )
        and (-2 < regression_data['PCT_day_change'] < 0)
        and (abs_week2High_less_than_week2Low(regression_data))
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:buyHighUpperTailPre')
    elif((high_tail_pct(regression_data) > 1.5 and low_tail_pct(regression_data) > 1.5)
        and (high_tail_pct_pre1(regression_data) > 1.5 and regression_data['low_pre1'] < regression_data['low'] and high_tail_pct_pre1(regression_data) > low_tail_pct_pre1(regression_data))
        and (-2 < regression_data['PCT_day_change'] < 0)
        and (regression_data['forecast_day_PCT2_change'] > 0 and regression_data['forecast_day_PCT3_change'] > 0)
        and (
            abs_week2High_less_than_week2Low(regression_data)
            or regression_data['week2HighChange'] > 0
            )
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:buyHighUpperTailPre-1')


def buy_tail_reversal_filter(regression_data, regressionResult, reg, ws):
    if(('MayBuy-CheckChart' in regression_data['filter1']) or ('MayBuyCheckChart' in regression_data['filter1'])):
        if(-2 < regression_data['PCT_day_change'] < -1
            and -2 < regression_data['PCT_change'] < -1
            and regression_data['PCT_day_change_pre1'] < -1
            and regression_data['PCT_day_change_pre2'] < 0
            and regression_data['PCT_day_change_pre3'] < 0
            and regression_data['monthLow'] >= regression_data['low']
            and (regression_data['forecast_day_PCT7_change'] < -10 or regression_data['forecast_day_PCT10_change'] < -10)
            # and regression_data['PCT_day_change_pre3'] < regression_data['PCT_day_change']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '$$MayBuy-CheckChart(downTrend-mayReverseLast4DaysDown)')
        elif(-2 < regression_data['PCT_day_change'] < -1
            and -2 < regression_data['PCT_change'] < -1
            and regression_data['PCT_day_change_pre1'] < -1
            and regression_data['PCT_day_change_pre2'] < 0
            and regression_data['PCT_day_change_pre3'] < 0
            and regression_data['monthLow'] >= regression_data['low']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '$$MayBuy-CheckChart(downTrend-mayReverseLast4DaysDown)-Risky')
    
    if(-1.3 < regression_data['monthLowChange'] < 0.75
        and regression_data['monthHighChange'] < -5
        and regression_data['weekLowChange'] < 0
        and abs(regression_data['month3HighChange']) < abs(regression_data['month3LowChange']) and regression_data['month3LowChange'] > 15
        and abs(regression_data['monthHighChange']) > abs(regression_data['monthLowChange'])
        and regression_data['year2LowChange'] > 0
        and (regression_data['PCT_day_change_pre3'] < -1 or regression_data['PCT_day_change_pre4'] < -1)
        and (low_tail_pct(regression_data) >= 1.5 and (low_tail_pct(regression_data) > (abs(regression_data['PCT_day_change']) / 3)))
        ):
        if(high_tail_pct(regression_data) > 1.5):
            add_in_csv(regression_data, regressionResult, ws, None, None, '$$MaySellContinue-CheckChart(inuptrend-monthlow)-highTail')
        elif(regression_data['monthHighChange'] < -10): 
            add_in_csv(regression_data, regressionResult, ws, None, None, '$$MayBuy-CheckChart-baseLine(inuptrend-monthlow)-MHCLT(-10)')
        elif(regression_data['PCT_day_change'] < 0): 
            add_in_csv(regression_data, regressionResult, ws, None, None, '$$MayBuy-CheckChart-baseLine(inuptrend-monthlow)-PCTDayChangeLT0')
        elif(regression_data['PCT_day_change'] > 2 and regression_data['monthHighChange'] > -10):
            add_in_csv(regression_data, regressionResult, ws, None, None, '$$MaySellContinue-CheckChart(inuptrend-monthlow)-PCTDayChangeGT2')
    elif(-1.3 < regression_data['monthLowChange'] < 3
        and regression_data['monthHighChange'] < -5
        and regression_data['weekLowChange'] < 0
        and abs(regression_data['month3HighChange']) < abs(regression_data['month3LowChange']) and regression_data['month3LowChange'] > 15
        and abs(regression_data['monthHighChange']) > abs(regression_data['monthLowChange'])
        and regression_data['year2LowChange'] > 0
        and regression_data['PCT_day_change'] > 1
        and (regression_data['PCT_day_change_pre3'] < -1 or regression_data['PCT_day_change_pre4'] < -1)
        and (low_tail_pct(regression_data) >= 1 or (low_tail_pct(regression_data) > (abs(regression_data['PCT_day_change']) / 3)))
        ):
        if(high_tail_pct(regression_data) > 1.5):
            add_in_csv(regression_data, regressionResult, ws, None, None, '$$MaySellContinue-CheckChart(inuptrend-monthlow)-highTail')
        elif(regression_data['monthHighChange'] < -10):
            add_in_csv(regression_data, regressionResult, ws, None, None, '$$(UPTREND-OR-GLOBALUP)MayBuy-CheckChart-baseLine(inuptrend-monthlow)-MHCLT(-10)')
        elif(regression_data['PCT_day_change'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, '$$(UPTREND-OR-GLOBALUP)MayBuy-CheckChart-baseLine(inuptrend-monthlow)-PCTDayChangeLT0')
        elif(regression_data['PCT_day_change'] > 2 and regression_data['monthHighChange'] > -10):
            add_in_csv(regression_data, regressionResult, ws, None, None, '$$MaySellContinue-CheckChart(inuptrend-monthlow)-PCTDayChangeGT2')
    
    if((-0.5 < regression_data['PCT_change'] < 0.5)
        and (-1 < regression_data['PCT_day_change'] < 0)
        and high_tail_pct(regression_data) < 0.5
        and (0.6 <= low_tail_pct(regression_data) < 1.5)
        and (low_tail_pct(regression_data) - high_tail_pct(regression_data)) >= 0.6
        # and (regression_data['score'] == '10')
        and (regression_data['PCT_day_change_pre1'] > 2)
        ):
        if(abs_month3High_more_than_month3Low(regression_data)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'MayBuyCheckChart-(|`|_|)')
    elif((-2.5 < regression_data['PCT_day_change'] <= -1)
        and (-4 < regression_data['PCT_change'] <= -1)
        ):
        if(('MayBuyCheckChart' in regression_data['filter1'])
            and (-15 < regression_data['forecast_day_PCT5_change'] < -1)
            and (-15 < regression_data['forecast_day_PCT7_change'] < -1)
            and (-15 < regression_data['forecast_day_PCT10_change'] < -1)
            and high_tail_pct(regression_data) < 0.8
            ):
            if(1.8 < low_tail_pct(regression_data) < 2.5):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'MayBuyCheckChart-(IndexNotUpInSecondHalf)')
    
    if('MayBuy-CheckChart' in regression_data['filter1']):
        if(regression_data['PCT_day_change_pre1'] > 2
            and regression_data['PCT_day_change_pre2'] < 0
            and is_ema14_sliding_up(regression_data)
            and (last_5_day_all_up_except_today(regression_data) != True)
            and regression_data['bar_low'] > regression_data['bar_low_pre1']
            and regression_data['low'] > regression_data['low_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'MayBuy-CheckChart(upTrend-lastDayDown)')            
    
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
            add_in_csv(regression_data, regressionResult, ws, None, None, "MayBuyCheckChart-last3DayDown")
        elif((-2 <= regression_data['PCT_day_change'] < -1) and (-2 <= regression_data['PCT_change'] < 0)
            and 3 > low_tail_pct(regression_data) > 1.8
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, "MayBuyCheckChart-Risky")
    elif(('MayBuyCheckChart' in regression_data['filter1'])
        and ('Reversal' not in regression_data['filter3'])
        and high_tail_pct(regression_data) < 0.5
        ):
        if((-5 <= regression_data['PCT_day_change'] < -3) and (-6 <= regression_data['PCT_change'] < -2)
            and 5 > low_tail_pct(regression_data) > 2.8
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, "MayBuyCheckChart-PCTDayChangeLT(-3)BigHighTail")
            
    if(regression_data['year2LowChange'] > 3
        and regression_data['low'] == regression_data['weekLow']
        and low_tail_pct(regression_data) > 1.5
        and (regression_data['PCT_day_change'] < 2)
        ):
        if(regression_data['weekLow'] < regression_data['week2Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, "weekLowLTweek2")
        if(regression_data['monthLowChange'] < 3
            and regression_data['monthLow'] != regression_data['weekLow']
            and regression_data['monthLow'] == regression_data['month2Low']
            # and (is_algo_buy(regression_data)
                # or ((regression_data['bar_low'] - regression_data['month2BarLow'])/regression_data['month2BarLow'])*100 < 1.5
                # or regression_data['PCT_day_change'] > 0
                # )
            ):
            if(regression_data['monthLowChange'] < -5):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLowChangeLT-5")
            elif(regression_data['monthLowChange'] < -4):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLowChangeLT-4")
            elif(regression_data['monthLowChange'] < -3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLowChangeLT-3")
            elif(regression_data['monthLowChange'] < -2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLowChangeLT-2")
            elif(regression_data['monthLowChange'] < -1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLowChangeLT-1")
            elif(regression_data['monthLowChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLowChangeLT0")
            elif(regression_data['monthLowChange'] < 1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLowChangeLT1")     
            elif(regression_data['monthLowChange'] < 2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLowChangeLT2")
            elif(regression_data['monthLowChange'] < 3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLowChangeLT3")     
            add_in_csv(regression_data, regressionResult, ws, None, None, "MayBuyCheckChart-monthLowReversal")
        elif(regression_data['monthLowChange'] < 3
            and regression_data['monthLow'] != regression_data['weekLow']
            ):
            if(regression_data['monthLowChange'] < -5):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLowChangeLT-5")
            elif(regression_data['monthLowChange'] < -4):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLowChangeLT-4")
            elif(regression_data['monthLowChange'] < -3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLowChangeLT-3")
            elif(regression_data['monthLowChange'] < -2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLowChangeLT-2")
            elif(regression_data['monthLowChange'] < -1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLowChangeLT-1")
            elif(regression_data['monthLowChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLowChangeLT0")
            elif(regression_data['monthLowChange'] < 1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLowChangeLT1")     
            elif(regression_data['monthLowChange'] < 2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLowChangeLT2")
            elif(regression_data['monthLowChange'] < 3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLowChangeLT3") 
            add_in_csv(regression_data, regressionResult, ws, None, None, "MayBuyCheckChart-monthLowReversal-risky")
        elif((regression_data['monthLowChange'] < 5 and regression_data['SMA9'] > 0)
            and regression_data['monthLow'] != regression_data['weekLow']
            and regression_data['monthLow'] == regression_data['month2Low']
            ):
            if(regression_data['monthLowChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLowChangeLT0")
            elif(regression_data['monthLowChange'] < 1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLowChangeLT1")     
            elif(regression_data['monthLowChange'] < 2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLowChangeLT2")
            elif(regression_data['monthLowChange'] < 3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLowChangeLT3")
            elif(regression_data['monthLowChange'] < 4):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLowChangeLT4")
            elif(regression_data['monthLowChange'] < 5):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLowChangeLT5") 
            add_in_csv(regression_data, regressionResult, ws, None, None, "MayBuyCheckChart-monthLowReversal-SMA9GT0")
        elif(regression_data['month2LowChange'] < 3
            and regression_data['month2Low'] != regression_data['weekLow']
            and regression_data['month2Low'] == regression_data['month3Low']
            # and (is_algo_buy(regression_data)
                # or ((regression_data['bar_low'] - regression_data['month3BarLow'])/regression_data['month3BarLow'])*100 < 1.5
                # or regression_data['PCT_day_change'] > 0
                # )
            ):
            if(regression_data['month2LowChange'] < -5):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2LowChangeLT-5")
            elif(regression_data['month2LowChange'] < -4):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2LowChangeLT-4")
            elif(regression_data['month2LowChange'] < -3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2LowChangeLT-3")
            elif(regression_data['month2LowChange'] < -2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2LowChangeLT-2")
            elif(regression_data['month2LowChange'] < -1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2LowChangeLT-1")
            elif(regression_data['month2LowChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2LowChangeLT0")
            elif(regression_data['month2LowChange'] < 1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2LowChangeLT1")     
            elif(regression_data['month2LowChange'] < 2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2LowChangeLT2")
            elif(regression_data['month2LowChange'] < 3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2LowChangeLT3") 
            add_in_csv(regression_data, regressionResult, ws, None, None, "MayBuyCheckChart-month2LowReversal")
        elif(regression_data['month2LowChange'] < 3
            and regression_data['month2Low'] != regression_data['weekLow']
            ):
            if(regression_data['month2LowChange'] < -5):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2LowChangeLT-5")
            elif(regression_data['month2LowChange'] < -4):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2LowChangeLT-4")
            elif(regression_data['month2LowChange'] < -3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2LowChangeLT-3")
            elif(regression_data['month2LowChange'] < -2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2LowChangeLT-2")
            elif(regression_data['month2LowChange'] < -1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2LowChangeLT-1")
            elif(regression_data['month2LowChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2LowChangeLT0")
            elif(regression_data['month2LowChange'] < 1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2LowChangeLT1")     
            elif(regression_data['month2LowChange'] < 2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2LowChangeLT2")
            elif(regression_data['month2LowChange'] < 3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2LowChangeLT3") 
            add_in_csv(regression_data, regressionResult, ws, None, None, "MayBuyCheckChart-month2LowReversal-risky")
        elif((regression_data['month2LowChange'] < 5 and regression_data['SMA9'] > 0)
            and regression_data['month2Low'] != regression_data['weekLow']
            and regression_data['month2Low'] == regression_data['month3Low']
            ):
            if(regression_data['month2LowChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2LowChangeLT0")
            elif(regression_data['month2LowChange'] < 1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2LowChangeLT1")     
            elif(regression_data['month2LowChange'] < 2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2LowChangeLT2")
            elif(regression_data['month2LowChange'] < 3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2LowChangeLT3")
            elif(regression_data['month2LowChange'] < 4):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2LowChangeLT4")
            elif(regression_data['month2LowChange'] < 5):
                add_in_csv(regression_data, regressionResult, ws, None, None, "month2LowChangeLT5")
            add_in_csv(regression_data, regressionResult, ws, None, None, "MayBuyCheckChart-month2LowReversal-SMA9GT0")
        elif(regression_data['month3LowChange'] < 3
            and regression_data['month3Low'] != regression_data['weekLow']
            # and regression_data['month3Low'] != regression_data['low_month3']
            and regression_data['month6Low'] == regression_data['yearLow']
            ):
            if(regression_data['month3LowChange'] < -5):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLow3ChangeLT-5")
            elif(regression_data['month3LowChange'] < -4):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLow3ChangeLT-4")
            elif(regression_data['month3LowChange'] < -3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLow3ChangeLT-3")
            elif(regression_data['month3LowChange'] < -2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLow3ChangeLT-2")
            elif(regression_data['month3LowChange'] < -1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLow3ChangeLT-1")
            elif(regression_data['month3LowChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLow3ChangeLT0")
            elif(regression_data['month3LowChange'] < 1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLow3ChangeLT1")     
            elif(regression_data['month3LowChange'] < 2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLow3ChangeLT2")
            elif(regression_data['month3LowChange'] < 3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLow3ChangeLT3") 
            add_in_csv(regression_data, regressionResult, ws, None, None, "MayBuyCheckChart-month3LowReversal")
        elif(regression_data['month3LowChange'] < 0
            and regression_data['month3Low'] != regression_data['weekLow']
            and regression_data['month3Low'] == regression_data['month6Low']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, "MayBuyCheckChart-month3LowBreakReversal")
        elif(regression_data['month6LowChange'] < 3
            and regression_data['month6Low'] != regression_data['weekLow']
            # and regression_data['month3Low'] != regression_data['low_month6']
            and regression_data['yearLow'] == regression_data['year2Low']
            ):
            if(regression_data['month6LowChange'] < -5):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLow6ChangeLT-5")
            elif(regression_data['month6LowChange'] < -4):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLow6ChangeLT-4")
            elif(regression_data['month6LowChange'] < -3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLow6ChangeLT-3")
            elif(regression_data['month6LowChange'] < -2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLow6ChangeLT-2")
            elif(regression_data['month6LowChange'] < -1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLow6ChangeLT-1")
            elif(regression_data['month6LowChange'] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLow6ChangeLT0")
            elif(regression_data['month6LowChange'] < 1):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLow6ChangeLT1")     
            elif(regression_data['month6LowChange'] < 2):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLow6ChangeLT2")
            elif(regression_data['month6LowChange'] < 3):
                add_in_csv(regression_data, regressionResult, ws, None, None, "monthLow6ChangeLT3") 
            add_in_csv(regression_data, regressionResult, ws, None, None, "MayBuyCheckChart-month6LowReversal")
        elif(regression_data['month6LowChange'] < 0
            and regression_data['month6Low'] != regression_data['weekLow']
            and regression_data['month6Low'] == regression_data['yearLow']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, "MayBuyCheckChart-month6LowBreakReversal")

                          
def buy_year_high(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(float(regression_data['forecast_day_VOL_change']) > 70
       and regression_data['PCT_day_change_pre1'] > -0.5
       and no_doji_or_spinning_buy_india(regression_data)
       ):
        if(-15 < regression_data['yearHighChange'] < -5 and regression_data['yearLowChange'] > 30
            and -0.5 < regression_data['PCT_day_change'] < 2 and regression_data['forecast_day_PCT2_change'] <= 2
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'buyYearHigh-0')
            return True
    elif(float(regression_data['forecast_day_VOL_change']) > 35
       and regression_data['PCT_day_change_pre1'] > -0.5
       and no_doji_or_spinning_buy_india(regression_data)
       ):
        if(-15 < regression_data['yearHighChange'] < -5 and regression_data['yearLowChange'] > 30
            and -0.5 < regression_data['PCT_day_change'] < 2 and regression_data['forecast_day_PCT2_change'] <= 2
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyYearHigh-1')
            return True
    elif(float(regression_data['forecast_day_VOL_change']) > 50
       and regression_data['PCT_day_change_pre1'] > -0.5
       and no_doji_or_spinning_buy_india(regression_data)
       ):
        if(-5 <= regression_data['yearHighChange'] < -1 and regression_data['yearLowChange'] > 15 
            and -0.5 < regression_data['PCT_day_change'] < 2 and regression_data['forecast_day_PCT2_change'] <= 2
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyYearHigh-2')
            return True
    elif(regression_data['PCT_day_change_pre1'] > -0.5):
        if(-5 <= regression_data['yearHighChange'] < -1 and regression_data['yearLowChange'] > 15 
            and -0.5 < regression_data['PCT_day_change'] < 2 and regression_data['forecast_day_PCT2_change'] <= 2
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyYearHigh-3')
            return True
    return False


def buy_year_low(regression_data, regressionResult, reg, ws, ws1):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(1 < regression_data['yearLowChange'] < 5 and regression_data['yearHighChange'] < -30 
        and 2 < regression_data['PCT_day_change'] < 6 and 2 < regression_data['PCT_day_change'] < 6
        and regression_data['forecast_day_PCT2_change'] > 0 and regression_data['forecast_day_PCT_change'] > 0
        and float(regression_data['forecast_day_VOL_change']) > 35
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'BuyYearLow')
        return True
    elif(5 < regression_data['yearLowChange'] < 15 and regression_data['yearHighChange'] < -75 
        and 2 < regression_data['PCT_day_change'] < 5 and 2 < regression_data['PCT_day_change'] < 5
        and 5 > regression_data['forecast_day_PCT2_change'] > -0.5 and regression_data['forecast_day_PCT_change'] > 0
        and float(regression_data['forecast_day_VOL_change']) > 35
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyYearLow1')
        return True
    return False


def buy_down_trend(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    
    if(regression_data['month3LowChange'] < 0 
        and regression_data['monthLowChange'] < 0
        and regression_data['week2LowChange'] < 0
        and regression_data['weekLowChange'] < 0
        and regression_data['monthHighChange'] < -20
        and regression_data['forecast_day_PCT_change'] < 0 and regression_data['forecast_day_PCT2_change'] < 0
        and (regression_data['PCT_day_change_pre1'] > 0 
             or regression_data['PCT_day_change_pre2'] > 0 
             or regression_data['PCT_day_change_pre3'] > 0
             or regression_data['PCT_day_change_pre4'] > 0
            )
        and -3 < regression_data['PCT_day_change'] < -1 and -4 < regression_data['PCT_change'] < -1
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisbuyDownTrend-month3Low')
        return True
    
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
            add_in_csv(regression_data, regressionResult, ws, None, None, 'NearLowYear2')
        elif('BreakLowYear2' in regression_data['filter3']):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'BreakLowYear2')
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyYear2Low')
        return True
    elif(regression_data['forecast_day_PCT10_change'] < -10
        and regression_data['year2HighChange'] < -60
        and regression_data['month3LowChange'] < 10
        and -1.5 < regression_data['forecast_day_PCT_change']
        and 3 < regression_data['PCT_day_change'] < 7
        and 2 < regression_data['PCT_change'] < 8
        and (regression_data['PCT_day_change_pre1'] < -4 or regression_data['PCT_day_change_pre2'] < -4)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellYear2LowContinue')
        return True
    if(all_day_pct_change_negative_except_today(regression_data) 
        and (regression_data['high'] > regression_data['high_pre1'])
        and 0 < regression_data['PCT_day_change'] < 4.5 and 0 < regression_data['PCT_change']
        and (2 < regression_data['PCT_day_change'] or 2 < regression_data['PCT_change'])
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
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyDownTrend-lowTail')
            return True
        elif(ten_days_less_than_minus_ten(regression_data)
            and regression_data['forecast_day_PCT7_change'] < -5
            and regression_data['forecast_day_PCT10_change'] < -10
            and (high_tail_pct(regression_data) > 2.5)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyDownTrend-highTail')
            return True
        elif(last_5_day_all_down_except_today(regression_data)
            and ten_days_less_than_minus_ten(regression_data)
            and regression_data['forecast_day_PCT7_change'] < -5
            and regression_data['forecast_day_PCT10_change'] < -10
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyDownTrend-Risky-0')
            return True
        elif(last_5_day_all_down_except_today(regression_data)
            and ten_days_less_than_minus_seven(regression_data)
            and regression_data['forecast_day_PCT7_change'] < -4
            and regression_data['forecast_day_PCT10_change'] < -4
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyDownTrend-Risky-1')
            return True
        elif(regression_data['forecast_day_PCT7_change'] < -4
            and regression_data['forecast_day_PCT10_change'] < -4
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyDownTrend-Risky-2')
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
        add_in_csv(regression_data, regressionResult, ws, None, None, '##buyTenDaysLessThanMinusTen')
        return True
        
    return False


def buy_up_trend(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    flag = False
    if(('NearLow' in regression_data['filter3'] or 'ReversalLow' in regression_data['filter3'])
        and 'GT0' not in regression_data['filter3']
        and regression_data['SMA4'] > 0
        and regression_data['SMA4_2daysBack'] > 0
        and regression_data['PCT_day_change'] > 0.5 and regression_data['PCT_change'] > 0
        # and (regression_data['PCT_day_change_pre2'] > 0 or regression_data['PCT_day_change_pre3'] > 0)
        and (regression_data['PCT_day_change_pre1'] < 0 or regression_data['PCT_day_change_pre2'] < 0)
        and regression_data['forecast_day_PCT_change'] > 0
        and regression_data['high'] > regression_data['high_pre1']
        ):
        if(regression_data['SMA4'] > regression_data['SMA4_2daysBack']
            and regression_data['SMA9'] > regression_data['SMA9_2daysBack']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyUpTrend-nearLow')
            flag = True
        else:
            #add_in_csv(regression_data, regressionResult, ws, None, None, 'chisUpTrend-Risky-nearLow')
            flag = True
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
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellUpTrend-0')
            flag = True
        elif(regression_data['yearHighChange'] < -10
           and 2 < regression_data['PCT_day_change'] < 3.5 and 2 < regression_data['forecast_day_PCT_change'] < 3
           and regression_data['series_trend'] != 'downTrend'
           and str(regression_data['score']) != '0-1' 
           and regression_data['forecast_day_PCT7_change'] < 0 and -6 < regression_data['forecast_day_PCT10_change'] < 0
           and 1 > low_tail_pct(regression_data) > .6
           and high_tail_pct(regression_data) < .5
           ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyUpTrend-0')
            flag = True
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
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellUpTrend-1')
            flag = True
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
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellUpTrend-2')
            flag = True
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
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyUpTrend-1')
            flag = True
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
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyUpTrend-1-YearHigh')
            flag = True
    if('shortUpTrend' in regression_data['series_trend']): 
        if(0 < regression_data['PCT_day_change'] < 1.3 and 0 < regression_data['PCT_change'] < 2
            and 1.5 < regression_data['PCT_day_change_pre1'] > regression_data['PCT_day_change']
            and 1.5 < regression_data['PCT_day_change_pre2'] > regression_data['PCT_day_change']
            and regression_data['forecast_day_PCT_change'] > 0
            and (-1 < regression_data['month3HighChange'] < 2
                or (abs(bar_high_change_month3(regression_data)) < 1 and high_tail_pct(regression_data) > 1)
                )
            and (low_tail_pct(regression_data) < 0.5 or low_tail_pct(regression_data) < high_tail_pct(regression_data)
                or abs(high_tail_pct(regression_data) - low_tail_pct(regression_data)) <= 0.2
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'shortUpTrendSellReversal-Month3High-Doji-Last2DayGTToday')
            flag = True
        elif(0 < regression_data['PCT_day_change'] < 1.3 and 0 < regression_data['PCT_change'] < 2
            and 1.5 < regression_data['PCT_day_change_pre1'] > regression_data['PCT_day_change']
            and 1.5 < regression_data['PCT_day_change_pre2'] > regression_data['PCT_day_change']
            and regression_data['forecast_day_PCT_change'] > 0
            and ((-1.5 < regression_data['monthHighChange'] < 0.5 and regression_data['month3HighChange'] < -20)
                or (abs(bar_high_change_month(regression_data)) < 1 and high_tail_pct(regression_data) > 1)
                )
            and (low_tail_pct(regression_data) < 0.5 or low_tail_pct(regression_data) < high_tail_pct(regression_data)
                or abs(high_tail_pct(regression_data) - low_tail_pct(regression_data)) <= 0.2
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'shortUpTrendSellReversal-MonthHigh-Doji-Last2DayGTToday')
            flag = True
        elif(0 < regression_data['PCT_day_change'] < 1.3 and 0 < regression_data['PCT_change'] < 2
            and 1.5 < regression_data['PCT_day_change_pre1'] > regression_data['PCT_day_change']
            and 1.5 < regression_data['PCT_day_change_pre2'] > regression_data['PCT_day_change']
            and regression_data['forecast_day_PCT_change'] > 0
            and regression_data['month3HighChange'] < -5
            and regression_data['monthLowChange'] > 5
            and abs(regression_data['monthHighChange']) > 1.5
            and abs(regression_data['monthHighChange']) < abs(regression_data['monthLowChange'])
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'shortUpTrendBuyContinue-Doji-Last2DayGTToday')
            flag = True
        if(regression_data['PCT_day_change'] > 0 and regression_data['PCT_change'] > 0
            and regression_data['forecast_day_PCT_change'] > 0
            and ((-1.5 < regression_data['monthHighChange'] < 1.5 and regression_data['monthHighChange'] == regression_data['month2HighChange'])
                and abs(bar_high_change_month(regression_data)) < 1
                )
            and high_tail_pct(regression_data) > 1 and low_tail_pct(regression_data) < high_tail_pct(regression_data)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'shortUpTrendSellReversal-MonthHigh')
            flag = True
    
    return flag


def buy_final(regression_data, regressionResult, reg, ws, ws1):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(regression_data['yearHighChange'] < -10 
        and regression_data['yearLowChange'] > 5
        and regression_data['month3LowChange'] > 3
        and 4 > regression_data['PCT_day_change'] > 1 and 4 > regression_data['PCT_change'] > 1
        # and abs(regression_data['PCT_day_CH']) < 0.3
        # and regression_data['forecast_day_VOL_change'] > 0
        and high_tail_pct(regression_data) < 1
        # and str(regression_data['score']) != '0-1'
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
            add_in_csv(regression_data, regressionResult, ws, None, None, 'buyFinal')
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
            add_in_csv(regression_data, regressionResult, ws, None, None, 'buyFinal1')
            return True
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
           # and regression_data['forecast_day_VOL_change'] > 0
           ):
            if(2 < regression_data['PCT_day_change'] < 4 and 2 < regression_data['PCT_change'] < 4
                and regression_data['PCT_day_change_pre1'] < 0
                and regression_data['forecast_day_PCT10_change'] > -20
                and regression_data['month3HighChange'] < -15
                and regression_data['SMA4'] > 0
                and regression_data['SMA9'] > -3
                and high_tail_pct(regression_data) < 1.5
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyFinalCandidate-(lastDayDown)')
                return True
            elif(2 < regression_data['PCT_day_change'] < 4 and 2 < regression_data['PCT_change'] < 4
                and no_doji_or_spinning_buy_india(regression_data)
                and regression_data['PCT_day_change_pre1'] > 0
                and regression_data['forecast_day_PCT10_change'] > -20
                and regression_data['month3HighChange'] < -15
                and regression_data['forecast_day_VOL_change'] > -20
                and high_tail_pct(regression_data) < 1.5
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyFinalCandidate-(lastDayUp)')
                return True
            elif(1 < regression_data['PCT_day_change'] < 4 and 1 < regression_data['PCT_change'] < 4
                and no_doji_or_spinning_buy_india(regression_data)
                and regression_data['PCT_day_change_pre1'] > 0
                and regression_data['forecast_day_VOL_change'] < -20
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellFinalContinue-(lastDayUp)-(volLow)')
                return True
            elif(1 < regression_data['PCT_day_change'] < 4 and 1 < regression_data['PCT_change'] < 4
                and regression_data['PCT_day_change_pre1'] < 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellFinalContinue-(lastDayDown)-1')
                return True
            elif(1 < regression_data['PCT_day_change'] < 4 and 1 < regression_data['PCT_change'] < 4
                and regression_data['PCT_day_change_pre1'] > 0
                ):
                if('P@[' in regression_data['sellIndia']):
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyFinalCandidate-(lastDayUp)-(sellPattern)')
                    return True
                elif('P@[' not in regression_data['buyIndia']):
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellFinalContinue-(lastDayUp)-1')
                    return True
            elif(0.5 < regression_data['PCT_day_change'] < 2.5 and 0.5 < regression_data['PCT_change'] < 2.5
                and regression_data['PCT_day_change_pre1'] < 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellFinalContinue-(lastDayDown)-2')
                return True
            elif(0.5 < regression_data['PCT_day_change'] < 2.5 and 0.5 < regression_data['PCT_change'] < 2.5
                and regression_data['PCT_day_change_pre1'] > 0
                ):
                if('P@[' in regression_data['sellIndia']):
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyFinalCandidate-(lastDayUp)-(sellPattern)')
                    return True
                else:
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellFinalContinue-(lastDayUp)-2')
                    return True
        if((((regression_data['close'] - regression_data['open']) * 1.5 > regression_data['high'] - regression_data['low']) or (regression_data['forecast_day_PCT_change'] > 0 and regression_data['PCT_day_change'] > 1))
            and (regression_data['yearHighChange'] < -30 or regression_data['yearLowChange'] < 30)
            ):
            if(1 < regression_data['PCT_day_change'] < 2.5 and 1 < regression_data['PCT_change'] < 2.5 
                and no_doji_or_spinning_sell_india(regression_data) and no_doji_or_spinning_buy_india(regression_data)
                ):
                if(regression_data['forecast_day_VOL_change'] > -20
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyFinalCandidate-2')
                    return True
            if(1 < regression_data['PCT_day_change'] < 4 and 1 < regression_data['PCT_change'] < 4 
                and no_doji_or_spinning_sell_india(regression_data) and no_doji_or_spinning_buy_india(regression_data)
                ):
                if(regression_data['forecast_day_VOL_change'] < -30
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyFinalCandidate-3')
                    return True
                
    return False

    
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
            and low_tail_pct(regression_data) > 2
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
                and (regression_data['open'] - regression_data['low']) >= ((regression_data['open'] - regression_data['close']) * 3)
                and (regression_data['open'] - regression_data['low']) >= ((regression_data['high'] - regression_data['close']) * 3)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyMorningStar-2(NotUpSecondHalfAndUp2to3)')
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
            and (regression_data['high'] - regression_data['close']) > ((regression_data['close'] - regression_data['open']))
            and (regression_data['high'] - regression_data['close']) >= ((regression_data['open'] - regression_data['low']) * 3)
            and ((regression_data['yearHighChange'] < -15) or (regression_data['yearHighChange'] > -2))
            and regression_data['forecast_day_PCT5_change'] < 10
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyEveningStar-0')
            return True
        elif(4 > regression_data['PCT_day_change'] > 2 and 4 > regression_data['PCT_change'] > 2
            and -15 < regression_data['yearHighChange'] 
            and regression_data['PCT_day_change_pre3'] > -1
            and regression_data['PCT_day_change_pre1'] > -1
            and regression_data['PCT_change_pre1'] > -1
            and regression_data['PCT_change_pre2'] > -1
            ):
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
                and (regression_data['high'] - regression_data['close']) >= ((regression_data['close'] - regression_data['open']) * 3)
                and (regression_data['high'] - regression_data['close']) >= ((regression_data['open'] - regression_data['low']) * 3)
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
           add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyDayLowVolLow')
           return True
        elif((regression_data['PCT_day_change'] < -5 or regression_data['PCT_change'] < -5)
           and float(regression_data['forecast_day_VOL_change']) < -30
           and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
           and regression_data['PCT_day_change_pre1'] < -1.5
           and regression_data['forecast_day_PCT_change'] < -4.5
           and regression_data['forecast_day_PCT10_change'] > 5
           ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyDayLowVolLow-0')
            return True
        elif((regression_data['PCT_day_change'] < -5 or regression_data['PCT_change'] < -5)
           and float(regression_data['forecast_day_VOL_change']) < -20
           and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
           and regression_data['PCT_day_change_pre1'] < -1.5
           and regression_data['forecast_day_PCT_change'] < -5
           # and regression_data['forecast_day_PCT10_change'] < -5
           ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellDayLowVolLow-0')
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
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyDayLowVolLow-01')
                return True
            elif(regression_data['month6LowChange'] > 10
                and regression_data['yearLowChange'] > 20
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellDayLowVolLow-01')
                return True
        elif((regression_data['PCT_day_change'] < -5 and regression_data['PCT_change'] < -4)
           and float(regression_data['forecast_day_VOL_change']) < -30
           and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
           and regression_data['PCT_day_change_pre1'] < -1.5
           and -20 < regression_data['SMA50'] < 10
           and regression_data['SMA9'] > -7
           # and regression_data['PCT_day_change_pre2'] < -1.5
           ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyDayLowVolLow-02-checkMorningTrend(.5SL)')
            return True
        elif((regression_data['PCT_day_change'] < -5 and regression_data['PCT_change'] < -4)
           and float(regression_data['forecast_day_VOL_change']) < 0
           and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
           and -5 < regression_data['PCT_day_change_pre1'] < -1.5
           and regression_data['PCT_day_change_pre2'] > 1.5
           and regression_data['year2LowChange'] > 10
           ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellDayLowVolLow-02-checkMorningTrend(.5SL)')
            return True
        elif((regression_data['PCT_day_change'] < -4 and regression_data['PCT_change'] < -2)
           and float(regression_data['forecast_day_VOL_change']) < 0
           and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
           and regression_data['PCT_day_change_pre1'] < -1.5
           and regression_data['PCT_day_change_pre2'] < -1.5
           and -20 < regression_data['SMA50']
           and regression_data['SMA9'] > -7
           ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellDayLowVolLow-03-checkMorningTrend(.5SL)')
            return True
        elif((regression_data['PCT_day_change'] < -4 and regression_data['PCT_change'] < -2)
           and float(regression_data['forecast_day_VOL_change']) < 0
           and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
           and regression_data['PCT_day_change_pre1'] < -1.5
           and regression_data['PCT_day_change_pre2'] < -1.5
           ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyDayLowVolLow-03-checkMorningTrend(.5SL)-after10:30')
            return True
        elif((regression_data['PCT_day_change'] < -4 and regression_data['PCT_change'] < -2)
           and float(regression_data['forecast_day_VOL_change']) < 0
           and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
           and regression_data['PCT_day_change_pre1'] < -1.5
           and regression_data['PCT_day_change_pre2'] < -1.5
           ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellDayLowVolLow-03-checkMorningTrend(.5SL)')
            return True
        elif((regression_data['PCT_day_change'] < -4 and regression_data['PCT_change'] < -2)
           and float(regression_data['forecast_day_VOL_change']) < 0
           and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1'] < 0
           and regression_data['PCT_day_change_pre1'] < -1.5
           and regression_data['PCT_day_change_pre2'] > 1.5
           ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None)
            return True
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
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellFinalContinue-00')
                return True
            elif(3 < regression_data['PCT_day_change'] < 5 and 3 < regression_data['PCT_change'] < 5
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyFinalContinueReversal-1')
                return True
            elif(regression_data['forecast_day_PCT_change'] > 0
                and regression_data['forecast_day_VOL_change'] <= 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyFinalContinueReversal-2')
                return True    
        return False
    return False            


def buy_trend_break(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    flag = False
    if(NIFTY_LOW and low_tail_pct(regression_data) > 1.5
       and -1 < regression_data['PCT_change'] < 1 and -1 < regression_data['PCT_day_change'] < 1
       and regression_data['forecast_day_PCT10_change'] < 10
       ):
        if(2 < regression_data['month3LowChange'] < 10):
            if(ten_days_less_than_minus_ten(regression_data)
               and regression_data['forecast_day_PCT10_change'] < -15
               and 5 > regression_data['PCT_day_change'] > 1 and 5 > regression_data['PCT_day_change'] > 1
               # and regression_data['forecast_day_VOL_change'] > 50
               and abs_yearHigh_more_than_yearLow(regression_data) == True
               ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBreakOutBuyCandidate(notUpLastDay)-1')
                flag = True
    if(0.5 < regression_data['forecast_day_PCT10_change'] < 2
        and regression_data['forecast_day_PCT_change'] > 1
        and 2 < regression_data['PCT_day_change'] < 5.5
        and 2 < regression_data['PCT_change'] < 5.5
        and regression_data['PCT_day_change_pre1'] > -0.5
        and 0.5 < high_tail_pct(regression_data) < 2
        and regression_data['month3LowChange'] > 4
        and ('P@[' not in regression_data['sellIndia'])
        and abs_month3High_more_than_month3Low(regression_data)
        and (abs_month6High_more_than_month6Low(regression_data))
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuy-2week-breakoutup')
        flag = True
    elif(0.5 < regression_data['forecast_day_PCT10_change'] < 3
        # and regression_data['forecast_day_PCT_change'] > 1
        and 2 < regression_data['PCT_day_change']
        and 2 < regression_data['PCT_change']
        and regression_data['PCT_day_change_pre1'] > -0.5
        and 0.5 < high_tail_pct(regression_data) < 2
        # and regression_data['buyIndia_avg'] > -0.75
        # and regression_data['sellIndia_avg'] > -0.75
        # and regression_data['month3LowChange'] > 4
        # and ('P@[' not in regression_data['sellIndia'])
        and abs_month3High_more_than_month3Low(regression_data)
        and (abs_month6High_more_than_month6Low(regression_data))
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSell-2week-breakoutup')
        flag = True
    if(0.5 < regression_data['forecast_day_PCT10_change'] < 3
        and regression_data['forecast_day_PCT_change'] > 1
        and 2 < regression_data['PCT_day_change'] < 5.5
        and 2 < regression_data['PCT_change'] < 5.5
        and high_tail_pct(regression_data) < 2.5
        and regression_data['month3LowChange'] > 4
        and ('P@[' not in regression_data['sellIndia'])
        and abs_month3High_more_than_month3Low(regression_data)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chis-breakoutup-2week')
        flag = True
        
    elif(0.5 < regression_data['forecast_day_PCT10_change'] < 3
        and regression_data['forecast_day_PCT_change'] > 1
        and 2 < regression_data['PCT_day_change'] < 5.5
        and 2 < regression_data['PCT_change'] < 5.5
        and high_tail_pct(regression_data) < 1
        # and regression_data['buyIndia_avg'] > -0.75
        # and regression_data['sellIndia_avg'] > -0.75
        and regression_data['month3LowChange'] > 4
        and regression_data['month3HighChange'] < -4
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuy-2week-breakoutup(|-|-| or --|)')
        flag = True
            
    if(regression_data['yearLowChange'] < 5):
       if(regression_data['forecast_day_PCT_change'] > 3 and regression_data['PCT_day_change'] > 3
           and abs(regression_data['PCT_day_change']) > abs(regression_data['PCT_day_change_pre1'])
           # and regression_data['open'] == regression_data['low']
           and regression_data['forecast_day_VOL_change'] >= -20
           and high_tail_pct(regression_data) < 0.5
           ):
               add_in_csv(regression_data, regressionResult, ws, None, None, 'chisFinalBreakOutBuy-1test-atYearLow')
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
           add_in_csv(regression_data, regressionResult, ws, None, None, 'chisFinalBreakOutBuyContinue-00-test-atYearLow')
           flag = True
       if(2 > regression_data['forecast_day_PCT_change'] > 0 and 2 > regression_data['PCT_day_change'] > 0
           and regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change_pre2'] > 0 and regression_data['PCT_day_change_pre3'] > 0
           and (regression_data['forecast_day_PCT_change'] > 0.75 or regression_data['PCT_day_change_pre1'] > 0.75 or regression_data['PCT_day_change_pre2'] > 0.75 or regression_data['PCT_day_change_pre3'] > 0.75)
           and (regression_data['open'] == regression_data['low'] or regression_data['forecast_day_VOL_change'] >= 0)
           and regression_data['forecast_day_VOL_change'] >= -50
           ):
           add_in_csv(regression_data, regressionResult, ws, None, None, 'chisFinalBreakOutBuyContinue-0-test-atYearLow')
           flag = True
    if(5 < regression_data['yearLowChange'] < 12 and abs_yearHigh_more_than_yearLow(regression_data)
       and regression_data['forecast_day_PCT10_change'] < 10
       and last_7_day_all_up(regression_data) == False
       and high_tail_pct(regression_data) < 0.7
       ):
       if(3 > regression_data['forecast_day_PCT_change'] > 2 and 3 > regression_data['PCT_day_change'] > 2
           and regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change_pre2'] > 0 and regression_data['PCT_day_change_pre3'] > 0
           # and regression_data['open'] == regression_data['low']
           and regression_data['forecast_day_VOL_change'] >= 0
           ):
               add_in_csv(regression_data, regressionResult, ws, None, None, 'chisFinalBreakOutBuyContinue-11-test-atYearLow')
               flag = True
       if(2 > regression_data['forecast_day_PCT_change'] > 0 and 2 > regression_data['PCT_day_change'] > 0
           and regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change_pre2'] > 0 and regression_data['PCT_day_change_pre3'] > 0
           and (regression_data['forecast_day_PCT_change'] > 0.75 or regression_data['PCT_day_change_pre1'] > 0.75 or regression_data['PCT_day_change_pre2'] > 0.75 or regression_data['PCT_day_change_pre3'] > 0.75)
           # and regression_data['open'] == regression_data['low']
           and regression_data['forecast_day_VOL_change'] >= 0
           ):
               add_in_csv(regression_data, regressionResult, ws, None, None, 'chisFinalBreakOutBuyContinue-1-test-atYearLow')
               flag = True
    if(regression_data['SMA200'] == 1
       and regression_data['PCT_day_change'] > 2 and regression_data['PCT_change'] > 2
       ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBreakOutBuyConsolidate-0')
        flag = True
    return flag   

           
def buy_oi(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    if(regression_data['PCT_day_change'] > 2 and regression_data['PCT_change'] > 2
        and abs(regression_data['PCT_day_change']) > abs(regression_data['PCT_day_change_pre1'])
        and regression_data['PCT_day_change_pre1'] > 0
        and regression_data['PCT_day_change_pre2'] > -0.5
        and regression_data['volume'] > regression_data['volume_pre1']
        and regression_data['volume'] > regression_data['volume_pre2']
        and (regression_data['forecast_day_VOL_change'] > 20
             or regression_data['volume'] > regression_data['volume_pre1'] > regression_data['volume_pre2']
            )
        ):
        if(regression_data['week2LowChange'] > 0
            and abs_week2High_less_than_week2Low(regression_data)
            and abs_monthHigh_less_than_monthLow(regression_data)
            and abs_month3High_less_than_month3Low(regression_data)
            and high_tail_pct(regression_data) > abs(regression_data['PCT_day_change']) / 2
            and regression_data['PCT_day_change'] > 5 and regression_data['PCT_change'] > regression_data['PCT_day_change']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:buyBelowTail-SellAtClose:upVol3dayUpWeek2High-highUpperTail')
        elif(regression_data['week2HighChange'] < -4.0
            and (regression_data['week2LowChange'] < 0 
                or abs_week2High_more_than_week2Low(regression_data)
                or abs_weekHigh_more_than_weekLow(regression_data)
                )
            and regression_data['PCT_day_change_pre3'] < 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:buy(GLOBALFUTDOWN-GLOBALMARKETDOWN)Sell-UpVol-3dayUp-Week2Low')
        elif(regression_data['week2LowChange'] > 4.0
            and (regression_data['PCT_day_change'] < 6 and regression_data['PCT_change'] < 6) 
            and (regression_data['PCT_day_change'] < 3 or regression_data['PCT_day_change_pre1'] > 1)
            and (regression_data['PCT_day_change_pre1'] > 1 or regression_data['PCT_day_change_pre2'] > 1)
            and (regression_data['high'] - regression_data['low']) > regression_data['PCT_day_change_pre1']
            and abs_week2High_less_than_week2Low(regression_data)
            and abs_monthHigh_less_than_monthLow(regression_data)
            and abs_month3High_less_than_month3Low(regression_data)
            and high_tail_pct(regression_data) < 2
            and regression_data['forecast_day_VOL_change'] > 10
            ):
            if(regression_data['PCT_day_change_pre1'] > 1 and regression_data['PCT_day_change_pre2'] > 1):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:sell-UpVol-3dayUp-Week2High')
    elif(regression_data['PCT_day_change'] > 1.5 and regression_data['PCT_change'] > 2
        and regression_data['PCT_day_change_pre1'] > 0
        and regression_data['PCT_day_change_pre2'] > -0.5
        and regression_data['volume'] < regression_data['volume_pre1']
        and regression_data['volume'] < regression_data['volume_pre2']
        and (regression_data['forecast_day_VOL_change'] < -20
            or regression_data['volume'] < regression_data['volume_pre1'] < regression_data['volume_pre2']
            )
        ):
        if(regression_data['PCT_day_change_pre1'] > 1.5 or regression_data['PCT_day_change_pre2'] > 1.5):
            if(regression_data['week2HighChange'] < -4.0
                and (regression_data['week2LowChange'] < 0 
                    or abs_week2High_more_than_week2Low(regression_data)
                    or abs_weekHigh_more_than_weekLow(regression_data)
                    )
                and regression_data['PCT_day_change_pre3'] < 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:sell-DownVol-3dayUp-Week2Low')
            elif(regression_data['week2LowChange'] > 4.0
                and (regression_data['high'] - regression_data['low']) > regression_data['PCT_day_change_pre1']
                and abs_week2High_less_than_week2Low(regression_data)
                and abs_monthHigh_less_than_monthLow(regression_data)
                and abs_month3High_less_than_month3Low(regression_data)
                and high_tail_pct(regression_data) < 2
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:sell-DownVol-3dayUp-Week2High')
        elif(regression_data['PCT_day_change_pre1'] < 1.5 and regression_data['PCT_day_change_pre2'] < 1.5
            and regression_data['PCT_day_change'] < 5
            ):
            if(regression_data['week2HighChange'] < -4.0
                and (regression_data['week2LowChange'] < 0 
                    or abs_week2High_more_than_week2Low(regression_data)
                    or abs_weekHigh_more_than_weekLow(regression_data)
                    )
                and regression_data['PCT_day_change_pre3'] < 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:buy-DownVol-3dayUp-Week2Low')
    
    elif(regression_data['PCT_day_change'] > 0.75 and regression_data['PCT_change'] > 0.75 and regression_data['PCT_day_change_pre1'] > 0
        and (regression_data['PCT_day_change'] > 2 or regression_data['PCT_day_change_pre1'] > 2)
        and abs(regression_data['weekHighChange']) > abs(regression_data['weekLowChange'])
        # and abs(abs(regression_data['PCT_day_change']) - abs(regression_data['PCT_day_change_pre1'])) > 1.5
        ):
        if(abs(regression_data['PCT_day_change']) > abs(regression_data['PCT_day_change_pre1'])
            and regression_data['forecast_day_VOL_change'] < 0
            and (abs(regression_data['PCT_day_change']) - abs(regression_data['PCT_day_change_pre1']) > 2
                or regression_data['forecast_day_VOL_change'] < -30
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:SellReversalLast2DayUp-VolDown')
        elif(abs(regression_data['PCT_day_change']) < abs(regression_data['PCT_day_change_pre1'])
            and regression_data['forecast_day_VOL_change'] > 0
            and (abs(regression_data['PCT_day_change']) - abs(regression_data['PCT_day_change_pre1']) < -2
                or regression_data['forecast_day_VOL_change'] > 30
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:SellReversalLast2DayUp-VolUp')
        elif(abs(regression_data['PCT_day_change']) > abs(regression_data['PCT_day_change_pre1'])
            and regression_data['forecast_day_VOL_change'] > 0
            and (abs(regression_data['PCT_day_change']) - abs(regression_data['PCT_day_change_pre1']) > 2
                or regression_data['forecast_day_VOL_change'] > 30
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:BuyContinueLast2DayUp-VolUp')
#         elif(abs(regression_data['PCT_day_change']) < abs(regression_data['PCT_day_change_pre1'])
#             and regression_data['forecast_day_VOL_change'] < 0
#             and (abs(regression_data['PCT_day_change']) - abs(regression_data['PCT_day_change_pre1']) < -2
#                 or regression_data['forecast_day_VOL_change'] < -30
#                 )
#             ):
#             add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:buyContinueLast2DayUp-VolDown')
           
    if(abs(regression_data['month3HighChange']) < abs(regression_data['month3LowChange'])
        and abs(regression_data['monthHighChange']) < abs(regression_data['monthLowChange'])
        and regression_data['PCT_day_change'] < 0
        and regression_data['PCT_day_change_pre1'] < 0
        and regression_data['PCT_day_change_pre2'] < 0
        and (regression_data['forecast_day_PCT3_change'] < -5 or regression_data['forecast_day_PCT4_change'] < -5)
        ):
        if(regression_data['PCT_day_change'] < -1
            and regression_data['PCT_day_change_pre1'] < -1
            and regression_data['PCT_day_change_pre2'] < -1
            and 0 < regression_data['PCT_day_change_pre3'] < 1
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:checkBuyRevarsalLast3DayDownAtMonth3High')
        if(regression_data['PCT_day_change'] < -1
            and regression_data['PCT_day_change_pre1'] < -1
            and regression_data['PCT_day_change_pre2'] < -1
            and ((abs(regression_data['PCT_day_change']) > abs(regression_data['PCT_day_change_pre1']) and regression_data['forecast_day_VOL_change'] < -10)
                or (abs(regression_data['PCT_day_change']) < abs(regression_data['PCT_day_change_pre1']) and regression_data['forecast_day_VOL_change'] > 10)
                or (abs(regression_data['PCT_day_change']) > (1.5 * abs(regression_data['PCT_day_change_pre1'])) and regression_data['volume'] < regression_data['volume_pre1'])
                or ((1.5 * abs(regression_data['PCT_day_change'])) < abs(regression_data['PCT_day_change_pre1']) and regression_data['volume'] > regression_data['volume_pre1'])
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:BuyRevarsalVolCrossed')
            
    if(regression_data['PCT_day_change'] < -1 and regression_data['PCT_change'] < -1
        and regression_data['PCT_day_change_pre1'] > 0
        and regression_data['PCT_day_change_pre2'] < -1
        and regression_data['volume'] > regression_data['volume_pre1']
        ):
        if(abs(regression_data['PCT_day_change']) > abs(regression_data['PCT_day_change_pre1'])
            and 0 > regression_data['forecast_day_PCT3_change'] > regression_data['forecast_day_PCT4_change'] > regression_data['forecast_day_PCT5_change']
            and -3 < regression_data['PCT_day_change'] < -1
            and regression_data['PCT_day_change_pre3'] < 0
            and 0 < regression_data['forecast_day_VOL_change'] < 150
            and 0 < regression_data['contract'] < 150 
            and 0 < regression_data['oi_next'] < 150
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'zigZagVolCrossedDowntrendFromUp')
        elif(abs(regression_data['PCT_day_change']) > 2 * abs(regression_data['PCT_day_change_pre1'])
            and regression_data['PCT_day_change'] < -4
            and regression_data['PCT_day_change_pre1'] > 1
            and 0 < regression_data['forecast_day_VOL_change'] < 150
            and 20 < regression_data['contract'] < 150 
            and 50 < regression_data['oi_next'] < 150
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'continueZigZagVolCrossedFromUp')
        elif(abs(regression_data['PCT_day_change']) < 2 * abs(regression_data['PCT_day_change_pre1'])
            and regression_data['PCT_day_change'] < -2
            and regression_data['PCT_day_change_pre1'] > 1
            and regression_data['PCT_day_change_pre3'] > 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'zigZagVolCrossedFromUp')
        
    if(regression_data['PCT_day_change'] > 2 and regression_data['PCT_change'] > 1
        and regression_data['PCT_day_change_pre1'] > 0
        and regression_data['PCT_day_change_pre2'] < 0
        and regression_data['PCT_day_change_pre3'] < 0
        and regression_data['PCT_day_change_pre4'] < 0
        and regression_data['volume'] > regression_data['volume_pre1']
        and regression_data['volume'] > regression_data['volume_pre2']
        and regression_data['volume'] > regression_data['volume_pre3']
        # and regression_data['volume'] > regression_data['volume_pre4']
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'volumeUpsergedLast2n3n4DayDown')
    elif(2 < regression_data['PCT_day_change'] < 5 and 1 < regression_data['PCT_change'] < 5
        and (regression_data['PCT_day_change_pre1'] > 1 or (regression_data['forecast_day_PCT3_change'] > 0 and regression_data['high'] > regression_data['high_pre3']))
        and regression_data['PCT_day_change_pre2'] < 0
        and regression_data['PCT_day_change_pre3'] < 0
        and regression_data['PCT_day_change_pre4'] > 0
        # and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change_pre2'])
        and (regression_data['monthHighChange'] > 0 or abs(regression_data['monthHighChange']) < abs(regression_data['monthLowChange']))
        and regression_data['volume'] > regression_data['volume_pre1']
        and regression_data['volume'] > regression_data['volume_pre2']
        and regression_data['volume'] > regression_data['volume_pre3']
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'volSellVolumeUpsergedLast2n3DayDown')
    elif(2 < regression_data['PCT_day_change'] < 5 and 1 < regression_data['PCT_change'] < 5
        and (0 < regression_data['PCT_day_change_pre1'] < 1 or (regression_data['forecast_day_PCT3_change'] < 0 and regression_data['high'] < regression_data['high_pre3']))
        and regression_data['PCT_day_change_pre2'] < 0
        and regression_data['PCT_day_change_pre3'] < 0
        and regression_data['PCT_day_change_pre4'] > 0
        # and abs(regression_data['PCT_day_change_pre1']) < abs(regression_data['PCT_day_change_pre2'])
        and (regression_data['monthLowChange'] < 0 or abs(regression_data['monthHighChange']) > abs(regression_data['monthLowChange']))
        and regression_data['volume'] > regression_data['volume_pre1']
        and regression_data['volume'] > regression_data['volume_pre2']
        and regression_data['volume'] > regression_data['volume_pre3']
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'volBuyVolumeUpsergedLast2n3DayDown')
    elif(regression_data['PCT_day_change'] > 2.5 and regression_data['PCT_change'] > 1
        and regression_data['PCT_day_change_pre1'] < 0
        and regression_data['PCT_day_change_pre2'] < 0
        and regression_data['volume'] > regression_data['volume_pre1']
        and regression_data['volume'] > regression_data['volume_pre2']
        and (regression_data['forecast_day_VOL_change'] > 50 or regression_data['PCT_day_change'] > 3)
        and 0 < regression_data['forecast_day_VOL_change'] < 150
        and 20 < regression_data['contract'] < 150 
        and 50 < regression_data['oi_next'] < 150
        and ()
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'volBuyVolumeUpsergedLast1n2DayDown')
        
    return True

       
def buy_heavy_uptrend_reversal(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    if(("upTrend" in regression_data['series_trend'])
        and (0 < regression_data['forecast_day_PCT4_change'] < 15)
        and (0 < regression_data['forecast_day_PCT5_change'] < 15)
        and (0 < regression_data['forecast_day_PCT7_change'] < 15)
        and (regression_data['forecast_day_PCT10_change'] < 15)
        ):
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
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'sellHeavyUpTrend-Reversal')
                else:
                    if(regression_data['forecast_day_VOL_change'] < 0):
                        add_in_csv(regression_data, regressionResult, ws, None, None, 'buyHeavyUpTrend-Continue-(Risky)')
                    elif('P@' in regression_data['buyIndia']
                        and regression_data['year2HighChange'] > -20
                        ):
                        add_in_csv(regression_data, regressionResult, ws, None, None, 'sellHeavyUpTrend-Reversal-(Risky)')
            elif((2 < regression_data['PCT_change'] < 7) and (3 < regression_data['PCT_day_change'] < 7)
                # and ten_days_more_than_seven(regression_data)
                and (('NearHighMonth3' in regression_data['filter3']) 
                      or ('BreakHighMonth3' in regression_data['filter3'])
                      or ('NearHighMonth6' in regression_data['filter3'])
                      or ('BreakHighMonth6' in regression_data['filter3'])
                    )
                and regression_data['year2HighChange'] < -20
                and regression_data['yearHighChange'] > -50
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'sellHeavyUpTrend-Reversal-1')

                   
def buy_random_filter(regression_data, regressionResult, reg, ws):
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
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyMay5DayCeilReversal')
        
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
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuycheck10DayLowReversal')
        
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
            # and (-1 < regression_data['PCT_day_change'] < 0) and (-1 < regression_data['PCT_change'] < 0)
            ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None)
        elif(regression_data['week2HighChange'] < -1):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyRisingMA-(check5MinuteUpTrendAndBuyUptrend)')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyRisingMA-(check5MinuteUpTrendAndBuyUptrend)-Already10DayDown')
    
    if((-0.75 < regression_data['PCT_day_change'] < 0) and (-0.75 < regression_data['PCT_change'] < 0)
        and (regression_data['SMA4_2daysBack'] > 0 or regression_data['SMA9_2daysBack'] > 0)
        and regression_data['SMA4'] < 0
        and regression_data['PCT_day_change_pre1'] < -0.5
        and regression_data['PCT_day_change_pre2'] < -0.5
        and (regression_data['PCT_day_change_pre1'] < -1.5 or regression_data['PCT_day_change_pre2'] < -1.5)
        ): 
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuySMA4Reversal')
        
    if((-2 < regression_data['PCT_day_change'] < 0) and (-2 < regression_data['PCT_change'] < 0)
        and regression_data['PCT_day_change_pre1'] < -7
        and low_tail_pct(regression_data) > 2
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyLastDayDownReversal')
        
    if((0.5 < regression_data['PCT_day_change'] < 2) and (-10 < regression_data['PCT_change'] < -4)
        and low_tail_pct(regression_data) > 1
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyLastDayHighDownReversal')
        
    if(regression_data['PCT_day_change'] > 0 and regression_data['PCT_day_change_pre1'] < -1 and regression_data['PCT_day_change_pre2'] < -1
        and (regression_data['forecast_day_PCT5_change'] < -5
            or regression_data['forecast_day_PCT7_change'] < -5
            or regression_data['forecast_day_PCT10_change'] < -5
            )
        and regression_data['monthHighChange'] < -5
        and regression_data['monthLowChange'] > 5
        ):
        if(regression_data['forecast_day_PCT3_change'] > 0 and regression_data['forecast_day_PCT4_change'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'AF:maySellStock-smallDowntrendContinue')
        elif((regression_data['forecast_day_PCT4_change'] < 0 or regression_data['forecast_day_PCT5_change'] < 0)
            and regression_data['PCT_day_change'] > 1
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuy-smallDowntrendReversal')
            
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
        add_in_csv(regression_data, regressionResult, ws, None, None, 'maySellAfter10:20HighVolatileLastDayUp-GT10')
        flag = True
    elif(regression_data['high'] > regression_data['high_pre1']
        and regression_data['high'] > regression_data['high_pre2']
        and (regression_data['PCT_day_change'] > 15 and regression_data['PCT_change'] > 10
            or regression_data['forecast_day_PCT2_change'] > 20)
        and regression_data['close'] > 50
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'maySellAfter10:20HighVolatileLastDayUp-GT10')
        flag = True
    elif(
        regression_data['forecast_day_PCT7_change'] < 0
        and regression_data['forecast_day_PCT10_change'] < 0
        and 8 < regression_data['PCT_day_change'] < 12 and 8 < regression_data['PCT_change'] < 12
        and regression_data['close'] > 50
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'mayBuyContinueHighVolatileLastDayUp-PCT10LT0-GT8')
    elif(
        regression_data['month3HighChange'] < 0 
        and (regression_data['week2HighChange'] > 0 or abs(regression_data['week2HighChange']) < abs(regression_data['week2LowChange']))
        and regression_data['forecast_day_PCT10_change'] < 20
        and 8 < regression_data['PCT_day_change'] < 12 and 8 < regression_data['PCT_change'] < 12
        and regression_data['close'] > 50
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'mayBuyContinueHighVolatileLastDayUp-month3HighLT0-GT8')
    elif(
        regression_data['month6HighChange'] < 0 
        and (regression_data['week2HighChange'] > 0 or abs(regression_data['week2HighChange']) < abs(regression_data['week2LowChange']))
        and regression_data['forecast_day_PCT10_change'] < 25
        and 8 < regression_data['PCT_day_change'] < 12 and 8 < regression_data['PCT_change'] < 12
        and regression_data['close'] > 50
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'mayBuyContinueHighVolatileLastDayUp-month6HighLT0-GT8')
    elif((regression_data['forecast_day_PCT3_change'] > 0 and regression_data['forecast_day_PCT4_change'] > 0)
        or regression_data['forecast_day_PCT5_change'] > 0
        or regression_data['forecast_day_PCT7_change'] > 0
        or regression_data['forecast_day_PCT10_change'] > 0
        ):
        if(4 < regression_data['PCT_day_change'] < 8 and 3 < regression_data['PCT_change'] < 10
            and (5 < regression_data['PCT_day_change'] or 5 < regression_data['PCT_change'])  
            and regression_data['PCT_day_change_pre1'] < 0
            and regression_data['PCT_day_change_pre2'] < 0
            and (regression_data['PCT_day_change_pre1'] < -1 or regression_data['PCT_day_change_pre2'] < -1)
            and high_tail_pct(regression_data) < abs(regression_data['PCT_day_change']) / 3
            and low_tail_pct(regression_data) < 2.5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'mayBuyContinueHighVolatileLastDayUp-GT5')


def buy_check_cup_filter(regression_data, regressionResult, reg, ws):
    
    if(-5.5 < regression_data['PCT_day_change'] < -2
        and -5.5 < regression_data['PCT_change'] < 1
        and regression_data['PCT_day_change_pre1'] > 2
        and (regression_data['PCT_day_change_pre2'] > 0
            or regression_data['PCT_day_change_pre3'] > 0
            )
        # and (regression_data['forecast_day_PCT5_change'] < 2)
        and (regression_data['forecast_day_PCT7_change'] < 0
            and regression_data['forecast_day_PCT10_change'] < 0
            )
        and regression_data['forecast_day_PCT2_change'] > 0
        and regression_data['weekLowChange'] > 3
        ):
        if(regression_data['week2HighChange'] < -5
            and abs_week2High_more_than_week2Low(regression_data)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupUp-lastDayDown-mayContinueBuy')  
        elif(regression_data['week2HighChange'] > -0.5):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupUp-lastDayDown-near2WeekHigh-mayReveresalSell')
    elif(-5.5 < regression_data['PCT_day_change'] < 0
        and -5.5 < regression_data['PCT_change'] < 3
        and regression_data['low'] > regression_data['low_pre1']
        and regression_data['bar_low'] > (regression_data['bar_high_pre1'] - ((regression_data['bar_high_pre1'] - regression_data['bar_low_pre1']) / 2))
        and ((regression_data['PCT_day_change_pre1'] > 2)
            or (regression_data['PCT_day_change_pre1'] > 1 and 0 > regression_data['PCT_day_change_pre2'] > -2)
            or (regression_data['PCT_day_change_pre1'] > 0 and 0 > regression_data['PCT_day_change_pre2'] > -1)
            )
        and (regression_data['forecast_day_PCT3_change'] < 0
            and regression_data['forecast_day_PCT4_change'] < 0
            and regression_data['forecast_day_PCT5_change'] < 0
            and regression_data['forecast_day_PCT7_change'] < 0
            and regression_data['forecast_day_PCT10_change'] < 0
            )
        and (regression_data['forecast_day_PCT7_change'] < -5
            or regression_data['forecast_day_PCT10_change'] < -5
            )
        and regression_data['forecast_day_PCT_change'] > 0
        and regression_data['weekLowChange'] > 0
        and regression_data['month3LowChange'] > 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupUp-start-lastDayDown-mayContinueBuy')
    elif(-5.5 < regression_data['PCT_day_change'] < 0
        and -5.5 < regression_data['PCT_change'] < 3
        and regression_data['low'] > regression_data['low_pre1']
        and regression_data['bar_low'] > (regression_data['bar_high_pre1'] - ((regression_data['bar_high_pre1'] - regression_data['bar_low_pre1']) / 2))
        and ((regression_data['PCT_day_change_pre1'] > 1.5)
            or (regression_data['PCT_day_change_pre1'] > 1 and 0 > regression_data['PCT_day_change_pre2'] > -2)
            or (regression_data['PCT_day_change_pre1'] > 0 and 0 > regression_data['PCT_day_change_pre2'] > -1)
            )
        and (regression_data['forecast_day_PCT4_change'] < 1
            and regression_data['forecast_day_PCT5_change'] < 1
            and regression_data['forecast_day_PCT7_change'] < 0
            and regression_data['forecast_day_PCT10_change'] < 0
            )
        and (regression_data['forecast_day_PCT4_change'] < -1
            or regression_data['forecast_day_PCT5_change'] < -1
            )
        and (regression_data['forecast_day_PCT7_change'] < -2
            or regression_data['forecast_day_PCT10_change'] < -2
            )
        and regression_data['forecast_day_PCT_change'] > 0
        and regression_data['weekLowChange'] > 0
        and regression_data['month3LowChange'] > 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupUp-start-lastDayDown-mayContinueBuy')
    elif(2 < regression_data['PCT_day_change'] < 5
        and 1.5 < regression_data['PCT_change'] < 5.5
        and (regression_data['forecast_day_PCT10_change'] < 1)
        and (regression_data['forecast_day_PCT7_change'] < 0
            or regression_data['forecast_day_PCT10_change'] < 0
            )
        and (regression_data['forecast_day_PCT_change'] > 0
            or regression_data['forecast_day_PCT2_change'] > 0
            or regression_data['forecast_day_PCT3_change'] > 0
            )
        and (((regression_data['low'] - regression_data['low_pre1']) / regression_data['low_pre1']) * 100) > 0
        and regression_data['weekLowChange'] > 3
        ):
        if(regression_data['week2HighChange'] > -0.5):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupUp-near2WeekHigh-mayReveresalSell')
        elif(regression_data['PCT_day_change_pre1'] > 2
            and regression_data['PCT_day_change_pre2'] > 2
            and regression_data['forecast_day_PCT5_change'] > 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupUp-3dayUp-mayReversalSell')
        elif(regression_data['PCT_day_change'] > 2
            and regression_data['PCT_day_change_pre1'] > 1
            and regression_data['PCT_day_change_pre2'] < 0
            and regression_data['PCT_day_change_pre3'] > 1
            and regression_data['forecast_day_PCT5_change'] > 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupUp-2dayUp-continue')
        elif(regression_data['PCT_day_change'] > 2
            and regression_data['PCT_day_change_pre1'] > 2
            and regression_data['forecast_day_PCT5_change'] > 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupUp-2dayUp-mayReversalSell')
        elif(2 < regression_data['PCT_day_change'] < 3
            and regression_data['week2HighChange'] < -3
            ):
            if(2 > regression_data['PCT_day_change_pre1'] > 0.5
                and regression_data['PCT_day_change_pre2'] > 0.5
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupUp-3dayUp')
            elif(2 > regression_data['PCT_day_change_pre1'] > 0.5
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupUp-2dayUp')
            elif(regression_data['forecast_day_PCT7_change'] < 1
                and regression_data['PCT_day_change_pre1'] < 0 
                and regression_data['PCT_day_change_pre2'] < 0
                and regression_data['PCT_day_change_pre3'] < 0
                and regression_data['forecast_day_PCT_change'] > 0
                and regression_data['forecast_day_PCT2_change'] > 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupUp-downTrendLastDayUp-mayReversalSell')
            elif(regression_data['forecast_day_PCT7_change'] < 1
                and (regression_data['PCT_day_change_pre2'] < 0
                    or regression_data['bar_high'] > regression_data['bar_high_pre1']
                    )
                and abs_month3High_less_than_month3Low(regression_data)
                ):
                if(regression_data['bar_high'] > regression_data['bar_high_pre1']):
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'bar_high')
                if(regression_data['forecast_day_PCT2_change'] > 1
                    and regression_data['forecast_day_PCT3_change'] > 1  
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupUp')
                else:
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupUp-inUpTrend')
            elif(regression_data['forecast_day_PCT7_change'] < 1
                and (regression_data['PCT_day_change_pre2'] < 0
                    or regression_data['bar_high'] > regression_data['bar_high_pre1']
                    )
                ):
                if(regression_data['bar_high'] > regression_data['bar_high_pre1']):
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'bar_high')
                if(regression_data['forecast_day_PCT2_change'] > 1
                    and regression_data['forecast_day_PCT3_change'] > 1  
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupUp-month3HighMTmonth3Low')
                else:
                    add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupUp-inUpTrend-month3HighMTmonth3Low')
            elif(regression_data['forecast_day_PCT7_change'] < 1
                and regression_data['PCT_day_change_pre1'] < 0 
                and regression_data['PCT_day_change_pre2'] > 0
                and regression_data['bar_high'] < regression_data['bar_high_pre1']
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupUp-mayReversalSell')


def buy_consolidation_breakout(regression_data, regressionResult, reg, ws):
    week2BarHighChange = ((regression_data['bar_high'] - regression_data['week2BarHigh']) / regression_data['bar_high']) * 100
    weekBarHighChange = ((regression_data['bar_high'] - regression_data['weekBarHigh']) / regression_data['bar_high']) * 100
    if(2 < regression_data['PCT_day_change'] < 6
        and regression_data['PCT_change'] < 6
        and (regression_data['PCT_day_change_pre1'] < 2 
             or regression_data['PCT_day_change_pre1'] < regression_data['PCT_day_change']
            )
        and (regression_data['PCT_day_change_pre1'] < 0 
             or regression_data['PCT_day_change_pre2'] < 0
             or regression_data['PCT_day_change_pre3'] < 0
            )
        # and regression_data['high'] > regression_data['high_pre3']
        and regression_data['high'] > regression_data['high_pre2']
        and regression_data['high'] > regression_data['high_pre1']
        and 0.5 < regression_data['forecast_day_PCT4_change'] < 3
        and 0 < regression_data['forecast_day_PCT3_change'] < 4
        and 0 < regression_data['forecast_day_PCT2_change'] < 4
        and 0 < regression_data['forecast_day_PCT_change'] < 3
        and 0 <= regression_data['forecast_day_PCT10_change'] <= 3
        and regression_data['bar_high'] >= regression_data['week2BarHigh']
        and (regression_data['week3BarHigh'] <= regression_data['week2BarHigh'])
        ):
        if(regression_data['weekBarHigh'] > regression_data['bar_high_pre1'] 
            and regression_data['week2BarHigh'] > regression_data['bar_high_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'brokenToday')
        if(regression_data['weekHigh'] > regression_data['week2High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'weekHighGTweek2High')
        if(week2BarHighChange > 5):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'week2BarHighChangeGT5')
        elif(week2BarHighChange > 2):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'week2BarHighChangeGT2')
        elif(week2BarHighChange > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'week2BarHighChangeGT0')
        if(regression_data['PCT_day_change'] > 2
            and regression_data['year2HighChange'] < -5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkBuyConsolidationBreakUp-2week')
        elif(regression_data['year2HighChange'] >= -5):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyConsolidationBreakUp-2week-(Risky)-year2High')
    elif(1.5 < regression_data['PCT_day_change'] < 6
        and regression_data['PCT_change'] < 6
        and regression_data['high'] > regression_data['high_pre2']
        and regression_data['high'] > regression_data['high_pre1']
        and regression_data['bar_high'] > regression_data['week2BarHigh']
        and (regression_data['bar_high'] < regression_data['week3BarHigh'] or (regression_data['bar_high'] < regression_data['week3High'] and regression_data['week3High'] != regression_data['week2High']))
        and (regression_data['bar_high_pre1'] < regression_data['week2BarHigh'] or regression_data['bar_high_pre1'] < regression_data['week2High'])
        ):
        if(regression_data['weekBarHigh'] > regression_data['bar_high_pre1'] 
            and regression_data['week2BarHigh'] > regression_data['bar_high_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'brokenToday')
        if(regression_data['weekHigh'] > regression_data['week2High']):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'weekHighGTweek2High')
        if(week2BarHighChange > 5):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'week2BarHighChangeGT5')
        elif(week2BarHighChange > 2):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'week2BarHighChangeGT2')
        elif(week2BarHighChange > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'week2BarHighChangeGT0')
        if(regression_data['PCT_day_change'] > 2
            and regression_data['year2HighChange'] < -5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkBuyConsolidationBreakUp-week2-highNotReachedWeek3')
    elif(2 < regression_data['PCT_day_change'] < 6
        and regression_data['PCT_change'] < 6
        and (regression_data['PCT_day_change_pre1'] < 0 or regression_data['PCT_day_change_pre2'] < 0)
        # and regression_data['high'] > regression_data['high_pre3']
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
        add_in_csv(regression_data, regressionResult, ws, None, None, 'checkBuyConsolidationBreakUp-month3HighLTMonth3Low')
    elif(2 < regression_data['PCT_day_change'] < 6
        and regression_data['PCT_change'] < 6
        and (regression_data['PCT_day_change_pre1'] < 0 or regression_data['PCT_day_change_pre2'] < 0)
        # and regression_data['high'] > regression_data['high_pre3']
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
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyConsolidationBreakUp-forecastDayPCT7changeGT0')
    elif(1.5 < regression_data['PCT_day_change'] < 6
        and regression_data['PCT_change'] < 6
        and regression_data['PCT_day_change_pre1'] > -1
        and regression_data['high'] > regression_data['high_pre2']
        and regression_data['high'] > regression_data['high_pre1']
        and 0.5 < regression_data['forecast_day_PCT4_change'] < 10
        and 0 < regression_data['forecast_day_PCT3_change'] < 10
        and 0 < regression_data['forecast_day_PCT2_change'] < 10
        and 0 < regression_data['forecast_day_PCT_change'] < 5
        and ((regression_data['bar_high_pre1'] <= regression_data['week2BarHigh'] and regression_data['bar_high_pre1'] < regression_data['week2High']
                and regression_data['bar_high'] >= regression_data['week2BarHigh']
                )
             or (regression_data['bar_high_pre1'] <= regression_data['week3BarHigh'] and regression_data['bar_high_pre1'] < regression_data['week3High']
                and regression_data['bar_high'] >= regression_data['week3BarHigh']
                )
             or (regression_data['bar_high_pre1'] <= regression_data['monthBarHigh'] and regression_data['bar_high_pre1'] < regression_data['monthHigh']
                and regression_data['bar_high'] >= regression_data['monthBarHigh']
                )
             or (regression_data['bar_high_pre1'] <= regression_data['month3BarHigh'] and regression_data['bar_high_pre1'] < regression_data['month3High']
                and regression_data['bar_high'] >= regression_data['month3BarHigh']
                )
            )
        ):
        if(regression_data['weekBarHigh'] > regression_data['bar_high_pre1'] 
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'brokenToday')
        if(weekBarHighChange > 5):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'weekBarHighChangeGT5')
        elif(weekBarHighChange > 2):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'weekBarHighChangeGT2')
        elif(weekBarHighChange > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'weekBarHighChangeGT0')
        if((regression_data['bar_high_pre1'] < regression_data['month3BarHigh'] or regression_data['bar_high_pre1'] < regression_data['month3High'])
            and regression_data['bar_high_pre1'] > regression_data['month6BarHigh']
            and regression_data['bar_low'] >= regression_data['month3BarHigh']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkBuyConsolidationBreakUp-month3')
        elif((regression_data['bar_high_pre1'] < regression_data['month2BarHigh'] or regression_data['bar_high_pre1'] < regression_data['month2High'])
            and regression_data['bar_high_pre1'] > regression_data['month3BarHigh']
            and regression_data['bar_low'] >= regression_data['month2BarHigh']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkBuyConsolidationBreakUp-month2')
        elif((regression_data['bar_high_pre1'] < regression_data['monthBarHigh'] or regression_data['bar_high_pre1'] < regression_data['monthHigh'])
            and regression_data['bar_high_pre1'] > regression_data['month2BarHigh']
            and regression_data['bar_low'] >= regression_data['monthBarHigh']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkBuyConsolidationBreakUp-month')
        elif((regression_data['bar_high_pre1'] < regression_data['week2BarHigh'] or regression_data['bar_high_pre1'] < regression_data['week2High'])
            and regression_data['bar_high_pre1'] > regression_data['monthBarHigh']
            and regression_data['bar_low'] >= regression_data['week2BarHigh']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkBuyConsolidationBreakUp-week2')
        
    if(regression_data['high'] > regression_data['high_pre1']
        and regression_data['high'] > regression_data['high_pre2']
        and regression_data['high'] > regression_data['high_pre3']
        and regression_data['high'] > regression_data['high_pre4']
        ):
        if(regression_data['forecast_day_PCT_change'] > 0
            and 2.5 < regression_data['PCT_day_change'] < 7
            and regression_data['bar_high'] > regression_data['bar_high_pre1']
            and regression_data['bar_high'] > regression_data['bar_high_pre2']
            and -1.5 < regression_data['PCT_day_change_pre1'] < 0
            and -1.5 < regression_data['PCT_day_change_pre2'] < 0
            and -1.5 < regression_data['PCT_day_change_pre3'] < 0 
            and -1.5 < regression_data['PCT_day_change_pre4'] < 1.5
            and (regression_data['yearHighChange'] < -10 or regression_data['PCT_day_change_pre3'] < 0)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkBuyConsolidationBreakout-allPreLT0')
        elif(regression_data['forecast_day_PCT_change'] > 0
            and 2 < regression_data['PCT_day_change'] < 4.5
            and regression_data['bar_high'] > regression_data['bar_high_pre1']
            and regression_data['bar_high'] > regression_data['bar_high_pre2']
            and -1.5 < regression_data['PCT_day_change_pre1'] < 1.5
            and -1.5 < regression_data['PCT_day_change_pre2'] < 1.5
            and -1.5 < regression_data['PCT_day_change_pre3'] < 1.5 
            and -1.5 < regression_data['PCT_day_change_pre4'] < 1.5
            and (regression_data['yearHighChange'] < -10 or regression_data['PCT_day_change_pre3'] < 0)
            ):
            if((regression_data['forecast_day_PCT10_change'] - regression_data['forecast_day_PCT5_change']) > 5
                or (regression_data['forecast_day_PCT7_change'] - regression_data['forecast_day_PCT5_change']) > 5
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisCheckConsolidationBreakout2WeekLT(4.5)')
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisCheckConsolidationBreakoutLT(4.5)')
        elif(regression_data['forecast_day_PCT_change'] > 0
            and 4.5 < regression_data['PCT_day_change'] < 7
            and regression_data['bar_high'] > regression_data['bar_high_pre1']
            and regression_data['bar_high'] > regression_data['bar_high_pre2']
            and -1.5 < regression_data['PCT_day_change_pre1'] < 1.5
            and -1.5 < regression_data['PCT_day_change_pre2'] < 1.5
            and -1.5 < regression_data['PCT_day_change_pre3'] < 1.5 
            and -1.5 < regression_data['PCT_day_change_pre4'] < 1.5
            and (regression_data['yearHighChange'] < -10 or regression_data['PCT_day_change_pre3'] < 0)
            ):
            if((regression_data['forecast_day_PCT10_change'] - regression_data['forecast_day_PCT5_change']) > 5
                or (regression_data['forecast_day_PCT7_change'] - regression_data['forecast_day_PCT5_change']) > 5
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisCheckConsolidationBreakout2WeekGT(4.5)')
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisCheckConsolidationBreakoutGT(4.5)')


def buy_supertrend(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    
    flag = False

    if ((regression_data['PCT_day_change'] < -6 or regression_data['PCT_change'] < -6)
        and (regression_data['forecast_day_PCT5_change'] < -10 or regression_data['forecast_day_PCT7_change'] < -10 or regression_data['forecast_day_PCT10_change'] < -15)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None,'%%:MayBuy-High-DownTrend')

    if(regression_data['year2HighChange'] > -3 or regression_data['year2LowChange'] < 3):
        return False
    
    if(1.5 < regression_data['PCT_day_change_pre1'] < 7.5 and 0.75 < regression_data['PCT_change_pre1'] < 8
        and regression_data['PCT_day_change_pre2'] > 0
        and ((regression_data['PCT_day_change_pre1'] > 2 or regression_data['PCT_day_change_pre2'] > 2)
             or (regression_data['PCT_day_change_pre2'] > 1 and regression_data['PCT_day_change_pre2'] > 1)
            )
        and (regression_data['PCT_day_change_pre3'] > 0 
             or regression_data['PCT_day_change_pre4'] > 0
             or low_tail_pct(regression_data) > 1.5
            )
        and (regression_data['PCT_day_change_pre1'] < 0 or regression_data['PCT_day_change_pre2'] < 0 or regression_data['PCT_day_change_pre3'] < 0 or regression_data['PCT_day_change_pre4'] < 0)     
        and -3 < regression_data['PCT_day_change'] < 1.5
        and regression_data['bar_low'] > regression_data['bar_low_pre1']
        and (regression_data['low'] > regression_data['low_pre1'] or regression_data['high'] > regression_data['high_pre1']) 
        and ((regression_data['forecast_day_PCT2_change'] > 0 and regression_data['forecast_day_PCT3_change'] > 0)
            or (regression_data['forecast_day_PCT3_change'] > 0 and regression_data['forecast_day_PCT4_change'] > 0)
            )
        and regression_data['forecast_day_PCT10_change'] < 15
        and ((regression_data['forecast_day_PCT7_change'] < 0 and regression_data['forecast_day_PCT10_change'] < 0)
            or (regression_data['forecast_day_PCT3_change'] > 0
                and regression_data['forecast_day_PCT4_change'] > 0
                and regression_data['forecast_day_PCT5_change'] > 0
                and regression_data['forecast_day_PCT7_change'] > 0
                and regression_data['forecast_day_PCT10_change'] > 0
                )
            )
        and low_tail_pct(regression_data) >= 0.9
        and (high_tail_pct(regression_data) <= low_tail_pct(regression_data))
        and (regression_data['monthHighChange'] > 2 or regression_data['monthLowChange'] > 10 or regression_data['month3LowChange'] > 10)
        and regression_data['month6HighChange'] < 0
        ):
        if(regression_data['PCT_day_change'] < 0
            and (high_tail_pct(regression_data) <= low_tail_pct(regression_data))
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%:buyUptrend-lastDayDown-ReversalLowTail')
        elif(regression_data['PCT_day_change'] > 0
            and regression_data['PCT_day_change_pre1'] > 4
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%:buyUptrend-lastDayUp-ReversalLowTail')
        flag = True
    
    if(-0.5 < regression_data['PCT_day_change'] < 0.5
        and (regression_data['PCT_day_change'] < 0 or regression_data['PCT_day_change_pre1'] < 0)
        and (regression_data['PCT_day_change'] > 0 or regression_data['PCT_day_change_pre1'] > 0)
        and (regression_data['PCT_day_change_pre1'] < 0 or regression_data['PCT_day_change_pre2'] < 0)
        and (regression_data['PCT_day_change_pre1'] > 1 or regression_data['PCT_day_change_pre2'] > 1)
        and abs(regression_data['PCT_day_change_pre1']) > 1
        and (regression_data['bar_low'] > regression_data['bar_low_pre1'] > regression_data['bar_low_pre2'])
        and (high_tail_pct(regression_data) > 1 or low_tail_pct(regression_data) > 1)
        and regression_data['forecast_day_PCT3_change'] > 0
        and regression_data['forecast_day_PCT4_change'] > 0
        and regression_data['forecast_day_PCT5_change'] > 0
        and regression_data['forecast_day_PCT7_change'] > 0
        and 0 < regression_data['forecast_day_PCT10_change'] < 15
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '%%:buyUpTrendDoji-0')
        return True
    elif(-0.5 < regression_data['PCT_day_change'] < 0.5
        and (regression_data['PCT_day_change'] < 0 or regression_data['PCT_day_change_pre1'] < 0)
        and (regression_data['PCT_day_change'] > 0 or regression_data['PCT_day_change_pre1'] > 0)
        and (regression_data['PCT_day_change_pre1'] < 0 or regression_data['PCT_day_change_pre2'] < 0)
        and (regression_data['PCT_day_change_pre1'] > 1 or regression_data['PCT_day_change_pre2'] > 1)
        and abs(regression_data['PCT_day_change_pre1']) > 1
        and (regression_data['low'] > regression_data['low_pre1'] > regression_data['low_pre2'])
        and (high_tail_pct(regression_data) > 1 or low_tail_pct(regression_data) > 1)
        and regression_data['forecast_day_PCT3_change'] > 0
        and regression_data['forecast_day_PCT4_change'] > 0
        and regression_data['forecast_day_PCT5_change'] > 0
        and regression_data['forecast_day_PCT7_change'] > 0
        and 0 < regression_data['forecast_day_PCT10_change'] < 15
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '%%:buyUpTrendDoji-1')
        return True

    if (-2.5 < regression_data['PCT_day_change'] < 1
        and -2.5 < regression_data['PCT_change'] < 1
        and regression_data['PCT_day_change_pre1'] > 3.5
        and abs(regression_data['PCT_day_change_pre1']) > 3*abs(regression_data['PCT_day_change'])
        #and (regression_data['bar_low'] > regression_data['bar_low_pre1'] > regression_data['bar_low_pre2'])
        #and regression_data['forecast_day_PCT3_change'] > 0
        #and regression_data['forecast_day_PCT4_change'] > 0
        #and regression_data['forecast_day_PCT5_change'] > 0
        #and regression_data['forecast_day_PCT7_change'] > 0
        #and 0 < regression_data['forecast_day_PCT10_change'] < 15
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '%%:buyUpDojiPre1')
        return True
    elif (-1.5 < regression_data['PCT_day_change'] < 1.5
        and  - 1.5 < regression_data['PCT_change'] < 1.5
        and  - 1.5 < regression_data['PCT_day_change_pre1'] < 1.5
        and regression_data['PCT_day_change_pre2'] > 3
        and abs(regression_data['PCT_day_change_pre2']) > 3 * abs(regression_data['PCT_day_change'])
        and abs(regression_data['PCT_day_change_pre2']) > 3 * abs(regression_data['PCT_day_change_pre1'])
        #and (regression_data['bar_low'] > regression_data['bar_low_pre1'])
        and (regression_data['bar_low'] > regression_data['bar_low_pre2'])
        and regression_data['forecast_day_PCT3_change'] > 0
        and regression_data['forecast_day_PCT4_change'] > 0
        and regression_data['forecast_day_PCT5_change'] > 0
        and regression_data['forecast_day_PCT7_change'] > 0
        and 0 < regression_data['forecast_day_PCT10_change'] < 15
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '%%:buyUpDojiPre2')
        return True

    if((abs(regression_data['week2HighChange']) > 3 or abs(regression_data['week2LowChange']) > 3)
        and regression_data['monthLowChange'] > 10
        and (regression_data['PCT_day_change_pre1'] < -1.5
            or regression_data['PCT_day_change_pre2'] < -1.5
            or regression_data['PCT_day_change_pre3'] < -1.5
            or (regression_data['PCT_day_change_pre1'] > 0 
                 and regression_data['PCT_day_change_pre2'] > 0
                 and low_tail_pct(regression_data) < abs(regression_data['PCT_day_change'])
                )
            )
        ):
        if(-7 < regression_data['month3HighChange'] < 0
            and -7 < regression_data['monthHighChange'] < 0
            and -7 < regression_data['week2HighChange'] < 0
            and -2 < regression_data['weekHighChange'] < 0
            and regression_data['month3HighChange'] == regression_data['monthHighChange']
            and regression_data['week2HighChange'] == regression_data['weekHighChange']
            and regression_data['month3LowChange'] > 10
            and 0 < regression_data['PCT_day_change'] < 3
            and 0 < regression_data['PCT_change'] < 5
            ):
            if(regression_data['PCT_day_change_pre1'] < 0 
                and (regression_data['PCT_day_change_pre3'] < 0 or regression_data['PCT_day_change_pre4'] < 0)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSell:monthHigh-alternateDayDown')
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSell:monthHigh')
            return True
        elif(-2 < regression_data['month3HighChange'] < 0
            and -2 < regression_data['monthHighChange'] < 0
            and -2 < regression_data['week2HighChange'] < 0
            and -2 < regression_data['weekHighChange'] < 0
            and regression_data['month3HighChange'] == regression_data['monthHighChange'] 
            and regression_data['monthHighChange'] == regression_data['week2HighChange']
            and abs(regression_data['bar_high'] - regression_data['month3BarHigh']) < 1
            and regression_data['month3LowChange'] > 10
            and 0 < regression_data['PCT_day_change'] < 3
            and 0 < regression_data['PCT_change'] < 5
            ):
            if(regression_data['PCT_day_change_pre1'] < 0 
                and (regression_data['PCT_day_change_pre3'] < 0 or regression_data['PCT_day_change_pre4'] < 0)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSell:01-monthHigh-alternateDayDown')
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSell:01-monthHigh')
            return True
        elif(-7 < regression_data['month3HighChange'] < 0
            and -7 < regression_data['monthHighChange'] < 0
            and -7 < regression_data['week2HighChange'] < 0
            and -7 < regression_data['weekHighChange'] < 0
            and regression_data['month3HighChange'] == regression_data['monthHighChange'] 
            and regression_data['monthHighChange'] == regression_data['week2HighChange']
            and regression_data['week2HighChange'] < regression_data['weekHighChange']
            and regression_data['month3LowChange'] > 10
            and 0 < regression_data['PCT_day_change'] < 3
            and 0 < regression_data['PCT_change'] < 5
            ):
            if(regression_data['PCT_day_change_pre1'] < 0 
                and (regression_data['PCT_day_change_pre3'] < 0 or regression_data['PCT_day_change_pre4'] < 0)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSell:02-monthHigh-alternateDayDown')
            elif(regression_data['bar_high'] > regression_data['bar_high_pre2']):
                add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkBuy:01-monthHigh')
            return True
        elif(-2 < regression_data['forecast_day_PCT5_change'] < 2
            and regression_data['forecast_day_PCT2_change'] > regression_data['forecast_day_PCT_change'] > 0
            and (regression_data['forecast_day_PCT7_change'] > 10 or regression_data['forecast_day_PCT10_change'] > 10)
            and (regression_data['PCT_day_change_pre3'] > 4 or regression_data['PCT_day_change_pre4'] > 4)
            and (regression_data['PCT_day_change_pre2'] < 0 and regression_data['PCT_day_change_pre3'] < 0)
            and (regression_data['PCT_day_change'] > 0 and regression_data['PCT_day_change_pre1'] > 0)
            and regression_data['bar_high'] > regression_data['bar_high_pre2']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkBuy:00-monthHigh')
            return True
        elif(-7 < regression_data['month3HighChange'] < 0
            and -7 < regression_data['monthHighChange'] < 0
            and -7 < regression_data['week2HighChange'] < 0
            and -7 < regression_data['weekHighChange'] < 0
            and (regression_data['month3HighChange'] == regression_data['monthHighChange'] 
                 or regression_data['monthHighChange'] == regression_data['week2HighChange']
                )
            and regression_data['week2HighChange'] == regression_data['weekHighChange']
            and 0 < regression_data['PCT_day_change'] < 3
            and 0 < regression_data['PCT_change'] < 5
            ):
            if(regression_data['PCT_day_change_pre1'] < 0 
                and (regression_data['PCT_day_change_pre3'] < 0 or regression_data['PCT_day_change_pre4'] < 0)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSell:Super03-monthHigh-alternateDayDown')
            elif(regression_data['bar_high'] > regression_data['bar_high_pre2']):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuy:Super03-monthHigh')
            return True
        
    if(regression_data['month3HighChange'] > 2
            and regression_data['monthHighChange'] > 2
            and regression_data['week2HighChange'] > 2
            and -2 < regression_data['weekHighChange'] 
            and (regression_data['month3HighChange'] == regression_data['monthHighChange'] 
                 and regression_data['monthHighChange'] == regression_data['week2HighChange']
                )
            and regression_data['year2HighChange'] < 0
            and regression_data['PCT_day_change'] < -2
            and regression_data['PCT_change'] < -2
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuy:continueUptrend')
            return True

    if (regression_data['close'] > 150
        and regression_data['forecast_day_PCT5_change'] > 2
        and regression_data['forecast_day_PCT7_change'] > 2
        and regression_data['forecast_day_PCT10_change'] > 2
        and (regression_data['forecast_day_PCT10_change'] > regression_data['forecast_day_PCT7_change'] > regression_data['forecast_day_PCT5_change']
             or regression_data['forecast_day_PCT4_change'] > regression_data['forecast_day_PCT3_change'] > 3
            )
        # and high_tail_pct(regression_data) > regression_data['PCT_day_change']
        # and low_tail_pct(regression_data) > regression_data['PCT_day_change']
        and regression_data['year2HighChange'] < -5
        and regression_data['yearLowChange'] > 10
        and regression_data['month3LowChange'] > 10
        ):
        if(-0.75 < regression_data['PCT_day_change'] < 1.5
            and -0.75 < regression_data['PCT_change'] < 1.5
            and -1 < regression_data['PCT_day_change_pre1'] < 1.5
            and -1 < regression_data['PCT_change_pre1'] < 1.5
            and (3 < regression_data['PCT_day_change_pre2'] < 8 or 3 < regression_data['PCT_day_change_pre3'] < 8)
            and (3 < regression_data['PCT_change_pre2'] < 8 or 3 < regression_data['PCT_change_pre3'] < 8)
            and -0.5 < regression_data['forecast_day_PCT_change']
            and -0.5 < regression_data['forecast_day_PCT2_change']
            and -0.5 < regression_data['forecast_day_PCT3_change']
            and -0.5 < regression_data['forecast_day_PCT4_change']
            and (regression_data['forecast_day_PCT_change'] < 0.1
                or regression_data['forecast_day_PCT2_change'] < 0.1
                or regression_data['forecast_day_PCT3_change'] < 0.1
                )
            and (abs(regression_data['PCT_day_change_pre2']) > 2*abs(regression_data['PCT_day_change'])
                or abs(regression_data['PCT_day_change_pre3']) > 3*abs(regression_data['PCT_day_change'])
                )
            and (regression_data['monthHighChange'] > -1 or regression_data['month3LowChange'] > 5)
            #and abs(regression_data['yearHighChange']) < abs(regression_data['yearLowChange'])
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkBuyAtS1:Super000000000')
            flag = True
    elif (regression_data['close'] > 150
        #and regression_data['year2HighChange'] < -5
        and regression_data['yearLowChange'] > 10
        and regression_data['month3LowChange'] > 10
        ):
        if(-0.75 < regression_data['PCT_day_change'] < 1.5
            and -0.75 < regression_data['PCT_change'] < 1.5
            and (2.5 < regression_data['PCT_day_change_pre1'] < 8 or 2.5 < regression_data['PCT_day_change_pre2'] < 8)
            and (2.5 < regression_data['PCT_change_pre1'] < 8 or 2.5 < regression_data['PCT_change_pre2'] < 8)
            and (abs(regression_data['PCT_day_change_pre2']) > 3*abs(regression_data['PCT_day_change'])
                or abs(regression_data['PCT_day_change_pre3']) > 3*abs(regression_data['PCT_day_change'])
                )
            and regression_data['high'] > regression_data['high_pre1']
            and regression_data['high'] > regression_data['high_pre2']
            and regression_data['week2HighChange'] > -1
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkBuy:SuperDoji')
            flag = True
    elif(regression_data['close'] > 50
        and regression_data['forecast_day_PCT7_change'] > 0
        and regression_data['forecast_day_PCT10_change'] > 0
        and high_tail_pct(regression_data) > regression_data['PCT_day_change']
        and low_tail_pct(regression_data) > regression_data['PCT_day_change']
        and regression_data['year2HighChange'] < -5
        and regression_data['yearLowChange'] > 15
        and regression_data['month3LowChange'] > 10 
        ):
        if(-0.75 < regression_data['PCT_day_change'] < 3
            and ((regression_data['PCT_day_change_pre1'] > 5 and high_tail_pct(regression_data) < 1.5)
                 or (regression_data['PCT_day_change_pre2'] > 5 and high_tail_pct(regression_data) < 1.5)
                )
            and 0 < regression_data['forecast_day_PCT_change']
            and 0 < regression_data['forecast_day_PCT2_change']
            and 0 < regression_data['forecast_day_PCT3_change']
            and 0 < regression_data['forecast_day_PCT4_change']
            
            # and regression_data['low'] > regression_data['low_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkBuy:Super0') 
            flag = True
    elif(regression_data['close'] > 50
        and regression_data['forecast_day_PCT7_change'] > 0
        and regression_data['forecast_day_PCT10_change'] > 0
        and high_tail_pct(regression_data) < 3.5 
        ):
        if(-0.75 < regression_data['PCT_day_change'] < 0.75
            and -0.75 < regression_data['PCT_day_change_pre1'] < 0.75
            and -0.75 < regression_data['PCT_day_change_pre2'] < 0.75
            and 3 < regression_data['PCT_day_change_pre3'] < 10
            and regression_data['forecast_day_PCT7_change'] > 10
            and regression_data['forecast_day_PCT10_change'] > 10
            and 0 < regression_data['forecast_day_PCT_change']
            and 0 < regression_data['forecast_day_PCT2_change']
            and 0 < regression_data['forecast_day_PCT3_change']
            and 0 < regression_data['forecast_day_PCT4_change']
            and regression_data['yearHighChange'] < -5
            and regression_data['yearLowChange'] > 15
            and regression_data['month3LowChange'] > 10 
            # and regression_data['low'] > regression_data['low_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkBuy:Super1') 
            flag = True
        elif(-2 < regression_data['PCT_day_change'] < 0 and (abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change']))
            and (2 < regression_data['PCT_day_change_pre1'] < 5 and 2 < regression_data['PCT_day_change_pre2'] < 5)
            and 0 < regression_data['forecast_day_PCT_change'] < regression_data['forecast_day_PCT2_change'] < regression_data['forecast_day_PCT3_change']
            and regression_data['high_pre2'] < regression_data['high_pre1'] < regression_data['high']
            and regression_data['forecast_day_PCT7_change'] < 15
            and regression_data['forecast_day_PCT10_change'] < 15
            and (regression_data['month3HighChange'] < -10
                 or regression_data['month6HighChange'] < -10
                 or regression_data['yearHighChange'] < -10
                 or regression_data['year2HighChange'] < -10
                 )
            and regression_data['yearHighChange'] < -5
            and regression_data['yearLowChange'] > 10
            ):
            if(high_tail_pct(regression_data) < 3.5 
                and low_tail_pct(regression_data) < 2.5
                and regression_data['forecast_day_PCT7_change'] < 13
                and regression_data['forecast_day_PCT10_change'] < 13
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkBuy:Super3')
                flag = True
            elif(high_tail_pct(regression_data) > 1.5
                and low_tail_pct(regression_data) > 2.5
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None)
                flag = True
        elif(-2 < regression_data['PCT_day_change'] < 0 and (abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change']))
            and (2 < regression_data['PCT_day_change_pre1'] < 7 and 2 < regression_data['PCT_day_change_pre2'] < 10)
            and (abs(regression_data['PCT_day_change_pre2']) > abs(regression_data['PCT_day_change_pre1']))
            # and 0 < regression_data['forecast_day_PCT_change'] < regression_data['forecast_day_PCT2_change'] < regression_data['forecast_day_PCT3_change']
            # and regression_data['forecast_day_PCT7_change'] < 30
            # and regression_data['forecast_day_PCT10_change'] < 30
            and (regression_data['month3HighChange'] < -10
                 or regression_data['month6HighChange'] < -10
                 or regression_data['yearHighChange'] < -10
                 or regression_data['year2HighChange'] < -10
                 )
            and regression_data['yearHighChange'] < -5
            and regression_data['yearLowChange'] > 10
            ):
            if(high_tail_pct(regression_data) < 3.5 
                and low_tail_pct(regression_data) < 2.5
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkBuy:Super4')
                flag = True
            elif(high_tail_pct(regression_data) > 1.5
                and low_tail_pct(regression_data) > 2.5
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None)
                flag = True
        
        if(-0.75 < regression_data['PCT_day_change_pre1'] < 5
            and -0.75 < regression_data['PCT_day_change'] < 0.5
            and (regression_data['PCT_day_change'] > 0 or regression_data['PCT_day_change_pre1'] > 0)
            and 0 < regression_data['forecast_day_PCT2_change'] < regression_data['forecast_day_PCT3_change'] < regression_data['forecast_day_PCT4_change']
            and regression_data['high_pre3'] < regression_data['high_pre2'] < regression_data['high_pre1'] 
            and (regression_data['forecast_day_PCT4_change'] > 5
                or regression_data['forecast_day_PCT5_change'] > 5
                )
            and (regression_data['forecast_day_PCT10_change'] < regression_data['forecast_day_PCT5_change']
                or regression_data['forecast_day_PCT10_change'] < regression_data['forecast_day_PCT7_change']
                )
            and (regression_data['PCT_day_change_pre1'] > 3 
                or regression_data['PCT_day_change_pre2'] > 3 
                or regression_data['PCT_day_change_pre3'] > 3
                )
            and (regression_data['PCT_day_change_pre1'] > 3 
                or regression_data['PCT_day_change_pre2'] > 3 
                or (regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change_pre2'] > 0)
                )
            and regression_data['yearHighChange'] < -5
            and regression_data['yearLowChange'] > 15
            and regression_data['month3LowChange'] > 10 
            # and regression_data['low'] > regression_data['low_pre1']
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
            
            if(regression_data['PCT_day_change_pre1'] < 0.75):
                add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkBuy:Super-Risky')
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuySuper-Risky')
            flag = True
        elif(1.5 < regression_data['PCT_day_change_pre1'] < 5 and (abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change']))
            and (regression_data['PCT_day_change_pre2'] > 1.5 or regression_data['PCT_day_change_pre3'] > 1.5)
            and -1.5 < regression_data['PCT_day_change'] < 0
            # and (regression_data['PCT_day_change'] > 0 or regression_data['PCT_day_change_pre1'] > 0)
            and 0 < regression_data['forecast_day_PCT2_change'] < regression_data['forecast_day_PCT3_change'] < regression_data['forecast_day_PCT4_change'] 
            and regression_data['high_pre3'] < regression_data['high_pre2'] < regression_data['high_pre1']
            and regression_data['forecast_day_PCT5_change'] > 5
            and (regression_data['forecast_day_PCT7_change'] < 15 or regression_data['forecast_day_PCT10_change'] < 15)
            and (regression_data['forecast_day_PCT7_change'] < 20 and regression_data['forecast_day_PCT10_change'] < 20)
            and regression_data['yearHighChange'] < -10
            and regression_data['yearLowChange'] > 10
            # and regression_data['month3LowChange'] > 10
            # and high_tail_pct(regression_data) < 2.5   
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
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkBuy:Super2')
            flag = True
            
    if(abs_monthHigh_less_than_monthLow(regression_data)
        and regression_data['week2HighChange'] == regression_data['weekHighChange']
        and regression_data['week2LowChange'] != regression_data['weekLowChange']
        and regression_data['weekHighChange'] < -2
        and regression_data['weekLowChange'] > 2
        and (regression_data['forecast_day_PCT2_change'] < 0.5
            or regression_data['forecast_day_PCT3_change'] < 0.5
            or regression_data['forecast_day_PCT4_change'] < 0.5
            )
        and regression_data['high_pre1'] < regression_data['weekHigh'] - 1
        and regression_data['high_pre2'] < regression_data['weekHigh']
        ):
        if(-0.75 < regression_data['PCT_day_change'] < 0
            and(regression_data['PCT_day_change_pre1'] > 2
                or regression_data['PCT_day_change_pre2'] > 2
                or regression_data['PCT_day_change_pre3'] > 2
                or regression_data['PCT_day_change_pre4'] > 2
                or regression_data['PCT_day_change_pre5'] > 2
               )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyFlagWeek-doji')
            flag = True
        elif(2 < regression_data['PCT_day_change'] and 0 < regression_data['PCT_change']
            # and regression_data['PCT_day_change_pre1'] > -1.5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyFlagWeek')
            flag = True
    elif(abs_month3High_less_than_month3Low(regression_data)
        and regression_data['monthHighChange'] == regression_data['week2HighChange']
        and regression_data['monthLowChange'] != regression_data['week2LowChange']
        and regression_data['weekHighChange'] < -2
        and regression_data['weekLowChange'] > 2
        and (regression_data['forecast_day_PCT2_change'] < 0
            or regression_data['forecast_day_PCT3_change'] < 0
            or regression_data['forecast_day_PCT4_change'] < 0
            or regression_data['forecast_day_PCT5_change'] < 0
            )
        and regression_data['high_pre1'] < regression_data['week2High'] - 2
        and regression_data['high_pre2'] < regression_data['week2High']
        ):
        if (-0.75 < regression_data['PCT_day_change'] < 0 
            and regression_data['PCT_day_change_pre1'] < regression_data['PCT_day_change']
            and regression_data['PCT_day_change_pre2'] < 0
            and (regression_data['low'] < regression_data['low_pre1']
                 or regression_data['PCT_day_change_pre1'] < -1
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyFlag2Week-doji')
            flag = True
        elif(2 < regression_data['PCT_day_change'] < 4 and 0 < regression_data['PCT_change']
            and regression_data['PCT_day_change_pre1'] > -1.5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyFlag2Week')
            flag = True
            
    elif(regression_data['week2HighChange'] >= regression_data['weekHighChange']
        and regression_data['week2LowChange'] != regression_data['weekLowChange']
        and regression_data['weekHighChange'] < -1
        and regression_data['weekLowChange'] > 1
        and (regression_data['forecast_day_PCT2_change'] < 0.5
            or regression_data['forecast_day_PCT3_change'] < 0.5
            or regression_data['forecast_day_PCT4_change'] < 0.5
            )
        and regression_data['high_pre1'] < regression_data['weekHigh'] - 1
        and regression_data['high_pre2'] < regression_data['weekHigh']
        ):
        if (-0.75 < regression_data['PCT_day_change'] < 0 
            and regression_data['PCT_day_change_pre1'] < regression_data['PCT_day_change']
            and regression_data['PCT_day_change_pre2'] < 0
            and (regression_data['low'] < regression_data['low_pre1']
                 or regression_data['PCT_day_change_pre1'] < -1
                )
            and(regression_data['PCT_day_change_pre3'] > 2
                or regression_data['PCT_day_change_pre4'] > 2
                or regression_data['PCT_day_change_pre5'] > 2
               )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyFlagWeek-doji-Risky')
            flag = True
        elif(2 < regression_data['PCT_day_change'] < 4 and 0 < regression_data['PCT_change'] 
            and regression_data['PCT_day_change_pre1'] > -1.5
            and regression_data['week2HighChange'] < -2
            and regression_data['weekLowChange'] > 2
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyFlagWeek-Risky')
            flag = True
    elif(regression_data['monthHighChange'] >= regression_data['week2HighChange']
        and regression_data['monthLowChange'] != regression_data['week2LowChange']
        and regression_data['week2HighChange'] < -1
        and regression_data['week2LowChange'] > 1
        and (regression_data['forecast_day_PCT2_change'] < 0
            or regression_data['forecast_day_PCT3_change'] < 0
            or regression_data['forecast_day_PCT4_change'] < 0
            or regression_data['forecast_day_PCT5_change'] < 0
            )
        and regression_data['high_pre1'] < regression_data['week2High'] - 2
        and regression_data['high_pre2'] < regression_data['week2High']
        ):
        if (-0.75 < regression_data['PCT_day_change'] < 0 
            and regression_data['PCT_day_change_pre1'] < regression_data['PCT_day_change']
            and regression_data['PCT_day_change_pre2'] < 0
            and (regression_data['low'] < regression_data['low_pre1']
                 or regression_data['PCT_day_change_pre1'] < -1
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyFlag2Week-doji-Risky')
            flag = True
        elif (2 < regression_data['PCT_day_change'] < 4 and 0 < regression_data['PCT_change']
            and regression_data['PCT_day_change_pre1'] > -1.5
            and regression_data['PCT_day_change_pre1'] < regression_data['PCT_day_change']
            and regression_data['PCT_day_change_pre2'] < regression_data['PCT_day_change']
            and regression_data['week2HighChange'] < -2
            and regression_data['weekLowChange'] > 2
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyFlag2Week-Risky')
            flag = True
    
    if(regression_data['week2HighChange'] == regression_data['weekHighChange']
        and regression_data['week2LowChange'] == regression_data['weekLowChange']
        and regression_data['weekHighChange'] < -2
        and regression_data['weekLowChange'] > 2
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None)
    
    if('checkBuyConsolidationBreakUp-2week' in regression_data['filter']
        and 1.5 < regression_data['PCT_day_change'] < 5
        and 1.5 < regression_data['PCT_change'] < 5
        and (regression_data['PCT_day_change_pre1'] < regression_data['PCT_day_change'] / 2
            # or 'MLBuy' in regression_data['filter']
            # or 'brokenToday' in regression_data['filter']
            )
        and (regression_data['PCT_day_change'] > 2 
            # or 'MLBuy' in regression_data['filter']
            or 'brokenToday' in regression_data['filter']
            )
        and (regression_data['month3HighChange'] < -5 or abs_month3High_more_than_month3Low(regression_data))
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkBuy:ConsolidationBreakUp(NotShapeV)-2week')
        flag = True
        
    if(-2.5 < regression_data['PCT_day_change'] < 2.5
        and -3.5 < regression_data['PCT_change'] < 3.5
        and regression_data['PCT_day_change_pre1'] > 1
        and abs(regression_data['PCT_day_change_pre1']) > 2 * (abs(regression_data['PCT_day_change']))
        and (regression_data['forecast_day_PCT5_change'] < 0
            and regression_data['forecast_day_PCT7_change'] < 0
            )
        and (regression_data['forecast_day_PCT2_change'] > 0 or regression_data['forecast_day_PCT_change'] > 0)
        and regression_data['week2HighChange'] < -5
        and abs_week2High_more_than_week2Low(regression_data)
        ):
        if(regression_data['weekLowChange'] > 3
            and (regression_data['PCT_day_change_pre1'] > 2 or regression_data['PCT_day_change_pre2'] > 2)
            ):
            if(regression_data['PCT_day_change_pre1'] > 2 
                and regression_data['PCT_day_change'] < 0
                ):
                if(regression_data['PCT_day_change_pre2'] > 0 or regression_data['PCT_day_change_pre3'] > 0):
                    add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkBuy:CupUpDoji')
                    flag = True    
            elif(regression_data['PCT_day_change_pre1'] > 2 
                and -.75 < regression_data['PCT_day_change'] < 0.75
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkBuy:CupUpDoji-lastDayGT2TodayDoji')
                flag = True
            elif(regression_data['PCT_day_change_pre2'] > 0 
                or regression_data['PCT_day_change'] < 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkBuy:CupUpDoji-last2lastDayGT0orTodayLT0')
                flag = True
            elif(regression_data['weekLowChange'] > 3
                and 1 < regression_data['PCT_day_change_pre1'] < 2 and 1 < regression_data['PCT_day_change_pre2'] < 2.5
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellContinueCupUpDoji-last2dayUp')
                flag = True      
        elif(regression_data['weekLowChange'] < 2.5
            and abs(regression_data['PCT_day_change']) < 1
            and regression_data['week2LowChange'] == regression_data['weekLowChange']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellContinueCupUpDoji')
            flag = True
        elif(1 < regression_data['PCT_day_change_pre1'] < 2 and 1 < regression_data['PCT_day_change_pre2'] < 2):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellContinueCupUpDoji-last2dayUp')
            flag = True
    
    if(4.5 < regression_data['PCT_day_change_pre1'] < 7.5 and 3 < regression_data['PCT_change_pre1'] < 10
        and (-1.5 < regression_data['PCT_day_change'] < 0 and -1.5 < regression_data['PCT_change'] < 0)  
        and (regression_data['PCT_day_change_pre2'] < 0 or regression_data['PCT_day_change_pre3'] < 0)
        and (regression_data['PCT_day_change_pre3'] < 0 or regression_data['PCT_day_change_pre4'] < 0)
        and (regression_data['PCT_day_change_pre2'] < 3 and regression_data['PCT_day_change_pre3'] < 3)
        and regression_data['forecast_day_PCT3_change'] > 0
        and regression_data['forecast_day_PCT4_change'] > 0
        and regression_data['high'] > regression_data['high_pre1']
        and regression_data['low'] > regression_data['low_pre1']
        and regression_data['month3LowChange'] > 10
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuylastDayGT(4.5)') 
    elif(4.5 < regression_data['PCT_day_change_pre1'] < 10 and 3 < regression_data['PCT_change_pre1'] < 10
        and (regression_data['PCT_day_change'] < -1 and regression_data['PCT_change'] < -1)   
        and regression_data['low'] < (regression_data['high_pre1'] - ((regression_data['high_pre1'] - regression_data['low_pre1']) / 2))
        # and regression_data['low'] > regression_data['low_pre1']
        and regression_data['month3HighChange'] > 0
        and low_tail_pct(regression_data) < 1.3
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSelllastDayGT(4.5)')
    elif(4.5 < regression_data['PCT_day_change_pre2'] < 10 and 0 < regression_data['PCT_change_pre2'] < 10
        and (regression_data['PCT_day_change_pre1'] < 0 and regression_data['PCT_change_pre1'] < 0)
        and (regression_data['PCT_day_change'] < -1 and regression_data['PCT_change'] < -1)  
        and regression_data['low'] > regression_data['low_pre2']
        and regression_data['month3HighChange'] > 0
        ):
        if(3 < regression_data['PCT_change_pre2'] < 10
            and abs(regression_data['PCT_day_change']) > abs(regression_data['PCT_day_change_pre1']) < 1
            and regression_data['low'] > (regression_data['high_pre2'] - ((regression_data['high_pre2'] - regression_data['low_pre2']) / 2))
            and low_tail_pct(regression_data) < 1.3
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSelllast2LastDayGT(4.5)')                            
    
    if(-7 < regression_data['PCT_day_change'] < -4 and -7 < regression_data['PCT_day_change_pre1'] < -4
        and (regression_data['PCT_day_change'] < -5.5 and regression_data['PCT_day_change_pre1'] < -5.5 and regression_data['PCT_day_change_pre2'] > -2)
        and regression_data['PCT_day_LC'] >= 1
        and (regression_data['month3LowChange'] > 15 or regression_data['month3LowChange'] < 0)
        and (regression_data['month3HighChange'] < -10 or regression_data['month3HighChange'] > 0)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyReversalLast2DayLow(LT-4)')
        flag = True

    if (regression_data['year2HighChange'] > -3
        and regression_data['month3LowChange'] > 15
        ):
        if(regression_data['PCT_day_change'] > 2
            and regression_data['PCT_change'] > 0
            and regression_data['PCT_day_change_pre1'] < 0
            and regression_data['PCT_change_pre1'] < 1
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '%%:Z_:NearOrUpYear2High, PCTdaychangepre1LT0')
            flag = True
        if (regression_data['PCT_day_change'] < 0.5
            and regression_data['PCT_change'] < 1
            and regression_data['PCT_day_change_pre1'] > 1.5
            and regression_data['PCT_change_pre1'] > 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, '%%:Z_:NearOrUpYear2High, PCTdaychangeDoji')
            flag = True
    
    return flag

#



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
                 or (("downTrend" in regression_data['series_trend']) and (1.5 < regression_data['PCT_change'] < 3) and (1.5 < regression_data['PCT_day_change'] < 3)))
            and regression_data['high'] > regression_data['high_pre1']
            and regression_data['bar_high'] > regression_data['bar_high_pre1']
            # and regression_data['SMA4_2daysBack'] < 0
            ):
            if(regression_data['SMA4_2daysBack'] > 0.5 and regression_data['SMA9_2daysBack'] > 0.5
                and (regression_data['SMA4_2daysBack'] > 1 or regression_data['SMA9_2daysBack'] > 1)
                and ('[') not in regression_data['sellIndia']
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '##buyMonth3High-Continue')
                return True
            elif(regression_data['SMA4_2daysBack'] < -0.5 and regression_data['SMA9_2daysBack'] < -0.5
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '##sellMonth3High-Continue')
                return True
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, '##Month3High-Continue')
                return True
            return False
    return False 


def buy_market_uptrend(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
#    return False
    
    if(3 < regression_data['PCT_day_change'] < 7 and 3 < regression_data['PCT_day_change_pre1'] < 7 and 3 < regression_data['PCT_day_change_pre2'] < 7
        and (3 < regression_data['PCT_change'] and 3 < regression_data['PCT_change_pre1']) 
        ):
        if(regression_data['month3HighChange'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##last3DayHighGT3-M3HGT0')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, '##last3DayHighGT3-M3HLT0')
        flag = True
    elif(3 < regression_data['PCT_day_change'] < 7 and 3 < regression_data['PCT_day_change_pre1'] < 7
        and (3 < regression_data['PCT_change'])
        ):
        if(regression_data['month3HighChange'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##last2DayHighGT3-M3HGT0')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, '##last2DayHighGT3-M3HLT0')
        flag = True
    elif(5 < regression_data['PCT_day_change_pre1'] < 10 and 1 < regression_data['PCT_day_change'] < 5
        and (3 < regression_data['PCT_change'])
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '##lastDayHighGT5TodayGT1')
        flag = True
    
    if(('[' not in regression_data['sellIndia'])
        and ((1.5 < regression_data['PCT_change'] < 6) 
            and (1.5 < regression_data['PCT_day_change'] < 6)
            and regression_data['close'] > regression_data['bar_high_pre1']
            )
        and regression_data['SMA4_2daysBack'] > -1
        and regression_data['SMA4'] > -1
        and regression_data['SMA9'] > -10
        # and regression_data['trend'] == 'up'
        ):
        if(('ReversalLowYear2' in regression_data['filter3']) and (regression_data['year2HighChange'] < -40)):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##UPTREND:buyYear2LowReversal(Confirm)')
            return True
        if(('ReversalLowYear' in regression_data['filter3']) and (regression_data['yearHighChange'] < -30)):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##UPTREND:buyYearLowReversal(Confirm)')
            return True
        if(('ReversalLowMonth6' in regression_data['filter3']) and (regression_data['month6HighChange'] < -25)):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##UPTREND:buyMonth6LowReversal(Confirm)')
            return True
        if(('ReversalLowMonth3' in regression_data['filter3']) and (regression_data['month3HighChange'] < -15)):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##UPTREND:buyMonth3LowReversal(Confirm)')
            return True
        if(regression_data['month3HighChange'] < -20 and (regression_data['month6HighChange'] < -20 or regression_data['yearHighChange'] < -30)
            ):
            if(('NearLowYear2' in regression_data['filter3']) and (regression_data['year2HighChange'] < -40)):
                add_in_csv(regression_data, regressionResult, ws, None, None, '##UPTREND:buyYear2Low')
                return True
            if(('NearLowYear' in regression_data['filter3']) and (regression_data['yearHighChange'] < -30)):
                add_in_csv(regression_data, regressionResult, ws, None, None, '##UPTREND:buyYearLow')
                return True
            if(('NearLowMonth6' in regression_data['filter3']) and (regression_data['month6HighChange'] < -25)):
                add_in_csv(regression_data, regressionResult, ws, None, None, '##UPTREND:buyMonth6Low')
                return True
            if(('NearLowMonth3' in regression_data['filter3']) and (regression_data['month3HighChange'] < -20)):
                add_in_csv(regression_data, regressionResult, ws, None, None, '##UPTREND:buyMonth3Low')
                return True


def buy_check_chart(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    # Check for last 5 from latest up should crossover
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
                add_in_csv(regression_data, regressionResult, ws, None, None, 'NearHighMonth3')
            elif('ReversalHighMonth3' in regression_data['filter3']):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'ReversalHighMonth3')
            elif('BreakHighMonth3' in regression_data['filter3']):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'BreakHighMonth3')
            add_in_csv(regression_data, regressionResult, ws, None, None, '##:month3High-InMinus')
            
    elif(('NearHighMonth6' in regression_data['filter3']) 
        or ('ReversalHighMonth6' in regression_data['filter3'])
        ):
        if(regression_data['month6LowChange'] > 20
            and ((-5 < regression_data['PCT_change'] < -1) and (-5 < regression_data['PCT_day_change'] < -2))
            and regression_data['close'] < regression_data['bar_low_pre1']
            and regression_data['close'] < regression_data['bar_low_pre2']
            ):
            if('NearHighMonth6' in regression_data['filter3']):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'NearHighMonth6')
            elif('ReversalHighMonth6' in regression_data['filter3']):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'ReversalHighMonth6')
            add_in_csv(regression_data, regressionResult, ws, None, None, '##:month6High-InMinus')
            
    elif(('NearHighYear' in regression_data['filter3']) 
        or ('ReversalHighYear' in regression_data['filter3'])
        ):
        if(regression_data['month6LowChange'] > 20
            and ((-5 < regression_data['PCT_change'] < -1) and (-5 < regression_data['PCT_day_change'] < -2))
            and regression_data['close'] < regression_data['bar_low_pre1']
            and regression_data['close'] < regression_data['bar_low_pre2']
            ):
            if('NearHighYear' in regression_data['filter3']):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'NearHighYear')
            elif('ReversalHighYear' in regression_data['filter3']):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'ReversalHighYear')
            add_in_csv(regression_data, regressionResult, ws, None, None, '##:YearHigh-InMinus')
        
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
                    add_in_csv(regression_data, regressionResult, ws, None, None, '##:year2High-InPlus')
                else:
                    add_in_csv(regression_data, regressionResult, ws, None, None, '##:year2High-InPlus')
                     
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
                    add_in_csv(regression_data, regressionResult, ws, None, None, '##:yearHigh-InPlus')
                else:
                    add_in_csv(regression_data, regressionResult, ws, None, None, '##:yearHigh-InPlus')


def buy_risingMA(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    
    if(regression_data['year2HighChange'] < -50
        ):
        if(regression_data['yearHighChange'] < -30
            and 2 < regression_data['PCT_day_change'] < 4
            # and regression_data['forecast_day_PCT_change'] < 1
            and regression_data['forecast_day_PCT_change'] < regression_data['forecast_day_PCT4_change']
            and regression_data['forecast_day_PCT2_change'] < 1
            and regression_data['forecast_day_PCT3_change'] < 1
            and regression_data['forecast_day_PCT4_change'] < 0
            and regression_data['forecast_day_PCT5_change'] < 0
            and regression_data['forecast_day_PCT7_change'] < 0
            and regression_data['forecast_day_PCT10_change'] < 0
            and high_tail_pct(regression_data) < 1
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##buyYear2LowBreakingUp')
        elif(regression_data['yearHighChange'] < -20
            and -1.5 < regression_data['PCT_day_change'] < -0.3
            and -2 < regression_data['PCT_change'] < 1 
            and regression_data['PCT_day_change_pre1'] < 0
            and regression_data['EMA14_2daysBack'] < regression_data['EMA14_1daysBack'] < regression_data['EMA14']
            and (((regression_data['bar_low'] - regression_data['bar_low_pre1']) / regression_data['bar_low']) * 100) > 0
            and regression_data['low'] > regression_data['low_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##buyMayYear2LowBreakingUp')
    
    if((-1.5 < regression_data['PCT_day_change'] < 0) and (-2 < regression_data['PCT_change'] < 0)
        and regression_data['year2HighChange'] < -50
        and regression_data['yearHighChange'] < -30
        and regression_data['month3LowChange'] > 10
        and regression_data['monthLowChange'] > 10
        and 0 < regression_data['SMA4'] < 10
        and 2 < regression_data['SMA9'] < 10
        ): 
        add_in_csv(regression_data, regressionResult, ws, None, None, '##buyYear2LowMovingSMA')
        return True
    
    if(regression_data['close'] > 50
        and regression_data['SMA4'] > 0
        and regression_data['SMA9'] > 5
        and regression_data['SMA25'] > 10
        and regression_data['year2HighChange'] < -5
        and (abs(regression_data['PCT_day_change']) > 1.5  
             or (-0.75 < regression_data['PCT_day_change'] < 0.75 and regression_data['PCT_day_change_pre1'] > 1.5
                 and abs(regression_data['PCT_day_change_pre1']) > 2 * abs(regression_data['PCT_day_change'])
                )
            )
        ):
        if(regression_data['SMA200'] > 0 and regression_data['SMA100'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##MA-SMA200GT0SMA100GT0')
        if(regression_data['SMA200'] > 0 and regression_data['SMA100'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##MA-SMA200GT0SMA100LT0')
        elif(regression_data['SMA200'] < 0 and regression_data['SMA100'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##MA-SMA200LT0SMA100GT0')
        elif(regression_data['SMA200'] < 0 and regression_data['SMA100'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##MA-SMA200LT0SMA100LT0')
        
        if(regression_data['PCT_change'] < -3
            and regression_data['PCT_day_change'] < -4.5):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##MAPositive_Uptrend(LT-4.5)')
        elif(regression_data['PCT_change'] < -1
            and -4.5 < regression_data['PCT_day_change'] < -2):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##MAPositive_Uptrend(LT-2)')
        elif(regression_data['PCT_change'] < 0
            and -2 < regression_data['PCT_day_change'] < -1):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##MAPositive_Uptrend(LT-1)')
        elif(-1.5 < regression_data['PCT_change'] < 1.5
            and -1 < regression_data['PCT_day_change'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##MAPositive_Uptrend(LT0)')
        elif(regression_data['PCT_change'] > 3
            and regression_data['PCT_day_change'] > 4.5):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##MAPositive_Uptrend(GT4.5)')
        elif(regression_data['PCT_change'] > 1
            and 4.5 > regression_data['PCT_day_change'] > 2):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##MAPositive_Uptrend(GT2)')
        elif(regression_data['PCT_change'] > 0
            and 2 > regression_data['PCT_day_change'] > 1):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##MAPositive_Uptrend(GT1)')
        elif(-1.5 < regression_data['PCT_change'] < 1.5
            and 1 > regression_data['PCT_day_change'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##MAPositive_Uptrend(GT0)')
    
    if(regression_data['close'] > 50
        ): 
        if(regression_data['SMA25'] > 0
            and 0 < regression_data['SMA50'] < 10
            and regression_data['SMA200'] < regression_data['SMA100'] < 0
            and -70 < regression_data['SMA200'] < -25
            # and regression_data['PCT_day_change'] < -1.5
            and regression_data['PCT_change'] < -1.5
            # and regression_data['series_trend'] != "downTrend"
            # and all_day_pct_change_negative_except_today(regression_data) != True
            and regression_data['month3HighChange'] < -5 
            ):
            if(regression_data['PCT_day_change_pre1'] > 1
                and regression_data['SMA4'] > -2
                and '[' not in regression_data['sellIndia']
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None)
                return True
            elif(regression_data['PCT_day_change_pre1'] < -1
                and -5 < regression_data['PCT_day_change'] < -1
                and all_day_pct_change_negative_except_today(regression_data) != True
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '##sellRisingMA')
                return True
            elif(regression_data['PCT_day_change_pre1'] > 1
                and regression_data['SMA50'] < 1
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '##sellRisingMA')
                return True
            else:
                #add_in_csv(regression_data, regressionResult, ws, None, None, '##RisingMA-Risky-0')
                return True
            return False
        elif(regression_data['SMA4_2daysBack'] > 0
            and regression_data['SMA9'] > 0
            and 2 < regression_data['SMA50'] < 10
            and regression_data['SMA200'] < regression_data['SMA100'] < 0
            and -70 < regression_data['SMA200'] < -10
            # and regression_data['PCT_day_change'] < -1.5
            and regression_data['PCT_change'] < -1.5
            # and regression_data['series_trend'] != "downTrend"
            # and all_day_pct_change_negative_except_today(regression_data) != True
            ):
            if(-4 < regression_data['PCT_day_change'] < -1
                and regression_data['forecast_day_PCT4_change'] < 10
                and ('[' not in regression_data['sellIndia'])
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '##buyRisingMA-1')
                return True
            elif(('P@' or 'M@') in regression_data['buyIndia']):
                add_in_csv(regression_data, regressionResult, ws, None, None, '##sellRisingMA-1')
                return True
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, '##SellRisingMA-Risky-1')
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
            add_in_csv(regression_data, regressionResult, ws, None, None, '##SellRisingMA-Risky-2')
            return True
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
                add_in_csv(regression_data, regressionResult, ws, None, None, '##sellRisingMAuptrend-0')
                return True
            elif(regression_data['month3LowChange'] < 10
                and ('P@[' or 'M@[') in regression_data['buyIndia']
                
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '##sellRisingMAuptrend-1')
                return True
            elif(high_tail_pct(regression_data) > 1.5
                and regression_data['month6HighChange'] > -80
                and ('P@[' or 'M@[') not in regression_data['buyIndia']
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '##sellRisingMAuptrend-2')
                return True
            elif(2 < regression_data['PCT_day_change'] < 4
                and 1.5 < regression_data['PCT_change'] < 4
                and regression_data['forecast_day_PCT7_change'] > 0
                and regression_data['forecast_day_PCT10_change'] > 0
                and (regression_data['month6HighChange'] > -80 and regression_data['month3HighChange'] > -80)
                and ('P@[' or 'M@[') in regression_data['buyIndia']
                # and is_algo_buy(regression_data)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '##buyRisingMAuptrend-(Risky)')
                return True
            elif(2 < regression_data['PCT_day_change'] < 4
                and 1.5 < regression_data['PCT_change'] < 4
                and regression_data['forecast_day_PCT7_change'] > 0
                and regression_data['forecast_day_PCT10_change'] > 0
                and (regression_data['month6HighChange'] < -80 or regression_data['month3HighChange'] < -80)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '##buyRisingMAuptrend-Risky')
                return True
        elif(regression_data['SMA200'] < regression_data['SMA100'] < regression_data['SMA50'] < regression_data['SMA25'] < regression_data['SMA9']
            ):
            if((((regression_data['PCT_change'] + regression_data['PCT_change_pre1']) < -4
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
                add_in_csv(regression_data, regressionResult, ws, None, None, '##buyRisingMA-down-0')
                return True
            elif((((regression_data['PCT_change'] + regression_data['PCT_change_pre1']) < -4
                and (regression_data['PCT_change'] < -3.5 or regression_data['PCT_change_pre1'] < -3.5)
                )
                )
                and regression_data['PCT_change'] < 0
                and regression_data['year2HighChange'] < -40
                and -5 < regression_data['SMA25'] < 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '##buylRisingMA-down-(Risky)')
                return True
            elif((
                -4 < regression_data['PCT_change'] < -2
                )
                and regression_data['year2HighChange'] < -30
                and -2.5 < regression_data['SMA9'] < 2
                and -5 < regression_data['SMA25'] < 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '##buyRisingMA-down-Risky')
                return True
                
        elif(regression_data['SMA200'] < regression_data['SMA100'] < regression_data['SMA50'] < regression_data['SMA25']
            and regression_data['SMA25'] > 0
            and regression_data['SMA50'] < 2
            and regression_data['SMA100'] < 0
            and regression_data['SMA200'] < 0
            and regression_data['year2HighChange'] < -40
            and regression_data['series_trend'] != "downTrend"
            and all_day_pct_change_negative_except_today(regression_data) != True
            ):
            if(-2 < regression_data['PCT_change'] < -0.5
                and -2 < regression_data['PCT_change'] < -1
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, '##:buyRisingMA-uptrend-SMA25gt0')
        
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
                if(((-3 < regression_data['PCT_change'] < 0) and (-3 < regression_data['PCT_day_change'] < 0))
                    and regression_data['SMA4'] > 0.5
                    and regression_data['SMA25'] > -10
                    and ('[') not in regression_data['sellIndia']
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, None, '##buyBottomReversal-0')
                if(((-3 < regression_data['PCT_change'] < 0) and (-3 < regression_data['PCT_day_change'] < 0))
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, None, None)
                    return True
                elif(((-3 < regression_data['PCT_change'] < -1.5) and (-3 < regression_data['PCT_day_change'] < -1.5))
                     ):
                     add_in_csv(regression_data, regressionResult, ws, None, None, '##UPTREND:buyBottomReversal-2')
                elif(regression_data['PCT_day_change_pre2'] < 0 and (regression_data['PCT_day_change'] > 1.5)):
                     add_in_csv(regression_data, regressionResult, ws, None, None, '##buyBottomReversal-1')
        return True

def buy_study_risingMA(regression_data, regressionResult, reg, ws):
    if(('EMA6-LT-May-MT-EMA14' in regression_data['filter4'])
        and 2.5 < regression_data['PCT_day_change'] < 4
        and 0 < regression_data['PCT_change'] < 4.5
        and regression_data['PCT_day_change_pre1'] > 0
        and (regression_data['PCT_day_change'] > 3 or regression_data['PCT_change'] > 3)
        and high_tail_pct(regression_data) < 1
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '##mayBuy-EMA6-LT-May-MT-EMA14')
    elif(('EMA6-MT-May-LT-EMA14' in regression_data['filter4'])
        and -4 < regression_data['PCT_day_change'] < -2.5
        and -4.5 < regression_data['PCT_change'] < 0
        and regression_data['PCT_day_change_pre1'] < 0
        and (regression_data['PCT_day_change'] < -3 or regression_data['PCT_change'] < -3)
        and low_tail_pct(regression_data) < 1
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '##maySell-EMA6-MT-May-LT-EMA14')
        
    if(('(Confirmed)EMA6>EMA14' in regression_data['filter4'])
        and 3 < regression_data['PCT_day_change'] 
        and 0 < regression_data['PCT_change']
        and regression_data['PCT_day_change_pre1'] < -1
        and (regression_data['PCT_day_change'] > 3 or regression_data['PCT_change'] > 3)
        ):
        if(regression_data['month3HighChange'] < 10):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##sellEMA6>EMA14')
        elif(regression_data['PCT_day_change'] > 3.5 or regression_data['PCT_change'] > 3.5):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##sellEMA6>EMA14-Risky')
    
    if('$$(Study)$$:RisingMA' in regression_data['filter4']
        ):
        if(-2.5 < regression_data['PCT_day_change'] < 0 and -2.5 < regression_data['PCT_change'] < 0
            and (regression_data['SMA50'] < 0 and regression_data['SMA25'] > 10 and regression_data['SMA4'] > 0)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, "##sellSMA25GT10")
        if(-4 < regression_data['PCT_day_change'] < -0.5
           and -4 < regression_data['PCT_change']
           and 5 > low_tail_pct(regression_data) > 2.5
           and high_tail_pct(regression_data) < 0.6
           and (low_tail_pct(regression_data) - high_tail_pct(regression_data)) > 1
           ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None)
            return True
        elif(-4 < regression_data['PCT_day_change'] < -0.5
           and -4 < regression_data['PCT_change']
           and 5 > low_tail_pct(regression_data) > 2.5
           and high_tail_pct(regression_data) < 2
           and (low_tail_pct(regression_data) - high_tail_pct(regression_data)) > 0.8
           ):
            add_in_csv(regression_data, regressionResult, ws, None, None, "##RisingMA-MayBuyCheckChart")
            return True
        elif(0.5 < regression_data['PCT_day_change'] < 4
           and regression_data['PCT_change'] < 4
           and low_tail_pct(regression_data) < 0.6
           and 5 > high_tail_pct(regression_data) > 2.5
           and (high_tail_pct(regression_data) - low_tail_pct(regression_data)) > 0.8
           ):
            add_in_csv(regression_data, regressionResult, ws, None, None, "##RisingMA-MaySellCheckChart")
            return True
        elif(0.5 < regression_data['PCT_day_change'] < 4
           and regression_data['PCT_change'] < 4
           and low_tail_pct(regression_data) < 2
           and 5 > high_tail_pct(regression_data) > 2.5
           and (high_tail_pct(regression_data) - low_tail_pct(regression_data)) > 0.8
           ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None)
            return True
        elif(0.5 < regression_data['PCT_day_change'] < 4
           and regression_data['PCT_day_change_pre1'] < 0
           and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change'])
           and ((regression_data['forecast_day_PCT_change'] < 0)
                # or (regression_data['open'] > regression_data['close_pre'])
                )
           and high_tail_pct(regression_data) < 1
           ):
            add_in_csv(regression_data, regressionResult, ws, None, None, "##RisingMA-1DayUp")
            return True
        elif(0.5 < regression_data['PCT_day_change'] < 4
           and 0.5 < regression_data['PCT_day_change_pre1'] < 4
           and regression_data['PCT_day_change_pre2'] < 0
           and regression_data['PCT_day_change_pre3'] < 0
           and abs(regression_data['PCT_day_change_pre2']) > abs(regression_data['PCT_day_change_pre1'])
           and regression_data['forecast_day_PCT_change'] > 0
           and high_tail_pct(regression_data) < 1
           ):
            add_in_csv(regression_data, regressionResult, ws, None, None, "##RisingMA-2DayUp")
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
            add_in_csv(regression_data, regressionResult, ws, None, None, "##RisingMA-1DayUp")
            return True
        
    if(regression_data['SMA9'] < 0 
        and regression_data['SMA4'] < 0
        and regression_data['forecast_day_PCT_change'] < -0.5
        and regression_data['forecast_day_PCT2_change'] < -0.5
        and regression_data['forecast_day_PCT5_change'] < -0.5
        and regression_data['forecast_day_PCT5_change'] > -5
        and regression_data['forecast_day_PCT7_change'] > -10
        and abs(regression_data['PCT_day_change_pre1']) > 2 * (regression_data['PCT_day_change'])
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
        add_in_csv(regression_data, regressionResult, ws, None, None, "##sellSMADownTrend") 
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
        add_in_csv(regression_data, regressionResult, ws, None, None, "##sellSMADownTrend-2DayUp-weekHighTouch")
        return True

def buy_test(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    regression_data['filter'] = ""
    flag = False
        
    return flag
