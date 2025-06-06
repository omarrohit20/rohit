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

connection = MongoClient('localhost',27017)
db = connection.Nsedata


def sell_high_volatility_boundary(regression_data, regressionResult):
    flag = False
    ws = None
    
    if(-1.5 < regression_data['PCT_day_change'] < -0.5
        and -3 < regression_data['PCT_day_change']
        and -5 < regression_data['PCT_day_change_pre1'] < 0
        and -2 < regression_data['PCT_day_change_pre2'] < 0
        and regression_data['PCT_day_change'] > regression_data['PCT_day_change_pre1']
        and regression_data['PCT_day_change_pre4'] > 0
        and -20 < regression_data['forecast_day_PCT10_change'] < -5
        and regression_data['year2LowChange'] > 3
        and low_tail_pct(regression_data) < 2
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'X_:DowntrendDojiMinus')
        flag = True
        
    if(regression_data['monthLowChange'] < -2
        and regression_data['week2HighChange'] < -7
        and regression_data['year2LowChange'] > 3
        and -25 < regression_data['forecast_day_PCT10_change'] < -5
        ):
        if (-1.5 < regression_data['PCT_day_change'] < -0.5
            and -3 < regression_data['PCT_day_change']
            and -5 < regression_data['PCT_day_change_pre1'] < 0
            and -2 < regression_data['PCT_day_change_pre2'] < 0
            and regression_data['PCT_day_change'] > regression_data['PCT_day_change_pre1']
            and regression_data['PCT_day_change_pre4'] > 0
            and -20 < regression_data['forecast_day_PCT10_change'] < -5
            and low_tail_pct(regression_data) < 2
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'X_:MonthLowDowntrendDojiMinus')
            flag = True
        elif (-4 < regression_data['PCT_day_change'] < -1.5
            and -7 < regression_data['PCT_day_change']
            and -5 < regression_data['PCT_day_change_pre1'] < 0
            and -5 < regression_data['PCT_day_change_pre2'] < 0
            and -5 < regression_data['PCT_day_change_pre3'] < 0
            and regression_data['PCT_day_change_pre4'] > 0
            and -20 < regression_data['forecast_day_PCT10_change'] < -5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'X_:MonthLowDowntrend4Days')
            flag = True
        elif (-4 < regression_data['PCT_day_change'] < -1.5
            and -7 < regression_data['PCT_day_change']
            and regression_data['PCT_day_change_pre1'] < 0
            and -5 < regression_data['PCT_day_change_pre2']
            and -5 < regression_data['PCT_day_change_pre3']
            and -20 < regression_data['forecast_day_PCT10_change'] < -10
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'X_:MonthLowDowntrend-continueDowntrendNifty/GlobalDown')
            flag = True
    if(regression_data['monthLowChange'] < -2
        and regression_data['week2HighChange'] < -5
        and -8 < regression_data['forecast_day_PCT10_change'] < -10
        ):
        if (-4 < regression_data['PCT_day_change'] < -1.5
            and -7 < regression_data['PCT_day_change']
            and regression_data['PCT_day_change_pre1'] < 0
            and regression_data['PCT_day_change_pre2'] < 0
            and regression_data['PCT_day_change_pre3'] > 0
            and (regression_data['PCT_day_change_pre1'] > -1.5 
                or regression_data['PCT_day_change_pre2'] > -1.5
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'X_:MonthLowDowntrend3Days')
            flag = True  
    if(regression_data['monthLowChange'] < -2
        and regression_data['week2HighChange'] < -5
        and -8 < regression_data['forecast_day_PCT10_change'] < -10
        ):
        if (-4 < regression_data['PCT_day_change'] < -1.5
            and -7 < regression_data['PCT_day_change']
            and regression_data['PCT_day_change_pre1'] < 0
            and regression_data['PCT_day_change_pre2'] > 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'X_:MonthLowDowntrend2Days')
            flag = True
            
    if(-2.6 < regression_data['PCT_day_change'] < -1.9
        and -4 < regression_data['PCT_change'] < -1.9
        and regression_data['monthLowChange'] > 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'X_SGXNIFTYDOWNLT(-.5)PC-GLOBALFUTDOWN-AfterUpTrend:PCTDayChangeBT-2.5and2.0')
        flag = True
    if(-4 < regression_data['PCT_day_change'] < -3
        and -4.5 < regression_data['PCT_change'] < -2.5
        and regression_data['monthLowChange'] > 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'X_LASTDAYNIFYUPGT2:PCTDayChangeBT-4and-3')
        flag = True
    if(regression_data['monthLowChange'] < -2
        and regression_data['week2HighChange'] < -7
        and regression_data['close'] < 70
        ):
        if (regression_data['PCT_day_change'] < -2
            and regression_data['PCT_change'] < -2
            and regression_data['PCT_day_change_pre1'] < -2
            and regression_data['PCT_day_change_pre2'] < -2
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'X_:MonthLowDowntrend3Days-risky-closelt70')
            flag = True
        elif (regression_data['PCT_day_change'] < -4
            and regression_data['PCT_change'] < -4
            and regression_data['PCT_day_change_pre1'] < -4
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'X_:MonthLowDowntrend2Days-risky-closelt70')
            flag = True
    elif(regression_data['monthLowChange'] < -2
        and regression_data['week2HighChange'] < -7
        and regression_data['close'] < 150
        ):
        if (regression_data['PCT_day_change'] < 0
            and regression_data['PCT_change'] < 0
            and regression_data['PCT_day_change_pre1'] < 0
            and regression_data['PCT_day_change_pre2'] < 0
            and regression_data['PCT_day_change_pre3'] < 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'X_:MonthLowDowntrend4Days-risky-closelt150')
            flag = True
    if(regression_data['PCT_day_change'] > 2
        and regression_data['PCT_change'] > 0
        and regression_data['monthHighChange'] > -1
        and regression_data['month3LowChange'] > 10
        ):
        if(regression_data['PCT_day_change_pre1'] < 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'PCTDayChangePre1LT0')
        elif(regression_data['PCT_day_change_pre2'] < 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'PCTDayChangePre2LT0')
            
        if(regression_data['PCT_day_change'] > 2 and regression_data['PCT_day_change_pre1'] > 2 and regression_data['PCT_day_change_pre2'] > 2
            and regression_data['monthHighChange'] > 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'PCTDayChangeLast3DaysGT2')
        elif(regression_data['PCT_day_change'] > 2 and regression_data['PCT_day_change_pre1'] > 2
            and regression_data['monthHighChange'] > 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'PCTDayChangeLast2DaysGT2')
        
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Z_:NearOrUpMonthHigh')
        flag = True
    if(regression_data['PCT_day_change'] > 2
        and regression_data['PCT_change'] > 0
        and regression_data['month3HighChange'] > -1
        and regression_data['month3LowChange'] > 15
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Z_:NearOrUpMonth3High')
        flag = True
    if(regression_data['PCT_day_change'] > 2
        and regression_data['PCT_change'] > 0
        and regression_data['year2HighChange'] > -1
        and regression_data['month3LowChange'] > 15
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Z_:NearOrUpYear2High')
        flag = True
    if(0 < regression_data['PCT_day_change'] < 1
        and regression_data['PCT_day_change_pre1'] < -1 
        and regression_data['PCT_day_change_pre2'] < 0
        and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change'])
        and abs(regression_data['PCT_day_change_pre1']) < abs(regression_data['PCT_day_change_pre2'])
        and regression_data['bar_low'] < regression_data['bar_low_pre1']
        and regression_data['bar_low_pre2'] < regression_data['bar_low_pre1'] 
        and regression_data['weekLowChange'] > 1
        ):
        #add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Y_:AlternateUpDownSell-Risky-ConNextDayIfWeekLowChangeGT0AfterToday')
        flag = True
    if(0 < regression_data['PCT_day_change'] < 1
        and regression_data['PCT_day_change_pre1'] < -1.5 
        and regression_data['PCT_day_change_pre2'] < 0
        and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change'])
        and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change_pre2'])
        and regression_data['bar_low'] < regression_data['bar_low_pre1'] < regression_data['bar_low_pre2']
        and regression_data['weekLowChange'] > 1
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Y_:AlternateUpDownSell-ConNextDayIfWeekLowChangeGT0AfterToday')
        flag = True
    if(-4 < regression_data['PCT_day_change'] < 2
        and -6 < regression_data['PCT_change'] < 2
        and regression_data['month3LowChange'] > 5
        and -3 < regression_data['monthLowChange'] < 2
        and regression_data['monthHighChange'] < -3
        and regression_data['forecast_day_PCT_change'] < 0
#         and regression_data['forecast_day_PCT2_change'] > 1
        #and regression_data['forecast_day_PCT3_change'] > 1
        #and regression_data['forecast_day_PCT4_change'] > 1
        and (regression_data['PCT_day_change'] > 0
             or regression_data['PCT_day_change_pre1'] > 0
             or regression_data['PCT_day_change_pre2'] > 0
             )
        and (regression_data['PCT_day_change_pre1'] < -1.5
             or regression_data['PCT_day_change_pre2'] < -1.5
             or regression_data['PCT_day_change_pre3'] < -1.5
             )
        and (regression_data['PCT_day_change_pre1'] > 0
             or regression_data['PCT_day_change_pre2'] > 0
             or regression_data['PCT_day_change_pre3'] > 0
             or regression_data['PCT_day_change_pre4'] > 0
             )
        ):
        if (((regression_data['PCT_day_change'] < 0 and regression_data['PCT_day_change_pre1'] < 0
                and (regression_data['PCT_day_change_pre2'] < 0 or regression_data['PCT_day_change_pre3'] < 0)
                )
            or (regression_data['PCT_day_change_pre1'] < 0 and regression_data['PCT_day_change_pre2'] < 0
                and (regression_data['PCT_day_change'] < 0 or regression_data['PCT_day_change_pre3'] < 0)
                )
            or (regression_data['PCT_day_change'] < 0 and regression_data['PCT_day_change_pre2'] < 0 
                and (regression_data['PCT_day_change_pre1'] < 0 or regression_data['PCT_day_change_pre3'] < 0)
                ))
            and regression_data['forecast_day_PCT_change'] < -1
            and (0 < regression_data['PCT_day_change'] < 2
                or regression_data['PCT_day_change'] < -1
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Y_:MonthHighReversalContinue')
            flag = True
        elif(regression_data['PCT_day_change'] > 0
            and regression_data['PCT_day_change_pre1'] < 0 
            and regression_data['PCT_day_change_pre2'] > 0 
            and regression_data['PCT_day_change_pre3'] < 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Y_:MonthHighReversalContinue-AlternateUpDown')
            flag = True
        
    if(-4 < regression_data['PCT_day_change'] < -1.9
        and -6 < regression_data['PCT_change'] < -1.9
        and regression_data['monthHighChange'] > -5
        and regression_data['monthLowChange'] > 5
        and (regression_data['monthHighChange'] > 0
            or abs(regression_data['monthLowChange']) > 3*abs(regression_data['monthHighChange'])
            )
        and low_tail_pct(regression_data) < 1.5
        and regression_data['PCT_day_change_pre1'] > 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Y_:MonthHighReversal-followNiftyDayTrend')
        flag = True
    if((regression_data['month3HighChange'] > -15
            and regression_data['month3LowChange'] > 5
            and regression_data['month6LowChange'] < -7.5
            #and regression_data['monthLowChange'] > 5
            and (regression_data['monthHighChange'] > -5
                or abs(regression_data['monthLowChange']) > 2*abs(regression_data['monthHighChange'])
                )
            and low_tail_pct(regression_data) < 1.5
            #and regression_data['PCT_day_change_pre1'] > 0
            )
        or ('ReversalHighMonth3' in regression_data['filter3']
            and regression_data['monthHighChange'] > -7
            and low_tail_pct(regression_data) < 1.5
            )
        ):
        if(-6 < regression_data['PCT_day_change'] < -1.5
            and -7 < regression_data['PCT_change'] < -1.5
            and regression_data['PCT_day_change_pre1'] > 0
            and regression_data['low'] < regression_data['low_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Y_:Month3HighReversal-followNiftyDayTrend')
            flag = True
        elif(-2 < regression_data['PCT_day_change'] < -1
            and -3 < regression_data['PCT_change'] < -0.5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Y_:Month3HighReversal-followNiftyDayTrend')
            flag = True
        elif(-1 < regression_data['PCT_day_change'] < 1
            and -2 < regression_data['PCT_change'] < 2
            and regression_data['PCT_day_change_pre1'] < 0
            and regression_data['PCT_day_change_pre2'] < 0
            and (regression_data['PCT_day_change_pre1'] < -1 or regression_data['PCT_day_change_pre2'] < -1)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Y_:Month3HighReversal-followNiftyDayTrend')
            flag = True
    if((regression_data['yearHighChange'] > -7
            and (regression_data['month3HighChange'] > -5
                or abs(regression_data['month3LowChange']) > 2*abs(regression_data['month3HighChange'])
                )
            and low_tail_pct(regression_data) < 1.5
            )
        or (('ReversalHighYear' in regression_data['filter3'] or 'ReversalHighYear2' in regression_data['filter3'])
            and regression_data['monthHighChange'] > -7
            and low_tail_pct(regression_data) < 1.5
            )
        ):
        if(-6 < regression_data['PCT_day_change'] < -1.5
            and -7 < regression_data['PCT_change'] < -1.5
            and regression_data['PCT_day_change_pre1'] > 0
            and regression_data['low'] < regression_data['low_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Y_:YearHighReversal-followNiftyDayTrend(redbarstart-high-month-highest)')
            flag = True
        elif(-2 < regression_data['PCT_day_change'] < -1
            and -3 < regression_data['PCT_change'] < -0.5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Y_:YearHighReversal-followNiftyDayTrend(redbarstart-high-month-highest)')
            flag = True
        elif(-1 < regression_data['PCT_day_change'] < 1
            and -2 < regression_data['PCT_change'] < 2
            and regression_data['PCT_day_change_pre1'] < 0
            and regression_data['PCT_day_change_pre2'] < 0
            and (regression_data['PCT_day_change_pre1'] < -1 or regression_data['PCT_day_change_pre2'] < -1)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'Y_:YearHighReversal-followNiftyDayTrend(redbarstart-high-month-highest)')
            flag = True
            
    return flag

def sell_high_volatility_monthLowNotReached(regression_data, regressionResult):
    flag = False
    ws = None
    
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
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'UPTRENDMARKET:buyStockHeavyDowntrend')
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
            #add_in_csv(regression_data, regressionResult, ws, None, None, None, 'checkForDownTrendContinueLastDayUp')
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None)
        elif(regression_data['PCT_day_change'] < -1
            and regression_data['PCT_day_change_pre1'] < -1
            and regression_data['PCT_day_change_pre2'] < -1
            and regression_data['week2LowChange'] > 3
            and (regression_data['PCT_day_change_pre1'] > 0 or regression_data['PCT_day_change_pre2'] > 0 or regression_data['PCT_day_change_pre3'] > 0)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'checkForDownTrendContinueWeek2LowNotReached')
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
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'DOWNTRENDMARKET:checkForDowntrendContinueMonthLow(NotMonth3LowMonth6Low)')
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'HEAVYDOWNTRENDMARKET:RISKY-Last4DayDown:checkForDowntrendContinueMonthLow(NotMonth3LowMonth6Low)')
        elif(regression_data['PCT_day_change'] < -1
            and regression_data['PCT_day_change_pre1'] < -0.75
            and regression_data['PCT_day_change_pre2'] < -0.75
            and (regression_data['PCT_day_change_pre1'] < -1 or regression_data['PCT_day_change_pre2'] < -1)
            and regression_data['monthLowChange'] < 2
            and regression_data['monthHighChange'] < -10
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'checkForDowntrendReversalMonthLow(5to10-minute-baseline-if-downtrend)')
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
            #add_in_csv(regression_data, regressionResult, ws, None, None, None, 'checkForDownTrendContinueLastDayUp')
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None)
        elif(regression_data['PCT_day_change'] < -1
            and regression_data['PCT_day_change_pre1'] < -1
            and regression_data['PCT_day_change_pre2'] < -1
            and regression_data['yearHighChange'] < -10
            and regression_data['week2LowChange'] > 3
            and (regression_data['PCT_day_change_pre1'] > 0 or regression_data['PCT_day_change_pre2'] > 0 or regression_data['PCT_day_change_pre3'] > 0)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'checkForDownTrendContinueWeek2LowNotReached')
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
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'DOWNTRENDMARKET:checkForDowntrendContinueMonthLow(NotMonth3LowMonth6Low)')
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'HEAVYDOWNTRENDMARKET:RISKY-Last4DayDown:checkForDowntrendContinueMonthLow(NotMonth3LowMonth6Low)')
        elif(regression_data['PCT_day_change'] < -1
            and regression_data['PCT_day_change_pre1'] < -0.75
            and regression_data['PCT_day_change_pre2'] < -0.75
            and (regression_data['PCT_day_change_pre1'] < -1 or regression_data['PCT_day_change_pre2'] < -1)
            and regression_data['monthLowChange'] < 2
            and regression_data['monthHighChange'] < -10
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'checkForDowntrendReversalMonthLow(5to10-minute-baseline-if-downtrend)')
        
#         if(regression_data['PCT_day_change'] < -5
#             and regression_data['PCT_change'] < -3
#             and regression_data['PCT_day_change_pre1'] < -1.5
#             and regression_data['PCT_day_change_pre2'] < -1.5
#             #and (regression_data['PCT_day_change_pre1'] < -2 or regression_data['PCT_day_change_pre2'] < -2)
#             ):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'TestmayBuyShortDownTrend') 
        flag = True
    
    if(('downTrend' in regression_data['series_trend'] or 'DownTrend' in regression_data['series_trend'] or 'trendDown' in regression_data['series_trend'])
        and regression_data['monthLowChange'] > 0
        and -6 < regression_data['PCT_day_change'] < -1
        and -6 < regression_data['PCT_change'] < -1
        and (regression_data['PCT_day_change'] < -1.5
            or regression_data['PCT_change'] < -1.5)
        and ((regression_data['bar_low'] < regression_data['weekBarLow'])
            or regression_data['weekLowChange'] < -0.5
            )
        and (regression_data['PCT_day_change_pre1'] > -0.5
             or regression_data['PCT_day_change_pre2'] > -0.5
             or regression_data['PCT_day_change_pre3'] > -0.5
             or regression_data['PCT_day_change_pre4'] > -0.5
            )
        and ('IT' not in regression_data['industry']
             and 'PHARMA' not in regression_data['industry']
             and 'HEALTH' not in regression_data['industry']
             )
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'GLOBALFUTDOWN-GLOBALMARKETDOWN-LASTDAYDOWN:mayContinueDownTrend-monthLowNotReached')
        
        if(regression_data['PCT_day_change'] < -3.5
            and (regression_data['PCT_day_change_pre1'] > 1 
                 or (low_tail_pct_pre1(regression_data) > 2 and regression_data['PCT_day_change_pre1'] > -1)
                 or (regression_data['PCT_day_change_pre1'] > 0 and (low_tail_pct_pre1(regression_data) + regression_data['PCT_day_change_pre1']) > 1 )
                )
            and (regression_data['monthLowChange'] > 3 
                 or (regression_data['monthLowChange'] > 1 and regression_data['week2LowChange'] > 1)
                )
            and regression_data['week2LowChange'] > -2
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None,'mayReversalDownTrend-monthLowNotReached')
        elif(-1.7 < regression_data['PCT_day_change'] < 0
            and regression_data['PCT_day_change_pre1'] > 0 
            and high_tail_pct(regression_data) > 1.5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None,'HEAVYDOWNTREND:mayReversalDownTrend-monthLowNotReached')
            
        elif(-3 < regression_data['PCT_day_change'] < -2 
            and (regression_data['PCT_day_change_pre1'] > 0 or regression_data['PCT_day_change_pre2'] > 0 or regression_data['PCT_day_change_pre3'] > 0)
            and (abs(regression_data['monthLowChange']) < abs(regression_data['monthHighChange']) or regression_data['week2LowChange'] < -3)
            and regression_data['monthHighChange'] < -5
            and (regression_data['monthLowChange'] > 2 
                 or regression_data['month3LowChange'] > 2
                 or regression_data['week2LowChange'] > 0
                 )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None,'mayContinueDownTrend-monthLowNotReached')
        elif(-2 > regression_data['PCT_day_change'] > -3.5
            and ((regression_data['PCT_day_change_pre1'] < 0 and regression_data['PCT_day_change_pre2'] < 0)
                 or (regression_data['PCT_day_change_pre2'] < 0 and regression_data['PCT_day_change_pre3'] < 0)
                 or (regression_data['PCT_day_change_pre3'] < 0 and regression_data['PCT_day_change_pre1'] < 0)
                 ) 
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None,'HEAVYDOWNTREND:mayContinueDownTrend-monthLowNotReached')
        flag = True
        
    return flag

def sell_high_volatility_pre1pre2doji(regression_data, regressionResult):
    flag = False
    ws = None
    
    if(regression_data['week2LowChange'] < 0
        and regression_data['week2HighChange'] < -5
        and regression_data['monthLowChange'] < 0
        #and regression_data['month3LowChange'] < 0
        and -8 < regression_data['PCT_day_change'] < -3
        and -8 < regression_data['PCT_change'] < -1
        and -1 < regression_data['PCT_day_change_pre1'] < 0
        and (regression_data['forecast_day_PCT5_change'] < -5 or  regression_data['forecast_day_PCT10_change'] < -5)
        ):
        if(regression_data['bar_low'] < regression_data['bar_low_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'GLOBALFUTDOWN-GLOBALMARKETDOWN:mayContinueShortDownTrend-PCTDayChangePre1LT0-todayLT(-3)')
            flag = True
    elif(regression_data['week2LowChange'] < 0
        and regression_data['week2HighChange'] < -5
        and -8 < regression_data['PCT_day_change'] < -3
        and 0 < regression_data['PCT_day_change_pre1'] < 1
        and regression_data['PCT_day_change_pre2'] < 0 
        and (regression_data['PCT_day_change_pre3'] < 0 or regression_data['PCT_day_change_pre4'] < 0)
        and (regression_data['forecast_day_PCT5_change'] < -5 or  regression_data['forecast_day_PCT10_change'] < -5)
        ):
        if(regression_data['bar_low'] < regression_data['bar_low_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'GLOBALFUTDOWN-GLOBALMARKETDOWN:mayContinueShortDownTrend-PCTDayChangePre1GT0-todayLT(-4)')
            flag = True
    elif(regression_data['week2LowChange'] < 0
        and regression_data['PCT_day_change_pre1'] > 0
        and (-1 < regression_data['PCT_day_change'] < 0
            #or (-1.5 < regression_data['PCT_day_change'] < 0 and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change']))
            )
        ):
        if(regression_data['year2LowChange'] < 0
            and regression_data['weekLowChange'] < 2
            and (regression_data['PCT_day_change_pre1'] > 1 or regression_data['bar_low'] < regression_data['bar_low_pre1'])
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'GLOBALFUTDOWN-GLOBALMARKETDOWN:mayContinueShortDownTrend-PCTDayChangePre1GT0-year2Low')
            flag = True
        elif(regression_data['month3LowChange'] < 0
            and regression_data['weekLowChange'] < 2
            and ((regression_data['PCT_day_change_pre1'] > 1 and regression_data['PCT_day_change_pre3'] < 0.75 )
                 or (regression_data['bar_low'] < regression_data['bar_low_pre1']
                     and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change'])
                     and regression_data['PCT_day_change_pre2'] > 1
                    )
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'GLOBALFUTDOWN-GLOBALMARKETDOWN:mayContinueShortDownTrend-PCTDayChangePre1GT0-month3Low')
            flag = True
#         elif(regression_data['month3LowChange'] < 0
#             and (regression_data['PCT_day_change_pre1'] < 1 and regression_data['bar_low'] > regression_data['bar_low_pre1'])
#             ):
#             add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'GLOBALFUTDOWN-GLOBALMARKETDOWN:mayReversalShortDownTrend-PCTDayChangePre1GT0-month3Low')
#             flag = True
    elif(regression_data['month3LowChange'] < 0
        and regression_data['weekLowChange'] < 2
        and -0.5 < regression_data['PCT_day_change_pre1'] < 0 and regression_data['bar_low'] > regression_data['bar_low_pre1']
        and 0 < regression_data['PCT_day_change'] < 0.5
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'GLOBALFUTUP-GLOBALMARKETUP:mayReversalShortDownTrend-PCTDayChangePre1LT0-month3Low')
        flag = True 
    elif('shortDownTrend' in regression_data['series_trend']
        and (regression_data['forecast_day_PCT5_change'] < -2 or regression_data['forecast_day_PCT7_change'] < -2
            or (regression_data['forecast_day_PCT5_change'] < 1 and regression_data['forecast_day_PCT7_change'] < 1
                and regression_data['PCT_day_change'] < 0)
            )
        ):
        if(0 < regression_data['PCT_day_change_pre1'] < 2
            and -2 < regression_data['PCT_day_change'] < 0
            ):
            if(regression_data['forecast_day_PCT_change'] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'GLOBALFUTDOWN-GLOBALMARKETDOWN:mayContinueShortDownTrend-PCTDayChangePre1GT0')
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'GLOBALFUTDOWN-GLOBALMARKETDOWN:mayUPTREND(Buy)DOWNTREND(Sell)ShortDownTrend-PCTDayChangePre1GT0')
            flag = True
        elif(0 < regression_data['PCT_day_change_pre2'] < 2
            and -2 < regression_data['PCT_day_change_pre1'] < 0
            and -2 < regression_data['PCT_day_change'] < 1
            and (regression_data['PCT_day_change'] > 0 or ((regression_data['forecast_day_PCT5_change'] > -2 or regression_data['forecast_day_PCT5_change'] > -2)
                                                           and (regression_data['bar_low'] > regression_data['bar_low_pre4'] or regression_data['bar_low'] > regression_data['bar_low_pre5'])
                                                        )
                )
            ):
            if(regression_data['PCT_day_change'] > 0
                and regression_data['forecast_day_PCT_change'] < 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'HEAVY:GLOBALFUTDOWN-GLOBALMARKETDOWN:mayContinueShortDownTrend-PCTDayChangePre2GT0')
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'HEAVY:GLOBALFUTDOWN-GLOBALMARKETDOWN:mayUPTREND(Buy)DOWNTREND(Sell)ShortDownTrend-PCTDayChangePre2GT0')
            flag = True
    elif('shortDownTrend' in regression_data['series_trend']
        ):
        if(0 < regression_data['PCT_day_change_pre2'] < 2
            and -2 < regression_data['PCT_day_change_pre1'] < 0
            and (regression_data['PCT_day_change'] > 1.5
                or (regression_data['forecast_day_PCT5_change'] > 1 and regression_data['forecast_day_PCT7_change'] > 1)
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'HEAVY:GLOBALFUTDOWN-GLOBALMARKETDOWN:mayReversalShortDownTrend-PCTDayChangePre2GT0')
            flag = True
    
    return flag

def sell_high_volatility_shortDownTrend(regression_data, regressionResult):
    flag = False
    ws = None
    
    if('shortDownTrend' in regression_data['series_trend']):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'shortDownTrend')    
        if(-1.3 < regression_data['PCT_day_change'] < 0 and -2 < regression_data['PCT_change'] < 0
            and -1.3 > regression_data['PCT_day_change_pre1'] < regression_data['PCT_day_change']
            and -1.3 > regression_data['PCT_day_change_pre2'] < regression_data['PCT_day_change']
            and regression_data['forecast_day_PCT_change'] < 0
            and (-2 < regression_data['month3LowChange'] < 1
                or (abs(bar_low_change_month3(regression_data)) < 1 and low_tail_pct(regression_data) > 1)
                )
            and (high_tail_pct(regression_data) < 0.5 or high_tail_pct(regression_data) < low_tail_pct(regression_data)
                or abs(high_tail_pct(regression_data) - low_tail_pct(regression_data)) <= 0.2   
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None,'shortDownTrendBuyReversal-Month3Low-Doji-Last2DayLTToday')
        elif(-1.3 < regression_data['PCT_day_change'] < 0 and -2 < regression_data['PCT_change'] < 0
            and -1.3 > regression_data['PCT_day_change_pre1'] < regression_data['PCT_day_change']
            and -1.3 > regression_data['PCT_day_change_pre2'] < regression_data['PCT_day_change']
            and regression_data['forecast_day_PCT_change'] < 0
            and ((-0.5 < regression_data['monthLowChange'] < 1.5 and regression_data['month3LowChange'] > 20)
                or (abs(bar_low_change_month(regression_data)) < 1 and low_tail_pct(regression_data) > 1)
                )
            and (high_tail_pct(regression_data) < 0.5 or high_tail_pct(regression_data) < low_tail_pct(regression_data)
                or abs(high_tail_pct(regression_data) - low_tail_pct(regression_data)) <= 0.2 
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None,'shortDownTrendBuyReversal-MonthLow-Doji-Last2DayLTToday')
        elif(-1.3 < regression_data['PCT_day_change'] < 0 and -2 < regression_data['PCT_change'] < 0
            and -2 > regression_data['PCT_day_change_pre1'] < regression_data['PCT_day_change']
            and -1.5 > regression_data['PCT_day_change_pre2'] < regression_data['PCT_day_change']
            and regression_data['forecast_day_PCT_change'] < 0
            and regression_data['month3LowChange'] > 5
            and regression_data['monthHighChange'] < -5
            and abs(regression_data['monthLowChange']) > 1.5
            and abs(regression_data['monthLowChange']) < abs(regression_data['monthHighChange'])
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None,'shortDownTrendSellContinue-Doji-Last2DayLTToday')
        elif(-1.3 < regression_data['PCT_day_change'] < 0 and -2 < regression_data['PCT_change'] < 0
            and -2 > regression_data['PCT_day_change_pre1'] < regression_data['PCT_day_change']
            and -2 > regression_data['PCT_day_change_pre2'] < regression_data['PCT_day_change']
            and regression_data['PCT_day_change_pre3'] > -1
            and regression_data['forecast_day_PCT_change'] < 0
            #and regression_data['month3LowChange'] > 5
            and regression_data['monthHighChange'] < -5
            and abs(regression_data['monthLowChange']) > 1.5
            and abs(regression_data['monthLowChange']) < abs(regression_data['monthHighChange'])
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None,'HEAVY:GLOBALFUTDOWN-GLOBALMARKETDOWN:shortDownTrendSellContinue-Doji-Last2DayLTToday')
        
        if(regression_data['PCT_day_change'] < 0 and regression_data['PCT_change'] < 0
            and regression_data['forecast_day_PCT_change'] < 0
            and ((-1.5 < regression_data['monthLowChange'] < 1.5 and regression_data['monthLowChange'] == regression_data['month2LowChange'])
                and abs(bar_low_change_month(regression_data)) < 1
                )
            and low_tail_pct(regression_data) > 1 and high_tail_pct(regression_data) < low_tail_pct(regression_data)
            and (high_tail_pct(regression_data) < 1 or (low_tail_pct(regression_data) - high_tail_pct(regression_data)) > 0.5)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None,'shortDownTrendBuyReversal-MonthLow')
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
    
    if(('shortDownTrend' in regression_data['series_trend'] or 'RISKY-DOWNTREND-BUY' in regression_data['filter1']) 
        and regression_data['PCT_day_change_pre1'] < 0
        and regression_data['PCT_day_change'] < 0
        and regression_data['PCT_day_change_pre2'] < 0
        and regression_data['PCT_day_change_pre3'] > 2
        and low_tail_pct(regression_data) > 0.9
        ):   
        if('shortDownTrend' in regression_data['series_trend']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'shortDownTrend-1')
            if((low_tail_pct(regression_data) > 2 or low_tail_pct_pre1(regression_data) > 2)
                and low_tail_pct(regression_data) > abs(regression_data['PCT_day_change'])
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None,'mayReversalBuy-pre3GT2-shortDownTrend')
        if('RISKY-DOWNTREND-BUY' in regression_data['filter1']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'RISKY-DOWNTREND-BUY-1')
            if((low_tail_pct(regression_data) > 2 or low_tail_pct_pre1(regression_data) > 2)
                and low_tail_pct(regression_data) > abs(regression_data['PCT_day_change'])
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None,'mayReversalBuy-pre3GT2-RISKY-DOWNTREND-BUY')
        flag = True
    elif(('shortDownTrend' in regression_data['series_trend'] or 'RISKY-DOWNTREND-BUY' in regression_data['filter1']) 
        and ((regression_data['PCT_day_change_pre1'] < -1.5 and -1.3 < regression_data['PCT_day_change'] < 0)
             or (regression_data['PCT_day_change_pre1'] < -3 and  -1.5 < regression_data['PCT_day_change'] < 0)
            )
        and regression_data['PCT_day_change_pre1'] < regression_data['PCT_day_change'] - 0.5
        and regression_data['PCT_day_change_pre2'] < 0 
        and low_tail_pct(regression_data) > 0.9
        ):   
        if('shortDownTrend' in regression_data['series_trend']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'shortDownTrend-1')
            flag = True
            if((low_tail_pct(regression_data) > 2 or low_tail_pct_pre1(regression_data) > 2)
                and -0.75 < regression_data['PCT_day_change']
                and regression_data['PCT_change'] > 0
                and regression_data['PCT_day_change_pre1'] < 0
                and regression_data['PCT_day_change_pre2'] < 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None,'mayReversalBuy-doji-shortDownTrend')
            elif(regression_data['month6LowChange'] > 0
                and (regression_data['PCT_day_change_pre1'] > 1
                    or regression_data['PCT_day_change_pre2'] > 1
                    or regression_data['PCT_day_change_pre3'] > 1
                    or regression_data['PCT_day_change_pre4'] > 1
                    )
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None,'mayContinueSell-doji-shortDownTrend')
            elif(regression_data['PCT_day_change_pre1'] < 0
                and regression_data['PCT_day_change_pre2'] < 0
                and regression_data['PCT_day_change_pre3'] < 0
                and regression_data['PCT_day_change_pre4'] < 0
                and regression_data['PCT_day_change_pre5'] < 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None,'mayReversalBuy-doji-downTrend')
                
    if('shortDownTrend' in regression_data['filter1']
        and -1.3 < regression_data['PCT_day_change'] < 0
        and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change'])*2
        and regression_data['PCT_day_change_pre1'] < -1
        and (regression_data['PCT_day_change_pre1'] < 0.5 and regression_data['PCT_day_change_pre2'] < 0.5)
        and (regression_data['PCT_day_change_pre1'] < -1 or regression_data['PCT_day_change_pre2'] < -1)
        and (regression_data['PCT_day_change_pre3'] > 1 or regression_data['PCT_day_change_pre4'] > 1)
        and (regression_data['PCT_day_change_pre3'] > -0.5 and regression_data['PCT_day_change_pre4'] > -0.5)
        and regression_data['year5LowChange'] > 5
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None,'TEST-DOWNTREND:mayContinueSell-(shortDownTrend)')
    return flag

def sell_high_volatility_riskyDowntrendBuy(regression_data, regressionResult):
    flag = False
    ws = None
    
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
        if(high_tail_pct(regression_data) <= 1.8
            and (0.6 <= high_tail_pct(regression_data) or regression_data['bar_high'] < regression_data['bar_high_pre1'])
            and 0 < regression_data['PCT_day_change'] < 1.7
            and (((regression_data['low'] < regression_data['low_pre1'] or regression_data['bar_high'] < regression_data['bar_high_pre1'])
                   and (regression_data['high'] < regression_data['high_pre1'])
                   and abs(regression_data['PCT_day_change']) < abs(regression_data['PCT_day_change_pre1']))
                )
            and abs(regression_data['month3LowChange']) > 2
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'RISKY-DOWNTREND-BUY-0')
            if(regression_data['high'] < regression_data['high_pre1']
                and regression_data['low'] < regression_data['low_pre1']
                and high_tail_pct(regression_data) > abs(regression_data['PCT_day_change'])    
                and low_tail_pct(regression_data) > abs(regression_data['PCT_day_change'])  
                and regression_data['bar_high'] < regression_data['bar_high_pre1']
                and regression_data['bar_low'] > regression_data['bar_low_pre1']
                and regression_data['forecast_day_PCT_change'] > regression_data['forecast_day_PCT2_change'] > regression_data['forecast_day_PCT3_change']
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None,'mayContinueSell-doji-RISKY-DOWNTREND-BUY')                                                          
        elif(0.6 <= high_tail_pct(regression_data) <= 1.8
            and 0 < regression_data['PCT_day_change'] < 1.7
            and (((regression_data['low'] < regression_data['low_pre1'] or regression_data['bar_low'] < regression_data['bar_low_pre1'])
                   and abs(regression_data['PCT_day_change']) < abs(regression_data['PCT_day_change_pre1']))
                or (regression_data['high'] < regression_data['high_pre1'] and regression_data['forecast_day_PCT_change'] < -0.5)
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'RISKY-DOWNTREND-BUY-1')
           
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
        and abs(regression_data['month3LowChange']) > 2
        and 0.5 < high_tail_pct(regression_data)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'RISKY-DOWNTREND-BUY-2')
        flag = True
        
    if('RISKY-DOWNTREND-BUY' in regression_data['filter5']
        and 'DOJI' in regression_data['filter5']
        and regression_data['PCT_day_change'] > 0
        and regression_data['PCT_day_change_pre1'] < 0
        and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change'])
        and (regression_data['PCT_day_change_pre1'] < -1 or abs(regression_data['PCT_day_change_pre1']) > 2*abs(regression_data['PCT_day_change']))
        and regression_data['week2LowChange'] < 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'RISKY-DOWNTREND-BUY-3')
        flag = True
        
    if('DOJI' in regression_data['filter5']
        and regression_data['PCT_day_change'] < 0
        and regression_data['PCT_day_change_pre1'] < -0.5
        and regression_data['PCT_day_change_pre2'] < -0.5
        and abs(regression_data['PCT_day_change']) < abs(regression_data['PCT_day_change_pre1'])
        and abs(regression_data['PCT_day_change']) < abs(regression_data['PCT_day_change_pre2'])
        and (abs(regression_data['PCT_day_change_pre1'])-abs(regression_data['PCT_day_change']))*100/abs(regression_data['PCT_day_change']) > 30
        ):
        if(regression_data['PCT_day_change_pre3'] > 0
            and (regression_data['week2LowChange'] > 3
                 or regression_data['weekLowChange'] > 3
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'RISKY-DOWNTREND-BUY-4-Sell')
        elif(regression_data['PCT_day_change_pre3'] < 0
            and regression_data['month3LowChange'] > 5
            and regression_data['low'] < regression_data['low_pre1']
            and regression_data['close'] < regression_data['close_pre1']
            and (regression_data['week2LowChange'] < 0.5)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'RISKY-DOWNTREND-BUY-4-Buy')
        elif(regression_data['PCT_day_change_pre3'] > -0.5
            and regression_data['month3LowChange'] < 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'RISKY-DOWNTREND-BUY-4-month3LowSell')
        
        flag = True
        
    if('RISKY-DOWNTREND-BUY' in regression_data['filter1']
       and 1.3 > regression_data['PCT_day_change'] > 0
       and -6 < regression_data['PCT_day_change_pre1'] < -1.3
       and (regression_data['PCT_day_change_pre1'] < -1.5 or regression_data['PCT_day_change_pre3'] > 0)
       and regression_data['PCT_day_change_pre2'] < 0
       and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change'])
       and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change_pre2'])
       and regression_data['forecast_day_PCT_change'] > regression_data['forecast_day_PCT2_change'] > regression_data['forecast_day_PCT3_change']
       and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change'])*2
       ):
        if(regression_data['PCT_day_change_pre3'] > 1 or regression_data['PCT_day_change_pre4'] > 1):
            add_in_csv(regression_data, regressionResult, ws, None, None, None,'mayReversalBuyInUptrend-ContinueSellInDownTrend-(RISKY-DOWNTREND-BUY)')
        elif(regression_data['PCT_day_change_pre3'] < -1 or regression_data['PCT_day_change_pre4'] < -1):
            add_in_csv(regression_data, regressionResult, ws, None, None, None,'mayContinueSell-(RISKY-DOWNTREND-BUY)') 
            
    if('RISKY-DOWNTREND-BUY' in regression_data['filter1']
       and 1.3 > regression_data['PCT_day_change'] > 0
       and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change'])*2
       and regression_data['PCT_day_change_pre1'] < -1
       and (regression_data['PCT_day_change_pre1'] < 0.5 and regression_data['PCT_day_change_pre2'] < 0.5)
       and (regression_data['PCT_day_change_pre1'] < -1 or regression_data['PCT_day_change_pre2'] < -1)
       and (regression_data['PCT_day_change_pre3'] > 1 or regression_data['PCT_day_change_pre4'] > 1)
       and (regression_data['PCT_day_change_pre3'] > -0.5 and regression_data['PCT_day_change_pre4'] > -0.5)
       #and regression_data['year5LowChange'] > 5
       ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None,'TEST-DOWNTREND:mayContinueSell-(RISKY-DOWNTREND-BUY)')
    elif(regression_data['PCT_day_change_pre1'] < -7
        and regression_data['PCT_day_change'] > 2
        and regression_data['bar_low_pre1'] < regression_data['bar_high'] < regression_data['bar_high_pre1']
        and high_tail_pct(regression_data) < 3
        and (regression_data['forecast_day_PCT5_change'] > 0 or regression_data['forecast_day_PCT10_change'])
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None,'TEST-DOWNTREND:mayLowerCircuitContinueDowntrend')
        flag = True
    elif('RISKY-DOWNTREND-BUY' in regression_data['filter1']
       and 1.3 > regression_data['PCT_day_change'] > 0
       and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change'])*2
       and (high_tail_pct(regression_data) > 1.5 or low_tail_pct(regression_data) > 1.5)
       and regression_data['PCT_day_change_pre1'] < 0
       and regression_data['PCT_day_change_pre2'] < 0
       and regression_data['PCT_day_change_pre3'] < 0
       ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None,'MCOpenUpGT0.7:mayContinueBuy-(RISKY-DOWNTREND-BUY)')
            
    return flag
    
def sell_high_volatility_lastDayUp(regression_data, regressionResult):
    flag = False
    ws = None
    
    if(regression_data['monthLowChange'] < 4 and regression_data['week2LowChange'] < 4 
        and (regression_data['weekLowChange'] < 4 or regression_data['week2LowChange'] < 0)
        and (regression_data['monthLowChange'] == regression_data['week2LowChange']
             or regression_data['week2LowChange'] == regression_data['weekLowChange']
             or regression_data['monthLowChange'] == regression_data['weekLowChange']
            )
        and abs(regression_data['monthHighChange']) > abs(regression_data['monthLowChange'])
        and abs(regression_data['week2HighChange']) > abs(regression_data['week2LowChange'])
        and 2 < regression_data['PCT_day_change'] < 7
        and 2 < regression_data['PCT_change'] < 7
        and regression_data['forecast_day_PCT7_change'] < -3 
        and regression_data['forecast_day_PCT10_change'] < -3 
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'morningSell-LastDayUp-DownTrend')
        if((regression_data['PCT_day_change_pre1'] < 0 and regression_data['PCT_day_change_pre2'] < 0)
            ):
            if(regression_data['bar_high'] > regression_data['bar_high_pre2']):
                add_in_csv(regression_data, regressionResult, ws, None, None, None,'mayFollowLast3DayTrendSellOrBuy-BrokenLast2DaySupport')
            elif(regression_data['bar_high'] < regression_data['bar_high_pre2']
                and regression_data['bar_high'] > regression_data['bar_high_pre1']
                and regression_data['PCT_day_change_pre1'] < -1 and regression_data['PCT_day_change_pre2'] < -1
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None,'mayMorning-BuyOrSell-5minutesMidcapTrend-last2DayUp')
        elif((regression_data['PCT_day_change_pre2'] < 0 and regression_data['PCT_day_change_pre3'] < 0)
            and regression_data['PCT_day_change_pre1'] > 0
            ):
            if(regression_data['bar_high'] > regression_data['bar_high_pre4']):
                add_in_csv(regression_data, regressionResult, ws, None, None, None,'mayFollowLast3DayTrendSellOrBuy-BrokenLast3DaySupport')
            elif(regression_data['bar_high'] < regression_data['bar_high_pre4']
                and regression_data['bar_high'] > regression_data['bar_high_pre3']
                and regression_data['PCT_day_change_pre2'] < -1 and regression_data['PCT_day_change_pre3'] < -1
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None,'mayMorning-BuyOrSell-5minutesMidcapTrend-lastDayDown')
        elif((regression_data['PCT_day_change'] < -1.5
                and regression_data['PCT_day_change_pre1'] < 0
                and regression_data['PCT_day_change_pre2'] < 0
                )
            ):
            if(regression_data['PCT_day_change_pre1'] < -1.5):
                add_in_csv(regression_data, regressionResult, ws, None, None, None,'mayBuy-Last3DayDown')
            elif(regression_data['PCT_day_change_pre1'] > -1):
                add_in_csv(regression_data, regressionResult, ws, None, None, None,'mayFollowMarketTrend')        
        elif(regression_data['PCT_day_change_pre2'] < 0
            and (regression_data['high'] > regression_data['high_pre3']
                or regression_data['bar_high'] > regression_data['bar_high_pre2'])
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None,'mayMorning(UPTREND-UPMARKET)Buy(DOWNTRENDTREND-DOWNMARKET)Sell')
        flag = True
    elif(regression_data['monthLowChange'] < 4 and regression_data['week2LowChange'] < 4 and regression_data['weekLowChange'] < 4
        and abs(regression_data['monthHighChange']) > abs(regression_data['monthLowChange'])
        and abs(regression_data['week2HighChange']) > abs(regression_data['week2LowChange'])
        and 2 < regression_data['PCT_day_change'] < 7
        and 2 < regression_data['PCT_change'] < 7
        and regression_data['PCT_day_change_pre1'] < 0
        and regression_data['PCT_day_change_pre2'] < 0
        and regression_data['forecast_day_PCT7_change'] < -3 
        and regression_data['forecast_day_PCT10_change'] < -3
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'morningSell-LastDayUp-DownTrend')
        if((regression_data['PCT_day_change_pre1'] < 0 and regression_data['PCT_day_change_pre2'] < 0)
            ):
            if(regression_data['bar_high'] > regression_data['bar_high_pre2']):
                add_in_csv(regression_data, regressionResult, ws, None, None, None,'mayFollowLast3DayTrendSellOrBuy-BrokenLast2DaySupport')
            elif(regression_data['bar_high'] < regression_data['bar_high_pre2']
                and regression_data['bar_high'] > regression_data['bar_high_pre1']
                and regression_data['PCT_day_change_pre1'] < -1 and regression_data['PCT_day_change_pre2'] < -1
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None,'mayMorning-BuyOrSell-5minutesMidcapTrend-last2DayUp')
        elif((regression_data['PCT_day_change_pre2'] < 0 and regression_data['PCT_day_change_pre3'] < 0)
            and regression_data['PCT_day_change_pre1'] > 0
            ):
            if(regression_data['bar_high'] > regression_data['bar_high_pre4']):
                add_in_csv(regression_data, regressionResult, ws, None, None, None,'mayFollowLast3DayTrendSellOrBuy-BrokenLast3DaySupport')
            elif(regression_data['bar_high'] < regression_data['bar_high_pre4']
                and regression_data['bar_high'] > regression_data['bar_high_pre3']
                and regression_data['PCT_day_change_pre2'] < -1 and regression_data['PCT_day_change_pre3'] < -1
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None,'mayMorning-BuyOrSell-5minutesMidcapTrend-lastDayDown')
        elif((regression_data['PCT_day_change'] < -1.5
                and regression_data['PCT_day_change_pre1'] < 0
                and regression_data['PCT_day_change_pre2'] < 0
                )
            ):
            if(regression_data['PCT_day_change_pre1'] < -1.5):
                add_in_csv(regression_data, regressionResult, ws, None, None, None,'mayBuy-Last3DayDown')
            elif(regression_data['PCT_day_change_pre1'] > -1):
                add_in_csv(regression_data, regressionResult, ws, None, None, None,'mayFollowMarketTrend')       
        elif(regression_data['PCT_day_change_pre2'] < 0
            and (regression_data['high'] > regression_data['high_pre3']
                or regression_data['bar_high'] > regression_data['bar_high_pre2'])
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None,'mayMorning(UPTREND-UPMARKET)Buy(DOWNTRENDTREND-DOWNMARKET)Sell')
        flag = True
        
    return flag
    
def sell_high_volatility(regression_data, regressionResult):
    flag = False
    ws = None
    
    if(regression_data['year2HighChange'] > -5):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'year2HighChangeGT-5')
    elif(regression_data['year2LowChange'] < 5):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'year2LowLT5')

    if (sell_high_volatility_shortDownTrend(regression_data, regressionResult)):
        flag = True

    if(sell_high_volatility_boundary(regression_data, regressionResult)):
        flag = True 
        
    if(sell_high_volatility_monthLowNotReached(regression_data, regressionResult)):
        flag = True
        
    if(sell_high_volatility_pre1pre2doji(regression_data, regressionResult)):
        flag = True
        
    if(sell_high_volatility_riskyDowntrendBuy(regression_data, regressionResult)):
        flag = True
        
    if(sell_high_volatility_lastDayUp(regression_data, regressionResult)):
        flag = True

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
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'checkSellConsolidationBreakDown(NotShapeA)-2week')
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
        and (regression_data['forecast_day_PCT7_change'] > 2 or regression_data['forecast_day_PCT10_change'] > 2)
        and regression_data['monthHighChange'] < -4
        and abs(regression_data['monthHighChange']) > abs(regression_data['monthLowChange'])
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'TEST:consolidationSellCandidate')
        flag = True
    elif((regression_data['forecast_day_PCT5_change'] < -10 or regression_data['forecast_day_PCT4_change'] < -10 or regression_data['forecast_day_PCT3_change'] < -10)
        and regression_data['PCT_day_change'] < -15
        and regression_data['close'] > 50
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'HEAVYDOWNTRENDMARKET:SellIfOpenHigh-BuyReversalIfOpenInLow(no-news-on-stock)(Nifty-down-last-3-days)')
        flag = True
    elif((regression_data['forecast_day_PCT5_change'] < -15 or regression_data['forecast_day_PCT4_change'] < -15 or regression_data['forecast_day_PCT3_change'] < -10)
        and regression_data['PCT_day_change'] < -5
        and (regression_data['PCT_day_change'] < -9 or "MLBuy" in regression_data['filter'])
        and regression_data['close'] > 50
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'HEAVYDOWNTRENDMARKET:BuyReversal(no-news-on-stock)(Nifty-down-last-3-days)')
        flag = True
            
    
   
    if('downTrend' in regression_data['series_trend'] 
        or 'DownTrend' in regression_data['series_trend'] 
        or 'trendDown' in regression_data['series_trend']
        or 'SMA9LT' in regression_data['series_trend']
        ):
        if(regression_data['PCT_day_change_pre1'] > 0.75 
            and regression_data['PCT_day_change'] > 0
            and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change'])
            and regression_data['high'] < regression_data['high_pre1']
            and 'DOJI' in regression_data['filter5']
            and regression_data['forecast_day_PCT5_change'] < -3
            and regression_data['forecast_day_PCT7_change'] < -3
            and regression_data['forecast_day_PCT10_change'] < -3
            and high_tail_pct(regression_data) < 1.5
            and low_tail_pct(regression_data) < 1.5
            ):
            #print(regression_data['scrip'])
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'DOWNTREND:mayContinueDownTrend-DOJI')
            flag = True
        elif(regression_data['PCT_day_change_pre1'] > 0 
            and regression_data['PCT_day_change'] > 0
            #and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change'])
            and regression_data['bar_high_pre1'] < regression_data['bar_high']
            #and regression_data['bar_high_pre1'] < regression_data['bar_high_pre2']
            and (regression_data['high'] < regression_data['high_pre2']
                 or regression_data['high'] < regression_data['high_pre3']
                 )
            and 'DOJI' in regression_data['filter5']
            and regression_data['forecast_day_PCT5_change'] < -3
            and regression_data['forecast_day_PCT7_change'] < -3
            and regression_data['forecast_day_PCT10_change'] < -3
            and high_tail_pct(regression_data) < 2.5
            and low_tail_pct(regression_data) < 2.5
            ):
            #print(regression_data['scrip'])
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'DOWNTREND:mayContinueDownTrend-DOJI-Risky')
            flag = True
        elif(regression_data['PCT_day_change_pre2'] < -0.5
            and regression_data['PCT_day_change_pre1'] > 0.5 
            and regression_data['PCT_day_change'] > 0.5
            and abs(regression_data['PCT_day_change_pre1']) < abs(regression_data['PCT_day_change'])
            and regression_data['bar_high_pre1'] < regression_data['bar_high']
            and regression_data['high'] < regression_data['high_pre3']
            and regression_data['forecast_day_PCT5_change'] < -3
            and regression_data['forecast_day_PCT7_change'] < -3
            and regression_data['forecast_day_PCT10_change'] < -5
            and (regression_data['forecast_day_PCT10_change'] < regression_data['forecast_day_PCT7_change'] < regression_data['forecast_day_PCT5_change']
                or (regression_data['forecast_day_PCT4_change'] < regression_data['forecast_day_PCT3_change'] - 2
                    and regression_data['forecast_day_PCT3_change'] < regression_data['forecast_day_PCT2_change'] -2
                    )
                )
            and high_tail_pct(regression_data) < 2.5
            and low_tail_pct(regression_data) < 2.5
            ):
            #print(regression_data['scrip'])
            add_in_csv(regression_data, regressionResult, ws, None, None, None, 'DOWNTREND:mayContinueDownTrend-Last2DayUp')
            flag = True

    if (regression_data['forecast_day_PCT5_change'] < regression_data['forecast_day_PCT4_change'] < regression_data[
        'forecast_day_PCT3_change'] < regression_data['forecast_day_PCT2_change'] < regression_data[
        'forecast_day_PCT_change'] < 1
        and regression_data['year2LowChange'] > 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, 'CheckChartUp-DowntrendLast5Day')
        flag = True
       
    if('%%' in regression_data['filter'] 
        or '$$' in regression_data['filter']
        or 'VOL:' in regression_data['filter']):
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
                #add_in_csv(regression_data, regressionResult, ws, None, None, 'CommonHL:maySellDownContinueGT-3')
                add_in_csv(regression_data, regressionResult, ws, None, None, None)
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
                #add_in_csv(regression_data, regressionResult, ws, None, None, 'CommonHL-(10:00to12:00):maySellDownContinueLT-3AfterSomeUpCheckBase')
                add_in_csv(regression_data, regressionResult, ws, None, None, None)
                
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
            #add_in_csv(regression_data, regressionResult, ws, None, None, 'AF:mayBuyReversalInSmallDowntrend')
            add_in_csv(regression_data, regressionResult, ws, None, None, None)
        elif(-4.0 < regression_data['PCT_day_change'] < -3 and -5 < regression_data['PCT_change'] < -1
            and ((regression_data['forecast_day_PCT3_change'] < 0 and regression_data['forecast_day_PCT4_change'] < 0)
                or regression_data['forecast_day_PCT5_change'] < 0
                or regression_data['forecast_day_PCT7_change'] < 0
                or regression_data['forecast_day_PCT10_change'] < 0
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'maySellDownContinueLT-3')
        elif(-4 < regression_data['PCT_day_change'] < -2 and -4 < regression_data['PCT_change'] < -1
            and regression_data['PCT_day_change_pre2'] < 1 
            and regression_data['low'] > regression_data['low_pre2']
            ):
            #add_in_csv(regression_data, regressionResult, ws, None, None, 'AF:maySellDownContinueGT-3')
            add_in_csv(regression_data, regressionResult, ws, None, None, None)

            
def sell_hltf_high_tail(regression_data, regressionResult, reg, ws):
    if(low_tail_pct(regression_data) <= 2 and 3 <= high_tail_pct(regression_data) <= 5.5
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
        add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:maySellTail-tailGT2-allDayGT0')
    elif(low_tail_pct(regression_data) <= 1.5 and 2 <= high_tail_pct(regression_data) <= 5.5
        and -5 < regression_data['PCT_day_change'] < 0 and -5 < regression_data['PCT_change'] < 5
        and regression_data['bar_high'] < regression_data['bar_high_pre1'] < regression_data['bar_high_pre2']
        and regression_data['forecast_day_PCT_change'] < 0
        and regression_data['forecast_day_PCT2_change'] < 0
        and regression_data['forecast_day_PCT7_change'] > 0
        and regression_data['forecast_day_PCT10_change'] > 0
        and regression_data['SMA25'] < 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:maySellTail-tailGT2-7,10thDayGT0')
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
        add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:maySellTail-tailGT2-2,3,4thDayGT0')
    elif(low_tail_pct(regression_data) < 2 and 1.5 < high_tail_pct(regression_data) < 2.1
        and (('MaySell-CheckChart' in regression_data['filter1']) or ('MaySellCheckChart' in regression_data['filter1']))
        and (-0.75 < regression_data['PCT_day_change'] < 0) and (-2.5 < regression_data['PCT_change'] < 1)
        and (regression_data['PCT_day_change'] < 0 or regression_data['PCT_change_pre1'] < 0)
        and (((regression_data['PCT_change_pre2'] > 0 or regression_data['PCT_change_pre3'] > 0)
                 and (regression_data['PCT_change_pre1'] < 0 or regression_data['PCT_change_pre2'] < 0 or regression_data['PCT_change_pre3'] < 0)
                 and regression_data['PCT_day_change'] < 0
                )
             )
        and high_tail_pct(regression_data) > low_tail_pct(regression_data)
        ): 
        add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:MaySellHighTail-LastDayMarketUp')
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
           add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:maySellTail-2,3,4thDayGT0')

    
    
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
        add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:buyHighLowerTail-Continue')
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
        add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:buyStockInUptrend')
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
        add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:sellStockInUptrendReversal')  
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
            if(regression_data['forecast_day_PCT7_change'] > 10 or regression_data['forecast_day_PCT10_change'] > 10):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:buyHighLowerTail-StockInUptrend')
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:buyHighLowerTail-LastDayMarketUp')
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
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:(NOT-GLOBAL/SGX-DOWN-Last2DayMarketDown)mayBuyTail-tailGT2(*)sellHighLowerTail')
            elif(regression_data['forecast_day_PCT7_change'] > 0 and regression_data['forecast_day_PCT10_change'] > 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:sellHighLowerTail-Reversal-LastDayMarketUp')
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:sellHighLowerTail-Reversal-LastDayMarketUp')
        elif(regression_data['PCT_day_change'] > 1 and regression_data['PCT_change'] > 1
            and regression_data['forecast_day_PCT7_change'] > 2
            and regression_data['forecast_day_PCT10_change'] > 2
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF:sellHighLowerTail-Reversal-LastDayMarketUp')
        elif(3.5 < low_tail_pct(regression_data) < 6
            and (regression_data['PCT_day_change_pre1'] > 1.5 or regression_data['PCT_day_change_pre2'] > 1.5)
            and regression_data['forecast_day_PCT7_change'] > 2
            and regression_data['forecast_day_PCT10_change'] > 2
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF-Last2DayMarketUp:sellHighLowerTail-Reversal-LastDayMarketUp')
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
        add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF-Last2DayMarketDown:buyHighUpperTailPre1-Reversal-LastDayMarketDown')



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
            add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF-Last2HighTail:sellHighUpperTailPre')
        elif(abs_monthHigh_less_than_monthLow(regression_data)):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF-Last2HighTail:sell(UPTREND)buy:HighUpperTailPre')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF-Last2HighTail:sellHighUpperTailPre')
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
        add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF-Last2HighTail:sellHighUpperTailPre-1')
    elif((high_tail_pct(regression_data) > 1.5 and high_tail_pct(regression_data) > low_tail_pct(regression_data))
        and (high_tail_pct_pre1(regression_data) > 1.5 and high_tail_pct_pre1(regression_data) > low_tail_pct_pre1(regression_data))
        and regression_data['high_pre1'] < regression_data['high']
        and regression_data['PCT_day_change'] > 0
        and regression_data['PCT_day_change_pre1'] > 0
        and abs_week2High_less_than_week2Low(regression_data)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF-Last2HighTail:(UPTREND)buy(DOWNTREND)sell:HighUpperTailPre-last2DayUp')
        
    if((low_tail_pct(regression_data) > 1.5 and high_tail_pct(regression_data) < low_tail_pct(regression_data))
        and ((low_tail_pct_pre1(regression_data) > 1.5 and regression_data['PCT_day_change'] < 0 and regression_data['low_pre1'] > regression_data['low'] and high_tail_pct_pre1(regression_data) < low_tail_pct_pre1(regression_data))
             or (low_tail_pct_pre2(regression_data) > 1.5 and regression_data['PCT_day_change'] < 0 and regression_data['low_pre2'] > regression_data['low'] and high_tail_pct_pre2(regression_data) < low_tail_pct_pre2(regression_data))
             )
        and (0 < regression_data['PCT_day_change'] < 2)
        and (abs_week2High_more_than_week2Low(regression_data))
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF-Last2LowTail:sellHighLowerTailPre')
    elif((low_tail_pct(regression_data) > 1.5 and high_tail_pct(regression_data) > 1.5)
        and (low_tail_pct_pre1(regression_data) > 1.5 and regression_data['high_pre1'] > regression_data['high'] and high_tail_pct_pre1(regression_data) < low_tail_pct_pre1(regression_data))
        and (0 < regression_data['PCT_day_change'] < 2)
        and (regression_data['forecast_day_PCT2_change'] < 0 and regression_data['forecast_day_PCT3_change'] < 0)
        and (abs_week2High_more_than_week2Low(regression_data)
             or regression_data['week2LowChange'] < 0
            )
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'HLTF-Last2LowTail:sellHighLowerTailPre-1')

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
        and (high_tail_pct(regression_data) >= 1.5 and (high_tail_pct(regression_data) > (abs(regression_data['PCT_day_change'])/3)))
        ):
        if(low_tail_pct(regression_data) > 1.5):
            add_in_csv(regression_data, regressionResult, ws, None, None, '$$MayBuyContinue-CheckChart(inUpTrend-monthHigh)-lowTail')
        elif(regression_data['monthLowChange'] > 10):
            add_in_csv(regression_data, regressionResult, ws, None, None, '$$MaySell-CheckChart-baseLine(inDownTrend-monthHigh)-MLCGT10')
        elif(regression_data['PCT_day_change'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, '$$MaySell-CheckChart-baseLine(inDownTrend-monthHigh)-PCTDayChangeGT0')
        elif(regression_data['PCT_day_change'] < -2 and regression_data['monthLowChange'] < 10):
            add_in_csv(regression_data, regressionResult, ws, None, None, '$$MayBuyContinue-CheckChart-baseLine(inDownTrend-monthHigh)-PCTDayChangeLT(-2)')
    elif(-3 < regression_data['monthHighChange'] < 1.3
        and regression_data['monthLowChange'] > 5
        and regression_data['weekHighChange'] > 0
        and abs(regression_data['month3HighChange']) > abs(regression_data['month3LowChange']) and regression_data['month3HighChange'] < -15
        and abs(regression_data['monthHighChange']) < abs(regression_data['monthLowChange'])
        and regression_data['year2HighChange'] < 0
        and regression_data['PCT_day_change'] < -1
        and (regression_data['PCT_day_change_pre3'] > 1 or regression_data['PCT_day_change_pre4'] > 1)
        and (high_tail_pct(regression_data) >= 1 or (high_tail_pct(regression_data) > (abs(regression_data['PCT_day_change'])/3)))
        ):
        if(low_tail_pct(regression_data) > 1.5):
            add_in_csv(regression_data, regressionResult, ws, None, None, '$$MayBuyContinue-CheckChart(inUpTrend-monthHigh)-lowTail')
        elif(regression_data['monthLowChange'] > 10):
            add_in_csv(regression_data, regressionResult, ws, None, None, '$$MaySell-CheckChart-baseLine(inDownTrend-monthHigh)-MLCGT10')
        elif(regression_data['PCT_day_change'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, '$$MaySell-CheckChart-baseLine(inDownTrend-monthHigh)-PCTDayChangeGT0')
        elif(regression_data['PCT_day_change'] < -2 and regression_data['monthLowChange'] < 10):
            add_in_csv(regression_data, regressionResult, ws, None, None, '$$(UPTREND-OR-GLOBALUP)$$MayBuyContinue-CheckChart-baseLine(inDownTrend-monthHigh)-PCTDayChangeLT(-2)')
    
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
    elif((1 <= regression_data['PCT_day_change'] < 2.5)
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
            add_in_csv(regression_data, regressionResult, ws, None, None, 'MaySell-CheckChart(downTrend-lastDayUp)')
    
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
            add_in_csv(regression_data, regressionResult, ws, None, None, "MaySellCheckChart-last3DayUp")
        elif((1 < regression_data['PCT_day_change'] <= 2) and (0 < regression_data['PCT_change'] <= 2)
            and 3 > high_tail_pct(regression_data) > 1.8
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, "MaySellCheckChart-Risky")
    elif(('MaySellCheckChart' in regression_data['filter1'])
        and ('Reversal' not in regression_data['filter3'])
        and regression_data['year2LowChange'] > 10
        and low_tail_pct(regression_data) < 0.5
        ):
        if((3 < regression_data['PCT_day_change'] <= 5) and (2 < regression_data['PCT_change'] <= 6)
            and 5 > high_tail_pct(regression_data) > 2.8
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, "MaySellCheckChart-PCTDayChangeGT(3)BigLowTail-Risky")
    
    if(regression_data['year2HighChange'] < -3
        and regression_data['high'] == regression_data['weekHigh'] 
        and high_tail_pct(regression_data) > 1.5
        and (regression_data['PCT_day_change'] > -2)
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
            add_in_csv(regression_data, regressionResult, ws, None, None, "MaySellCheckChart-monthHighReversal")
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
            add_in_csv(regression_data, regressionResult, ws, None, None, "MaySellCheckChart-monthHighReversal-risky")
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
            add_in_csv(regression_data, regressionResult, ws, None, None, "MaySellCheckChart-month2HighReversal-SMA9LT0")
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
            add_in_csv(regression_data, regressionResult, ws, None, None, "MaySellCheckChart-month2HighReversal")
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
            add_in_csv(regression_data, regressionResult, ws, None, None, "MaySellCheckChart-month2HighReversal-risky")
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
            add_in_csv(regression_data, regressionResult, ws, None, None, "MaySellCheckChart-month2HighReversal-SMA9LT0")
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
            add_in_csv(regression_data, regressionResult, ws, None, None, "MaySellCheckChart-month3HighReversal")
        elif(regression_data['month3HighChange'] > 0
            and regression_data['month3High'] != regression_data['weekHigh']
            and regression_data['month3High'] == regression_data['month6High'] 
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, "MaySellCheckChart-month3HighBreakReversal")
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
            add_in_csv(regression_data, regressionResult, ws, None, None, "MaySellCheckChart-month6HighReversal")
        elif(regression_data['month6HighChange'] > 0
            and regression_data['month6High'] != regression_data['weekHigh']
            and regression_data['month6High'] == regression_data['yearHigh'] 
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, "MaySellCheckChart-month6HighBreakReversal")
    
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
    
    if(regression_data['month3HighChange'] > 0 
        and regression_data['monthHighChange'] > 0
        and regression_data['week2HighChange'] > 0
        and regression_data['weekHighChange'] > 0
        and regression_data['monthLowChange'] > 20
        and regression_data['forecast_day_PCT_change'] > 0 and regression_data['forecast_day_PCT2_change'] > 0
        and (regression_data['PCT_day_change_pre1'] < 0 
             or regression_data['PCT_day_change_pre2'] < 0 
             or regression_data['PCT_day_change_pre3'] < 0
             or regression_data['PCT_day_change_pre4'] < 0
            )
        and 1 < regression_data['PCT_day_change'] < 3 and 1 < regression_data['PCT_change'] < 4
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellUpTrend-month3High')
        return True
        
    
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
    flag = False
    if(('NearHigh' in regression_data['filter3'] or 'ReversalHigh' in regression_data['filter3'])
        and 'LT0' not in regression_data['filter3']
        and regression_data['SMA4'] < 0
        and regression_data['SMA4_2daysBack'] < 0
        and regression_data['PCT_day_change'] < -0.5 and regression_data['PCT_change'] < 0
        #and (regression_data['PCT_day_change_pre2'] < 0 or regression_data['PCT_day_change_pre3'] < 0)
        and (regression_data['PCT_day_change_pre1'] > 0 or regression_data['PCT_day_change_pre2'] > 0)
        and regression_data['forecast_day_PCT_change'] < 0
        and regression_data['low'] < regression_data['low_pre1']
        ):
        if(regression_data['SMA4'] < regression_data['SMA4_2daysBack']
            and regression_data['SMA9'] < regression_data['SMA9_2daysBack']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellDownTrend-nearHigh')
            flag = True
        else:
            #add_in_csv(regression_data, regressionResult, ws, None, None, 'chisDownTrend-Risky-nearHigh')
            flag = True
    if(regression_data['forecast_day_PCT10_change'] < -10
        and regression_data['year2HighChange'] < -60
        and regression_data['month3LowChange'] < 10
        and (regression_data['forecast_day_PCT_change'] >= -1.5)
        and 3 < regression_data['PCT_day_change'] < 7
        and 2 < regression_data['PCT_change'] < 8
        and (regression_data['PCT_day_change_pre1'] < -4 or regression_data['PCT_day_change_pre2'] < -4)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellYear2LowContinue')
        flag = True
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
            flag = True
        elif(abs_yearHigh_less_than_yearLow(regression_data)
           and -4 < regression_data['PCT_day_change'] < -2 and -4 < regression_data['forecast_day_PCT_change'] < -2
           and regression_data['PCT_change'] < regression_data['PCT_day_change'] - 0.2
           and regression_data['forecast_day_PCT_change'] < regression_data['PCT_day_change'] - 0.2
           and regression_data['series_trend'] != 'upTrend'
           and str(regression_data['score']) != '10' 
           and (regression_data['forecast_day_PCT7_change'] > 0 and regression_data['forecast_day_PCT10_change'] > 0)
           ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellDownTrend-00')
            flag = True
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
            flag = True
        elif(abs_yearHigh_less_than_yearLow(regression_data)
           and regression_data['yearLowChange'] > 10 
           and -4 < regression_data['PCT_day_change'] < -2 and -4 < regression_data['forecast_day_PCT_change'] 
           and regression_data['forecast_day_PCT_change'] > regression_data['PCT_change']
           and regression_data['series_trend'] != 'upTrend'
           and str(regression_data['score']) != '10'
           and (regression_data['forecast_day_PCT7_change'] > -5 and regression_data['forecast_day_PCT10_change'] > -7) 
           ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##longDownTrend-1-IndexNotDownLastDay(checkBase)')
            flag = True
        elif(-4 < regression_data['PCT_day_change'] < -2 and -4 < regression_data['forecast_day_PCT_change'] 
           and regression_data['forecast_day_PCT_change'] > regression_data['PCT_change']
           and regression_data['series_trend'] != 'upTrend'
           and str(regression_data['score']) != '10'
           and (regression_data['forecast_day_PCT7_change'] > -5 and regression_data['forecast_day_PCT10_change'] > -7) 
           ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##longDownTrend-2-IndexNotDownLastDay(checkBase)')
            flag = True
    elif(all_day_pct_change_negative(regression_data) and -4 < regression_data['PCT_day_change'] < -2 and regression_data['yearLowChange'] > 30
        and regression_data['forecast_day_PCT10_change'] <= regression_data['PCT_change'] - 2
        and regression_data['forecast_day_PCT10_change'] <= regression_data['PCT_day_change'] - 2
        and float(regression_data['forecast_day_VOL_change']) > 30
        and regression_data['PCT_day_change_pre1'] < 0.5
        and float(regression_data['contract']) > 10
        and no_doji_or_spinning_sell_india(regression_data)):
        #add_in_csv(regression_data, regressionResult, ws, None, None, '##longDownTrend-Risky-IndexNotDownLastDay(checkBase)')
        flag = True
    
    if('shortDownTrend' in regression_data['series_trend']):
        if(-1.3 < regression_data['PCT_day_change'] < 0 and -2 < regression_data['PCT_change'] < 0
            and -1.3 > regression_data['PCT_day_change_pre1'] < regression_data['PCT_day_change']
            and -1.3 > regression_data['PCT_day_change_pre2'] < regression_data['PCT_day_change']
            and regression_data['forecast_day_PCT_change'] < 0
            and (-2 < regression_data['month3LowChange'] < 1
                or (abs(bar_low_change_month3(regression_data)) < 1 and low_tail_pct(regression_data) > 1)
                )
            and (high_tail_pct(regression_data) < 0.5 or high_tail_pct(regression_data) < low_tail_pct(regression_data)
                or abs(high_tail_pct(regression_data) - low_tail_pct(regression_data)) <= 0.2   
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None,'shortDownTrendBuyReversal-Month3Low-Doji-Last2DayLTToday')
            flag = True
        elif(-1.3 < regression_data['PCT_day_change'] < 0 and -2 < regression_data['PCT_change'] < 0
            and -1.3 > regression_data['PCT_day_change_pre1'] < regression_data['PCT_day_change']
            and -1.3 > regression_data['PCT_day_change_pre2'] < regression_data['PCT_day_change']
            and regression_data['forecast_day_PCT_change'] < 0
            and ((-0.5 < regression_data['monthLowChange'] < 1.5 and regression_data['month3LowChange'] > 20)
                or (abs(bar_low_change_month(regression_data)) < 1 and low_tail_pct(regression_data) > 1)
                )
            and (high_tail_pct(regression_data) < 0.5 or high_tail_pct(regression_data) < low_tail_pct(regression_data)
                or abs(high_tail_pct(regression_data) - low_tail_pct(regression_data)) <= 0.2 
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None,'shortDownTrendBuyReversal-MonthLow-Doji-Last2DayLTToday')
            flag = True
        elif(-1.3 < regression_data['PCT_day_change'] < 0 and -2 < regression_data['PCT_change'] < 0
            and -1.3 > regression_data['PCT_day_change_pre1'] < regression_data['PCT_day_change']
            and -1.3 > regression_data['PCT_day_change_pre2'] < regression_data['PCT_day_change']
            and regression_data['forecast_day_PCT_change'] < 0
            and regression_data['month3LowChange'] > 5
            and regression_data['monthHighChange'] < -5
            and abs(regression_data['monthLowChange']) > 1.5
            and abs(regression_data['monthLowChange']) < abs(regression_data['monthHighChange'])
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None,'shortDownTrendSellContinue-Doji-Last2DayLTToday')
            flag = True
        if(regression_data['PCT_day_change'] < 0 and regression_data['PCT_change'] < 0
            and regression_data['forecast_day_PCT_change'] < 0
            and ((-1.5 < regression_data['monthLowChange'] < 1.5 and regression_data['monthLowChange'] == regression_data['month2LowChange'])
                and abs(bar_low_change_month(regression_data)) < 1
                )
            and low_tail_pct(regression_data) > 1 and high_tail_pct(regression_data) < low_tail_pct(regression_data)
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None,'shortDownTrendBuyReversal-MonthLow')
            flag = True
    return flag

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
                add_in_csv(regression_data, regressionResult, ws, None, None, '##sellFinalCandidate-2')
                return True
        elif((((regression_data['open'] - regression_data['close']) * 1.5 > regression_data['high'] - regression_data['low']) or (regression_data['forecast_day_PCT_change'] < 0 and regression_data['PCT_day_change'] < -1))
            and (regression_data['yearHighChange'] > -30 or regression_data['yearLowChange'] > 30)
            ):
            if(-2.5 < regression_data['PCT_day_change'] < -1 and -2.5 < regression_data['PCT_change'] < -1 
                and no_doji_or_spinning_sell_india(regression_data) and no_doji_or_spinning_buy_india(regression_data)
                ):
                if(regression_data['forecast_day_VOL_change'] > -20):
                    add_in_csv(regression_data, regressionResult, ws, None, None, '##sellFinalCandidate-3')
                    return True
            elif(-5 < regression_data['PCT_day_change'] < -1 and -5 < regression_data['PCT_change'] < -1 
                and no_doji_or_spinning_sell_india(regression_data) and no_doji_or_spinning_buy_india(regression_data)
                ):
                if(regression_data['forecast_day_VOL_change'] > 0):
                    add_in_csv(regression_data, regressionResult, ws, None, None, '##sellFinalCandidate-4')
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
            add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:sellAboveTail-BuyAtClose:upVol3dayDownWeek2Low-highLowerTail')
        elif(regression_data['week2LowChange'] > 4.0
            and (regression_data['week2HighChange'] > 0
                or abs_week2High_less_than_week2Low(regression_data)
                or abs_weekHigh_less_than_weekLow(regression_data)
                )
            and regression_data['PCT_day_change_pre3'] > 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:sell(GLOBALFUTUP-GLOBALMARKETUP)Buy-UpVol-3dayDown-Week2High')
        elif(regression_data['week2HighChange'] < -4.0
            and (regression_data['low']-regression_data['high']) < regression_data['PCT_day_change_pre1']
            and (regression_data['PCT_day_change'] > -6 and regression_data['PCT_change'] > -6) 
            and (regression_data['PCT_day_change'] > -3 or regression_data['PCT_day_change_pre1'] < -1)
            and (regression_data['PCT_day_change_pre1'] < -1 or regression_data['PCT_day_change_pre2'] < -1)
            and abs_week2High_more_than_week2Low(regression_data)
            and abs_monthHigh_more_than_monthLow(regression_data)
            and abs_month3High_more_than_month3Low(regression_data)
            and low_tail_pct(regression_data) < 2
            and regression_data['forecast_day_VOL_change'] > 10
            ):
            if(regression_data['PCT_day_change_pre1'] < -1 and regression_data['PCT_day_change_pre2'] < -1):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:buy-UpVol-3dayDown-Week2Low')
             
    elif(regression_data['PCT_day_change'] < -2 and regression_data['PCT_change'] < -2
        and regression_data['PCT_day_change_pre1'] < 0
        and regression_data['PCT_day_change_pre2'] < 0.5
        and regression_data['volume'] < regression_data['volume_pre1']
        and regression_data['volume'] < regression_data['volume_pre2']
        and (regression_data['forecast_day_VOL_change'] < -20
            or regression_data['volume'] < regression_data['volume_pre1'] < regression_data['volume_pre2']
            )
        ):
        if(regression_data['PCT_day_change_pre1'] < -1.5 or regression_data['PCT_day_change_pre2'] < -1.5):
            if(regression_data['week2LowChange'] > 4.0
                and (regression_data['week2HighChange'] > 0
                    or abs_week2High_less_than_week2Low(regression_data)
                    or abs_weekHigh_less_than_weekLow(regression_data)
                    )
                and regression_data['PCT_day_change_pre3'] > 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:buy-DownVol-3dayDown-Week2High')
            elif(regression_data['week2HighChange'] < -4.0
                and (regression_data['low']-regression_data['high']) < regression_data['PCT_day_change_pre1']
                and abs_week2High_more_than_week2Low(regression_data)
                and abs_monthHigh_more_than_monthLow(regression_data)
                and abs_month3High_more_than_month3Low(regression_data)
                and low_tail_pct(regression_data) < 2
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'vol-buy-DownVol-3dayDown-Week2Low') 
        elif(regression_data['PCT_day_change_pre1'] < -1.5 and regression_data['PCT_day_change_pre2'] < -1.5
            and regression_data['PCT_day_change'] > -5
            ):
            if(regression_data['week2LowChange'] > 4.0
                and (regression_data['week2HighChange'] > 0
                    or abs_week2High_less_than_week2Low(regression_data)
                    or abs_weekHigh_less_than_weekLow(regression_data)
                    )
                and regression_data['PCT_day_change_pre3'] > 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:sell-DownVol-3dayDown-Week2High')      
    elif(regression_data['PCT_day_change'] < -0.75 and regression_data['PCT_change'] < -0.75 and regression_data['PCT_day_change_pre1'] < 0
        and (regression_data['PCT_day_change'] < -2 or regression_data['PCT_day_change_pre1'] < -2)
        and abs(regression_data['weekLowChange']) > abs(regression_data['weekHighChange'])
        #and abs(abs(regression_data['PCT_day_change']) - abs(regression_data['PCT_day_change_pre1'])) > 1.5 
        ):
        if(abs(regression_data['PCT_day_change']) > abs(regression_data['PCT_day_change_pre1'])
            and regression_data['forecast_day_VOL_change'] < 0
            and (abs(regression_data['PCT_day_change']) - abs(regression_data['PCT_day_change_pre1']) > 2
                or regression_data['forecast_day_VOL_change'] < -30
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:BuyReversalLast2DayDown-VolDown')
        elif(abs(regression_data['PCT_day_change']) < abs(regression_data['PCT_day_change_pre1'])
            and regression_data['forecast_day_VOL_change'] > 0
            and (abs(regression_data['PCT_day_change']) - abs(regression_data['PCT_day_change_pre1']) < -2
                or regression_data['forecast_day_VOL_change'] > 30
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:BuyReversalLast2DayDown-VolUp')
        elif(abs(regression_data['PCT_day_change']) > abs(regression_data['PCT_day_change_pre1'])
            and regression_data['forecast_day_VOL_change'] > 0
            and (abs(regression_data['PCT_day_change']) - abs(regression_data['PCT_day_change_pre1']) > 2
                or regression_data['forecast_day_VOL_change'] > 30
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:SellContinueLast2DayDown-VolUp')
#         elif(abs(regression_data['PCT_day_change']) < abs(regression_data['PCT_day_change_pre1'])
#             and regression_data['forecast_day_VOL_change'] < 0
#             and (abs(regression_data['PCT_day_change']) - abs(regression_data['PCT_day_change_pre1']) < -2
#                 or regression_data['forecast_day_VOL_change'] < -30
#                 )
#             ):
#             add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:sellContinueLast2DayDown-VolDown')
        
        
        
             
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
            add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:checkSellRevarsalLast3DayUpAtMonth3Low') 
        if(regression_data['PCT_day_change'] > 1
            and regression_data['PCT_day_change_pre1'] > 1
            and regression_data['PCT_day_change_pre2'] > 1
            and ((abs(regression_data['PCT_day_change']) > abs(regression_data['PCT_day_change_pre1']) and regression_data['forecast_day_VOL_change'] < -10)
                or (abs(regression_data['PCT_day_change']) < abs(regression_data['PCT_day_change_pre1']) and regression_data['forecast_day_VOL_change'] > 10)
                or (abs(regression_data['PCT_day_change']) > (1.5*abs(regression_data['PCT_day_change_pre1'])) and regression_data['volume'] < regression_data['volume_pre1'])
                or ((1.5*abs(regression_data['PCT_day_change'])) < abs(regression_data['PCT_day_change_pre1']) and regression_data['volume'] > regression_data['volume_pre1'])
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'VOL:SellRevarsalVolCrossed')
            
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
            add_in_csv(regression_data, regressionResult, ws, None, None, 'zigZagVolCrossedUptrendFromDown')
        elif(abs(regression_data['PCT_day_change']) > 2*abs(regression_data['PCT_day_change_pre1'])
            and regression_data['PCT_day_change'] > 4
            and regression_data['PCT_day_change_pre1'] < -1
            and 0 < regression_data['forecast_day_VOL_change'] < 150
            and 20 < regression_data['contract'] < 150 
            and 50 < regression_data['oi_next'] < 150
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'continueZigZagVolCrossedFromDown')
        elif(abs(regression_data['PCT_day_change']) < 2*abs(regression_data['PCT_day_change_pre1'])
            and regression_data['PCT_day_change'] > 2
            and regression_data['PCT_day_change_pre1'] < -1 
            and regression_data['PCT_day_change_pre3'] < 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'zigZagVolCrossedFromDown')
        
            
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
        add_in_csv(regression_data, regressionResult, ws, None, None, 'volumeUpsergedLast2n3n4DayUp')
    elif(-5 < regression_data['PCT_day_change'] < -2 and -5 < regression_data['PCT_change'] < -1
        and (regression_data['PCT_day_change_pre1'] < -1 or (regression_data['forecast_day_PCT3_change'] < 0 and regression_data['low'] < regression_data['low_pre3']))
        and regression_data['PCT_day_change_pre2'] > 0
        and regression_data['PCT_day_change_pre3'] > 0
        and regression_data['PCT_day_change_pre4'] < 0
        #and abs(regression_data['PCT_day_change_pre1']) > abs(regression_data['PCT_day_change_pre2'])
        and (regression_data['monthLowChange'] < 0 or abs(regression_data['monthHighChange']) > abs(regression_data['monthLowChange']))
        and regression_data['volume'] > regression_data['volume_pre1']
        and regression_data['volume'] > regression_data['volume_pre2']
        and regression_data['volume'] > regression_data['volume_pre3']
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'volBuyVolumeUpsergedLast2n3DayUp')
    elif(-5 < regression_data['PCT_day_change'] < -2 and -5 < regression_data['PCT_change'] < -1
        and (-1 < regression_data['PCT_day_change_pre1'] < 0 or (regression_data['forecast_day_PCT3_change'] > 0 and regression_data['low'] > regression_data['low_pre3']))
        and regression_data['PCT_day_change_pre2'] > 0
        and regression_data['PCT_day_change_pre3'] > 0
        and regression_data['PCT_day_change_pre4'] < 0
        #and abs(regression_data['PCT_day_change_pre1']) < abs(regression_data['PCT_day_change_pre2'])
        and (regression_data['monthHighChange'] > 0 or abs(regression_data['monthHighChange']) < abs(regression_data['monthLowChange']))
        and regression_data['volume'] > regression_data['volume_pre1']
        and regression_data['volume'] > regression_data['volume_pre2']
        and regression_data['volume'] > regression_data['volume_pre3']
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'volSellVolumeUpsergedLast2n3DayUp')
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
        add_in_csv(regression_data, regressionResult, ws, None, None, 'volSellVolumeUpsergedLast1n2DayUp')
        
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
        else:
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
    elif(
        regression_data['forecast_day_PCT7_change'] > 0
        and regression_data['forecast_day_PCT10_change'] > 0
        and -12 < regression_data['PCT_day_change'] < -8 and -12 < regression_data['PCT_change'] < -8
        and regression_data['close'] > 50
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'maySellContinueHighVolatileLastDayDOWN-PCT10GT0-(LT-8)')
    elif(
        regression_data['month3LowChange'] > 0 
        and (regression_data['week2LowChange'] < 0 or abs(regression_data['week2HighChange']) > abs(regression_data['week2LowChange']))
        and regression_data['forecast_day_PCT10_change'] > -20
        and -12 < regression_data['PCT_day_change'] < -8 and -12 < regression_data['PCT_change'] < -8
        and regression_data['close'] > 50
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'maySellContinueHighVolatileLastDayDOWN-month3LowGT0-(LT-8)')
    elif(
        regression_data['month6LowChange'] > 0 
        and (regression_data['week2LowChange'] < 0 or abs(regression_data['week2HighChange']) > abs(regression_data['week2LowChange']))
        and regression_data['forecast_day_PCT10_change'] > -20
        and -12 < regression_data['PCT_day_change'] < -8 and -12 < regression_data['PCT_change'] < -8
        and regression_data['close'] > 50
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'maySellContinueHighVolatileLastDayDOWN-month6LowGT0-(LT-8)')
    elif((regression_data['forecast_day_PCT3_change'] < 0 and regression_data['forecast_day_PCT4_change'] < 0)
        or regression_data['forecast_day_PCT5_change'] < 0
        or regression_data['forecast_day_PCT7_change'] < 0
        or regression_data['forecast_day_PCT10_change'] < 0
        ):
        if( -8 < regression_data['PCT_day_change'] < -4 and -10 < regression_data['PCT_change'] < -3
            and (regression_data['PCT_day_change'] < -5 or regression_data['PCT_change'] < -5)  
            and regression_data['PCT_day_change_pre1'] > 0
            and regression_data['PCT_day_change_pre2'] > 0
            and (regression_data['PCT_day_change_pre1'] > 1 or regression_data['PCT_day_change_pre2'] > 1)
            and high_tail_pct(regression_data) < 2.5
            and low_tail_pct(regression_data) < abs(regression_data['PCT_day_change'])/3
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'maySellContinueHighVolatileLastDayDOWN-(LT-5)')    
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
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkCupDown-2dayDown-continue')
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
    weekBarLowChange = ((regression_data['bar_low'] - regression_data['weekBarLow'])/regression_data['bar_low'])*100
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
        and (regression_data['week3BarLow'] >= regression_data['week2BarLow'])
        ):
        if(regression_data['weekBarLow'] < regression_data['bar_low_pre1'] 
            and regression_data['week2BarLow'] < regression_data['bar_low_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'brokenToday')
        if(regression_data['weekLow'] < regression_data['week2Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'weekLowLTweek2Low')
        if(week2BarLowChange < -5):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'week2BarLowChangeLT-5')
        elif(week2BarLowChange < -2):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'week2BarLowChangeLT-2')
        elif(week2BarLowChange < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'week2BarLowChangeLT0')
        if(regression_data['PCT_day_change'] < -2
            and regression_data['year2LowChange'] > 5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkSellConsolidationBreakDown-2week')
        elif(regression_data['year2LowChange'] < 5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkSellConsolidationBreakDown-2week-(Risky)-year2Low')
    elif(-6 < regression_data['PCT_day_change'] < -1.5
        and -6 < regression_data['PCT_change']
        and regression_data['PCT_day_change_pre1'] < 1
        and regression_data['low'] < regression_data['high_pre2']
        and regression_data['low'] < regression_data['high_pre1']
        and regression_data['bar_low'] < regression_data['week2BarLow']
        and (regression_data['bar_low'] > regression_data['week3BarLow'] or (regression_data['bar_low'] > regression_data['week3Low'] and regression_data['week3Low'] != regression_data['week2Low']))
        and (regression_data['bar_low_pre1'] > regression_data['week2BarLow'] or regression_data['bar_low_pre1'] > regression_data['week2Low'])
        ):
        if(regression_data['weekLow'] < regression_data['week2Low']):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'weekLowLTweek2Low')
        if(week2BarLowChange < -5):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'week2BarLowChangeLT-5')
        elif(week2BarLowChange < -2):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'week2BarLowChangeLT-2')
        elif(week2BarLowChange < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'week2BarLowChangeLT0')
        if(regression_data['PCT_day_change'] < -1.5
            and regression_data['year2LowChange'] > 5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkSellConsolidationBreakDown-week2-lowNotReachedWeek3')
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
    elif(-6 < regression_data['PCT_day_change'] < -1.5
        and -6 < regression_data['PCT_change']
        and regression_data['PCT_day_change_pre1'] < 1
        #and regression_data['low'] < regression_data['high_pre3']
        and regression_data['low'] < regression_data['high_pre2']
        and regression_data['low'] < regression_data['high_pre1']
        and -10 < regression_data['forecast_day_PCT4_change'] < -0.5
        and -10 < regression_data['forecast_day_PCT3_change'] < 0
        and -10 < regression_data['forecast_day_PCT2_change'] < 0
        and -4 < regression_data['forecast_day_PCT_change'] < 0
        and ((regression_data['bar_low_pre1'] >= regression_data['week2BarLow'] and regression_data['bar_low_pre1'] > regression_data['week2Low']
                and regression_data['bar_low'] <= regression_data['week2BarLow']
                )
             or (regression_data['bar_low_pre1'] >= regression_data['week3BarLow'] and regression_data['bar_low_pre1'] > regression_data['week3Low']
                and regression_data['bar_low'] <= regression_data['week3BarLow']
                )
             or (regression_data['bar_low_pre1'] >= regression_data['monthBarLow'] and regression_data['bar_low_pre1'] > regression_data['monthLow']
                and regression_data['bar_low'] <= regression_data['monthBarLow'] 
                )
             or (regression_data['bar_low_pre1'] >= regression_data['month3BarLow'] and regression_data['bar_low_pre1'] > regression_data['month3Low']
                and regression_data['bar_low'] <= regression_data['month3BarLow']
                )
            )
        ):
        if(regression_data['weekBarLow'] < regression_data['bar_low_pre1'] 
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'brokenToday')
        if(weekBarLowChange < -5):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'weekBarLowChangeLT-5')
        elif(weekBarLowChange < -2):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'weekBarLowChangeLT-2')
        elif(weekBarLowChange < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'weekBarLowChangeLT0')
        if((regression_data['bar_low_pre1'] > regression_data['month3BarLow'] or regression_data['bar_low_pre1'] > regression_data['month3Low'])
            and regression_data['bar_low_pre1'] < regression_data['month6BarLow']
            and regression_data['bar_low'] <= regression_data['month3BarLow']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkSellConsolidationBreakDown-month3')
        elif((regression_data['bar_low_pre1'] > regression_data['month2BarLow'] or regression_data['bar_low_pre1'] > regression_data['month2Low'])
            and regression_data['bar_low_pre1'] < regression_data['month3BarLow']
            and regression_data['bar_low'] <= regression_data['month2BarLow']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkSellConsolidationBreakDown-month2')
        elif((regression_data['bar_low_pre1'] > regression_data['monthBarLow'] or regression_data['bar_low_pre1'] > regression_data['monthLow'])
            and regression_data['bar_low_pre1'] < regression_data['month2BarLow']
            and regression_data['bar_low'] <= regression_data['monthBarLow']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkSellConsolidationBreakDown-month')
        elif((regression_data['bar_low_pre1'] > regression_data['week2BarLow'] or regression_data['bar_low_pre1'] > regression_data['week2Low'])
            and regression_data['bar_low_pre1'] < regression_data['monthBarLow']
            and regression_data['bar_low'] <= regression_data['week2BarLow']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'checkSellConsolidationBreakDown-week2')
        
        
    if(regression_data['low'] < regression_data['low_pre1']
        and regression_data['low'] < regression_data['low_pre2']
        and regression_data['low'] < regression_data['low_pre3']
        and regression_data['low'] < regression_data['low_pre4']
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
            and -4.5 < regression_data['PCT_day_change'] < -2.5
            and regression_data['bar_low'] < regression_data['bar_low_pre1']
            and regression_data['bar_low'] < regression_data['bar_low_pre2']
            and -1.5 < regression_data['PCT_day_change_pre1'] < 1.5
            and -1.5 < regression_data['PCT_day_change_pre2'] < 1.5
            and -1.5 < regression_data['PCT_day_change_pre3'] < 1.5
            and -1.5 < regression_data['PCT_day_change_pre4'] < 1.5 
            ):
            if((regression_data['forecast_day_PCT10_change'] - regression_data['forecast_day_PCT5_change']) < -5
                or (regression_data['forecast_day_PCT7_change'] - regression_data['forecast_day_PCT5_change']) < -5
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisConsolidationBreakdown2WeekGT(-4.5)')
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisConsolidationBreakdownGT(-4.5)')
        elif(regression_data['forecast_day_PCT_change'] < 0
            and -7 < regression_data['PCT_day_change'] < -4.5
            and regression_data['bar_low'] < regression_data['bar_low_pre1']
            and regression_data['bar_low'] < regression_data['bar_low_pre2']
            and -1.5 < regression_data['PCT_day_change_pre1'] < 1.5
            and -1.5 < regression_data['PCT_day_change_pre2'] < 1.5
            and -1.5 < regression_data['PCT_day_change_pre3'] < 1.5
            and -1.5 < regression_data['PCT_day_change_pre4'] < 1.5 
            ):
            if((regression_data['forecast_day_PCT10_change'] - regression_data['forecast_day_PCT5_change']) < -5
                or (regression_data['forecast_day_PCT7_change'] - regression_data['forecast_day_PCT5_change']) < -5
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisConsolidationBreakdown2WeekLT(-4.5)')
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisConsolidationBreakdownLT(-4.5)')

def sell_supertrend(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    
    flag = False

    if ((regression_data['PCT_day_change'] > 6 or regression_data['PCT_change'] > 6)
        and (regression_data['forecast_day_PCT5_change'] > 10 or regression_data['forecast_day_PCT7_change'] > 10 or regression_data['forecast_day_PCT10_change'] > 15)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None,'%%:MaySell-High-UpTrend')
    
    if(regression_data['year2HighChange'] > -3 or regression_data['year2LowChange'] < 3):
        return False
    
    if( -7.5 < regression_data['PCT_day_change_pre1'] < -1.5 and -8 < regression_data['PCT_change_pre1'] < -0.75
        and regression_data['PCT_day_change_pre2'] < 0
        and ((regression_data['PCT_day_change_pre1'] < -2 or regression_data['PCT_day_change_pre2'] < -2)
             or (regression_data['PCT_day_change_pre2'] < -1 and regression_data['PCT_day_change_pre2'] < -1)
            )
        and (regression_data['PCT_day_change_pre3'] < 0 
             or regression_data['PCT_day_change_pre4'] < 0
             or high_tail_pct(regression_data) > 1.5
            )
        and (regression_data['PCT_day_change_pre1'] > 0 or regression_data['PCT_day_change_pre2'] > 0 or regression_data['PCT_day_change_pre3'] > 0 or regression_data['PCT_day_change_pre4'] > 0)
        and -1.5 < regression_data['PCT_day_change'] < 3
        and regression_data['bar_high'] < regression_data['bar_high_pre1']
        and (regression_data['high'] < regression_data['high_pre1'] or regression_data['low'] < regression_data['low_pre1'])
        and ((regression_data['forecast_day_PCT2_change'] < 0 and regression_data['forecast_day_PCT3_change'] < 0)
            or (regression_data['forecast_day_PCT3_change'] < 0 and regression_data['forecast_day_PCT4_change'] < 0)
            )
        and regression_data['forecast_day_PCT10_change'] > -15
        and ((regression_data['forecast_day_PCT7_change'] > 0 and regression_data['forecast_day_PCT10_change'] > 0)
            or (regression_data['forecast_day_PCT3_change'] < 0
                and regression_data['forecast_day_PCT4_change'] < 0
                and regression_data['forecast_day_PCT5_change'] < 0
                and regression_data['forecast_day_PCT7_change'] < 0
                and regression_data['forecast_day_PCT10_change'] < 0
                )
            )
        and high_tail_pct(regression_data) > 0.9
        and (high_tail_pct(regression_data) >= low_tail_pct(regression_data))
        and (regression_data['monthLowChange'] < -2 or regression_data['monthHighChange'] < -10 or regression_data['month3HighChange'] < -10)
        and regression_data['month6LowChange'] > 0
        ):
        if(regression_data['PCT_day_change'] > 0
            and (high_tail_pct(regression_data) >= low_tail_pct(regression_data))
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%:sellDowntrend-lastDayUp-ReversalHighTail')
        elif(regression_data['PCT_day_change'] < 0
            and regression_data['PCT_day_change_pre1'] < -4
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%:sellDowntrend-lastDayDown-ReversalHighTail')
        flag = True

    if (-1 < regression_data['PCT_day_change'] < 2.5
        and -1 < regression_data['PCT_change'] < 2.5
        and regression_data['PCT_day_change_pre1'] < -3.5
        and abs(regression_data['PCT_day_change_pre1']) > 3 * abs(regression_data['PCT_day_change'])
        #and (regression_data['bar_high'] < regression_data['bar_high_pre1'] < regression_data['bar_high_pre2'])
        #and regression_data['forecast_day_PCT3_change'] < 0
        #and regression_data['forecast_day_PCT4_change'] < 0
        #and regression_data['forecast_day_PCT5_change'] < 0
        #and regression_data['forecast_day_PCT7_change'] < 0
        #and -15 < regression_data['forecast_day_PCT10_change'] < 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '%%:sellDownDojiPre1')
        return True
    elif (-1.5 < regression_data['PCT_day_change'] < 1.5
        and -1.5 < regression_data['PCT_change'] < 1.5
        and -1.5 < regression_data['PCT_day_change_pre1'] < 1.5
        and regression_data['PCT_day_change_pre2'] < -3
        and abs(regression_data['PCT_day_change_pre2']) > 3 * abs(regression_data['PCT_day_change'])
        and abs(regression_data['PCT_day_change_pre2']) > 3 * abs(regression_data['PCT_day_change_pre1'])
        #and (regression_data['bar_high'] < regression_data['bar_high_pre1'])
        and (regression_data['bar_high'] < regression_data['bar_high_pre2'])
        and regression_data['forecast_day_PCT3_change'] < 0
        and regression_data['forecast_day_PCT4_change'] < 0
        and regression_data['forecast_day_PCT5_change'] < 0
        and regression_data['forecast_day_PCT7_change'] < 0
        and -15 < regression_data['forecast_day_PCT10_change'] < 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '%%:sellDownDojiPre2')
        return True

    if((abs(regression_data['week2HighChange']) > 3 or abs(regression_data['week2LowChange']) > 3)
       and regression_data['monthHighChange'] < -10
       and (regression_data['PCT_day_change_pre1'] > 1.5
            or regression_data['PCT_day_change_pre2'] > 1.5
            or regression_data['PCT_day_change_pre3'] > 1.5
            or ( regression_data['PCT_day_change_pre1'] < 0 
                 and regression_data['PCT_day_change_pre2'] < 0
                 and high_tail_pct(regression_data) < abs(regression_data['PCT_day_change'])
                )
            )
        ):
        if(0 < regression_data['month3LowChange'] < 7
            and 0 < regression_data['monthLowChange'] < 7
            and 0 < regression_data['week2LowChange'] < 7
            and 0 < regression_data['weekLowChange'] < 2
            and regression_data['month3LowChange'] == regression_data['monthLowChange'] 
            and regression_data['week2LowChange'] == regression_data['weekLowChange']
            and regression_data['month3HighChange'] < -10
            and -3 < regression_data['PCT_day_change'] < 0
            and -5 < regression_data['PCT_change'] < 0
            ):
            if(regression_data['PCT_day_change_pre1'] > 0 
                and (regression_data['PCT_day_change_pre3'] > 0 or regression_data['PCT_day_change_pre4'] > 0)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuy:monthLow-alternateDayUp')
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkSell:monthLow')
            return True
        elif(0 < regression_data['month3LowChange'] < 2
            and 0 < regression_data['monthLowChange'] < 2
            and 0 < regression_data['week2LowChange'] < 2
            and 0 < regression_data['weekLowChange'] < 2
            and regression_data['month3LowChange'] == regression_data['monthLowChange'] 
            and regression_data['monthLowChange'] == regression_data['week2LowChange']
            and abs(regression_data['bar_low'] - regression_data['month3BarLow']) < 1
            and regression_data['month3HighChange'] < -10
            and -3 < regression_data['PCT_day_change'] < 0
            and -5 < regression_data['PCT_change'] < 0
            ):
            if(regression_data['PCT_day_change_pre1'] > 0 
                and (regression_data['PCT_day_change_pre3'] > 0 or regression_data['PCT_day_change_pre4'] > 0)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuy:01-monthLow-alternateDayUp')
            else:
                add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkSell:01-monthLow')
            return True
        elif(0 < regression_data['month3LowChange'] < 7
            and 0 < regression_data['monthLowChange'] < 7
            and 0 < regression_data['week2LowChange'] < 7
            and 0 < regression_data['weekLowChange'] < 7
            and regression_data['month3LowChange'] == regression_data['monthLowChange'] 
            and regression_data['monthLowChange'] == regression_data['week2LowChange']
            and regression_data['week2LowChange'] > regression_data['weekLowChange']
            and regression_data['month3HighChange'] < -10
            and -3 < regression_data['PCT_day_change'] < 0
            and -5 < regression_data['PCT_change'] < 0
            ):
            if(regression_data['PCT_day_change_pre1'] > 0 
                and (regression_data['PCT_day_change_pre3'] > 0 or regression_data['PCT_day_change_pre4'] > 0)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuy:02-monthLow-alternateDayUp')
            elif(regression_data['bar_low'] < regression_data['bar_low_pre2']):
                add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkSell:02-monthLow')
            return True
        elif(-2 < regression_data['forecast_day_PCT5_change'] < 2
            and regression_data['forecast_day_PCT2_change'] < regression_data['forecast_day_PCT_change'] < 0
            and (regression_data['forecast_day_PCT7_change'] < -10 or regression_data['forecast_day_PCT10_change'] < -10)
            and (regression_data['PCT_day_change_pre3'] < -4 or regression_data['PCT_day_change_pre4'] < -4)
            and (regression_data['PCT_day_change_pre2'] > 0 and regression_data['PCT_day_change_pre3'] > 0)
            and (regression_data['PCT_day_change'] < 0 and regression_data['PCT_day_change_pre1'] < 0)
            and regression_data['bar_low'] < regression_data['bar_low_pre2']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkSell:03-monthLow')
            return True
        elif(0 < regression_data['month3LowChange'] < 7
            and 0 < regression_data['monthLowChange'] < 7
            and 0 < regression_data['week2LowChange'] < 7
            and 0 < regression_data['weekLowChange'] < 7
            and (regression_data['month3LowChange'] == regression_data['monthLowChange'] 
                 or regression_data['monthLowChange'] == regression_data['week2LowChange']
                )
            and regression_data['week2LowChange'] == regression_data['weekLowChange']
            and regression_data['month3HighChange'] < -10
            and -3 < regression_data['PCT_day_change'] < 0
            and -5 < regression_data['PCT_change'] < 0
            ):
            if(regression_data['PCT_day_change_pre1'] > 0 
                and (regression_data['PCT_day_change_pre3'] > 0 or regression_data['PCT_day_change_pre4'] > 0)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuy:Super03-monthLow-alternateDayUp')
            elif(regression_data['bar_low'] < regression_data['bar_low_pre2']):
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSell:Super03-monthLow')
            return True

    if (regression_data['close'] > 150
        and regression_data['forecast_day_PCT5_change'] < -2
        and regression_data['forecast_day_PCT7_change'] < -2
        and regression_data['forecast_day_PCT10_change'] < -2
        and (regression_data['forecast_day_PCT10_change'] < regression_data['forecast_day_PCT7_change'] < regression_data['forecast_day_PCT5_change']
             or regression_data['forecast_day_PCT4_change'] < regression_data['forecast_day_PCT3_change'] < -3
            )
        and regression_data['year2LowChange'] > 5
        and regression_data['year2HighChange'] < -10
        and regression_data['month3HighChange'] < -10
        ):
        if(-1.5 < regression_data['PCT_day_change'] < 0.75
            and -1.5 < regression_data['PCT_change'] < 0.75
            and -1.5 < regression_data['PCT_day_change_pre1'] < 1
            and -1.5 < regression_data['PCT_change_pre1'] < 1
            and (-8 < regression_data['PCT_day_change_pre2'] < -3 or -8 < regression_data['PCT_day_change_pre3'] < -3)
            and (-8 < regression_data['PCT_change_pre2'] < -3 or -8 < regression_data['PCT_change_pre3'] < -3)
            and 0.5 > regression_data['forecast_day_PCT_change']
            and 0.5 > regression_data['forecast_day_PCT2_change']
            and 0.5 > regression_data['forecast_day_PCT3_change']
            and 0.5 > regression_data['forecast_day_PCT4_change']
            and (regression_data['forecast_day_PCT_change'] > -0.1
                 or regression_data['forecast_day_PCT2_change'] > -0.1
                 or regression_data['forecast_day_PCT3_change'] > -0.1
                )
            and (abs(regression_data['PCT_day_change_pre2']) > 2 * abs(regression_data['PCT_day_change'])
                 or abs(regression_data['PCT_day_change_pre3']) > 3 * abs(regression_data['PCT_day_change'])
            )
            and (regression_data['monthLowChange'] < 1 or regression_data['month3HighChange'] < -5)
            #and abs(regression_data['yearHighChange']) > abs(regression_data['yearLowChange'])
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkSellAtR1:Super000000000')
            flag = True
    elif (regression_data['close'] > 150
        #and regression_data['year2LowChange'] > 5
        and regression_data['year2HighChange'] < -10
        and regression_data['month3HighChange'] < -10
        ):
        if(-1.5 < regression_data['PCT_day_change'] < 0.75
            and -1.5 < regression_data['PCT_change'] < 0.75
            and (-7 < regression_data['PCT_day_change_pre1'] < -2.5 or -7 < regression_data['PCT_day_change_pre2'] < -2.5)
            and (-7 < regression_data['PCT_change_pre1'] < -2.5 or -7 < regression_data['PCT_change_pre2'] < -2.5)
            and (abs(regression_data['PCT_day_change_pre2']) > 3*abs(regression_data['PCT_day_change'])
                or abs(regression_data['PCT_day_change_pre3']) > 3*abs(regression_data['PCT_day_change'])
                )
            and regression_data['low'] < regression_data['low_pre1']
            and regression_data['low'] < regression_data['low_pre2']
            and regression_data['week2LowChange'] < 1
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkSell:SuperDoji')
            flag = True
    elif(regression_data['close'] > 50
        and regression_data['forecast_day_PCT7_change'] < 0
        and regression_data['forecast_day_PCT10_change'] < 0
        and high_tail_pct(regression_data) > regression_data['PCT_day_change']
        and low_tail_pct(regression_data) > regression_data['PCT_day_change']
        and regression_data['year2LowChange'] > 5
        and regression_data['year2HighChange'] < -15
        and regression_data['month3HighChange'] < -10 
        ):
        if(-3 < regression_data['PCT_day_change'] < 0.75
            and ((regression_data['PCT_day_change_pre1'] < -5 and low_tail_pct(regression_data) < 1.5)
                 or (regression_data['PCT_day_change_pre2'] < -5 and low_tail_pct(regression_data) < 1.5)
                )
            and 0 > regression_data['forecast_day_PCT_change']
            and 0 > regression_data['forecast_day_PCT2_change']
            and 0 > regression_data['forecast_day_PCT3_change']
            and 0 > regression_data['forecast_day_PCT4_change']
            
            #and regression_data['low'] > regression_data['low_pre1']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, '%%:checkSell:Super0') 
            flag = True
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
                add_in_csv(regression_data, regressionResult, ws, None, None, 'buyReversal-checkSellSuper3')
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
        and regression_data['low_pre1'] > regression_data['weekLow'] + 1
        and regression_data['low_pre2'] > regression_data['weekLow']
        ):
        if (0 < regression_data['PCT_day_change'] < 0.75
            and(regression_data['PCT_day_change_pre1'] < -2
                or regression_data['PCT_day_change_pre2'] < -2
                or regression_data['PCT_day_change_pre3'] < -2
                or regression_data['PCT_day_change_pre4'] < -2
                or regression_data['PCT_day_change_pre5'] < -2
               )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellFlagWeek-doji')
            flag = True
        elif(regression_data['PCT_day_change'] < -2 and regression_data['PCT_day_change'] < 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellFlagWeek')
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
        and regression_data['low_pre1'] > regression_data['week2Low'] + 2
        and regression_data['low_pre2'] > regression_data['week2Low']
        ):
        if (0 < regression_data['PCT_day_change'] < 0.75
            and regression_data['PCT_day_change_pre1'] > regression_data['PCT_day_change']
            and regression_data['PCT_day_change_pre2'] > 0
            and (regression_data['high'] > regression_data['high_pre1']
                 or regression_data['PCT_day_change_pre1'] > 1
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellFlag2Week-doji')
            flag = True 
        elif(-4 < regression_data['PCT_day_change'] < -2 and regression_data['PCT_change'] < 0
            and regression_data['PCT_day_change_pre1'] < 1.5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSellFlag2Week')
            flag = True 
    elif(regression_data['week2HighChange'] != regression_data['weekHighChange']
        and regression_data['week2LowChange'] <= regression_data['weekLowChange']
        and regression_data['weekHighChange'] < -1
        and regression_data['weekLowChange'] > 1
        and (regression_data['forecast_day_PCT2_change'] > -0.5
            or regression_data['forecast_day_PCT3_change'] > -0.5
            or regression_data['forecast_day_PCT4_change'] > -0.5
            )
        and regression_data['low_pre1'] > regression_data['weekLow'] + 1
        and regression_data['low_pre2'] > regression_data['weekLow']
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
        and regression_data['low_pre1'] > regression_data['week2Low'] + 2
        and regression_data['low_pre2'] > regression_data['week2Low']
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
                add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyContinueCupDownDoji-last2dayUp')
                flag = True
        elif(regression_data['weekHighChange'] > -2.5
            and abs(regression_data['PCT_day_change']) < 1
            and regression_data['week2HighChange'] == regression_data['weekHighChange']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyContinueCupDownDoji')
            flag = True
        elif(-2 < regression_data['PCT_day_change_pre1'] < -1 and -2 < regression_data['PCT_day_change_pre2'] < -1):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'chisBuyContinueCupDownDoji-last2dayUp')
            flag = True
            
    if( -7.5 < regression_data['PCT_day_change_pre1'] < -4.5 and -10 < regression_data['PCT_change_pre1'] < -3
        and (0 < regression_data['PCT_day_change'] < 1.5 and 0 < regression_data['PCT_change'] < 1.5)  
        and (regression_data['PCT_day_change_pre2'] > 0 or regression_data['PCT_day_change_pre3'] > 0)
        and (regression_data['PCT_day_change_pre3'] > 0 or regression_data['PCT_day_change_pre4'] > 0)
        and (regression_data['PCT_day_change_pre2'] > -3 and regression_data['PCT_day_change_pre3'] > -3)
        and regression_data['forecast_day_PCT3_change'] < 0
        and regression_data['forecast_day_PCT4_change'] < 0
        and regression_data['low'] < regression_data['low_pre1']
        and regression_data['high'] < regression_data['high_pre1']
        and regression_data['month3HighChange'] < -10
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'chisSelllastDayLT(-4.5)') 
        
    if(4 < regression_data['PCT_day_change'] < 7 and 4 < regression_data['PCT_day_change_pre1'] < 7
        and (5.5 < regression_data['PCT_day_change'] and 5.5 < regression_data['PCT_day_change_pre1'] and regression_data['PCT_day_change_pre2'] < 2)
        and regression_data['PCT_day_CH'] <= -1
        and (regression_data['month3LowChange'] > 10 or regression_data['month3LowChange'] < 0)
        and (regression_data['month3HighChange'] < -15 or regression_data['month3HighChange'] > 0)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'sellReversalLast2DayHighGT4')
        flag = True
    elif(2 < regression_data['PCT_day_change'] and 2 < regression_data['PCT_day_change_pre1'] < 7
        and (5.5 < regression_data['PCT_day_change'] and 5.5 < regression_data['PCT_day_change_pre1'] and (regression_data['PCT_day_change_pre2'] > 2 or regression_data['PCT_change_pre2'] > 2))
        and ((regression_data['PCT_day_CH'] >= -1 and regression_data['PCT_day_change'] < 7) or (regression_data['PCT_day_change'] > 7 and regression_data['PCT_day_CH'] < -2.5 and regression_data['PCT_day_change_pre3'] > 0))
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'buyContinueLast2DayHighGT4')
        flag = True
            
    return flag



def sell_market_downtrend(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    #return False
    
    if(-7 < regression_data['PCT_day_change'] < -3 and -7 < regression_data['PCT_day_change_pre1'] < -3 and -7 < regression_data['PCT_day_change_pre2'] < -3
        and (regression_data['PCT_change'] < -3 and regression_data['PCT_change_pre1'] < -3)
        ):
        if(regression_data['month3LowChange'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##last3DayLow(LT-3)-M3LLT0')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, '##last3DayLow(LT-3)-M3LGT0')
        flag = True
    elif(-7 < regression_data['PCT_day_change'] < -3 and -7 < regression_data['PCT_day_change_pre1'] < -3
        and (regression_data['PCT_change'] < -3)
        ):
        if(regression_data['month3LowChange'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##last2DayLow(LT-3)-M3LLT0')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, '##last2DayLow(LT-3)-M3LGT0')
        flag = True
    elif(-10 < regression_data['PCT_day_change_pre1'] < -5 and -5 < regression_data['PCT_day_change'] < -1
        and (3 < regression_data['PCT_change'])
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '##lastDayHigh(LT-5)Today(LT-1)')
        flag = True 
    
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
            add_in_csv(regression_data, regressionResult, ws, None, None, '##Month3Low-Continue(InUpTrend)')
            
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
            add_in_csv(regression_data, regressionResult, ws, None, None, '##:month3Low-InPlus')
            
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
            add_in_csv(regression_data, regressionResult, ws, None, None, '##:month6Low-InPlus')
                
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
            add_in_csv(regression_data, regressionResult, ws, None, None, '##:yearLow-InPlus')
                        
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
                    add_in_csv(regression_data, regressionResult, ws, None, None, '##:year2Low-InMinus')
                elif(regression_data['PCT_change'] < -2.5 and regression_data['PCT_day_change'] < -2.5
                    and ('NearLowYear2' in regression_data['filter3'])
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, None, '##:year2Low-InMinus')
                else:
                    add_in_csv(regression_data, regressionResult, ws, None, None, '##:year2Low-InMinus')
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
                    add_in_csv(regression_data, regressionResult, ws, None, None, '##:yearLow-InMinus')
                elif(regression_data['PCT_change'] < -2.5 and regression_data['PCT_day_change'] < -2.5
                    and ('NearLowYear' in regression_data['filter3'])
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, None, '##:yearLow-InMinus')
                else:
                    add_in_csv(regression_data, regressionResult, ws, None, None, '##:yearLow-InMinus')

def sell_downingMA(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, reg)
    
    if(regression_data['SMA4'] < 0
        and regression_data['SMA9'] < 0
        and regression_data['SMA25'] < 0
        and regression_data['SMA100'] < -10
        and regression_data['SMA200'] < -10
        and regression_data['year2HighChange'] > 5
        and regression_data['yearHighChange'] > 5
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, '##AllMANegative-Downtrend')
        return True
    
    if(regression_data['close'] > 50
        and regression_data['SMA4'] < 0
        and regression_data['SMA9'] < -5
        and regression_data['SMA25'] < -10
        and regression_data['year2LowChange'] > 5
        and (abs(regression_data['PCT_day_change']) > 1.5  
             or (-0.75 < regression_data['PCT_day_change'] < 0.75 and regression_data['PCT_day_change_pre1'] < -1.5
                 and abs(regression_data['PCT_day_change_pre1']) > 2*abs(regression_data['PCT_day_change'])
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
            add_in_csv(regression_data, regressionResult, ws, None, None, '##MANegative_Downtrend_(LT-4.5)')
        elif(regression_data['PCT_change'] < -1
            and -4.5 < regression_data['PCT_day_change'] < -2):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##MANegative_Downtrend_(LT-2)')
        elif(regression_data['PCT_change'] < 0
            and -2 < regression_data['PCT_day_change'] < -1):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##MANegative_Downtrend_(LT-1)')
        elif(-1.5 < regression_data['PCT_change'] < 1.5
            and -1 < regression_data['PCT_day_change'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##MANegative_Downtrend_(LT0)')
        elif(regression_data['PCT_change'] >3
            and regression_data['PCT_day_change'] > 4.5):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##MANegative_Downtrend_(GT4.5)')
        elif(regression_data['PCT_change'] > 1
            and 4.5 > regression_data['PCT_day_change'] > 2):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##MANegative_Downtrend_(GT2)')
        elif(regression_data['PCT_change'] > 0
            and 2 > regression_data['PCT_day_change'] > 1):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##MANegative_Downtrend_(GT1)')
        elif(-1.5 < regression_data['PCT_change'] < 1.5
            and 1 > regression_data['PCT_day_change'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##MANegative_Downtrend_(GT0)')
    
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
            add_in_csv(regression_data, regressionResult, ws, None, None, '##buyEMA6<EMA14')
        elif(regression_data['PCT_day_change'] < -3.5 or regression_data['PCT_change'] < -3.5):
            add_in_csv(regression_data, regressionResult, ws, None, None, '##buyEMA6<EMA14-Risky')
        
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
        add_in_csv(regression_data, regressionResult, ws, None, None, "##buySMAUpTrend")
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
        add_in_csv(regression_data, regressionResult, ws, None, None, "##buySMAUpTrend-2DayDown-weekLowTouch")
    return True


def sell_test(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, reg)
    regression_data['filter'] = ""
    flag = False
    
    return flag