import os, logging, sys, json, csv
sys.path.insert(0, '../')

from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import Color, PatternFill, Font, Border
from pymongo import MongoClient
from multiprocessing.dummy import Pool as ThreadPool
from bson import json_util

import quandl, math, time
import pandas as pd
import numpy as np
from talib.abstract import *

import datetime
import time
import gc
import copy
import json

from util.util import pct_change_filter, getScore, all_day_pct_change_negative, all_day_pct_change_positive, no_doji_or_spinning_buy_india, no_doji_or_spinning_sell_india, scrip_patterns_to_dict
from util.util import is_algo_buy, is_algo_sell, is_filter_all_accuracy, is_filter_hist_accuracy, is_any_reg_algo_gt1, is_any_reg_algo_lt_minus1, is_any_reg_algo_gt1_not_other, is_any_reg_algo_lt_minus1_not_other
from util.util import get_regressionResult
from util.util import buy_pattern_from_history, buy_all_rule, buy_year_high, buy_year_low, buy_up_trend, buy_down_trend, buy_final, buy_pattern
from util.util import sell_pattern_from_history, sell_all_rule, sell_year_high, sell_year_low, sell_up_trend, sell_down_trend, sell_final, sell_pattern
from util.util import buy_pattern_without_mlalgo, sell_pattern_without_mlalgo, buy_oi, sell_oi, all_withoutml
from util.util import buy_oi_candidate, sell_oi_candidate
from util.util import buy_other_indicator, buy_indicator_after_filter_accuracy, buy_all_common, buy_all_common_High_Low, sell_other_indicator, sell_indicator_after_filter_accuracy, sell_all_common, sell_all_common_High_Low
from util.util import buy_all_rule_classifier, sell_all_rule_classifier
from util.util import is_algo_buy_classifier, is_algo_sell_classifier
from util.util import sell_day_high, buy_day_low
from util.util import filter_avg_gt_2_count_any, filter_avg_lt_minus_2_count_any
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
ws_allFilterAcc.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])
ws_highBuyStrongFilterAcc = wb.create_sheet("HighBuyAllFilterAcc")
ws_highBuyStrongFilterAcc.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])
ws_lowSellStrongFilterAcc = wb.create_sheet("LowSellAllFilterAcc")
ws_lowSellStrongFilterAcc.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])
ws_highBuy = wb.create_sheet("HighBuy")
ws_highBuy.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])
ws_lowSell = wb.create_sheet("LowSell")
ws_lowSell.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])


ws_highAnalysis = wb.create_sheet("HighAnalysis")
ws_highAnalysis.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])
ws_lowAnalysis = wb.create_sheet("LowAnalysis")
ws_lowAnalysis.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])

ws_highBuyStrongBoth = wb.create_sheet("HighBuyStrongBoth")
ws_highBuyStrongBoth.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])
ws_lowSellStrongBoth = wb.create_sheet("LowSellStrongBoth")
ws_lowSellStrongBoth.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])
ws_highBuyStrong = wb.create_sheet("HighBuyStrong")
ws_highBuyStrong.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])
ws_lowSellStrong = wb.create_sheet("LowSellStrong")
ws_lowSellStrong.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])

ws_lowBuyStrong = wb.create_sheet("LowBuyStrong")
ws_lowBuyStrong.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])
ws_highSellStrong = wb.create_sheet("HighSellStrong")
ws_highSellStrong.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])
ws_highBuyReg = wb.create_sheet("HighBuyReg")
ws_highBuyReg.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])
ws_lowSellReg = wb.create_sheet("LowSellReg")
ws_lowSellReg.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])

