import urllib2
import json
import datetime
import time
import sys
from pymongo import MongoClient
connection = MongoClient('localhost', 27017)
db = connection.Nsedata

def insert_scripdata(scripdata, futures): 
    data = {}
    data['dataset_code'] = scripdata['dataset']['dataset_code']
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
    print start_date + ' to ' + end_date
    
    for data in db.scrip.find():
        futures = data['futures']
        scrip = (data['scrip']).encode('UTF8').replace('&','').replace('-','_')
        try:
            data = db.history.find_one({'dataset_code':scrip})
            if(data is None):
                scripdata = json.loads(urllib2.urlopen("https://www.quandl.com/api/v3/datasets/NSE/"+scrip+".json?api_key=xMH7BiBu6s24LHCizug3&start_date="+start_date+"&end_date="+end_date).read())
                insert_scripdata(scripdata, futures)
                print scrip      
        except:
            time.sleep(2)
            try:
                scripdata = json.loads(urllib2.urlopen("https://www.quandl.com/api/v3/datasets/NSE/"+scrip+".json?api_key=xMH7BiBu6s24LHCizug3&start_date="+start_date+"&end_date="+end_date).read())
                insert_scripdata(scripdata, futures)
                print scrip
            except:
                print 'historical fail', str(data['scrip'])  
                pass


connection.close()
print 'Done Historical'