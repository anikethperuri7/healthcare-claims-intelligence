-- Specialty-aware peer benchmarking using window functions.
WITH provider_kpis AS (
  SELECT
    c.provider_id,
    p.specialty,
    COUNT(*) AS claim_count,
    COUNT(DISTINCT c.member_id) AS unique_members,
    AVG(c.allowed_amount) AS avg_allowed,
    SUM(c.allowed_amount) AS total_allowed
  FROM claims c
  JOIN providers p ON c.provider_id = p.provider_id
  GROUP BY c.provider_id, p.specialty
), ranked AS (
  SELECT
    *,
    PERCENT_RANK() OVER (PARTITION BY specialty ORDER BY avg_allowed) AS avg_allowed_pct_rank,
    PERCENT_RANK() OVER (PARTITION BY specialty ORDER BY claim_count * 1.0 / NULLIF(unique_members,0)) AS frequency_pct_rank,
    RANK() OVER (PARTITION BY specialty ORDER BY total_allowed DESC) AS spend_rank_in_specialty
  FROM provider_kpis
)
SELECT *
FROM ranked
WHERE avg_allowed_pct_rank >= 0.90 OR frequency_pct_rank >= 0.90
ORDER BY specialty, avg_allowed_pct_rank DESC;
