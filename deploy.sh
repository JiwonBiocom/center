#!/bin/bash

# AIBIO Center 배포 스크립트
# 사용법: ./deploy.sh [production|staging]

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 환경 변수
ENVIRONMENT=${1:-staging}
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/backups/aibio_center/${TIMESTAMP}"

echo -e "${GREEN}🚀 AIBIO Center 배포 시작 - 환경: ${ENVIRONMENT}${NC}"

# 1. 환경 검증
if [ "$ENVIRONMENT" != "production" ] && [ "$ENVIRONMENT" != "staging" ]; then
    echo -e "${RED}❌ 오류: 올바른 환경을 선택하세요 (production 또는 staging)${NC}"
    exit 1
fi

# 2. 의존성 확인
echo -e "${YELLOW}📦 의존성 확인...${NC}"
command -v python3 >/dev/null 2>&1 || { echo -e "${RED}Python3가 필요합니다.${NC}" >&2; exit 1; }
command -v node >/dev/null 2>&1 || { echo -e "${RED}Node.js가 필요합니다.${NC}" >&2; exit 1; }
command -v pg_dump >/dev/null 2>&1 || { echo -e "${RED}PostgreSQL 클라이언트가 필요합니다.${NC}" >&2; exit 1; }

# 3. 백업
echo -e "${YELLOW}💾 데이터베이스 백업...${NC}"
mkdir -p "$BACKUP_DIR"
if [ "$ENVIRONMENT" = "production" ]; then
    source backend/.env
    pg_dump "$DATABASE_URL" > "$BACKUP_DIR/database_backup.sql"
    echo -e "${GREEN}✅ 데이터베이스 백업 완료: $BACKUP_DIR/database_backup.sql${NC}"
fi

# 4. 코드 업데이트
echo -e "${YELLOW}📥 최신 코드 가져오기...${NC}"
git pull origin main

# 5. 백엔드 배포
echo -e "${YELLOW}🔧 백엔드 배포...${NC}"
cd backend

# 가상환경 활성화
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 환경 파일 설정
if [ "$ENVIRONMENT" = "production" ]; then
    cp .env.production .env
else
    cp .env.staging .env
fi

# 데이터베이스 마이그레이션
echo -e "${YELLOW}🗄️ 데이터베이스 마이그레이션...${NC}"
python scripts/add_indexes.py

# 테스트 실행 (staging만)
if [ "$ENVIRONMENT" = "staging" ]; then
    echo -e "${YELLOW}🧪 테스트 실행...${NC}"
    pytest tests/ -v
fi

# 6. 프론트엔드 배포
echo -e "${YELLOW}🎨 프론트엔드 배포...${NC}"
cd ../frontend

# 의존성 설치
npm install

# 환경 파일 설정
if [ "$ENVIRONMENT" = "production" ]; then
    cp .env.production .env
else
    cp .env.staging .env
fi

# 빌드
npm run build

# 빌드 검증
if [ ! -d "dist" ]; then
    echo -e "${RED}❌ 프론트엔드 빌드 실패${NC}"
    exit 1
fi

# 7. 서비스 재시작
echo -e "${YELLOW}🔄 서비스 재시작...${NC}"
cd ../backend

if [ "$ENVIRONMENT" = "production" ]; then
    # Production: systemd 서비스 재시작
    sudo systemctl restart aibio-backend
    sudo systemctl restart nginx
    
    # 헬스체크
    sleep 5
    if curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 백엔드 서비스 정상 작동${NC}"
    else
        echo -e "${RED}❌ 백엔드 서비스 응답 없음${NC}"
        exit 1
    fi
else
    # Staging: PM2로 관리
    pm2 restart aibio-backend || pm2 start main.py --name aibio-backend --interpreter python3
    pm2 save
fi

# 8. 캐시 클리어
echo -e "${YELLOW}🧹 캐시 클리어...${NC}"
if command -v redis-cli >/dev/null 2>&1; then
    redis-cli FLUSHDB
    echo -e "${GREEN}✅ Redis 캐시 클리어 완료${NC}"
fi

# 9. 로그 로테이션
echo -e "${YELLOW}📋 로그 로테이션...${NC}"
if [ -f "/var/log/aibio/app.log" ]; then
    mv /var/log/aibio/app.log "/var/log/aibio/app.log.${TIMESTAMP}"
    touch /var/log/aibio/app.log
fi

# 10. 모니터링 알림
if [ "$ENVIRONMENT" = "production" ]; then
    echo -e "${YELLOW}📢 배포 알림 전송...${NC}"
    # Slack 또는 다른 알림 서비스에 배포 완료 알림
    # curl -X POST -H 'Content-type: application/json' \
    #      --data '{"text":"AIBIO Center 배포 완료 - '${ENVIRONMENT}'"}' \
    #      YOUR_SLACK_WEBHOOK_URL
fi

# 11. 최종 검증
echo -e "${YELLOW}✔️ 최종 검증...${NC}"
HEALTH_CHECK_URLS=(
    "http://localhost:8000/api/v1/health"
    "http://localhost:8000/api/v1/customers/count"
    "http://localhost:5173" # 프론트엔드
)

for url in "${HEALTH_CHECK_URLS[@]}"; do
    if curl -f "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $url - 정상${NC}"
    else
        echo -e "${YELLOW}⚠️ $url - 응답 없음${NC}"
    fi
done

echo -e "${GREEN}🎉 배포 완료!${NC}"
echo -e "${GREEN}환경: ${ENVIRONMENT}${NC}"
echo -e "${GREEN}시간: $(date)${NC}"
echo -e "${GREEN}백업 위치: ${BACKUP_DIR}${NC}"

# 배포 로그 기록
echo "[$(date)] 배포 완료 - 환경: ${ENVIRONMENT}" >> /var/log/aibio/deployments.log