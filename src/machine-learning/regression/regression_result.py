import os, logging, sys, json, csv
sys.path.insert(0, '../')

from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import Color, PatternFill, Font, Border
from pymongo import MongoClient
from multiprocessing.dummy import Pool as ThreadPool

import quandl, math, time
import pandas as pd
import numpy as np
from talib.abstract import *

import datetime
import time
import gc

from util.util import getScore, all_day_pct_change_negative, all_day_pct_change_positive, no_doji_or_spinning_buy_india, no_doji_or_spinning_sell_india, scrip_patterns_to_dict
from util.util import is_algo_buy, is_algo_sell
from util.util import get_regressionResult
from util.util import buy_pattern_from_history, buy_all_rule, buy_year_high, buy_year_low, buy_up_trend, buy_down_trend, buy_final, buy_high_indicators, buy_pattern
from util.util import sell_pattern_from_history, sell_all_rule, sell_year_high, sell_year_low, sell_up_trend, sell_down_trend, sell_final, sell_high_indicators, sell_pattern
from util.util import buy_pattern_without_mlalgo, sell_pattern_without_mlalgo, buy_oi, sell_oi, all_withoutml
from util.util import buy_oi_candidate, sell_oi_candidate
from util.util import buy_other_indicator, buy_all_common, buy_all_common_High_Low, sell_other_indicator, sell_all_common, sell_all_common_High_Low
from util.util import buy_all_rule_classifier, sell_all_rule_classifier
from util.util import is_algo_buy_classifier, is_algo_sell_classifier
from util.util import sell_oi_negative, sell_day_high, buy_oi_negative, buy_day_low
from util.util import buy_filter_accuracy, sell_filter_accuracy



connection = MongoClient('localhost', 27017)
db = connection.Nsedata

buyPatternsDict=scrip_patterns_to_dict('../../data-import/nselist/patterns-buy.csv')
sellPatternsDict=scrip_patterns_to_dict('../../data-import/nselist/patterns-sell.csv')

directory = '../../output/final'
logname = '../../output/final' + '/all-result' + time.strftime("%d%m%y-%H%M%S")

newsDict = {}
wb = Workbook()

ws_highBuyCla = wb.create_sheet("HighBuyCla")
ws_highBuyCla.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "trend", "Score", "HighTail", "LowTail", "PCT_Day_Change", "PCT_Change", "Symbol", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter1Acc", "Filter1Count"])
ws_lowSellCla = wb.create_sheet("LowSellCla")
ws_lowSellCla.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "trend", "Score", "HighTail", "LowTail", "PCT_Day_Change", "PCT_Change", "Symbol", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter1Acc", "Filter1Count"])

ws_highBuyAll = wb.create_sheet("HighBuyAll")
ws_highBuyAll.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "trend", "Score", "HighTail", "LowTail", "PCT_Day_Change", "PCT_Change", "Symbol", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter1Acc", "Filter1Count"])
ws_lowSellAll = wb.create_sheet("LowSellAll")
ws_lowSellAll.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "trend", "Score", "HighTail", "LowTail", "PCT_Day_Change", "PCT_Change", "Symbol", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter1Acc", "Filter1Count"])
ws_highBothBuyAll = wb.create_sheet("HighBothBuyAll")
ws_highBothBuyAll.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "trend", "Score", "HighTail", "LowTail", "PCT_Day_Change", "PCT_Change", "Symbol", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter1Acc", "Filter1Count"])
ws_lowBothSellAll = wb.create_sheet("LowBothSellAll")
ws_lowBothSellAll.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "trend", "Score", "HighTail", "LowTail", "PCT_Day_Change", "PCT_Change", "Symbol", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter1Acc", "Filter1Count"])

