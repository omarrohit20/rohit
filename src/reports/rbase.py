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

def highlight_category_row(df, color='NA'):
    """Highlights the entire row based on the 'Category' column value."""
    styled_df = ''
    if color == 'G':
        styled_df = df.style.set_properties(**{'background-color': '#B0FFD0', 'color': 'black'})
    elif color == 'R':
        styled_df = df.style.set_properties(**{'background-color': '#FA866E', 'color': 'black'})
    elif color == 'LG':
        styled_df = df.style.set_properties(**{'background-color': '#A1A1A1', 'color': 'black'})
    return styled_df

def getdf(collection_name):
    collection = dbcl[collection_name]
    df = pd.DataFrame(list(collection.find()))
    return df

def render(st, name, collection, height=300, color='NA', column_order=column_order_default, column_conf=column_config_default):
    st.write("********"+ name.upper() + "********")
    df = getdf(collection)
    if color != 'NA':
        df = highlight_category_row(df, color=color)
    st.dataframe(df, height=height, column_order=column_order, column_config=column_conf, use_container_width=True)