from seleniumwire import webdriver
from seleniumwire.webdriver import DesiredCapabilities
from browsermobproxy import Server
from datetime import datetime
from datetime import timedelta
from datetime import date
from pymongo import MongoClient
from bson import json_util
import json
import time
import pandas as pd
import base64

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
capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
capabilities['acceptSslCerts'] = True
capabilities['acceptInsecureCerts'] = True


driver = None

def log_filter(log_):
    return (
        # is an actual response
        log_["method"] == "Network.responseReceived"
        # and json
        and "json" in log_["params"]["response"]["mimeType"]
    )

def process_backtest(rawdata, processor, starttime, endtime, filtered=False):
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
            needToPrint = False
            tempScrip = ''
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
                # industry = ""
                # if(dbnse['scrip'].find_one({'scrip':scrip}) is None):
                #     industry = scrip
                if(dbnse['scrip'].find_one({'scrip':scrip}) is None and scrip != 'Largecap' and scrip != 'Midcap' and scrip != 'Smallcap'):
                    industry = scrip
                    if(needToPrint == True):
                        print(industry)
                        needToPrint = False
                    if((db[industry].find_one({'scrip':tempScrip, 'processor':processor}) is None) and tempScrip != ''):
                        record = {}
                        record['scrip'] = tempScrip
                        record['processor'] = processor
                        record['epochtime'] = epochtime
                        record['eventtime'] = eventtime
                        record['systemtime'] = systemtime
                        json_data = json.loads(json.dumps(record, default=json_util.default))
                        db[industry].insert_one(json_data)
                        tempScrip = ''
                if(dbnse['scrip'].find_one({'scrip':scrip}) is not None
                    and eventdateonly == (date.today()).strftime('%Y-%m-%d')
                    and currenttime >= starttime and currenttime <= endtime
                    ):
                    if((db[processor].find_one({'scrip':scrip}) is None)):
                        mldatahigh = ''
                        mldatalow = ''
                        highVol = ''
                        resultDeclared = ''
                        filtersFlag = False
                        
                        try:
                            data1 = db['morning-volume-bs'].find_one({'scrip':scrip})
                            if(data1 is not None): 
                                highVol = data1['keyIndicator']
                            data2 = db['breakout-morning-volume'].find_one({'scrip':scrip})
                            if(data2 is not None): 
                                highVol = highVol + ':' + data2['keyIndicator']
                            if ('CheckNews' not in processor
                                and data2 is not None
                                and (('buy' in processor and 'buy' in highVol) 
                                     or ('sell' in processor and 'sell' in highVol))
                                ):
                                filtersFlag = True 
                              
                                
                            if((dbnse['highBuy'].find_one({'scrip':scrip}) is not None)):
                                data = dbnse.highBuy.find_one({'scrip':scrip})
                                mldatahigh =  data['filter2'] + '|' + data['filter']
                                if ('buy' in processor
                                    and ('MLlowSell' not in data['ml'])
                                    and ('MLlowSellStrong' not in data['ml'])
                                    and (('MLhighBuy' in data['ml'])
                                         or ('MLhighBuyStrong' in data['ml'])
                                         or ('buy' in mldatahigh)
                                         or ('Buy' in mldatahigh)
                                         )
                                    ):
                                    mldatahigh = data['ml'] + '|' + mldatahigh  + '|' + data['filter3']
                                    if (data['filter3']!= '' and 'CheckNews' not in processor):
                                        filtersFlag = True
                                    if (data['filter']!= ''):
                                        filtersFlag = True
                                    if (data['ml']!=''):
                                        filtersFlag = True
                                    filtersFlag = True
                            if((dbnse['lowSell'].find_one({'scrip':scrip}) is not None)):
                                data = dbnse.lowSell.find_one({'scrip':scrip})
                                mldatalow =  data['filter2'] + '|' + data['filter']
                                if ('sell' in processor 
                                    and ('MLhighBuy' not in data['ml'])
                                    and ('MLhighBuyStrong' not in data['ml'])
                                    and (('MLlowSell' in data['ml'])
                                         or ('MLlowSellStrong' in data['ml'])
                                         or ('sell' in mldatalow)
                                         or ('Sell' in mldatalow)
                                         )
                                    ):
                                    mldatalow = data['ml'] + '|' + mldatalow  + '|' + data['filter3']
                                    if (data['filter3']!= '' and ('CheckNews' not in processor)):
                                        filtersFlag = True
                                    if (data['filter']!= ''):
                                        filtersFlag = True
                                    if (data['ml']!=''):
                                        filtersFlag = True
                                    filtersFlag = True
                            
                            if((dbnse['scrip_result'].find_one({'scrip':scrip}) is not None)):
                                data = dbnse.scrip_result.find_one({'scrip':scrip})
                                resultDeclared = data['resultDeclared'] + ',' + data['result_sentiment']
                                if(resultDeclared != ''):
                                    filtersFlag = True
                                    
                                
                               
                        except: 
                            print('')
                        
                        
                        # if(processor == 'buy-dayconsolidation-breakout-04(11:45-to-1:00)' or processor == 'sell-dayconsolidation-breakout-04(10:00-to-12:00)'):
                        #     if((db['morning-volume-breakout'].find_one({'scrip':scrip}) is None)): 
                        #         print(reportedtime, ':', processor, ' : ', scrip, ' : ', systemtime , ' : ', mldatahigh, ' : ', mldatalow)
                        # else:
                        #     print(reportedtime, ':', processor, ' : ', scrip, ' : ', systemtime , ' : ', mldatahigh, ' : ', mldatalow)

                        if ('buy' in processor
                            and 'Sell-AnyGT2' in mldatahigh
                            and 'Sell-AnyGT2-1.0' not in mldatahigh
                            and 'Sell-AnyGT2-2.0' not in mldatahigh
                            and ('Sell-SUPER-Risky' in mldatahigh
                                or 'Sell-Risky' in mldatahigh
                                or 'Sell-AnyGT2-3.0' not in mldatahigh)
                            ):
                            needToPrint = True
                        elif ('sell' in processor
                            and 'Buy-AnyGT2' in mldatalow
                            and 'Buy-AnyGT2-1.0' not in mldatalow
                            and 'Buy-AnyGT2-2.0' not in mldatalow
                            and ('Buy-SUPER-Risky' in mldatalow
                                 or 'Buy-Risky' in mldatalow
                                 or 'Buy-AnyGT2-3.0' not in mldatalow)
                            ):
                            needToPrint = True
                        elif(filtered == False):
                            print(reportedtime, ':', processor, ' : ', scrip, ' : ', systemtime , ' : ', mldatahigh, ' : ', mldatalow, ' : ', highVol, ' : ', resultDeclared)
                            needToPrint = True
                        elif(filtered == True and filtersFlag == True):
                            print(reportedtime, ':', processor, ' : ', scrip, ' : ', systemtime , ' : ', mldatahigh, ' : ', mldatalow, ' : ', highVol, ' : ', resultDeclared)
                            needToPrint = True
                        
                        tempScrip = scrip
                            
                        record = {}
                        record['dataset_code'] = scrip
                        record['scrip'] = scrip
                        record['epochtime'] = epochtime
                        record['eventtime'] = eventtime
                        record['systemtime'] = systemtime
                        record['resultDeclared'] = resultDeclared
                        json_data = json.loads(json.dumps(record, default=json_util.default))
                        db[processor].insert_one(json_data)
                i += 1
    except KeyError:
        None
    except TypeError:
        None
            
