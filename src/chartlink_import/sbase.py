from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from selenium import *
from browsermobproxy import Server
from datetime import datetime
from datetime import timedelta
from datetime import date
from pymongo import MongoClient
from bson import json_util
import json
import time
import pandas as pd

pd.options.mode.chained_assignment = None  # default='warn'



global connection, db;
global nw, hrs, zero
global path, proxy, option, capabilities, driver

connection = MongoClient('localhost', 27017)
db = connection.chartlink
dbnse = connection.Nsedata

nw = datetime.now()
hrs = nw.hour;mins = nw.minute;secs = nw.second;
zero = timedelta(seconds = secs+mins*60+hrs*3600)



    

path = './browsermob/bin/browsermob-proxy' #your path to browsermob-proxy

proxy = None

option = webdriver.ChromeOptions()
prefs = {"profile.password_manager_enabled": True}
option.add_experimental_option("prefs", prefs)
option.add_argument('--no-sandbox')
option.add_argument('--disable-gpu')



capabilities = DesiredCapabilities.CHROME.copy()
capabilities['acceptSslCerts'] = True
capabilities['acceptInsecureCerts'] = True

driver = None


def process_backtest(rawdata, processor, starttime, endtime):
    response_json = json.loads(rawdata)
    try:
        aggregatedStockList = response_json["aggregatedStockList"]
        tradeTimes = response_json["metaData"][0]["tradeTimes"]
        df = pd.DataFrame({'aggregatedStockList': aggregatedStockList, 'tradeTimes': tradeTimes})
        #df = df[-80:] 
        df.drop(df[df['aggregatedStockList'].str.len().lt(1)].index, inplace=True)
        df.iloc[::-1]
        for ind in df.index: 
            i = 0
            while (i < len(df['aggregatedStockList'][ind])):
                epochtime = str(df['tradeTimes'][ind])[0:-3]
                eventtime = time.localtime(int(epochtime))
                systemtime = time.strftime('%Y-%m-%d %H:%M:%S', eventtime)
                eventdateonly = time.strftime('%Y-%m-%d', eventtime)
                #eventtimeonly = time.strftime('%H:%M:%S', eventtime)
                currenttime = datetime.strptime(systemtime, '%Y-%m-%d %H:%M:%S')
                reportedtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                scrip = df['aggregatedStockList'][ind][i]
                #print(scrip, systemtime)
                if(i%3 == 0 and eventdateonly == (date.today()).strftime('%Y-%m-%d')
                    and currenttime >= starttime and currenttime <= endtime
                    ):
                    if((db[processor].find_one({'scrip':scrip}) is None)):
                        mldatahigh = ''
                        mldatalow = ''
                        highVol = ''
                        if((dbnse['highBuy'].find_one({'scrip':scrip}) is not None)):
                            data = dbnse.highBuy.find_one({'scrip':scrip})
                            mldatahigh = data['ml'] + '|' + data['filter2'] + '|' + data['filter']
                        if((dbnse['lowSell'].find_one({'scrip':scrip}) is not None)):
                            data = dbnse.lowSell.find_one({'scrip':scrip})
                            mldatalow = data['ml'] + '|' + data['filter2'] + '|' + data['filter']
                        if((db['morning-volume-breakout-buy'].find_one({'scrip':scrip}) is not None)): 
                            highVol = 'morning-volume-breakout-buy'
                        if((db['morning-volume-breakout-sell'].find_one({'scrip':scrip}) is not None)): 
                            highVol = 'morning-volume-breakout-sell'
                        
                        # if(processor == 'buy-dayconsolidation-breakout-04(11:45-to-1:00)' or processor == 'sell-dayconsolidation-breakout-04(10:00-to-12:00)'):
                        #     if((db['morning-volume-breakout'].find_one({'scrip':scrip}) is None)): 
                        #         print(reportedtime, ':', processor, ' : ', scrip, ' : ', systemtime , ' : ', mldatahigh, ' : ', mldatalow)
                        # else:
                        #     print(reportedtime, ':', processor, ' : ', scrip, ' : ', systemtime , ' : ', mldatahigh, ' : ', mldatalow)
                        
                        print(reportedtime, ':', processor, ' : ', scrip, ' : ', systemtime , ' : ', mldatahigh, ' : ', mldatalow, ' : ', highVol)
                        record = {}
                        record['dataset_code'] = scrip
                        record['scrip'] = scrip
                        record['epochtime'] = epochtime
                        record['eventtime'] = eventtime
                        record['systemtime'] = systemtime
                        json_data = json.loads(json.dumps(record, default=json_util.default))
                        db[processor].insert_one(json_data)
                i += 1
    except KeyError:
        None
    except TypeError:
        None
            
