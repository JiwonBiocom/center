# 고객관리 시스템 데이터베이스 마이그레이션 계획서

## 📋 문서 정보
- **작성일**: 2025-06-06
- **버전**: 1.0
- **관련 문서**: [PRD](./prd-customer-enhanced.md), [API 설계](./customer-enhanced-api-design.md)

---

## 🎯 마이그레이션 목표

### 주요 목표
1. 기존 엑셀 데이터를 PostgreSQL로 안전하게 이전
2. 고객 테이블 확장으로 새로운 기능 지원
3. 데이터 무결성 보장 및 중복 제거
4. 롤백 가능한 마이그레이션 전략 수립

### 마이그레이션 범위
- **고객 기본 정보**: 950명 (고객관리대장_전체고객.csv)
- **키트 수령 정보**: 16명 (고객관리대장_키트고객.csv)
- **유입 고객 정보**: 176명 (유입고객_DB리스트.csv)
- **결제 현황**: 2025년 데이터 (2025년_결제현황.csv)

---

## 📊 현재 상태 분석

### 기존 데이터 구조
```
docs/AIBIO 관리대장 파일모음/
├── 고객관리대장_전체고객.csv (950명)
│   └── 컬럼: 번호, 첫방문일, 이름, 연락처, 거주지역, 방문경로, 
│        리뷰제안, 후기제안, 고객파일, 호소문제, 비고, 담당자
├── 고객관리대장_키트고객.csv (16명)
│   └── 컬럼: 고객명, 키트, 시리얼번호, 키트수령일, 결과지 수령일, 결과지 전달일
├── 유입고객_DB리스트.csv (176명)
│   └── 컬럼: 이름, 유입경로, DB작성 채널, 당근아이디, 나이, 거주지역, 
│        시청 광고, 가격안내, A/B 테스트, 연락처, DB입력일, 방문상담일 등
└── 2025년_결제현황.csv
    └── 월별 매출 집계 데이터
```

### 데이터베이스 현재 구조
```sql
-- 기존 customers 테이블
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    first_visit_date DATE,
    region VARCHAR(50),
    referral_source VARCHAR(100),
    health_concerns TEXT,
    notes TEXT,
    assigned_staff VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔄 마이그레이션 전략

### Phase 1: 스키마 확장 (Day 1)

#### 1.1 customers 테이블 확장
```sql
-- 새로운 컬럼 추가
ALTER TABLE customers ADD COLUMN IF NOT EXISTS birth_year INTEGER;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS gender VARCHAR(10);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS email VARCHAR(100);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS address TEXT;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS emergency_contact VARCHAR(100);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS occupation VARCHAR(50);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS membership_level VARCHAR(20) DEFAULT 'basic';
ALTER TABLE customers ADD COLUMN IF NOT EXISTS customer_status VARCHAR(20) DEFAULT 'active';
ALTER TABLE customers ADD COLUMN IF NOT EXISTS preferred_time_slots JSONB;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS health_goals TEXT;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS last_visit_date DATE;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS total_visits INTEGER DEFAULT 0;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS average_visit_interval INTEGER;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS total_revenue DECIMAL(10,2) DEFAULT 0;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS average_satisfaction DECIMAL(3,2);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS risk_level VARCHAR(20) DEFAULT 'stable';

