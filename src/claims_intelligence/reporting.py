from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


def _save_fig(fig, path: Path):
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def generate_outputs(
    claims,
    members,
    providers,
    procedures,
    diagnoses,
    provider_scores,
    claim_features,
    quality,
    evaluation,
    out_dir,
):
    out = Path(out_dir)
    charts = out / "charts"
    exports = out / "dashboard_exports"

    charts.mkdir(parents=True, exist_ok=True)
    exports.mkdir(parents=True, exist_ok=True)

    queue_cols = [
        "provider_id",
        "specialty",
        "region",
        "network_status",
        "review_score",
        "priority_band",
        "review_reasons",
        "claim_count",
        "unique_members",
        "total_allowed",
        "avg_allowed",
        "claims_per_member",
        "repeat_pattern_share",
        "high_intensity_share",
        "claim_volume_change_pct",
        "allowed_change_pct",
        "associated_review_spend",
    ]

    provider_scores[queue_cols].to_csv(
        out / "provider_investigation_queue.csv",
        index=False,
    )

    claim_queue = claim_features.nlargest(500, "claim_rule_score")[
        [
            "claim_id",
            "member_id",
            "provider_id",
            "specialty",
            "procedure_code",
            "service_date",
            "allowed_amount",
            "paid_amount",
            "allowed_vs_peer_ratio",
            "same_day_repeat_count",
            "claim_rule_score",
        ]
    ]

    claim_queue.to_csv(out / "claim_review_queue.csv", index=False)
    quality.to_csv(out / "data_quality_results.csv", index=False)

    # Dashboard exports
    claims.to_csv(exports / "fact_claims.csv", index=False)
    members.to_csv(exports / "dim_members.csv", index=False)
    providers.to_csv(exports / "dim_providers.csv", index=False)
    procedures.to_csv(exports / "dim_procedures.csv", index=False)
    diagnoses.to_csv(exports / "dim_diagnoses.csv", index=False)
    provider_scores[queue_cols].to_csv(
        exports / "provider_scores.csv",
        index=False,
    )
    claim_queue.to_csv(exports / "claim_review_queue.csv", index=False)

    # Charts

    # Monthly spend — exclude an incomplete final month so a partial
    # reporting period is not presented as a real spending decline.
    dated_claims = claims.copy()
    dated_claims["service_date"] = pd.to_datetime(dated_claims["service_date"])
    dated_claims["month"] = dated_claims["service_date"].dt.to_period("M")

    monthly = (
        dated_claims.groupby("month")["allowed_amount"]
        .sum()
        .sort_index()
    )

    last_service_date = dated_claims["service_date"].max()
    last_month = last_service_date.to_period("M")
    last_calendar_day = last_month.to_timestamp(how="end").normalize()

    if last_service_date.normalize() < last_calendar_day:
        monthly = monthly[monthly.index != last_month]

    monthly.index = monthly.index.astype(str)

    fig, ax = plt.subplots(figsize=(13, 6.5))
    monthly.plot(ax=ax)
    ax.set_title("Monthly Allowed Spend", fontsize=18)
    ax.set_xlabel("Month", fontsize=13)
    ax.set_ylabel("Allowed spend ($)", fontsize=13)
    ax.tick_params(axis="x", rotation=45, labelsize=10)
    ax.tick_params(axis="y", labelsize=11)
    _save_fig(fig, charts / "monthly_allowed_spend.png")

    # Highest-priority providers
    top = provider_scores.head(15).sort_values("review_score")

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.barh(top["provider_id"], top["review_score"])
    ax.set_title("Top Provider Review Scores", fontsize=18)
    ax.set_xlabel("Review score (0–100)", fontsize=13)
    ax.tick_params(labelsize=11)
    _save_fig(fig, charts / "top_provider_review_scores.png")

    # Only show specialties with review-candidate spend.
    spec = (
        provider_scores.groupby(
            "specialty",
            as_index=False,
        )["associated_review_spend"]
        .sum()
        .query("associated_review_spend > 0")
        .sort_values("associated_review_spend")
    )

    fig, ax = plt.subplots(figsize=(12, 6.5))
    ax.barh(
        spec["specialty"],
        spec["associated_review_spend"],
    )
    ax.set_title(
        "Spend Associated With Review Candidates by Specialty",
        fontsize=17,
    )
    ax.set_xlabel("Associated allowed spend ($)", fontsize=13)
    ax.tick_params(labelsize=11)
    _save_fig(
        fig,
        charts / "review_candidate_spend_by_specialty.png",
    )

    # Distribution of provider review scores
    score_dist = provider_scores["review_score"]

    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.hist(score_dist, bins=25)
    ax.set_title("Provider Review Score Distribution", fontsize=18)
    ax.set_xlabel("Review score", fontsize=13)
    ax.set_ylabel("Providers", fontsize=13)
    ax.tick_params(labelsize=11)
    _save_fig(fig, charts / "provider_score_distribution.png")

    # Report metrics
    total_spend = float(claims["allowed_amount"].sum())
    review_spend = float(provider_scores["associated_review_spend"].sum())
    very_high = int((provider_scores["review_score"] >= 75).sum())
    qpass = int(quality["passed"].sum())
    qtotal = int(len(quality))

    report = f"""# Healthcare Claims Intelligence — Example Report

## Executive summary

- Claims analyzed: **{len(claims):,}**
- Members: **{claims['member_id'].nunique():,}**
- Providers: **{claims['provider_id'].nunique():,}**
- Total allowed spend: **${total_spend:,.0f}**
- Providers with review score ≥ 75: **{very_high:,}**
- Spend associated with providers scoring ≥ 60: **${review_spend:,.0f}**
- Data-quality checks passed: **{qpass}/{qtotal}**
- Synthetic detection average precision: **{evaluation['average_precision']:.3f}**
- Precision@20: **{evaluation['precision_at_20']:.1%}**
- Recall@20: **{evaluation['recall_at_20']:.1%}**

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
"""

    (out / "report.md").write_text(report, encoding="utf-8")