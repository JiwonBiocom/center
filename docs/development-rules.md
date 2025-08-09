# 📐 Center Project Development Rules
> Version: 1.0.0
> Last updated: 2025-06-22
> Purpose: 프로젝트 전체 개발 규칙 (backend/CLAUDE.md 중복 규칙 통합)

## 📋 목차
1. [코드 스타일](#1-코드-스타일)
2. [아키텍처 규칙](#2-아키텍처-규칙)
3. [FastAPI 라우팅](#3-fastapi-라우팅)
4. [데이터베이스](#4-데이터베이스)
5. [에러 처리](#5-에러-처리)
6. [테스팅](#6-테스팅)
7. [코드 리뷰 체크리스트](#7-코드-리뷰-체크리스트)

## 1. 코드 스타일

### Python (Backend)
- **Formatter**: Black 24.x
- **Import sorter**: isort
- **Linter**: flake8, mypy
- **최대 파일 길이**: 300 LoC (테스트 제외)
- **함수 최대 길이**: 50 LoC

### TypeScript/JavaScript (Frontend)
- **Linter**: ESLint @latest
- **Formatter**: Prettier
- **최대 파일 길이**: 300 LoC
- **컴포넌트 최대 길이**: 250 LoC

### 공통 규칙
```python
# ✅ 좋은 예: 명확한 함수명
def calculate_membership_discount(customer: Customer) -> float:
    pass

# ❌ 나쁜 예: 모호한 함수명
def calc(c):
    pass
```

## 2. 아키텍처 규칙

### 2.1 SOLID 원칙
- **S**ingle Responsibility: 하나의 클래스/함수는 하나의 책임
- **O**pen/Closed: 확장에는 열려있고 수정에는 닫혀있게
- **L**iskov Substitution: 상속 관계의 일관성
- **I**nterface Segregation: 인터페이스 분리
- **D**ependency Inversion: 의존성 역전

### 2.2 레이어 아키텍처
```
API Route → Service → Repository → Database
    ↓           ↓           ↓
  Schema    Business    SQLAlchemy
            Logic        Models
```

### 2.3 의존성 방향
- 상위 레이어는 하위 레이어에만 의존
- 순환 의존성 금지
- 인터페이스를 통한 의존성 주입

## 3. FastAPI 라우팅

### 3.1 기본 규칙
```python
# ✅ 올바른 예
@router.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pass
```

### 3.2 Trailing Slash 정책
> 🔗 상세 내용: [`api-routing-style.md`](api-routing-style.md)

```python
# POST, PUT, PATCH는 반드시 두 버전 모두 등록
@router.post("/customers", response_model=CustomerResponse)
@router.post("/customers/", response_model=CustomerResponse)
async def create_customer(...):
    pass
```

### 3.3 API 버전 관리
- 모든 엔드포인트는 `/api/v1/` 프리픽스 사용
- 버전 업그레이드 시 하위 호환성 유지

## 4. 데이터베이스

### 4.1 ORM 사용
```python
# SQLAlchemy 2.0 Declarative 스타일
class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=func.now())
```

### 4.2 마이그레이션
- **도구**: Alembic 또는 Supabase Migration
- **규칙**: 모든 스키마 변경은 마이그레이션 파일로
- **금지**: 프로덕션 DB 직접 수정

### 4.3 쿼리 최적화
```python
# ✅ 좋은 예: 필요한 컬럼만 선택
query = db.query(Customer.customer_id, Customer.name)

# ❌ 나쁜 예: 전체 선택
query = db.query(Customer)
```

### 4.4 데이터 마이그레이션 검증 규칙 🆕
> 💡 추가 배경: Excel 데이터 마이그레이션 시 담당자 정보 누락 사례 방지

#### 4.4.1 필수 검증 사항
```python
# ✅ 올바른 예: 모든 컬럼 매핑 검증
def migrate_payments(excel_data):
    # 1. 원본 데이터 컬럼 확인
    required_columns = ['고객명', '결제일자', '결제 금액', '결제 담당자']
    missing = [col for col in required_columns if col not in excel_data.columns]
    if missing:
        raise ValueError(f"필수 컬럼 누락: {missing}")

    # 2. 실제 데이터 매핑
    payment_data = {
        'customer_name': row['고객명'],
        'payment_date': row['결제일자'],
        'amount': row['결제 금액'],
        'payment_staff': row['결제 담당자']  # 하드코딩 금지!
    }

# ❌ 나쁜 예: 하드코딩된 기본값
payment_data = {
    'payment_staff': '직원'  # 절대 금지!
}
```

#### 4.4.2 마이그레이션 체크리스트
- [ ] **원본 데이터 분석**: 모든 시트와 컬럼 구조 문서화
- [ ] **매핑 테이블 작성**: 원본 컬럼 → DB 필드 매핑 명시
- [ ] **샘플 검증**: 최소 10건의 데이터를 수동으로 대조
- [ ] **통계 검증**: 원본과 마이그레이션 후 데이터 수, 합계 등 비교
- [ ] **NULL 처리**: 누락된 데이터의 명시적 처리 (하드코딩 금지)

#### 4.4.3 검증 스크립트 필수
```python
# scripts/validate_migration.py
def validate_migration(source_file, target_table):
    """마이그레이션 검증 스크립트"""
    # 1. 원본 데이터 통계
    source_stats = get_source_statistics(source_file)

    # 2. DB 데이터 통계
    db_stats = get_db_statistics(target_table)

    # 3. 비교 리포트 생성
    report = compare_statistics(source_stats, db_stats)

    # 4. 누락된 필드 검출
    missing_fields = detect_missing_mappings(source_file, target_table)

    return report, missing_fields
```

## 5. 에러 처리

### 5.1 표준 에러 응답
```python
# Pydantic 검증 실패 → 422 Unprocessable Entity
# 비즈니스 로직 에러 → 400 Bad Request
raise HTTPException(
    status_code=400,
    detail={
        "code": "CUSTOMER_NOT_FOUND",
        "message": "고객을 찾을 수 없습니다",
        "data": {"customer_id": customer_id}
    }
)
```

### 5.2 에러 코드 체계
- `AUTH_*`: 인증/인가 관련
- `CUSTOMER_*`: 고객 관련
- `PAYMENT_*`: 결제 관련
- `SYSTEM_*`: 시스템 에러

## 6. 테스팅

### 6.1 테스트 피라미드
```
         /\
        /E2E\      10%
       /------\
      /  통합  \    20%
     /----------\
    /   단위     \  70%
   /--------------\
```

### 6.2 필수 테스트
- **Happy Path**: 정상 동작 케이스
- **Edge Cases**: 경계값 테스트
- **Error Cases**: 가장 흔한 에러 2가지

### 6.3 테스트 도구
- **Backend**: pytest, pytest-asyncio, pytest-cov
- **Frontend**: Jest, React Testing Library
- **E2E**: Playwright

> 🔗 상세 전략: [`test-strategy.md`](test-strategy.md)

## 7. 코드 리뷰 체크리스트

### PR 제출 전
- [ ] Lint 검사 통과
- [ ] 단위 테스트 커버리지 > 70%
- [ ] 문서/주석 업데이트
- [ ] 불필요한 console.log, print 제거

### 리뷰어 체크
- [ ] SOLID 원칙 준수
- [ ] 에러 처리 적절성
- [ ] 성능 영향도
- [ ] 보안 취약점

### 머지 전
- [ ] CI 모든 체크 통과
- [ ] 최소 1명 승인
- [ ] 충돌 해결 완료

---

## 🔗 관련 문서
- [글로벌 개발 원칙](../../CLAUDE.md)
- [백엔드 특화 규칙](../backend/CLAUDE.md)
- [프론트엔드 특화 규칙](../frontend/CLAUDE.md)
- [API 라우팅 스타일](api-routing-style.md)
- [테스트 전략](test-strategy.md)

## 📝 문서 이력
- 2025-06-22: 초안 작성 (backend/CLAUDE.md 중복 규칙 통합)
- 2025-06-24: 데이터 마이그레이션 검증 규칙 추가 (4.4절)

_관리 책임자: @dev-lead_
