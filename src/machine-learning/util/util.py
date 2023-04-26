import csv
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import Color, PatternFill, Font, Border
import json
from pymongo import MongoClient
from multiprocessing.dummy import Pool as ThreadPool

import math, time
from datetime import date
import datetime   
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np

from util.util_buy import *
from util.util_sell import *
from util.util_base import *

connection = MongoClient('localhost',27017)
db = connection.Nsedata
filterstsell = patterns_to_dict_st('../../data-import/nselist/sell_test_short_term_filter.csv')
filter3stsell = patterns_to_dict_st('../../data-import/nselist/sell_test_short_term_filter3.csv')
filter4stsell = patterns_to_dict_st('../../data-import/nselist/sell_test_short_term_filter4.csv')
filter345sell = patterns_to_dict('../../data-import/nselist/filter-345-sell.csv')
filtersell = patterns_to_dict('../../data-import/nselist/filter-sell.csv')
filterpctchangesell = patterns_to_dict('../../data-import/nselist/filter-pct-change-sell.csv')
filterallsell = patterns_to_dict('../../data-import/nselist/filter-all-sell.csv')
filtertechsell = patterns_to_dict('../../data-import/nselist/filter-tech-buy.csv')
filtertechallsell = patterns_to_dict('../../data-import/nselist/filter-tech-all-buy.csv')
filtertechallpctchangesell = patterns_to_dict('../../data-import/nselist/filter-tech-all-pct-change-buy.csv')
filterstbuy = patterns_to_dict_st('../../data-import/nselist/buy_test_short_term_filter.csv')
filter3stbuy = patterns_to_dict_st('../../data-import/nselist/buy_test_short_term_filter3.csv')
filter4stbuy = patterns_to_dict_st('../../data-import/nselist/buy_test_short_term_filter4.csv')
filter345buy = patterns_to_dict('../../data-import/nselist/filter-345-buy.csv')
filterbuy = patterns_to_dict('../../data-import/nselist/filter-buy.csv')
filterpctchangebuy = patterns_to_dict('../../data-import/nselist/filter-pct-change-buy.csv')
filterallbuy = patterns_to_dict('../../data-import/nselist/filter-all-buy.csv')
filtertechbuy = patterns_to_dict('../../data-import/nselist/filter-tech-buy.csv')
filtertechallbuy = patterns_to_dict('../../data-import/nselist/filter-tech-all-buy.csv')
filtertechallpctchangebuy = patterns_to_dict('../../data-import/nselist/filter-tech-all-pct-change-buy.csv')

def insert_scripdata_st(scrip, date, filter, avg5, pct5, avg10, pct10, count, regression_data):
    if (abs(pct5) > 70 and regression_data['industry'] != ''):
        data = {}
        data['scrip'] = scrip
        data['date'] = date
        data['filter'] = filter
        data['avg5'] = avg5
        data['pct5'] = pct5
        data['avg10'] = avg10
        data['pct10'] = pct10
        data['count'] = count
        json_data = json.loads(json.dumps(data))
        if (db.sttips.count_documents(json_data)) < 1:
            print(json_data)
            db.sttips.insert_one(json_data)


def insert_year2LowReversal(regression_data):
    if ((regression_data['year2HighChange'] < -50 and 'ReversalLowYear2' in regression_data['filter3']
            and regression_data['industry'] != '')
        or (regression_data['year2HighChange'] < -60
            and regression_data['industry'] != '' and regression_data['month3HighChange'] > -10 and regression_data['month3LowChange'] < 10)):
        data = {}
        data['scrip'] = regression_data['scrip']
        data['industry'] = regression_data['industry']
        data['date'] = regression_data['date']
        data['close'] = regression_data['close']
        data['year5HighChange'] = regression_data['year5HighChange']
        data['year2HighChange'] = regression_data['year2HighChange']
        data['year5LowChange'] = regression_data['year5LowChange']
        data['month3HighChange'] = regression_data['month3HighChange']
        data['month3LowChange'] = regression_data['month3LowChange']
        json_data = json.loads(json.dumps(data))
        if (db.reversalY2LLT60.count_documents({'scrip':data['scrip']})) < 1 and regression_data['year2HighChange'] < -60:
            db.reversalY2LLT60.insert_one(json_data)
        elif (db.reversalY2LLT50.count_documents({'scrip':data['scrip']})) < 1 and regression_data['year2HighChange'] < -50:
            db.reversalY2LLT50.insert_one(json_data)


    
def insert_year5LowBreakoutY2H(regression_data):
    if (regression_data['year2HighChange'] > -5 and regression_data['year2LowChange'] > 30 and regression_data['year5HighChange'] < -50):
        data = {}
        data['scrip'] = regression_data['scrip']
        data['industry'] = regression_data['industry']
        data['date'] = regression_data['date']
        data['close'] = regression_data['close']
        data['year5HighChange'] = regression_data['year5HighChange']
        data['year2HighChange'] = regression_data['year2HighChange']
        data['year5LowChange'] = regression_data['year5LowChange']
        json_data = json.loads(json.dumps(data))
        if ((db.breakoutY2H.count_documents({'scrip': data['scrip']})) < 1 and (db.breakoutYH.count_documents({'scrip': data['scrip']})) < 1):
            db.breakoutY2H.insert_one(json_data)
        return True

def insert_year5LowBreakoutYH(regression_data):
    if (regression_data['yearHighChange'] > -5 and regression_data['yearLowChange'] > 20 and regression_data['year5HighChange'] < -70):
        data = {}
        data['scrip'] = regression_data['scrip']
        data['industry'] = regression_data['industry']
        data['date'] = regression_data['date']
        data['close'] = regression_data['close']
        data['year5HighChange'] = regression_data['year5HighChange']
        data['year2HighChange'] = regression_data['year2HighChange']
        data['year5LowChange'] = regression_data['year5LowChange']
        json_data = json.loads(json.dumps(data))
        if ((db.breakoutY2H.count_documents({'scrip': data['scrip']})) < 1 and (db.breakoutYH.count_documents({'scrip': data['scrip']})) < 1):
            db.breakoutYH.insert_one(json_data)
        return True

def insert_year2HighNearBreakout(regression_data):
    if (regression_data['year2HighChange'] > -5 and regression_data['year2LowChange'] > 30  and regression_data['year5HighChange'] > -10 and regression_data['industry'] != ''):
        data = {}
        data['scrip'] = regression_data['scrip']
        data['industry'] = regression_data['industry']
        data['date'] = regression_data['date']
        data['close'] = regression_data['close']
        data['year5HighChange'] = regression_data['year5HighChange']
        data['year2HighChange'] = regression_data['year2HighChange']
        data['year5LowChange'] = regression_data['year5LowChange']
        json_data = json.loads(json.dumps(data))
        if (db.nearY2H.count_documents({'scrip': data['scrip']})) < 1:
            db.nearY2H.insert_one(json_data)


def buy_all_rule(regression_data, regressionResult, buyIndiaAvg, ws):
    if(high_tail_pct(regression_data) < 1.5):
        if(regression_data['PCT_day_change'] > 2 and regression_data['PCT_day_change_pre1'] > 2 and regression_data['PCT_day_change_pre2'] > 2):
            add_in_csv(regression_data, regressionResult, ws, 'Last3DayGT2')
        elif(regression_data['PCT_day_change'] > 2 and regression_data['PCT_day_change_pre1'] > 2 and regression_data['PCT_day_change_pre2'] > 0):
            add_in_csv(regression_data, regressionResult, ws, 'Last2DayGT2-3rdDayGT0')
        elif(regression_data['PCT_day_change'] > 2 and regression_data['PCT_day_change_pre1'] > 2 and regression_data['PCT_day_change_pre2'] < 0):
            add_in_csv(regression_data, regressionResult, ws, 'Last2DayGT2')
        elif(regression_data['PCT_day_change'] > 2 and regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change_pre2'] < 0):
            add_in_csv(regression_data, regressionResult, ws, 'Last1DayGT2-2ndDayGT0')
        elif(regression_data['PCT_day_change'] > 2 and regression_data['PCT_day_change_pre1'] < 0):
            add_in_csv(regression_data, regressionResult, ws, 'Last1DayGT2')
        else:
            if(high_tail_pct(regression_data) < regression_data['PCT_day_change'] or high_tail_pct(regression_data) < regression_data['PCT_change']):
                if(regression_data['PCT_day_change'] >= 1 and regression_data['PCT_day_change_pre1'] >= 1 and regression_data['PCT_day_change_pre2'] >= 1):
                    add_in_csv(regression_data, regressionResult, ws, 'Last3DayGT1')
                elif(regression_data['PCT_day_change'] >= 1 and regression_data['PCT_day_change_pre1'] >= 1 and regression_data['PCT_day_change_pre2'] > 0):
                    add_in_csv(regression_data, regressionResult, ws, 'Last2DayGT1-3rdDayGT0')
                elif(regression_data['PCT_day_change'] >= 1 and regression_data['PCT_day_change_pre1'] >= 1 and regression_data['PCT_day_change_pre2'] < 0):
                    add_in_csv(regression_data, regressionResult, ws, 'Last2DayGT1')
                elif(regression_data['PCT_day_change'] >= 1 and 0 < regression_data['PCT_day_change_pre1'] < 1 and regression_data['PCT_day_change_pre2'] < 0 and regression_data['PCT_day_change_pre3'] > 0):
                    add_in_csv(regression_data, regressionResult, ws, 'Last1DayGT1-2ndDayDojiGT0-3rdDayLT0:MayBuyUptrend-SellDownTrend')
                elif(regression_data['PCT_day_change'] >= 1 
                    and (0 < regression_data['PCT_day_change_pre1'] < 1 or (0 < regression_data['PCT_day_change_pre1'] and 2*abs(regression_data['PCT_day_change_pre1']) < abs(regression_data['PCT_day_change_pre2'])))
                    and regression_data['PCT_day_change_pre2'] > 0
                    and regression_data['PCT_day_change_pre3'] < 0.5
                    ):
                    if(abs(regression_data['monthHighChange']) < abs(regression_data['monthLowChange'])):
                        add_in_csv(regression_data, regressionResult, ws, 'Last1DayGT1-2ndDayDojiGT0-3rdDayGT0:MayBuy')
                    elif(abs(regression_data['monthHighChange']) > abs(regression_data['monthLowChange'])):
                        add_in_csv(regression_data, regressionResult, ws, 'Last1DayGT1-2ndDayDojiGT0-3rdDayGT0:MaySell')
                elif(regression_data['PCT_day_change'] >= 1 
                    and (regression_data['PCT_day_change_pre1'] < 0 and 2*abs(regression_data['PCT_day_change_pre1']) < abs(regression_data['PCT_day_change_pre2']))
                    and regression_data['PCT_day_change_pre2'] > 0
                    and regression_data['PCT_day_change_pre3'] < 0.5
                    ):
                    add_in_csv(regression_data, regressionResult, ws, 'Last1DayGT1-2ndDayDojiLT0-3rdDayGT0:MayBuyUptrend-SellDownTrend')
                elif(regression_data['PCT_day_change'] >= 1 and regression_data['PCT_day_change_pre1'] < 0):
                    add_in_csv(regression_data, regressionResult, ws, 'Last1DayGT1')
    
        if(regression_data['PCT_day_change'] >= 1 
            and -1 < regression_data['PCT_day_change_pre1'] < 0
            and 0 < regression_data['PCT_day_change_pre2'] < 1
            and regression_data['PCT_day_change_pre3'] > 1
            and regression_data['bar_high'] > regression_data['bar_high_pre3'] > regression_data['bar_high_pre1'] 
            and regression_data['bar_high'] > regression_data['bar_high_pre3'] > regression_data['bar_high_pre2']
            and regression_data['month3HighChange'] < -1
            ):
            add_in_csv(regression_data, regressionResult, ws, None, 'DojiLastDayGT2Today')            
    
    if(regression_data['PCT_day_change'] >= 1.5 and regression_data['PCT_change'] >= 1.5
        and high_tail_pct(regression_data) <= 1
        ):
        if(regression_data['month3HighChange'] < 1
            and regression_data['monthHighChange'] < 1
            and regression_data['week2HighChange'] < 1
            ):
            add_in_csv(regression_data, regressionResult, ws, 'CheckSmoothMA-LTMonth3High')
        elif(regression_data['month3HighChange'] > 1
            and regression_data['monthHighChange'] > 1
            and regression_data['week2HighChange'] > 1
            ):
            add_in_csv(regression_data, regressionResult, ws, 'CheckSmoothMA-GTMonth3High')
        if(regression_data['month3HighChange'] < 1
            and regression_data['monthHighChange'] < 1
            ):
            add_in_csv(regression_data, regressionResult, ws, 'CheckSmoothMA-LTMonth3High')
        elif(regression_data['month3HighChange'] > 1
            and regression_data['monthHighChange'] > 1
            ):
            add_in_csv(regression_data, regressionResult, ws, 'CheckSmoothMA-GTMonth3High')
    
    if( 0 < regression_data['PCT_day_change'] < 0.5
        and 0 < regression_data['PCT_change'] < 0.5
        and 2 < regression_data['PCT_day_change_pre1'] < 7
        and (regression_data['PCT_day_change_pre3'] < 0 or regression_data['PCT_day_change_pre4'] < 0)
        and regression_data['bar_high'] > regression_data['bar_high_pre2']
        and (high_tail_pct(regression_data) < 1.5 and low_tail_pct(regression_data) < 1.5)
        ):
        add_in_csv(regression_data, regressionResult, ws, 'DojiTodayGT2LastDay')
    
    if('DOJI' in regression_data['filter5']
        #and regression_data['forecast_day_PCT7_change'] > 0
        and regression_data['forecast_day_PCT10_change'] >= 2
        and (regression_data['PCT_day_change'] < 0
            or (regression_data['forecast_day_PCT_change'] < 0
                and regression_data['forecast_day_PCT2_change'] < 0
                )
            )
        and (high_tail_pct(regression_data) < 4.0 and low_tail_pct(regression_data) < 4.0)
        ):
        add_in_csv(regression_data, regressionResult, ws, 'Buy-LastDayNiftyMidCapDown(LT-1)-TodayUpMorningNiftyGT0.5')
    
           
    if(is_algo_buy(regression_data)):    
        if(-15 < regression_data['PCT_day_change'] < -3.5 and -15 < regression_data['PCT_change'] < -3.5):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'AFML:BuyPCTDayChangeLT-3.5')
        elif(regression_data['week2HighChange'] < -20 and regression_data['weekHighChange'] < -10
            and 5 > regression_data['PCT_day_change'] > 2
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'AFML:(NOT-DOWNTREND)0-mlBuyWeek2HighLT-20')
#         elif(regression_data['week2HighChange'] < -10 and regression_data['weekHighChange'] < -10
#             and (regression_data['week2HighChange'] < -15 or regression_data['weekHighChange'] < -15)
#             and 4 > regression_data['PCT_day_change'] > 0
#             and is_any_sell_LTMinus2_from_all_filter_(regression_data) == False
#             ):
#             add_in_csv(regression_data, regressionResult, ws, None, None, 'AF:1-mlBuyWeek2HighLT-10')
#         elif(regression_data['week2HighChange'] < -5 and regression_data['weekHighChange'] < -10
#             and 5 > regression_data['PCT_day_change'] > 2
#             and is_any_sell_LTMinus2_from_all_filter_(regression_data) == False
#             ):
#             add_in_csv(regression_data, regressionResult, ws, None, None, 'AF:1-mlBuyWeekHighLT-10')    
        if('NearLow' in regression_data['filter3']
            and'GT0' in regression_data['filter3']
            and regression_data['PCT_day_change'] < 0 and regression_data['PCT_change'] < 1
            and regression_data['forecast_day_PCT_change'] < regression_data['forecast_day_PCT2_change'] < regression_data['forecast_day_PCT3_change']
            and regression_data['forecast_day_PCT_change'] < 0
            and regression_data['forecast_day_PCT2_change'] < 0
            and regression_data['forecast_day_PCT3_change'] < 0
            and regression_data['forecast_day_PCT4_change'] < 0
            and regression_data['forecast_day_PCT5_change'] < 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'AFML:(UPTRENDMARKET)buyNearLowBaseReversal')
        if((regression_data['yearHighChange'] < -5) and ('BreakHighMonth6' in regression_data['filter3'])
            and'GT0' in regression_data['filter3']
            and regression_data['PCT_day_change'] < 0 and regression_data['PCT_change'] < 1
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'AFML:(UPTRENDMARKET)buyBreakHighBaseContinue')
        if(regression_data['monthHighChange'] < -0.5
            and regression_data['monthLow'] != regression_data['week2Low'] 
            and regression_data['monthLowChange'] > 7 
            and 1 < regression_data['PCT_day_change'] < 4 and 1 < regression_data['PCT_change'] < 5
            and regression_data['PCT_day_change'] > regression_data['PCT_day_change_pre1']
            and regression_data['PCT_day_change_pre1'] > 0
            and regression_data['PCT_day_change_pre2'] > 0
            and high_tail_pct(regression_data) < 1
            and low_tail_pct(regression_data) < 1
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'AFML:(UPTRENDMARKET)buyContinueLessThanMonthHigh')
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
        and ((last_7_day_all_up(regression_data) == False) or (regression_data['forecast_day_PCT10_change'] < 10))
        and (MARKET_IN_UPTREND or (last_4_day_all_up(regression_data) == False)) #Uncomment0 If very less data
        and breakout_or_no_consolidation(regression_data) == True
        and '(Confirmed)EMA6>EMA14' not in regression_data['filter4']
        and regression_data['close'] > 50
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None)
        return True
    return False

def buy_all_common(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, True)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, True)
    mlpValue_cla, kNeighboursValue_cla = get_reg_or_cla(regression_data, False)
    mlpValue_other_cla, kNeighboursValue_other_cla = get_reg_or_cla_other(regression_data, False)
                
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
        and 'sell' not in regression_data['filter']
        and 'Sell' not in regression_data['filter']
        ):    
        if(regression_data['SMA9'] > 1):
            add_in_csv(regression_data, regressionResult, ws, 'Common:buyNotM3HighLow-0(SMA9GT1)')
        elif(regression_data['SMA25'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None)  
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None)
             
    return False

def buy_all_common_High_Low(regression_data, regressionResult, reg, ws):
    if(((regression_data['forecast_day_PCT_change'] > 0.5 and regression_data['forecast_day_PCT2_change'] > regression_data['forecast_day_PCT_change'])
        or (regression_data['forecast_day_PCT3_change'] > 0 and regression_data['forecast_day_PCT4_change'] > 0)
        or regression_data['forecast_day_PCT5_change'] > 0
        or regression_data['forecast_day_PCT7_change'] > 0
        or regression_data['forecast_day_PCT10_change'] > 0
        )
        and(regression_data['month3HighChange'] > 0
            or (regression_data['monthHighChange'] > 0 and regression_data['month3HighChange'] < 0
                and regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change_pre2'] > 0
                )
            or abs(regression_data['week2HighChange']) > abs(regression_data['week2LowChange'])
            or (regression_data['week2HighChange'] < -2
                and regression_data['week2LowChange'] > 0
                and abs(regression_data['week2HighChange']) < abs(regression_data['week2LowChange'])
                and (abs(regression_data['monthHighChange']) < (regression_data['monthLowChange'])
                    or abs(regression_data['month3HighChange']) < abs(regression_data['month3LowChange'])
                    )
                )
            or (regression_data['monthHighChange'] < -2
                and regression_data['monthLowChange'] > 0
                and abs(regression_data['monthHighChange']) < abs(regression_data['monthLowChange'])
                and (abs(regression_data['month3HighChange']) < (regression_data['month3LowChange'])
                    or abs(regression_data['month6HighChange']) < abs(regression_data['month6LowChange'])
                    )
                )
            )
        and 'sell' not in regression_data['filter']
        and 'Sell' not in regression_data['filter']
        ):
