import pandas as pd
from claims_intelligence.quality import run_quality_checks


def test_quality_checks_pass_for_valid_minimal_data():
    claims = pd.DataFrame({
        "claim_id": ["C1"], "member_id": ["M1"], "provider_id": ["P1"],
        "procedure_code": ["PX1"], "diagnosis_code": ["DX1"], "service_date": ["2025-01-01"],
        "allowed_amount": [100.0], "paid_amount": [80.0], "member_liability": [20.0], "units": [1]
    })
    members = pd.DataFrame({"member_id": ["M1"]})
    providers = pd.DataFrame({"provider_id": ["P1"]})
    result = run_quality_checks(claims, members, providers)
    assert result["passed"].all()
