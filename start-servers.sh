#!/bin/bash

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}AIBIO 센터 관리 시스템 서버 시작${NC}"
echo "================================"

# 기존 프로세스 정리
echo -e "${YELLOW}기존 서버 프로세스 종료 중...${NC}"
pkill -f "python.*main.py"
pkill -f vite

# 잠시 대기
sleep 2

# 백엔드 서버 시작
echo -e "${YELLOW}백엔드 서버 시작 중...${NC}"
cd /Users/vibetj/coding/center/backend
python main.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

# 프론트엔드 서버 시작
echo -e "${YELLOW}프론트엔드 서버 시작 중...${NC}"
cd /Users/vibetj/coding/center/frontend
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!

# 서버 시작 대기
echo -e "${YELLOW}서버 시작 대기 중...${NC}"
sleep 5

# 상태 확인
echo ""
echo -e "${YELLOW}서버 상태 확인:${NC}"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5173 | grep -q "200"; then
    echo -e "${GREEN}✅ 프론트엔드 서버: 정상 (http://localhost:5173)${NC}"
else
    echo -e "${RED}❌ 프론트엔드 서버: 실패${NC}"
    tail -n 20 /tmp/frontend.log
fi

if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs | grep -q "200"; then
    echo -e "${GREEN}✅ 백엔드 서버: 정상 (http://localhost:8000)${NC}"
else
    echo -e "${RED}❌ 백엔드 서버: 실패${NC}"
    tail -n 20 /tmp/backend.log
fi

echo ""
echo -e "${YELLOW}프로세스 정보:${NC}"
echo "백엔드 PID: $BACKEND_PID"
echo "프론트엔드 PID: $FRONTEND_PID"
echo ""
echo -e "${YELLOW}로그 확인 명령어:${NC}"
echo "백엔드: tail -f /tmp/backend.log"
echo "프론트엔드: tail -f /tmp/frontend.log"
echo ""
echo -e "${GREEN}서버가 시작되었습니다!${NC}"
echo -e "${GREEN}브라우저에서 http://localhost:5173 으로 접속하세요.${NC}"