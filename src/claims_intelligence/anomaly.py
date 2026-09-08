from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler


def add_anomaly_signals(features: pd.DataFrame, random_state: int = 42) -> pd.DataFrame:
    f = features.copy()
    model_cols = [
        "avg_allowed_peer_z", "claims_per_member_peer_z", "allowed_per_member_peer_z",
        "repeat_pattern_share_peer_z", "high_intensity_share_peer_z",
        "claim_volume_change_pct", "allowed_change_pct",
    ]
    X = f[model_cols].replace([np.inf, -np.inf], np.nan).fillna(0)
    Xs = RobustScaler().fit_transform(X)
    model = IsolationForest(n_estimators=300, contamination=0.08, random_state=random_state)
    model.fit(Xs)
    raw = -model.score_samples(Xs)
    lo, hi = np.quantile(raw, [0.05, 0.98])
    f["isolation_signal"] = ((raw - lo) / max(hi - lo, 1e-9)).clip(0, 1)
    return f
