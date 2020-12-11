import os, logging, sys, json, csv, time
sys.path.insert(0, '../')

from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import Color, PatternFill, Font, Border
from pymongo import MongoClient
from multiprocessing.dummy import Pool as ThreadPool

import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np

from regression.regression_high import process_regression_high
from regression.regression_low import process_regression_low
from technical import ta_lib_data_df
from util.util import historical_data
from talib.abstract import *
from regression_result import result_data_reg

directory = '../../output' + '/regression/' + time.strftime("%d%m%y-%H%M%S")
logname = '../../output' + '/regression/mllog' + time.strftime("%d%m%y-%H%M%S")
logging.basicConfig(filename=logname, filemode='a', stream=sys.stdout, level=logging.INFO)
log = logging.getLogger(__name__)

connection = MongoClient('localhost', 27017)
db = connection.nsehistnew
dbNsedata = connection.Nsedata

forecast_out = 1
run_ml_algo = False

def regression_ta_data(scrip):
    data = db.regressionHistoryScrip.find_one({'dataset_code':scrip})
    if(data is not None):
        return
    
    data = dbNsedata.history.find_one({'dataset_code':scrip})
    if(data is None or (np.array(data['data'])).size < 1000):
        print('Main Missing or very less Data for ', scrip)
        return
        
    hsdate, hsopen, hshigh, hslow, hsclose, hsquantity = historical_data(data)   
    df = pd.DataFrame({
        'date': hsdate,
        'open': hsopen,
        'high': hshigh,
        'low': hslow,
        'close': hsclose,
        'volume': hsquantity
    })
    df = df[['date','open','high','low','close','volume']]
    
    df=df.rename(columns = {'total trade quantity':'volume'})
    df['volume_pre'] = df['volume'].shift(+1)
    df['open_pre'] = df['open'].shift(+1)
    df['high_pre'] = df['high'].shift(+1)
    df['low_pre'] = df['low'].shift(+1)
    df['close_pre'] = df['close'].shift(+1)
    df['VOL_change'] = (((df['volume'] - df['volume_pre'])/df['volume_pre'])*100)
    df['PCT_change'] = (((df['close'] - df['close_pre'])/df['close_pre'])*100)
    df['Act_PCT_change'] = df['PCT_change'].shift(-forecast_out)
    df['PCT_day_change'] = (((df['close'] - df['open'])/df['open'])*100)
    df['PCT_day_change_pre'] = (((df['close_pre'] - df['open_pre'])/df['open_pre'])*100)
    df['Act_PCT_day_change'] = df['PCT_day_change'].shift(-forecast_out)
    df['PCT_day_LH'] = (((df['high'] - df['low'])/df['low'])*100).astype(float)
    df['PCT_day_LC'] = (((df['close'] - df['low'])/df['low'])*100).astype(float)
    df['PCT_day_CH'] = (((df['close'] - df['high'])/df['close'])*100).astype(float)
    df['PCT_day_OL'] = (((df['low'] - df['open'])/df['open'])*100).astype(float)
    df['Act_PCT_day_OL'] = df['PCT_day_OL'].shift(-forecast_out)
    df['PCT_day_HO'] = (((df['high'] - df['open'])/df['open'])*100).astype(float)
    df['Act_PCT_day_HO'] = df['PCT_day_HO'].shift(-forecast_out)
    df['High_change'] = (((df['high'] - df['high_pre'])/df['high_pre'])*100)
    df['Act_High_change'] = df['High_change'].shift(-forecast_out)
    df['Low_change'] = (((df['low'] - df['low_pre'])/df['low_pre'])*100)
    df['Act_Low_change'] = df['Low_change'].shift(-forecast_out)
    
    df['bar_high'] = np.where(df['close'] > df['open'], df['close'], df['open'])
    df['bar_low'] = np.where(df['close'] > df['open'], df['open'], df['close'])
    df['high_tail'] = (df['high'] - df['bar_high'])
    df['low_tail'] = (df['low'] - df['bar_low'])
    df['high_tail_pct'] = np.where((df['high'] - df['bar_high'] == 0), 0, (((df['high'] - df['bar_high'])/df['bar_high'])*100))
    df['low_tail_pct'] = np.where((df['low'] - df['bar_low'] == 0), 0, (((df['low'] - df['bar_low'])/df['bar_low'])*100))
    df['bar_high_pre'] = np.where(df['close_pre'] > df['open_pre'], df['close_pre'], df['open_pre'])
    df['bar_low_pre'] = np.where(df['close_pre'] > df['open_pre'], df['open_pre'], df['close_pre'])
    df['uptrend'] = np.where((df['bar_high'] >  df['bar_high_pre']) & (df['high'] > df['high_pre']), 1, 0)
    df['downtrend'] = np.where((df['bar_low'] <  df['bar_low_pre']) & (df['low'] < df['low_pre']), -1, 0)
    df['greentrend'] = np.where((df['PCT_day_change'] > 0) & (df['PCT_day_change_pre'] > 0), 1, 0)
    df['redtrend'] = np.where((df['PCT_day_change'] < 0) & (df['PCT_day_change_pre'] < 0), -1, 0)
    df['bar'] = df['bar_high'] - df['bar_low']
    df['HH'] = np.where((df['high']-df['bar_high']) > (df['bar_high']-df['bar_low']), 1, 0)
    df['LL'] = np.where((df['bar_low']-df['low']) > (df['bar_high']-df['bar_low']), 1, 0)
    df['HHPc'] = ((((df['high']-df['bar_high']) - df['bar'])/df['bar'])*100).astype(float).round(1)
    df['LLPc'] = ((((df['bar_low']-df['low']) - df['bar'])/df['bar'])*100).astype(float).round(1)

    df['MACD'], df['MACDSIGNAL'], df['MACDHIST'] = MACD(df)
    df['EMA9'] = EMA(df,9)
    df['EMA21'] = EMA(df,21)
    df['EMA50'] = EMA(df,50)
    df['EMA100'] = EMA(df,100)
    df['EMA200'] = EMA(df,200)
    
    df.dropna(subset=['Act_PCT_change'], inplace = True)
    size = int((int(np.floor(df.shape[0]))/4)*3)
    print(scrip + " " + str(size))
    for x in range(size):
        try:
            close = df.tail(1).loc[-1:, 'close'].values[0]
            if (50 < close < 10000):
                #print(scrip + " " + str(size) + " " + str(close))
                db.technical.delete_many({'dataset_code':scrip})
                ta_lib_data_df(scrip, df, False) 
                regression_high = process_regression_high(scrip, df, directory, run_ml_algo, True)
                regression_low = process_regression_low(scrip, df, directory, run_ml_algo, True)
                result_data_reg(regression_high, regression_low, scrip)
            df = df[:-1]
        except IndexError as e:
            print(e)
        except Exception as e:
            print(e)
        
    db.regressionHistoryScrip.insert_one({
        "dataset_code": scrip,
        "date":(df['date'].values)[-1]
        })    

def calculateParallel(threads=1):
    pool = ThreadPool(threads)
    with open('../../data-import/nselist/test.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        scrips = []
        for row in readCSV:
            scrips.append(row[0])   
        scrips.sort()
        pool.map(regression_ta_data, scrips)   
                     
if __name__ == "__main__":
    if not os.path.exists(directory):
        os.makedirs(directory)
    calculateParallel(4)
    connection.close()