-- AIBIO 센터 관리자 계정 생성
-- Supabase SQL Editor에서 실행

-- 1. 기존 admin 계정 확인
SELECT user_id, email, name, role, is_active 
FROM users 
WHERE email IN ('admin@aibio.com', 'admin@aibio.kr');

-- 2. admin@aibio.com 계정 생성 (없는 경우)
INSERT INTO users (email, password_hash, name, role, is_active, created_at, updated_at) 
VALUES (
    'admin@aibio.com',
    '$2b$12$9IJvP1fdzag90RF2cf1w0.Z59BtvvxlKy1KbPZywIFk7Z3NmdUh4a',
    '관리자',
    'admin',
    true,
    NOW(),
    NOW()
)
ON CONFLICT (email) DO UPDATE 
SET 
    password_hash = EXCLUDED.password_hash,
    is_active = true,
    updated_at = NOW();

-- 3. 생성 확인
SELECT user_id, email, name, role, is_active,
       created_at, updated_at
FROM users 
WHERE email = 'admin@aibio.com';