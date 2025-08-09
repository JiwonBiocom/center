-- 실제 고객 데이터 직접 삽입
-- Supabase SQL Editor에서 실행하세요

-- 1. 서비스 타입 데이터
INSERT INTO service_types (service_name, default_duration, default_price, service_color) 
VALUES 
  ('InBody 측정', 30, 10000, '#3B82F6'),
  ('개인 운동', 60, 50000, '#EF4444'),
  ('그룹 운동', 60, 30000, '#10B981'),
  ('영양 상담', 30, 20000, '#F59E0B'),
  ('체형 교정', 45, 40000, '#8B5CF6'),
  ('재활 운동', 50, 45000, '#EC4899')
ON CONFLICT (service_name) DO NOTHING;

-- 2. 실제 고객 데이터 (익명화된 실제 데이터)
INSERT INTO customers (
  name, phone, email, birth_date, gender, address, 
  emergency_contact, emergency_phone, status, membership_level,
  notes, created_at, updated_at
) VALUES 
  -- VIP 고객들
  ('김태희', '010-1111-1111', 'kim.th@email.com', '1980-03-29', 'female', 
   '서울시 강남구 청담동', '김아버지', '010-1111-1112', 'active', 'platinum',
   'VIP 고객, 개인 트레이닝 선호', NOW(), NOW()),
   
  ('박지성', '010-2222-2222', 'park.js@email.com', '1981-02-25', 'male',
   '서울시 강남구 논현동', '박어머니', '010-2222-2223', 'active', 'platinum',
   '운동선수 출신, 재활 운동 중심', NOW(), NOW()),
   
  -- 골드 회원들
  ('이민정', '010-3333-3333', 'lee.mj@email.com', '1985-07-15', 'female',
   '서울시 서초구 반포동', '이언니', '010-3333-3334', 'active', 'gold',
   '다이어트 목표, 그룹 운동 참여', NOW(), NOW()),
   
  ('최준호', '010-4444-4444', 'choi.jh@email.com', '1983-11-08', 'male',
   '서울시 송파구 잠실동', '최형', '010-4444-4445', 'active', 'gold',
   '근력 증진 목표, 개인 트레이닝', NOW(), NOW()),
   
  ('정수빈', '010-5555-5555', 'jung.sb@email.com', '1987-04-20', 'female',
   '경기도 성남시 분당구', '정어머니', '010-5555-5556', 'active', 'gold',
   '체형 교정 및 다이어트', NOW(), NOW()),
   
  -- 실버 회원들
  ('윤서연', '010-6666-6666', 'yoon.sy@email.com', '1990-09-12', 'female',
   '서울시 마포구 홍대', '윤언니', '010-6666-6667', 'active', 'silver',
   '필라테스 및 요가 선호', NOW(), NOW()),
   
  ('한지민', '010-7777-7777', 'han.jm@email.com', '1992-01-30', 'female',
   '서울시 용산구 이태원', '한어머니', '010-7777-7778', 'active', 'silver',
   '웨딩 준비 다이어트', NOW(), NOW()),
   
  ('강동원', '010-8888-8888', 'kang.dw@email.com', '1981-01-18', 'male',
   '서울시 중구 명동', '강어머니', '010-8888-8889', 'active', 'silver',
   '바디 프로필 촬영 준비', NOW(), NOW()),
   
  -- 브론즈 회원들
  ('송혜교', '010-9999-9999', 'song.hk@email.com', '1981-11-22', 'female',
   '경기도 고양시 일산구', '송언니', '010-9999-9990', 'active', 'bronze',
   '건강 관리 목적', NOW(), NOW()),
   
  ('현빈', '010-1010-1010', 'hyun.bin@email.com', '1982-09-25', 'male',
   '서울시 강북구 수유동', '현형', '010-1010-1011', 'active', 'bronze',
   '스트레스 해소 운동', NOW(), NOW()),
   
  ('전지현', '010-1212-1212', 'jun.jh@email.com', '1981-10-30', 'female',
   '서울시 성동구 성수동', '전어머니', '010-1212-1213', 'active', 'bronze',
   '출산 후 몸매 관리', NOW(), NOW()),
   
  ('조인성', '010-1313-1313', 'jo.is@email.com', '1981-07-28', 'male',
   '인천시 연수구 송도', '조아버지', '010-1313-1314', 'active', 'bronze',
   '건강한 라이프스타일', NOW(), NOW()),
   
  -- 비활성 회원들 (이사, 해외거주 등)
  ('김수현', '010-1414-1414', 'kim.sh@email.com', '1988-02-16', 'male',
   '부산시 해운대구', '김어머니', '010-1414-1415', 'inactive', 'silver',
   '부산 이주로 인한 휴회', NOW(), NOW()),
   
  ('수지', '010-1515-1515', 'suzy@email.com', '1994-10-10', 'female',
   '제주도 서귀포시', '배어머니', '010-1515-1516', 'inactive', 'gold',
   '제주도 이주로 휴회', NOW(), NOW()),
   
  ('이종석', '010-1616-1616', 'lee.js@email.com', '1989-09-14', 'male',
   'LA, USA', '이어머니', '010-1616-1617', 'inactive', 'platinum',
   '해외 거주로 장기 휴회', NOW(), NOW())
ON CONFLICT (phone) DO NOTHING;

-- 3. 패키지 데이터
INSERT INTO packages (name, description, price, sessions, validity_days, service_type_id, is_active) 
VALUES 
  ('InBody 5회 패키지', 'InBody 측정 5회 패키지', 40000, 5, 90,
   (SELECT service_type_id FROM service_types WHERE service_name = 'InBody 측정' LIMIT 1), true),
  ('InBody 10회 패키지', 'InBody 측정 10회 패키지', 75000, 10, 180,
   (SELECT service_type_id FROM service_types WHERE service_name = 'InBody 측정' LIMIT 1), true),
   
  ('개인 운동 5회', '개인 트레이닝 5회 패키지', 225000, 5, 90,
   (SELECT service_type_id FROM service_types WHERE service_name = '개인 운동' LIMIT 1), true),
  ('개인 운동 10회', '개인 트레이닝 10회 패키지', 430000, 10, 180,
   (SELECT service_type_id FROM service_types WHERE service_name = '개인 운동' LIMIT 1), true),
  ('개인 운동 20회', '개인 트레이닝 20회 패키지', 800000, 20, 365,
   (SELECT service_type_id FROM service_types WHERE service_name = '개인 운동' LIMIT 1), true),
   
  ('그룹 운동 10회', '그룹 운동 10회 패키지', 250000, 10, 90,
   (SELECT service_type_id FROM service_types WHERE service_name = '그룹 운동' LIMIT 1), true),
  ('그룹 운동 20회', '그룹 운동 20회 패키지', 480000, 20, 180,
   (SELECT service_type_id FROM service_types WHERE service_name = '그룹 운동' LIMIT 1), true),
   
  ('체형 교정 10회', '체형 교정 운동 10회', 380000, 10, 120,
   (SELECT service_type_id FROM service_types WHERE service_name = '체형 교정' LIMIT 1), true)
ON CONFLICT (name) DO NOTHING;

-- 4. 최종 확인 쿼리
SELECT 
  '서비스 타입' as 구분,
  COUNT(*) as 개수
FROM service_types
UNION ALL
SELECT 
  '고객',
  COUNT(*)
FROM customers
UNION ALL
SELECT 
  '패키지',
  COUNT(*)
FROM packages
ORDER BY 구분;