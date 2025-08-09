# 개발 환경 설정 가이드

## Pre-commit Hook 설정

이 프로젝트는 코드 품질 유지를 위해 pre-commit hook을 사용합니다.

### 1. 필수 도구 설치

```bash
# pre-commit 설치
pip install pre-commit

# actionlint 설치 (GitHub Actions 워크플로우 검증)
# macOS
brew install actionlint

# Ubuntu/Debian
wget https://github.com/rhysd/actionlint/releases/latest/download/actionlint_1.7.5_linux_amd64.tar.gz
tar -xvf actionlint_1.7.5_linux_amd64.tar.gz
sudo mv actionlint /usr/local/bin/

# Windows (scoop 사용)
scoop install actionlint
```

### 2. Pre-commit Hook 활성화

```bash
# 프로젝트 루트에서 실행
pre-commit install
```

### 3. 수동 실행 (선택사항)

```bash
# 모든 파일 검사
pre-commit run --all-files

# 특정 hook만 실행
pre-commit run yamllint --all-files
pre-commit run actionlint --all-files
```

## Pre-commit Hook 목록

### 1. **yamllint**
- YAML 파일 문법 및 스타일 검사
- 라인 길이 120자 제한
- truthy 값 허용 (yes/no, on/off 등)

### 2. **actionlint**
- GitHub Actions 워크플로우 파일 검증
- 문법 오류, 타입 오류 등 사전 감지

### 3. **check-enums**
- 백엔드와 프론트엔드의 enum 값 일치 검증
- 프로덕션 500 에러 예방

### 4. **check-api-routes**
- API 경로 일관성 검증
- 404 에러 사전 감지

### 5. **기본 파일 검사**
- trailing-whitespace: 줄 끝 공백 제거
- end-of-file-fixer: 파일 끝 개행 문자 추가
- check-yaml: YAML 문법 검증
- check-json: JSON 문법 검증
- check-added-large-files: 1MB 이상 파일 경고
- check-merge-conflict: merge conflict 마커 감지

## 문제 해결

### yamllint 에러
```bash
# 자동 수정 가능한 문제들
yamllint --fix .github/workflows/*.yml
```

### actionlint 미설치 시
pre-commit은 실행되지만 actionlint 검사는 건너뜁니다.
CI/CD에서는 GitHub Actions가 자동으로 검증합니다.

### enum/route 검사 실패
```bash
# 화이트리스트 업데이트
vi scripts/route_checker_ignore.txt

# enum 값 확인
python scripts/check_enum_values.py
```

---

*더 자세한 내용은 [.pre-commit-config.yaml](../.pre-commit-config.yaml) 파일을 참조하세요.*
