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
from util.util import morning_star_sell, buy_oi_candidate, morning_star_buy, sell_oi_candidate

connection = MongoClient('localhost', 27017)
db = connection.Nsedata

buyPatternsDict=scrip_patterns_to_dict('../../data-import/nselist/patterns-buy.csv')
sellPatternsDict=scrip_patterns_to_dict('../../data-import/nselist/patterns-sell.csv')

directory = '../../output/final'
logname = '../../output/final' + '/regression-result' + time.strftime("%d%m%y-%H%M%S")

newsDict = {}
wb = Workbook()
ws_buyAll = wb.create_sheet("BuyAll")
ws_buyAll.append(["BuyIndicators", "SellIndicators", "Symbol", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "PCT_Day_Change", "PCT_Change","Score", "MLP", "KNeighbors", "trend", "yHighChange","yLowChange", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "Filter", "Avg", "Count"])
ws_buyYearHigh = wb.create_sheet("buyYearHigh")
ws_buyYearHigh.append(["BuyIndicators", "SellIndicators", "Symbol", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "PCT_Day_Change", "PCT_Change","Score", "MLP", "KNeighbors", "trend", "yHighChange","yLowChange", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "Filter", "Avg", "Count"])
ws_buyYearLow = wb.create_sheet("buyYearLow")
ws_buyYearLow.append(["BuyIndicators", "SellIndicators", "Symbol", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "PCT_Day_Change", "PCT_Change","Score", "MLP", "KNeighbors", "trend", "yHighChange","yLowChange", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "Filter", "Avg", "Count"])
ws_buyYearLow1 = wb.create_sheet("buyYearLow1")
ws_buyYearLow1.append(["BuyIndicators", "SellIndicators", "Symbol", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "PCT_Day_Change", "PCT_Change","Score", "MLP", "KNeighbors", "trend", "yHighChange","yLowChange", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "Filter", "Avg", "Count"])
ws_buyFinal = wb.create_sheet("BuyFinal")
ws_buyFinal.append(["BuyIndicators", "SellIndicators", "Symbol", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "PCT_Day_Change", "PCT_Change","Score", "MLP", "KNeighbors", "trend", "yHighChange","yLowChange", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "Filter", "Avg", "Count"])
ws_buyFinal1 = wb.create_sheet("BuyFinal1")
ws_buyFinal1.append(["BuyIndicators", "SellIndicators", "Symbol", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "PCT_Day_Change", "PCT_Change","Score", "MLP", "KNeighbors", "trend", "yHighChange","yLowChange", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "Filter", "Avg", "Count"])
ws_buyUpTrend = wb.create_sheet("buyUpTrend")
ws_buyUpTrend.append(["BuyIndicators", "SellIndicators", "Symbol", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "PCT_Day_Change", "PCT_Change","Score", "MLP", "KNeighbors", "trend", "yHighChange","yLowChange", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "Filter", "Avg", "Count"])
ws_buyDownTrend = wb.create_sheet("buyDownTrend")
ws_buyDownTrend.append(["BuyIndicators", "SellIndicators", "Symbol", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "PCT_Day_Change", "PCT_Change","Score", "MLP", "KNeighbors", "trend", "yHighChange","yLowChange", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "Filter", "Avg", "Count"])
ws_buyHighIndicators = wb.create_sheet("BuyHighIndicators")
ws_buyHighIndicators.append(["BuyIndicators", "SellIndicators", "Symbol", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "PCT_Day_Change", "PCT_Change","Score", "MLP", "KNeighbors", "trend", "yHighChange","yLowChange", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "Filter", "Avg", "Count"])
ws_buyPattern2 = wb.create_sheet("buyPattern2")
ws_buyPattern2.append(["BuyIndicators", "SellIndicators", "Symbol", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "PCT_Day_Change", "PCT_Change","Score", "MLP", "KNeighbors", "trend", "yHighChange","yLowChange", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "Filter", "Avg", "Count"])
ws_buyOI = wb.create_sheet("buyOI")
ws_buyOI.append(["BuyIndicators", "SellIndicators", "Symbol", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "PCT_Day_Change", "PCT_Change","Score", "MLP", "KNeighbors", "trend", "yHighChange","yLowChange", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "Filter", "Avg", "Count"])
ws_buyPattern = wb.create_sheet("BuyPattern")
ws_buyPattern.append(["BuyIndicators", "SellIndicators", "Symbol", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "PCT_Day_Change", "PCT_Change","Score", "MLP", "KNeighbors", "trend", "yHighChange","yLowChange", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "Filter", "Avg", "Count"])
ws_buyPattern1 = wb.create_sheet("BuyPattern1")
ws_buyPattern1.append(["BuyIndicators", "SellIndicators", "Symbol", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "PCT_Day_Change", "PCT_Change","Score", "MLP", "KNeighbors", "trend", "yHighChange","yLowChange", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "Filter", "Avg", "Count"])

