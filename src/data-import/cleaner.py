import json, datetime, time, copy, sys, csv, logging
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from pymongo import MongoClient
from multiprocessing.dummy import Pool as ThreadPool

import numpy as np
import talib 
from talib.abstract import *

from datetime import datetime, timedelta

connection = MongoClient('localhost', 27017)
db = connection.Nsedata
dbchartlink = connection.chartlink

db.drop_collection('technical')
db.drop_collection('buy.overlap')
db.drop_collection('sell.overlap')
db.drop_collection('buy.pattern')
db.drop_collection('sell.pattern')
db.drop_collection('buy.momentum')
db.drop_collection('sell.momentum')
db.drop_collection('buy.volume')
db.drop_collection('sell.volume')
db.drop_collection('regression')
db.drop_collection('regressionhigh')
db.drop_collection('regressionlow')
db.drop_collection('regressionhigh_vol')
db.drop_collection('regressionlow_vol')
db.drop_collection('classification')
db.drop_collection('classificationhigh')
db.drop_collection('classificationlow')
db.drop_collection('scrip_result')
db.drop_collection('resultScripFutures')
db.drop_collection('highBuy')
db.drop_collection('lowSell')

collection = dbchartlink.list_collection_names()
for collect in collection:
    dbchartlink.drop_collection(collect)


DATE_FIELD = "date" # The field in your documents with the date string
DATE_FORMAT = "%Y-%m-%d" # Your string date format, e.g., "2025-09-19"


# Define the particular datetime
# Example: Delete documents older than January 1, 2024, 00:00:00
particular_datetime = datetime.now() - timedelta(days=5)
cutoff_date = particular_datetime.strftime(DATE_FORMAT)

# Define the query to find documents with a 'created_at' field (or your date field)
# that is less than the particular_datetime
query = {DATE_FIELD: {"$lt": cutoff_date}}

# Execute the delete operation
result = db["breakoutMH"].delete_many(query)
print(f"Deleted {result.deleted_count} documents.")
result = db["breakoutM2H"].delete_many(query)
print(f"Deleted {result.deleted_count} documents.")
result = db["breakoutML"].delete_many(query)
print(f"Deleted {result.deleted_count} documents.")
result = db["breakoutM2L"].delete_many(query)
print(f"Deleted {result.deleted_count} documents.")