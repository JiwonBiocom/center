# Post-Mortem: 고객 등록 API 에러 분석

## 발생한 문제
1. **404 에러**: POST /api/v1/customers 엔드포인트 없음
2. **500 에러**: membership_level enum 값 불일치 ("bronze" vs "basic")

## 근본 원인

### 1. 스키마 드리프트 (Schema Drift)
- **문제**: 데이터베이스의 실제 enum 값과 애플리케이션 코드의 enum 값이 다름
- **원인**: 
  - DB: membership_level = ['basic', 'silver', 'gold', 'platinum', 'vip']
  - 코드: membership_level = ['bronze', 'silver', 'gold', 'platinum']
- **영향**: 런타임에서만 발견되는 치명적 에러

### 2. API 경로 일관성 문제
- **문제**: FastAPI의 redirect_slashes=False 설정으로 정확한 경로 매칭 필요
- **원인**: 프론트엔드와 백엔드 간 trailing slash 처리 방식 불일치
- **영향**: 특정 환경(프로덕션)에서만 발생하는 404 에러

### 3. 환경 간 불일치
- **문제**: 로컬 개발 환경과 프로덕션 환경의 차이
- **원인**: 배포 프로세스에서 스키마 검증 부재
- **영향**: 배포 후에야 문제 발견

## 핵심 교훈
1. **타입 안정성**: Enum 값은 단일 소스에서 관리되어야 함
2. **스키마 동기화**: DB 스키마와 코드 스키마는 자동으로 동기화되어야 함
3. **배포 전 검증**: 프로덕션 배포 전 스키마 일치 검증 필수

## 방지 방안
1. DB enum 값을 코드에서 자동으로 가져오는 메커니즘
2. 배포 파이프라인에 스키마 검증 단계 추가
3. API 경로 테스트 자동화