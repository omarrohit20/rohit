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
    end_date = datetime.datetime.now()
    print(end_date.year)
    stock_fut = get_history(symbol=scrip,
                            start = date(end_date.year, end_date.month, (end_date.day - 10)),
                            end = date(end_date.year, end_date.month, (end_date.day)),
                            futures=True,
                            expiry_date=get_expiry_date(end_date.year, end_date.month))
    return stock_fut

def insert_scripdata(scrip, data):
    if data is not None: 
        record = {}
        record['scrip'] = scrip
        data = data.iloc[::-1]
        df = data[['Number of Contracts', 'Open Interest', 'Change in OI']]
        df['Date'] = data.index.astype(str)
        record['data'] = df.values.tolist()
        record['column_names'] = df.columns.tolist()
        json_data = json.loads(json.dumps(record, default=json_util.default))
        db.historyOpenInterest.insert_one(json_data) 
 
if __name__ == "__main__":   
    for data in db.scrip.find({'futures':'Yes'}):
        futures = data['futures']
        scrip = data['scrip']
        if((db.resultScripFutures.find_one({'scrip':data['scrip']}) is not None) 
           and (db.historyOpenInterest.find_one({'scrip':data['scrip']}) is None)):
            print(scrip)
            data = futures_data(scrip)
            insert_scripdata(scrip, data)
    
connection.close()
print('Done Historical')