-- 인덱스 추가
CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_customers_membership_level ON customers(membership_level);
CREATE INDEX idx_customers_last_visit ON customers(last_visit_date);
CREATE INDEX idx_customers_risk_level ON customers(risk_level);
```

#### 1.2 새로운 관련 테이블 생성
```sql
-- 고객 선호도 테이블
CREATE TABLE IF NOT EXISTS customer_preferences (
    preference_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    preferred_services TEXT[],
    preferred_time VARCHAR(20),
    preferred_intensity VARCHAR(20),
    health_interests TEXT[],
    communication_preference VARCHAR(20),
    marketing_consent BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 고객 분석 데이터 테이블
CREATE TABLE IF NOT EXISTS customer_analytics (
    analytics_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    analysis_date DATE NOT NULL,
    visit_frequency VARCHAR(20),
    consistency_score INTEGER,
    most_used_service VARCHAR(20),
    ltv_estimate DECIMAL(10,2),
    churn_risk VARCHAR(20),
    churn_probability INTEGER,
    retention_score INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 마케팅 리드 테이블 (유입 고객용)
CREATE TABLE IF NOT EXISTS marketing_leads (
    lead_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    age INTEGER,
    region VARCHAR(50),
    lead_channel VARCHAR(50),
    carrot_id VARCHAR(100),
    ad_watched VARCHAR(100),
    price_informed BOOLEAN,
    ab_test_group VARCHAR(20),
    db_entry_date DATE,
    phone_consult_date DATE,
    visit_consult_date DATE,
    registration_date DATE,
    purchased_product VARCHAR(200),
    no_registration_reason TEXT,
    notes TEXT,
    revenue DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'new',
    converted_customer_id INTEGER REFERENCES customers(customer_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 키트 수령 정보 테이블
CREATE TABLE IF NOT EXISTS kit_receipts (
    kit_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    kit_type VARCHAR(100),
    serial_number VARCHAR(100) UNIQUE,
    receipt_date DATE,
    result_received_date DATE,
    result_delivered_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Phase 2: 데이터 정제 및 검증 (Day 2-3)

#### 2.1 데이터 정제 스크립트
```python
# scripts/clean_customer_data.py
import pandas as pd
import re
from datetime import datetime

def clean_phone_number(phone):
    """전화번호 정규화"""
    if pd.isna(phone):
        return None
    # 숫자만 추출
    numbers = re.sub(r'[^0-9]', '', str(phone))
    # 010-XXXX-XXXX 형식으로 변환
    if len(numbers) == 11 and numbers.startswith('010'):
        return f"{numbers[:3]}-{numbers[3:7]}-{numbers[7:]}"
    return phone

def parse_birth_year(name_or_note):
    """이름이나 메모에서 생년 추출"""
    # 패턴: 85년생, 1985년생 등
    patterns = [
        r'(\d{2})년생',
        r'(\d{4})년생',
        r'(\d{2})년',
    ]
    # 구현 로직...
    return None

def identify_duplicates(df):
    """중복 고객 식별"""
    # 이름 + 전화번호로 중복 체크
    duplicates = df[df.duplicated(['이름', '연락처'], keep=False)]
    return duplicates

def merge_duplicate_customers(duplicates):
    """중복 고객 정보 병합"""
    # 최신 정보 우선, 누락된 정보는 이전 레코드에서 보완
    # 구현 로직...
    pass
```

#### 2.2 데이터 검증 체크리스트
- [ ] 전화번호 형식 통일
- [ ] 중복 고객 제거 및 병합
- [ ] 날짜 형식 검증
- [ ] 필수 필드 누락 확인
- [ ] 참조 무결성 검증

### Phase 3: 단계별 마이그레이션 (Day 4-5)

#### 3.1 마이그레이션 순서
1. **고객 기본 정보 마이그레이션**
   ```python
   # scripts/migrate_customers.py
   def migrate_customers():
       # 1. CSV 읽기
       df = pd.read_csv('docs/AIBIO 관리대장 파일모음/고객관리대장_전체고객.csv')
       
       # 2. 데이터 정제
       df['phone'] = df['연락처'].apply(clean_phone_number)
       df['first_visit_date'] = pd.to_datetime(df['첫방문일'])
       
       # 3. 중복 처리
       df = handle_duplicates(df)
       
       # 4. DB 삽입
       for _, row in df.iterrows():
           insert_customer(row)
   ```

2. **마케팅 리드 마이그레이션**
   ```python
   def migrate_leads():
       df = pd.read_csv('docs/AIBIO 관리대장 파일모음/유입고객_DB리스트.csv')
       # 고객 테이블과 매칭
       # 신규 리드는 marketing_leads 테이블에 저장
   ```

3. **키트 정보 마이그레이션**
   ```python
   def migrate_kits():
       df = pd.read_csv('docs/AIBIO 관리대장 파일모음/고객관리대장_키트고객.csv')
       # 고객명으로 customer_id 매칭
       # kit_receipts 테이블에 저장
   ```

4. **서비스 이용 내역 재구성**
   - 월별 시트 데이터에서 서비스 이용 패턴 추출
   - service_sessions 테이블에 저장

#### 3.2 트랜잭션 관리
```python
def migrate_with_transaction():
    with db.begin() as conn:
        try:
            # 모든 마이그레이션 작업
            migrate_customers()
            migrate_leads()
            migrate_kits()
            migrate_service_history()
            
            # 통계 업데이트
            update_customer_statistics()
            
            # 커밋
            conn.commit()
        except Exception as e:
            # 롤백
            conn.rollback()
            raise e
```

### Phase 4: 데이터 검증 및 보정 (Day 6)

#### 4.1 마이그레이션 검증
```sql
-- 데이터 건수 확인
SELECT 
    'customers' as table_name, 
    COUNT(*) as count 
FROM customers
UNION ALL
SELECT 
    'marketing_leads', 
    COUNT(*) 
FROM marketing_leads
UNION ALL
SELECT 
    'kit_receipts', 
    COUNT(*) 
FROM kit_receipts;

-- 데이터 무결성 확인
SELECT 
    c.customer_id,
    c.name,
    c.phone,
    COUNT(DISTINCT k.kit_id) as kit_count,
    COUNT(DISTINCT s.session_id) as session_count
FROM customers c
LEFT JOIN kit_receipts k ON c.customer_id = k.customer_id
LEFT JOIN service_sessions s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.name, c.phone
HAVING COUNT(DISTINCT k.kit_id) > 0 OR COUNT(DISTINCT s.session_id) > 0;
```

#### 4.2 통계 데이터 생성
```python
def generate_customer_analytics():
    """고객별 분석 데이터 생성"""
    customers = get_all_customers()
    
    for customer in customers:
        # 방문 패턴 분석
        visit_pattern = analyze_visit_pattern(customer.customer_id)
        
        # 서비스 이용 분석
        service_usage = analyze_service_usage(customer.customer_id)
        
        # 매출 기여도 계산
        revenue_stats = calculate_revenue_contribution(customer.customer_id)
        
        # 위험도 평가
        risk_assessment = assess_churn_risk(customer.customer_id)
        
        # customer_analytics 테이블에 저장
        save_analytics(customer.customer_id, {
            'visit_pattern': visit_pattern,
            'service_usage': service_usage,
            'revenue_stats': revenue_stats,
            'risk_assessment': risk_assessment
        })
```

---

## 🛡️ 안전 장치

### 1. 백업 전략
```bash
# 마이그레이션 전 전체 백업
pg_dump -h localhost -U postgres -d aibio_center > backup_$(date +%Y%m%d_%H%M%S).sql

# 테이블별 백업
pg_dump -h localhost -U postgres -d aibio_center -t customers > customers_backup.sql
```

### 2. 롤백 계획
```sql
-- 롤백 스크립트 준비
-- 1. 새 컬럼 제거
ALTER TABLE customers DROP COLUMN IF EXISTS birth_year CASCADE;
-- ... (기타 컬럼들)

-- 2. 새 테이블 제거
DROP TABLE IF EXISTS customer_preferences CASCADE;
DROP TABLE IF EXISTS customer_analytics CASCADE;
DROP TABLE IF EXISTS marketing_leads CASCADE;
DROP TABLE IF EXISTS kit_receipts CASCADE;

-- 3. 백업에서 복원
psql -h localhost -U postgres -d aibio_center < customers_backup.sql
```

### 3. 단계별 검증
- [ ] Phase 1 완료: 스키마 확장 성공
- [ ] Phase 2 완료: 데이터 정제 완료
- [ ] Phase 3 완료: 마이그레이션 성공
- [ ] Phase 4 완료: 검증 통과

---

## 📈 마이그레이션 후 작업

### 1. 성능 최적화
```sql
-- 통계 업데이트
ANALYZE customers;
ANALYZE customer_preferences;
ANALYZE customer_analytics;

-- 인덱스 재구성
REINDEX TABLE customers;
```

### 2. 모니터링 설정
- 쿼리 성능 모니터링
- 데이터 일관성 체크 (일일)
- 백업 자동화 설정

### 3. 문서화
- 마이그레이션 결과 보고서
- 데이터 딕셔너리 업데이트
- 운영 가이드 작성

---

## ⚠️ 주의사항

### 절대 금지 사항
1. **프로덕션에서 직접 실행 금지**
2. **백업 없이 마이그레이션 금지**
3. **근무 시간 중 마이그레이션 금지**

### 권장 사항
1. **스테이징 환경에서 먼저 테스트**
2. **단계별 검증 필수**
3. **롤백 계획 사전 검토**
4. **관련 담당자 사전 공지**

---

## 📊 예상 결과

### 마이그레이션 완료 후
- 고객 테이블: 950+ 레코드
- 마케팅 리드: 176 레코드
- 키트 수령: 16 레코드
- 고객 분석 데이터: 자동 생성

### 개선 효과
- 데이터 조회 속도: 80% 향상
- 분석 가능 항목: 300% 증가
- 데이터 정확도: 95% 이상

---

*이 문서는 고객관리 시스템 데이터베이스 마이그레이션의 상세 계획서입니다. 실행 전 반드시 검토하세요.*