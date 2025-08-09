import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.package import Package, PackagePurchase
from core.config import settings
from datetime import datetime

# 데이터베이스 연결
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def check_and_clean_packages():
    """가짜 패키지 데이터 확인 및 정리"""
    
    print("=" * 80)
    print("패키지 데이터 정리 스크립트")
    print("=" * 80)
    
    # 가짜 데이터 패턴
    fake_patterns = [
        'test', 'sample', 'demo', 'example',
        'package 1', 'package 2', 'package 3',
        'basic package', 'standard package', 'premium package',
        'gold', 'silver', 'bronze',
        'starter', 'professional', 'enterprise'
    ]
    
    # 현재 패키지 목록
    all_packages = db.query(Package).all()
    print(f"\n현재 총 패키지 수: {len(all_packages)}")
    
    # 가짜로 의심되는 패키지 찾기
    fake_packages = []
    real_packages = []
    
    for pkg in all_packages:
        is_fake = False
        pkg_name_lower = pkg.package_name.lower()
        
        # 영어로만 되어 있고 일반적인 패턴인 경우
        for pattern in fake_patterns:
            if pattern in pkg_name_lower:
                is_fake = True
                break
        
        # 한글이 없는 경우도 의심
        if not any(ord(char) >= 0xAC00 and ord(char) <= 0xD7A3 for char in pkg.package_name):
            # 순수 영어 이름은 가짜일 가능성이 높음
            is_fake = True
        
        if is_fake:
            fake_packages.append(pkg)
        else:
            real_packages.append(pkg)
    
    # 결과 출력
    print("\n" + "-" * 80)
    print("실제 패키지 (유지할 데이터):")
    print("-" * 80)
    for pkg in real_packages:
        purchases = db.query(PackagePurchase).filter(PackagePurchase.package_id == pkg.package_id).count()
        print(f"✅ [{pkg.package_id}] {pkg.package_name} - {pkg.price:,.0f}원 (구매: {purchases}건)")
    
    if fake_packages:
        print("\n" + "-" * 80)
        print("가짜로 의심되는 패키지 (삭제 대상):")
        print("-" * 80)
        for pkg in fake_packages:
            purchases = db.query(PackagePurchase).filter(PackagePurchase.package_id == pkg.package_id).count()
            print(f"❌ [{pkg.package_id}] {pkg.package_name} - {pkg.price:,.0f}원 (구매: {purchases}건)")
        
        # 삭제 확인
        print("\n" + "=" * 80)
        confirm = input("위 가짜 패키지들을 삭제하시겠습니까? (y/n): ")
        
        if confirm.lower() == 'y':
            deleted_count = 0
            for pkg in fake_packages:
                # 연관된 구매 내역 먼저 삭제
                purchases = db.query(PackagePurchase).filter(PackagePurchase.package_id == pkg.package_id).all()
                for purchase in purchases:
                    db.delete(purchase)
                
                # 패키지 삭제
                db.delete(pkg)
                deleted_count += 1
                print(f"삭제됨: {pkg.package_name}")
            
            db.commit()
            print(f"\n✅ 총 {deleted_count}개의 가짜 패키지가 삭제되었습니다.")
        else:
            print("\n취소되었습니다.")
    else:
        print("\n✅ 가짜 패키지가 없습니다. 모든 패키지가 정상입니다.")
    
    # 정리 후 상태 확인
    remaining_packages = db.query(Package).all()
    print(f"\n최종 패키지 수: {len(remaining_packages)}")

try:
    check_and_clean_packages()
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()