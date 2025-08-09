# 🧪 테스트 규칙 및 가이드라인

> 작성일: 2025-06-21  
> 최종 수정: 2025-06-21  
> 프로젝트: AIBIO 센터 관리 시스템

## 📋 목차
1. [콘솔 메시지 체크 규칙](#콘솔-메시지-체크-규칙)
2. [API 테스트 규칙](#api-테스트-규칙)
3. [로그인 필수 페이지 테스트](#로그인-필수-페이지-테스트)
4. [Playwright 테스트 작성 규칙](#playwright-테스트-작성-규칙)
5. [테스트 실패 시 대응](#테스트-실패-시-대응)

## 콘솔 메시지 체크 규칙

### ❌ 잘못된 방법
```bash
# 메인 페이지만 체크하는 스크립트
python scripts/quick_console_check.py https://center-ten.vercel.app

# 문제점:
# 1. 로그인 페이지의 콘솔만 확인
# 2. 인증이 필요한 페이지 접근 불가
# 3. 특정 페이지의 에러를 놓칠 수 있음
```

### ✅ 올바른 방법
```bash
# 특정 페이지의 콘솔을 정확히 체크
python scripts/check_specific_page_console.py /customers

# 또는 전체 시스템 체크
python scripts/check_full_system.py
```

### 필수 체크 항목
1. **로그인 수행**: 인증이 필요한 페이지는 반드시 로그인 후 테스트
2. **페이지 이동**: 테스트할 페이지로 직접 이동
3. **네트워크 대기**: `networkidle` 상태까지 대기
4. **모든 메시지 수집**: error, warning, log 모두 확인

### 콘솔 체크 템플릿
```python
async def check_console_properly(page_path):
    # 1. 로그인
    await page.goto("https://center-ten.vercel.app/login")
    await page.fill('input[type="email"]', "admin@aibio.com")
    await page.fill('input[type="password"]', "admin123")
    await page.click('button[type="submit"]')
    await page.wait_for_url("**/")
    
    # 2. 콘솔 메시지 초기화 (로그인 페이지 메시지 제외)
    console_messages.clear()
    
    # 3. 테스트할 페이지로 이동
    await page.goto(f"https://center-ten.vercel.app{page_path}")
    await page.wait_for_load_state("networkidle")
    
    # 4. 에러 분석
    errors = [msg for msg in console_messages if msg["type"] == "error"]
```

## API 테스트 규칙

### 엔드포인트 테스트
1. **슬래시(/) 확인**: FastAPI는 trailing slash에 민감
   ```bash
   # 잘못된 예
   curl https://api.example.com/api/v1/customers
   
   # 올바른 예  
   curl https://api.example.com/api/v1/customers/
   ```

2. **인증 토큰 포함**: 보호된 엔드포인트는 토큰 필수
   ```bash
   curl -H "Authorization: Bearer $TOKEN" https://api.example.com/api/v1/customers/
   ```

3. **응답 상태 확인**: 200, 404, 500 등 상태 코드 확인

## 로그인 필수 페이지 테스트

### 테스트해야 할 주요 페이지
- `/` (대시보드)
- `/customers` (고객관리)
- `/services` (서비스관리)
- `/payments` (결제관리)
- `/notifications` (알림)
- `/reports` (리포트)
- `/settings` (설정)

### 각 페이지별 체크리스트
- [ ] 페이지 로드 성공
- [ ] 콘솔 에러 없음
- [ ] API 호출 성공 (404 없음)
- [ ] 데이터 표시 또는 빈 상태 메시지
- [ ] UI 요소 정상 렌더링

## Playwright 테스트 작성 규칙

### 1. 헤드리스 모드 사용
```python
browser = await p.chromium.launch(headless=True)
```

### 2. 타임아웃 설정
```python
# 페이지 로드 타임아웃
await page.goto(url, timeout=30000)  # 30초

# 요소 대기 타임아웃
await page.wait_for_selector('button', timeout=5000)  # 5초
```

### 3. 에러 처리
```python
try:
    await page.goto(url)
except Exception as e:
    print(f"❌ 페이지 로드 실패: {e}")
    # 스크린샷 저장
    await page.screenshot(path="error.png")
```

### 4. 스크린샷 활용
```python
# 테스트 실패 시 스크린샷
if errors:
    await page.screenshot(path=f"error_{page_path.replace('/', '_')}.png")
```

## 테스트 실패 시 대응

### 1. 즉시 확인 사항
- **네트워크 에러**: API 서버가 실행 중인가?
- **404 에러**: 엔드포인트 경로가 올바른가?
- **500 에러**: 백엔드 로그 확인
- **CORS 에러**: CORS 설정 확인

### 2. 디버깅 도구 활용
```bash
# Railway 로그 확인
railway logs -f

# API 문서 확인
curl https://api.example.com/docs

# 네트워크 요청 추적
python scripts/check_frontend_api.py
```

### 3. 문제 보고 형식
```markdown
## 테스트 실패 보고

### 실패한 테스트
- 페이지: /customers
- 시간: 2025-06-21 10:30

### 에러 내용
- 유형: 404 Not Found
- API: GET /api/v1/customers
- 콘솔 메시지: [전체 에러 메시지]

### 시도한 해결책
1. API 엔드포인트 확인
2. 인증 토큰 확인
3. CORS 설정 확인

### 근본 원인
- API 경로에 trailing slash 누락
```

## 테스트 우선순위

### 1. Critical (즉시 수정)
- 로그인 불가
- API 500 에러
- 데이터 손실 가능성

### 2. High (당일 수정)
- 404 에러
- 주요 기능 작동 불가
- 콘솔 에러

### 3. Medium (1주 내 수정)
- 콘솔 경고
- UI 깨짐
- 성능 이슈

### 4. Low (여유 있을 때)
- 코드 스타일
- 최적화
- 리팩토링

## 자동화된 테스트 스크립트

### 전체 시스템 체크
```bash
# 모든 페이지와 API 체크
python scripts/check_full_system.py
```

### 특정 페이지 체크
```bash
# 고객관리 페이지만 체크
python scripts/check_specific_page_console.py /customers
```

### 로그인 플로우 체크
```bash
# 로그인 및 대시보드 접근
python scripts/test_login_flow.py
```

## 베스트 프랙티스

### 1. 테스트 전 환경 확인
```bash
# 백엔드 상태
curl https://api.example.com/health

# 프론트엔드 빌드
echo $VITE_API_URL
```

### 2. 병렬 테스트 주의
- Playwright는 병렬 실행 시 리소스 많이 사용
- 순차적으로 실행 권장

### 3. 테스트 데이터 관리
- 테스트용 계정 사용
- 프로덕션 데이터 건드리지 않기
- 테스트 후 정리

### 4. 지속적인 모니터링
```bash
# 5분마다 헬스체크
watch -n 300 'curl -s https://api.example.com/health'
```

---

*이 문서는 AIBIO 센터 관리 시스템의 테스트 규칙을 정의합니다.*
*테스트 시 반드시 이 가이드라인을 따라주세요.*