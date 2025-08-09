#!/usr/bin/env python3
"""
AIBIO 원래 서비스 타입으로 복원하는 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from core.config import settings
from datetime import datetime

# Create engine directly
engine = create_engine(settings.DATABASE_URL)

def restore_original_services():
    """원래 AIBIO 서비스로 복원"""

    # 원래 서비스 타입 (가격표 문서 기준)
    original_services = [
        {
            'service_name': '브레인케어',
            'description': '뇌파 측정 및 분석, 뉴로피드백 트레이닝',
            'default_duration': 60,
            'default_price': 150000,
            'service_color': '#8B5CF6'  # Purple
        },
        {
            'service_name': '펄스케어',
            'description': '전신 펄스 자극 치료, 혈액순환 개선',
            'default_duration': 45,
            'default_price': 120000,
            'service_color': '#3B82F6'  # Blue
        },
        {
            'service_name': '레드케어',
            'description': '적외선 광선 치료, 세포 재생 촉진',
            'default_duration': 30,
            'default_price': 100000,
            'service_color': '#EF4444'  # Red
        },
        {
            'service_name': '림프케어',
            'description': '림프 순환 마사지, 독소 배출 촉진',
            'default_duration': 90,
            'default_price': 180000,
            'service_color': '#10B981'  # Green
        },
        {
            'service_name': 'AI바이크',
            'description': 'AI 기반 운동 프로그램, 적외선 치료 병행',
            'default_duration': 40,
            'default_price': 80000,
            'service_color': '#F59E0B'  # Amber
        },
        {
            'service_name': '상담',
            'description': '건강 상태 종합 분석, 맞춤형 케어 플랜',
            'default_duration': 30,
            'default_price': 100000,
            'service_color': '#FF6B6B'  # Rose
        },
        {
            'service_name': '인바디측정',
            'description': '체성분 분석 및 건강 상태 측정',
            'default_duration': 15,
            'default_price': 20000,
            'service_color': '#7209B7'  # Purple
        },
        {
            'service_name': 'DNA검사',
            'description': '유전자 분석을 통한 맞춤 건강 관리',
            'default_duration': 30,
            'default_price': 150000,
            'service_color': '#C77DFF'  # Light Purple
        }
    ]

    with engine.connect() as conn:
        trans = conn.begin()

        try:
            # 현재 서비스 타입 백업
            print("현재 서비스 타입 백업 중...")
            backup = conn.execute(text("""
                SELECT service_type_id, service_name, description,
                       default_duration, default_price, service_color
                FROM service_types
                ORDER BY service_type_id
            """)).fetchall()

            print("\n현재 서비스 타입:")
            for row in backup:
                print(f"  - {row[1]} (ID: {row[0]})")

            # 기존 서비스 타입 삭제
            print("\n기존 서비스 타입 삭제 중...")
            conn.execute(text("DELETE FROM service_types"))

            # 새 서비스 타입 추가
            print("\n원래 서비스 타입 추가 중...")
            for idx, service in enumerate(original_services, 1):
                conn.execute(
                    text("""
                        INSERT INTO service_types (
                            service_type_id,
                            service_name,
                            description,
                            default_duration,
                            default_price,
                            service_color,
                            is_active,
                            created_at
                        ) VALUES (
                            :service_type_id,
                            :service_name,
                            :description,
                            :default_duration,
                            :default_price,
                            :service_color,
                            true,
                            :created_at
                        )
                    """),
                    {
                        'service_type_id': idx,
                        'service_name': service['service_name'],
                        'description': service.get('description'),
                        'default_duration': service['default_duration'],
                        'default_price': service['default_price'],
                        'service_color': service['service_color'],
                        'created_at': datetime.now()
                    }
                )
                print(f"  + {service['service_name']} 추가됨")

            # 확인
            print("\n복원 후 서비스 타입:")
            result = conn.execute(text("""
                SELECT service_type_id, service_name, default_price
                FROM service_types
                ORDER BY service_type_id
            """)).fetchall()

            for row in result:
                print(f"  - {row[1]} (ID: {row[0]}, 가격: {row[2]:,}원)")

            # 사용자 확인
            confirm = input("\n이대로 진행하시겠습니까? (y/n): ")
            if confirm.lower() == 'y':
                trans.commit()
                print("\n✅ 서비스 타입이 원래대로 복원되었습니다!")
            else:
                trans.rollback()
                print("\n❌ 취소되었습니다. 변경사항이 저장되지 않았습니다.")

        except Exception as e:
            trans.rollback()
            print(f"\n❌ 오류 발생: {e}")
            raise

if __name__ == "__main__":
    print("=" * 50)
    print("AIBIO 서비스 타입 복원 스크립트")
    print("=" * 50)
    print("\n⚠️  주의: 이 스크립트는 모든 서비스 타입을 삭제하고 다시 생성합니다.")
    print("기존 서비스 사용 기록은 유지되지만, service_type_id가 변경될 수 있습니다.")

    proceed = input("\n계속하시겠습니까? (y/n): ")
    if proceed.lower() == 'y':
        restore_original_services()
    else:
        print("취소되었습니다.")
