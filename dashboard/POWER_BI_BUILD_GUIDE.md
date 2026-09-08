# Power BI Build Guide

Import all CSVs from `reports/latest/dashboard_exports/`.

## Model

Create a star-style model around `fact_claims.csv`:

- `dim_members.csv` → `fact_claims.member_id`
- `dim_providers.csv` → `fact_claims.provider_id`
- `dim_procedures.csv` → `fact_claims.procedure_code`
- `dim_diagnoses.csv` → `fact_claims.diagnosis_code`
- `provider_scores.csv` → `dim_providers.provider_id`

Use single-direction relationships from dimensions to facts.

## Page 1 — Executive Overview

Cards:
- Total Claims
- Total Allowed Spend
- PMPM
- High-Priority Providers
- Review-Candidate Spend

Visuals:
- Monthly spend trend
- Spend by service category
- Review-candidate spend by specialty
- Top 10 providers by review score

## Page 2 — Provider Risk

Slicers: specialty, region, network status, score band.

Visuals:
- provider review score ranking
- avg allowed vs specialty median
- claims/member vs specialty median
- reason-code matrix
- drill-through table to claim detail

## Page 3 — Claims Review

Use `claim_review_queue.csv` as the primary table. Add conditional formatting for score/reason columns and drill-through to member/provider context.

## Page 4 — Cost & Utilization

Show monthly trends, service mix, cost per member, high-utilization members, and procedure category concentration.

## Page 5 — Temporal Signals

Show recent-vs-prior provider volume/spend change and highlight providers with abrupt shifts.

## Design guidance

Use a restrained professional layout, large KPI cards, readable axis labels, and minimal decoration. The goal is an investigation workflow, not a decorative dashboard.
