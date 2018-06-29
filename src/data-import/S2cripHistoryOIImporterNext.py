from urllib.request import urlopen
from nsepy.derivatives import get_expiry_date
from nsepy import get_history
from datetime import date
import pandas as pd
import json
from bson import json_util
import datetime
import time
import sys
import csv
from pymongo import MongoClient
connection = MongoClient('localhost', 27017)
db = connection.Nsedata

def futures_data(scrip):
    stock_fut = get_history(symbol=scrip,
                            start = datetime.date.today() - datetime.timedelta(days=7),
                            end = datetime.date.today(),
                            futures=True,
                            expiry_date=get_expiry_date(datetime.date.today().year, datetime.date.today().month + 1))
    return stock_fut

def insert_scripdata(scrip, data):
    if data is not None: 
        record = {}
        record['scrip'] = scrip
        data = data.iloc[::-1]
        df = data[['Number of Contracts', 'Open Interest', 'Change in OI']]
        df['Date'] = data.index.astype(str)
        df['Number of Contracts Pre'] = df['Number of Contracts'].shift(-1)
        df['Open Interest Pre'] = df['Open Interest'].shift(-1)
        df['OI_PCT_change'] = (((df['Open Interest'] - df['Open Interest Pre'])/df['Open Interest Pre'])*100)
        df['Contracts_PCT_change'] = (((df['Number of Contracts'] - df['Number of Contracts Pre'])/df['Number of Contracts Pre'])*100)
        record['data'] = df.values.tolist()
        record['column_names'] = df.columns.tolist()
        json_data = json.loads(json.dumps(record, default=json_util.default))
        db.historyOpenInterestNext.insert_one(json_data) 
 
if __name__ == "__main__":
    if(sys.argv[1] is None or sys.argv[1] != 'update'):
         db.drop_collection('historyOpenInterestNext')   
    for data in db.scrip.find({'futures':'Yes'}):
        futures = data['futures']
        scrip = data['scrip']
        if(
            #(db.resultScripFutures.find_one({'scrip':data['scrip']}) is not None) 
            (db.historyOpenInterestNext.find_one({'scrip':data['scrip']}) is None)
           ):
            print(scrip)
            data = futures_data(scrip)
            insert_scripdata(scrip, data)
    
connection.close()
print('Done Historical')