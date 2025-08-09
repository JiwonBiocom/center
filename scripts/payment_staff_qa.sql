-- 결제 담당자 복구 QA 쿼리 모음
-- 실행 전후 비교를 위한 검증 쿼리들

-- 1. 현재 담당자 분포 확인
SELECT '현재 담당자 분포' as query_name;
SELECT
    payment_staff,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
FROM payments
GROUP BY payment_staff
ORDER BY count DESC;

-- 2. 매칭 가능한 레코드 수 확인
SELECT '매칭 가능 레코드' as query_name;
WITH payment_with_names AS (
    SELECT
        p.payment_id,
        c.name as customer_name,
        p.payment_date,
        p.amount,
        p.payment_staff
    FROM payments p
    JOIN customers c ON p.customer_id = c.customer_id
)
SELECT COUNT(*) as matchable_records
FROM payment_with_names p
WHERE EXISTS (
    SELECT 1
    FROM staging_payment_staff s
    WHERE p.customer_name = s.customer_name
      AND p.payment_date = s.payment_date
      AND p.amount = s.amount
);

-- 3. 중복 키 상세 확인
SELECT '중복 키 상세' as query_name;
WITH duplicates AS (
    SELECT
        customer_name,
        payment_date,
        amount,
        COUNT(*) as duplicate_count,
        STRING_AGG(DISTINCT payment_staff, ', ') as staff_variations
    FROM staging_payment_staff
    GROUP BY customer_name, payment_date, amount
    HAVING COUNT(*) > 1
)
SELECT * FROM duplicates
ORDER BY duplicate_count DESC, payment_date DESC
LIMIT 20;

-- 4. 김준호 사례 검증
SELECT '김준호 검증' as query_name;
SELECT
    p.payment_id,
    c.name,
    p.payment_date,
    p.amount,
    p.payment_staff as current_staff,
    s.payment_staff as expected_staff,
    CASE
        WHEN p.payment_staff = s.payment_staff THEN '일치'
        ELSE '불일치'
    END as status
FROM payments p
JOIN customers c ON p.customer_id = c.customer_id
LEFT JOIN staging_payment_staff s ON
    c.name = s.customer_name
    AND p.payment_date = s.payment_date
    AND p.amount = s.amount
WHERE c.name = '김준호'
ORDER BY p.payment_date;

-- 5. 월별 담당자 변화 추이
SELECT '월별 담당자 추이' as query_name;
SELECT
    DATE_TRUNC('month', payment_date) as month,
    payment_staff,
    COUNT(*) as count
FROM payments
WHERE payment_date >= '2025-01-01'
GROUP BY DATE_TRUNC('month', payment_date), payment_staff
ORDER BY month, count DESC;

-- 6. 미매칭 레코드 분석
SELECT '미매칭 레코드' as query_name;
SELECT
    s.customer_name,
    s.payment_date,
    s.amount,
    s.payment_staff,
    CASE
        WHEN NOT EXISTS (SELECT 1 FROM customers c WHERE c.name = s.customer_name)
            THEN '고객 미존재'
        WHEN NOT EXISTS (
            SELECT 1 FROM payments p
            JOIN customers c ON p.customer_id = c.customer_id
            WHERE c.name = s.customer_name
              AND p.payment_date = s.payment_date
        ) THEN '날짜 불일치'
        ELSE '금액 불일치'
    END as mismatch_reason
FROM staging_payment_staff s
WHERE NOT EXISTS (
    SELECT 1
    FROM payments p
    JOIN customers c ON p.customer_id = c.customer_id
    WHERE c.name = s.customer_name
      AND p.payment_date = s.payment_date
      AND p.amount = s.amount
)
LIMIT 20;

-- 7. 데이터 무결성 체크섬
SELECT '데이터 체크섬' as query_name;
SELECT
    'Excel' as source,
    COUNT(*) as total_records,
    SUM(amount) as total_amount,
    COUNT(DISTINCT customer_name) as unique_customers,
    COUNT(DISTINCT payment_staff) as unique_staff
FROM staging_payment_staff
UNION ALL
SELECT
    'DB' as source,
    COUNT(*) as total_records,
    SUM(amount) as total_amount,
    COUNT(DISTINCT customer_id) as unique_customers,
    COUNT(DISTINCT payment_staff) as unique_staff
FROM payments;

-- 8. 업데이트 시뮬레이션
SELECT '업데이트 시뮬레이션' as query_name;
WITH update_preview AS (
    SELECT
        p.payment_id,
        c.name as customer_name,
        p.payment_date,
        p.amount,
        p.payment_staff as current_staff,
        s.payment_staff as new_staff
    FROM payments p
    JOIN customers c ON p.customer_id = c.customer_id
    JOIN staging_payment_staff s ON
        c.name = s.customer_name
        AND p.payment_date = s.payment_date
        AND p.amount = s.amount
    WHERE p.payment_staff != s.payment_staff
)
SELECT
    current_staff,
    new_staff,
    COUNT(*) as change_count
FROM update_preview
GROUP BY current_staff, new_staff
ORDER BY change_count DESC;
