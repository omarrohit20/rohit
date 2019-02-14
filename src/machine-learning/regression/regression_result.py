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
from util.util import buy_all_filter, buy_all_common, sell_all_filter, sell_all_common
from util.util import buy_all_rule_classifier, sell_all_rule_classifier
from util.util import is_algo_buy_classifier, is_algo_sell_classifier
from util.util import sell_oi_negative, sell_day_high, buy_oi_negative, buy_day_low



connection = MongoClient('localhost', 27017)
db = connection.Nsedata

buyPatternsDict=scrip_patterns_to_dict('../../data-import/nselist/patterns-buy.csv')
sellPatternsDict=scrip_patterns_to_dict('../../data-import/nselist/patterns-sell.csv')

directory = '../../output/final'
logname = '../../output/final' + '/all-result' + time.strftime("%d%m%y-%H%M%S")

newsDict = {}
wb = Workbook()
ws_highBuyReg = wb.create_sheet("HighBuyReg")
ws_highBuyReg.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "trend", "Score", "HighTail", "LowTail", "PCT_Day_Change", "PCT_Change", "Symbol", "Filter", "Filter1", "Filter2", "Filter3"])
ws_highOIReg = wb.create_sheet("HighOIReg")
ws_highOIReg.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "trend", "Score", "HighTail", "LowTail", "PCT_Day_Change", "PCT_Change", "Symbol", "Filter", "Filter1", "Filter2", "Filter3"])

ws_lowSellReg = wb.create_sheet("LowSellReg")
ws_lowSellReg.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "trend", "Score", "HighTail", "LowTail", "PCT_Day_Change", "PCT_Change", "Symbol", "Filter", "Filter1", "Filter2", "Filter3"])
ws_lowOIReg = wb.create_sheet("LowOIReg")
ws_lowOIReg.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "trend", "Score", "HighTail", "LowTail", "PCT_Day_Change", "PCT_Change", "Symbol", "Filter", "Filter1", "Filter2", "Filter3"])

ws_highBuyCla = wb.create_sheet("HighBuyCla")
ws_highBuyCla.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "trend", "Score", "HighTail", "LowTail", "PCT_Day_Change", "PCT_Change", "Symbol", "Filter", "Filter1", "Filter2", "Filter3"])
ws_highOICla = wb.create_sheet("HighOICla")
ws_highOICla.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "trend", "Score", "HighTail", "LowTail", "PCT_Day_Change", "PCT_Change", "Symbol", "Filter", "Filter1", "Filter2", "Filter3"])

ws_lowSellCla = wb.create_sheet("LowSellCla")
ws_lowSellCla.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "trend", "Score", "HighTail", "LowTail", "PCT_Day_Change", "PCT_Change", "Symbol", "Filter", "Filter1", "Filter2", "Filter3"])
ws_lowOICla = wb.create_sheet("LowOICla")
ws_lowOICla.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "trend", "Score", "HighTail", "LowTail", "PCT_Day_Change", "PCT_Change", "Symbol", "Filter", "Filter1", "Filter2", "Filter3"])

ws_highBothBuy = wb.create_sheet("HighBothBuy")
ws_highBothBuy.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "trend", "Score", "HighTail", "LowTail", "PCT_Day_Change", "PCT_Change", "Symbol", "Filter", "Filter1", "Filter2", "Filter3"])
ws_highBothSell = wb.create_sheet("HighBothSell")
ws_highBothSell.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "trend", "Score", "HighTail", "LowTail", "PCT_Day_Change", "PCT_Change", "Symbol", "Filter", "Filter1", "Filter2", "Filter3"])
ws_lowBothBuy = wb.create_sheet("LowBothBuy")
ws_lowBothBuy.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "trend", "Score", "HighTail", "LowTail", "PCT_Day_Change", "PCT_Change", "Symbol", "Filter", "Filter1", "Filter2", "Filter3"])
ws_lowBothSell = wb.create_sheet("LowBothSell")
ws_lowBothSell.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "trend", "Score", "HighTail", "LowTail", "PCT_Day_Change", "PCT_Change", "Symbol", "Filter", "Filter1", "Filter2", "Filter3"])
ws_high = wb.create_sheet("HighAll")
ws_high.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "trend", "Score", "HighTail", "LowTail", "PCT_Day_Change", "PCT_Change", "Symbol", "Filter", "Filter1", "Filter2", "Filter3"])
ws_low = wb.create_sheet("LowAll")
ws_low.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "trend", "Score", "HighTail", "LowTail", "PCT_Day_Change", "PCT_Change", "Symbol", "Filter", "Filter1", "Filter2", "Filter3"])

