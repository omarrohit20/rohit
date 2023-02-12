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
from util.util import buy_all_rule, buy_year_high, buy_year_low, buy_up_trend, buy_down_trend, buy_final
from util.util import sell_all_rule, sell_year_high, sell_year_low, sell_up_trend, sell_down_trend, sell_final
from util.util import buy_oi, sell_oi, all_withoutml, withoutml
from util.util import buy_other_indicator, buy_all_common, buy_all_common_High_Low, sell_other_indicator, sell_all_common, sell_all_common_High_Low
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
from util.util import insert_year2LowReversal, insert_year5LowBreakout



connection = MongoClient('localhost', 27017)
db = connection.Nsedata

directory = '../../output/final'
logname = '../../output/final' + '/all-result' + time.strftime("%d%m%y-%H%M%S")

newsDict = {}
wb = Workbook()

ws_allFilterAcc = wb.create_sheet("AllFilterAcc")
ws_allFilterAcc.append(["BuyIndicators", "SellIndicators", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh5Change", "yLow5Change", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct","filterst_avg5","filterst_pct5","filterst_avg10","filterst_pct10","filterst_count","filter3st_avg5","filter3st_pct5","filter3st_avg10","filter3st_pct10","filter3st_count","filter4st_avg5","filter4st_pct5","filter4st_avg10","filter4st_pct10", "filter4st_count"])
ws_highBuyStrongFilterAcc = wb.create_sheet("HighBuyAllFilterAcc")
ws_highBuyStrongFilterAcc.append(["BuyIndicators", "SellIndicators", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh5Change", "yLow5Change", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct","filterst_avg5","filterst_pct5","filterst_avg10","filterst_pct10","filterst_count","filter3st_avg5","filter3st_pct5","filter3st_avg10","filter3st_pct10","filter3st_count","filter4st_avg5","filter4st_pct5","filter4st_avg10","filter4st_pct10", "filter4st_count"])
ws_lowSellStrongFilterAcc = wb.create_sheet("LowSellAllFilterAcc")
ws_lowSellStrongFilterAcc.append(["BuyIndicators", "SellIndicators", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh5Change", "yLow5Change", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct","filterst_avg5","filterst_pct5","filterst_avg10","filterst_pct10","filterst_count","filter3st_avg5","filter3st_pct5","filter3st_avg10","filter3st_pct10","filter3st_count","filter4st_avg5","filter4st_pct5","filter4st_avg10","filter4st_pct10", "filter4st_count"])
ws_highBuy = wb.create_sheet("HighBuy")
ws_highBuy.append(['scrip', 'PCT_change', 'PCT_day_change', 'ml', 'filter', 'filter2', 'filter3'])
ws_lowSell = wb.create_sheet("LowSell")
ws_lowSell.append(['scrip', 'PCT_change', 'PCT_day_change', 'ml', 'filter', 'filter2', 'filter3'])

ws_highAnalysis = wb.create_sheet("HighAnalysis")
ws_highAnalysis.append(["BuyIndicators", "SellIndicators", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh5Change", "yLow5Change", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct","filterst_avg5","filterst_pct5","filterst_avg10","filterst_pct10","filterst_count","filter3st_avg5","filter3st_pct5","filter3st_avg10","filter3st_pct10","filter3st_count","filter4st_avg5","filter4st_pct5","filter4st_avg10","filter4st_pct10", "filter4st_count"])
ws_lowAnalysis = wb.create_sheet("LowAnalysis")
ws_lowAnalysis.append(["BuyIndicators", "SellIndicators", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh5Change", "yLow5Change", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct","filterst_avg5","filterst_pct5","filterst_avg10","filterst_pct10","filterst_count","filter3st_avg5","filter3st_pct5","filter3st_avg10","filter3st_pct10","filter3st_count","filter4st_avg5","filter4st_pct5","filter4st_avg10","filter4st_pct10", "filter4st_count"])

ws_highBuyStrongBoth = wb.create_sheet("HighBuyStrongBoth")
ws_highBuyStrongBoth.append(["BuyIndicators", "SellIndicators", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh5Change", "yLow5Change", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct","filterst_avg5","filterst_pct5","filterst_avg10","filterst_pct10","filterst_count","filter3st_avg5","filter3st_pct5","filter3st_avg10","filter3st_pct10","filter3st_count","filter4st_avg5","filter4st_pct5","filter4st_avg10","filter4st_pct10", "filter4st_count"])
ws_lowSellStrongBoth = wb.create_sheet("LowSellStrongBoth")
ws_lowSellStrongBoth.append(["BuyIndicators", "SellIndicators", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh5Change", "yLow5Change", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct","filterst_avg5","filterst_pct5","filterst_avg10","filterst_pct10","filterst_count","filter3st_avg5","filter3st_pct5","filter3st_avg10","filter3st_pct10","filter3st_count","filter4st_avg5","filter4st_pct5","filter4st_avg10","filter4st_pct10", "filter4st_count"])
ws_highBuyStrong = wb.create_sheet("HighBuyStrong")
ws_highBuyStrong.append(["BuyIndicators", "SellIndicators", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh5Change", "yLow5Change", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct","filterst_avg5","filterst_pct5","filterst_avg10","filterst_pct10","filterst_count","filter3st_avg5","filter3st_pct5","filter3st_avg10","filter3st_pct10","filter3st_count","filter4st_avg5","filter4st_pct5","filter4st_avg10","filter4st_pct10", "filter4st_count"])
ws_lowSellStrong = wb.create_sheet("LowSellStrong")
ws_lowSellStrong.append(["BuyIndicators", "SellIndicators", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh5Change", "yLow5Change", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct","filterst_avg5","filterst_pct5","filterst_avg10","filterst_pct10","filterst_count","filter3st_avg5","filter3st_pct5","filter3st_avg10","filter3st_pct10","filter3st_count","filter4st_avg5","filter4st_pct5","filter4st_avg10","filter4st_pct10", "filter4st_count"])

