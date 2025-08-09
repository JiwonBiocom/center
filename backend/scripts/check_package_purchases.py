import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from models.package import Package, PackagePurchase
from models.customer import Customer
from core.config import settings
from datetime import datetime
import pandas as pd

# 데이터베이스 연결
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    print("=" * 80)
    print("패키지 구매 현황 확인")
    print("=" * 80)
    
    # 전체 구매 건수
    total_purchases = db.query(PackagePurchase).count()
    print(f"\n총 패키지 구매 건수: {total_purchases}")
    
    if total_purchases > 0:
        # 최근 구매 내역
        print("\n" + "=" * 80)
        print("최근 패키지 구매 내역 (최대 20건)")
        print("=" * 80)
        
        recent_purchases = db.query(
            PackagePurchase,
            Customer.name.label('customer_name'),
            Package.package_name
        ).join(
            Customer, PackagePurchase.customer_id == Customer.customer_id
        ).join(
            Package, PackagePurchase.package_id == Package.package_id
        ).order_by(
            PackagePurchase.purchase_date.desc()
        ).limit(20).all()
        
        purchase_data = []
        for purchase, customer_name, package_name in recent_purchases:
            purchase_data.append({
                'ID': purchase.purchase_id,
                '고객명': customer_name,
                '패키지명': package_name,
                '구매일': purchase.purchase_date.strftime('%Y-%m-%d'),
                '만료일': purchase.expiry_date.strftime('%Y-%m-%d') if purchase.expiry_date else '',
                '총 세션': purchase.total_sessions,
                '사용': purchase.used_sessions,
                '잔여': purchase.remaining_sessions
            })
        
        df = pd.DataFrame(purchase_data)
        print(df.to_string(index=False))
        
        # 월별 구매 통계
        print("\n" + "=" * 80)
        print("월별 패키지 구매 통계")
        print("=" * 80)
        
        monthly_stats = db.query(
            func.date_trunc('month', PackagePurchase.purchase_date).label('month'),
            func.count(PackagePurchase.purchase_id).label('count'),
            func.sum(Package.price).label('total_revenue')
        ).join(
            Package, PackagePurchase.package_id == Package.package_id
        ).group_by(
            func.date_trunc('month', PackagePurchase.purchase_date)
        ).order_by('month').all()
        
        monthly_data = []
        for stat in monthly_stats:
            monthly_data.append({
                '월': stat.month.strftime('%Y-%m'),
                '구매 건수': stat.count,
                '총 매출': f"{stat.total_revenue:,.0f}" if stat.total_revenue else "0"
            })
        
        if monthly_data:
            monthly_df = pd.DataFrame(monthly_data)
            print(monthly_df.to_string(index=False))
        
        # 패키지별 구매 통계
        print("\n" + "=" * 80)
        print("패키지별 구매 통계")
        print("=" * 80)
        
        package_stats = db.query(
            Package.package_name,
            func.count(PackagePurchase.purchase_id).label('purchase_count'),
            func.sum(Package.price).label('total_revenue')
        ).join(
            PackagePurchase, Package.package_id == PackagePurchase.package_id
        ).group_by(
            Package.package_name
        ).order_by(
            func.count(PackagePurchase.purchase_id).desc()
        ).all()
        
        package_data = []
        for stat in package_stats:
            package_data.append({
                '패키지명': stat.package_name,
                '구매 건수': stat.purchase_count,
                '총 매출': f"{stat.total_revenue:,.0f}" if stat.total_revenue else "0"
            })
        
        if package_data:
            package_df = pd.DataFrame(package_data)
            print(package_df.to_string(index=False))
    
    else:
        print("\n아직 패키지 구매 내역이 없습니다.")
    
    # 샘플 데이터 확인
    print("\n" + "=" * 80)
    print("샘플 데이터 패턴 확인")
    print("=" * 80)
    
    # 특정 패턴의 고객 이름 확인
    sample_patterns = ['테스트', 'Test', 'Sample', '샘플']
    
    for pattern in sample_patterns:
        sample_purchases = db.query(
            PackagePurchase,
            Customer.name
        ).join(
            Customer, PackagePurchase.customer_id == Customer.customer_id
        ).filter(
            Customer.name.ilike(f'%{pattern}%')
        ).count()
        
        if sample_purchases > 0:
            print(f"'{pattern}' 패턴이 포함된 고객의 구매: {sample_purchases}건")

except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()

finally:
    db.close()