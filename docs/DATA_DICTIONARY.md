# Data Dictionary

## members
- `member_id`: synthetic member identifier
- `birth_year`: synthetic birth year
- `sex`: synthetic demographic category
- `risk_band`: low / medium / high synthetic utilization-risk band
- `region`: synthetic geographic region

## providers
- `provider_id`: synthetic provider identifier
- `specialty`: provider peer group
- `region`: synthetic region
- `network_status`: in-network / out-of-network

## procedures
- `procedure_code`: synthetic procedure code
- `procedure_name`: synthetic procedure label
- `service_category`: professional, imaging, lab, facility, therapy, emergency
- `intensity_level`: 1–5 synthetic resource-intensity indicator
- `base_allowed_amount`: generator baseline, not a real reimbursement rate

## diagnoses
- `diagnosis_code`: synthetic diagnosis code
- `diagnosis_group`: simplified diagnosis category

## claims
- `claim_id`: claim identifier
- `member_id`, `provider_id`, `procedure_code`, `diagnosis_code`: foreign keys
- `service_date`: synthetic service date
- `allowed_amount`: synthetic allowed cost
- `paid_amount`: synthetic paid cost
- `member_liability`: allowed minus paid
- `units`: synthetic service units
- `place_of_service`: simplified setting

## review_ground_truth
Used only to evaluate synthetic detection performance.
- `provider_id`
- `scenario_type`
- `scenario_start_date`
- `scenario_description`
