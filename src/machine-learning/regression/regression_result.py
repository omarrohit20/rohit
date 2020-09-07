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

from util.util import pct_change_filter, getScore, all_day_pct_change_negative, all_day_pct_change_positive, no_doji_or_spinning_buy_india, no_doji_or_spinning_sell_india, scrip_patterns_to_dict
from util.util import is_algo_buy, is_algo_sell, is_filter_all_accuracy, is_any_reg_algo_gt1, is_any_reg_algo_lt_minus1, is_any_reg_algo_gt1_not_other, is_any_reg_algo_lt_minus1_not_other
from util.util import get_regressionResult
from util.util import buy_pattern_from_history, buy_all_rule, buy_year_high, buy_year_low, buy_up_trend, buy_down_trend, buy_final, buy_pattern
from util.util import sell_pattern_from_history, sell_all_rule, sell_year_high, sell_year_low, sell_up_trend, sell_down_trend, sell_final, sell_pattern
from util.util import buy_pattern_without_mlalgo, sell_pattern_without_mlalgo, buy_oi, sell_oi, all_withoutml
from util.util import buy_oi_candidate, sell_oi_candidate
from util.util import buy_other_indicator, buy_indicator_after_filter_accuracy, buy_all_common, buy_all_common_High_Low, sell_other_indicator, sell_indicator_after_filter_accuracy, sell_all_common, sell_all_common_High_Low
from util.util import buy_all_rule_classifier, sell_all_rule_classifier
from util.util import is_algo_buy_classifier, is_algo_sell_classifier
from util.util import sell_day_high, buy_day_low
from util.util import buy_filter_345_accuracy, sell_filter_345_accuracy
from util.util import buy_filter_accuracy, sell_filter_accuracy
from util.util import buy_filter_pct_change_accuracy, sell_filter_pct_change_accuracy
from util.util import buy_filter_all_accuracy, sell_filter_all_accuracy
from util.util_buy import buy_high_volatility
from util.util_sell import sell_high_volatility



connection = MongoClient('localhost', 27017)
db = connection.Nsedata

buyPatternsDict=scrip_patterns_to_dict('../../data-import/nselist/patterns-buy.csv')
sellPatternsDict=scrip_patterns_to_dict('../../data-import/nselist/patterns-sell.csv')

directory = '../../output/final'
logname = '../../output/final' + '/all-result' + time.strftime("%d%m%y-%H%M%S")

newsDict = {}
wb = Workbook()

ws_allFilterAcc = wb.create_sheet("AllFilterAcc")
ws_allFilterAcc.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])
ws_highBuyStrongFilterAcc = wb.create_sheet("HighBuyAllFilterAcc")
ws_highBuyStrongFilterAcc.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])
ws_lowSellStrongFilterAcc = wb.create_sheet("LowSellAllFilterAcc")
ws_lowSellStrongFilterAcc.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])

ws_highAnalysis = wb.create_sheet("HighAnalysis")
ws_highAnalysis.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])
ws_lowAnalysis = wb.create_sheet("LowAnalysis")
ws_lowAnalysis.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])

ws_highBuyStrongBoth = wb.create_sheet("HighBuyStrongBoth")
ws_highBuyStrongBoth.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])
ws_lowSellStrongBoth = wb.create_sheet("LowSellStrongBoth")
ws_lowSellStrongBoth.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])
ws_highBuyStrong = wb.create_sheet("HighBuyStrong")
ws_highBuyStrong.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])
ws_lowSellStrong = wb.create_sheet("LowSellStrong")
ws_lowSellStrong.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])

ws_highBuyBothHL = wb.create_sheet("HighBuyBothHL")
ws_highBuyBothHL.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])
ws_lowSellBothHL = wb.create_sheet("LowSellBothHL")
ws_lowSellBothHL.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])
ws_highBuyReg = wb.create_sheet("HighBuyReg")
ws_highBuyReg.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])
ws_lowSellReg = wb.create_sheet("LowSellReg")
ws_lowSellReg.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])
ws_highBuy = wb.create_sheet("HighBuy")
ws_highBuy.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])
ws_lowSell = wb.create_sheet("LowSell")
ws_lowSell.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])

ws_high = wb.create_sheet("HighAll")
ws_high.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])
ws_low = wb.create_sheet("LowAll")
ws_low.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])

