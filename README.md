# Credit Risk Monitoring Report

**Author:** Thanh Pham
**Program:** MSc Finance & Data Analysis — ESSCA
**Reference Date:** 31 December 2025
**Portfolio Scope:** 25 entities (15 banks, 10 sovereigns)

---

## Overview

This project implements an internal credit risk monitoring framework for a simulated clearing house environment. It produces a professional committee-style PDF report covering portfolio risk assessment, watchlist management, and market signal monitoring across 25 financial counterparties.

The report replicates the structure and analytical standards of a real-world Credit & Counterparty Risk division — including internal scoring models, rating mapping, market alert triggers, and escalation logic.

---

## Repository Contents

| File | Description |
|---|---|
| `ThanhPham_CreditRisk_Report.pdf` | Final PDF report output — Credit Risk Committee format |
| `ThanhPham_CreditRisk_Report.md` | Markdown version of the report |
| `credit_report.py` | Primary PDF generator — ReportLab-based, professional layout |
| `credit_report_v1.py` | Matplotlib-based PDF generator (earlier version, requires data CSV files) |

---

## Methodology

### Internal Scoring — Banks (7-factor model)

| Factor | Weight |
|---|---|
| CET1 ratio | 25% |
| NPL ratio | 20% |
| ROE | 15% |
| Leverage | 10% |
| Loan-to-deposit ratio | 10% |
| Cost-to-income ratio | 10% |
| Liquidity ratio | 10% |

### Internal Scoring — Sovereigns (7-factor model)

| Factor | Weight |
|---|---|
| Debt / GDP | 25% |
| Fiscal balance | 20% |
| Inflation | 15% |
| FX reserves | 15% |
| GDP growth | 10% |
| Political risk | 10% |
| Current account | 5% |

### Rating Mapping

| Score Range | Implied Rating |
|---|---|
| 85 - 100 | AA |
| 75 - 84 | A |
| 65 - 74 | BBB |
| 55 - 64 | BB |
| 40 - 54 | B |
| < 40 | CCC |

### Market Alert Triggers

Four independent signals monitored daily:
- CDS widening > 20bp over 5 trading days
- Bond spread widening > 25bp over 5 trading days
- 5-day equity return below -10%
- 30-day implied equity volatility above 35%

### Watchlist Criteria

An entity is placed on the watchlist if it meets at least one of:
- Internal score below 60
- Non-investment-grade external rating
- Two or more concurrent market alerts
- Score deterioration exceeding 10 points versus prior snapshot

---

## Key Findings (Reference Date: 31 December 2025)

- **18 of 25 entities** on the watchlist (72% of portfolio)
- **Monte dei Paschi** is the sole escalated name — CCC internal rating, CDS at 306bp, NPL ratio 12.4%, negative ROE
- **8 of 10 sovereigns** watchlisted, driven by high debt/GDP, fiscal deficits, and limited reserve buffers
- Only **4 entities** carry investment-grade internal ratings (Nordea A, JPMorgan Chase BBB, ING Group BBB, Intesa Sanpaolo BBB)
- **CDS-bond spread correlation: 0.98** — stress expressed through credit markets, not broad equity sell-off
- Watchlist entities trade at **2x the CDS spread** of non-watchlist names (135bp vs. 68bp average)

---

## How to Run

### Requirements

```bash
pip install reportlab matplotlib pandas
```

### Generate the PDF report

```bash
python credit_report.py
```

Output: `ThanhPham_CreditRisk_Report.pdf`

---

## Data

All portfolio data is **synthetic** — generated to reflect realistic credit risk distributions for educational and analytical purposes. No real market data or proprietary information is used.

---

## Disclaimer

This report is prepared for academic purposes as part of the MSc Finance & Data Analysis program at ESSCA. Internal ratings and scores do not constitute investment advice and are not derived from any real clearing house system.
