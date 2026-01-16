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
            "Dch",
            format="%.2f"),
    "systemtime": "systime",
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
            "f10ch",
            format="%.2f"),
    "forecast_day_PCT7_change":  st.column_config.NumberColumn(
            "forecast_day_PCT7_change",
            format="%.2f"),
    "forecast_day_PCT5_change":  st.column_config.NumberColumn(
            "forecast_day_PCT5_change",
            format="%.2f"),
    "filter5": "filter5",
    "filter": "filter",
    "filter3": "filter3",
    "processor": "processor"
}

column_config_ml={
    "scrip": "scrip",
    "PCT_day_change": st.column_config.NumberColumn(
            "Dch",
            format="%.2f"),
    "industry": "industry",
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
    "kNeighboursValue_reg":  st.column_config.NumberColumn(
            "kNeighboursValue_reg",
            format="%.2f"),
    "mlpValue_reg":  st.column_config.NumberColumn(
            "mlpValue_reg",
            format="%.2f"),
    "kNeighboursValue_reg_merged":  st.column_config.NumberColumn(
            "kNeighboursValue_reg_merged",
            format="%.2f"),
    "mlpValue_reg_merged":  st.column_config.NumberColumn(
            "mlpValue_reg_merged",
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
            "f10ch",
            format="%.2f"),
    "forecast_day_PCT7_change":  st.column_config.NumberColumn(
            "forecast_day_PCT7_change",
            format="%.2f"),
    "forecast_day_PCT5_change":  st.column_config.NumberColumn(
            "forecast_day_PCT5_change",
            format="%.2f"),
    "filter5": "filter5",
    "filter": "filter",
    "filter3": "filter3"
}

column_config_merged={
    "scrip": "scrip",
    "PCT_day_change": st.column_config.NumberColumn(
            "Dch",
            format="%.2f"),
    "systemtime": "systime",
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
            "f10ch",
            format="%.2f"),
    "forecast_day_PCT7_change":  st.column_config.NumberColumn(
            "forecast_day_PCT7_change",
            format="%.2f"),
    "forecast_day_PCT5_change":  st.column_config.NumberColumn(
            "forecast_day_PCT5_change",
            format="%.2f"),
    "filter5": "filter5",
    "filter": "filter",
    "filter3": "filter3",
    "processor": "processor",
    "systemtime_merged": "systime_merged",
    "processor_merged": "processor_merged"
}

column_order_default=["scrip",
    "PCT_day_change",
    "systemtime",
    "mlData",
    "forecast_day_PCT10_change",
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
    "forecast_day_PCT7_change",
    "forecast_day_PCT5_change",
    "filter5",
    "filter",
    "filter3",
    "processor"
]

column_order_ml=["scrip",
    "PCT_day_change",
    "industry",
    "PCT_change",
    "PCT_day_change_pre1",
    "PCT_day_change_pre2",
    "forecast_day_PCT10_change",
    "highTail",
    "lowTail",
    "kNeighboursValue_reg",
    "mlpValue_reg",
    "kNeighboursValue_reg_merged",
    "mlpValue_reg_merged",
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
    "forecast_day_PCT7_change",
    "forecast_day_PCT5_change",
    "filter5",
    "filter",
    "filter3",
]

column_order_merged=["scrip",
    "PCT_day_change",
    "systemtime",
    "mlData",
    "forecast_day_PCT10_change",
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
    "forecast_day_PCT7_change",
    "forecast_day_PCT5_change",
    "filter5",
    "filter",
    "filter3",
    "processor",
    "systemtime_merged",
    "processor_merged"
]

column_order_p=["scrip",
    "PCT_day_change",
    "systemtime",
    "processor",
    "mlData",
    "forecast_day_PCT10_change",
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
    "forecast_day_PCT7_change",
    "forecast_day_PCT5_change",
    "filter5",
    "filter",
    "filter3",
    "systemtime_merged",
    "processor_merged"
]

