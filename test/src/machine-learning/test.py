import pandas as pd
import quandl
import math
import time
import numpy as np
from pymongo import MongoClient
from talib.abstract import *
from multiprocessing.dummy import Pool as ThreadPool

connection = MongoClient('localhost', 27017)
db = connection.Nsedata

def historical_data(data):
    ardate = np.array([x.encode('UTF8') for x in (np.array(data['data'])[:,0][::-1]).tolist()])
    aropen = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,1][::-1]).tolist()])
    arhigh = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,2][::-1]).tolist()])
    arlow  = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,3][::-1]).tolist()])
    arlast = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,4][::-1]).tolist()])
    arclose= np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,5][::-1]).tolist()])
    arquantity = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,6][::-1]).tolist()])
    arturnover = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,7][::-1]).tolist()])
    return ardate, aropen, arhigh, arlow, arlast, arclose, arquantity, arturnover

def ta_lib_data(scrip):
    data = db.history.find_one({'dataset_code':scrip.encode('UTF8').replace('&','').replace('-','_')})
    if(data is None):
        print  'Missing Data for ',scrip.encode('UTF8'), '\n'
        return
        
    hsdate, hsopen, hshigh, hslow, hslast, hsclose, hsquantity, hsturnover = historical_data(data)   
    df = pd.DataFrame({
        'date': hsdate,
        'open': hsopen,
        'high': hshigh,
        'low': hslow,
        'close': hsclose,
        'volume': hsquantity,
        'turnover':hsturnover
    })
    df = df[['date','open','high','low','close','volume','turnover']]
        
    if (df is not None):
        df.columns = df.columns.str.lower()
        df=df.rename(columns = {'total trade quantity':'volume'})
        df=df.rename(columns = {'turnover (lacs)': 'turnover'})
        df['PCT_change'] = ((df['close'] - df['open'])/df['open'])*100
        
        df['ADX'] = ADX(df) #Average Directional Movement Index http://www.investopedia.com/terms/a/adx.asp
        df['ADXR'] = ADXR(df) #Average Directional Movement Index Rating https://www.scottrade.com/knowledge-center/investment-education/research-analysis/technical-analysis/the-indicators/average-directional-movement-index-rating-adxr.html
        df['APO'] = APO(df) #Absolute Price Oscillator https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/apo
        aroon = AROON(df) #Aroon http://www.investopedia.com/terms/a/aroon.asp
        df['AROONUP'], df['AROONDOWN'] = aroon['aroonup'], aroon['aroondown']
        df['AROONOSC'] = AROONOSC(df)
        df['BOP'] = BOP(df) #Balance Of Power https://www.marketvolume.com/technicalanalysis/balanceofpower.asp
        df['CCI'] = CCI(df) #Commodity Channel Index http://www.investopedia.com/articles/trading/05/041805.asp
        df['CMO'] = CMO(df) #Chande Momentum Oscillator https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/cmo
        df['DX'] = DX(df) #Directional Movement Index http://www.investopedia.com/terms/d/dmi.asp
        macd = MACD(df)
        df['MACD'], df['MACDSIGNAL'], df['MACDHIST'] = macd['macd'], macd['macdsignal'], macd['macdhist']
        #df['MACDEXT'] = MACDEXT(df)
        #df['MACDFIX'] = MACDFIX(df)
        df['MFI'] = MFI(df)
        df['MINUS_DI'] = MINUS_DI(df)
        df['MINUS_DM'] = MINUS_DM(df)
        df['MOM'] = MOM(df)
        df['PLUS_DI'] = PLUS_DI(df)
        df['PLUS_DM'] = PLUS_DM(df)
        df['PPO'] = PPO(df)
        df['ROC'] = ROC(df)
        df['ROCP'] = ROCP(df)
        df['ROCR'] = ROCR(df)
        df['ROCR100'] = ROCR100(df)
        df['RSI'] = RSI(df)
        #df['STOCH'] = STOCH(df)
        #df['STOCHF'] = STOCHF(df)
        #df['STOCHRSI'] = STOCHRSI(df)
        df['TRIX'] = TRIX(df)
        df['ULTOSC'] = ULTOSC(df)
        df['WILLR'] = WILLR(df)
        
        bbands = BBANDS(df)
        df['BBANDSUPPER'], df['BBANDSMIDDLE'], df['BBANDSLOWER'] = bbands['upperband'], bbands['middleband'], bbands['lowerband']
        
