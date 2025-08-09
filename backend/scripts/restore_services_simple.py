#!/usr/bin/env python3
"""
서비스 타입 복원 - 간단 버전
"""

from sqlalchemy import create_engine, text
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/aibio_center")
engine = create_engine(DATABASE_URL)

# 서비스 매핑
updates = [
    ("발가락케어", "브레인피드백", "뇌파 측정 및 분석, 뉴로피드백 트레이닝", 60, 150000, "#8B5CF6"),
    ("종아리케어", "펄스", "전신 펄스 자극 치료, 혈액순환 개선", 45, 120000, "#3B82F6"),
    ("뱃살케어", "레드", "적외선 광선 치료, 세포 재생 촉진", 30, 100000, "#EF4444"),
    ("등케어", "림프", "림프 순환 마사지, 독소 배출 촉진", 90, 180000, "#10B981")
]

new_services = [
    ("AI바이크", "AI 기반 운동 프로그램", 40, 80000, "#F59E0B"),
    ("종합대사기능검사", "종합적인 대사 기능 분석 검사", 30, 200000, "#9333EA"),
    ("음식물과민증검사", "음식물 과민증 및 알레르기 검사", 30, 150000, "#EC4899"),
    ("영양중금속검사", "영양 상태 및 중금속 축적 검사", 30, 180000, "#14B8A6")
]

with engine.connect() as conn:
    trans = conn.begin()
    try:
        # DNA검사 삭제
        conn.execute(text("DELETE FROM service_types WHERE service_name = 'DNA검사'"))
        print("DNA검사 삭제됨")

        # 기존 서비스 업데이트
        for old_name, new_name, desc, duration, price, color in updates:
            conn.execute(text("""
                UPDATE service_types
                SET service_name = :new_name,
                    description = :desc,
                    default_duration = :duration,
                    default_price = :price,
                    service_color = :color
                WHERE service_name = :old_name
            """), {
                'old_name': old_name,
                'new_name': new_name,
                'desc': desc,
                'duration': duration,
                'price': price,
                'color': color
            })
            print(f"{old_name} → {new_name}")

        # 새 서비스 추가
        for name, desc, duration, price, color in new_services:
            # 이미 있는지 확인
            exists = conn.execute(
                text("SELECT 1 FROM service_types WHERE service_name = :name"),
                {'name': name}
            ).fetchone()

            if not exists:
                # 다음 ID 가져오기
                max_id = conn.execute(text(
                    "SELECT COALESCE(MAX(service_type_id), 0) + 1 FROM service_types"
                )).scalar()

                conn.execute(text("""
                    INSERT INTO service_types
                    (service_type_id, service_name, description, default_duration,
                     default_price, service_color, is_active, created_at)
                    VALUES (:id, :name, :desc, :duration, :price, :color, true, :now)
                """), {
                    'id': max_id,
                    'name': name,
                    'desc': desc,
                    'duration': duration,
                    'price': price,
                    'color': color,
                    'now': datetime.now()
                })
                print(f"{name} 추가됨")

        trans.commit()
        print("\n✅ 완료!")

    except Exception as e:
        trans.rollback()
        print(f"❌ 오류: {e}")
        raise
