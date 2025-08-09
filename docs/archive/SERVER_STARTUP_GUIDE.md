# 서버 실행 가이드

## 문제 상황 분석

### 실패한 방법들
1. **터미널 차단 방식**
   ```bash
   cd /Users/vibetj/coding/center/frontend && npm run dev
   ```
   - 문제: 명령어가 포그라운드에서 실행되어 터미널이 차단됨
   - 타임아웃 후에도 프로세스가 제대로 유지되지 않음

2. **백그라운드 실행 시도 (&)**
   ```bash
   cd /Users/vibetj/coding/center/backend && python main.py &
   ```
   - 백엔드는 이 방법으로 성공했지만 프론트엔드는 실패

### 성공한 방법
1. **백엔드 서버**
   ```bash
   cd /Users/vibetj/coding/center/backend && python main.py &
   ```
   - 백그라운드 실행으로 성공
   - 포트: 8000

2. **프론트엔드 서버**
   ```bash
   cd /Users/vibetj/coding/center/frontend && npm run dev > /tmp/vite.log 2>&1 &
   ```
   - 출력을 로그 파일로 리다이렉션하여 백그라운드 실행
   - 포트: 5173

## 권장 서버 실행 순서

### 1. 기존 프로세스 정리
```bash
# 기존 프로세스 확인
ps aux | grep -E "python.*main|node|vite" | grep -v grep

# 필요시 종료
pkill -f "python.*main.py"
pkill -f vite
```

### 2. 백엔드 서버 실행
```bash
cd /Users/vibetj/coding/center/backend
python main.py &

# 또는 uvicorn 직접 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
```

### 3. 프론트엔드 서버 실행
```bash
cd /Users/vibetj/coding/center/frontend
npm run dev > /tmp/vite.log 2>&1 &

# 로그 확인이 필요한 경우
tail -f /tmp/vite.log
```

### 4. 서버 상태 확인
```bash
# 3초 대기 후 확인
sleep 3

# 프론트엔드 확인
curl -s -o /dev/null -w "%{http_code}" http://localhost:5173
# 기대값: 200

# 백엔드 API 확인  
curl -s http://localhost:8000/api/v1/auth/me -w "\nHTTP Status: %{http_code}"
# 기대값: HTTP Status: 401 (인증 필요)
```

## 문제 해결 팁

### 포트 충돌 시
```bash
# 포트 사용 확인
lsof -i :5173
lsof -i :8000

# 강제 종료
kill -9 $(lsof -t -i:5173)
kill -9 $(lsof -t -i:8000)
```

### Vite 서버가 시작되지 않을 때
1. node_modules 재설치
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

2. 캐시 정리
   ```bash
   npm cache clean --force
   ```

3. 다른 포트로 실행
   ```bash
   npm run dev -- --port 3000
   ```

### 백엔드 서버 오류 시
1. 가상환경 확인
   ```bash
   cd backend
   source venv/bin/activate  # 또는 python -m venv venv 후 활성화
   pip install -r requirements.txt
   ```

2. 환경변수 확인
   ```bash
   cat .env  # DATABASE_URL, JWT_SECRET 등 필수 값 확인
   ```

## 자동 실행 스크립트

`start-servers.sh` 파일 생성:
```bash
#!/bin/bash

# 기존 프로세스 정리
echo "기존 서버 프로세스 종료 중..."
pkill -f "python.*main.py"
pkill -f vite

# 잠시 대기
sleep 2

# 백엔드 서버 시작
echo "백엔드 서버 시작 중..."
cd /Users/vibetj/coding/center/backend
python main.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

# 프론트엔드 서버 시작
echo "프론트엔드 서버 시작 중..."
cd /Users/vibetj/coding/center/frontend
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!

# 서버 시작 대기
echo "서버 시작 대기 중..."
sleep 5

# 상태 확인
echo "서버 상태 확인:"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5173 | grep -q "200"; then
    echo "✅ 프론트엔드 서버: 정상 (http://localhost:5173)"
else
    echo "❌ 프론트엔드 서버: 실패"
    tail -n 20 /tmp/frontend.log
fi

if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs | grep -q "200"; then
    echo "✅ 백엔드 서버: 정상 (http://localhost:8000)"
else
    echo "❌ 백엔드 서버: 실패"
    tail -n 20 /tmp/backend.log
fi

echo ""
echo "프로세스 ID:"
echo "백엔드: $BACKEND_PID"
echo "프론트엔드: $FRONTEND_PID"
echo ""
echo "로그 확인:"
echo "백엔드: tail -f /tmp/backend.log"
echo "프론트엔드: tail -f /tmp/frontend.log"
```

실행 권한 부여:
```bash
chmod +x start-servers.sh
```

## 주의사항

1. **Payment 모델 오류**: 현재 `Payment.status` 속성 관련 오류가 있지만 서버 실행에는 영향 없음
2. **타임아웃**: Claude Code에서는 2분 타임아웃이 있으므로 백그라운드 실행 필수
3. **로그 파일**: `/tmp` 디렉토리의 로그 파일은 시스템 재시작 시 삭제됨

## 문제 발생 시 체크리스트

- [ ] 포트가 이미 사용 중인가?
- [ ] 가상환경이 활성화되어 있는가? (백엔드)
- [ ] node_modules가 설치되어 있는가? (프론트엔드)  
- [ ] .env 파일이 올바르게 설정되어 있는가?
- [ ] 충분한 시간을 기다렸는가? (서버 시작에 3-5초 필요)