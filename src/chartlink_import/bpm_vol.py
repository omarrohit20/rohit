from multiprocessing.dummy import Pool as ThreadPool
from pymongo import MongoClient
connection = MongoClient('localhost', 27017)
db = connection.Nsedata


    
     
 
                     
if __name__ == "__main__":
    print('###############Buy#################')    
    regression_ta_data_buy()
    print('###############Sell#################')  
    regression_ta_data_sell()
    connection.close()
    