ws_sellAll = wb.create_sheet("SellAll")
ws_sellAll.append(["BuyIndicators", "SellIndicators", "Symbol", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "PCT_Day_Change", "PCT_Change","Score", "MLP", "KNeighbors", "trend", "yHighChange","yLowChange", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "Filter", "Avg", "Count"])
ws_sellYearLow = wb.create_sheet("sellYearLow")
ws_sellYearLow.append(["BuyIndicators", "SellIndicators", "Symbol", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "PCT_Day_Change", "PCT_Change","Score", "MLP", "KNeighbors", "trend", "yHighChange","yLowChange", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "Filter", "Avg", "Count"])
ws_sellYearHigh = wb.create_sheet("sellYearHigh")
ws_sellYearHigh.append(["BuyIndicators", "SellIndicators", "Symbol", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "PCT_Day_Change", "PCT_Change","Score", "MLP", "KNeighbors", "trend", "yHighChange","yLowChange", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "Filter", "Avg", "Count"])
ws_sellYearHigh1 = wb.create_sheet("sellYearHigh1")
ws_sellYearHigh1.append(["BuyIndicators", "SellIndicators", "Symbol", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "PCT_Day_Change", "PCT_Change","Score", "MLP", "KNeighbors", "trend", "yHighChange","yLowChange", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "Filter", "Avg", "Count"])
ws_sellFinal = wb.create_sheet("SellFinal")
ws_sellFinal.append(["BuyIndicators", "SellIndicators", "Symbol", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "PCT_Day_Change", "PCT_Change","Score", "MLP", "KNeighbors", "trend", "yHighChange","yLowChange", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "Filter", "Avg", "Count"])
ws_sellFinal1 = wb.create_sheet("SellFinal1")
ws_sellFinal1.append(["BuyIndicators", "SellIndicators", "Symbol", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "PCT_Day_Change", "PCT_Change","Score", "MLP", "KNeighbors", "trend", "yHighChange","yLowChange", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "Filter", "Avg", "Count"])
ws_sellDownTrend = wb.create_sheet("sellDownTrend")
ws_sellDownTrend.append(["BuyIndicators", "SellIndicators", "Symbol", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "PCT_Day_Change", "PCT_Change","Score", "MLP", "KNeighbors", "trend", "yHighChange","yLowChange", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "Filter", "Avg", "Count"])
ws_sellUpTrend = wb.create_sheet("sellUpTrend")
ws_sellUpTrend.append(["BuyIndicators", "SellIndicators", "Symbol", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "PCT_Day_Change", "PCT_Change","Score", "MLP", "KNeighbors", "trend", "yHighChange","yLowChange", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "Filter", "Avg", "Count"])
ws_sellHighIndicators = wb.create_sheet("SellHighIndicators")
ws_sellHighIndicators.append(["BuyIndicators", "SellIndicators", "Symbol", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "PCT_Day_Change", "PCT_Change","Score", "MLP", "KNeighbors", "trend", "yHighChange","yLowChange", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "Filter", "Avg", "Count"])
ws_sellPattern2 = wb.create_sheet("sellPattern2")
ws_sellPattern2.append(["BuyIndicators", "SellIndicators", "Symbol", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "PCT_Day_Change", "PCT_Change","Score", "MLP", "KNeighbors", "trend", "yHighChange","yLowChange", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "Filter", "Avg", "Count"])
ws_sellOI = wb.create_sheet("sellOI")
ws_sellOI.append(["BuyIndicators", "SellIndicators", "Symbol", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "PCT_Day_Change", "PCT_Change","Score", "MLP", "KNeighbors", "trend", "yHighChange","yLowChange", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "Filter", "Avg", "Count"])
ws_sellPattern = wb.create_sheet("SellPattern")
ws_sellPattern.append(["BuyIndicators", "SellIndicators", "Symbol", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "PCT_Day_Change", "PCT_Change","Score", "MLP", "KNeighbors", "trend", "yHighChange","yLowChange", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "Filter", "Avg", "Count"])
ws_sellPattern1 = wb.create_sheet("SellPattern1")
ws_sellPattern1.append(["BuyIndicators", "SellIndicators", "Symbol", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "PCT_Day_Change", "PCT_Change","Score", "MLP", "KNeighbors", "trend", "yHighChange","yLowChange", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "Filter", "Avg", "Count"])

