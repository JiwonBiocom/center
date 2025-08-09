#!/usr/bin/env python3
"""
Quick Schema Baseline Update Script

GitHub Actions에서 감지된 스키마 변경사항을 바탕으로 baseline을 업데이트합니다.
"""

import json
import os
from datetime import datetime
from pathlib import Path

def add_detected_tables_to_baseline():
    """감지된 새 테이블들을 baseline에 추가합니다."""
    baseline_path = Path(__file__).parent.parent / 'ci' / 'schema_baseline.json'

    if not baseline_path.exists():
        print(f"❌ Baseline 파일을 찾을 수 없습니다: {baseline_path}")
        return False

    # 기존 baseline 로드
    with open(baseline_path, 'r', encoding='utf-8') as f:
        baseline = json.load(f)

    # GitHub Actions에서 감지된 새 테이블들
    new_tables = {
        "staging_additional_fields": {
            "columns": [
                {
                    "name": "id",
                    "type": "integer",
                    "nullable": False,
                    "default": "nextval('staging_additional_fields_id_seq'::regclass)",
                    "max_length": None,
                    "precision": 32,
                    "scale": 0
                },
                {
                    "name": "table_name",
                    "type": "character varying",
                    "nullable": True,
                    "default": None,
                    "max_length": 255,
                    "precision": None,
                    "scale": None
                },
                {
                    "name": "field_data",
                    "type": "text",
                    "nullable": True,
                    "default": None,
                    "max_length": None,
                    "precision": None,
                    "scale": None
                },
                {
                    "name": "created_at",
                    "type": "timestamp without time zone",
                    "nullable": True,
                    "default": "CURRENT_TIMESTAMP",
                    "max_length": None,
                    "precision": None,
                    "scale": None
                }
            ],
            "indexes": [],
            "foreign_keys": []
        },
        "payments_additional_backup": {
            "columns": [
                {
                    "name": "payment_id",
                    "type": "integer",
                    "nullable": False,
                    "default": None,
                    "max_length": None,
                    "precision": 32,
                    "scale": 0
                },
                {
                    "name": "backup_data",
                    "type": "text",
                    "nullable": True,
                    "default": None,
                    "max_length": None,
                    "precision": None,
                    "scale": None
                },
                {
                    "name": "created_at",
                    "type": "timestamp without time zone",
                    "nullable": True,
                    "default": "CURRENT_TIMESTAMP",
                    "max_length": None,
                    "precision": None,
                    "scale": None
                }
            ],
            "indexes": [],
            "foreign_keys": []
        }
    }

    # 기존 baseline에 새 테이블들 추가
    baseline["tables"].update(new_tables)

    # payments 테이블에 card_holder_name 컬럼 추가
    if "payments" in baseline["tables"]:
        payments_columns = baseline["tables"]["payments"]["columns"]

        # card_holder_name 컬럼이 이미 있는지 확인
        has_card_holder = any(col["name"] == "card_holder_name" for col in payments_columns)

        if not has_card_holder:
            new_column = {
                "name": "card_holder_name",
                "type": "character varying",
                "nullable": True,
                "default": None,
                "max_length": 255,
                "precision": None,
                "scale": None
            }
            payments_columns.append(new_column)
            print("✅ payments 테이블에 card_holder_name 컬럼 추가")

    # 메타데이터 업데이트
    baseline["generated_at"] = datetime.now().isoformat()
    baseline["version"] = "1.1"

    # 백업 생성
    backup_path = baseline_path.with_suffix(f'.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    backup_path.write_text(baseline_path.read_text(), encoding='utf-8')
    print(f"📦 기존 baseline 백업: {backup_path}")

    # 새 baseline 저장
    with open(baseline_path, 'w', encoding='utf-8') as f:
        json.dump(baseline, f, indent=2, ensure_ascii=False)

    print(f"✅ Schema baseline 업데이트 완료: {baseline_path}")
    print(f"📊 새로 추가된 테이블: {len(new_tables)}개")
    print("   - staging_additional_fields")
    print("   - payments_additional_backup")
    print("📝 수정된 테이블: payments (card_holder_name 컬럼 추가)")

    return True

def main():
    """메인 실행 함수"""
    try:
        print("🔄 Schema baseline을 GitHub Actions 감지 결과로 업데이트 중...")

        if add_detected_tables_to_baseline():
            print("\n🎉 Schema baseline 업데이트가 완료되었습니다!")
            print("   이제 다음 명령어로 변경사항을 커밋하세요:")
            print("   git add ci/schema_baseline.json")
            print("   git commit -m 'chore: update schema baseline with detected changes'")
        else:
            print("❌ Schema baseline 업데이트에 실패했습니다.")
            return 1

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
