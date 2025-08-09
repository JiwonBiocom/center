#!/bin/bash

echo "🌐 Browser MCP 시작 중..."
echo "프로젝트: $(basename $(pwd))"
echo ""

# MCP 설정 파일 확인
if [ ! -f ".mcp.json" ]; then
    echo "❌ .mcp.json 파일이 없습니다!"
    echo "현재 디렉토리: $(pwd)"
    exit 1
fi

echo "✅ MCP 설정 파일 확인됨"
echo ""
echo "🚀 Claude Chat with Browser MCP 시작..."
echo "대화형 모드에서 다음과 같은 명령어들을 사용하실 수 있습니다:"
echo ""
echo "  /mcp__browsermcp__browser_navigate https://www.google.com"
echo "  /mcp__browsermcp__browser_screenshot"
echo "  /mcp__browsermcp__browser_get_page_content"
echo ""
echo "종료하려면 Ctrl+C를 누르세요."
echo "════════════════════════════════════════════════════════"
echo ""

# Claude Chat 실행 (권한 체크 생략 + Browser MCP)
claude-dev

# Claude Chat 실행 (권한 체크 생략 + Browser MCP)
claude chat --dangerously-skip-permissions --mcp-config .mcp.json --allowedTools "mcp__browsermcp"
