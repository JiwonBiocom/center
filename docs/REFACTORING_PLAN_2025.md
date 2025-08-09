# AIBIO 센터 관리 시스템 리팩토링 계획

> 작성일: 2025-06-12  
> 대상: AIBIO 센터 관리 시스템  
> 목표: 코드 품질 개선 및 유지보수성 향상  
> 제약: UX/UI 변경 없음, 배포 환경 호환성 유지

## 📋 목차
1. [개요](#개요)
2. [현재 상태 분석](#현재-상태-분석)
3. [리팩토링 원칙](#리팩토링-원칙)
4. [단계별 실행 계획](#단계별-실행-계획)
5. [배포 환경 고려사항](#배포-환경-고려사항)
6. [검증 계획](#검증-계획)
7. [일정 및 마일스톤](#일정-및-마일스톤)

## 개요

### 목표
- 코드 중복 제거 및 일관성 확보
- 유지보수성 향상
- 배포 안정성 보장
- **UX/UI 변경 없이** 내부 구조만 개선

### 배포 환경
- **Frontend**: Vercel
- **Backend**: Railway
- **Database**: Supabase (PostgreSQL)

## 현재 상태 분석

### 주요 문제점
1. **중복 코드**
   - Backend: CRUD 작업 반복, 에러 처리 불일치
   - Frontend: Modal 컴포넌트 중복, 유틸리티 함수 산재

2. **일관성 부족**
   - API 응답 구조 불일치
   - 에러 처리 방식 제각각
   - 네이밍 규칙 일부 불일치

3. **타입 관리**
   - Backend/Frontend 타입 동기화 부재
   - 일부 컴포넌트 자체 타입 정의

## 리팩토링 원칙

### 핵심 원칙
1. **점진적 개선**: 작은 단위로 나누어 안전하게 진행
2. **무중단 배포**: 각 단계별 배포 가능한 상태 유지
3. **UX/UI 불변**: 사용자 경험 변경 없음
4. **테스트 우선**: 모든 변경 전후 테스트 실행

### 제약사항
- 한 번에 하나의 영역만 수정
- 각 변경 후 즉시 배포 테스트
- API 엔드포인트 URL 변경 금지
- 데이터베이스 스키마 변경 최소화

## 단계별 실행 계획

### Phase 1: 기초 정리 (1주차)

#### 1.1 공통 유틸리티 함수 생성
```typescript
// frontend/src/lib/utils/format.ts
export const formatters = {
  date: (date: Date | string) => {
    const d = typeof date === 'string' ? new Date(date) : date
    return d.toLocaleDateString('ko-KR')
  },
  
  phone: (phone: string) => {
    const cleaned = phone.replace(/\D/g, '')
    if (cleaned.length === 11) {
      return cleaned.replace(/(\d{3})(\d{4})(\d{4})/, '$1-$2-$3')
    }
    return cleaned.replace(/(\d{3})(\d{3})(\d{4})/, '$1-$2-$3')
  },
  
  currency: (amount: number) => {
    return `₩${amount.toLocaleString('ko-KR')}`
  }
}
```

**작업 내용**:
- [ ] `/frontend/src/lib/utils/format.ts` 생성
- [ ] 기존 컴포넌트에서 포맷팅 로직 제거 및 import로 대체
- [ ] 테스트 작성

**배포 영향**: 없음 (Frontend 빌드만 확인)

#### 1.2 Backend 에러 핸들러 통일
```python
# backend/utils/error_handlers.py 확장
from functools import wraps
from sqlalchemy.orm import Session
from fastapi import HTTPException
import logging

def handle_api_errors(operation: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"{operation} 실패: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"{operation} 중 오류가 발생했습니다"
                )
        return wrapper
    return decorator
```

**작업 내용**:
- [ ] 에러 핸들러 데코레이터 확장
- [ ] 모든 API 엔드포인트에 적용
- [ ] 로깅 표준화

**배포 영향**: Railway 환경 변수 확인 필요

### Phase 2: 구조 개선 (2-3주차)

#### 2.1 Frontend Modal 베이스 컴포넌트
```typescript
// frontend/src/components/common/BaseModal.tsx
interface BaseModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
  onSubmit?: (e: React.FormEvent) => Promise<void>
  loading?: boolean
}

export function BaseModal({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  onSubmit,
  loading = false 
}: BaseModalProps) {
  if (!isOpen) return null
  
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black opacity-50" onClick={onClose} />
      <div className="relative bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">{title}</h2>
        {onSubmit ? (
          <form onSubmit={onSubmit}>
            {children}
            <div className="flex justify-end space-x-2 mt-6">
              <button type="button" onClick={onClose} disabled={loading}>
                취소
              </button>
              <button type="submit" disabled={loading}>
                {loading ? '처리중...' : '저장'}
              </button>
            </div>
          </form>
        ) : (
          children
        )}
      </div>
    </div>
  )
}
```

**작업 내용**:
- [ ] BaseModal 컴포넌트 생성
- [ ] 기존 Modal들을 BaseModal 기반으로 리팩토링
- [ ] useModal 커스텀 훅 생성

**배포 영향**: UI 변경 없음 확인 필요

#### 2.2 Backend CRUD 베이스 클래스
```python
# backend/api/v1/base.py
from typing import Type, TypeVar, Generic, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def get(self, db: Session, id: int) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
```

**작업 내용**:
- [ ] CRUD 베이스 클래스 생성
- [ ] 각 모델별 CRUD 클래스 생성
- [ ] API 엔드포인트 리팩토링

**배포 영향**: API 응답 구조 변경 없음 확인

### Phase 3: API 표준화 (4주차)

#### 3.1 API 응답 구조 통일
```python
# backend/schemas/response.py
from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[dict] = None
    meta: Optional[dict] = None

class PaginatedResponse(BaseModel, Generic[T]):
    success: bool
    data: List[T]
    total: int
    page: int
    page_size: int
```

**작업 내용**:
- [ ] 표준 응답 스키마 정의
- [ ] 모든 엔드포인트에 점진적 적용
- [ ] Frontend API 클라이언트 수정

**배포 영향**: Frontend/Backend 동시 배포 필요

### Phase 4: 타입 동기화 (5주차)

#### 4.1 타입 자동 생성 설정
```json
// package.json 추가
{
  "scripts": {
    "generate-types": "openapi-typescript http://localhost:8000/openapi.json -o src/types/api.d.ts"
  }
}
```

**작업 내용**:
- [ ] OpenAPI 스키마 생성 설정
- [ ] TypeScript 타입 자동 생성
- [ ] 기존 타입 정의 마이그레이션

**배포 영향**: 빌드 프로세스 변경

## 배포 환경 고려사항

### Vercel (Frontend)
```json
// vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ]
}
```

**체크리스트**:
- [ ] 환경 변수 설정 (VITE_API_URL)
- [ ] 빌드 크기 모니터링
- [ ] Preview 배포로 테스트

### Railway (Backend)
```toml
# railway.toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/api/v1/health"
```

**체크리스트**:
- [ ] 환경 변수 확인
- [ ] 헬스체크 엔드포인트 유지
- [ ] 로그 스트리밍 확인

### Supabase (Database)
**체크리스트**:
- [ ] 마이그레이션 스크립트 준비
- [ ] 연결 풀 설정 확인
- [ ] 백업 스케줄 확인

## 검증 계획

### 각 Phase별 검증
1. **단위 테스트**
   ```bash
   # Backend
   pytest tests/
   
   # Frontend
   npm run test
   ```

2. **통합 테스트**
   ```bash
   # API 엔드포인트 테스트
   python test_all_endpoints.py
   ```

3. **배포 테스트**
   - Preview 환경에서 먼저 테스트
   - 주요 사용자 시나리오 수동 테스트
   - 성능 메트릭 비교

### 롤백 계획
- 각 Phase별 git 태그 생성
- 문제 발생 시 이전 버전으로 즉시 롤백
- 데이터베이스 변경은 항상 reversible하게 작성

## 일정 및 마일스톤

### 전체 일정: 5주

| 주차 | Phase | 주요 작업 | 완료 기준 |
|------|-------|-----------|-----------|
| 1주 | Phase 1 | 유틸리티 함수, 에러 핸들러 | 빌드 성공, 테스트 통과 |
| 2-3주 | Phase 2 | Modal/CRUD 베이스 | UI 변경 없음 확인 |
| 4주 | Phase 3 | API 표준화 | API 호환성 유지 |
| 5주 | Phase 4 | 타입 동기화 | 자동 생성 설정 완료 |

### 주간 체크포인트
- 매주 금요일: 진행 상황 검토
- 매주 월요일: 다음 주 작업 계획
- 각 Phase 완료 시: 프로덕션 배포

## 위험 관리

### 주요 위험 요소
1. **API 호환성 문제**
   - 완화: 단계적 마이그레이션
   - 모니터링: API 버저닝 고려

2. **배포 중 장애**
   - 완화: Blue-Green 배포
   - 모니터링: 실시간 에러 추적

3. **성능 저하**
   - 완화: 성능 테스트 포함
   - 모니터링: 응답 시간 측정

## 성공 지표

### 정량적 지표
- 코드 중복률 50% 감소
- 빌드 시간 20% 단축
- 번들 크기 10% 감소

### 정성적 지표
- 신규 기능 개발 시간 단축
- 버그 발생률 감소
- 개발자 만족도 향상

## 결론

이 리팩토링 계획은 UX/UI를 변경하지 않으면서도 코드 품질을 크게 개선할 수 있도록 설계되었습니다. 각 단계는 독립적으로 배포 가능하며, 문제 발생 시 즉시 롤백할 수 있습니다.

**핵심 성공 요인**:
- 점진적이고 안전한 접근
- 철저한 테스트와 검증
- 배포 환경 특성 고려
- 명확한 롤백 계획

---

*이 문서는 리팩토링 진행 중 지속적으로 업데이트됩니다.*