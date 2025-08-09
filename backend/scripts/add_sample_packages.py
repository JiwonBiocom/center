import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
from models.package import Package

def add_sample_packages():
    session = SessionLocal()
    try:
        packages = [
            Package(
                package_name="브레인 10회 패키지",
                total_sessions=10,
                price=1500000,
                valid_days=60,
                description="뇌 최적화 프로그램 10회"
            ),
            Package(
                package_name="브레인 20회 패키지",
                total_sessions=20,
                price=2800000,
                valid_days=90,
                description="뇌 최적화 프로그램 20회 (10% 할인)"
            ),
            Package(
                package_name="펄스 10회 패키지",
                total_sessions=10,
                price=1200000,
                valid_days=60,
                description="전신 순환 개선 프로그램 10회"
            ),
            Package(
                package_name="림프 10회 패키지",
                total_sessions=10,
                price=1000000,
                valid_days=60,
                description="림프 순환 개선 프로그램 10회"
            ),
            Package(
                package_name="레드 10회 패키지",
                total_sessions=10,
                price=800000,
                valid_days=60,
                description="적외선 치료 프로그램 10회"
            ),
            Package(
                package_name="종합 패키지 (4종)",
                total_sessions=40,
                price=4000000,
                valid_days=120,
                description="브레인, 펄스, 림프, 레드 각 10회"
            ),
            Package(
                package_name="프리미엄 종합 패키지",
                total_sessions=80,
                price=7200000,
                valid_days=180,
                description="브레인, 펄스, 림프, 레드 각 20회 (20% 할인)"
            )
        ]
        
        for package in packages:
            session.add(package)
        
        session.commit()
        print(f"Added {len(packages)} sample packages")
    finally:
        session.close()

if __name__ == "__main__":
    add_sample_packages()