ws_lowBuyStrong = wb.create_sheet("LowBuyStrong")
ws_lowBuyStrong.append(["BuyIndicators", "SellIndicators", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh5Change", "yLow5Change", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct","filterst_avg5","filterst_pct5","filterst_avg10","filterst_pct10","filterst_count","filter3st_avg5","filter3st_pct5","filter3st_avg10","filter3st_pct10","filter3st_count","filter4st_avg5","filter4st_pct5","filter4st_avg10","filter4st_pct10", "filter4st_count"])
ws_highSellStrong = wb.create_sheet("HighSellStrong")
ws_highSellStrong.append(["BuyIndicators", "SellIndicators", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh5Change", "yLow5Change", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct","filterst_avg5","filterst_pct5","filterst_avg10","filterst_pct10","filterst_count","filter3st_avg5","filter3st_pct5","filter3st_avg10","filter3st_pct10","filter3st_count","filter4st_avg5","filter4st_pct5","filter4st_avg10","filter4st_pct10", "filter4st_count"])
ws_highBuyReg = wb.create_sheet("HighBuyReg")
ws_highBuyReg.append(["BuyIndicators", "SellIndicators", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh5Change", "yLow5Change", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct","filterst_avg5","filterst_pct5","filterst_avg10","filterst_pct10","filterst_count","filter3st_avg5","filter3st_pct5","filter3st_avg10","filter3st_pct10","filter3st_count","filter4st_avg5","filter4st_pct5","filter4st_avg10","filter4st_pct10", "filter4st_count"])
ws_lowSellReg = wb.create_sheet("LowSellReg")
ws_lowSellReg.append(["BuyIndicators", "SellIndicators", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh5Change", "yLow5Change", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct","filterst_avg5","filterst_pct5","filterst_avg10","filterst_pct10","filterst_count","filter3st_avg5","filter3st_pct5","filter3st_avg10","filter3st_pct10","filter3st_count","filter4st_avg5","filter4st_pct5","filter4st_avg10","filter4st_pct10", "filter4st_count"])

ws_high = wb.create_sheet("HighAll")
ws_high.append(["BuyIndicators", "SellIndicators", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh5Change", "yLow5Change", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct","filterst_avg5","filterst_pct5","filterst_avg10","filterst_pct10","filterst_count","filter3st_avg5","filter3st_pct5","filter3st_avg10","filter3st_pct10","filter3st_count","filter4st_avg5","filter4st_pct5","filter4st_avg10","filter4st_pct10", "filter4st_count"])
ws_low = wb.create_sheet("LowAll")
ws_low.append(["BuyIndicators", "SellIndicators", "Symbol", "seriesTrend", "SMA4_2daysBack", "SMA9_2daysBack", "SMA4", "SMA9", "SMA25", "SMA50", "SMA100", "SMA200", "ResultDate", "ResultDeclared", "ResultSentiment", "ResultComment", "VOL_change", "OI_change", "Contract_change", "OI_change_next", "Contract_change_next", "PCT", "PCT2", "PCT3", "PCT4", "PCT5", "PCT7", "PCT10", "MLP_reg", "KNeighbors_reg", "MLP_cla", "KNeighbors_cla","MLP_reg_Other", "KNeighbors_reg_Other", "MLP_cla_Other", "KNeighbors_cla_Other", "forecast_mlpValue_reg", "forecast_kNeighboursValue_reg", "forecast_mlpValue_cla", "forecast_kNeighboursValue_cla", "yHigh5Change", "yLow5Change", "yHigh2Change", "yLow2Change", "yHighChange", "yLowChange", "m6HighChange", "m6LowChange", "m3HighChange", "m3LowChange", "mHighChange", "mLowChange", "w2HighChange", "w2LowChange", "wHighChange", "wLowChange", "trend", "Score", "HighTail", "LowTail", "Close", "PCT_Day_Change", "PCT_Change", "Symbol", "Industry", "Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter", "FilterBuy", "FilterSell", "Filter345Acc", "Filter345Count", "Filter345Pct", "Filter1Acc", "Filter1Count", "Filter1Pct", "FilterPctDayChangeAcc", "FilterPctDayChangeCount", "FilterPctDayChangePct", "FilterAllAcc", "FilterAllCount", "FilterAllPct", "FilterTechAcc", "FilterTechCount", "FilterTechPct", "FilterTechAllAcc", "FilterTechAllCount", "FilterTechAllPct", "FilterTechAllPctChangeAcc", "FilterTechAllPctChangeCount", "FilterTechAllPctChangePct","filterst_avg5","filterst_pct5","filterst_avg10","filterst_pct10","filterst_count","filter3st_avg5","filter3st_pct5","filter3st_avg10","filter3st_pct10","filter3st_count","filter4st_avg5","filter4st_pct5","filter4st_avg10","filter4st_pct10", "filter4st_count"])

