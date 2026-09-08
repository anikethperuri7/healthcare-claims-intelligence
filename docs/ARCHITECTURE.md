# Architecture

## Analytical flow

The project separates responsibilities so each stage can be tested and explained independently.

1. `generate_data.py` creates synthetic dimensions and claims plus hidden scenario labels.
2. `database.py` loads normalized tables into SQLite and creates indexes.
3. SQL scripts demonstrate analyst-facing warehouse queries.
4. `quality.py` validates the generated warehouse before analysis.
5. `features.py` creates provider- and claim-level analytical features.
6. `anomaly.py` produces robust-statistical, Isolation Forest, and temporal-change signals.
7. `scoring.py` combines explainable signals into a 0–100 review score and reason codes.
8. `evaluation.py` compares ranked review candidates with synthetic scenario labels.
9. `reporting.py` writes high-resolution charts, investigation queues, dashboard exports, and an executive report.

## Design choice: hidden synthetic ground truth

The generator writes `review_ground_truth.csv`, but detection functions do not use it as an input feature. It is joined only during evaluation. This makes the project more rigorous than simply generating anomalies and then directly scoring the labels that created them.
