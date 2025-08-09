"""
센터가격표와 고객관리대장의 모든 패키지 통합 업데이트 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.package import Package as PackageModel

def update_all_packages():
    """모든 패키지 데이터 업데이트"""
    db = SessionLocal()
    
    # 1. 기존 패키지명 업데이트 (종합 -> 올케어)
    name_updates = [
        {
            "old_name": "종합 패키지 (4종)",
            "new_name": "올케어 40",
            "new_description": "브레인, 펄스, 림프, 레드 각 10회 (총 40회)",
            "new_price": 2500000  # 평균가격
        },
        {
            "old_name": "프리미엄 종합 패키지",
            "new_name": "올케어 80",
            "new_description": "브레인, 펄스, 림프, 레드 각 20회 (총 80회)",
            "new_price": 3800000  # 평균가격
        }
    ]
    
    # 2. 신규 패키지 추가
    new_packages = [
        {
            "package_name": "올케어 120",
            "description": "모든 서비스 자유롭게 선택하여 120회 이용",
            "total_sessions": 120,
            "price": 5148000,
            "valid_days": 365,  # 12개월
            "is_active": True
        },
        {
            "package_name": "펄스+레드 패키지 20회",
            "description": "펄스 10회 + 레드 10회",
            "total_sessions": 20,
            "price": 1780000,
            "valid_days": 90,  # 3개월
            "is_active": True
        },
        {
            "package_name": "브레인+펄스 패키지 20회",
            "description": "브레인 10회 + 펄스 10회",
            "total_sessions": 20,
            "price": 2476900,
            "valid_days": 90,  # 3개월
            "is_active": True
        },
        {
            "package_name": "대사개선+화이트닝 20회",
            "description": "대사개선 프로그램과 화이트닝 케어",
            "total_sessions": 20,
            "price": 2013800,
            "valid_days": 90,  # 3개월
            "is_active": True
        }
    ]
    
    try:
        # 기존 패키지명 업데이트
        print("=== 기존 패키지 업데이트 ===")
        for update in name_updates:
            package = db.query(PackageModel).filter(
                PackageModel.package_name == update["old_name"]
            ).first()
            
            if package:
                print(f"업데이트: {update['old_name']} -> {update['new_name']}")
                package.package_name = update["new_name"]
                package.description = update["new_description"]
                package.price = update["new_price"]
            else:
                print(f"패키지를 찾을 수 없음: {update['old_name']}")
        
        # 신규 패키지 추가
        print("\n=== 신규 패키지 추가 ===")
        added_count = 0
        for pkg_data in new_packages:
            # 중복 확인
            existing = db.query(PackageModel).filter(
                PackageModel.package_name == pkg_data["package_name"]
            ).first()
            
            if existing:
                print(f"이미 존재: {pkg_data['package_name']}")
                continue
            
            # 새 패키지 생성
            new_package = PackageModel(
                package_name=pkg_data["package_name"],
                description=pkg_data["description"],
                total_sessions=pkg_data["total_sessions"],
                price=pkg_data["price"],
                valid_days=pkg_data["valid_days"],
                is_active=pkg_data["is_active"],
                created_at=datetime.utcnow()
            )
            
            db.add(new_package)
            added_count += 1
            print(f"추가됨: {pkg_data['package_name']} - {pkg_data['price']:,}원")
        
        db.commit()
        print(f"\n✅ 총 {added_count}개의 패키지가 추가되었습니다.")
        
        # 전체 패키지 목록 출력
        print("\n📦 전체 패키지 목록:")
        all_packages = db.query(PackageModel).filter(PackageModel.is_active == True).order_by(PackageModel.price).all()
        for pkg in all_packages:
            print(f"- {pkg.package_name}: {pkg.price:,}원 ({pkg.total_sessions}회, {pkg.valid_days}일)")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🏥 AIBIO Center 패키지 통합 업데이트")
    print("=" * 50)
    update_all_packages()