# Railway 환경변수 체크리스트

Railway Variables 탭에서 다음 환경변수들이 정확히 설정되어 있는지 확인하세요:

```env
# 1. 데이터베이스 (YOUR-PASSWORD를 실제 Supabase 비밀번호로 교체)
DATABASE_URL=postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:[YOUR-PASSWORD]@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres

# 2. JWT 인증
JWT_SECRET_KEY=zW8CY0kShUKFIOZugtEq04BNtEFbTOpgWBXJlKsish8
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 3. CORS 설정 (가장 중요!)
CORS_ORIGINS=https://center-ten.vercel.app

# 4. 환경 설정
PYTHON_ENV=production
LOG_LEVEL=INFO
```

## 확인 방법:

1. Railway 대시보드 → center 프로젝트
2. Variables 탭
3. Raw Editor 토글 ON
4. 위 환경변수들이 모두 있는지 확인

특히 CORS_ORIGINS가 정확한지 확인!

## 테스트:

1. https://center-production-1421.up.railway.app/health 접속
   - {"status": "healthy"} 응답이 와야 함

2. https://center-production-1421.up.railway.app/docs 접속
   - FastAPI 문서가 보여야 함

3. 문서에서 /api/v1/auth/login 엔드포인트 테스트
   - email: admin@aibio.kr
   - password: admin123