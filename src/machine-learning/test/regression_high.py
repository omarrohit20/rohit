import os, logging, sys, json, csv
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
    mergeDataframes, count_missing, applyTimeLag, performRegression
    
from util.util import getScore, all_day_pct_change_negative, all_day_pct_change_positive, historical_data    
    
from technical import ta_lib_data  

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
from sklearn.grid_search import GridSearchCV

connection = MongoClient('localhost', 27017)
db = connection.Nsedata

forecast_out = 1
split = .99
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
        EMA9 = columns[-2]
        EMA21 = columns[-1]
#         for dele in range(1, 11):
#             addFeaturesVolChange(df, dfp, volume, dele)     
        for dele in range(1, 16):
            addFeaturesHighChange(df, dfp, high, dele)
        for dele in range(1, 16):
            addFeaturesLowChange(df, dfp, low, dele) 
        if regressor != 'mlp':      
            for dele in range(1, 2):  
                addFeaturesEMA9Change(df, dfp, EMA9, dele)
                addFeaturesEMA21Change(df, dfp, EMA21, dele) 
        dfp['uptrend'] = df['uptrend']
        dfp['downtrend'] = df['downtrend']    
       
 
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

def create_csv(forecast_day_date, forecast_day_OL, forecast_day_HO, scrip, regressionResult):
    futures = str(regressionResult[0])   
    trainSize = int(regressionResult[1])
    buyIndia = str(regressionResult[2])
    sellIndia = str(regressionResult[3])
    scrip = str(regressionResult[4])
    forecast_day_VOL_change = int(regressionResult[5])
    forecast_day_PCT_change = float(regressionResult[6])
    forecast_day_PCT2_change = float(regressionResult[7])
    forecast_day_PCT3_change = float(regressionResult[8])
    forecast_day_PCT4_change = float(regressionResult[9])
    forecast_day_PCT5_change = float(regressionResult[10])
    forecast_day_PCT7_change = float(regressionResult[11])
    forecast_day_PCT10_change = float(regressionResult[12])
    PCT_day_change = float(regressionResult[13])
    PCT_change = float(regressionResult[14])
    score = str(regressionResult[15])
    kNeighboursValue = float(regressionResult[16])
    kNeighboursAccuracy = float(regressionResult[17])
    randomForestValue = float(regressionResult[18])
    randomForestAccuracy = float(regressionResult[19])
    mlpValue = float(regressionResult[20])
    mlpAccuracy = float(regressionResult[21])
    baggingValue = float(regressionResult[22])
    baggingAccuracy = float(regressionResult[23])
    adaBoostValue = float(regressionResult[24])
    adaBoostAccuracy = float(regressionResult[25])
    gradientBoostingValue = float(regressionResult[26])
    gradientBoostingAccuracy = float(regressionResult[27])
    trend = str(regressionResult[28])
    yearHighChange = float(regressionResult[29])
    yearLowChange = float(regressionResult[30])
    regressionResult.append(forecast_day_date)
    regressionResult.append(forecast_day_OL)
    regressionResult.append(forecast_day_HO)
    
    regression_data = {}
    regression_data['date'] = forecast_day_date
    regression_data['trainSize'] = trainSize
    regression_data['buyIndia'] = buyIndia
    regression_data['sellIndia'] = sellIndia
    regression_data['scrip'] = scrip
    regression_data['forecast_day_VOL_change'] = forecast_day_VOL_change
    regression_data['forecast_day_PCT_change'] = forecast_day_PCT_change
    regression_data['forecast_day_PCT2_change'] = forecast_day_PCT2_change
    regression_data['forecast_day_PCT3_change'] = forecast_day_PCT3_change
    regression_data['forecast_day_PCT4_change'] = forecast_day_PCT4_change
    regression_data['forecast_day_PCT5_change'] = forecast_day_PCT5_change
    regression_data['forecast_day_PCT7_change'] = forecast_day_PCT7_change
    regression_data['forecast_day_PCT10_change'] = forecast_day_PCT10_change
    regression_data['PCT_day_change'] = PCT_day_change
    regression_data['PCT_change'] = PCT_change
    regression_data['score'] = score
    regression_data['mlpValue'] = mlpValue
    regression_data['kNeighboursValue'] = kNeighboursValue
    regression_data['trend'] = trend 
    regression_data['yearHighChange'] = yearHighChange 
    regression_data['yearLowChange'] = yearLowChange
    regression_data['patterns'] = ''
    regression_data['forecast_day_OL'] = forecast_day_OL
    regression_data['forecast_day_HO'] = forecast_day_HO
    json_data = json.loads(json.dumps(regression_data))
    
    score = ''
    if(regression_data['score'] == '10' or regression_data['score'] == '1-1'):
        score = 'up'    
    dayClose = False
    if(regression_data['PCT_day_change'] > .5 and regression_data['PCT_change'] < .1):
        dayClose = True
    longTrend = False 
    if(all_day_pct_change_positive(regression_data)):
        longTrend = True     
    if(((regression_data['mlpValue'] >= 1 and regression_data['kNeighboursValue'] >= 0.5) or (regression_data['mlpValue'] >= 0.5 and regression_data['kNeighboursValue'] >= 1))
       and 'P@[' not in str(regression_data['sellIndia'])):
        stored = db.RbuyAll.find_one({'scrip':regression_data['scrip'], 'date':regression_data['date']})
        if stored is None:
            if (regression_data['buyIndia'] != ''):
                regression_data['patterns'] = 'Other'
            if(-5 <= regression_data['yearHighChange'] < -1 and regression_data['yearLowChange'] > 5 
                and -0.5 < regression_data['PCT_day_change'] < 3 and regression_data['forecast_day_PCT2_change'] <= 5):
                regression_data['patterns'] = regression_data['patterns'] + ', buyYearHigh'
                db.RbuyYearHigh.insert_one(json_data)
            elif(-15 < regression_data['yearHighChange'] < -5 and regression_data['yearLowChange'] > 5 
                and -0.5 < regression_data['PCT_day_change'] < 3 and (score == 'up'  or regression_data['forecast_day_PCT_change'] > 0)):
                regression_data['patterns'] = regression_data['patterns'] + ', buyYearHigh'
                db.RbuyYearHigh.insert_one(json_data)
                
            if(1 < regression_data['yearLowChange'] < 10 and regression_data['yearHighChange'] < -10 
                and 0 < regression_data['PCT_day_change'] < 3 and score == 'up'
                and (regression_data['forecast_day_PCT10_change'] <= -5 or regression_data['forecast_day_PCT5_change'] > 5)):
                regression_data['patterns'] = regression_data['patterns'] + ', buyYearLow' 
                db.RbuyYearLow.insert_one(json_data)
                
            if(longTrend and 0 < regression_data['PCT_day_change'] < 8 and regression_data['yearHighChange'] < -10
                and regression_data['forecast_day_PCT10_change'] >= regression_data['PCT_change'] + 2):
                regression_data['patterns'] = regression_data['patterns'] + ', buyUpTrend' 
                db.RbuyUpTrend.insert_one(json_data)   
                   
            if(regression_data['yearHighChange'] < -5 and regression_data['yearLowChange'] > 5 and regression_data['score'] != '0-1'):   
                if(2 > regression_data['PCT_day_change'] > 0 and str(regression_data['sellIndia']) == '' and -95 < regression_data['yearHighChange'] < -15
                    and regression_data['forecast_day_PCT5_change'] <= 1 and regression_data['forecast_day_PCT7_change'] <= 1 and regression_data['forecast_day_PCT10_change'] <= 1):
                    regression_data['patterns'] = regression_data['patterns'] + ', buyFinal'
                    db.RbuyFinal.insert_one(json_data)
                elif(2 > regression_data['PCT_day_change'] > 0
                    and regression_data['forecast_day_PCT5_change'] <= 1 and regression_data['forecast_day_PCT7_change'] <= -1 and regression_data['forecast_day_PCT10_change'] <= -5):
                    regression_data['patterns'] = regression_data['patterns'] + ', buyFinal1' 
                    db.RbuyFinal1.insert_one(json_data)
                 
            if(regression_data['PCT_day_change'] < 4 and regression_data['yearLowChange'] > 5):
                if(('MARUBOZU' in str(regression_data['buyIndia']) and regression_data['forecast_day_PCT5_change'] <= 0 and regression_data['forecast_day_PCT10_change'] <= 1)
                   or ('HAMMER' in str(regression_data['buyIndia']) and regression_data['PCT_day_change'] > 0)
                   #or 'ENGULFING' in str(regression_data['buyIndia'])
                   #or 'PIERCING' in str(regression_data['buyIndia'])
                   or ('MORNINGSTAR' in str(regression_data['buyIndia']) and regression_data['forecast_day_PCT5_change'] <= 0 and regression_data['forecast_day_PCT10_change'] <= 1)
                   #or ':DOJISTAR' in str(regression_data['buyIndia'])
                   #or 'MORNINGDOJISTAR' in str(regression_data['buyIndia'])
                   or 'ABANDONEDBABY' in str(regression_data['buyIndia'])
                   or 'COUNTERATTACK' in str(regression_data['buyIndia'])
                   or 'KICKING' in str(regression_data['buyIndia'])
                   or 'BREAKAWAY' in str(regression_data['buyIndia'])
                   #or 'TRISTAR' in str(regression_data['buyIndia'])
                   #or '3WHITESOLDIERS' in str(regression_data['buyIndia'])
                   #or '3INSIDE' in str(regression_data['buyIndia'])
                   ):
                    regression_data['patterns'] = regression_data['patterns'] + ', buyPattern'
                    db.RbuyPattern.insert_one(json_data) 
                elif(('CCI:BOP' in str(regression_data['buyIndia']) and 'BELTHOLD' in str(regression_data['buyIndia']))
                   or ('AROON:BOP' in str(regression_data['buyIndia']) and 'BELTHOLD' in str(regression_data['buyIndia']) and 'ENGULFING' in str(regression_data['buyIndia']))
                   or ('BELTHOLD' == str(regression_data['buyIndia']) and regression_data['forecast_day_PCT5_change'] <= 0 and score == 'up')
                   or ('3OUTSIDE' in str(regression_data['buyIndia']) and regression_data['forecast_day_PCT5_change'] <= 0 and score == 'up')
                   or ('HARAMI' in str(regression_data['buyIndia']) and regression_data['forecast_day_PCT5_change'] <= 0 and score == 'up')
                   or (regression_data['yearHighChange'] <= -35 and 'HARAMI' in str(regression_data['buyIndia']) and 'SHORTLINE' in str(regression_data['buyIndia']) and regression_data['PCT_day_change'] > 0)
                   or ('DOJI' in str(regression_data['buyIndia']) and 'GRAVESTONEDOJI' in str(regression_data['buyIndia']) and 'LONGLEGGEDDOJI' in str(regression_data['buyIndia']) and regression_data['PCT_day_change'] > 0)
                   or ('P@[,HIKKAKE]' == str(regression_data['buyIndia']) and regression_data['PCT_day_change'] < 0)
                   #or (regression_data['yearHighChange'] <= -35 and 'BELTHOLD' in str(regression_data['buyIndia']) and 'LONGLINE' in str(regression_data['buyIndia']))
                   #or (regression_data['yearHighChange'] <= -35 and ',CCI:BOP' in str(regression_data['buyIndia']) and 'LONGLINE' in str(regression_data['buyIndia']))
                   ):
                    regression_data['patterns'] = regression_data['patterns'] + ', buyPattern1'
                    db.RbuyPattern1.insert_one(json_data)
                elif((('MARUBOZU' in str(regression_data['buyIndia']) and regression_data['forecast_day_PCT5_change'] <= 0 and regression_data['forecast_day_PCT10_change'] <= 1)
                   or ('HAMMER' in str(regression_data['buyIndia']) and regression_data['PCT_day_change'] > 0)
                   or 'ENGULFING' in str(regression_data['buyIndia'])
                   or 'PIERCING' in str(regression_data['buyIndia'])
                   or ('MORNINGSTAR' in str(regression_data['buyIndia']) and regression_data['forecast_day_PCT5_change'] <= 0 and regression_data['forecast_day_PCT10_change'] <= 1)
                   or ':DOJISTAR' in str(regression_data['buyIndia'])
                   or 'MORNINGDOJISTAR' in str(regression_data['buyIndia'])
                   or 'ABANDONEDBABY' in str(regression_data['buyIndia'])
                   or 'COUNTERATTACK' in str(regression_data['buyIndia'])
                   or 'KICKING' in str(regression_data['buyIndia'])
                   or 'BREAKAWAY' in str(regression_data['buyIndia'])
                   or 'TRISTAR' in str(regression_data['buyIndia'])
                   or '3WHITESOLDIERS' in str(regression_data['buyIndia'])
                   or '3INSIDE' in str(regression_data['buyIndia'])
                   ) and (regression_data['forecast_day_PCT5_change'] <= -5) and (regression_data['forecast_day_PCT10_change'] <= -5)): 
                    regression_data['patterns'] = regression_data['patterns'] + ', buyPattern2'
                    db.RbuyPattern2.insert_one(json_data)
            if regression_data['patterns'] == 'Other':
                db.RbuyOthers.insert_one(json_data)
            db.RbuyAll.insert_one(json_data)    
    