def process_url(url, processor, starttime, endtime):
    proxy.new_har("file_name", options={'captureHeaders': False, 'captureContent': True, 'captureBinaryContent': True})
    driver.get(url)
    time.sleep(60)
    #WebDriverWait(driver, 30).until(lambda x: x.find_element_by_id("backtest-chart"))
    proxy.wait_for_traffic_to_stop(1, 30)
    #print(proxy.har)
    for ent in proxy.har['log']['entries']:
        _url = ent['request']['url']
        _response = ent['response']
        #print(_response)
        if (_url == 'https://chartink.com/backtest/process') and ('text' in ent['response']['content']):
            data = _response['content']['text']
            #print(data)
            process_backtest(data, processor, starttime, endtime)

def process_backtest_volBreakout(rawdata, processor, starttime, endtime):
    response_json = json.loads(rawdata)
    try:
        aggregatedStockList = response_json["aggregatedStockList"]
        tradeTimes = response_json["metaData"][0]["tradeTimes"]
        df = pd.DataFrame({'aggregatedStockList': aggregatedStockList, 'tradeTimes': tradeTimes})
        df = df[-1:] 
        df.drop(df[df['aggregatedStockList'].str.len().lt(1)].index, inplace=True)
        df.iloc[::-1]
        
        for ind in df.index: 
            i = 0
            epochtime = str(df['tradeTimes'][ind])[0:-3]
            eventtime = time.localtime(int(epochtime))
            systemtime = time.strftime('%Y-%m-%d %H:%M:%S', eventtime)
            eventdateonly = time.strftime('%Y-%m-%d', eventtime)
            #eventtimeonly = time.strftime('%H:%M:%S', eventtime)
            currenttime = datetime.strptime(systemtime, '%Y-%m-%d %H:%M:%S')
            reportedtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            while (i < len(df['aggregatedStockList'][ind])):
                scrip = df['aggregatedStockList'][ind][i]
                if(i%3 == 0 
                    and db[processor].find_one({'scrip':scrip}) is None
                    and eventdateonly == (date.today()).strftime('%Y-%m-%d')
                    and currenttime >= starttime and currenttime <= endtime
                    ):
                    #print(scrip)
                    mldatahigh = ''
                    mldatalow = ''
                    if((dbnse['highBuy'].find_one({'scrip':scrip}) is not None)):
                        data = dbnse.highBuy.find_one({'scrip':scrip})
                        mldatahigh = data['ml'] + '|' + data['filter2'] + '|' + data['filter'] + '|' + data['filter3']
                    if((dbnse['lowSell'].find_one({'scrip':scrip}) is not None)):
                        data = dbnse.lowSell.find_one({'scrip':scrip})
                        mldatalow = data['ml'] + '|' + data['filter2'] + '|' + data['filter'] + '|' + data['filter3']
                        
                    if((dbnse['highBuy'].find_one({'scrip':scrip}) is not None) or (dbnse['lowSell'].find_one({'scrip':scrip}) is not None)):
                        print(reportedtime, ':', processor, ' : ', scrip, ' : ', systemtime , ' : ', mldatahigh, ' : ', mldatalow)
                        
                    record = {}
                    record['dataset_code'] = scrip
                    record['scrip'] = scrip
                    record['epochtime'] = epochtime
                    record['eventtime'] = eventtime
                    record['systemtime'] = systemtime
                    json_data = json.loads(json.dumps(record, default=json_util.default))
                    db[processor].insert_one(json_data)
                i = i + 1
                
    except KeyError:
        None
    except TypeError:
        None
            
def process_url_volBreakout(url, processor, starttime, endtime):
    proxy.new_har("file_name", options={'captureHeaders': False, 'captureContent': True, 'captureBinaryContent': True})
    driver.get(url)
    time.sleep(10)
    #WebDriverWait(driver, 30).until(lambda x: x.find_element_by_id("backtest-chart"))
    proxy.wait_for_traffic_to_stop(1, 30)
    #print(proxy.har)
    for ent in proxy.har['log']['entries']:
        _url = ent['request']['url']
        _response = ent['response']
        #print(_response)
        if (_url == 'https://chartink.com/backtest/process') and ('text' in ent['response']['content']):
            data = _response['content']['text']
            #print(data)
            process_backtest_volBreakout(data, processor, starttime, endtime)
            
            