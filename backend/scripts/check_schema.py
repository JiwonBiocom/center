#!/usr/bin/env python3
"""
데이터베이스 스키마 확인 유틸리티
API 개발 전에 실행하여 실제 DB 구조를 확인할 수 있습니다.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine
from sqlalchemy import inspect
import argparse

def check_table_exists(table_name):
    """특정 테이블의 존재 여부 확인"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if table_name in tables:
        print(f"✅ 테이블 '{table_name}'이(가) 존재합니다.")
        return True
    else:
        print(f"❌ 테이블 '{table_name}'이(가) 존재하지 않습니다.")
        print(f"   사용 가능한 유사한 테이블: {[t for t in tables if table_name.lower() in t.lower()]}")
        return False

def check_column_exists(table_name, column_name):
    """특정 컬럼의 존재 여부 확인"""
    inspector = inspect(engine)
    
    if not check_table_exists(table_name):
        return False
    
    columns = inspector.get_columns(table_name)
    column_names = [col['name'] for col in columns]
    
    if column_name in column_names:
        print(f"✅ 컬럼 '{table_name}.{column_name}'이(가) 존재합니다.")
        return True
    else:
        print(f"❌ 컬럼 '{table_name}.{column_name}'이(가) 존재하지 않습니다.")
        print(f"   사용 가능한 컬럼: {column_names}")
        return False

def show_table_structure(table_name):
    """테이블 구조 표시"""
    inspector = inspect(engine)
    
    if not check_table_exists(table_name):
        return
    
    print(f"\n📋 {table_name} 테이블 구조:")
    print("-" * 60)
    
    columns = inspector.get_columns(table_name)
    for col in columns:
        nullable = "NULL" if col['nullable'] else "NOT NULL"
        print(f"  - {col['name']:<25} {str(col['type']):<20} {nullable}")
    
    # Foreign Keys
    fks = inspector.get_foreign_keys(table_name)
    if fks:
        print("\n  Foreign Keys:")
        for fk in fks:
            print(f"    - {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}")
    
    # Indexes
    indexes = inspector.get_indexes(table_name)
    if indexes:
        print("\n  Indexes:")
        for idx in indexes:
            print(f"    - {idx['name']}: {idx['column_names']}")

def list_all_tables():
    """모든 테이블 목록 표시"""
    inspector = inspect(engine)
    tables = sorted(inspector.get_table_names())
    
    print("📊 데이터베이스의 모든 테이블:")
    print("-" * 60)
    
    # 카테고리별로 그룹화
    categories = {
        '고객 관련': ['customers', 'customer_preferences', 'customer_analytics'],
        '패키지 관련': ['packages', 'package_purchases'],
        '서비스 관련': ['service_usage', 'service_types', 'reservations'],
        '결제 관련': ['payments'],
        '시스템': ['users', 'system_settings'],
        '기타': []
    }
    
    # 테이블 분류
    categorized = set()
    for category, patterns in categories.items():
        category_tables = []
        for table in tables:
            for pattern in patterns:
                if pattern in table:
                    category_tables.append(table)
                    categorized.add(table)
                    break
        
        if category_tables:
            print(f"\n{category}:")
            for table in sorted(category_tables):
                print(f"  - {table}")
    
    # 분류되지 않은 테이블
    uncategorized = set(tables) - categorized
    if uncategorized:
        print("\n기타:")
        for table in sorted(uncategorized):
            print(f"  - {table}")

def main():
    parser = argparse.ArgumentParser(description='데이터베이스 스키마 확인 도구')
    parser.add_argument('--table', '-t', help='특정 테이블 구조 확인')
    parser.add_argument('--column', '-c', help='특정 컬럼 존재 확인 (예: payments.payment_status)')
    parser.add_argument('--list', '-l', action='store_true', help='모든 테이블 목록 표시')
    
    args = parser.parse_args()
    
    if args.column:
        if '.' in args.column:
            table, column = args.column.split('.')
            check_column_exists(table, column)
        else:
            print("❌ 컬럼은 'table.column' 형식으로 지정해주세요.")
    elif args.table:
        show_table_structure(args.table)
    elif args.list:
        list_all_tables()
    else:
        # 기본: 주요 테이블 구조 표시
        print("🔍 주요 테이블 구조 확인")
        print("=" * 60)
        
        main_tables = ['customers', 'packages', 'package_purchases', 'payments', 'service_usage']
        for table in main_tables:
            show_table_structure(table)
            print()

if __name__ == "__main__":
    main()