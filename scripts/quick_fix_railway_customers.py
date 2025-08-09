#!/usr/bin/env python3
"""
Railway 백엔드 customers API 500 에러 빠른 수정
birth_date -> birth_year 변경 누락 부분 수정
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    print("=== Railway Customers API 500 에러 수정 ===")
    print("\n수정 내용:")
    print("1. customers.py의 엑셀 import/export에서 birth_date -> birth_year 변경")
    print("2. ExcelHandler에 parse_year 메서드 추가")
    
    # 파일 경로
    customers_file = project_root / "backend" / "api" / "v1" / "customers.py"
    excel_utils_file = project_root / "backend" / "utils" / "excel.py"
    
    print(f"\n✅ 수정된 파일:")
    print(f"   - {customers_file}")
    print(f"   - {excel_utils_file}")
    
    print("\n🚀 Railway에 배포하는 방법:")
    print("1. git add backend/api/v1/customers.py backend/utils/excel.py")
    print("2. git commit -m 'fix: customers API birth_date -> birth_year 변경 누락 수정'")
    print("3. git push")
    print("\nRailway는 자동으로 배포를 시작합니다.")
    
    print("\n📝 변경 사항 요약:")
    print("- import_customers_from_excel: birth_date -> birth_year")
    print("- export_customers_to_excel: 생년월일 -> 출생연도")
    print("- ExcelHandler.parse_year 메서드 추가 (날짜에서 연도 추출)")

if __name__ == "__main__":
    main()