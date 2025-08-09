-- Railway 프로덕션 데이터베이스 사용자 비밀번호 초기화
-- Supabase SQL Editor에서 실행

-- 1. 현재 사용자 확인
SELECT user_id, email, name, role, is_active
FROM users
ORDER BY user_id;

-- 2. admin@aibio.kr 비밀번호 초기화 (admin123)
UPDATE users
SET password_hash = '$2b$12$81f.4a5BI4cIQiXIWekca.FzKXUvyFlbIylN2mjIe/7d/fvtYeDNa'
WHERE email = 'admin@aibio.kr';

-- 3. taejun@biocom.kr 비밀번호 초기화 (admin1234) 및 권한 확인
UPDATE users
SET password_hash = '$2b$12$SVp3ZWDNvs0V98keTtbgveZtdAmakDZWD35Cu6dDNefPEzmKGx78e',
    role = 'master',
    is_active = true
WHERE email = 'taejun@biocom.kr';

-- 4. manager@aibio.kr 비밀번호 초기화 (manager123)
UPDATE users
SET password_hash = '$2b$12$xRhpnyA2jAISRnQFeciee.rr8PHtj74HKD2NyhKPODkoCNtHwQEQe',
    is_active = true
WHERE email = 'manager@aibio.kr';

-- 5. admin 계정이 없으면 생성
INSERT INTO users (email, name, password_hash, role, is_active)
SELECT 'admin@aibio.kr', '관리자', '$2b$12$81f.4a5BI4cIQiXIWekca.FzKXUvyFlbIylN2mjIe/7d/fvtYeDNa', 'admin', true
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'admin@aibio.kr');

-- 6. taejun 계정이 없으면 생성
INSERT INTO users (email, name, password_hash, role, is_active)
SELECT 'taejun@biocom.kr', 'TaeJun', '$2b$12$SVp3ZWDNvs0V98keTtbgveZtdAmakDZWD35Cu6dDNefPEzmKGx78e', 'master', true
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'taejun@biocom.kr');

-- 7. 결과 확인
SELECT user_id, email, name, role, is_active, created_at
FROM users
WHERE email IN ('admin@aibio.kr', 'taejun@biocom.kr', 'manager@aibio.kr')
ORDER BY user_id;

-- 비밀번호 해시 정보:
-- admin@aibio.kr: admin123 → $2b$12$81f.4a5BI4cIQiXIWekca.FzKXUvyFlbIylN2mjIe/7d/fvtYeDNa
-- taejun@biocom.kr: admin1234 → $2b$12$SVp3ZWDNvs0V98keTtbgveZtdAmakDZWD35Cu6dDNefPEzmKGx78e
-- manager@aibio.kr: manager123 → $2b$12$xRhpnyA2jAISRnQFeciee.rr8PHtj74HKD2NyhKPODkoCNtHwQEQe
