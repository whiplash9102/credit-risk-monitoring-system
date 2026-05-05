# Credit Risk Monitoring Project

**Author:** Thanh Pham  
**Program:** MSc Finance & Data Analysis — ESSCA  
**Reference Date:** 31 December 2025  
**Portfolio:** 25 entities — 15 Banks / 10 Sovereigns

---

## What this project does

This project builds an internal credit risk monitoring framework for a simulated clearing house.
It covers **25 financial counterparties** (banks and sovereigns) and produces two outputs:

| Output | Purpose | File |
|--------|---------|------|
| **Live monitor** | Interactive scoring dashboard — day-to-day use | `notebooks/credit_monitor.ipynb` |
| **Committee report** | Formatted PDF for risk committee presentation | `reports/ThanhPham_CreditRisk_Report.pdf` |

The two outputs share the same **data and business logic** but are completely independent in implementation.

---

## Repository structure

```
.
├── README.md
├── data/                         ← Raw input data (edit to refresh the monitor)
│   ├── banks_sample.csv          ← 15 banks × 7 financial ratios
│   ├── sovereigns_sample.csv     ← 10 sovereigns × 7 macro indicators
│   └── market_data_sample.csv    ← Daily CDS, spread, vol per entity (~1,650 rows)
├── notebooks/
│   ├── credit_monitor.ipynb      ← Main monitoring notebook (start here)
│   ├── credit_report.ipynb       ← Notebook version of the PDF generator
│   └── credit_risk_monitoring.ipynb
├── outputs/                      ← Generated monitoring tables and charts
├── reports/
│   ├── ThanhPham_CreditRisk_Report.pdf
│   └── ThanhPham_CreditRisk_Report.md
├── src/
│   └── credit_report.py          ← PDF generator (ReportLab)
└── archive/
    └── credit_report_v1.py       ← Earlier PDF version (matplotlib-based)
```

---

## Quick start

### 1. Set up the environment

All code runs in the **`final_project`** conda environment.

```bash
conda activate final_project
pip install pandas matplotlib seaborn numpy scipy plotly ipywidgets
```

### 2. Open the monitoring notebook

```bash
jupyter lab notebooks/credit_monitor.ipynb
```

Run all cells top-to-bottom. The notebook will:
1. Read raw factor data from `data/`
2. Calculate scores from scratch
3. Assign ratings and watchlist flags
4. Render all charts and tables

### 3. Regenerate the PDF report (optional)

```bash
conda run -n final_project python src/credit_report.py
```

Output: `reports/ThanhPham_CreditRisk_Report.pdf`

---

## How the scoring works

### Banks — 7-factor weighted model

| Factor | Weight | Direction |
|--------|--------|-----------|
| CET1 ratio | 25% | Higher = better |
| NPL ratio | 20% | Lower = better |
| ROE | 15% | Higher = better |
| Leverage ratio | 10% | Higher = better |
| Loan-to-deposit ratio | 10% | Lower = better |
| Cost-to-income ratio | 10% | Lower = better |
| Liquidity ratio | 10% | Higher = better |

### Sovereigns — 7-factor weighted model

| Factor | Weight | Direction |
|--------|--------|-----------|
| Debt / GDP | 25% | Lower = better |
| Fiscal balance (% GDP) | 20% | Higher = better |
| Inflation | 15% | Lower = better |
| FX reserves (months) | 15% | Higher = better |
| GDP growth | 10% | Higher = better |
| Political risk (1–10) | 10% | Lower = better |
| Current account | 5% | Higher = better |

Each factor is **min-max normalised** across the peer group to a 0–100 scale, then multiplied by its weight. The final score is the weighted sum (0–100).

### Rating mapping

| Score | Rating |
|-------|--------|
| ≥ 85 | AA |
| ≥ 75 | A |
| ≥ 65 | BBB |
| ≥ 55 | BB |
| ≥ 40 | B |
| < 40 | CCC |

### Watchlist triggers (any one is sufficient)

- Internal score < 60
- ≥ 2 active market alerts on the reference date
- Score deterioration > 10 pts vs prior snapshot

### Market alert triggers (each counts +1, max 4)

| Alert | Condition |
|-------|-----------|
| CDS widening | > 20 bp over 5 trading days |
| Bond spread widening | > 25 bp over 5 trading days |
| Equity return | < −10% over 5 trading days |
| Implied volatility | > 35% (30-day) |

### Action tiers

| Action | Meaning |
|--------|---------|
| Monitor | Standard surveillance |
| Review | Analytical review within 5 business days |
| Escalate | Immediate committee action — exposure and collateral review required |

---

## How to update for a new monitoring period

1. **Edit the CSV files** in `data/` with updated factor values and market data
2. **Change `REF_DATE`** in Section 1 of `notebooks/credit_monitor.ipynb`
3. **Run all cells** — scores, ratings, watchlist, and all charts regenerate automatically

To add or remove an entity, add or delete a row in the relevant CSV file. No code changes needed.

---

## Key findings (Reference Date: 31 December 2025)

- **17 of 25 entities** on the watchlist (68% of portfolio)
- **Monte dei Paschi** is the sole escalated name — CCC internal rating, CDS 306 bp, NPL ratio 12.4%, negative ROE
- **8 of 10 sovereigns** watchlisted, driven by high debt/GDP, fiscal deficits, and limited reserve buffers
- **Nordea** (AA, score 96.8) and **Germany** (AA, score 91.7) are the strongest names in the portfolio
- Watchlist entities trade at approximately **2× the CDS spread** of non-watchlist names

---

## Disclaimer

All portfolio data is **synthetic** — generated to reflect realistic credit risk distributions for educational purposes. Internal ratings do not constitute investment advice and are not derived from any real clearing house system. Prepared as part of the MSc Finance & Data Analysis program at ESSCA.