def saveReports():
    ws_allFilterAcc.append([""])
    ws_highBuyStrongFilterAcc.append([""])
    ws_lowSellStrongFilterAcc.append([""])
    
    ws_highAnalysis.append([""])
    ws_lowAnalysis.append([""])
    
    ws_highBuyBothHL.append([""])
    ws_lowSellBothHL.append([""])
    ws_highBuyStrong.append([""])
    ws_lowSellStrong.append([""])
    
    ws_highBuyStrongBoth.append([""])
    ws_lowSellStrongBoth.append([""])
    ws_highBuyReg.append([""])
    ws_lowSellReg.append([""])
    
    ws_high.append([""])
    ws_low.append([""])
    
    
    # Add a default style with striped rows and banded columns
    style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
               showLastColumn=False, showRowStripes=True, showColumnStripes=True)
    
    count = 0
    for row in ws_allFilterAcc.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:CP" + str(count))
    tab.tableStyleInfo = style
    ws_allFilterAcc.add_table(tab)
    
    count = 0
    for row in ws_highBuyStrongBoth.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:CP" + str(count))
    tab.tableStyleInfo = style
    ws_highBuyStrongBoth.add_table(tab)
    
    
    count = 0
    for row in ws_highBuyReg.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:CP" + str(count))
    tab.tableStyleInfo = style
    ws_highBuyReg.add_table(tab)
    
    count = 0
    for row in ws_highBuyStrong.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:CP" + str(count))
    tab.tableStyleInfo = style
    ws_highBuyStrong.add_table(tab)
    
    count = 0
    for row in ws_highBuyStrongFilterAcc.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:CP" + str(count))
    tab.tableStyleInfo = style
    ws_highBuyStrongFilterAcc.add_table(tab)
    
    count = 0
    for row in ws_highAnalysis.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:CP" + str(count))
    tab.tableStyleInfo = style
    ws_highAnalysis.add_table(tab)
    
    count = 0
    for row in ws_high.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:CP" + str(count))
    tab.tableStyleInfo = style
    ws_high.add_table(tab)
    
    
    count = 0
    for row in ws_lowSellStrongBoth.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:CP" + str(count))
    tab.tableStyleInfo = style
    ws_lowSellStrongBoth.add_table(tab)
    
    count = 0
    for row in ws_lowSellReg.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:CP" + str(count))
    tab.tableStyleInfo = style
    ws_lowSellReg.add_table(tab)
    
    count = 0
    for row in ws_lowSellStrong.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:CP" + str(count))
    tab.tableStyleInfo = style
    ws_lowSellStrong.add_table(tab)
      
    count = 0
    for row in ws_lowSellStrongFilterAcc.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:CP" + str(count))
    tab.tableStyleInfo = style
    ws_lowSellStrongFilterAcc.add_table(tab)
    
    count = 0
    for row in ws_lowAnalysis.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:CP" + str(count))
    tab.tableStyleInfo = style
    ws_lowAnalysis.add_table(tab)
        
    count = 0
    for row in ws_low.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:CP" + str(count))
    tab.tableStyleInfo = style
    ws_low.add_table(tab)
    
    count = 0
    for row in ws_highBuyStrongBoth.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:CP" + str(count))
    tab.tableStyleInfo = style
    ws_highBuyStrongBoth.add_table(tab)
    
    count = 0
    for row in ws_lowSellStrongBoth.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:CP" + str(count))
    tab.tableStyleInfo = style
    ws_lowSellStrongBoth.add_table(tab)
    
    count = 0
    for row in ws_highBuyBothHL.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:CP" + str(count))
    tab.tableStyleInfo = style
    ws_highBuyBothHL.add_table(tab)
    
    count = 0
    for row in ws_lowSellBothHL.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:CP" + str(count))
    tab.tableStyleInfo = style
    ws_lowSellBothHL.add_table(tab)
    
    count = 0
    for row in ws_highBuy.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:CP" + str(count))
    tab.tableStyleInfo = style
    ws_highBuy.add_table(tab)
    
    count = 0
    for row in ws_lowSell.iter_rows(row_offset=1):
        count += 1
    tab = Table(displayName="Table1", ref="A1:CP" + str(count))
    tab.tableStyleInfo = style
    ws_lowSell.add_table(tab)
    
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
        buy_filter_all_accuracy(regression_data, regressionResult)
        buy_indicator_after_filter_accuracy(regression_data, regressionResult, True, None)
        buy_all_common(regression_data, regressionResult, True, None)
    if (sell_all_rule(regression_data, regressionResult, buyIndiaAvgReg, None)
        and sell_all_rule_classifier(regression_data, regressionResult, buyIndiaAvgReg, None)
        ):
        sell_other_indicator(regression_data, regressionResult, True, None)
        sell_other_indicator(regression_data, regressionResult, False, None)
        sell_filter_all_accuracy(regression_data, regressionResult)
        sell_indicator_after_filter_accuracy(regression_data, regressionResult, True, None)
        sell_all_common(regression_data, regressionResult, True, None)
    if (buy_all_rule(regression_data, regressionResult, buyIndiaAvgReg, None)
        and buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvgReg, None)
        ):
        all_withoutml(regression_data, regressionResult, ws_highBuyStrongBoth)
    
    regression_data = regression_low
    regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_high['mlpValue_reg'], 
                                            regression_high['kNeighboursValue_reg'],
                                            regression_high['mlpValue_cla'], 
                                            regression_high['kNeighboursValue_cla'],
                                            False
                                            )
    sell_pattern_without_mlalgo(regression_data, regressionResult)
    if (sell_all_rule(regression_data, regressionResult, sellIndiaAvgReg, None)
        and sell_all_rule_classifier(regression_data, regressionResult, sellIndiaAvgReg, None)
        ):
        sell_other_indicator(regression_data, regressionResult, True, None)
        sell_other_indicator(regression_data, regressionResult, False, None)
        sell_filter_all_accuracy(regression_data, regressionResult)
        sell_indicator_after_filter_accuracy(regression_data, regressionResult, True, None)
        sell_all_common(regression_data, regressionResult, True, None)
    if (buy_all_rule(regression_data, regressionResult, buyIndiaAvgReg, None)
        and buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvgReg, None)
        ):
        buy_other_indicator(regression_data, regressionResult, True, None)
        buy_other_indicator(regression_data, regressionResult, False, None)
        buy_filter_all_accuracy(regression_data, regressionResult)
        buy_indicator_after_filter_accuracy(regression_data, regressionResult, True, None)
        buy_all_common(regression_data, regressionResult, True, None)
    if (sell_all_rule(regression_data, regressionResult, sellIndiaAvgReg, None)
        and sell_all_rule_classifier(regression_data, regressionResult, sellIndiaAvgReg, None)
        ):
        all_withoutml(regression_data, regressionResult, ws_lowSellStrongBoth)
                                                
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
        buy_filter_all_accuracy(regression_data, regressionResult)
        buy_indicator_after_filter_accuracy(regression_data, regressionResult, True, None) 
        if(buy_high_volatility(regression_data, regressionResult)):
            all_withoutml(regression_data, regressionResult, ws_highAnalysis)
        if(is_filter_all_accuracy(regression_data, regression_high, regression_low, regressionResult, 'High', None)):
            all_withoutml(regression_data, regressionResult, ws_highBuyStrongFilterAcc)
        if (is_algo_buy(regression_data)):
            buy_all_rule(regression_data, regressionResult, True, None)
            all_withoutml(regression_data, regressionResult, ws_highBuyReg)
        if (is_algo_buy(regression_high) and is_any_reg_algo_gt1_not_other(regression_data)):
            buy_all_common_High_Low(regression_data, regressionResult, True, None)
            all_withoutml(regression_data, regressionResult, ws_highBuyStrong) 
        if (is_algo_buy(regression_high, True) and is_algo_buy(regression_low, True) and is_any_reg_algo_gt1(regression_data)):
            buy_all_common_High_Low(regression_data, regressionResult, True, None)
            all_withoutml(regression_data, regressionResult, ws_highBuyBothHL)
        if (is_algo_buy(regression_high, True) and is_algo_buy(regression_low, True) 
            and is_any_reg_algo_gt1(regression_data)
            and is_any_reg_algo_gt1_not_other(regression_data)
            ):
            buy_all_common_High_Low(regression_data, regressionResult, True, None)
            all_withoutml(regression_data, regressionResult, ws_highBuyStrongBoth)
         
        all_withoutml(regression_data, regressionResult, ws_high)
          
                
    regression_data = regression_low
    if(regression_data is not None):
        sellIndiaAvg, result = sell_pattern_from_history(regression_data, None)
        regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_high['mlpValue_reg'], 
                                            regression_high['kNeighboursValue_reg'],
                                            regression_high['mlpValue_cla'], 
                                            regression_high['kNeighboursValue_cla'],
                                            False
                                            )
        sell_pattern_without_mlalgo(regression_data, regressionResult)
        sell_other_indicator(regression_data, regressionResult, True, None)
        sell_filter_all_accuracy(regression_data, regressionResult)
        sell_indicator_after_filter_accuracy(regression_data, regressionResult, True, None)
        if(sell_high_volatility(regression_data, regressionResult)):
            all_withoutml(regression_data, regressionResult, ws_lowAnalysis)
        if(is_filter_all_accuracy(regression_data, regression_high, regression_low, regressionResult, 'Low', None)):
            all_withoutml(regression_data, regressionResult, ws_lowSellStrongFilterAcc)
        if (is_algo_sell(regression_data)):
            sell_all_rule(regression_data, regressionResult, True, None)
            all_withoutml(regression_data, regressionResult, ws_lowSellReg)                               
        if (is_algo_sell(regression_high) and is_any_reg_algo_lt_minus1_not_other(regression_data)):
            sell_all_common_High_Low(regression_data, regressionResult, True, None)
            all_withoutml(regression_data, regressionResult, ws_lowSellStrong)
        if (is_algo_sell(regression_high, True) and is_algo_sell(regression_low, True) and is_any_reg_algo_lt_minus1(regression_data)):
            sell_all_common_High_Low(regression_data, regressionResult, True, None)
            all_withoutml(regression_data, regressionResult, ws_lowSellBothHL)
        if (is_algo_sell(regression_high, True) and is_algo_sell(regression_low, True) 
            and is_any_reg_algo_lt_minus1(regression_data)
            and is_any_reg_algo_lt_minus1_not_other(regression_data)
            ):
            sell_all_common_High_Low(regression_data, regressionResult, True, None)
            all_withoutml(regression_data, regressionResult, ws_lowSellStrongBoth)
        
        all_withoutml(regression_data, regressionResult, ws_low)
        
        regression_data = regression_high
        if (is_algo_sell(regression_high) != True and is_algo_sell(regression_low) != True):
            buy_indicator_after_filter_accuracy(regression_data, regressionResult, True, None)
            all_withoutml(regression_data, regressionResult, ws_highBuy)
        regression_data = regression_low
        if (is_algo_buy(regression_high) != True and is_algo_buy(regression_low) != True):
            sell_indicator_after_filter_accuracy(regression_data, regressionResult, True, None)
            all_withoutml(regression_data, regressionResult, ws_lowSell)
            
        if(is_filter_all_accuracy(regression_high, regression_high, regression_low, regressionResult, "None", None)
            and is_filter_all_accuracy(regression_low, regression_high, regression_low, regressionResult, "None", None)
            ):
            all_withoutml(regression_high, regressionResult, ws_allFilterAcc) 
            all_withoutml(regression_low, regressionResult, ws_allFilterAcc)
        
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
            buy_filter_all_accuracy(regression_data, regressionResult)
            buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvg, ws_highBuyStrongFilterAcc)
                
    regression_data = regression_low
    if(regression_data is not None):
        sellIndiaAvg, result = sell_pattern_from_history(regression_data, None)
        regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_high['mlpValue_reg'], 
                                            regression_high['kNeighboursValue_reg'],
                                            regression_high['mlpValue_cla'], 
                                            regression_high['kNeighboursValue_cla'],
                                            False
                                            )
        sell_pattern_without_mlalgo(regression_data, regressionResult)
        if sell_all_rule_classifier(regression_data, regressionResult, sellIndiaAvg, None):
            sell_other_indicator(regression_data, regressionResult, True, None)
            sell_filter_all_accuracy(regression_data, regressionResult)
            sell_all_rule_classifier(regression_data, regressionResult, sellIndiaAvg, ws_lowSellStrongFilterAcc)                              
                                             
