# AIBIO 엑셀 파일 구조 및 데이터베이스 전환 분석 보고서

## 1. 엑셀 파일 구조 분석

### 1.1 고객관리대장2025.xlsm

#### 파일 개요
- **시트 수**: 52개 (전체 고객관리, 월별 이용현황, 키트수령, 유입 퍼널 등)
- **관리 기간**: 2021년 5월 ~ 2025년 5월
- **총 고객 수**: 약 950명

#### 주요 시트 구조

**1) 전체 고객관리대장**
- 고객 기본 정보 관리
- 주요 컬럼:
  - NO (고객번호)
  - 첫방문일
  - 성함
  - 연락처
  - 거주지역 (서울 강서구 집중: 145명)
  - 방문경로 (당근: 225명, 검색: 62명)
  - 호소문제 (건강 관련 주요 증상)
  - 비고 (메모)
  - 담당자

**2) 월별 이용현황 시트 (40개)**
- 일별 서비스 이용 기록
- 서비스 종류: 브레인, 펄스, 림프, 레드
- 관리 항목:
  - 이용일자
  - 고객명
  - 실행 패키지/프로모션
  - 세션 진행 사항 (상세 시술 내용)
  - 서비스별 잔여횟수
  - 서비스별 이용횟수/전체횟수

**3) 키트수령고객**
- 검사 키트 관리
- 키트 종류: 유기산, 음식물과민증
- 시리얼번호 관리
- 결과지 수령/전달일 추적

**4) 유입 퍼널**
- 마케팅 성과 추적
- 광고비 집행, 방문자수, DB 수집, 전환율 관리

### 1.2 유입 고객 DB 리스트.xlsx

#### 파일 개요
- **시트 수**: 5개 (신규, 재등록대상, 재등록, 월별 목표매출)
- **신규 리드**: 176명
- **재등록 고객**: 30명

#### 리드 관리 구조
- **신규 고객 퍼널**:
  - DB입력 → 전화상담 (97.2%) → 방문상담 (67.6%) → 등록 (15.3%)
- **주요 유입경로**:
  - 유튜브: 83명 (47%)
  - 당근: 39명 (22%)
  - 메타: 17명 (10%)
  - 지인소개: 16명 (9%)

### 1.3 ★2025년 AIBIO 결제현황.xlsx

#### 파일 개요
- **시트 수**: 44개 (전체매출 + 월별 결제 현황)
- **관리 기간**: 2022년 1월 ~ 2025년 5월

#### 결제 데이터 구조
- 결제일자
- 고객명
- 결제 프로그램 (패키지 상세)
- 결제 금액
- 결제 방법 (카드/계좌이체)
- 승인번호
- 결제 담당자
- 유입 경로
- 고객 등급 (신규/재구매)
- 구매 차수

## 2. 데이터 특성 분석

### 2.1 데이터 품질 이슈
1. **중복 데이터**: 같은 고객이 여러 시트에 분산 기록
2. **일관성 부족**: 
   - 지역명 표기 불일치 (예: "서울시 강서구" vs "서울 강서구")
   - 날짜 형식 불일치
   - 금액 표기 방식 다양
3. **누락 데이터**:
   - 연락처 누락: 약 1.5%
   - 거주지역 누락: 약 20%
   - 방문경로 누락: 약 18%

### 2.2 비즈니스 인사이트
1. **고객 분포**:
   - 강서구 중심의 지역 집중도 높음
   - 온라인 마케팅 (당근, 유튜브) 효과 높음
2. **서비스 이용 패턴**:
   - 복합 서비스 이용 고객 다수
   - 월 평균 3-5회 방문 고객이 주요 고객층
3. **재구매율**:
   - 재등록 고객 평균 매출: 130만원
   - 신규 대비 재구매 고객 객단가 3배 이상

## 3. 데이터베이스 설계 제안

### 3.1 정규화된 테이블 구조

