import json, datetime, time, copy, sys, csv, logging
sys.path.insert(0, '../')

from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.styles import Color, PatternFill, Font, Border
from pymongo import MongoClient
from multiprocessing.dummy import Pool as ThreadPool

import quandl, math, time
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
from talib.abstract import *
#from pip.req.req_file import preprocess
from Algorithms.regression_helpers import load_dataset, addFeatures, addFeaturesVolChange, \
    addFeaturesOpenChange, addFeaturesHighChange, addFeaturesLowChange, addFeaturesEMA9Change, addFeaturesEMA21Change, \
    mergeDataframes, count_missing, applyTimeLag, performRegression, performClassification
    
from util.util import getScore, all_day_pct_change_negative, all_day_pct_change_positive, historical_data
from util.util import soft  

from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import BaggingRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn import neighbors
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
#from sklearn.svm import SVR
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.svm import SVC, SVR
#from sklearn.qda import QDA
#from sklearn.grid_search import GridSearchCV

connection = MongoClient('localhost', 27017)
db = connection.Nsedata

forecast_out = 1
split = .98
randomForest = False
mlp = True
bagging = False
adaBoost = False
kNeighbours = True
gradientBoosting = False

def get_data_frame(df, regressor='kn', type='reg'):
    if (df is not None):
        #dfp = df[['PCT_day_change', 'HL_change', 'CL_change', 'CH_change', 'OL_change', 'OH_change']]
        dfp = df[['PCT_day_change']]
        if regressor == 'kn':
            #dfp['PCT_change'] = df['PCT_change']
            dfp['high_tail_pct'] = df['high_tail_pct']
            dfp['low_tail_pct'] = df['low_tail_pct']
            #dfp['bar_high'] = df['bar_high']
            #dfp['bar_low'] = df['bar_low']
#         dfp.loc[df['VOL_change'] > 20, 'VOL_change'] = 1
#         dfp.loc[df['VOL_change'] < 20, 'VOL_change'] = 0
#         dfp.loc[df['VOL_change'] < -20, 'VOL_change'] = -1
        columns = df.columns
        open = columns[1]
        high = columns[2]
        low = columns[3]
        close = columns[4]
        volume = columns[5]
        EMA9 = columns[-5]
        EMA21 = columns[-4]
#         for dele in range(1, 11):
#             addFeaturesVolChange(df, dfp, volume, dele)     
        for dele in range(1, 16):
            addFeaturesHighChange(df, dfp, high, dele)
        for dele in range(1, 16):
            addFeaturesLowChange(df, dfp, low, dele) 
        
        if type == 'reg':
            if regressor != 'mlp':
                dfp['EMA9'] = df['EMA9']
                dfp['EMA21'] = df['EMA21']
#         if regressor != 'mlp':      
#             for dele in range(1, 2):  
#                 addFeaturesEMA9Change(df, dfp, EMA9, dele)
#                 addFeaturesEMA21Change(df, dfp, EMA21, dele) 
 
        dfp['uptrend'] = df['uptrend']
        dfp['downtrend'] = df['downtrend']
#         dfp['greentrend'] = df['greentrend']
#         dfp['redtrend'] = df['redtrend']
        if soft == False:
            dfp['HH'] = df['HH']
            dfp['LL'] = df['LL']  
       
        if regressor != 'mlp':      
            dfp['ADX'] = ADX(df).apply(lambda x: 1 if x > 20 else 0) #Average Directional Movement Index http://www.investopedia.com/terms/a/adx.asp
            dfp['ADXR'] = ADXR(df).apply(lambda x: 1 if x > 20 else 0) #Average Directional Movement Index Rating https://www.scottrade.com/knowledge-center/investment-education/research-analysis/technical-analysis/the-indicators/average-directional-movement-index-rating-adxr.html
        dfp['APO'] = APO(df).apply(lambda x: 1 if x > 0 else 0) #Absolute Price Oscillator https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/apo
#         aroon = AROON(df) #Aroon http://www.investopedia.com/terms/a/aroon.asp
#         dfp['AROONUP'], dfp['AROONDOWN'] = aroon['aroonup'], aroon['aroondown']
        dfp['AROONOSC'] = AROONOSC(df).apply(lambda x: 1 if x > 0 else 0)
        dfp['BOP'] = BOP(df).apply(lambda x: 1 if x > 0 else 0) #Balance Of Power https://www.marketvolume.com/technicalanalysis/balanceofpower.asp
#         dfp['CCI'] = CCI(df) #Commodity Channel Index http://www.investopedia.com/articles/trading/05/041805.asp
#         dfp['CMO'] = CMO(df) #Chande Momentum Oscillator https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/cmo
#         dfp['DX'] = DX(df) #Directional Movement Index http://www.investopedia.com/terms/d/dmi.asp
#         macd = MACD(df)
#         dfp['MACD'], dfp['MACDSIGNAL'], dfp['MACDHIST'] = macd['macd'], macd['macdsignal'], macd['macdhist']
#         #dfp['MACDEXT'] = MACDEXT(df)
#         #dfp['MACDFIX'] = MACDFIX(df)
#         dfp['MFI'] = MFI(df)
#         dfp['MINUS_DI'] = MINUS_DI(df)
#         dfp['MINUS_DM'] = MINUS_DM(df)
#         dfp['MOM'] = MOM(df)
#         dfp['PLUS_DI'] = PLUS_DI(df)
#         dfp['PLUS_DM'] = PLUS_DM(df)
#         dfp['PPO'] = PPO(df)
#         dfp['ROC'] = ROC(df)
#         dfp['ROCP'] = ROCP(df)
#         dfp['ROCR'] = ROCR(df)
#         dfp['ROCR100'] = ROCR100(df)
#        dfp['RSI'] = RSI(df)
        #dfp['STOCH'] = STOCH(df)
        #dfp['STOCHF'] = STOCHF(df)
        #dfp['STOCHRSI'] = STOCHRSI(df)
