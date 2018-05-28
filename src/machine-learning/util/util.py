import csv
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import Color, PatternFill, Font, Border
from pymongo import MongoClient
from multiprocessing.dummy import Pool as ThreadPool

import quandl, math, time
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np

buyMLP = 1
buyMLP_MIN = 1
buyKN = 0.5
buyKN_MIN = 0
sellMLP = -1
sellMLP_MIN = -1
sellKN = -0.5
sellKN_MIN = 0

def getScore(vol_change, pct_change):
    try:
        return float(vol_change)/float(pct_change) 
    except ZeroDivisionError:
        return 0

def all_day_pct_change_negative(regression_data):
    if(regression_data['forecast_day_PCT_change'] < 0
        and regression_data['forecast_day_PCT2_change'] <= 0
        and regression_data['forecast_day_PCT3_change'] <= 0
        and regression_data['forecast_day_PCT4_change'] <= 0
        and regression_data['forecast_day_PCT5_change'] <= 0
        and regression_data['forecast_day_PCT7_change'] <= 0
        and regression_data['forecast_day_PCT10_change'] <= 0):
        return True;
    
def all_day_pct_change_positive(regression_data):
    if(regression_data['forecast_day_PCT_change'] > 0
        and regression_data['forecast_day_PCT2_change'] > -0.5
        and regression_data['forecast_day_PCT3_change'] > -0.5
        and regression_data['forecast_day_PCT4_change'] > -0.5
        and regression_data['forecast_day_PCT5_change'] > -0.5
        and regression_data['forecast_day_PCT7_change'] > -0.5
        and regression_data['forecast_day_PCT10_change'] > -0.5):
        return True;    
        
def historical_data(data):
    ardate = np.array([str(x) for x in (np.array(data['data'])[:,0][::-1]).tolist()])
    aropen = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,1][::-1]).tolist()])
    arhigh = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,2][::-1]).tolist()])
    arlow  = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,3][::-1]).tolist()])
    arlast = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,4][::-1]).tolist()])
    arclose= np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,5][::-1]).tolist()])
    arquantity = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,6][::-1]).tolist()])
    arturnover = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,7][::-1]).tolist()])
    return ardate, aropen, arhigh, arlow, arlast, arclose, arquantity, arturnover

def no_doji_or_spinning_buy_india(regression_data):
    if ('SPINNINGTOP' not in str(regression_data['buyIndia']) and 'DOJI' not in str(regression_data['buyIndia'])):
        return True;
    else:
        return False
    
def no_doji_or_spinning_sell_india(regression_data): 
    if ('SPINNINGTOP' not in str(regression_data['sellIndia']) and 'DOJI' not in str(regression_data['sellIndia'])):
        return True;
    else:
        return False   
 
def scrip_patterns_to_dict(filename):  
    tempDict = {}
    count = 0
    with open(filename) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            try:
                if (count != 0):
                    dictValue = {}
                    dictValue['avg'] = row[1]
                    dictValue['count'] = row[2]
                    tempDict[row[0]] = dictValue
                count = count + 1
            except:
                pass
    return tempDict 