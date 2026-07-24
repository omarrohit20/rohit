# Conviction · Sentiment · Probability Score

Mandatory fields on every mongo-trade-agent ranked result (Priority board +
horizon detail + News snapshot when useful).

## Required columns

| Field | Values / format | Source |
|-------|-----------------|--------|
| **Sentiment** | `Bullish` · `Bearish` · `Neutral` · `Mixed` | Helper `bias` + news polish |
| **Conviction** | `High` · `Med` · `Low` | Score magnitude + R:R + tag density |
| **Prob%** (`probability_score`) | Integer **0–100** (helper emits ~10–95) | Calibrated from score, R:R, tags |

Helper (`query_suggestions.py`) emits these on each ranked row. The agent may
nudge Sentiment to `Mixed` when news conflicts with tape, and may trim Prob% if
adverse news appears — never invent High conviction without supporting scan tags.

## How the helper derives them

1. **Sentiment** ← horizon `bias` (`bullish`/`bearish`/`neutral`).
2. **Prob%** ← `50 + score×5`, then ± for R:R and tag count; clamp 10–95.
3. **Conviction** ← High if `|score|≥5` and R:R≥1.0 (or `|score|≥4` with R:R≥1.2 / strong tags); Med if `|score|≥2`; else Low.

## Lead table shapes

### Single table

| Priority | Symbol | Sentiment | Conviction | Prob% | Why |
|----------|--------|-----------|------------|-------|-----|
| 1 | TECHM | Bullish | High | 78 | Q1 results + AnchisBuyUp / ReversalLow; already +2% |

### Multiple tables

| Priority | Table | Symbol | Sentiment | Conviction | Prob% | Why |
|----------|-------|--------|-----------|------------|-------|-----|
| 1 | highBuy | TECHM | Bullish | High | 78 | … |

## Agent polish rules

| Situation | Adjust |
|-----------|--------|
| Fresh aligned news catalyst | Keep or +3–5 Prob%; Conviction may stay High/Med |
| News conflicts with bias | Sentiment → `Mixed`; Conviction ≤ Med; cut Prob% |
| Adverse news / broken setup | Sentiment Bearish or Neutral; Conviction Low; may_extend No |
| Extended move, weak R:R | Conviction ≤ Med; Prob% ≤ 60 |

## Do not

- Omit Sentiment, Conviction, or Prob% from Priority or horizon result rows
- Report Prob% as a float or letter grade
- Claim High conviction on Neutral sentiment without explaining the edge
