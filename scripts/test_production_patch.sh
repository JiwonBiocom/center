#!/bin/bash
# 프로덕션 PATCH 테스트를 위한 간단한 쉘 스크립트

echo "🧪 프로덕션 PATCH 메서드 빠른 테스트"
echo "=================================="

# 환경 변수에서 토큰 읽기 (보안상 권장)
TOKEN=${JWT_TOKEN:-"YOUR_TOKEN_HERE"}
CUSTOMER_ID=${CUSTOMER_ID:-543}
PRODUCTION_URL="https://center-production-1421.up.railway.app"

echo "📍 URL: $PRODUCTION_URL/api/v1/customers/$CUSTOMER_ID"
echo ""

# 1. OPTIONS 메서드로 허용된 메서드 확인
echo "1️⃣ OPTIONS 메서드 확인..."
curl -X OPTIONS \
  -H "Authorization: Bearer $TOKEN" \
  -H "Access-Control-Request-Method: PATCH" \
  -i \
  "$PRODUCTION_URL/api/v1/customers/$CUSTOMER_ID" 2>/dev/null | grep -E "(Allow:|HTTP/)"

echo ""
echo "2️⃣ PATCH 메서드 테스트..."

# 2. PATCH 메서드 테스트
RESPONSE=$(curl -X PATCH \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"테스트_$(date +%s)\"}" \
  -w "\n%{http_code}" \
  -s \
  "$PRODUCTION_URL/api/v1/customers/$CUSTOMER_ID")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

echo "응답 코드: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ PATCH 메서드 성공!"
elif [ "$HTTP_CODE" = "405" ]; then
    echo "❌ 405 Method Not Allowed - PATCH가 라우팅되지 않음"
    echo ""
    echo "3️⃣ PUT 메서드로 재시도..."
    
    PUT_RESPONSE=$(curl -X PUT \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"name\":\"테스트_$(date +%s)\"}" \
      -w "\n%{http_code}" \
      -s \
      "$PRODUCTION_URL/api/v1/customers/$CUSTOMER_ID")
    
    PUT_CODE=$(echo "$PUT_RESPONSE" | tail -n1)
    
    if [ "$PUT_CODE" = "200" ]; then
        echo "✅ PUT 메서드는 작동함"
        echo "💡 프론트엔드를 PUT으로 변경하거나, 백엔드 라우팅 설정 확인 필요"
    else
        echo "❌ PUT도 실패: $PUT_CODE"
    fi
else
    echo "❌ 예상치 못한 응답: $HTTP_CODE"
    echo "응답 내용:"
    echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
fi

echo ""
echo "=================================="
echo "💡 사용법:"
echo "  export JWT_TOKEN='your-token-here'"
echo "  export CUSTOMER_ID=543"
echo "  ./scripts/test_production_patch.sh"