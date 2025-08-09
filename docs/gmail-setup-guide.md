# Gmail 이메일 알림 설정 가이드

## 개요
AIBIO 시스템은 Health Check 실패, 스키마 변경 등의 중요 이벤트를 Gmail을 통해 이메일로 알려줍니다.

## 설정 단계

### 1. Google Cloud Console 설정

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. **API 및 서비스** > **사용 설정된 API** 클릭
4. **+ API 및 서비스 사용 설정** 클릭
5. "Gmail API" 검색 후 사용 설정

### 2. OAuth2 인증 정보 생성

1. **API 및 서비스** > **사용자 인증 정보** 이동
2. **+ 사용자 인증 정보 만들기** > **OAuth 클라이언트 ID** 선택
3. 애플리케이션 유형: **데스크톱 앱** 선택
4. 이름 입력 (예: "AIBIO Health Check")
5. **만들기** 클릭
6. JSON 파일 다운로드

### 3. 로컬 설정

```bash
# 1. config 디렉토리 생성
mkdir -p config

# 2. 다운로드한 JSON 파일을 복사
cp ~/Downloads/client_secret_*.json config/gmail_credentials.json

# 3. Gmail OAuth 설정 실행
python scripts/setup_gmail_oauth.py

# 4. 브라우저가 열리면 Gmail 계정으로 로그인하고 권한 승인
```

### 4. GitHub Secrets 설정

1. 생성된 `config/gmail_token.json` 파일의 내용을 복사
2. GitHub 저장소 > Settings > Secrets and variables > Actions
3. 다음 시크릿 추가:
   - `GMAIL_TOKEN`: gmail_token.json 파일 내용
   - `ALERT_EMAIL_RECIPIENTS`: 알림 받을 이메일 주소 (콤마 구분)
     ```
     example1@gmail.com,example2@company.com
     ```

## 사용 방법

### 수동 테스트
```bash
# 환경 변수 설정
export ALERT_EMAIL_RECIPIENTS="your-email@gmail.com"

# Health check 실행 (실패 시 이메일 발송)
python scripts/daily_health_check.py
```

### 프로그래밍 방식
```python
from scripts.email_notifier import EmailNotifier

# 초기화
notifier = EmailNotifier()

# 커스텀 이메일 발송
notifier.send_email(
    recipients=["user@example.com"],
    subject="테스트 알림",
    body="<h1>테스트</h1><p>이메일 알림 테스트입니다.</p>",
    is_html=True
)
```

## 알림 종류

### 1. Health Check 실패 알림
- **발송 조건**: 데이터베이스 또는 API 서버 비정상
- **발송 시간**: 매일 새벽 3시 (실패 시)
- **내용**: 시스템 상태, 실패 원인, 조치 사항

### 2. 스키마 변경 알림
- **발송 조건**: 프로덕션 DB 스키마 변경 감지
- **발송 시간**: Push/PR 시 즉시
- **내용**: 추가/삭제/변경된 테이블과 컬럼 정보

## 문제 해결

### "Gmail credentials file not found" 에러
```bash
# credentials 파일이 올바른 위치에 있는지 확인
ls -la config/gmail_credentials.json
```

### "Token has been expired or revoked" 에러
```bash
# 토큰 재생성
rm config/gmail_token.json
python scripts/setup_gmail_oauth.py
```

### 이메일이 도착하지 않는 경우
1. 스팸함 확인
2. `ALERT_EMAIL_RECIPIENTS` 환경 변수 확인
3. Gmail API 할당량 확인 (일일 250개 제한)

## 보안 주의사항

- `gmail_token.json` 파일은 절대 Git에 커밋하지 마세요
- `.gitignore`에 `config/` 디렉토리가 포함되어 있는지 확인
- 토큰이 노출된 경우 즉시 재생성

## 추가 기능 아이디어

1. **이메일 템플릿 커스터마이징**
2. **알림 우선순위 설정**
3. **일일 요약 리포트**
4. **Slack, Discord 등 다른 채널 연동**