# 시드 데이터 디렉토리

이 디렉토리는 프로덕션 데이터베이스에 초기 데이터를 시드하기 위한 파일들을 포함합니다.

## 파일 구조
- `marketing_leads.xlsx` - 유입고객 데이터
- `kit_receipts.xlsx` - 검사키트 수령 데이터

## Git LFS 사용
대용량 Excel 파일은 Git LFS를 통해 관리됩니다.

```bash
# Git LFS 설치 (최초 1회)
brew install git-lfs
git lfs install

# 파일 추가 시
git add backend/seed/marketing_leads.xlsx
git commit -m "feat: 유입고객 시드 데이터 추가"
```

## 시드 실행
GitHub Actions를 통해 자동으로 실행됩니다:
1. 이 디렉토리의 파일이 변경되면 자동 트리거
2. 수동 실행: Actions 탭 → "Seed Production Database" → Run workflow

## 주의사항
- 중복 데이터 방지를 위해 upsert 전략 사용
- 민감한 개인정보는 마스킹 처리 필수
- 변경 전 반드시 PR 리뷰 받기