```sql
-- 1. 고객 마스터 테이블
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    phone VARCHAR(20) UNIQUE,
    first_visit_date DATE,
    region VARCHAR(100),
    referral_source VARCHAR(50),
    health_concerns TEXT,
    notes TEXT,
    assigned_staff VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 서비스 타입 테이블
CREATE TABLE service_types (
    service_type_id SERIAL PRIMARY KEY,
    service_name VARCHAR(20) NOT NULL UNIQUE,
    description TEXT
);

-- 3. 패키지 정보 테이블
CREATE TABLE packages (
    package_id SERIAL PRIMARY KEY,
    package_name VARCHAR(100) NOT NULL,
    total_sessions INT,
    price DECIMAL(10,2),
    valid_days INT
);

-- 4. 서비스 이용 내역 테이블
CREATE TABLE service_usage (
    usage_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    service_date DATE NOT NULL,
    service_type_id INT REFERENCES service_types(service_type_id),
    package_id INT REFERENCES packages(package_id),
    session_details TEXT,
    session_number INT,
    created_by VARCHAR(50)
);

-- 5. 패키지 구매 내역 테이블
CREATE TABLE package_purchases (
    purchase_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    package_id INT REFERENCES packages(package_id),
    purchase_date DATE NOT NULL,
    expiry_date DATE,
    total_sessions INT,
    used_sessions INT DEFAULT 0,
    remaining_sessions INT
);

-- 6. 결제 내역 테이블
CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    payment_date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(20),
    card_holder_name VARCHAR(50),
    approval_number VARCHAR(50),
    payment_staff VARCHAR(50),
    purchase_type VARCHAR(20),
    purchase_order INT
);

-- 7. 마케팅 리드 테이블
CREATE TABLE marketing_leads (
    lead_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    lead_date DATE NOT NULL,
    channel VARCHAR(50),
    db_entry_date DATE,
    phone_consult_date DATE,
    visit_consult_date DATE,
    registration_date DATE,
    status VARCHAR(20),
    converted_customer_id INT REFERENCES customers(customer_id)
);

-- 8. 키트 관리 테이블
CREATE TABLE kit_management (
    kit_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    kit_type VARCHAR(50) NOT NULL,
    serial_number VARCHAR(50) UNIQUE,
    received_date DATE,
    result_received_date DATE,
    result_delivered_date DATE
);
```

### 3.2 데이터 마이그레이션 전략

#### Phase 1: 데이터 정제 (2주)
1. **고객 데이터 통합**
   - 이름/연락처 기준 중복 제거
   - 고유 customer_id 생성
   - 연락처 형식 표준화

2. **날짜 데이터 표준화**
   - 모든 날짜를 YYYY-MM-DD 형식으로 변환
   - 잘못된 날짜 데이터 수정

3. **금액 데이터 정리**
   - 문자 제거 및 숫자 변환
   - 음수 값 (환불) 처리 로직 정의

#### Phase 2: 데이터 이관 (1주)
1. **마스터 데이터 우선 이관**
   - customers 테이블
   - service_types 테이블
   - packages 테이블

2. **트랜잭션 데이터 이관**
   - 월별 시트 데이터 → service_usage
   - 결제 시트 데이터 → payments
   - 리드 데이터 → marketing_leads

#### Phase 3: 검증 및 보완 (1주)
1. **데이터 무결성 검증**
   - 외래키 관계 확인
   - 잔여 세션 수 재계산
   - 금액 합계 검증

2. **보고서 생성 테스트**
   - 기존 엑셀 보고서와 비교
   - 누락 데이터 확인

### 3.3 추가 기능 제안

1. **자동화 기능**
   - 잔여 세션 자동 차감
   - 패키지 만료 알림
   - 재구매 시점 예측

2. **분석 대시보드**
   - 실시간 매출 현황
   - 서비스별 이용률
   - 고객 LTV (Life Time Value) 분석
   - 마케팅 채널 ROI 분석

3. **CRM 기능**
   - 고객 상담 이력 관리
   - 자동 문자 발송
   - 예약 관리 시스템 연동

## 4. 구현 로드맵

### 단기 (1-2개월)
1. 데이터베이스 스키마 구축
2. 데이터 마이그레이션
3. 기본 CRUD 기능 구현
4. 기존 업무 프로세스 유지를 위한 엑셀 내보내기 기능

### 중기 (3-4개월)
1. 웹 기반 관리 시스템 구축
2. 실시간 대시보드 개발
3. 모바일 대응
4. 직원 교육

### 장기 (5-6개월)
1. 고급 분석 기능 추가
2. AI 기반 고객 행동 예측
3. 마케팅 자동화 연동
4. 타 시스템 연동 (POS, 예약 시스템 등)

## 5. 예상 효과

1. **업무 효율성 향상**
   - 데이터 입력 시간 50% 감소
   - 보고서 생성 자동화로 업무 시간 단축
   - 실시간 데이터 조회 가능

2. **데이터 정확성 향상**
   - 중복 입력 방지
   - 자동 계산으로 오류 감소
   - 데이터 일관성 보장

3. **비즈니스 인사이트**
   - 실시간 경영 지표 확인
   - 고객 행동 패턴 분석
   - 마케팅 효율성 개선

4. **고객 만족도 향상**
   - 빠른 정보 조회
   - 체계적인 이력 관리
   - 맞춤형 서비스 제공 가능