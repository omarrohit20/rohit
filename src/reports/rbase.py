# Create a streamlit app that shows the mongodb data
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import pymongo
import streamlit as st
from pymongo import MongoClient

connection = MongoClient('localhost', 27017)
dbcl = connection.chartlink
dbnse = connection.Nsedata

# Global collection filter
selected_collection = None

column_config_default={
    "scrip": "scrip",
    "PCT_day_change": st.column_config.NumberColumn(
            "Dch",
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

column_config_result={
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
    "kNeighboursValue_reg_other":  st.column_config.NumberColumn(
            "kNeighboursValue_reg_other",
            format="%.2f"),
    "mlpValue_reg_other":  st.column_config.NumberColumn(
            "mlpValue_reg_other",
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
    "intradaytech": "intradaytech",
    "index": "index"
}

column_config_merged={
    "scrip": "scrip",
    "PCT_day_change": st.column_config.NumberColumn(
            "Dch",
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
    "systemtime_merged": "systemtime_merged",
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

column_order_result=["scrip",
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
    "kNeighboursValue_reg_other",
    "mlpValue_reg_other",
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
    "intradaytech",
    "index"
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
testLearning=False

 # Function to create cumulative data in 10-minute intervals
def parse_timestamp(item):
    # Prefer explicit systemtime stored as string in DB
    sys_ts = item.get('systemtime')
    if isinstance(sys_ts, str):
        try:
            return datetime.strptime(sys_ts, '%Y-%m-%d %H:%M:%S')
        except Exception:
            # Fallback to ISO parsing if format differs
            try:
                return datetime.fromisoformat(sys_ts.replace('Z', '+00:00'))
            except Exception:
                pass
    # Other possible fields
    ts = item.get('timestamp') or item.get('time') or item.get('datetime')
    if isinstance(ts, str):
        try:
            return datetime.fromisoformat(ts.replace('Z', '+00:00'))
        except Exception:
            return None
    if ts:
        return ts
    # Last resort: use ObjectId generation time
    try:
        return item.get('_id').generation_time
    except Exception:
        return None

def create_cumulative_data(data, label):
    if not data:
        return [], []
    
    # Extract timestamps using table's stored time
    timestamps = []
    for item in data:
        ts = parse_timestamp(item)
        if ts:
            timestamps.append(ts)
    
    if not timestamps:
        return [], []
    
    # Sort timestamps
    timestamps.sort()
    
    # Find the earliest timestamp and round down to 10-minute interval
    min_time = timestamps[0].replace(second=0, microsecond=0)
    min_time = min_time.replace(minute=(min_time.minute // 10) * 10)
    
    # Find the latest timestamp
    max_time = timestamps[-1]
    
    # Create 10-minute intervals
    intervals = []
    cumulative_counts = []
    current_time = min_time
    cumulative_count = 0
    
    while current_time <= max_time + timedelta(minutes=10):
        # Count records up to current_time
        count = sum(1 for ts in timestamps if ts <= current_time)
        intervals.append(current_time)
        cumulative_counts.append(count)
        current_time += timedelta(minutes=10)
    
    return intervals, cumulative_counts
            
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

def highlight_category_column(value, systemtime):
    """Highlights the entire row based on the 'Category' column value."""

    if "0@@CROSSED" in value and "6@" in value and "CROSSED1DayL@GT6" not in value and "CROSSED1DayH@LT-6" not in value:
        return 'background-color: #fff4cf'
    elif "0@@SUPER" in value and "6@" in value:
        return 'background-color: #fff4cf'
    
    count_9_3 = 0
    try:
        coll = dbcl['09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)']
        count_9_3 = coll.count_documents({'systemtime': {'$regex': '9:3'}})
    except Exception:
        pass

    if (count_9_3 > 6 and "H@" in value and "09:" in systemtime):
        return 

    count_9_3 = 0
    try:
        coll = dbcl['09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)']
        count_9_3 = coll.count_documents({'systemtime': {'$regex': '9:3'}})
    except Exception:
        pass

    if (count_9_3 > 6 and "L@" in value and "09:" in systemtime):
        return 

    count_9_3_s = 0
    try:
        coll = dbcl['supertrend-morning-buy']
        count_9_3_s = coll.count_documents({'systemtime': {'$regex': '09:'}})
    except Exception:
        pass

    if (count_9_3_s > 6 and "H@" in value and "09:" in systemtime):
        return

    count_9_3_s = 0
    try:
        coll = dbcl['supertrend-morning-sell']
        count_9_3_s = coll.count_documents({'systemtime': {'$regex': '09:'}})
    except Exception:
        pass

    if (count_9_3_s > 6 and "L@" in value and "09:" in systemtime):
        return

    

    if "0@@CROSSED" in value and "7@" in value and "CROSSED1DayH@GT7@" not in value and "CROSSED1DayL@LT-7@" not in value:
        return 'background-color: #800080'
    elif "0@@SUPER" in value and "7@" in value:
        return 'background-color: #800080'
    elif "0@@CROSSED" in value and "2@" in value and "CROSSED1DayH@GT2@" not in value and "CROSSED1DayL@LT-2@" not in value:
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

def apply_highlight_column(row):
    """Apply highlight_category_column to mlData column with systemtime context."""
    styles = pd.Series('', index=row.index)
    try:
        ml_value = str(row.get('mlData', ''))
        systime = str(row.get('systemtime', ''))
        styles['mlData'] = highlight_category_column(ml_value, systime) or ''
    except Exception:
        pass
    return styles

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
        row["systemtime"],
    )
    # use the same color for every column in the row
    return pd.Series(color, index=row.index)

def apply_f10_sell(row):
    color = highlight_category_column_f10_sell(
        row["forecast_day_PCT10_change"],
        row["forecast_day_PCT7_change"],
        row["forecast_day_PCT5_change"],
        row["systemtime"],
    )
    # use the same color for every column in the row
    return pd.Series(color, index=row.index)

def highlight_category_column_f10_buy(value10, value7, value5, systemtime):
    """Highlights the entire row based on the 'Category' column value."""
    count_9_3 = 0
    try:
        coll = dbcl['09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)']
        count_9_3 = coll.count_documents({'systemtime': {'$regex': '9:3'}})
    except Exception:
        pass

    count_9_3_s = 0
    try:
        coll = dbcl['supertrend-morning-buy']
        count_9_3_s = coll.count_documents({'systemtime': {'$regex': '09:'}})
    except Exception:
        pass

    if (count_9_3 > 6 or count_9_3_s > 6) and "9:" in systemtime:
        return 'background-color: #A1A1A1'

    if float(value10) >= 7 and float(value7) > -2 and float(value5) > -2 and (float(value7) > (float(value10)-5) or float(value5) > (float(value10)-5)):
        return 'background-color: #800080'
    elif float(value10) >= 2 and float(value10) < 7 and float(value7) > -3 and float(value5) > -3 and (float(value7) > (float(value10)-4) or float(value5) > (float(value10)-4)):
        return 'background-color: #3EB9FB'
    elif float(value10) >= -2 and float(value10) < 2 and float(value7) < 2 and float(value5) < 2 and float(value7) >-2 and float(value5) > -2:
        return 'background-color: #CBEDFF'
    elif float(value10) <= -9 and float(value7) < -1 and float(value5) < -1:
        return 'background-color: #ffd546'
    elif float(value10) <= -6 and float(value7) < 0 and float(value5) < 0:
        return 'background-color: #fff0bc'
    elif float(value10) <= -3 and float(value7) < 2 and float(value5) < 2:
        return 'background-color: #F9FAFB'
    else:
        return 'background-color: #A1A1A1'   
        
def highlight_category_column_f10_sell(value10, value7, value5, systemtime):
    count_9_3 = 0
    try:
        coll = dbcl['09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)']
        count_9_3 = coll.count_documents({'systemtime': {'$regex': '9:3'}})
    except Exception:
        pass

    count_9_3_s = 0
    try:
        coll = dbcl['supertrend-morning-sell']
        count_9_3_s = coll.count_documents({'systemtime': {'$regex': '09:'}})
    except Exception:
        pass

    if (count_9_3 > 6 or count_9_3_s > 6) and "9:" in systemtime:
        return 'background-color: #A1A1A1'

    """Highlights the entire row based on the 'Category' column value."""
    if float(value10) <= -7 and float(value7) < 2 and float(value5) < 2 and (float(value7) < (float(value10)+5) or float(value5) < (float(value10)+5)):
        return 'background-color: #800080'
    elif float(value10) <= -2 and float(value10) > -7 and float(value7) < 3 and float(value5) < 3 and (float(value7) < (float(value10)+4) or float(value5) < (float(value10)+4)):
        return 'background-color: #3EB9FB'
    elif float(value10) <= 2 and float(value10) > -2 and float(value7) > -2 and float(value5) > -2 and float(value7) < 2 and float(value5) < 2:
        return 'background-color: #CBEDFF'
    elif float(value10) >= 9 and float(value7) > 1 and float(value5) > 1:
        return 'background-color: #ffd546'
    elif float(value10) >= 6 and float(value7) > 0 and float(value5) > 0:
        return 'background-color: #fff0bc'
    elif float(value10) >= 3 and float(value7) > -2 and float(value5) > -2:
        return 'background-color: #F9FAFB'
    else:
        return 'background-color: #A1A1A1'

def apply_f10_buy_00(row):
    color = highlight_category_column_f10_buy_00(
        row["forecast_day_PCT10_change"],
        row["forecast_day_PCT7_change"],
        row["forecast_day_PCT5_change"],
        row["systemtime"],
    )
    # use the same color for every column in the row
    return pd.Series(color, index=row.index)

def apply_f10_sell_00(row):
    color = highlight_category_column_f10_sell_00(
        row["forecast_day_PCT10_change"],
        row["forecast_day_PCT7_change"],
        row["forecast_day_PCT5_change"],
        row["systemtime"],
    )
    # use the same color for every column in the row
    return pd.Series(color, index=row.index)

def highlight_category_column_f10_buy_00(value10, value7, value5, systemtime):
    count_9_3 = 0
    try:
        coll = dbcl['09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)']
        count_9_3 = coll.count_documents({'systemtime': {'$regex': '9:3'}})
    except Exception:
        pass

    count_9_3_s = 0
    try:
        coll = dbcl['supertrend-morning-buy']
        count_9_3_s = coll.count_documents({'systemtime': {'$regex': '09:'}})
    except Exception:
        pass

    if (((count_9_3 < 6 and count_9_3_s < 6) or ("9:3" not in systemtime and "9:4" not in systemtime))
        ):
        """Highlights the entire row based on the 'Category' column value."""
        if float(value10) >= 7 and float(value7) > 7 and float(value5) > 7 and ( float(value10) > 10 or float(value7) > 10 or float(value5) > 10):
            return 'background-color: #800080'
        elif float(value10) >= -2 and float(value10) < 1 and float(value7) < 2 and float(value5) < 2 and float(value7) > -2 and float(value5) > -2:
            return 'background-color: #CBEDFF'
        elif float(value10) <= -9:
            return 'background-color: #ffd546'
        elif float(value10) <= -6:
            return 'background-color: #fff0bc'
        elif float(value10) < -3:
            return 'background-color: #A1A1A1'
        else:
            return 'background-color: #A1A1A1'
        
def highlight_category_column_f10_sell_00(value10, value7, value5, systemtime):
    count_9_3 = 0
    try:
        coll = dbcl['09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)']
        count_9_3 = coll.count_documents({'systemtime': {'$regex': '9:3'}})
    except Exception:
        pass

    count_9_3_s = 0
    try:
        coll = dbcl['supertrend-morning-sell']
        count_9_3_s = coll.count_documents({'systemtime': {'$regex': '09:'}})
    except Exception:
        pass

    if (((count_9_3 < 6 and count_9_3_s < 6) or ("9:3" not in systemtime and "9:4" not in systemtime))):
        """Highlights the entire row based on the 'Category' column value."""
        if float(value10) <= -7 and float(value7) < -7 and float(value5) < -7 and ( float(value10) < -10 or float(value7) < -10 or float(value5) < -10):
            return 'background-color: #800080'
        elif float(value10) <= 2 and float(value10) > -1 and float(value7) > -2 and float(value5) > -2 and float(value7) < 2 and float(value5) < 2:
            return 'background-color: #CBEDFF'
        elif float(value10) >= 9:
            return 'background-color: #ffd546'
        elif float(value10) >= 6:
            return 'background-color: #fff0bc'
        elif float(value10) >= 3:
            return 'background-color: #A1A1A1'
        else:
            return 'background-color: #A1A1A1'

def apply_f10_buy_01(row):
    color = highlight_category_column_f10_buy_01(
        row["forecast_day_PCT10_change"],
        row["forecast_day_PCT7_change"],
        row["forecast_day_PCT5_change"],
        row["systemtime"],
    )
    # use the same color for every column in the row
    return pd.Series(color, index=row.index)

def apply_f10_sell_01(row):
    color = highlight_category_column_f10_sell_01(
        row["forecast_day_PCT10_change"],
        row["forecast_day_PCT7_change"],
        row["forecast_day_PCT5_change"],
        row["systemtime"],
    )
    # use the same color for every column in the row
    return pd.Series(color, index=row.index)

def highlight_category_column_f10_buy_01(value10, value7, value5, systemtime):
    count_9_3 = 0
    try:
        coll = dbcl['09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)']
        count_9_3 = coll.count_documents({'systemtime': {'$regex': '9:3'}})
    except Exception:
        pass

    count_9_3_s = 0
    try:
        coll = dbcl['supertrend-morning-buy']
        count_9_3_s = coll.count_documents({'systemtime': {'$regex': '09:'}})
    except Exception:
        pass

    if (((count_9_3 < 6 and count_9_3_s < 6) or ("9:3" not in systemtime and "9:4" not in systemtime))):
        """Highlights the entire row based on the 'Category' column value."""
        if float(value10) > 7 and float(value7) > 7 and float(value5) > 7 and ( float(value10) > 10 or float(value7) > 10 or float(value5) > 10):
            return 'background-color: #800080'
        elif float(value10) > -2 and float(value10) < 1 and float(value7) < 2 and float(value5) < 2 and float(value7) >-2 and float(value5) > -2:
            return 'background-color: #CBEDFF'
        elif float(value10) < -7:
            return 'background-color: #A1A1A1'
        elif float(value10) < -3:
            return 'background-color: #A1A1A1'
        else:
            return 'background-color: #A1A1A1'
        
def highlight_category_column_f10_sell_01(value10, value7, value5, systemtime):
    count_9_3 = 0
    try:
        coll = dbcl['09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)']
        count_9_3 = coll.count_documents({'systemtime': {'$regex': '9:3'}})
    except Exception:
        pass

    count_9_3_s = 0
    try:
        coll = dbcl['supertrend-morning-sell']
        count_9_3_s = coll.count_documents({'systemtime': {'$regex': '09:'}})
    except Exception:
        pass

    if (((count_9_3 < 6 and count_9_3_s < 6) or ("9:3" not in systemtime and "9:4" not in systemtime))):
        """Highlights the entire row based on the 'Category' column value."""
        if float(value10) < -7 and float(value7) < -7 and float(value5) < -7 and ( float(value10) < -10 or float(value7) < -10 or float(value5) < -10):
            return 'background-color: #800080'
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

def apply_breakout_highlight(row):
    """Return a Series of styles for a row: preserve existing mlData styles
    but force pink for mlData when systemtime contains '10:' and mlData
    indicates a 'CROSSED' event.
    """
    styles = pd.Series('', index=row.index)
    try:
        # # Only apply this special pink highlight for chartlink1 views
        # if not chartlink1 and not testLearning and not applyBreakOut:
        #     # preserve existing mlData style
        #     ml_value = str(row.get('mlData', ''))
        #     system_time = str(row.get('systemtime'))
        #     try:
        #         styles['mlData'] = highlight_category_column(ml_value, system_time) or ''
        #     except Exception:
        #         styles['mlData'] = ''
        #     return styles

        ml_value = str(row.get('mlData', ''))
        system_time = str(row.get('systemtime'))
        scrip = row.get('scrip')

        # Default to existing mlData style
        existing = ''
        try:
            existing = highlight_category_column(ml_value, system_time) or ''
        except Exception:
            existing = ''

        # If systemtime contains '10:' and the scrip is present in the
        # 'crossed-day-high' collection, set mlData cell to pink.
        try:
            coll = dbcl['buy-morning-volume-breakout(Check-News)']
            count = coll.count_documents({'systemtime': {'$regex': '09:'}})

            if count < 6:
                # Check if any document exists with specific time patterns
                if coll.find_one({'scrip': scrip, 'systemtime': {'$regex': '09:|10:00:00|10:05|10:1|10:2|10:30'}}):
                    styles['scrip'] = 'background-color: #E0FFDE'
                    return styles
            else:
                if coll.find_one({'scrip': scrip, 'systemtime': {'$regex': '10:2|10:3|10:4|10:50'}}):
                    styles['scrip'] = 'background-color: #E0FFDE'
                    return styles

            
        except Exception:
            # fallback to existing style on any DB error
            pass

        try:
            coll = dbcl['sell-morning-volume-breakout(Check-News)']
            count = coll.count_documents({'systemtime': {'$regex': '09:'}})

            if count < 6:
                # Check if any document exists with specific time patterns
                if coll.find_one({'scrip': scrip, 'systemtime': {'$regex': '09:|10:00:00|10:05|10:1|10:2|10:30'}}):
                    styles['scrip'] = 'background-color: #FCCFD2'
                    return styles
            else:
                # Check if any document exists with systemtime starting with '10:' or '11:'
                if coll.find_one({'scrip': scrip, 'systemtime': {'$regex': '10:2|10:3|10:4|10:50'}}):
                    styles['scrip'] = 'background-color: #FCCFD2'
                    return styles
        except Exception:
            # fallback to existing style on any DB error
            pass

        
        try:
            coll = dbcl['Breakout-Buy-after-10']
            if coll.find_one({'scrip': scrip, 'systemtime': {'$regex': '09:4|09:5|10:00:00|10:05|10:1|10:2|10:30'}}):
                styles['scrip'] = 'background-color: #E0FFDE'
                return styles
        except Exception:
            # fallback to existing style on any DB error
            pass

        try:
            coll = dbcl['Breakout-Sell-after-10']
            if coll.find_one({'scrip': scrip, 'systemtime': {'$regex': '09:4|09:5|10:00:00|10:05|10:1|10:2|10:30'}}):
                styles['scrip'] = 'background-color: #FCCFD2'
                return styles
        except Exception:
            # fallback to existing style on any DB error
            pass


        try:
            coll = dbcl['1-Bbuyy-morningUp-downConsolidation']
            if coll.find_one({'scrip': scrip, 'systemtime': {'$regex': '09:4|09:5|10:00:00|10:05|10:1|10:2|10:30'}}):
                styles['scrip'] = 'background-color: #E0FFDE'
                return styles
        except Exception:
            # fallback to existing style on any DB error
            pass

        try:
            coll = dbcl['1-Sselll-morningDown-upConsolidation']
            if coll.find_one({'scrip': scrip, 'systemtime': {'$regex': '09:4|09:5|10:00:00|10:05|10:1|10:2|10:30'}}):
                styles['scrip'] = 'background-color: #FCCFD2'
                return styles
        except Exception:
            # fallback to existing style on any DB error
            pass


        try:
            df = getdf('morning-volume-breakout-buy')
            buy_df = df
            buy_df_2 = df
            try:
                buy_df = df[
                    (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('09:5', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False))
                    ]
                
                buy_df_2 = df[
                    (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) 
                    ]
            except KeyError as e:
                pass


            if ('10:' in system_time and '10:4' not in system_time and '10:5' not in system_time) and scrip and len(buy_df) < 8:
                if len(buy_df_2) < 15:
                    try:
                        coll = dbcl['crossed-day-high']
                        if len(coll) < 12 and coll.find_one({'scrip': scrip}):
                            styles['mlData'] = 'background-color: #fb87ec'
                            return styles
                    except Exception:
                        # fallback to existing style on any DB error
                        pass
                
                try:
                    coll = dbcl['09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)']
                    if len(coll) < 5 and coll.find_one({'scrip': scrip}):
                        styles['mlData'] = 'background-color: #fb87ec'
                        return styles
                except Exception:
                    # fallback to existing style on any DB error
                    pass

                try:
                    coll = dbcl['supertrend-morning-buy']
                    if len(coll) < 5 and coll.find_one({'scrip': scrip, 'systemtime': {'$regex': '09:5|10:'}}):
                        styles['mlData'] = 'background-color: #fb87ec'
                        return styles
                except Exception:
                    # fallback to existing style on any DB error
                    pass


            df = getdf('morning-volume-breakout-sell')
            sell_df = df
            sell_df_2 = df
            try:
                sell_df = df[
                    (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('09:5', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('10:', case=False, regex=True, na=False)) &
                    (~df['systemtime'].str.contains('11:', case=False, regex=True, na=False)) 
                ]

                sell_df_2 = df[
                    (~df['systemtime'].str.contains('09:2', case=False, regex=True, na=False)) 
                    ]

            except KeyError as e:
                pass

            
            if ('10:' in system_time and '10:4' not in system_time and '10:5' not in system_time) and scrip and len(sell_df) < 8:
                if len(sell_df_2) < 15:
                    try:
                        coll = dbcl['crossed-day-low']
                        if len(coll) < 12 and coll.find_one({'scrip': scrip, 'systemtime': {'$regex': '09:5|10:'}}):
                            styles['mlData'] = 'background-color: #fb87ec'
                            return styles
                    except Exception:
                        # fallback to existing style on any DB error
                        pass

                try:
                    coll = dbcl['09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)']
                    if len(coll) < 5 and coll.find_one({'scrip': scrip}):
                        styles['mlData'] = 'background-color: #fb87ec'
                        return styles
                except Exception:
                    # fallback to existing style on any DB error
                    pass

                try:
                    coll = dbcl['supertrend-morning-sell']
                    if len(coll) < 5 and coll.find_one({'scrip': scrip, 'systemtime': {'$regex': '09:5|10:'}}):
                        styles['mlData'] = 'background-color: #fb87ec'
                        return styles
                except Exception:
                    # fallback to existing style on any DB error
                    pass

        

                


        except Exception:
            # fallback to existing style on any DB error
            pass

        styles['mlData'] = existing
    except Exception:
        pass
    return styles

def get_chartlink_collections():
    """Get list of collection names in chartlink database"""
    return sorted(dbcl.list_collection_names())

def get_collection_scrips(collection_name):
    """Get unique scrips from a collection"""
    collection = dbcl[collection_name]
    scrips = collection.distinct('scrip')
    return sorted(scrips) if scrips else []

def set_selected_collection(collection_name):
    """Set the selected collection globally"""
    global selected_collection
    selected_collection = collection_name

def get_selected_collection():
    """Get the currently selected collection"""
    global selected_collection
    return selected_collection

def getdf(collection_name):
    collection = dbcl[collection_name]
    df = pd.DataFrame(list(collection.find()))
    
    # Filter by selected collection scrips if set
    selected_coll = get_selected_collection()
    if selected_coll and selected_coll != "All":
        try:
            scrips = get_collection_scrips(selected_coll)
            if scrips:
                df = df[df['scrip'].isin(scrips)]
        except Exception as e:
            print(f"Error filtering by collection: {e}")
    
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

def getdfResult(collection_name):
    collection = dbcl[collection_name]
    df = pd.DataFrame(list(collection.find()))
    
    # Filter by selected collection scrips if set
    selected_coll = get_selected_collection()
    if selected_coll and selected_coll != "All":
        try:
            scrips = get_collection_scrips(selected_coll)
            if scrips:
                df = df[df['scrip'].isin(scrips)]
        except Exception as e:
            print(f"Error filtering by collection: {e}")
    
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
        df['kNeighboursValue_reg'] = pd.to_numeric(df['kNeighboursValue_reg'], errors='coerce')
        df['mlpValue_reg'] = pd.to_numeric(df['mlpValue_reg'], errors='coerce')
        df['kNeighboursValue_reg_other'] = pd.to_numeric(df['kNeighboursValue_reg_other'], errors='coerce')
        df['mlpValue_reg_other'] = pd.to_numeric(df['mlpValue_reg_other'], errors='coerce')
        df['intradaytech'] = df['intradaytech'].fillna('').astype(str)
        df['index'] = df['index'].fillna('').astype(str)
        
    except KeyError as e:
        print(f"KeyError: {e}")
    return df

def render(st, df, name, height=200, color='NA', column_order=column_order_default, column_conf=column_config_default, renderml=False, renderf10buy=False, renderf10sell=False, f10=0, renderf10buy00=False, renderf10sell00=False, renderf10buy01=False, renderf10sell01=False, applyBreakOut=False):
    st.write("********"+ name + "********")
    try:
        df = df[
                ((abs(df['monthLowChange']) > 3) | (abs(df['monthHighChange']) > 3)) | ((abs(df['month3LowChange']) > 10) | (abs(df['month3HighChange']) > 10))
                ]
    except KeyError as e:
        print("")
    
    try:
        df = df[
                ((abs(df['PCT_change']) - abs(df['PCT_day_change'])) < 4) 
                ]
    except KeyError as e:
        print("")

    try:
        df = df[
                (df['highTail'] < 3.3) & (df['lowTail'] < 3.3)
                ]
    except KeyError as e:
        print("")
    #
    # Main Code Execution

    if renderml:
        df_styled = highlight_category_row(df, color=color)
        st.dataframe(df_styled, height=height, column_order=column_order, column_config=column_conf, use_container_width=True)
    elif (df.empty):
        st.dataframe(df, height=height, column_order=column_order, column_config=column_conf, use_container_width=True)
    else:
        df_styled = highlight_category_row(df, color=color)
        
        if renderf10buy:
            df_styled = df_styled.apply(apply_f10_buy, axis=1)
        elif renderf10sell:
            df_styled = df_styled.apply(apply_f10_sell, axis=1)
        elif renderf10buy00:
            df_styled = df_styled.apply(apply_f10_buy_00, axis=1)
        elif renderf10sell00:
            df_styled = df_styled.apply(apply_f10_sell_00, axis=1)
        elif renderf10buy01:
            df_styled = df_styled.apply(apply_f10_buy_01, axis=1)
        elif renderf10sell01:
            df_styled = df_styled.apply(apply_f10_sell_01, axis=1)
        elif (not df.empty):
            if ((chartlink0) and (color == 'G' or color == 'R')):
                df_styled = df_styled.apply(apply_highlight_column, axis=1)
            else:
                df_styled = df_styled.apply(apply_highlight_column, axis=1)
    
        
        if(chartlink1 or testLearning or applyBreakOut) and color =='LG':
            df_styled = df_styled.apply(apply_breakout_highlight, axis=1)
        st.dataframe(df_styled, height=height, column_order=column_order, column_config=column_conf, use_container_width=True)
   

def render_rawdata(st, df, name, height=200, color='NA', column_order=column_order_default, column_conf=column_config_default):
    st.write("********"+ name + "********")
    st.dataframe(df, height=height, use_container_width=True)