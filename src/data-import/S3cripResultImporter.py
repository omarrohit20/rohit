import csv
import datetime
import time
import gc
import copy
import json
from pymongo import MongoClient
connection = MongoClient('localhost', 27017)
db = connection.Nsedata
db.drop_collection('scrip_result')


count = 0
with open('nselist/ind_result.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        try:
            if (count != 0):
                
                start_date = (datetime.datetime.now())
                today = datetime.datetime(start_date.year, start_date.month, start_date.day)
                
                start_date = (datetime.datetime.now() - datetime.timedelta(days=4))
                today_pre2 = datetime.datetime(start_date.year, start_date.month, start_date.day)
                
                start_date = (datetime.datetime.now() - datetime.timedelta(days=3))
                today_pre1 = datetime.datetime(start_date.year, start_date.month, start_date.day)
                
                start_date = (datetime.datetime.now() + datetime.timedelta(days=1))
                today_next1 = datetime.datetime(start_date.year, start_date.month, start_date.day)
                start_date = (datetime.datetime.now() + datetime.timedelta(days=2))
                today_next2 = datetime.datetime(start_date.year, start_date.month, start_date.day)
                start_date = (datetime.datetime.now() + datetime.timedelta(days=3))
                today_next3 = datetime.datetime(start_date.year, start_date.month, start_date.day)
                start_date = (datetime.datetime.now() + datetime.timedelta(days=4))
                today_next4 = datetime.datetime(start_date.year, start_date.month, start_date.day)
                
                result_time = datetime.datetime.strptime(row[1], "%Y-%m-%d")
                
                
                regdata = db.history.find_one({'dataset_code':row[0]})
                if(regdata is not None):
                    today_pre1 = datetime.datetime.strptime(regdata['end_date'], "%Y-%m-%d")
                    today_pre2 = today_pre1 - datetime.timedelta(days=1)
                    
                resultDeclared = ''
                if today_pre2 <= result_time < today_pre1:
                    resultDeclared = 'DayBeforeYesterday'
                elif today_pre1 <= result_time < today:
                    resultDeclared = 'Yesterday'
                elif today <= result_time < today_next1:
                    resultDeclared = 'Today'
                elif today_next1 <= result_time < today_next2:
                    resultDeclared = 'Tomorrow'
                elif today_next2 <= result_time < today_next3:
                    resultDeclared = 'DayAfterTomorrow'
                #elif today_next3 <= result_time < today_next4:
                    #resultDeclared = 'DayAfterTomorrow + 1'
                
                if(resultDeclared != ''):   
                    db.scrip_result.insert_one({
                        "scrip": row[0],
                        "result_date":row[1],
                        "result_sentiment":row[2],
                        "comment":row[3],
                        "resultDeclared":resultDeclared
                        })
                    print(row[0] + ' : ' + resultDeclared)
            count = count + 1
        except:
            pass    
print(count)

connection.close()


