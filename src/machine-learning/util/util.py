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

from util.util_buy import *
from util.util_sell import *
from util.util_base import *

connection = MongoClient('localhost',27017)
db = connection.Nsedata

filter345sell = patterns_to_dict('../../data-import/nselist/filter-345-sell.csv')
filtersell = patterns_to_dict('../../data-import/nselist/filter-sell.csv')
filterpctchangesell = patterns_to_dict('../../data-import/nselist/filter-pct-change-sell.csv')
filterallsell = patterns_to_dict('../../data-import/nselist/filter-all-sell.csv')
filtertechsell = patterns_to_dict('../../data-import/nselist/filter-tech-buy.csv')
filtertechallsell = patterns_to_dict('../../data-import/nselist/filter-tech-all-buy.csv')
filtertechallpctchangesell = patterns_to_dict('../../data-import/nselist/filter-tech-all-pct-change-buy.csv')
filter345buy = patterns_to_dict('../../data-import/nselist/filter-345-buy.csv')
filterbuy = patterns_to_dict('../../data-import/nselist/filter-buy.csv')
filterpctchangebuy = patterns_to_dict('../../data-import/nselist/filter-pct-change-buy.csv')
filterallbuy = patterns_to_dict('../../data-import/nselist/filter-all-buy.csv')
filtertechbuy = patterns_to_dict('../../data-import/nselist/filter-tech-buy.csv')
filtertechallbuy = patterns_to_dict('../../data-import/nselist/filter-tech-all-buy.csv')
filtertechallpctchangebuy = patterns_to_dict('../../data-import/nselist/filter-tech-all-pct-change-buy.csv')


def buy_all_rule(regression_data, regressionResult, buyIndiaAvg, ws):        
    if(is_algo_buy(regression_data)):    
        if(-15 < regression_data['PCT_day_change'] < -3.5 and -15 < regression_data['PCT_change'] < -3.5):
            add_in_csv(regression_data, regressionResult, ws, 'AF:mlBuyPCTDayChangeLT-4.5')
        elif(regression_data['week2HighChange'] < -20 and regression_data['weekHighChange'] < -10
            and 10 > regression_data['PCT_day_change'] > 2
            ):
            add_in_csv(regression_data, regressionResult, ws, 'AF:(NOT-DOWNTREND)0-mlBuyWeek2HighLT-20')
#         elif(regression_data['week2HighChange'] < -10 and regression_data['weekHighChange'] < -10
#             and (regression_data['week2HighChange'] < -15 or regression_data['weekHighChange'] < -15)
#             and 4 > regression_data['PCT_day_change'] > 0
#             and is_any_sell_LTMinus2_from_all_filter_(regression_data) == False
#             ):
#             add_in_csv(regression_data, regressionResult, ws, 'AF:1-mlBuyWeek2HighLT-10')
#         elif(regression_data['week2HighChange'] < -5 and regression_data['weekHighChange'] < -10
#             and 5 > regression_data['PCT_day_change'] > 2
#             and is_any_sell_LTMinus2_from_all_filter_(regression_data) == False
#             ):
#             add_in_csv(regression_data, regressionResult, ws, 'AF:1-mlBuyWeekHighLT-10')    
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
        and '(Confirmed)EMA6>EMA14' not in regression_data['filter4']
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
            add_in_csv(regression_data, regressionResult, ws, None, 'Common:buyNotM3HighLow-0(SMA9GT1)')
        elif(regression_data['SMA25'] > 0):
            add_in_csv(regression_data, regressionResult, ws, None, None)  
        else:
            add_in_csv(regression_data, regressionResult, ws, None)
             
    return False

def buy_all_common_High_Low(regression_data, regressionResult, reg, ws):
    if((regression_data['forecast_day_PCT3_change'] > 0 and regression_data['forecast_day_PCT4_change'] > 0)
        or regression_data['forecast_day_PCT5_change'] > 0
        or regression_data['forecast_day_PCT7_change'] > 0
        or regression_data['forecast_day_PCT10_change'] > 0
        ):
        if(2 < low_tail_pct_pre1(regression_data) < 6 and 2.9 < regression_data['PCT_day_change'] < 4.1
            and regression_data['PCT_day_change_pre1'] > -1.3 
            and abs(regression_data['PCT_day_change_pre1']) < 1.5
            and regression_data['PCT_day_change_pre2'] < -1
            and abs(regression_data['PCT_day_change_pre2']) > abs(regression_data['PCT_day_change_pre1'])
            #and regression_data['high'] >= regression_data['bar_high_pre2']
            #and abs(regression_data['month6HighChange']) < abs(regression_data['month6LowChange'])
            and low_tail_pct(regression_data) < 1.5
            and high_tail_pct(regression_data) < 1.5
            ):
            add_in_csv(regression_data, regressionResult, ws, 'CommonHL:HighUptrend')
        elif(2.7 < regression_data['PCT_day_change'] < 5.5
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
            and regression_data['forecast_day_PCT4_change'] > 0
            and regression_data['forecast_day_PCT5_change'] > 0
            and regression_data['SMA4'] > 2
            and regression_data['SMA9'] > 2
            and high_tail_pct(regression_data) < 2.5
            and low_tail_pct(regression_data) < 2.5
            and low_tail_pct_pre1(regression_data) < 2.5
            ):
            if(regression_data['PCT_day_change'] < 2.95
    #             and (regression_data['PCT_day_change_pre1'] > 0
    #                 or regression_data['PCT_day_change_pre2'] > 0
    #                 or regression_data['PCT_day_change_pre3'] > 0
    #                 or regression_data['PCT_day_change_pre4'] > 0
    #                 )
                ):
                add_in_csv(regression_data, regressionResult, ws, 'CommonHL:HEAVYUPTRENDMARKET:HighUptrend')
            elif(regression_data['PCT_day_change_pre1'] > 0
                or regression_data['PCT_day_change_pre2'] > 0
                or regression_data['PCT_day_change_pre3'] > 0
                ):
                add_in_csv(regression_data, regressionResult, ws, 'CommonHL:HEAVYUPTRENDMARKET:HighUptrend-(NOT-GLOBAL-DOWN)')
        
    if((regression_data['forecast_day_PCT7_change'] > 15 or regression_data['forecast_day_PCT5_change'] > 15)
        and (regression_data['PCT_day_change_pre1'] > 2.5 or regression_data['PCT_day_change_pre2'] > 2.5)
        and ('set1' in regression_data['filter'] or 'set2' in regression_data['filter'])
        and low_tail_pct(regression_data) < 2.5
        and high_tail_pct(regression_data) < 2.5
        ):
        add_in_csv(regression_data, regressionResult, ws, 'CommonHL:HighSuperUpTrend')
        
    buy_common_up_continued(regression_data, regressionResult, reg, ws)
         
    if(last_4_day_all_up(regression_data) == False
        and -10 < regression_data['year2HighChange'] < -1 and regression_data['weekHighChange'] < -2
        and regression_data['yearLowChange'] > 30
        and ((-1 < regression_data['PCT_change'] < 1.75
            and -1 < regression_data['PCT_day_change'] < 0
            and (high_tail_pct(regression_data) > 0.8
                or low_tail_pct(regression_data) > 0.8
                or abs(regression_data['forecast_day_PCT_change']) > 0.5
                )
            )
            or(-2 < regression_data['PCT_change'] < 1.75
                and -2 < regression_data['PCT_day_change'] < -1
                and regression_data['PCT_day_change_pre1'] < -0.5
                )
            )
        ):
        if(((regression_data['low'] > regression_data['low_pre1'])
            or regression_data['week2LowChange'] < 0.5)):
            add_in_csv(regression_data, regressionResult, ws, 'CommonHL:DOWNTREND:buyYear2High')
        else:
            add_in_csv(regression_data, regressionResult, ws, 'CommonHL:DOWNTREND:buyYear2High-afterMorningBase')
            
    if((2 < regression_data['PCT_day_change'] < 3.25) and (1.5 < regression_data['PCT_change'] < 3.25)
        and regression_data['bar_high'] > regression_data['bar_high_pre1']
        ):
        if(regression_data['high_pre1'] < regression_data['high_pre2'] < regression_data['high_pre3']):
            add_in_csv(regression_data, regressionResult, ws, None)
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
            add_in_csv(regression_data, regressionResult, ws, 'CommonHL:UPTREND:buyYear2LowLT-50(triggerAfter-9:15)')    
       
