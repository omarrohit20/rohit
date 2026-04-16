# Performance & Loading Issues Analysis

## Critical Issues Found

### 1. **Full Collection Loads (Memory Leak Risk)**
**File**: `rbase.py` - `getdf()`, `getdf_raw()`, `getdfResult()` functions
**Issue**: Functions load ALL documents from MongoDB collections into memory without pagination or filtering

```python
# CURRENT (Lines 1340-1385)
def getdf(collection_name):
    collection = dbcl[collection_name]
    df = pd.DataFrame(list(collection.find()))  # ⚠️ Loads all documents!
```

**Impact**: 
- If a collection has 100K+ documents, entire dataset loaded into RAM
- Causes slow page loads and crashes on large collections
- Streamlit reruns multiply the problem

**Fix Priority**: CRITICAL
**Recommendation**: 
```python
# Add pagination/filtering at query level
def getdf(collection_name, limit=5000, filter_query=None):
    collection = dbcl[collection_name]
    query = filter_query or {}
    df = pd.DataFrame(list(collection.find(query).limit(limit)))
    # Add UI for pagination or time-based filtering
```

---

### 2. **N+1 Query Pattern (Database Thrashing)**
**File**: `rbase.py` - `apply_breakout_highlight()` function (lines ~1000-1150)
**Issue**: Multiple sequential database queries for the same conditions

```python
# Lines 1003-1055 - Each scrip triggers multiple count_documents calls:
coll = dbcl['buy-morning-volume-breakout(Check-News)']
count = coll.count_documents({'systemtime': {'$regex': '09:|10:00:00'}})  # Query 1
if coll.find_one({'scrip': scrip, ... }):  # Query 2
    
coll = dbcl['sell-morning-volume-breakout(Check-News)']
count = coll.count_documents({'systemtime': {'$regex': '09:|10:00:00'}})  # Query 3
if coll.find_one({'scrip': scrip, ... }):  # Query 4
# ... 10+ more queries per row!
```

**Impact**:
- With 100 rows, this triggers 1000+ database queries per page load
- Each call has network/IO overhead
- Causes exponential slowdown with more rows

**Fix Priority**: CRITICAL
**Recommendation**:
```python
# Cache count_documents results
@st.cache_data(ttl=60)
def get_collection_counts():
    return {
        'buy': dbcl['buy-morning-volume-breakout(Check-News)'].count_documents({'systemtime': {'$regex': '09:|10:00:00'}}),
        'sell': dbcl['sell-morning-volume-breakout(Check-News)'].count_documents({'systemtime': {'$regex': '09:|10:00:00'}}),
        # ... other counts
    }

# Use aggregation pipeline instead of multiple queries:
def check_scrip_batch(scrips):
    pipeline = [
        {'$match': {'scrip': {'$in': scrips}, 'systemtime': {'$regex': '09:|10:00:00|...'}}},
        {'$group': {'_id': '$scrip', 'count': {'$sum': 1}}},
        {'$project': {'scrip': '$_id', 'exists': True}}
    ]
    return list(collection.aggregate(pipeline))
```

---

### 3. **Missing Database Indexes**
**File**: MongoDB collections in `rbase.py`
**Issue**: Queries use regex patterns and complex filters without indexes

```python
# No indexes on these frequently queried fields:
{'systemtime': {'$regex': '09:|10:00:00|...'}}  # Regex on unindexed field!
{'scrip': scrip, 'yearLowChange': {'$gt': 15}}  # Compound query
```

**Impact**:
- MongoDB does COLLSCAN (full table scan) for each query
- Regex queries are especially slow
- Problem multiplies with large collections

**Fix Priority**: HIGH
**Recommendation**:
```javascript
// Create indexes in MongoDB:
db.collection('buy-morning-volume-breakout(Check-News)').createIndex({ 'systemtime': 1 })
db.collection('buy-morning-volume-breakout(Check-News)').createIndex({ 'scrip': 1 })
db.collection('buy-morning-volume-breakout(Check-News)').createIndex({ 'scrip': 1, 'yearLowChange': 1 })
db.collection('buy-morning-volume-breakout(Check-News)').createIndex({ 'systemtime': 1, 'scrip': 1 })

// Use exact match instead of regex where possible
// Change: {'$regex': '09:'} to stored time_hour: 9 (numerictype)
```

---

### 4. **Module Reloading on Every Run**
**File**: `index.py` lines 109-113
**Issue**: Resetting global variables forces module reloads in Streamlit

```python
# CURRENT (Lines 109-113)
try:
    import rbase as rb
    rb.chartlink0 = False
    rb.chartlink1 = False
    rb.testLearning = False  # ⚠️ Modifying globals causes reruns!
except Exception:
    pass
```

**Impact**:
- Every page load resets these flags → module reexecuted
- Database connections reset
- Cached data invalidated
- Cascading reruns cause delays

**Fix Priority**: MEDIUM
**Recommendation**:
```python
# Use Streamlit session state instead:
if 'page_loaded' not in st.session_state:
    import rbase as rb
    st.session_state.rb = rb
    st.session_state.page_loaded = True

# Access via: st.session_state.rb.chartlink0
# No module reload = faster page loads
```

