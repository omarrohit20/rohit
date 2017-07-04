import urllib2
import json
import datetime
from pymongo import MongoClient
from multiprocessing.dummy import Pool as ThreadPool
connection = MongoClient('localhost', 27017)
db = connection.NseDataTA
db.drop_collection('history')
end_date = (datetime.date.today()).strftime('%d-%m-%Y')
start_date = (datetime.date.today() - datetime.timedelta(days=250)).strftime('%d-%m-%Y')
print start_date + ' to ' + end_date


def dataDownloader(scrip):
    try:
        scripdata = json.loads(urllib2.urlopen("https://www.quandl.com/api/v3/datasets/NSE/"+scrip+".json?api_key=TipsAmiHm6nzXRhoabFs&start_date="+start_date+"&end_date="+end_date).read())
        db.history.insert_one(scripdata)
        #print scripdata
    except:
        try:
            scripdata = json.loads(urllib2.urlopen("https://www.quandl.com/api/v3/datasets/NSE/"+scrip+".json?api_key=TipsAmiHm6nzXRhoabFs&start_date="+start_date+"&end_date="+end_date).read())
            db.history.insert_one(scripdata)
            #print scripdata
        except: 
            print scrip
            pass 
        pass    


# function to be mapped over
def calculateParallel(threads=2):
    pool = ThreadPool(threads)
    
    scrips = []
    for data in db.scrip.find():
        scrips.append((data['scrip']).encode('UTF8').replace('&','').replace('-','_'))
    scrips.sort()
    
    pool.map(dataDownloader, scrips)
    
    
    
    

if __name__ == "__main__":
    calculateParallel(10)
    connection.close()