def buy_other_indicator(regression_data, regressionResult, reg, ws):
    tail_pct_filter(regression_data, regressionResult)
    base_line(regression_data, regressionResult, reg, ws)
    filterMA(regression_data, regressionResult)
    tail_reversal_filter(regression_data, regressionResult)
    if(regression_data['close'] > 50):
        buy_year_high(regression_data, regressionResult, reg, ws)
        buy_year_low(regression_data, regressionResult, reg, ws, ws)
        buy_down_trend(regression_data, regressionResult, reg, ws)
        buy_final(regression_data, regressionResult, reg, ws, ws)
        buy_pattern(regression_data, regressionResult, reg, ws, ws)
        buy_morning_star_buy(regression_data, regressionResult, reg, ws)
        buy_evening_star_sell(regression_data, regressionResult, reg, ws)
        buy_day_low(regression_data, regressionResult, reg, ws)
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
        buy_tail_reversal_filter(regression_data, regressionResult, reg, ws)
        
        sell_up_trend(regression_data, regressionResult, reg, ws)
        sell_down_trend(regression_data, regressionResult, reg, ws)
        sell_final(regression_data, regressionResult, reg, ws, ws)
        sell_pattern(regression_data, regressionResult, reg, ws, ws)
        sell_base_line_buy(regression_data, regressionResult, reg, ws)
        sell_morning_star_buy(regression_data, regressionResult, reg, ws)
        sell_evening_star_sell(regression_data, regressionResult, reg, ws)
        sell_day_high(regression_data, regressionResult, reg, ws)
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
        sell_tail_reversal_filter(regression_data, regressionResult, reg, ws)
        return True
    if(buy_skip_close_lt_50(regression_data, regressionResult, reg, ws)):
        return True
    return False

def buy_indicator_after_filter_accuracy(regression_data, regressionResult, reg, ws):
    if(is_any_sell_from_all_filter(regression_data) != True):
        buy_af_high_indicators(regression_data, regressionResult, reg, ws)
        buy_af_oi_negative(regression_data, regressionResult, reg, ws)
        buy_af_vol_contract(regression_data, regressionResult, reg, ws)
        buy_af_vol_contract_contrarian(regression_data, regressionResult, reg, ws)
        buy_af_others(regression_data, regressionResult, reg, ws)
        #buy_af_high_volatility(regression_data, regressionResult, reg, ws)
    buy_af_low_tail(regression_data, regressionResult, reg, ws)
    buy_af_up_continued(regression_data, regressionResult, reg, ws)
    #sell_af_high_tail(regression_data, regressionResult, reg, ws)
            
def buy_skip_close_lt_50(regression_data, regressionResult, reg, ws):
    return False
        
def buy_test_345(regression_data, regressionResult, reg, ws):
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
    regression_data['filterTest'] = filterName + ',' \
                                    + regression_data['series_trend'] + ',' \
                                    + regression_data['filter2'] + ',' \
                                    + regression_data['filter3'] + ',' \
                                    + regression_data['filter4'] + ',' \
                                    + regression_data['filter5']
    
    if regression_data['filterTest'] != '':
        return True  
    
    return False
  
def buy_test(regression_data, regressionResult, reg, ws):
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
                                    + pctChange5Day + ','\
                                    + regression_data['filter2'] + ',' \
                                    + regression_data['filter3'] + ',' \
                                    + regression_data['filter4'] + ',' \
                                    + regression_data['filter5']
                                    
    
    if regression_data['filterTest'] != '':
        return True  
    
    return False

def buy_test_pct_change(regression_data, regressionResult, reg, ws):
    regression_data['filter'] = " "
    regression_data['filter1'] = " "
    regression_data['filter2'] = " "
    regression_data['filter3'] = " "
    regression_data['filter4'] = " "
    regression_data['filter5'] = " "
    regression_data['filter6'] = " "
    regression_data['series_trend'] = trend_calculator(regression_data)
    flag = buy_other_indicator(regression_data, regressionResult, reg, ws)
    if regression_data['filterTest'] != '':
        filterName = pct_change_filter(regression_data, regressionResult, False)
        filterNameTail = tail_change_filter(regression_data, regressionResult, False)
        regression_data['filterTest'] = filterName + ',' \
                                        + filterNameTail + ',' \
                                        + regression_data['filterTest'].replace("[MLBuy]:", "").replace("[MLSell]:", "").strip()
    
    if regression_data['filterTest'] != '':
        return True
    
    return False  

def buy_test_all(regression_data, regressionResult, reg, ws):
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
    regression_data['filterTest'] = filterName + ',' \
                                    + filterNameTail + ',' \
                                    + regression_data['series_trend'] + ',' \
                                    + regression_data['filter2'] + ',' \
                                    + regression_data['filter3'] + ',' \
                                    + regression_data['filter4'] + ',' \
                                    + regression_data['filter5'] + ',' \
                                    + regression_data['filterTest'].replace("[MLBuy]:", "").replace("[MLSell]:", "").strip()
    if regression_data['filterTest'] != '':
        return True  
    return False

def buy_test_tech(regression_data, regressionResult, reg, ws):
    regression_data['filter'] = " "
    regression_data['filter1'] = " "
    regression_data['filter2'] = " "
    regression_data['filter3'] = " "
    regression_data['filter4'] = " "
    regression_data['filter5'] = " "
    regression_data['filter6'] = " "
    regression_data['series_trend'] = trend_calculator(regression_data)
    if (regression_data['buyIndia'] != '' or regression_data['sellIndia'] != ''):
        regression_data['filterTest'] = 'B@{' + regression_data['buyIndia'] + '}' \
                                        + 'S@{' + regression_data['sellIndia'] + '}'
        return True
    
    return False

def buy_test_tech_all(regression_data, regressionResult, reg, ws):
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
        regression_data['filterTest'] = filterName + ',' \
                                        + filterNameTail + ',' \
                                        + regression_data['series_trend'] + ',' \
                                        + 'B@{' + regression_data['buyIndia'] + '}' \
                                        + 'S@{' + regression_data['sellIndia'] + '}'
        return True
    
    return False

def buy_test_tech_all_pct_change(regression_data, regressionResult, reg, ws):
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
        regression_data['filterTest'] = filterName + ',' \
                                        + filterNameTail + ',' \
                                        + 'B@{' + regression_data['buyIndia'] + '}' \
                                        + 'S@{' + regression_data['sellIndia'] + '}' \
                                        + regression_data['filter2'] + ',' \
                                        + regression_data['filter3'] + ',' \
                                        + regression_data['filter4'] + ',' \
                                        + regression_data['filter5']
        return True
    
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
        if buy_day_low(regression_data, regressionResult, reg, ws):
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
    if buy_af_high_indicators(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws, None)
        flag = True
    if buy_pattern(regression_data, regressionResult, reg, None, None):
        add_in_csv(regression_data, regressionResult, ws, None)
        flag = True
    if buy_oi(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws, None)
        flag = True
    return flag

def buy_filter_345_accuracy(regression_data, regressionResult):
    filtersDict=filter345buy
    filterName = pct_change_filter(regression_data, regressionResult, False)
    filter = filterName + ',' \
            + regression_data['series_trend'] + ',' \
            + regression_data['filter2'] + ',' \
            + regression_data['filter3'] + ',' \
            + regression_data['filter4'] + ',' \
            + regression_data['filter5']
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
            + regression_data['filter2'] + ',' \
            + regression_data['filter3'] + ',' \
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
    if regression_data['filter'] != '':
        filterName = pct_change_filter(regression_data, regressionResult, False)
        filterNameTail = tail_change_filter(regression_data, regressionResult, False)
        filter = filterName + ',' \
                + filterNameTail + ',' \
                + regression_data['filter'].replace("[MLBuy]:", "").replace("[MLSell]:", "").strip()
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
    filter = filterName + ',' \
            + filterNameTail + ',' \
            + regression_data['series_trend'] + ',' \
            + regression_data['filter2'] + ',' \
            + regression_data['filter3'] + ',' \
            + regression_data['filter4'] + ',' \
            + regression_data['filter5'] + ',' \
            + regression_data['filter'].replace("[MLBuy]:", "").replace("[MLSell]:", "").strip()
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
    filter = 'B@{' + regression_data['buyIndia'] + '}' \
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
    filter = filterName + ',' \
            + filterNameTail + ',' \
            + regression_data['series_trend'] + ',' \
            + 'B@{' + regression_data['buyIndia'] + '}' \
            + 'S@{' + regression_data['sellIndia'] + '}'
            
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
    filter = filterName + ',' \
            + filterNameTail + ',' \
            + 'B@{' + regression_data['buyIndia'] + '}' \
            + 'S@{' + regression_data['sellIndia'] + '}' \
            + regression_data['filter2'] + ',' \
            + regression_data['filter3'] + ',' \
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
    buy_filter_345_accuracy(regression_data, regressionResult)
    buy_filter_accuracy(regression_data, regressionResult)
    buy_filter_pct_change_accuracy(regression_data, regressionResult) 
    buy_filter_345_all_accuracy(regression_data, regressionResult)
    buy_filter_tech_accuracy(regression_data, regressionResult)
    buy_filter_tech_all_accuracy(regression_data, regressionResult)
    buy_filter_tech_all_pct_change_accuracy(regression_data, regressionResult)
                           
