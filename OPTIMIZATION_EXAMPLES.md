# Optimization Implementation Examples

## PRIORITY 1: Add MongoDB Indexes

These indexes will immediately improve query performance. Run in MongoDB client:

```javascript
// Connection: mongodb://localhost:27017/chartlink

// Indexes for main collections
db['buy-morning-volume-breakout(Check-News)'].createIndex({ "systemtime": 1 })
db['buy-morning-volume-breakout(Check-News)'].createIndex({ "scrip": 1 })
db['buy-morning-volume-breakout(Check-News)'].createIndex({ "scrip": 1, "yearLowChange": 1 })
db['buy-morning-volume-breakout(Check-News)'].createIndex({ "systemtime": 1, "scrip": 1 })

db['sell-morning-volume-breakout(Check-News)'].createIndex({ "systemtime": 1 })
db['sell-morning-volume-breakout(Check-News)'].createIndex({ "scrip": 1 })
db['sell-morning-volume-breakout(Check-News)'].createIndex({ "scrip": 1, "yearLowChange": 1 })
db['sell-morning-volume-breakout(Check-News)'].createIndex({ "systemtime": 1, "scrip": 1 })

db['Breakout-Buy-after-10'].createIndex({ "systemtime": 1 })
db['Breakout-Buy-after-10'].createIndex({ "scrip": 1 })

db['Breakout-Sell-after-10'].createIndex({ "systemtime": 1 })
db['Breakout-Sell-after-10'].createIndex({ "scrip": 1 })

db['09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)'].createIndex({ "systemtime": 1 })
db['09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)'].createIndex({ "scrip": 1 })

db['09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)'].createIndex({ "systemtime": 1 })
db['09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)'].createIndex({ "scrip": 1 })

db['supertrend-morning-buy'].createIndex({ "systemtime": 1 })
db['supertrend-morning-buy'].createIndex({ "scrip": 1 })

db['supertrend-morning-sell'].createIndex({ "systemtime": 1 })
db['supertrend-morning-sell'].createIndex({ "scrip": 1 })

db['crossed-day-high'].createIndex({ "scrip": 1 })
db['crossed-day-low'].createIndex({ "scrip": 1 })

db['morning-volume-breakout-buy'].createIndex({ "systemtime": 1 })
db['morning-volume-breakout-sell'].createIndex({ "systemtime": 1 })
```

---

## PRIORITY 2: Optimize rbase.py - Add Caching Layer

Replace the current imports section (top of file) with:

```python
# === OPTIMIZED CONNECTION & CACHING ===
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import pymongo
import streamlit as st
from pymongo import MongoClient
from functools import lru_cache
import hashlib

# Connection with pooling
connection = MongoClient(
    'localhost', 
    27017,
    maxPoolSize=50,
    minPoolSize=10,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=10000
)
dbcl = connection.chartlink
dbnse = connection.Nsedata

# === CACHING FUNCTIONS ===
@st.cache_data(ttl=60)
def get_collection_stats():
    """Cache collection counts to avoid repeated count_documents calls"""
    return {
        'buy_morning': dbcl['buy-morning-volume-breakout(Check-News)'].count_documents({'systemtime': {'$regex': '09:|10:00:00'}}),
        'sell_morning': dbcl['sell-morning-volume-breakout(Check-News)'].count_documents({'systemtime': {'$regex': '09:|10:00:00'}}),
        'buy_breakout10': dbcl['Breakout-Buy-after-10'].count_documents({'systemtime': {'$regex': '09:|10:00:00'}}),
        'sell_breakout10': dbcl['Breakout-Sell-after-10'].count_documents({'systemtime': {'$regex': '09:|10:00:00'}}),
    }

@st.cache_data(ttl=60)
def get_scrip_batch_status(scrips_tuple, collection_name):
    """Batch check multiple scrips at once instead of one at a time"""
    scrips = list(scrips_tuple)
    collection = dbcl[collection_name]
    
    # Use aggregation to get all matching scrips in one query
    pipeline = [
        {
            '$match': {
                'scrip': {'$in': scrips},
                'systemtime': {'$regex': '09:|10:00:00|10:05|10:1|10:2|10:30'},
                'yearLowChange': {'$gt': 15}
            }
        },
        {
            '$group': {
                '_id': '$scrip',
                'count': {'$sum': 1}
            }
        }
    ]
    
    results = list(collection.aggregate(pipeline))
    return {r['_id']: True for r in results}  # Convert to set for O(1) lookup
```

---

## PRIORITY 3: Optimize getdf() Function

Replace lines 1340-1385 with:

