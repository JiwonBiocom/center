# 리드 관리 시스템 분석 및 마이그레이션 계획

## 1. 현재 상태 분석

### 1.1 데이터베이스 구조
- **모델**: `models/customer_extended.py`의 `MarketingLead` 클래스
- **테이블명**: `marketing_leads`
- **주요 필드**:
  - 기본 정보: name, phone, age, region
  - 유입 정보: lead_channel, carrot_id, ad_watched, price_informed
  - 상담 진행: db_entry_date, phone_consult_date, visit_consult_date, registration_date
  - 결과: purchased_product, revenue, status, converted_customer_id

### 1.2 현재 데이터 현황
- **전체 리드 수**: 176개
- **상태별 분포**:
  - db_entered: 62개 (35.2%)
  - visit_consulted: 60개 (34.1%)
  - phone_consulted: 27개 (15.3%)
  - converted: 27개 (15.3%)
- **채널별 분포**:
  - 유튜브: 83개 (47.2%)
  - 당근: 41개 (23.3%)
  - 메타: 17개 (9.7%)
  - 지인소개: 17개 (9.7%)
  - 검색: 10개 (5.7%)
- **전환율**: 14.2% (25개)
- **샘플 데이터**: 1개 발견

### 1.3 API 현황
- **엔드포인트**: `/api/v1/leads`
- **주요 기능**:
  - CRUD 작업 (생성, 조회, 수정, 삭제)
  - 퍼널 통계 (`/stats/funnel`)
  - 채널별 통계 (`/stats/by-channel`)
  - 고객 전환 (`/{lead_id}/convert`)
  - 엑셀 가져오기/내보내기

## 2. CSV 파일 분석

### 2.1 파일 정보
- **파일 경로**: `/docs/AIBIO 관리대장 파일모음/유입고객_DB리스트.csv`
- **전체 행 수**: 176개
- **전체 컬럼 수**: 21개

### 2.2 주요 데이터 현황
- **매출 데이터**: 28명, 총 69,746,700원
- **등록 완료**: 27명
- **방문 상담**: 119명
- **전화 상담**: 171명

### 2.3 컬럼 매핑
| CSV 컬럼 | DB 필드 | 비고 |
|---------|---------|------|
| 이름 | name | 필수 |
| 연락처 | phone | 정규화 필요 |
| 나이 | age | |
| 거주지역 | region | |
| 유입경로 | lead_channel | |
| 당근아이디 | carrot_id | |
| 시청 광고 | ad_watched | |
| 가격안내 | price_informed | 불린 변환 |
| A/B 테스트 | ab_test_group | |
| DB입력일 | db_entry_date | 날짜 파싱 |
| 전화상담일 | phone_consult_date | 날짜 파싱 |
| 방문상담일 | visit_consult_date | 날짜 파싱 |
| 등록일 | registration_date | 날짜 파싱 |
| 구매상품 | purchased_product | |
| 미등록사유 | no_registration_reason | |
| 비고 | notes | |
| 매출 | revenue | 숫자 변환 |

### 2.4 추가 처리 필요 항목
- **DB작성 채널**: notes 필드에 추가
- **lead_date**: DB입력일을 기본값으로 설정
- **status**: 날짜 데이터 기반 자동 결정

## 3. 마이그레이션 계획

### 3.1 작업 순서
1. **백업**: 현재 리드 데이터 엑셀 백업
2. **샘플 데이터 삭제**: 테스트/샘플 패턴 삭제
3. **전체 삭제**: 기존 리드 데이터 전체 삭제
4. **데이터 정제**:
   - 전화번호 정규화 (010-xxxx-xxxx)
   - 날짜 형식 통일
   - 매출 데이터 숫자 변환
5. **데이터 입력**: CSV 데이터 마이그레이션
6. **검증**: API 테스트 및 통계 확인

### 3.2 주의사항
- 전화번호가 10자리인 경우 010 추가
- 다양한 날짜 형식 처리 (YYYY-MM-DD, YYYY.MM.DD 등)
- 매출 데이터의 쉼표, '원' 제거
- 상태(status)는 날짜 데이터 기반 자동 설정

### 3.3 스크립트 파일
- **분석**: `scripts/check_current_leads.py` - 현재 DB 상태 확인
- **CSV 분석**: `scripts/analyze_lead_csv.py` - CSV 구조 분석
- **마이그레이션**: `scripts/migrate_real_leads.py` - 실제 데이터 마이그레이션

## 4. 실행 방법

```bash
# 1. 현재 상태 확인
python scripts/check_current_leads.py

# 2. CSV 파일 분석
python scripts/analyze_lead_csv.py

# 3. 데이터 마이그레이션 (주의: 기존 데이터 삭제됨)
python scripts/migrate_real_leads.py
```

## 5. 마이그레이션 후 확인사항
- [ ] 전체 리드 수 일치 확인
- [ ] 매출 총액 일치 확인
- [ ] 상태별 분포 확인
- [ ] API 엔드포인트 정상 작동 확인
- [ ] 프론트엔드 리드 관리 페이지 확인