# AIBIO 센터 관리 시스템 - 상세 기능 명세서

## 1. 고객 관리 모듈

### 1.1 고객 등록
```typescript
interface Customer {
  customer_id: number;
  name: string;
  phone: string;
  first_visit_date: Date;
  region: string;
  referral_source: string;
  health_concerns: string;
  notes: string;
  assigned_staff: string;
  created_at: Date;
  updated_at: Date;
}
```

**기능 상세**
- 필수 입력: 이름, 연락처
- 선택 입력: 거주지역, 방문경로, 호소문제, 담당자
- 연락처 형식 자동 변환 (010-1234-5678)
- 중복 고객 검사 (이름 + 연락처)

### 1.2 고객 검색
- 실시간 검색 (debounce 300ms)
- 검색 필터: 이름, 전화번호, 지역, 방문경로
- 정렬: 최근 방문순, 이름순, 등록일순
- 페이지네이션 (20건/페이지)

### 1.3 고객 상세 정보
- 기본 정보 표시
- 서비스 이용 내역 (타임라인 뷰)
- 구매 패키지 현황
- 결제 내역
- 상담 메모 히스토리

## 2. 서비스 이용 관리 모듈

### 2.1 서비스 등록
```typescript
interface ServiceUsage {
  usage_id: number;
  customer_id: number;
  service_date: Date;
  service_type: 'brain' | 'pulse' | 'lymph' | 'red';
  package_id: number;
  session_details: string;
  session_number: number;
  created_by: string;
}
```

**기능 상세**
- 고객 선택 (자동완성)
- 서비스 종류 선택 (다중 선택 가능)
- 패키지 자동 차감
- 세션 상세 내용 기록
- 담당자 자동 기록

### 2.2 일별 서비스 현황
- 캘린더 뷰 제공
- 서비스별 색상 구분
- 드래그 앤 드롭으로 일정 변경
- 일별 서비스 통계

### 2.3 패키지 잔여 관리
- 실시간 잔여 횟수 표시
- 만료 임박 패키지 알림 (7일 전)
- 패키지별 이용 히스토리
- 잔여 횟수 수동 조정 (권한 필요)

## 3. 결제 관리 모듈

### 3.1 결제 등록
```typescript
interface Payment {
  payment_id: number;
  customer_id: number;
  payment_date: Date;
  amount: number;
  payment_method: 'card' | 'transfer' | 'cash';
  card_holder_name?: string;
  approval_number?: string;
  payment_staff: string;
  purchase_type: 'new' | 'renewal';
  purchase_order: number;
}
```

**기능 상세**
- 패키지 선택 시 금액 자동 입력
- 결제 방법별 필수 정보 체크
- 영수증 즉시 출력
- 결제 취소 기능 (권한 필요)

### 3.2 결제 내역 조회
- 기간별 조회 (일/주/월/년)
- 결제 방법별 필터
- 엑셀 다운로드
- 매출 집계 표시

## 4. 패키지 관리 모듈

### 4.1 패키지 설정
```typescript
interface Package {
  package_id: number;
  package_name: string;
  total_sessions: number;
  price: number;
  valid_days: number;
  service_types: string[];
  is_active: boolean;
}
```

**기능 상세**
- 패키지 CRUD
- 서비스 종류 매핑
- 가격 히스토리 관리
- 판매 중단/재개

### 4.2 패키지 구매 관리
- 구매 시 자동 만료일 계산
- 패키지 연장 기능
- 패키지 양도 기능
- 환불 처리

## 5. 마케팅 리드 관리 모듈

### 5.1 리드 등록
```typescript
interface MarketingLead {
  lead_id: number;
  name: string;
  phone: string;
  lead_date: Date;
  channel: 'youtube' | 'carrot' | 'meta' | 'friend' | 'search' | 'other';
  status: 'new' | 'phone_consult' | 'visit_consult' | 'registered' | 'dropped';
  converted_customer_id?: number;
}
```

**기능 상세**
- 리드 상태 자동 추적
- 전환 퍼널 분석
- 채널별 ROI 계산
- 리드 → 고객 자동 전환

### 5.2 리드 추적
- 칸반 보드 뷰
- 상태별 자동 이동
- 담당자 배정
- 팔로우업 알림

## 6. 대시보드 모듈

### 6.1 매출 대시보드
- 실시간 매출 현황
- 전일/전주/전월 대비
- 결제 방법별 비중
- 시간대별 매출 추이

### 6.2 서비스 대시보드
- 서비스별 이용률
- 인기 서비스 순위
- 시간대별 이용 현황
- 직원별 서비스 제공 현황

### 6.3 고객 대시보드
- 신규/재방문 비율
- 지역별 고객 분포
- 고객 생애 가치 (LTV)
- 이탈 고객 분석

### 6.4 마케팅 대시보드
- 채널별 유입 현황
- 전환율 추이
- 획득 비용 (CAC)
- ROI 분석

## 7. 시스템 관리 모듈

### 7.1 사용자 관리
- 직원 계정 CRUD
- 권한 그룹 설정
- 접근 로그 조회
- 비밀번호 정책

### 7.2 데이터 관리
- 엑셀 가져오기 (템플릿 제공)
- 엑셀 내보내기 (커스텀 포맷)
- 자동 백업 설정
- 데이터 복원

### 7.3 시스템 설정
- 업체 정보 관리
- 서비스 종류 관리
- 알림 설정
- API 키 관리

## 8. 보고서 모듈

### 8.1 정기 보고서
- 일일 매출 보고서
- 주간 운영 보고서
- 월간 경영 보고서
- 분기별 성과 보고서

### 8.2 맞춤 보고서
- 보고서 빌더
- 차트 선택
- 필터 설정
- PDF/엑셀 내보내기

## 9. 알림 시스템

### 9.1 실시간 알림
- 신규 고객 등록
- 대기 고객 알림
- 패키지 만료 임박
- 매출 목표 달성

### 9.2 예약 알림
- 일일 매출 요약 (오후 6시)
- 주간 리포트 (월요일 오전 9시)
- 월간 정산 알림
- 재구매 시점 알림

## 10. 모바일 대응

### 10.1 반응형 디자인
- 태블릿 최적화 (768px~1024px)
- 모바일 최적화 (~767px)
- 터치 인터페이스
- 스와이프 제스처

### 10.2 모바일 전용 기능
- QR 코드 체크인
- 간편 서비스 등록
- 푸시 알림
- 오프라인 모드