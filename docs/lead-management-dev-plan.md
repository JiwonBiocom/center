# 유입고객 관리 시스템 개발 계획

## 1. 현재 상태 분석

### 기존 시스템
- **테이블**: marketing_leads
- **주요 필드**: 23개 (lead_date 포함)
- **현재 데이터**: 176개 실제 유입고객 데이터
- **프론트엔드**: 기본적인 리스트/필터 기능

### 추가 필요 필드
1. DB작성 채널 (현재 notes에 포함)
2. 전화상담 결과
3. 전화상담 리마인드 일자
4. 방문취소 여부/사유
5. 재등록 대상 여부
6. 마지막 이용일
7. 재등록 제안일
8. 담당자 정보

## 2. 데이터베이스 설계

### 2.1 marketing_leads 테이블 확장
```sql
-- 기존 필드는 유지하고 추가
ALTER TABLE marketing_leads ADD COLUMN db_channel VARCHAR(50);
ALTER TABLE marketing_leads ADD COLUMN phone_consult_result VARCHAR(100);
ALTER TABLE marketing_leads ADD COLUMN remind_date DATE;
ALTER TABLE marketing_leads ADD COLUMN visit_cancelled BOOLEAN DEFAULT FALSE;
ALTER TABLE marketing_leads ADD COLUMN visit_cancel_reason TEXT;
ALTER TABLE marketing_leads ADD COLUMN is_reregistration_target BOOLEAN DEFAULT FALSE;
ALTER TABLE marketing_leads ADD COLUMN last_service_date DATE;
ALTER TABLE marketing_leads ADD COLUMN reregistration_proposal_date DATE;
ALTER TABLE marketing_leads ADD COLUMN assigned_staff_id INTEGER REFERENCES users(user_id);
```

### 2.2 새로운 테이블
```sql
-- 상담 이력 테이블
CREATE TABLE lead_consultation_history (
    history_id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES marketing_leads(lead_id),
    consultation_type VARCHAR(20), -- phone, visit
    consultation_date TIMESTAMP,
    result VARCHAR(100),
    notes TEXT,
    created_by INTEGER REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 재등록 캠페인 테이블
CREATE TABLE reregistration_campaigns (
    campaign_id SERIAL PRIMARY KEY,
    campaign_name VARCHAR(100),
    start_date DATE,
    end_date DATE,
    target_criteria JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 3. API 설계

### 3.1 엔드포인트 구조
```
/api/v1/leads/ → /api/v1/customer-leads/

GET    /customer-leads/              # 리스트 조회 (고급 필터)
GET    /customer-leads/{id}          # 상세 조회
POST   /customer-leads/              # 신규 생성
PUT    /customer-leads/{id}          # 수정
DELETE /customer-leads/{id}          # 삭제 (soft delete)

# 추가 엔드포인트
POST   /customer-leads/bulk-import   # 엑셀 일괄 등록
GET    /customer-leads/export        # 엑셀 다운로드
GET    /customer-leads/stats         # 통계 조회
POST   /customer-leads/{id}/consultation  # 상담 기록 추가
GET    /customer-leads/reregistration-targets  # 재등록 대상 조회
POST   /customer-leads/assign-staff  # 담당자 일괄 지정
```

### 3.2 필터 파라미터
```python
class CustomerLeadFilter(BaseModel):
    # 기간 필터
    db_entry_date_from: Optional[date]
    db_entry_date_to: Optional[date]
    
    # 상태 필터
    status: Optional[List[str]]
    has_phone_consult: Optional[bool]
    has_visit_consult: Optional[bool]
    is_registered: Optional[bool]
    is_reregistration_target: Optional[bool]
    
    # 채널 필터
    lead_channel: Optional[List[str]]
    db_channel: Optional[List[str]]
    
    # 기타 필터
    age_from: Optional[int]
    age_to: Optional[int]
    region: Optional[List[str]]
    assigned_staff_id: Optional[int]
    
    # 검색
    search: Optional[str]  # 이름, 전화번호, 비고