chartlink1=False
chartlink0=False

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

def highlight_category_column(value):
    """Highlights the entire row based on the 'Category' column value."""

    
    if "0@@CROSSED" in value and "2@" in value and "CROSSED1DayH@GT2@" not in value and "CROSSED1DayL@LT-2@" not in value:
        return 'background-color: #3EB9FB'
    elif "0@@SUPER" in value and "2@" in value:
        return 'background-color: #3EB9FB'
    elif "0@@CROSSED" in value and "1@" in value:
        return 'background-color: #CBEDFF'
    elif "0@@SUPER" in value and "1@" in value:
        return 'background-color: #CBEDFF'
    elif "0@@CROSSED" in value and "6@" in value and "CROSSED1DayL@GT6" not in value and "CROSSED1DayH@LT-6" not in value:
        return 'background-color: #fff4cf'
    elif "0@@SUPER" in value and "6@" in value:
        return 'background-color: #fff4cf'
    
#     if "MLBuy0" in value or "MLBuy1" in value or "MLBuy2" in value:
#         return 'background-color: #E0FFDE'
#     if "MLSell0" in value or "MLSell1" in value or "MLSell2" in value:
#         return 'background-color: #FCCFD2'
    
#     else:
#         if "0@@CROSSED" in value:
#                 return 'background-color: #FBED78'
#         if "0@@SUPER" in value:
#                 return 'background-color: #3EB9FB'

f10_cols = [
    "forecast_day_PCT10_change",
    "forecast_day_PCT7_change",
    "forecast_day_PCT5_change",
]

def apply_f10_buy(row):
    color = highlight_category_column_f10_buy(
        row["forecast_day_PCT10_change"],
        row["forecast_day_PCT7_change"],
        row["forecast_day_PCT5_change"],
    )
    # use the same color for every column in the row
    return pd.Series(color, index=row.index)


def apply_f10_sell(row):
    color = highlight_category_column_f10_sell(
        row["forecast_day_PCT10_change"],
        row["forecast_day_PCT7_change"],
        row["forecast_day_PCT5_change"],
    )
    # use the same color for every column in the row
    return pd.Series(color, index=row.index)


def highlight_category_column_f10_buy(value10, value7, value5):
    """Highlights the entire row based on the 'Category' column value."""
    if float(value10) > 2 and float(value10) < 10:
        return 'background-color: #3EB9FB'
    elif float(value10) > -2 and float(value10) < 3 and float(value7) < 3 and float(value5) < 3 and float(value7) >-2 and float(value5) > -2:
        return 'background-color: #CBEDFF'
    elif float(value10) < -6:
        return 'background-color: #fff4cf'
    elif float(value10) < -3:
        return 'background-color: #F9FAFB'
    else:
        return 'background-color: #A1A1A1'
        
def highlight_category_column_f10_sell(value10, value7, value5):
    """Highlights the entire row based on the 'Category' column value."""
    if float(value10) < -2 and float(value10) > -10:
        return 'background-color: #3EB9FB'
    elif float(value10) < 2 and float(value10) > -3 and float(value7) > -3 and float(value5) > -3 and float(value7) < 2 and float(value5) < 2:
        return 'background-color: #CBEDFF'
    elif float(value10) > 6:
        return 'background-color: #fff4cf'
    elif float(value10) > 3:
        return 'background-color: #F9FAFB'
    else:
        return 'background-color: #A1A1A1'

def apply_f10_buy_00(row):
    color = highlight_category_column_f10_buy_00(
        row["forecast_day_PCT10_change"],
        row["forecast_day_PCT7_change"],
        row["forecast_day_PCT5_change"],
    )
    # use the same color for every column in the row
    return pd.Series(color, index=row.index)

