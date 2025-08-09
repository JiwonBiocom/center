#!/bin/bash
# 배포 전 스키마 드리프트 체크 스크립트

echo "🚀 배포 전 체크리스트 실행"
echo "================================"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 체크 결과 저장
ERRORS=0

# 1. Python 스키마 검증
echo -e "\n📊 데이터베이스 스키마 검증..."
if [ -f "scripts/check_db_schema_diff.py" ]; then
    python scripts/check_db_schema_diff.py
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 스키마 불일치 발견!${NC}"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}✅ 스키마 동기화 확인${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  스키마 검증 스크립트 없음${NC}"
fi

# 2. 타입 체크
echo -e "\n🔍 TypeScript 타입 체크..."
cd frontend
if command -v npm &> /dev/null; then
    npm run type-check 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ TypeScript 타입 에러!${NC}"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}✅ 타입 체크 통과${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  npm이 설치되지 않음${NC}"
fi
cd ..

# 3. 테스트 실행
echo -e "\n🧪 테스트 실행..."
# 백엔드 테스트
if [ -d "backend" ]; then
    cd backend
    if command -v pytest &> /dev/null; then
        pytest -q --tb=short
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ 백엔드 테스트 실패!${NC}"
            ERRORS=$((ERRORS + 1))
        else
            echo -e "${GREEN}✅ 백엔드 테스트 통과${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  pytest가 설치되지 않음${NC}"
    fi
    cd ..
fi

# 4. 환경 변수 확인
echo -e "\n🔐 환경 변수 확인..."
REQUIRED_VARS=(
    "DATABASE_URL"
    "JWT_SECRET"
    "VITE_API_URL"
)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ $var 환경 변수 누락!${NC}"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}✅ $var 설정됨${NC}"
    fi
done

# 5. Git 상태 확인
echo -e "\n📝 Git 상태 확인..."
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  커밋되지 않은 변경사항이 있습니다${NC}"
    git status --short
fi

# 6. 마이그레이션 파일 확인
echo -e "\n📁 마이그레이션 파일 확인..."
if [ -d "supabase/migrations" ]; then
    MIGRATION_COUNT=$(ls -1 supabase/migrations/*.sql 2>/dev/null | wc -l)
    echo -e "${GREEN}✅ $MIGRATION_COUNT개의 마이그레이션 파일 발견${NC}"
else
    echo -e "${YELLOW}⚠️  Supabase 마이그레이션 폴더 없음${NC}"
fi

# 7. API 헬스 체크 (로컬)
echo -e "\n🏥 로컬 API 헬스 체크..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 백엔드 서버 응답 정상${NC}"
else
    echo -e "${YELLOW}⚠️  백엔드 서버가 실행 중이 아님${NC}"
fi

# 결과 요약
echo -e "\n================================"
echo "📋 체크리스트 결과"
echo "================================"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ 모든 체크 통과! 배포 준비 완료${NC}"
    echo -e "\n다음 명령어로 배포를 진행하세요:"
    echo "  git push origin main"
    exit 0
else
    echo -e "${RED}❌ $ERRORS개의 문제 발견! 배포 전 수정 필요${NC}"
    echo -e "\n문제를 해결한 후 다시 실행하세요."
    exit 1
fi