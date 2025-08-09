#!/usr/bin/env python3
"""
AIBIO 서비스 타입을 원래 서비스로 업데이트하는 스크립트 (안전 버전)
기존 서비스 사용 기록을 유지하면서 이름과 정보만 업데이트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from core.config import settings
from datetime import datetime

# Create engine directly
engine = create_engine(settings.DATABASE_URL)

def update_to_original_services():
    """서비스 타입을 원래 AIBIO 서비스로 업데이트"""

    # 매핑 테이블: 현재 -> 원래
    service_mapping = {
        '상담': {
            'new_name': '상담',
            'description': '건강 상태 종합 분석, 맞춤형 케어 플랜',
            'default_duration': 30,
            'default_price': 100000,
            'service_color': '#FF6B6B'
        },
        '발가락케어': {
            'new_name': '브레인케어',
            'description': '뇌파 측정 및 분석, 뉴로피드백 트레이닝',
            'default_duration': 60,
            'default_price': 150000,
            'service_color': '#8B5CF6'
        },
        '종아리케어': {
            'new_name': '펄스케어',
            'description': '전신 펄스 자극 치료, 혈액순환 개선',
            'default_duration': 45,
            'default_price': 120000,
            'service_color': '#3B82F6'
        },
        '뱃살케어': {
            'new_name': '레드케어',
            'description': '적외선 광선 치료, 세포 재생 촉진',
            'default_duration': 30,
            'default_price': 100000,
            'service_color': '#EF4444'
        },
        '등케어': {
            'new_name': '림프케어',
            'description': '림프 순환 마사지, 독소 배출 촉진',
            'default_duration': 90,
            'default_price': 180000,
            'service_color': '#10B981'
        },
        'DNA검사': {
            'new_name': 'DNA검사',
            'description': '유전자 분석을 통한 맞춤 건강 관리',
            'default_duration': 30,
            'default_price': 150000,
            'service_color': '#C77DFF'
        },
        '인바디측정': {
            'new_name': '인바디측정',
            'description': '체성분 분석 및 건강 상태 측정',
            'default_duration': 15,
            'default_price': 20000,
            'service_color': '#7209B7'
        }
    }

    # 추가할 새 서비스 (기존에 없는 것)
    new_services = [
        {
            'service_name': 'AI바이크',
            'description': 'AI 기반 운동 프로그램, 적외선 치료 병행',
            'default_duration': 40,
            'default_price': 80000,
            'service_color': '#F59E0B'
        }
    ]

    with engine.connect() as conn:
        trans = conn.begin()

        try:
            # 현재 서비스 타입 확인
            print("현재 서비스 타입 확인 중...")
            current_services = conn.execute(text("""
                SELECT service_type_id, service_name, default_price
                FROM service_types
                ORDER BY service_type_id
            """)).fetchall()

            print("\n현재 서비스 타입:")
            for row in current_services:
                print(f"  - {row[1]} (ID: {row[0]}, 가격: {row[2]:,}원)")

            # 기존 서비스 업데이트
            print("\n서비스 타입 업데이트 중...")
            for row in current_services:
                service_id = row[0]
                current_name = row[1]

                if current_name in service_mapping:
                    mapping = service_mapping[current_name]
                    conn.execute(
                        text("""
                            UPDATE service_types
                            SET service_name = :new_name,
                                description = :description,
                                default_duration = :default_duration,
                                default_price = :default_price,
                                service_color = :service_color,
                                updated_at = :updated_at
                            WHERE service_type_id = :service_id
                        """),
                        {
                            'service_id': service_id,
                            'new_name': mapping['new_name'],
                            'description': mapping['description'],
                            'default_duration': mapping['default_duration'],
                            'default_price': mapping['default_price'],
                            'service_color': mapping['service_color'],
                            'updated_at': datetime.now()
                        }
                    )
                    print(f"  ✓ {current_name} → {mapping['new_name']}")

            # 새 서비스 추가
            print("\n새 서비스 추가 중...")
            for service in new_services:
                # 다음 ID 찾기
                max_id_result = conn.execute(text("""
                    SELECT COALESCE(MAX(service_type_id), 0) + 1 FROM service_types
                """)).scalar()

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
                        'service_type_id': max_id_result,
                        'service_name': service['service_name'],
                        'description': service['description'],
                        'default_duration': service['default_duration'],
                        'default_price': service['default_price'],
                        'service_color': service['service_color'],
                        'created_at': datetime.now()
                    }
                )
                print(f"  + {service['service_name']} 추가됨")

            # 결과 확인
            print("\n업데이트 후 서비스 타입:")
            result = conn.execute(text("""
                SELECT service_type_id, service_name, default_price, description
                FROM service_types
                ORDER BY service_type_id
            """)).fetchall()

            for row in result:
                print(f"  - {row[1]} (ID: {row[0]}, 가격: {row[2]:,}원)")
                if row[3]:
                    print(f"    └─ {row[3]}")

            # 사용자 확인
            confirm = input("\n이대로 진행하시겠습니까? (y/n): ")
            if confirm.lower() == 'y':
                trans.commit()
                print("\n✅ 서비스 타입이 업데이트되었습니다!")
                print("기존 서비스 사용 기록은 모두 유지됩니다.")
            else:
                trans.rollback()
                print("\n❌ 취소되었습니다. 변경사항이 저장되지 않았습니다.")

        except Exception as e:
            trans.rollback()
            print(f"\n❌ 오류 발생: {e}")
            raise

if __name__ == "__main__":
    print("=" * 50)
    print("AIBIO 서비스 타입 업데이트 스크립트 (안전 버전)")
    print("=" * 50)
    print("\n이 스크립트는 기존 서비스 사용 기록을 유지하면서")
    print("서비스 이름과 정보만 업데이트합니다.")
    print("\n변경 내용:")
    print("  발가락케어 → 브레인케어")
    print("  종아리케어 → 펄스케어")
    print("  뱃살케어 → 레드케어")
    print("  등케어 → 림프케어")
    print("  + AI바이크 추가")

    proceed = input("\n계속하시겠습니까? (y/n): ")
    if proceed.lower() == 'y':
        update_to_original_services()
    else:
        print("취소되었습니다.")
