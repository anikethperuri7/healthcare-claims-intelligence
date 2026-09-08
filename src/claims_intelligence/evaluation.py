from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import average_precision_score


def evaluate_provider_ranking(scored: pd.DataFrame, ground_truth: pd.DataFrame, output_path: str | Path | None = None) -> dict:
    s = scored[["provider_id", "review_score"]].copy()
    positives = set(ground_truth["provider_id"].astype(str))
    s["is_injected_scenario"] = s["provider_id"].astype(str).isin(positives).astype(int)
    total_pos = max(int(s["is_injected_scenario"].sum()), 1)
    metrics = {
        "providers_evaluated": int(len(s)),
        "injected_scenario_providers": int(s["is_injected_scenario"].sum()),
        "average_precision": round(float(average_precision_score(s["is_injected_scenario"], s["review_score"])), 4),
    }
    for k in [10, 20, 30, 50]:
        top = s.nlargest(min(k, len(s)), "review_score")
        tp = int(top["is_injected_scenario"].sum())
        metrics[f"precision_at_{k}"] = round(tp / len(top), 4)
        metrics[f"recall_at_{k}"] = round(tp / total_pos, 4)
    if output_path:
        Path(output_path).write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics
