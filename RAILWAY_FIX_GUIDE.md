# Railway 배포 500 에러 해결 가이드

## 문제 요약
Railway에 배포된 센터 관리 시스템이 500 에러를 발생시키고 있으며, 주요 원인은 데이터베이스 스키마 불일치입니다.

## 확인된 문제들

### 1. notifications 테이블 문제
- **에러**: `Column notifications.user_id does not exist`
- **원인**: 실제 DB에 user_id 컬럼이 없음
- **해결**: ALTER TABLE로 컬럼 추가

### 2. packages 테이블 문제  
- **에러**: `Column packages.price does not exist`
- **원인**: 코드는 base_price를 사용하지만 DB는 price 컬럼을 가지고 있을 수 있음
- **해결**: price → base_price로 컬럼명 변경

### 3. 기타 잠재적 문제
- valid_days → valid_months 변경 필요
- customer_payments 레거시 테이블 존재 가능성

## 해결 방법

### 1단계: 생성된 SQL 파일 실행
다음 파일들 중 하나를 Supabase SQL Editor에서 실행:
- `schema_fix_20250621_103045.sql` - 기본 수정사항
- `railway_complete_fix.sql` - 전체 수정사항 (권장)

### 2단계: Supabase에서 SQL 실행
1. [Supabase Dashboard](https://app.supabase.com) 접속
2. 해당 프로젝트 선택
3. SQL Editor 메뉴 클릭
4. `railway_complete_fix.sql` 내용 복사/붙여넣기
5. Run 버튼 클릭

### 3단계: Railway 애플리케이션 재시작
1. [Railway Dashboard](https://railway.app) 접속
2. 해당 서비스 선택
3. Settings → Restart Service 클릭
   또는
4. 새로운 커밋을 푸시하여 자동 재배포 트리거

### 4단계: 검증
1. 배포 완료 후 로그 확인
2. 500 에러가 사라졌는지 확인
3. API 엔드포인트 테스트

## 추가 확인 사항

### 로컬에서 스키마 검증
```bash
cd backend
python scripts/check_schema.py --list
python scripts/check_schema.py --table notifications
python scripts/check_schema.py --table packages
```

### Railway 로그 모니터링
```bash
railway logs -f
```

## 문제가 지속될 경우

1. **전체 스키마 덤프 확인**
   - Supabase에서 현재 스키마 전체를 덤프
   - 로컬 모델과 비교

2. **환경 변수 확인**
   - Railway의 DATABASE_URL이 올바른지 확인
   - Supabase 연결 정보 검증

3. **마이그레이션 히스토리 확인**
   - 이전에 실행된 마이그레이션 스크립트 확인
   - 누락된 마이그레이션이 있는지 체크

## 예방 조치

1. **스키마 버전 관리**
   - Alembic 같은 마이그레이션 도구 도입 고려
   - 모든 스키마 변경사항을 마이그레이션 파일로 관리

2. **배포 전 체크리스트**
   - [ ] 로컬 스키마와 프로덕션 스키마 비교
   - [ ] 모든 모델 변경사항이 마이그레이션에 포함되었는지 확인
   - [ ] 스테이징 환경에서 먼저 테스트

3. **모니터링 강화**
   - Railway 로그 알림 설정
   - 에러 추적 도구 (Sentry 등) 도입 고려