def sell_all_rule(regression_data, regressionResult, sellIndiaAvg, ws):           
    if(is_algo_sell(regression_data)):
        if(3.5 < regression_data['PCT_day_change'] < 15 and 3.5 < regression_data['PCT_change'] < 15):
            add_in_csv(regression_data, regressionResult, ws, 'AF:mlSellPCTDayChangeGT4.5')
        elif(regression_data['week2LowChange'] > 20 and regression_data['weekLowChange'] > 10
            and -10 < regression_data['PCT_day_change'] < -2
            ):
            add_in_csv(regression_data, regressionResult, ws, 'AF:(NOT-UPTREND)0-mlSellWeek2LowGT20')
        elif(regression_data['week2LowChange'] > 10 and regression_data['weekLowChange'] > 10
            and (regression_data['week2LowChange'] > 15 or regression_data['weekLowChange'] > 15) 
            and -4 < regression_data['PCT_day_change'] < -2
            and is_any_buy_GT2_from_all_filter(regression_data) == False
            ):
            add_in_csv(regression_data, regressionResult, ws, 'AF:(NOT-UPTREND)1-mlSellWeek2LowOrWeekLowGT15')
#         elif(regression_data['week2LowChange'] > 5 and regression_data['weekLowChange'] > 10
#             and -5 < regression_data['PCT_day_change'] < -2
#             and is_any_buy_GT2_from_all_filter(regression_data) == False
#             ):
#             add_in_csv(regression_data, regressionResult, ws, 'AF:1-mlSellWeekLowGT10')
#         elif(regression_data['week2LowChange'] > 5 and regression_data['weekLowChange'] > 0
#             and -4 < regression_data['PCT_day_change'] < 1
#             and is_any_buy_GT2_from_all_filter(regression_data) == False
#             ):
#             add_in_csv(regression_data, regressionResult, ws, 'AF:3-mlSellWeek2LowGT5')
    
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
        and '(Confirmed)EMA6<EMA14' not in regression_data['filter4']
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
            add_in_csv(regression_data, regressionResult, ws, 'CommonHL:sellNotM3HighLow-0(SMA9LT-1)') 
        elif(regression_data['SMA25'] < 0):
            add_in_csv(regression_data, regressionResult, ws, None) 
        else:
            add_in_csv(regression_data, regressionResult, ws, None) 
                
    return False

def sell_all_common_High_Low(regression_data, regressionResult, reg, ws):
    if((regression_data['forecast_day_PCT3_change'] < 0 and regression_data['forecast_day_PCT4_change'] < 0)
        or regression_data['forecast_day_PCT5_change'] < 0
        or regression_data['forecast_day_PCT7_change'] < 0
        or regression_data['forecast_day_PCT10_change'] < 0
        ):
        if(-2.9 > regression_data['PCT_day_change'] > -4.1 and -1 > regression_data['PCT_change'] > -4.5
            and regression_data['PCT_day_change_pre1'] < 1.3
            and (regression_data['PCT_day_change_pre1'] > 0
                 or regression_data['PCT_day_change_pre2'] > 0
                 or regression_data['PCT_day_change_pre3'] > 0
                 )
            and low_tail_pct(regression_data) < 1.29
            and high_tail_pct(regression_data) < 2.5
            ):
            add_in_csv(regression_data, regressionResult, ws, 'CommonHL:HighDowntrend')
        elif(-2.7 > regression_data['PCT_day_change'] > -5.5
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
            and regression_data['forecast_day_PCT4_change'] < 0
            and regression_data['forecast_day_PCT5_change'] < 0
            and regression_data['SMA4'] < -2
            and regression_data['SMA9'] < -2 
            and low_tail_pct(regression_data) < 2.5
            and high_tail_pct(regression_data) < 2.5
            ):
            if(-2.95 > regression_data['PCT_day_change']
    #             and(regression_data['PCT_day_change_pre1'] < 0
    #                 or regression_data['PCT_day_change_pre2'] < 0
    #                 or regression_data['PCT_day_change_pre3'] < 0
    #                 or regression_data['PCT_day_change_pre4'] < 0
    #                 )
                ):
                add_in_csv(regression_data, regressionResult, ws, 'CommonHL:HEAVYDOWNTRENDMARKET:HighDowntrend')
            elif(regression_data['PCT_day_change_pre1'] < 0
                or regression_data['PCT_day_change_pre2'] < 0
                or regression_data['PCT_day_change_pre3'] < 0
                ):
                add_in_csv(regression_data, regressionResult, ws, 'CommonHL:HEAVYDOWNTRENDMARKET:HighDowntrend-(NOT-GLOBAL-UP)')
    
    if((regression_data['forecast_day_PCT7_change'] < -15 or regression_data['forecast_day_PCT5_change'] < -15)
        and (regression_data['PCT_day_change_pre1'] < -2.5 or regression_data['PCT_day_change_pre2'] < -2.5)
        and ('set1' in regression_data['filter'] or 'set2' in regression_data['filter'])
        and low_tail_pct(regression_data) < 2.5
        and high_tail_pct(regression_data) < 2.5
        ):
        add_in_csv(regression_data, regressionResult, ws, 'CommonHL:HighSuperDownTrend')
        
    sell_common_down_continued(regression_data, regressionResult, reg, ws)
          
def sell_other_indicator(regression_data, regressionResult, reg, ws):
    tail_pct_filter(regression_data, regressionResult)
    base_line(regression_data, regressionResult, reg, ws)
    filterMA(regression_data, regressionResult)
    tail_reversal_filter(regression_data, regressionResult)
    if(regression_data['close'] > 50):
        sell_up_trend(regression_data, regressionResult, reg, ws)
        sell_down_trend(regression_data, regressionResult, reg, ws)
        sell_final(regression_data, regressionResult, reg, ws, ws)
        sell_pattern(regression_data, regressionResult, reg, ws, ws)
        sell_base_line_buy(regression_data, regressionResult, reg, ws)
        sell_morning_star_buy(regression_data, regressionResult, reg, ws)
        sell_evening_star_sell(regression_data, regressionResult, reg, ws)
        sell_day_high(regression_data, regressionResult, reg, ws)
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
        sell_tail_reversal_filter(regression_data, regressionResult, reg, ws)
        
        buy_year_high(regression_data, regressionResult, reg, ws)
        buy_year_low(regression_data, regressionResult, reg, ws, ws)
        buy_down_trend(regression_data, regressionResult, reg, ws)
        buy_final(regression_data, regressionResult, reg, ws, ws)
        buy_pattern(regression_data, regressionResult, reg, ws, ws)
        buy_morning_star_buy(regression_data, regressionResult, reg, ws)
        buy_evening_star_sell(regression_data, regressionResult, reg, ws)
        buy_day_low(regression_data, regressionResult, reg, ws)
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
        buy_tail_reversal_filter(regression_data, regressionResult, reg, ws)
        return True
    if(sell_skip_close_lt_50(regression_data, regressionResult, reg, ws)):
        return True
    return False

def sell_indicator_after_filter_accuracy(regression_data, regressionResult, reg, ws):
    if(is_any_buy_from_all_filter(regression_data) != True):
        sell_af_high_indicators(regression_data, regressionResult, reg, ws)
        sell_af_oi_negative(regression_data, regressionResult, reg, ws)
        sell_af_vol_contract(regression_data, regressionResult, reg, ws)
        sell_af_vol_contract_contrarian(regression_data, regressionResult, reg, ws)
        sell_af_others(regression_data, regressionResult, reg, ws)
        #sell_af_high_volatility(regression_data, regressionResult, reg, ws)
    sell_af_high_tail(regression_data, regressionResult, reg, ws)
    sell_af_down_continued(regression_data, regressionResult, reg, ws)
    
                