ws_high = wb.create_sheet("HighAll")
ws_high.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])
ws_low = wb.create_sheet("LowAll")
ws_low.append(["BuyIndicators", "Buy_Avg","Buy_Count", "SellIndicators", "Sell_Avg", "Sell_Count", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct"])

def saveReports():
    ws_allFilterAcc.append([""])
    ws_highBuyStrongFilterAcc.append([""])
    ws_lowSellStrongFilterAcc.append([""])
    
    ws_highAnalysis.append([""])
    ws_lowAnalysis.append([""])
    
    ws_lowBuyStrong.append([""])
    ws_highSellStrong.append([""])
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
    for row in ws_allFilterAcc.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="allFilterAcc", ref="A1:CR" + str(count))
    tab.tableStyleInfo = style
    ws_allFilterAcc.add_table(tab)
    
    count = 0
    for row in ws_highBuyReg.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="highBuyReg", ref="A1:CR" + str(count))
    tab.tableStyleInfo = style
    ws_highBuyReg.add_table(tab)
    
    count = 0
    for row in ws_highBuyStrong.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="highBuyStrong", ref="A1:CR" + str(count))
    tab.tableStyleInfo = style
    ws_highBuyStrong.add_table(tab)
    
    count = 0
    for row in ws_highBuyStrongFilterAcc.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="highBuyStrongFilterAcc", ref="A1:CR" + str(count))
    tab.tableStyleInfo = style
    ws_highBuyStrongFilterAcc.add_table(tab)
    
    count = 0
    for row in ws_highAnalysis.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="highAnalysis", ref="A1:CR" + str(count))
    tab.tableStyleInfo = style
    ws_highAnalysis.add_table(tab)
    
    count = 0
    for row in ws_high.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="high", ref="A1:CR" + str(count))
    tab.tableStyleInfo = style
    ws_high.add_table(tab)
    
    
    count = 0
    for row in ws_lowSellReg.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="lowSellReg", ref="A1:CR" + str(count))
    tab.tableStyleInfo = style
    ws_lowSellReg.add_table(tab)
    
    count = 0
    for row in ws_lowSellStrong.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="lowSellStrong", ref="A1:CR" + str(count))
    tab.tableStyleInfo = style
    ws_lowSellStrong.add_table(tab)
      
    count = 0
    for row in ws_lowSellStrongFilterAcc.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="lowSellStrongFilterAcc", ref="A1:CR" + str(count))
    tab.tableStyleInfo = style
    ws_lowSellStrongFilterAcc.add_table(tab)
    
    count = 0
    for row in ws_lowAnalysis.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="lowAnalysis", ref="A1:CR" + str(count))
    tab.tableStyleInfo = style
    ws_lowAnalysis.add_table(tab)
        
    count = 0
    for row in ws_low.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="low", ref="A1:CR" + str(count))
    tab.tableStyleInfo = style
    ws_low.add_table(tab)
    
    count = 0
    for row in ws_highBuyStrongBoth.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="highBuyStrongBoth", ref="A1:CR" + str(count))
    tab.tableStyleInfo = style
    ws_highBuyStrongBoth.add_table(tab)
    
    count = 0
    for row in ws_lowSellStrongBoth.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="lowSellStrongBoth", ref="A1:CR" + str(count))
    tab.tableStyleInfo = style
    ws_lowSellStrongBoth.add_table(tab)
    
    count = 0
    for row in ws_lowBuyStrong.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="lowBuyStrong", ref="A1:CR" + str(count))
    tab.tableStyleInfo = style
    ws_lowBuyStrong.add_table(tab)
    
    count = 0
    for row in ws_highSellStrong.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="highSellStrong", ref="A1:CR" + str(count))
    tab.tableStyleInfo = style
    ws_highSellStrong.add_table(tab)
    
    count = 0
    for row in ws_highBuy.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="highBuy", ref="A1:CR" + str(count))
    tab.tableStyleInfo = style
    ws_highBuy.add_table(tab)
    
    count = 0
    for row in ws_lowSell.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="lowSell", ref="A1:CR" + str(count))
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
        regressionResultHigh = get_regressionResult(regression_data, scrip, db, 
                                            regression_low['mlpValue_reg'], 
                                            regression_low['kNeighboursValue_reg'],
                                            regression_low['mlpValue_cla'], 
                                            regression_low['kNeighboursValue_cla'],
                                            )
        buy_pattern_without_mlalgo(regression_data, regressionResultHigh)
        buy_other_indicator(regression_data, regressionResultHigh, True, None)
        buy_filter_all_accuracy(regression_data, regressionResultHigh)
        buy_indicator_after_filter_accuracy(regression_data, regressionResultHigh, True, None) 
        
        if(is_filter_all_accuracy(regression_data, regression_high, regression_low, regressionResultHigh, 'High', None)):
            all_withoutml(regression_data, regressionResultHigh, None)
        buy_all_rule(regression_data, regressionResultHigh, True, None)
        #if (is_algo_buy(regression_data)):
            #all_withoutml(regression_data, regressionResultHigh, ws_highBuyReg)
        if (is_algo_buy(regression_high) and is_any_reg_algo_gt1_not_other(regression_data)):
            buy_all_common_High_Low(regression_data, regressionResultHigh, True, None)
            #all_withoutml(regression_data, regressionResultHigh, ws_highBuyStrong) 
        if (is_algo_buy(regression_high, True) and is_algo_buy(regression_low, True) and is_any_reg_algo_gt1(regression_data)):
            buy_all_common_High_Low(regression_data, regressionResultHigh, True, None)
            #all_withoutml(regression_data, regressionResultHigh, ws_lowBuyStrong)
        if (is_algo_buy(regression_high, True) and is_algo_buy(regression_low, True) 
            and is_any_reg_algo_gt1(regression_data)
            and is_any_reg_algo_gt1_not_other(regression_data)
            ):
            buy_all_common_High_Low(regression_data, regressionResultHigh, True, None)
            #all_withoutml(regression_data, regressionResultHigh, ws_highBuyStrongBoth)
         
        all_withoutml(regression_data, regressionResultHigh, ws_high)
        if("%%:" in regression_data['filter']
            or 'ConsolidationBreakout' in regression_data['filter']
            ):
            if((db['highBuy'].find_one({'scrip':scrip}) is None)):
                record = {}
                record['scrip'] = scrip
                record['ml'] = ''
                record['filter'] = regression_data['filter']
                record['filter2'] = ''
                record['filter3'] = ''
                json_data = json.loads(json.dumps(record, default=json_util.default))
                db['highBuy'].insert_one(json_data)
            else:
                db['highBuy'].update_one({'scrip':scrip}, { "$set": {'filter':regression_data['filter']}})
          
                
    regression_data = regression_low
    if(regression_data is not None):
        sellIndiaAvg, result = sell_pattern_from_history(regression_data, None)
        regressionResultLow = get_regressionResult(regression_data, scrip, db, 
                                            regression_high['mlpValue_reg'], 
                                            regression_high['kNeighboursValue_reg'],
                                            regression_high['mlpValue_cla'], 
                                            regression_high['kNeighboursValue_cla'],
                                            False
                                            )
        sell_pattern_without_mlalgo(regression_data, regressionResultLow)
        sell_other_indicator(regression_data, regressionResultLow, True, None)
        sell_filter_all_accuracy(regression_data, regressionResultLow)
        sell_indicator_after_filter_accuracy(regression_data, regressionResultLow, True, None)
        
        if(is_filter_all_accuracy(regression_data, regression_high, regression_low, regressionResultLow, 'Low', None)):
            all_withoutml(regression_data, regressionResultLow, None)
        sell_all_rule(regression_data, regressionResultLow, True, None)
        #if (is_algo_sell(regression_data)):
            #all_withoutml(regression_data, regressionResultLow, ws_lowSellReg)                               
        if (is_algo_sell(regression_high) and is_any_reg_algo_lt_minus1_not_other(regression_data)):
            sell_all_common_High_Low(regression_data, regressionResultLow, True, None)
            #all_withoutml(regression_data, regressionResultLow, ws_lowSellStrong)
        if (is_algo_sell(regression_high, True) and is_algo_sell(regression_low, True) and is_any_reg_algo_lt_minus1(regression_data)):
            sell_all_common_High_Low(regression_data, regressionResultLow, True, None)
            #all_withoutml(regression_data, regressionResultLow, ws_highSellStrong)
        if (is_algo_sell(regression_high, True) and is_algo_sell(regression_low, True) 
            and is_any_reg_algo_lt_minus1(regression_data)
            and is_any_reg_algo_lt_minus1_not_other(regression_data)
            ):
            sell_all_common_High_Low(regression_data, regressionResultLow, True, None)
            #all_withoutml(regression_data, regressionResultLow, ws_lowSellStrongBoth)
        
        all_withoutml(regression_data, regressionResultLow, ws_low)
        if("%%:" in regression_data['filter']
            or 'ConsolidationBreakout' in regression_data['filter']
            ):
            if((db['lowSell'].find_one({'scrip':scrip}) is None)):
                record = {}
                record['scrip'] = scrip
                record['ml'] = ''
                record['filter'] = regression_data['filter']
                record['filter2'] = ''
                record['filter3'] = ''
                json_data = json.loads(json.dumps(record, default=json_util.default))
                db['lowSell'].insert_one(json_data)
            else:
                db['lowSell'].update_one({'scrip':scrip}, { "$set": {'filter':regression_data['filter']}})
        
        regression_data = regression_high
        reg_data_filter = regression_data['filter']
        list = regression_data['filter'].partition(']:')
        lt_minus_2_count_any, lt_minus_2_cnt = filter_avg_lt_minus_2_count_any(regression_data)
        gt_2_count_any, gt_2_cnt = filter_avg_gt_2_count_any(regression_data)
        if(list[1] == ']:'):
            reg_data_filter = list[2]
        if ((is_algo_buy(regression_high) == True and 'Buy-AnyGT2' in regression_data['filter2'] and ('buy' in reg_data_filter or 'Buy' in reg_data_filter))
            or (is_algo_sell(regression_high) == True and 'Sell-AnyGT2' in regression_data['filter2'] and ('sell' in reg_data_filter or 'Sell' in reg_data_filter))
            or ((gt_2_count_any > 1 or ('Buy-SUPER' in regression_data['filter2'])) and gt_2_cnt > 1)
            or ((lt_minus_2_count_any > 1 or ('Sell-SUPER' in regression_data['filter2'])) and lt_minus_2_cnt > 1)
            ):
            all_withoutml(regression_data, regressionResultHigh, ws_highBuy)
        regression_data = regression_low
        reg_data_filter = regression_data['filter']
        list = regression_data['filter'].partition(']:')
        if(list[1] == ']:'):
            reg_data_filter = list[2]
        if ((is_algo_buy(regression_low) == True and 'Buy-AnyGT2' in regression_data['filter2'] and  ('buy' in reg_data_filter or 'Buy' in reg_data_filter))
            or (is_algo_sell(regression_low) == True and 'Sell-AnyGT2' in regression_data['filter2'] and  ('sell' in reg_data_filter or 'Sell' in reg_data_filter))
            or ((gt_2_count_any > 1 or ('Buy-SUPER' in regression_data['filter2'])) and gt_2_cnt > 1)
            or ((lt_minus_2_count_any > 1 or ('Sell-SUPER' in regression_data['filter2'])) and lt_minus_2_cnt > 1)
            ):
            all_withoutml(regression_data, regressionResultLow, ws_lowSell)
            
        
        regression_high_copy = copy.deepcopy(regression_high)
        regression_high_copy1 = copy.deepcopy(regression_high)
        regression_high_copy2 = copy.deepcopy(regression_high)
        regression_low_copy = copy.deepcopy(regression_low)
        regression_low_copy1 = copy.deepcopy(regression_low)
        regression_low_copy2 = copy.deepcopy(regression_low)
        
        regression_data = regression_high_copy2
        if(buy_high_volatility(regression_high_copy2, regressionResultHigh)):
            all_withoutml(regression_high_copy2, regressionResultHigh, ws_highAnalysis)
        if (is_algo_buy(regression_high_copy2)):
            all_withoutml(regression_data, regressionResultHigh, ws_highBuyReg)
        if ((is_algo_buy(regression_high_copy2) and is_any_reg_algo_gt1_not_other(regression_data))
            or (is_algo_buy(regression_high_copy2, True) and is_algo_buy(regression_low_copy2, True) and is_any_reg_algo_gt1(regression_data))
            ):
            buy_all_common_High_Low(regression_data, regressionResultHigh, True, None)
            all_withoutml(regression_data, regressionResultHigh, ws_highBuyStrong) 
            if((db['highBuy'].find_one({'scrip':scrip}) is None)):
                record = {}
                record['scrip'] = scrip
                record['ml'] = 'MLhighBuy'
                record['filter'] = ''
                record['filter2'] = ''
                record['filter3'] = ''
                json_data = json.loads(json.dumps(record, default=json_util.default))
                db['highBuy'].insert_one(json_data)
            else:
                dataHighBuy = db['highBuy'].find_one({'scrip':scrip})
                if(dataHighBuy['ml'] == ''):
                    db['highBuy'].update_one({'scrip':scrip}, { "$set": {'ml':'MLhighBuy'}})
        if ((is_algo_sell(regression_high_copy2) and is_any_reg_algo_lt_minus1_not_other(regression_data))
            or (is_algo_sell(regression_high_copy2, True) and is_algo_sell(regression_low_copy2, True) and is_any_reg_algo_lt_minus1(regression_data))
            ):
            sell_all_common_High_Low(regression_data, regressionResultLow, True, None)
            all_withoutml(regression_data, regressionResultLow, ws_highSellStrong)
        
        if (is_algo_buy(regression_high_copy2, True) and is_algo_buy(regression_low_copy2, True) 
            and is_any_reg_algo_gt1(regression_data)
            #and is_any_reg_algo_gt1_not_other(regression_data)
            ):
            buy_all_common_High_Low(regression_data, regressionResultHigh, True, None)
            all_withoutml(regression_data, regressionResultHigh, ws_highBuyStrongBoth)
            if((db['highBuy'].find_one({'scrip':scrip}) is None)):
                record = {}
                record['scrip'] = scrip
                record['ml'] = 'MLhighBuyStrongBoth'
                record['filter'] = ''
                record['filter2'] = ''
                record['filter3'] = ''
                json_data = json.loads(json.dumps(record, default=json_util.default))
                db['highBuy'].insert_one(json_data)
            else:
                db['highBuy'].update_one({'scrip':scrip}, { "$set": {'ml':'MLhighBuyStrongBoth'}})
                
        regression_data = regression_low_copy2
        if(sell_high_volatility(regression_low_copy2, regressionResultLow)):
            all_withoutml(regression_low_copy2, regressionResultLow, ws_lowAnalysis)
        if (is_algo_sell(regression_low_copy2)):
            all_withoutml(regression_data, regressionResultHigh, ws_lowSellReg)
        if ((is_algo_sell(regression_low_copy2) and is_any_reg_algo_lt_minus1_not_other(regression_data))
            or (is_algo_sell(regression_high_copy2, True) and is_algo_sell(regression_low_copy2, True) and is_any_reg_algo_lt_minus1(regression_data))
            ):
            sell_all_common_High_Low(regression_data, regressionResultLow, True, None)
            all_withoutml(regression_data, regressionResultLow, ws_lowSellStrong)
            if((db['lowSell'].find_one({'scrip':scrip}) is None)):
                record = {}
                record['scrip'] = scrip
                record['ml'] = 'MLlowSell'
                record['filter'] = ''
                record['filter2'] = ''
                record['filter3'] = ''
                json_data = json.loads(json.dumps(record, default=json_util.default))
                db['lowSell'].insert_one(json_data)
            else:
                dataLowSell = db['lowSell'].find_one({'scrip':scrip})
                if(dataLowSell['ml'] == ''):
                    db['lowSell'].update_one({'scrip':scrip}, { "$set": {'ml':'MLlowSell'}})
        if ((is_algo_buy(regression_low_copy2) and is_any_reg_algo_gt1_not_other(regression_data))
            or (is_algo_buy(regression_high_copy2, True) and is_algo_buy(regression_low_copy2, True) and is_any_reg_algo_gt1(regression_data))
            ):
            buy_all_common_High_Low(regression_data, regressionResultHigh, True, None)
            all_withoutml(regression_data, regressionResultHigh, ws_lowBuyStrong)
        
        if (is_algo_sell(regression_high_copy2, True) and is_algo_sell(regression_low_copy2, True) 
            and is_any_reg_algo_lt_minus1(regression_data)
            #and is_any_reg_algo_lt_minus1_not_other(regression_data)
            ):
            sell_all_common_High_Low(regression_data, regressionResultLow, True, None)
            all_withoutml(regression_data, regressionResultLow, ws_lowSellStrongBoth)
            if((db['lowSell'].find_one({'scrip':scrip}) is None)):
                record = {}
                record['scrip'] = scrip
                record['ml'] = 'MLlowSellStrongBoth'
                record['filter'] = ''
                record['filter2'] = ''
                record['filter3'] = ''
                json_data = json.loads(json.dumps(record, default=json_util.default))
                db['lowSell'].insert_one(json_data)
            else:
                db['lowSell'].update_one({'scrip':scrip}, { "$set": {'ml':'MLlowSellStrongBoth'}})
        
        regression_high_copy['filter1']=""
        if(is_filter_all_accuracy(regression_high_copy, regression_high, regression_low, regressionResultHigh, 'High', None)):
            all_withoutml(regression_high_copy, regressionResultHigh, ws_highBuyStrongFilterAcc)
            if(is_filter_hist_accuracy(regression_high_copy, regression_high, regression_low, regressionResultHigh, 'High', None)):
                if((db['highBuy'].find_one({'scrip':scrip}) is None)):
                    record = {}
                    record['scrip'] = scrip
                    record['ml'] = ''
                    record['filter'] = ''
                    record['filter2'] = regression_high_copy['filter2']
                    record['filter3'] = ''
                    json_data = json.loads(json.dumps(record, default=json_util.default))
                    db['highBuy'].insert_one(json_data)
                else:
                    db['highBuy'].update_one({'scrip':scrip}, { "$set": {'filter2':regression_high_copy['filter2']}})
                    
            if("ReversalLow" in regression_data['filter3']):     
                if((db['highBuy'].find_one({'scrip':scrip}) is None)):
                    record = {}
                    record['scrip'] = scrip
                    record['ml'] = ''
                    record['filter'] = ''
                    record['filter2'] = ''
                    record['filter3'] = regression_high_copy['filter3']
                    json_data = json.loads(json.dumps(record, default=json_util.default))
                    db['highBuy'].insert_one(json_data)
                else:
                    db['highBuy'].update_one({'scrip':scrip}, { "$set": {'filter3':regression_high_copy['filter3']}})
                    
            
        regression_low_copy['filter1']=""
        if(is_filter_all_accuracy(regression_low_copy, regression_high, regression_low, regressionResultLow, 'Low', None)):
            all_withoutml(regression_low_copy, regressionResultLow, ws_lowSellStrongFilterAcc)
            if(is_filter_hist_accuracy(regression_low_copy, regression_high, regression_low, regressionResultLow, 'Low', None)):
                if((db['lowSell'].find_one({'scrip':scrip}) is None)):
                    record = {}
                    record['scrip'] = scrip
                    record['ml'] = ''
                    record['filter'] = ''
                    record['filter2'] = regression_low_copy['filter2']
                    record['filter3'] = ''
                    json_data = json.loads(json.dumps(record, default=json_util.default))
                    db['lowSell'].insert_one(json_data)
                else:
                    db['lowSell'].update_one({'scrip':scrip}, { "$set": {'filter2':regression_low_copy['filter2']}})
                    
            if("ReversalHigh" in regression_data['filter3']):     
                if((db['lowSell'].find_one({'scrip':scrip}) is None)):
                    record = {}
                    record['scrip'] = scrip
                    record['ml'] = ''
                    record['filter'] = ''
                    record['filter2'] = ''
                    record['filter3'] = regression_low_copy['filter3']
                    json_data = json.loads(json.dumps(record, default=json_util.default))
                    db['lowSell'].insert_one(json_data)
                else:
                    db['lowSell'].update_one({'scrip':scrip}, { "$set": {'filter3':regression_low_copy['filter3']}})
        
        
        if(is_filter_all_accuracy(regression_high_copy1, regression_high, regression_low, regressionResultHigh, "None", None)
            and is_filter_all_accuracy(regression_low_copy1, regression_high, regression_low, regressionResultLow, "None", None)
            ):
            all_withoutml(regression_high_copy1, regressionResultHigh, ws_allFilterAcc) 
            all_withoutml(regression_low_copy1, regressionResultLow, ws_allFilterAcc)       
        
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
                                             
