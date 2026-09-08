from __future__ import annotations

import pandas as pd

REQUIRED_CLAIM_COLUMNS = {
    "claim_id", "member_id", "provider_id", "procedure_code", "diagnosis_code",
    "service_date", "allowed_amount", "paid_amount", "member_liability", "units",
}


def run_quality_checks(claims: pd.DataFrame, members: pd.DataFrame, providers: pd.DataFrame) -> pd.DataFrame:
    results = []
    missing_cols = REQUIRED_CLAIM_COLUMNS - set(claims.columns)
    results.append(("required_columns_present", len(missing_cols) == 0, f"missing={sorted(missing_cols)}"))
    results.append(("claim_id_unique", claims["claim_id"].is_unique, f"duplicates={claims['claim_id'].duplicated().sum()}"))
    results.append(("allowed_amount_nonnegative", bool((claims["allowed_amount"] >= 0).all()), f"negative={(claims['allowed_amount'] < 0).sum()}"))
    results.append(("paid_not_above_allowed", bool((claims["paid_amount"] <= claims["allowed_amount"] + 0.01).all()), f"violations={(claims['paid_amount'] > claims['allowed_amount'] + 0.01).sum()}"))
    results.append(("member_fk_valid", bool(claims["member_id"].isin(members["member_id"]).all()), f"invalid={(~claims['member_id'].isin(members['member_id'])).sum()}"))
    results.append(("provider_fk_valid", bool(claims["provider_id"].isin(providers["provider_id"]).all()), f"invalid={(~claims['provider_id'].isin(providers['provider_id'])).sum()}"))
    return pd.DataFrame(results, columns=["check", "passed", "details"])