def sell_skip_close_lt_50(regression_data, regressionResult, reg, ws):
    if((regression_data['weekLowChange'] > 15) 
        and (-10 < regression_data['PCT_change'] < -4)
        and (-10 < regression_data['PCT_day_change'] < -4)
        ):
        add_in_csv(regression_data, regressionResult, ws, '(Test)sellUptrendReversal')
        return True
    return False

def sell_test_345(regression_data, regressionResult, reg, ws):
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
    regression_data['filterTest'] = filterName + ',' \
                                    + regression_data['series_trend'] + ',' \
                                    + regression_data['filter2'] + ',' \
                                    + regression_data['filter3'] + ',' \
                                    + regression_data['filter4'] + ',' \
                                    + regression_data['filter5']
    if regression_data['filterTest'] != '':
        return True  
    return False
        
def sell_test(regression_data, regressionResult, reg, ws):
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
                                    + regression_data['filter2'] + ',' \
                                    + regression_data['filter3'] + ',' \
                                    + regression_data['filter4'] + ',' \
                                    + regression_data['filter5']
                                    
    if regression_data['filterTest'] != '':
        return True  
    return False

def sell_test_pct_change(regression_data, regressionResult, reg, ws):
    regression_data['filter'] = " "
    regression_data['filter1'] = " "
    regression_data['filter2'] = " "
    regression_data['filter3'] = " "
    regression_data['filter4'] = " "
    regression_data['filter5'] = " "
    regression_data['filter6'] = " "
    regression_data['series_trend'] = trend_calculator(regression_data)
    flag = sell_other_indicator(regression_data, regressionResult, reg, ws)
    if regression_data['filterTest'] != '':
        filterName = pct_change_filter(regression_data, regressionResult, False)
        filterNameTail = tail_change_filter(regression_data, regressionResult, False)
        regression_data['filterTest'] = filterName + ',' \
                                        + filterNameTail + ',' \
                                        + regression_data['filterTest'].replace("[MLBuy]:", "").replace("[MLSell]:", "").strip()
    
    if regression_data['filterTest'] != '':
        return True
        
    return False

def sell_test_all(regression_data, regressionResult, reg, ws):
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
    regression_data['filterTest'] = filterName + ',' \
                                    + filterNameTail + ',' \
                                    + regression_data['series_trend'] + ',' \
                                    + regression_data['filter2'] + ',' \
                                    + regression_data['filter3'] + ',' \
                                    + regression_data['filter4'] + ',' \
                                    + regression_data['filter5'] + ',' \
                                    + regression_data['filterTest'].replace("[MLBuy]:", "").replace("[MLSell]:", "").strip()
    if regression_data['filterTest'] != '':
        return True  
    return False

def sell_test_tech(regression_data, regressionResult, reg, ws):
    regression_data['filter'] = " "
    regression_data['filter1'] = " "
    regression_data['filter2'] = " "
    regression_data['filter3'] = " "
    regression_data['filter4'] = " "
    regression_data['filter5'] = " "
    regression_data['filter6'] = " "
    regression_data['series_trend'] = trend_calculator(regression_data)
    if (regression_data['buyIndia'] != '' or regression_data['sellIndia'] != ''):
        regression_data['filterTest'] = 'B@{' + regression_data['buyIndia'] + '}' \
                                        + 'S@{' + regression_data['sellIndia'] + '}' 
        return True
    
    return False

def sell_test_tech_all(regression_data, regressionResult, reg, ws):
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
        regression_data['filterTest'] = filterName + ',' \
                                        + filterNameTail + ',' \
                                        + regression_data['series_trend'] + ',' \
                                        + 'B@{' + regression_data['buyIndia'] + '}' \
                                        + 'S@{' + regression_data['sellIndia'] + '}'
        return True
    
    return False

def sell_test_tech_all_pct_change(regression_data, regressionResult, reg, ws):
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
        regression_data['filterTest'] = filterName + ',' \
                                        + filterNameTail + ',' \
                                        + 'B@{' + regression_data['buyIndia'] + '}' \
                                        + 'S@{' + regression_data['sellIndia'] + '}' \
                                        + regression_data['filter2'] + ',' \
                                        + regression_data['filter3'] + ',' \
                                        + regression_data['filter4'] + ',' \
                                        + regression_data['filter5']
        return True
    
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
        if sell_day_high(regression_data, regressionResult, reg, ws):
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
    if sell_af_high_indicators(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws, None)
        flag = True
    if sell_pattern(regression_data, regressionResult, reg, None, None):
        add_in_csv(regression_data, regressionResult, ws, None)
        flag = True
    if sell_oi(regression_data, regressionResult, reg, None):
        add_in_csv(regression_data, regressionResult, ws, None)
        flag = True
    return flag

def sell_filter_345_accuracy(regression_data, regressionResult):
    filtersDict = filter345sell
    filterName = pct_change_filter(regression_data, regressionResult, False)
    filter = filterName + ',' \
                + regression_data['series_trend'] + ',' \
                + regression_data['filter2'] + ',' \
                + regression_data['filter3'] + ',' \
                + regression_data['filter4'] + ',' \
                + regression_data['filter5']
                
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
            + regression_data['filter2'] + ',' \
            + regression_data['filter3'] + ',' \
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
    if regression_data['filter'] != '':
        filterName = pct_change_filter(regression_data, regressionResult, False)
        filterNameTail = tail_change_filter(regression_data, regressionResult, False)
        filter = filterName + ',' \
                + filterNameTail + ',' \
                + regression_data['filter'].replace("[MLBuy]:", "").replace("[MLSell]:", "").strip()
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
    filter = filterName + ',' \
                + filterNameTail + ',' \
                + regression_data['series_trend'] + ',' \
                + regression_data['filter2'] + ',' \
                + regression_data['filter3'] + ',' \
                + regression_data['filter4'] + ',' \
                + regression_data['filter5'] + ',' \
                + regression_data['filter'].replace("[MLBuy]:", "").replace("[MLSell]:", "").strip()
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
    filter ='B@{' + regression_data['buyIndia'] + '}' \
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
    filter = filterName + ',' \
            + filterNameTail + ',' \
            + regression_data['series_trend'] + ',' \
            + 'B@{' + regression_data['buyIndia'] + '}' \
            + 'S@{' + regression_data['sellIndia'] + '}'
            
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
    filter = filterName + ',' \
            + filterNameTail + ',' \
            + 'B@{' + regression_data['buyIndia'] + '}' \
            + 'S@{' + regression_data['sellIndia'] + '}' \
            + regression_data['filter2'] + ',' \
            + regression_data['filter3'] + ',' \
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
    if(regression_data['filter_345_avg'] > val
        and (regression_data['filter_345_pct'] >= 60 or regression_data['filter_345_pct'] == 0)
        and regression_data['filter_345_avg'] != regression_data['filter_all_avg']
        ):
        count = count + 1
        if(regression_data['filter_345_count'] > 1):
            cnt = cnt + 1  
    if(regression_data['filter_avg'] > val
        and (regression_data['filter_pct'] >= 60 or regression_data['filter_pct'] == 0)
        and regression_data['filter_avg'] != regression_data['filter_all_avg']
        ):
        count = count + 1
        if(regression_data['filter_count'] > 1):
            cnt = cnt + 1
    if(regression_data['filter_pct_change_avg'] > val
        and (regression_data['filter_pct_change_pct'] >= 60 or regression_data['filter_pct_change_pct'] == 0)
        ):
        count = count + 1
        if(regression_data['filter_pct_change_count'] > 1):
            cnt = cnt + 1
    if(regression_data['filter_all_avg'] > val
        and (regression_data['filter_all_pct'] >= 60 or regression_data['filter_all_pct'] == 0)
        ):
        count = count + 1
        if(regression_data['filter_all_count'] > 1):
            cnt = cnt + 1
    if(regression_data['filter_tech_avg'] > val
        and (regression_data['filter_tech_pct'] >= 70 or regression_data['filter_tech_pct'] == 0)
        ):
        count = count + 1
        if(regression_data['filter_tech_count'] > 1):
            cnt = cnt + 1
    if(regression_data['filter_tech_all_avg'] > 2
        and (regression_data['filter_tech_all_pct'] >= 70 or regression_data['filter_tech_all_pct'] == 0)
        ):
        count = count + 1
        if(regression_data['filter_tech_all_count'] > 1):
            cnt = cnt + 1
    if(regression_data['filter_tech_all_pct_change_avg'] > 2
        and (regression_data['filter_tech_all_pct_change_pct'] >= 70 or regression_data['filter_tech_all_pct_change_pct'] == 0)
        ):
        count = count + 1
        if(regression_data['filter_tech_all_pct_change_count'] > 1):
            cnt = cnt + 1
    return count, cnt
    
def filter_avg_lt_count(regression_data, val):
    count = 0
    cnt = 0
    if(regression_data['filter_345_avg'] < val
        and (regression_data['filter_345_pct'] < -60 or regression_data['filter_345_pct'] == 0)
        and regression_data['filter_345_avg'] != regression_data['filter_all_avg']
        ):
        count = count + 1
        if(regression_data['filter_345_count'] > 1):
            cnt = cnt + 1
    if(regression_data['filter_avg'] < val
        and (regression_data['filter_pct'] < -60 or regression_data['filter_pct'] == 0)
        and regression_data['filter_avg'] != regression_data['filter_all_avg']
        ):
        count = count + 1
        if(regression_data['filter_count'] > 1):
            cnt = cnt + 1
    if(regression_data['filter_pct_change_avg'] < val
        and (regression_data['filter_pct_change_pct'] < -60 or regression_data['filter_pct_change_pct'] == 0)
        ):
        count = count + 1
        if(regression_data['filter_pct_change_count'] > 1):
            cnt = cnt + 1
    if(regression_data['filter_all_avg'] < val
        and (regression_data['filter_all_pct'] < -60 or regression_data['filter_all_pct'] == 0)
        ):
        count = count + 1
        if(regression_data['filter_all_count'] > 1):
            cnt = cnt + 1
    if(regression_data['filter_tech_avg'] < val
        and (regression_data['filter_tech_pct'] < -70 or regression_data['filter_tech_pct'] == 0)
        ):
        count = count + 1
        if(regression_data['filter_tech_count'] > 1):
            cnt = cnt + 1
    if(regression_data['filter_tech_all_avg'] < -2
        and (regression_data['filter_tech_all_pct'] < -70 or regression_data['filter_tech_all_pct'] == 0)
        ):
        count = count + 1
        if(regression_data['filter_tech_all_count'] > 1):
            cnt = cnt + 1
    if(regression_data['filter_tech_all_pct_change_avg'] < -2
        and (regression_data['filter_tech_all_pct_change_pct'] < -70 or regression_data['filter_tech_all_pct_change_pct'] == 0)
        ):
        count = count + 1
        if(regression_data['filter_tech_all_pct_change_count'] > 1):
            cnt = cnt + 1
    return count, cnt

def filter_avg_gt_1_count(regression_data):
    count = 0
    cnt = 0
    count, cnt = filter_avg_gt_count(regression_data, 1)
    if(cnt > 0):
        return count
    else:
        return 0
    
def filter_avg_lt_minus_1_count(regression_data):
    count = 0
    cnt = 0
    count, cnt = filter_avg_lt_count(regression_data, -1)
    if(cnt > 0):
        return count
    else:
        return 0

def filter_avg_gt_point9_count(regression_data):
    count = 0
    cnt = 0
    count, cnt = filter_avg_gt_count(regression_data, 0.9)
    if(cnt > 0):
        return count
    else:
        return 0
    
def filter_avg_lt_minus_point9_count(regression_data):
    count = 0
    cnt = 0
    count, cnt = filter_avg_lt_count(regression_data, -0.9)
    if(cnt > 0):
        return count
    else:
        return 0

def filter_avg_gt_2_count(regression_data):
    count = 0
    cnt = 0
    count, cnt = filter_avg_gt_count(regression_data, 2)
    if(cnt > 0):
        return count
    else:
        return 0
    
def filter_avg_lt_minus_2_count(regression_data):
    count = 0
    cnt = 0
    count, cnt = filter_avg_lt_count(regression_data, -2)
    if(cnt > 0):
        return count
    else:
        return 0
         
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
            add_in_csv(regression_data, regressionResult, ws, None, None, 'Sell-SUPER') 
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, 'Sell-SUPER-Risky')  
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
            add_in_csv(regression_data, regressionResult, ws, None, None, 'Buy-SUPER')
        else:
            add_in_csv(regression_data, regressionResult, ws, None, None, 'Buy-SUPER-risky')
    elif(filter_avg_lt_minus_point9_count(regression_data) >= 2
       and 'RISKYBASELINESELL' not in regression_data['filter5']
      ):
       add_in_csv(regression_data, regressionResult, ws, None, None, 'LT-0.9-Sell-SUPER-Risky')  
    elif(filter_avg_gt_point9_count(regression_data) >= 2
       and 'RISKYBASELINEBUY' not in regression_data['filter5']
       ):
       add_in_csv(regression_data, regressionResult, ws, None, None, 'GT0.9-Buy-SUPER-risky')
    
    
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
    if(abs(regression_data['filter_tech_avg']) > 2):
        flag = filter_accuracy_finder_all(regression_data, regression_high, regression_low, regressionResult, high_or_low, ws, 'filter_tech_avg', 'filter_tech_count', 'filter_tech_pct')
        if(flag):
            superflag = True
    if((abs(regression_data['filter_tech_all_avg']) > 3 and regression_data['filter_tech_all_count'] >= 3) or regression_data['filter_tech_all_count'] > 5):
        flag = filter_accuracy_finder_all(regression_data, regression_high, regression_low, regressionResult, high_or_low, ws, 'filter_tech_all_avg', 'filter_tech_all_count', 'filter_tech_all_pct')
        if(flag):
            superflag = True
    if((abs(regression_data['filter_tech_all_pct_change_avg']) > 3 and regression_data['filter_tech_all_pct_change_count'] >= 3) or regression_data['filter_tech_all_pct_change_count'] > 5):
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
    if(abs(regression_data['filter_tech_avg']) > 2):
        flag = filter_accuracy_finder(regression_data, regression_high, regression_low, regressionResult, high_or_low, ws, 'filter_tech_avg', 'filter_tech_count', 'filter_tech_pct')
        if(flag):
            superflag = True
    if((abs(regression_data['filter_tech_all_avg']) > 3 and regression_data['filter_tech_all_count'] >= 3) or regression_data['filter_tech_all_count'] > 5):
        flag = filter_accuracy_finder(regression_data, regression_high, regression_low, regressionResult, high_or_low, ws, 'filter_tech_all_avg', 'filter_tech_all_count', 'filter_tech_all_pct')
        if(flag):
            superflag = True
    if((abs(regression_data['filter_tech_all_pct_change_avg']) > 3 and regression_data['filter_tech_all_pct_change_count'] >= 3) or regression_data['filter_tech_all_pct_change_count'] > 5):
        flag = filter_accuracy_finder(regression_data, regression_high, regression_low, regressionResult, high_or_low, ws, 'filter_tech_all_pct_change_avg', 'filter_tech_all_pct_change_count', 'filter_tech_all_pct_change_pct')
        if(flag):
            superflag = True
    
    flag = filter_accuracy_finder_stable_all(regression_data, regressionResult, high_or_low, ws, 'filter_345_avg', 'filter_345_count', 'filter_345_pct')
    if(flag):
        superflag = True   
    flag = filter_accuracy_finder_stable_all(regression_data, regressionResult, high_or_low, ws, 'filter_avg', 'filter_count', 'filter_pct')
    if(flag):
        superflag = True
    flag = filter_accuracy_finder_stable_all(regression_data, regressionResult, high_or_low, ws, 'filter_pct_change_avg', 'filter_pct_change_count', 'filter_pct_change_pct')
    if(flag):
        superflag = True
    flag = filter_accuracy_finder_stable_all(regression_data, regressionResult, high_or_low, ws, 'filter_all_avg', 'filter_all_count', 'filter_all_pct')
    if(flag):
        superflag = True 
    if(abs(regression_data['filter_tech_avg']) > 2):    
        flag = filter_accuracy_finder_stable_all(regression_data, regressionResult, high_or_low, ws, 'filter_tech_avg', 'filter_tech_count', 'filter_tech_pct')
        if(flag):
            superflag = True
    if((abs(regression_data['filter_tech_all_avg']) > 2 and regression_data['filter_tech_all_count'] >= 3) or regression_data['filter_tech_all_avg'] > 5):
        flag = filter_accuracy_finder_stable_all(regression_data, regressionResult, high_or_low, ws, 'filter_tech_all_avg', 'filter_tech_all_count', 'filter_tech_all_pct')
        if(flag):
            superflag = True
    if((abs(regression_data['filter_tech_all_pct_change_avg']) > 2 and regression_data['filter_tech_all_pct_change_count'] >= 3) or regression_data['filter_tech_all_avg'] > 5):
        flag = filter_accuracy_finder_stable_all(regression_data, regressionResult, high_or_low, ws, 'filter_tech_all_pct_change_avg', 'filter_tech_all_pct_change_count', 'filter_tech_all_pct_change_pct')
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
      
    flag = filter_accuracy_finder_stable(regression_data, regressionResult, high_or_low, ws, 'filter_pct_change_avg', 'filter_pct_change_count', 'filter_pct_change_pct')
    if(flag):
        superflag = True 
        
       
    
