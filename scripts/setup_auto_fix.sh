#!/bin/bash
# 자동 스키마 수정 설정 스크립트

echo "🚀 Setting up automatic schema sync..."

# 1. GitHub Secrets 설정 안내
echo "
📋 GitHub Secrets 설정 필요:
1. GitHub 저장소 > Settings > Secrets and variables > Actions
2. 다음 시크릿 추가:
   - DATABASE_URL: Supabase 연결 URL
   - SUPABASE_ACCESS_TOKEN: Supabase 액세스 토큰
   - SUPABASE_PROJECT_ID: 프로젝트 ID

현재 DATABASE_URL: ${DATABASE_URL:0:30}...
"

# 2. Pre-commit hook 설치
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
echo "🔍 Checking schema before push..."
python scripts/check_db_schema_diff.py

if [ $? -ne 0 ]; then
    echo "❌ Schema drift detected! Fix before pushing."
    echo "Run: python scripts/auto_fix_schema.py"
    exit 1
fi
EOF

chmod +x .git/hooks/pre-push
echo "✅ Pre-push hook installed"

# 3. 즉시 실행 가능한 명령어 출력
echo "
🛠️ 사용 가능한 명령어:

# 스키마 차이 확인만
python scripts/check_db_schema_diff.py

# 자동 수정 (확인 후 적용)
python scripts/auto_fix_schema.py

# 자동 수정 (바로 적용 - 개발환경만)
python scripts/auto_fix_schema.py --auto

# GitHub Actions 수동 실행
gh workflow run schema-check.yml
"

# 4. 현재 스키마 상태 확인
echo "
📊 현재 스키마 상태 확인 중..."
python scripts/auto_fix_schema.py --dry-run 2>/dev/null || echo "스크립트 실행 중 에러. 환경 확인 필요."