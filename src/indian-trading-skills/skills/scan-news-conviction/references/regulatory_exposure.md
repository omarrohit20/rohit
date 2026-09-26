# Regulatory sector news — high-exposure scrips

Used by `scan-news-conviction` and `scan-news-conviction-futures` when a **sector-wide**
regulatory headline (IRDAI / RBI / SEBI) applies only to **high-exposure** names and the
scrip’s recomputed **conviction is High**.

## Gates (both skills)

1. Headline matches a **regulatory theme** (patterns in `ingest_scan_news.py`)
2. `impact_score >= 6`
3. Scrip is on the theme’s **high-exposure list**, **or** headline explicitly flags the
   scrip/company as exposed (`most exposed`, `hit hardest`, etc.)
4. **High conviction** after scoring — otherwise the regulatory headline is dropped

## Themes

### `irdai_distribution`

IRDAI distribution / commission / bancassurance reforms (e.g. Sep 2026 draft paper).

| High exposure | Rationale |
|---------------|-----------|
| POLICYBZR | PB Fintech — distribution aggregator; brokerages flag as most exposed |
| HDFCLIFE, MAXFIN | Higher distribution-cost / commission exposure (HSBC, Jefferies) |
| IDFCFIRSTB, INDUSINDBK | Highest bancassurance fee share vs earnings (Jefferies) |
| AXISBANK, HDFCBANK | Material bancassurance fees (Macquarie) |
| STARHEALTH, ICICIGI | General / health insurers on commission caps (Jefferies) |

### `rbi_banking`

RBI banking regulation affecting fee income / lending norms (extend as needed).

| High exposure | Rationale |
|---------------|-----------|
| IDFCFIRSTB, INDUSINDBK, AXISBANK, HDFCBANK | Private banks with material fee / distribution income |
| RBLBANK, AUBANK | Smaller private banks, higher relative fee sensitivity |

### `sebi_market`

SEBI rules affecting brokers / market infrastructure (extend as needed).

| High exposure | Rationale |
|---------------|-----------|
| POLICYBZR | Broker-adjacent distribution platform |
| BSE, MCX | Exchange / market infra |

Update scrip lists when brokerages publish exposure rankings for new circulars.
