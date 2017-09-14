import json
from pymongo import MongoClient
connection = MongoClient('localhost', 27017)
db = connection.Nsedata

def calculateParallel(threads=2):
    pool = ThreadPool(threads)
    
    scrips = []
    for data in db.scrip.find():
        scrips.append(((data['scrip']).encode('UTF8').replace('&','').replace('-','_'), data['company']))
    
    pool.map(regression_ta_data, scrips)
                     
if __name__ == "__main__":
    calculateParallel(1)
    connection.close()