-- Railway 배포 환경 완전 수정 SQL
-- Generated at: 2025-06-21
-- Based on Railway deployment errors

-- ============================================
-- 1. notifications 테이블 user_id 컬럼 추가
-- ============================================
-- 에러: Column notifications.user_id does not exist
ALTER TABLE notifications ADD COLUMN IF NOT EXISTS user_id INTEGER;

-- 기본값 설정 (NULL인 경우 1로 설정)
UPDATE notifications SET user_id = 1 WHERE user_id IS NULL;

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);

-- ============================================
-- 2. packages 테이블 price -> base_price 변경
-- ============================================
-- 에러: Column packages.price does not exist
-- 주의: 이미 변경되었을 수 있으므로 IF EXISTS 사용

-- price 컬럼이 존재하고 base_price가 없는 경우에만 실행
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'packages' AND column_name = 'price')
       AND NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name = 'packages' AND column_name = 'base_price') THEN
        ALTER TABLE packages RENAME COLUMN price TO base_price;
    END IF;
END $$;

-- base_price가 없는 경우 추가
ALTER TABLE packages ADD COLUMN IF NOT EXISTS base_price INTEGER;

-- ============================================
-- 3. valid_days -> valid_months 변경
-- ============================================
-- packages 테이블의 valid_days를 valid_months로 변경
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'packages' AND column_name = 'valid_days')
       AND NOT EXISTS (SELECT 1 FROM information_schema.columns 
                       WHERE table_name = 'packages' AND column_name = 'valid_months') THEN
        ALTER TABLE packages RENAME COLUMN valid_days TO valid_months;
    END IF;
END $$;

-- valid_months가 없는 경우 추가
ALTER TABLE packages ADD COLUMN IF NOT EXISTS valid_months INTEGER;

-- ============================================
-- 4. customer_payments 테이블 처리
-- ============================================
-- Railway 로그에 customer_payments 관련 에러가 있는 경우
-- 이 테이블이 레거시인지 확인 필요

-- customer_payments가 존재하는지 확인
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables 
               WHERE table_name = 'customer_payments') THEN
        -- 데이터가 있는지 확인
        RAISE NOTICE 'customer_payments table exists. Check if it contains data.';
    END IF;
END $$;

-- ============================================
-- 5. Foreign Key 제약 조건 확인 및 수정
-- ============================================
-- notifications.user_id -> users.user_id FK 추가
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'notifications_user_id_fkey' 
        AND table_name = 'notifications'
    ) THEN
        ALTER TABLE notifications 
        ADD CONSTRAINT notifications_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES users(user_id);
    END IF;
END $$;

-- ============================================
-- 6. 필수 인덱스 생성
-- ============================================
CREATE INDEX IF NOT EXISTS idx_packages_is_active ON packages(is_active);
CREATE INDEX IF NOT EXISTS idx_packages_base_price ON packages(base_price);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);

-- ============================================
-- 7. 데이터 정합성 검증 쿼리
-- ============================================
-- 검증 1: notifications의 모든 레코드가 user_id를 가지고 있는지
SELECT 
    'notifications without user_id' as check_name,
    COUNT(*) as count 
FROM notifications 
WHERE user_id IS NULL;

-- 검증 2: packages의 base_price가 설정되어 있는지
SELECT 
    'packages without base_price' as check_name,
    COUNT(*) as count 
FROM packages 
WHERE base_price IS NULL;

-- 검증 3: packages의 valid_months가 설정되어 있는지
SELECT 
    'packages without valid_months' as check_name,
    COUNT(*) as count 
FROM packages 
WHERE valid_months IS NULL;

-- ============================================
-- 8. 최종 스키마 확인
-- ============================================
-- notifications 테이블 구조 확인
SELECT 
    column_name, 
    data_type, 
    is_nullable 
FROM information_schema.columns 
WHERE table_name = 'notifications' 
ORDER BY ordinal_position;

-- packages 테이블 구조 확인
SELECT 
    column_name, 
    data_type, 
    is_nullable 
FROM information_schema.columns 
WHERE table_name = 'packages' 
ORDER BY ordinal_position;

-- ============================================
-- 9. 애플리케이션 재시작 필요
-- ============================================
-- 이 SQL 실행 후 Railway 애플리케이션을 재시작해야 합니다.
-- Railway Dashboard에서 서비스를 재시작하거나
-- 새로운 커밋을 푸시하여 자동 재배포를 트리거하세요.