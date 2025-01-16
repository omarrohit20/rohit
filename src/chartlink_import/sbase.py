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
option.add_argument('--headless=new')
option.add_argument('--no-sandbox')
option.add_argument('--disable-gpu')
option.binary_location = 'C:\git\cft\chrome.exe'

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
            mldatahigh = ''
            mldatalow = ''
            highVol = ''
            intradaytech = ''
            PCT_day_change = ''
            PCT_change = ''
            year5HighChange = ''
            yearHighChange = ''
            yearLowChange = ''
            month3HighChange = ''
            month3LowChange = ''
            monthHighChange = ''
            monthLowChange = ''
            week2HighChange = ''
            week2LowChange = ''
            forecast_day_PCT10_change = ''
            filter = ''
            filter3 = ''
            highTail = ''
            lowTail = ''
            shorttermtech = ''
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
                            record['mldatahigh'] = mldatahigh
                            record['mldatalow'] = mldatalow
                            record['highVol'] = highVol
                            record['intradaytech'] = intradaytech
                            record['PCT_day_change'] = PCT_day_change
                            record['PCT_change'] = PCT_change
                            record['year5HighChange'] = year5HighChange
                            record['yearHighChange'] = yearHighChange
                            record['yearLowChange'] = yearLowChange
                            record['month3HighChange'] = month3HighChange
                            record['month3LowChange'] = month3LowChange
                            record['monthHighChange'] = monthHighChange
                            record['monthLowChange'] = monthLowChange
                            record['week2HighChange'] = week2HighChange
                            record['week2LowChange'] = week2LowChange
                            record['forecast_day_PCT10_change'] = forecast_day_PCT10_change
                            record['filter'] = filter
                            record['filter3'] = filter3
                            record['highTail'] = highTail
                            record['lowTail'] = lowTail
                            record['resultDeclared'] = resultDeclared
                            record['processor'] = processor
                            record['epochtime'] = epochtime
                            record['eventtime'] = eventtime
                            record['systemtime'] = systemtime
                            record['keyIndicator'] = keyIndicator
                            record['tobuy'] = tobuy
                            record['tosell'] = tosell

                            json_data = json.loads(json.dumps(record, default=json_util.default))
                            db[processor].insert_one(json_data)

                            if(('morninglow-high-volume-buy' not in processor) and ('morning-volume-breakout-buy' not in processor)):
                                if ((('buy' in processor) or ('Buy' in processor) or ('Bbuyy' in processor)) and (('09_30:' not in processor) and ('dayconsolidation-breakout-03' not in processor))):
                                    db['buy_all_processor'].insert_one(json_data)
                            if (('morninghigh-high-volume-sell' not in processor) and ('morning-volume-breakout-sell' not in processor)):
                                if ((('sell' in processor) or ('Sell' in processor) or ('Sselll' in processor)) and (('09_30:' not in processor) and ('dayconsolidation-breakout-03' not in processor))):
                                    db['sell_all_processor'].insert_one(json_data)

                            tempScrip = ''
                            mlData = ''
                            mldatahigh = ''
                            mldatalow = ''
                            highVol = ''
                            intradaytech = ''
                            PCT_day_change = ''
                            PCT_change = ''
                            year5HighChange = ''
                            yearHighChange = ''
                            yearLowChange = ''
                            month3HighChange = ''
                            month3LowChange = ''
                            monthHighChange = ''
                            monthLowChange = ''
                            week2HighChange = ''
                            week2LowChange = ''
                            forecast_day_PCT10_change = ''
                            filter = ''
                            filter3 = ''
                            highTail = ''
                            lowTail = ''
                            shorttermtech = ''
                            resultDeclared = ''
                            tobuy = ''
                            tosell = ''

                if(dbnse['scrip'].find_one({'scrip':scrip}) is not None
                    and db[processor].find_one({'scrip':scrip}) is None
                    and eventdateonly == (date.today()).strftime('%Y-%m-%d')
                    and currenttime >= starttime and currenttime <= endtime
                    ):
                    #print(scrip)
                    mlData = ''
                    mldatahigh = ''
                    mldatalow = ''
                    highVol = ''
                    intradaytech = ''
                    PCT_day_change = ''
                    PCT_change = ''
                    year5HighChange = ''
                    yearHighChange = ''
                    yearLowChange = ''
                    month3HighChange = ''
                    month3LowChange = ''
                    monthHighChange = ''
                    monthLowChange = ''
                    week2HighChange = ''
                    week2LowChange = ''
                    forecast_day_PCT10_change = ''
                    filter = ''
                    filter3 = ''
                    highTail = ''
                    lowTail = ''
                    shorttermtech = ''
                    resultDeclared = ''
                    filtersFlag = False

                    try:
                        if ((dbnse['scrip_result'].find_one({'scrip': scrip}) is not None)):
                            data = dbnse.scrip_result.find_one({'scrip': scrip})
                            resultDeclared = data['resultDeclared'] + ',' + data['result_sentiment']

                        if ((dbnse['highBuy'].find_one({'scrip': scrip}) is not None)):
                            data = dbnse.highBuy.find_one({'scrip': scrip})
                            PCT_day_change = data['PCT_day_change']
                            PCT_change = data['PCT_change']
                            year5HighChange = data['year5HighChange']
                            yearHighChange = data['yearHighChange']
                            yearLowChange = data['yearLowChange']
                            month3HighChange = data['month3HighChange']
                            month3LowChange = data['month3LowChange']
                            monthHighChange = data['monthHighChange']
                            monthLowChange = data['monthLowChange']
                            week2HighChange = data['week2HighChange']
                            week2LowChange = data['week2LowChange']
                            forecast_day_PCT10_change = data['forecast_day_PCT10_change']
                            filter = data['filter']
                            filter3 = data['filter3']
                            highTail = data['highTail']
                            lowTail = data['lowTail']
                            if ('buy' in processor and ('MLhigh' in data['ml'] or '%%' in data['filter'] or 'Buy-AnyGT2' in data['filter2'] or 'Buy-AnyGT' in data['filter2'] or 'Sell-AnyGT2' in data['filter2'])):
                                mldatahigh = data['ml']
                                mldatahigh = mldatahigh + '|' + data['filter2'] + '|' + data['filter']
                            if (('BreakHighYear' in data['filter3'] or 'NearHighYear' in data['filter3']) and data['year5HighChange']):
                                mldatahigh = 'MayBuyHighYear-OpenedOrAtLow' + '|' + mldatahigh
                        if ((dbnse['lowSell'].find_one({'scrip': scrip}) is not None)):
                            data = dbnse.lowSell.find_one({'scrip': scrip})
                            if ('sell' in processor and ('MLlow' in data['ml'] or '%%' in data['filter'] or 'Sell-AnyGT2' in data['filter2'] or 'Sell-AnyGT' in data['filter2'] or 'Buy-AnyGT2' in data['filter2'])):
                                mldatalow = data['ml']
                                mldatalow = mldatalow + '|' + data['filter2'] + '|' + data['filter']
                            if ('BreakLowYear' in data['filter3'] or 'NearLowYear' in data['filter3']):
                                mldatalow = 'MaySellLowYear-OpenedOrAtHigh' + '|' + mldatalow
                        if (data['intradaytech'] != ""):
                            intradaytech = data['intradaytech']
                            filtersFlag = True
                    except:
                        needToPrint = True  # do-nothing

                    try:
                        regressionhigh = dbnse.highBuy.find_one({'scrip': scrip})
                        regressionlow = dbnse.lowSell.find_one({'scrip': scrip})

                        if ('buy' in processor or 'Buy' in processor or 'breakout2-morning-volume' in processor or 'morning-volume-bs' in processor):
                           mldatahigh = regressionhigh['shorttermtech'] + '|' + mldatahigh
                           if (regressionhigh['PCT_day_change'] < 1 or regressionhigh['PCT_day_change_pre1'] < 1
                                or 2 * abs(regressionhigh['PCT_day_change']) < abs(regressionhigh['PCT_day_change_pre1'])
                                ):
                                tobuy = 'buyrecommended'

                        if ('sell' in processor or 'Sell' in processor or 'breakout2-morning-volume' in processor or 'morning-volume-bs' in processor):
                            mldatalow = regressionlow['shorttermtech'] + '|' + mldatalow
                            if (regressionlow['PCT_day_change'] > -1 or regressionlow['PCT_day_change_pre1'] > -1
                                or 2 * abs(regressionlow['PCT_day_change']) < abs(regressionlow['PCT_day_change_pre1'])
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

                    if (processor == 'morning-volume-breakout-buy'):
                        if (db['morning-volume-breakout-buy'].count_documents({}) < 5):
                            intradaytech = '#TOP5B##' + intradaytech
                        elif (db['morning-volume-breakout-buy'].count_documents({}) < 10):
                            intradaytech = '#TOP10B##' + intradaytech
                        elif (db['morning-volume-breakout-buy'].count_documents({}) < 15):
                            intradaytech = '#TOP15B##' + intradaytech
                        elif (db['morning-volume-breakout-buy'].count_documents({}) < 15):
                            intradaytech = 'TOP25B##' + intradaytech
                    elif (processor == 'morning-volume-breakout-sell'):
                        if (db['morning-volume-breakout-sell'].count_documents({}) < 5):
                            intradaytech = '#TOP5S##' + intradaytech
                        elif (db['morning-volume-breakout-sell'].count_documents({}) < 10):
                            intradaytech = '#TOP10S##' + intradaytech
                        elif (db['morning-volume-breakout-sell'].count_documents({}) < 15):
                            intradaytech = '#TOP15S##' + intradaytech
                        elif (db['morning-volume-breakout-sell'].count_documents({}) < 15):
                            intradaytech = 'TOP25S##' + intradaytech
                    elif (any(d['scrip'] == scrip for d in db['morning-volume-breakout-buy'].find().sort('_id').limit(5))
                        ):
                        intradaytech = '#TOP5B##' + intradaytech
                    elif (any(d['scrip'] == scrip for d in db['morning-volume-breakout-buy'].find().sort('_id').limit(10))):
                        intradaytech = '#TOP10B##' + intradaytech
                    elif (any(d['scrip'] == scrip for d in db['morning-volume-breakout-buy'].find().sort('_id').limit(15))):
                        intradaytech = '#TOP15B##' + intradaytech
                    elif (any(d['scrip'] == scrip for d in db['morning-volume-breakout-buy'].find().sort('_id').limit(25))):
                        intradaytech = '#TOP25B##' + intradaytech
                    elif (any(d['scrip'] == scrip for d in db['morning-volume-breakout-sell'].find().sort('_id').limit(5))
                        ):
                        intradaytech = '#TOP5S##' + intradaytech
                    elif (any(d['scrip'] == scrip for d in db['morning-volume-breakout-sell'].find().sort('_id').limit(10))
                        ):
                        intradaytech = '#TOP10S##' + intradaytech
                    elif (any(d['scrip'] == scrip for d in db['morning-volume-breakout-sell'].find().sort('_id').limit(15))
                        ):
                        intradaytech = '#TOP15S##' + intradaytech
                    elif (any(d['scrip'] == scrip for d in db['morning-volume-breakout-sell'].find().sort('_id').limit(25))
                        ):
                        intradaytech = '#TOP25S##' + intradaytech

                    if (any(d['scrip'] == scrip for d in db['morninglow-high-volume-buy'].find())
                        ):
                        intradaytech = '#BUYMORNINGLOW#' + intradaytech
                    elif (any(d['scrip'] == scrip for d in db['morninghigh-high-volume-sell'].find())
                        ):
                        intradaytech = '#SELLMORNINGHIGH#' + intradaytech


                    needToPrint = True
                                
                    tempScrip = scrip
                    mlData = intradaytech + ' $ ' + mldatahigh + ' $ ' + mldatalow + ' $ ' + highVol
                    mldatahigh = intradaytech + ' $ ' + mldatahigh
                    mldatalow = intradaytech + ' $ ' + mldatalow
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
