# Create a streamlit app that shows the mongodb data
import pandas as pd
import numpy as np
import pymongo
import streamlit as st
from pymongo import MongoClient

connection = MongoClient('localhost', 27017)
dbcl = connection.chartlink
dbnse = connection.Nsedata

column_config_default={
    "scrip": "scrip",
    "PCT_day_change": st.column_config.NumberColumn(
            "PCTDaych",
            format="%.2f"),
    "systemtime": "systemtime",
    "industry": "industry",
    "mlData": "mlData",
    "PCT_change": st.column_config.NumberColumn(
            "PCT_change",
            format="%.2f"),
    "PCT_day_change_pre1": st.column_config.NumberColumn(
            "PCT_day_change_pre1",
            format="%.2f"),
    "PCT_day_change_pre2":  st.column_config.NumberColumn(
            "PCT_day_change_pre2",
            format="%.2f"),
    "highTail":  st.column_config.NumberColumn(
            "highTail",
            format="%.2f"),
    "lowTail":  st.column_config.NumberColumn(
            "lowTail",
            format="%.2f"),
    "year5HighChange":  st.column_config.NumberColumn(
            "year5HighChange",
            format="%.2f"),
    "yearHighChange":  st.column_config.NumberColumn(
            "yearHighChange",
            format="%.2f"),
    "yearLowChange":  st.column_config.NumberColumn(
            "yearLowChange",
            format="%.2f"),
    "month3HighChange":  st.column_config.NumberColumn(
            "month3HighChange",
            format="%.2f"),
    "month3LowChange":  st.column_config.NumberColumn(
            "month3LowChange",
            format="%.2f"),
    "monthHighChange":  st.column_config.NumberColumn(
            "monthHighChange",
            format="%.2f"),
    "monthLowChange":  st.column_config.NumberColumn(
            "monthLowChange",
            format="%.2f"),
    "week2HighChange":  st.column_config.NumberColumn(
            "week2HighChange",
            format="%.2f"),
    "week2LowChange":  st.column_config.NumberColumn(
            "week2LowChange",
            format="%.2f"),
    "weekHighChange":  st.column_config.NumberColumn(
            "weekHighChange",
            format="%.2f"),
    "weekLowChange":  st.column_config.NumberColumn(
            "weekLowChange",
            format="%.2f"),
    "forecast_day_PCT10_change":  st.column_config.NumberColumn(
            "forecast_day_PCT10_change",
            format="%.2f"),
    "filter5": "filter5",
    "filter": "filter",
    "filter3": "filter3",
    "processor": "processor"
}

column_order_default=["scrip",
    "PCT_day_change",
    "systemtime",
    "mlData",
    "industry",
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
        styled_df = df.style.set_properties(**{'background-color': '#E0FFDE', 'color': 'black'})
    elif color == 'R':
        styled_df = df.style.set_properties(**{'background-color': '#FCCFD2', 'color': 'black'})
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