def apply_f10_sell_00(row):
    color = highlight_category_column_f10_sell_00(
        row["forecast_day_PCT10_change"],
        row["forecast_day_PCT7_change"],
        row["forecast_day_PCT5_change"],
    )
    # use the same color for every column in the row
    return pd.Series(color, index=row.index)

def highlight_category_column_f10_buy_00(value10, value7, value5):
    """Highlights the entire row based on the 'Category' column value."""
    if float(value10) > 7 and float(value7) > 7 and float(value5) > 7 and ( float(value10) > 10 or float(value7) > 10 or float(value5) > 10):
        return 'background-color: #3EB9FB'
    elif float(value10) > -2 and float(value10) < 1 and float(value7) < 2 and float(value5) < 2 and float(value7) >-2 and float(value5) > -2:
        return 'background-color: #CBEDFF'
    elif float(value10) < -7:
        return 'background-color: #fff4cf'
    elif float(value10) < -3:
        return 'background-color: #A1A1A1'
    else:
        return 'background-color: #A1A1A1'
        
def highlight_category_column_f10_sell_00(value10, value7, value5):
    """Highlights the entire row based on the 'Category' column value."""
    if float(value10) < -7 and float(value7) < -7 and float(value5) < -7 and ( float(value10) < -10 or float(value7) < -10 or float(value5) < -10):
        return 'background-color: #3EB9FB'
    elif float(value10) < 2 and float(value10) > -1 and float(value7) > -2 and float(value5) > -2 and float(value7) < 2 and float(value5) < 2:
        return 'background-color: #CBEDFF'
    elif float(value10) > 7:
        return 'background-color: #fff4cf'
    elif float(value10) > 3:
        return 'background-color: #A1A1A1'
    else:
        return 'background-color: #A1A1A1'

def highlight_category_column_super(value):
    """Highlights the entire row based on the 'Category' column value."""
    if "0@@SUPER" in value:
        return 'background-color: #CBC3E3'

def apply_f10_buy_01(row):
    color = highlight_category_column_f10_buy_01(
        row["forecast_day_PCT10_change"],
        row["forecast_day_PCT7_change"],
        row["forecast_day_PCT5_change"],
    )
    # use the same color for every column in the row
    return pd.Series(color, index=row.index)

def apply_f10_sell_01(row):
    color = highlight_category_column_f10_sell_01(
        row["forecast_day_PCT10_change"],
        row["forecast_day_PCT7_change"],
        row["forecast_day_PCT5_change"],
    )
    # use the same color for every column in the row
    return pd.Series(color, index=row.index)

def highlight_category_column_f10_buy_01(value10, value7, value5):
    """Highlights the entire row based on the 'Category' column value."""
    if float(value10) > 7 and float(value7) > 7 and float(value5) > 7 and ( float(value10) > 10 or float(value7) > 10 or float(value5) > 10):
        return 'background-color: #3EB9FB'
    elif float(value10) > -2 and float(value10) < 1 and float(value7) < 2 and float(value5) < 2 and float(value7) >-2 and float(value5) > -2:
        return 'background-color: #CBEDFF'
    elif float(value10) < -7:
        return 'background-color: #A1A1A1'
    elif float(value10) < -3:
        return 'background-color: #A1A1A1'
    else:
        return 'background-color: #A1A1A1'
        
def highlight_category_column_f10_sell_01(value10, value7, value5):
    """Highlights the entire row based on the 'Category' column value."""
    if float(value10) < -7 and float(value7) < -7 and float(value5) < -7 and ( float(value10) < -10 or float(value7) < -10 or float(value5) < -10):
        return 'background-color: #3EB9FB'
    elif float(value10) < 2 and float(value10) > -1 and float(value7) > -2 and float(value5) > -2 and float(value7) < 2 and float(value5) < 2:
        return 'background-color: #CBEDFF'
    elif float(value10) > 7:
        return 'background-color: #A1A1A1'
    elif float(value10) > 3:
        return 'background-color: #A1A1A1'
    else:
        return 'background-color: #A1A1A1'

