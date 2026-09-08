-- Compare recent quarter with the prior quarter at provider level.
WITH q AS (
  SELECT
    provider_id,
    SUM(CASE WHEN service_date >= '2025-10-01' THEN 1 ELSE 0 END) AS recent_claims,
    SUM(CASE WHEN service_date >= '2025-10-01' THEN allowed_amount ELSE 0 END) AS recent_allowed,
    SUM(CASE WHEN service_date >= '2025-07-01' AND service_date < '2025-10-01' THEN 1 ELSE 0 END) AS prior_claims,
    SUM(CASE WHEN service_date >= '2025-07-01' AND service_date < '2025-10-01' THEN allowed_amount ELSE 0 END) AS prior_allowed
  FROM claims
  GROUP BY provider_id
)
SELECT
  *,
  ROUND(100.0 * (recent_claims - prior_claims) / NULLIF(prior_claims,0), 1) AS claim_change_pct,
  ROUND(100.0 * (recent_allowed - prior_allowed) / NULLIF(prior_allowed,0), 1) AS spend_change_pct
FROM q
WHERE prior_claims >= 5
ORDER BY spend_change_pct DESC;
