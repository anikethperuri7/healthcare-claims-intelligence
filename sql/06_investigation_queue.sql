-- SQL-only preliminary review queue; Python later adds multivariate scoring.
WITH provider_stats AS (
  SELECT c.provider_id, p.specialty,
         COUNT(*) AS claims,
         COUNT(DISTINCT member_id) AS members,
         AVG(allowed_amount) AS avg_allowed,
         SUM(allowed_amount) AS total_allowed
  FROM claims c JOIN providers p USING(provider_id)
  GROUP BY c.provider_id, p.specialty
), peer AS (
  SELECT *,
         PERCENT_RANK() OVER (PARTITION BY specialty ORDER BY avg_allowed) AS cost_rank,
         PERCENT_RANK() OVER (PARTITION BY specialty ORDER BY claims * 1.0 / NULLIF(members,0)) AS frequency_rank
  FROM provider_stats
)
SELECT provider_id, specialty, claims, members, avg_allowed, total_allowed, cost_rank, frequency_rank,
       ROUND(100 * (0.55 * cost_rank + 0.45 * frequency_rank), 1) AS sql_review_score
FROM peer
ORDER BY sql_review_score DESC
LIMIT 50;
