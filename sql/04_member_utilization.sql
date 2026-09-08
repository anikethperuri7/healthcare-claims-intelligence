WITH member_kpis AS (
  SELECT
    member_id,
    COUNT(*) AS claims,
    COUNT(DISTINCT provider_id) AS providers_seen,
    SUM(allowed_amount) AS total_allowed,
    AVG(allowed_amount) AS avg_allowed
  FROM claims
  GROUP BY member_id
)
SELECT *
FROM member_kpis
ORDER BY total_allowed DESC
LIMIT 100;
