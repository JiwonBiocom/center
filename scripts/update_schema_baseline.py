#!/usr/bin/env python3
"""
스키마 베이스라인에 새로운 테이블 추가
"""
import json
from datetime import datetime

# 기존 베이스라인 읽기
with open('ci/schema_baseline.json', 'r', encoding='utf-8') as f:
    baseline = json.load(f)

# unreflected_customers 테이블 추가
baseline['tables']['unreflected_customers'] = {
    "columns": [
        {"name": "id", "type": "integer", "nullable": False, "default": "nextval('unreflected_customers_id_seq'::regclass)", "max_length": None, "precision": 32, "scale": 0},
        {"name": "original_customer_id", "type": "integer", "nullable": True, "default": None, "max_length": None, "precision": 32, "scale": 0},
        {"name": "name", "type": "character varying", "nullable": False, "default": None, "max_length": 100, "precision": None, "scale": None},
        {"name": "phone", "type": "character varying", "nullable": True, "default": None, "max_length": 20, "precision": None, "scale": None},
        {"name": "email", "type": "character varying", "nullable": True, "default": None, "max_length": 100, "precision": None, "scale": None},
        {"name": "first_visit_date", "type": "date", "nullable": True, "default": None, "max_length": None, "precision": None, "scale": None},
        {"name": "region", "type": "character varying", "nullable": True, "default": None, "max_length": 100, "precision": None, "scale": None},
        {"name": "referral_source", "type": "character varying", "nullable": True, "default": None, "max_length": 100, "precision": None, "scale": None},
        {"name": "health_concerns", "type": "text", "nullable": True, "default": None, "max_length": None, "precision": None, "scale": None},
        {"name": "notes", "type": "text", "nullable": True, "default": None, "max_length": None, "precision": None, "scale": None},
        {"name": "assigned_staff", "type": "character varying", "nullable": True, "default": None, "max_length": 50, "precision": None, "scale": None},
        {"name": "birth_year", "type": "integer", "nullable": True, "default": None, "max_length": None, "precision": 32, "scale": 0},
        {"name": "gender", "type": "character varying", "nullable": True, "default": None, "max_length": 10, "precision": None, "scale": None},
        {"name": "address", "type": "text", "nullable": True, "default": None, "max_length": None, "precision": None, "scale": None},
        {"name": "emergency_contact", "type": "character varying", "nullable": True, "default": None, "max_length": 20, "precision": None, "scale": None},
        {"name": "occupation", "type": "character varying", "nullable": True, "default": None, "max_length": 100, "precision": None, "scale": None},
        {"name": "data_source", "type": "character varying", "nullable": True, "default": None, "max_length": 200, "precision": None, "scale": None},
        {"name": "import_date", "type": "timestamp without time zone", "nullable": True, "default": "now()", "max_length": None, "precision": None, "scale": None},
        {"name": "import_notes", "type": "text", "nullable": True, "default": None, "max_length": None, "precision": None, "scale": None},
        {"name": "created_at", "type": "timestamp without time zone", "nullable": True, "default": "now()", "max_length": None, "precision": None, "scale": None},
        {"name": "updated_at", "type": "timestamp without time zone", "nullable": True, "default": None, "max_length": None, "precision": None, "scale": None},
        {"name": "status", "type": "character varying", "nullable": True, "default": "'pending'::character varying", "max_length": 20, "precision": None, "scale": None}
    ],
    "indexes": [],
    "foreign_keys": []
}

# alembic_version 테이블 추가
baseline['tables']['alembic_version'] = {
    "columns": [
        {"name": "version_num", "type": "character varying", "nullable": False, "default": None, "max_length": 32, "precision": None, "scale": None}
    ],
    "indexes": [],
    "foreign_keys": []
}

# 타임스탬프 업데이트
baseline['generated_at'] = datetime.now().isoformat()

# 저장
with open('ci/schema_baseline.json', 'w', encoding='utf-8') as f:
    json.dump(baseline, f, indent=2, ensure_ascii=False)

print("✅ 스키마 베이스라인 업데이트 완료")
print("   - unreflected_customers 테이블 추가")
print("   - alembic_version 테이블 추가")