#         dfp['TRIX'] = TRIX(df)
#         dfp['ULTOSC'] = ULTOSC(df)
#         dfp['WILLR'] = WILLR(df)
#         
#         bbands = BBANDS(df)
#         dfp['BBANDSUPPER'], dfp['BBANDSMIDDLE'], dfp['BBANDSLOWER'] = bbands['upperband'], bbands['middleband'], bbands['lowerband']
#         
# #       dfp['DEMA'] = DEMA(df)
#         dfp['EMA9'] = EMA(df,9)
#         dfp['EMA21'] = EMA(df,21)
#         dfp['EMA25'] = EMA(df,25)
#         dfp['EMA50'] = EMA(df,50)
#         dfp['EMA100'] = EMA(df,100)
#         dfp['EMA200'] = EMA(df,200)
#         dfp['HT_TRENDLINE'] = HT_TRENDLINE(df)
#         dfp['KAMA'] = KAMA(df)
#         dfp['MA'] = MA(df)
#         #dfp['MAMA'] = MAMA(df)
#         #dfp['MAVP'] = MAVP(df)
#         dfp['MIDPOINT'] = MIDPOINT(df)
#         dfp['MIDPRICE'] = MIDPRICE(df)
#         dfp['SAR'] = SAR(df)
#         dfp['SAREXT'] = SAREXT(df)
#         dfp['SMA'] = SMA(df)
#         dfp['SMA9'] = SMA(df, 9)
#         dfp['T3'] = T3(df)
#         dfp['TEMA'] = TEMA(df)
#         dfp['TRIMA'] = TRIMA(df)
#         dfp['WMA'] = WMA(df)


        dfp['CDL2CROWS'] = CDL2CROWS(df)
        dfp['CDL3BLACKCROWS'] = CDL3BLACKCROWS(df)
        dfp['CDL3INSIDE'] = CDL3INSIDE(df)
        dfp['CDL3LINESTRIKE'] = CDL3LINESTRIKE(df)
        dfp['CDL3OUTSIDE'] = CDL3OUTSIDE(df)
        dfp['CDL3STARSINSOUTH'] = CDL3STARSINSOUTH(df)
        dfp['CDL3WHITESOLDIERS'] = CDL3WHITESOLDIERS(df)
        dfp['CDLABANDONEDBABY'] = CDLABANDONEDBABY(df)
        dfp['CDLADVANCEBLOCK'] = CDLADVANCEBLOCK(df) #Bearish reversal. prior trend Upward. Look for three white candles in an upward price trend. On each candle, price opens within the body of the previous candle. The height of the shadows grow taller on the last two candles.
        dfp['CDLBELTHOLD'] = CDLBELTHOLD(df) # Bearish reversal. prior trend upward. Price opens at the high for the day and closes near the low, forming a tall black candle, often with a small lower shadow.
        dfp['CDLBREAKAWAY'] = CDLBREAKAWAY(df) # Bearish reversal. prior trend upward. Look for 5 candle lines in an upward price trend with the first candle being a tall white one. The second day should be a white candle with a gap between the two bodies, but the shadows can overlap. Day three should have a higher close and the candle can be any color. Day 4 shows a white candle with a higher close. The last day is a tall black candle with a close within the gap between the bodies of the first two candles.
        dfp['CDLCLOSINGMARUBOZU'] = CDLCLOSINGMARUBOZU(df)
        dfp['CDLCONCEALBABYSWALL'] = CDLCONCEALBABYSWALL(df)
        dfp['CDLCOUNTERATTACK'] = CDLCOUNTERATTACK(df)
        dfp['CDLDARKCLOUDCOVER'] = CDLDARKCLOUDCOVER(df)
        dfp['CDLDOJI'] = CDLDOJI(df)
        dfp['CDLDOJISTAR'] = CDLDOJISTAR(df)
        dfp['CDLDRAGONFLYDOJI'] = CDLDRAGONFLYDOJI(df)
        dfp['CDLENGULFING'] = CDLENGULFING(df)
        dfp['CDLEVENINGDOJISTAR'] = CDLEVENINGDOJISTAR(df)
        dfp['CDLEVENINGSTAR'] = CDLEVENINGSTAR(df)
        dfp['CDLGAPSIDESIDEWHITE'] = CDLGAPSIDESIDEWHITE(df)
        dfp['CDLGRAVESTONEDOJI'] = CDLGRAVESTONEDOJI(df)
        dfp['CDLHAMMER'] = CDLHAMMER(df)
        dfp['CDLHANGINGMAN'] = CDLHANGINGMAN(df)
        dfp['CDLHARAMI'] = CDLHARAMI(df)
        dfp['CDLHARAMICROSS'] = CDLHARAMICROSS(df)
        dfp['CDLHIGHWAVE'] = CDLHIGHWAVE(df)
        dfp['CDLHIKKAKE'] = CDLHIKKAKE(df)
        dfp['CDLHIKKAKEMOD'] = CDLHIKKAKEMOD(df)
        dfp['CDLHOMINGPIGEON'] = CDLHOMINGPIGEON(df)
        dfp['CDLIDENTICAL3CROWS'] = CDLIDENTICAL3CROWS(df)
        dfp['CDLINNECK'] = CDLINNECK(df)
        dfp['CDLINVERTEDHAMMER'] = CDLINVERTEDHAMMER(df)
        dfp['CDLKICKING'] = CDLKICKING(df)
        dfp['CDLKICKINGBYLENGTH'] = CDLKICKINGBYLENGTH(df)
        dfp['CDLLADDERBOTTOM'] = CDLLADDERBOTTOM(df)
        dfp['CDLLONGLEGGEDDOJI'] = CDLLONGLEGGEDDOJI(df)
        dfp['CDLLONGLINE'] = CDLLONGLINE(df)
        dfp['CDLMARUBOZU'] = CDLMARUBOZU(df)
        dfp['CDLMATCHINGLOW'] = CDLMATCHINGLOW(df)
        dfp['CDLMATHOLD'] = CDLMATHOLD(df)
        dfp['CDLMORNINGDOJISTAR'] = CDLMORNINGDOJISTAR(df)
        dfp['CDLMORNINGSTAR'] = CDLMORNINGSTAR(df)
        dfp['CDLONNECK'] = CDLONNECK(df)
        dfp['CDLPIERCING'] = CDLPIERCING(df)
        dfp['CDLRICKSHAWMAN'] = CDLRICKSHAWMAN(df)
        dfp['CDLRISEFALL3METHODS'] = CDLRISEFALL3METHODS(df)
        dfp['CDLSEPARATINGLINES'] = CDLSEPARATINGLINES(df)
        dfp['CDLSHOOTINGSTAR'] = CDLSHOOTINGSTAR(df)
        dfp['CDLSHORTLINE'] = CDLSHORTLINE(df)
        dfp['CDLSPINNINGTOP'] = CDLSPINNINGTOP(df)
        dfp['CDLSTALLEDPATTERN'] = CDLSTALLEDPATTERN(df)
        dfp['CDLSTICKSANDWICH'] = CDLSTICKSANDWICH(df)
        dfp['CDLTAKURI'] = CDLTAKURI(df)
        dfp['CDLTASUKIGAP'] = CDLTASUKIGAP(df)
        dfp['CDLTHRUSTING'] = CDLTHRUSTING(df)
        dfp['CDLTRISTAR'] = CDLTRISTAR(df)
        dfp['CDLUNIQUE3RIVER'] = CDLUNIQUE3RIVER(df)
        dfp['CDLUPSIDEGAP2CROWS'] = CDLUPSIDEGAP2CROWS(df)
        dfp['CDLXSIDEGAP3METHODS'] = CDLXSIDEGAP3METHODS(df)

