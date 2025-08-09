# 🚀 로컬 데이터 전체 마이그레이션 종합 계획

## 📊 현재 상황 분석

### 1. 마이그레이션 완료된 데이터
- ✅ payments (결제): 412건 - 단, 일부 필드 누락
  - ❌ purchase_type (구매 항목)
  - ❌ payment_staff (담당자)
  - ❌ card_holder_name (카드 소유자)
  - ❌ approval_number (승인번호)
  - ❌ purchase_order (구매 순서)

### 2. 마이그레이션 필요한 데이터
- ❌ packages (패키지 정보)
- ❌ package_purchases (패키지 구매 내역)
- ❌ services (서비스 이용 내역)
- ❌ service_types (서비스 종류)
- ❌ kits (키트 정보)
- ❌ reservations (예약 정보)
- ❌ inbody_records (인바디 기록)
- ❌ customer_extended 관련 데이터
- ❌ leads (유입 고객)
- ❌ staff_schedule (직원 스케줄)
- ❌ 기타 설정 및 메타데이터

## 🎯 마이그레이션 목표
1. 로컬 SQLite DB의 **모든 데이터**를 Supabase PostgreSQL로 이전
2. 데이터 무결성 100% 보장
3. 외래키 관계 유지
4. 누락된 필드 복원
5. 자동화된 프로세스 구축

## 📋 단계별 실행 계획

### Phase 1: 데이터 분석 (10분)
1. 로컬 DB 전체 스키마 추출
2. 각 테이블별 데이터 건수 파악
3. 테이블 간 의존성 분석
4. Supabase 스키마와 차이점 분석

### Phase 2: 결제 데이터 보완 (20분)
1. payments 테이블의 누락된 필드 데이터 추출
2. 전체 컬럼 포함한 CSV 재생성
3. UPDATE 쿼리로 누락 필드 업데이트

### Phase 3: 핵심 테이블 마이그레이션 (30분)
우선순위 순서:
1. **service_types** - 서비스 종류 마스터
2. **packages** - 패키지 마스터
3. **package_purchases** - 패키지 구매 내역
4. **services** - 서비스 이용 내역
5. **kits** - 키트 정보

### Phase 4: 고객 관련 데이터 (20분)
1. **customer_extended** 필드 업데이트
2. **leads** - 유입 고객 정보
3. **inbody_records** - 인바디 측정 기록
4. **questionnaire_responses** - 문진 응답

### Phase 5: 운영 데이터 (15분)
1. **reservations** - 예약 정보
2. **staff_schedule** - 직원 스케줄
3. **notifications** - 알림 내역
4. **settings** - 시스템 설정

### Phase 6: 검증 및 보고 (15분)
1. 각 테이블별 데이터 건수 비교
2. 주요 통계 지표 검증
3. 데이터 무결성 테스트
4. 최종 보고서 생성

## 🛠️ 기술적 접근 방법

### 1. 통합 마이그레이션 스크립트
```python
# migrate_all_data.py
1. SQLite 연결
2. PostgreSQL 연결
3. 테이블별 순차 마이그레이션
4. 트랜잭션 관리
5. 진행 상황 실시간 표시
```

### 2. 데이터 변환 규칙
- 날짜/시간: SQLite → PostgreSQL 형식
- 한글 → 영문 매핑 (payment_method 등)
- NULL 처리 규칙
- 외래키 검증

### 3. 백업 및 롤백 전략
- 마이그레이션 전 Supabase 백업
- 각 테이블별 체크포인트
- 실패 시 자동 롤백

## 📊 예상 데이터 규모

```
테이블명                예상 건수
----------------------------------
customers              918
payments               412+
packages               10-20
package_purchases      500+
services               1000+
service_types          7
kits                   100+
reservations           200+
inbody_records         500+
leads                  100+
staff_schedule         50+
----------------------------------
총 예상 레코드 수      3,500+
```

## 🚨 주의사항

1. **데이터 보안**
   - 민감 정보 마스킹 불필요 (프로덕션 데이터)
   - HTTPS 통신 사용
   - 로그에 개인정보 미포함

2. **성능 고려사항**
   - 배치 처리 (100-500건 단위)
   - 인덱스 일시 비활성화
   - 트랜잭션 크기 관리

3. **의존성 순서**
   - customers → payments
   - service_types → services
   - packages → package_purchases
   - 외래키 제약 순서 준수

## 📝 실행 체크리스트

- [ ] 로컬 DB 백업 생성
- [ ] Supabase 현재 상태 백업
- [ ] 마이그레이션 스크립트 작성
- [ ] 테스트 실행 (일부 데이터)
- [ ] 전체 마이그레이션 실행
- [ ] 데이터 검증
- [ ] 애플리케이션 테스트
- [ ] 최종 보고서 작성

## 🎯 성공 기준

1. **정량적 지표**
   - 모든 테이블 데이터 100% 이전
   - 외래키 관계 100% 유지
   - 데이터 건수 일치율 100%

2. **정성적 지표**
   - 애플리케이션 모든 기능 정상 작동
   - 보고서 및 통계 정확성
   - 사용자 경험 동일성

## 🔄 다음 단계

1. 이 계획 승인 요청
2. Phase 1 즉시 실행 (데이터 분석)
3. 분석 결과 기반 상세 스크립트 작성
4. 단계별 실행 및 검증

---

준비되셨으면 Phase 1부터 시작하겠습니다! 🚀