def highlight_category_column_super(value):
    """Highlights the entire row based on the 'Category' column value."""
    if "0@@SUPER" in value:
        return 'background-color: #CBC3E3'


def getdf(collection_name):
    collection = dbcl[collection_name]
    df = pd.DataFrame(list(collection.find()))
    try:
        df['PCT_day_change'] = pd.to_numeric(df['PCT_day_change'])
        df['PCT_change'] = pd.to_numeric(df['PCT_change'], errors='coerce')
        df['PCT_day_change_pre1'] = pd.to_numeric(df['PCT_day_change_pre1'], errors='coerce')
        df['PCT_day_change_pre2'] = pd.to_numeric(df['PCT_day_change_pre2'], errors='coerce')

        df['highTail'] = pd.to_numeric(df['highTail'], errors='coerce')
        df['lowTail'] = pd.to_numeric(df['lowTail'], errors='coerce')
        df['year5HighChange'] = pd.to_numeric(df['year5HighChange'], errors='coerce')
        df['yearHighChange'] = pd.to_numeric(df['year5HighChange'], errors='coerce')
        df['yearLowChange'] = pd.to_numeric(df['yearLowChange'], errors='coerce')
        df['month3HighChange'] = pd.to_numeric(df['month3HighChange'], errors='coerce')
        df['month3LowChange'] = pd.to_numeric(df['month3LowChange'], errors='coerce')
        df['monthHighChange'] = pd.to_numeric(df['monthHighChange'], errors='coerce')
        df['monthLowChange'] = pd.to_numeric(df['monthLowChange'], errors='coerce')
        df['week2HighChange'] = pd.to_numeric(df['week2HighChange'], errors='coerce')
        df['week2LowChange'] = pd.to_numeric(df['week2LowChange'], errors='coerce')
        df['weekHighChange'] = pd.to_numeric(df['weekHighChange'], errors='coerce')
        df['weekLowChange'] = pd.to_numeric(df['weekLowChange'], errors='coerce')
        df['forecast_day_PCT10_change'] = pd.to_numeric(df['forecast_day_PCT10_change'], errors='coerce')
        df['forecast_day_PCT7_change'] = pd.to_numeric(df['forecast_day_PCT7_change'], errors='coerce')
        df['forecast_day_PCT5_change'] = pd.to_numeric(df['forecast_day_PCT5_change'], errors='coerce')
        df['systemtime'] = pd.to_datetime(df['systemtime']).dt.time.astype(str)
        df['mlData'] = df['mlData'].fillna('').astype(str)
    except KeyError as e:
        print(f"")
    return df