---

### 5. **Inefficient DataFrame Filtering**
**File**: `rbase.py` lines 1350-1365 (getdf function)
**Issue**: Post-query filtering instead of pre-query filtering

```python
# CURRENT
df = pd.DataFrame(list(collection.find()))  # Load all documents
selected_coll = get_selected_collection()
if selected_coll and selected_coll != "All":
    scrips = get_collection_scrips(selected_coll)
    df = df[df['scrip'].isin(scrips)]  # Filter in memory after loading
```

**Impact**:
- Loads unnecessary data then discards it
- Memory spike for large filtered result sets
- Each rerun repeats the full load + filter

**Fix Priority**: HIGH
**Recommendation**:
```python
# Filter at database query level:
def getdf(collection_name):
    collection = dbcl[collection_name]
    
    selected_coll = get_selected_collection()
    query = {}
    if selected_coll and selected_coll != "All":
        scrips = get_collection_scrips(selected_coll)
        query['scrip'] = {'$in': scrips}
    
    df = pd.DataFrame(list(collection.find(query)))  # Only fetch needed docs
```

---

### 6. **Uncached Streamlit Function**
**File**: `rbase.py` line 1076 (apply_breakout_highlight)
**Issue**: Function decorated with `@st.cache_data(ttl=10)` but takes unhashable parameter

```python
# CURRENT
@st.cache_data(ttl=10)
def apply_breakout_highlight(row):  # row is a pandas Series (unhashable!)
    # pandas Series can't be cached - changes every render
```

**Impact**:
- Cache never hits
- Function runs every time despite decorator
- Wastes resources applying styles multiple times

**Fix Priority**: MEDIUM
**Recommendation**:
```python
# Don't cache row-by-row operations that change constantly
# Cache the static count checks instead:

@st.cache_data(ttl=60)
def get_breakout_collections_status():
    return {
        'buy_count': dbcl['buy-morning-volume-breakout(Check-News)'].count_documents(...),
        'sell_count': dbcl['sell-morning-volume-breakout(Check-News)'].count_documents(...),
        # ...
    }

# Use in function instead of querying each time
```

---

### 7. **Synchronous Blocking I/O**
**File**: `index.py` lines ~145+ (subprocess management)
**Issue**: All database operations are synchronous and blocking

**Impact**:
- UI freezes during database queries
- Can't handle multiple page loads concurrently
- Poor user experience on slow connections

**Fix Priority**: LOW (requires async refactor)
**Recommendation**:
```python
# Use asyncio or threading for long operations
# Consider: motor (async MongoDB driver)
# Or: ThreadPoolExecutor for background queries
```

---

## Quick Wins (Easy Fixes)

### 1. Enable MongoDB Connection Pooling
```python
# CURRENT (Line 9-10)
connection = MongoClient('localhost', 27017)

# BETTER
connection = MongoClient(
    'localhost', 
    27017,
    maxPoolSize=50,
    minPoolSize=10,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=10000
)
```

### 2. Batch Similar Queries
```python
# Instead of:
count1 = coll1.count_documents({...})
count2 = coll2.count_documents({...})
count3 = coll3.count_documents({...})

# Use aggregation pipeline:
pipeline = [
    {'$facet': {
        'morning_buy': [{'$match': {...}}, {'$count': 'count'}],
        'morning_sell': [{'$match': {...}}, {'$count': 'count'}],
        'supertrend_buy': [{'$match': {...}}, {'$count': 'count'}]
    }}
]
```

### 3. Add Query Limits
```python
# More defensive limits
collection.find(query).limit(1000)  # Prevent runaway queries
```

## Summary of Issues by Severity

| Issue | Severity | Location | Impact | Fix Time |
|-------|----------|----------|--------|----------|
| Full collection loads | 🔴 CRITICAL | getdf() | Memory/crashes | 2-3 hours |
| N+1 query pattern | 🔴 CRITICAL | apply_breakout_highlight | Database thrashing | 3-4 hours |
| Missing indexes | 🔴 CRITICAL | MongoDB | Slow queries | 1 hour |
| Module reloading | 🟠 HIGH | index.py | Re-execution overhead | 1 hour |
| Post-query filtering | 🟠 HIGH | getdf() | Wasted I/O | 1-2 hours |
| Cache miss | 🟡 MEDIUM | apply_breakout_highlight | Unnecessary recomputation | 30 min |
| Sync blocking I/O | 🟡 MEDIUM | General | UI freezing | 4-8 hours |

## Recommended Fix Order

1. **Create MongoDB indexes** (1 hour) - Immediate benefit for all queries
2. **Move module imports to session state** (1 hour) - Reduces reloads  
3. **Cache collection counts** (30 min) - Reduces N+1 queries significantly
4. **Add query limits & filters** (1-2 hours) - Prevents runaway data loads
5. **Refactor getdf to use DB-level filtering** (2-3 hours) - Major memory improvement
6. **Batch similar queries** (2-3 hours) - Further reduce database hits

