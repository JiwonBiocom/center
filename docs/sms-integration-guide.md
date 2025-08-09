# SMS 통합 가이드

## 개요
AIBIO 센터 관리 시스템에 Aligo API를 통한 SMS 발송 기능이 추가되었습니다.

## 주요 기능

### 1. SMS 발송 기능
- **개별 발송**: 고객 관리 페이지에서 각 고객별로 SMS 발송 가능
- **템플릿 메시지**: 
  - 생일 축하 메시지
  - 휴면 고객 재활성화 메시지
  - 사용자 정의 메시지
- **자동 SMS/LMS 구분**: 90자 초과 시 자동으로 LMS로 전환

### 2. 통합 위치
- 고객 관리 페이지: 각 고객 행에 SMS 버튼 추가
- 예약 관리 페이지: 예약 확인/변경 시 SMS 발송 (구현 예정)
- 유입고객 관리: 캠페인 SMS 발송 (구현 예정)

## 기술 구현

### 백엔드
1. **Aligo 서비스** (`/backend/services/aligo_service.py`)
   - SMS/LMS 발송
   - 잔여 건수 조회
   - 대량 발송 지원

2. **API 엔드포인트** (`/backend/api/v1/sms_v2.py`)
   - `POST /api/v1/sms/send`: SMS 발송
   - `GET /api/v1/sms/remain`: 잔여 건수 조회

3. **환경 변수** (`.env`)
   ```
   ALIGO_API_KEY=your_api_key
   ALIGO_USER_ID=your_user_id
   ALIGO_SENDER=02-2039-2783
   ```

### 프론트엔드
1. **SMS 모달** (`/frontend/src/components/SMSModal.tsx`)
   - 메시지 타입 선택
   - 메시지 미리보기
   - 발송 확인

2. **고객 테이블** (`/frontend/src/components/customers/CustomerTable.tsx`)
   - 각 고객별 SMS 버튼 추가
   - 모달 연동

## 사용 방법

### 개별 SMS 발송
1. 고객 관리 페이지에서 원하는 고객의 SMS 버튼 클릭
2. 메시지 타입 선택 (생일 축하/휴면 재활성화/사용자 정의)
3. 메시지 내용 확인/수정
4. 발송 버튼 클릭

### 템플릿 메시지
- **생일 축하**: `[AIBIO 센터] 생일 축하\n{고객명}님, 생일을 진심으로 축하드립니다! 🎂`
- **휴면 재활성화**: `[AIBIO 센터] 고객님을 기다립니다\n{고객명}님, 오랜만이에요! 다시 찾아주세요.`

## 주의사항
- SMS는 90자, LMS는 2000자 제한
- 발신번호는 사전 등록된 번호만 사용 가능
- 잔여 건수 확인 필요

## 향후 계획
- [ ] 설정 페이지에 SMS 설정 탭 추가
- [ ] 예약 관리 SMS 자동 발송
- [ ] 캠페인 대량 SMS 발송
- [ ] 발송 이력 관리