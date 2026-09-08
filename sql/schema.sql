PRAGMA foreign_keys = ON;

CREATE TABLE members (
  member_id TEXT PRIMARY KEY,
  birth_year INTEGER NOT NULL,
  sex TEXT NOT NULL,
  risk_band TEXT NOT NULL,
  region TEXT NOT NULL
);

CREATE TABLE providers (
  provider_id TEXT PRIMARY KEY,
  specialty TEXT NOT NULL,
  region TEXT NOT NULL,
  network_status TEXT NOT NULL
);

CREATE TABLE procedures (
  procedure_code TEXT PRIMARY KEY,
  procedure_name TEXT NOT NULL,
  service_category TEXT NOT NULL,
  intensity_level INTEGER NOT NULL,
  base_allowed_amount REAL NOT NULL
);

CREATE TABLE diagnoses (
  diagnosis_code TEXT PRIMARY KEY,
  diagnosis_group TEXT NOT NULL
);

CREATE TABLE claims (
  claim_id TEXT PRIMARY KEY,
  member_id TEXT NOT NULL REFERENCES members(member_id),
  provider_id TEXT NOT NULL REFERENCES providers(provider_id),
  procedure_code TEXT NOT NULL REFERENCES procedures(procedure_code),
  diagnosis_code TEXT NOT NULL REFERENCES diagnoses(diagnosis_code),
  service_date DATE NOT NULL,
  allowed_amount REAL NOT NULL,
  paid_amount REAL NOT NULL,
  member_liability REAL NOT NULL,
  units INTEGER NOT NULL,
  place_of_service TEXT NOT NULL
);
