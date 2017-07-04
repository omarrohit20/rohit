import datetime
from pymongo import MongoClient
import numpy as np
from talib.abstract import *
connection = MongoClient('localhost', 27017)
db = connection.Nsedata

def numpy_conversion(arr):
    return np.array([x.encode('UTF8') for x in arr.tolist()])

def historical_data(data, todaydata):
    ardate = np.array([x.encode('UTF8') for x in (np.array(data['data'])[:,0]).tolist()])
    aropen = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,1]).tolist()])
    arhigh = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,2]).tolist()])
    arlow  = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,3]).tolist()])
    arlast = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,4]).tolist()])
    arclose= np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,5]).tolist()])
    arquantity = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,6]).tolist()])
    arturnover = np.array([float(x.encode('UTF8')) for x in (np.array(data['data'])[:,7]).tolist()])
    
    date = str(todaydata['secDate'])
    open = float(todaydata['open'])
    high = float(todaydata['dayHigh'])
    low  = float(todaydata['dayLow'])
    last = float(todaydata['lastPrice'])
    close = todaydata['closePrice']
    if (close == 'None' or close == None):
        close = last
    close = float(close)    
    quantity = float(todaydata['quantityTraded'])
    turnover = float(todaydata['totalTradedValue'])
    
    return np.insert(ardate, 0, date), np.insert(aropen, 0, open), np.insert(arhigh, 0, high), np.insert(arlow, 0, low), np.insert(arlast, 0, last), np.insert(arclose, 0, close), np.insert(arquantity, 0, quantity), np.insert(arturnover, 0, turnover)

def today_data(todaydata):
    date = str(todaydata['secDate'])
    open = float(todaydata['open'])
    high = float(todaydata['dayHigh'])
    low  = float(todaydata['dayLow'])
    last = float(todaydata['lastPrice'])
    close = todaydata['closePrice']
    if (close == 'None' or close == None):
        close = last
    close = float(close)    
    quantity = float(todaydata['quantityTraded'])
    turnover = float(todaydata['totalTradedValue'])
    return np.array([date]), np.array([open]), np.array([high]), np.array([low]), np.array([last]), np.array([close]), np.array([quantity]), np.array([turnover])

if __name__ == "__main__":
    end_date = datetime.date.today().strftime('%d-%m-%Y')
    start_date = (datetime.date.today() - datetime.timedelta(days=30)).strftime('%d-%m-%Y')
    print start_date + ' to ' + end_date
    
    for symbol in db.scrip.find():
        try:
            
            data = db.history.find_one({'dataset_code':(symbol['scrip']).encode('UTF8').replace('&','').replace('-','_')})
            todaydata = db.fundamental.find_one({'symbol':(symbol['scrip']).encode('UTF8')})
            
            if(todaydata is None or data is None):
                continue
                print  'Missing Data for ',(symbol['scrip']).encode('UTF8'), '\n' 
                
              
            hsdate, hsopen, hshigh, hslow, hslast, hsclose, hsquantity, hsturnover = historical_data(data, todaydata)   
            tddate, tdopen, tdhigh, tdlow, tdlast, tdclose, tdquantity, tdturnover = today_data(todaydata) 
            
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
        
        
            print data['dataset']['dataset_code'], ' CDLMARUBOZU:', CDLMARUBOZU(todayInputs), ' CDLCLOSINGMARUBOZU:', CDLCLOSINGMARUBOZU(todayInputs), ' CDLDOJI:', CDLDOJI(todayInputs), ' CDLHAMMER:', CDLHAMMER(todayInputs), ' CDLHANGINGMAN:', CDLHANGINGMAN(todayInputs), '\n'
            
              

                 
            
            
                       
                 
        except:
            pass
    
    
    connection.close()