#         dfp['AVGPRICE'] = AVGPRICE(df)
#         dfp['MEDPRICE'] = MEDPRICE(df)
#         dfp['TYPPRICE'] = TYPPRICE(df)
#         dfp['WCLPRICE'] = WCLPRICE(df)
# 
# #         dfp['ATR'] = ATR(df)
# #         dfp['NATR'] = NATR(df)
# #         dfp['TRANGE'] = TRANGE(df)
#         
#        dfp['AD'] = AD(df)
#        dfp['ADOSC'] = ADOSC(df)
#        dfp['OBV'] = OBV(df)
        dfp = dfp.ix[50:]    
        forecast_col = 'High_change1'
        dfp.dropna(inplace=True)
        dfp['label'] = dfp[forecast_col].shift(-forecast_out) 
        return dfp

def create_csv(regression_data):
    regression_data_db = db.regressionhigh.find_one({'scrip':regression_data['scrip']})
    if(regression_data_db is None):
        json_data = json.loads(json.dumps(regression_data))
        db.regressionhigh.insert_one(json_data)    
    
def process_regression_high(scrip, df, directory, run_ml_algo):
    regression_data_db = db.regressionhigh.find_one({'scrip':scrip})
    if(regression_data_db is not None):
        return
    
    dfp = get_data_frame(df, 'kn', 'reg')
    
    regression_data = {}
    if (kNeighbours and run_ml_algo):
        #result = performRegression(dfp, split, scrip, directory, forecast_out, KNeighborsRegressor(n_jobs=1, weights='distance'))
        result = performRegression(dfp, split, scrip, directory, forecast_out, RandomForestRegressor(max_depth=2, n_estimators=100, min_samples_leaf=5, n_jobs=1, random_state= 0))
