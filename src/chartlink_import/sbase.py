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
        and "XHR" in log_["params"]["type"]
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
                            data3 = db['breakout2-morning-volume'].find_one({'scrip': scrip})
                            if (data3 is not None):
                                highVol = '****' + highVol

                            if((dbnse['highBuy'].find_one({'scrip':scrip}) is not None)
                                and 'CheckNews' not in processor
                                ):
                                datahigh = dbnse.highBuy.find_one({'scrip':scrip})
                                mldatahigh =  datahigh['filter2'] + '|' + datahigh['filter']
                                mldatahigh = datahigh['ml'] + '|' + mldatahigh
                                if('ReversalYear' in datahigh['filter3'] or 'BreakYear' in datahigh['filter3'] or 'NearYear' in datahigh['filter3']):
                                    mldatahigh = mldatahigh + '|' + datahigh['filter3']
                                if('buy' in processor
                                    and ('buy' in datahigh['filter'] or 'Buy' in datahigh['filter'])
                                    and ('%%' in datahigh['filter']
                                        or "$$" in datahigh['filter']
                                        or 'ConsolidationBreakout' in datahigh['filter']
                                        or '%%HLTF:mayBuyTail-tailGT2-allDayLT0' in datahigh['filter']
                                        or '%%HLTF:mayBuyTail-tailGT2-7,10thDayLT0' in datahigh['filter']
                                        or '$$MayBuy-CheckChart(downTrend-mayReverseLast4DaysDown)' in datahigh['filter']
                                        or 'buyYearHigh-0' in datahigh['filter']
                                        or 'BuyYearLow' in datahigh['filter']
                                        or '%%:buyDownTrend-month3Low' in datahigh['filter']
                                        or 'buyFinal' in datahigh['filter']
                                        or 'buyMorningStar-HighLowerTail' in datahigh['filter']
                                        or 'checkCupUp' in datahigh['filter']
                                        or 'checkBuyConsolidationBreakUp' in datahigh['filter']
                                        or 'buyYear2LowBreakingUp' in datahigh['filter']
                                        )
                                    ):
                                    filtersFlag = True

                            if ((dbnse['lowSell'].find_one({'scrip': scrip}) is not None)
                                and 'CheckNews' not in processor
                                ):
                                datalow = dbnse.lowSell.find_one({'scrip': scrip})
                                mldatalow = datalow['filter2'] + '|' + datalow['filter']
                                mldatalow = datalow['ml'] + '|' + mldatalow
                                if ('ReversalYear' in datalow['filter3'] or 'BreakYear' in datalow['filter3'] or 'NearYear' in datalow['filter3']):
                                    mldatalow = mldatalow + '|' + datalow['filter3']
                                if ('sell' in processor
                                    and ('sell' in datahigh['filter'] or 'Sell' in datahigh['filter'])
                                    and ('%%' in datahigh['filter']
                                        or "$$" in datahigh['filter']
                                        or 'ConsolidationBreakdown' in datahigh['filter']
                                        or '%%HLTF:maySellTail-tailGT2-allDayGT0' in datahigh['filter']
                                        or '%%HLTF:maySellTail-tailGT2-7,10thDayGT0' in datahigh['filter']
                                        or '$$MaySell-CheckChart(downTrend-mayReverseLast4DaysUp)' in datahigh['filter']
                                        or 'sellYearLow' in datahigh['filter']
                                        or 'sellYearHigh' in datahigh['filter']
                                        or 'sellFinal' in datahigh['filter']
                                        or 'sellEveningStar-0' in datahigh['filter']
                                        or 'checkCupDown' in datahigh['filter']
                                        or 'checkSellConsolidationBreakDown' in datahigh['filter']
                                        )
                                    ):
                                    filtersFlag = True

                            if (data1 is not None
                                and data2 is not None
                                and data3 is not None
                                and ('MLhighBuyStrong' in mldatahigh or 'MLlowSellStrong' in mldatalow)
                                and (('buy' in processor and ('buy' in highVol or 'Buy' in highVol))
                                     or ('sell' in processor and ('sell' in highVol or 'Sell' in highVol))
                                    )
                                ):
                                filtersFlag = True

                            if ('CheckNews' not in processor
                                and 'buy' in processor and ('buy' in highVol or 'Buy' in highVol)
                                and data2 is not None
                                and data3 is not None
                                and ('MLhighBuyStrong' in mldatahigh or data1 is not None)
                                ):
                                filtersFlag = True

                            if ('CheckNews' not in processor
                                and 'sell' in processor and ('sell' in highVol or 'Sell' in highVol)
                                and data2 is not None
                                and data3 is not None
                                and ('MLlowSellStrong' in mldatalow or data1 is not None)
                                ):
                                filtersFlag = True
                            
                            if((dbnse['scrip_result'].find_one({'scrip':scrip}) is not None)):
                                data = dbnse.scrip_result.find_one({'scrip':scrip})
                                resultDeclared = data['resultDeclared'] + ',' + data['result_sentiment']
                                if('Today' not in resultDeclared
                                    and 'Yesterday' not in resultDeclared
                                    ):
                                    filtersFlag = True

                            if ('buy' in processor
                                and 'Buy-AnyGT2' in mldatahigh
                                and 'Buy-AnyGT2-1.0' not in mldatahigh
                                and 'Buy-AnyGT2-2.0' not in mldatahigh
                                and 'Sell-AnyGT2-2.0' not in mldatahigh
                                and 'Sell-AnyGT2-3.0' not in mldatahigh
                                ):
                                filtersFlag = True
                            elif ('sell' in processor
                                and 'Sell-AnyGT2' in mldatalow
                                and 'Sell-AnyGT2-1.0' not in mldatahigh
                                and 'Sell-AnyGT2-2.0' not in mldatahigh
                                and 'Buy-AnyGT2-2.0' not in mldatalow
                                and 'Buy-AnyGT2-3.0' not in mldatalow
                                ):
                                filtersFlag = True
                        except: 
                            print('')

                        if (('%%' in mldatahigh and 'buy' in processor) or ('%%' in mldatalow and 'sell' in processor)):
                            print(reportedtime, ':', processor, ' : ', scrip, ' : ', systemtime, ' : ', mldatahigh, ' : ', mldatalow, ' : ', highVol, ' : ', resultDeclared + '  $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                            needToPrint = True
                        elif (filtersFlag == True
                              and 'Today' not in resultDeclared
                              and 'Yesterday' not in resultDeclared
                            ):
                            print(reportedtime, ':', processor, ' : ', scrip, ' : ', systemtime, ' : ', mldatahigh,' : ', mldatalow, ' : ', highVol, ' : ', resultDeclared)
                            needToPrint = True
                        elif(filtered == False
                            and (data1 is not None or data2 is not None or data3 is not None)
                            and 'Today' not in resultDeclared
                            and 'Yesterday' not in resultDeclared
                            ):
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

                        if('buy' in processor and regressionhigh['month3LowChange'] < 5):
                            mldatahigh = mldatahigh + '|' + 'month3LowChangeLT5'
                        if((dbnse['lowSell'].find_one({'scrip':scrip}) is not None)):
                            data = dbnse.lowSell.find_one({'scrip':scrip})
                            if ('sell' in processor):
                                mldatalow = data['ml']
                            mldatalow = mldatalow + '|' + data['filter2'] + '|' + data['filter']

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
                    data = db['breakout2-morning-volume'].find_one({'scrip': scrip})
                    if (data is not None):
                        # filtersFlag = True
                        highVol = '****' + highVol

                    if (processor == 'morning-volume-bs' or processor == 'breakout2-morning-volume'):
                        needToPrint = True  # do-nothing
                    elif (processor == 'breakout-morning-volume'):
                        if(('%%' in mldatahigh and 'buy' in keyIndicator) or ('%%' in mldatalow and 'sell' in keyIndicator)
                            or ('Buy-AnyGT2' in mldatahigh and 'buy' in keyIndicator) or ('Sell-AnyGT2' in mldatahigh and 'sell' in keyIndicator)
                            or ('Yesterday' in resultDeclared or 'Today' in resultDeclared)
                            ):
                            print(reportedtime, ':', processor, ' : ', scrip, ' : ', systemtime, ' : ', mldatahigh, ' : ', mldatalow, ' : ', highVol, ' : ', resultDeclared + '  $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                    else:
                        if (('%%' in mldatahigh and 'buy' in processor) or ('%%' in mldatalow and 'sell' in processor)
                            or ('Buy-AnyGT2' in mldatahigh and 'buy' in processor) or ('Sell-AnyGT2' in mldatahigh and 'sell' in processor)
                            or ('(LT2)' in processor and ('Yesterday' in resultDeclared or 'Today' in resultDeclared))
                            or ('(GT-2)' in processor and ('Yesterday' in resultDeclared or 'Today' in resultDeclared))
                            or (processor == 'morning-volume-breakout-buy' and resultDeclared != '')
                            or (processor == 'morning-volume-breakout-sell' and resultDeclared != '')
                            ):
                            print(reportedtime, ':', processor, ' : ', scrip, ' : ', systemtime, ' : ', mldatahigh, ' : ', mldatalow, ' : ', highVol, ' : ', resultDeclared + '  $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                        elif(any(d['scrip'] == scrip for d in db['morning-volume-breakout-buy'].find().sort('_id').limit(5))
                            or any(d['scrip'] == scrip for d in db['morning-volume-breakout-sell'].find().sort('_id').limit(5))
                            ):
                            print(reportedtime, ':', processor, ' : ', scrip, ' : ', systemtime, ' : ', mldatahigh, ' : ', mldatalow, ' : ', highVol, ' : ', resultDeclared + '  #################################')
                        else:
                            print(reportedtime, ':', processor, ' : ', scrip, ' : ', systemtime, ' : ', mldatahigh, ' : ', mldatalow, ' : ', highVol, ' : ', resultDeclared)

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
            histData = ' %%%% ' + scrip + ' : ' + data['ml'] + '|' + data['filter2'] + '|' + data['filter'] + '|' + data['filter3']
            #if(data['ml'] != '' or data['filter'] != '' or data['filter2'] != ''):
            if(('%%' in histData and 'Super' in histData)
                or 'checkBuyConsolidationBreakout-allPreLT0' in histData
                or '%%:checkBuy:Consolidation' in histData
                ):
                print(histData)
    for data in dbnse.scrip.find({'futures': 'Yes'}):
        scrip = data['scrip']
        if ((dbnse['highBuy'].find_one({'scrip': scrip}) is not None)):
            data = dbnse.highBuy.find_one({'scrip': scrip})
            histData = ' #### ' + scrip + ' : ' + data['ml'] + '|' + data['filter2'] + '|' + data['filter'] + '|' + data['filter3']
            # if(data['ml'] != '' or data['filter'] != '' or data['filter2'] != ''):
            if ("$$" in histData
                or 'ConsolidationBreakout' in histData
                or '%%HLTF:mayBuyTail-tailGT2-allDayLT0' in histData
                or '%%HLTF:mayBuyTail-tailGT2-7,10thDayLT0' in histData
                or '$$MayBuy-CheckChart(downTrend-mayReverseLast4DaysDown)' in histData
                or 'buyYearHigh-0' in histData
                or 'BuyYearLow' in histData
                or '%%:buyDownTrend-month3Low' in histData
                or 'buyFinal' in histData
                or 'buyMorningStar-HighLowerTail' in histData
                or 'sellEveningStar-0' in histData
                or 'checkCupUp' in histData
                or 'checkBuyConsolidationBreakUp' in histData
                or 'buyYear2LowBreakingUp' in histData
                ):
                print(histData)

    
def regression_ta_data_sell():
    for data in dbnse.scrip.find({'futures':'Yes'}):
        scrip = data['scrip']
        if((dbnse['lowSell'].find_one({'scrip':scrip}) is not None)):
            data = dbnse.lowSell.find_one({'scrip':scrip})
            histData = ' %%%% ' + scrip + ' : ' + data['ml'] + '|' + data['filter2'] + '|' + data['filter'] + '|' + data['filter3']
            #if(data['ml'] != '' or data['filter'] != '' or data['filter2'] != ''):
            if (('%%' in histData and 'Super' in histData)
                or 'checkSellConsolidationBreakdown-allPreGT0' in histData
                or '%%:checkBuy:Consolidation' in histData
                ):
                print(histData) 
    for data in dbnse.scrip.find({'futures': 'Yes'}):
        scrip = data['scrip']
        if ((dbnse['lowSell'].find_one({'scrip': scrip}) is not None)):
            data = dbnse.lowSell.find_one({'scrip': scrip})
            histData = ' #### ' + scrip + ' : ' + data['ml'] + '|' + data['filter2'] + '|' + data['filter'] + '|' + data['filter3']
            # if(data['ml'] != '' or data['filter'] != '' or data['filter2'] != ''):
            if ("$$" in histData
                or 'ConsolidationBreakdown' in histData
                or '%%HLTF:maySellTail-tailGT2-allDayGT0' in histData
                or '%%HLTF:maySellTail-tailGT2-7,10thDayGT0' in histData
                or '$$MaySell-CheckChart(downTrend-mayReverseLast4DaysUp)' in histData
                or 'sellYearLow' in histData
                or 'sellYearHigh' in histData
                or '%%:sellUpTrend-month3High' in histData
                or 'sellFinal' in histData
                or 'sellEveningStar-0' in histData
                or 'checkCupDown' in histData
                or 'checkSellConsolidationBreakDown' in histData
                ):
                print(histData)
