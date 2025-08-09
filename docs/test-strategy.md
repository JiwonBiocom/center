# 🧪 Test Strategy - Center Project
> Version: 1.0.0
> Updated: 2025-06-22
> Scope: All teams (Backend, Frontend, Mobile)

## 📋 목차
1. [테스트 목표](#1-테스트-목표)
2. [테스트 레이어 정의](#2-테스트-레이어-정의)
3. [브랜치별 테스트 정책](#3-브랜치별-테스트-정책)
4. [픽스처 관리](#4-픽스처-관리)
5. [테스트 리포팅](#5-테스트-리포팅)
6. [비기능 테스트](#6-비기능-테스트-선택사항)

## 1. 테스트 목표

| Metric | Target | Tool | 측정 방법 |
|--------|--------|------|----------|
| Unit Coverage | ≥ 70% lines | pytest-cov / jest | 코드 라인 커버리지 |
| Integration Routes | 모든 CRUD + 주요 에러 | pytest-async / supertest | API 엔드포인트 커버리지 |
| E2E Critical Path | 핵심 사용자 시나리오 | Playwright | 시나리오 완료율 |

### 핵심 사용자 시나리오
1. **회원가입 → 로그인**
2. **서비스 예약 → 결제**
3. **고객 정보 수정**
4. **관리자 대시보드 조회**

## 2. 테스트 레이어 정의

### 2.1 단위 테스트 (Unit Tests)
- **대상**: 순수 함수, 클래스, 유틸리티
- **특징**: DB/네트워크 모킹, 빠른 실행
- **예시**:
```python
# backend/tests/unit/test_discount_calculator.py
def test_calculate_membership_discount():
    customer = Customer(membership_level="gold")
    discount = calculate_discount(customer, 100000)
    assert discount == 10000  # 10% 할인
```

### 2.2 통합 테스트 (Integration Tests)
- **대상**: API 엔드포인트, DB 연동
- **특징**: TestClient 사용, 실제 DB (Docker)
- **예시**:
```python
# backend/tests/integration/test_customer_api.py
async def test_create_customer(client: TestClient, db: Session):
    response = await client.post("/api/v1/customers/", json={
        "name": "테스트고객",
        "phone": "010-1234-5678"
    })
    assert response.status_code == 201
    assert response.json()["name"] == "테스트고객"
```

### 2.3 E2E 테스트 (End-to-End Tests)
- **대상**: 전체 사용자 플로우
- **특징**: 실제 브라우저, Staging 환경
- **예시**:
```typescript
// e2e/tests/reservation-flow.spec.ts
test('예약 전체 플로우', async ({ page }) => {
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password');
    await page.click('button[type="submit"]');

    await page.goto('/services');
    await page.click('text=AI 건강검진');
    await page.click('text=예약하기');
    // ... 결제까지 진행
});
```

## 3. 브랜치별 테스트 정책

| Layer | When to Run | CI Job | 실패 시 조치 |
|-------|-------------|--------|------------|
| Unit | 모든 push | `test-unit` | 즉시 수정 필요 |
| Integration | PR open/update | `test-integration` | PR 머지 차단 |
| E2E | nightly + pre-release | `test-e2e` | 배포 중단 |

### GitHub Actions 설정
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run unit tests
        run: |
          cd backend && pytest tests/unit -v --cov=app --cov-report=xml
          cd ../frontend && npm test -- --coverage
```

## 4. 픽스처 관리

### 4.1 백엔드 픽스처
```python
# backend/tests/fixtures/customer.py
@pytest.fixture
def sample_customer(db: Session):
    customer = Customer(
        name="테스트고객",
        phone="010-1234-5678",
        membership_level="gold"
    )
    db.add(customer)
    db.commit()
    yield customer
    db.delete(customer)
    db.commit()
```

### 4.2 프론트엔드 목 데이터
```typescript
// frontend/tests/mocks/customers.ts
export const mockCustomers = [
  {
    customer_id: 1,
    name: "테스트고객",
    phone: "010-1234-5678",
    membership_level: "gold"
  }
];
```

### 4.3 Supabase Seed 데이터
```sql
-- supabase/seed.sql
INSERT INTO customers (name, phone, membership_level) VALUES
  ('테스트고객1', '010-1111-1111', 'basic'),
  ('테스트고객2', '010-2222-2222', 'gold');
```

## 5. 테스트 리포팅

### 5.1 커버리지 배지
```markdown
![Coverage](https://codecov.io/gh/your-org/center/branch/main/graph/badge.svg)

- 🔴 Red: < 70% (실패)
- 🟡 Orange: 70-80% (경고)
- 🟢 Green: ≥ 80% (정상)
```

### 5.2 테스트 결과 리포트
- **단위 테스트**: `pytest-html` → GitHub Actions artifacts
- **통합 테스트**: API 응답 시간 포함
- **E2E 테스트**: 스크린샷/비디오 첨부

### 5.3 일일 리포트
```
📊 Daily Test Report (2025-06-22)
- Unit Tests: 156/160 passed (97.5%)
- Integration: 45/45 passed (100%)
- E2E: 8/10 passed (80%)
- Coverage: 78.3%
```

## 6. 비기능 테스트 (선택사항)

### 6.1 성능 테스트
- **도구**: k6, Locust
- **목표**:
  - API 응답시간 < 200ms (p95)
  - TPS > 50
- **스크립트 위치**: `/perf/`

### 6.2 보안 테스트
- **정적 분석**: Bandit (Python), ESLint security plugin
- **동적 분석**: OWASP ZAP baseline scan
- **주기**: 주 1회

### 6.3 접근성 테스트
- **도구**: axe-core, Pa11y
- **기준**: WCAG 2.1 Level AA
- **대상**: 모든 public 페이지

## 🚦 실패 게이트 (Failure Gates)

### 필수 통과 조건
1. **Unit coverage < 70%** → CI 실패
2. **Integration test 실패** → PR 머지 차단
3. **E2E 핵심 시나리오 실패** → 배포 중단
4. **보안 취약점 High 이상** → 즉시 수정

### 권장 사항
- 신규 기능은 테스트 먼저 작성 (TDD)
- 버그 수정 시 재발 방지 테스트 추가
- 리팩토링 전후 테스트 결과 동일 확인

---

## 🔗 관련 문서
- [개발 규칙](development-rules.md)
- [API 문서](API_DOCUMENTATION.md)
- [CI/CD 가이드](INFRASTRUCTURE.md)
- [테스트 규칙](TEST_RULES.md)

## 📝 부록: 테스트 명명 규칙

### Python (pytest)
```python
def test_<기능>_<시나리오>_<예상결과>():
    # test_create_customer_with_valid_data_returns_201
    # test_login_with_invalid_password_returns_401
```

### TypeScript (Jest)
```typescript
describe('CustomerService', () => {
  it('should create customer with valid data', () => {
    // ...
  });

  it('should throw error when phone is invalid', () => {
    // ...
  });
});
```

---

_문의: @test-lead 또는 #dev-testing 채널_
