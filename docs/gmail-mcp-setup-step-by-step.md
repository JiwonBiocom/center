# Gmail MCP Server 설정 가이드 (단계별)

## 📋 준비사항
- Google 계정
- Claude Desktop 앱
- 터미널 접근

## 🔧 Step 1: Google Cloud Console 설정

### 1.1 프로젝트 생성
1. [Google Cloud Console](https://console.cloud.google.com) 접속
2. 상단의 프로젝트 선택 드롭다운 클릭
3. "새 프로젝트" 클릭
4. 프로젝트 이름: "AIBIO-MCP-Email" (또는 원하는 이름)
5. "만들기" 클릭

### 1.2 Gmail API 활성화
1. 왼쪽 메뉴에서 "API 및 서비스" → "라이브러리" 클릭
2. "Gmail API" 검색
3. Gmail API 선택 후 "사용" 버튼 클릭

### 1.3 OAuth 2.0 클라이언트 생성
1. 왼쪽 메뉴에서 "API 및 서비스" → "사용자 인증 정보" 클릭
2. 상단의 "+ 사용자 인증 정보 만들기" → "OAuth 클라이언트 ID" 선택
3. 애플리케이션 유형: "데스크톱 앱" 선택
4. 이름: "Claude MCP Gmail Client"
5. "만들기" 클릭
6. 생성된 클라이언트 ID와 시크릿이 표시됨
7. "JSON 다운로드" 버튼 클릭하여 `gcp-oauth.keys.json` 파일 다운로드

## 🚀 Step 2: Gmail MCP Server 설치

터미널을 열고 다음 명령어를 순서대로 실행:

```bash
# 1. Gmail MCP 폴더 생성
mkdir -p ~/.gmail-mcp

# 2. 다운로드한 OAuth 파일을 해당 폴더로 이동
# (Downloads 폴더에 다운로드했다고 가정)
mv ~/Downloads/client_secret_*.json ~/.gmail-mcp/gcp-oauth.keys.json

# 또는 수동으로 파일명 변경 후 이동
# mv ~/Downloads/[다운로드한파일명].json ~/.gmail-mcp/gcp-oauth.keys.json

# 3. 파일이 제대로 이동되었는지 확인
ls -la ~/.gmail-mcp/
# gcp-oauth.keys.json 파일이 보여야 함

# 4. Gmail MCP Server 인증 실행
npx @gongrzhe/server-gmail-autoauth-mcp auth
```

인증 실행 시:
- 브라우저가 자동으로 열립니다
- Google 계정으로 로그인
- "이 앱이 Google 계정에 액세스하도록 허용" 페이지에서 "허용" 클릭
- "인증이 완료되었습니다" 메시지가 나타나면 성공

## 📝 Step 3: Claude Desktop 설정

### 3.1 설정 파일 위치 찾기
```bash
# macOS에서 Claude Desktop 설정 폴더 생성 (없는 경우)
mkdir -p ~/Library/Application\ Support/Claude

# 설정 파일 생성/편집
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### 3.2 설정 파일 내용 작성
다음 내용을 복사하여 붙여넣기:

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

### 3.3 파일 저장
- `Ctrl + O` 눌러서 저장
- `Enter` 눌러서 확인
- `Ctrl + X` 눌러서 나가기

## 🔄 Step 4: Claude Desktop 재시작

1. Claude Desktop 완전히 종료
   - 상단 메뉴바의 Claude 아이콘 클릭
   - "Quit Claude" 선택

2. Claude Desktop 다시 실행

3. 설정 확인
   - Claude Desktop에서 새 대화 시작
   - "Gmail을 통해 테스트 이메일을 보낼 수 있나요?" 라고 물어보기

## ✅ Step 5: 테스트

Claude Desktop에서 다음과 같이 요청해보세요:

```
"Gmail을 사용해서 ej8641@gmail.com으로 테스트 이메일을 보내주세요. 
제목은 'MCP Gmail 테스트'로 하고, 
본문에는 'Gmail MCP Server가 정상적으로 작동합니다!'라고 적어주세요."
```

## 🛠️ 문제 해결

### 1. "command not found: npx" 오류
```bash
# Node.js가 설치되어 있지 않은 경우
brew install node
```

### 2. 인증 오류
```bash
# 기존 토큰 삭제 후 재인증
rm -rf ~/.gmail-mcp/tokens
npx @gongrzhe/server-gmail-autoauth-mcp auth
```

### 3. Claude Desktop에서 Gmail을 인식하지 못하는 경우
- 설정 파일 경로가 올바른지 확인
- JSON 문법 오류가 없는지 확인 (쉼표, 중괄호 등)
- Claude Desktop 완전히 종료 후 재시작

### 4. 권한 오류
- Google 계정의 보안 설정에서 "보안 수준이 낮은 앱의 액세스" 허용
- 또는 2단계 인증 사용 시 앱 비밀번호 생성

## 🎯 설정 완료 후 사용 예시

1. **보고서 발송**
   ```
   "Gmail을 통해 ej8641@gmail.com으로 AI 건강분석 보고서를 보내주세요."
   ```

2. **첨부파일 포함**
   ```
   "Gmail로 보고서를 보내는데, /Users/vibetj/coding/center/docs/ai-health-analysis-report.html 파일을 첨부해주세요."
   ```

3. **이메일 검색**
   ```
   "Gmail에서 최근 받은 이메일 중 '보고서'가 포함된 이메일을 찾아주세요."
   ```

## 📌 참고사항

- Gmail MCP Server는 OAuth 2.0을 사용하여 안전하게 인증됩니다
- 토큰은 `~/.gmail-mcp/tokens/` 폴더에 저장됩니다
- 필요한 권한: Gmail 읽기/쓰기 권한
- 하루 발송 한도: Gmail 일반 계정은 500통/일

설정 중 문제가 있으면 각 단계에서 알려주세요!