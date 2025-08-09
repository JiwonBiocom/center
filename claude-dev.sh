#!/bin/bash

# 🚀 Claude 개발 모드 (권한 체크 생략 + Browser MCP)
# 사용법: ./claude-dev.sh

echo "🚀 Claude 개발 모드 시작..."

claude chat --dangerously-skip-permissions --mcp-config .mcp.json --allowedTools "mcp__browsermcp"
