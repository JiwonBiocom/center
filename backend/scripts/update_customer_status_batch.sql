-- 고객 상태 일괄 업데이트 스크립트

-- 1. last_visit_date가 NULL인 고객은 모두 dormant로
UPDATE customers 
SET customer_status = 'dormant'
WHERE last_visit_date IS NULL
AND customer_status != 'dormant';

-- 2. 30일 이내 방문 고객은 active로
UPDATE customers 
SET customer_status = 'active'
WHERE last_visit_date >= CURRENT_DATE - INTERVAL '30 days'
AND customer_status != 'active';

-- 3. 31-90일 사이 방문 고객은 inactive로
UPDATE customers 
SET customer_status = 'inactive'
WHERE last_visit_date < CURRENT_DATE - INTERVAL '30 days'
AND last_visit_date >= CURRENT_DATE - INTERVAL '90 days'
AND customer_status != 'inactive';

-- 4. 90일 초과 미방문 고객은 dormant로
UPDATE customers 
SET customer_status = 'dormant'
WHERE last_visit_date < CURRENT_DATE - INTERVAL '90 days'
AND customer_status != 'dormant';

-- 5. 상태별 고객 수 확인
SELECT customer_status, COUNT(*) as count
FROM customers
GROUP BY customer_status
ORDER BY customer_status;