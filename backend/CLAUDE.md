# Backend 개발 가이드

> 📌 이 문서는 백엔드 특화 규칙입니다.
> 글로벌 개발 원칙은 [글로벌 CLAUDE.md](../../CLAUDE.md)를 먼저 참조하세요.
> 프로젝트 원칙은 [루트 CLAUDE.md](../CLAUDE.md)를 참조하세요.
> 적용 우선순위: 글로벌 → 프로젝트 → 백엔드 규칙

## 📢 중요 공지
> 🔄 많은 규칙이 프로젝트 전체 [`development-rules.md`](../docs/development-rules.md)로 통합되었습니다.
> 이 문서는 백엔드 특화 내용만 담고 있습니다.

## 목차
1. [백엔드 특화 규칙](#1-백엔드-특화-규칙)
2. [FastAPI 특화 설정](#2-fastapi-특화-설정)
3. [자주 사용하는 Import](#3-자주-사용하는-import)
4. [환경 변수](#4-환경-변수)
5. [백엔드 체크리스트](#5-백엔드-체크리스트)

## 1. 백엔드 특화 규칙

### 1.1 FastAPI 애플리케이션 구조
```python
# main.py
app = FastAPI(
    title="AIBIO Center API",
    version="1.0.0",
    redirect_slashes=False  # 중요: trailing slash 엄격 모드
)
```

### 1.2 비동기 프로그래밍
- 모든 엔드포인트는 `async def` 사용
- DB 작업은 `asyncio` 호환 드라이버 사용
- 동기 작업은 `run_in_executor` 활용

### 1.3 의존성 주입 패턴
```python
# 재사용 가능한 의존성
async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
```

## 2. FastAPI 특화 설정

### 2.1 미들웨어 순서
```python
# CORS는 가장 먼저
app.add_middleware(CORSMiddleware, ...)
# 그 다음 인증
app.add_middleware(AuthenticationMiddleware, ...)
# 마지막에 로깅
app.add_middleware(LoggingMiddleware, ...)
```

### 2.2 백그라운드 태스크
```python
from fastapi import BackgroundTasks

@router.post("/send-notification/")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email_notification, email)
    return {"message": "Notification will be sent"}
```

## 3. 자주 사용하는 Import
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from core.database import get_db
from core.auth import get_current_user
from models.user import User
```

## 4. 환경 변수

### 4.1 필수 환경 변수
```bash
# .env
DATABASE_URL=postgresql://user:pass@localhost/dbname
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
ENVIRONMENT=development
```

### 4.2 환경 변수 로딩
```python
# core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()
```

## 5. 백엔드 체크리스트

### 5.1 API 개발 체크리스트
- [ ] 엔드포인트 경로가 `/api/v1/` 프리픽스 사용
- [ ] POST/PUT/PATCH는 trailing slash 두 버전 모두 등록
- [ ] 응답 모델(response_model) 정의
- [ ] 인증이 필요한 경우 `Depends(get_current_user)` 추가
- [ ] 적절한 HTTP 상태 코드 반환
- [ ] 에러 케이스 처리 (try/except)

### 5.2 데이터베이스 체크리스트
- [ ] 마이그레이션 파일 생성
- [ ] 인덱스 필요 여부 검토
- [ ] Foreign Key 제약 조건 설정
- [ ] 트랜잭션 범위 적절성

### 5.3 보안 체크리스트
- [ ] SQL Injection 방지 (파라미터 바인딩)
- [ ] 민감한 정보 로깅 금지
- [ ] CORS 설정 확인
- [ ] Rate Limiting 적용

---

## 🔗 관련 문서
- [개발 규칙](../docs/development-rules.md) - 프로젝트 전체 개발 규칙
- [API 라우팅 스타일](../docs/api-routing-style.md) - Trailing slash 정책 상세
- [테스트 전략](../docs/test-strategy.md) - 백엔드 테스트 가이드
- [데이터베이스 스키마](../docs/database-schema.md) - 최신 DB 구조

*백엔드 작업 시 이 문서와 프로젝트 개발 규칙을 함께 참조하세요.*
