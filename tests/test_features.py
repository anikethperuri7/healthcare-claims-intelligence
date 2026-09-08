from claims_intelligence.generate_data import generate_synthetic_claims
from claims_intelligence.features import build_provider_features


def test_provider_features_have_peer_columns():
    d = generate_synthetic_claims(n_claims=5000, seed=7)
    f = build_provider_features(d.claims, d.providers, d.procedures)
    assert "avg_allowed_peer_z" in f.columns
    assert "claims_per_member_peer_z" in f.columns
    assert len(f) > 100
