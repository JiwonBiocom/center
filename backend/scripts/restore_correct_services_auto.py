#!/usr/bin/env python3
"""
AIBIO 실제 서비스로 복원하는 스크립트 (자동 실행 버전)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from core.config import settings
from datetime import datetime

# Create engine directly
engine = create_engine(settings.DATABASE_URL)

def restore_correct_services():
    """서비스 타입을 실제 AIBIO 서비스로 업데이트"""

    # 정확한 서비스 매핑
    service_mapping = {
        '상담': {
            'new_name': '상담',
            'description': '건강 상태 종합 분석, 맞춤형 케어 플랜',
            'default_duration': 30,
            'default_price': 100000,
            'service_color': '#FF6B6B'
        },
        '발가락케어': {
            'new_name': '브레인피드백',
            'description': '뇌파 측정 및 분석, 뉴로피드백 트레이닝',
            'default_duration': 60,
            'default_price': 150000,
            'service_color': '#8B5CF6'
        },
        '종아리케어': {
            'new_name': '펄스',
            'description': '전신 펄스 자극 치료, 혈액순환 개선',
            'default_duration': 45,
            'default_price': 120000,
            'service_color': '#3B82F6'
        },
        '뱃살케어': {
            'new_name': '레드',
            'description': '적외선 광선 치료, 세포 재생 촉진',
            'default_duration': 30,
            'default_price': 100000,
            'service_color': '#EF4444'
        },
        '등케어': {
            'new_name': '림프',
            'description': '림프 순환 마사지, 독소 배출 촉진',
            'default_duration': 90,
            'default_price': 180000,
            'service_color': '#10B981'
        },
        'DNA검사': {
            'delete': True,
            'new_name': None
        },
        '인바디측정': {
            'new_name': '인바디측정',
            'description': '체성분 분석 및 건강 상태 측정',
            'default_duration': 15,
            'default_price': 20000,
            'service_color': '#7209B7'
        }
    }

    # 추가할 새 서비스
    new_services = [
        {
            'service_name': 'AI바이크',
            'description': 'AI 기반 운동 프로그램',
            'default_duration': 40,
            'default_price': 80000,
            'service_color': '#F59E0B'
        },
        {
            'service_name': '종합대사기능검사',
            'description': '종합적인 대사 기능 분석 검사',
            'default_duration': 30,
            'default_price': 200000,
            'service_color': '#9333EA'
        },
        {
            'service_name': '음식물과민증검사',
            'description': '음식물 과민증 및 알레르기 검사',
            'default_duration': 30,
            'default_price': 150000,
            'service_color': '#EC4899'
        },
        {
            'service_name': '영양중금속검사',
            'description': '영양 상태 및 중금속 축적 검사',
            'default_duration': 30,
            'default_price': 180000,
            'service_color': '#14B8A6'
        }
    ]

    with engine.connect() as conn:
        trans = conn.begin()

        try:
            print("=" * 60)
            print("AIBIO 서비스 타입 복원 (자동 실행)")
            print("=" * 60)

            # 현재 서비스 타입 확인
            current_services = conn.execute(text("""
                SELECT service_type_id, service_name, default_price
                FROM service_types
                ORDER BY service_type_id
            """)).fetchall()

            print("\n[현재 상태]")
            for row in current_services:
                print(f"  - {row[1]} (ID: {row[0]})")

            # 기존 서비스 업데이트
            print("\n[변경 작업 진행 중...]")
            for row in current_services:
                service_id = row[0]
                current_name = row[1]

                if current_name in service_mapping:
                    mapping = service_mapping[current_name]

                    # DNA검사는 삭제
                    if mapping.get('delete'):
                        conn.execute(
                            text("DELETE FROM service_types WHERE service_type_id = :service_id"),
                            {'service_id': service_id}
                        )
                        print(f"  🗑️  {current_name} 삭제됨")
                        continue

                    if current_name != mapping['new_name']:
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
                        print(f"  ✏️  {current_name} → {mapping['new_name']}")

            # 새 서비스 추가
            for service in new_services:
                exists = conn.execute(
                    text("SELECT 1 FROM service_types WHERE service_name = :name"),
                    {'name': service['service_name']}
                ).fetchone()

                if not exists:
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
                    print(f"  ➕ {service['service_name']} 추가됨")

            # 커밋
            trans.commit()

            # 결과 확인
            print("\n[복원 완료 - 최종 상태]")
            result = conn.execute(text("""
                SELECT service_type_id, service_name, default_price
                FROM service_types
                ORDER BY service_type_id
            """)).fetchall()

            for row in result:
                print(f"  ✅ {row[1]} (ID: {row[0]}, 가격: {row[2]:,}원)")

            print("\n✅ 서비스 타입이 성공적으로 복원되었습니다!")
            print("   기존 서비스 사용 기록은 모두 유지됩니다.")

        except Exception as e:
            trans.rollback()
            print(f"\n❌ 오류 발생: {e}")
            raise

if __name__ == "__main__":
    restore_correct_services()
