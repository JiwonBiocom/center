import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.package import Package
from core.config import settings
from datetime import datetime

# 데이터베이스 연결
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def update_packages():
    """최신 가격표에 맞춰 패키지 업데이트"""
    
    print("=" * 80)
    print("패키지 데이터 업데이트")
    print("=" * 80)
    
    # 현재 패키지와 최신 가격표 비교
    current_packages = {
        "브레인 10회 패키지": {"sessions": 10, "price": 1500000, "days": 60},
        "브레인 20회 패키지": {"sessions": 20, "price": 2800000, "days": 90},
        "펄스 10회 패키지": {"sessions": 10, "price": 1200000, "days": 60},
        "림프 10회 패키지": {"sessions": 10, "price": 1000000, "days": 60},
        "레드 10회 패키지": {"sessions": 10, "price": 800000, "days": 60},
        "종합 패키지 (4종)": {"sessions": 40, "price": 4000000, "days": 120},
        "프리미엄 종합 패키지": {"sessions": 80, "price": 7200000, "days": 180}
    }
    
    # 추가할 수 있는 새로운 패키지 (add_pricing_packages.py 참고)
    new_packages = {
        "스타터 패키지": {
            "sessions": 13,
            "price": 1200000,
            "days": 90,
            "description": "브레인케어 4회 + 펄스케어 4회 + 레드케어 4회 + 초기상담 1회 (정가 대비 20% 할인)"
        },
        "체험 패키지": {
            "sessions": 5,
            "price": 500000,
            "days": 30,
            "description": "각 서비스 1회씩 체험 (브레인, 펄스, 레드, 림프, AI바이크) - 신규 회원 전용"
        },
        "VIP 패키지": {
            "sessions": 240,
            "price": 5000000,
            "days": 365,
            "description": "모든 서비스 무제한 이용 (월 20회 한도, 전담 케어 매니저, 분기별 건강 리포트)"
        }
    }
    
    # 현재 데이터베이스의 패키지 확인
    existing_packages = db.query(Package).all()
    existing_names = [pkg.package_name for pkg in existing_packages]
    
    print("\n현재 패키지 목록:")
    for pkg in existing_packages:
        print(f"- {pkg.package_name}: {pkg.price:,.0f}원 ({pkg.total_sessions}회)")
    
    # 추가 가능한 패키지 확인
    print("\n" + "-" * 80)
    print("추가 가능한 새 패키지:")
    print("-" * 80)
    
    can_add = []
    for name, info in new_packages.items():
        if name not in existing_names:
            can_add.append((name, info))
            print(f"+ {name}: {info['price']:,.0f}원 ({info['sessions']}회)")
            print(f"  설명: {info['description']}")
    
    if can_add:
        print("\n" + "=" * 80)
        confirm = input("위 패키지들을 추가하시겠습니까? (y/n): ")
        
        if confirm.lower() == 'y':
            added_count = 0
            for name, info in can_add:
                new_pkg = Package(
                    package_name=name,
                    total_sessions=info['sessions'],
                    price=info['price'],
                    valid_days=info['days'],
                    description=info['description'],
                    is_active=True
                )
                db.add(new_pkg)
                added_count += 1
                print(f"추가됨: {name}")
            
            db.commit()
            print(f"\n✅ 총 {added_count}개의 패키지가 추가되었습니다.")
        else:
            print("\n취소되었습니다.")
    else:
        print("추가할 새 패키지가 없습니다.")
    
    # 최종 패키지 목록
    print("\n" + "=" * 80)
    print("최종 패키지 목록:")
    print("=" * 80)
    final_packages = db.query(Package).filter(Package.is_active == True).order_by(Package.price).all()
    for pkg in final_packages:
        print(f"{pkg.package_name}: {pkg.price:,.0f}원 ({pkg.total_sessions}회, {pkg.valid_days}일)")

try:
    update_packages()
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()