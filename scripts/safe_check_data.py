#!/usr/bin/env python3
"""
안전한 데이터베이스 데이터 확인 스크립트
각 쿼리를 독립적인 트랜잭션으로 실행
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import psycopg2
from psycopg2 import sql

# 프로젝트 루트 디렉토리
project_root = Path(__file__).parent.parent
backend_path = project_root / "backend"

# .env 파일 로드
from dotenv import load_dotenv
env_path = backend_path / ".env"
load_dotenv(env_path)

# 데이터베이스 연결 정보
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL이 설정되지 않았습니다.")
    sys.exit(1)

# 테이블 목록
TABLES = [
    "users",
    "customers", 
    "services",
    "packages",
    "payments",
    "package_purchases",
    "service_usage",
    "notifications",
    "customer_leads",
    "lead_consultation_history",
    "reregistration_campaigns",
]

def check_table_data(table_name):
    """개별 테이블 데이터 확인"""
    conn = None
    try:
        # 각 테이블마다 새로운 연결
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True  # 자동 커밋 모드
        
        with conn.cursor() as cursor:
            # 테이블 존재 여부 확인
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, (table_name,))
            
            exists = cursor.fetchone()[0]
            
            if not exists:
                return {"exists": False, "count": None, "sample": None}
            
            # 데이터 수 확인
            query = sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table_name))
            cursor.execute(query)
            count = cursor.fetchone()[0]
            
            # 샘플 데이터 (3개까지)
            sample = None
            if count > 0:
                if table_name == "customers":
                    cursor.execute(f"SELECT id, name, email FROM {table_name} LIMIT 3")
                    sample = [{"id": r[0], "name": r[1], "email": r[2]} for r in cursor.fetchall()]
                elif table_name == "services":
                    cursor.execute(f"SELECT id, name, price FROM {table_name} LIMIT 3")
                    sample = [{"id": r[0], "name": r[1], "price": r[2]} for r in cursor.fetchall()]
                elif table_name == "packages":
                    cursor.execute(f"SELECT id, name, price FROM {table_name} LIMIT 3")
                    sample = [{"id": r[0], "name": r[1], "price": r[2]} for r in cursor.fetchall()]
            
            return {"exists": True, "count": count, "sample": sample}
            
    except Exception as e:
        return {"exists": True, "count": None, "error": str(e)}
    finally:
        if conn:
            conn.close()

def main():
    """메인 함수"""
    print("🔍 데이터베이스 데이터 현황 확인 (안전 모드)")
    print("="*70)
    print(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # 결과 저장
    results = {
        "total": 0,
        "exists": 0,
        "has_data": 0,
        "empty": 0,
        "missing": 0,
        "errors": 0,
        "details": {}
    }
    
    print("\n📊 테이블별 상태:")
    print("-"*70)
    print(f"{'테이블명':<25} {'상태':<15} {'데이터 수':<15} {'비고'}")
    print("-"*70)
    
    for table_name in TABLES:
        result = check_table_data(table_name)
        results["total"] += 1
        results["details"][table_name] = result
        
        if not result["exists"]:
            status = "❓ 없음"
            count_str = "-"
            note = "테이블이 존재하지 않음"
            results["missing"] += 1
        elif result.get("error"):
            status = "❌ 에러"
            count_str = "-"
            note = result["error"][:30] + "..."
            results["errors"] += 1
        elif result["count"] == 0:
            status = "⚠️ 비어있음"
            count_str = "0"
            note = "데이터 추가 필요"
            results["exists"] += 1
            results["empty"] += 1
        else:
            status = "✅ 정상"
            count_str = str(result["count"])
            note = ""
            results["exists"] += 1
            results["has_data"] += 1
            
            # 샘플 데이터 표시
            if result.get("sample") and len(result["sample"]) > 0:
                if table_name == "customers":
                    samples = [f"{s['name']} ({s['email']})" for s in result["sample"][:2]]
                    note = "예: " + ", ".join(samples)
                elif table_name in ["services", "packages"]:
                    samples = [f"{s['name']} (₩{s['price']:,})" for s in result["sample"][:2]]
                    note = "예: " + ", ".join(samples)
        
        print(f"{table_name:<25} {status:<15} {count_str:<15} {note}")
    
    # 요약
    print("\n"+"="*70)
    print("📈 요약:")
    print(f"   확인한 테이블: {results['total']}개")
    print(f"   존재하는 테이블: {results['exists']}개")
    print(f"   데이터 있음: {results['has_data']}개")
    print(f"   비어있음: {results['empty']}개")
    print(f"   존재하지 않음: {results['missing']}개")
    if results['errors'] > 0:
        print(f"   에러 발생: {results['errors']}개")
    
    # 권장사항
    print("\n💡 권장사항:")
    
    # 필수 테이블 확인
    essential_tables = ["customers", "services", "packages", "payments"]
    missing_essential = []
    empty_essential = []
    
    for table in essential_tables:
        if not results["details"][table]["exists"]:
            missing_essential.append(table)
        elif results["details"][table].get("count") == 0:
            empty_essential.append(table)
    
    if missing_essential:
        print(f"\n🚨 필수 테이블이 없습니다: {', '.join(missing_essential)}")
        print("   → 스키마 마이그레이션이 필요합니다")
    
    if empty_essential:
        print(f"\n⚠️ 필수 테이블이 비어있습니다: {', '.join(empty_essential)}")
        print("   → 테스트 데이터 추가가 필요합니다")
        print("\n   다음 명령으로 테스트 데이터를 생성하세요:")
        print("   python scripts/create_test_data.py")
    
    if not missing_essential and not empty_essential:
        print("\n✅ 모든 필수 테이블에 데이터가 있습니다!")
        
        # 고객 데이터가 많은 경우
        if results["details"]["customers"].get("count", 0) > 100:
            print(f"   - 고객 데이터: {results['details']['customers']['count']}명")
            print("   - 충분한 테스트 데이터가 있습니다")

if __name__ == "__main__":
    main()