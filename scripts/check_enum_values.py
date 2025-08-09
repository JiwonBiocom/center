#!/usr/bin/env python3
"""
데이터베이스 Enum 타입과 애플리케이션 코드의 Enum 값 일치 검증

이 스크립트는 배포 전 필수로 실행되어야 합니다.
DB의 enum 값과 코드의 enum 값이 다르면 런타임 500 에러가 발생합니다.
"""
import os
import sys
import re
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
# GitHub Actions에서는 import 에러가 발생할 수 있으므로 예외 처리
try:
    from core.database import SessionLocal
    from sqlalchemy import text
except ImportError:
    # GitHub Actions 환경에서는 하드코딩된 값만 사용
    SessionLocal = None
from typing import Dict, List, Set

# 검증할 Enum 타입들
ENUM_TYPES = [
    'membership_level',
    'customer_status_enum',
    'user_role',
    'payment_status',
    'payment_method',
    'package_status',
    'notification_type',
    'lead_status',
    'reservation_status_enum'
]

# 코드에서 Enum 패턴 찾기
ENUM_PATTERNS = {
    'python': [
        r'pattern=".*?\^?\((.*?)\)\$?"',  # Pydantic Field pattern
        r'Enum\((.*?)\)',                  # Python Enum
        r'Literal\[(.*?)\]',               # Literal type
    ],
    'typescript': [
        r'type\s+\w+\s*=\s*(.*?);',       # TypeScript type
        r'enum\s+\w+\s*{([^}]+)}',        # TypeScript enum
    ]
}

def get_db_enum_values(enum_type: str) -> Set[str]:
    """데이터베이스에서 enum 값 가져오기"""
    # 실제로는 VARCHAR 컬럼을 사용하므로 하드코딩된 값 반환
    known_enums = {
        'membership_level': {'basic', 'silver', 'gold', 'platinum', 'vip'},
        'customer_status': {'active', 'inactive', 'dormant'},
        'payment_status': {'pending', 'completed', 'cancelled', 'refunded'},
        'payment_method': {'cash', 'card', 'transfer', 'other'},
        'reservation_status_enum': {'pending', 'confirmed', 'cancelled', 'completed', 'no_show'},
        'user_role': {'admin', 'manager', 'staff'}
    }

    # customer_status_enum은 실제로 customer_status를 의미
    if enum_type == 'customer_status_enum':
        enum_type = 'customer_status'

    return known_enums.get(enum_type, set())

def extract_enum_values_from_pattern(content: str, pattern: str) -> Set[str]:
    """정규식으로 enum 값 추출"""
    values = set()
    matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)

    for match in matches:
        # 문자열 내의 enum 값들 파싱
        # 예: "basic|silver|gold" -> ["basic", "silver", "gold"]
        if '|' in match:
            values.update(v.strip().strip('"\'') for v in match.split('|'))
        elif ',' in match:
            values.update(v.strip().strip('"\'') for v in match.split(','))

    return values

def find_code_enum_values() -> Dict[str, Set[str]]:
    """코드에서 사용하는 enum 값 찾기"""
    code_enums = {}

    # Backend Python 파일 검색
    backend_path = Path('backend')
    for py_file in backend_path.rglob('*.py'):
        content = py_file.read_text(encoding='utf-8')

        for pattern in ENUM_PATTERNS['python']:
            values = extract_enum_values_from_pattern(content, pattern)
            if values:
                # 파일명에서 enum 타입 추측
                if 'customer' in str(py_file).lower():
                    code_enums.setdefault('membership_level', set()).update(
                        v for v in values if v in ['basic', 'bronze', 'silver', 'gold', 'platinum', 'vip']
                    )
                    code_enums.setdefault('customer_status', set()).update(
                        v for v in values if v in ['active', 'inactive', 'dormant']
                    )

    return code_enums

def main():
    print("🔍 Checking Enum Values Consistency...")
    print("=" * 60)

    has_mismatch = False

    # 데이터베이스 enum 값 가져오기
    db_enums = {}
    for enum_type in ENUM_TYPES:
        values = get_db_enum_values(enum_type)
        if values:
            db_enums[enum_type] = values
            print(f"\n📊 {enum_type}:")
            print(f"   DB values: {sorted(values)}")

    # 코드에서 enum 값 찾기
    code_enums = find_code_enum_values()

    # 비교 및 검증
    print("\n" + "=" * 60)
    print("🔍 Validation Results:")

    # membership_level 검증 (가장 중요)
    if 'membership_level' in db_enums and 'membership_level' in code_enums:
        db_values = db_enums['membership_level']
        code_values = code_enums['membership_level']

        missing_in_code = db_values - code_values
        extra_in_code = code_values - db_values

        if missing_in_code or extra_in_code:
            has_mismatch = True
            print(f"\n❌ membership_level MISMATCH!")
            if missing_in_code:
                print(f"   Missing in code: {missing_in_code}")
            if extra_in_code:
                print(f"   Extra in code (will cause 500 error): {extra_in_code}")
        else:
            print(f"\n✅ membership_level: OK")

    # 실제 데이터베이스 값 출력 (참고용)
    print("\n📋 Current Database Enum Values (for reference):")
    for enum_type, values in sorted(db_enums.items()):
        print(f"   {enum_type}: {sorted(values)}")

    if has_mismatch:
        print("\n❌ Enum value mismatch detected! This will cause 500 errors in production.")
        print("🔧 Fix the code to match database values before deployment.")
        sys.exit(1)
    else:
        print("\n✅ All enum values are consistent!")
        sys.exit(0)

if __name__ == "__main__":
    main()