def saveReports(run_type=None):
    ws_buyAll.append([""])
    ws_buyYearHigh.append([""])
    ws_buyYearLow.append([""])
    ws_buyYearLow1.append([""])
    ws_buyFinal.append([""])
    ws_buyFinal1.append([""])
    ws_buyUpTrend.append([""])
    ws_buyDownTrend.append([""])
    ws_buyHighIndicators.append([""])
    ws_buyPattern2.append([""])
    ws_buyPattern.append([""])
    ws_buyPattern1.append([""])
        
    ws_sellAll.append([""])
    ws_sellYearLow.append([""])
    ws_sellYearHigh.append([""])
    ws_sellYearHigh1.append([""])
    ws_sellFinal.append([""])
    ws_sellFinal1.append([""])
    ws_sellDownTrend.append([""])
    ws_sellUpTrend.append([""])
    ws_sellHighIndicators.append([""])
    ws_sellPattern2.append([""])
    ws_sellPattern.append([""])
    ws_sellPattern1.append([""])

    
    # Add a default style with striped rows and banded columns
    style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
               showLastColumn=False, showRowStripes=True, showColumnStripes=True)
    
    count = 0
    for row in ws_buyAll.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:AD" + str(count))
    tab.tableStyleInfo = style
    ws_buyAll.add_table(tab)
    
    count = 0
    for row in ws_buyYearHigh.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:AD" + str(count))
    tab.tableStyleInfo = style
    ws_buyYearHigh.add_table(tab)
     
    count = 0
    for row in ws_buyYearLow.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:AD" + str(count))
    tab.tableStyleInfo = style
    ws_buyYearLow.add_table(tab)
   
    count = 0
    for row in ws_buyYearLow1.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:AD" + str(count))
    tab.tableStyleInfo = style
    ws_buyYearLow1.add_table(tab)
     
    count = 0
    for row in ws_buyFinal.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:AD" + str(count))
    tab.tableStyleInfo = style
    ws_buyFinal.add_table(tab)
     
    count = 0
    for row in ws_buyFinal1.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:AD" + str(count))
    tab.tableStyleInfo = style
    ws_buyFinal1.add_table(tab)
     
    count = 0
    for row in ws_buyPattern.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:AD" + str(count))
    tab.tableStyleInfo = style
    ws_buyPattern.add_table(tab)
     
    count = 0
    for row in ws_buyPattern1.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:AD" + str(count))
    tab.tableStyleInfo = style
    ws_buyPattern1.add_table(tab)
     
    count = 0
    for row in ws_buyPattern2.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:AD" + str(count))
    tab.tableStyleInfo = style
    ws_buyPattern2.add_table(tab)
    
    count = 0
    for row in ws_buyOI.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:AD" + str(count))
    tab.tableStyleInfo = style
    ws_buyOI.add_table(tab)
     
    count = 0
    for row in ws_buyUpTrend.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:AD" + str(count))
    tab.tableStyleInfo = style
    ws_buyUpTrend.add_table(tab)
    
    count = 0
    for row in ws_buyDownTrend.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:AD" + str(count))
    tab.tableStyleInfo = style
    ws_buyDownTrend.add_table(tab)
     
    count = 0
    for row in ws_buyHighIndicators.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:AD" + str(count))
    tab.tableStyleInfo = style
    ws_buyHighIndicators.add_table(tab)
    
    
    count = 0
    for row in ws_sellAll.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:AD" + str(count))
    tab.tableStyleInfo = style
    ws_sellAll.add_table(tab)
    
    count = 0
    for row in ws_sellYearHigh.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:AD" + str(count))
    tab.tableStyleInfo = style
    ws_sellYearHigh.add_table(tab)
    
    count = 0
    for row in ws_sellYearHigh1.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:AD" + str(count))
    tab.tableStyleInfo = style
    ws_sellYearHigh1.add_table(tab)
    
    count = 0
    for row in ws_sellYearLow.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:AD" + str(count))
    tab.tableStyleInfo = style
    ws_sellYearLow.add_table(tab)
    
    count = 0
    for row in ws_sellFinal.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:AD" + str(count))
    tab.tableStyleInfo = style
    ws_sellFinal.add_table(tab)
    
    count = 0
    for row in ws_sellFinal1.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:AD" + str(count))
    tab.tableStyleInfo = style
    ws_sellFinal1.add_table(tab)
    
    count = 0
    for row in ws_sellPattern.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:AD" + str(count))
    tab.tableStyleInfo = style
    ws_sellPattern.add_table(tab)
    
    count = 0
    for row in ws_sellPattern1.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:AD" + str(count))
    tab.tableStyleInfo = style
    ws_sellPattern1.add_table(tab)
    
    count = 0
    for row in ws_sellPattern2.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:AD" + str(count))
    tab.tableStyleInfo = style
    ws_sellPattern2.add_table(tab)
    
    count = 0
    for row in ws_sellOI.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:AD" + str(count))
    tab.tableStyleInfo = style
    ws_sellOI.add_table(tab)
    
    count = 0
    for row in ws_sellDownTrend.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:AD" + str(count))
    tab.tableStyleInfo = style
    ws_sellDownTrend.add_table(tab)
    
    count = 0
    for row in ws_sellUpTrend.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:AD" + str(count))
    tab.tableStyleInfo = style
    ws_sellUpTrend.add_table(tab)
    
    count = 0
    for row in ws_sellHighIndicators.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:AD" + str(count))
    tab.tableStyleInfo = style
    ws_sellHighIndicators.add_table(tab)
    
    wb.save(logname + ".xlsx")

