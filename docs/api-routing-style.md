# 📡 API Routing Style Guide

> 버전: 1.0.0
> 최종 업데이트: 2025-06-22
> 목적: FastAPI 라우팅 정책과 trailing slash 처리 표준화

## 📋 목차
1. [핵심 문제](#-핵심-문제)
2. [Trailing Slash 정책](#-trailing-slash-정책)
3. [구현 가이드](#-구현-가이드)
4. [테스트 방법](#-테스트-방법)
5. [마이그레이션 가이드](#-마이그레이션-가이드)

## 🔥 핵심 문제

### 현재 상황
- **FastAPI 설정**: `redirect_slashes=False` (엄격 모드)
- **프론트엔드**: API 클라이언트가 POST/PUT/PATCH 요청에 자동으로 trailing slash 추가
- **결과**: 백엔드가 단일 경로만 정의하면 404 에러 발생

### 실제 발생한 문제 (2025-06)
```javascript
// 프론트엔드 (api.ts)
api.interceptors.request.use((config) => {
  if (['post', 'put', 'patch'].includes(config.method?.toLowerCase())) {
    if (!config.url.endsWith('/')) {
      config.url += '/';  // 자동으로 추가!
    }
  }
});

// 요청: POST /api/v1/users/ (trailing slash 포함)
```

```python
# 백엔드 (잘못된 예)
@router.post("/users")  # /users만 정의
def create_user(...):
    pass

# 결과: 404 Not Found ❌
```

## 🛡️ Trailing Slash 정책

### 1️⃣ 기본 원칙
- **POST/PUT/PATCH**: 반드시 두 버전 모두 정의 (with & without trailing slash)
- **GET/DELETE**: 프로젝트 표준에 따라 일관성 있게 하나만 정의
- **특수 경로**: 동적 경로(`/{id}`)도 동일한 규칙 적용

### 2️⃣ HTTP 메서드별 가이드

#### POST/PUT/PATCH (필수: 두 버전)
```python
# ✅ 올바른 구현
@router.post("/users")
@router.post("/users/")  # trailing slash 버전
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return {"message": "User created"}

@router.put("/users/{user_id}")
@router.put("/users/{user_id}/")  # trailing slash 버전
async def update_user(user_id: int, user: UserUpdate):
    return {"message": "User updated"}

@router.patch("/users/{user_id}")
@router.patch("/users/{user_id}/")  # trailing slash 버전
async def patch_user(user_id: int, user: UserPatch):
    return {"message": "User patched"}
```

#### GET/DELETE (선택: 일관성 유지)
```python
# 프로젝트 표준: trailing slash 없음
@router.get("/users")
async def get_users():
    return []

@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    return {"message": "User deleted"}

# 또는 프로젝트 표준: trailing slash 있음
@router.get("/users/")
async def get_users():
    return []
```

## 📝 구현 가이드

### 1. 새 엔드포인트 작성 시
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter()

# 리소스 목록 조회 (GET)
@router.get("/resources")
async def list_resources(db: Session = Depends(get_db)):
    return []

# 리소스 생성 (POST) - 두 버전 필수!
@router.post("/resources", response_model=ResourceResponse)
@router.post("/resources/", response_model=ResourceResponse)
async def create_resource(resource: ResourceCreate, db: Session = Depends(get_db)):
    return resource

# 특정 리소스 조회 (GET)
@router.get("/resources/{resource_id}")
async def get_resource(resource_id: int):
    return {}

# 리소스 수정 (PUT) - 두 버전 필수!
@router.put("/resources/{resource_id}")
@router.put("/resources/{resource_id}/")
async def update_resource(resource_id: int, resource: ResourceUpdate):
    return resource

# 리소스 삭제 (DELETE)
@router.delete("/resources/{resource_id}")
async def delete_resource(resource_id: int):
    return {"deleted": True}
```

### 2. 복잡한 경로 처리
```python
# 중첩된 리소스
@router.post("/users/{user_id}/preferences")
@router.post("/users/{user_id}/preferences/")
async def update_preferences(user_id: int, prefs: dict):
    return prefs

# 액션 엔드포인트
@router.post("/reservations/{reservation_id}/cancel")
@router.post("/reservations/{reservation_id}/cancel/")
async def cancel_reservation(reservation_id: int):
    return {"cancelled": True}
```

### 3. 일괄 처리 데코레이터 (선택적)
```python
def dual_route(path: str):
    """POST/PUT/PATCH 라우트에 자동으로 trailing slash 버전 추가"""
    def decorator(func):
        func = router.post(path)(func)
        func = router.post(f"{path}/")(func)
        return func
    return decorator

# 사용 예
@dual_route("/items")
async def create_item(item: ItemCreate):
    return item
```

## 🧪 테스트 방법

### 1. 단위 테스트
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_trailing_slash_handling():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # trailing slash 없는 버전
        response = await client.post("/api/v1/users", json={"name": "test"})
        assert response.status_code == 200

        # trailing slash 있는 버전
        response = await client.post("/api/v1/users/", json={"name": "test"})
        assert response.status_code == 200
```

### 2. Smoke Test Script
```bash
#!/bin/bash
# scripts/test-trailing-slash.sh

endpoints=(
  "POST /auth/login"
  "POST /users"
  "PUT /users/1"
  "PATCH /settings/profile"
)

for endpoint in "${endpoints[@]}"; do
  method=$(echo $endpoint | cut -d' ' -f1)
  path=$(echo $endpoint | cut -d' ' -f2)

  # Test without trailing slash
  echo -n "Testing $method $path ... "
  curl -s -X $method "http://localhost:8000/api/v1$path" > /dev/null
  [ $? -eq 0 ] && echo "✅" || echo "❌"

  # Test with trailing slash
  echo -n "Testing $method $path/ ... "
  curl -s -X $method "http://localhost:8000/api/v1$path/" > /dev/null
  [ $? -eq 0 ] && echo "✅" || echo "❌"
done
```

## 🔄 마이그레이션 가이드

### 기존 코드 업데이트
1. **찾기**: POST/PUT/PATCH 엔드포인트 식별
   ```bash
   grep -r "@router\.\(post\|put\|patch\)" api/
   ```

2. **수정**: trailing slash 버전 추가
   ```python
   # Before
   @router.post("/endpoint")
   def handler():
       pass

   # After
   @router.post("/endpoint")
   @router.post("/endpoint/")
   def handler():
       pass
   ```

3. **검증**: 테스트 실행
   ```bash
   python scripts/test-trailing-slash.py
   ```

### 점진적 마이그레이션
```python
# Phase 1: 로깅만 추가
@app.middleware("http")
async def log_trailing_slash(request: Request, call_next):
    if request.method in ["POST", "PUT", "PATCH"]:
        if request.url.path.endswith("/") and not any(
            route.path == request.url.path for route in app.routes
        ):
            logger.warning(f"Missing trailing slash route: {request.url.path}")
    return await call_next(request)

# Phase 2: 자동 리다이렉트 (임시)
# redirect_slashes=True 설정 고려

# Phase 3: 완전 마이그레이션
# 모든 엔드포인트에 두 버전 정의
```

## 🤔 FAQ

### Q: 왜 redirect_slashes=False를 사용하나요?
A: 명시적인 라우트 정의로 예측 가능한 동작을 보장하고, 307 리다이렉트로 인한 성능 오버헤드를 방지합니다.

### Q: GET 요청도 두 버전이 필요한가요?
A: 아니요. GET/DELETE는 프로젝트 표준에 따라 일관성 있게 하나만 정의하면 됩니다.

### Q: 프론트엔드 interceptor를 제거하면 안 되나요?
A: 가능하지만, 기존 코드와의 호환성을 위해 백엔드에서 두 버전을 지원하는 것이 안전합니다.

## 🔗 관련 문서
- [Backend 개발 가이드](../backend/CLAUDE.md)
- [배포 체크리스트](./deployment-checklist.md)
- [API 문서](./API_DOCUMENTATION.md)

## 📊 체크리스트
- [ ] 모든 POST 엔드포인트에 trailing slash 버전 추가
- [ ] 모든 PUT 엔드포인트에 trailing slash 버전 추가
- [ ] 모든 PATCH 엔드포인트에 trailing slash 버전 추가
- [ ] GET/DELETE 엔드포인트 일관성 확인
- [ ] 테스트 코드 업데이트
- [ ] API 문서 업데이트
- [ ] 배포 전 smoke test 실행

---

*이 가이드는 2025-06-22 trailing slash 404 에러 대응을 위해 작성되었습니다.*
