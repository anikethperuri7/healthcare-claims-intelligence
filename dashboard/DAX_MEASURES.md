# Suggested DAX Measures

```DAX
Total Claims = COUNTROWS(fact_claims)

Total Allowed Spend = SUM(fact_claims[allowed_amount])

Total Paid Spend = SUM(fact_claims[paid_amount])

Unique Members = DISTINCTCOUNT(fact_claims[member_id])

PMPM = DIVIDE([Total Allowed Spend], [Unique Members] * 24)

High Priority Providers =
CALCULATE(
    DISTINCTCOUNT(provider_scores[provider_id]),
    provider_scores[review_score] >= 75
)

Review Candidate Spend =
SUM(provider_scores[associated_review_spend])
```

Adjust PMPM denominator if the generated time horizon changes from 24 months.
