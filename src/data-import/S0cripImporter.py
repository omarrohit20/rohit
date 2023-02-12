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
                futures = "Yes"
                
                db.scrip_futures.insert_one({
                    "company": row[0],
                    "industry": "",
                    "scrip": row[1],
                    "futures":futures,
                    "index":"futures"
                    })
            count = count + 1
        except:
            pass    
print(count)

count = 0
with open('nselist/ind_nifty500list.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        try:
            if (count != 0):
                print(row[0])
                
                data = db.scrip_futures.find_one({'scrip':row[2]})
                if(data is None):
                    futures = "No"
                else:
                    futures = "Yes"

                db.scrip.insert_one({
                    "company": row[0],
                    "industry": row[1],
                    "scrip": row[2],
                    "futures":futures,
                    "index": "nifty500"
                    })
            count = count + 1
        except:
            pass    
print(count)

count = 0
with open('nselist/ind_niftycash.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        try:
            if (count != 0):
                print(row[0])
                
                data = db.scrip.find_one({'scrip':row[1]})
                if(data is None):
                    futures = "No"

                    db.scrip.insert_one({
                        "company": row[0],
                        "industry": "",
                        "scrip": row[1],
                        "futures":futures,
                        "index": "cash"
                        })
            count = count + 1
        except:
            pass    
print(count)

connection.close()


