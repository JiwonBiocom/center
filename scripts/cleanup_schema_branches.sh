#!/bin/bash

# 누적된 auto/fix-schema-* 브랜치들을 정리하는 스크립트

echo "🧹 Cleaning up auto/fix-schema-* branches..."

# 원격 브랜치 목록 가져오기
branches=$(git branch -r --list "origin/auto/fix-schema-*" | sed 's/origin\///')

if [ -z "$branches" ]; then
  echo "✅ No auto/fix-schema-* branches found to clean up."
  exit 0
fi

echo "Found the following branches to delete:"
echo "$branches"
echo ""

# 사용자 확인
read -p "Do you want to delete these branches? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
  # GitHub CLI 사용 가능 여부 확인
  if command -v gh &> /dev/null; then
    echo "Using GitHub CLI to delete branches..."
    for branch in $branches; do
      echo "Deleting $branch..."
      gh api -X DELETE "repos/:owner/:repo/git/refs/heads/$branch" 2>/dev/null || echo "Failed to delete $branch"
    done
  else
    echo "GitHub CLI not found. Using git commands..."
    for branch in $branches; do
      echo "Deleting $branch..."
      git push origin --delete "$branch" 2>/dev/null || echo "Failed to delete $branch"
    done
  fi
  echo "✅ Cleanup completed!"
else
  echo "❌ Cleanup cancelled."
fi
