-- Core warehouse quality checks.
SELECT COUNT(*) AS duplicate_claim_ids
FROM (SELECT claim_id FROM claims GROUP BY claim_id HAVING COUNT(*) > 1);

SELECT COUNT(*) AS negative_allowed_amounts
FROM claims WHERE allowed_amount < 0;

SELECT COUNT(*) AS paid_above_allowed
FROM claims WHERE paid_amount > allowed_amount;

SELECT COUNT(*) AS missing_provider_keys
FROM claims c LEFT JOIN providers p ON c.provider_id = p.provider_id
WHERE p.provider_id IS NULL;