def process_regression_high(scrip, df, buy, sell, trend, yearHighChange, yearLowChange, directory):
    if 'P@[' in str(sell):
        return
    dfp = get_data_frame(df)
    PCT_change = df.tail(1).loc[-forecast_out:,'PCT_change'].values[0]
    PCT_day_change = dfp.tail(1).loc[-forecast_out:,'PCT_day_change'].values[0]
    forecast_day_PCT_change = dfp.tail(1).loc[-forecast_out:, 'High_change1'].values[0]
    forecast_day_PCT2_change = dfp.tail(1).loc[-forecast_out:, 'High_change2'].values[0]
    forecast_day_PCT3_change = dfp.tail(1).loc[-forecast_out:, 'High_change3'].values[0]
    forecast_day_PCT4_change = dfp.tail(1).loc[-forecast_out:, 'High_change4'].values[0]
    forecast_day_PCT5_change = dfp.tail(1).loc[-forecast_out:, 'High_change5'].values[0]
    forecast_day_PCT7_change = dfp.tail(1).loc[-forecast_out:, 'High_change7'].values[0]
    forecast_day_PCT10_change = dfp.tail(1).loc[-forecast_out:, 'High_change10'].values[0]
    forecast_day_VOL_change = df.tail(1).loc[-forecast_out:, 'VOL_change'].values[0]
    forecast_day_date = df.tail(1).loc[-forecast_out:, 'date'].values[0]
    forecast_day_OL = df.tail(1).loc[-forecast_out:, 'OL_change'].values[0]
    forecast_day_HO = df.tail(1).loc[-forecast_out:, 'HO_change'].values[0]
    
    #score = getScore(forecast_day_VOL_change, forecast_day_PCT_change) 
    score = df.tail(1).loc[-forecast_out:, 'uptrend'].values[0].astype(str) + '' + df.tail(1).loc[-forecast_out:, 'downtrend'].values[0].astype(str)
    trainSize = int((df.shape)[0])
    
    regressionResult = [ ]
    regressionResult.append('YES')
    regressionResult.append(str(trainSize))
    regressionResult.append(str(buy))
    regressionResult.append(str(sell))
    regressionResult.append(str(scrip))
    regressionResult.append(forecast_day_VOL_change)
    regressionResult.append(forecast_day_PCT_change)
    regressionResult.append(forecast_day_PCT2_change)
    regressionResult.append(forecast_day_PCT3_change)
    regressionResult.append(forecast_day_PCT4_change)
    regressionResult.append(forecast_day_PCT5_change)
    regressionResult.append(forecast_day_PCT7_change)
    regressionResult.append(forecast_day_PCT10_change)
    regressionResult.append(PCT_day_change)
    regressionResult.append(PCT_change)
    regressionResult.append(score)
    
    #dfp.to_csv(directory + '/' + scrip + '_dfp.csv', encoding='utf-8')
    if kNeighbours:
        result = performRegression(dfp, split, scrip, directory, forecast_out, KNeighborsRegressor(n_jobs=1))
        if float(result[0]) < .5:
            return
        regressionResult.extend(result)
    else:
        regressionResult.extend([0,0])
    
    if randomForest:
        regressionResult.extend(performRegression(dfp, split, scrip, directory, forecast_out, RandomForestRegressor(max_depth=30, n_estimators=10, n_jobs=1)))
    else: 
        regressionResult.extend([0,0])
            
    if mlp:
        dfp_mlp = get_data_frame(df, 'mlp')
        regressionResult.extend(performRegression(dfp_mlp, split, scrip, directory, forecast_out, MLPRegressor(activation='tanh', solver='adam', max_iter=1000, hidden_layer_sizes=(57, 39, 27))))
    else:
        regressionResult.extend([0,0])
        
    if bagging:
        regressionResult.extend(performRegression(dfp, split, scrip, directory, forecast_out, SVR(C=1e3, cache_size=500, coef0=0.0, degree=3, epsilon=0.2, gamma=.05,
    kernel='rbf', max_iter=5000, shrinking=True, tol=0.001, verbose=False)))
    else:
        regressionResult.extend([0,0])
        
    if adaBoost:
        regressionResult.extend(performRegression(dfp, split, scrip, directory, forecast_out, AdaBoostRegressor()))
    else:
        regressionResult.extend([0,0])
        
    if gradientBoosting:
        regressionResult.extend(performRegression(dfp, split, scrip, directory, forecast_out, GradientBoostingRegressor()))
    else:
        regressionResult.extend([0,0])
    
    regressionResult.append(trend)
    regressionResult.append(yearHighChange)
    regressionResult.append(yearLowChange)
    create_csv(forecast_day_date, forecast_day_OL, forecast_day_HO, scrip, regressionResult)  
                                                          