#!/usr/bin/env python3
"""
kit_receipts 데이터를 kit_management 테이블로 마이그레이션
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
    print("🔄 kit_receipts → kit_management 마이그레이션 시작...")
    
    with Session(engine) as session:
        # 1. 기본 키트 타입 생성 (없으면)
        print("\n📋 키트 타입 확인 중...")
        kit_types = session.query(KitType).all()
        
        if not kit_types:
            print("키트 타입이 없습니다. 기본 타입을 생성합니다.")
            default_types = [
                {"name": "장내미생물", "code": "GUT", "price": 150000},
                {"name": "유기산", "code": "ORGANIC", "price": 180000},
                {"name": "종합검사", "code": "TOTAL", "price": 250000}
            ]
            
            for kt in default_types:
                kit_type = KitType(
                    name=kt["name"],
                    code=kt["code"],
                    description=f"{kt['name']} 검사 키트",
                    price=kt["price"],
                    is_active=True
                )
                session.add(kit_type)
            
            session.commit()
            kit_types = session.query(KitType).all()
        
        # 키트 타입 맵핑
        kit_type_map = {kt.name: kt.kit_type_id for kt in kit_types}
        print(f"사용 가능한 키트 타입: {list(kit_type_map.keys())}")
        
        # 2. kit_receipts 데이터 읽기
        print("\n📊 kit_receipts 데이터 읽는 중...")
        kit_receipts = session.query(KitReceipt).all()
        print(f"총 {len(kit_receipts)}개의 키트 수령 정보 발견")
        
        if not kit_receipts:
            print("⚠️  마이그레이션할 데이터가 없습니다.")
            return
        
        # 3. kit_management로 마이그레이션
        print("\n🔄 kit_management로 마이그레이션 중...")
        
        # 기존 데이터 삭제 (옵션)
        session.execute(text("DELETE FROM kit_management"))
        session.commit()
        
        success_count = 0
        error_count = 0
        
        for kr in kit_receipts:
            try:
                # 키트 타입 매칭
                kit_type_id = None
                if kr.kit_type in kit_type_map:
                    kit_type_id = kit_type_map[kr.kit_type]
                elif "유기산" in kit_type_map:
                    # 기본값으로 유기산 사용
                    kit_type_id = kit_type_map["유기산"]
                
                # kit_management 생성
                km = KitManagement(
                    customer_id=kr.customer_id,
                    kit_type=kr.kit_type,
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
        
        # 샘플 확인
        samples = session.execute(text("""
            SELECT km.kit_id, c.name, km.kit_type, km.serial_number, km.received_date
            FROM kit_management km
            JOIN customers c ON km.customer_id = c.customer_id
            ORDER BY km.kit_id DESC
            LIMIT 5
        """)).fetchall()
        
        if samples:
            print(f"\n📋 마이그레이션된 데이터 샘플:")
            for sample in samples:
                print(f"   - ID: {sample[0]}, {sample[1]}, {sample[2]}, {sample[3]}, {sample[4]}")

if __name__ == "__main__":
    main()