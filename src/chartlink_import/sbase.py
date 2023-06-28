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
            tobuy = ''
            tosell = ''
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
                        record['tobuy'] = tobuy
                        record['tosell'] = tosell
                        json_data = json.loads(json.dumps(record, default=json_util.default))
                        db[industry].insert_one(json_data)
                        tempScrip = ''
                        tobuy = ''
                        tosell = ''
                if(dbnse['scrip'].find_one({'scrip':scrip}) is not None
                    and eventdateonly == (date.today()).strftime('%Y-%m-%d')
                    and currenttime >= starttime and currenttime <= endtime
                    ):
                    if((db[processor].find_one({'scrip':scrip}) is None)):
                        mldatahigh = ''
                        mldatalow = ''
                        highVol = ''
                        resultDeclared = ''
                        intradaytech = ''
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
                                intradaytech = datahigh['intradaytech']
                                mldatahigh =  datahigh['filter2'] + '|' + datahigh['filter']
                                mldatahigh = datahigh['ml'] + ':' + datahigh['intradaytech'] + '|' + mldatahigh
                                if('ReversalYear' in datahigh['filter3'] or 'BreakYear' in datahigh['filter3'] or 'NearYear' in datahigh['filter3']):
                                    mldatahigh = mldatahigh + '|' + datahigh['filter3']
                                if('buy' in processor
                                    and ('buy' in datahigh['filter'] or 'Buy' in datahigh['filter'])
                                    and ('%%' in datahigh['filter']
                                        or "$$" in datahigh['filter']
                                        #or 'ConsolidationBreakout' in datahigh['filter']
                                        or '%%HLTF:mayBuyTail-tailGT2-allDayLT0' in datahigh['filter']
                                        or '%%HLTF:mayBuyTail-tailGT2-7,10thDayLT0' in datahigh['filter']
                                        or '$$MayBuy-CheckChart(downTrend-mayReverseLast4DaysDown)' in datahigh[
                                         'filter']
                                        or 'buyYearHigh-0' in datahigh['filter']
                                        #or 'BuyYearLow' in datahigh['filter']
                                        or '%%:buyDownTrend-month3Low' in datahigh['filter']
                                        or 'buyFinal' in datahigh['filter']
                                        or 'buyMorningStar-HighLowerTail' in datahigh['filter']
                                        or 'checkCupUp' in datahigh['filter']
                                        #or 'checkBuyConsolidationBreakUp' in datahigh['filter']
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
                                    mldatalow = mldatalow + ':' + datalow['intradaytech'] + '|' + datalow['filter3']
                                if ('sell' in processor
                                    and ('sell' in datalow['filter'] or 'Sell' in datalow['filter'])
                                    and ('%%' in datalow['filter']
                                         or "$$" in datalow['filter']
                                         #or 'ConsolidationBreakdown' in datahigh['filter']
                                         or '%%HLTF:maySellTail-tailGT2-allDayGT0' in datalow['filter']
                                         or '%%HLTF:maySellTail-tailGT2-7,10thDayGT0' in datalow['filter']
                                         or '$$MaySell-CheckChart(downTrend-mayReverseLast4DaysUp)' in datalow[
                                             'filter']
                                         or 'sellYearLow' in datalow['filter']
                                         #or 'sellYearHigh' in datahigh['filter']
                                         or 'sellFinal' in datalow['filter']
                                         or 'sellEveningStar-0' in datalow['filter']
                                         or 'checkCupDown' in datalow['filter']
                                         #or 'checkSellConsolidationBreakDown' in datalow['filter']
                                        )
                                    ):
                                    filtersFlag = True

                            if (data1 is not None
                                and data2 is not None
                                and data3 is not None
                                and ('MLhighBuyStrong' in mldatahigh or 'MLlowSellStrong' in mldatalow or intradaytech != "")
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
                                and 'Sell-AnyGT2-2.0' not in mldatahigh
                                and 'Sell-AnyGT2-3.0' not in mldatahigh
                                ):
                                filtersFlag = True
                            elif ('sell' in processor
                                and 'Sell-AnyGT2' in mldatalow
                                and 'Sell-AnyGT2-1.0' not in mldatalow
                                and 'Buy-AnyGT2-2.0' not in mldatalow
                                and 'Buy-AnyGT2-3.0' not in mldatalow
                                ):
                                filtersFlag = True

                            regressionhigh = dbnse.highBuy.find_one({'scrip': scrip})
                            regressionlow = dbnse.lowSell.find_one({'scrip': scrip})
                            if ('buy' in processor or 'Buy' in processor or 'breakout2-morning-volume' in processor or 'morning-volume-bs' in processor):
                                if (regressionhigh['month3LowChange'] < 5):
                                    if (regressionhigh['month3LowChange'] == regressionhigh['weekLowChange']):
                                        mldatahigh = mldatahigh + '|' + '0-month3LowChangeLT5-shortuptrend'
                                    elif ((regressionhigh['monthLowChange'] + regressionhigh['weekHighChange'] + regressionhigh['weekLowChange']) < 4.5):
                                        mldatahigh = mldatahigh + '|' + '1-month3LowChangeLT5-shortdowntrend'
                                    else:
                                        mldatahigh = mldatahigh + '|' + 'month3LowChangeLT5-indexhigh'
                                elif (regressionlow['month3HighChange'] > -5):
                                    if (regressionhigh['monthHighChange'] == regressionhigh['weekHighChange']
                                        and (regressionhigh['PCT_day_change_pre1'] < 0 or regressionhigh['PCT_day_change_pre2'] < 0)
                                        ):
                                        mldatahigh = mldatahigh + '|' + 'sell-m3HGT-5-shortdowntrend'
                                    elif ((regressionhigh['monthHighChange'] + regressionhigh['weekHighChange'] +
                                        regressionhigh['weekLowChange']) > -4.5
                                        and (regressionhigh['PCT_day_change_pre1'] > 0 or regressionhigh['PCT_day_change_pre2'] > 0)
                                        and regressionhigh['yearLowChange'] > 10
                                        and (regressionhigh['year2HighChange'] < -5 or regressionhigh['year2HighChange'] < -5 or regressionhigh['PCT_day_change_pre1'] < -1)
                                        ):
                                        mldatahigh = mldatahigh + '|' + 'buy-m3HGT-5-shortuptrend'
                                        if ('MLhighBuyStrong' in mldatahigh or data1 is not None):
                                            filtersFlag = True
                                if ('shortUpTrend' in regressionhigh['filter1'] and '(upTrend)' in regressionhigh['series_trend']
                                    and abs(regressionhigh['month3LowChange']) < abs(regressionhigh['month3HighChange'])
                                    ):
                                    mldatahigh = mldatahigh + '|' + 'shortUpTrend'
                                    filtersFlag = True

                                if (regressionhigh['PCT_day_change'] < 1 or regressionhigh['PCT_day_change_pre1'] < 1
                                    or 2*abs(regressionhigh['PCT_day_change']) < abs(regressionhigh['PCT_day_change_pre1'])
                                    ):
                                    tobuy = 'buyrecommended'

                            if ('sell' in processor or 'Sell' in processor or 'breakout2-morning-volume' in processor or 'morning-volume-bs' in processor):
                                if (regressionlow['month3HighChange'] > -5):
                                    if (regressionlow['monthHighChange'] == regressionlow['weekHighChange']):
                                        mldatalow = mldatalow + '|' + '0-month3HighChangeGT-5-shortdowntrend'
                                    elif ((regressionlow['monthHighChange'] + regressionlow['weekHighChange'] + regressionlow['weekLowChange']) > -4.5):
                                        mldatalow = mldatalow + '|' + '1-month3HighChangeGT-5-shortuptrend'
                                    else:
                                        mldatalow = mldatalow + '|' + 'month3HighChangeGT-5-indexhigh'
                                elif (regressionhigh['month3LowChange'] < 5):
                                    if (regressionlow['month3LowChange'] == regressionlow['weekLowChange']
                                        and (regressionlow['PCT_day_change_pre1'] > 0 or regressionlow['PCT_day_change_pre2'] > 0)
                                        ):
                                        mldatalow = mldatalow + '|' + 'buy-m3LowLT5-shortuptrend'
                                    elif ((regressionlow['monthLowChange'] + regressionlow['weekHighChange'] + regressionlow['weekLowChange']) < 4.5
                                        and (regressionlow['PCT_day_change_pre1'] < 0 or regressionlow['PCT_day_change_pre2'] < 0)
                                        and regressionlow['yearHighChange'] < -10
                                        and (regressionlow['year2LowCange'] > 5 or regressionlow['yearLowCange'] > 5 or regressionlow['PCT_day_change_pre1'] > 1)

                                    ):
                                        mldatalow = mldatalow + '|' + 'sell-m3LowLT5-shortdowntrend'
                                        if ('MLlowSellStrong' in mldatalow or data1 is not None):
                                            filtersFlag = True
                                if ('shorDownTrend' in regressionhigh['filter1'] and '(downTrend)' in regressionhigh['series_trend']
                                    and abs(regressionhigh['month3LowChange']) > abs(regressionhigh['month3HighChange'])
                                    ):
                                    mldatalow = mldatalow + '|' + 'shortDownTrend'
                                    filtersFlag = True

                                if (regressionhigh['PCT_day_change'] > -1 or regressionhigh['PCT_day_change_pre1'] > -1
                                    or 2*abs(regressionhigh['PCT_day_change']) < abs(regressionhigh['PCT_day_change_pre1'])
                                    ):
                                    tosell = 'sellrecommended'



                        except: 
                            needToPrint = True
                        
                        
                        # if(processor == 'buy-dayconsolidation-breakout-04(11:45-to-1:00)' or processor == 'sell-dayconsolidation-breakout-04(10:00-to-12:00)'):
                        #     if((db['morning-volume-breakout'].find_one({'scrip':scrip}) is None)): 
                        #         print(reportedtime, ':', processor, ' : ', scrip, ' : ', systemtime , ' : ', mldatahigh, ' : ', mldatalow)
                        # else:
                        #     print(reportedtime, ':', processor, ' : ', scrip, ' : ', systemtime , ' : ', mldatahigh, ' : ', mldatalow)


                        if (('%%' in mldatahigh and 'buy' in processor) or ('%%' in mldatalow and 'sell' in processor)):
                            print(reportedtime, ':', processor, ' : ', scrip, ' : ', systemtime, ' : ', mldatahigh, ' : ', mldatalow, ' : ', highVol, ' : ', resultDeclared + '  $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                            needToPrint = True
                        elif(filtered == True and filtersFlag == True
                            and 'Today' not in resultDeclared
                            and 'Yesterday' not in resultDeclared
                            ):
                            print(reportedtime, ':', processor, ' : ', scrip, ' : ', systemtime , ' : ', mldatahigh, ' : ', mldatalow, ' : ', highVol, ' : ', resultDeclared)
                            needToPrint = True
                        elif (filtersFlag == True
                            and 'Today' not in resultDeclared
                            and 'Yesterday' not in resultDeclared
                            ):
                            print(reportedtime, ':', processor, ' : ', scrip, ' : ', systemtime, ' : ', mldatahigh, ' : ', mldatalow, ' : ', highVol, ' : ', resultDeclared)
                            needToPrint = True
                        elif (filtered == False
                            and (data3 is not None)
                            and (('buy' in processor and ('buy' in highVol or 'Buy' in highVol))
                                or ('sell' in processor and ('sell' in highVol or 'Sell' in highVol))
                                )
                            and 'Today' not in resultDeclared
                            and 'Yesterday' not in resultDeclared
                            ):
                            print(reportedtime, ':', processor, ' : ', scrip, ' : ', systemtime, ' : ', mldatahigh, ' : ', mldatalow, ' : ', highVol, ' : ', resultDeclared)
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
            tobuy = ''
            tosell = ''
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
                            record['tobuy'] = tobuy
                            record['tosell'] = tosell

                            json_data = json.loads(json.dumps(record, default=json_util.default))
                            db[processor].insert_one(json_data)
                            tempScrip = ''
                            mlData = ''
                            resultDeclared = ''
                            tobuy = ''
                            tosell = ''

                if(dbnse['scrip'].find_one({'scrip':scrip}) is not None
                    and db[processor].find_one({'scrip':scrip}) is None
                    and eventdateonly == (date.today()).strftime('%Y-%m-%d')
                    and currenttime >= starttime and currenttime <= endtime
                    ):
                    #print(scrip)
                    mldatahigh = ''
                    mldatalow = ''
                    highVol = ''
                    resultDeclared = ''
                    filtersFlag = False

                    try:
                        if ((dbnse['scrip_result'].find_one({'scrip': scrip}) is not None)):
                            data = dbnse.scrip_result.find_one({'scrip': scrip})
                            resultDeclared = data['resultDeclared'] + ',' + data['result_sentiment']

                        if ((dbnse['highBuy'].find_one({'scrip': scrip}) is not None)):
                            data = dbnse.highBuy.find_one({'scrip': scrip})
                            mldatahigh = data['intradaytech']
                            if ('buy' in processor and ('MLhigh' in data['ml'] or '%%' in data['filter'] or 'Buy-AnyGT2' in data['filter2'] or 'Buy-AnyGT' in data['filter2'] or 'Sell-AnyGT2' in data['filter2'])):
                                mldatahigh = data['ml'] + ':' + data['intradaytech']
                                mldatahigh = mldatahigh + '|' + data['filter2'] + '|' + data['filter']
                        if ((dbnse['lowSell'].find_one({'scrip': scrip}) is not None)):
                            data = dbnse.lowSell.find_one({'scrip': scrip})
                            mldatalow = data['intradaytech']
                            if ('sell' in processor and ('MLhigh' in data['ml'] or '%%' in data['filter'] or 'Sell-AnyGT2' in data['filter2'] or 'Suy-AnyGT' in data['filter2'] or 'Buy-AnyGT2' in data['filter2'])):
                                mldatalow = data['ml'] + ':' + data['intradaytech']
                                mldatalow = mldatalow + '|' + data['filter2'] + '|' + data['filter']
                    except:
                        needToPrint = True  # do-nothing

                    try:
                        regressionhigh = dbnse.highBuy.find_one({'scrip': scrip})
                        regressionlow = dbnse.lowSell.find_one({'scrip': scrip})

                        if ('buy' in processor or 'Buy' in processor or 'breakout2-morning-volume' in processor or 'morning-volume-bs' in processor):
                            if(regressionhigh['month3LowChange'] < 5):
                                if (regressionhigh['month3LowChange'] == regressionhigh['weekLowChange']):
                                    mldatahigh = mldatahigh + '|' + '0-month3LowChangeLT5-shortuptrend'
                                elif ((regressionhigh['monthLowChange'] + regressionhigh['weekHighChange'] + regressionhigh['weekLowChange']) < 4.5):
                                    mldatahigh = mldatahigh + '|' + '1-month3LowChangeLT5-shortdowntrend'
                                else:
                                    mldatahigh = mldatahigh + '|' + 'month3LowChangeLT5-indexhigh'
                            elif (regressionlow['month3HighChange'] > -5):
                                if (regressionhigh['monthHighChange'] == regressionhigh['weekHighChange']
                                    and (regressionhigh['PCT_day_change_pre1'] < 0 or regressionhigh['PCT_day_change_pre2'] < 0)
                                    ):
                                    mldatahigh = mldatahigh + '|' + 'sell-m3HGT-5-shortdowntrend'
                                elif ((regressionhigh['monthHighChange'] + regressionhigh['weekHighChange'] + regressionhigh['weekLowChange']) > -4.5
                                    and (regressionhigh['PCT_day_change_pre1'] > 0 or regressionhigh['PCT_day_change_pre2'] > 0)
                                    and regressionhigh['yearLowChange'] > 10
                                    and (regressionhigh['year2HighChange'] < -5 or regressionhigh['year2HighChange'] < -5 or regressionhigh['PCT_day_change_pre1'] < -1)
                                    ):
                                    mldatahigh = mldatahigh + '|' + 'buy-m3HGT-5-shortuptrend'
                            if ('shortUpTrend' in regressionhigh['filter1'] and '(upTrend)' in regressionhigh['series_trend']
                                and abs(regressionhigh['month3LowChange']) < abs(regressionhigh['month3HighChange'])
                                ):
                                mldatahigh = mldatahigh + '|' + 'shortUpTrend'
                            if (regressionhigh['PCT_day_change'] < 1 or regressionhigh['PCT_day_change_pre1'] < 1
                                or 2 * abs(regressionhigh['PCT_day_change']) < abs(regressionhigh['PCT_day_change_pre1'])
                                ):
                                tobuy = 'buyrecommended'

                        if ('sell' in processor or 'Sell' in processor or 'breakout2-morning-volume' in processor or 'morning-volume-bs' in processor):
                            if  (regressionlow['month3HighChange'] > -5):
                                if(regressionlow['monthHighChange'] == regressionlow['weekHighChange']):
                                    mldatalow = mldatalow + '|' + '0-month3HighChangeGT-5-shortdowntrend'
                                elif((regressionlow['monthHighChange'] + regressionlow['weekHighChange'] + regressionlow['weekLowChange']) > -4.5):
                                    mldatalow = mldatalow + '|' + '1-month3HighChangeGT-5-shortuptrend'
                                else:
                                    mldatalow = mldatalow + '|' + 'month3HighChangeGT-5-indexhigh'
                            elif (regressionhigh['month3LowChange'] < 5):
                                if (regressionlow['month3LowChange'] == regressionlow['weekLowChange']
                                    and (regressionlow['PCT_day_change_pre1'] > 0 or regressionlow['PCT_day_change_pre2'] > 0)
                                    ):
                                    mldatalow = mldatalow + '|' + 'buy-m3LowLT5-shortuptrend'
                                elif ((regressionlow['monthLowChange'] + regressionlow['weekHighChange'] + regressionlow['weekLowChange']) < 4.5
                                    and (regressionlow['PCT_day_change_pre1'] < 0 or regressionlow['PCT_day_change_pre2'] < 0)
                                    and regressionlow['yearHighChange'] < -10
                                    and (regressionlow['year2LowCange'] > 5 or regressionlow['yearLowCange'] > 5 or regressionlow['PCT_day_change_pre1'] > 1)
                                    ):
                                    mldatalow = mldatalow + '|' + 'sell-m3LowLT5-shortdowntrend'
                            if ('shorDownTrend' in regressionhigh['filter1'] and '(downTrend)' in regressionhigh['series_trend']
                                and abs(regressionhigh['month3LowChange']) > abs(regressionhigh['month3HighChange'])
                                ):
                                mldatalow = mldatalow + '|' + 'shortDownTrend'
                            if (regressionhigh['PCT_day_change'] > -1 or regressionhigh['PCT_day_change_pre1'] > -1
                                or 2 * abs(regressionhigh['PCT_day_change']) < abs(regressionhigh['PCT_day_change_pre1'])
                                ):
                                tosell = 'sellrecommended'

                        if ('buy-breakup-intraday-9:40-to-10:10' in processor and regressionhigh['forecast_day_PCT3_change'] < 5 and regressionhigh['forecast_day_PCT4_change'] < 5):
                            filtersFlag = True
                        if ('sell-breakdown-intraday-9:40-to-10:10' in processor and regressionhigh['forecast_day_PCT3_change'] > -5 and regressionhigh['forecast_day_PCT4_change'] > -5):
                            filtersFlag = True

                    except: 
                        needToPrint = True  # do-nothing
                        
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

                    if filtersFlag:
                        print(reportedtime, ':', processor, ' : ', scrip, ' : ', systemtime, ' : ', mldatahigh, ' : ', mldatalow, ' : ', highVol, ' : ', resultDeclared)
                    elif(processor == 'morning-volume-bs' or processor == 'breakout2-morning-volume' or processor == 'breakout-morning-volume'):
                        needToPrint = True  # do-nothing
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
                    mlData = mldatahigh + ' : ' + mldatalow + ' : ' + highVol
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
            histData = ' %%%% ' + scrip + ' : ' + data['ml'] + '|' + data['intradaytech'] + '|' + data['filter2'] + '|' + data['filter'] + '|' + data['filter3']
            #if(data['ml'] != '' or data['filter'] != '' or data['filter2'] != ''):
            if(('%%' in histData and 'Super' in histData)
                or 'checkBuyConsolidationBreakout-allPreLT0' in histData
                or '%%:checkBuy:Consolidation' in histData
                or (data['intradaytech'] != "" and data['ml'] != "")
                ):
                print(histData)

    for data in dbnse.scrip.find({'futures': 'Yes'}):
        scrip = data['scrip']
        if ((dbnse['highBuy'].find_one({'scrip': scrip}) is not None)):
            data = dbnse.highBuy.find_one({'scrip': scrip})
            histData = ' #### ' + scrip + ' : ' + data['ml'] + '|' + data['intradaytech'] + '|' + data['filter2'] + '|' + data['filter'] + '|' + data['filter3']
            # if(data['ml'] != '' or data['filter'] != '' or data['filter2'] != ''):
            if ("$$" in histData
                #or 'ConsolidationBreakout' in histData
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
                #or 'checkBuyConsolidationBreakUp' in histData
                or 'buyYear2LowBreakingUp' in histData
                ):
                print(histData)

    
def regression_ta_data_sell():
    for data in dbnse.scrip.find({'futures':'Yes'}):
        scrip = data['scrip']
        if((dbnse['lowSell'].find_one({'scrip':scrip}) is not None)):
            data = dbnse.lowSell.find_one({'scrip':scrip})
            histData = ' %%%% ' + scrip + ' : ' + data['ml'] + '|' + data['intradaytech'] + '|' + data['filter2'] + '|' + data['filter'] + '|' + data['filter3']
            #if(data['ml'] != '' or data['filter'] != '' or data['filter2'] != ''):
            if (('%%' in histData and 'Super' in histData)
                or 'checkSellConsolidationBreakdown-allPreGT0' in histData
                or '%%:checkBuy:Consolidation' in histData
                or (data['intradaytech'] != "" and data['ml'] != "")
                ):
                print(histData) 
    for data in dbnse.scrip.find({'futures': 'Yes'}):
        scrip = data['scrip']
        if ((dbnse['lowSell'].find_one({'scrip': scrip}) is not None)):
            data = dbnse.lowSell.find_one({'scrip': scrip})
            histData = ' #### ' + scrip + ' : ' + data['ml'] + '|' + data['intradaytech'] + '|' + data['filter2'] + '|' + data['filter'] + '|' + data['filter3']
            # if(data['ml'] != '' or data['filter'] != '' or data['filter2'] != ''):
            if ("$$" in histData
                #or 'ConsolidationBreakdown' in histData
                or '%%HLTF:maySellTail-tailGT2-allDayGT0' in histData
                or '%%HLTF:maySellTail-tailGT2-7,10thDayGT0' in histData
                or '$$MaySell-CheckChart(downTrend-mayReverseLast4DaysUp)' in histData
                or 'sellYearLow' in histData
                or 'sellYearHigh' in histData
                or '%%:sellUpTrend-month3High' in histData
                or 'sellFinal' in histData
                or 'sellEveningStar-0' in histData
                or 'checkCupDown' in histData
                #or 'checkSellConsolidationBreakDown' in histData
                ):
                print(histData)
