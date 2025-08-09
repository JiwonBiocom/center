#!/bin/bash
# Railway 강제 배포 스크립트

echo "🚂 Railway 강제 배포 시작..."
echo "================================"

# 현재 커밋 정보
CURRENT_COMMIT=$(git rev-parse --short HEAD)
echo "📍 현재 커밋: $CURRENT_COMMIT"

# Railway 환경 설정
echo "🔧 Production 환경으로 전환..."
railway environment production

# 캐시 없이 강제 배포
echo "🚀 캐시 없이 배포 시작..."
RAILWAY_NOCACHE=1 railway up --service center --detach

echo "✅ 배포 명령 실행 완료!"
echo ""
echo "📋 배포 상태 확인:"
echo "1. Railway 대시보드에서 배포 진행 상황 확인"
echo "2. 약 2-3분 후 다음 명령어로 확인:"
echo "   python scripts/check_railway_deployment.py"