def getintersectdf(collection_name1, collection_name2):
    collection1 = dbcl[collection_name1]
    collection2 = dbcl[collection_name2]
    df1 = pd.DataFrame(list(collection1.find()))
    df2 = pd.DataFrame(list(collection2.find()))
    expected_columns = list(set(df1.columns))
    df = pd.DataFrame(columns=expected_columns)
    try:
        df = df1.merge(
            df2,
            on='scrip',
            how='inner',
            suffixes=('', '_merged')
        )
        df['PCT_day_change'] = pd.to_numeric(df['PCT_day_change'])
        df['PCT_change'] = pd.to_numeric(df['PCT_change'], errors='coerce')
        df['PCT_day_change_pre1'] = pd.to_numeric(df['PCT_day_change_pre1'], errors='coerce')
        df['PCT_day_change_pre2'] = pd.to_numeric(df['PCT_day_change_pre2'], errors='coerce')

        df['highTail'] = pd.to_numeric(df['highTail'], errors='coerce')
        df['lowTail'] = pd.to_numeric(df['lowTail'], errors='coerce')
        df['year5HighChange'] = pd.to_numeric(df['year5HighChange'], errors='coerce')
        df['yearHighChange'] = pd.to_numeric(df['year5HighChange'], errors='coerce')
        df['yearLowChange'] = pd.to_numeric(df['yearLowChange'], errors='coerce')
        df['month3HighChange'] = pd.to_numeric(df['month3HighChange'], errors='coerce')
        df['month3LowChange'] = pd.to_numeric(df['month3LowChange'], errors='coerce')
        df['monthHighChange'] = pd.to_numeric(df['monthHighChange'], errors='coerce')
        df['monthLowChange'] = pd.to_numeric(df['monthLowChange'], errors='coerce')
        df['week2HighChange'] = pd.to_numeric(df['week2HighChange'], errors='coerce')
        df['week2LowChange'] = pd.to_numeric(df['week2LowChange'], errors='coerce')
        df['weekHighChange'] = pd.to_numeric(df['weekHighChange'], errors='coerce')
        df['weekLowChange'] = pd.to_numeric(df['weekLowChange'], errors='coerce')
        df['forecast_day_PCT10_change'] = pd.to_numeric(df['forecast_day_PCT10_change'], errors='coerce')
        df['forecast_day_PCT7_change'] = pd.to_numeric(df['forecast_day_PCT7_change'], errors='coerce')
        df['forecast_day_PCT5_change'] = pd.to_numeric(df['forecast_day_PCT5_change'], errors='coerce')
        df['systemtime'] = pd.to_datetime(df['systemtime']).dt.time.astype(str)
        df['systemtime_merged'] = pd.to_datetime(df['systemtime_merged']).dt.time.astype(str)
        df['mlData'] = df['mlData'].fillna('').astype(str)
    except KeyError as e:
        print(f"")

    return df

def getintersectdf_ml(collection_name1, collection_name2):
    collection1 = dbnse[collection_name1]
    collection2 = dbnse[collection_name2]
    df1 = pd.DataFrame(list(collection1.find()))
    df2 = pd.DataFrame(list(collection2.find()))
    expected_columns = list(set(df1.columns))
    df = pd.DataFrame(columns=expected_columns)
    try:
        df = df1.merge(
            df2,
            on='scrip',
            how='inner',
            suffixes=('', '_merged')
        )
        df['PCT_day_change'] = pd.to_numeric(df['PCT_day_change'])
        df['PCT_change'] = pd.to_numeric(df['PCT_change'], errors='coerce')
        df['PCT_day_change_pre1'] = pd.to_numeric(df['PCT_day_change_pre1'], errors='coerce')
        df['PCT_day_change_pre2'] = pd.to_numeric(df['PCT_day_change_pre2'], errors='coerce')

        df['highTail'] = pd.to_numeric(df['highTail'], errors='coerce')
        df['lowTail'] = pd.to_numeric(df['lowTail'], errors='coerce')
        df['year5HighChange'] = pd.to_numeric(df['year5HighChange'], errors='coerce')
        df['yearHighChange'] = pd.to_numeric(df['year5HighChange'], errors='coerce')
        df['yearLowChange'] = pd.to_numeric(df['yearLowChange'], errors='coerce')
        df['month3HighChange'] = pd.to_numeric(df['month3HighChange'], errors='coerce')
        df['month3LowChange'] = pd.to_numeric(df['month3LowChange'], errors='coerce')
        df['monthHighChange'] = pd.to_numeric(df['monthHighChange'], errors='coerce')
        df['monthLowChange'] = pd.to_numeric(df['monthLowChange'], errors='coerce')
        df['week2HighChange'] = pd.to_numeric(df['week2HighChange'], errors='coerce')
        df['week2LowChange'] = pd.to_numeric(df['week2LowChange'], errors='coerce')
        df['weekHighChange'] = pd.to_numeric(df['weekHighChange'], errors='coerce')
        df['weekLowChange'] = pd.to_numeric(df['weekLowChange'], errors='coerce')
        df['forecast_day_PCT10_change'] = pd.to_numeric(df['forecast_day_PCT10_change'], errors='coerce')
        df['forecast_day_PCT7_change'] = pd.to_numeric(df['forecast_day_PCT7_change'], errors='coerce')
        df['forecast_day_PCT5_change'] = pd.to_numeric(df['forecast_day_PCT5_change'], errors='coerce')
        df['kNeighboursValue_reg'] = pd.to_numeric(df['kNeighboursValue_reg'], errors='coerce')
        df['mlpValue_reg'] = pd.to_numeric(df['mlpValue_reg'], errors='coerce')
        df['kNeighboursValue_reg_merged'] = pd.to_numeric(df['kNeighboursValue_reg_merged'], errors='coerce')
        df['mlpValue_reg_merged'] = pd.to_numeric(df['mlpValue_reg_merged'], errors='coerce')
    except KeyError as e:
        print(f"")

    return df

