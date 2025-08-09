#!/bin/bash
# API Route Smoke Test Script
# 배포 전 모든 주요 API 엔드포인트의 trailing slash 처리를 검증합니다.

API_BASE="${API_BASE:-https://center-production-1421.up.railway.app/api/v1}"
TOKEN="${JWT_TOKEN:-}"

echo "🔍 API Route Smoke Test 시작..."
echo "API Base: $API_BASE"

# POST/PUT/PATCH 엔드포인트 trailing slash 검증
endpoints=(
  "POST /auth/login/"
  "POST /auth/refresh/"
  "POST /customers/"
  "PUT /customers/1/"
  "POST /payments/"
  "PUT /payments/1/"
  "POST /services/usage/"
  "POST /settings/password/change/"
  "PUT /settings/profile/"
  "POST /reservations/"
  "PUT /reservations/1/"
  "POST /staff-schedule/"
  "PUT /staff-schedule/1/"
)

failed=0
passed=0

for endpoint in "${endpoints[@]}"; do
  method=$(echo $endpoint | cut -d' ' -f1)
  path=$(echo $endpoint | cut -d' ' -f2)

  # trailing slash 있는 버전 테스트
  if [ -n "$TOKEN" ]; then
    response=$(curl -s -o /dev/null -w "%{http_code}" -X $method "$API_BASE$path" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{}')
  else
    response=$(curl -s -o /dev/null -w "%{http_code}" -X $method "$API_BASE$path" -H "Content-Type: application/json" -d '{}')
  fi

  if [[ $response == "404" || $response == "307" ]]; then
    echo "❌ $method $path - 응답: $response"
    ((failed++))
  else
    echo "✅ $method $path - 응답: $response"
    ((passed++))
  fi
done

echo ""
echo "📊 테스트 결과:"
echo "✅ 성공: $passed"
echo "❌ 실패: $failed"

if [ $failed -gt 0 ]; then
  echo ""
  echo "❌ $failed개의 엔드포인트가 trailing slash를 제대로 처리하지 못했습니다!"
  exit 1
fi

echo ""
echo "✅ 모든 API 엔드포인트가 정상 작동합니다!"
exit 0
