# Middleware Documentation

## TrailingSlashMiddleware

### 개요
`TrailingSlashMiddleware`는 API 경로의 trailing slash 문제를 해결하기 위한 미들웨어입니다.

### 작동 방식
- **POST/PUT/PATCH 요청**: trailing slash가 있으면 자동으로 제거
- **GET/DELETE 요청**: 변경하지 않음 (캐시 키 일관성 유지)
- **예외 경로**: `/docs`, `/redoc`, `/ws`, `/upload` 등은 처리하지 않음

### 설정
```python
# main.py
from middleware.trailing_slash import TrailingSlashMiddleware
app.add_middleware(TrailingSlashMiddleware)
```

### 예시
```
POST /api/v1/auth/login/  → POST /api/v1/auth/login (미들웨어가 처리)
GET /api/v1/packages/     → GET /api/v1/packages/ (그대로 유지)
```

### 주의사항
- CORS 미들웨어보다 먼저 등록해야 합니다
- WebSocket이나 파일 업로드 경로는 자동으로 예외 처리됩니다

### 향후 계획
- 3단계에서 중복 라우트 제거 예정
- 모든 엔드포인트가 하나의 경로만 가지도록 정리
