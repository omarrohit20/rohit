import os, logging, sys, json, csv
sys.path.insert(0, '../')

from pymongo import MongoClient
from multiprocessing.dummy import Pool as ThreadPool

import time


connection = MongoClient('localhost', 27017)
db = connection.nsehistnew


directory = '../../output/final'
logname = '../../output/final' + '/all-result' + time.strftime("%d%m%y-%H%M%S")
      
                                    
def result_data_reg(regression_high, regression_low, scrip):
    if(regression_high is None or regression_low is None):
        return
    
    regression_data = regression_high
    if(regression_data is not None):
        db.ws_high.insert_one(json.loads(json.dumps(regression_high)))
                
    regression_data = regression_low
    if(regression_data is not None):
        db.ws_low.insert_one(json.loads(json.dumps(regression_low)))
        
                                         

def calculateParallel(threads=2, futures=None):
    pool = ThreadPool(threads)
    scrips = []
    for data in db.scrip.find({'futures':futures}):
        scrips.append(data['scrip'])
    scrips.sort()
    pool.map(result_data, scrips)
    pool.map(result_data_cla, scrips)
    pool.map(result_data_reg, scrips)
                      
if __name__ == "__main__":
    if not os.path.exists(directory):
        os.makedirs(directory)
    calculateParallel(1, sys.argv[1])
    connection.close()
    saveReports(sys.argv[1])