import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.package import Package, PackagePurchase
from core.config import settings
from datetime import datetime
import pandas as pd

# 데이터베이스 연결
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    print("=" * 80)
    print("패키지 데이터 확인")
    print("=" * 80)
    
    # 모든 패키지 조회
    packages = db.query(Package).order_by(Package.package_id).all()
    
    print(f"\n총 패키지 수: {len(packages)}")
    print("-" * 80)
    
    # 패키지 상세 정보 출력
    package_data = []
    for pkg in packages:
        package_data.append({
            'ID': pkg.package_id,
            '패키지명': pkg.package_name,
            '총 세션수': pkg.total_sessions,
            '가격': f"{pkg.price:,.0f}" if pkg.price else "0",
            '유효기간(일)': pkg.valid_days,
            '활성': '활성' if pkg.is_active else '비활성',
            '설명': pkg.description[:50] + '...' if pkg.description and len(pkg.description) > 50 else pkg.description,
            '생성일': pkg.created_at.strftime('%Y-%m-%d') if pkg.created_at else ''
        })
    
    # DataFrame으로 변환하여 보기 좋게 출력
    df = pd.DataFrame(package_data)
    print(df.to_string(index=False))
    
    print("\n" + "=" * 80)
    print("패키지별 구매 현황")
    print("=" * 80)
    
    # 패키지별 구매 통계
    purchase_stats = []
    for pkg in packages:
        purchases = db.query(PackagePurchase).filter(PackagePurchase.package_id == pkg.package_id).all()
        total_purchases = len(purchases)
        total_revenue = total_purchases * (pkg.price if pkg.price else 0)
        
        purchase_stats.append({
            '패키지명': pkg.package_name,
            '총 구매 수': total_purchases,
            '총 매출': f"{total_revenue:,.0f}",
            '상태': '활성' if pkg.is_active else '비활성'
        })
    
    # 구매 통계 출력
    stats_df = pd.DataFrame(purchase_stats)
    print(stats_df.to_string(index=False))
    
    print("\n" + "=" * 80)
    print("가짜 데이터로 추정되는 패키지 (일반적인 이름 패턴)")
    print("=" * 80)
    
    # 가짜 데이터 패턴
    fake_patterns = [
        'Premium Package', 'Basic Package', 'Standard Package',
        'Gold Package', 'Silver Package', 'Bronze Package',
        'Starter', 'Professional', 'Enterprise',
        '테스트', 'Test', 'Sample'
    ]
    
    fake_packages = []
    for pkg in packages:
        for pattern in fake_patterns:
            if pattern.lower() in pkg.package_name.lower():
                fake_packages.append({
                    'ID': pkg.package_id,
                    '패키지명': pkg.package_name,
                    '가격': f"{pkg.price:,.0f}" if pkg.price else "0",
                    '구매 수': len(db.query(PackagePurchase).filter(PackagePurchase.package_id == pkg.package_id).all())
                })
                break
    
    if fake_packages:
        fake_df = pd.DataFrame(fake_packages)
        print(fake_df.to_string(index=False))
    else:
        print("가짜 데이터로 추정되는 패키지가 없습니다.")
    
    print("\n" + "=" * 80)
    print("실제 패키지로 추정되는 항목 (한글 이름 포함)")
    print("=" * 80)
    
    # 한글이 포함된 패키지 찾기
    real_packages = []
    for pkg in packages:
        # 한글이 포함되어 있거나 특정 패턴이 없는 경우
        if any(ord(char) >= 0xAC00 and ord(char) <= 0xD7A3 for char in pkg.package_name):
            real_packages.append({
                'ID': pkg.package_id,
                '패키지명': pkg.package_name,
                '세션수': pkg.total_sessions,
                '가격': f"{pkg.price:,.0f}" if pkg.price else "0",
                '유효기간': f"{pkg.valid_days}일" if pkg.valid_days else "",
                '구매 수': len(db.query(PackagePurchase).filter(PackagePurchase.package_id == pkg.package_id).all())
            })
    
    if real_packages:
        real_df = pd.DataFrame(real_packages)
        print(real_df.to_string(index=False))
    else:
        print("한글 이름의 패키지가 없습니다.")

except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()

finally:
    db.close()