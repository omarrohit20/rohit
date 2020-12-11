import json, datetime, time, copy, sys, csv, logging
from dateutil import parser
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from pymongo import MongoClient
from multiprocessing.dummy import Pool as ThreadPool

import pandas as pd
from datetime import date
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
import talib 
from talib.abstract import *

logname = '../../output' + '/technical' + time.strftime("%d%m%y-%H%M%S")
logging.basicConfig(filename=logname, filemode='a', level=logging.INFO)
log = logging.getLogger(__name__)

connection = MongoClient('localhost',27017)
db = connection.nsehistnew
db = connection.Nsedata
# db.drop_collection('technical')
# db.drop_collection('buy.overlap')
# db.drop_collection('sell.overlap')
# db.drop_collection('buy.pattern')
# db.drop_collection('sell.pattern')
# db.drop_collection('buy.momentum')
# db.drop_collection('sell.momentum')
# db.drop_collection('buy.volume')
# db.drop_collection('sell.volume')

wb = Workbook()
ws = wb.active
ws.append(["Symbol", "Buy", "Sell"])

def saveReports():
    tab = Table(displayName="Table1", ref="A1:C503")
    # Add a default style with striped rows and banded columns
    style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
               showLastColumn=False, showRowStripes=True, showColumnStripes=True)
    tab.tableStyleInfo = style
    ws.add_table(tab)
    wb.save(logname + ".xlsx")

def numpy_conversion(arr):
    return np.array([x.encode('UTF8') for x in arr.tolist()])

def historical_data(data):
    ardate = np.array([x.encode('UTF8') for x in (np.array(data['data'])[:,0][::-1]).tolist()])
    aropen = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,1][::-1]).tolist()])
    arhigh = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,2][::-1]).tolist()])
    arlow  = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,3][::-1]).tolist()])
    arclose= np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,5][::-1]).tolist()])
    arquantity = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,6][::-1]).tolist()])
    return ardate, aropen, arhigh, arlow, arclose, arquantity

def today_data(data):
    ardate = np.array([x.encode('UTF8') for x in (np.array(data['data'])[:,0]).tolist()])
    aropen = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,1]).tolist()])
    arhigh = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,2]).tolist()])
    arlow  = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,3]).tolist()])
    arclose= np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,5]).tolist()])
    arquantity = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,6]).tolist()])
    hs = 0
    date = ardate[hs]
    open = aropen[hs]
    high = arhigh[hs]
    low  = arlow[hs]
    close = arclose[hs]
    quantity = arquantity[hs]
    change = (close - open)*100/open
    return np.array([date]), np.array([open]), np.array([high]), np.array([low]), np.array([close]), np.array([quantity]), change

def today_data_df(df):
    ardate = df['date'].values
    aropen = df['open'].values
    arhigh = df['high'].values
    arlow  = df['low'].values
    arclose= df['close'].values
    arquantity = df['volume'].values
    hs = -1
    date = ardate[hs]
    open = aropen[hs]
    high = arhigh[hs]
    low  = arlow[hs]
    close = arclose[hs]
    quantity = arquantity[hs]
    change = (close - open)*100/open
    return np.array([date]), np.array([open]), np.array([high]), np.array([low]), np.array([close]), np.array([quantity]), change

def overlap_screener(data, todayInputs, tdchange, historicalInputs, hchange):
    technical_indicators = copy.deepcopy(data)
    overlap_studies = technical_indicators['overlap_studies']
    momentum_indicators = technical_indicators['momentum_indicators']
    
    slow = 21
    fast = 50
    while slow < 100:
        SLOWEMA = 'EMA' + str(slow)
        FASTEMA = 'EMA' + str(fast)
        if (overlap_studies[SLOWEMA][0] > overlap_studies[FASTEMA][0]) and (overlap_studies[SLOWEMA][1] < overlap_studies[FASTEMA][1]): 
            technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',CROSSOVER' + str(slow) 
        if (overlap_studies[SLOWEMA][0] < overlap_studies[FASTEMA][0]) and (overlap_studies[SLOWEMA][1] > overlap_studies[FASTEMA][1]): 
            technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',CROSSOVER' + str(slow)
        if slow == 50:
            slow = 100
            fast = 200 
        elif slow == 21:
            slow = 50
            fast = 100 
        elif slow == 9:
            slow = 21
            fast = 50                          
    
    
    today_short_term = "0"
    yesterday_short_term = "0"
    if(overlap_studies['0-EMA6'] > overlap_studies['0-EMA16'] > overlap_studies['0-EMA26'] > overlap_studies['0-MA50']):
        today_short_term = "1"
    if(overlap_studies['0-EMA6'] < overlap_studies['0-EMA16'] < overlap_studies['0-EMA26'] < overlap_studies['0-MA50']):
        today_short_term = "-1"
    if(overlap_studies['1-EMA6'] > overlap_studies['1-EMA16'] > overlap_studies['1-EMA26'] > overlap_studies['1-MA50']):
        yesterday_short_term = "1"
    if(overlap_studies['1-EMA6'] < overlap_studies['1-EMA16'] < overlap_studies['1-EMA26'] < overlap_studies['1-MA50']):
        yesterday_short_term = "-1"
    short_term = yesterday_short_term + today_short_term
    
    today_long_term = "0"
    yesterday_long_term = "0"
    if(overlap_studies['0-MA50'] > overlap_studies['0-MA200']):
        today_long_term = "1"
    if(overlap_studies['0-MA50'] < overlap_studies['0-MA200']):
        today_long_term = "-1"
    if(overlap_studies['1-MA50'] > overlap_studies['1-MA200']):
        today_long_term = "1"
    if(overlap_studies['1-MA50'] < overlap_studies['1-MA200']):
        today_long_term = "-1"
    long_term = yesterday_long_term + today_long_term
    
    consolidation = 0
    EMA5Change = ((float(overlap_studies['0-EMA30'])-float(overlap_studies['5-EMA30']))/float(overlap_studies['5-EMA30']))*100
    EMA10Change = ((float(overlap_studies['0-EMA30'])-float(overlap_studies['10-EMA30']))/float(overlap_studies['10-EMA30']))*100
    
    if((0 < abs(EMA5Change) < 0.5) and (0 < abs(EMA10Change) < 0.5)):
        consolidation = 1
               
    json_data = json.loads(json.dumps(technical_indicators))
    if technical_indicators['BuyIndicators'] != '' and technical_indicators['SellIndicators'] == '':
        #db.buy.overlap.insert_one(json_data) 
        return 'buy', 'O@[' + technical_indicators['BuyIndicators'] + ']', short_term, long_term, consolidation
    elif technical_indicators['SellIndicators'] != '' and technical_indicators['BuyIndicators'] == '':
        #db.sell.overlap.insert_one(json_data)
        return 'sell', 'O@[' + technical_indicators['SellIndicators'] + ']', short_term, long_term, consolidation
    else:
        return '', '', short_term, long_term, consolidation
                       
