from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


def build_sqlite_database(data_dir: str | Path, db_path: str | Path) -> Path:
    data_dir = Path(data_dir)
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    tables = {
        "members": "members.csv",
        "providers": "providers.csv",
        "procedures": "procedures.csv",
        "diagnoses": "diagnoses.csv",
        "claims": "claims.csv",
        "review_ground_truth": "review_ground_truth.csv",
    }
    with sqlite3.connect(db_path) as conn:
        for table, filename in tables.items():
            df = pd.read_csv(data_dir / filename)
            df.to_sql(table, conn, index=False, if_exists="replace")
        conn.executescript("""
            CREATE INDEX idx_claims_provider ON claims(provider_id);
            CREATE INDEX idx_claims_member ON claims(member_id);
            CREATE INDEX idx_claims_service_date ON claims(service_date);
            CREATE INDEX idx_claims_procedure ON claims(procedure_code);
        """)
    return db_path
