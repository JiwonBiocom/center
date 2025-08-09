-- Customer 테이블의 NULL 값 처리를 위한 마이그레이션
-- 실행일: 2025-06-21

-- 1. 기본값 설정
ALTER TABLE customers
  ALTER COLUMN total_visits SET DEFAULT 0,
  ALTER COLUMN total_revenue SET DEFAULT 0,
  ALTER COLUMN updated_at SET DEFAULT now();

-- 2. 기존 NULL 값 업데이트
UPDATE customers
  SET total_visits = 0
  WHERE total_visits IS NULL;

UPDATE customers
  SET total_revenue = 0
  WHERE total_revenue IS NULL;

UPDATE customers
  SET updated_at = created_at
  WHERE updated_at IS NULL;

-- 3. 통계 확인
SELECT 
  COUNT(*) as total_customers,
  COUNT(total_visits) as with_visits,
  COUNT(total_revenue) as with_revenue,
  COUNT(updated_at) as with_updated_at
FROM customers;