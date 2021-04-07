from selenium import webdriver
from browsermobproxy import Server
from datetime import datetime
from datetime import timedelta
from datetime import date
from pymongo import MongoClient
from subprocess import *
from bson import json_util
import json
import time
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np

connection = MongoClient('localhost', 27017)
db = connection.chartlink

def process_backtest(rawdata, processor, starttime, endtime):
    response_json = json.loads(rawdata)
    aggregatedStockList = response_json["aggregatedStockList"]
    tradeTimes = response_json["metaData"][0]["tradeTimes"]
    df = pd.DataFrame({'aggregatedStockList': aggregatedStockList, 'tradeTimes': tradeTimes})
    df = df[-80:] 
    df.drop(df[df['aggregatedStockList'].str.len().lt(1)].index, inplace=True)
    df.iloc[::-1]
    for ind in df.index: 
        i = 0
        while i < len(df['aggregatedStockList'][ind]):
            epochtime = str(df['tradeTimes'][ind])[0:-3]
            eventtime = time.localtime(int(epochtime))
            systemtime = time.strftime('%Y-%m-%d %H:%M:%S', eventtime)
            eventdateonly = time.strftime('%Y-%m-%d', eventtime)
            eventtimeonly = time.strftime('%H:%M:%S', eventtime)
            currenttime = datetime.strptime(systemtime, '%Y-%m-%d %H:%M:%S')
            reportedtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            scrip = df['aggregatedStockList'][ind][i]
            #print(scrip, systemtime)
            if(i%3 == 0 and eventdateonly == (date.today()).strftime('%Y-%m-%d')
                and currenttime >= starttime and currenttime <= endtime
                ):
                if((db[processor].find_one({'scrip':scrip}) is None)):
                    print(reportedtime, ':', processor, ' : ', scrip, ' : ', systemtime)
                    record = {}
                    record['dataset_code'] = scrip
                    record['scrip'] = scrip
                    record['epochtime'] = epochtime
                    record['eventtime'] = eventtime
                    record['systemtime'] = systemtime
                    json_data = json.loads(json.dumps(record, default=json_util.default))
                    db[processor].insert_one(json_data)
            i += 1
            
def process_url(url, processor, starttime, endtime):
    proxy.new_har("file_name", options={'captureHeaders': False, 'captureContent': True, 'captureBinaryContent': True})
    driver.get(url)
    proxy.wait_for_traffic_to_stop(1, 10)
    for ent in proxy.har['log']['entries']:
      _url = ent['request']['url']
      _response = ent['response']
      if (_url == 'https://chartink.com/backtest/process') and ('text' in ent['response']['content']):
        data = _response['content']['text']
        process_backtest(data, processor, starttime, endtime)
        
if __name__ == "__main__":
    path = 'browsermob/bin/browsermob-proxy' #your path to browsermob-proxy
    server = Server(path)
    server.start()
    proxy = server.create_proxy()
    fireFoxOptions = webdriver.FirefoxOptions()
    fireFoxOptions.set_headless()
    fireFoxProfile  = webdriver.FirefoxProfile('/Users/rohit/Library/Application Support/Firefox/Profiles/p2dahe48.default')
    fireFoxProfile.set_proxy(proxy.selenium_proxy())
    driver = webdriver.Firefox(firefox_profile=fireFoxProfile, firefox_options=fireFoxOptions)
    
    nw = datetime.now()
    hrs = nw.hour;mins = nw.minute;secs = nw.second;
    zero = timedelta(seconds = secs+mins*60+hrs*3600)
    st = nw - zero # this take me to 0 hours. 
    time_09_30 = st + timedelta(seconds=9*3600+25*60) # this gives 9:30 AM
    time_09_40 = st + timedelta(seconds=9*3600+40*60) # this gives 9:40 AM
    time_09_50 = st + timedelta(seconds=9*3600+50*60) # this gives 9:50 AM
    time_10_00 = st + timedelta(seconds=10*3600) # this gives 10:00 AM
    time_10_10 = st + timedelta(seconds=10*3600+10*60) # this gives 10:10 AM
    time_10_15 = st + timedelta(seconds=10*3600+15*60) # this gives 10:15 AM
    time_10_30 = st + timedelta(seconds=10*3600+30*60) # this gives 10:30 AM
    time_11_30 = st + timedelta(seconds=11*3600+30*60) # this gives 11:30 AM
    time_12_00 = st + timedelta(seconds=12*3600) # this gives 12:00 PM
    time_13_30 = st + timedelta(seconds=13*3600+30*60) # this gives 1:30 PM
    time_14_30 = st + timedelta(seconds=14*3600+30*60) # this gives 2:30 PM
    time_15_30 = st + timedelta(seconds=15*3600+30*60)  # this gives 2:30 PM
    while (nw <= time_13_30): 
        
        if(nw>= time_09_30 and nw <= time_10_30):
            process_url('https://chartink.com/screener/copy-sell-final-check-breakdown-first5minutered', 'sell-final-check-breakdown-first5minutered', time_09_30, time_10_30)
            
            process_url('https://chartink.com/screener/sell-check-morning-up-breakdown-01', 'sell-check-morning-up-breakdown-01', time_09_30, time_10_30)
            
                
        if(nw>= time_10_30 and nw <= time_13_30):
            process_url('https://chartink.com/screener/sell-dayconsolidation-breakout-01', 'sell-dayconsolidation-breakout-01', time_10_30, time_13_30)
        
            
        
        time.sleep(200)
        nw = datetime.now()
        
    server.stop()
    driver.quit()
    