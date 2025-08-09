#!/bin/bash
# Vercel 빌드 환경변수 검증 스크립트

echo "🔍 환경변수 및 빌드 검증"
echo "=========================="

# 1. 현재 환경변수 확인
echo -e "\n1. 현재 환경변수:"
echo "VITE_API_URL: ${VITE_API_URL:-'not set'}"

# 2. .env.production 파일 확인
echo -e "\n2. .env.production 파일 내용:"
if [ -f "frontend/.env.production" ]; then
    cat frontend/.env.production
else
    echo "⚠️  .env.production 파일이 없습니다!"
fi

# 3. 로컬 빌드 테스트
echo -e "\n3. 로컬 빌드 테스트..."
cd frontend
VITE_API_URL=https://center-production-1421.up.railway.app npm run build

# 4. 빌드된 파일에서 URL 검색
echo -e "\n4. 빌드 결과 확인:"
echo "HTTP URL 검색:"
grep -o "http://center-production[^\"]*" dist/assets/*.js | head -5 || echo "✅ HTTP URL 없음"

echo -e "\nHTTPS URL 검색:"
grep -o "https://center-production[^\"]*" dist/assets/*.js | head -5 || echo "❌ HTTPS URL 없음"

echo -e "\n5. Vercel 환경변수 설정 필요:"
echo "================================"
echo "Vercel 대시보드에서 다음 환경변수를 설정하세요:"
echo "VITE_API_URL = https://center-production-1421.up.railway.app"
echo ""
echo "설정 경로: Settings > Environment Variables"
echo "주의: 변수명은 반드시 VITE_ 로 시작해야 합니다!"