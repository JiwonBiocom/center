-- 프로덕션 데이터베이스 스키마 수정 SQL
-- 주의: 이 스크립트는 Supabase SQL Editor에서 실행하세요

-- 1. notifications 테이블에 user_id 컬럼 추가
ALTER TABLE notifications 
ADD COLUMN IF NOT EXISTS user_id INTEGER;

-- 2. packages 테이블 컬럼명 변경
-- price를 base_price로 변경
ALTER TABLE packages 
RENAME COLUMN price TO base_price;

-- valid_days를 valid_months로 변경
ALTER TABLE packages 
RENAME COLUMN valid_days TO valid_months;

-- 3. user_id에 임시 값 설정 (관리자 ID로)
UPDATE notifications 
SET user_id = 1 
WHERE user_id IS NULL;

-- 4. 인덱스 추가 (선택사항)
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);

-- 5. 스키마 확인
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM 
    information_schema.columns
WHERE 
    table_name IN ('notifications', 'packages')
    AND column_name IN ('user_id', 'base_price', 'valid_months')
ORDER BY 
    table_name, 
    ordinal_position;