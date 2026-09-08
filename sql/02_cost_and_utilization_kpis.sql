-- Executive cost and utilization KPIs.
SELECT
  COUNT(*) AS total_claims,
  COUNT(DISTINCT member_id) AS unique_members,
  COUNT(DISTINCT provider_id) AS unique_providers,
  ROUND(SUM(allowed_amount), 2) AS total_allowed_spend,
  ROUND(AVG(allowed_amount), 2) AS avg_allowed_per_claim,
  ROUND(SUM(allowed_amount) / COUNT(DISTINCT member_id), 2) AS allowed_per_member
FROM claims;

-- Monthly trend.
SELECT
  substr(service_date, 1, 7) AS month,
  COUNT(*) AS claims,
  ROUND(SUM(allowed_amount), 2) AS allowed_spend
FROM claims
GROUP BY month
ORDER BY month;