def is_buy_filter(regression_data):
    if('%%:' in regression_data['filter']
        or "$$" in regression_data['filter']
        or 'ConsolidationBreakout' in regression_data['filter']
        or '%%HLTF:mayBuyTail-tailGT2-allDayLT0' in regression_data['filter']
        or '%%HLTF:mayBuyTail-tailGT2-7,10thDayLT0' in regression_data['filter']
        or '$$MayBuy-CheckChart(downTrend-mayReverseLast4DaysDown)' in regression_data['filter']
        or 'buyYearHigh-0' in regression_data['filter']
        or 'BuyYearLow' in regression_data['filter']
        or '%%:buyDownTrend-month3Low' in regression_data['filter']
        or 'buyFinal' in regression_data['filter']
        or 'buyMorningStar-HighLowerTail' in regression_data['filter']
        or 'sellEveningStar-0' in regression_data['filter']
        or 'checkCupUp' in regression_data['filter']
        or 'checkBuyConsolidationBreakUp' in regression_data['filter']
        or 'buyYear2LowBreakingUp' in regression_data['filter']
        or 'VOL:buy' in regression_data['filter']
        or 'VOL:Buy' in regression_data['filter']
        or regression_data['filter'].startswith('check')
        or regression_data['filter'].startswith('[MLBuy]:check')
        or regression_data['filter'].startswith('[MLSell]:check')
        or regression_data['filter'].startswith('buy')
        or regression_data['filter'].startswith('[MLBuy]:buy')
        or regression_data['filter'].startswith('[MLSell]:buy')
        or regression_data['filter'].startswith('Buy')
        or regression_data['filter'].startswith('[MLBuy]:Buy')
        or regression_data['filter'].startswith('[MLSell]:Buy')
        ):
        return True
    else:
        return False
    
def is_buy_filter2(regression_data):
    if('RISKY-UPTREND-SELL-0' in regression_data['filter2']
        or 'RISKY-UPTREND-SELL-1' in regression_data['filter2']
        or 'RISKY-UPTREND-SELL-2' in regression_data['filter2']
        or 'RISKY-UPTREND-SELL-3' in regression_data['filter2']
        or 'RISKY-UPTREND-SELL-4' in regression_data['filter2']
        ):
        return True
    else:
        return False
    
def is_buy_filter5(regression_data):
    if(regression_data['PCT_day_change'] > 2.5 or regression_data['PCT_change'] > 3 or ('DOJI' in regression_data['filter5'])):
        if('RISKY-UPTREND-SELL' in regression_data['filter5']):
            return 'RISKY-UPTREND-SELL'
        elif('RISKY-BUY-UPTREND-CONT' in regression_data['filter5']):
            return 'RISKY-BUY-UPTREND-CONT'
        else:
            return ""
    else:
        return ""
    
def is_buy_filterBuy(regression_data):
    if('Last3Day(GT1)' in regression_data['filterbuy']):
        return "Last3Day(GT1)"
    elif('Last2Day(GT1)' in regression_data['filterbuy']):
        return "Last2Day(GT1)"
    elif('Last3Day(GT2)' in regression_data['filterbuy']):
        return "Last3Day(GT2)"
    else:
        return ""
    
    
def is_sell_filter(regression_data):
    if('%%:' in regression_data['filter']
        or "$$" in regression_data['filter']
        or 'ConsolidationBreakdown' in regression_data['filter']
        or '%%HLTF:maySellTail-tailGT2-allDayGT0' in regression_data['filter']
        or '%%HLTF:maySellTail-tailGT2-7,10thDayGT0' in regression_data['filter']
        or '$$MaySell-CheckChart(downTrend-mayReverseLast4DaysUp)' in regression_data['filter']
        or 'sellYearLow' in regression_data['filter']
        or 'sellYearHigh' in regression_data['filter']
        or '%%:sellUpTrend-month3High' in regression_data['filter']
        or 'sellFinal' in regression_data['filter']
        or 'sellEveningStar-0' in regression_data['filter']
        or 'checkCupDown' in regression_data['filter']
        or 'checkSellConsolidationBreakDown' in regression_data['filter']
        or 'VOL:sell' in regression_data['filter']
        or 'VOL:Sell' in regression_data['filter']
        or regression_data['filter'].startswith('check')
        or regression_data['filter'].startswith('[MLBuy]:check')
        or regression_data['filter'].startswith('[MLSell]:check')
        or regression_data['filter'].startswith('sell')
        or regression_data['filter'].startswith('[MLBuy]:sell')
        or regression_data['filter'].startswith('[MLSell]:sell')
        or regression_data['filter'].startswith('Sell')
        or regression_data['filter'].startswith('[MLBuy]:Sell')
        or regression_data['filter'].startswith('[MLSell]:Sell')
        ):
        return True
    else:
        return False
    
def is_sell_filter2(regression_data):
    if('RISKY-DOWNTREND-BUY-0' in regression_data['filter2']
        or 'RISKY-DOWNTREND-BUY-1' in regression_data['filter2']
        or 'RISKY-DOWNTREND-BUY-2' in regression_data['filter2']
        or 'RISKY-DOWNTREND-BUY-3' in regression_data['filter2']
        or 'RISKY-DOWNTREND-BUY-4' in regression_data['filter2']
        ):
        return True
    else:
        return False
    
def is_sell_filter5(regression_data):
    if(regression_data['PCT_day_change'] < -2.5 or regression_data['PCT_change'] < -3 or ('DOJI' in regression_data['filter5'])):
        if('RISKY-DOWNTREND-BUY' in regression_data['filter5']):
            return 'RISKY-DOWNTREND-BUY'
        elif('RISKY-SELL-DOWNTREND-CONT' in regression_data['filter5']):
            return 'RISKY-SELL-DOWNTREND-CONT'
        else:
            return ""
    else:
        return ""
    

