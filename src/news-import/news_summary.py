import urllib2
import json
import datetime
import time
import sys, logging
from pymongo import MongoClient

logname = '../../output' + '/news' + time.strftime("%d%m%y-%H%M%S")
logging.basicConfig(filename=logname, filemode='a', stream=sys.stdout, level=logging.INFO)
log = logging.getLogger(__name__)

connection = MongoClient('localhost', 27017)
db = connection.Nsedata
 
if __name__ == "__main__":  
    start_date = (datetime.datetime.now() - datetime.timedelta(hours=0))
    start_date = datetime.datetime(start_date.year, start_date.month, start_date.day, start_date.hour) 
    end_date = (datetime.datetime.now() - datetime.timedelta(hours=17))
    end_date = datetime.datetime(end_date.year, end_date.month, end_date.day, end_date.hour)
    newsDict = {}
    for data in db.news.find():
        newslist = data['news']
        scrip = (data['scrip']).encode('UTF8').replace('&','').replace('-','_')
        
        for news in newslist:
            newstime = news['timestamp']
            newssummary = news['summary']
            newslink = news['link']
            try:
                news_time = datetime.datetime.strptime(newstime, "%H:%M:%S %d-%m-%Y")
                if start_date > news_time > end_date: 
                    if newslink in newsDict:
                        newsDict[newslink]['scrip'] = newsDict[newslink]['scrip'] + ',' + scrip
                    else:
                        newsValue = {}
                        newsValue['newssummary'] = newssummary
                        newsValue['newstime'] = newstime
                        newsValue['scrip'] = scrip
                        newsDict[newslink] = newsValue
                    
                    
            except:
                pass        

connection.close()
for newslink,newsValue in newsDict.iteritems():
    log.info("\n\n###############")
    log.info("%s", newsValue['newssummary'])
    log.info("%s", newslink) 
    log.info("%s", newsValue['scrip'])

    log.info("%s", newsValue['newstime'])
    log.info("---------------------") 
print 'Done News'