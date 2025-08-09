#!/usr/bin/env python3
"""
AIBIO 실제 서비스로 복원하는 스크립트
문서와 PRD를 기반으로 정확한 서비스명으로 업데이트
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

    # 정확한 서비스 매핑 (PRD 문서 기준)
    service_mapping = {
        '상담': {
            'new_name': '상담',
            'description': '건강 상태 종합 분석, 맞춤형 케어 플랜',
            'default_duration': 30,
            'default_price': 100000,
            'service_color': '#FF6B6B'
        },
        '발가락케어': {  # 테스트 데이터
            'new_name': '브레인피드백',  # 정확한 서비스명
            'description': '뇌파 측정 및 분석, 뉴로피드백 트레이닝',
            'default_duration': 60,
            'default_price': 150000,
            'service_color': '#8B5CF6'
        },
        '종아리케어': {  # 테스트 데이터
            'new_name': '펄스',
            'description': '전신 펄스 자극 치료, 혈액순환 개선',
            'default_duration': 45,
            'default_price': 120000,
            'service_color': '#3B82F6'
        },
        '뱃살케어': {  # 테스트 데이터
            'new_name': '레드',
            'description': '적외선 광선 치료, 세포 재생 촉진',
            'default_duration': 30,
            'default_price': 100000,
            'service_color': '#EF4444'
        },
        '등케어': {  # 테스트 데이터
            'new_name': '림프',
            'description': '림프 순환 마사지, 독소 배출 촉진',
            'default_duration': 90,
            'default_price': 180000,
            'service_color': '#10B981'
        },
        'DNA검사': {  # 잘못 들어간 데이터 - 삭제 예정
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
            'service_color': '#9333EA'  # Purple
        },
        {
            'service_name': '음식물과민증검사',
            'description': '음식물 과민증 및 알레르기 검사',
            'default_duration': 30,
            'default_price': 150000,
            'service_color': '#EC4899'  # Pink
        },
        {
            'service_name': '영양중금속검사',
            'description': '영양 상태 및 중금속 축적 검사',
            'default_duration': 30,
            'default_price': 180000,
            'service_color': '#14B8A6'  # Teal
        }
    ]

    with engine.connect() as conn:
        trans = conn.begin()

        try:
            # 현재 서비스 타입 확인
            print("=" * 60)
            print("AIBIO 서비스 타입 복원")
            print("=" * 60)
            print("\n현재 서비스 타입 확인 중...")

            current_services = conn.execute(text("""
                SELECT service_type_id, service_name, default_price
                FROM service_types
                ORDER BY service_type_id
            """)).fetchall()

            print("\n[현재 상태]")
            for row in current_services:
                status = "⚠️  테스트 데이터" if row[1] in ['발가락케어', '종아리케어', '뱃살케어', '등케어'] else "✅"
                print(f"  {status} {row[1]} (ID: {row[0]}, 가격: {row[2]:,}원)")

            # 기존 서비스 업데이트
            print("\n[변경 작업]")
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
                    else:
                        print(f"  ✅ {current_name} (변경 없음)")

            # 새 서비스 추가
            for service in new_services:
                # 이미 존재하는지 확인
                exists = conn.execute(
                    text("SELECT 1 FROM service_types WHERE service_name = :name"),
                    {'name': service['service_name']}
                ).fetchone()

                if not exists:
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
                    print(f"  ➕ {service['service_name']} 추가됨")

            # 결과 확인
            print("\n[복원 후 상태]")
            result = conn.execute(text("""
                SELECT service_type_id, service_name, default_price, description
                FROM service_types
                ORDER BY service_type_id
            """)).fetchall()

            for row in result:
                print(f"  ✅ {row[1]} (ID: {row[0]}, 가격: {row[2]:,}원)")
                if row[3]:
                    print(f"     └─ {row[3]}")

            # 테스트 데이터 확인
            print("\n[기타 테스트 데이터 정보]")
            print("  ⚠️  샘플 고객: 김영희, 이철수, 박민수 등")
            print("  ⚠️  export_schema_for_supabase.py에 하드코딩된 서비스")
            print("  ⚠️  add_sample_data.py의 테스트 데이터")

            # 사용자 확인
            print("\n" + "=" * 60)
            confirm = input("\n이대로 진행하시겠습니까? (y/n): ")
            if confirm.lower() == 'y':
                trans.commit()
                print("\n✅ 서비스 타입이 정상적으로 복원되었습니다!")
                print("   기존 서비스 사용 기록은 모두 유지됩니다.")
            else:
                trans.rollback()
                print("\n❌ 취소되었습니다. 변경사항이 저장되지 않았습니다.")

        except Exception as e:
            trans.rollback()
            print(f"\n❌ 오류 발생: {e}")
            raise

if __name__ == "__main__":
    print("\nAIBIO 서비스 타입 복원 스크립트")
    print("테스트 데이터를 실제 서비스로 변경합니다.")
    print("\n주요 변경사항:")
    print("  • 발가락케어 → 브레인피드백")
    print("  • 종아리케어 → 펄스")
    print("  • 뱃살케어 → 레드")
    print("  • 등케어 → 림프")
    print("  • DNA검사 → 삭제")
    print("  • AI바이크 추가")
    print("  • 종합대사기능검사 추가")
    print("  • 음식물과민증검사 추가")
    print("  • 영양중금속검사 추가")

    restore_correct_services()
