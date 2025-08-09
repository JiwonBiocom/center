#!/usr/bin/env python3
"""
데이터베이스 데이터 현황 확인 스크립트
각 테이블의 데이터 수를 확인하고 테스트 데이터 생성 필요성 판단
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 백엔드 디렉토리 추가
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# .env 파일 로드
env_path = backend_path / ".env"
load_dotenv(env_path)

# 데이터베이스 연결
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL이 설정되지 않았습니다.")
    sys.exit(1)

# 주요 테이블 목록
TABLES = [
    {"name": "users", "display": "사용자", "required": True},
    {"name": "customers", "display": "고객", "required": True},
    {"name": "services", "display": "서비스", "required": True},
    {"name": "packages", "display": "패키지", "required": True},
    {"name": "payments", "display": "결제", "required": True},
    {"name": "package_purchases", "display": "패키지 구매", "required": False},
    {"name": "service_usage", "display": "서비스 이용", "required": False},
    {"name": "notifications", "display": "알림", "required": False},
    {"name": "customer_leads", "display": "유입고객", "required": False},
    {"name": "lead_consultation_history", "display": "상담이력", "required": False},
    {"name": "reregistration_campaigns", "display": "재등록 캠페인", "required": False},
]

def check_data():
    """데이터베이스 데이터 현황 확인"""
    
    print("🔍 데이터베이스 데이터 현황 확인")
    print("="*70)
    print(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"DB: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'Unknown'}")
    print("="*70)
    
    engine = create_engine(DATABASE_URL)
    
    # 결과 저장
    results = {
        "total_tables": 0,
        "empty_tables": [],
        "populated_tables": [],
        "missing_tables": [],
        "data_count": {}
    }
    
    print("\n📊 테이블별 데이터 수:")
    print("-"*70)
    print(f"{'테이블명':<30} {'데이터 수':<15} {'상태':<20}")
    print("-"*70)
    
    with engine.connect() as conn:
        for table_info in TABLES:
            table_name = table_info["name"]
            display_name = table_info["display"]
            required = table_info["required"]
            
            try:
                # 데이터 수 확인
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                
                results["total_tables"] += 1
                results["data_count"][table_name] = count
                
                # 상태 판단
                if count == 0:
                    status = "❌ 비어있음" + (" (필수)" if required else "")
                    results["empty_tables"].append(table_name)
                    status_color = "🔴" if required else "⚠️"
                else:
                    status = f"✅ 데이터 있음"
                    results["populated_tables"].append(table_name)
                    status_color = "✅"
                
                print(f"{display_name:<28} {count:<15} {status_color} {status}")
                
                # 샘플 데이터 확인 (데이터가 있는 경우)
                if count > 0 and count <= 5:
                    # 첫 몇 개 데이터 확인
                    if table_name == "customers":
                        sample = conn.execute(text(f"SELECT id, name, email FROM {table_name} LIMIT 3"))
                        print(f"   └─ 샘플: ", end="")
                        for row in sample:
                            print(f"{row.name} ({row.email})", end=", ")
                        print()
                    elif table_name == "services":
                        sample = conn.execute(text(f"SELECT id, name FROM {table_name} LIMIT 3"))
                        print(f"   └─ 샘플: ", end="")
                        for row in sample:
                            print(f"{row.name}", end=", ")
                        print()
                
            except Exception as e:
                if "does not exist" in str(e):
                    print(f"{display_name:<28} {'N/A':<15} ❓ 테이블 없음")
                    results["missing_tables"].append(table_name)
                else:
                    print(f"{display_name:<28} {'ERROR':<15} ❌ 오류: {str(e)[:30]}...")
    
    # 요약
    print("\n"+"="*70)
    print("📈 요약:")
    print(f"   총 테이블: {results['total_tables']}개")
    print(f"   데이터 있음: {len(results['populated_tables'])}개")
    print(f"   비어있음: {len(results['empty_tables'])}개")
    if results["missing_tables"]:
        print(f"   존재하지 않음: {len(results['missing_tables'])}개")
    
    # 필수 테이블 중 비어있는 것
    empty_required = [t for t in results["empty_tables"] if any(table["name"] == t and table["required"] for table in TABLES)]
    
    if empty_required:
        print("\n🚨 필수 테이블 중 비어있는 것:")
        for table in empty_required:
            display = next(t["display"] for t in TABLES if t["name"] == table)
            print(f"   - {display} ({table})")
    
    # 권장사항
    print("\n💡 권장사항:")
    if empty_required:
        print("   1. 필수 테이블에 테스트 데이터 추가 필요")
        print("   2. 특히 customers, services, packages 테이블은 기본 데이터 필요")
        print("   3. payments는 customers와 packages 데이터 이후 생성 가능")
    else:
        print("   ✅ 모든 필수 테이블에 데이터가 있습니다!")
    
    # 테스트 데이터 생성 명령 제안
    if empty_required:
        print("\n🛠️ 테스트 데이터 생성 방법:")
        print("   python scripts/create_test_data.py")
        print("   또는")
        print("   python scripts/migrate_from_excel.py [엑셀파일경로]")
    
    return results

if __name__ == "__main__":
    check_data()