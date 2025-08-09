#!/usr/bin/env python3
"""
테스트용 결제 데이터 CSV 생성
실행: python scripts/generate_test_payments_csv.py
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

def generate_payments_csv():
    """테스트용 결제 데이터 CSV 생성"""
    
    print("🚀 테스트용 결제 데이터 CSV 생성")
    print("=" * 50)
    
    # CSV 디렉토리 생성
    csv_dir = Path("backend/seed")
    csv_dir.mkdir(exist_ok=True)
    csv_path = csv_dir / "payments.csv"
    
    # 고객 ID 범위 (1-50 가정)
    customer_ids = list(range(1, 51))
    payment_methods = ['card', 'transfer', 'cash']
    amounts = [50000, 80000, 100000, 120000, 150000, 180000, 200000, 250000, 300000]
    
    base_date = date.today()
    
    # CSV 파일 생성
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        # 헤더 작성
        writer.writerow(["payment_id", "customer_id", "payment_date", "amount", "payment_method", "created_at"])
        
        # 100개의 테스트 데이터 생성
        for payment_id in range(1, 101):
            customer_id = random.choice(customer_ids)
            payment_date = base_date - timedelta(days=random.randint(1, 90))
            amount = random.choice(amounts)
            payment_method = random.choice(payment_methods)
            created_at = payment_date  # 결제일과 동일하게 설정
            
            writer.writerow([
                payment_id,
                customer_id,
                payment_date.isoformat(),
                amount,
                payment_method,
                created_at.isoformat()
            ])
    
    print(f"✅ CSV 파일 생성 완료: {csv_path}")
    print(f"📁 파일 크기: {csv_path.stat().st_size / 1024:.1f} KB")
    print(f"📊 생성된 레코드: 100개")
    
    # 샘플 데이터 표시
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
        print("\n📋 샘플 데이터 (첫 5개):")
        for i, row in enumerate(rows[:5]):
            print(f"  {i+1}. ID:{row['payment_id']} | {row['payment_date']} | ₩{int(row['amount']):,} | {row['payment_method']}")
    
    return True

def main():
    """메인 실행 함수"""
    success = generate_payments_csv()
    
    if success:
        print("\n🎉 생성 완료!")
        print("💡 다음 단계:")
        print("   1. git add backend/seed/payments.csv")
        print("   2. GitHub Actions로 Supabase 자동 로드 설정")

if __name__ == "__main__":
    main()