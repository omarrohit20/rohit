import urllib2
import json
import datetime
from pymongo import MongoClient
import numpy as np
import datetime
import talib
import numpy
connection = MongoClient('localhost', 27017)
db = connection.NseDataTA
db.drop_collection('indicators.black_marubozu')
db.drop_collection('indicators.white_marubozu')
db.drop_collection('indicators.short_white_candle')
db.drop_collection('indicators.long_white_candle')
db.drop_collection('indicators.long_black_candle')
db.drop_collection('indicators.short_black_candle')
db.drop_collection('indicators.doji')
db.drop_collection('indicators.highdoji')
db.drop_collection('indicators.lowdoji')
    
end_date = datetime.date.today().strftime('%d-%m-%Y')
start_date = (datetime.date.today() - datetime.timedelta(days=30)).strftime('%d-%m-%Y')
print start_date + ' to ' + end_date

for data in db.history.find():
    try:
        ardate = np.array([x.encode('UTF8') for x in (np.array(data['dataset']['data'])[:,0]).tolist()])
        aropen = np.array([float(x.encode('UTF8')) for x in (np.array(data['dataset']['data'])[:,1]).tolist()])
        arhigh = np.array([float(x.encode('UTF8')) for x in (np.array(data['dataset']['data'])[:,2]).tolist()])
        arlow  = np.array([float(x.encode('UTF8')) for x in (np.array(data['dataset']['data'])[:,3]).tolist()])
        arlast = np.array([float(x.encode('UTF8')) for x in (np.array(data['dataset']['data'])[:,4]).tolist()])
        arclose= np.array([float(x.encode('UTF8')) for x in (np.array(data['dataset']['data'])[:,5]).tolist()])
        arquantity = np.array([float(x.encode('UTF8')) for x in (np.array(data['dataset']['data'])[:,6]).tolist()])
        arturnover = np.array([float(x.encode('UTF8')) for x in (np.array(data['dataset']['data'])[:,7]).tolist()])
        
         
        
        inputs = {
            'open': aropen,
            'high': arhigh,
            'low': arlow,
            'close': arclose,
            'volume': arquantity
        }
        
         
        
        
        from talib.abstract import *

        # uses close prices (default)
        output = SMA(inputs, timeperiod=10)
        
        print data['dataset']['dataset_code'], ' ', CDLMARUBOZU(inputs), '\n'
        print data['dataset']['dataset_code'], ' ', CDLCLOSINGMARUBOZU(inputs), '\n'
        
       
             
    except:
        pass


connection.close()