def process_url(url, processor, starttime, endtime, filtered=False):
    try:
        time.sleep(5)
        driver.get(url)
        time.sleep(10)

        logs_raw = driver.get_log("performance")
        logs = [json.loads(lr["message"])["message"] for lr in logs_raw]

        for log in filter(log_filter, logs):
            request_id = log["params"]["requestId"]
            resp_url = log["params"]["response"]["url"]
            if (resp_url == 'https://chartink.com/backtest/process'):
                data = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})['body']
                # print(f"Caught {resp_url}")
                # print(data)
                process_backtest(data, processor, starttime, endtime, filtered)
        # print()
    except Exception as e:
        print('driver failed')

def process_backtest_volBreakout(rawdata, processor, starttime, endtime, keyIndicator=None):
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
            needToPrint = False
            tempScrip = ''
            mlData = ''
            resultDeclared = ''
            while (i < len(df['aggregatedStockList'][ind])):
                scrip = df['aggregatedStockList'][ind][i]
                industry = ""
                if(dbnse['scrip'].find_one({'scrip':scrip}) is None and scrip != 'Largecap' and scrip != 'Midcap' and scrip != 'Smallcap'):
                    if(needToPrint == True):
                        #print(scrip)
                        industry = scrip
                        needToPrint = False
                        if((db[processor].find_one({'scrip':tempScrip}) is None) and tempScrip != ''):
                            record = {}
                            record['scrip'] = tempScrip
                            record['industry'] = industry
                            record['mlData'] = mlData
                            record['epochtime'] = epochtime
                            record['eventtime'] = eventtime
                            record['systemtime'] = systemtime
                            record['processor'] = processor
                            record['keyIndicator'] = keyIndicator
                            record['resultDeclared'] = resultDeclared
                            
                            json_data = json.loads(json.dumps(record, default=json_util.default))
                            db[processor].insert_one(json_data)
                            tempScrip = ''
                            mlData = ''
                            resultDeclared = ''
                if(dbnse['scrip'].find_one({'scrip':scrip}) is not None
                    and db[processor].find_one({'scrip':scrip}) is None
                    and eventdateonly == (date.today()).strftime('%Y-%m-%d')
                    and currenttime >= starttime and currenttime <= endtime
                    ):
                    #print(scrip)
                    mldatahigh = ''
                    mldatalow = ''
                    highVol = ''
                    try: 
                        regressionhigh = dbnse.regressionhigh.find_one({'scrip':scrip})
                        regressionlow = dbnse.regressionlow.find_one({'scrip':scrip})
                        if((dbnse['highBuy'].find_one({'scrip':scrip}) is not None)):
                            data = dbnse.highBuy.find_one({'scrip':scrip})
                            if ('buy' in processor):
                                mldatahigh = data['ml']
                            mldatahigh = mldatahigh + '|' + data['filter2'] + '|' + data['filter']
                            if ('buy' in processor
                                and (regressionhigh['PCT_day_change'] > 1 
                                     or (regressionhigh['PCT_day_change_pre1'] > 1 and abs(regressionhigh['PCT_day_change']) < abs(regressionhigh['PCT_day_change_pre1']))
                                     )
                                ):
                                mldatahigh = mldatahigh + '|' + data['filter3']
                                if(regressionhigh['month3HighChange'] < -5):
                                    mldatahigh = mldatahigh + '|' + 'lastDayUp'
                        if('buy' in processor and regressionhigh['month3LowChange'] < 5):
                            mldatahigh = mldatahigh + '|' + 'month3LowChangeLT5'
                        if((dbnse['lowSell'].find_one({'scrip':scrip}) is not None)):
                            data = dbnse.lowSell.find_one({'scrip':scrip})
                            if ('sell' in processor):
                                mldatalow = data['ml']
                            mldatalow = mldatalow + '|' + data['filter2'] + '|' + data['filter']
                            if ('sell' in processor
                                and (regressionlow['PCT_day_change'] < -1 
                                     or (regressionlow['PCT_day_change_pre1'] < -1 and abs(regressionlow['PCT_day_change']) < abs(regressionlow['PCT_day_change_pre1']))
                                     )
                                ):
                                mldatalow = mldatalow + '|' + data['filter3']
                                if(regressionlow['month3LowChange'] > 5):
                                    mldatalow = mldatalow + '|' + 'lastDayDown'
                        if('sell' in processor and regressionlow['month3HighChange'] > -5):
                            mldatalow = mldatalow + '|' + 'month3HighChangeGT-5'
                            
                        if((dbnse['scrip_result'].find_one({'scrip':scrip}) is not None)):
                            data = dbnse.scrip_result.find_one({'scrip':scrip})
                            resultDeclared = data['resultDeclared'] + ',' + data['result_sentiment']
                    except: 
                        print('')
                        
                    data = db['morning-volume-bs'].find_one({'scrip':scrip})
                    if(data is not None): 
                        #filtersFlag = True
                        highVol = data['keyIndicator']
                    data = db['breakout-morning-volume'].find_one({'scrip':scrip})
                    if(data is not None): 
                        #filtersFlag = True
                        highVol = highVol + ':' + data['keyIndicator']
                    
                    if((dbnse['highBuy'].find_one({'scrip':scrip}) is not None) or (dbnse['lowSell'].find_one({'scrip':scrip}) is not None)):
                        if(processor == 'morning-volume-bs'):
                            needToPrint = True #do-nothing
                        elif(processor == 'breakout-morning-volume'):
                            needToPrint = True #do-nothing
                        else:
                            print(reportedtime, ':', processor, ' : ', scrip, ' : ', systemtime , ' : ', mldatahigh, ' : ', mldatalow, ' : ', highVol, ' : ', resultDeclared)
                        needToPrint = True
                    else:
                        if(processor == 'morning-volume-bs'):
                            needToPrint = True #do-nothing
                        elif(processor == 'breakout-morning-volume'):
                            needToPrint = True #do-nothing
                        else:
                            print(reportedtime, ':', processor, ' : ', scrip, ' : ', systemtime , ' : ', mldatahigh, ' : ', mldatalow, ' : ', highVol, ' : ', resultDeclared)
                        needToPrint = True
                                
                    tempScrip = scrip
                    mlData = mldatahigh + ' : ' + mldatalow
                i = i + 1
                
    except KeyError:
        None
    except TypeError:
        None
            