def pattern_screener(data, todayInputs, tdchange, historicalInputs, hchange):
    technical_indicators = copy.deepcopy(data)
    pattern_recognition = technical_indicators['pattern_recognition']
    #Pattern Indicator    
    if pattern_recognition['CDLMARUBOZU'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',MARUBOZU'
    if pattern_recognition['CDLMARUBOZU'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',MARUBOZU' 
        
    if pattern_recognition['CDLHAMMER'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',HAMMER'
    if pattern_recognition['CDLHANGINGMAN'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',HANGINGMAN'
        
    if pattern_recognition['CDLINVERTEDHAMMER'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',CDLINVERTEDHAMMER'     
    
    if pattern_recognition['CDLSHOOTINGSTAR'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',SHOOTINGSTAR'    
    if pattern_recognition['CDLSHOOTINGSTAR'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',SHOOTINGSTAR'    
    
    if pattern_recognition['CDLBELTHOLD'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',BELTHOLD'
    if pattern_recognition['CDLBELTHOLD'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',BELTHOLD'
          
    if pattern_recognition['CDLBREAKAWAY'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',BREAKAWAY'
    if pattern_recognition['CDLBREAKAWAY'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',BREAKAWAY'  
    
    if pattern_recognition['CDLENGULFING'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',ENGULFING'
    if pattern_recognition['CDLENGULFING'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',ENGULFING'  
        
    if pattern_recognition['CDLHARAMI'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',HARAMI'
    if pattern_recognition['CDLHARAMI'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',HARAMI'
        
    if pattern_recognition['CDLHARAMICROSS'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',HARAMICROSS'
    if pattern_recognition['CDLHARAMICROSS'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',HARAMICROSS'    
        
    if pattern_recognition['CDLCLOSINGMARUBOZU'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',CLOSINGMARUBOZU'
    if pattern_recognition['CDLCLOSINGMARUBOZU'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',CLOSINGMARUBOZU'
        
    if pattern_recognition['CDLCONCEALBABYSWALL'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',CONCEALBABYSWALL'
    if pattern_recognition['CDLCONCEALBABYSWALL'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',CONCEALBABYSWALL'  
        
    if pattern_recognition['CDLCOUNTERATTACK'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',COUNTERATTACK'
    if pattern_recognition['CDLCOUNTERATTACK'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',COUNTERATTACK' 
        
    if pattern_recognition['CDLPIERCING'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',PIERCING'
    if pattern_recognition['CDLPIERCING'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',PIERCING'  
        
    if pattern_recognition['CDLKICKING'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',KICKING'
    if pattern_recognition['CDLKICKING'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',KICKING'
             
    if pattern_recognition['CDLKICKINGBYLENGTH'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',KICKINGBYLENGTH'
    if pattern_recognition['CDLKICKINGBYLENGTH'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',KICKINGBYLENGTH'
        
    if pattern_recognition['CDLMORNINGSTAR'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',MORNINGSTAR'
    if pattern_recognition['CDLEVENINGSTAR'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',EVENINGSTAR'
    
    if pattern_recognition['CDLDOJI'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',DOJI'
    if pattern_recognition['CDLDOJI'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',DOJI'      
         
    if pattern_recognition['CDLDOJISTAR'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',DOJISTAR'
    if pattern_recognition['CDLDOJISTAR'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',DOJISTAR' 
         
    if pattern_recognition['CDLDRAGONFLYDOJI'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',DRAGONFLYDOJI'
    if pattern_recognition['CDLDRAGONFLYDOJI'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',DRAGONFLYDOJI' 
         
    if pattern_recognition['CDLGRAVESTONEDOJI'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',GRAVESTONEDOJI'
    if pattern_recognition['CDLGRAVESTONEDOJI'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',GRAVESTONEDOJI'
         
    if pattern_recognition['CDLLONGLEGGEDDOJI'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',LONGLEGGEDDOJI'
    if pattern_recognition['CDLLONGLEGGEDDOJI'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',LONGLEGGEDDOJI' 
         
    if pattern_recognition['CDLSPINNINGTOP'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',SPINNINGTOP'
    if pattern_recognition['CDLSPINNINGTOP'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',SPINNINGTOP'                 
        
    if pattern_recognition['CDLMORNINGDOJISTAR'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',MORNINGDOJISTAR'
    if pattern_recognition['CDLEVENINGDOJISTAR'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',EVENINGDOJISTAR'
        
    if pattern_recognition['CDLABANDONEDBABY'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',ABANDONEDBABY'
    if pattern_recognition['CDLABANDONEDBABY'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',ABANDONEDBABY'
        
    if pattern_recognition['CDLTRISTAR'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',TRISTAR'
    if pattern_recognition['CDLTRISTAR'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',TRISTAR'
        
    if pattern_recognition['CDL3STARSINSOUTH'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',3STARSINSOUTH' 
        
    if pattern_recognition['CDL3WHITESOLDIERS'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',3WHITESOLDIERS'          
        
    if pattern_recognition['CDL2CROWS'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',2CROWS' 
        
    if pattern_recognition['CDL3BLACKCROWS'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',3BLACKCROWS'                     
    
    if pattern_recognition['CDLDARKCLOUDCOVER'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',DARKCLOUDCOVER'     
        
    if pattern_recognition['CDL3INSIDE'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',3INSIDE'
    if pattern_recognition['CDL3INSIDE'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',3INSIDE'
        
    if pattern_recognition['CDL3LINESTRIKE'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',3LINESTRIKE'
    if pattern_recognition['CDL3LINESTRIKE'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',3LINESTRIKE'  
        
    if pattern_recognition['CDL3OUTSIDE'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',3OUTSIDE'
    if pattern_recognition['CDL3OUTSIDE'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',3OUTSIDE' 

    if pattern_recognition['CDLADVANCEBLOCK'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',ADVANCEBLOCK'
    if pattern_recognition['CDLADVANCEBLOCK'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',ADVANCEBLOCK' 
        
    if pattern_recognition['CDLHIGHWAVE'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',HIGHWAVE'
    if pattern_recognition['CDLHIGHWAVE'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',HIGHWAVE'
         
    if pattern_recognition['CDLHIKKAKE'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',HIKKAKE'
    if pattern_recognition['CDLHIKKAKE'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',HIKKAKE'
         
    if pattern_recognition['CDLHIKKAKEMOD'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',HIKKAKEMOD'
    if pattern_recognition['CDLHIKKAKEMOD'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',HIKKAKEMOD'
         
    if pattern_recognition['CDLHOMINGPIGEON'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',HOMINGPIGEON'
    if pattern_recognition['CDLHOMINGPIGEON'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',HOMINGPIGEON'
         
    if pattern_recognition['CDLIDENTICAL3CROWS'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',IDENTICAL3CROWS'
    if pattern_recognition['CDLIDENTICAL3CROWS'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',IDENTICAL3CROWS'
         
    if pattern_recognition['CDLINNECK'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',INNECK'
    if pattern_recognition['CDLINNECK'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',INNECK'
         
    if pattern_recognition['CDLLONGLINE'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',LONGLINE'
    if pattern_recognition['CDLLONGLINE'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',LONGLINE'
         
    if pattern_recognition['CDLMATCHINGLOW'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',MATCHINGLOW'
    if pattern_recognition['CDLMATCHINGLOW'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',MATCHINGLOW'
         
    if pattern_recognition['CDLMATHOLD'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',MATHOLD'
    if pattern_recognition['CDLMATHOLD'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',MATHOLD' 
         
    if pattern_recognition['CDLONNECK'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',ONNECK'
    if pattern_recognition['CDLONNECK'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',ONNECK'
         
    if pattern_recognition['CDLRICKSHAWMAN'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',RICKSHAWMAN'
    if pattern_recognition['CDLRICKSHAWMAN'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',RICKSHAWMAN'
         
    if pattern_recognition['CDLRISEFALL3METHODS'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',RISEFALL3METHODS'
    if pattern_recognition['CDLRISEFALL3METHODS'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',RISEFALL3METHODS'
         
    if pattern_recognition['CDLSEPARATINGLINES'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',SEPARATINGLINES'
    if pattern_recognition['CDLSEPARATINGLINES'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',SEPARATINGLINES'
         
    if pattern_recognition['CDLSHORTLINE'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',SHORTLINE'
    if pattern_recognition['CDLSHORTLINE'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',SHORTLINE'
         
    if pattern_recognition['CDLSTALLEDPATTERN'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',STALLEDPATTERN'
    if pattern_recognition['CDLSTALLEDPATTERN'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',STALLEDPATTERN'
         
    if pattern_recognition['CDLSTICKSANDWICH'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',STICKSANDWICH'
    if pattern_recognition['CDLSTICKSANDWICH'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',STICKSANDWICH'
         
    if pattern_recognition['CDLTAKURI'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',TAKURI'
    if pattern_recognition['CDLTAKURI'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',TAKURI'
         
    if pattern_recognition['CDLTASUKIGAP'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',TASUKIGAP'
    if pattern_recognition['CDLTASUKIGAP'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',TASUKIGAP'
         
    if pattern_recognition['CDLTHRUSTING'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',THRUSTING'
    if pattern_recognition['CDLTHRUSTING'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',THRUSTING'
         
    if pattern_recognition['CDLUNIQUE3RIVER'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',UNIQUE3RIVER'
    if pattern_recognition['CDLUNIQUE3RIVER'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',UNIQUE3RIVER'
         
    if pattern_recognition['CDLUPSIDEGAP2CROWS'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',UPSIDEGAP2CROWS'
    if pattern_recognition['CDLUPSIDEGAP2CROWS'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',UPSIDEGAP2CROWS'
         
    if pattern_recognition['CDLXSIDEGAP3METHODS'][0] == 100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',XSIDEGAP3METHODS'
    if pattern_recognition['CDLXSIDEGAP3METHODS'][0] == -100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',XSIDEGAP3METHODS'                                                                  
         
#     if pattern_recognition[''][0] == 100:
#         technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ','
#     if pattern_recognition[''][0] == -100:
#         technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ','                                                  
        
    json_data = json.loads(json.dumps(technical_indicators))
    if technical_indicators['BuyIndicators'] != '' and technical_indicators['SellIndicators'] == '':
        #db.buy.pattern.insert_one(json_data)
        return 'buy', 'P@[' + technical_indicators['BuyIndicators'] + ']'
    elif technical_indicators['SellIndicators'] != '' and technical_indicators['BuyIndicators'] == '':
        #db.sell.pattern.insert_one(json_data)  
        return 'sell', 'P@[' + technical_indicators['SellIndicators'] + ']'
    else:
        return '', ''  
 
def volume_screener(data, todayInputs, tdchange, historicalInputs, hchange):
    technical_indicators = copy.deepcopy(data)
    volume_indicators = technical_indicators['volume_indicators']
    #Volume Indicator    
    if volume_indicators['AD'][0] > 0 and volume_indicators['AD'][1] < 0:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',AD'
    if volume_indicators['AD'][0] < 0 and volume_indicators['AD'][1] > 0:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',AD'      
        
    json_data = json.loads(json.dumps(technical_indicators))
    
        
    if technical_indicators['BuyIndicators'] != '' and technical_indicators['SellIndicators'] == '':
        #db.buy.volume.insert_one(json_data)
        if tdchange > 0 and volume_indicators['OBV'][0] > volume_indicators['OBV'][1]:
            technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ':OBV'
        return 'buy', 'V@[' + technical_indicators['BuyIndicators'] + ']'
    elif technical_indicators['SellIndicators'] != '' and technical_indicators['BuyIndicators'] == '':
        #db.sell.volume.insert_one(json_data)
        if tdchange < 0 and volume_indicators['OBV'][0] < volume_indicators['OBV'][1]:
            technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ':OBV'
        return 'sell', 'V@[' + technical_indicators['SellIndicators'] + ']'
    else: 
        return '', ''     

def momentum_screener(data, todayInputs, tdchange, historicalInputs, hchange):
    technical_indicators = copy.deepcopy(data)
    momentum_indicators = technical_indicators['momentum_indicators']
    #Momentum Indicator    
    if tdchange > 0 and momentum_indicators['ADXR'][0] > 20 and momentum_indicators['ADXR'][1] < 20:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',ADXR20'
    if tdchange < 0 and momentum_indicators['ADXR'][0] > 20 and momentum_indicators['ADXR'][1] < 20:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',ADXR20'  
        
    if tdchange > 0 and momentum_indicators['ADXR'][0] > 40 and momentum_indicators['ADXR'][1] < 40:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',ADXR40'
    if tdchange < 0 and momentum_indicators['ADXR'][0] > 40 and momentum_indicators['ADXR'][1] < 40:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',ADXR40'     
        
    if tdchange > 0 and momentum_indicators['APO'][0] > 0 and momentum_indicators['APO'][1] < 0:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',APO'
    if tdchange < 0 and momentum_indicators['APO'][0] < 0 and momentum_indicators['APO'][1] > 0:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',APO' 
        
    if tdchange > 0 and momentum_indicators['AROONUP'][0] > momentum_indicators['AROONDOWN'][0] and momentum_indicators['AROONUP'][1] < momentum_indicators['AROONDOWN'][1]:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',AROON'
    if tdchange < 0 and momentum_indicators['AROONUP'][0] < momentum_indicators['AROONDOWN'][0] and momentum_indicators['AROONUP'][1] > momentum_indicators['AROONDOWN'][1]:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',AROON'  
        
    if momentum_indicators['RSI'][0] < 20:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',RSI'
    if momentum_indicators['RSI'][0] > 80:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',RSI'    
        
    if(momentum_indicators['MACDSIGNAL'][0] > momentum_indicators['MACD'][0]) and (momentum_indicators['MACDSIGNAL'][1] < momentum_indicators['MACD'][1]): 
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',CROSSOVER-MACD' 
    if(momentum_indicators['MACDSIGNAL'][0] < momentum_indicators['MACD'][0]) and (momentum_indicators['MACDSIGNAL'][1] > momentum_indicators['MACD'][1]): 
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',CROSSOVER-MACD' 
        
    if tdchange > 0 and momentum_indicators['CCI'][0] > -100 and momentum_indicators['CCI'][1] < -100:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',CCI'
    if tdchange > 0 and momentum_indicators['CCI'][0] < 100 and momentum_indicators['CCI'][1] > 100:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',CCI'  
        
    if momentum_indicators['CMO'][0] > -50 and momentum_indicators['CMO'][1] < -50:
        technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ',RSI'
    if momentum_indicators['CMO'][0] < 50 and momentum_indicators['CMO'][1] > 50:
        technical_indicators['SellIndicators'] = technical_indicators['SellIndicators'] + ',RSI'                 
        
    json_data = json.loads(json.dumps(technical_indicators))
    if technical_indicators['BuyIndicators'] != '' and technical_indicators['SellIndicators'] == '':
        #db.buy.momentum.insert_one(json_data)
        if tdchange > 0 and momentum_indicators['BOP'][0] > 0:
            technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ':BOP'
        return 'buy', 'M@[' + technical_indicators['BuyIndicators'] + ']'
    elif technical_indicators['SellIndicators'] != '' and technical_indicators['BuyIndicators'] == '':
        #db.sell.momentum.insert_one(json_data)  
        if tdchange > 0 and momentum_indicators['BOP'][0] < 0:
            technical_indicators['BuyIndicators'] = technical_indicators['BuyIndicators'] + ':BOP'
        return 'sell', 'M@[' + technical_indicators['SellIndicators'] + ']' 
    else: 
        return '', ''      

def ta_lib_data(scrip):
    try:
        stored_data = db.technical.find_one({'dataset_code':scrip})
        if(stored_data is not None):
            return stored_data['BuyIndicators'], stored_data['SellIndicators'], stored_data['trend'], stored_data['yearHighChange'], stored_data['yearLowChange']    
        
        data = db.history.find_one({'dataset_code':scrip})
        if(data is None):
            print('Missing or very less Data for ', scrip) 
            return
            
        hsdate, hsopen, hshigh, hslow, hsclose, hsquantity = historical_data(data)   
        tddate, tdopen, tdhigh, tdlow, tdclose, tdquantity, tdchange = today_data(data) 
        
        todayInputs = {
            'open': tdopen,
            'high': tdhigh,
            'low': tdlow,
            'close': tdclose,
            'volume': tdquantity
        }
        
        historicalInputs = {
            'open': hsopen,
            'high': hshigh,
            'low': hslow,
            'close': hsclose,
            'volume': hsquantity
        }
        
        df = pd.DataFrame({
            'date': hsdate,
            'open': hsopen,
            'high': hshigh,
            'low': hslow,
            'close': hsclose,
            'volume': hsquantity
        })
        
        end_date = (datetime.date.today() - datetime.timedelta(days=0)).strftime('%Y-%m-%d')
        start_date = (datetime.date.today() - datetime.timedelta(weeks=52)).strftime('%Y-%m-%d')
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        yearHigh = df['high'].max()
        yearLow = df['low'].min()
        yearHighChange = (hsclose[-1] - yearHigh)*100/yearHigh
        yearLowChange = (hsclose[-1] - yearLow)*100/yearLow
        
        hchange = (hsclose[-2]-hsclose[-10])*100/hsclose[-10]
        change = (hsclose[-1]-hsclose[-2])*100/hsclose[-2]
        pchange = (hsclose[-2]-hsclose[-3])*100/hsclose[-3]
        trend = "NA"
        if change > 1 and pchange > 1:
            trend = "up" 
        elif change < -1 and pchange < -1:
            trend = "down"      
    
        technical_indicators={}
        technical_indicators['dataset_code'] = data['dataset_code']
        technical_indicators['name'] = data['name']
        technical_indicators['end_date'] = data['end_date']
        technical_indicators['column_names'] = data['column_names']
        technical_indicators['data'] = data['data']
        technical_indicators['change'] = change
        technical_indicators['pChange'] = pchange
        technical_indicators['trend'] = trend
        technical_indicators['yearHigh'] = yearHigh
        technical_indicators['yearLow'] = yearLow
        technical_indicators['yearHighChange'] = yearHighChange
        technical_indicators['yearLowChange'] = yearLowChange
        technical_indicators['BuyIndicators'] = ''
        technical_indicators['SellIndicators'] = ''
        technical_indicators['BuyIndicatorsCount'] = 0
        technical_indicators['SellIndicatorsCount'] = 0
        
        momentum_indicators={}
        #Momentum Indicators
        momentum_indicators['ADX'] = ADX(historicalInputs).tolist()[::-1] #Average Directional Movement Index http://www.investopedia.com/terms/a/adx.asp
        momentum_indicators['ADXR'] = ADXR(historicalInputs).tolist()[::-1] #Average Directional Movement Index Rating https://www.scottrade.com/knowledge-center/investment-education/research-analysis/technical-analysis/the-indicators/average-directional-movement-index-rating-adxr.html
        momentum_indicators['APO'] = APO(historicalInputs).tolist()[::-1] #Absolute Price Oscillator https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/apo
        momentum_indicators['AROONDOWN'], momentum_indicators['AROONUP'] = AROON(historicalInputs) #Aroon http://www.investopedia.com/terms/a/aroon.asp
        momentum_indicators['AROONDOWN'] = (momentum_indicators['AROONDOWN']).tolist()[::-1]
        momentum_indicators['AROONUP'] = (momentum_indicators['AROONUP']).tolist()[::-1]
        momentum_indicators['AROONOSC'] = AROONOSC(historicalInputs).tolist()[::-1]
        momentum_indicators['BOP'] = BOP(historicalInputs).tolist()[::-1] #Balance Of Power https://www.marketvolume.com/technicalanalysis/balanceofpower.asp
        momentum_indicators['CCI'] = CCI(historicalInputs).tolist()[::-1] #Commodity Channel Index http://www.investopedia.com/articles/trading/05/041805.asp
        momentum_indicators['CMO'] = CMO(historicalInputs).tolist()[::-1] #Chande Momentum Oscillator https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/cmo
        momentum_indicators['DX'] = DX(historicalInputs).tolist()[::-1] #Directional Movement Index http://www.investopedia.com/terms/d/dmi.asp
        momentum_indicators['MACD'], momentum_indicators['MACDSIGNAL'], momentum_indicators['MACDHIST'] = MACD(historicalInputs)
        momentum_indicators['MACD'] = (momentum_indicators['MACD']).tolist()[::-1] #Moving Average Convergence/Divergence #http://www.investopedia.com/terms/m/macd.asp
        momentum_indicators['MACDSIGNAL'] = (momentum_indicators['MACDSIGNAL']).tolist()[::-1]
        momentum_indicators['MACDHIST'] = (momentum_indicators['MACDHIST']).tolist()[::-1]
        #momentum_indicators['MACDEXT'] = MACDEXT(historicalInputs).tolist()[::-1]
        #momentum_indicators['MACDFIX'] = MACDFIX(historicalInputs).tolist()[::-1]
        momentum_indicators['MFI'] = MFI(historicalInputs).tolist()[::-1]
        momentum_indicators['MINUS_DI'] = MINUS_DI(historicalInputs).tolist()[::-1]
        momentum_indicators['MINUS_DM'] = MINUS_DM(historicalInputs).tolist()[::-1]
        momentum_indicators['MOM'] = MOM(historicalInputs).tolist()[::-1]
        momentum_indicators['PLUS_DI'] = PLUS_DI(historicalInputs).tolist()[::-1]
        momentum_indicators['PLUS_DM'] = PLUS_DM(historicalInputs).tolist()[::-1]
        momentum_indicators['PPO'] = PPO(historicalInputs).tolist()[::-1]
        momentum_indicators['ROC'] = ROC(historicalInputs).tolist()[::-1]
        momentum_indicators['ROCP'] = ROCP(historicalInputs).tolist()[::-1]
        momentum_indicators['ROCR'] = ROCR(historicalInputs).tolist()[::-1]
        momentum_indicators['ROCR100'] = ROCR100(historicalInputs).tolist()[::-1]
        momentum_indicators['RSI'] = RSI(historicalInputs).tolist()[::-1]
        #momentum_indicators['STOCH'] = STOCH(historicalInputs).tolist()[::-1]
        #momentum_indicators['STOCHF'] = STOCHF(historicalInputs).tolist()[::-1]
        #momentum_indicators['STOCHRSI'] = STOCHRSI(historicalInputs).tolist()[::-1]
        momentum_indicators['TRIX'] = TRIX(historicalInputs).tolist()[::-1]
        momentum_indicators['ULTOSC'] = ULTOSC(historicalInputs).tolist()[::-1]
        momentum_indicators['WILLR'] = WILLR(historicalInputs).tolist()[::-1]
        
        
        overlap_studies = {}
        overlap_studies['BBANDSUPPER'], overlap_studies['BBANDSMIDDLE'], overlap_studies['BBANDSLOWER'] = BBANDS(historicalInputs)
        overlap_studies['BBANDSUPPER'] = (overlap_studies['BBANDSUPPER']).tolist()[::-1]
        overlap_studies['BBANDSMIDDLE'] = (overlap_studies['BBANDSMIDDLE']).tolist()[::-1]
        overlap_studies['BBANDSLOWER'] = (overlap_studies['BBANDSLOWER']).tolist()[::-1]
        
#            overlap_studies['DEMA'] = DEMA(historicalInputs).tolist()[::-1]
        overlap_studies['EMA9'] = EMA(historicalInputs, 9).tolist()[::-1]
        overlap_studies['EMA21'] = EMA(historicalInputs, 21).tolist()[::-1]
        overlap_studies['EMA25'] = EMA(historicalInputs, 25).tolist()[::-1]
        overlap_studies['EMA50'] = EMA(historicalInputs, 50).tolist()[::-1]
        overlap_studies['EMA100'] = EMA(historicalInputs, 100).tolist()[::-1]
        overlap_studies['EMA200'] = EMA(historicalInputs, 200).tolist()[::-1]
        overlap_studies['HT_TRENDLINE'] = HT_TRENDLINE(historicalInputs).tolist()[::-1]
        overlap_studies['KAMA'] = KAMA(historicalInputs).tolist()[::-1]
        overlap_studies['MA'] = MA(historicalInputs).tolist()[::-1]
        #overlap_studies['MAMA'] = MAMA(historicalInputs).tolist()[::-1]
        #overlap_studies['MAVP'] = MAVP(historicalInputs).tolist()[::-1]
        overlap_studies['MIDPOINT'] = MIDPOINT(historicalInputs).tolist()[::-1]
        overlap_studies['MIDPRICE'] = MIDPRICE(historicalInputs).tolist()[::-1]
        overlap_studies['SAR'] = SAR(historicalInputs).tolist()[::-1]
        overlap_studies['SAREXT'] = SAREXT(historicalInputs).tolist()[::-1]
        overlap_studies['SMA'] = SMA(historicalInputs).tolist()[::-1]
        overlap_studies['SMA4'] = SMA(historicalInputs, 4).tolist()[::-1]
        overlap_studies['SMA9'] = SMA(historicalInputs, 9).tolist()[::-1]
        overlap_studies['SMA25'] = SMA(historicalInputs, 25).tolist()[::-1]
        overlap_studies['SMA50'] = SMA(historicalInputs, 50).tolist()[::-1]
        overlap_studies['SMA100'] = SMA(historicalInputs, 100).tolist()[::-1]
        overlap_studies['SMA200'] = SMA(historicalInputs, 200).tolist()[::-1]
        changeSMA25 = (hsclose[-1]-overlap_studies['SMA25'])*100/overlap_studies['SMA25']
        changeSMA50 = (hsclose[-1]-overlap_studies['SMA50'])*100/overlap_studies['SMA50']
        changeSMA100 = (hsclose[-1]-overlap_studies['SMA100'])*100/overlap_studies['SMA100']
        changeSMA200 = (hsclose[-1]-overlap_studies['SMA200'])*100/overlap_studies['SMA200']
        overlap_studies['T3'] = T3(historicalInputs).tolist()[::-1]
        overlap_studies['TEMA'] = TEMA(historicalInputs).tolist()[::-1]
        overlap_studies['TRIMA'] = TRIMA(historicalInputs).tolist()[::-1]
        overlap_studies['WMA'] = WMA(historicalInputs).tolist()[::-1]
#             
        pattern_recognition = {}
        pattern_recognition['CDL2CROWS'] = CDL2CROWS(historicalInputs).tolist()[::-1]
        pattern_recognition['CDL3BLACKCROWS'] = CDL3BLACKCROWS(historicalInputs).tolist()[::-1]
        pattern_recognition['CDL3INSIDE'] = CDL3INSIDE(historicalInputs).tolist()[::-1]
        pattern_recognition['CDL3LINESTRIKE'] = CDL3LINESTRIKE(historicalInputs).tolist()[::-1]
        pattern_recognition['CDL3OUTSIDE'] = CDL3OUTSIDE(historicalInputs).tolist()[::-1]
        pattern_recognition['CDL3STARSINSOUTH'] = CDL3STARSINSOUTH(historicalInputs).tolist()[::-1]
        pattern_recognition['CDL3WHITESOLDIERS'] = CDL3WHITESOLDIERS(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLABANDONEDBABY'] = CDLABANDONEDBABY(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLADVANCEBLOCK'] = CDLADVANCEBLOCK(historicalInputs).tolist()[::-1] #Bearish reversal. prior trend Upward. Look for three white candles in an upward price trend. On each candle, price opens within the body of the previous candle. The height of the shadows grow taller on the last two candles.
        pattern_recognition['CDLBELTHOLD'] = CDLBELTHOLD(historicalInputs).tolist()[::-1] # Bearish reversal. prior trend upward. Price opens at the high for the day and closes near the low, forming a tall black candle, often with a small lower shadow.
        pattern_recognition['CDLBREAKAWAY'] = CDLBREAKAWAY(historicalInputs).tolist()[::-1] # Bearish reversal. prior trend upward. Look for 5 candle lines in an upward price trend with the first candle being a tall white one. The second day should be a white candle with a gap between the two bodies, but the shadows can overlap. Day three should have a higher close and the candle can be any color. Day 4 shows a white candle with a higher close. The last day is a tall black candle with a close within the gap between the bodies of the first two candles.
        pattern_recognition['CDLCLOSINGMARUBOZU'] = CDLCLOSINGMARUBOZU(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLCONCEALBABYSWALL'] = CDLCONCEALBABYSWALL(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLCOUNTERATTACK'] = CDLCOUNTERATTACK(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLDARKCLOUDCOVER'] = CDLDARKCLOUDCOVER(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLDOJI'] = CDLDOJI(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLDOJISTAR'] = CDLDOJISTAR(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLDRAGONFLYDOJI'] = CDLDRAGONFLYDOJI(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLENGULFING'] = CDLENGULFING(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLEVENINGDOJISTAR'] = CDLEVENINGDOJISTAR(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLEVENINGSTAR'] = CDLEVENINGSTAR(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLGAPSIDESIDEWHITE'] = CDLGAPSIDESIDEWHITE(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLGRAVESTONEDOJI'] = CDLGRAVESTONEDOJI(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLHAMMER'] = CDLHAMMER(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLHANGINGMAN'] = CDLHANGINGMAN(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLHARAMI'] = CDLHARAMI(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLHARAMICROSS'] = CDLHARAMICROSS(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLHIGHWAVE'] = CDLHIGHWAVE(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLHIKKAKE'] = CDLHIKKAKE(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLHIKKAKEMOD'] = CDLHIKKAKEMOD(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLHOMINGPIGEON'] = CDLHOMINGPIGEON(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLIDENTICAL3CROWS'] = CDLIDENTICAL3CROWS(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLINNECK'] = CDLINNECK(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLINVERTEDHAMMER'] = CDLINVERTEDHAMMER(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLKICKING'] = CDLKICKING(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLKICKINGBYLENGTH'] = CDLKICKINGBYLENGTH(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLLADDERBOTTOM'] = CDLLADDERBOTTOM(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLLONGLEGGEDDOJI'] = CDLLONGLEGGEDDOJI(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLLONGLINE'] = CDLLONGLINE(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLMARUBOZU'] = CDLMARUBOZU(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLMATCHINGLOW'] = CDLMATCHINGLOW(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLMATHOLD'] = CDLMATHOLD(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLMORNINGDOJISTAR'] = CDLMORNINGDOJISTAR(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLMORNINGSTAR'] = CDLMORNINGSTAR(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLONNECK'] = CDLONNECK(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLPIERCING'] = CDLPIERCING(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLRICKSHAWMAN'] = CDLRICKSHAWMAN(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLRISEFALL3METHODS'] = CDLRISEFALL3METHODS(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLSEPARATINGLINES'] = CDLSEPARATINGLINES(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLSHOOTINGSTAR'] = CDLSHOOTINGSTAR(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLSHORTLINE'] = CDLSHORTLINE(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLSPINNINGTOP'] = CDLSPINNINGTOP(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLSTALLEDPATTERN'] = CDLSTALLEDPATTERN(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLSTICKSANDWICH'] = CDLSTICKSANDWICH(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLTAKURI'] = CDLTAKURI(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLTASUKIGAP'] = CDLTASUKIGAP(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLTHRUSTING'] = CDLTHRUSTING(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLTRISTAR'] = CDLTRISTAR(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLUNIQUE3RIVER'] = CDLUNIQUE3RIVER(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLUPSIDEGAP2CROWS'] = CDLUPSIDEGAP2CROWS(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLXSIDEGAP3METHODS'] = CDLXSIDEGAP3METHODS(historicalInputs).tolist()[::-1]
#             
        price_transform = {}
        price_transform['AVGPRICE'] = AVGPRICE(historicalInputs).tolist()[::-1]
        price_transform['MEDPRICE'] = MEDPRICE(historicalInputs).tolist()[::-1]
        price_transform['TYPPRICE'] = TYPPRICE(historicalInputs).tolist()[::-1]
        price_transform['WCLPRICE'] = WCLPRICE(historicalInputs).tolist()[::-1]
#         
        volatility_indicators = {}
#         volatility_indicators['ATR'] = ATR(historicalInputs).tolist()[::-1]
#         volatility_indicators['NATR'] = NATR(historicalInputs).tolist()[::-1]
#         volatility_indicators['TRANGE'] = TRANGE(historicalInputs).tolist()[::-1]
        
        volume_indicators = {}
        volume_indicators['AD'] = AD(historicalInputs).tolist()[::-1]
        volume_indicators['ADOSC'] = ADOSC(historicalInputs).tolist()[::-1]
        volume_indicators['OBV'] = OBV(historicalInputs).tolist()[::-1]
   
        
        technical_indicators['momentum_indicators'] = momentum_indicators 
        technical_indicators['overlap_studies'] = overlap_studies
        technical_indicators['pattern_recognition'] = pattern_recognition
        technical_indicators['price_transform'] = price_transform
        technical_indicators['volatility_indicators'] = volatility_indicators
        technical_indicators['volume_indicators'] = volume_indicators   
        
        all_buy_indicators = ''
        all_sell_indicators = ''
        call, indicators = momentum_screener(technical_indicators, todayInputs, tdchange, historicalInputs, hchange)
        if call == 'buy':
            all_buy_indicators = all_buy_indicators + indicators
        if call == 'sell':  
            all_sell_indicators = all_sell_indicators + indicators  
        
        call, indicators = pattern_screener(technical_indicators, todayInputs, tdchange, historicalInputs, hchange)
        if call == 'buy':
            all_buy_indicators = all_buy_indicators + indicators
        if call == 'sell':  
            all_sell_indicators = all_sell_indicators + indicators 
        
        call, indicators = overlap_screener(technical_indicators, todayInputs, tdchange, historicalInputs, hchange)
        if call == 'buy':
            all_buy_indicators = all_buy_indicators + indicators
        if call == 'sell':  
            all_sell_indicators = all_sell_indicators + indicators
        
        call, indicators = volume_screener(technical_indicators, todayInputs, tdchange, historicalInputs, hchange)
        if call == 'buy':
            all_buy_indicators = all_buy_indicators + indicators
        if call == 'sell':  
            all_sell_indicators = all_sell_indicators + indicators
        
        if all_buy_indicators != '':
            technical_indicators['BuyIndicatorsCount'] = all_buy_indicators.count(',')
            technical_indicators['BuyIndicators'] = all_buy_indicators
        if all_sell_indicators != '':
            technical_indicators['SellIndicatorsCount'] = all_sell_indicators.count(',') 
            technical_indicators['SellIndicators'] = all_sell_indicators   
        
        if technical_indicators['BuyIndicatorsCount'] > 0:
            log.info('%s Buy: %s', data['dataset_code'], technical_indicators['BuyIndicators'])
        if technical_indicators['SellIndicatorsCount'] > 0:
            log.info('%s Sell: %s', data['dataset_code'], technical_indicators['SellIndicators']) 
            
        ws.append([data['dataset_code'], technical_indicators['BuyIndicators'], technical_indicators['SellIndicators']])    
        json_data = json.loads(json.dumps(technical_indicators))
        db.technical.insert_one(json_data) 
        return technical_indicators['BuyIndicators'], technical_indicators['SellIndicators'], technical_indicators['trend'], technical_indicators['yearHighChange'], technical_indicators['yearLowChange']  
            
    except Exception:
        print(Exception)
        pass  

def ta_lib_data_df(scrip, dfp, db_store=False):
    try:
        if db_store:
            technical_indicators = db.technical.find_one({'dataset_code':scrip})
            if(technical_indicators is not None):
                return technical_indicators['BuyIndicators'], technical_indicators['SellIndicators'], technical_indicators['trend'], technical_indicators['changeSMA25'], technical_indicators['changeSMA50'], technical_indicators['changeSMA100'], technical_indicators['changeSMA200'] 
                
        data = db.history.find_one({'dataset_code':scrip})
        if(data is None):
            print('Missing or very less Data for ', scrip) 
            return
        
        df = dfp.tail(1000)
        
        historicalInputs = {
            'open': df['open'].values,
            'high': df['high'].values,
            'low': df['low'].values,
            'close': df['close'].values,
            'volume': df['volume'].values
        }
        
        hsclose = (df['close'].values)    
        tddate, tdopen, tdhigh, tdlow, tdclose, tdquantity, tdchange = today_data_df(df) 
        todayInputs = {
            'open': tdopen,
            'high': tdhigh,
            'low': tdlow,
            'close': tdclose,
            'volume': tdquantity
        }
        
        end_date = parser.parse(tddate.tostring().decode()).strftime('%Y-%m-%d')
        start_date = (parser.parse(end_date) - datetime.timedelta(weeks=52)).strftime('%Y-%m-%d')
        df_time = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        yearHigh = df_time['high'].max()
        yearLow = df_time['low'].min()
        yearHighChange = (hsclose[-1] - yearHigh)*100/yearHigh
        yearLowChange = (hsclose[-1] - yearLow)*100/yearLow
        
        hchange = (hsclose[-2]-hsclose[-10])*100/hsclose[-10]
        change = (hsclose[-1]-hsclose[-2])*100/hsclose[-2]
        pchange = (hsclose[-2]-hsclose[-3])*100/hsclose[-3]
        trend = "NA"
        if change > 1 and pchange > 1:
            trend = "up" 
        elif change < -1 and pchange < -1:
            trend = "down"      
    
        technical_indicators={}
        technical_indicators['dataset_code'] = data['dataset_code']
        technical_indicators['name'] = data['name']
        technical_indicators['end_date'] = data['end_date']
        technical_indicators['column_names'] = data['column_names']
        technical_indicators['data'] = data['data']
        technical_indicators['change'] = change
        technical_indicators['pChange'] = pchange
        technical_indicators['trend'] = trend
        technical_indicators['yearHigh'] = yearHigh
        technical_indicators['yearLow'] = yearLow
        technical_indicators['yearHighChange'] = yearHighChange
        technical_indicators['yearLowChange'] = yearLowChange
        technical_indicators['BuyIndicators'] = ''
        technical_indicators['SellIndicators'] = ''
        technical_indicators['BuyIndicatorsCount'] = 0
        technical_indicators['SellIndicatorsCount'] = 0
        technical_indicators['short_term'] = 0
        technical_indicators['long_term'] = 0
        technical_indicators['consolidation'] = 0
        technical_indicators['changeSMA25'] = 0
        technical_indicators['changeSMA50'] = 0
        technical_indicators['changeSMA100'] = 0
        technical_indicators['changeSMA200'] = 0
        
        momentum_indicators={}
        #Momentum Indicators
        momentum_indicators['ADX'] = ADX(historicalInputs).tolist()[::-1] #Average Directional Movement Index http://www.investopedia.com/terms/a/adx.asp
        momentum_indicators['ADXR'] = ADXR(historicalInputs).tolist()[::-1] #Average Directional Movement Index Rating https://www.scottrade.com/knowledge-center/investment-education/research-analysis/technical-analysis/the-indicators/average-directional-movement-index-rating-adxr.html
        momentum_indicators['APO'] = APO(historicalInputs).tolist()[::-1] #Absolute Price Oscillator https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/apo
        momentum_indicators['AROONDOWN'], momentum_indicators['AROONUP'] = AROON(historicalInputs) #Aroon http://www.investopedia.com/terms/a/aroon.asp
        momentum_indicators['AROONDOWN'] = (momentum_indicators['AROONDOWN']).tolist()[::-1]
        momentum_indicators['AROONUP'] = (momentum_indicators['AROONUP']).tolist()[::-1]
        momentum_indicators['AROONOSC'] = AROONOSC(historicalInputs).tolist()[::-1]
        momentum_indicators['BOP'] = BOP(historicalInputs).tolist()[::-1] #Balance Of Power https://www.marketvolume.com/technicalanalysis/balanceofpower.asp
        momentum_indicators['CCI'] = CCI(historicalInputs).tolist()[::-1] #Commodity Channel Index http://www.investopedia.com/articles/trading/05/041805.asp
        momentum_indicators['CMO'] = CMO(historicalInputs).tolist()[::-1] #Chande Momentum Oscillator https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/cmo
        momentum_indicators['DX'] = DX(historicalInputs).tolist()[::-1] #Directional Movement Index http://www.investopedia.com/terms/d/dmi.asp
        momentum_indicators['MACD'], momentum_indicators['MACDSIGNAL'], momentum_indicators['MACDHIST'] = MACD(historicalInputs)
        momentum_indicators['MACD'] = (momentum_indicators['MACD']).tolist()[::-1] #Moving Average Convergence/Divergence #http://www.investopedia.com/terms/m/macd.asp
        momentum_indicators['MACDSIGNAL'] = (momentum_indicators['MACDSIGNAL']).tolist()[::-1]
        momentum_indicators['MACDHIST'] = (momentum_indicators['MACDHIST']).tolist()[::-1]
        #momentum_indicators['MACDEXT'] = MACDEXT(historicalInputs).tolist()[::-1]
        #momentum_indicators['MACDFIX'] = MACDFIX(historicalInputs).tolist()[::-1]
        momentum_indicators['MFI'] = MFI(historicalInputs).tolist()[::-1]
        momentum_indicators['MINUS_DI'] = MINUS_DI(historicalInputs).tolist()[::-1]
        momentum_indicators['MINUS_DM'] = MINUS_DM(historicalInputs).tolist()[::-1]
        momentum_indicators['MOM'] = MOM(historicalInputs).tolist()[::-1]
        momentum_indicators['PLUS_DI'] = PLUS_DI(historicalInputs).tolist()[::-1]
        momentum_indicators['PLUS_DM'] = PLUS_DM(historicalInputs).tolist()[::-1]
        momentum_indicators['PPO'] = PPO(historicalInputs).tolist()[::-1]
        momentum_indicators['ROC'] = ROC(historicalInputs).tolist()[::-1]
        momentum_indicators['ROCP'] = ROCP(historicalInputs).tolist()[::-1]
        momentum_indicators['ROCR'] = ROCR(historicalInputs).tolist()[::-1]
        momentum_indicators['ROCR100'] = ROCR100(historicalInputs).tolist()[::-1]
        momentum_indicators['RSI'] = RSI(historicalInputs).tolist()[::-1]
        #momentum_indicators['STOCH'] = STOCH(historicalInputs).tolist()[::-1]
        #momentum_indicators['STOCHF'] = STOCHF(historicalInputs).tolist()[::-1]
        #momentum_indicators['STOCHRSI'] = STOCHRSI(historicalInputs).tolist()[::-1]
        momentum_indicators['TRIX'] = TRIX(historicalInputs).tolist()[::-1]
        momentum_indicators['ULTOSC'] = ULTOSC(historicalInputs).tolist()[::-1]
        momentum_indicators['WILLR'] = WILLR(historicalInputs).tolist()[::-1]
        
        
        overlap_studies = {}
        overlap_studies['BBANDSUPPER'], overlap_studies['BBANDSMIDDLE'], overlap_studies['BBANDSLOWER'] = BBANDS(historicalInputs)
        overlap_studies['BBANDSUPPER'] = (overlap_studies['BBANDSUPPER']).tolist()[::-1]
        overlap_studies['BBANDSMIDDLE'] = (overlap_studies['BBANDSMIDDLE']).tolist()[::-1]
        overlap_studies['BBANDSLOWER'] = (overlap_studies['BBANDSLOWER']).tolist()[::-1]
        
        overlap_studies['0-EMA6'] = EMA(historicalInputs, 6).tolist()[::-1][0]
        overlap_studies['0-EMA16'] = EMA(historicalInputs, 16).tolist()[::-1][0]
        overlap_studies['0-EMA26'] = EMA(historicalInputs, 26).tolist()[::-1][0]
        overlap_studies['0-MA50'] = MA(historicalInputs, 50).tolist()[::-1][0]
        overlap_studies['0-MA200'] = MA(historicalInputs, 200).tolist()[::-1][0]
        overlap_studies['1-EMA6'] = EMA(historicalInputs, 6).tolist()[::-1][1]
        overlap_studies['1-EMA16'] = EMA(historicalInputs, 16).tolist()[::-1][1]
        overlap_studies['1-EMA26'] = EMA(historicalInputs, 26).tolist()[::-1][1]
        overlap_studies['1-MA50'] = MA(historicalInputs, 50).tolist()[::-1][1]
        overlap_studies['1-MA200'] = MA(historicalInputs, 200).tolist()[::-1][1]
        overlap_studies['0-EMA30'] = EMA(historicalInputs, 6).tolist()[::-1][0]
        overlap_studies['5-EMA30'] = EMA(historicalInputs, 6).tolist()[::-1][5]
        overlap_studies['10-EMA30'] = EMA(historicalInputs, 6).tolist()[::-1][10]     
        
#       overlap_studies['DEMA'] = DEMA(historicalInputs).tolist()[::-1]
        overlap_studies['EMA6'] = EMA(historicalInputs, 6).tolist()[::-1]
        overlap_studies['EMA9'] = EMA(historicalInputs, 9).tolist()[::-1]
        overlap_studies['EMA14'] = EMA(historicalInputs, 14).tolist()[::-1]
        overlap_studies['EMA21'] = EMA(historicalInputs, 21).tolist()[::-1]
        overlap_studies['EMA25'] = EMA(historicalInputs, 25).tolist()[::-1]
        overlap_studies['EMA50'] = EMA(historicalInputs, 50).tolist()[::-1]
        overlap_studies['EMA100'] = EMA(historicalInputs, 100).tolist()[::-1]
        overlap_studies['EMA200'] = EMA(historicalInputs, 200).tolist()[::-1]
        overlap_studies['HT_TRENDLINE'] = HT_TRENDLINE(historicalInputs).tolist()[::-1]
        overlap_studies['KAMA'] = KAMA(historicalInputs).tolist()[::-1]
        overlap_studies['MA'] = MA(historicalInputs).tolist()[::-1]
        #overlap_studies['MAMA'] = MAMA(historicalInputs).tolist()[::-1]
        #overlap_studies['MAVP'] = MAVP(historicalInputs).tolist()[::-1]
        overlap_studies['MIDPOINT'] = MIDPOINT(historicalInputs).tolist()[::-1]
        overlap_studies['MIDPRICE'] = MIDPRICE(historicalInputs).tolist()[::-1]
        overlap_studies['SAR'] = SAR(historicalInputs).tolist()[::-1]
        overlap_studies['SAREXT'] = SAREXT(historicalInputs).tolist()[::-1]
        overlap_studies['SMA'] = SMA(historicalInputs).tolist()[::-1]
        overlap_studies['SMA4'] = SMA(historicalInputs, 4).tolist()[::-1]
        overlap_studies['SMA9'] = SMA(historicalInputs, 9).tolist()[::-1]
        overlap_studies['SMA25'] = SMA(historicalInputs, 25).tolist()[::-1]
        overlap_studies['SMA50'] = SMA(historicalInputs, 50).tolist()[::-1]
        overlap_studies['SMA100'] = SMA(historicalInputs, 100).tolist()[::-1]
        overlap_studies['SMA200'] = SMA(historicalInputs, 200).tolist()[::-1]
        technical_indicators['changeSMA25'] = (hsclose[-1]-overlap_studies['SMA25'][0])*100/overlap_studies['SMA25'][0]
        technical_indicators['changeSMA50'] = (hsclose[-1]-overlap_studies['SMA50'][0])*100/overlap_studies['SMA50'][0]
        technical_indicators['changeSMA100'] = (hsclose[-1]-overlap_studies['SMA100'][0])*100/overlap_studies['SMA100'][0]
        technical_indicators['changeSMA200'] = (hsclose[-1]-overlap_studies['SMA200'][0])*100/overlap_studies['SMA200'][0]
        overlap_studies['T3'] = T3(historicalInputs).tolist()[::-1]
        overlap_studies['TEMA'] = TEMA(historicalInputs).tolist()[::-1]
        overlap_studies['TRIMA'] = TRIMA(historicalInputs).tolist()[::-1]
        overlap_studies['WMA'] = WMA(historicalInputs).tolist()[::-1]
#             
        pattern_recognition = {}
        pattern_recognition['CDL2CROWS'] = CDL2CROWS(historicalInputs).tolist()[::-1]
        pattern_recognition['CDL3BLACKCROWS'] = CDL3BLACKCROWS(historicalInputs).tolist()[::-1]
        pattern_recognition['CDL3INSIDE'] = CDL3INSIDE(historicalInputs).tolist()[::-1]
        pattern_recognition['CDL3LINESTRIKE'] = CDL3LINESTRIKE(historicalInputs).tolist()[::-1]
        pattern_recognition['CDL3OUTSIDE'] = CDL3OUTSIDE(historicalInputs).tolist()[::-1]
        pattern_recognition['CDL3STARSINSOUTH'] = CDL3STARSINSOUTH(historicalInputs).tolist()[::-1]
        pattern_recognition['CDL3WHITESOLDIERS'] = CDL3WHITESOLDIERS(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLABANDONEDBABY'] = CDLABANDONEDBABY(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLADVANCEBLOCK'] = CDLADVANCEBLOCK(historicalInputs).tolist()[::-1] #Bearish reversal. prior trend Upward. Look for three white candles in an upward price trend. On each candle, price opens within the body of the previous candle. The height of the shadows grow taller on the last two candles.
        pattern_recognition['CDLBELTHOLD'] = CDLBELTHOLD(historicalInputs).tolist()[::-1] # Bearish reversal. prior trend upward. Price opens at the high for the day and closes near the low, forming a tall black candle, often with a small lower shadow.
        pattern_recognition['CDLBREAKAWAY'] = CDLBREAKAWAY(historicalInputs).tolist()[::-1] # Bearish reversal. prior trend upward. Look for 5 candle lines in an upward price trend with the first candle being a tall white one. The second day should be a white candle with a gap between the two bodies, but the shadows can overlap. Day three should have a higher close and the candle can be any color. Day 4 shows a white candle with a higher close. The last day is a tall black candle with a close within the gap between the bodies of the first two candles.
        pattern_recognition['CDLCLOSINGMARUBOZU'] = CDLCLOSINGMARUBOZU(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLCONCEALBABYSWALL'] = CDLCONCEALBABYSWALL(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLCOUNTERATTACK'] = CDLCOUNTERATTACK(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLDARKCLOUDCOVER'] = CDLDARKCLOUDCOVER(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLDOJI'] = CDLDOJI(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLDOJISTAR'] = CDLDOJISTAR(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLDRAGONFLYDOJI'] = CDLDRAGONFLYDOJI(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLENGULFING'] = CDLENGULFING(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLEVENINGDOJISTAR'] = CDLEVENINGDOJISTAR(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLEVENINGSTAR'] = CDLEVENINGSTAR(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLGAPSIDESIDEWHITE'] = CDLGAPSIDESIDEWHITE(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLGRAVESTONEDOJI'] = CDLGRAVESTONEDOJI(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLHAMMER'] = CDLHAMMER(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLHANGINGMAN'] = CDLHANGINGMAN(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLHARAMI'] = CDLHARAMI(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLHARAMICROSS'] = CDLHARAMICROSS(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLHIGHWAVE'] = CDLHIGHWAVE(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLHIKKAKE'] = CDLHIKKAKE(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLHIKKAKEMOD'] = CDLHIKKAKEMOD(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLHOMINGPIGEON'] = CDLHOMINGPIGEON(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLIDENTICAL3CROWS'] = CDLIDENTICAL3CROWS(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLINNECK'] = CDLINNECK(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLINVERTEDHAMMER'] = CDLINVERTEDHAMMER(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLKICKING'] = CDLKICKING(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLKICKINGBYLENGTH'] = CDLKICKINGBYLENGTH(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLLADDERBOTTOM'] = CDLLADDERBOTTOM(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLLONGLEGGEDDOJI'] = CDLLONGLEGGEDDOJI(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLLONGLINE'] = CDLLONGLINE(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLMARUBOZU'] = CDLMARUBOZU(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLMATCHINGLOW'] = CDLMATCHINGLOW(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLMATHOLD'] = CDLMATHOLD(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLMORNINGDOJISTAR'] = CDLMORNINGDOJISTAR(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLMORNINGSTAR'] = CDLMORNINGSTAR(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLONNECK'] = CDLONNECK(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLPIERCING'] = CDLPIERCING(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLRICKSHAWMAN'] = CDLRICKSHAWMAN(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLRISEFALL3METHODS'] = CDLRISEFALL3METHODS(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLSEPARATINGLINES'] = CDLSEPARATINGLINES(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLSHOOTINGSTAR'] = CDLSHOOTINGSTAR(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLSHORTLINE'] = CDLSHORTLINE(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLSPINNINGTOP'] = CDLSPINNINGTOP(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLSTALLEDPATTERN'] = CDLSTALLEDPATTERN(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLSTICKSANDWICH'] = CDLSTICKSANDWICH(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLTAKURI'] = CDLTAKURI(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLTASUKIGAP'] = CDLTASUKIGAP(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLTHRUSTING'] = CDLTHRUSTING(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLTRISTAR'] = CDLTRISTAR(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLUNIQUE3RIVER'] = CDLUNIQUE3RIVER(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLUPSIDEGAP2CROWS'] = CDLUPSIDEGAP2CROWS(historicalInputs).tolist()[::-1]
        pattern_recognition['CDLXSIDEGAP3METHODS'] = CDLXSIDEGAP3METHODS(historicalInputs).tolist()[::-1]
#             
        price_transform = {}
        price_transform['AVGPRICE'] = AVGPRICE(historicalInputs).tolist()[::-1]
        price_transform['MEDPRICE'] = MEDPRICE(historicalInputs).tolist()[::-1]
        price_transform['TYPPRICE'] = TYPPRICE(historicalInputs).tolist()[::-1]
        price_transform['WCLPRICE'] = WCLPRICE(historicalInputs).tolist()[::-1]
#         
        volatility_indicators = {}
#         volatility_indicators['ATR'] = ATR(historicalInputs).tolist()[::-1]
#         volatility_indicators['NATR'] = NATR(historicalInputs).tolist()[::-1]
#         volatility_indicators['TRANGE'] = TRANGE(historicalInputs).tolist()[::-1]
        
        volume_indicators = {}
        volume_indicators['AD'] = AD(historicalInputs).tolist()[::-1]
        volume_indicators['ADOSC'] = ADOSC(historicalInputs).tolist()[::-1]
        volume_indicators['OBV'] = OBV(historicalInputs).tolist()[::-1]
   
        
        technical_indicators['momentum_indicators'] = momentum_indicators 
        technical_indicators['overlap_studies'] = overlap_studies
        technical_indicators['pattern_recognition'] = pattern_recognition
        technical_indicators['price_transform'] = price_transform
        technical_indicators['volatility_indicators'] = volatility_indicators
        technical_indicators['volume_indicators'] = volume_indicators   
        
        all_buy_indicators = ''
        all_sell_indicators = ''
        call, indicators = momentum_screener(technical_indicators, todayInputs, tdchange, historicalInputs, hchange)
        if call == 'buy':
            all_buy_indicators = all_buy_indicators + indicators
        if call == 'sell':  
            all_sell_indicators = all_sell_indicators + indicators  
        
        call, indicators = pattern_screener(technical_indicators, todayInputs, tdchange, historicalInputs, hchange)
        if call == 'buy':
            all_buy_indicators = all_buy_indicators + indicators
        if call == 'sell':  
            all_sell_indicators = all_sell_indicators + indicators 
        
        call, indicators, short_term, long_term, consolidation = overlap_screener(technical_indicators, todayInputs, tdchange, historicalInputs, hchange)
        if call == 'buy':
            all_buy_indicators = all_buy_indicators + indicators
        if call == 'sell':  
            all_sell_indicators = all_sell_indicators + indicators
        
        call, indicators = volume_screener(technical_indicators, todayInputs, tdchange, historicalInputs, hchange)
        if call == 'buy':
            all_buy_indicators = all_buy_indicators + indicators
        if call == 'sell':  
            all_sell_indicators = all_sell_indicators + indicators
        
        if all_buy_indicators != '':
            technical_indicators['BuyIndicatorsCount'] = all_buy_indicators.count(',')
            technical_indicators['BuyIndicators'] = all_buy_indicators
        if all_sell_indicators != '':
            technical_indicators['SellIndicatorsCount'] = all_sell_indicators.count(',') 
            technical_indicators['SellIndicators'] = all_sell_indicators 
        technical_indicators['short_term'] = short_term
        technical_indicators['long_term'] = long_term
        technical_indicators['consolidation'] = consolidation
        
        if technical_indicators['BuyIndicatorsCount'] > 0:
            log.info('%s Buy: %s', data['dataset_code'], technical_indicators['BuyIndicators'])
        if technical_indicators['SellIndicatorsCount'] > 0:
            log.info('%s Sell: %s', data['dataset_code'], technical_indicators['SellIndicators']) 
            
        ws.append([data['dataset_code'], technical_indicators['BuyIndicators'], technical_indicators['SellIndicators']])    
        json_data = json.loads(json.dumps(technical_indicators))
        if db_store: 
            db.technical.insert_one(json_data) 
        return technical_indicators['BuyIndicators'], technical_indicators['SellIndicators'], technical_indicators['trend'], technical_indicators['changeSMA25'], technical_indicators['changeSMA50'], technical_indicators['changeSMA100'], technical_indicators['changeSMA200'] 
            
    except Exception:
        print(Exception)
        pass  
        
def calculateParallel(threads=2, run_type=None, futures=None):
    pool = ThreadPool(threads)
    
    if(run_type == 'broker'):
        count=0
        scrips = []
        with open('../data-import/nselist/ind_broker_buy.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV:
                if (count != 0):
                    scrips.append(row[0])
                count = count + 1
                
            scrips.sort()
            pool.map(ta_lib_data, scrips)
        with open('../data-import/nselist/ind_broker_sell.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV:
                if (count != 0):
                    scrips.append(row[0])
                count = count + 1
                
            scrips.sort()
            pool.map(ta_lib_data, scrips)    
    elif(run_type == 'result'):
        count=0
        scrips = []
        with open('../data-import/nselist/ind_result.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV:
                if (count != 0):
                    scrips.append(row[0])
                count = count + 1
                
            scrips.sort()
            pool.map(ta_lib_data, scrips) 
    elif(run_type == 'result_declared'):
        count=0
        scrips = []
        with open('../data-import/nselist/ind_result_declared.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV:
                if (count != 0):
                    scrips.append(row[0])
                count = count + 1
                
            scrips.sort()
            pool.map(ta_lib_data, scrips)          
    else:
        scrips = []
        for data in db.scrip.find({'futures':futures}):
            scrips.append(data['scrip'])
        scrips.sort()
        pool.map(ta_lib_data, scrips)     
               
if __name__ == "__main__":
    end_date = datetime.date.today().strftime('%d-%m-%Y')
    start_date = (datetime.date.today() - datetime.timedelta(days=30)).strftime('%d-%m-%Y')
    log.info('%s to %s', start_date, end_date)
    calculateParallel(1, sys.argv[1], sys.argv[2])
    
    connection.close() 
    saveReports()   
    
    