#!/usr/bin/env python3
"""
인바디 테이블 생성 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine
from models.inbody import InBodyRecord
from sqlalchemy import inspect

def create_inbody_table():
    """인바디 테이블 생성"""
    inspector = inspect(engine)
    
    # 테이블이 이미 존재하는지 확인
    if inspector.has_table('inbody_records'):
        print("✅ inbody_records 테이블이 이미 존재합니다.")
        return
    
    try:
        # 테이블 생성
        InBodyRecord.metadata.create_all(bind=engine)
        print("✅ inbody_records 테이블이 성공적으로 생성되었습니다.")
        
        # 테이블 구조 확인
        columns = inspector.get_columns('inbody_records')
        print("\n📋 테이블 구조:")
        for column in columns:
            print(f"  - {column['name']}: {column['type']}")
            
    except Exception as e:
        print(f"❌ 테이블 생성 실패: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 인바디 테이블 생성을 시작합니다...")
    create_inbody_table()
    print("✨ 작업 완료!")