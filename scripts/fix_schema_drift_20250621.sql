-- 🔧 스키마 드리프트 수정 SQL
-- 생성일: 2025-06-21
-- 목적: GitHub Actions에서 감지한 스키마 차이점 수정

-- ============================================================
-- notifications 테이블 수정
-- ============================================================

-- 1. user_id 컬럼 추가 (nullable로 먼저 추가)
ALTER TABLE notifications 
ADD COLUMN IF NOT EXISTS user_id INTEGER;

-- 2. 기본값 설정 (기존 데이터가 있다면)
-- admin 계정(user_id=1)으로 설정
UPDATE notifications 
SET user_id = 1 
WHERE user_id IS NULL;

-- 3. NOT NULL 제약 조건 추가
ALTER TABLE notifications 
ALTER COLUMN user_id SET NOT NULL;

-- 4. 외래 키 제약 조건 추가
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'fk_notifications_user'
    ) THEN
        ALTER TABLE notifications 
        ADD CONSTRAINT fk_notifications_user 
        FOREIGN KEY (user_id) REFERENCES users(user_id);
    END IF;
END $$;

-- 5. 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_notifications_user_id 
ON notifications(user_id);

-- 6. 코멘트 추가
COMMENT ON COLUMN notifications.user_id IS '알림을 생성한 사용자 ID';

-- ============================================================
-- 스키마 검증
-- ============================================================

-- notifications 테이블 구조 확인
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'notifications'
AND table_schema = 'public'
ORDER BY ordinal_position;