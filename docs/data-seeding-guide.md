# 프로덕션 데이터 시딩 가이드

## 개요
이 문서는 프로덕션 데이터베이스에 초기 데이터(marketing_leads, kit_receipts 등)를 안전하게 시드하는 방법을 설명합니다.

## 아키텍처

```mermaid
graph LR
    A[Excel/CSV 파일] -->|prepare_seed_data.py| B[backend/seed/]
    B -->|Git LFS| C[GitHub]
    C -->|GitHub Actions| D[import_*.py 스크립트]
    D -->|psycopg2| E[Production DB]
    E -->|Nightly Check| F[Validation Workflow]
    F -->|실패 시| G[GitHub Issue 생성]
```

## 구성 요소

### 1. 시드 데이터 파일
- **위치**: `backend/seed/`
- **형식**: Excel (.xlsx)
- **Git LFS**: 대용량 파일 관리

### 2. 마이그레이션 스크립트
- `scripts/import_marketing_leads.py` - 유입고객 데이터
- `scripts/import_kit_receipts.py` - 검사키트 수령 데이터

### 3. GitHub Actions 워크플로
- `.github/workflows/seed-production-db.yml` - 자동 시드 실행
- `.github/workflows/nightly-seed-validation.yml` - 매일 밤 검증

## 사용 방법

### 초기 설정 (1회만)

1. **GitHub Secrets 설정**
   ```
   Settings → Secrets → Actions → New repository secret
   - Name: DATABASE_URL
   - Value: postgresql://user:pass@host:port/dbname
   ```

2. **Git LFS 설치**
   ```bash
   brew install git-lfs
   git lfs install
   ```

### 데이터 시드 프로세스

#### 방법 1: 자동 시드 (권장)
1. 시드 파일 업데이트
   ```bash
   python scripts/prepare_seed_data.py
   ```

2. 커밋 & 푸시
   ```bash
   git add backend/seed/*.xlsx
   git commit -m "feat: 시드 데이터 업데이트"
   git push origin main
   ```

3. GitHub Actions가 자동으로 시드 실행

#### 방법 2: 수동 시드
1. GitHub Actions 탭 이동
2. "Seed Production Database" 워크플로 선택
3. "Run workflow" 클릭
4. 대상 테이블 선택 후 실행

### 데이터 검증

#### 자동 검증 (매일 새벽 2시)
- Nightly 워크플로가 자동 실행
- 최소 레코드 수 미달 시 Issue 생성

#### 수동 검증
```bash
# 로컬에서 확인
python -c "
import psycopg2
from urllib.parse import urlparse
import os

# .env 파일에서 DATABASE_URL 로드
from dotenv import load_dotenv
load_dotenv()

url = urlparse(os.environ['DATABASE_URL'])
conn = psycopg2.connect(
    host=url.hostname,
    port=url.port,
    database=url.path[1:],
    user=url.username,
    password=url.password,
    sslmode='require'
)

cur = conn.cursor()
tables = ['marketing_leads', 'kit_receipts']
for table in tables:
    cur.execute(f'SELECT COUNT(*) FROM {table}')
    count = cur.fetchone()[0]
    print(f'{table}: {count} records')

cur.close()
conn.close()
"
```

## 보안 고려사항

### 개인정보 보호
- 민감한 정보는 마스킹 처리
- 프로덕션 데이터는 Git LFS로만 관리
- DATABASE_URL은 GitHub Secrets로만 관리

### 데이터 무결성
- Upsert 전략으로 중복 방지
- 트랜잭션 단위 처리
- 실패 시 자동 롤백

## 트러블슈팅

### 시드 실패 시
1. GitHub Actions 로그 확인
2. 데이터 형식 검증
3. DB 연결 정보 확인

### 검증 실패 시
1. 생성된 Issue 확인
2. 누락된 데이터 확인
3. 수동 시드 재실행

## 개선 계획

### 단기
- [ ] 더 많은 테이블 지원
- [ ] 데이터 마스킹 자동화
- [ ] 시드 이력 관리

### 장기
- [ ] Preview DB 자동 생성
- [ ] Google Sheets 연동
- [ ] 실시간 동기화

## 참고 자료
- [GitHub Actions 문서](https://docs.github.com/actions)
- [Git LFS 가이드](https://git-lfs.github.com/)
- [PostgreSQL Upsert](https://www.postgresql.org/docs/current/sql-insert.html#SQL-ON-CONFLICT)