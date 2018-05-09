import json, datetime, time, copy, sys, csv, logging
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from pymongo import MongoClient
from multiprocessing.dummy import Pool as ThreadPool

import numpy as np
import talib 
from talib.abstract import *

connection = MongoClient('localhost',27017)
db = connection.Nsedata
db.drop_collection('RbuyAll')
db.drop_collection('RbuyYearHigh')
db.drop_collection('RbuyYearLow')
db.drop_collection('RbuyUpTrend')
db.drop_collection('RbuyFinal')
db.drop_collection('RbuyFinal1')
db.drop_collection('RbuyPattern')
db.drop_collection('RbuyPattern1')
db.drop_collection('RbuyPattern2')
db.drop_collection('RbuyOthers')
db.drop_collection('RsellAll')
db.drop_collection('RsellYearHigh')
db.drop_collection('RsellYearLow')
db.drop_collection('RsellUpTrend')
db.drop_collection('RsellFinal')
db.drop_collection('RsellFinal1')
db.drop_collection('RsellPattern')
db.drop_collection('RsellPattern1')
db.drop_collection('RsellPattern2')
db.drop_collection('RsellOthers')
db.drop_collection('regressionHistoryScrip')
