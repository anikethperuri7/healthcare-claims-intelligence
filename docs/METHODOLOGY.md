# Methodology

## Review scenarios

The synthetic generator creates ordinary variation across specialty, procedure, member risk, and time. It then injects a small number of **synthetic review scenarios** such as:

- unusually high allowed amounts relative to same-specialty peers,
- excessive procedure frequency,
- repeated same-day claim patterns,
- abrupt month-over-month billing increases, and
- unusual high-intensity procedure mix.

These labels are used only for model evaluation.

## Provider feature families

Provider features cover:

- volume: claims, unique members, claims per member,
- cost: total allowed, average allowed, cost per member,
- coding mix: high-intensity share and procedure diversity,
- repetition: same-member/same-procedure repeat rate,
- temporal behavior: recent-vs-prior monthly volume and spend change,
- peer-normalized measures within specialty.

## Detection methods

### Robust peer statistics

Median/MAD-based robust z-scores reduce sensitivity to already-extreme providers when measuring peer deviation.

### Isolation Forest

An unsupervised Isolation Forest operates on standardized provider features. Its output is used as one signal, not as the sole decision rule.

### Temporal change detection

Recent 90-day behavior is compared with the provider's prior baseline. Large changes in volume and cost add explicit, explainable signals.

## Review score

The final score is a weighted combination of capped signal strengths and is scaled to 0–100. High scores mean **higher analytical review priority**, not higher certainty of fraud.

Each provider receives reason codes such as:

- `COST_ABOVE_SPECIALTY_PEERS`
- `CLAIM_FREQUENCY_ABOVE_PEERS`
- `REPEAT_SERVICE_PATTERN`
- `SUDDEN_SPEND_INCREASE`
- `MULTIVARIATE_ANOMALY`

## Evaluation

Because this is synthetic data, injected scenario labels provide a limited ground truth. The report includes ranking-oriented metrics such as precision@K, recall@K, and average precision. This evaluates whether the system surfaces injected scenarios without leaking their labels into features.

## Financial exposure

`associated_review_spend` is spending tied to review candidates. It is deliberately not called savings, overpayment, or recoverable dollars.
