import urllib2
import json
import datetime
import time
import re
from pymongo import MongoClient
connection = MongoClient('localhost', 27017)
db = connection.NseDataTA
db.drop_collection('history')
    
end_date = (datetime.date.today()).strftime('%d-%m-%Y')
start_date = (datetime.date.today() - datetime.timedelta(days=30)).strftime('%d-%m-%Y')
print start_date + ' to ' + end_date

for data in db.scrip.find():
    scrip = (data['scrip']).encode('UTF8').replace('&','').replace('-','_')
    try:
        scripdata = json.loads(urllib2.urlopen("https://www.quandl.com/api/v3/datasets/NSE/"+scrip+".json?api_key=xMH7BiBu6s24LHCizug3&start_date="+start_date+"&end_date="+end_date).read())
        db.history.insert_one(scripdata)
    except:
        time.sleep(2)
        try:
            scripdata = json.loads(urllib2.urlopen("https://www.quandl.com/api/v3/datasets/NSE/"+scrip+".json?api_key=xMH7BiBu6s24LHCizug3&start_date="+start_date+"&end_date="+end_date).read())
            db.history.insert_one(scripdata)
        except:
            print data['scrip']
            pass


connection.close()