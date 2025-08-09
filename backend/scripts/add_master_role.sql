-- user_role enum에 master 추가
-- Railway 콘솔에서 실행할 SQL

-- 1. 현재 enum 값 확인
SELECT enum_range(NULL::user_role) as current_values;

-- 2. master role 추가
ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'master' AFTER 'admin';

-- 3. 추가 확인
SELECT enum_range(NULL::user_role) as updated_values;

-- 4. TaeJun 마스터 계정 생성 또는 업데이트
-- 기존 사용자가 있는지 확인
SELECT user_id, email, name, role FROM users WHERE email = 'taejun@biocom.kr';

-- 기존 사용자가 있으면 업데이트 (위 쿼리 결과에 따라 아래 중 하나 실행)
-- UPDATE users SET role = 'master' WHERE email = 'taejun@biocom.kr';

-- 또는 새로 생성 (비밀번호는 admin1234의 bcrypt 해시)
-- INSERT INTO users (email, name, password_hash, role, is_active)
-- VALUES ('taejun@biocom.kr', 'TaeJun', '$2b$12$KshQ/HHnBioCjrIQDUOwRuwqEUwc52r1IwebKzHfRXMzMZb7AAIUS', 'master', true);

-- 5. 결과 확인
SELECT user_id, email, name, role, is_active FROM users WHERE role = 'master';
