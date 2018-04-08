import csv
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
                print(row[0])
                db.scrip_result.insert_one({
                    "scrip": row[0],
                    "result_date":row[1],
                    "result_sentiment":row[2],
                    "comment":row[3],
                    })
            count = count + 1
        except:
            pass    
print(count)

connection.close()


