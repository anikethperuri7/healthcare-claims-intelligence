from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


SPECIALTIES = [
    "Cardiology", "Dermatology", "Emergency Medicine", "Family Medicine",
    "Gastroenterology", "Neurology", "Oncology", "Orthopedics",
    "Radiology", "Urology",
]
SERVICE_CATEGORIES = ["Professional", "Imaging", "Laboratory", "Facility", "Therapy", "Emergency"]
DIAGNOSIS_GROUPS = ["Cardiovascular", "Digestive", "Musculoskeletal", "Neurologic", "Oncology", "Respiratory", "General"]
REGIONS = ["Northeast", "Midwest", "South", "West"]


@dataclass
class GeneratedData:
    members: pd.DataFrame
    providers: pd.DataFrame
    procedures: pd.DataFrame
    diagnoses: pd.DataFrame
    claims: pd.DataFrame
    ground_truth: pd.DataFrame


def generate_synthetic_claims(n_claims: int = 120_000, seed: int = 42) -> GeneratedData:
    rng = np.random.default_rng(seed)
    n_members = max(2500, n_claims // 20)
    n_providers = max(220, n_claims // 343)

    members = pd.DataFrame({
        "member_id": [f"M{i:06d}" for i in range(1, n_members + 1)],
        "birth_year": rng.integers(1940, 2006, n_members),
        "sex": rng.choice(["F", "M"], n_members),
        "risk_band": rng.choice(["Low", "Medium", "High"], n_members, p=[0.55, 0.32, 0.13]),
        "region": rng.choice(REGIONS, n_members, p=[0.18, 0.22, 0.38, 0.22]),
    })

    providers = pd.DataFrame({
        "provider_id": [f"P{i:04d}" for i in range(1, n_providers + 1)],
        "specialty": rng.choice(SPECIALTIES, n_providers),
        "region": rng.choice(REGIONS, n_providers, p=[0.18, 0.22, 0.38, 0.22]),
        "network_status": rng.choice(["In Network", "Out of Network"], n_providers, p=[0.88, 0.12]),
    })

    proc_rows = []
    for i in range(1, 41):
        category = SERVICE_CATEGORIES[(i - 1) % len(SERVICE_CATEGORIES)]
        intensity = int(rng.integers(1, 6))
        base = float(np.round(rng.uniform(45, 600) * (0.65 + 0.35 * intensity), 2))
        proc_rows.append((f"PX{i:03d}", f"Synthetic Procedure {i:02d}", category, intensity, base))
    procedures = pd.DataFrame(proc_rows, columns=["procedure_code", "procedure_name", "service_category", "intensity_level", "base_allowed_amount"])

    diagnoses = pd.DataFrame({
        "diagnosis_code": [f"DX{i:03d}" for i in range(1, 31)],
        "diagnosis_group": [DIAGNOSIS_GROUPS[(i - 1) % len(DIAGNOSIS_GROUPS)] for i in range(1, 31)],
    })

    dates = pd.date_range("2024-01-01", "2025-12-31", freq="D")
    member_weights = members["risk_band"].map(
        {"Low": 1.0, "Medium": 1.55, "High": 2.5}
    ).to_numpy(dtype=float, copy=True)
    member_weights /= member_weights.sum()
    provider_weights = rng.lognormal(mean=0.0, sigma=0.55, size=n_providers)
    provider_weights /= provider_weights.sum()

    member_idx = rng.choice(n_members, n_claims, p=member_weights)
    provider_idx = rng.choice(n_providers, n_claims, p=provider_weights)
    proc_idx = rng.integers(0, len(procedures), n_claims)
    diag_idx = rng.integers(0, len(diagnoses), n_claims)
    service_dates = rng.choice(dates.to_numpy(), n_claims)

    base_amount = procedures.loc[proc_idx, "base_allowed_amount"].to_numpy(float)
    risk_mult = members.loc[member_idx, "risk_band"].map({"Low": 0.95, "Medium": 1.05, "High": 1.15}).to_numpy(float)
    network_mult = providers.loc[provider_idx, "network_status"].map({"In Network": 1.0, "Out of Network": 1.18}).to_numpy(float)
    noise = rng.lognormal(mean=0.0, sigma=0.30, size=n_claims)
    units = rng.choice([1, 1, 1, 1, 2, 3], n_claims)
    allowed = base_amount * risk_mult * network_mult * noise * np.sqrt(units)
    paid_pct = rng.uniform(0.72, 0.96, n_claims)

    claims = pd.DataFrame({
        "claim_id": [f"C{i:07d}" for i in range(1, n_claims + 1)],
        "member_id": members.loc[member_idx, "member_id"].to_numpy(),
        "provider_id": providers.loc[provider_idx, "provider_id"].to_numpy(),
        "procedure_code": procedures.loc[proc_idx, "procedure_code"].to_numpy(),
        "diagnosis_code": diagnoses.loc[diag_idx, "diagnosis_code"].to_numpy(),
        "service_date": pd.to_datetime(service_dates),
        "allowed_amount": np.round(allowed, 2),
        "paid_amount": np.round(allowed * paid_pct, 2),
        "units": units,
        "place_of_service": rng.choice(["Office", "Outpatient", "Inpatient", "Emergency"], n_claims, p=[0.52, 0.25, 0.13, 0.10]),
    })
    claims["member_liability"] = np.round(claims["allowed_amount"] - claims["paid_amount"], 2)

    # Inject synthetic review scenarios at provider level. Ground-truth labels are not used by scoring.
    candidate_providers = providers["provider_id"].to_numpy()
    selected = rng.choice(candidate_providers, size=min(28, max(16, n_providers // 12)), replace=False)
    scenarios = ["HIGH_COST", "EXCESS_FREQUENCY", "DUPLICATE_PATTERN", "SUDDEN_SPIKE", "HIGH_INTENSITY_MIX"]
    truth_rows = []

    for j, pid in enumerate(selected):
        scenario = scenarios[j % len(scenarios)]
        mask = claims["provider_id"].eq(pid)
        idx = claims.index[mask]
        if len(idx) < 20:
            continue
        if scenario == "HIGH_COST":
            claims.loc[idx, "allowed_amount"] *= 1.9
            claims.loc[idx, "paid_amount"] = claims.loc[idx, "allowed_amount"] * 0.88
        elif scenario == "EXCESS_FREQUENCY":
            base = claims.loc[idx].sample(
                min(60, len(idx)),
                replace=True,
                random_state=seed + j,
            ).copy()
            base["claim_id"] = [f"X{j:03d}{k:05d}" for k in range(len(base))]
            base["service_date"] = pd.to_datetime(base["service_date"]) + pd.to_timedelta(
                rng.integers(1, 60, len(base)), unit="D"
            )
            base["service_date"] = base["service_date"].clip(
                upper=pd.Timestamp("2025-12-31")
            )
            claims = pd.concat([claims, base], ignore_index=True)

        elif scenario == "DUPLICATE_PATTERN":
            samp = claims.loc[idx].sample(min(40, len(idx)), random_state=seed + j).copy()
            dup = samp.copy()
            dup["claim_id"] = [f"D{j:03d}{k:05d}" for k in range(len(dup))]
            dup["allowed_amount"] *= rng.uniform(0.96, 1.04, len(dup))
            dup["paid_amount"] = dup["allowed_amount"] * 0.86
            claims = pd.concat([claims, dup], ignore_index=True)
        elif scenario == "SUDDEN_SPIKE":
            recent = idx[pd.to_datetime(claims.loc[idx, "service_date"]).values >= np.datetime64("2025-10-01")]
            if len(recent) > 0:
                claims.loc[recent, "allowed_amount"] *= 2.2
            base = claims.loc[idx].sample(min(45, len(idx)), replace=True, random_state=seed + j).copy()
            base["claim_id"] = [f"S{j:03d}{k:05d}" for k in range(len(base))]
            base["service_date"] = pd.to_datetime(rng.choice(pd.date_range("2025-10-01", "2025-12-31"), len(base)))
            claims = pd.concat([claims, base], ignore_index=True)
        elif scenario == "HIGH_INTENSITY_MIX":
            hi_codes = procedures.loc[procedures["intensity_level"] >= 4, "procedure_code"].to_numpy()
            claims.loc[idx, "procedure_code"] = rng.choice(hi_codes, len(idx))
            claims.loc[idx, "allowed_amount"] *= 1.35

        truth_rows.append({
            "provider_id": pid,
            "scenario_type": scenario,
            "scenario_start_date": "2025-10-01" if scenario == "SUDDEN_SPIKE" else "2024-01-01",
            "scenario_description": {
                "HIGH_COST": "Synthetic provider allowed amounts elevated relative to peers.",
                "EXCESS_FREQUENCY": "Synthetic provider receives additional high-frequency claims.",
                "DUPLICATE_PATTERN": "Synthetic repeated same-member/procedure/date patterns added.",
                "SUDDEN_SPIKE": "Synthetic late-period volume/spend increase added.",
                "HIGH_INTENSITY_MIX": "Synthetic procedure mix shifted toward high-intensity services.",
            }[scenario],
        })

    claims["allowed_amount"] = claims["allowed_amount"].round(2)
    claims["paid_amount"] = claims["paid_amount"].round(2)
    claims["member_liability"] = (claims["allowed_amount"] - claims["paid_amount"]).round(2)
    claims = claims.sort_values(["service_date", "claim_id"]).reset_index(drop=True)
    ground_truth = pd.DataFrame(truth_rows)
    return GeneratedData(members, providers, procedures, diagnoses, claims, ground_truth)


def write_generated_data(data: GeneratedData, out_dir: str | Path) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    data.members.to_csv(out / "members.csv", index=False)
    data.providers.to_csv(out / "providers.csv", index=False)
    data.procedures.to_csv(out / "procedures.csv", index=False)
    data.diagnoses.to_csv(out / "diagnoses.csv", index=False)
    data.claims.to_csv(out / "claims.csv", index=False)
    data.ground_truth.to_csv(out / "review_ground_truth.csv", index=False)