#         if(2 < low_tail_pct_pre1(regression_data) < 6 and 2.9 < regression_data['PCT_day_change'] < 4.1
#             and regression_data['PCT_day_change_pre1'] > -1.3 
#             and abs(regression_data['PCT_day_change_pre1']) < 1.5
#             and regression_data['PCT_day_change_pre2'] < -1
#             and abs(regression_data['PCT_day_change_pre2']) > abs(regression_data['PCT_day_change_pre1'])
#             #and regression_data['high'] >= regression_data['bar_high_pre2']
#             #and abs_month6High_less_than_month6Low(regression_data)
#             and low_tail_pct(regression_data) < 1.5
#             and high_tail_pct(regression_data) < 1.5
#             ):
        if( 2.9 < regression_data['PCT_day_change'] < 4.1 and 3 < regression_data['PCT_change'] < 4.5
            and -0.75 < regression_data['PCT_day_change_pre1'] < 4
            and regression_data['PCT_day_change_pre2'] < 4
            and (regression_data['PCT_day_change_pre1'] > 0.5
                 or regression_data['PCT_day_change_pre2'] > 0.5
                 or regression_data['PCT_day_change_pre3'] > 0.5
                )
            and ((regression_data['PCT_day_change_pre1'] < 0 and regression_data['PCT_day_change_pre2'] < 0 and regression_data['PCT_day_change_pre3'] < 0)
                 or (regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change_pre2'] < 0 and regression_data['PCT_day_change_pre3'] < 0)
                 or (regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change_pre2'] > 0 and regression_data['PCT_day_change_pre3'] < 0 and regression_data['month3HighChange'] > 0)
                 or (regression_data['PCT_day_change_pre1'] < 0 and regression_data['PCT_day_change_pre2'] > 0 and regression_data['PCT_day_change_pre3'] > -1 and regression_data['month3HighChange'] > 0)
                 or (regression_data['monthHighChange'] < -2 and regression_data['monthLowChange'] > 0)
                )
            and high_tail_pct(regression_data) < 1.29
            and low_tail_pct(regression_data) < 2.5
            ):
            add_in_csv(regression_data, regressionResult, ws, 'CommonHL:HighUptrend')
        elif(2.7 < regression_data['PCT_day_change'] < 5.5
            and 3 < regression_data['PCT_change'] 
            and regression_data['PCT_day_change_pre1'] > -1.3
            and (regression_data['PCT_day_change_pre2'] > -1.3 
                 or (regression_data['PCT_day_change_pre1'] > 0 
                     and regression_data['PCT_day_change_pre3'] > 0
                     and regression_data['low_pre2'] > regression_data['low_pre3'] 
                     and regression_data['high_pre2'] > regression_data['high_pre3']
                     )
                 )
            and (regression_data['PCT_day_change_pre1'] < 1
                 or regression_data['PCT_day_change_pre2'] < 1
                 or regression_data['PCT_day_change_pre3'] < 1
                )
            and ((regression_data['PCT_day_change_pre1'] < 0 and regression_data['PCT_day_change_pre2'] < 0 and regression_data['PCT_day_change_pre3'] < 0)
                 or (regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change_pre2'] < 0 and regression_data['PCT_day_change_pre3'] < 0)
                 or (regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change_pre2'] > 0 and regression_data['PCT_day_change_pre3'] < 0 and regression_data['month3HighChange'] > 0)
                 or (regression_data['PCT_day_change_pre1'] < 0 and regression_data['PCT_day_change_pre2'] > 0 and regression_data['PCT_day_change_pre3'] > -1 and regression_data['month3HighChange'] > 0)
                 or (regression_data['monthHighChange'] < -2 and regression_data['monthLowChange'] > 0)
                )
            and regression_data['forecast_day_PCT4_change'] > 0
            and regression_data['forecast_day_PCT5_change'] > 0
            and regression_data['SMA4'] > 2
            and regression_data['SMA9'] > 2
            and high_tail_pct(regression_data) < 2.5
            and low_tail_pct(regression_data) < 2.5
            and low_tail_pct_pre1(regression_data) < 2.5
            ):
            if(regression_data['PCT_day_change'] < 2.95
                or (regression_data['PCT_day_change_pre1'] < 0
                    or regression_data['PCT_day_change_pre2'] < 0
                    or regression_data['PCT_day_change_pre3'] < 0
                    )
                ):
                add_in_csv(regression_data, regressionResult, ws, 'CommonHL:HEAVYUPTRENDMARKET:HighUptrend')
            elif(regression_data['PCT_day_change_pre1'] > 0
                or regression_data['PCT_day_change_pre2'] > 0
                or regression_data['PCT_day_change_pre3'] > 0
                ):
                add_in_csv(regression_data, regressionResult, ws, 'CommonHL:HEAVYUPTRENDMARKET:HighUptrend-(UPTREND-GLOBALUP)')
        if( 4 < regression_data['PCT_day_change'] < 8 and 3 < regression_data['PCT_change'] < 10
            and (5 < regression_data['PCT_day_change'] or 5 < regression_data['PCT_change'])  
            and -0.75 < regression_data['PCT_day_change_pre1'] < 4
            and regression_data['PCT_day_change_pre2'] < 4
            and (regression_data['PCT_day_change_pre1'] < 0 or regression_data['PCT_day_change_pre2'] < 0 or regression_data['PCT_day_change_pre3'] < 0)
            and (regression_data['PCT_day_change_pre1'] < 0.75 or regression_data['PCT_day_change_pre2'] < 0.75)
            and (regression_data['PCT_day_change_pre2'] < 0.75 or regression_data['PCT_day_change_pre3'] < 0.75)
            and high_tail_pct(regression_data) < abs(regression_data['PCT_day_change'])/3
            and low_tail_pct(regression_data) < 2.5
            ):
            if(regression_data['PCT_day_change_pre1'] < 0): 
                add_in_csv(regression_data, regressionResult, ws, 'CommonHL(9:30):HighUptrend-2')
            else:
                add_in_csv(regression_data, regressionResult, ws, 'CommonHL:HighUptrend-2')
        
    buy_common_up_continued(regression_data, regressionResult, reg, ws)
         
    if((2 < regression_data['PCT_day_change'] < 3.25) and (1.5 < regression_data['PCT_change'] < 3.25)
        and regression_data['bar_high'] > regression_data['bar_high_pre1']
        ):
        if(regression_data['high_pre1'] < regression_data['high_pre2'] < regression_data['high_pre3']):
            add_in_csv(regression_data, regressionResult, ws, None, None, None)
        elif(regression_data['year2HighChange'] < -40
            and regression_data['yearHighChange'] < -30
            and (regression_data['PCT_day_change_pre1'] < 0 or regression_data['PCT_day_change_pre2'] < -2)
            and ((regression_data['PCT_day_change_pre1'] > 0 or regression_data['PCT_day_change_pre2'] > -2)
                 or regression_data['high_pre1'] > regression_data['high_pre2'] > regression_data['high_pre3']
                )
            and regression_data['SMA25'] < 0
            and regression_data['SMA50'] < 0
            and regression_data['SMA100'] < 0
            #and regression_data['high_pre1'] > regression_data['high_pre5']
            ):   
            add_in_csv(regression_data, regressionResult, ws, None, None, 'buyYear2LowLT-50(triggerAfter-9:15)')    
    
    if(2.5 < regression_data['PCT_day_change'] < 3 and 2.5 < regression_data['PCT_change'] < 5
        and -2 < regression_data['PCT_day_change_pre1'] < 1
        and -2 < regression_data['PCT_day_change_pre2'] < 1
        and (regression_data['week2LowChange'] > 2 or regression_data['weekLowChange'] > 2)
        and low_tail_pct(regression_data) < 2.5
        and high_tail_pct(regression_data) < 2
        ):
        add_in_csv(regression_data, regressionResult, ws, 'CommonHL:UpTrendLast2Day-GlobalUp-GlobalFutureUp-NiftyUp')
    elif(1.5 < regression_data['PCT_day_change'] < 2 and 3 < regression_data['PCT_change'] < 4
        and (regression_data['PCT_change'] - regression_data['PCT_day_change']) > 1.5
        and low_tail_pct(regression_data) < 2.5
        and high_tail_pct(regression_data) < 1.3
        ):
        add_in_csv(regression_data, regressionResult, ws, 'CommonHL:LastDay-PCTDayChange-GT2-PCTChange')
    elif(2 < regression_data['PCT_day_change'] < 3 and 4 < regression_data['PCT_change'] < 5
        and (regression_data['PCT_change'] - regression_data['PCT_day_change']) > 1.5
        and low_tail_pct(regression_data) < 2.5
        and high_tail_pct(regression_data) < 1.3
        ):
        add_in_csv(regression_data, regressionResult, ws, 'CommonHL:LastDay-PCTDayChange-GT3-PCTChange')
              
def buy_other_indicator(regression_data, regressionResult, reg, ws):
    tail_pct_filter(regression_data, regressionResult)
    base_line(regression_data, regressionResult, reg, ws)
    filterMA(regression_data, regressionResult)
    tail_reversal_filter(regression_data, regressionResult)
    
    sell_market_downtrend(regression_data, regressionResult, reg, ws)
    sell_check_chart(regression_data, regressionResult, reg, ws)
    sell_downingMA(regression_data, regressionResult, reg, ws)
    sell_study_downingMA(regression_data, regressionResult, reg, ws)
    
    buy_market_uptrend(regression_data, regressionResult, reg, ws)
    buy_month3_high_continue(regression_data, regressionResult, reg, ws)
    buy_risingMA(regression_data, regressionResult, reg, ws)
    buy_study_risingMA(regression_data, regressionResult, reg, ws)
    buy_check_chart(regression_data, regressionResult, reg, ws)
    
    buy_high_volatility(regression_data, regressionResult)
    if(regression_data['close'] > 50):
        sell_up_trend(regression_data, regressionResult, reg, ws)
        sell_down_trend(regression_data, regressionResult, reg, ws)
        sell_final(regression_data, regressionResult, reg, ws, ws)
        sell_morning_star_buy(regression_data, regressionResult, reg, ws)
        sell_evening_star_sell(regression_data, regressionResult, reg, ws)
        sell_day_high(regression_data, regressionResult, reg, ws)
        sell_trend_reversal(regression_data, regressionResult, reg, ws)
        sell_trend_break(regression_data, regressionResult, reg, ws)
        sell_consolidation_breakdown(regression_data, regressionResult, reg, ws)
        sell_final_candidate(regression_data, regressionResult, reg, ws)
        sell_oi(regression_data, regressionResult, reg, ws)
        sell_heavy_downtrend(regression_data, regressionResult, reg, ws)
        sell_tail_reversal_filter(regression_data, regressionResult, reg, ws)
        
        buy_year_high(regression_data, regressionResult, reg, ws)
        buy_year_low(regression_data, regressionResult, reg, ws, ws)
        buy_down_trend(regression_data, regressionResult, reg, ws)
        buy_final(regression_data, regressionResult, reg, ws, ws)
        buy_morning_star_buy(regression_data, regressionResult, reg, ws)
        buy_evening_star_sell(regression_data, regressionResult, reg, ws)
        buy_day_low(regression_data, regressionResult, reg, ws)
        buy_trend_reversal(regression_data, regressionResult, reg, ws)
        buy_trend_break(regression_data, regressionResult, reg, ws)
        buy_final_candidate(regression_data, regressionResult, reg, ws)
        buy_oi(regression_data, regressionResult, reg, ws)
        buy_up_trend(regression_data, regressionResult, reg, ws)
        buy_heavy_uptrend_reversal(regression_data, regressionResult, reg, ws)
        buy_tail_reversal_filter(regression_data, regressionResult, reg, ws)
        buy_hltf_low_tail(regression_data, regressionResult, reg, ws)
        
        buy_check_cup_filter(regression_data, regressionResult, reg, ws)
        buy_consolidation_breakout(regression_data, regressionResult, reg, ws)
        buy_supertrend(regression_data, regressionResult, reg, ws)
        return True
    if(buy_skip_close_lt_50(regression_data, regressionResult, reg, ws)):
        return True
    return False

def buy_indicator_after_filter_accuracy(regression_data, regressionResult, reg, ws):
    return False
            
def buy_skip_close_lt_50(regression_data, regressionResult, reg, ws):
    return False

def test_short_term_filter(regression_data, regressionResult, reg, ws):
    regression_data['filterbuy'] = " "
    regression_data['filtersell'] = " "
    regression_data['filter'] = " "
    regression_data['filter1'] = " "
    regression_data['filter2'] = " "
    regression_data['filter3'] = " "
    regression_data['filter4'] = " "
    regression_data['filter5'] = " "
    regression_data['filter6'] = " "
    regression_data['series_trend'] = trend_calculator(regression_data)
    flag = buy_other_indicator(regression_data, regressionResult, reg, ws)
    filterName = pct_change_filter(regression_data, regressionResult, False)
    filterNameTail = tail_change_filter(regression_data, regressionResult, False)
    pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
    regression_data['filterTest'] = regression_data['filter'] + ',' + regression_data['filter1']
    if (regression_data['filterTest'] == ',' or regression_data['filterTest'] == ' , '):
        return False
    return True

def test_short_term_filter3(regression_data, regressionResult, reg, ws):
    regression_data['filterbuy'] = " "
    regression_data['filtersell'] = " "
    regression_data['filter'] = " "
    regression_data['filter1'] = " "
    regression_data['filter2'] = " "
    regression_data['filter3'] = " "
    regression_data['filter4'] = " "
    regression_data['filter5'] = " "
    regression_data['filter6'] = " "
    regression_data['series_trend'] = trend_calculator(regression_data)
    flag = buy_other_indicator(regression_data, regressionResult, reg, ws)
    filterName = pct_change_filter(regression_data, regressionResult, False)
    filterNameTail = tail_change_filter(regression_data, regressionResult, False)
    pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
    regression_data['filterTest'] = regression_data['filter'] + ',' + regression_data['filter3']
    if(regression_data['filterTest'] == ',' or regression_data['filterTest'] == ' , '):
        return False
    return True

def buy_test_345(regression_data, regressionResult, reg, ws):
    regression_data['filterbuy'] = " "
    regression_data['filtersell'] = " "
    regression_data['filter'] = " "
    regression_data['filter1'] = " "
    regression_data['filter2'] = " "
    regression_data['filter3'] = " "
    regression_data['filter4'] = " "
    regression_data['filter5'] = " "
    regression_data['filter6'] = " "
    regression_data['series_trend'] = trend_calculator(regression_data)
    flag = buy_other_indicator(regression_data, regressionResult, reg, ws)
    filterName = pct_change_filter(regression_data, regressionResult, False)
    filterNameTail = tail_change_filter(regression_data, regressionResult, False)
    pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
    regression_data['filterTest'] = filterName + ',' \
                                    + filterNameTail + ',' \
                                    + pctChange5Day + ',' \
                                    + regression_data['series_trend'] + ',' \
                                    + regression_data['filter1'] + ',' \
                                    + regression_data['filter3']
    
    if regression_data['filterTest'] != '':
        return True  
    
    return False
  
def buy_test(regression_data, regressionResult, reg, ws):
    regression_data['filterbuy'] = " "
    regression_data['filtersell'] = " "
    regression_data['filter'] = " "
    regression_data['filter1'] = " "
    regression_data['filter2'] = " "
    regression_data['filter3'] = " "
    regression_data['filter4'] = " "
    regression_data['filter5'] = " "
    regression_data['filter6'] = " "
    regression_data['series_trend'] = trend_calculator(regression_data)
    flag = buy_other_indicator(regression_data, regressionResult, reg, ws)
    filterName = pct_change_filter(regression_data, regressionResult, False)
    filterNameTail = tail_change_filter(regression_data, regressionResult, False)
    pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
    regression_data['filterTest'] = filterName + ',' \
                                    + filterNameTail + ',' \
                                    + pctChange5Day + ',' \
                                    + regression_data['series_trend'] + ',' \
                                    + regression_data['filter2'] + ',' \
                                    + regression_data['filter4'] + ',' \
                                    + regression_data['filter5']
                                    
    
    if regression_data['filterTest'] != '':
        return True  
    
    return False

def buy_test_pct_change(regression_data, regressionResult, reg, ws):
    regression_data['filterbuy'] = " "
    regression_data['filtersell'] = " "
    regression_data['filter'] = " "
    regression_data['filter1'] = " "
    regression_data['filter2'] = " "
    regression_data['filter3'] = " "
    regression_data['filter4'] = " "
    regression_data['filter5'] = " "
    regression_data['filter6'] = " "
    regression_data['series_trend'] = trend_calculator(regression_data)
    flag = buy_other_indicator(regression_data, regressionResult, reg, ws)
    filtercombine = regression_data['filterbuy'].strip() + ',' \
            + regression_data['filtersell'].strip() + ',' \
            + regression_data['filter'].strip()
    if filtercombine != ",,":
        filterName = pct_change_filter(regression_data, regressionResult, False)
        filterNameTail = tail_change_filter(regression_data, regressionResult, False)
        pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
        regression_data['filterTest'] = filterName + ',' \
                                        + filterNameTail + ',' \
                                        + filtercombine 
    
    if regression_data['filterTest'] != '':
        return True
    
    return False  

def buy_test_all(regression_data, regressionResult, reg, ws):
    regression_data['filterbuy'] = " "
    regression_data['filtersell'] = " "
    regression_data['filter'] = " "
    regression_data['filter1'] = " "
    regression_data['filter2'] = " "
    regression_data['filter3'] = " "
    regression_data['filter4'] = " "
    regression_data['filter5'] = " "
    regression_data['filter6'] = " "
    regression_data['series_trend'] = trend_calculator(regression_data)
    flag = buy_other_indicator(regression_data, regressionResult, reg, ws)
    filterName = pct_change_filter(regression_data, regressionResult, False)
    filterNameTail = tail_change_filter(regression_data, regressionResult, False)
    pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
    filterOrFilter3 = regression_data['filterbuy'].strip() + ',' \
                      + regression_data['filtersell'].strip() + ',' \
                      + regression_data['filter'].strip()
    if(filterOrFilter3 == ",,"):
        filterOrFilter3 = regression_data['filter3']  + ',' \
                          + regression_data['filter4']
        
    regression_data['filterTest'] = filterName + ',' \
                                    + filterNameTail + ',' \
                                    + regression_data['series_trend'] + ',' \
                                    + pctChange5Day + ','\
                                    + regression_data['filter2'] + ',' \
                                    + filterOrFilter3 + ','\
                                    + regression_data['filter5']
                                    
    if regression_data['filterTest'] != '':
        return True  
    return False

def buy_test_tech(regression_data, regressionResult, reg, ws):
    regression_data['filterbuy'] = " "
    regression_data['filtersell'] = " "
    regression_data['filter'] = " "
    regression_data['filter1'] = " "
    regression_data['filter2'] = " "
    regression_data['filter3'] = " "
    regression_data['filter4'] = " "
    regression_data['filter5'] = " "
    regression_data['filter6'] = " "
    regression_data['series_trend'] = trend_calculator(regression_data)
    if (regression_data['buyIndia'] != '' or regression_data['sellIndia'] != ''):
        filterName = pct_change_filter(regression_data, regressionResult, False)
        filterNameTail = tail_change_filter(regression_data, regressionResult, False)
        pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
        regression_data['filterTest'] = filterName + ',' \
                                        + filterNameTail + ',' \
                                        + regression_data['series_trend'] + ',' \
                                        + 'B@{' + regression_data['buyIndia'] + '}' \
                                        + 'S@{' + regression_data['sellIndia'] + '}'
        return True
    
    return False

def buy_test_tech_all(regression_data, regressionResult, reg, ws):
    regression_data['filterbuy'] = " "
    regression_data['filtersell'] = " "
    regression_data['filter'] = " "
    regression_data['filter1'] = " "
    regression_data['filter2'] = " "
    regression_data['filter3'] = " "
    regression_data['filter4'] = " "
    regression_data['filter5'] = " "
    regression_data['filter6'] = " "
    regression_data['series_trend'] = trend_calculator(regression_data)
    flag = buy_other_indicator(regression_data, regressionResult, reg, ws)
    if (regression_data['buyIndia'] != '' or regression_data['sellIndia'] != ''):
        filterName = pct_change_filter(regression_data, regressionResult, False)
        filterNameTail = tail_change_filter(regression_data, regressionResult, False)
        pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
        regression_data['filterTest'] = filterName + ',' \
                                        + filterNameTail + ',' \
                                        + pctChange5Day + ','\
                                        + 'B@{' + regression_data['buyIndia'] + '}' \
                                        + 'S@{' + regression_data['sellIndia'] + '}' \
                                        + regression_data['filter2'] + ',' \
                                        + regression_data['filter3'] + ',' \
                                        + regression_data['filter5']
        return True
    
    return False

def buy_test_tech_all_pct_change(regression_data, regressionResult, reg, ws):
    regression_data['filterbuy'] = " "
    regression_data['filtersell'] = " "
    regression_data['filter'] = " "
    regression_data['filter1'] = " "
    regression_data['filter2'] = " "
    regression_data['filter3'] = " "
    regression_data['filter4'] = " "
    regression_data['filter5'] = " "
    regression_data['filter6'] = " "
    regression_data['series_trend'] = trend_calculator(regression_data)
    flag = buy_other_indicator(regression_data, regressionResult, reg, ws)
    if (regression_data['buyIndia'] != '' or regression_data['sellIndia'] != ''):
        filterName = pct_change_filter(regression_data, regressionResult, False)
        filterNameTail = tail_change_filter(regression_data, regressionResult, False)
        pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
        regression_data['filterTest'] = filterName + ',' \
                                        + filterNameTail + ',' \
                                        + pctChange5Day + ','\
                                        + 'B@{' + regression_data['buyIndia'] + '}' \
                                        + 'S@{' + regression_data['sellIndia'] + '}' \
                                        + regression_data['filter4'] + ',' \
                                        + regression_data['filter5']
        return True
    
    return False

def buy_all_filter(regression_data, regressionResult, reg, ws):
    flag = False
    if buy_year_high(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws, None, None, None)
        flag = True
    if buy_year_low(regression_data, regressionResult, reg, None, None):
        add_in_csv(regression_data, regressionResult, ws, None, None, None)
        flag = True
    if buy_up_trend(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws, None, None, None)
        flag = True
    if buy_down_trend(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws, None, None, None)
        flag = True
    if buy_final(regression_data, regressionResult, reg, None, None):
        add_in_csv(regression_data, regressionResult, ws, None, None, None)
        flag = True
    if buy_oi(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws, None, None, None)
        flag = True
    return flag

def buy_filter_st_accuracy(regression_data, regressionResult):
    filtersDict = filterstbuy
    filter = regression_data['filter'] + ',' + regression_data['filter1']
    if (filter != '') and (filter in filtersDict):
        if float(filtersDict[filter]['count']) >= 3:
            if abs(float(filtersDict[filter]['avg5'])) >= 5 and abs(float(filtersDict[filter]['avg10'])) > abs(
                    float(filtersDict[filter]['avg5'])):
                regression_data['filterst_avg5'] = float(filtersDict[filter]['avg5'])
                regression_data['filterst_avg10'] = float(filtersDict[filter]['avg10'])
                regression_data['filterst_count'] = float(filtersDict[filter]['count'])
                if float(filtersDict[filter]['avg5']) >= 0:
                    regression_data['filterst_pct5'] = (float(filtersDict[filter]['countgt5']) * 100) / float(
                        filtersDict[filter]['count'])
                    regression_data['filterst_pct10'] = (float(filtersDict[filter]['countgt10']) * 100) / float(
                        filtersDict[filter]['count'])
                else:
                    regression_data['filterst_pct5'] = -(float(filtersDict[filter]['countlt5']) * 100) / float(
                        filtersDict[filter]['count'])
                    regression_data['filterst_pct10'] = -(float(filtersDict[filter]['countlt10']) * 100) / float(
                        filtersDict[filter]['count'])
                insert_scripdata_st(regression_data['scrip'],
                                    regression_data['date'],
                                    filter,
                                    regression_data['filterst_avg5'],
                                    regression_data['filterst_pct5'],
                                    regression_data['filterst_avg10'],
                                    regression_data['filterst_pct10'],
                                    regression_data['filterst_count'],
                                    regression_data
                                    )
    filtersDict = filter3stbuy
    filter = regression_data['filter'] + ',' + regression_data['filter3']
    if (filter != '') and (filter in filtersDict):
        if float(filtersDict[filter]['count']) >= 3:
            if abs(float(filtersDict[filter]['avg5'])) >= 5 and abs(float(filtersDict[filter]['avg10'])) > abs(
                    float(filtersDict[filter]['avg5'])):
                regression_data['filter3st_avg5'] = float(filtersDict[filter]['avg5'])
                regression_data['filter3st_avg10'] = float(filtersDict[filter]['avg10'])
                regression_data['filter3st_count'] = float(filtersDict[filter]['count'])
                if float(filtersDict[filter]['avg5']) >= 0:
                    regression_data['filter3st_pct5'] = (float(filtersDict[filter]['countgt5']) * 100) / float(
                        filtersDict[filter]['count'])
                    regression_data['filter3st_pct10'] = (float(filtersDict[filter]['countgt10']) * 100) / float(
                        filtersDict[filter]['count'])
                else:
                    regression_data['filter3st_pct5'] = -(float(filtersDict[filter]['countlt5']) * 100) / float(
                        filtersDict[filter]['count'])
                    regression_data['filter3st_pct10'] = -(float(filtersDict[filter]['countlt10']) * 100) / float(
                        filtersDict[filter]['count'])
                insert_scripdata_st(regression_data['scrip'],
                                    regression_data['date'],
                                    filter,
                                    regression_data['filter3st_avg5'],
                                    regression_data['filter3st_pct5'],
                                    regression_data['filter3st_avg10'],
                                    regression_data['filter3st_pct10'],
                                    regression_data['filter3st_count'],
                                    regression_data
                                    )
    filtersDict = filter4stbuy
    filter = regression_data['filter4']
    if (filter != '') and (filter in filtersDict):
        if float(filtersDict[filter]['count']) >= 3:
            if abs(float(filtersDict[filter]['avg5'])) >= 5 and abs(float(filtersDict[filter]['avg10'])) > abs(
                    float(filtersDict[filter]['avg5'])):
                regression_data['filter4st_avg5'] = float(filtersDict[filter]['avg5'])
                regression_data['filter4st_avg10'] = float(filtersDict[filter]['avg10'])
                regression_data['filter4st_count'] = float(filtersDict[filter]['count'])
                if float(filtersDict[filter]['avg5']) >= 0:
                    regression_data['filter4st_pct5'] = (float(filtersDict[filter]['countgt5']) * 100) / float(
                        filtersDict[filter]['count'])
                    regression_data['filter4st_pct10'] = (float(filtersDict[filter]['countgt10']) * 100) / float(
                        filtersDict[filter]['count'])
                else:
                    regression_data['filter4st_pct5'] = -(float(filtersDict[filter]['countlt5']) * 100) / float(
                        filtersDict[filter]['count'])
                    regression_data['filter4st_pct10'] = -(float(filtersDict[filter]['countlt10']) * 100) / float(
                        filtersDict[filter]['count'])
                insert_scripdata_st(regression_data['scrip'],
                                    regression_data['date'],
                                    filter,
                                    regression_data['filter4st_avg5'],
                                    regression_data['filter4st_pct5'],
                                    regression_data['filter4st_avg10'],
                                    regression_data['filter4st_pct10'],
                                    regression_data['filter4st_count'],
                                    regression_data
                                    )

def buy_filter_345_accuracy(regression_data, regressionResult):
    filtersDict=filter345buy
    filterName = pct_change_filter(regression_data, regressionResult, False)
    filterNameTail = tail_change_filter(regression_data, regressionResult, False)
    pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
    filter = filterName + ',' \
            + filterNameTail + ',' \
            + pctChange5Day + ','\
            + regression_data['series_trend'] + ',' \
            + regression_data['filter1'] + ',' \
            + regression_data['filter3']
    if (filter != '') and (filter in filtersDict):
        regression_data['filter_345_avg'] = float(filtersDict[filter]['avg'])
        regression_data['filter_345_count'] = float(filtersDict[filter]['count'])
        if float(filtersDict[filter]['count']) >= 2:
            if float(filtersDict[filter]['avg']) >= 0:
                regression_data['filter_345_pct'] = (float(filtersDict[filter]['countgt'])*100)/float(filtersDict[filter]['count'])
            else:
                regression_data['filter_345_pct'] = -(float(filtersDict[filter]['countlt'])*100)/float(filtersDict[filter]['count'])

def buy_filter_accuracy(regression_data, regressionResult):
    filtersDict=filterbuy
    filterName = pct_change_filter(regression_data, regressionResult, False)
    filterNameTail = tail_change_filter(regression_data, regressionResult, False)
    pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
    filter = filterName + ',' \
            + filterNameTail + ',' \
            + pctChange5Day + ','\
            + regression_data['series_trend'] + ',' \
            + regression_data['filter2'] + ',' \
            + regression_data['filter4'] + ',' \
            + regression_data['filter5']
            
    if filter != '' and filter in filtersDict:
        regression_data['filter_avg'] = float(filtersDict[filter]['avg'])
        regression_data['filter_count'] = float(filtersDict[filter]['count'])
        if float(filtersDict[filter]['count']) >= 2:
            if float(filtersDict[filter]['avg']) >= 0:
                regression_data['filter_pct'] = (float(filtersDict[filter]['countgt'])*100)/float(filtersDict[filter]['count'])
            else:
                regression_data['filter_pct'] = -(float(filtersDict[filter]['countlt'])*100)/float(filtersDict[filter]['count'])

def buy_filter_pct_change_accuracy(regression_data, regressionResult):
    filtersDict=filterpctchangebuy
    filtercombine =  regression_data['filterbuy'].replace("[MLBuy]:", "").replace("[MLSell]:", "").strip() + ',' \
                + regression_data['filtersell'].replace("[MLBuy]:", "").replace("[MLSell]:", "").strip() + ',' \
                + regression_data['filter'].replace("[MLBuy]:", "").replace("[MLSell]:", "").strip()
    if filtercombine != ',,':
        filterName = pct_change_filter(regression_data, regressionResult, False)
        filterNameTail = tail_change_filter(regression_data, regressionResult, False)
        pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
        filter = filterName + ',' \
                + filterNameTail + ',' \
                + filtercombine
        if filter != '' and filter in filtersDict:
            regression_data['filter_pct_change_avg'] = float(filtersDict[filter]['avg'])
            regression_data['filter_pct_change_count'] = float(filtersDict[filter]['count'])
            if float(filtersDict[filter]['count']) >= 2:
                if float(filtersDict[filter]['avg']) >= 0:
                    regression_data['filter_pct_change_pct'] = (float(filtersDict[filter]['countgt'])*100)/float(filtersDict[filter]['count'])
                else:
                    regression_data['filter_pct_change_pct'] = -(float(filtersDict[filter]['countlt'])*100)/float(filtersDict[filter]['count'])
                
def buy_filter_345_all_accuracy(regression_data, regressionResult):
    filtersDict=filterallbuy
    filterName = pct_change_filter(regression_data, regressionResult, False)
    filterNameTail = tail_change_filter(regression_data, regressionResult, False)
    pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
    filterOrFilter3 = regression_data['filterbuy'].replace("[MLBuy]:", "").replace("[MLSell]:", "").strip() + ',' \
                      + regression_data['filtersell'].replace("[MLBuy]:", "").replace("[MLSell]:", "").strip() + ',' \
                      + regression_data['filter'].replace("[MLBuy]:", "").replace("[MLSell]:", "").strip()
    if(filterOrFilter3 == ",,"):
        filterOrFilter3 = regression_data['filter3'] + ',' \
                          + regression_data['filter4'] 
   
    filter = filterName + ',' \
            + filterNameTail + ',' \
            + regression_data['series_trend'] + ',' \
            + pctChange5Day + ','\
            + regression_data['filter2'] + ',' \
            + filterOrFilter3 + ','\
            + regression_data['filter5']
            
    if (filter != '') and (filter in filtersDict):
        regression_data['filter_all_avg'] = float(filtersDict[filter]['avg'])
        regression_data['filter_all_count'] = float(filtersDict[filter]['count'])
        if float(filtersDict[filter]['count']) >= 2:
            if float(filtersDict[filter]['avg']) >= 0:
                regression_data['filter_all_pct'] = (float(filtersDict[filter]['countgt'])*100)/float(filtersDict[filter]['count'])
            else:
                regression_data['filter_all_pct'] = -(float(filtersDict[filter]['countlt'])*100)/float(filtersDict[filter]['count'])

def buy_filter_tech_accuracy(regression_data, regressionResult):
    filtersDict=filtertechbuy
    filterName = pct_change_filter(regression_data, regressionResult, False)
    filterNameTail = tail_change_filter(regression_data, regressionResult, False)
    pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
    filter = filterName + ',' \
            + filterNameTail + ',' \
            + regression_data['series_trend'] + ',' \
            + 'B@{' + regression_data['buyIndia'] + '}' \
            + 'S@{' + regression_data['sellIndia'] + '}' 
    if (filter != '') and (filter in filtersDict):
        regression_data['filter_tech_avg'] = float(filtersDict[filter]['avg'])
        regression_data['filter_tech_count'] = float(filtersDict[filter]['count'])
        if float(filtersDict[filter]['count']) >= 2:
            if float(filtersDict[filter]['avg']) >= 0:
                regression_data['filter_tech_pct'] = (float(filtersDict[filter]['countgt'])*100)/float(filtersDict[filter]['count'])
            else:
                regression_data['filter_tech_pct'] = -(float(filtersDict[filter]['countlt'])*100)/float(filtersDict[filter]['count'])

def buy_filter_tech_all_accuracy(regression_data, regressionResult):
    filtersDict=filtertechallbuy
    filterName = pct_change_filter(regression_data, regressionResult, False)
    filterNameTail = tail_change_filter(regression_data, regressionResult, False)
    pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
    filter = filterName + ',' \
            + filterNameTail + ',' \
            + pctChange5Day + ','\
            + 'B@{' + regression_data['buyIndia'] + '}' \
            + 'S@{' + regression_data['sellIndia'] + '}' \
            + regression_data['filter2'] + ',' \
            + regression_data['filter3'] + ',' \
            + regression_data['filter5']
            
    if (filter != '') and (filter in filtersDict):
        regression_data['filter_tech_all_avg'] = float(filtersDict[filter]['avg'])
        regression_data['filter_tech_all_count'] = float(filtersDict[filter]['count'])
        if float(filtersDict[filter]['count']) >= 2:
            if float(filtersDict[filter]['avg']) >= 0:
                regression_data['filter_tech_all_pct'] = (float(filtersDict[filter]['countgt'])*100)/float(filtersDict[filter]['count'])
            else:
                regression_data['filter_tech_all_pct'] = -(float(filtersDict[filter]['countlt'])*100)/float(filtersDict[filter]['count'])

def buy_filter_tech_all_pct_change_accuracy(regression_data, regressionResult):
    filtersDict=filtertechallpctchangebuy
    filterName = pct_change_filter(regression_data, regressionResult, False)
    filterNameTail = tail_change_filter(regression_data, regressionResult, False)
    pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
    filter = filterName + ',' \
            + filterNameTail + ',' \
            + pctChange5Day + ','\
            + 'B@{' + regression_data['buyIndia'] + '}' \
            + 'S@{' + regression_data['sellIndia'] + '}' \
            + regression_data['filter4'] + ',' \
            + regression_data['filter5']
            
    if (filter != '') and (filter in filtersDict):
        regression_data['filter_tech_all_pct_change_avg'] = float(filtersDict[filter]['avg'])
        regression_data['filter_tech_all_pct_change_count'] = float(filtersDict[filter]['count'])
        if float(filtersDict[filter]['count']) >= 2:
            if float(filtersDict[filter]['avg']) >= 0:
                regression_data['filter_tech_all_pct_change_pct'] = (float(filtersDict[filter]['countgt'])*100)/float(filtersDict[filter]['count'])
            else:
                regression_data['filter_tech_all_pct_change_pct'] = -(float(filtersDict[filter]['countlt'])*100)/float(filtersDict[filter]['count'])

def buy_filter_all_accuracy(regression_data, regressionResult):
    if(regression_data['close'] > CLOSEPRICE):
        buy_filter_st_accuracy(regression_data, regressionResult)
        buy_filter_345_accuracy(regression_data, regressionResult)
        buy_filter_accuracy(regression_data, regressionResult)
        buy_filter_pct_change_accuracy(regression_data, regressionResult) 
        buy_filter_345_all_accuracy(regression_data, regressionResult)
        buy_filter_tech_accuracy(regression_data, regressionResult)
        buy_filter_tech_all_accuracy(regression_data, regressionResult)
        buy_filter_tech_all_pct_change_accuracy(regression_data, regressionResult)
                           
def sell_all_rule(regression_data, regressionResult, sellIndiaAvg, ws): 
    if(low_tail_pct(regression_data) < 1.5):          
        if(regression_data['PCT_day_change'] < -2 and regression_data['PCT_day_change_pre1'] < -2 and regression_data['PCT_day_change_pre2'] < -2):
            add_in_csv(regression_data, regressionResult, ws, None, 'Last3Day(LT-2)')
        elif(regression_data['PCT_day_change'] < -2 and regression_data['PCT_day_change_pre1'] < -2 and regression_data['PCT_day_change_pre2'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, 'Last2Day(LT-2)-3rdDayLT0')
        elif(regression_data['PCT_day_change'] < -2 and regression_data['PCT_day_change_pre1'] < -2 and regression_data['PCT_day_change_pre2'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, 'Last2Day(LT-2)')
        elif(regression_data['PCT_day_change'] < -2 and regression_data['PCT_day_change_pre1'] < 0 and regression_data['PCT_day_change_pre2'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, 'Last1Day(LT-2)-2ndDayLT0')
        elif(regression_data['PCT_day_change'] < -2 and regression_data['PCT_day_change_pre1'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, 'Last1Day(LT-2)')
        else:
            if(low_tail_pct(regression_data) < abs(regression_data['PCT_day_change']) or low_tail_pct(regression_data) < abs(regression_data['PCT_change'])):
                if(regression_data['PCT_day_change'] <= -1 and regression_data['PCT_day_change_pre1'] <= -1 and regression_data['PCT_day_change_pre2'] <= -1):
                    add_in_csv(regression_data, regressionResult, ws, None, 'Last3Day(LT-1)')
                elif(regression_data['PCT_day_change'] <= -1 and regression_data['PCT_day_change_pre1'] <= -1 and regression_data['PCT_day_change_pre2'] < 0):
                    add_in_csv(regression_data, regressionResult, ws, None, 'Last2Day(LT-1)-3rdDayLT0')
                elif(regression_data['PCT_day_change'] <= -1 and regression_data['PCT_day_change_pre1'] <= -1 and regression_data['PCT_day_change_pre2'] > 0):
                    add_in_csv(regression_data, regressionResult, ws, None, 'Last2Day(LT-1)')
                elif(regression_data['PCT_day_change'] <= -1 and -1 < regression_data['PCT_day_change_pre1'] < 0 and regression_data['PCT_day_change_pre2'] > 0 and regression_data['PCT_day_change_pre3'] < 0):
                    add_in_csv(regression_data, regressionResult, ws, None, 'Last1Day(LT-1)-2ndDayDojiLT0-3rdDayGT0:MaySellDowntrend-BuyUptrend')
                elif(regression_data['PCT_day_change'] <= -1 
                    and (-1 < regression_data['PCT_day_change_pre1'] < 0 or (regression_data['PCT_day_change_pre1'] < 0 and 2*abs(regression_data['PCT_day_change_pre1']) < abs(regression_data['PCT_day_change_pre2'])))
                    and regression_data['PCT_day_change_pre2'] < 0
                    and regression_data['PCT_day_change_pre3'] > -0.5
                    ):
                    if(abs(regression_data['monthHighChange']) < abs(regression_data['monthLowChange'])):
                        add_in_csv(regression_data, regressionResult, ws, None, 'Last1Day(LT-1)-2ndDayDojiLT0-3rdDayLT0:MayBuy')
                    elif(abs(regression_data['monthHighChange']) > abs(regression_data['monthLowChange'])):
                        add_in_csv(regression_data, regressionResult, ws, None, 'Last1Day(LT-1)-2ndDayDojiLT0-3rdDayLT0:MaySell')
                elif(regression_data['PCT_day_change'] <= -1 
                    and (0 < regression_data['PCT_day_change_pre1'] < 1 and 2*abs(regression_data['PCT_day_change_pre1']) < abs(regression_data['PCT_day_change_pre2']))
                    and regression_data['PCT_day_change_pre2'] < 0
                    and regression_data['PCT_day_change_pre3'] > -0.5
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, 'MaySell:Last1Day(LT-1)-2ndDayDojiGT0-3rdDayLT0:MaySellDownTrend-BuyUptrend')
                elif(regression_data['PCT_day_change'] <= -1 and regression_data['PCT_day_change_pre1'] > 0):
                    add_in_csv(regression_data, regressionResult, ws, None, 'Last1Day(LT-1)')
                    
                    
        if(regression_data['PCT_day_change'] <= -1 
            and 0 < regression_data['PCT_day_change_pre1'] < 1 
            and -1 < regression_data['PCT_day_change_pre2'] < 0 
            and regression_data['PCT_day_change_pre3'] <= -1
            and regression_data['bar_low'] < regression_data['bar_low_pre3'] < regression_data['bar_low_pre1'] 
            and regression_data['bar_low'] < regression_data['bar_low_pre3'] < regression_data['bar_low_pre2']
            and regression_data['month3LowChange'] > 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, 'DojiLastDay(LT-1)Today')
    
    if(regression_data['PCT_day_change'] <= -1.5 and regression_data['PCT_change'] <= -1.5
        and low_tail_pct(regression_data) <= 1
        ):
        if(regression_data['month3LowChange'] < 1
            and regression_data['monthLowChange'] < 1
            and regression_data['week2LowChange'] < 1
            ):
            add_in_csv(regression_data, regressionResult, ws, None, 'CheckSmoothMA-LTMonth3Low')
        elif(regression_data['month3LowChange'] > 1
            and regression_data['monthLowChange'] > 1
            and regression_data['week2LowChange'] > 1
            ):
            add_in_csv(regression_data, regressionResult, ws, None, 'CheckSmoothMA-GTMonth3Low')
        if(regression_data['month3LowChange'] < 1
            and regression_data['monthLowChange'] < 1
            ):
            add_in_csv(regression_data, regressionResult, ws, None, 'CheckSmoothMA-LTMonth3Low')
        elif(regression_data['month3LowChange'] > 1
            and regression_data['monthLowChange'] > 1
            ):
            add_in_csv(regression_data, regressionResult, ws, None, 'CheckSmoothMA-GTMonth3Low')
        
    if( -0.5 < regression_data['PCT_day_change'] < 0
        and -0.5 < regression_data['PCT_change'] < 0
        and -7 < regression_data['PCT_day_change_pre1'] < -2
        and (regression_data['PCT_day_change_pre3'] > 0 or regression_data['PCT_day_change_pre4'] > 0)
        and regression_data['bar_low'] < regression_data['bar_low_pre2']
        and (high_tail_pct(regression_data) < 1.5 and low_tail_pct(regression_data) < 1.5)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, 'DojiToday(LT-2)LastDay')
        
    if('DOJI' in regression_data['filter5']
        #and regression_data['forecast_day_PCT7_change'] > 0
        and regression_data['forecast_day_PCT10_change'] <= -2
        and (regression_data['PCT_day_change'] > 0
            or (regression_data['forecast_day_PCT_change'] > 0
                and regression_data['forecast_day_PCT2_change'] > 0
                )
            )
        and (high_tail_pct(regression_data) < 4.0 and low_tail_pct(regression_data) < 4.0)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, 'Sell-LastDayNiftyMidCapUpGT1-TodayDownMorningNifty(LT-0.5)')
    
    if(is_algo_sell(regression_data)):
        if(3.5 < regression_data['PCT_day_change'] < 15 and 3.5 < regression_data['PCT_change'] < 15):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'AFML:mlSellPCTDayChangeGT3.5')
        elif(regression_data['week2LowChange'] > 20 and regression_data['weekLowChange'] > 10
            and -5 < regression_data['PCT_day_change'] < -2
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'AFML:(NOT-UPTREND)0-mlSellWeek2LowGT20')
        elif(regression_data['week2LowChange'] > 10 and regression_data['weekLowChange'] > 10
            and (regression_data['week2LowChange'] > 15 or regression_data['weekLowChange'] > 15) 
            and -4 < regression_data['PCT_day_change'] < -2
            and is_any_buy_GT2_from_all_filter(regression_data) == False
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'AFML:(NOT-UPTREND)1-mlSellWeek2LowOrWeekLowGT15')
#         elif(regression_data['week2LowChange'] > 5 and regression_data['weekLowChange'] > 10
#             and -5 < regression_data['PCT_day_change'] < -2
#             and is_any_buy_GT2_from_all_filter(regression_data) == False
#             ):
#             add_in_csv(regression_data, regressionResult, ws, None, None, 'AF:1-mlSellWeekLowGT10')
#         elif(regression_data['week2LowChange'] > 5 and regression_data['weekLowChange'] > 0
#             and -4 < regression_data['PCT_day_change'] < 1
#             and is_any_buy_GT2_from_all_filter(regression_data) == False
#             ):
#             add_in_csv(regression_data, regressionResult, ws, None, None, 'AF:3-mlSellWeek2LowGT5')
        if('NearHigh' in regression_data['filter3']
            and'LT0' in regression_data['filter3']
            and regression_data['PCT_day_change'] > 0 and regression_data['PCT_change'] > -1
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'AFML:(DOWNTRENDMARKET)sellNearHighBaseReversal')
        if((regression_data['yearLowChange'] > 5) and ('BreakLowMonth6' in regression_data['filter3'])
            and'LT0' in regression_data['filter3']
            and regression_data['PCT_day_change'] < 0 and regression_data['PCT_change'] < 1
            and regression_data['forecast_day_PCT_change'] > regression_data['forecast_day_PCT2_change'] > regression_data['forecast_day_PCT3_change']
            and regression_data['forecast_day_PCT_change'] > 0
            and regression_data['forecast_day_PCT2_change'] > 0
            and regression_data['forecast_day_PCT3_change'] > 0
            and regression_data['forecast_day_PCT4_change'] > 0
            and regression_data['forecast_day_PCT5_change'] > 0
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'AFML:(DOWNTRENDMARKET)sellBreakLowBaseContinue')
        if(regression_data['monthLowChange'] > 0.5 
            and regression_data['monthHigh'] != regression_data['week2High']
            and regression_data['monthHighChange'] < -7
            and -4 < regression_data['PCT_day_change'] < -1 and -5 < regression_data['PCT_change'] < -1
            and regression_data['PCT_day_change'] < regression_data['PCT_day_change_pre1']
            and regression_data['PCT_day_change_pre1'] < 0
            and regression_data['PCT_day_change_pre2'] < 0
            and high_tail_pct(regression_data) < 1
            and low_tail_pct(regression_data) < 1
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, 'AFML:(DOWNTRENDMARKET)sellContinueMoreThanMonthLow')
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
        and ((last_7_day_all_down(regression_data) == False) or (regression_data['forecast_day_PCT10_change'] > -10))
        and (MARKET_IN_DOWNTREND or (last_4_day_all_down(regression_data) == False)) #Uncomment0 If very less data
        and breakout_or_no_consolidation(regression_data) == True
        and '(Confirmed)EMA6<EMA14' not in regression_data['filter4']
        and regression_data['close'] > 50
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None)
        return True
    return False

def sell_all_common(regression_data, regressionResult, reg, ws):
    mlpValue, kNeighboursValue = get_reg_or_cla(regression_data, True)
    mlpValue_other, kNeighboursValue_other = get_reg_or_cla_other(regression_data, True)
    mlpValue_cla, kNeighboursValue_cla = get_reg_or_cla(regression_data, False)
    mlpValue_other_cla, kNeighboursValue_other_cla = get_reg_or_cla_other(regression_data, False)
    
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
        and 'buy' not in regression_data['filter']
        and 'Buy' not in regression_data['filter']
        ):    
        if(regression_data['SMA9'] < -1):
            add_in_csv(regression_data, regressionResult, ws, None, 'CommonHL:sellNotM3HighLow-0(SMA9LT-1)') 
        elif(regression_data['SMA25'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None, None, None) 
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None) 
                
    return False

def sell_all_common_High_Low(regression_data, regressionResult, reg, ws):
    if(((regression_data['forecast_day_PCT_change'] < -0.5 and regression_data['forecast_day_PCT2_change'] < regression_data['forecast_day_PCT_change'])
        or (regression_data['forecast_day_PCT3_change'] < 0 and regression_data['forecast_day_PCT4_change'] < 0)
        or regression_data['forecast_day_PCT5_change'] < 0
        or regression_data['forecast_day_PCT7_change'] < 0
        or regression_data['forecast_day_PCT10_change'] < 0
        )
        and (
            regression_data['month3LowChange'] < 0
            or (regression_data['monthLowChange'] < 0 and regression_data['month3LowChange'] > 0
                and regression_data['PCT_day_change_pre1'] < 0 and regression_data['PCT_day_change_pre2'] < 0
                )
            #or regression_data['monthLowChange'] < 0
            or abs(regression_data['week2HighChange']) < abs(regression_data['week2LowChange'])
            or (regression_data['week2HighChange'] < 0
                and regression_data['week2LowChange'] > 2
                and abs(regression_data['week2HighChange']) > abs(regression_data['week2LowChange'])
                and (abs(regression_data['monthHighChange']) > abs(regression_data['monthLowChange'])
                    or abs(regression_data['month3HighChange']) > abs(regression_data['month3LowChange'])
                    )
               )
            or (regression_data['monthHighChange'] < 0
                and regression_data['monthLowChange'] > 2
                and abs(regression_data['monthHighChange']) > abs(regression_data['monthLowChange'])
                and (abs(regression_data['month3HighChange']) > abs(regression_data['month3LowChange'])
                    or abs(regression_data['month6HighChange']) > abs(regression_data['month6LowChange'])
                    )
               )
            )
        and 'buy' not in regression_data['filter']
        and 'Buy' not in regression_data['filter']
        ):
        if(-2.9 > regression_data['PCT_day_change'] > -4.1 and -3 > regression_data['PCT_change'] > -4.5
            and -4 < regression_data['PCT_day_change_pre1'] < 0.75
            and -4 < regression_data['PCT_day_change_pre2']
            and (regression_data['PCT_day_change_pre1'] < -0.5
                or regression_data['PCT_day_change_pre2'] < -0.5
                or regression_data['PCT_day_change_pre3'] < -0.5
                )
            and ((regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change_pre2'] > 0 and regression_data['PCT_day_change_pre3'] > 0)
                or (regression_data['PCT_day_change_pre1'] < 0 and regression_data['PCT_day_change_pre2'] > 0 and regression_data['PCT_day_change_pre3'] > 0)
                or (regression_data['PCT_day_change_pre1'] < 0 and regression_data['PCT_day_change_pre2'] < 0 and regression_data['PCT_day_change_pre3'] > 0 and regression_data['month3LowChange'] < 0)
                or (regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change_pre2'] < 0 and regression_data['PCT_day_change_pre3'] < 1 and regression_data['month3LowChange'] > 0)
                or (regression_data['monthHighChange'] < 0 and regression_data['monthLowChange'] > 2)
                )
            and low_tail_pct(regression_data) < 1.29
            and high_tail_pct(regression_data) < 2.5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, 'CommonHL:HighDowntrend')
        elif(-2.7 > regression_data['PCT_day_change'] > -5.5
            and -3 > regression_data['PCT_change'] 
            and regression_data['PCT_day_change_pre1'] < 1.3
            and (regression_data['PCT_day_change_pre2'] < 1.3 
                 or (regression_data['PCT_day_change_pre1'] < 0 
                     and regression_data['PCT_day_change_pre3'] < 0
                     and regression_data['low_pre2'] < regression_data['low_pre3'] 
                     and regression_data['high_pre2'] < regression_data['high_pre3']
                     )
                 )
            and (regression_data['PCT_day_change_pre1'] > -1
                 or regression_data['PCT_day_change_pre2'] > -1
                 or regression_data['PCT_day_change_pre3'] > -1
            )
            and ((regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change_pre2'] > 0 and regression_data['PCT_day_change_pre3'] > 0)
                or (regression_data['PCT_day_change_pre1'] < 0 and regression_data['PCT_day_change_pre2'] > 0 and regression_data['PCT_day_change_pre3'] > 0)
                or (regression_data['PCT_day_change_pre1'] < 0 and regression_data['PCT_day_change_pre2'] < 0 and regression_data['PCT_day_change_pre3'] > 0 and regression_data['month3LowChange'] < 0)
                or (regression_data['PCT_day_change_pre1'] > 0 and regression_data['PCT_day_change_pre2'] < 0 and regression_data['PCT_day_change_pre3'] < 1 and regression_data['month3LowChange'] > 0)
                or (regression_data['monthHighChange'] < 0 and regression_data['monthLowChange'] > 2)
                )
            and regression_data['forecast_day_PCT4_change'] < 0
            and regression_data['forecast_day_PCT5_change'] < 0
            and regression_data['SMA4'] < -2
            and regression_data['SMA9'] < -2 
            and low_tail_pct(regression_data) < 2.5
            and high_tail_pct(regression_data) < 2.5
            ):
            if(-2.95 > regression_data['PCT_day_change']
                or (regression_data['PCT_day_change_pre1'] > 0
                    or regression_data['PCT_day_change_pre2'] > 0
                    or regression_data['PCT_day_change_pre3'] > 0
                    )
                ):
                add_in_csv(regression_data, regressionResult, ws, None, 'CommonHL:HEAVYDOWNTRENDMARKET:HighDowntrend')
            elif(regression_data['PCT_day_change_pre1'] < 0
                or regression_data['PCT_day_change_pre2'] < 0
                or regression_data['PCT_day_change_pre3'] < 0
                ):
                add_in_csv(regression_data, regressionResult, ws, None, 'CommonHL:HEAVYDOWNTRENDMARKET:HighDowntrend-(DOWNTREND-GLOBALDOWN)')
        
        if( -8 < regression_data['PCT_day_change'] < -4 and -10 < regression_data['PCT_change'] < -3
            and (regression_data['PCT_day_change'] < -5 or regression_data['PCT_change'] < -5)  
            and -4 < regression_data['PCT_day_change_pre1'] < 0.75
            and -4 < regression_data['PCT_day_change_pre2']
            and (regression_data['PCT_day_change_pre1'] > 0 or regression_data['PCT_day_change_pre2'] > 0 or regression_data['PCT_day_change_pre3'] > 0)
            and (regression_data['PCT_day_change_pre1'] > -0.75 or regression_data['PCT_day_change_pre2'] > -0.75)
            and (regression_data['PCT_day_change_pre2'] > -0.75 or regression_data['PCT_day_change_pre3'] > -0.75)
            and high_tail_pct(regression_data) < 2.5
            and low_tail_pct(regression_data) < abs(regression_data['PCT_day_change'])/3
            ):
            if(regression_data['PCT_day_change_pre1'] > 0):
                add_in_csv(regression_data, regressionResult, ws, None, 'CommonHL(9:30):HighDowntrend-2')
            else:
                add_in_csv(regression_data, regressionResult, ws, None, 'CommonHL:HighDowntrend-2')
                
    if(-2.5 > regression_data['PCT_day_change'] > -3 and -2.5 > regression_data['PCT_change'] > -5
        and -1 < regression_data['PCT_day_change_pre1'] < 2
        and -1 < regression_data['PCT_day_change_pre2'] < 2
        and (regression_data['week2HighChange'] < -2 or regression_data['weekHighChange'] < -2)
        and low_tail_pct(regression_data) < 2
        and high_tail_pct(regression_data) < 2.5
        ):
        add_in_csv(regression_data, regressionResult, ws, None, 'CommonHL:DownTrendLast2Day-GlobalDown-GlobalFutureDown-NiftyDown')
    elif(-2 < regression_data['PCT_day_change'] < -1.5 and -4 < regression_data['PCT_change'] < -3
        and (regression_data['PCT_change'] - regression_data['PCT_day_change']) < -1.5
        and low_tail_pct(regression_data) < 1.3
        and high_tail_pct(regression_data) < 2.5
        ):
        add_in_csv(regression_data, regressionResult, ws, 'CommonHL:LastDay-PCTDayChange-LT(-2)-PCTChange') 
    elif(-3 < regression_data['PCT_day_change'] < -2 and -5 < regression_data['PCT_change'] < -4
        and (regression_data['PCT_change'] - regression_data['PCT_day_change']) < -1.5
        and low_tail_pct(regression_data) < 1.3
        and high_tail_pct(regression_data) < 2.5
        ):
        add_in_csv(regression_data, regressionResult, ws, 'CommonHL:LastDay-PCTDayChange-LT(-3)-PCTChange') 
    
    sell_common_down_continued(regression_data, regressionResult, reg, ws)
          
def sell_other_indicator(regression_data, regressionResult, reg, ws):
    tail_pct_filter(regression_data, regressionResult)
    base_line(regression_data, regressionResult, reg, ws)
    filterMA(regression_data, regressionResult)
    tail_reversal_filter(regression_data, regressionResult)
    
    buy_market_uptrend(regression_data, regressionResult, reg, ws)
    buy_month3_high_continue(regression_data, regressionResult, reg, ws)
    buy_risingMA(regression_data, regressionResult, reg, ws)
    buy_study_risingMA(regression_data, regressionResult, reg, ws)
    buy_check_chart(regression_data, regressionResult, reg, ws)
    
    sell_market_downtrend(regression_data, regressionResult, reg, ws)
    sell_check_chart(regression_data, regressionResult, reg, ws)
    sell_downingMA(regression_data, regressionResult, reg, ws)
    sell_study_downingMA(regression_data, regressionResult, reg, ws)
    
    sell_high_volatility(regression_data, regressionResult)
    if(regression_data['close'] > 50):
        buy_year_high(regression_data, regressionResult, reg, ws)
        buy_year_low(regression_data, regressionResult, reg, ws, ws)
        buy_down_trend(regression_data, regressionResult, reg, ws)
        buy_final(regression_data, regressionResult, reg, ws, ws)
        buy_morning_star_buy(regression_data, regressionResult, reg, ws)
        buy_evening_star_sell(regression_data, regressionResult, reg, ws)
        buy_day_low(regression_data, regressionResult, reg, ws)
        buy_trend_reversal(regression_data, regressionResult, reg, ws)
        buy_trend_break(regression_data, regressionResult, reg, ws)
        buy_consolidation_breakout(regression_data, regressionResult, reg, ws)
        buy_final_candidate(regression_data, regressionResult, reg, ws)
        buy_oi(regression_data, regressionResult, reg, ws)
        buy_up_trend(regression_data, regressionResult, reg, ws)
        buy_heavy_uptrend_reversal(regression_data, regressionResult, reg, ws)
        buy_tail_reversal_filter(regression_data, regressionResult, reg, ws)
        
        sell_up_trend(regression_data, regressionResult, reg, ws)
        sell_down_trend(regression_data, regressionResult, reg, ws)
        sell_final(regression_data, regressionResult, reg, ws, ws)
        sell_morning_star_buy(regression_data, regressionResult, reg, ws)
        sell_evening_star_sell(regression_data, regressionResult, reg, ws)
        sell_day_high(regression_data, regressionResult, reg, ws)
        sell_trend_reversal(regression_data, regressionResult, reg, ws)
        sell_trend_break(regression_data, regressionResult, reg, ws)
        sell_final_candidate(regression_data, regressionResult, reg, ws)
        sell_oi(regression_data, regressionResult, reg, ws)
        sell_heavy_downtrend(regression_data, regressionResult, reg, ws)
        sell_tail_reversal_filter(regression_data, regressionResult, reg, ws)
        sell_hltf_high_tail(regression_data, regressionResult, reg, ws)
        
        #sell_random_filter(regression_data, regressionResult, reg, ws)
        sell_check_cup_filter(regression_data, regressionResult, reg, ws)
        sell_consolidation_breakdown(regression_data, regressionResult, reg, ws)
        sell_supertrend(regression_data, regressionResult, reg, ws)
        return True
    if(sell_skip_close_lt_50(regression_data, regressionResult, reg, ws)):
        return True
    return False

def sell_indicator_after_filter_accuracy(regression_data, regressionResult, reg, ws):
    return False

def sell_skip_close_lt_50(regression_data, regressionResult, reg, ws):
    if((regression_data['weekLowChange'] > 15) 
        and (-10 < regression_data['PCT_change'] < -4)
        and (-10 < regression_data['PCT_day_change'] < -4)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, 'sellUptrendReversalHeavyBuyHeavySell')
        return True
    return False

def sell_test_345(regression_data, regressionResult, reg, ws):
    regression_data['filterbuy'] = " "
    regression_data['filtersell'] = " "
    regression_data['filter'] = " "
    regression_data['filter1'] = " "
    regression_data['filter2'] = " "
    regression_data['filter3'] = " "
    regression_data['filter4'] = " "
    regression_data['filter5'] = " "
    regression_data['filter6'] = " "
    regression_data['series_trend'] = trend_calculator(regression_data)
    flag = sell_other_indicator(regression_data, regressionResult, reg, ws)
    filterName = pct_change_filter(regression_data, regressionResult, False)
    filterNameTail = tail_change_filter(regression_data, regressionResult, False)
    pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
    regression_data['filterTest'] = filterName + ',' \
                                    + filterNameTail + ',' \
                                    + pctChange5Day + ',' \
                                    + regression_data['series_trend'] + ',' \
                                    + regression_data['filter1'] + ',' \
                                    + regression_data['filter3']
    if regression_data['filterTest'] != '':
        return True  
    return False
        
def sell_test(regression_data, regressionResult, reg, ws):
    regression_data['filterbuy'] = " "
    regression_data['filtersell'] = " "
    regression_data['filter'] = " "
    regression_data['filter1'] = " "
    regression_data['filter2'] = " "
    regression_data['filter3'] = " "
    regression_data['filter4'] = " "
    regression_data['filter5'] = " "
    regression_data['filter6'] = " "
    regression_data['series_trend'] = trend_calculator(regression_data)
    flag = sell_other_indicator(regression_data, regressionResult, reg, ws)
    filterName = pct_change_filter(regression_data, regressionResult, False)
    filterNameTail = tail_change_filter(regression_data, regressionResult, False)
    pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
    regression_data['filterTest'] = filterName + ',' \
                                    + filterNameTail + ',' \
                                    + pctChange5Day + ',' \
                                    + regression_data['series_trend'] + ',' \
                                    + regression_data['filter2'] + ',' \
                                    + regression_data['filter4'] + ',' \
                                    + regression_data['filter5']
                                    
    if regression_data['filterTest'] != '':
        return True  
    return False

def sell_test_pct_change(regression_data, regressionResult, reg, ws):
    regression_data['filterbuy'] = " "
    regression_data['filtersell'] = " "
    regression_data['filter'] = " "
    regression_data['filter1'] = " "
    regression_data['filter2'] = " "
    regression_data['filter3'] = " "
    regression_data['filter4'] = " "
    regression_data['filter5'] = " "
    regression_data['filter6'] = " "
    regression_data['series_trend'] = trend_calculator(regression_data)
    flag = sell_other_indicator(regression_data, regressionResult, reg, ws)
    filtercombine=regression_data['filterbuy'].strip() + ',' \
              + regression_data['filtersell'].strip() + ',' \
              + regression_data['filter'].strip()
    if filtercombine != ",,":
        filterName = pct_change_filter(regression_data, regressionResult, False)
        filterNameTail = tail_change_filter(regression_data, regressionResult, False)
        pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
        regression_data['filterTest'] = filterName + ',' \
                                        + filterNameTail + ',' \
                                        + filtercombine
    
    if regression_data['filterTest'] != '':
        return True
        
    return False

def sell_test_all(regression_data, regressionResult, reg, ws):
    regression_data['filterbuy'] = " "
    regression_data['filtersell'] = " "
    regression_data['filter'] = " "
    regression_data['filter1'] = " "
    regression_data['filter2'] = " "
    regression_data['filter3'] = " "
    regression_data['filter4'] = " "
    regression_data['filter5'] = " "
    regression_data['filter6'] = " "
    regression_data['series_trend'] = trend_calculator(regression_data)
    flag = sell_other_indicator(regression_data, regressionResult, reg, ws)
    filterName = pct_change_filter(regression_data, regressionResult, False)
    filterNameTail = tail_change_filter(regression_data, regressionResult, False)
    pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
    filterOrFilter3 = regression_data['filterbuy'].strip() + ',' \
                      + regression_data['filtersell'].strip() + ',' \
                      + regression_data['filter'].strip()
    if(filterOrFilter3 == ",,"):
        filterOrFilter3 = regression_data['filter3'] + ',' \
                          + regression_data['filter4']
        
    regression_data['filterTest'] = filterName + ',' \
                                    + filterNameTail + ',' \
                                    + regression_data['series_trend'] + ',' \
                                    + pctChange5Day + ','\
                                    + regression_data['filter2'] + ',' \
                                    + filterOrFilter3 + ','\
                                    + regression_data['filter5']
                                    
    if regression_data['filterTest'] != '':
        return True  
    return False

def sell_test_tech(regression_data, regressionResult, reg, ws):
    regression_data['filterbuy'] = " "
    regression_data['filtersell'] = " "
    regression_data['filter'] = " "
    regression_data['filter1'] = " "
    regression_data['filter2'] = " "
    regression_data['filter3'] = " "
    regression_data['filter4'] = " "
    regression_data['filter5'] = " "
    regression_data['filter6'] = " "
    regression_data['series_trend'] = trend_calculator(regression_data)
    if (regression_data['buyIndia'] != '' or regression_data['sellIndia'] != ''):
        filterName = pct_change_filter(regression_data, regressionResult, False)
        filterNameTail = tail_change_filter(regression_data, regressionResult, False)
        pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
        regression_data['filterTest'] = filterName + ',' \
                                        + filterNameTail + ',' \
                                        + regression_data['series_trend'] + ',' \
                                        + 'B@{' + regression_data['buyIndia'] + '}' \
                                        + 'S@{' + regression_data['sellIndia'] + '}' 
        return True
    
    return False

def sell_test_tech_all(regression_data, regressionResult, reg, ws):
    regression_data['filterbuy'] = " "
    regression_data['filtersell'] = " "
    regression_data['filter'] = " "
    regression_data['filter1'] = " "
    regression_data['filter2'] = " "
    regression_data['filter3'] = " "
    regression_data['filter4'] = " "
    regression_data['filter5'] = " "
    regression_data['filter6'] = " "
    regression_data['series_trend'] = trend_calculator(regression_data)
    flag = buy_other_indicator(regression_data, regressionResult, reg, ws)
    if (regression_data['buyIndia'] != '' or regression_data['sellIndia'] != ''):
        filterName = pct_change_filter(regression_data, regressionResult, False)
        filterNameTail = tail_change_filter(regression_data, regressionResult, False)
        pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
        regression_data['filterTest'] = filterName + ',' \
                                        + filterNameTail + ',' \
                                        + pctChange5Day + ',' \
                                        + 'B@{' + regression_data['buyIndia'] + '}' \
                                        + 'S@{' + regression_data['sellIndia'] + '}' \
                                        + regression_data['filter2'] + ',' \
                                        + regression_data['filter3'] + ',' \
                                        + regression_data['filter5']
        return True
    
    return False

def sell_test_tech_all_pct_change(regression_data, regressionResult, reg, ws):
    regression_data['filterbuy'] = " "
    regression_data['filtersell'] = " "
    regression_data['filter'] = " "
    regression_data['filter1'] = " "
    regression_data['filter2'] = " "
    regression_data['filter3'] = " "
    regression_data['filter4'] = " "
    regression_data['filter5'] = " "
    regression_data['filter6'] = " "
    regression_data['series_trend'] = trend_calculator(regression_data)
    flag = buy_other_indicator(regression_data, regressionResult, reg, ws)
    if (regression_data['buyIndia'] != '' or regression_data['sellIndia'] != ''):
        filterName = pct_change_filter(regression_data, regressionResult, False)
        filterNameTail = tail_change_filter(regression_data, regressionResult, False)
        pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
        regression_data['filterTest'] = filterName + ',' \
                                        + filterNameTail + ',' \
                                        + pctChange5Day + ',' \
                                        + 'B@{' + regression_data['buyIndia'] + '}' \
                                        + 'S@{' + regression_data['sellIndia'] + '}' \
                                        + regression_data['filter4'] + ',' \
                                        + regression_data['filter5']
        return True
    
    return False
      
def sell_all_filter(regression_data, regressionResult, reg, ws):
    flag = False
    if sell_year_high(regression_data, regressionResult, reg, None, None):
        add_in_csv(regression_data, regressionResult, ws, None, None, None)
        flag = True
    if sell_year_low(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws, None, None, None)
        flag = True
    if sell_up_trend(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws, None, None, None)
        flag = True
    if sell_down_trend(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws, None, None, None)
        flag = True
    if sell_final(regression_data, regressionResult, reg, None, None):
        add_in_csv(regression_data, regressionResult, ws, None, None, None)
        flag = True
    if sell_oi(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws, None, None, None)
        flag = True
    return flag

def sell_filter_st_accuracy(regression_data, regressionResult):
    filtersDict = filterstsell
    filter = regression_data['filter'] + ',' + regression_data['filter1']
    if (filter != '') and (filter in filtersDict):
        if float(filtersDict[filter]['count']) >= 3:
            if abs(float(filtersDict[filter]['avg5'])) >= 5 and abs(float(filtersDict[filter]['avg10'])) > abs(
                    float(filtersDict[filter]['avg5'])):
                regression_data['filterst_avg5'] = float(filtersDict[filter]['avg5'])
                regression_data['filterst_avg10'] = float(filtersDict[filter]['avg10'])
                regression_data['filterst_count'] = float(filtersDict[filter]['count'])
                if float(filtersDict[filter]['avg5']) >= 0:
                    regression_data['filterst_pct5'] = (float(filtersDict[filter]['countgt5']) * 100) / float(
                        filtersDict[filter]['count'])
                    regression_data['filterst_pct10'] = (float(filtersDict[filter]['countgt10']) * 100) / float(
                        filtersDict[filter]['count'])
                else:
                    regression_data['filterst_pct5'] = -(float(filtersDict[filter]['countlt5']) * 100) / float(
                        filtersDict[filter]['count'])
                    regression_data['filterst_pct10'] = -(float(filtersDict[filter]['countlt10']) * 100) / float(
                        filtersDict[filter]['count'])
                insert_scripdata_st(regression_data['scrip'],
                                    regression_data['date'],
                                    filter,
                                    regression_data['filterst_avg5'],
                                    regression_data['filterst_pct5'],
                                    regression_data['filterst_avg10'],
                                    regression_data['filterst_pct10'],
                                    regression_data['filterst_count'],
                                    regression_data
                                    )
    filtersDict = filter3stsell
    filter = regression_data['filter'] + ',' + regression_data['filter3']
    if (filter != '') and (filter in filtersDict):
        if float(filtersDict[filter]['count']) >= 3:
            if abs(float(filtersDict[filter]['avg5'])) >= 5 and abs(float(filtersDict[filter]['avg10'])) > abs(
                    float(filtersDict[filter]['avg5'])):
                regression_data['filter3st_avg5'] = float(filtersDict[filter]['avg5'])
                regression_data['filter3st_avg10'] = float(filtersDict[filter]['avg10'])
                regression_data['filter3st_count'] = float(filtersDict[filter]['count'])
                if float(filtersDict[filter]['avg5']) >= 0:
                    regression_data['filter3st_pct5'] = (float(filtersDict[filter]['countgt5']) * 100) / float(
                        filtersDict[filter]['count'])
                    regression_data['filter3st_pct10'] = (float(filtersDict[filter]['countgt10']) * 100) / float(
                        filtersDict[filter]['count'])
                else:
                    regression_data['filter3st_pct5'] = -(float(filtersDict[filter]['countlt5']) * 100) / float(
                        filtersDict[filter]['count'])
                    regression_data['filter3st_pct10'] = -(float(filtersDict[filter]['countlt10']) * 100) / float(
                        filtersDict[filter]['count'])
                insert_scripdata_st(regression_data['scrip'],
                                    regression_data['date'],
                                    filter,
                                    regression_data['filter3st_avg5'],
                                    regression_data['filter3st_pct5'],
                                    regression_data['filter3st_avg10'],
                                    regression_data['filter3st_pct10'],
                                    regression_data['filter3st_count'],
                                    regression_data
                                    )
    filtersDict = filter4stsell
    filter = regression_data['filter4']
    if (filter != '') and (filter in filtersDict):
        if float(filtersDict[filter]['count']) >= 3:
            if abs(float(filtersDict[filter]['avg5'])) >= 5 and abs(float(filtersDict[filter]['avg10'])) > abs(
                    float(filtersDict[filter]['avg5'])):
                regression_data['filter4st_avg5'] = float(filtersDict[filter]['avg5'])
                regression_data['filter4st_avg10'] = float(filtersDict[filter]['avg10'])
                regression_data['filter4st_count'] = float(filtersDict[filter]['count'])
                if float(filtersDict[filter]['avg5']) >= 0:
                    regression_data['filter4st_pct5'] = (float(filtersDict[filter]['countgt5']) * 100) / float(
                        filtersDict[filter]['count'])
                    regression_data['filter4st_pct10'] = (float(filtersDict[filter]['countgt10']) * 100) / float(
                        filtersDict[filter]['count'])
                else:
                    regression_data['filter4st_pct5'] = -(float(filtersDict[filter]['countlt5']) * 100) / float(
                        filtersDict[filter]['count'])
                    regression_data['filter4st_pct10'] = -(float(filtersDict[filter]['countlt10']) * 100) / float(
                        filtersDict[filter]['count'])
                insert_scripdata_st(regression_data['scrip'],
                                    regression_data['date'],
                                    filter,
                                    regression_data['filter4st_avg5'],
                                    regression_data['filter4st_pct5'],
                                    regression_data['filter4st_avg10'],
                                    regression_data['filter4st_pct10'],
                                    regression_data['filter4st_count'],
                                    regression_data
                                    )


def sell_filter_345_accuracy(regression_data, regressionResult):
    filtersDict = filter345sell
    filterName = pct_change_filter(regression_data, regressionResult, False)
    filterNameTail = tail_change_filter(regression_data, regressionResult, False)
    pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
    filter = filterName + ',' \
            + filterNameTail + ',' \
            + pctChange5Day + ',' \
            + regression_data['series_trend'] + ',' \
            + regression_data['filter1'] + ',' \
            + regression_data['filter3']
                
    if (filter != '') and (filter in filtersDict):
        regression_data['filter_345_avg'] = float(filtersDict[filter]['avg'])
        regression_data['filter_345_count'] = float(filtersDict[filter]['count'])
        if float(filtersDict[filter]['count']) >= 2:
            if float(filtersDict[filter]['avg']) >= 0:
                regression_data['filter_345_pct'] = (float(filtersDict[filter]['countgt'])*100)/float(filtersDict[filter]['count'])
            else:
                regression_data['filter_345_pct'] = -(float(filtersDict[filter]['countlt'])*100)/float(filtersDict[filter]['count'])
                
def sell_filter_accuracy(regression_data, regressionResult):
    filtersDict=filtersell
    filterName = pct_change_filter(regression_data, regressionResult, False)
    filterNameTail = tail_change_filter(regression_data, regressionResult, False)
    pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
    filter = filterName + ',' \
            + filterNameTail + ',' \
            + pctChange5Day + ',' \
            + regression_data['series_trend'] + ',' \
            + regression_data['filter2'] + ',' \
            + regression_data['filter4'] + ',' \
            + regression_data['filter5']
            
    if filter != '' and filter in filtersDict:
        regression_data['filter_avg'] = float(filtersDict[filter]['avg'])
        regression_data['filter_count'] = float(filtersDict[filter]['count'])
        if float(filtersDict[filter]['count']) >= 2:
            if float(filtersDict[filter]['avg']) >= 0:
                regression_data['filter_pct'] = (float(filtersDict[filter]['countgt'])*100)/float(filtersDict[filter]['count'])
            else:
                regression_data['filter_pct'] = -(float(filtersDict[filter]['countlt'])*100)/float(filtersDict[filter]['count'])
                     
def sell_filter_pct_change_accuracy(regression_data, regressionResult):
    filtersDict=filterpctchangesell
    filtercombine =  regression_data['filterbuy'].replace("[MLBuy]:", "").replace("[MLSell]:", "").strip() + ',' \
                + regression_data['filtersell'].replace("[MLBuy]:", "").replace("[MLSell]:", "").strip() + ',' \
                + regression_data['filter'].replace("[MLBuy]:", "").replace("[MLSell]:", "").strip()
    if filtercombine != ",,":
        filterName = pct_change_filter(regression_data, regressionResult, False)
        filterNameTail = tail_change_filter(regression_data, regressionResult, False)
        pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
        filter = filterName + ',' \
                + filterNameTail + ',' \
                + filtercombine
        if filter != '' and filter in filtersDict:
            regression_data['filter_pct_change_avg'] = float(filtersDict[filter]['avg'])
            regression_data['filter_pct_change_count'] = float(filtersDict[filter]['count'])
            if float(filtersDict[filter]['count']) >= 2:
                if float(filtersDict[filter]['avg']) >= 0:
                    regression_data['filter_pct_change_pct'] = (float(filtersDict[filter]['countgt'])*100)/float(filtersDict[filter]['count'])
                else:
                    regression_data['filter_pct_change_pct'] = -(float(filtersDict[filter]['countlt'])*100)/float(filtersDict[filter]['count'])

def sell_filter_345_all_accuracy(regression_data, regressionResult):
    filtersDict=filterallsell
    filterName = pct_change_filter(regression_data, regressionResult, False)
    filterNameTail = tail_change_filter(regression_data, regressionResult, False)
    pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
    filterOrFilter3 = regression_data['filterbuy'].replace("[MLBuy]:", "").replace("[MLSell]:", "").strip() + ',' \
                      + regression_data['filtersell'].replace("[MLBuy]:", "").replace("[MLSell]:", "").strip() + ',' \
                      + regression_data['filter'].replace("[MLBuy]:", "").replace("[MLSell]:", "").strip()
    if(filterOrFilter3 == ",,"):
        filterOrFilter3 = regression_data['filter3'] + ',' \
                          + regression_data['filter4']
        
    filter = filterName + ',' \
                + filterNameTail + ',' \
                + regression_data['series_trend'] + ',' \
                + pctChange5Day + ','\
                + regression_data['filter2'] + ',' \
                + filterOrFilter3 + ','\
                + regression_data['filter5'] 
                        
    if (filter != '') and (filter in filtersDict):
        regression_data['filter_all_avg'] = float(filtersDict[filter]['avg'])
        regression_data['filter_all_count'] = float(filtersDict[filter]['count'])
        if float(filtersDict[filter]['count']) >= 2:
            if float(filtersDict[filter]['avg']) >= 0:
                regression_data['filter_all_pct'] = (float(filtersDict[filter]['countgt'])*100)/float(filtersDict[filter]['count'])
            else:
                regression_data['filter_all_pct'] = -(float(filtersDict[filter]['countlt'])*100)/float(filtersDict[filter]['count'])

def sell_filter_tech_accuracy(regression_data, regressionResult):
    filtersDict=filtertechsell
    filterName = pct_change_filter(regression_data, regressionResult, False)
    filterNameTail = tail_change_filter(regression_data, regressionResult, False)
    pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
    filter = filterName + ',' \
            + filterNameTail + ',' \
            + regression_data['series_trend'] + ',' \
            + 'B@{' + regression_data['buyIndia'] + '}' \
            + 'S@{' + regression_data['sellIndia'] + '}'
    if (filter != '') and (filter in filtersDict):
        regression_data['filter_tech_avg'] = float(filtersDict[filter]['avg'])
        regression_data['filter_tech_count'] = float(filtersDict[filter]['count'])
        if float(filtersDict[filter]['count']) >= 2:
            if float(filtersDict[filter]['avg']) >= 0:
                regression_data['filter_tech_pct'] = (float(filtersDict[filter]['countgt'])*100)/float(filtersDict[filter]['count'])
            else:
                regression_data['filter_tech_pct'] = -(float(filtersDict[filter]['countlt'])*100)/float(filtersDict[filter]['count'])

def sell_filter_tech_all_accuracy(regression_data, regressionResult):
    filtersDict=filtertechallsell
    filterName = pct_change_filter(regression_data, regressionResult, False)
    filterNameTail = tail_change_filter(regression_data, regressionResult, False)
    pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
    filter = filterName + ',' \
            + filterNameTail + ',' \
            + pctChange5Day + ',' \
            + 'B@{' + regression_data['buyIndia'] + '}' \
            + 'S@{' + regression_data['sellIndia'] + '}' \
            + regression_data['filter2'] + ',' \
            + regression_data['filter3'] + ',' \
            + regression_data['filter5']
            
    if (filter != '') and (filter in filtersDict):
        regression_data['filter_tech_all_avg'] = float(filtersDict[filter]['avg'])
        regression_data['filter_tech_all_count'] = float(filtersDict[filter]['count'])
        if float(filtersDict[filter]['count']) >= 2:
            if float(filtersDict[filter]['avg']) >= 0:
                regression_data['filter_tech_all_pct'] = (float(filtersDict[filter]['countgt'])*100)/float(filtersDict[filter]['count'])
            else:
                regression_data['filter_tech_all_pct'] = -(float(filtersDict[filter]['countlt'])*100)/float(filtersDict[filter]['count'])

def sell_filter_tech_all_pct_change_accuracy(regression_data, regressionResult):
    filtersDict=filtertechallpctchangesell
    filterName = pct_change_filter(regression_data, regressionResult, False)
    filterNameTail = tail_change_filter(regression_data, regressionResult, False)
    pctChange5Day = pct_change_filter_days(regression_data, regressionResult, False)
    filter = filterName + ',' \
            + filterNameTail + ',' \
            + pctChange5Day + ',' \
            + 'B@{' + regression_data['buyIndia'] + '}' \
            + 'S@{' + regression_data['sellIndia'] + '}' \
            + regression_data['filter4'] + ',' \
            + regression_data['filter5']
            
    if (filter != '') and (filter in filtersDict):
        regression_data['filter_tech_all_pct_change_avg'] = float(filtersDict[filter]['avg'])
        regression_data['filter_tech_all_pct_change_count'] = float(filtersDict[filter]['count'])
        if float(filtersDict[filter]['count']) >= 2:
            if float(filtersDict[filter]['avg']) >= 0:
                regression_data['filter_tech_all_pct_change_pct'] = (float(filtersDict[filter]['countgt'])*100)/float(filtersDict[filter]['count'])
            else:
                regression_data['filter_tech_all_pct_change_pct'] = -(float(filtersDict[filter]['countlt'])*100)/float(filtersDict[filter]['count'])

def sell_filter_all_accuracy(regression_data, regressionResult):
    if(regression_data['close'] > CLOSEPRICE):
        sell_filter_st_accuracy(regression_data, regressionResult)
        sell_filter_345_accuracy(regression_data, regressionResult)
        sell_filter_accuracy(regression_data, regressionResult)
        sell_filter_pct_change_accuracy(regression_data, regressionResult) 
        sell_filter_345_all_accuracy(regression_data, regressionResult)
        sell_filter_tech_accuracy(regression_data, regressionResult)
        sell_filter_tech_all_accuracy(regression_data, regressionResult)
        sell_filter_tech_all_pct_change_accuracy(regression_data, regressionResult)
        
def is_reg_buy_from_filter(regression_data, filter_avg, filter_count, filter_pct):
    if(regression_data[filter_avg] > 1.5
        and regression_data[filter_count] > 1
        and regression_data[filter_pct] >= 90
        ):
        return True
    else:
        return False
   
def is_reg_sell_from_filter(regression_data, filter_avg, filter_count, filter_pct):
    if(regression_data[filter_avg] < -1.5
        and regression_data[filter_count] > 1
        and regression_data[filter_pct] <= -90
        ):
        return True
    else:
        return False

def filter_avg_gt_count(regression_data, val):
    count = 0
    cnt = 0
    max = 0
    if(regression_data['filter_345_avg'] > val
        and (regression_data['filter_345_pct'] >= 66 or regression_data['filter_345_pct'] == 0)
        and regression_data['filter_345_avg'] != regression_data['filter_all_avg']
        ):
        count = count + 1
        cnt = cnt + regression_data['filter_345_count']
        if max < regression_data['filter_345_count']:
            max = regression_data['filter_345_count']
    if(regression_data['filter_avg'] > val
        and (regression_data['filter_pct'] >= 66 or regression_data['filter_pct'] == 0)
        and regression_data['filter_avg'] != regression_data['filter_all_avg']
        ):
        count = count + 1
        cnt = cnt + regression_data['filter_count']
        if max < regression_data['filter_count']:
            max = regression_data['filter_count']
    if(regression_data['filter_pct_change_avg'] > val
        and (regression_data['filter_pct_change_pct'] >= 66 or regression_data['filter_pct_change_pct'] == 0)
        ):
        count = count + 1
        cnt = cnt + regression_data['filter_pct_change_count']
        if max < regression_data['filter_pct_change_count']:
            max = regression_data['filter_pct_change_count']
    if(regression_data['filter_all_avg'] > val
        and (regression_data['filter_all_pct'] >= 66 or regression_data['filter_all_pct'] == 0)
        ):
        count = count + 1
        cnt = cnt + regression_data['filter_all_count']
        if max < regression_data['filter_all_count']:
            max = regression_data['filter_all_count']
    if(regression_data['filter_tech_avg'] > val
        and (regression_data['filter_tech_pct'] >= 70 or regression_data['filter_tech_pct'] == 0)
        ):
        count = count + 1
        cnt = cnt + regression_data['filter_tech_count']
        if max < regression_data['filter_tech_count']:
            max = regression_data['filter_tech_count']
    if(regression_data['filter_tech_all_avg'] > 3
        and (regression_data['filter_tech_all_pct'] >= 70 or regression_data['filter_tech_all_pct'] == 0)
        ):
        count = count + 1
        cnt = cnt + regression_data['filter_tech_all_count']
        if max < regression_data['filter_tech_all_count']:
            max = regression_data['filter_tech_all_count']
    if(regression_data['filter_tech_all_pct_change_avg'] > 3
        and (regression_data['filter_tech_all_pct_change_pct'] >= 70 or regression_data['filter_tech_all_pct_change_pct'] == 0)
        ):
        count = count + 1
        cnt = cnt + regression_data['filter_tech_all_pct_change_count']
        if max < regression_data['filter_tech_all_pct_change_count']:
            max = regression_data['filter_tech_all_pct_change_count']
    return count, cnt, max
    
def filter_avg_lt_count(regression_data, val):
    count = 0
    cnt = 0
    max = 0
    if(regression_data['filter_345_avg'] < val
        and (regression_data['filter_345_pct'] < -66 or regression_data['filter_345_pct'] == 0)
        and regression_data['filter_345_avg'] != regression_data['filter_all_avg']
        ):
        count = count + 1
        cnt = cnt + regression_data['filter_345_count']
        if max < regression_data['filter_345_count']:
            max = regression_data['filter_345_count']
    if(regression_data['filter_avg'] < val
        and (regression_data['filter_pct'] < -66 or regression_data['filter_pct'] == 0)
        and regression_data['filter_avg'] != regression_data['filter_all_avg']
        ):
        count = count + 1
        cnt = cnt + regression_data['filter_count']
        if max < regression_data['filter_count']:
            max = regression_data['filter_count']
    if(regression_data['filter_pct_change_avg'] < val
        and (regression_data['filter_pct_change_pct'] < -66 or regression_data['filter_pct_change_pct'] == 0)
        ):
        count = count + 1
        cnt = cnt + regression_data['filter_pct_change_count']
        if max < regression_data['filter_pct_change_count']:
            max = regression_data['filter_pct_change_count']
    if(regression_data['filter_all_avg'] < val
        and (regression_data['filter_all_pct'] < -66 or regression_data['filter_all_pct'] == 0)
        ):
        count = count + 1
        cnt = cnt + regression_data['filter_all_count']
        if max < regression_data['filter_all_count']:
            max = regression_data['filter_all_count']
    if(regression_data['filter_tech_avg'] < val
        and (regression_data['filter_tech_pct'] < -70 or regression_data['filter_tech_pct'] == 0)
        ):
        count = count + 1
        cnt = cnt + regression_data['filter_tech_count']
        if max < regression_data['filter_tech_count']:
            max = regression_data['filter_tech_count']
    if(regression_data['filter_tech_all_avg'] < -3
        and (regression_data['filter_tech_all_pct'] < -70 or regression_data['filter_tech_all_pct'] == 0)
        ):
        count = count + 1
        cnt = cnt + regression_data['filter_tech_all_count']
        if max < regression_data['filter_tech_all_count']:
            max = regression_data['filter_tech_all_count']
    if(regression_data['filter_tech_all_pct_change_avg'] < -3
        and (regression_data['filter_tech_all_pct_change_pct'] < -70 or regression_data['filter_tech_all_pct_change_pct'] == 0)
        ):
        count = count + 1
        cnt = cnt + regression_data['filter_tech_all_pct_change_count']
        if max < regression_data['filter_tech_all_pct_change_count']:
            max = regression_data['filter_tech_all_pct_change_count']
    return count, cnt, max

def filter_avg_gt_point9_count(regression_data):
    count = 0
    cnt = 0
    max = 0
    count, cnt, max = filter_avg_gt_count(regression_data, 0.9)
    if(cnt > 1):
        return count
    else:
        return 0
    
def filter_avg_lt_minus_point9_count(regression_data):
    count = 0
    cnt = 0
    max = 0
    count, cnt, max = filter_avg_lt_count(regression_data, -0.9)
    if(cnt > 1):
        return count
    else:
        return 0

def filter_avg_gt_1_count(regression_data):
    count = 0
    cnt = 0
    max = 0
    count, cnt, max = filter_avg_gt_count(regression_data, 1)
    if(cnt > 1):
        return count
    else:
        return 0
    
def filter_avg_lt_minus_1_count(regression_data):
    count = 0
    cnt = 0
    max = 0
    count, cnt, max = filter_avg_lt_count(regression_data, -1)
    if(cnt > 1):
        return count
    else:
        return 0

def filter_avg_gt_2_count(regression_data):
    count = 0
    cnt = 0
    max = 0
    count, cnt, max = filter_avg_gt_count(regression_data, 2)
    if(cnt > 1):
        return count
    else:
        return 0
    
def filter_avg_lt_minus_2_count(regression_data):
    count = 0
    cnt = 0
    max = 0
    count, cnt, max = filter_avg_lt_count(regression_data, -2)
    if(cnt > 1):
        return count
    else:
        return 0
 
def filter_avg_gt_1_count_any(regression_data):
    count = 0
    cnt = 0
    max = 0
    count, cnt, max = filter_avg_gt_count(regression_data, 1)
    return count, cnt, max
    
def filter_avg_lt_minus_1_count_any(regression_data):
    count = 0
    cnt = 0
    max = 0
    count, cnt, max = filter_avg_lt_count(regression_data, -1)
    return count, cnt, max

def filter_avg_gt_2_count_any(regression_data):
    count = 0
    cnt = 0
    max = 0
    count, cnt, max = filter_avg_gt_count(regression_data, 2)
    return count, cnt, max
    
def filter_avg_lt_minus_2_count_any(regression_data):
    count = 0
    cnt = 0
    max = 0
    count, cnt, max = filter_avg_lt_count(regression_data, -2)
    return count, cnt, max
 
def is_any_buy_GT2_from_all_filter(regression_data):
    if(is_buy_GT2_from_filter(regression_data, 'filter_345_avg', 'filter_345_count', 'filter_345_pct')
        or is_buy_GT2_from_filter(regression_data, 'filter_avg', 'filter_count', 'filter_pct')
        or is_buy_GT2_from_filter(regression_data, 'filter_pct_change_avg', 'filter_pct_change_count', 'filter_pct_change_pct')
        or is_buy_GT2_from_filter(regression_data, 'filter_all_avg', 'filter_all_count', 'filter_all_pct')
        or is_buy_GT2_from_filter(regression_data, 'filter_tech_avg', 'filter_tech_count', 'filter_tech_pct')
        or is_buy_GT2_from_filter(regression_data, 'filter_tech_all_avg', 'filter_tech_all_count', 'filter_tech_all_pct')
        or is_buy_GT2_from_filter(regression_data, 'filter_tech_all_pct_change_avg', 'filter_tech_all_pct_change_count', 'filter_tech_all_pct_change_pct')
        ):
        return True
    else:
        return False
       
def is_any_sell_LTMinus2_from_all_filter_(regression_data):
    if(is_sell_LTMinus2_from_filter(regression_data, 'filter_345_avg', 'filter_345_count', 'filter_345_pct')
        or is_sell_LTMinus2_from_filter(regression_data, 'filter_avg', 'filter_count', 'filter_pct')
        or is_sell_LTMinus2_from_filter(regression_data, 'filter_pct_change_avg', 'filter_pct_change_count', 'filter_pct_change_pct')
        or is_sell_LTMinus2_from_filter(regression_data, 'filter_all_avg', 'filter_all_count', 'filter_all_pct')
        or is_sell_LTMinus2_from_filter(regression_data, 'filter_tech_avg', 'filter_tech_count', 'filter_tech_pct')
        or is_sell_LTMinus2_from_filter(regression_data, 'filter_tech_all_avg', 'filter_tech_all_count', 'filter_tech_all_pct')
        or is_sell_LTMinus2_from_filter(regression_data, 'filter_tech_all_pct_change_avg', 'filter_tech_all_pct_change_count', 'filter_tech_all_pct_change_pct')
        ):
        return True
    else:
        return False                      
                       
def is_buy_GT2_from_filter(regression_data, filter_avg, filter_count, filter_pct):
    if(regression_data[filter_avg] > 2 and regression_data[filter_pct] >= 60):
        return True
    else:
        return False
   
def is_sell_LTMinus2_from_filter(regression_data, filter_avg, filter_count, filter_pct):
    if(regression_data[filter_avg] < -2 and regression_data[filter_pct] <= -60):
        return True
    else:
        return False

def is_any_buy_from_all_filter(regression_data):
    if(is_buy_from_filter(regression_data, 'filter_345_avg', 'filter_345_count', 'filter_345_pct')
        or is_buy_from_filter(regression_data, 'filter_avg', 'filter_count', 'filter_pct')
        or is_buy_from_filter(regression_data, 'filter_pct_change_avg', 'filter_pct_change_count', 'filter_pct_change_pct')
        or is_buy_from_filter(regression_data, 'filter_all_avg', 'filter_all_count', 'filter_all_pct')
        or is_buy_from_filter(regression_data, 'filter_tech_avg', 'filter_tech_count', 'filter_tech_pct')
        or is_buy_from_filter(regression_data, 'filter_tech_all_avg', 'filter_tech_all_count', 'filter_tech_all_pct')
        ):
        return True
    else:
        return False
       
def is_any_sell_from_all_filter(regression_data):
    if(is_sell_from_filter(regression_data, 'filter_345_avg', 'filter_345_count', 'filter_345_pct')
        or is_sell_from_filter(regression_data, 'filter_avg', 'filter_count', 'filter_pct')
        or is_sell_from_filter(regression_data, 'filter_pct_change_avg', 'filter_pct_change_count', 'filter_pct_change_pct')
        or is_sell_from_filter(regression_data, 'filter_all_avg', 'filter_all_count', 'filter_all_pct')
        or is_sell_from_filter(regression_data, 'filter_tech_avg', 'filter_tech_count', 'filter_tech_pct')
        or is_sell_from_filter(regression_data, 'filter_tech_all_avg', 'filter_tech_all_count', 'filter_tech_all_pct')
        ):
        return True
    else:
        return False                      
                       
def is_buy_from_filter(regression_data, filter_avg, filter_count, filter_pct):
    if((regression_data[filter_avg] > 3 and regression_data[filter_pct] == 0)
       or (regression_data[filter_avg] > 1 and regression_data[filter_pct] >= 80)
       or (regression_data[filter_avg] > 0.75 and regression_data[filter_pct] >= 70 and regression_data[filter_count] >= 3)
       ):
        return True
    else:
        return False
   
def is_sell_from_filter(regression_data, filter_avg, filter_count, filter_pct):
    if((regression_data[filter_avg] < -3 and regression_data[filter_pct] == 0)
       or (regression_data[filter_avg] < -1 and regression_data[filter_pct] <= -80)
       or (regression_data[filter_avg] < -0.75 and regression_data[filter_pct] <= -70 and regression_data[filter_count] >= 3)
       ):
        return True
    else:
        return False
        
def is_buy_filter_not_risky(regression_data):
    if((high_tail_pct(regression_data) < 2 or high_tail_pct(regression_data) > 4
            or (regression_data['PCT_day_change'] < 0 and regression_data['PCT_change'] < 0)
        )
#         and (high_tail_pct(regression_data) < 1 
#             or (regression_data['PCT_day_change'] < 0 and regression_data['PCT_change'] < 0)
#             or ("MLBuy" in regression_data['filter'])
#         )
       ):
        return True

def is_sell_filter_not_risky(regression_data):
    if((low_tail_pct(regression_data) < 2 or low_tail_pct(regression_data) > 4
             or (regression_data['PCT_day_change'] > 0 and regression_data['PCT_change'] > 0)
             )
#         and (low_tail_pct(regression_data) < 1
#              or (regression_data['PCT_day_change'] > 0 and regression_data['PCT_change'] > 0)
#              or ("MLSell" in regression_data['filter'])
#              )
       ):
        return True

def is_reg_buy_pct_filter(regression_data):
    if(2< regression_data['PCT_day_change']):
        return False
    elif(regression_data['PCT_day_change'] < 2 
        or (regression_data['PCT_day_change'] > 5.5 and regression_data['PCT_change'] > regression_data['PCT_day_change']
            and regression_data['monthHighChange'] > 0
            )
        ):
        return True
    else:
        return False

def is_reg_sell_pct_filter(regression_data):
    if(regression_data['PCT_day_change'] < -2):
        return False
    elif(regression_data['PCT_day_change'] > -2 
        or (regression_data['PCT_day_change'] < -5.5 and regression_data['PCT_change'] > regression_data['PCT_day_change']
            and regression_data['monthLowChange'] < 0
            )
        ):
        return True
    else:
        return False
    
def is_filter_hist_accuracy(regression_data, regression_high, regression_low, regressionResult, high_or_low, ws):
    pct_filter_345_avg = 0
    pct_filter_avg = 0
    pct_filter_pct_change_avg = 0
    pct_filter_all_avg = 0

    lt_minus_2_count_any, lt_minus_2_cnt, lt_minus_2_max = filter_avg_lt_minus_2_count_any(regression_data)
    lt_minus_1_count_any, lt_minus_1_cnt, lt_minus_1_max = filter_avg_lt_minus_1_count_any(regression_data)
    gt_2_count_any, gt_2_cnt, gt_2_max = filter_avg_gt_2_count_any(regression_data)
    gt_1_count_any, gt_1_cnt, gt_2_max = filter_avg_gt_1_count_any(regression_data)
    if(((lt_minus_2_count_any == 1 and lt_minus_2_cnt > 5 and gt_2_cnt < 2 and gt_1_cnt < 3)
        or (lt_minus_2_count_any > 1 and lt_minus_2_max > 5 and gt_2_cnt < 2 and gt_1_cnt < 3)
        or (lt_minus_2_count_any > 1 and lt_minus_2_cnt > 9 and gt_2_cnt < 2 and gt_1_cnt < 3))
        ):
        return True
    elif(
        ((gt_2_count_any == 1 and gt_2_cnt > 5 and lt_minus_2_cnt < 2 and lt_minus_1_cnt < 3)
        or (gt_2_count_any > 1 and gt_2_max > 5 and lt_minus_2_cnt < 2 and lt_minus_1_cnt < 3)
        or (gt_2_count_any > 1 and gt_2_cnt > 9 and lt_minus_2_cnt < 2 and lt_minus_1_cnt < 3))
        ):
        return True
    else:
        return False
         
def is_filter_all_accuracy(regression_data, regression_high, regression_low, regressionResult, high_or_low, ws):
    pct_filter_345_avg = 0
    pct_filter_avg = 0
    pct_filter_pct_change_avg = 0
    pct_filter_all_avg = 0
    if(regression_data['PCT_day_change'] != 0):
        pct_filter_345_avg = ((regression_data['filter_345_avg'] - regression_data['PCT_day_change'])*100)/abs(regression_data['PCT_day_change'])
        pct_filter_avg = ((regression_data['filter_avg'] - regression_data['PCT_day_change'])*100)/abs(regression_data['PCT_day_change'])
        pct_filter_pct_change_avg = ((regression_data['filter_pct_change_avg'] - regression_data['PCT_day_change'])*100)/abs(regression_data['PCT_day_change'])
        pct_filter_all_avg = ((regression_data['filter_all_avg'] - regression_data['PCT_day_change'])*100)/abs(regression_data['PCT_day_change'])

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
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'RISKY-DOWNTREND-BUY') 
    elif(-5.5 < regression_data['PCT_day_change'] < 0
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
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'RISKY-UPTREND-SELL')

    lt_minus_2_count_any, lt_minus_2_cnt, lt_minus_2_max = filter_avg_lt_minus_2_count_any(regression_data)
    lt_minus_1_count_any, lt_minus_1_cnt, lt_minus_1_max = filter_avg_lt_minus_1_count_any(regression_data)
    gt_2_count_any, gt_2_cnt, gt_2_max = filter_avg_gt_2_count_any(regression_data)
    gt_1_count_any, gt_1_cnt, gt_1_max = filter_avg_gt_1_count_any(regression_data)
    if(lt_minus_2_count_any >= 1
        ):
        if(regression_data['PCT_day_change'] < -2 or regression_data['PCT_change'] < -2):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'Sell-Risky')
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'Sell-AnyGT2-' + str(lt_minus_2_cnt)) 
    else:
        if(lt_minus_1_count_any >= 1
            ):
            if(regression_data['PCT_day_change'] < -2 or regression_data['PCT_change'] < -2):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'Sell-Risky')
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'Sell-Any-' + str(lt_minus_1_cnt))
            
        
    if(gt_2_count_any >= 1
        ):
        if(regression_data['PCT_day_change'] > 2 or regression_data['PCT_change'] > 2):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'Buy-Risky')
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'Buy-AnyGT2-' + str(gt_2_cnt))    
    else:
        if(gt_1_count_any >= 1
            ):
            if(regression_data['PCT_day_change'] > 2 or regression_data['PCT_change'] > 2):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'Buy-Risky')
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'Buy-Any-' + str(gt_1_cnt))
    
    
    if(filter_avg_lt_minus_1_count(regression_data) >= 2
        and 'RISKYBASELINESELL' not in regression_data['filter5']
        ):
        if(regression_data['PCT_day_change'] < 0
            and ((pct_filter_345_avg < 10 and regression_data['filter_345_pct'] < -60)
                or (pct_filter_avg < 10 and regression_data['filter_pct'] < -60)
                or (pct_filter_pct_change_avg < 10 and regression_data['filter_pct_change_pct'] < -60)
                or (pct_filter_all_avg < 10 and regression_data['filter_all_pct'] < -60)
            )
            and "MLBuy" not in regression_data['filter']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'Sell-SUPER') 
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'Sell-SUPER-Risky')  
    elif(filter_avg_gt_1_count(regression_data) >= 2
        and 'RISKYBASELINEBUY' not in regression_data['filter5']
        ):
        if(regression_data['PCT_day_change'] > 0
            and ((pct_filter_345_avg > -10 and regression_data['filter_345_pct'] > 60)
                or (pct_filter_avg > -10 and regression_data['filter_pct'] > 60)
                or (pct_filter_pct_change_avg > -10 and regression_data['filter_pct_change_pct'] > 60)
                or (pct_filter_pct_change_avg > -10 and regression_data['filter_all_pct'] > 60)
            )
            and "MLSell" not in regression_data['filter']
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'Buy-SUPER')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'Buy-SUPER-risky')
#     elif(filter_avg_lt_minus_point9_count(regression_data) >= 2
#        and 'RISKYBASELINESELL' not in regression_data['filter5']
#        and "MLBuy" in regression_data['filter']
#       ):
#        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'LT-0.9-Sell-SUPER-Risky')  
#     elif(filter_avg_gt_point9_count(regression_data) >= 2
#        and 'RISKYBASELINEBUY' not in regression_data['filter5']
#        and "MLSell" in regression_data['filter']
#        ):
#        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, 'GT0.9-Buy-SUPER-risky')
    
    
    superflag = False
    flag = filter_accuracy_finder_all(regression_data, regression_high, regression_low, regressionResult, high_or_low, ws, 'filter_345_avg', 'filter_345_count', 'filter_345_pct')
    if(flag):
        superflag = True
    flag = filter_accuracy_finder_all(regression_data, regression_high, regression_low, regressionResult, high_or_low, ws, 'filter_avg', 'filter_count', 'filter_pct')
    if(flag):
        superflag = True
    flag = filter_accuracy_finder_all(regression_data, regression_high, regression_low, regressionResult, high_or_low, ws, 'filter_pct_change_avg', 'filter_pct_change_count', 'filter_pct_change_pct')
    if(flag):
        superflag = True
    flag = filter_accuracy_finder_all(regression_data, regression_high, regression_low, regressionResult, high_or_low, ws, 'filter_all_avg', 'filter_all_count', 'filter_all_pct')
    if(flag):
        superflag = True
    if(regression_data['filter_tech_count'] > 5):
        flag = filter_accuracy_finder_all(regression_data, regression_high, regression_low, regressionResult, high_or_low, ws, 'filter_tech_avg', 'filter_tech_count', 'filter_tech_pct')
        if(flag):
            superflag = True
    if((abs(regression_data['filter_tech_all_avg']) > 2 and regression_data['filter_tech_all_count'] >= 4) or abs(regression_data['filter_tech_all_avg']) > 4 or regression_data['filter_tech_all_avg'] > 5):
        flag = filter_accuracy_finder_all(regression_data, regression_high, regression_low, regressionResult, high_or_low, ws, 'filter_tech_all_avg', 'filter_tech_all_count', 'filter_tech_all_pct')
        if(flag):
            superflag = True
    if((abs(regression_data['filter_tech_all_pct_change_avg']) > 2 and regression_data['filter_tech_all_pct_change_count'] >= 4) or abs(regression_data['filter_tech_all_pct_change_avg']) > 4 or regression_data['filter_tech_all_avg'] > 5):
        flag = filter_accuracy_finder_all(regression_data, regression_high, regression_low, regressionResult, high_or_low, ws, 'filter_tech_all_pct_change_avg', 'filter_tech_all_pct_change_count', 'filter_tech_all_pct_change_pct')
        if(flag):
            superflag = True
    
    
    flag = filter_accuracy_finder(regression_data, regression_high, regression_low, regressionResult, high_or_low, ws, 'filter_345_avg', 'filter_345_count', 'filter_345_pct')
    if(flag):
        superflag = True
    flag = filter_accuracy_finder(regression_data, regression_high, regression_low, regressionResult, high_or_low, ws, 'filter_avg', 'filter_count', 'filter_pct')
    if(flag):
        superflag = True
    flag = filter_accuracy_finder(regression_data, regression_high, regression_low, regressionResult, high_or_low, ws, 'filter_pct_change_avg', 'filter_pct_change_count', 'filter_pct_change_pct')
    if(flag):
        superflag = True
    flag = filter_accuracy_finder(regression_data, regression_high, regression_low, regressionResult, high_or_low, ws, 'filter_all_avg', 'filter_all_count', 'filter_all_pct')
    if(flag):
        superflag = True
    if(regression_data['filter_tech_count'] > 5):
        flag = filter_accuracy_finder(regression_data, regression_high, regression_low, regressionResult, high_or_low, ws, 'filter_tech_avg', 'filter_tech_count', 'filter_tech_pct')
        if(flag):
            superflag = True
    if((abs(regression_data['filter_tech_all_avg']) > 2 and regression_data['filter_tech_all_count'] >= 4) or abs(regression_data['filter_tech_all_avg']) > 4 or regression_data['filter_tech_all_avg'] > 5):
        flag = filter_accuracy_finder(regression_data, regression_high, regression_low, regressionResult, high_or_low, ws, 'filter_tech_all_avg', 'filter_tech_all_count', 'filter_tech_all_pct')
        if(flag):
            superflag = True
    if((abs(regression_data['filter_tech_all_pct_change_avg']) > 2 and regression_data['filter_tech_all_pct_change_count'] >= 4) or abs(regression_data['filter_tech_all_pct_change_avg']) > 4 or regression_data['filter_tech_all_avg'] > 5):
        flag = filter_accuracy_finder(regression_data, regression_high, regression_low, regressionResult, high_or_low, ws, 'filter_tech_all_pct_change_avg', 'filter_tech_all_pct_change_count', 'filter_tech_all_pct_change_pct')
        if(flag):
            superflag = True
    
     
    flag = filter_accuracy_finder_risky(regression_data, regressionResult, high_or_low, ws, 'filter_345_avg', 'filter_345_count', 'filter_345_pct')
    if(flag):
        superflag = True
    flag = filter_accuracy_finder_risky(regression_data, regressionResult, high_or_low, ws, 'filter_avg', 'filter_count', 'filter_pct')
    if(flag):
        superflag = True
    flag = filter_accuracy_finder_risky(regression_data, regressionResult, high_or_low, ws, 'filter_pct_change_avg', 'filter_pct_change_count', 'filter_pct_change_pct')
    if(flag):
        superflag = True
    flag = filter_accuracy_finder_risky(regression_data, regressionResult, high_or_low, ws, 'filter_all_avg', 'filter_all_count', 'filter_all_pct')
    if(flag):
        superflag = True
    flag = filter_accuracy_finder_risky(regression_data, regressionResult, high_or_low, ws, 'filter_tech_avg', 'filter_tech_count', 'filter_tech_pct')
    if(flag):
        superflag = True
    flag = filter_accuracy_finder_risky(regression_data, regressionResult, high_or_low, ws, 'filter_tech_all_avg', 'filter_tech_all_count', 'filter_tech_all_pct')
    if(flag):
        superflag = True
    flag = filter_accuracy_finder_risky(regression_data, regressionResult, high_or_low, ws, 'filter_tech_all_pct_change_avg', 'filter_tech_all_pct_change_count', 'filter_tech_all_pct_change_pct')
    if(flag):
        superflag = True
        
    
