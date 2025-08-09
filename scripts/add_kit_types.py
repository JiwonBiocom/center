"""
검사키트 종류 데이터 추가 스크립트
"""
import sys
import os
from datetime import datetime

# backend 디렉토리를 Python 경로에 추가
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_path)

from core.database import SessionLocal, engine, Base
from sqlalchemy import text

# 검사키트 종류 정의
KIT_TYPES = [
    {
        'name': '종합 대사기능 검사',
        'code': 'METABOLIC',
        'description': '신체의 전반적인 대사 기능을 종합적으로 분석하는 검사',
        'price': 350000
    },
    {
        'name': '음식물 과민증 검사',
        'code': 'FOOD_SENSITIVITY',
        'description': '특정 음식물에 대한 과민 반응을 검사하여 맞춤형 식단 제공',
        'price': 280000
    },
    {
        'name': '영양 중금속 검사',
        'code': 'NUTRIENT_HEAVY_METAL',
        'description': '체내 영양소 상태와 중금속 축적도를 동시에 분석',
        'price': 320000
    },
    {
        'name': '스트레스 호르몬 검사',
        'code': 'STRESS_HORMONE',
        'description': '코티솔 등 스트레스 관련 호르몬 수치를 측정하여 스트레스 상태 평가',
        'price': 250000
    },
    {
        'name': '마이크로바이옴 검사',
        'code': 'MICROBIOME',
        'description': '장내 미생물 균형 상태를 분석하여 장 건강 평가',
        'price': 450000
    }
]

def create_kit_types_table():
    """검사키트 종류 테이블 생성"""
    db = SessionLocal()
    try:
        # 테이블이 없으면 생성
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS kit_types (
            kit_type_id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            code VARCHAR(50) UNIQUE NOT NULL,
            description TEXT,
            price INTEGER NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        db.execute(text(create_table_sql))
        db.commit()
        print("kit_types 테이블이 생성되었습니다.")
    except Exception as e:
        print(f"테이블 생성 중 오류: {e}")
        db.rollback()
    finally:
        db.close()

def add_kit_types():
    """검사키트 종류 데이터 추가"""
    db = SessionLocal()
    try:
        # 기존 데이터 확인
        existing_count = db.execute(text("SELECT COUNT(*) FROM kit_types")).scalar()
        if existing_count > 0:
            print(f"이미 {existing_count}개의 키트 종류가 등록되어 있습니다.")
            return
        
        # 데이터 추가
        for kit_type in KIT_TYPES:
            insert_sql = """
            INSERT INTO kit_types (name, code, description, price)
            VALUES (:name, :code, :description, :price)
            """
            db.execute(text(insert_sql), kit_type)
        
        db.commit()
        print(f"{len(KIT_TYPES)}개의 검사키트 종류가 추가되었습니다.")
        
        # 추가된 데이터 확인
        result = db.execute(text("SELECT kit_type_id, name, code, price FROM kit_types ORDER BY kit_type_id"))
        print("\n추가된 검사키트 목록:")
        for row in result:
            print(f"- ID: {row[0]}, 이름: {row[1]}, 코드: {row[2]}, 가격: {row[3]:,}원")
            
    except Exception as e:
        print(f"데이터 추가 중 오류: {e}")
        db.rollback()
    finally:
        db.close()

def update_kit_management_table():
    """kit_management 테이블에 kit_type_id 컬럼 추가"""
    db = SessionLocal()
    try:
        # kit_type_id 컬럼 추가 (이미 있을 수 있으므로 예외 처리)
        try:
            alter_sql = """
            ALTER TABLE kit_management 
            ADD COLUMN kit_type_id INTEGER REFERENCES kit_types(kit_type_id);
            """
            db.execute(text(alter_sql))
            db.commit()
            print("kit_management 테이블에 kit_type_id 컬럼이 추가되었습니다.")
        except Exception as e:
            if "already exists" in str(e):
                print("kit_type_id 컬럼이 이미 존재합니다.")
            else:
                raise e
                
    except Exception as e:
        print(f"테이블 수정 중 오류: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("검사키트 종류 데이터 추가 시작...")
    
    # 1. kit_types 테이블 생성
    create_kit_types_table()
    
    # 2. 검사키트 종류 데이터 추가
    add_kit_types()
    
    # 3. kit_management 테이블 업데이트
    update_kit_management_table()
    
    print("\n완료!")