ws_highBothBuy = wb.create_sheet("HighBothBuy")
ws_highBothBuy.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "trend", "Score", "HighTail", "LowTail", "PCT_Day_Change", "PCT_Change", "Symbol", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter1Acc", "Filter1Count"])
ws_lowBothSell = wb.create_sheet("LowBothSell")
ws_lowBothSell.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "trend", "Score", "HighTail", "LowTail", "PCT_Day_Change", "PCT_Change", "Symbol", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter1Acc", "Filter1Count"])
ws_highBuyReg = wb.create_sheet("HighBuyReg")
ws_highBuyReg.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "trend", "Score", "HighTail", "LowTail", "PCT_Day_Change", "PCT_Change", "Symbol", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter1Acc", "Filter1Count"])
ws_lowSellReg = wb.create_sheet("LowSellReg")
ws_lowSellReg.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "trend", "Score", "HighTail", "LowTail", "PCT_Day_Change", "PCT_Change", "Symbol", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter1Acc", "Filter1Count"])


ws_high = wb.create_sheet("HighAll")
ws_high.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "trend", "Score", "HighTail", "LowTail", "PCT_Day_Change", "PCT_Change", "Symbol", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter1Acc", "Filter1Count"])
ws_low = wb.create_sheet("LowAll")
ws_low.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "trend", "Score", "HighTail", "LowTail", "PCT_Day_Change", "PCT_Change", "Symbol", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter1Acc", "Filter1Count"])

def saveReports(run_type=None):
    ws_highBuyCla.append([""])
    ws_lowSellCla.append([""])
    
    
    
    ws_highBothBuyAll.append([""])
    ws_lowBothSellAll.append([""])
    ws_highBuyAll.append([""])
    ws_lowSellAll.append([""])
    
    ws_highBothBuy.append([""])
    ws_lowBothSell.append([""])
    ws_highBuyReg.append([""])
    ws_lowSellReg.append([""])
    
    ws_high.append([""])
    ws_low.append([""])
    
    
    # Add a default style with striped rows and banded columns
    style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
               showLastColumn=False, showRowStripes=True, showColumnStripes=True)
    
    count = 0
    for row in ws_highBothBuy.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BK" + str(count))
    tab.tableStyleInfo = style
    ws_highBothBuy.add_table(tab)
    
    
    count = 0
    for row in ws_highBuyReg.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BK" + str(count))
    tab.tableStyleInfo = style
    ws_highBuyReg.add_table(tab)
    
    count = 0
    for row in ws_highBuyAll.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BK" + str(count))
    tab.tableStyleInfo = style
    ws_highBuyAll.add_table(tab)
    
    count = 0
    for row in ws_highBuyCla.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BK" + str(count))
    tab.tableStyleInfo = style
    ws_highBuyCla.add_table(tab)
    
    count = 0
    for row in ws_high.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BK" + str(count))
    tab.tableStyleInfo = style
    ws_high.add_table(tab)
    
    
    count = 0
    for row in ws_lowBothSell.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BK" + str(count))
    tab.tableStyleInfo = style
    ws_lowBothSell.add_table(tab)
    
    count = 0
    for row in ws_lowSellReg.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BK" + str(count))
    tab.tableStyleInfo = style
    ws_lowSellReg.add_table(tab)
    
    count = 0
    for row in ws_lowSellAll.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BK" + str(count))
    tab.tableStyleInfo = style
    ws_lowSellAll.add_table(tab)
      
    count = 0
    for row in ws_lowSellCla.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BK" + str(count))
    tab.tableStyleInfo = style
    ws_lowSellCla.add_table(tab)
        
    count = 0
    for row in ws_low.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BK" + str(count))
    tab.tableStyleInfo = style
    ws_low.add_table(tab)
    
    count = 0
    for row in ws_highBothBuy.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BK" + str(count))
    tab.tableStyleInfo = style
    ws_highBothBuy.add_table(tab)
    
    count = 0
    for row in ws_lowBothSell.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BK" + str(count))
    tab.tableStyleInfo = style
    ws_lowBothSell.add_table(tab)
    
    count = 0
    for row in ws_highBothBuyAll.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BK" + str(count))
    tab.tableStyleInfo = style
    ws_highBothBuyAll.add_table(tab)
    
    count = 0
    for row in ws_lowBothSellAll.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BK" + str(count))
    tab.tableStyleInfo = style
    ws_lowBothSellAll.add_table(tab)
    
    
    wb.save(logname + ".xlsx")
      
