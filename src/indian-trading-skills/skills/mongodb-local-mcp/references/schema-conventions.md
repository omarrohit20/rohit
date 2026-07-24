# Financial Data Schema Conventions

Standard schema for Indian market data stored in local MongoDB. Adapt field names if the discovered schema differs.

## Database: `trading`

### Collection: `symbols`

Master list of NSE/BSE instruments.

```javascript
{
  symbol: "RELIANCE",           // NSE ticker
  exchange: "NSE",              // NSE | BSE
  name: "Reliance Industries Ltd",
  isin: "INE002A01018",
  sector: "Oil & Gas",
  industry: "Refineries",
  marketCap: 1850000,           // Crores INR
  isFno: true,
  lotSize: 250,
  updatedAt: ISODate("...")
}
```

### Collection: `candles_intraday`

Intraday OHLCV bars. One document per bar.

```javascript
{
  symbol: "RELIANCE",
  exchange: "NSE",
  interval: "5m",               // 1m | 5m | 15m | 30m | 60m
  timestamp: ISODate("..."),    // Bar open time (UTC or IST — be consistent)
  tradeDate: "2026-06-20",    // IST trading date (YYYY-MM-DD) — optional but useful
  open: 2850.50,
  high: 2865.00,
  low: 2845.25,
  close: 2860.75,
  volume: 125000,
  oi: 0                         // Open interest (F&O only)
}
```

**Recommended index:** `{ symbol: 1, interval: 1, timestamp: -1 }`

### Collection: `candles_daily`

Daily OHLCV. Adjusted for splits/bonus if available.

```javascript
{
  symbol: "TCS",
  exchange: "NSE",
  timestamp: ISODate("2026-06-20T00:00:00Z"),
  open: 4100.00,
  high: 4150.00,
  low: 4080.00,
  close: 4140.50,
  volume: 2500000,
  deliveryVolume: 1200000,    // Optional — NSE delivery %
  adjustedClose: 4140.50      // Optional — split-adjusted
}
```

### Collection: `candles_weekly`

Weekly aggregated bars (Friday close or last trading day of week).

```javascript
{
  symbol: "NIFTY50",
  exchange: "NSE",
  weekEnding: ISODate("..."),
  open: 24000, high: 24300, low: 23850, close: 24250, volume: 0
}
```

### Collection: `fundamentals`

Point-in-time fundamental snapshots.

```javascript
{
  symbol: "HDFCBANK",
  exchange: "NSE",
  asOfDate: ISODate("2026-03-31"),
  pe: 18.5,
  pb: 2.8,
  roe: 16.2,
  eps: 85.4,
  marketCap: 1200000,
  debtToEquity: 0.0,
  promoterHolding: 25.4,
  fiiHolding: 32.1
}
```

### Collection: `technicals` (optional pre-computed)

```javascript
{
  symbol: "INFY",
  exchange: "NSE",
  timeframe: "daily",
  asOfDate: ISODate("..."),
  rsi14: 58.2,
  sma20: 1850.0,
  sma50: 1800.0,
  sma200: 1650.0,
  atr14: 35.5,
  macd: { macd: 12.5, signal: 10.2, histogram: 2.3 }
}
```

## Time Horizon → Collection Mapping

| Horizon | Primary collection | Interval / lookback |
|---------|-------------------|---------------------|
| Intraday | `candles_intraday` | 1m, 5m, 15m — current or last session |
| Short-term | `candles_daily` | Last 20–60 trading days |
| Long-term | `candles_daily` or `candles_weekly` | 6 months – 5 years |

## IST Time Handling

- NSE/BSE session: 9:15 AM – 3:30 PM IST (no lunch break)
- Store `tradeDate` as IST date string to simplify intraday filters
- If timestamps are UTC, convert: IST = UTC + 5:30
- Exclude pre-open (9:00–9:15) and post-close unless explicitly analyzing those

## Data Quality Checks

Before analysis, verify:

1. **Completeness:** Expected bar count for interval (e.g., ~75 five-minute bars per session)
2. **Gaps:** Missing bars around holidays — cross-check NSE holiday calendar
3. **Corporate actions:** Use `adjustedClose` for long-term return calculations
4. **Circuit limits:** Flag if high == low == open == close (possible circuit hit)
