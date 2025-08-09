# Gmail 이메일 알림 빠른 설정 가이드

## 필요한 정보
1. Google 계정 (Gmail 발송용)
2. OAuth 2.0 클라이언트 JSON 파일

## 단계별 설정

### 1단계: Google Cloud Console에서 OAuth 클라이언트 생성

1. **Google Cloud Console 접속**
   - https://console.cloud.google.com/

2. **프로젝트 생성/선택**
   - 상단 드롭다운에서 "새 프로젝트" 클릭
   - 프로젝트 이름: "AIBIO-Notifications" (예시)

3. **Gmail API 활성화**
   - 좌측 메뉴 → "API 및 서비스" → "사용 설정된 API"
   - "+ API 및 서비스 사용 설정" 클릭
   - "Gmail API" 검색 → 선택 → "사용" 클릭

4. **OAuth 동의 화면 설정**
   - 좌측 메뉴 → "OAuth 동의 화면"
   - 사용자 유형: "외부" 선택
   - 앱 정보 입력:
     - 앱 이름: "AIBIO Health Monitor"
     - 사용자 지원 이메일: 본인 이메일
     - 개발자 연락처: 본인 이메일
   - 범위 추가: gmail.send
   - 테스트 사용자 추가: 본인 이메일

5. **OAuth 2.0 클라이언트 ID 생성**
   - 좌측 메뉴 → "사용자 인증 정보"
   - "+ 사용자 인증 정보 만들기" → "OAuth 클라이언트 ID"
   - 애플리케이션 유형: **"데스크톱 앱"**
   - 이름: "AIBIO Email Client"
   - "만들기" 클릭
   - **JSON 다운로드** 클릭 (중요!)

### 2단계: 로컬 환경 설정

```bash
# 1. config 디렉토리 생성
cd /Users/vibetj/coding/center
mkdir -p config

# 2. 다운로드한 JSON 파일 복사 (파일명 예시)
cp ~/Downloads/client_secret_*.json config/gmail_credentials.json

# 3. 패키지 설치
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# 4. Gmail OAuth 설정 실행
python scripts/setup_gmail_oauth.py
```

### 3단계: 브라우저 인증
1. 스크립트 실행 시 브라우저가 자동으로 열림
2. Google 계정으로 로그인
3. "이 앱은 Google에서 확인하지 않았습니다" 경고 시:
   - "고급" 클릭
   - "AIBIO Health Monitor(으)로 이동" 클릭
4. 권한 요청 승인 (Gmail 전송 권한)

### 4단계: 테스트
```bash
# 이메일 발송 테스트
python scripts/test_email_alert.py

# 본인 이메일 입력하여 테스트
```

### 5단계: GitHub Actions 설정 (선택사항)

1. 생성된 `config/gmail_token.json` 파일 내용 복사
2. GitHub 저장소 → Settings → Secrets → Actions
3. 새 시크릿 추가:
   - Name: `GMAIL_TOKEN`
   - Value: 복사한 JSON 내용 전체
4. 추가 시크릿:
   - Name: `ALERT_EMAIL_RECIPIENTS`
   - Value: `알림받을이메일@gmail.com,추가이메일@company.com`

## 자주 묻는 질문

### Q: "이 앱은 Google에서 확인하지 않았습니다" 경고가 나옵니다
A: 개발/테스트 단계이므로 정상입니다. "고급" → "앱으로 이동" 클릭하세요.

### Q: 어떤 Gmail 계정을 사용해야 하나요?
A: 시스템 알림 전용 Gmail 계정을 만들거나, 기존 계정을 사용할 수 있습니다.

### Q: 토큰이 만료되면 어떻게 하나요?
A: `rm config/gmail_token.json` 후 다시 설정 스크립트를 실행하세요.

## 보안 주의사항
- `config/` 폴더는 절대 Git에 커밋하지 마세요
- 프로덕션 환경에서는 서비스 계정 사용을 권장합니다

## 다음 단계
설정이 완료되면:
1. Health check 실패 시 자동 이메일 발송
2. DB 스키마 변경 시 자동 이메일 발송
3. 필요시 커스텀 알림 발송 가능