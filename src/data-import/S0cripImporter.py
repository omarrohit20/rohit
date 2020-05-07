import csv
from pymongo import MongoClient
connection = MongoClient('localhost', 27017)
db = connection.Nsedata
db.drop_collection('scrip')
db.drop_collection('scrip_futures')


count = 0
with open('nselist/ind_niftyfuturelist.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        try:
            if (count != 0):
                print(row[0])
                db.scrip_futures.insert_one({
                    "company": row[0],
                    "scrip": row[1]
                    })
            count = count + 1
        except:
            pass    
print(count)

count = 0
with open('nselist/ind_nifty200list.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        try:
            if (count != 0):
                print(row[0])
                
                futures = "Yes"
                data = db.scrip_futures.find_one({'scrip':row[2]})
                if(data is None):
                    futures = "No"

                db.scrip.insert_one({
                    "company": row[0],
                    "industry": row[1],
                    "scrip": row[2],
                    "futures":futures
                    })
            count = count + 1
        except:
            pass    
print(count)

connection.close()


