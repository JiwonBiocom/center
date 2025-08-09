"""
올케어 패키지 데이터 확인 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.package import Package as PackageModel

def check_olcare_packages():
    """올케어 패키지 데이터 확인"""
    db = SessionLocal()
    
    try:
        # 모든 패키지 확인
        print("\n=== 현재 데이터베이스의 모든 패키지 ===")
        all_packages = db.query(PackageModel).filter(PackageModel.is_active == True).all()
        for pkg in all_packages:
            print(f"- {pkg.package_name}: {pkg.price:,}원 ({pkg.total_sessions}회, {pkg.valid_days}일)")
        
        # 종합/올케어 관련 패키지 찾기
        print("\n=== 종합/올케어 관련 패키지 ===")
        related_packages = db.query(PackageModel).filter(
            (PackageModel.package_name.like('%종합%')) | 
            (PackageModel.package_name.like('%올케어%'))
        ).all()
        
        if related_packages:
            for pkg in related_packages:
                print(f"- {pkg.package_name}: {pkg.price:,}원 ({pkg.total_sessions}회)")
        else:
            print("종합/올케어 패키지가 없습니다.")
            
    except Exception as e:
        print(f"오류 발생: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    check_olcare_packages()