def is_sell_filterSell(regression_data):
    if('Last3Day(LT-1)' in regression_data['filtersell']):
        return 'Last3Day(LT-1)'
    elif('Last2Day(LT-1)' in regression_data['filtersell']):
        return 'Last2Day(LT-1)'
    elif('Last3Day(LT-2)' in regression_data['filtersell']):
        return 'Last3Day(LT-2)'
    else:
        return ""
    

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
    tab = Table(displayName="allFilterAcc", ref="A1:DE" + str(count))
    tab.tableStyleInfo = style
    ws_allFilterAcc.add_table(tab)
    
    count = 0
    for row in ws_highBuyReg.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="highBuyReg", ref="A1:DE" + str(count))
    tab.tableStyleInfo = style
    ws_highBuyReg.add_table(tab)
    
    count = 0
    for row in ws_highBuyStrong.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="highBuyStrong", ref="A1:DE" + str(count))
    tab.tableStyleInfo = style
    ws_highBuyStrong.add_table(tab)
    
    count = 0
    for row in ws_highBuyStrongFilterAcc.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="highBuyStrongFilterAcc", ref="A1:DE" + str(count))
    tab.tableStyleInfo = style
    ws_highBuyStrongFilterAcc.add_table(tab)
    
    count = 0
    for row in ws_highAnalysis.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="highAnalysis", ref="A1:DE" + str(count))
    tab.tableStyleInfo = style
    ws_highAnalysis.add_table(tab)
    
    count = 0
    for row in ws_high.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="high", ref="A1:DE" + str(count))
    tab.tableStyleInfo = style
    ws_high.add_table(tab)
    
    
    count = 0
    for row in ws_lowSellReg.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="lowSellReg", ref="A1:DE" + str(count))
    tab.tableStyleInfo = style
    ws_lowSellReg.add_table(tab)
    
    count = 0
    for row in ws_lowSellStrong.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="lowSellStrong", ref="A1:DE" + str(count))
    tab.tableStyleInfo = style
    ws_lowSellStrong.add_table(tab)
      
    count = 0
    for row in ws_lowSellStrongFilterAcc.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="lowSellStrongFilterAcc", ref="A1:DE" + str(count))
    tab.tableStyleInfo = style
    ws_lowSellStrongFilterAcc.add_table(tab)
    
    count = 0
    for row in ws_lowAnalysis.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="lowAnalysis", ref="A1:DE" + str(count))
    tab.tableStyleInfo = style
    ws_lowAnalysis.add_table(tab)
        
    count = 0
    for row in ws_low.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="low", ref="A1:DE" + str(count))
    tab.tableStyleInfo = style
    ws_low.add_table(tab)
    
    count = 0
    for row in ws_highBuyStrongBoth.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="highBuyStrongBoth", ref="A1:DE" + str(count))
    tab.tableStyleInfo = style
    ws_highBuyStrongBoth.add_table(tab)
    
    count = 0
    for row in ws_lowSellStrongBoth.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="lowSellStrongBoth", ref="A1:DE" + str(count))
    tab.tableStyleInfo = style
    ws_lowSellStrongBoth.add_table(tab)
    
    count = 0
    for row in ws_lowBuyStrong.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="lowBuyStrong", ref="A1:DE" + str(count))
    tab.tableStyleInfo = style
    ws_lowBuyStrong.add_table(tab)
    
    count = 0
    for row in ws_highSellStrong.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="highSellStrong", ref="A1:DE" + str(count))
    tab.tableStyleInfo = style
    ws_highSellStrong.add_table(tab)
    
    count = 0
    for row in ws_highBuy.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="highBuy", ref="A1:G" + str(count))
    tab.tableStyleInfo = style
    ws_highBuy.add_table(tab)
    
    count = 0
    for row in ws_lowSell.iter_rows(min_row=2):
        count += 1
    tab = Table(displayName="lowSell", ref="A1:G" + str(count))
    tab.tableStyleInfo = style
    ws_lowSell.add_table(tab)
    
    wb.save(logname + ".xlsx")
      
