import json
import datetime
from pymongo import MongoClient
import numpy as np
connection = MongoClient('localhost', 27017)
db = connection.Nsedata
db.drop_collection('indicators.black_marubozu')
db.drop_collection('indicators.white_marubozu')
db.drop_collection('indicators.short_white_candle')
db.drop_collection('indicators.long_white_candle')
db.drop_collection('indicators.long_black_candle')
db.drop_collection('indicators.short_black_candle')
db.drop_collection('indicators.doji')
db.drop_collection('indicators.highdoji')
db.drop_collection('indicators.lowdoji')

if __name__ == "__main__":
    end_date = datetime.date.today().strftime('%d-%m-%Y')
    start_date = (datetime.date.today() - datetime.timedelta(days=30)).strftime('%d-%m-%Y')
    print start_date + ' to ' + end_date
    
    for symbol in db.scrip.find():
        try:
            
            data = db.history.find_one({'dataset_code':(symbol['scrip']).encode('UTF8').replace('&','').replace('-','_')})
            
            if(data is None):
                continue
                print  'Missing Data for ',(symbol['scrip']).encode('UTF8'), '\n' 
                
            ardate = [x.encode('UTF8') for x in (np.array(data['data'])[:,0]).tolist()]
            aropen = [float(x.encode('UTF8')) for x in (np.array(data['data'])[:,1]).tolist()]
            arhigh = [float(x.encode('UTF8')) for x in (np.array(data['data'])[:,2]).tolist()]
            arlow  = [float(x.encode('UTF8')) for x in (np.array(data['data'])[:,3]).tolist()]
            arlast = [float(x.encode('UTF8')) for x in (np.array(data['data'])[:,4]).tolist()]
            arclose= [float(x.encode('UTF8')) for x in (np.array(data['data'])[:,5]).tolist()]
            arquantity = [float(x.encode('UTF8')) for x in (np.array(data['data'])[:,6]).tolist()]
            arturnover = [float(x.encode('UTF8')) for x in (np.array(data['data'])[:,7]).tolist()]
                
            hs = 0
            date = ardate[hs]
            open = aropen[hs]
            high = arhigh[hs]
            low  = arlow[hs]
            last = arlast[hs]
            close = arclose[hs]
            quantity = arquantity[hs]
            turnover = arturnover[hs]
            change = (close - open)*100/open  
            
            hs = 11
            hsdate = ardate[hs]
            hsopen = aropen[hs]
            hshigh = arhigh[hs]
            hslow  = arlow[hs]
            hslast = arlast[hs]
            hsclose = arclose[hs]
            hsquantity = arquantity[hs]
            hsturnover = arturnover[hs]
            
            he = 1
            hedate = ardate[he]
            heopen = aropen[he]
            hehigh = arhigh[he]
            helow  = arlow[he]
            helast = arclose[he]
            heclose = arclose[he]
            hequantity = arquantity[he]
            heturnover = arturnover[he]
            
            hchange = (heclose-hsclose)*100/hsclose   
            
            print data['data'][0] 
            print data['dataset_code'] , ' change:' , change , ' hchange:' , hchange
            print data['data'][he]
            print data['data'][hs]  
                 
            
            #Black Marubozu
            if(abs(change) > 3
               and (close < open) 
               and (high==open) 
               and ((close-low)>(high-low)*10/100) 
               and ((open-close)>(high-low)*55/100)):
                print 'Black Marubozu'
                db.indicators.black_marubozu.insert_one({
                        "scrip": data['dataset_code'],
                        "date": date,
                        "indicator": 'Black Marubozu',
                        "quantity": quantity,
                        "turnover": turnover,
                        "change": change,
                        "hchange": hchange,
                        "datastart": data['data'][hs],
                        "dataend": data['data'][he],
                        "open":open,
                        "high":high,
                        "low":low,
                        "close":close
                        })
                
            #White Marubozu
            if(abs(change) > 3
               and (close > open) 
               and (open==low) 
               and ((high-close)>(high-low)*10/100) 
               and ((close-open)>(high-low)*55/100)): 
                print 'White Marubozu'
                db.indicators.white_marubozu.insert_one({
                        "scrip": data['dataset_code'],
                        "date": date,
                        "indicator": 'White Marubozu',
                        "quantity": quantity,
                        "turnover": turnover,
                        "change": change,
                        "hchange": hchange,
                        "datastart": data['data'][hs],
                        "dataend": data['data'][he],
                        "open":open,
                        "high":high,
                        "low":low,
                        "close":close
                        })
                
    #         #Black Marubozu
    #         if((close < open) 
    #            and (high==open) 
    #            and ((close-low)>(high-low)*10/100) 
    #            and ((open-close)>(high-low)*55/100)):
    #             print 'Black Marubozu'
    #             db.indicators.black_marubozu.insert_one({
    #                     "scrip": data['dataset_code'],
    #                     "date": date,
    #                     "indicator": 'Black Marubozu',
    #                     "quantity": quantity,
    #                     "turnover": turnover,
    #                     "change": change,
    #                     "hchange": hchange,
    #                     "datalatest": data['data'][0],
    #                     "datastart": data['data'][hs],
    #                     "dataend": data['data'][he]
    #                     })
    #             
    #         #White Marubozu
    #         if((close > open) 
    #            and (open==low) 
    #            and ((high-close)>(high-low)*10/100) 
    #            and ((close-open)>(high-low)*55/100)): 
    #             print 'White Marubozu'
    #             db.indicators.white_marubozu.insert_one({
    #                     "scrip": data['dataset_code'],
    #                     "date": date,
    #                     "indicator": 'White Marubozu',
    #                     "quantity": quantity,
    #                     "turnover": turnover,
    #                     "change": change,
    #                     "hchange": hchange,
    #                     "datalatest": data['data'][0],
    #                     "datastart": data['data'][hs],
    #                     "dataend": data['data'][he]
    #                     })  
                
    #         #Long white candle    
    #         if((close>open) 
    #            and ((close-open)>2*(high-close)) 
    #            and ((close-open)>2*(open-low))): 
    #             print 'Long White Candle'
    #             db.indicators.long_white_candle.insert_one({
    #                     "scrip": data['dataset_code'],
    #                     "date": date,
    #                     "indicator": 'Long White Candle',
    #                     "quantity": quantity,
    #                     "turnover": turnover,
    #                     "change": change,
    #                     "hchange": hchange,
    #                     "datalatest": data['data'][0],
    #                     "datastart": data['data'][hs],
    #                     "dataend": data['data'][he]
    #                     })
    #             
    #         #Short white candle
    #         if((close>open) 
    #            and ((high-close)>(high-low)*10/100) 
    #            and ((high-close)<(high-low)*45/100) 
    #            and ((open-low)>(high-low)*10/100) 
    #            and ((open-low)<(high-low)*50/100) 
    #            and ((close-open)>(high-low)*45/100)): 
    #             print 'Short White Candle'
    #             db.indicators.short_white_candle.insert_one({
    #                     "scrip": data['dataset_code'],
    #                     "date": date,
    #                     "indicator": 'Short White Candle',
    #                     "quantity": quantity,
    #                     "turnover": turnover,
    #                     "change": change,
    #                     "hchange": hchange,
    #                     "datalatest": data['data'][0],
    #                     "datastart": data['data'][hs],
    #                     "dataend": data['data'][he]
    #                     })
    #             
    #         #Long black candle
    #         if((close<open) 
    #            and ((open-close)>2*(high-open))
    #            and ((open-close)>2*(close-low))): 
    #             print 'Long Black Candle' 
    #             db.indicators.long_black_candle.insert_one({
    #                     "scrip": data['dataset_code'],
    #                     "date": date,
    #                     "indicator": 'Long Black Candle',
    #                     "quantity": quantity,
    #                     "turnover": turnover,
    #                     "change": change,
    #                     "hchange": hchange,
    #                     "datalatest": data['data'][0],
    #                     "datastart": data['data'][hs],
    #                     "dataend": data['data'][he]
    #                     })
    #             
    #         #Short black candle
    #         if((close<open) 
    #            and (abs(high-open)>(high-low)*5/100)
    #            and (abs(high-open)<(high-low)*45/100)
    #            and ((close-low)>(high-low)*5/100)
    #            and ((close-low)<(high-low)*45/100)
    #            and ((open-close)>(high>low)*45/100)): 
    #             print 'Short Black Candle'
    #             db.indicators.short_black_candle.insert_one({
    #                     "scrip": data['dataset_code'],
    #                     "date": date,
    #                     "indicator": 'Short Black Candle',
    #                     "quantity": quantity,
    #                     "turnover": turnover,
    #                     "change": change,
    #                     "hchange": hchange,
    #                     "datalatest": data['data'][0],
    #                     "datastart": data['data'][hs],
    #                     "dataend": data['data'][he]
    #                     })
                
            #Doji
            if(abs(hchange) > 10
               and abs(close-open)< abs(high-low)*30/100): 
                print 'Doji'  
                db.indicators.doji.insert_one({
                        "scrip": data['dataset_code'],
                        "date": date,
                        "indicator": 'Doji',
                        "quantity": quantity,
                        "turnover": turnover,
                        "change": change,
                        "hchange": hchange,
                        "datastart": data['data'][hs],
                        "dataend": data['data'][he],
                        "open":open,
                        "high":high,
                        "low":low,
                        "close":close
                        }) 
                
            #Historical High --> Doji
            if(hchange > 20
               and abs(close-open)< abs(high-low)*30/100): 
                print 'HighDoji'  
                db.indicators.highdoji.insert_one({
                        "scrip": data['dataset_code'],
                        "date": date,
                        "indicator": 'HighDoji',
                        "quantity": quantity,
                        "turnover": turnover,
                        "change": change,
                        "hchange": hchange,
                        "datastart": data['data'][hs],
                        "dataend": data['data'][he],
                        "open":open,
                        "high":high,
                        "low":low,
                        "close":close
                        }) 
                
            #Historical Low --> Doji
            if(hchange < -20
               and abs(close-open)< abs(high-low)*30/100): 
                print 'LowDoji'  
                db.indicators.lowdoji.insert_one({
                        "scrip": data['dataset_code'],
                        "date": date,
                        "indicator": 'LowDoji',
                        "quantity": quantity,
                        "turnover": turnover,
                        "change": change,
                        "hchange": hchange,
                        "datastart": data['data'][hs],
                        "dataend": data['data'][he],
                        "open":open,
                        "high":high,
                        "low":low,
                        "close":close
                        })                
                 
        except:
            pass
    
    
    connection.close()