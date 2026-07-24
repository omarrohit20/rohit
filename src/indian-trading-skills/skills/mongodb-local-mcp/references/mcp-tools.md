# MongoDB MCP Tools Reference

## Tool Invocation Pattern

1. List MCP tool descriptors in the project's `mcps` folder (or Cursor MCP settings)
2. Read the schema for the target tool before calling
3. Use `CallMcpTool` with `server: "MongoDB"` and the tool name

## Core Tools

### list-databases

No arguments. Returns all database names on the connected instance.

### list-collections

```json
{ "database": "trading" }
```

### collection-schema

```json
{ "database": "trading", "collection": "candles_daily" }
```

Returns inferred field names and types from sample documents.

### find

```json
{
  "database": "trading",
  "collection": "candles_daily",
  "filter": { "symbol": "RELIANCE", "exchange": "NSE" },
  "projection": { "timestamp": 1, "open": 1, "high": 1, "low": 1, "close": 1, "volume": 1 },
  "sort": { "timestamp": -1 },
  "limit": 100
}
```

### aggregate

```json
{
  "database": "trading",
  "collection": "candles_intraday",
  "pipeline": [
    { "$match": { "symbol": "RELIANCE", "interval": "5m", "timestamp": { "$gte": { "$date": "2026-06-20T00:00:00Z" } } } },
    { "$sort": { "timestamp": 1 } },
    { "$group": {
        "_id": null,
        "dayHigh": { "$max": "$high" },
        "dayLow": { "$min": "$low" },
        "totalVolume": { "$sum": "$volume" },
        "vwap": { "$avg": { "$divide": [{ "$add": ["$high", "$low", "$close"] }, 3] } }
    }}
  ]
}
```

### count

```json
{
  "database": "trading",
  "collection": "candles_daily",
  "filter": { "symbol": "TCS" }
}
```

## Common Query Patterns for Indian Markets

### Latest N daily candles

```javascript
{ symbol: "INFY", exchange: "NSE" }
// sort: { timestamp: -1 }, limit: 252  // ~1 year trading days
```

### Intraday session (IST trading day)

NSE/BSE hours: 9:15 AM – 3:30 PM IST. Filter by date range in UTC or store `tradeDate` as IST string.

```javascript
{
  symbol: "BANKNIFTY",
  interval: "5m",
  tradeDate: "2026-06-20"   // if stored as IST date string
}
```

### Multi-symbol screen (relative strength)

```javascript
[
  { "$match": { "timestamp": { "$gte": ISODate("2026-05-01") } } },
  { "$sort": { "symbol": 1, "timestamp": 1 } },
  { "$group": {
      "_id": "$symbol",
      "startClose": { "$first": "$close" },
      "endClose": { "$last": "$close" }
  }},
  { "$project": {
      "returnPct": { "$multiply": [{ "$divide": [{ "$subtract": ["$endClose", "$startClose"] }, "$startClose"] }, 100] }
  }},
  { "$sort": { "returnPct": -1 } },
  { "$limit": 20 }
]
```

## Index Recommendations

If queries are slow, suggest these indexes (user must create outside read-only mode):

```javascript
db.candles_daily.createIndex({ symbol: 1, exchange: 1, timestamp: -1 })
db.candles_intraday.createIndex({ symbol: 1, interval: 1, timestamp: -1 })
db.candles_intraday.createIndex({ symbol: 1, tradeDate: 1, interval: 1 })
db.symbols.createIndex({ symbol: 1, exchange: 1 }, { unique: true })
```

## Adapting to Unknown Schemas

If field names differ from conventions:

| Expected | Common alternatives |
|----------|-------------------|
| `symbol` | `ticker`, `tradingsymbol`, `instrument` |
| `timestamp` | `date`, `datetime`, `time`, `ts` |
| `close` | `c`, `closePrice`, `ltp` |
| `volume` | `vol`, `tradedVolume` |
| `interval` | `timeframe`, `resolution`, `granularity` |

Always run `collection-schema` and sample `find` before building pipelines.
