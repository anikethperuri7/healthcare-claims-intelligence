from claims_intelligence.anomaly import add_anomaly_signals
from claims_intelligence.features import build_provider_features
from claims_intelligence.generate_data import generate_synthetic_claims
from claims_intelligence.scoring import score_providers


def test_scores_are_explainable_and_bounded():
    d = generate_synthetic_claims(n_claims=6000, seed=11)
    f = add_anomaly_signals(build_provider_features(d.claims, d.providers, d.procedures), random_state=11)
    s = score_providers(f)
    assert s["review_score"].between(0, 100).all()
    assert s["review_reasons"].notna().all()
