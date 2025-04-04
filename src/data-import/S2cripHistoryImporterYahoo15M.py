from urllib.request import urlopen
import yfinance as yf
from datetime import date
import pandas as pd
import json
from bson import json_util
import datetime
import time
import sys
import csv
from pymongo import MongoClient
pd.options.mode.chained_assignment = None  # default='warn'
connection = MongoClient('localhost', 27017)
db = connection.Nsedata

def historical_data(scrip, start_date, end_date):
    stock_fut = get_history(symbol=scrip,
                            start = start_date,
                            end = end_date)
    return stock_fut

def insert_scripdata(scrip, data, futures):
    if(data.empty == False): 
        record = {}
        record['dataset_code'] = scrip
        record['name'] = scrip
        data = data.iloc[::-1]
        temp = data[['Open', 'High', 'Low', 'Close', 'Volume']]
        temp['Date'] = data.index.astype(str)
        df = temp[['Date','Open', 'High', 'Low', 'Close', 'Volume']]
        df = df.round(1)
        record['end_date'] = data.index.astype(str)[0]
        record['data'] = df.values.tolist()
        record['column_names'] = df.columns.tolist()
        record['futures'] = futures
        json_data = json.loads(json.dumps(record, default=json_util.default))
        db.history15m.insert_one(json_data) 
 
if __name__ == "__main__":
    if(sys.argv[1] is None or sys.argv[1] != 'update'):
         db.drop_collection('history15m')
    end_date = (datetime.date.today() + datetime.timedelta(days=1))
    start_date = (datetime.date.today() - datetime.timedelta(days=10))
    print(start_date.strftime('%d-%m-%Y') + ' to ' + end_date.strftime('%d-%m-%Y'))

    for data in db.scrip.find({'futures':sys.argv[2]}):
        futures = data['futures']
        #scrip = data['scrip'].replace('&','').replace('-','_')
        scrip = data['scrip']
        try:
            data = db.history15m.find_one({'dataset_code':scrip})
            if(data is None):
                time.sleep(0.5)
                ticker = yf.Ticker(scrip + '.NS')
                data = ticker.history(start=start_date, end=end_date, interval = "15m")
                #print(data)
                insert_scripdata(scrip, data, futures)
            print(scrip)      
        except:
            time.sleep(2)
            try:
                ticker = yf.Ticker(scrip + '.NS')
                data = ticker.history(start=start_date, end=end_date, interval = "15m")
                insert_scripdata(scrip, data, futures)
                print(scrip)
            except:
                print('historical fail ', scrip)
                pass
            pass

    for data in db.scrip.find({'index':'nifty500'}):
        futures = data['futures']
        #scrip = data['scrip'].replace('&','').replace('-','_')
        scrip = data['scrip']
        try:
            data = db.history15m.find_one({'dataset_code':scrip})
            if(data is None):
                ticker = yf.Ticker(scrip + '.NS')
                data = ticker.history(start=start_date, end=end_date, interval = "15m")
                #print(data)
                insert_scripdata(scrip, data, futures)
            print(scrip)
        except:
            time.sleep(2)
            try:
                ticker = yf.Ticker(scrip + '.NS')
                data = ticker.history(start=start_date, end=end_date, interval = "15m")
                insert_scripdata(scrip, data, futures)
                print(scrip)
            except:
                print('historical fail ', scrip)
                pass
            pass
            
                
connection.close()
print('Done 15MData')