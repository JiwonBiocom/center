"""
리드 테이블 구조 확인 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import inspect
from core.database import engine

def check_lead_table():
    """리드 테이블 구조 확인"""
    inspector = inspect(engine)
    
    # marketing_leads 테이블의 컬럼 정보 가져오기
    columns = inspector.get_columns('marketing_leads')
    
    print("=== marketing_leads 테이블 구조 ===")
    print(f"총 컬럼 수: {len(columns)}개\n")
    
    print("컬럼명 | 타입 | NULL 허용 | 기본값")
    print("-" * 60)
    
    for col in columns:
        nullable = "YES" if col['nullable'] else "NO"
        default = col.get('default', '')
        print(f"{col['name']:<25} | {str(col['type']):<15} | {nullable:<10} | {default}")
    
    # 인덱스 정보
    indexes = inspector.get_indexes('marketing_leads')
    print(f"\n=== 인덱스 정보 ===")
    for idx in indexes:
        print(f"- {idx['name']}: {', '.join(idx['column_names'])}")
    
    # 외래키 정보
    foreign_keys = inspector.get_foreign_keys('marketing_leads')
    print(f"\n=== 외래키 정보 ===")
    for fk in foreign_keys:
        print(f"- {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

if __name__ == "__main__":
    check_lead_table()