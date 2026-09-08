from __future__ import annotations

from pathlib import Path

import pandas as pd

from .anomaly import add_anomaly_signals
from .database import build_sqlite_database
from .evaluation import evaluate_provider_ranking
from .features import build_claim_features, build_provider_features
from .generate_data import generate_synthetic_claims, write_generated_data
from .quality import run_quality_checks
from .reporting import generate_outputs
from .scoring import score_providers


def run_pipeline(n_claims=120_000, seed=42, project_root: str | Path = ".", output_dir="reports/latest"):
    root = Path(project_root)
    data_dir = root / "data" / "generated"
    out = root / output_dir
    data = generate_synthetic_claims(n_claims=n_claims, seed=seed)
    write_generated_data(data, data_dir)
    build_sqlite_database(data_dir, data_dir / "claims_intelligence.sqlite")
    quality = run_quality_checks(data.claims, data.members, data.providers)
    if not quality["passed"].all():
        raise RuntimeError("Data-quality checks failed. See generated quality output.")
    pf = build_provider_features(data.claims, data.providers, data.procedures)
    pf = add_anomaly_signals(pf, random_state=seed)
    scored = score_providers(pf)
    cf = build_claim_features(data.claims, data.providers, data.procedures)
    evaluation = evaluate_provider_ranking(scored, data.ground_truth, out / "model_evaluation.json")
    generate_outputs(data.claims, data.members, data.providers, data.procedures, data.diagnoses, scored, cf, quality, evaluation, out)
    return {"quality": quality, "provider_scores": scored, "claim_features": cf, "evaluation": evaluation}