#     if(buy_high_volatility(regression_data, regressionResult, reg, ws)):
#         superflag = True
#     if(sell_high_volatility(regression_data, regressionResult, reg, ws)):
#         superflag = True 
    if(regression_data['filter_pct_change_avg'] > 2 and regression_data['filter_pct_change_count'] >= 2 and regression_data['filter_pct_change_pct'] > 70
        and "MLSell" not in regression_data['filter']
        ):
        add_in_csv(regression_data, regressionResult, ws, None,'Filter-All-Buy')
    elif(regression_data['filter_pct_change_avg'] > 1.5 and regression_data['filter_pct_change_count'] >= 2 and regression_data['filter_pct_change_pct'] > 70
        and "MLSell" not in regression_data['filter'] 
        ):
        add_in_csv(regression_data, regressionResult, ws, None,'Filter-All-Buy-risky')
    if(regression_data['filter_pct_change_avg'] < -2 and regression_data['filter_pct_change_count'] >= 2 and regression_data['filter_pct_change_pct'] < -70
        and "MLBuy" not in regression_data['filter']
        ):
        add_in_csv(regression_data, regressionResult, ws, None,'Filter-All-Sell')
    elif(regression_data['filter_pct_change_avg'] < -1.5 and regression_data['filter_pct_change_count'] >= 2 and regression_data['filter_pct_change_pct'] < -70
        and "MLBuy" not in regression_data['filter']
        ):
        add_in_csv(regression_data, regressionResult, ws, None,'Filter-All-Sell-risky')
        
    
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
            
        buyRisky, sellRisky =  is_filter_risky(regression_data, regressionResult, high_or_low, ws, filter_avg, filter_count, filter_pct, False)   
        if(len(regression_data['filter']) > 9 
            and ((regression_data[filter_avg] >= 0.75 and regression_data[filter_count] >= 3 and regression_data[filter_pct] > 100 and regression_data['PCT_day_change'] < 2)
                 or (regression_data[filter_avg] >= 1.5 and regression_data[filter_count] >= 5 and regression_data[filter_pct] > 80)
                 or (regression_data[filter_avg] >= 2 and regression_data[filter_count] >= 4 and regression_data[filter_pct] > 80)
                 #or (regression_data[filter_avg] >= 2.5 and regression_data[filter_count] >= 2 and regression_data[filter_pct] >= 80)
                 )
            and ("MLBuy" in regression_data['filter'])
            and is_buy_filter_not_risky(regression_data)
            #and high_tail_pct(regression_data) < 1.5 and low_tail_pct(regression_data) < 2.5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, 'Filter-Buy')
            flag = True
        
        if(len(regression_data['filter']) > 9
            and ((regression_data[filter_avg] <= -0.75 and regression_data[filter_count] >= 3 and regression_data[filter_pct] < -100 and regression_data['PCT_day_change'] > -2)
                 or (regression_data[filter_avg] <= -1.5 and regression_data[filter_count] >= 5 and regression_data[filter_pct] < -80)
                 or (regression_data[filter_avg] <= -2 and regression_data[filter_count] >= 4 and regression_data[filter_pct] < -80)
                 #or (regression_data[filter_avg] <= -2.5 and regression_data[filter_count] >= 2 and regression_data[filter_pct] <= -80)
                 )
            and ("MLSell" in regression_data['filter'])
            and is_sell_filter_not_risky(regression_data)
            #and low_tail_pct(regression_data) < 1.5 and high_tail_pct(regression_data) < 2.5
            ):
            add_in_csv(regression_data, regressionResult, ws, None, 'Filter-Sell')
            flag = True      
                
        if(regression_data[filter_count] >= 3
            and abs(regression_data[filter_pct]) >= 90
            and abs(regression_data[filter_avg]) >= 2
            ):
            if(regression_data[filter_avg] >= 0 
                and (filter_avg_gt_1_count(regression_data) >= 2 or regression_data[filter_count] >= 4)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-8-Buy')
            elif(regression_data[filter_avg] < 0 
                and (filter_avg_lt_minus_1_count(regression_data) >= 2 or regression_data[filter_count] >= 4)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-8-Sell')
        
        if(regression_data[filter_count] >= 3
            and abs(regression_data[filter_pct]) >= 85
            and abs(regression_data[filter_avg]) >= 3
            ):
            if(regression_data[filter_avg] >= 0):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-5-Buy')
            elif(regression_data[filter_avg] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-5-Sell')
        elif(regression_data[filter_count] >= 2
            and((abs(regression_data[filter_pct]) >= 100 and abs(regression_data[filter_avg]) >= 2.5 and regression_data[filter_count] >= 3)
                 or (abs(regression_data[filter_pct]) >= 70 and abs(regression_data[filter_avg]) >= 3.5)
                 )
            ):
            if(regression_data[filter_avg] >= 0 and is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-6-Buy')
            elif(regression_data[filter_avg] < 0 and is_algo_sell(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-6-Sell')
        elif(regression_data[filter_count] >= 2
            and abs(regression_data[filter_pct]) >= 80
            and abs(regression_data[filter_avg]) >= 2
            and (abs(regression_data[filter_avg]) > 3 or regression_data[filter_count] > 3)
            ):
            if(regression_data[filter_avg] >= 0 and is_algo_buy(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-7-Buy')
            elif(regression_data[filter_avg] < 0 and is_algo_sell(regression_data)):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-7-Sell')
            
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
    if(abs(regression_data[filter_avg]) > 0.5
        and ((regression_data[filter_avg] > 0 and (high_tail_pct(regression_data) < 1.3 or regression_data['PCT_day_change'] < 0 or regression_data['PCT_day_change'] > 3))
             or (regression_data[filter_avg] < 0 and (low_tail_pct(regression_data) < 1.3 or regression_data['PCT_day_change'] > 0 or regression_data['PCT_day_change'] < -3))
            )
        and regression_data[filter_count] >= 1
        and regression_data['close'] > 60
        #and (regression_data[filter_count_oth] >= 2
        #    or (regression_data[filter_count_oth] >= 1 and abs(regression_data[filter_avg_oth]) > 2))
        ):
        if((("MLSell" in regression_data['filter']) and (float(regression_data[filter_avg]) > 1) and (abs(float(regression_data[filter_pct])) > 70))
            or (("MLBuy" in regression_data['filter']) and (float(regression_data[filter_avg]) < -1) and (abs(float(regression_data[filter_pct])) > 70))
            or (("MLSell" in regression_data['filter']) and ("Buy-SUPER" in regression_data['filter2']))
            or (("MLBuy" in regression_data['filter']) and ("Sell-SUPER" in regression_data['filter2']))
            ):
            return False
            
        if(regression_data[filter_count] >= 3
            and abs(regression_data[filter_pct]) > 80
            and abs(regression_data[filter_avg]) > 3
            ):
            if(regression_data[filter_avg] >= 0):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-2-Buy')
            elif(regression_data[filter_avg] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-2-Sell')   
        elif(regression_data[filter_count] >= 3
            and abs(regression_data[filter_pct]) > 85
            and abs(regression_data[filter_avg]) > 2.5
            and abs(regression_data[filter_count] * regression_data[filter_avg]) > 9
            ):
            if(regression_data[filter_avg] >= 0):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-3-Buy')
            elif(regression_data[filter_avg] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-3-Sell')
        elif(regression_data[filter_count] >= 3
            and abs(regression_data[filter_pct]) >= 85
            and abs(regression_data[filter_avg]) >= 2.0
            ):
            if(regression_data[filter_avg] >= 0):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-4-Buy')
            elif(regression_data[filter_avg] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-4-Sell')
        elif(regression_data[filter_count] > 5
            and abs(regression_data[filter_pct]) >= 80
            and abs(regression_data[filter_avg]) > 1.5
            ):
            if(regression_data[filter_avg] >= 0
                and ((abs(regression_data[filter_avg]) > 1.5 and abs(regression_data[filter_pct]) >= 80) or is_algo_buy(regression_data))
                #and (abs(regression_data[filter_avg]) > 2 or regression_data['PCT_day_change'] < 0)
                and (abs(regression_data[filter_avg]) > 2 
                     or (abs(regression_data[filter_avg])*2 > abs(regression_data['PCT_day_change']))
                     or high_or_low == 'High'
                     or high_or_low == 'None'
                     )
                ):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-Risky-Buy')
            elif(regression_data[filter_avg] < 0
                and ((abs(regression_data[filter_avg]) > 1.5 and abs(regression_data[filter_pct]) >= 80) or is_algo_sell(regression_data))
                #and (abs(regression_data[filter_avg]) > 2 or regression_data['PCT_day_change'] > 0)
                and (abs(regression_data[filter_avg]) > 2 
                     or (abs(regression_data[filter_avg])*2 > abs(regression_data['PCT_day_change']))
                     or high_or_low == 'Low'
                     or high_or_low == 'None'
                     )
                ):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-Risky-Sell')
        
        
        if(regression_data[filter_count] >= 3
            and abs(regression_data[filter_pct]) >= 100
            and abs(regression_data[filter_avg]) > 2
            ):
            if(regression_data[filter_avg] >= 0
                and is_algo_sell(regression_high) != True
                and is_algo_sell(regression_low) != True
                #and (is_algo_buy(regression_high) == True or is_algo_buy(regression_low) == True)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-1-Buy')
            elif(regression_data[filter_avg] < 0
                and is_algo_buy(regression_high) != True
                and is_algo_buy(regression_low) != True
                #and (is_algo_sell(regression_high) == True or is_algo_sell(regression_low) == True)
                ):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-1-Sell')
                
        if(regression_data[filter_count] >= 5
            and abs(regression_data[filter_pct]) >= 100
            and abs(regression_data[filter_avg]) > 2
            ):
            if(regression_data[filter_avg] >= 0):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-0-Buy')
            elif(regression_data[filter_avg] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-0-Sell')
        elif(regression_data[filter_count] >= 4
            and abs(regression_data[filter_pct]) >= 100
            and abs(regression_data[filter_avg]) > 2.5
            ):
            if(regression_data[filter_avg] >= 0):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-0-Buy')
            elif(regression_data[filter_avg] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-0-Sell')
        elif(regression_data[filter_count] >= 3
            and abs(regression_data[filter_pct]) >= 100
            and abs(regression_data[filter_avg]) > 5
            ):
            if(regression_data[filter_avg] >= 0):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-0-Buy')
            elif(regression_data[filter_avg] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-0-Sell')
        
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
                    
        #is_filter_risky(regression_data, regressionResult, high_or_low, ws, filter_avg, filter_count, filter_pct)
        return flag            

def filter_accuracy_finder_stable(regression_data, regressionResult, high_or_low, ws, filter_avg, filter_count, filter_pct):   
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
        
        if(regression_data[filter_count] >= 5
            and abs(regression_data[filter_pct]) > 70
            and abs(regression_data[filter_avg]) > 1.5
            ):
            if(regression_data[filter_avg] >= 0
                and ((abs(regression_data[filter_avg]) > 1 and abs(regression_data[filter_pct]) >= 80) or is_algo_buy(regression_data))
                and ("MLSell" not in regression_data['filter'])
                ):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-Buy-count')
            elif(regression_data[filter_avg] < 0
                and ((abs(regression_data[filter_avg]) > 1 and abs(regression_data[filter_pct]) >= 80) or is_algo_sell(regression_data))
                and ("MLBuy" not in regression_data['filter'])
                ):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-Sell-count')
            flag = True
        elif(regression_data[filter_count] >= 2
            and abs(regression_data[filter_pct]) > 80
            and abs(regression_data[filter_avg]) > 1.5
            ):
            if(regression_data[filter_avg] >= 0
                and regression_data['PCT_day_change'] > 0
                and ("MLSell" not in regression_data['filter'])
                ):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-Buy-avg')
            elif(regression_data[filter_avg] <= 0
                and regression_data['PCT_day_change'] < 0
                and ("MLBuy" not in regression_data['filter'])
                ):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-Sell-avg')
            flag = True
        return flag

def filter_accuracy_finder_stable_all(regression_data, regressionResult, high_or_low, ws, filter_avg, filter_count, filter_pct):
    if(abs(regression_data[filter_avg]) >= 0.5
        and ((regression_data[filter_avg] > 0 and (high_tail_pct(regression_data) < 1.3 or regression_data['PCT_day_change'] < 0 or regression_data['PCT_day_change'] > 3))
             or (regression_data[filter_avg] < 0 and (low_tail_pct(regression_data) < 1.3 or regression_data['PCT_day_change'] > 0 or regression_data['PCT_day_change'] < -3))
            )
        and regression_data[filter_count] >= 1
        #and (regression_data[filter_count_oth] >= 2
        #    or (regression_data[filter_count_oth] >= 1 and abs(regression_data[filter_avg_oth]) > 2))
        ):
        flag = False
        if(regression_data[filter_count] >= 3
            and abs(regression_data[filter_pct]) >= 85
            and abs(regression_data[filter_avg]) > 5
            ):
            if(regression_data[filter_avg] >= 0):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-SUPER-Buy')
            elif(regression_data[filter_avg] < 0):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-SUPER-Sell')
            flag = True
            
        if(regression_data[filter_count] >= 0
            and abs(regression_data[filter_pct]) >= 60
            and 'STRONG' not in regression_data['filter1']
            ):
            if(regression_data[filter_avg] >= 0
                and abs(regression_data[filter_avg]) > 1.75
                and regression_data['PCT_day_change'] < 2
                and (regression_data[filter_count] >= 3 
                     or (regression_data[filter_avg] - regression_data['PCT_day_change']) > 2
                    )
                and regression_data[filter_avg] > regression_data['PCT_day_change']
                and 'MLSell' not in regression_data['filter']
                and ('Buy-SUPER' in regression_data['filter2'] or 'Buy-SUPER-risky' in regression_data['filter2'])
                ):
                add_in_csv(regression_data, regressionResult, ws, None, 'SUPER-Buy')
                flag = True
            elif(regression_data[filter_avg] <= 0
                and abs(regression_data[filter_avg]) > 1.75
                and regression_data['PCT_day_change'] > -2
                and (regression_data[filter_count] >= 3 
                     or (regression_data[filter_avg] - regression_data['PCT_day_change']) < -2
                     )
                and regression_data[filter_avg] < regression_data['PCT_day_change']
                and 'MLBuy' not in regression_data['filter']
                and ('Sell-SUPER' in regression_data['filter2'] or 'Sell-SUPER-risky' in regression_data['filter2'])
                ):
                add_in_csv(regression_data, regressionResult, ws, None, 'SUPER-Sell')
                flag = True
            elif(regression_data[filter_count] >= 3
                and abs(regression_data[filter_avg]) > 1
                and regression_data[filter_pct] >= 79 
                and (abs(regression_data[filter_avg]) > 2 
                     or (abs(regression_data[filter_avg])*2 > abs(regression_data['PCT_day_change']))
                     or high_or_low == 'High'
                     or high_or_low == 'None'
                     )
                and 'MLSell' not in regression_data['filter']
                ):
                add_in_csv(regression_data, regressionResult, ws, None, 'WEAK-Buy')
                flag = True
            elif(regression_data[filter_count] >= 3
                and abs(regression_data[filter_avg]) > 1  
                and regression_data[filter_pct] <= -79
                and (abs(regression_data[filter_avg]) > 2 
                     or (abs(regression_data[filter_avg])*2 > abs(regression_data['PCT_day_change']))
                     or high_or_low == 'Low'
                     or high_or_low == 'None'
                     )
                and 'MLBuy' not in regression_data['filter'] 
                ):
                add_in_csv(regression_data, regressionResult, ws, None, 'WEAK-Sell')
                flag = True
            elif(((regression_data[filter_count] >= 2 and regression_data[filter_pct] >= 79) or 'Buy-SUPER-risky' in regression_data['filter2'])
                and regression_data[filter_avg] > 1.9
                and regression_data['PCT_day_change'] < 1 
                and (abs(regression_data[filter_avg]) > 2 
                     or (abs(regression_data[filter_avg])*2 > abs(regression_data['PCT_day_change']))
                     or high_or_low == 'High'
                     or high_or_low == 'None'
                     )
                and 'MLSell' not in regression_data['filter']  
                and ('MLBuy' in regression_data['filter'] or 'Buy-SUPER-risky' in regression_data['filter2'])
                and is_any_sell_from_all_filter(regression_data) == False
                ):
                add_in_csv(regression_data, regressionResult, ws, None, 'WEAK-Buy')
                flag = True
            elif(((regression_data[filter_count] >= 2 and regression_data[filter_pct] <= -79) or 'Sell-SUPER-risky' in regression_data['filter2'])
                and regression_data[filter_avg] < -1.9 
                and regression_data['PCT_day_change'] > -1
                and (abs(regression_data[filter_avg]) > 2 
                     or (abs(regression_data[filter_avg])*2 > abs(regression_data['PCT_day_change']))
                     or high_or_low == 'Low'
                     or high_or_low == 'None'
                     )
                and 'MLBuy' not in regression_data['filter']
                and ('MLSell' in regression_data['filter'] or 'Sell-SUPER-risky' in regression_data['filter2']) 
                and is_any_buy_from_all_filter(regression_data) == False
                ):
                add_in_csv(regression_data, regressionResult, ws, None, 'WEAK-Sell')
                flag = True
                
        if('STRONG' not in regression_data['filter1']
            ):
            if(regression_data[filter_avg] >= 5
                and is_any_sell_from_all_filter(regression_data) == False
                and 'MLSell' not in regression_data['filter']
                ):
                add_in_csv(regression_data, regressionResult, ws, None, '**DUPER-Buy')
                flag = True
            elif(regression_data[filter_avg] < -5
                and is_any_buy_from_all_filter(regression_data) == False
                and 'MLBuy' not in regression_data['filter']
                ):
                add_in_csv(regression_data, regressionResult, ws, None, '**DUPER-Sell')
                flag = True
        
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
                ):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-Risky-01-Buy')
            elif(regression_data[filter_avg] < 0 and filter_avg_lt_minus_1_count(regression_data) >=2
                #and (abs(regression_data[filter_avg]) > 2 or regression_data['PCT_day_change'] > 0)
                and (abs(regression_data[filter_avg]) > 2 
                     or (abs(regression_data[filter_avg])*2 > abs(regression_data['PCT_day_change']))
                     or high_or_low == 'Low'
                     or high_or_low == 'None'
                     )
                ):
                add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-Risky-01-Sell')  
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
#                 add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-9-Buy')
#             elif(regression_data[filter_avg] < 0):
#                 add_in_csv(regression_data, regressionResult, ws, None, 'STRONG-9-Sell')    
        return flag
      
def is_filter_risky(regression_data, regressionResult, high_or_low, ws, filter_avg, filter_count, filter_pct, update=True): 
    BuyRisky = False
    SellRisky = False
    
    if(regression_data[filter_avg] < -0.75
        and regression_data['PCT_day_change'] > 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'UPTREND:OR:GLOBALUP-DONT-SELL')
    elif(regression_data[filter_avg] > 0.75
        and regression_data['PCT_day_change'] < 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'DOWNTREND:OR:GLOBALDOWN-DONT-BUY')
    
    if(regression_data[filter_avg] < -0.75
        and regression_data['PCT_day_change'] < -2.5
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'DON\'TSELL-NIFTYDOWN1PC')
    elif(regression_data[filter_avg] > 0.75
        and regression_data['PCT_day_change'] > 2.5
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'DON\'TBUY-NIFTYUP1PC')
    
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
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'RISKY-DOWNTREND-BUY') 
    elif(regression_data['PCT_day_change'] < 0
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
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'RISKY-UPTREND-SELL')
    
    if(float(regression_data[filter_avg]) < -1
        and regression_data['PCT_day_change'] > 0
        and regression_data['PCT_change'] > 0
        and (regression_data['PCT_day_change'] > 1 or regression_data['PCT_change'] > 1)
        and regression_data['monthLowChange'] < 5
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'RISKY-SELL-UPTRENDMARKET')
    elif(float(regression_data[filter_avg]) > 1
        and regression_data['PCT_day_change'] < 0
        and regression_data['PCT_change'] < 0
        and (regression_data['PCT_day_change'] < -1 or regression_data['PCT_change'] < -1)
        and regression_data['monthHighChange'] > -5
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'RISKY-BUY-DOWNTRENDMARKET')  
        
    if(((low_tail_pct(regression_data) > 1.5 or high_tail_pct(regression_data) > 2.5) and regression_data[filter_avg] < -0.5)
        or ((high_tail_pct(regression_data) > 1.5 and low_tail_pct(regression_data) > 2.5) and regression_data[filter_avg] > 0.5)
        ):
        if update:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'TAILRisk')
            
    if(((regression_data['filter'] == " " and abs(float(regression_data[filter_avg])) > 0.75)
            or ("MLBuy" in regression_data['filter'] and float(regression_data[filter_avg]) < -0.5)
            or ("MLSell" in regression_data['filter'] and float(regression_data[filter_avg]) > 0.5)
            )
        and regression_data['filter4'].startswith('@s@')
        and regression_data['filter4'].endswith('@e@,') 
        ):
        if update:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'FilterRisk')
    
    
    
    if((regression_data['PCT_day_change'] < -3 or regression_data['PCT_change'] < -3)
        and regression_data['monthHighChange'] < -5
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'RISKY-SELL-LASTDAYDOWN')
    elif((regression_data['PCT_day_change'] < -3 or regression_data['PCT_change'] < -3)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'RISKY-SELL-LASTDAYDOWN-UPTRENDMARKET')
    if((regression_data['PCT_day_change'] > 3 or regression_data['PCT_change'] > 3)
        and regression_data['monthLowChange'] > 5
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'RISKY-BUY-LASTDAYUP')
    elif((regression_data['PCT_day_change'] > 3 or regression_data['PCT_change'] > 3)
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'RISKY-BUY-LASTDAYUP-DOWNTRENDMARKET')
            
    
    if((
            #-2 < regression_data['week2LowChange'] < 2 
            #-2 < regression_data['monthLowChange'] < 2
            -2 < regression_data['month3LowChange'] < 2
            #or -2 < regression_data['month6LowChange'] < 2
            )
        and regression_data['year2LowChange'] > 0
        ):
        if update:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'RISKYBASELINESELL')
    if((
            #-2 < regression_data['week2HighChange'] < 2
            #-2 < regression_data['monthHighChange'] < 2
            -2 < regression_data['month3HighChange'] < 2
            #or -2 < regression_data['month6HighChange'] < 2
            )
        and regression_data['year2HighChange'] < 0
        ):
        if update:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'RISKYBASELINEBUY')
    if(-4 < regression_data['PCT_day_change'] < 0
        and -4 < regression_data['PCT_change'] < 0
        and regression_data['PCT_day_change_pre1'] < 0
        and regression_data['PCT_day_change_pre2'] < 0
        and regression_data['PCT_day_change_pre3'] < 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'RISKY-SELL-DOWNTREND-CONT(MARKET-DOWNTREND-NOTRISKY)')
    if(4 > regression_data['PCT_day_change'] > 0
        and 4 > regression_data['PCT_change'] > 0
        and regression_data['PCT_day_change_pre1'] > 0
        and regression_data['PCT_day_change_pre2'] > 0
        and regression_data['PCT_day_change_pre3'] > 0
        ):
        add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'RISKY-BUY-UPTREND-CONT(MARKET-UPTREND-NOTRISKY)')
    
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
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, None)
        else:
            if update:
                add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'DOJI')
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
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'DOJI-BuyMayFail')
        BuyRisky = True
    if(-1 < float(regression_data['PCT_day_change']) < 0
        and -3 < float(regression_data['PCT_change']) < 3 
        #and ("downTrend" in regression_data['series_trend'])
        and regression_data['forecast_day_PCT_change'] > regression_data['forecast_day_PCT2_change'] > regression_data['forecast_day_PCT3_change'] > regression_data['forecast_day_PCT4_change']
        and float(regression_data[filter_avg]) > dojivalue and (regression_data[filter_pct] > 70 or regression_data[filter_pct] ==0)
        ):
        if update:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'DOJI-BuyMayFail')
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
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'DOJI-SellMayFail')
        SellRisky = True
    if(0 < float(regression_data['PCT_day_change']) < 1
        and -3 < float(regression_data['PCT_change']) < 3 
        #and ("upTrend" in regression_data['series_trend'])
        and regression_data['forecast_day_PCT_change'] < regression_data['forecast_day_PCT2_change'] < regression_data['forecast_day_PCT3_change'] < regression_data['forecast_day_PCT4_change']
        and float(regression_data[filter_avg]) < -dojivalue and (regression_data[filter_pct] < -70 or regression_data[filter_pct] ==0)
        ):
        if update:
            add_in_csv(regression_data, regressionResult, ws, None, None, None, None, None, 'DOJI-SellMayFail')
        SellRisky = True
        
    return BuyRisky, SellRisky  
    
        
    
        
        
        
        
        

            