def saveReports(run_type=None):
    ws_highBuyReg.append([""])
    ws_highOIReg.append([""])
    ws_lowSellReg.append([""])
    ws_lowOIReg.append([""])
    
    ws_highBuyCla.append([""])
    ws_highOICla.append([""]) 
    ws_lowSellCla.append([""])
    ws_lowOICla.append([""])
    
    ws_highBothBuy.append([""])
    ws_highBothSell.append([""])
    ws_lowBothBuy.append([""])
    ws_lowBothSell.append([""])
    ws_high.append([""])
    ws_low.append([""])
    
    
    # Add a default style with striped rows and banded columns
    style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
               showLastColumn=False, showRowStripes=True, showColumnStripes=True)
    
    count = 0
    for row in ws_highBothBuy.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BG" + str(count))
    tab.tableStyleInfo = style
    ws_highBothBuy.add_table(tab)
    
    
    count = 0
    for row in ws_highBuyReg.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BG" + str(count))
    tab.tableStyleInfo = style
    ws_highBuyReg.add_table(tab)
    
    count = 0
    for row in ws_highOIReg.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BG" + str(count))
    tab.tableStyleInfo = style
    ws_highOIReg.add_table(tab)
    
    count = 0
    for row in ws_highBuyCla.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BG" + str(count))
    tab.tableStyleInfo = style
    ws_highBuyCla.add_table(tab)
    
    count = 0
    for row in ws_highOICla.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BG" + str(count))
    tab.tableStyleInfo = style
    ws_highOICla.add_table(tab)
    
    count = 0
    for row in ws_high.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BG" + str(count))
    tab.tableStyleInfo = style
    ws_high.add_table(tab)
    
    
    count = 0
    for row in ws_lowBothSell.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BG" + str(count))
    tab.tableStyleInfo = style
    ws_lowBothSell.add_table(tab)
    
    count = 0
    for row in ws_lowSellReg.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BG" + str(count))
    tab.tableStyleInfo = style
    ws_lowSellReg.add_table(tab)
    
    count = 0
    for row in ws_lowOIReg.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BG" + str(count))
    tab.tableStyleInfo = style
    ws_lowOIReg.add_table(tab)
    
    count = 0
    for row in ws_lowSellCla.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BG" + str(count))
    tab.tableStyleInfo = style
    ws_lowSellCla.add_table(tab)
    
    count = 0
    for row in ws_lowOICla.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BG" + str(count))
    tab.tableStyleInfo = style
    ws_lowOICla.add_table(tab)
    
    count = 0
    for row in ws_low.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BG" + str(count))
    tab.tableStyleInfo = style
    ws_low.add_table(tab)
    
    count = 0
    for row in ws_highBothBuy.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BG" + str(count))
    tab.tableStyleInfo = style
    ws_highBothBuy.add_table(tab)
    
    count = 0
    for row in ws_highBothSell.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BG" + str(count))
    tab.tableStyleInfo = style
    ws_highBothSell.add_table(tab)

    count = 0
    for row in ws_lowBothBuy.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BG" + str(count))
    tab.tableStyleInfo = style
    ws_lowBothBuy.add_table(tab)
    
    count = 0
    for row in ws_lowBothSell.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:BG" + str(count))
    tab.tableStyleInfo = style
    ws_lowBothSell.add_table(tab)
    
    
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
    re_oi = buy_oi_candidate(regression_data, regressionResult, True, None)
    cl_oi = buy_oi_candidate(regression_data, regressionResult, False, None)
    if (buy_all_rule(regression_data, regressionResult, buyIndiaAvgReg, None)
        and buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvgReg, None)
        ):
        buy_all_filter(regression_data, regressionResult, True, None)
        buy_all_common(regression_data, regressionResult, True, None)
        buy_all_filter(regression_data, regressionResult, False, None)
        buy_all_common(regression_data, regressionResult, False, None)
    if (sell_all_rule(regression_data, regressionResult, buyIndiaAvgReg, None)
        and sell_all_rule_classifier(regression_data, regressionResult, buyIndiaAvgReg, None)
        ):
        buy_all_filter(regression_data, regressionResult, True, None)
        buy_all_common(regression_data, regressionResult, True, None)
        buy_all_filter(regression_data, regressionResult, False, None)
        buy_all_common(regression_data, regressionResult, False, None)
    
    if (buy_all_rule(regression_data, regressionResult, buyIndiaAvgReg, None)
        and buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvgReg, None)
        ):
        if (buy_all_rule(regression_data, regressionResult, buyIndiaAvgReg, ws_highBothBuy)
            or buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvgReg, ws_highBothBuy)):
            print('')
    if (sell_all_rule(regression_data, regressionResult, buyIndiaAvgReg, None)
        and sell_all_rule_classifier(regression_data, regressionResult, buyIndiaAvgReg, None)
        ):
        if (sell_all_rule(regression_data, regressionResult, sellIndiaAvgReg, ws_highBothSell)
            or sell_all_rule_classifier(regression_data, regressionResult, sellIndiaAvgReg, ws_highBothSell)):
            print('') 
    
    regression_data = regression_low
    regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_high['mlpValue_reg'], 
                                            regression_high['kNeighboursValue_reg'],
                                            regression_high['mlpValue_cla'], 
                                            regression_high['kNeighboursValue_cla']
                                            )
    re_oi = sell_oi_candidate(regression_data, regressionResult, True, None)
    cl_oi = sell_oi_candidate(regression_data, regressionResult, False, None)
    if (sell_all_rule(regression_data, regressionResult, sellIndiaAvgReg, None)
        and sell_all_rule_classifier(regression_data, regressionResult, sellIndiaAvgReg, None)
        ):
        sell_all_filter(regression_data, regressionResult, True, None)
        sell_all_common(regression_data, regressionResult, True, None)
        sell_all_filter(regression_data, regressionResult, False, None)
        sell_all_common(regression_data, regressionResult, False, None)
    if (buy_all_rule(regression_data, regressionResult, buyIndiaAvgReg, None)
        and buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvgReg, None)
        ):
        sell_all_filter(regression_data, regressionResult, True, None)
        sell_all_common(regression_data, regressionResult, True, None)
        sell_all_filter(regression_data, regressionResult, False, None)
        sell_all_common(regression_data, regressionResult, False, None) 
    
    if (sell_all_rule(regression_data, regressionResult, sellIndiaAvgReg, None)
        and sell_all_rule_classifier(regression_data, regressionResult, sellIndiaAvgReg, None)
        ):
        if (sell_all_rule(regression_data, regressionResult, sellIndiaAvgReg, ws_lowBothSell)
            or sell_all_rule_classifier(regression_data, regressionResult, sellIndiaAvgReg, ws_lowBothSell)):
            print('')   
    if (buy_all_rule(regression_data, regressionResult, buyIndiaAvgReg, None)
        and buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvgReg, None)
        ):
        if (buy_all_rule(regression_data, regressionResult, buyIndiaAvgReg, ws_lowBothBuy)
            or buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvgReg, ws_lowBothBuy)):
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
        buy_pattern_without_mlalgo(regression_data, regressionResult, None, None)
        oi = buy_oi_candidate(regression_data, regressionResult, True, None)
        if buy_all_rule(regression_data, regressionResult, buyIndiaAvg, None):
            buy_year_high(regression_data, regressionResult, True, None)
            buy_year_low(regression_data, regressionResult, True, None, None)
            buy_final(regression_data, regressionResult, True, None, None)
            buy_up_trend(regression_data, regressionResult, True, None)
            buy_down_trend(regression_data, regressionResult, True, None)
            buy_oi(regression_data, regressionResult, True, None)
            buy_high_indicators(regression_data, regressionResult, True, None)
            buy_pattern(regression_data, regressionResult, True, None, None)
            buy_all_rule(regression_data, regressionResult, buyIndiaAvg, ws_highBuyReg)
        all_withoutml(regression_data, regressionResult, ws_high)
        if oi:
            all_withoutml(regression_data, regressionResult, ws_highOIReg)
                
    regression_data = regression_low
    if(regression_data is not None):
        sellIndiaAvg, result = sell_pattern_from_history(regression_data, None)
        regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_high['mlpValue_reg'], 
                                            regression_high['kNeighboursValue_reg'],
                                            regression_high['mlpValue_cla'], 
                                            regression_high['kNeighboursValue_cla']
                                            )
        sell_pattern_without_mlalgo(regression_data, regressionResult, None, None)
        oi = sell_oi_candidate(regression_data, regressionResult, True, None)
        if sell_all_rule(regression_data, regressionResult, sellIndiaAvg, None):
            sell_year_high(regression_data, regressionResult, True, None, None)
            sell_year_low(regression_data, regressionResult, True, None)
            sell_final(regression_data, regressionResult, True, None, None)
            sell_up_trend(regression_data, regressionResult, True, None)
            sell_down_trend(regression_data, regressionResult, True, None)
            sell_oi(regression_data, regressionResult, True, None)
            sell_high_indicators(regression_data, regressionResult, True, None)
            sell_pattern(regression_data, regressionResult, True, None, None)
            sell_all_rule(regression_data, regressionResult, sellIndiaAvg, ws_lowSellReg)                                
        all_withoutml(regression_data, regressionResult, ws_low)
        if oi:
            all_withoutml(regression_data, regressionResult, ws_lowOIReg)
        
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
        buy_pattern_without_mlalgo(regression_data, regressionResult, None, None)
        oi = buy_oi_candidate(regression_data, regressionResult, False, None)
        if buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvg, None):
            buy_year_high(regression_data, regressionResult, False, None)
            buy_year_low(regression_data, regressionResult, False, None, None)
            buy_final(regression_data, regressionResult, False, None, None)
            buy_up_trend(regression_data, regressionResult, False, None)
            buy_down_trend(regression_data, regressionResult, False, None)
            buy_oi(regression_data, regressionResult, False, None)
            buy_high_indicators(regression_data, regressionResult, False, None)
            buy_pattern(regression_data, regressionResult, False, None, None)
            buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvg, ws_highBuyCla)
        if oi:
            all_withoutml(regression_data, regressionResult, ws_highOICla)
                
    regression_data = regression_low
    if(regression_data is not None):
        sellIndiaAvg, result = sell_pattern_from_history(regression_data, None)
        regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_high['mlpValue_reg'], 
                                            regression_high['kNeighboursValue_reg'],
                                            regression_high['mlpValue_cla'], 
                                            regression_high['kNeighboursValue_cla']
                                            )
        sell_pattern_without_mlalgo(regression_data, regressionResult, None, None)
        oi = sell_oi_candidate(regression_data, regressionResult, False, None)
        if sell_all_rule_classifier(regression_data, regressionResult, sellIndiaAvg, None):
            sell_year_high(regression_data, regressionResult, False, None, None)
            sell_year_low(regression_data, regressionResult, False, None)
            sell_final(regression_data, regressionResult, False, None, None)
            sell_up_trend(regression_data, regressionResult, False, None)
            sell_down_trend(regression_data, regressionResult, False, None)
            sell_oi(regression_data, regressionResult, False, None)
            sell_high_indicators(regression_data, regressionResult, False, None)
            sell_pattern(regression_data, regressionResult, False, None, None)
            sell_all_rule_classifier(regression_data, regressionResult, sellIndiaAvg, ws_lowSellCla)
        if oi:
            all_withoutml(regression_data, regressionResult, ws_lowOICla)                                 
                                             
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