def result_data(scrip):
    regression_high = db.regressionhigh.find_one({'scrip':scrip})
    regression_low = db.regressionlow.find_one({'scrip':scrip})
    if(regression_high is None or regression_low is None):
        return
    
    buyIndiaAvgReg, result = buy_pattern_from_history(regression_high, None)
    sellIndiaAvgReg, result = sell_pattern_from_history(regression_low, None)
    
    regression_data = regression_high
    regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_low['mlpValue_reg'], 
                                            regression_low['kNeighboursValue_reg'],
                                            regression_low['mlpValue_cla'], 
                                            regression_low['kNeighboursValue_cla'],
                                            )
    buy_pattern_without_mlalgo(regression_data, regressionResult)
    if (buy_all_rule(regression_data, regressionResult, buyIndiaAvgReg, None)
        and buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvgReg, None)
        ):
        buy_other_indicator(regression_data, regressionResult, True, None)
        buy_other_indicator(regression_data, regressionResult, False, None)
        buy_filter_accuracy(regression_data, regressionResult, False, None)
        buy_all_common(regression_data, regressionResult, True, None)
    if (sell_all_rule(regression_data, regressionResult, buyIndiaAvgReg, None)
        and sell_all_rule_classifier(regression_data, regressionResult, buyIndiaAvgReg, None)
        ):
        sell_other_indicator(regression_data, regressionResult, True, None)
        sell_other_indicator(regression_data, regressionResult, False, None)
        sell_filter_accuracy(regression_data, regressionResult, False, None)
        sell_all_common(regression_data, regressionResult, True, None)
    if (buy_all_rule(regression_data, regressionResult, buyIndiaAvgReg, None)
        and buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvgReg, None)
        ):
        if (buy_all_rule(regression_data, regressionResult, buyIndiaAvgReg, ws_highBothBuy)
            or buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvgReg, ws_highBothBuy)):
            print('') 
    
    regression_data = regression_low
    regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_high['mlpValue_reg'], 
                                            regression_high['kNeighboursValue_reg'],
                                            regression_high['mlpValue_cla'], 
                                            regression_high['kNeighboursValue_cla']
                                            )
    sell_pattern_without_mlalgo(regression_data, regressionResult)
    if (sell_all_rule(regression_data, regressionResult, sellIndiaAvgReg, None)
        and sell_all_rule_classifier(regression_data, regressionResult, sellIndiaAvgReg, None)
        ):
        sell_other_indicator(regression_data, regressionResult, True, None)
        sell_other_indicator(regression_data, regressionResult, False, None)
        sell_filter_accuracy(regression_data, regressionResult, False, None)
        sell_all_common(regression_data, regressionResult, True, None)
    if (buy_all_rule(regression_data, regressionResult, buyIndiaAvgReg, None)
        and buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvgReg, None)
        ):
        buy_other_indicator(regression_data, regressionResult, True, None)
        buy_other_indicator(regression_data, regressionResult, False, None)
        buy_filter_accuracy(regression_data, regressionResult, False, None) 
        buy_all_common(regression_data, regressionResult, True, None)
    if (sell_all_rule(regression_data, regressionResult, sellIndiaAvgReg, None)
        and sell_all_rule_classifier(regression_data, regressionResult, sellIndiaAvgReg, None)
        ):
        if (sell_all_rule(regression_data, regressionResult, sellIndiaAvgReg, ws_lowBothSell)
            or sell_all_rule_classifier(regression_data, regressionResult, sellIndiaAvgReg, ws_lowBothSell)):
            print('')
                                                