#       df['DEMA'] = DEMA(df)
        df['EMA9'] = EMA(df,9)
        df['EMA21'] = EMA(df,21)
        df['EMA25'] = EMA(df,25)
        df['EMA50'] = EMA(df,50)
        df['EMA100'] = EMA(df,100)
        df['EMA200'] = EMA(df,200)
        df['HT_TRENDLINE'] = HT_TRENDLINE(df)
        df['KAMA'] = KAMA(df)
        df['MA'] = MA(df)
        #df['MAMA'] = MAMA(df)
        #df['MAVP'] = MAVP(df)
        df['MIDPOINT'] = MIDPOINT(df)
        df['MIDPRICE'] = MIDPRICE(df)
        df['SAR'] = SAR(df)
        df['SAREXT'] = SAREXT(df)
        df['SMA'] = SMA(df)
        df['SMA9'] = SMA(df, 9)
        df['T3'] = T3(df)
        df['TEMA'] = TEMA(df)
        df['TRIMA'] = TRIMA(df)
        df['WMA'] = WMA(df)


        df['CDL2CROWS'] = CDL2CROWS(df)
        df['CDL3BLACKCROWS'] = CDL3BLACKCROWS(df)
        df['CDL3INSIDE'] = CDL3INSIDE(df)
        df['CDL3LINESTRIKE'] = CDL3LINESTRIKE(df)
        df['CDL3OUTSIDE'] = CDL3OUTSIDE(df)
        df['CDL3STARSINSOUTH'] = CDL3STARSINSOUTH(df)
        df['CDL3WHITESOLDIERS'] = CDL3WHITESOLDIERS(df)
        df['CDLABANDONEDBABY'] = CDLABANDONEDBABY(df)
        df['CDLADVANCEBLOCK'] = CDLADVANCEBLOCK(df) #Bearish reversal. prior trend Upward. Look for three white candles in an upward price trend. On each candle, price opens within the body of the previous candle. The height of the shadows grow taller on the last two candles.
        df['CDLBELTHOLD'] = CDLBELTHOLD(df) # Bearish reversal. prior trend upward. Price opens at the high for the day and closes near the low, forming a tall black candle, often with a small lower shadow.
        df['CDLBREAKAWAY'] = CDLBREAKAWAY(df) # Bearish reversal. prior trend upward. Look for 5 candle lines in an upward price trend with the first candle being a tall white one. The second day should be a white candle with a gap between the two bodies, but the shadows can overlap. Day three should have a higher close and the candle can be any color. Day 4 shows a white candle with a higher close. The last day is a tall black candle with a close within the gap between the bodies of the first two candles.
        df['CDLCLOSINGMARUBOZU'] = CDLCLOSINGMARUBOZU(df)
        df['CDLCONCEALBABYSWALL'] = CDLCONCEALBABYSWALL(df)
        df['CDLCOUNTERATTACK'] = CDLCOUNTERATTACK(df)
        df['CDLDARKCLOUDCOVER'] = CDLDARKCLOUDCOVER(df)
        df['CDLDOJI'] = CDLDOJI(df)
        df['CDLDOJISTAR'] = CDLDOJISTAR(df)
        df['CDLDRAGONFLYDOJI'] = CDLDRAGONFLYDOJI(df)
        df['CDLENGULFING'] = CDLENGULFING(df)
        df['CDLEVENINGDOJISTAR'] = CDLEVENINGDOJISTAR(df)
        df['CDLEVENINGSTAR'] = CDLEVENINGSTAR(df)
        df['CDLGAPSIDESIDEWHITE'] = CDLGAPSIDESIDEWHITE(df)
        df['CDLGRAVESTONEDOJI'] = CDLGRAVESTONEDOJI(df)
        df['CDLHAMMER'] = CDLHAMMER(df)
        df['CDLHANGINGMAN'] = CDLHANGINGMAN(df)
        df['CDLHARAMI'] = CDLHARAMI(df)
        df['CDLHARAMICROSS'] = CDLHARAMICROSS(df)
        df['CDLHIGHWAVE'] = CDLHIGHWAVE(df)
        df['CDLHIKKAKE'] = CDLHIKKAKE(df)
        df['CDLHIKKAKEMOD'] = CDLHIKKAKEMOD(df)
        df['CDLHOMINGPIGEON'] = CDLHOMINGPIGEON(df)
        df['CDLIDENTICAL3CROWS'] = CDLIDENTICAL3CROWS(df)
        df['CDLINNECK'] = CDLINNECK(df)
        df['CDLINVERTEDHAMMER'] = CDLINVERTEDHAMMER(df)
        df['CDLKICKING'] = CDLKICKING(df)
        df['CDLKICKINGBYLENGTH'] = CDLKICKINGBYLENGTH(df)
        df['CDLLADDERBOTTOM'] = CDLLADDERBOTTOM(df)
        df['CDLLONGLEGGEDDOJI'] = CDLLONGLEGGEDDOJI(df)
        df['CDLLONGLINE'] = CDLLONGLINE(df)
        df['CDLMARUBOZU'] = CDLMARUBOZU(df)
        df['CDLMATCHINGLOW'] = CDLMATCHINGLOW(df)
        df['CDLMATHOLD'] = CDLMATHOLD(df)
        df['CDLMORNINGDOJISTAR'] = CDLMORNINGDOJISTAR(df)
        df['CDLMORNINGSTAR'] = CDLMORNINGSTAR(df)
        df['CDLONNECK'] = CDLONNECK(df)
        df['CDLPIERCING'] = CDLPIERCING(df)
        df['CDLRICKSHAWMAN'] = CDLRICKSHAWMAN(df)
        df['CDLRISEFALL3METHODS'] = CDLRISEFALL3METHODS(df)
        df['CDLSEPARATINGLINES'] = CDLSEPARATINGLINES(df)
        df['CDLSHOOTINGSTAR'] = CDLSHOOTINGSTAR(df)
        df['CDLSHORTLINE'] = CDLSHORTLINE(df)
        df['CDLSPINNINGTOP'] = CDLSPINNINGTOP(df)
        df['CDLSTALLEDPATTERN'] = CDLSTALLEDPATTERN(df)
        df['CDLSTICKSANDWICH'] = CDLSTICKSANDWICH(df)
        df['CDLTAKURI'] = CDLTAKURI(df)
        df['CDLTASUKIGAP'] = CDLTASUKIGAP(df)
        df['CDLTHRUSTING'] = CDLTHRUSTING(df)
        df['CDLTRISTAR'] = CDLTRISTAR(df)
        df['CDLUNIQUE3RIVER'] = CDLUNIQUE3RIVER(df)
        df['CDLUPSIDEGAP2CROWS'] = CDLUPSIDEGAP2CROWS(df)
        df['CDLXSIDEGAP3METHODS'] = CDLXSIDEGAP3METHODS(df)

        df['AVGPRICE'] = AVGPRICE(df)
        df['MEDPRICE'] = MEDPRICE(df)
        df['TYPPRICE'] = TYPPRICE(df)
        df['WCLPRICE'] = WCLPRICE(df)

#         df['ATR'] = ATR(df)
#         df['NATR'] = NATR(df)
#         df['TRANGE'] = TRANGE(df)
        
        df['AD'] = AD(df)
        df['ADOSC'] = ADOSC(df)
        df['OBV'] = OBV(df)
        
        df.to_csv('temp/' + scrip + '.csv', encoding='utf-8')
             
def calculateParallel(threads=2):
    pool = ThreadPool(threads)
    
    scrips = []
    for data in db.scrip.find():
        scrips.append((data['scrip']).encode('UTF8').replace('&','').replace('-','_'))
    scrips.sort()
    
    pool.map(ta_lib_data, scrips)
                     
if __name__ == "__main__":
    calculateParallel(1)
    connection.close()


    
        