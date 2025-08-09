#!/usr/bin/env python3
"""
직원 근무표 테이블 생성 스크립트
"""

import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from core.config import settings
from core.database import Base, engine
from models.staff_schedule import StaffSchedule

def create_staff_schedule_table():
    """직원 근무표 테이블 생성"""
    try:
        print("직원 근무표 테이블 생성 중...")
        
        # 테이블 생성
        StaffSchedule.__table__.create(engine, checkfirst=True)
        
        print("✅ staff_schedules 테이블이 생성되었습니다.")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    create_staff_schedule_table()