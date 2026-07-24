# Target Methodology Reference

Detailed rules for computing price targets across horizons. Used by the mongodb-financial-analysis skill.

## General Principles

1. **Targets are zones, not exact prices** — round to tick size (₹0.05 for most NSE stocks, ₹0.50 for higher-priced)
2. **Risk-first** — define stop-loss before targets; reject setups with R:R < 1:1.5
3. **Confluence increases confidence** — target at intersection of Fib + prior S/R + moving average scores higher
4. **Volume validates** — breakout targets require above-average volume on the breakout bar

## Intraday Target Detail

### VWAP Bands

```
Upper band = VWAP + (0.3% × VWAP)
Lower band = VWAP - (0.3% × VWAP)
```

Mean-reversion: fade moves to outer band back toward VWAP.
Momentum: hold above VWAP for longs, below for shorts.

### Classic Pivot Points

From previous session's H, L, C:

```
P  = (H + L + C) / 3
R1 = (2 × P) - L
R2 = P + (H - L)
R3 = H + 2 × (P - L)
S1 = (2 × P) - H
S2 = P - (H - L)
S3 = L - 2 × (H - P)
```

Use R1/S1 for T1, R2/S2 for T2 in trending sessions.

### Opening Range Breakout (ORB)

- Define range: first 15 min (3 × 5m bars) or 30 min (6 bars)
- Long entry: break above OR high with volume > 1.5× average 5m volume
- T1: OR height projected above breakout
- Stop: OR low (long) or OR high (short)

## Short-Term Target Detail

### Measured Move

```
Breakout level = swing high (long) or swing low (short)
Pattern height = swing high - swing low of base
Target = breakout level + pattern height (long)
```

### ATR-Based Stops and Targets

```
ATR(14) on daily bars
Stop distance  = 1.5 × ATR
T1 distance    = 1.0 × ATR
T2 distance    = 2.0 × ATR
T3 distance    = 3.0 × ATR
```

### RSI Filters

| RSI Zone | Interpretation | Target approach |
|----------|---------------|-----------------|
| 30–40 | Recovering from oversold | T1 at 20 SMA, T2 at prior swing high |
| 40–60 | Healthy trend | Standard measured move |
| 60–70 | Strong but not extended | Tighter stops, T1 at prior resistance |
| > 70 | Overbought | Reduce size; mean-reversion to 20 SMA |
| < 30 | Oversold | Counter-trend only with reversal pattern |

## Long-Term Target Detail

### Fibonacci Extensions

Identify major swing: significant low → significant high (uptrend).

```
Range = swing high - swing low
T1 (1.000) = swing high (already reached)
T2 (1.272) = swing high + 0.272 × range
T3 (1.618) = swing high + 0.618 × range
```

### 52-Week Range Position

```
Position % = (close - 52wLow) / (52wHigh - 52wLow) × 100
```

| Position | Interpretation |
|----------|---------------|
| 0–20% | Near lows — reversal or value zone |
| 20–50% | Lower half — recovery phase |
| 50–80% | Upper half — trending |
| 80–100% | Near highs — breakout or exhaustion |

### Trend Channel

Fit linear regression on 6-month daily closes.

- Upper channel: regression + 2σ
- Lower channel: regression - 2σ
- Target at upper channel for longs in established uptrend

## India-Specific Adjustments

| Factor | Adjustment |
|--------|------------|
| Circuit limit (10%) | Cap targets at 90% of upper circuit from prev close |
| F&O ban period | Flag stock; avoid fresh swing entries |
| Results week | Widen stops by 0.5× ATR; reduce position size |
| Gap up/down > 2% | Recalculate pivots from prior close; gap may act as S/R |
| Low liquidity (< ₹5 Cr daily turnover) | Widen targets; reduce conviction |

## Confidence Scoring

Assign 1 point each (max 5 per horizon):

1. Trend alignment (price vs key MAs)
2. Volume confirmation
3. Multi-timeframe agreement
4. Clean S/R level (tested 2+ times)
5. Favorable R:R ≥ 1:2

| Score | Confidence |
|-------|------------|
| 4–5 | High |
| 2–3 | Medium |
| 0–1 | Low — note as watchlist only |
