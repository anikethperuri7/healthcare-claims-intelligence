from __future__ import annotations

import numpy as np
import pandas as pd


def _positive_signal(s: pd.Series, scale: float) -> pd.Series:
    return (s.clip(lower=0) / scale).clip(0, 1)


def score_providers(features: pd.DataFrame) -> pd.DataFrame:
    f = features.copy()
    f["cost_signal"] = _positive_signal(f["avg_allowed_peer_z"], 4)
    f["frequency_signal"] = _positive_signal(f["claims_per_member_peer_z"], 4)
    f["repeat_signal"] = _positive_signal(f["repeat_pattern_share_peer_z"], 4)
    f["intensity_signal"] = _positive_signal(f["high_intensity_share_peer_z"], 4)
    f["temporal_signal"] = np.maximum(
        _positive_signal(f["claim_volume_change_pct"], 180),
        _positive_signal(f["allowed_change_pct"], 180),
    )
    weights = {
        "cost_signal": 0.20,
        "frequency_signal": 0.18,
        "repeat_signal": 0.18,
        "intensity_signal": 0.12,
        "temporal_signal": 0.14,
        "isolation_signal": 0.18,
    }
    f["review_score"] = 100 * sum(f[k] * v for k, v in weights.items())
    f["review_score"] = f["review_score"].clip(0, 100).round(1)

    def reasons(r):
        out = []
        if r["avg_allowed_peer_z"] >= 2.5: out.append("COST_ABOVE_SPECIALTY_PEERS")
        if r["claims_per_member_peer_z"] >= 2.5: out.append("CLAIM_FREQUENCY_ABOVE_PEERS")
        if r["repeat_pattern_share_peer_z"] >= 2.5: out.append("REPEAT_SERVICE_PATTERN")
        if r["high_intensity_share_peer_z"] >= 2.5: out.append("HIGH_INTENSITY_MIX")
        if max(r["claim_volume_change_pct"], r["allowed_change_pct"]) >= 100: out.append("SUDDEN_BEHAVIOR_CHANGE")
        if r["isolation_signal"] >= 0.75: out.append("MULTIVARIATE_ANOMALY")
        return "; ".join(out) if out else "LOW_SIGNAL"

    f["review_reasons"] = f.apply(reasons, axis=1)
    f["priority_band"] = pd.cut(f["review_score"], bins=[-1, 40, 60, 75, 100], labels=["Low", "Moderate", "High", "Very High"])
    f["associated_review_spend"] = np.where(f["review_score"] >= 60, f["total_allowed"], 0).round(2)
    return f.sort_values("review_score", ascending=False).reset_index(drop=True)
