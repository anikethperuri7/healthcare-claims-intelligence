from __future__ import annotations

import numpy as np
import pandas as pd


def _robust_z(series: pd.Series) -> pd.Series:
    med = series.median()
    mad = np.median(np.abs(series - med))
    if mad == 0 or np.isnan(mad):
        return pd.Series(np.zeros(len(series)), index=series.index)
    return 0.6745 * (series - med) / mad


def build_provider_features(claims: pd.DataFrame, providers: pd.DataFrame, procedures: pd.DataFrame) -> pd.DataFrame:
    c = claims.copy()
    c["service_date"] = pd.to_datetime(c["service_date"])
    c = c.merge(procedures[["procedure_code", "intensity_level", "service_category"]], on="procedure_code", how="left")
    c["is_high_intensity"] = (c["intensity_level"] >= 4).astype(int)

    # Repeated same member/provider/procedure/day patterns.
    repeat_counts = c.groupby(["provider_id", "member_id", "procedure_code", "service_date"])["claim_id"].transform("count")
    c["is_repeat_pattern"] = (repeat_counts > 1).astype(int)

    g = c.groupby("provider_id")
    f = g.agg(
        claim_count=("claim_id", "count"),
        unique_members=("member_id", "nunique"),
        total_allowed=("allowed_amount", "sum"),
        avg_allowed=("allowed_amount", "mean"),
        median_allowed=("allowed_amount", "median"),
        total_paid=("paid_amount", "sum"),
        avg_units=("units", "mean"),
        high_intensity_share=("is_high_intensity", "mean"),
        repeat_pattern_share=("is_repeat_pattern", "mean"),
        procedure_diversity=("procedure_code", "nunique"),
    ).reset_index()
    f["claims_per_member"] = f["claim_count"] / f["unique_members"].clip(lower=1)
    f["allowed_per_member"] = f["total_allowed"] / f["unique_members"].clip(lower=1)

    recent = c[c["service_date"] >= pd.Timestamp("2025-10-01")].groupby("provider_id").agg(
        recent_claims=("claim_id", "count"), recent_allowed=("allowed_amount", "sum")
    )
    prior = c[(c["service_date"] >= pd.Timestamp("2025-07-01")) & (c["service_date"] < pd.Timestamp("2025-10-01"))].groupby("provider_id").agg(
        prior_claims=("claim_id", "count"), prior_allowed=("allowed_amount", "sum")
    )
    f = f.merge(recent, on="provider_id", how="left").merge(prior, on="provider_id", how="left").fillna(0)
    f["claim_volume_change_pct"] = 100 * (f["recent_claims"] - f["prior_claims"]) / f["prior_claims"].clip(lower=5)
    f["allowed_change_pct"] = 100 * (f["recent_allowed"] - f["prior_allowed"]) / f["prior_allowed"].clip(lower=1000)

    f = f.merge(providers, on="provider_id", how="left")
    peer_cols = ["avg_allowed", "claims_per_member", "allowed_per_member", "repeat_pattern_share", "high_intensity_share"]
    for col in peer_cols:
        f[f"{col}_peer_z"] = f.groupby("specialty")[col].transform(_robust_z)
        f[f"{col}_peer_median"] = f.groupby("specialty")[col].transform("median")
    return f


def build_claim_features(claims: pd.DataFrame, providers: pd.DataFrame, procedures: pd.DataFrame) -> pd.DataFrame:
    c = claims.copy()
    c["service_date"] = pd.to_datetime(c["service_date"])
    c = c.merge(providers[["provider_id", "specialty"]], on="provider_id", how="left")
    c = c.merge(procedures[["procedure_code", "service_category", "intensity_level"]], on="procedure_code", how="left")
    peer_med = c.groupby(["specialty", "procedure_code"])["allowed_amount"].transform("median")
    c["allowed_vs_peer_ratio"] = c["allowed_amount"] / peer_med.clip(lower=1)
    repeat_counts = c.groupby(["provider_id", "member_id", "procedure_code", "service_date"])["claim_id"].transform("count")
    c["same_day_repeat_count"] = repeat_counts
    c["claim_rule_score"] = (
        (c["allowed_vs_peer_ratio"].clip(upper=4) - 1).clip(lower=0) * 25
        + (c["same_day_repeat_count"] - 1).clip(lower=0, upper=3) * 20
        + (c["units"] - 1).clip(lower=0, upper=4) * 5
    ).clip(0, 100)
    return c
