from urllib.request import urlopen
import json
import datetime
import time
import sys
import csv
from pymongo import MongoClient
connection = MongoClient('localhost', 27017)
db = connection.Nsedata
API_KEY="hni7BykTJ6oEzMs3pwz_" #guptanikrohit@gmail.com

def insert_scripdata(scrip, scripdata, futures): 
    data = {}
    data['dataset_code'] = scrip
    data['name'] = scripdata['dataset']['name']
    data['end_date'] = scripdata['dataset']['end_date']
    data['column_names'] = scripdata['dataset']['column_names']
    data['data'] = scripdata['dataset']['data']
    data['futures'] = futures
    json_data = json.loads(json.dumps(data))
    db.history.insert_one(json_data) 
 
if __name__ == "__main__":   
    if(sys.argv[1] is None or sys.argv[1] != 'update'):
         db.drop_collection('history')
    end_date = (datetime.date.today() - datetime.timedelta(days=0)).strftime('%d-%m-%Y')
    start_date = (datetime.date.today() - datetime.timedelta(days=4000)).strftime('%d-%m-%Y')
    print(start_date + ' to ' + end_date)
    
    for data in db.scrip.find({'futures':sys.argv[2]}):
        futures = data['futures']
        scrip = data['scrip'].replace('&','').replace('-','_')
        try:
            data = db.history.find_one({'dataset_code':data['scrip']})
            if(data is None):
                scripdata = json.loads(urlopen("https://www.quandl.com/api/v3/datasets/NSE/"+scrip+".json?api_key="+API_KEY+"&start_date="+start_date+"&end_date="+end_date).read().decode())
                insert_scripdata(data['scrip'], scripdata, futures)
            print(scrip)      
        except:
            time.sleep(2)
            try:
                scripdata = json.loads(urlopen("https://www.quandl.com/api/v3/datasets/NSE/"+scrip+".json?api_key="+API_KEY+"&start_date="+start_date+"&end_date="+end_date).read().decode())
                insert_scripdata(data['scrip'], scripdata, futures)
                print(scrip)
            except:
                print('historical fail', str(data['scrip'])) 
                pass                   

    
connection.close()
print('Done Historical')