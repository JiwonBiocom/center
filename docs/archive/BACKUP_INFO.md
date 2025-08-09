# 백업 정보

## 백업 일시: 2025년 6월 5일

### 주요 변경 파일
1. **백엔드 API**
   - `/backend/api/v1/kits.py` - 검사키트 API (새로 생성)
   - `/backend/api/v1/customers.py` - async → sync 변환, 정렬 개선
   - `/backend/api/v1/dashboard.py` - async → sync 변환, 통계 API
   - 기타 API 파일들 - 모두 sync로 변환

2. **모델 및 스키마**
   - `/backend/models/kit.py` - KitType, KitManagement 추가
   - `/backend/schemas/kit.py` - 검사키트 스키마 (새로 생성)

3. **프론트엔드**
   - `/frontend/src/pages/Kits.tsx` - 검사키트 관리 페이지 (새로 생성)
   - `/frontend/src/pages/Customers.tsx` - 페이지네이션 추가
   - `/frontend/src/pages/Dashboard.tsx` - 만원 단위 변경
   - `/frontend/src/components/KitModal.tsx` - 검사키트 모달 (새로 생성)
   - `/frontend/src/lib/api.ts` - FastAPI 슬래시 처리

4. **스크립트**
   - `/scripts/add_kit_types.py` - 검사키트 종류 추가
   - `/scripts/fix_all_apis.py` - API sync 변환 스크립트

5. **문서**
   - `/CLAUDE.md` - 데이터 관리 규칙 추가
   - `/DEVELOPMENT_LOG.md` - 개발 로그 (새로 생성)

### 데이터베이스 변경사항
- `kit_types` 테이블 추가 (5개 검사키트 종류)
- `kit_management` 테이블에 `kit_type_id` 컬럼 추가
- 2025년 6월 잘못된 결제 데이터 삭제

### 중요 설정
- 모든 API는 동기(sync) 방식 사용
- FastAPI 엔드포인트는 슬래시(/) 필요
- 페이지당 20개 항목 표시
- 전화번호 없는 고객은 후순위 정렬