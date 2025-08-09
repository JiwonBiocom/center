"""
패키지명을 센터가격표와 일치하도록 업데이트하는 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.package import Package as PackageModel

def update_package_names():
    """패키지명을 올케어로 업데이트"""
    db = SessionLocal()
    
    try:
        # 종합 패키지를 올케어로 업데이트
        updates = [
            {
                "old_name": "종합 패키지 (4종)",
                "new_name": "올케어 40회",
                "new_description": "브레인, 펄스, 림프, 레드 각 10회 (총 40회)"
            },
            {
                "old_name": "프리미엄 종합 패키지",
                "new_name": "올케어 80회",
                "new_description": "브레인, 펄스, 림프, 레드 각 20회 (총 80회, 20% 할인)"
            }
        ]
        
        for update in updates:
            package = db.query(PackageModel).filter(
                PackageModel.package_name == update["old_name"]
            ).first()
            
            if package:
                print(f"업데이트: {update['old_name']} -> {update['new_name']}")
                package.package_name = update["new_name"]
                package.description = update["new_description"]
            else:
                print(f"패키지를 찾을 수 없음: {update['old_name']}")
        
        db.commit()
        print("\n✅ 패키지명 업데이트 완료")
        
        # 업데이트된 패키지 목록 확인
        print("\n=== 업데이트된 패키지 목록 ===")
        all_packages = db.query(PackageModel).filter(PackageModel.is_active == True).all()
        for pkg in all_packages:
            print(f"- {pkg.package_name}: {pkg.price:,}원 ({pkg.total_sessions}회)")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_package_names()