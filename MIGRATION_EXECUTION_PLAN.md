# 🚀 로컬 데이터 마이그레이션 실행 계획 v2

## 📊 Phase 1 분석 결과

### 데이터 현황
- **총 테이블**: 20개
- **총 레코드**: 1,590개
- **주요 데이터**:
  - customers: 979개 (918개보다 많음!)
  - payments: 412개 (payment_staff는 모두 "직원")
  - packages: 12개 (패키지 마스터 데이터)
  - marketing_leads: 176개 (유입 고객)
  - kit_types: 5개
  - service_types: 5개

### 놀라운 발견
1. **service_usage 테이블이 비어있음** - 서비스 이용 내역이 없음
2. **package_purchases 테이블이 비어있음** - 패키지 구매 내역이 없음
3. **payments에 payment_staff가 있음** - 모두 "직원"으로 기록

## 🎯 수정된 마이그레이션 전략

### 즉시 실행 가능한 작업 (Phase 2-A)

#### 1. Payments 테이블 업데이트 (5분)
```sql
-- payment_staff 필드 업데이트
UPDATE payments 
SET payment_staff = '직원'
WHERE payment_staff IS NULL;
```

#### 2. 마스터 데이터 마이그레이션 (10분)
순서대로:
1. **service_types** (5개) - 서비스 종류
2. **kit_types** (5개) - 키트 종류  
3. **packages** (12개) - 패키지 정보

#### 3. 고객 데이터 동기화 (15분)
- 로컬 979개 vs 온라인 918개 차이 분석
- 누락된 61명 추가

#### 4. 유입 고객 마이그레이션 (10분)
- **marketing_leads** (176개)

### 데이터 연결 작업 (Phase 2-B)

#### 문제: 구매 내역 복원
- package_purchases가 비어있지만 payments에는 결제가 있음
- 어떻게 연결할 것인가?

#### 해결 방안:
1. payments 테이블의 amount와 packages의 price 매칭
2. payment_date 기준으로 package_purchases 생성
3. 수동 검증 필요

## 🛠️ 실행 스크립트 구조

### 1. 마스터 데이터 스크립트
```python
# migrate_master_data.py
- service_types 마이그레이션
- kit_types 마이그레이션  
- packages 마이그레이션
```

### 2. 고객 데이터 동기화
```python
# sync_customers.py
- 로컬/온라인 차이 분석
- 누락 고객 추가
- 중복 제거
```

### 3. Payments 보완
```python
# update_payments.py
- payment_staff 업데이트
- 누락 필드 채우기
```

### 4. 유입 고객 마이그레이션
```python
# migrate_leads.py
- marketing_leads 전체 이전
```

## 📋 우선순위 재정렬

### 🔴 긴급 (30분 내)
1. ✅ Payments payment_staff 업데이트
2. ✅ Packages 마스터 데이터 마이그레이션
3. ✅ Service_types 마이그레이션
4. ✅ 누락된 고객 61명 추가

### 🟡 중요 (1시간 내)
1. Marketing_leads 마이그레이션
2. Kit_types 마이그레이션
3. Package_purchases 복원 (payments 기반)

### 🟢 추가 작업 (선택적)
1. 빈 테이블들의 용도 파악
2. 시스템 설정 마이그레이션
3. 감사 로그 설정

## 💡 특별 고려사항

### 1. Package Purchases 복원 전략
```python
# payments의 amount로 package 추측
1. 1,500,000원 → 12회 멤버십
2. 750,000원 → 6회 멤버십
3. 패턴 분석 후 자동 매칭
```

### 2. 서비스 이용 내역 부재
- service_usage가 비어있음
- 별도 Excel이나 다른 시스템에서 관리했을 가능성
- 수동 입력 필요할 수 있음

### 3. 데이터 검증 포인트
- 고객 수 불일치 (979 vs 918)
- 결제 합계 금액 일치 여부
- 패키지별 판매 수량

## 🚀 즉시 실행 가능한 첫 번째 작업

**Packages 마스터 데이터 마이그레이션부터 시작하시겠습니까?**

이것만 해도:
- 패키지 관리 페이지가 정상 작동
- 결제와 패키지 연결 가능
- 패키지 구매 내역 복원 준비 완료

준비되셨으면 바로 시작하겠습니다! 🎯