def result_data_reg(scrip):
    regression_high = db.regressionhigh.find_one({'scrip':scrip})
    regression_low = db.regressionlow.find_one({'scrip':scrip})
    if(regression_high is None or regression_low is None):
        return
    
    regression_data = regression_high
    if(regression_data is not None):
        buyIndiaAvg, result = buy_pattern_from_history(regression_data, None)
        regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_low['mlpValue_reg'], 
                                            regression_low['kNeighboursValue_reg'],
                                            regression_low['mlpValue_cla'], 
                                            regression_low['kNeighboursValue_cla'],
                                            )
        buy_pattern_without_mlalgo(regression_data, regressionResult)
        buy_other_indicator(regression_data, regressionResult, True, None)
        buy_filter_accuracy(regression_data, regressionResult, False, None)
        if buy_all_rule(regression_data, regressionResult, buyIndiaAvg, None):
            buy_all_rule(regression_data, regressionResult, buyIndiaAvg, ws_highBuyReg)
        if (is_algo_buy(regression_high) and is_algo_buy(regression_low)):
            buy_all_common_High_Low(regression_data, regressionResult, True, None)
            all_withoutml(regression_data, regressionResult, ws_highBuyAll) 
        if (is_algo_buy(regression_high, True) and is_algo_buy(regression_low, True)):
            buy_all_common_High_Low(regression_data, regressionResult, True, None)
            all_withoutml(regression_data, regressionResult, ws_highBothBuyAll) 
        all_withoutml(regression_data, regressionResult, ws_high)
          
                
    regression_data = regression_low
    if(regression_data is not None):
        sellIndiaAvg, result = sell_pattern_from_history(regression_data, None)
        regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_high['mlpValue_reg'], 
                                            regression_high['kNeighboursValue_reg'],
                                            regression_high['mlpValue_cla'], 
                                            regression_high['kNeighboursValue_cla']
                                            )
        sell_pattern_without_mlalgo(regression_data, regressionResult)
        sell_other_indicator(regression_data, regressionResult, True, None)
        sell_filter_accuracy(regression_data, regressionResult, False, None)
        if sell_all_rule(regression_data, regressionResult, sellIndiaAvg, None):
            sell_all_rule(regression_data, regressionResult, sellIndiaAvg, ws_lowSellReg)                               
        if (is_algo_sell(regression_high) and is_algo_sell(regression_low)):
            sell_all_common_High_Low(regression_data, regressionResult, True, None)
            all_withoutml(regression_data, regressionResult, ws_lowSellAll)
        if (is_algo_sell(regression_high, True) and is_algo_sell(regression_low, True)):
            sell_all_common_High_Low(regression_data, regressionResult, True, None)
            all_withoutml(regression_data, regressionResult, ws_lowBothSellAll)
        all_withoutml(regression_data, regressionResult, ws_low)
        
def result_data_cla(scrip):
    regression_high = db.regressionhigh.find_one({'scrip':scrip})
    regression_low = db.regressionlow.find_one({'scrip':scrip})
    if(regression_high is None or regression_low is None):
        return
    
    regression_data = regression_high
    if(regression_data is not None):
        buyIndiaAvg, result = buy_pattern_from_history(regression_data, None)
        regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_low['mlpValue_reg'], 
                                            regression_low['kNeighboursValue_reg'],
                                            regression_low['mlpValue_cla'], 
                                            regression_low['kNeighboursValue_cla'],
                                            )
        buy_pattern_without_mlalgo(regression_data, regressionResult)
        if buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvg, None):
            buy_other_indicator(regression_data, regressionResult, True, None)
            buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvg, ws_highBuyCla)
                
    regression_data = regression_low
    if(regression_data is not None):
        sellIndiaAvg, result = sell_pattern_from_history(regression_data, None)
        regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_high['mlpValue_reg'], 
                                            regression_high['kNeighboursValue_reg'],
                                            regression_high['mlpValue_cla'], 
                                            regression_high['kNeighboursValue_cla']
                                            )
        sell_pattern_without_mlalgo(regression_data, regressionResult)
        if sell_all_rule_classifier(regression_data, regressionResult, sellIndiaAvg, None):
            sell_other_indicator(regression_data, regressionResult, True, None)
            sell_all_rule_classifier(regression_data, regressionResult, sellIndiaAvg, ws_lowSellCla)                              
                                             
def calculateParallel(threads=2, futures=None):
    pool = ThreadPool(threads)
    scrips = []
    for data in db.scrip.find({'futures':futures}):
        scrips.append(data['scrip'])
    scrips.sort()
    pool.map(result_data, scrips)
    pool.map(result_data_cla, scrips)
    pool.map(result_data_reg, scrips)
                      
if __name__ == "__main__":
    if not os.path.exists(directory):
        os.makedirs(directory)
    calculateParallel(1, sys.argv[1])
    connection.close()
    saveReports(sys.argv[1])