#         result = performRegression(dfp, split, scrip, directory, forecast_out, RandomForestRegressor(bootstrap=True, criterion='mse', max_depth=2,
#            max_features='auto', max_leaf_nodes=None,
#            min_impurity_decrease=0.0, min_impurity_split=None,
#            min_samples_leaf=1, min_samples_split=2,
#            min_weight_fraction_leaf=0.0, n_estimators=100, n_jobs=None,
#            oob_score=False, random_state=0, verbose=0, warm_start=False))
        regression_data['kNeighboursValue_reg'] = float(result[0])
    else:
        regression_data['kNeighboursValue_reg'] = float(0)
            
    if (mlp and run_ml_algo):
        dfp = get_data_frame(df, 'mlp', 'reg')
        result = performRegression(dfp, split, scrip, directory, forecast_out, MLPRegressor(random_state=0, activation='tanh', solver='adam', max_iter=1000, hidden_layer_sizes=(57, 39, 27)))
        regression_data['mlpValue_reg'] = float(result[0])
    else:
        regression_data['mlpValue_reg'] = float(0)
        
    if (kNeighbours and run_ml_algo):
        dfp = get_data_frame(df, 'kn', 'cla')
        result = performClassification(dfp, split, scrip, directory, forecast_out, neighbors.KNeighborsClassifier(n_jobs=1, n_neighbors=3, weights='distance'))
        #result = performClassification(dfp, split, scrip, directory, forecast_out, RandomForestClassifier(n_estimators=10, n_jobs=1))
        #result = performClassification(dfp, split, scrip, directory, forecast_out, RandomForestClassifier(random_state=1, n_estimators=10, max_depth=None, min_samples_split=2, n_jobs=1))
        regression_data['kNeighboursValue_cla'] = float(result[0])
    else:
        regression_data['kNeighboursValue_cla'] = float(0)
            
    if (mlp and run_ml_algo):
        dfp = get_data_frame(df, 'mlp', 'cla')
        result = performClassification(dfp, split, scrip, directory, forecast_out, MLPClassifier(random_state=0, activation='tanh', solver='adam', max_iter=1000, hidden_layer_sizes=(51, 35, 25)))
        regression_data['mlpValue_cla'] = float(result[0])
    else:
        regression_data['mlpValue_cla'] = float(0)
    
    forecast_day_PCT_change = dfp.tail(1).loc[-forecast_out:, 'High_change1'].values[0]
    forecast_day_PCT2_change = dfp.tail(1).loc[-forecast_out:, 'High_change2'].values[0]
    forecast_day_PCT3_change = dfp.tail(1).loc[-forecast_out:, 'High_change3'].values[0]
    forecast_day_PCT4_change = dfp.tail(1).loc[-forecast_out:, 'High_change4'].values[0]
    forecast_day_PCT5_change = dfp.tail(1).loc[-forecast_out:, 'High_change5'].values[0]
    forecast_day_PCT7_change = dfp.tail(1).loc[-forecast_out:, 'High_change7'].values[0]
    forecast_day_PCT10_change = dfp.tail(1).loc[-forecast_out:, 'High_change10'].values[0]
    forecast_day_VOL_change = df.tail(1).loc[-forecast_out:, 'VOL_change'].values[0]
    forecast_day_date = df.tail(1).loc[-forecast_out:, 'date'].values[0]
    forecast_day_date_pre1 = df.tail(2).loc[-forecast_out:, 'date'].values[0]
    PCT_change_pre1 = df.tail(2).loc[-forecast_out:,'PCT_change'].values[0]
    PCT_change_pre2 = df.tail(3).loc[-forecast_out:,'PCT_change'].values[0]
    PCT_change_pre3 = df.tail(4).loc[-forecast_out:,'PCT_change'].values[0]
    PCT_change_pre4 = df.tail(5).loc[-forecast_out:,'PCT_change'].values[0]
    PCT_change_pre5 = df.tail(6).loc[-forecast_out:,'PCT_change'].values[0]
    PCT_day_change_pre1 = df.tail(2).loc[-forecast_out:,'PCT_day_change'].values[0]
    PCT_day_change_pre2 = df.tail(3).loc[-forecast_out:,'PCT_day_change'].values[0]
    PCT_day_change_pre3 = df.tail(4).loc[-forecast_out:,'PCT_day_change'].values[0]
    PCT_day_change_pre4 = df.tail(5).loc[-forecast_out:,'PCT_day_change'].values[0]
    PCT_day_change_pre5 = df.tail(6).loc[-forecast_out:,'PCT_day_change'].values[0]
    PCT_day_change_pre6 = df.tail(7).loc[-forecast_out:,'PCT_day_change'].values[0]
    PCT_day_change_pre7 = df.tail(8).loc[-forecast_out:,'PCT_day_change'].values[0]
    PCT_day_change_pre8 = df.tail(9).loc[-forecast_out:,'PCT_day_change'].values[0]
    PCT_change = df.tail(1).loc[-forecast_out:,'PCT_change'].values[0]
    PCT_day_change = df.tail(1).loc[-forecast_out:,'PCT_day_change'].values[0]
    PCT_day_OL = df.tail(1).loc[-forecast_out:, 'PCT_day_OL'].values[0]
    PCT_day_HO = df.tail(1).loc[-forecast_out:, 'PCT_day_HO'].values[0]
    PCT_day_CH = df.tail(1).loc[-forecast_out:, 'PCT_day_CH'].values[0]
    PCT_day_LC = df.tail(1).loc[-forecast_out:, 'PCT_day_LC'].values[0]
    Act_PCT_change = df.tail(1).loc[-forecast_out:,'Act_PCT_change'].values[0]
    Act_PCT_day_change = df.tail(1).loc[-forecast_out:,'Act_PCT_day_change'].values[0]
    Act_PCT_day_OL = df.tail(1).loc[-forecast_out:, 'Act_PCT_day_OL'].values[0]
    Act_PCT_day_HO = df.tail(1).loc[-forecast_out:, 'Act_PCT_day_HO'].values[0]
    Act_High_change = df.tail(1).loc[-forecast_out:, 'Act_High_change'].values[0]
    Act_Low_change = df.tail(1).loc[-forecast_out:, 'Act_Low_change'].values[0]
    score = df.tail(1).loc[-forecast_out:, 'uptrend'].values[0].astype(str) + '' + df.tail(1).loc[-forecast_out:, 'downtrend'].values[0].astype(str)
    volume = df.tail(1).loc[-forecast_out:, 'volume'].values[0]
    volume_pre1 = df.tail(2).loc[-forecast_out:, 'volume'].values[0]
    volume_pre2 = df.tail(3).loc[-forecast_out:, 'volume'].values[0]
    volume_pre3 = df.tail(4).loc[-forecast_out:, 'volume'].values[0]
    volume_pre4 = df.tail(5).loc[-forecast_out:, 'volume'].values[0]
    volume_pre5 = df.tail(6).loc[-forecast_out:, 'volume'].values[0]
    open = df.tail(1).loc[-forecast_out:, 'open'].values[0]
    open_pre1 = df.tail(2).loc[-forecast_out:, 'open'].values[0]
    open_pre2 = df.tail(3).loc[-forecast_out:, 'open'].values[0]
    high = df.tail(1).loc[-forecast_out:, 'high'].values[0]
    high_pre1 = df.tail(2).loc[-forecast_out:, 'high'].values[0]
    high_pre2 = df.tail(3).loc[-forecast_out:, 'high'].values[0]
    high_pre3 = df.tail(4).loc[-forecast_out:, 'high'].values[0]
    high_pre4 = df.tail(5).loc[-forecast_out:, 'high'].values[0]
    low = df.tail(1).loc[-forecast_out:, 'low'].values[0]
    low_pre1 = df.tail(2).loc[-forecast_out:, 'low'].values[0]
    low_pre2 = df.tail(3).loc[-forecast_out:, 'low'].values[0]
    low_pre3 = df.tail(4).loc[-forecast_out:, 'low'].values[0]
    low_pre4 = df.tail(5).loc[-forecast_out:, 'low'].values[0]
    close = df.tail(1).loc[-forecast_out:, 'close'].values[0]
    close_pre1 = df.tail(2).loc[-forecast_out:, 'close'].values[0]
    close_pre2 = df.tail(3).loc[-forecast_out:, 'close'].values[0]
    bar_high = df.tail(1).loc[-forecast_out:, 'bar_high'].values[0]
    bar_high_pre1 = df.tail(2).loc[-forecast_out:, 'bar_high'].values[0]
    bar_high_pre2 = df.tail(3).loc[-forecast_out:, 'bar_high'].values[0]
    bar_low = df.tail(1).loc[-forecast_out:, 'bar_low'].values[0]
    bar_low_pre1 = df.tail(2).loc[-forecast_out:, 'bar_low'].values[0]
    bar_low_pre2 = df.tail(3).loc[-forecast_out:, 'bar_low'].values[0]
    greentrend = df.tail(1).loc[-forecast_out:, 'greentrend'].values[0]
    redtrend = df.tail(1).loc[-forecast_out:, 'redtrend'].values[0]
    
    today_date = datetime.datetime.strptime(forecast_day_date, "%Y-%m-%d").date()
    
    end_date = (today_date - datetime.timedelta(weeks=1)).strftime('%Y-%m-%d')
    start_date = (today_date - datetime.timedelta(weeks=104)).strftime('%Y-%m-%d')
    dftemp = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    year2High = dftemp['high'].max()
    year2Low = dftemp['low'].min()
    year2BarHigh = max(dftemp['open'].max(), dftemp['close'].max())
    year2BarLow = min(dftemp['open'].min(), dftemp['close'].min())
    year2HighChange = (high - year2High)*100/year2High
    year2LowChange = (low - year2Low)*100/year2Low
    high_year2 = dftemp.tail(-1).loc[-forecast_out:, 'high'].values[0]
    low_year2 = dftemp.tail(-1).loc[-forecast_out:, 'low'].values[0]
    
    start_date = (today_date - datetime.timedelta(weeks=52)).strftime('%Y-%m-%d')
    dftemp = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    yearHigh = dftemp['high'].max()
    yearLow = dftemp['low'].min()
    yearBarHigh = max(dftemp['open'].max(), dftemp['close'].max())
    yearBarLow = min(dftemp['open'].min(), dftemp['close'].min())
    yearHighChange = (high - yearHigh)*100/yearHigh
    yearLowChange = (low - yearLow)*100/yearLow
    high_year = dftemp.tail(-1).loc[-forecast_out:, 'high'].values[0]
    low_year = dftemp.tail(-1).loc[-forecast_out:, 'low'].values[0]
    
    start_date = (today_date - datetime.timedelta(weeks=26)).strftime('%Y-%m-%d')
    dftemp = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    month6High = dftemp['high'].max()
    month6Low = dftemp['low'].min()
    month6BarHigh = max(dftemp['open'].max(), dftemp['close'].max())
    month6BarLow = min(dftemp['open'].min(), dftemp['close'].min())
    month6HighChange = (high - month6High)*100/month6High
    month6LowChange = (low - month6Low)*100/month6Low
    high_month6 = dftemp.tail(-1).loc[-forecast_out:, 'high'].values[0]
    low_month6 = dftemp.tail(-1).loc[-forecast_out:, 'low'].values[0]
    
    start_date = (today_date - datetime.timedelta(weeks=13)).strftime('%Y-%m-%d')
    dftemp = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    month3High = dftemp['high'].max()
    month3Low = dftemp['low'].min()
    month3BarHigh = max(dftemp['open'].max(), dftemp['close'].max())
    month3BarLow = min(dftemp['open'].min(), dftemp['close'].min())
    month3HighChange = (high - month3High)*100/month3High
    month3LowChange = (low - month3Low)*100/month3Low
    high_month3 = dftemp.tail(-1).loc[-forecast_out:, 'high'].values[0]
    low_month3 = dftemp.tail(-1).loc[-forecast_out:, 'low'].values[0]
    
    start_date = (today_date - datetime.timedelta(weeks=9)).strftime('%Y-%m-%d')
    dftemp = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    month2High = dftemp['high'].max()
    month2Low = dftemp['low'].min()
    month2BarHigh = max(dftemp['open'].max(), dftemp['close'].max())
    month2BarLow = min(dftemp['open'].min(), dftemp['close'].min())
    month2HighChange = (high - month2High)*100/month3High
    month2LowChange = (low - month2Low)*100/month3Low
    high_month2 = dftemp.tail(-1).loc[-forecast_out:, 'high'].values[0]
    low_month2 = dftemp.tail(-1).loc[-forecast_out:, 'low'].values[0]
    
    start_date = (today_date - datetime.timedelta(weeks=4)).strftime('%Y-%m-%d')
    dftemp = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    monthHigh = dftemp['high'].max()
    monthLow = dftemp['low'].min()
    monthBarHigh = max(dftemp['open'].max(), dftemp['close'].max())
    monthBarLow = min(dftemp['open'].min(), dftemp['close'].min())
    monthHighChange = (high - monthHigh)*100/monthHigh
    monthLowChange = (low - monthLow)*100/monthLow
    high_month = dftemp.tail(-1).loc[-forecast_out:, 'high'].values[0]
    low_month = dftemp.tail(-1).loc[-forecast_out:, 'low'].values[0]
    
    start_date = (today_date - datetime.timedelta(weeks=3)).strftime('%Y-%m-%d')
    dftemp = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    week3High = dftemp['high'].max()
    week3Low = dftemp['low'].min()
    week3BarHigh = max(dftemp['open'].max(), dftemp['close'].max())
    week3BarLow = min(dftemp['open'].min(), dftemp['close'].min())
    week3HighChange = (high - week3High)*100/week3High
    week3LowChange = (low - week3Low)*100/week3Low
    high_week3 = dftemp.tail(-1).loc[-forecast_out:, 'high'].values[0]
    low_week3 = dftemp.tail(-1).loc[-forecast_out:, 'low'].values[0]
    
    start_date = (today_date - datetime.timedelta(weeks=2)).strftime('%Y-%m-%d')
    dftemp = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    week2High = dftemp['high'].max()
    week2Low = dftemp['low'].min()
    week2BarHigh = max(dftemp['open'].max(), dftemp['close'].max())
    week2BarLow = min(dftemp['open'].min(), dftemp['close'].min())
    week2HighChange = (high - week2High)*100/week2High
    week2LowChange = (low - week2Low)*100/week2Low
    high_week2 = dftemp.tail(-1).loc[-forecast_out:, 'high'].values[0]
    low_week2 = dftemp.tail(-1).loc[-forecast_out:, 'low'].values[0]
    
    end_date = forecast_day_date_pre1
    start_date = (today_date - datetime.timedelta(weeks=1)).strftime('%Y-%m-%d')
    dftemp = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    weekHigh = dftemp['high'].max()
    weekLow = dftemp['low'].min()
    weekBarHigh = max(dftemp['open'].max(), dftemp['close'].max())
    weekBarLow = min(dftemp['open'].min(), dftemp['close'].min())
    weekHighChange = (high - weekHigh)*100/weekHigh
    weekLowChange = (low - weekLow)*100/weekLow
    high_week = dftemp.tail(-1).loc[-forecast_out:, 'high'].values[0]
    low_week = dftemp.tail(-1).loc[-forecast_out:, 'low'].values[0]
    
    scripinfo = db.scrip.find_one({'scrip':scrip})
    technical = db.technical.find_one({'dataset_code':scrip})
    regression_data['date'] = forecast_day_date
    regression_data['scrip'] = str(scrip)
    regression_data['industry'] = scripinfo['industry']
    regression_data['buyIndia'] = str(technical['BuyIndicators'])
    regression_data['sellIndia'] = str(technical['SellIndicators'])
    regression_data['forecast_day_VOL_change'] = float(forecast_day_VOL_change)
    regression_data['forecast_day_PCT_change'] = float(forecast_day_PCT_change)
    regression_data['forecast_day_PCT2_change'] = float(forecast_day_PCT2_change)
    regression_data['forecast_day_PCT3_change'] = float(forecast_day_PCT3_change)
    regression_data['forecast_day_PCT4_change'] = float(forecast_day_PCT4_change)
    regression_data['forecast_day_PCT5_change'] = float(forecast_day_PCT5_change)
    regression_data['forecast_day_PCT7_change'] = float(forecast_day_PCT7_change)
    regression_data['forecast_day_PCT10_change'] = float(forecast_day_PCT10_change)
    regression_data['score'] = score
    #regression_data['mlpValue'] = mlpValue
    #regression_data['kNeighboursValue'] = kNeighboursValue
    regression_data['trend'] = technical['trend']
    regression_data['year2HighChange'] = float(year2HighChange) 
    regression_data['year2LowChange'] = float(year2LowChange)
    regression_data['yearHighChange'] = float(yearHighChange) 
    regression_data['yearLowChange'] = float(yearLowChange)
    regression_data['month6HighChange'] = float(month6HighChange) 
    regression_data['month6LowChange'] = float(month6LowChange)
    regression_data['month3HighChange'] = float(month3HighChange) 
    regression_data['month3LowChange'] = float(month3LowChange)
    regression_data['month2HighChange'] = float(month2HighChange) 
    regression_data['month2LowChange'] = float(month2LowChange)
    regression_data['monthHighChange'] = float(monthHighChange) 
    regression_data['monthLowChange'] = float(monthLowChange)
    regression_data['week2HighChange'] = float(week2HighChange) 
    regression_data['week2LowChange'] = float(week2LowChange)
    regression_data['weekHighChange'] = float(weekHighChange) 
    regression_data['weekLowChange'] = float(weekLowChange)
    regression_data['year2High'] = float(year2High) 
    regression_data['year2Low'] = float(year2Low)
    regression_data['year2BarHigh'] = float(year2BarHigh) 
    regression_data['year2BarLow'] = float(year2BarLow)
    regression_data['yearHigh'] = float(yearHigh) 
    regression_data['yearLow'] = float(yearLow)
    regression_data['yearBarHigh'] = float(yearBarHigh) 
    regression_data['yearBarLow'] = float(yearBarLow)
    regression_data['month6High'] = float(month6High) 
    regression_data['month6Low'] = float(month6Low)
    regression_data['month6BarHigh'] = float(month6BarHigh) 
    regression_data['month6BarLow'] = float(month6BarLow)
    regression_data['month3High'] = float(month3High) 
    regression_data['month3Low'] = float(month3Low)
    regression_data['month3BarHigh'] = float(month3BarHigh) 
    regression_data['month3BarLow'] = float(month3BarLow)
    regression_data['month2High'] = float(month2High) 
    regression_data['month2Low'] = float(month2Low)
    regression_data['month2BarHigh'] = float(month2BarHigh) 
    regression_data['month2BarLow'] = float(month2BarLow)
    regression_data['monthHigh'] = float(monthHigh) 
    regression_data['monthLow'] = float(monthLow)
    regression_data['monthBarHigh'] = float(monthBarHigh) 
    regression_data['monthBarLow'] = float(monthBarLow)
    regression_data['week3High'] = float(week3High) 
    regression_data['week3Low'] = float(week3Low)
    regression_data['week3BarHigh'] = float(week3BarHigh) 
    regression_data['week3BarLow'] = float(week3BarLow)
    regression_data['week2High'] = float(week2High) 
    regression_data['week2Low'] = float(week2Low)
    regression_data['week2BarHigh'] = float(week2BarHigh) 
    regression_data['week2BarLow'] = float(week2BarLow)
    regression_data['weekHigh'] = float(weekHigh) 
    regression_data['weekLow'] = float(weekLow)
    regression_data['weekBarHigh'] = float(weekBarHigh) 
    regression_data['weekBarLow'] = float(weekBarLow)   
    regression_data['patterns'] = ''
    regression_data['PCT_change_pre1'] = float(PCT_change_pre1)
    regression_data['PCT_change_pre2'] = float(PCT_change_pre2)
    regression_data['PCT_change_pre3'] = float(PCT_change_pre3)
    regression_data['PCT_change_pre4'] = float(PCT_change_pre4)
    regression_data['PCT_change_pre5'] = float(PCT_change_pre5)
    regression_data['PCT_day_change_pre1'] = float(PCT_day_change_pre1)
    regression_data['PCT_day_change_pre2'] = float(PCT_day_change_pre2)
    regression_data['PCT_day_change_pre3'] = float(PCT_day_change_pre3)
    regression_data['PCT_day_change_pre4'] = float(PCT_day_change_pre4)
    regression_data['PCT_day_change_pre5'] = float(PCT_day_change_pre5)
    regression_data['PCT_day_change_pre6'] = float(PCT_day_change_pre6)
    regression_data['PCT_day_change_pre7'] = float(PCT_day_change_pre7)
    regression_data['PCT_day_change_pre8'] = float(PCT_day_change_pre8)
    regression_data['PCT_change'] = float(PCT_change)
    regression_data['PCT_day_change'] = float(PCT_day_change)
    regression_data['PCT_day_OL'] = float(PCT_day_OL)
    regression_data['PCT_day_HO'] = float(PCT_day_HO)
    regression_data['PCT_day_CH'] = float(PCT_day_CH)
    regression_data['PCT_day_LC'] = float(PCT_day_LC)
    regression_data['Act_PCT_change'] = float(Act_PCT_change)
    regression_data['Act_PCT_day_change'] = float(Act_PCT_day_change)
    regression_data['Act_PCT_day_OL'] = float(Act_PCT_day_OL)
    regression_data['Act_PCT_day_HO'] = float(Act_PCT_day_HO)
    regression_data['Act_High_change'] = float(Act_High_change)
    regression_data['Act_Low_change'] = float(Act_Low_change)
    regression_data['volume'] = float(volume)
    regression_data['volume_pre1'] = float(volume_pre1)
    regression_data['volume_pre2'] = float(volume_pre2)
    regression_data['volume_pre3'] = float(volume_pre3)
    regression_data['volume_pre4'] = float(volume_pre4)
    regression_data['volume_pre5'] = float(volume_pre5)
    regression_data['open'] = float(open)
    regression_data['open_pre1'] = float(open_pre1)
    regression_data['open_pre2'] = float(open_pre2)
    regression_data['high'] = float(high)
    regression_data['high_pre1'] = float(high_pre1)
    regression_data['high_pre2'] = float(high_pre2)
    regression_data['high_pre3'] = float(high_pre3)
    regression_data['high_pre4'] = float(high_pre4)
    regression_data['high_year2'] = float(high_year2) 
    regression_data['high_year'] = float(high_year) 
    regression_data['high_month6'] = float(high_month6) 
    regression_data['high_month3'] = float(high_month3)
    regression_data['high_month2'] = float(high_month2) 
    regression_data['high_month'] = float(high_month)
    regression_data['high_week3'] = float(high_week3)
    regression_data['high_week2'] = float(high_week2)
    regression_data['high_week'] = float(high_week) 
    regression_data['low'] = float(low)
    regression_data['low_pre1'] = float(low_pre1)
    regression_data['low_pre2'] = float(low_pre2)
    regression_data['low_pre3'] = float(low_pre3)
    regression_data['low_pre4'] = float(low_pre4)
    regression_data['low_year2'] = float(low_year2)
    regression_data['low_year'] = float(low_year)
    regression_data['low_month6'] = float(low_month6)
    regression_data['low_month3'] = float(low_month3)
    regression_data['low_month2'] = float(low_month2)
    regression_data['low_month'] = float(low_month)
    regression_data['low_week3'] = float(low_week3)
    regression_data['low_week2'] = float(low_week2)
    regression_data['low_week'] = float(low_week)
    regression_data['close'] = float(close)
    regression_data['close_pre1'] = float(close_pre1)
    regression_data['close_pre2'] = float(close_pre2)
    regression_data['bar_high'] = float(bar_high)
    regression_data['bar_high_pre1'] = float(bar_high_pre1)
    regression_data['bar_high_pre2'] = float(bar_high_pre2)
    regression_data['bar_low'] = float(bar_low)
    regression_data['bar_low_pre1'] = float(bar_low_pre1)
    regression_data['bar_low_pre2'] = float(bar_low_pre2)
    regression_data['greentrend'] = float(greentrend)
    regression_data['redtrend'] = float(redtrend)
    regression_data['EMA6'] = technical['overlap_studies']['EMA6'][0]
    regression_data['EMA14'] = technical['overlap_studies']['EMA14'][0]
    regression_data['EMA6_1daysBack'] = technical['overlap_studies']['EMA6'][1]
    regression_data['EMA14_1daysBack'] = technical['overlap_studies']['EMA14'][1]
    regression_data['EMA6_2daysBack'] = technical['overlap_studies']['EMA6'][2]
    regression_data['EMA14_2daysBack'] = technical['overlap_studies']['EMA14'][2]
    regression_data['SMA4_2daysBack'] = (float(close)-technical['overlap_studies']['SMA4'][2])*100/technical['overlap_studies']['SMA4'][2]
    regression_data['SMA9_2daysBack'] = (float(close)-technical['overlap_studies']['SMA9'][2])*100/technical['overlap_studies']['SMA9'][2]
    regression_data['ema6-14'] = (((technical['overlap_studies']['EMA6'][0] - technical['overlap_studies']['EMA14'][0])/technical['overlap_studies']['EMA14'][0])*100)
    regression_data['ema6-14_pre1'] = (((technical['overlap_studies']['EMA6'][1] - technical['overlap_studies']['EMA14'][1])/technical['overlap_studies']['EMA14'][1])*100)
    regression_data['ema6-14_pre2'] = (((technical['overlap_studies']['EMA6'][2] - technical['overlap_studies']['EMA14'][2])/technical['overlap_studies']['EMA14'][2])*100)
    regression_data['ema6-14_pre3'] = (((technical['overlap_studies']['EMA6'][3] - technical['overlap_studies']['EMA14'][3])/technical['overlap_studies']['EMA14'][3])*100)
    regression_data['ema6-14_pre4'] = (((technical['overlap_studies']['EMA6'][4] - technical['overlap_studies']['EMA14'][4])/technical['overlap_studies']['EMA14'][4])*100)
    regression_data['ema6-14_pre4'] = (((technical['overlap_studies']['EMA6'][5] - technical['overlap_studies']['EMA14'][5])/technical['overlap_studies']['EMA14'][5])*100)
    regression_data['ema6-14_pre5'] = (((technical['overlap_studies']['EMA6'][6] - technical['overlap_studies']['EMA14'][6])/technical['overlap_studies']['EMA14'][6])*100)
    regression_data['ema6-14_pre6'] = (((technical['overlap_studies']['EMA6'][7] - technical['overlap_studies']['EMA14'][7])/technical['overlap_studies']['EMA14'][7])*100)
    regression_data['ema6-14_pre7'] = (((technical['overlap_studies']['EMA6'][8] - technical['overlap_studies']['EMA14'][8])/technical['overlap_studies']['EMA14'][8])*100)
    regression_data['ema6-14_pre8'] = (((technical['overlap_studies']['EMA6'][9] - technical['overlap_studies']['EMA14'][9])/technical['overlap_studies']['EMA14'][9])*100)
    regression_data['SMA4_2daysBack'] = (float(close)-technical['overlap_studies']['SMA4'][2])*100/technical['overlap_studies']['SMA4'][2]
    regression_data['SMA9_2daysBack'] = (float(close)-technical['overlap_studies']['SMA9'][2])*100/technical['overlap_studies']['SMA9'][2]
    regression_data['SMA4'] = (float(close)-technical['overlap_studies']['SMA4'][0])*100/technical['overlap_studies']['SMA4'][0]
    regression_data['SMA9'] = (float(close)-technical['overlap_studies']['SMA9'][0])*100/technical['overlap_studies']['SMA9'][0]
    regression_data['SMA25'] = (float(close)-technical['overlap_studies']['SMA25'][0])*100/technical['overlap_studies']['SMA25'][0]
    regression_data['SMA50'] = (float(close)-technical['overlap_studies']['SMA50'][0])*100/technical['overlap_studies']['SMA50'][0]
    regression_data['SMA100'] = (float(close)-technical['overlap_studies']['SMA100'][0])*100/technical['overlap_studies']['SMA100'][0]
    regression_data['SMA200'] = (float(close)-technical['overlap_studies']['SMA200'][0])*100/technical['overlap_studies']['SMA200'][0]
    regression_data['mlpValue_reg_other'] = 0
    regression_data['kNeighboursValue_reg_other'] = 0
    regression_data['mlpValue_cla_other'] = 0
    regression_data['kNeighboursValue_cla_other'] = 0
    regression_data['forecast_kNeighboursValue_reg'] = 0
    regression_data['forecast_mlpValue_reg'] = 0
    regression_data['forecast_kNeighboursValue_cla'] = 0
    regression_data['forecast_mlpValue_cla'] = 0
    
    regression_data['highTail'] = 0
    regression_data['lowTail'] = 0
    if(regression_data['high'] - regression_data['bar_high'] == 0):
        regression_data['highTail'] = 0
    else:
        regression_data['highTail'] = (((regression_data['high'] - regression_data['bar_high'])/regression_data['bar_high'])*100)
    
    if((regression_data['bar_low'] - regression_data['low']) == 0):
        regression_data['lowTail'] = 0
    else:
        regression_data['lowTail'] = (((regression_data['bar_low'] - regression_data['low'])/regression_data['bar_low'])*100)
        
    regression_data['highTail_pre1'] = 0
    regression_data['lowTail_pre1'] = 0
    if(regression_data['high_pre1'] - regression_data['bar_high_pre1'] == 0):
        regression_data['highTail_pre1'] = 0
    else:
        regression_data['highTail_pre1'] = (((regression_data['high_pre1'] - regression_data['bar_high_pre1'])/regression_data['bar_high_pre1'])*100)
    
    if((regression_data['bar_low_pre1'] - regression_data['low_pre1']) == 0):
        regression_data['lowTail_pre1'] = 0
    else:
        regression_data['lowTail_pre1'] = (((regression_data['bar_low_pre1'] - regression_data['low_pre1'])/regression_data['bar_low_pre1'])*100)
    
    regression_data['highTail_pre2'] = 0
    regression_data['lowTail_pre2'] = 0
    if(regression_data['high_pre2'] - regression_data['bar_high_pre2'] == 0):
        regression_data['highTail_pre2'] = 0
    else:
        regression_data['highTail_pre2'] = (((regression_data['high_pre2'] - regression_data['bar_high_pre2'])/regression_data['bar_high_pre2'])*100)
    
    if((regression_data['bar_low_pre2'] - regression_data['low_pre2']) == 0):
        regression_data['lowTail_pre2'] = 0
    else:
        regression_data['lowTail_pre2'] = (((regression_data['bar_low_pre2'] - regression_data['low_pre2'])/regression_data['bar_low_pre2'])*100)
    #dfp.to_csv(directory + '/' + scrip + '_dfp.csv', encoding='utf-8')
    create_csv(regression_data)