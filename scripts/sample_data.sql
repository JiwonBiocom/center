-- 테스트용 고객 데이터 추가
-- Supabase SQL Editor에서 실행하세요

-- 1. 서비스 타입 데이터 (이미 있을 수 있음)
INSERT INTO service_types (name, description, price, duration_minutes, category, is_active) 
VALUES 
  ('InBody 측정', 'InBody 체성분 분석', 10000, 30, 'measurement', true),
  ('개인 운동', '1:1 개인 트레이닝', 50000, 60, 'training', true),
  ('그룹 운동', '소그룹 운동 클래스', 30000, 60, 'training', true),
  ('영양 상담', '영양사 상담', 20000, 30, 'consultation', true)
ON CONFLICT (name) DO NOTHING;

-- 2. 테스트 고객 데이터
INSERT INTO customers (
  name, phone, email, birth_date, gender, address, 
  emergency_contact, emergency_phone, status, membership_level,
  notes, created_at, updated_at
) VALUES 
  ('김철수', '010-1234-5678', 'kim@example.com', '1985-03-15', 'male', 
   '서울시 강남구 역삼동', '김영희(배우자)', '010-1234-5679', 'active', 'bronze',
   '무릎 부상 병력 있음', NOW(), NOW()),
   
  ('박미영', '010-2345-6789', 'park@example.com', '1990-07-22', 'female',
   '서울시 서초구 반포동', '박아버지', '010-2345-6788', 'active', 'silver',
   '다이어트 목표', NOW(), NOW()),
   
  ('이준호', '010-3456-7890', 'lee@example.com', '1988-11-08', 'male',
   '서울시 송파구 잠실동', '이어머니', '010-3456-7891', 'active', 'gold',
   '근력 증진 목표', NOW(), NOW()),
   
  ('최유진', '010-4567-8901', 'choi@example.com', '1992-04-30', 'female',
   '경기도 성남시 분당구', '최언니', '010-4567-8902', 'active', 'bronze',
   '체형 교정 희망', NOW(), NOW()),
   
  ('정민수', '010-5678-9012', 'jung@example.com', '1987-09-14', 'male',
   '서울시 마포구 홍대', '정형', '010-5678-9013', 'inactive', 'silver',
   '장기 해외 출장으로 휴회', NOW(), NOW())
ON CONFLICT (phone) DO NOTHING;

-- 확인 쿼리
SELECT name, phone, status, membership_level, created_at 
FROM customers 
ORDER BY created_at DESC;
EOF < /dev/null