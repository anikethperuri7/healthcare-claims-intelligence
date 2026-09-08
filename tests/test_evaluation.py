from claims_intelligence.anomaly import add_anomaly_signals
from claims_intelligence.evaluation import evaluate_provider_ranking
from claims_intelligence.features import build_provider_features
from claims_intelligence.generate_data import generate_synthetic_claims
from claims_intelligence.scoring import score_providers


def test_evaluation_returns_ranking_metrics():
    d = generate_synthetic_claims(n_claims=8000, seed=3)
    s = score_providers(add_anomaly_signals(build_provider_features(d.claims, d.providers, d.procedures), random_state=3))
    m = evaluate_provider_ranking(s, d.ground_truth)
    assert 0 <= m["average_precision"] <= 1
    assert "precision_at_20" in m