```python
@st.cache_data(ttl=30)
def getdf(collection_name, limit=5000):
    """
    Optimized function with:
    1. Database-level filtering (not post-query)
    2. Row limit to prevent memory issues
    3. Efficient data type conversion
    """
    collection = dbcl[collection_name]
    
    # Build query at database level
    query = {}
    
    # Add scrip filter if needed
    selected_coll = get_selected_collection()
    if selected_coll and selected_coll != "All":
        try:
            scrips = get_collection_scrips(selected_coll)
            if scrips:
                query['scrip'] = {'$in': scrips}
        except Exception as e:
            print(f"Error filtering by collection: {e}")
    
    # Fetch with query filter and limit
    df = pd.DataFrame(list(
        collection.find(query, projection={
            'scrip': 1,
            'PCT_day_change': 1,
            'systemtime': 1,
            'industry': 1,
            'mlData': 1,
            'PCT_change': 1,
            'yearLowChange': 1,
            'yearHighChange': 1,
            # ... Add only needed fields
        }).limit(limit)
    ))
    
    if df.empty:
        return df
    
    # Efficient type conversion using pd.to_numeric with errors='coerce'
    numeric_cols = [
        'PCT_day_change', 'PCT_change', 'PCT_day_change_pre1', 'PCT_day_change_pre2',
        'highTail', 'lowTail', 'year5HighChange', 'yearHighChange', 'yearLowChange',
        'month3HighChange', 'month3LowChange', 'monthHighChange', 'monthLowChange',
        'week2HighChange', 'week2LowChange', 'weekHighChange', 'weekLowChange',
        'forecast_day_PCT10_change', 'forecast_day_PCT7_change', 'forecast_day_PCT5_change'
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # String conversions
    if 'systemtime' in df.columns:
        try:
            df['systemtime'] = pd.to_datetime(df['systemtime']).dt.time.astype(str)
        except:
            pass
    
    if 'mlData' in df.columns:
        df['mlData'] = df['mlData'].fillna('').astype(str)
    
    return df
```

---

## PRIORITY 4: Optimize index.py - Use Session State

Replace lines 105-115 with:

```python
# === OPTIMIZED MODULE LOADING ===
if 'rbase_module' not in st.session_state:
    import rbase as rb
    st.session_state.rbase_module = rb
    # Set flags only once
    rb.chartlink0 = False
    rb.chartlink1 = False
    rb.testLearning = False

# Access the module without reimporting
rbase = st.session_state.rbase_module

# Use in code like: rbase.getdf(...) instead of importing fresh each time
```

---

## PRIORITY 5: Refactor apply_breakout_highlight()

Replace the multiple sequential queries with a batch approach:

```python
@st.cache_data(ttl=60)
def get_breakout_scrips_batch(scrips_tuple):
    """Fetch all breakout status for multiple scrips in one pass"""
    scrips = list(scrips_tuple)
    
    result = {
        'buy_green': set(),
        'sell_pink': set(),
        'breakout_buy_green': set(),
        'breakout_sell_red': set(),
    }
    
    try:
        coll = dbcl['buy-morning-volume-breakout(Check-News)']
        count = coll.count_documents({'systemtime': {'$regex': '09:|10:00:00'}})
        
        if count < 5:
            found = coll.find({
                'scrip': {'$in': scrips},
                'systemtime': {'$regex': '09:|10:00:00|10:05|10:1|10:2|10:30'},
                'yearLowChange': {'$gt': 15}
            }, projection={'scrip': 1})
        else:
            found = coll.find({
                'scrip': {'$in': scrips},
                'systemtime': {'$regex': '10:2|10:3|10:4|10:50'},
                'yearLowChange': {'$gt': 15}
            }, projection={'scrip': 1})
        
        result['buy_green'] = {doc['scrip'] for doc in found}
    except Exception as e:
        print(f"Error fetching buy scrips: {e}")
    
    # Similar for other collections...
    
    return result

def apply_breakout_highlight_optimized(row):
    """Optimized version using precomputed results"""
    styles = pd.Series('', index=row.index)
    
    try:
        scrip = row.get('scrip')
        system_time = str(row.get('systemtime', ''))
        
        if not scrip:
            return styles
        
        # Get precomputed scrip status (cached)
        scrips_status = get_breakout_scrips_batch((scrip,))
        
        if scrip in scrips_status['buy_green']:
            styles['scrip'] = 'background-color: #E0FFDE'
            return styles
        elif scrip in scrips_status['sell_pink']:
            styles['scrip'] = 'background-color: #FCCFD2'
            return styles
        
        # ... Continue with other checks using cached data
        
    except Exception:
        pass
    
    return styles
```

---

## Testing Checklist

- [ ] Run MongoDB index creation script
- [ ] Verify indexes created: `db.collection.getIndexes()`
- [ ] Update rbase.py with caching layer
- [ ] Update index.py to use session_state
- [ ] Test getdf() with limit parameter
- [ ] Measure page load time before/after
- [ ] Monitor MongoDB connections with `mongostat`
- [ ] Check memory usage with large collections

---

## Performance Metrics to Monitor

After implementing these optimizations:

1. **Page Load Time**: Should drop by 50-80%
2. **Database Queries**: Should reduce from 50+/page to 5-10/page
3. **Memory Usage**: Should use 60% less RAM
4. **CPU Usage**: Should significantly decrease during filtering