#     flag = filter_accuracy_finder_stable(regression_data, regressionResult, high_or_low, ws, 'filter_345_avg', 'filter_345_count', 'filter_345_pct')
#     if(flag):
#         superflag = True
#     flag = filter_accuracy_finder_stable(regression_data, regressionResult, high_or_low, ws, 'filter_avg', 'filter_count', 'filter_pct')
#     if(flag):
#         superflag = True
#     flag = filter_accuracy_finder_stable(regression_data, regressionResult, high_or_low, ws, 'filter_tech_avg', 'filter_tech_count', 'filter_tech_pct')
#     if(flag):
#         superflag = True
    
      
    if(regression_data['filter_pct_change_avg'] > 1 and regression_data['filter_pct_change_count'] >= 1 and regression_data['filter_pct_change_pct'] > 66
        and "MLSell" not in regression_data['filter']
        ):
        superflag = True
    if(regression_data['filter_pct_change_avg'] < -2 and regression_data['filter_pct_change_count'] >= 1 and regression_data['filter_pct_change_pct'] < -66
        and "MLBuy" not in regression_data['filter']
        ):
        superflag = True
    
    is_filter_risky(regression_data, regressionResult, high_or_low, ws, 'filter_345_avg', 'filter_345_count', 'filter_345_pct')
    is_filter_risky(regression_data, regressionResult, high_or_low, ws, 'filter_avg', 'filter_count', 'filter_pct')
    is_filter_risky(regression_data, regressionResult, high_or_low, ws, 'filter_pct_change_avg', 'filter_pct_change_count', 'filter_pct_change_pct')
    is_filter_risky(regression_data, regressionResult, high_or_low, ws, 'filter_all_avg', 'filter_all_count', 'filter_all_pct')
    is_filter_risky(regression_data, regressionResult, high_or_low, ws, 'filter_tech_avg', 'filter_tech_count', 'filter_tech_pct')
    is_filter_risky(regression_data, regressionResult, high_or_low, ws, 'filter_tech_all_avg', 'filter_tech_all_count', 'filter_tech_all_pct')
    is_filter_risky(regression_data, regressionResult, high_or_low, ws, 'filter_tech_all_pct_change_avg', 'filter_tech_all_pct_change_count', 'filter_tech_all_pct_change_pct')
    
    if(superflag):
        return superflag       