def process_url_volBreakout(url, processor, starttime, endtime, keyIndicator=None):
    try:
        time.sleep(5)
        driver.get(url)
        time.sleep(10)

        logs_raw = driver.get_log("performance")
        logs = [json.loads(lr["message"])["message"] for lr in logs_raw]

        for log in filter(log_filter, logs):
            request_id = log["params"]["requestId"]
            resp_url = log["params"]["response"]["url"]
            if (resp_url == 'https://chartink.com/backtest/process'):
                data = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})['body']
                # print(f"Caught {resp_url}")
                # print(data)
                process_backtest_volBreakout(data, processor, starttime, endtime, keyIndicator)
        # print()
    except Exception as e:
        print('driver failed')

def regression_ta_data_buy():
    for data in dbnse.scrip.find({'futures':'Yes'}):
        scrip = data['scrip']
        if((dbnse['highBuy'].find_one({'scrip':scrip}) is not None)):
            data = dbnse.highBuy.find_one({'scrip':scrip})
            histData = ' :::: ' + scrip + ' : ' + data['ml'] + '|' + data['filter2'] + '|' + data['filter'] + '|' + data['filter3']
            if(data['ml'] != '' or data['filter'] != '' or data['filter2'] != ''):
                print(histData)
    
def regression_ta_data_sell():
    for data in dbnse.scrip.find({'futures':'Yes'}):
        scrip = data['scrip']
        if((dbnse['lowSell'].find_one({'scrip':scrip}) is not None)):
            data = dbnse.lowSell.find_one({'scrip':scrip})
            histData = ' :::: ' + scrip + ' : ' + data['ml'] + '|' + data['filter2'] + '|' + data['filter'] + '|' + data['filter3']
            if(data['ml'] != '' or data['filter'] != '' or data['filter2'] != ''):
                print(histData)            
