# Railway 배포 가이드

## 필수 환경 변수 설정

Railway 대시보드에서 다음 환경 변수를 설정해야 합니다:

### 1. 데이터베이스 (필수)
```
DATABASE_URL=postgresql://user:password@host:port/database
```

### 2. Supabase (필수)
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### 3. 보안 (필수)
```
SECRET_KEY=your-secure-random-secret-key
```

### 4. CORS 설정
```
BACKEND_CORS_ORIGINS=["https://your-frontend-domain.com"]
```

### 5. 선택 사항
- Kakao API 키 (SMS 전송 시 필요)
- Aligo API 키 (SMS 전송 시 필요)

## 배포 프로세스

1. 환경 변수 설정
2. Git push 시 자동 배포
3. 빌드 로그 확인
4. Health check: `/health` 엔드포인트로 확인

## 문제 해결

### Python path 에러
- `main.py` 상단에 sys.path 추가됨
- 자동으로 backend 디렉토리를 Python path에 추가

### 환경 변수 에러
- Railway 대시보드에서 모든 필수 환경 변수 확인
- 특히 DATABASE_URL과 SUPABASE 관련 키 확인