def calculateParallel(threads=2, futures='Yes', processing_date=""):
    pool = ThreadPool(threads)
    scrips = []
    
    if(processing_date == ""):
        processing_date = (datetime.date.today() - datetime.timedelta(days=0)).strftime('%Y-%m-%d')
    for data in db.scrip.find({'futures':futures}):
        #print('Scrip ', data)
        regdata = db.regressionlow.find_one({'scrip':data['scrip']})
        if(regdata is None):
            print('Missing or very less Data for ', data['scrip'])
        if(regdata is not None and regdata['date'] != processing_date):
            print('End Date ', regdata['date'], 'not recent for', data['scrip'])
        else: 
            scrips.append(data['scrip'])
    if (futures =='No' or futures =='NO' or futures =='no'):
        for data in db.scrip.find({'futures':'Yes'}):
            #print('Scrip ', data)
            regdata = db.regressionlow.find_one({'scrip':data['scrip']})
            if(regdata is None):
                print('Missing or very less Data for ', data['scrip'])
            if(regdata is not None and regdata['date'] != processing_date):
                print('End Date ', regdata['date'], 'not recent for', data['scrip'])
            else: 
                scrips.append(data['scrip'])
    scrips.sort()
    #pool.map(result_data, scrips)
    #pool.map(result_data_cla, scrips)
    pool.map(result_data_reg, scrips)

                      
if __name__ == "__main__":
    if not os.path.exists(directory):
        os.makedirs(directory)
    calculateParallel(1, sys.argv[1], sys.argv[2])
    connection.close()
    saveReports()