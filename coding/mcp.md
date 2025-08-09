# 🌐 MCP (Model Context Protocol) 설정 및 사용 가이드

## 📋 현재 설정 상태

### ✅ 설정 완료된 MCP 서버들
- **Browser MCP**: Version 0.1.3 - 웹 브라우저 자동화 ✅ **정상 작동**
- **Notion MCP**: Notion API 연동 (Claude Desktop 설정)

### 📁 설정 파일 위치
- **프로젝트별 설정**: `.mcp.json` (프로젝트 루트)
- **전역 설정**: `~/Library/Application Support/Claude/claude_desktop_config.json`

## 🌐 Browser MCP 사용법

### 🎯 빠른 시작
```bash
# 대화형 모드로 브라우저 제어 시작
claude chat --mcp-config .mcp.json --allowedTools "mcp__browsermcp"
```

### ⚠️ 중요: 올바른 사용법
- **대화형 모드에서만 작동**: `--print` 옵션과 함께 사용하지 마세요
- **슬래시 명령 사용**: 대화형 모드 내에서 `/mcp__browsermcp__` 명령 사용
- **단계별 진행**: 한 번에 하나의 명령씩 실행

### 🔧 사용 가능한 브라우저 명령어

| 명령어 | 기능 | 예시 |
|--------|------|------|
| `browser_navigate` | 페이지 이동 | `/mcp__browsermcp__browser_navigate https://example.com` |
| `browser_click` | 요소 클릭 | `/mcp__browsermcp__browser_click "button.submit"` |
| `browser_type` | 텍스트 입력 | `/mcp__browsermcp__browser_type "#email" "test@example.com"` |
| `browser_scroll` | 페이지 스크롤 | `/mcp__browsermcp__browser_scroll "down"` |
| `browser_screenshot` | 스크린샷 캡처 | `/mcp__browsermcp__browser_screenshot` |
| `browser_get_page_content` | 페이지 내용 가져오기 | `/mcp__browsermcp__browser_get_page_content` |
| `browser_wait_for_element` | 요소 대기 | `/mcp__browsermcp__browser_wait_for_element ".loading"` |
| `browser_execute_script` | 자바스크립트 실행 | `/mcp__browsermcp__browser_execute_script "window.scrollTo(0, 0)"` |

### 💡 실전 활용 시나리오

#### 1. 웹사이트 UI 테스트
**대화형 모드에서 단계별로 실행:**
```bash
# 1단계: Claude CLI 시작
claude chat --mcp-config .mcp.json --allowedTools "mcp__browsermcp"

# 2단계: 대화형 모드에서 다음 명령들을 순서대로 입력
/mcp__browsermcp__browser_navigate http://localhost:3000/login
/mcp__browsermcp__browser_type "#username" "admin"
/mcp__browsermcp__browser_type "#password" "password123"
/mcp__browsermcp__browser_click "button[type='submit']"
/mcp__browsermcp__browser_screenshot
```

#### 2. 데이터 스크래핑
```bash
# 대화형 모드에서:
/mcp__browsermcp__browser_navigate https://example.com/data
/mcp__browsermcp__browser_get_page_content
/mcp__browsermcp__browser_execute_script "document.querySelector('.data-table').innerText"
```

#### 3. 성능 모니터링
```bash
# 대화형 모드에서:
/mcp__browsermcp__browser_execute_script "performance.now()"
/mcp__browsermcp__browser_navigate https://myapp.com
/mcp__browsermcp__browser_execute_script "performance.now()"
```

#### 4. AIBIO 센터 시스템 테스트 예시
```bash
# 대화형 모드에서 단계별로:
/mcp__browsermcp__browser_navigate https://www.google.com
/mcp__browsermcp__browser_type "input[name='q']" "AIBIO 바이오해킹 센터"
/mcp__browsermcp__browser_click "input[type='submit']"
/mcp__browsermcp__browser_screenshot

# 로컬 개발 서버 테스트
/mcp__browsermcp__browser_navigate http://localhost:3000
/mcp__browsermcp__browser_screenshot
/mcp__browsermcp__browser_click "nav a[href='/customers']"
```

## ⚙️ 고급 설정

### CI/CD 파이프라인용 Headless 모드
`.mcp.json`에서 환경변수 수정:
```json
{
  "mcpServers": {
    "browsermcp": {
      "command": "npx",
      "args": ["-y", "@browsermcp/mcp"],
      "env": {
        "PLAYWRIGHT_HEADLESS": "true"
      }
    }
  },
  "allowedTools": [
    "mcp__browsermcp__browser_navigate",
    "mcp__browsermcp__browser_click",
    "mcp__browsermcp__browser_type",
    "mcp__browsermcp__browser_scroll",
    "mcp__browsermcp__browser_screenshot",
    "mcp__browsermcp__browser_get_page_content",
    "mcp__browsermcp__browser_wait_for_element",
    "mcp__browsermcp__browser_execute_script"
  ]
}
```

### 다중 탭 관리
- 각 탭에 고유 ID 할당하여 여러 페이지 동시 제어 가능
- Browser MCP 1.2.x 이상에서 multi-tab API 지원

## 🛡️ 보안 및 주의사항

- `.mcp.json`은 민감한 설정을 포함할 수 있으므로 git에 커밋하지 않음 (`.gitignore`에 추가됨)
- 프로덕션 환경에서는 신뢰할 수 있는 도메인으로만 제한 권장
- **대화형 모드 필수**: Cursor/IDE 환경에서는 MCP 도구가 직접 활성화되지 않음
- Claude CLI를 통해 별도 세션에서 사용 필수

## 🐛 문제해결

### ✅ 해결됨: "browsermcp ✘ failed" 에러
**문제**: MCP 서버가 시작되지 않음
**해결**: `.mcp.json`에 `-y` 플래그 추가
```json
"args": ["-y", "@browsermcp/mcp"]  // ← -y 플래그 필수!
```

### 브라우저가 열리지 않는 경우:
```bash
# Playwright 브라우저 재설치
npx playwright install chromium
```

### MCP 연결 오류 시:
```bash
# Browser MCP 패키지 재설치
npm uninstall -g @browsermcp/mcp
npm install -g @browsermcp/mcp

# 또는 최신 버전 설치
npx @browsermcp/mcp@latest
```

### Claude CLI 권한 오류 시:
```bash
# allowedTools 설정 확인
claude chat --mcp-config .mcp.json --allowedTools "mcp__browsermcp" --help
```

### 슬래시 명령이 작동하지 않는 경우:
- `--print` 옵션 사용하지 말고 대화형 모드 사용
- 명령어 앞에 `/` 기호 반드시 포함
- 한 번에 하나의 명령만 실행

## 📚 추가 MCP 서버 설정

### 다른 MCP 서버 추가하기
```json
{
  "mcpServers": {
    "browsermcp": {
      "command": "npx",
      "args": ["-y", "@browsermcp/mcp"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/dir"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token_here"
      }
    }
  }
}
```

---
**🚀 MCP를 활용한 자동화로 개발 생산성을 높이세요!**
