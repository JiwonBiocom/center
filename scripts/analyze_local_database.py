#!/usr/bin/env python3
"""
로컬 SQLite 데이터베이스 전체 분석
Phase 1: 데이터 현황 파악
"""
import sqlite3
from pathlib import Path
import json
from datetime import datetime

def analyze_local_database():
    """로컬 데이터베이스 전체 분석"""
    
    print("🔍 로컬 데이터베이스 전체 분석 시작")
    print("=" * 70)
    
    # 로컬 데이터베이스 경로
    db_path = Path("backend/aibio_center.db")
    
    if not db_path.exists():
        print(f"❌ 데이터베이스 파일을 찾을 수 없습니다: {db_path}")
        return None
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    analysis_result = {
        "analysis_date": datetime.now().isoformat(),
        "database_path": str(db_path),
        "tables": {},
        "total_records": 0,
        "total_tables": 0
    }
    
    try:
        # 1. 모든 테이블 목록 가져오기
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = cursor.fetchall()
        
        print(f"\n📊 발견된 테이블: {len(tables)}개")
        print("-" * 70)
        
        # 2. 각 테이블 분석
        for table_name, in tables:
            # 레코드 수
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            record_count = cursor.fetchone()[0]
            
            # 컬럼 정보
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # 샘플 데이터 (최대 3개)
            sample_data = []
            if record_count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                sample_rows = cursor.fetchall()
                column_names = [col[1] for col in columns]
                sample_data = [dict(zip(column_names, row)) for row in sample_rows]
            
            # 외래키 정보
            cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            foreign_keys = cursor.fetchall()
            
            table_info = {
                "record_count": record_count,
                "columns": [
                    {
                        "name": col[1],
                        "type": col[2],
                        "nullable": not col[3],
                        "primary_key": bool(col[5])
                    } for col in columns
                ],
                "foreign_keys": [
                    {
                        "column": fk[3],
                        "references_table": fk[2],
                        "references_column": fk[4]
                    } for fk in foreign_keys
                ],
                "sample_data": sample_data
            }
            
            analysis_result["tables"][table_name] = table_info
            analysis_result["total_records"] += record_count
            
            # 콘솔 출력
            print(f"\n📋 {table_name}")
            print(f"   레코드 수: {record_count:,}개")
            print(f"   컬럼 수: {len(columns)}개")
            if foreign_keys:
                print(f"   외래키: {len(foreign_keys)}개")
            
            # 중요 테이블 상세 정보
            if table_name in ['payments', 'packages', 'services', 'package_purchases']:
                print("   주요 컬럼:")
                for col in columns[:5]:  # 처음 5개만
                    print(f"     - {col[1]} ({col[2]})")
        
        analysis_result["total_tables"] = len(tables)
        
        # 3. 특별 분석: payments 테이블의 누락된 필드 확인
        print("\n" + "=" * 70)
        print("💰 payments 테이블 특별 분석")
        print("-" * 70)
        
        # NULL이 아닌 값이 있는 필드 확인
        payment_fields = ['payment_staff', 'purchase_type', 'card_holder_name', 'approval_number']
        for field in payment_fields:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM payments WHERE {field} IS NOT NULL AND {field} != ''")
                non_null_count = cursor.fetchone()[0]
                print(f"   {field}: {non_null_count}개 데이터 존재")
                
                if non_null_count > 0:
                    # 샘플 데이터
                    cursor.execute(f"SELECT DISTINCT {field} FROM payments WHERE {field} IS NOT NULL AND {field} != '' LIMIT 5")
                    samples = [row[0] for row in cursor.fetchall()]
                    print(f"     샘플: {samples}")
            except:
                print(f"   {field}: 컬럼 없음")
        
        # 4. 의존성 분석
        print("\n" + "=" * 70)
        print("🔗 테이블 의존성 분석")
        print("-" * 70)
        
        dependencies = {}
        for table_name in analysis_result["tables"]:
            fks = analysis_result["tables"][table_name]["foreign_keys"]
            if fks:
                dependencies[table_name] = [fk["references_table"] for fk in fks]
                print(f"   {table_name} → {', '.join(dependencies[table_name])}")
        
        # 5. 마이그레이션 우선순위 제안
        print("\n" + "=" * 70)
        print("📌 마이그레이션 우선순위 제안")
        print("-" * 70)
        
        # 의존성이 없는 테이블부터
        priority_tables = []
        for table in analysis_result["tables"]:
            if not analysis_result["tables"][table]["foreign_keys"]:
                priority_tables.append((table, analysis_result["tables"][table]["record_count"]))
        
        priority_tables.sort(key=lambda x: x[1], reverse=True)
        
        print("\n1단계 (독립 테이블):")
        for table, count in priority_tables[:5]:
            print(f"   - {table}: {count:,}개")
        
        # 결과 저장
        output_path = Path("local_db_analysis.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n✅ 분석 완료! 상세 결과: {output_path}")
        print(f"📊 총 {analysis_result['total_tables']}개 테이블, {analysis_result['total_records']:,}개 레코드")
        
        conn.close()
        return analysis_result
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        conn.close()
        return None

if __name__ == "__main__":
    analyze_local_database()