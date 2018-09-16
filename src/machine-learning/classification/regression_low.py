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
    mergeDataframes, count_missing, applyTimeLag, performClassification
    
from util.util import getScore, all_day_pct_change_negative, all_day_pct_change_positive, historical_data
from util.util import soft 

from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import BaggingRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor, RadiusNeighborsClassifier
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
from sklearn.grid_search import GridSearchCV

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

def get_data_frame(df, regressor="None"):
    if (df is not None):
        #dfp = df[['PCT_day_change', 'HL_change', 'CL_change', 'CH_change', 'OL_change', 'OH_change']]
        dfp = df[['PCT_day_change']]
#         dfp.loc[df['VOL_change'] > 20, 'VOL_change'] = 1
#         dfp.loc[df['VOL_change'] < 20, 'VOL_change'] = 0
#         dfp.loc[df['VOL_change'] < -20, 'VOL_change'] = -1
        columns = df.columns
        open = columns[1]
        high = columns[2]
        low = columns[3]
        close = columns[4]
        volume = columns[5]
        EMA21 = columns[-4]
        EMA9 = columns[-5]
#         for dele in range(1, 11):
#             addFeaturesVolChange(df, dfp, volume, dele)     
        for dele in range(1, 16):
            addFeaturesHighChange(df, dfp, high, dele)
        for dele in range(1, 16):
            addFeaturesLowChange(df, dfp, low, dele) 
        
#         dfp['EMA9'] = df['EMA9']
#         dfp['EMA21'] = df['EMA21'] 
#         dfp['EMA50'] = df['EMA50'] 
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
        forecast_col = 'Low_change1'
        dfp.dropna(inplace=True)
        dfp['label'] = dfp[forecast_col].shift(-forecast_out) 
        return dfp

def create_csv(regression_data):
    regression_data_db = db.classificationlow.find_one({'scrip':regression_data['scrip']})
    if(regression_data_db is None):
        json_data = json.loads(json.dumps(regression_data))
        db.classificationlow.insert_one(json_data)    

def process_regression_low(scrip, df, buy, sell, trend, short_term, long_term, consolidation, directory):
    regression_data_db = db.classificationlow.find_one({'scrip':scrip})
    if(regression_data_db is not None):
        return
    
    dfp = get_data_frame(df)
    
    regression_data = {}
    if kNeighbours:
        result = performClassification(dfp, split, scrip, directory, forecast_out, neighbors.KNeighborsClassifier(n_jobs=1, n_neighbors=3))
        #result = performClassification(dfp, split, scrip, directory, forecast_out, RandomForestClassifier(random_state=1, n_estimators=10, max_depth=None, min_samples_split=2, n_jobs=1))
        #result = performClassification(dfp, split, scrip, directory, forecast_out, neighbors.RadiusNeighborsClassifier(radius=1.0))
        regression_data['kNeighboursValue'] = float(result[0])
    else:
        regression_data['kNeighboursValue'] = float(0)
            
    if mlp:
        dfp_mlp = get_data_frame(df, 'mlp')
        result = performClassification(dfp_mlp, split, scrip, directory, forecast_out, MLPClassifier(random_state=1, activation='tanh', solver='adam', max_iter=1000, hidden_layer_sizes=(51, 35, 25)))
        regression_data['mlpValue'] = float(result[0])
    else:
        regression_data['mlpValue'] = float(0)
    
    forecast_day_PCT_change = dfp.tail(1).loc[-forecast_out:, 'Low_change1'].values[0]
    forecast_day_PCT2_change = dfp.tail(1).loc[-forecast_out:, 'Low_change2'].values[0]
    forecast_day_PCT3_change = dfp.tail(1).loc[-forecast_out:, 'Low_change3'].values[0]
    forecast_day_PCT4_change = dfp.tail(1).loc[-forecast_out:, 'Low_change4'].values[0]
    forecast_day_PCT5_change = dfp.tail(1).loc[-forecast_out:, 'Low_change5'].values[0]
    forecast_day_PCT7_change = dfp.tail(1).loc[-forecast_out:, 'Low_change7'].values[0]
    forecast_day_PCT10_change = dfp.tail(1).loc[-forecast_out:, 'Low_change10'].values[0]
    forecast_day_VOL_change = df.tail(1).loc[-forecast_out:, 'VOL_change'].values[0]
    forecast_day_date = df.tail(1).loc[-forecast_out:, 'date'].values[0]
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
    open = df.tail(1).loc[-forecast_out:, 'open'].values[0]
    high = df.tail(1).loc[-forecast_out:, 'high'].values[0]
    low = df.tail(1).loc[-forecast_out:, 'low'].values[0]
    bar_high = df.tail(1).loc[-forecast_out:, 'bar_high'].values[0]
    bar_low = df.tail(1).loc[-forecast_out:, 'bar_low'].values[0]
    bar_high_pre = df.tail(1).loc[-forecast_out:, 'bar_high_pre'].values[0]
    bar_low_pre = df.tail(1).loc[-forecast_out:, 'bar_low_pre'].values[0]
    close = df.tail(1).loc[-forecast_out:, 'close'].values[0]
    greentrend = df.tail(1).loc[-forecast_out:, 'greentrend'].values[0]
    redtrend = df.tail(1).loc[-forecast_out:, 'redtrend'].values[0]
    
    today_date = datetime.datetime.strptime(forecast_day_date, '%Y-%m-%d').date()
    start_date = (today_date - datetime.timedelta(weeks=52)).strftime('%Y-%m-%d')
    df = df[(df['date'] >= start_date) & (df['date'] <= forecast_day_date)]
    yearHigh = df['high'].max()
    yearLow = df['low'].min()
    yearHighChange = (close - yearHigh)*100/yearHigh
    yearLowChange = (close - yearLow)*100/yearLow
    
    start_date = (datetime.date.today() - datetime.timedelta(weeks=104)).strftime('%Y-%m-%d')
    df = df[(df['date'] >= start_date) & (df['date'] <= forecast_day_date)]
    yearHigh = df['high'].max()
    yearLow = df['low'].min()
    yearHigh2Change = (close - yearHigh)*100/yearHigh
    yearLow2Change = (close - yearLow)*100/yearLow
    
    regression_data['date'] = forecast_day_date
    regression_data['scrip'] = str(scrip)
    regression_data['buyIndia'] = str(buy)
    regression_data['sellIndia'] = str(sell)
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
    regression_data['trend'] = trend 
    regression_data['yearHighChange'] = float(yearHighChange) 
    regression_data['yearLowChange'] = float(yearLowChange)
    regression_data['yearHigh2Change'] = float(yearHigh2Change) 
    regression_data['yearLow2Change'] = float(yearLow2Change)
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
    regression_data['open'] = float(open)
    regression_data['high'] = float(high)
    regression_data['low'] = float(low)
    regression_data['bar_high'] = float(bar_high)
    regression_data['bar_low'] = float(bar_low)
    regression_data['bar_high_pre'] = float(bar_high_pre)
    regression_data['bar_low_pre'] = float(bar_low_pre)
    regression_data['close'] = float(close)
    regression_data['greentrend'] = float(greentrend)
    regression_data['redtrend'] = float(redtrend)
    regression_data['short_term'] = short_term
    regression_data['long_term'] = long_term
    regression_data['consolidation'] = float(consolidation)
    
    #dfp.to_csv(directory + '/' + scrip + '_dfp.csv', encoding='utf-8')
    create_csv(regression_data)