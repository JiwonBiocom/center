#!/bin/bash
# 배포 검증 스크립트

echo "🔍 배포 검증 시작..."
echo "====================="

# 1. 프로덕션 사이트 접속
echo -e "\n1. 프로덕션 사이트 HTML 다운로드..."
curl -s https://center-ten.vercel.app > /tmp/vercel-index.html

# 2. 빌드된 JS 파일 URL 추출
echo -e "\n2. JS 파일 URL 추출..."
JS_URL=$(grep -o '/assets/index-[^"]*\.js' /tmp/vercel-index.html | head -1)
echo "JS 파일: $JS_URL"

# 3. JS 파일 다운로드 및 검사
if [ ! -z "$JS_URL" ]; then
    echo -e "\n3. JS 파일 다운로드 및 HTTP URL 검색..."
    curl -s "https://center-ten.vercel.app$JS_URL" > /tmp/vercel-app.js
    
    echo -e "\nHTTP URL 검색 결과:"
    grep -o "http://center-production[^\"']*" /tmp/vercel-app.js | head -5 || echo "✅ HTTP URL 없음"
    
    echo -e "\nHTTPS URL 검색 결과:"
    grep -o "https://center-production[^\"']*" /tmp/vercel-app.js | head -5 || echo "❌ HTTPS URL 없음"
fi

# 4. API 호출 테스트
echo -e "\n4. API 호출 테스트..."
curl -I -H "Origin: https://center-ten.vercel.app" \
     -H "Content-Type: application/json" \
     https://center-production-1421.up.railway.app/api/v1/auth/login 2>/dev/null | grep -E "(access-control|HTTP/)"

echo -e "\n✅ 검증 완료"