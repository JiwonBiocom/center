# 데이터베이스 종합 가이드

> 이 문서는 데이터베이스 스키마, 보호 가이드, 작업 규칙을 통합한 종합 문서입니다.
> DATABASE_PROTECTION_GUIDE.md의 내용이 이 문서로 통합되었습니다.

최종 업데이트: 2025-06-08

## 📋 목차
1. [데이터베이스 보호 원칙](#데이터베이스-보호-원칙)
2. [주요 테이블 구조](#주요-테이블-구조)
3. [명명 규칙](#명명-규칙)
4. [주의사항](#주의사항)
5. [스키마 확인 방법](#스키마-확인-방법)
6. [백업 및 복구](#백업-및-복구)
7. [위험한 작업 방지](#위험한-작업-방지)

## 데이터베이스 보호 원칙

### ⚠️ 절대 금지 사항
1. **`init_db.py` 실행 금지** - 모든 테이블을 삭제하는 위험한 스크립트
2. **`drop_all()`, `TRUNCATE`, `DROP TABLE` 사용 금지**
3. **프로덕션 환경에서 직접 쿼리 실행 금지**

### ✅ 안전한 작업 방법
1. **테이블 생성**: `scripts/safe_create_tables.py` 사용
2. **마이그레이션**: Alembic 같은 마이그레이션 도구 사용
3. **환경 변수 설정**: `.env`에 `ENVIRONMENT=production` 추가
4. **백업 우선**: 중요한 작업 전 반드시 백업 실행

### 🛡️ 프로덕션 환경 보호
```python
# init_db.py에 추가해야 할 안전장치
if os.getenv('ENVIRONMENT') == 'production':
    raise Exception("Cannot drop tables in production!")
```

## 주요 테이블 구조

### customers (고객)
```sql
- customer_id: INTEGER (PK)
- name: VARCHAR(50)
- phone: VARCHAR(20)
- email: VARCHAR(100)
- first_visit_date: DATE
- last_visit_date: DATE
- total_visits: INTEGER
- region: VARCHAR(50)
- referral_source: VARCHAR(50)
- health_concerns: TEXT
- notes: TEXT
- membership_level: VARCHAR(20)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

### packages (패키지)
```sql
- package_id: INTEGER (PK)
- package_name: VARCHAR(100)
- total_sessions: INTEGER
- price: NUMERIC(10, 2)
- valid_days: INTEGER  -- NOT validity_months!
- description: VARCHAR(500)
- is_active: BOOLEAN
- created_at: TIMESTAMP
```

### package_purchases (패키지 구매)
```sql
- purchase_id: INTEGER (PK)
- customer_id: INTEGER (FK)
- package_id: INTEGER (FK)
- purchase_date: DATE
- expiry_date: DATE
- total_sessions: INTEGER
- used_sessions: INTEGER
- remaining_sessions: INTEGER
- created_at: TIMESTAMP
```
**주의**: customer_packages나 package_usage 테이블은 존재하지 않음!

### payments (결제)
```sql
- payment_id: INTEGER (PK)
- customer_id: INTEGER (FK)
- payment_date: DATE
- amount: NUMERIC(10, 2)
- payment_method: VARCHAR(20)
- card_holder_name: VARCHAR(50)
- approval_number: VARCHAR(50)
- payment_staff: VARCHAR(50)
- purchase_type: VARCHAR(100)
- purchase_order: INTEGER
- service_type: VARCHAR(255)
- memo: TEXT
- created_at: TIMESTAMP
```
**주의**: payment_status, description, created_by 컬럼은 존재하지 않음!

### service_usage (서비스 이용)
```sql
- usage_id: INTEGER (PK)
- customer_id: INTEGER (FK)
- service_date: DATE
- service_name: VARCHAR(50)
- service_duration: INTEGER
- therapist_name: VARCHAR(50)
- room_number: VARCHAR(20)
- notes: TEXT
- package_used: BOOLEAN
- package_purchase_id: INTEGER (FK)
- created_at: TIMESTAMP
```

### users (사용자/직원)
```sql
- user_id: INTEGER (PK)
- email: VARCHAR(100)  -- NOT username!
- password_hash: VARCHAR(255)
- name: VARCHAR(50)
- role: VARCHAR(20)
- is_active: BOOLEAN
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

### reservations (예약)
```sql
- reservation_id: INTEGER (PK)
- customer_id: INTEGER (FK)
- service_type: VARCHAR(50)
- reservation_date: DATE
- start_time: TIME
- end_time: TIME
- status: VARCHAR(20)
- therapist_name: VARCHAR(50)
- room_number: VARCHAR(20)
- notes: TEXT
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

### customer_preferences (고객 선호도)
```sql
- preference_id: INTEGER (PK)
- customer_id: INTEGER (FK)
- preferred_service: VARCHAR(100)
- preferred_therapist: VARCHAR(100)
- preferred_time: VARCHAR(50)
- preferred_day: VARCHAR(20)
- notes: TEXT
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

### inbody_records (인바디 기록)
```sql
- record_id: INTEGER (PK)
- customer_id: INTEGER (FK)
- measurement_date: DATE
- weight: NUMERIC(5, 2)
- muscle_mass: NUMERIC(5, 2)
- body_fat_mass: NUMERIC(5, 2)
- body_fat_percentage: NUMERIC(5, 2)
- bmi: NUMERIC(5, 2)
- basal_metabolic_rate: INTEGER
- visceral_fat_level: INTEGER
- created_at: TIMESTAMP
```

## 명명 규칙

1. **테이블명**: 복수형 사용 (customers, packages, payments)
2. **Primary Key**: `{table_singular}_id` (customer_id, package_id)
3. **날짜 컬럼**: `_date` 접미사 (purchase_date, payment_date)
4. **Boolean 컬럼**: `is_` 접두사 (is_active)
5. **타임스탬프**: created_at, updated_at

## 주의사항

1. **존재하지 않는 테이블**:
   - customer_packages ❌
   - package_usage ❌
   - customer_service_usage ❌

2. **자주 착각하는 컬럼명**:
   - packages.validity_months ❌ → packages.valid_days ✅
   - users.username ❌ → users.email ✅
   - payments.payment_status ❌ (존재하지 않음)

3. **관계**:
   - 고객의 패키지 구매 → package_purchases 테이블
   - 서비스 이용 기록 → service_usage 테이블
   - 결제 정보 → payments 테이블

## 데이터베이스 스키마 확인 방법

```python
from core.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)

# 모든 테이블 목록
tables = inspector.get_table_names()
print("Tables:", tables)

# 특정 테이블의 컬럼 정보
columns = inspector.get_columns('table_name')
for col in columns:
    print(f"{col['name']}: {col['type']}")
```

## 백업 및 복구

### 백업 전략
1. **매일 자동 백업**: cron job으로 설정
2. **중요 작업 전 수동 백업**: 
   ```bash
   python scripts/backup_database.py
   ```
3. **백업 파일 관리**: 
   - 최소 7일치 백업 유지
   - 외부 저장소에 추가 백업

### 긴급 복구 방법
1. **백업에서 복원**:
   ```bash
   psql -d database_name < backup.sql
   ```

2. **Excel 파일에서 재마이그레이션**:
   ```bash
   python scripts/migrate_real_data.py
   ```

3. **특정 테이블만 복원**:
   ```bash
   psql -d database_name -c "TRUNCATE table_name;"
   psql -d database_name < table_backup.sql
   ```

## 위험한 작업 방지

### 권장 폴더 구조
```
backend/
├── scripts/
│   ├── safe/          # 안전한 스크립트
│   └── dangerous/     # 위험한 스크립트 (init_db.py 등)
└── core/
    └── init_db.py     # 삭제하거나 안전하게 수정
```

### 체크리스트
- [ ] init_db.py 파일 수정 또는 삭제
- [ ] 환경 변수 설정 확인
- [ ] 백업 시스템 구축
- [ ] 팀원들에게 주의사항 공유
- [ ] 위험한 스크립트 격리

### 모니터링
- 데이터베이스 변경 로그 활성화
- 테이블 삭제 시 알림 설정
- 정기적인 데이터 무결성 체크

---

**중요**: 
- API나 모델 작업 전에 반드시 이 문서를 확인하고, 변경사항이 있으면 즉시 업데이트할 것!
- 데이터베이스 작업 시 반드시 백업을 먼저 수행할 것!
- 의심스러운 명령은 실행 전에 반드시 검토할 것!