def result_data(scrip):
    regression_data = db.regressionhigh.find_one({'scrip':scrip.replace('&','').replace('-','_')})
    if(regression_data is not None):
        regressionResult = get_regressionResult(regression_data, scrip, db)
        buy_pattern_without_mlalgo(regression_data, regressionResult, ws_buyPattern2, ws_sellPattern2)
        morning_star_sell(regression_data, regressionResult, None)
        buy_oi_candidate(regression_data, regressionResult, None)
        all_withoutml(regression_data, regressionResult, ws_buyOI)
        buyIndiaAvg, result = buy_pattern_from_history(regression_data, regressionResult, ws_buyPattern2)
        if buy_all_rule(regression_data, regressionResult, buyIndiaAvg, None):
            buy_year_high(regression_data, regressionResult, ws_buyYearHigh)
            buy_year_low(regression_data, regressionResult, ws_buyYearLow, ws_buyYearLow1)
            buy_up_trend(regression_data, regressionResult, ws_buyUpTrend)
            buy_down_trend(regression_data, regressionResult, ws_buyDownTrend)
            buy_final(regression_data, regressionResult, ws_buyFinal, ws_buyFinal1)
            buy_high_indicators(regression_data, regressionResult, ws_buyHighIndicators)
            #buy_pattern(regression_data, regressionResult, ws_buyPattern, ws_buyPattern1)
            buy_oi(regression_data, regressionResult, None)
            buy_all_rule(regression_data, regressionResult, buyIndiaAvg, ws_buyAll)
                
    regression_data = db.regressionlow.find_one({'scrip':scrip.replace('&','').replace('-','_')})
    if(regression_data is not None):
        regressionResult = get_regressionResult(regression_data, scrip, db)
        sell_pattern_without_mlalgo(regression_data, regressionResult, ws_buyPattern2, ws_sellPattern2)
        morning_star_buy(regression_data, regressionResult, None)
        sell_oi_candidate(regression_data, regressionResult, None)
        all_withoutml(regression_data, regressionResult, ws_sellOI)
        sellIndiaAvg, result = sell_pattern_from_history(regression_data, regressionResult, ws_sellPattern2)
        if sell_all_rule(regression_data, regressionResult, sellIndiaAvg, None):
            sell_year_high(regression_data, regressionResult, ws_sellYearHigh, ws_sellYearHigh1)
            sell_year_low(regression_data, regressionResult, ws_sellYearLow)
            sell_up_trend(regression_data, regressionResult, ws_sellUpTrend)
            sell_down_trend(regression_data, regressionResult, ws_sellDownTrend)
            sell_final(regression_data, regressionResult, ws_sellFinal, ws_sellFinal1)
            sell_high_indicators(regression_data, regressionResult, ws_sellHighIndicators)
            #sell_pattern(regression_data, regressionResult, ws_sellPattern, ws_sellPattern1)
            sell_oi(regression_data, regressionResult, None)
            sell_all_rule(regression_data, regressionResult, sellIndiaAvg, ws_sellAll)                                
                                                  
def calculateParallel(threads=2, futures=None):
    pool = ThreadPool(threads)
    scrips = []
    for data in db.scrip.find({'futures':futures}):
        scrips.append(data['scrip'].replace('&','').replace('-','_'))
    scrips.sort()
    pool.map(result_data, scrips)       
                     
if __name__ == "__main__":
    if not os.path.exists(directory):
        os.makedirs(directory)
    calculateParallel(1, sys.argv[1])
    connection.close()
    saveReports(sys.argv[1])