def filter_accuracy_finder(regression_data, regression_high, regression_low, regressionResult, high_or_low, ws, filter_avg, filter_count, filter_pct):
    flag = False   
    if(abs(regression_data[filter_avg]) > 0.5
        and ((regression_data[filter_avg] > 0 and (high_tail_pct(regression_data) < 1.3 or regression_data['PCT_day_change'] < 0 or regression_data['PCT_day_change'] > 3))
             or (regression_data[filter_avg] < 0 and (low_tail_pct(regression_data) < 1.3 or regression_data['PCT_day_change'] > 0 or regression_data['PCT_day_change'] < -3))
            )
        and regression_data[filter_count] >= 1
        and regression_data['close'] > 60
        #and (regression_data[filter_count_oth] >= 2
        #    or (regression_data[filter_count_oth] >= 1 and abs(regression_data[filter_avg_oth]) > 2))
        ):
        if(flag == False):
            if((("MLSell" in regression_data['filter']) and (float(regression_data[filter_avg]) > 1) and (abs(float(regression_data[filter_pct])) > 70))
                or (("MLBuy" in regression_data['filter']) and (float(regression_data[filter_avg]) < -1) and (abs(float(regression_data[filter_pct])) > 70))
                or (("MLSell" in regression_data['filter']) and ("Buy-SUPER" in regression_data['filter2']))
                or (("MLBuy" in regression_data['filter']) and ("Sell-SUPER" in regression_data['filter2']))
                ):
                return False
            
        if((regression_data[filter_avg] > 1 and 'RISKY-DOWNTREND-BUY' in regression_data['filter1'])
            or (regression_data[filter_avg] < -1 and 'RISKY-UPTREND-SELL' in regression_data['filter1'])
            ):
            return False
            
        buyRisky, sellRisky =  is_filter_risky(regression_data, regressionResult, high_or_low, ws, filter_avg, filter_count, filter_pct, False)   
              
                
        if(regression_data[filter_count] >= 3
            and abs(regression_data[filter_pct]) >= 90
            and abs(regression_data[filter_avg]) >= 2
            ):
            if(regression_data[filter_avg] >= 0 
                and (filter_avg_gt_1_count(regression_data) >= 2 or regression_data[filter_count] >= 4)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-8-Buy')
            elif(regression_data[filter_avg] < 0 
                and (filter_avg_lt_minus_1_count(regression_data) >= 2 or regression_data[filter_count] >= 4)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-8-Sell')
        
        if(regression_data[filter_count] >= 3
            and abs(regression_data[filter_pct]) >= 85
            and abs(regression_data[filter_avg]) >= 3
            ):
            if(regression_data[filter_avg] >= 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-5-Buy')
            elif(regression_data[filter_avg] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-5-Sell')
        elif(regression_data[filter_count] >= 2
            and((abs(regression_data[filter_pct]) >= 100 and abs(regression_data[filter_avg]) >= 2.5 and regression_data[filter_count] >= 3)
                 or (abs(regression_data[filter_pct]) >= 70 and abs(regression_data[filter_avg]) >= 3.5)
                 )
            ):
            if(regression_data[filter_avg] >= 0 and is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-6-Buy')
            elif(regression_data[filter_avg] < 0 and is_algo_sell(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-6-Sell')
        elif(regression_data[filter_count] >= 2
            and abs(regression_data[filter_pct]) >= 80
            and abs(regression_data[filter_avg]) >= 2
            and (abs(regression_data[filter_avg]) > 3 or regression_data[filter_count] > 3)
            ):
            if(regression_data[filter_avg] >= 0 and is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-7-Buy')
            elif(regression_data[filter_avg] < 0 and is_algo_sell(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-7-Sell')
                
        if(regression_data[filter_count] >= 3
            and abs(regression_data[filter_pct]) > 80
            and abs(regression_data[filter_avg]) > 3
            ):
            if(regression_data[filter_avg] >= 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-2-Buy')
            elif(regression_data[filter_avg] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-2-Sell')   
        elif(regression_data[filter_count] >= 3
            and abs(regression_data[filter_pct]) > 85
            and abs(regression_data[filter_avg]) > 2.5
            and abs(regression_data[filter_count] * regression_data[filter_avg]) > 9
            ):
            if(regression_data[filter_avg] >= 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-3-Buy')
            elif(regression_data[filter_avg] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-3-Sell')
        elif(regression_data[filter_count] >= 3
            and abs(regression_data[filter_pct]) >= 85
            and abs(regression_data[filter_avg]) >= 2.0
            ):
            if(regression_data[filter_avg] >= 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-4-Buy')
            elif(regression_data[filter_avg] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-4-Sell')
        
        if(regression_data[filter_count] >= 3
            and abs(regression_data[filter_pct]) >= 100
            and abs(regression_data[filter_avg]) > 2
            ):
            if(regression_data[filter_avg] >= 0
                and is_algo_sell(regression_high) != True
                and is_algo_sell(regression_low) != True
                #and (is_algo_buy(regression_high) == True or is_algo_buy(regression_low) == True)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-1-Buy')
            elif(regression_data[filter_avg] < 0
                and is_algo_buy(regression_high) != True
                and is_algo_buy(regression_low) != True
                #and (is_algo_sell(regression_high) == True or is_algo_sell(regression_low) == True)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-1-Sell')
                
        if(regression_data[filter_count] >= 5
            and abs(regression_data[filter_pct]) >= 100
            and abs(regression_data[filter_avg]) > 2
            ):
            if(regression_data[filter_avg] >= 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-0-Buy')
            elif(regression_data[filter_avg] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-0-Sell')
        elif(regression_data[filter_count] >= 4
            and abs(regression_data[filter_pct]) >= 100
            and abs(regression_data[filter_avg]) > 2.5
            ):
            if(regression_data[filter_avg] >= 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-0-Buy')
            elif(regression_data[filter_avg] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-0-Sell')
        elif(regression_data[filter_count] >= 3
            and abs(regression_data[filter_pct]) >= 100
            and abs(regression_data[filter_avg]) > 5
            ):
            if(regression_data[filter_avg] >= 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-0-Buy')
            elif(regression_data[filter_avg] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-0-Sell')
            
        if(abs(float(regression_data[filter_avg])) > 1
            and abs(regression_data[filter_pct]) > 66
            ):
            flag = True
            
        if(("MLBuy" in regression_data['filter']) 
            and regression_data[filter_avg] >= 1.5
            and (regression_data[filter_pct] >= 80 or regression_data[filter_pct] == 0)
            ):
            flag = True
            
        if(("MLSell" in regression_data['filter']) 
            and regression_data[filter_avg] <= -1.5
            and (regression_data[filter_pct] <= -80 or regression_data[filter_pct] == 0)
            ):
            flag = True
                    
    return flag            

def filter_accuracy_finder_all(regression_data, regression_high, regression_low, regressionResult, high_or_low, ws, filter_avg, filter_count, filter_pct):
    flag = False    
    if(abs(float(regression_data[filter_avg])) > 1
        and abs(regression_data[filter_pct]) > 66
        ):
        flag = True
        
    if(abs(float(regression_data[filter_avg])) > 2
        and abs(regression_data[filter_pct]) == 0
        ):
        flag = True
        
    if(("MLBuy" in regression_data['filter']) 
        and regression_data[filter_avg] >= 1.5
        and (regression_data[filter_pct] >= 80 or regression_data[filter_pct] == 0)
        ):
        flag = True
        
    if(("MLSell" in regression_data['filter']) 
        and regression_data[filter_avg] <= -1.5
        and (regression_data[filter_pct] <= -80 or regression_data[filter_pct] == 0)
        ):
        flag = True
                    
    return flag            

def filter_accuracy_finder_stable(regression_data, regressionResult, high_or_low, ws, filter_avg, filter_count, filter_pct):   
    flag = False
    
    reg_data_filter = regression_data['filter']
    list = regression_data['filter'].partition(']:')
    if(list[1] == ']:'):
        reg_data_filter = list[2]
    
    if(abs(regression_data[filter_avg]) >= 0.5
        #and ((regression_data[filter_avg] > 0 and (high_tail_pct(regression_data) < 1.3 or regression_data['PCT_day_change'] < 0 or regression_data['PCT_day_change'] > 3))
        #     or (regression_data[filter_avg] < 0 and (low_tail_pct(regression_data) < 1.3 or regression_data['PCT_day_change'] > 0 or regression_data['PCT_day_change'] < -3))
        #    )
        and regression_data[filter_count] >= 1
        #and (regression_data[filter_count_oth] >= 2
        #    or (regression_data[filter_count_oth] >= 1 and abs(regression_data[filter_avg_oth]) > 2))
        ):
        
        if(regression_data[filter_count] >= 2
            and (abs(regression_data[filter_pct]) >= 70 or regression_data[filter_pct] == 0)
            ):
            if((('sell' in reg_data_filter or 'Sell' in reg_data_filter) and (1 < regression_data[filter_avg] and  regression_data[filter_count] <= 3))
                or (('buy' in reg_data_filter or 'Buy' in reg_data_filter) and (regression_data[filter_avg] < -1 and regression_data[filter_count] <= 3))
                ):
                return  flag
            
            if((regression_data[filter_avg] > 1 and 'RISKY-DOWNTREND-BUY' in regression_data['filter1'])
                or (regression_data[filter_avg] < -1 and 'RISKY-UPTREND-SELL' in regression_data['filter1'])
                ):
                return flag
            
            if((regression_data[filter_avg] > 1 and 'Sell-AnyGT2' in regression_data['filter2'])
                or (regression_data[filter_avg] < -1 and 'Buy-AnyGT2' in regression_data['filter2'])
                ):
                return flag
        
            if(regression_data[filter_count] >= 5
                and abs(regression_data[filter_pct]) > 70
                and abs(regression_data[filter_avg]) > 2
                ):
                if(regression_data[filter_avg] >= 0
                    and ((abs(regression_data[filter_avg]) > 1 and abs(regression_data[filter_pct]) >= 80) or is_algo_buy(regression_data))
                    and ("MLSell" not in regression_data['filter'])
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-Buy-count')
                elif(regression_data[filter_avg] < 0
                    and ((abs(regression_data[filter_avg]) > 1 and abs(regression_data[filter_pct]) >= 80) or is_algo_sell(regression_data))
                    and ("MLBuy" not in regression_data['filter'])
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-Sell-count')
                flag = True
                
            if(regression_data[filter_count] >= 2
                and abs(regression_data[filter_pct]) > 90
                and abs(regression_data[filter_avg]) >= 2
                and ((abs(regression_data[filter_avg]) > 3 or regression_data[filter_count] > 3)
                     )
                     
                ):
                if(regression_data[filter_avg] >= 0
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, None, None, 'stable-filter-buy')
                elif(regression_data[filter_avg] < 0
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, None, None, 'stable-filter-sell')
                flag = True
            elif(regression_data[filter_count] >= 2
                and abs(regression_data[filter_pct]) > 90
                and abs(regression_data[filter_avg]) >= 2.5
                and ((abs(regression_data[filter_avg]) > 3 or regression_data[filter_count] >= 3)
                     )
                     
                ):
                if(regression_data[filter_avg] >= 0
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, None, None, 'stable-filter-risky-buy')
                elif(regression_data[filter_avg] < 0
                    ):
                    add_in_csv(regression_data, regressionResult, ws, None, None, None, 'stable-filter-risky-sell')
                flag = True
        return flag
    
def filter_accuracy_finder_risky(regression_data, regressionResult, high_or_low, ws, filter_avg, filter_count, filter_pct):   
    flag = False
    if(abs(regression_data[filter_avg]) >= 0.5
        and ((regression_data[filter_avg] > 0 and (high_tail_pct(regression_data) < 1.3 or regression_data['PCT_day_change'] < 0 or regression_data['PCT_day_change'] > 3))
             or (regression_data[filter_avg] < 0 and (low_tail_pct(regression_data) < 1.3 or regression_data['PCT_day_change'] > 0 or regression_data['PCT_day_change'] < -3))
            )
        and regression_data[filter_count] >= 1
        #and (regression_data[filter_count_oth] >= 2
        #    or (regression_data[filter_count_oth] >= 1 and abs(regression_data[filter_avg_oth]) > 2))
        ):
        if((("MLSell" in regression_data['filter']) and (float(regression_data[filter_avg]) > 1) and (abs(float(regression_data[filter_pct])) > 70))
            or (("MLBuy" in regression_data['filter']) and (float(regression_data[filter_avg]) < -1) and (abs(float(regression_data[filter_pct])) > 70))
            or (("MLSell" in regression_data['filter']) and ("Buy-SUPER" in regression_data['filter2']))
            or (("MLBuy" in regression_data['filter']) and ("Sell-SUPER" in regression_data['filter2']))
            ):
            return False
        
        if((regression_data[filter_avg] > 1 and 'RISKY-DOWNTREND-BUY' in regression_data['filter1'])
            or (regression_data[filter_avg] < -1 and 'RISKY-UPTREND-SELL' in regression_data['filter1'])
            ):
            return False
        
        if(regression_data[filter_count] > 5
            and abs(regression_data[filter_pct]) > 70
            and abs(regression_data[filter_avg]) > 1
            and (abs(regression_data[filter_avg]) > 1.5 or abs(regression_data[filter_pct]) > 90)
            #and abs(regression_data['PCT_day_change']) > 1
            #and abs(regression_data['PCT_change']) > 1
            ):
            if(regression_data[filter_avg] >= 0 and filter_avg_gt_1_count(regression_data) >=2
                #and (abs(regression_data[filter_avg]) > 2 or regression_data['PCT_day_change'] < 0)
                and (abs(regression_data[filter_avg]) > 2 
                     or (abs(regression_data[filter_avg])*2 > abs(regression_data['PCT_day_change']))
                     or high_or_low == 'High'
                     or high_or_low == 'None'
                     )
                and regression_data['PCT_day_change'] < 3
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-Risky-01-Buy')
            elif(regression_data[filter_avg] < 0 and filter_avg_lt_minus_1_count(regression_data) >=2
                #and (abs(regression_data[filter_avg]) > 2 or regression_data['PCT_day_change'] > 0)
                and (abs(regression_data[filter_avg]) > 2 
                     or (abs(regression_data[filter_avg])*2 > abs(regression_data['PCT_day_change']))
                     or high_or_low == 'Low'
                     or high_or_low == 'None'
                     )
                and regression_data['PCT_day_change'] > -3
                ):
                add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-Risky-01-Sell')  
            flag = True
            
        if(flag == False):
            if((("MLSell" in regression_data['filter']) and (float(regression_data[filter_avg]) > 1) and (abs(float(regression_data[filter_pct])) > 70))
                or (("MLBuy" in regression_data['filter']) and (float(regression_data[filter_avg]) < -1) and (abs(float(regression_data[filter_pct])) > 70))
                ):
                return False
                
#         if(regression_data[filter_count] >= 2
#             and abs(regression_data[filter_pct]) >= 90
#             and abs(regression_data[filter_avg]) >= 2
#             and 'STRONG' not in regression_data['filter1']
#             ):
#             if(regression_data[filter_avg] >= 0):
#                 add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-9-Buy')
#             elif(regression_data[filter_avg] < 0):
#                 add_in_csv(regression_data, regressionResult, ws, None, None, None, 'STRONG-9-Sell')    
        return flag
      
def is_filter_risky(regression_data, regressionResult, high_or_low, ws, filter_avg, filter_count, filter_pct, update=True): 
    BuyRisky = False
    SellRisky = False
    
    if(regression_data[filter_avg] < -0.75
        and regression_data['PCT_day_change'] > 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, None, 'UPTREND:OR:GLOBALUP-DONT-SELL')
    elif(regression_data[filter_avg] > 0.75
        and regression_data['PCT_day_change'] < 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, None, 'DOWNTREND:OR:GLOBALDOWN-DONT-BUY')
    
    if(regression_data[filter_avg] < -0.75
        and regression_data['PCT_day_change'] < -2.5
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, None, 'DON\'TSELL-NIFTYDOWN1PC')
    elif(regression_data[filter_avg] > 0.75
        and regression_data['PCT_day_change'] > 2.5
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, None, 'DON\'TBUY-NIFTYUP1PC')
    
    if(regression_data['PCT_day_change'] > 0
        and regression_data['PCT_day_change_pre1'] < 0
        and regression_data['PCT_day_change_pre2'] < 0
        and (regression_data['PCT_day_change_pre1'] < -1 
             or regression_data['PCT_day_change_pre2'] < -1
             or regression_data['PCT_day_change_pre3'] < -1
             )
        #and regression_data['close'] > regression_data['low_pre1']
        and (regression_data['close'] < regression_data['low_pre2'] 
             or regression_data['close'] < regression_data['low_pre3']
             or (regression_data['close'] < regression_data['high_pre2'] and regression_data['close'] < regression_data['high_pre3'])
             )
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, None, 'RISKY-DOWNTREND-BUY') 
    elif(regression_data['PCT_day_change'] < 0
        and regression_data['PCT_day_change_pre1'] > 0
        and regression_data['PCT_day_change_pre2'] > 0
        and (regression_data['PCT_day_change_pre1'] > 1 
             or regression_data['PCT_day_change_pre2'] > 1 
             or regression_data['PCT_day_change_pre3'] > 1
             )
        #and regression_data['close'] < regression_data['high_pre1']
        and (regression_data['close'] > regression_data['high_pre2'] 
             or regression_data['close'] > regression_data['high_pre3']
             or (regression_data['close'] > regression_data['low_pre2'] and regression_data['close'] > regression_data['low_pre3'])
             )
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, None, 'RISKY-UPTREND-SELL')
    
    if(float(regression_data[filter_avg]) < -1
        and regression_data['PCT_day_change'] > 0
        and regression_data['PCT_change'] > 0
        and (regression_data['PCT_day_change'] > 1 or regression_data['PCT_change'] > 1)
        and regression_data['monthLowChange'] < 5
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, None, 'RISKY-SELL-UPTRENDMARKET')
    elif(float(regression_data[filter_avg]) > 1
        and regression_data['PCT_day_change'] < 0
        and regression_data['PCT_change'] < 0
        and (regression_data['PCT_day_change'] < -1 or regression_data['PCT_change'] < -1)
        and regression_data['monthHighChange'] > -5
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, None, 'RISKY-BUY-DOWNTRENDMARKET')  
        
    if(((low_tail_pct(regression_data) > 1.5 or high_tail_pct(regression_data) > 2.5) and regression_data[filter_avg] < -0.5)
        or ((high_tail_pct(regression_data) > 1.5 and low_tail_pct(regression_data) > 2.5) and regression_data[filter_avg] > 0.5)
        ):
        if update:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, None, 'TAILRisk')
            
    if(((regression_data['filter'] == " " and abs(float(regression_data[filter_avg])) > 0.75)
            or ("MLBuy" in regression_data['filter'] and float(regression_data[filter_avg]) < -0.5)
            or ("MLSell" in regression_data['filter'] and float(regression_data[filter_avg]) > 0.5)
            )
        and regression_data['filter4'].startswith('@s@')
        and regression_data['filter4'].endswith('@e@,') 
        ):
        if update:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, None, 'FilterRisk')
    
    
    
    if((regression_data['PCT_day_change'] < -3 or regression_data['PCT_change'] < -3)
        and regression_data['monthHighChange'] < -5
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, None, 'RISKY-SELL-LASTDAYDOWN')
    elif((regression_data['PCT_day_change'] < -3 or regression_data['PCT_change'] < -3)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, None, 'RISKY-SELL-LASTDAYDOWN-UPTRENDMARKET')
    if((regression_data['PCT_day_change'] > 3 or regression_data['PCT_change'] > 3)
        and regression_data['monthLowChange'] > 5
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, None, 'RISKY-BUY-LASTDAYUP')
    elif((regression_data['PCT_day_change'] > 3 or regression_data['PCT_change'] > 3)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, None, 'RISKY-BUY-LASTDAYUP-DOWNTRENDMARKET')
                
    if(-4 < regression_data['PCT_day_change'] < 0
        and -4 < regression_data['PCT_change'] < 0
        and regression_data['PCT_day_change_pre1'] < 0
        and regression_data['PCT_day_change_pre2'] < 0
        and regression_data['PCT_day_change_pre3'] < 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, None, 'RISKY-SELL-DOWNTREND-CONT(MARKET-DOWNTREND-NOTRISKY)')
    if(4 > regression_data['PCT_day_change'] > 0
        and 4 > regression_data['PCT_change'] > 0
        and regression_data['PCT_day_change_pre1'] > 0
        and regression_data['PCT_day_change_pre2'] > 0
        and regression_data['PCT_day_change_pre3'] > 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, None, 'RISKY-BUY-UPTREND-CONT(MARKET-UPTREND-NOTRISKY)')
    
    if(((-1.3 < regression_data['monthLowChange'] < 0.75 and regression_data['month3LowChange'] > 10 and regression_data['month6LowChange'] > 10)
           or(-1.3 < regression_data['month3LowChange'] < 0.75 and regression_data['month6LowChange'] > 10 and regression_data['yearLowChange'] > 10)
        )
        and regression_data['year2LowChange'] > 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, None, 'RISKYBASELINESELL')
    if(((-0.75 < regression_data['monthHighChange'] < 1.3 and regression_data['month3HighChange'] < -10 and regression_data['month6HighChange'] < -10)
            or(-0.75 < regression_data['month3HighChange'] < 1.3 and regression_data['month6HighChange'] < -10 and regression_data['yearHighChange'] < -10)  
        )
        and regression_data['year2HighChange'] < 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, None, 'RISKYBASELINEBUY')
            
    dojivalue = 1
    if(abs(float(regression_data['PCT_day_change'])) < 0.85
        and -3 < float(regression_data['PCT_change']) < 3
        #and regression_data['series_trend'] == "NA$NA:NA$NA"
        ):
        if((regression_data['forecast_day_PCT_change'] < regression_data['forecast_day_PCT2_change'] < regression_data['forecast_day_PCT3_change'] < regression_data['forecast_day_PCT4_change']
                and float(regression_data[filter_avg]) > dojivalue
                )
            or (regression_data['forecast_day_PCT_change'] > regression_data['forecast_day_PCT2_change'] > regression_data['forecast_day_PCT3_change'] > regression_data['forecast_day_PCT4_change']
                and float(regression_data[filter_avg]) < -dojivalue
                )
            ):
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, None, None)
        else:
            if update:
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, None, 'DOJI')
            BuyRisky = True
            SellRisky = True
    if(0 < float(regression_data['PCT_day_change']) < 1
        and -3 < float(regression_data['PCT_change']) < 3
#         and ("shortDownTrend" in regression_data['series_trend']
#              or "downTrend" in regression_data['series_trend']
#             )
        and regression_data['forecast_day_PCT_change'] > regression_data['forecast_day_PCT2_change'] > regression_data['forecast_day_PCT3_change'] > regression_data['forecast_day_PCT4_change']
        and float(regression_data[filter_avg]) > dojivalue and (regression_data[filter_pct] > 70 or regression_data[filter_pct] ==0)
        ):
        if update:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, None, 'DOJI-BuyMayFail')
        BuyRisky = True
    if(-1 < float(regression_data['PCT_day_change']) < 0
        and -3 < float(regression_data['PCT_change']) < 3 
        #and ("downTrend" in regression_data['series_trend'])
        and regression_data['forecast_day_PCT_change'] > regression_data['forecast_day_PCT2_change'] > regression_data['forecast_day_PCT3_change'] > regression_data['forecast_day_PCT4_change']
        and float(regression_data[filter_avg]) > dojivalue and (regression_data[filter_pct] > 70 or regression_data[filter_pct] ==0)
        ):
        if update:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, None, 'DOJI-BuyMayFail')
        BuyRisky = True
    if(-1 < float(regression_data['PCT_day_change']) < 0
        and -3 < float(regression_data['PCT_change']) < 3 
#         and (("shortUpTrend" in regression_data['series_trend'])
#              or ("upTrend" in regression_data['series_trend'])
#             )
        and regression_data['forecast_day_PCT_change'] < regression_data['forecast_day_PCT2_change'] < regression_data['forecast_day_PCT3_change'] < regression_data['forecast_day_PCT4_change']
        and float(regression_data[filter_avg]) < -dojivalue and (regression_data[filter_pct] < -70 or regression_data[filter_pct] ==0)
        ):
        if update:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, None, 'DOJI-SellMayFail')
        SellRisky = True
    if(0 < float(regression_data['PCT_day_change']) < 1
        and -3 < float(regression_data['PCT_change']) < 3 
        #and ("upTrend" in regression_data['series_trend'])
        and regression_data['forecast_day_PCT_change'] < regression_data['forecast_day_PCT2_change'] < regression_data['forecast_day_PCT3_change'] < regression_data['forecast_day_PCT4_change']
        and float(regression_data[filter_avg]) < -dojivalue and (regression_data[filter_pct] < -70 or regression_data[filter_pct] ==0)
        ):
        if update:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None, None, 'DOJI-SellMayFail')
        SellRisky = True
        
    return BuyRisky, SellRisky  
    
        
    
        
        
        
        
        

            