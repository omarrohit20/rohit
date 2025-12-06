# Create a streamlit app that shows the mongodb data
import pandas as pd
import numpy as np
import pymongo
from pymongo import MongoClient

connection = MongoClient('localhost', 27017)
dbcl = connection.chartlink
dbnse = connection.Nsedata

column_config_default={
    "scrip": "scrip",
    "PCT_day_change": "PCTDaych",
    "systemtime": "systemtime",
    "industry": "industry",
    "mlData": "mlData",
    "PCT_change": "PCT_change",
    "PCT_day_change_pre1": "PCT_day_change_pre1",
    "PCT_day_change_pre2": "PCT_day_change_pre2",
    "highTail": "highTail",
    "lowTail": "lowTail",
    "year5HighChange": "year5HighChange",
    "yearHighChange": "yearHighChange",
    "yearLowChange": "yearLowChange",
    "month3HighChange": "month3HighChange",
    "month3LowChange": "month3LowChange",
    "monthHighChange": "monthHighChange",
    "monthLowChange": "monthLowChange",
    "week2HighChange": "week2HighChange",
    "week2LowChange": "week2LowChange",
    "weekHighChange": "weekHighChange",
    "weekLowChange": "weekLowChange",
    "forecast_day_PCT10_change": "forecast_day_PCT10_change",
    "filter5": "filter5",
    "filter": "filter",
    "filter3": "filter3",
    "processor": "processor"
}

column_order_default=["scrip",
    "PCT_day_change",
    "systemtime",
    "industry",
    "mlData",
    "PCT_change",
    "PCT_day_change_pre1",
    "PCT_day_change_pre2",
    "highTail",
    "lowTail",
    "year5HighChange",
    "yearHighChange",
    "yearLowChange",
    "month3HighChange",
    "month3LowChange",
    "monthHighChange",
    "monthLowChange",
    "week2HighChange",
    "week2LowChange",
    "weekHighChange",
    "weekLowChange",
    "forecast_day_PCT10_change",
    "filter5",
    "filter",
    "filter3",
    "processor"
]

def getdf(collection_name):
    collection = dbcl[collection_name]
    df = pd.DataFrame(list(collection.find()))
    return df

def render(st, name, collection, column_order=column_order_default, column_conf=column_config_default):
    st.write("********"+ name.upper() + "********")
    df = getdf(collection)
    st.dataframe(df, column_order=column_order, column_config=column_conf, use_container_width=True)