def result_data(scrip):
    regression_high = db.regressionhigh.find_one({'scrip':scrip})
    regression_low = db.regressionlow.find_one({'scrip':scrip})
    if(regression_high is None or regression_low is None):
        return
    
    
    regression_data = regression_high
    regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_low['mlpValue_reg'], 
                                            regression_low['kNeighboursValue_reg'],
                                            regression_low['mlpValue_cla'], 
                                            regression_low['kNeighboursValue_cla'],
                                            )
    if (buy_all_rule(regression_data, regressionResult, None, None)
        and buy_all_rule_classifier(regression_data, regressionResult, None, None)
        ):
        buy_other_indicator(regression_data, regressionResult, True, None)
        buy_other_indicator(regression_data, regressionResult, False, None)
        buy_filter_all_accuracy(regression_data, regressionResult)
        buy_all_common(regression_data, regressionResult, True, None)
    if (sell_all_rule(regression_data, regressionResult, None, None)
        and sell_all_rule_classifier(regression_data, regressionResult, None, None)
        ):
        sell_other_indicator(regression_data, regressionResult, True, None)
        sell_other_indicator(regression_data, regressionResult, False, None)
        sell_filter_all_accuracy(regression_data, regressionResult)
        sell_all_common(regression_data, regressionResult, True, None)
    if (buy_all_rule(regression_data, regressionResult, None, None)
        and buy_all_rule_classifier(regression_data, regressionResult, None, None)
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
    if (sell_all_rule(regression_data, regressionResult, None, None)
        and sell_all_rule_classifier(regression_data, regressionResult, None, None)
        ):
        sell_other_indicator(regression_data, regressionResult, True, None)
        sell_other_indicator(regression_data, regressionResult, False, None)
        sell_filter_all_accuracy(regression_data, regressionResult)
        sell_all_common(regression_data, regressionResult, True, None)
    if (buy_all_rule(regression_data, regressionResult, None, None)
        and buy_all_rule_classifier(regression_data, regressionResult, None, None)
        ):
        buy_other_indicator(regression_data, regressionResult, True, None)
        buy_other_indicator(regression_data, regressionResult, False, None)
        buy_filter_all_accuracy(regression_data, regressionResult)
        buy_all_common(regression_data, regressionResult, True, None)
    if (sell_all_rule(regression_data, regressionResult, None, None)
        and sell_all_rule_classifier(regression_data, regressionResult, None, None)
        ):
        all_withoutml(regression_data, regressionResult, ws_lowSellStrongBoth)

def result_data_summary(scrip):
    regression_high = db.highBuy.find_one({'scrip':scrip})
    regression_low = db.lowSell.find_one({'scrip':scrip})
    if(regression_high is not None):
        withoutml(regression_high, ws_highBuy)
    
    if(regression_low is not None):
        withoutml(regression_low, ws_lowSell)
                                                        
def result_data_reg(scrip):
    regression_high = db.regressionhigh.find_one({'scrip':scrip})
    regression_low = db.regressionlow.find_one({'scrip':scrip})
    if(regression_high is None or regression_low is None):
        return
    
    regression_data = regression_high
    if(regression_data is not None):
        regressionResultHigh = get_regressionResult(regression_data, scrip, db, 
                                            regression_low['mlpValue_reg'], 
                                            regression_low['kNeighboursValue_reg'],
                                            regression_low['mlpValue_cla'], 
                                            regression_low['kNeighboursValue_cla'],
                                            )
        buy_other_indicator(regression_data, regressionResultHigh, True, None)
        buy_filter_all_accuracy(regression_data, regressionResultHigh)
        
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
        if(is_buy_filter(regression_data)):
            if((db['highBuy'].find_one({'scrip':scrip}) is None)):
                record = {}
                record['scrip'] = scrip
                record['PCT_change'] =regression_data['PCT_change']
                record['PCT_day_change'] =regression_data['PCT_day_change']
                record['ml'] = ''
                record['filter'] = regression_data['filter']
                record['filter2'] = ''
                record['filter3'] = ''
                json_data = json.loads(json.dumps(record, default=json_util.default))
                db['highBuy'].insert_one(json_data)
            else:
                db['highBuy'].update_one({'scrip':scrip}, { "$set": {'filter':regression_data['filter']}})
                
        if("ReversalLow" in regression_data['filter3']):
            if((db['highBuy'].find_one({'scrip':scrip}) is None)):
                record = {}
                record['scrip'] = scrip
                record['PCT_change'] =regression_data['PCT_change']
                record['PCT_day_change'] =regression_data['PCT_day_change']
                record['ml'] = ''
                record['filter'] = ''
                record['filter2'] = ''
                record['filter3'] = regression_data['filter3']
                json_data = json.loads(json.dumps(record, default=json_util.default))
                db['highBuy'].insert_one(json_data)
            else:
                db['highBuy'].update_one({'scrip':scrip}, { "$set": {'filter3':regression_data['filter3']}})
        
          
                
    regression_data = regression_low
    if(regression_data is not None):
        regressionResultLow = get_regressionResult(regression_data, scrip, db, 
                                            regression_high['mlpValue_reg'], 
                                            regression_high['kNeighboursValue_reg'],
                                            regression_high['mlpValue_cla'], 
                                            regression_high['kNeighboursValue_cla'],
                                            False
                                            )
        sell_other_indicator(regression_data, regressionResultLow, True, None)
        sell_filter_all_accuracy(regression_data, regressionResultLow)
        
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
        if(is_sell_filter(regression_data)):
            if((db['lowSell'].find_one({'scrip':scrip}) is None)):
                record = {}
                record['scrip'] = scrip
                record['PCT_change'] =regression_data['PCT_change']
                record['PCT_day_change'] =regression_data['PCT_day_change']
                record['ml'] = ''
                record['filter'] = regression_data['filter']
                record['filter2'] = ''
                record['filter3'] = ''
                json_data = json.loads(json.dumps(record, default=json_util.default))
                db['lowSell'].insert_one(json_data)
            else:
                db['lowSell'].update_one({'scrip':scrip}, { "$set": {'filter':regression_data['filter']}})
                
        if("ReversalHigh" in regression_data['filter3']):
            if((db['lowSell'].find_one({'scrip':scrip}) is None)):
                record = {}
                record['scrip'] = scrip
                record['PCT_change'] =regression_data['PCT_change']
                record['PCT_day_change'] =regression_data['PCT_day_change']
                record['ml'] = ''
                record['filter'] = ''
                record['filter2'] = ''
                record['filter3'] = regression_data['filter3']
                json_data = json.loads(json.dumps(record, default=json_util.default))
                db['lowSell'].insert_one(json_data)
            else:
                db['lowSell'].update_one({'scrip':scrip}, { "$set": {'filter3':regression_data['filter3']}})
        
    
        regression_data = regression_high
        reg_data_filter = regression_data['filter']
        list = regression_data['filter'].partition(']:')
        lt_minus_2_count_any, lt_minus_2_cnt, lt_minus_2_max = filter_avg_lt_minus_2_count_any(regression_data)
        gt_2_count_any, gt_2_cnt, gt_2_max = filter_avg_gt_2_count_any(regression_data)
        if(list[1] == ']:'):
            reg_data_filter = list[2]
        # if ((is_algo_buy(regression_high) == True and 'Buy-AnyGT2' in regression_data['filter2'] and ('buy' in reg_data_filter or 'Buy' in reg_data_filter))
        #     or (is_algo_sell(regression_high) == True and 'Sell-AnyGT2' in regression_data['filter2'] and ('sell' in reg_data_filter or 'Sell' in reg_data_filter))
        #     or ((gt_2_count_any > 1 or ('Buy-SUPER' in regression_data['filter2'])) and gt_2_cnt > 1)
        #     or ((lt_minus_2_count_any > 1 or ('Sell-SUPER' in regression_data['filter2'])) and lt_minus_2_cnt > 1)
        #     ):
        #     all_withoutml(regression_data, regressionResultHigh, ws_highBuy)
        regression_data = regression_low
        reg_data_filter = regression_data['filter']
        list = regression_data['filter'].partition(']:')
        if(list[1] == ']:'):
            reg_data_filter = list[2]
        # if ((is_algo_buy(regression_low) == True and 'Buy-AnyGT2' in regression_data['filter2'] and  ('buy' in reg_data_filter or 'Buy' in reg_data_filter))
        #     or (is_algo_sell(regression_low) == True and 'Sell-AnyGT2' in regression_data['filter2'] and  ('sell' in reg_data_filter or 'Sell' in reg_data_filter))
        #     or ((gt_2_count_any > 1 or ('Buy-SUPER' in regression_data['filter2'])) and gt_2_cnt > 1)
        #     or ((lt_minus_2_count_any > 1 or ('Sell-SUPER' in regression_data['filter2'])) and lt_minus_2_cnt > 1)
        #     ):
        #     all_withoutml(regression_data, regressionResultLow, ws_lowSell)
            
        
        regression_high_copy = copy.deepcopy(regression_high)
        regression_high_copy1 = copy.deepcopy(regression_high)
        regression_high_copy2 = copy.deepcopy(regression_high)
        regression_low_copy = copy.deepcopy(regression_low)
        regression_low_copy1 = copy.deepcopy(regression_low)
        regression_low_copy2 = copy.deepcopy(regression_low)
        
        regression_data = regression_high_copy2
        if(buy_high_volatility(regression_high_copy2, regressionResultHigh)):
            all_withoutml(regression_high_copy2, regressionResultHigh, ws_highAnalysis)
            filterbuy = is_buy_filterBuy(regression_data)
            filter5 = is_buy_filter5(regression_data)
            # if(is_buy_filter2(regression_data)):
            #     if((db['highBuy'].find_one({'scrip':scrip}) is None)):
            #         record = {}
            #         record['scrip'] = scrip
            #         record['PCT_change'] =regression_data['PCT_change']
            #         record['PCT_day_change'] =regression_data['PCT_day_change']
            #         record['ml'] = ''
            #         record['filter'] = ''
            #         record['filter2'] = regression_data['filter2']
            #         record['filter3'] = ''
            #         json_data = json.loads(json.dumps(record, default=json_util.default))
            #         db['highBuy'].insert_one(json_data)
            #     else:
            #         db['highBuy'].update_one({'scrip':scrip}, { "$set": {'filter2':regression_data['filter2']}})
            # if(filterbuy != ""):
            #     if((db['highBuy'].find_one({'scrip':scrip}) is None)):
            #         record = {}
            #         record['scrip'] = scrip
            #         record['PCT_change'] =regression_data['PCT_change']
            #         record['PCT_day_change'] =regression_data['PCT_day_change']
            #         record['ml'] = ''
            #         record['filter'] = ''
            #         record['filter2'] = filterbuy
            #         record['filter3'] = ''
            #         json_data = json.loads(json.dumps(record, default=json_util.default))
            #         db['highBuy'].insert_one(json_data)
            #     else:
            #         temp = db['highBuy'].find_one({'scrip':scrip})
            #         db['highBuy'].update_one({'scrip':scrip}, { "$set": {'filter2':filterbuy + ',' + temp['filter2']}})
            # if(filter5 != ""):
            #     if((db['highBuy'].find_one({'scrip':scrip}) is None)):
            #         record = {}
            #         record['scrip'] = scrip
            #         record['PCT_change'] =regression_data['PCT_change']
            #         record['PCT_day_change'] =regression_data['PCT_day_change']
            #         record['ml'] = ''
            #         record['filter'] = ''
            #         record['filter2'] = filter5
            #         record['filter3'] = ''
            #         json_data = json.loads(json.dumps(record, default=json_util.default))
            #         db['highBuy'].insert_one(json_data)
            #     else:
            #         temp = db['highBuy'].find_one({'scrip':scrip})
            #         db['highBuy'].update_one({'scrip':scrip}, { "$set": {'filter2':filter5 + ',' + temp['filter2']}})
            
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
                record['PCT_change'] =regression_data['PCT_change']
                record['PCT_day_change'] =regression_data['PCT_day_change']
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
                record['PCT_change'] =regression_data['PCT_change']
                record['PCT_day_change'] =regression_data['PCT_day_change']
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
            filtersell = is_sell_filterSell(regression_data)
            filter5 = is_sell_filter5(regression_data)
            # if(is_sell_filter2(regression_data)):
            #     if((db['lowSell'].find_one({'scrip':scrip}) is None)):
            #         record = {}
            #         record['scrip'] = scrip
            #         record['PCT_change'] =regression_data['PCT_change']
            #         record['PCT_day_change'] =regression_data['PCT_day_change']
            #         record['ml'] = ''
            #         record['filter'] = ''
            #         record['filter2'] = regression_data['filter2']
            #         record['filter3'] = ''
            #         json_data = json.loads(json.dumps(record, default=json_util.default))
            #         db['lowSell'].insert_one(json_data)
            #     else:
            #         db['lowSell'].update_one({'scrip':scrip}, { "$set": {'filter2':regression_data['filter2']}})
            # if(filtersell != ""):
            #     if((db['lowSell'].find_one({'scrip':scrip}) is None)):
            #         record = {}
            #         record['scrip'] = scrip
            #         record['PCT_change'] =regression_data['PCT_change']
            #         record['PCT_day_change'] =regression_data['PCT_day_change']
            #         record['ml'] = ''
            #         record['filter'] = ''
            #         record['filter2'] = filtersell
            #         record['filter3'] = ''
            #         json_data = json.loads(json.dumps(record, default=json_util.default))
            #         db['lowSell'].insert_one(json_data)
            #     else:
            #         temp = db['lowSell'].find_one({'scrip':scrip})
            #         db['lowSell'].update_one({'scrip':scrip}, { "$set": {'filter2':(filtersell + ',' + temp['filter2'])}})
            # if(filter5 != ""):
            #     if((db['lowSell'].find_one({'scrip':scrip}) is None)):
            #         record = {}
            #         record['scrip'] = scrip
            #         record['PCT_change'] =regression_data['PCT_change']
            #         record['PCT_day_change'] =regression_data['PCT_day_change']
            #         record['ml'] = ''
            #         record['filter'] = ''
            #         record['filter2'] = filter5
            #         record['filter3'] = ''
            #         json_data = json.loads(json.dumps(record, default=json_util.default))
            #         db['lowSell'].insert_one(json_data)
            #     else:
            #         temp = db['lowSell'].find_one({'scrip':scrip})
            #         db['lowSell'].update_one({'scrip':scrip}, { "$set": {'filter2':(filter5 + ',' + temp['filter2'])}})
            
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
                record['PCT_change'] =regression_data['PCT_change']
                record['PCT_day_change'] =regression_data['PCT_day_change']
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
                record['PCT_change'] =regression_data['PCT_change']
                record['PCT_day_change'] =regression_data['PCT_day_change']
                record['ml'] = 'MLlowSellStrongBoth'
                record['filter'] = ''
                record['filter2'] = ''
                record['filter3'] = ''
                json_data = json.loads(json.dumps(record, default=json_util.default))
                db['lowSell'].insert_one(json_data)
            else:
                db['lowSell'].update_one({'scrip':scrip}, { "$set": {'ml':'MLlowSellStrongBoth'}})
        
        regression_high_copy['filter2']=""
        if(is_filter_all_accuracy(regression_high_copy, regression_high, regression_low, regressionResultHigh, 'High', None)):
            all_withoutml(regression_high_copy, regressionResultHigh, ws_highBuyStrongFilterAcc)
            if(is_filter_hist_accuracy(regression_high_copy, regression_high, regression_low, regressionResultHigh, 'High', None)):
                if((db['highBuy'].find_one({'scrip':scrip}) is None)):
                    record = {}
                    record['scrip'] = scrip
                    record['PCT_change'] =regression_data['PCT_change']
                    record['PCT_day_change'] =regression_data['PCT_day_change']
                    record['ml'] = ''
                    record['filter'] = ''
                    record['filter2'] = regression_high_copy['filter2']
                    record['filter3'] = ''
                    json_data = json.loads(json.dumps(record, default=json_util.default))
                    db['highBuy'].insert_one(json_data)
                else:
                    db['highBuy'].update_one({'scrip':scrip}, { "$set": {'filter2':regression_high_copy['filter2']}})
                            
            
        regression_low_copy['filter2']=""
        if(is_filter_all_accuracy(regression_low_copy, regression_high, regression_low, regressionResultLow, 'Low', None)):
            all_withoutml(regression_low_copy, regressionResultLow, ws_lowSellStrongFilterAcc)
            if(is_filter_hist_accuracy(regression_low_copy, regression_high, regression_low, regressionResultLow, 'Low', None)):
                if((db['lowSell'].find_one({'scrip':scrip}) is None)):
                    record = {}
                    record['scrip'] = scrip
                    record['PCT_change'] =regression_data['PCT_change']
                    record['PCT_day_change'] =regression_data['PCT_day_change']
                    record['ml'] = ''
                    record['filter'] = ''
                    record['filter2'] = regression_low_copy['filter2']
                    record['filter3'] = ''
                    json_data = json.loads(json.dumps(record, default=json_util.default))
                    db['lowSell'].insert_one(json_data)
                else:
                    db['lowSell'].update_one({'scrip':scrip}, { "$set": {'filter2':regression_low_copy['filter2']}})
                    
        
        if(is_filter_all_accuracy(regression_high_copy1, regression_high, regression_low, regressionResultHigh, "None", None)
            and is_filter_all_accuracy(regression_low_copy1, regression_high, regression_low, regressionResultLow, "None", None)
            ):
            if(('Buy-AnyGT2'in regression_high_copy1['filter2'] or 'Buy-AnyGT2' in regression_low_copy1['filter2']
                and 'Buy-AnyGT2-1.0' not in regression_high_copy1['filter2']
                and 'Buy-AnyGT2-1.0' not in regression_low_copy1['filter2']
                and 'Buy-AnyGT2-2.0' not in regression_high_copy1['filter2']
                and 'Buy-AnyGT2-2.0' not in regression_low_copy1['filter2']
                and 'Sell-Any' not in regression_high_copy1['filter2']
                and 'Sell-Any' not in regression_low_copy1['filter2']
                )
                #and 'Buy-Any' in regression_high_copy1['filter2'] and 'Buy-Any' in regression_low_copy1['filter2']
                #and 'Sell-Any' not in regression_high_copy1['filter2'] and 'Sell-Any' not in regression_low_copy1['filter2']
                #and (abs(regression_high_copy1['PCT_change']) > 1.5 or abs(regression_high_copy1['PCT_change_pre1']) > 1.5)
                ):
                all_withoutml(regression_high_copy1, regressionResultHigh, ws_allFilterAcc)
                all_withoutml(regression_low_copy1, regressionResultLow, ws_allFilterAcc)  
            if(('Sell-AnyGT2'in regression_high_copy1['filter2'] or 'Sell-AnyGT2' in regression_low_copy1['filter2']
                and 'Sell-AnyGT2-1.0' not in regression_high_copy1['filter2']
                and 'Sell-AnyGT2-1.0' not in regression_low_copy1['filter2']
                and 'Sell-AnyGT2-2.0' not in regression_high_copy1['filter2']
                and 'Sell-AnyGT2-2.0' not in regression_low_copy1['filter2']
                and 'Buy-Any' not in regression_high_copy1['filter2']
                and 'Buy-Any' not in regression_low_copy1['filter2']
                )
                #and 'Sell-Any' in regression_high_copy1['filter2'] and 'Sell-Any' in regression_low_copy1['filter2']
                #and 'Buy-Any' not in regression_high_copy1['filter2'] and 'Buy-Any' not in regression_low_copy1['filter2']
                #and (abs(regression_high_copy1['PCT_change']) > 1.5 or abs(regression_high_copy1['PCT_change_pre1']) > 1.5)
                ):
                all_withoutml(regression_high_copy1, regressionResultHigh, ws_allFilterAcc)
                all_withoutml(regression_low_copy1, regressionResultLow, ws_allFilterAcc)
            '''
            if (('Buy-SUPER' in regression_high_copy1['filter2'] or 'Buy-SUPER' in regression_low_copy1['filter2'])
                and (abs(regression_high_copy1['PCT_change']) > 2 or abs(regression_high_copy1['PCT_change_pre1']) > 2)
                ):
                all_withoutml(regression_high_copy1, regressionResultHigh, ws_allFilterAcc)
                all_withoutml(regression_low_copy1, regressionResultLow, ws_allFilterAcc)
            if (('Sell-SUPER' in regression_high_copy1['filter2'] or 'Sell-SUPER' in regression_low_copy1['filter2'])
                and (abs(regression_high_copy1['PCT_change']) > 2 or abs(regression_high_copy1['PCT_change_pre1']) > 2)
                ):
                all_withoutml(regression_high_copy1, regressionResultHigh, ws_allFilterAcc)
                all_withoutml(regression_low_copy1, regressionResultLow, ws_allFilterAcc)
            '''
        insert_year5LowBreakout(regression_data)
        insert_year2LowReversal(regression_data)
        
def result_data_cla(scrip):
    regression_high = db.regressionhigh.find_one({'scrip':scrip})
    regression_low = db.regressionlow.find_one({'scrip':scrip})
    if(regression_high is None or regression_low is None):
        return
    
    regression_data = regression_high
    if(regression_data is not None):
        regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_low['mlpValue_reg'], 
                                            regression_low['kNeighboursValue_reg'],
                                            regression_low['mlpValue_cla'], 
                                            regression_low['kNeighboursValue_cla'],
                                            )
        if buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvg, None):
            buy_other_indicator(regression_data, regressionResult, True, None)
            buy_filter_all_accuracy(regression_data, regressionResult)
            buy_all_rule_classifier(regression_data, regressionResult, buyIndiaAvg, ws_highBuyStrongFilterAcc)
                
    regression_data = regression_low
    if(regression_data is not None):
        regressionResult = get_regressionResult(regression_data, scrip, db, 
                                            regression_high['mlpValue_reg'], 
                                            regression_high['kNeighboursValue_reg'],
                                            regression_high['mlpValue_cla'], 
                                            regression_high['kNeighboursValue_cla'],
                                            False
                                            )
        if sell_all_rule_classifier(regression_data, regressionResult, None, None):
            sell_other_indicator(regression_data, regressionResult, True, None)
            sell_filter_all_accuracy(regression_data, regressionResult)
            sell_all_rule_classifier(regression_data, regressionResult, None, ws_lowSellStrongFilterAcc)                              
                                             
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
    pool.map(result_data_summary, scrips)

                      
if __name__ == "__main__":
    if not os.path.exists(directory):
        os.makedirs(directory)
    calculateParallel(1, sys.argv[1], sys.argv[2])
    connection.close()
    saveReports()