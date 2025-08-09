# Gmail MCP Server 설정 가이드

## 개요
MCP(Model Context Protocol)를 사용하여 Claude Desktop에서 직접 이메일을 보낼 수 있습니다.

## 설치 방법

### 1. Gmail API 설정
1. [Google Cloud Console](https://console.cloud.google.com)에 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. Gmail API 활성화
4. OAuth 2.0 클라이언트 ID 생성
5. `gcp-oauth.keys.json` 파일 다운로드

### 2. Gmail MCP Server 설치

```bash
# 인증 파일 설정
mkdir -p ~/.gmail-mcp
mv ~/Downloads/gcp-oauth.keys.json ~/.gmail-mcp/

# 인증 실행
npx @gongrzhe/server-gmail-autoauth-mcp auth
```

### 3. Claude Desktop 설정

Claude Desktop의 설정 파일에 다음 내용 추가:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "gmail": {
      "command": "npx",
      "args": [
        "@gongrzhe/server-gmail-autoauth-mcp"
      ]
    }
  }
}
```

### 4. Claude Desktop 재시작

설정 후 Claude Desktop을 재시작하면 Gmail 기능을 사용할 수 있습니다.

## 사용 예시

### 이메일 발송
```
"Gmail을 통해 ej8641@gmail.com으로 AI 건강분석 보고서를 보내주세요. 
첨부파일로 ai-health-analysis-report.html과 ai-health-analysis-report.md를 포함해주세요."
```

### 이메일 검색
```
"최근 일주일 간 받은 이메일 중 '보고서'가 포함된 이메일을 찾아주세요."
```

## 주요 기능

1. **이메일 발송**: 제목, 본문, 첨부파일, 수신자 지정
2. **이메일 조회**: ID로 특정 이메일 읽기
3. **이메일 검색**: 제목, 발신자, 날짜 범위로 검색
4. **라벨 관리**: Gmail 라벨 생성, 수정, 삭제
5. **배치 처리**: 최대 50개 이메일 동시 처리

## 보안 주의사항

- OAuth 인증을 사용하여 안전하게 Gmail에 접근
- 인증 토큰은 로컬에 안전하게 저장됨
- 필요한 권한만 요청 (이메일 읽기/쓰기)

## 문제 해결

1. **인증 오류**: `~/.gmail-mcp/` 폴더의 토큰 파일 삭제 후 재인증
2. **연결 오류**: Claude Desktop 재시작
3. **권한 오류**: Google 계정에서 앱 권한 확인

## 대안: 간단한 이메일 발송

Gmail 설정이 복잡하다면, 더 간단한 SMTP 기반 MCP 서버를 만들 수도 있습니다:

```python
# simple-email-mcp-server.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to, subject, body, smtp_config):
    msg = MIMEMultipart()
    msg['From'] = smtp_config['from']
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))
    
    with smtplib.SMTP(smtp_config['server'], smtp_config['port']) as server:
        server.starttls()
        server.login(smtp_config['user'], smtp_config['password'])
        server.send_message(msg)
```

이 방법은 Gmail API보다 설정이 간단하지만 기능이 제한적입니다.