def render(st, df, name, height=200, color='NA', column_order=column_order_default, column_conf=column_config_default, renderml=False, renderf10buy=False, renderf10sell=False, f10=0, renderf10buy00=False, renderf10sell00=False, renderf10buy01=False, renderf10sell01=False):
    st.write("********"+ name + "********")
    # Main Code Execution
    if renderf10buy:
        df_styled = highlight_category_row(df, color=color)
        df_styled = df_styled.apply(apply_f10_buy, axis=1)
        st.dataframe(df_styled, height=height, column_order=column_order, column_config=column_conf, use_container_width=True)
    elif renderf10sell:
        df_styled = highlight_category_row(df, color=color)
        df_styled = df_styled.apply(apply_f10_sell, axis=1)
        st.dataframe(df_styled, height=height, column_order=column_order, column_config=column_conf, use_container_width=True)
    elif renderf10buy00:
        df_styled = highlight_category_row(df, color=color)
        df_styled = df_styled.apply(apply_f10_buy_00, axis=1)
        st.dataframe(df_styled, height=height, column_order=column_order, column_config=column_conf, use_container_width=True)
    elif renderf10sell00:
        df_styled = highlight_category_row(df, color=color)
        df_styled = df_styled.apply(apply_f10_sell_00, axis=1)
        st.dataframe(df_styled, height=height, column_order=column_order, column_config=column_conf, use_container_width=True)
    elif renderf10buy01:
        df_styled = highlight_category_row(df, color=color)
        df_styled = df_styled.apply(apply_f10_buy_01, axis=1)
        st.dataframe(df_styled, height=height, column_order=column_order, column_config=column_conf, use_container_width=True)
    elif renderf10sell01:
        df_styled = highlight_category_row(df, color=color)
        df_styled = df_styled.apply(apply_f10_sell_01, axis=1)
        st.dataframe(df_styled, height=height, column_order=column_order, column_config=column_conf, use_container_width=True)
    elif renderml:
        df_styled = highlight_category_row(df, color=color)
        st.dataframe(df_styled, height=height, column_order=column_order, column_config=column_conf, use_container_width=True)
    elif not df.empty:
        df_styled = highlight_category_row(df, color=color)
        if(chartlink1) and color =='LG':
            df_styled = df_styled.applymap(highlight_category_column, subset=['mlData'])
        elif ((chartlink0) and (color == 'G' or color == 'R')):
            df_styled = df_styled.applymap(highlight_category_column, subset=['mlData'])
        else:
            df_styled = df_styled.applymap(highlight_category_column, subset=['mlData'])
        # Apply the second style *directly* to the Styler object
        st.dataframe(df_styled, height=height, column_order=column_order, column_config=column_conf, use_container_width=True)
    else:
        st.dataframe(df, height=height, column_order=column_order, column_config=column_conf, use_container_width=True)

def render_rawdata(st, df, name, height=200, color='NA', column_order=column_order_default, column_conf=column_config_default):
    st.write("********"+ name + "********")
    st.dataframe(df, height=height, use_container_width=True)