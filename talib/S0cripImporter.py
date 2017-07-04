import csv
from pymongo import MongoClient
connection = MongoClient('localhost', 27017)
db = connection.NseDataTA
db.drop_collection('scrip')

count = 0
with open('../nselist/ind_nifty500list.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        try:
            if (count != 0):
                print row[0]
                db.scrip.insert_one({
                    "company": row[0],
                    "industry": row[1],
                    "scrip": row[2]
                    })
            count = count + 1
        except:
            pass    
print count

connection.close()


