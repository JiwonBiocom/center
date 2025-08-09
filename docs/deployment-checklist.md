# 🚀 배포 체크리스트 및 스키마 드리프트 방지 가이드

> 버전: 1.0.0
> 최종 업데이트: 2025-06-21
> 목적: 데이터베이스 스키마와 애플리케이션 코드의 불일치로 인한 500 에러 방지

## 📋 목차
1. [문제의 근원](#-문제의-근원)
2. [8대 핵심 규칙](#-8대-핵심-규칙)
3. [배포 전 체크리스트](#-배포-전-체크리스트)
4. [구현 로드맵](#-구현-로드맵)
5. [즉시 적용 가능한 조치](#-즉시-적용-가능한-조치)

## 🔥 문제의 근원

### 2025-06-21 발생한 실제 사례 #1:
- **증상**: API 500 Internal Server Error
- **원인**:
  - `notifications.user_id` 컬럼 누락 (코드는 `user_id`, DB는 `customer_id`)
  - `packages.price` → `base_price` 불일치
  - `packages.valid_days` → `valid_months` 불일치
- **영향**: 프로덕션 전체 API 장애

### 2025-06-21 발생한 실제 사례 #2:
- **증상**: 고객 등록 시 404 → 500 에러
- **원인**:
  - FastAPI `redirect_slashes=False` 설정으로 경로 불일치
  - **Enum 값 불일치**: DB는 `membership_level = 'basic'`, 코드는 `'bronze'`
- **영향**: 신규 고객 등록 불가
- **교훈**: Enum 타입은 특히 위험 - 런타임에서만 발견됨

## 🛡️ 8대 핵심 규칙

### 1️⃣ 단일 소스 오브 트루스 (Single Source of Truth)
```bash
# ✅ 올바른 방법
supabase migration new add_user_id_to_notifications
supabase db diff

# ❌ 절대 금지
# - Supabase Studio UI에서 직접 테이블 수정
# - SQL Editor에서 수동 ALTER TABLE
```

**적용 방법**:
```yaml
# .github/CODEOWNERS
supabase/migrations/ @backend-lead @dba
```

### 2️⃣ PR 템플릿 강제
```markdown
<!-- .github/pull_request_template.md -->
## 데이터베이스 변경사항
- [ ] DB 스키마를 변경했으면 `supabase/migrations/`에 새 파일을 추가했나요?
- [ ] `supabase db diff` 결과가 0 라인인지 확인했나요?
- [ ] ORM 모델과 실제 스키마가 일치하나요?
- [ ] 백엔드와 프론트엔드 타입이 동기화되었나요?
```

### 3️⃣ CI 자동 검증
```yaml
# .github/workflows/schema-check.yml
name: Schema Drift Check
on: [pull_request]

jobs:
  schema-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Supabase CLI
        uses: supabase/setup-cli@v1

      - name: Check Schema Drift
        run: |
          supabase db diff --db-url ${{ secrets.SHADOW_DB_URL }} -q
          if [ -n "$(supabase db diff --db-url ${{ secrets.SHADOW_DB_URL }})" ]; then
            echo "❌ Schema drift detected!"
            exit 1
          fi
```

### 4️⃣ 마이그레이션 우선 배포
```yaml
# Railway/Vercel 배포 순서
steps:
  1_database:
    - supabase db push --db-url $PROD_DB_URL
    - sleep 10  # 스키마 전파 대기

  2_backend:
    - railway up

  3_frontend:
    - vercel deploy --prod
```

### 5️⃣ 네이밍 컨벤션
```sql
-- ✅ 표준 컨벤션
CREATE TABLE notifications (
    notification_id INTEGER PRIMARY KEY,  -- PK는 <table>_id
    user_id INTEGER NOT NULL,            -- FK는 <entity>_id
    is_read BOOLEAN DEFAULT FALSE,       -- 상태는 is_*
    created_at TIMESTAMP DEFAULT NOW()   -- 시간은 *_at
);

-- ❌ 금지된 네이밍
-- customer_id (notifications에서)  → user_id 사용
-- read_flag                        → is_read 사용
-- date_created                     → created_at 사용
```

### 6️⃣ 타입 세이프 ORM
```typescript
// Prisma 설정 예시
// prisma/schema.prisma
model Notification {
  id        Int      @id @default(autoincrement()) @map("notification_id")
  userId    Int      @map("user_id")
  isRead    Boolean  @default(false) @map("is_read")
  createdAt DateTime @default(now()) @map("created_at")

  user User @relation(fields: [userId], references: [id])

  @@map("notifications")
}
```

### 7️⃣ Preview 데이터베이스
```bash
# PR별 자동 Preview DB
supabase link --project-ref $PR_PREVIEW_PROJECT
supabase db push
npm run test:e2e
```

### 8️⃣ 데이터 마이그레이션 체크리스트
```markdown
## 대량 데이터 변경 시
- [ ] 실행 계획(EXPLAIN) 확인
- [ ] 백업 완료
- [ ] 롤백 SQL 준비
- [ ] 점진적 마이그레이션 스크립트
- [ ] 다운타임 공지
```

### 9️⃣ Enum 타입 동기화 (신규 추가)
```python
# ❌ 위험한 방법 - 하드코딩된 Enum
class MembershipLevel(str, Enum):
    BRONZE = "bronze"  # DB와 불일치 시 500 에러!

# ✅ 안전한 방법 - DB에서 동적으로 가져오기
def get_enum_values(enum_type: str):
    result = db.execute(text(f"SELECT unnest(enum_range(NULL::{enum_type}))"))
    return [row[0] for row in result]

# 또는 시작 시 검증
MEMBERSHIP_LEVELS = get_enum_values('membership_level')
assert 'basic' in MEMBERSHIP_LEVELS, "Enum mismatch detected!"
```

## 📝 배포 전 체크리스트

### 🔍 개발 단계
```bash
# 1. 로컬 스키마 확인
supabase db diff

# 2. 타입 생성
supabase gen types typescript --local > types/database.types.ts

# 3. ORM 모델 검증
npm run db:validate

# 4. 🆕 Enum 값 검증 (중요!)
python scripts/check_enum_values.py
# - membership_level: ['basic', 'silver', 'gold', 'platinum', 'vip']
# - customer_status: ['active', 'inactive', 'dormant']

# 5. 🆕 API 경로 일관성 검증
python scripts/check_api_routes.py
# - FastAPI redirect_slashes 설정 확인
# - 모든 라우트의 trailing slash 처리 확인
```

### 🚦 CI/CD 단계
```yaml
deployment_checklist:
  pre_deploy:
    - backup_database
    - run_migrations_on_shadow
    - validate_schema_drift
    - generate_rollback_script

  deploy:
    - apply_migrations
    - deploy_backend
    - deploy_frontend
    - run_smoke_tests

  post_deploy:
    - monitor_error_rates
    - check_api_health
    - validate_critical_paths
```

### 🎯 Smoke Test
```typescript
// scripts/smoke-test.ts
const criticalEndpoints = [
  { path: '/api/v1/health', expected: 200 },
  { path: '/api/v1/customers?limit=1', expected: 200 },
  { path: '/api/v1/auth/login', method: 'POST', expected: 401 },
  // 🆕 POST 엔드포인트 테스트 (redirect_slashes 문제 방지)
  { path: '/api/v1/customers', method: 'POST', expected: 401 },
  { path: '/api/v1/customers/', method: 'POST', expected: 401 }
];

for (const endpoint of criticalEndpoints) {
  const response = await fetch(BASE_URL + endpoint.path, {
    method: endpoint.method || 'GET'
  });
  assert(response.status === endpoint.expected);
}
```

### 🆕 4️⃣ API Route Smoke Test
배포 전 모든 주요 API 엔드포인트의 trailing slash 처리를 검증합니다.

```bash
#!/bin/bash
# scripts/check-api-routes.sh

API_BASE="https://center-production-1421.up.railway.app/api/v1"
TOKEN="Bearer $JWT_TOKEN"

echo "🔍 API Route Smoke Test 시작..."

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
)

failed=0
for endpoint in "${endpoints[@]}"; do
  method=$(echo $endpoint | cut -d' ' -f1)
  path=$(echo $endpoint | cut -d' ' -f2)

  # trailing slash 있는 버전 테스트
  response=$(curl -s -o /dev/null -w "%{http_code}" -X $method "$API_BASE$path" -H "Authorization: $TOKEN")
  if [[ $response == "404" || $response == "307" ]]; then
    echo "❌ $method $path - 응답: $response"
    ((failed++))
  else
    echo "✅ $method $path - 응답: $response"
  fi
done

if [ $failed -gt 0 ]; then
  echo "❌ $failed개의 엔드포인트가 trailing slash를 제대로 처리하지 못했습니다!"
  exit 1
fi

echo "✅ 모든 API 엔드포인트가 정상 작동합니다!"
```

#### Trailing Slash 정책 요약
- **FastAPI 설정**: `redirect_slashes=False` (엄격 모드)
- **프론트엔드**: POST/PUT/PATCH에 자동으로 trailing slash 추가
- **백엔드 대응**: 모든 POST/PUT/PATCH 엔드포인트에 두 버전 등록
- **상세 가이드**: [API Routing Style Guide](./api-routing-style.md) 참조

## 🗺️ 구현 로드맵

### Phase 1: 즉시 적용 (1주)
- [ ] PR 템플릿 추가
- [ ] 네이밍 컨벤션 문서화
- [ ] 수동 스키마 체크 스크립트

### Phase 2: 자동화 (2주)
- [ ] GitHub Actions CI 설정
- [ ] Supabase CLI 통합
- [ ] Shadow DB 구축

### Phase 3: 고도화 (1개월)
- [ ] Prisma/Drizzle ORM 도입
- [ ] Preview DB 자동화
- [ ] 모니터링 대시보드

## 🚨 즉시 적용 가능한 조치

### 1. 현재 스키마 동기화
```bash
# 현재 불일치 수정
cd /Users/vibetj/coding/center
python scripts/check_db_schema_diff.py

# 마이그레이션 생성
supabase migration new fix_schema_drift
```

### 2. 간단한 검증 스크립트
```bash
#!/bin/bash
# scripts/check-schema.sh
echo "🔍 스키마 드리프트 체크..."

# Python 모델과 DB 스키마 비교
python scripts/validate_models.py

# 결과가 0이 아니면 실패
if [ $? -ne 0 ]; then
  echo "❌ 스키마 불일치 발견!"
  exit 1
fi

echo "✅ 스키마 동기화 확인!"
```

### 3. 팀 교육
```markdown
## 필수 규칙 (팀 전체 공유)
1. **절대** Supabase Studio에서 직접 테이블 수정 금지
2. 모든 스키마 변경은 마이그레이션 파일로
3. PR 전에 `supabase db diff` 실행
4. 컬럼명 변경 시 반드시 백엔드/프론트엔드 동시 수정
```

## 📊 효과 측정

### 성공 지표
- 스키마 관련 500 에러: 0건/월
- 배포 롤백 횟수: 50% 감소
- 평균 배포 시간: 30% 단축

### 모니터링
```javascript
// 에러 추적
Sentry.init({
  beforeSend(event) {
    if (event.exception?.values?.[0]?.value?.includes('column')) {
      // 스키마 관련 에러 특별 태깅
      event.tags = { ...event.tags, schema_error: true };
    }
    return event;
  }
});
```

## 🤖 다음 단계: 완전 자동화

이 체크리스트를 수동으로 따르는 것도 좋지만, 더 나은 방법이 있습니다!

👉 **[스키마 동기화 자동화 가이드](./schema-sync-automation.md)** 참조

- GitHub Actions + Supabase CLI로 자동 감지
- Claude Code Bot이 PR 자동 리뷰
- 런타임 Self-Healing으로 500 에러 자동 수정
- RAG 기반 Supabase 문법 지원

"수동 SQL → 500 → 디버그" 루프를 완전히 자동화로 해결할 수 있습니다!

## 🔗 관련 문서
- [스키마 동기화 자동화](./schema-sync-automation.md) 🆕
- [시스템 아키텍처](./system-overview.md)
- [개발 규칙](./development-rules.md)
<!-- - [리팩토링 가이드](./refactoring-guide.md) - 파일 없음 -->

---

*이 문서는 2025-06-21 발생한 프로덕션 장애를 계기로 작성되었습니다.*
*모든 개발자는 배포 전 이 체크리스트를 반드시 확인해야 합니다.*
