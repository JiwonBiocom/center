#!/usr/bin/env python3
"""
키트 타입 설정 및 kit_receipts → kit_management 마이그레이션
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine
from models.customer_extended import KitReceipt
from models.kit import KitManagement, KitType
from sqlalchemy.orm import Session
from sqlalchemy import text

def main():
    print("🔧 키트 타입 설정 및 마이그레이션...")
    
    with Session(engine) as session:
        # 1. 필요한 키트 타입 추가
        print("\n📋 키트 타입 설정 중...")
        
        # 유기산 키트 타입 확인/추가
        organic_kit = session.query(KitType).filter(KitType.name == "유기산").first()
        if not organic_kit:
            organic_kit = KitType(
                name="유기산",
                code="ORGANIC",
                description="유기산 검사 키트",
                price=180000,
                is_active=True
            )
            session.add(organic_kit)
            session.commit()
            print("✅ '유기산' 키트 타입 추가됨")
        
        # 장내미생물 키트 타입 확인/추가
        gut_kit = session.query(KitType).filter(KitType.name == "장내미생물").first()
        if not gut_kit:
            gut_kit = KitType(
                name="장내미생물",
                code="GUT",
                description="장내미생물 검사 키트",
                price=150000,
                is_active=True
            )
            session.add(gut_kit)
            session.commit()
            print("✅ '장내미생물' 키트 타입 추가됨")
        
        # 모든 키트 타입 확인
        kit_types = session.query(KitType).all()
        kit_type_map = {kt.name: kt.kit_type_id for kt in kit_types}
        print(f"사용 가능한 키트 타입: {list(kit_type_map.keys())}")
        
        # 2. kit_receipts 데이터 읽기
        print("\n📊 kit_receipts 데이터 읽는 중...")
        kit_receipts = session.query(KitReceipt).all()
        print(f"총 {len(kit_receipts)}개의 키트 수령 정보 발견")
        
        if not kit_receipts:
            print("⚠️  마이그레이션할 데이터가 없습니다.")
            return
        
        # 3. kit_management 기존 데이터 삭제 후 마이그레이션
        print("\n🔄 kit_management로 마이그레이션 중...")
        session.execute(text("DELETE FROM kit_management"))
        session.commit()
        
        success_count = 0
        error_count = 0
        
        for kr in kit_receipts:
            try:
                # 키트 타입 매칭
                kit_type_name = kr.kit_type if kr.kit_type else "유기산"
                kit_type_id = kit_type_map.get(kit_type_name, kit_type_map.get("유기산"))
                
                # kit_management 생성
                km = KitManagement(
                    customer_id=kr.customer_id,
                    kit_type=kit_type_name,
                    kit_type_id=kit_type_id,
                    serial_number=kr.serial_number,
                    received_date=kr.receipt_date,
                    result_received_date=kr.result_received_date,
                    result_delivered_date=kr.result_delivered_date
                )
                
                session.add(km)
                success_count += 1
                
            except Exception as e:
                error_count += 1
                print(f"❌ 마이그레이션 오류: {str(e)}")
                session.rollback()
                continue
        
        # 커밋
        session.commit()
        
        # 결과 확인
        total_count = session.execute(text("SELECT COUNT(*) FROM kit_management")).scalar()
        
        print(f"\n✅ 마이그레이션 완료!")
        print(f"   - 성공: {success_count}개")
        print(f"   - 실패: {error_count}개")
        print(f"   - kit_management 전체: {total_count}개")
        
        # 상세 확인
        samples = session.execute(text("""
            SELECT km.kit_id, c.name, km.kit_type, kt.name as kit_type_name, 
                   km.serial_number, km.received_date
            FROM kit_management km
            JOIN customers c ON km.customer_id = c.customer_id
            LEFT JOIN kit_types kt ON km.kit_type_id = kt.kit_type_id
            ORDER BY km.kit_id DESC
            LIMIT 5
        """)).fetchall()
        
        if samples:
            print(f"\n📋 마이그레이션된 데이터 샘플:")
            for sample in samples:
                print(f"   - ID: {sample[0]}, {sample[1]}, {sample[2]} ({sample[3]}), {sample[4]}, {sample[5]}")

if __name__ == "__main__":
    main()