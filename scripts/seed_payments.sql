-- 결제 데이터 시드 SQL
-- 실행: supabase db remote exec -f scripts/seed_payments.sql

-- 테스트용 결제 데이터 생성
INSERT INTO payments (customer_id, payment_date, amount, payment_method)
SELECT 
    c.customer_id,
    CURRENT_DATE - (n * INTERVAL '1 day'),
    CASE 
        WHEN random() < 0.2 THEN 50000
        WHEN random() < 0.4 THEN 80000  
        WHEN random() < 0.6 THEN 100000
        WHEN random() < 0.8 THEN 150000
        ELSE 200000
    END,
    CASE 
        WHEN random() < 0.4 THEN 'card'
        WHEN random() < 0.7 THEN 'transfer'
        ELSE 'cash'
    END
FROM customers c
CROSS JOIN generate_series(1, 2) AS n  -- 고객당 최대 2개 결제
WHERE c.customer_id <= 20  -- 처음 20명만
ORDER BY random()
LIMIT 30;  -- 총 30개 결제 데이터

-- 결과 확인
SELECT 
    COUNT(*) as total_payments,
    COUNT(DISTINCT customer_id) as customers_with_payments,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_amount
FROM payments;