# Macro Country Scorecard

A quantitative sovereign risk scoring framework covering **14 countries** across **5 macro dimensions**, designed to support country-level credit assessment, investment eligibility screening, and portfolio risk monitoring.

---

## Overview

This tool ingests macroeconomic time series data, computes standardised Z-scores across multiple time horizons, applies a multi-step score transformation pipeline, and generates structured PDF scorecard reports per country.

It was built to address a core challenge in EM fixed income and treasury portfolios: producing **consistent, comparable, and reproducible** country risk assessments across heterogeneous data sources.

---

## Country Coverage

| Region | Countries |
|--------|-----------|
| Americas | USA, BRA, MEX, ARG, CHL, COL |
| Asia-Pacific | IND, IDN, CHN, MYS |
| EMEA | ZAF, TUR, EGY, CZE |

---

## Scoring Framework

Risk is assessed across **5 macro areas**, each decomposed into criteria and individual indicators:

| Area | Key Criteria |
|------|-------------|
| **Economic Stability** | GDP growth, inflation, unemployment, REER, output gap |
| **Fiscal Soundness** | Government balance, debt/GDP, interest payments, debt sustainability |
| **External Vulnerability** | Current account, FX reserves, external debt, FDI, IIP |
| **Credit & Liquidity** | Credit-to-GDP gap, broad money, financial soundness indicators |
| **Market & Sovereign Risk** | Country risk premium, credit ratings, CLI, TFP, GINI |

Each indicator is sourced from international databases (World Bank WDI, IMF WEO/IFS/BOP, OECD, BIS, TacEconomics).

---

## Methodology

### Z-Score Computation
For each indicator `i`, country `c`, and time `t`:

```
Z(i,c,t) = (X(i,c,t) - μ(i)) / σ(i)
```

Three temporal horizons are computed:
- **Current** — latest available observation
- **1-Year rolling** — 12-month rolling window
- **3-Year rolling** — 36-month rolling window

### Score Transformation Pipeline

The raw Z-score passes through three successive transformations before grading:

**1. Normalised score** — Z-score rescaled to a continuous [0, 100] range, ensuring cross-indicator comparability regardless of the original unit or distribution of the macro series.

**2. Dilated score** — non-linear expansion of the normalised score to amplify differentiation in the tails, reducing central compression and improving discrimination between borderline cases.

**3. Smoothed score** — exponentially weighted moving average applied to the dilated score, reducing noise from monthly data revisions and improving signal stability for trend monitoring and reporting.

### Grading Scale
The final smoothed score is mapped to a **0–5 ordinal grade**:

| Z-Score Range | Grade |
|--------------|-------|
| ≤ −2.0 | 0 — Very Weak |
| −2.0 to −1.0 | 1 — Weak |
| −1.0 to 0.0 | 2 — Below Average |
| 0.0 to +1.0 | 3 — Average |
| +1.0 to +2.0 | 4 — Strong |
| > +2.0 | 5 — Very Strong |

Grades are aggregated bottom-up: symbol → criterion (17) → area (5) → overall country score.

---

## Pipeline

```
data/
├── LIST_MACRO_INDICATOR.csv              # Indicator metadata (symbol, area, criterion, source)
├── LIST_COUNTRIES.csv                    # Country universe
├── CONSOLIDATEDDATASET.csv               # Raw time series (178,000+ observations)
├── TransformedDataset.csv                # Enriched dataset with Z-scores and transformed scores
├── {CCY}_scorecard.xlsx                  # Aggregated scorecard per country (3 tabs)
├── SPREAD_YIELD_EM.csv                   # Sovereign spreads (monthly)
└── CDS_EM.csv                            # 5Y CDS spreads (monthly)

scripts/
├── taceconomics_script.py                # Data ingestion via TacEconomics API
├── DATAcountryspecific.py                # Rolling Z-score computation per country
├── DATAGrade.py                          # Grade assignment (0–5 scale)
├── DATAscorecard.py                      # Area/criterion aggregation + PDF generation
└── _OUTPUT_TEST_GRAPH_SCORECARD_.py      # Visualisation layer (radar charts, heatmaps)

output/
└── {CCY}_Macro_Analysis_Report.pdf       # Final scorecard report per country
```

---

## Output

Each country scorecard (`{CCY}_scorecard.xlsx`) contains three structured tabs:

- **Symbol Scores** — 47 indicators × Z-score / 1Y / 3Y
- **Criterion Scores** — 17 criteria aggregated
- **Area Scores** — 5 macro areas aggregated

Each country PDF report includes:

- **Cover page** — Overall grade, 1Y and 3Y grade evolution
- **Summary tables** — Z-scores and grades by area
- **Radar charts** — Area-level profile across 3 time horizons
- **Heatmaps** — Criterion-level grades and Z-scores over time
- **Contribution matrix** — Criterion × Area decomposition

---

## Dataset Scale

| Dimension | Count |
|-----------|-------|
| Countries | 14 |
| Macro indicators | 47 symbols |
| Criteria | 17 |
| Macro areas | 5 |
| Raw observations | ~178,000 |
| Transformed observations (with scores) | ~178,000 |
| Time series start | 2000 |

Market data layer (separate feeds):
- **Sovereign spreads** (EMBI-style, monthly, 7 EM countries)
- **CDS 5Y** (monthly, 14 countries)

---

## Key Dependencies

```
pandas
numpy
matplotlib
seaborn
openpyxl
taceconomics    # API key required — set via TAC_API_KEY env variable
```

Install with:
```bash
pip install -r requirements.txt
```

> ⚠️ API key must be set as an environment variable: `export TAC_API_KEY=your_key_here`

---

## Use Cases

- **Counterparty / issuer eligibility screening** for treasury and liquidity portfolios
- **Sovereign credit monitoring** across EM and DM universes
- **Relative value analysis** — cross-country grade comparison
- **Risk reporting** — structured PDF output for investment committees or risk functions

---

## Author

Victor | Asset Management & Fixed Income Portfolio Management  
*Master 222 Asset Management — Paris Dauphine | Master Financial Markets & Risk — TSE*