def calculateParallel(threads=2, futures=None):
    pool = ThreadPool(threads)
    scrips = []
    
    processing_date = (datetime.date.today() - datetime.timedelta(days=0)).strftime('%Y-%m-%d')
    #processing_date = '2020-09-04'
    for data in db.scrip.find({'futures':'Yes'}):
        #print('Scrip ', data)
        regdata = db.regressionlow.find_one({'scrip':data['scrip']})
        if(regdata is None):
            print('Missing or very less Data for ', data['scrip'])
        if(regdata is not None and regdata['date'] != processing_date):
            print('End Date ', regdata['date'], 'not recent for', data['scrip'])
        else: 
            scrips.append(data['scrip'])
#     for data in db.scrip.find({'futures':'No'}):
#         #print('Scrip ', data)
#         regdata = db.regressionlow.find_one({'scrip':data['scrip']})
#         if(regdata is None):
#             print('Missing or very less Data for ', data['scrip'])
#         if(regdata is not None and regdata['date'] != processing_date):
#             print('End Date ', regdata['date'], 'not recent for', data['scrip'])
#         else: 
#             scrips.append(data['scrip'])
    scrips.sort()
    #pool.map(result_data, scrips)
    #pool.map(result_data_cla, scrips)
    pool.map(result_data_reg, scrips)

                      
if __name__ == "__main__":
    if not os.path.exists(directory):
        os.makedirs(directory)
    calculateParallel(1)
    connection.close()
    saveReports()