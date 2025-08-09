#!/usr/bin/env python3
"""
로컬 SQLite 데이터베이스에서 모든 결제 데이터를 추출
실행: python scripts/export_local_payments.py
"""
import csv
import sqlite3
from datetime import datetime
from pathlib import Path

def export_local_payments():
    """로컬 SQLite DB에서 모든 결제 데이터 추출"""
    
    print("🚀 로컬 데이터베이스에서 결제 데이터 추출 시작")
    print("=" * 50)
    
    # 로컬 데이터베이스 경로
    db_path = Path("backend/aibio_center.db")
    
    if not db_path.exists():
        print(f"❌ 데이터베이스 파일을 찾을 수 없습니다: {db_path}")
        return False
    
    # 출력 CSV 경로
    csv_dir = Path("backend/seed")
    csv_dir.mkdir(exist_ok=True)
    csv_path = csv_dir / "local_payments_export.csv"
    
    try:
        # SQLite 연결
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 실제 payments 테이블 구조 확인
        cursor.execute("PRAGMA table_info(payments)")
        columns = cursor.fetchall()
        print("\n📋 payments 테이블 구조:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # 모든 결제 데이터 조회
        query = """
        SELECT 
            payment_id,
            customer_id,
            payment_date,
            amount,
            payment_method,
            created_at
        FROM payments
        ORDER BY payment_id
        """
        
        cursor.execute(query)
        payments = cursor.fetchall()
        
        print(f"\n📊 추출된 결제 데이터: {len(payments)}건")
        
        if len(payments) == 0:
            print("⚠️ 결제 데이터가 없습니다.")
            return False
        
        # CSV로 저장
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # 헤더 작성
            writer.writerow(["payment_id", "customer_id", "payment_date", "amount", "payment_method", "created_at"])
            
            # 데이터 작성
            for payment in payments:
                writer.writerow(payment)
        
        print(f"\n✅ CSV 파일 생성 완료: {csv_path}")
        print(f"📁 파일 크기: {csv_path.stat().st_size / 1024:.1f} KB")
        
        # 샘플 데이터 표시
        print("\n📋 샘플 데이터 (처음 5개):")
        for i, payment in enumerate(payments[:5]):
            print(f"  {i+1}. ID:{payment[0]} | {payment[2]} | ₩{payment[3]:,.0f} | {payment[4]}")
        
        # 통계 정보
        cursor.execute("""
        SELECT 
            COUNT(*) as total_count,
            COUNT(DISTINCT customer_id) as unique_customers,
            SUM(amount) as total_revenue,
            MIN(payment_date) as first_payment,
            MAX(payment_date) as last_payment
        FROM payments
        """)
        
        stats = cursor.fetchone()
        print("\n📈 결제 데이터 통계:")
        print(f"  - 총 결제 건수: {stats[0]:,}건")
        print(f"  - 고유 고객 수: {stats[1]:,}명")
        print(f"  - 총 매출액: ₩{stats[2]:,.0f}")
        print(f"  - 첫 결제일: {stats[3]}")
        print(f"  - 마지막 결제일: {stats[4]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def main():
    """메인 실행 함수"""
    success = export_local_payments()
    
    if success:
        print("\n🎉 추출 완료!")
        print("💡 다음 단계:")
        print("   1. backend/seed/local_payments_export.csv 확인")
        print("   2. Supabase로 데이터 마이그레이션")

if __name__ == "__main__":
    main()