# Healthcare Claims Intelligence — Example Report

## Executive summary

- Claims analyzed: **120,825**
- Members: **6,000**
- Providers: **349**
- Total allowed spend: **$82,284,565**
- Providers with review score ≥ 75: **2**
- Spend associated with providers scoring ≥ 60: **$652,940**
- Data-quality checks passed: **6/6**
- Synthetic detection average precision: **0.881**
- Precision@20: **85.0%**
- Recall@20: **60.7%**

> Review scores prioritize unusual synthetic patterns for investigation. They do not establish fraud, overpayment, or recoverable savings.

## Visuals

![Monthly allowed spend](charts/monthly_allowed_spend.png)

![Top provider review scores](charts/top_provider_review_scores.png)

![Review-candidate spend by specialty](charts/review_candidate_spend_by_specialty.png)

![Provider score distribution](charts/provider_score_distribution.png)

## Investigation workflow

Use `provider_investigation_queue.csv` to review high-scoring providers and their reason codes, then drill into `claim_review_queue.csv` for individual claim patterns. The Power BI exports provide the same curated model for interactive exploration.

## Methodology

Provider scores combine specialty-aware robust peer statistics, repeated-service patterns, temporal change detection, and an Isolation Forest multivariate anomaly signal. Synthetic scenario labels are excluded from features and used only for evaluation.