```

## 4. 프론트엔드 설계

### 4.1 컴포넌트 구조
```
pages/
├── CustomerLeads.tsx          # 메인 페이지
components/
├── customer-leads/
│   ├── CustomerLeadTable.tsx      # 테이블 뷰
│   ├── CustomerLeadCard.tsx       # 카드 뷰
│   ├── CustomerLeadDetail.tsx     # 상세 모달
│   ├── CustomerLeadFilters.tsx    # 고급 필터
│   ├── CustomerLeadStats.tsx      # 통계 대시보드
│   ├── ConsultationHistory.tsx    # 상담 이력
│   ├── ReregistrationTargets.tsx  # 재등록 대상
│   └── BulkActions.tsx           # 일괄 작업
```

### 4.2 상태 관리
```typescript
interface CustomerLeadState {
  // 리스트 데이터
  leads: CustomerLead[];
  totalCount: number;
  loading: boolean;
  
  // 필터 상태
  filters: CustomerLeadFilter;
  savedFilters: SavedFilter[];
  
  // 선택 상태
  selectedLeads: number[];
  
  // 뷰 설정
  viewMode: 'table' | 'card';
  visibleColumns: string[];
  sortBy: string;
  sortOrder: 'asc' | 'desc';
}
```

## 5. 주요 기능 구현 상세

### 5.1 상담 워크플로우
1. **전화상담**
   - 상담 예약 (날짜/시간)
   - 상담 결과 기록
   - 자동 상태 변경
   - 다음 액션 제안

2. **방문상담**
   - 예약 시스템 연동
   - 방문 확인/취소 처리
   - 상담 결과 → 등록 연계

### 5.2 재등록 대상 관리
1. **자동 선별 조건**
   - 마지막 이용일 > 3개월
   - 패키지 만료 고객
   - 특정 미등록 사유

2. **캠페인 실행**
   - 대상 선정
   - 일괄 연락 기록
   - 결과 추적

### 5.3 엑셀 연동
1. **Import 매핑**
   ```
   엑셀 컬럼 → DB 필드
   이름 → name
   유입경로 → lead_channel
   DB작성 채널 → db_channel
   연락처 → phone
   ...
   ```

2. **중복 처리**
   - 전화번호 기준 체크
   - 업데이트/스킵 옵션

## 6. 마이그레이션 계획

### 6.1 데이터 마이그레이션
1. 기존 notes 필드에서 DB작성 채널 추출
2. 고객 테이블과 연계하여 마지막 이용일 계산
3. 재등록 대상 자동 표시

### 6.2 단계별 전환
1. **1단계**: 새 스키마 생성, 기존 데이터 유지
2. **2단계**: 병렬 운영 (신규 데이터는 새 시스템)
3. **3단계**: 전체 전환 및 기존 시스템 폐기

## 7. 테스트 계획

### 7.1 단위 테스트
- API 엔드포인트별 테스트
- 필터링 로직 테스트
- 상태 전환 테스트

### 7.2 통합 테스트
- 상담 워크플로우 전체 과정
- 엑셀 import/export
- 권한별 접근 제어

### 7.3 성능 테스트
- 대량 데이터 필터링 (10,000건+)
- 동시 사용자 처리
- 엑셀 처리 속도

## 8. 일정 계획 (4주)

### Week 1: 백엔드 기초
- [ ] DB 스키마 확장
- [ ] 모델 업데이트
- [ ] 기본 CRUD API
- [ ] 마이그레이션 스크립트

### Week 2: 백엔드 고급
- [ ] 고급 필터링 API
- [ ] 상담 워크플로우 API
- [ ] 통계 API
- [ ] 엑셀 연동 API

### Week 3: 프론트엔드 기초
- [ ] 메뉴 및 라우팅
- [ ] 테이블/카드 뷰
- [ ] 기본 필터
- [ ] 상세 모달

### Week 4: 프론트엔드 고급
- [ ] 고급 필터 UI
- [ ] 상담 워크플로우 UI
- [ ] 대시보드
- [ ] 일괄 작업
- [ ] 테스트 및 버그 수정

## 9. 위험 요소 및 대응

1. **데이터 정합성**
   - 리스크: 마이그레이션 중 데이터 손실
   - 대응: 백업 및 검증 스크립트

2. **성능 이슈**
   - 리스크: 복잡한 필터링으로 속도 저하
   - 대응: 인덱스 최적화, 페이징, 캐싱

3. **사용자 교육**
   - 리스크: 복잡한 UI로 사용 어려움
   - 대응: 단계별 기능 공개, 가이드 제공