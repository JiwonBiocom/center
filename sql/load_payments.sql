-- Supabase에 결제 데이터 로드
-- 실행: supabase db remote exec -f sql/load_payments.sql < backend/seed/payments.csv

-- 중복 방지를 위한 UPSERT 방식 사용
CREATE TEMP TABLE temp_payments (
    payment_id INTEGER,
    customer_id INTEGER,
    payment_date DATE,
    amount DECIMAL(10,2),
    payment_method VARCHAR(20),
    created_at TIMESTAMP
);

-- CSV 데이터를 임시 테이블에 로드
COPY temp_payments (payment_id, customer_id, payment_date, amount, payment_method, created_at)
FROM stdin WITH (FORMAT csv, HEADER true);

-- 기존 데이터와 중복되지 않게 삽입
INSERT INTO payments (customer_id, payment_date, amount, payment_method, created_at)
SELECT 
    tp.customer_id,
    tp.payment_date,
    tp.amount,
    tp.payment_method,
    tp.created_at::timestamp
FROM temp_payments tp
LEFT JOIN payments p ON p.customer_id = tp.customer_id 
    AND p.payment_date = tp.payment_date 
    AND p.amount = tp.amount
WHERE p.payment_id IS NULL;  -- 중복되지 않는 데이터만 삽입

-- 결과 확인
SELECT 
    COUNT(*) as total_payments,
    COUNT(DISTINCT customer_id) as customers_with_payments,
    SUM(amount) as total_revenue,
    MIN(payment_date) as earliest_payment,
    MAX(payment_date) as latest_payment
FROM payments;