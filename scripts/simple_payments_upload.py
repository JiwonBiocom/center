#!/usr/bin/env python3
"""
간단한 결제 데이터 업로드 스크립트
실행: python scripts/simple_payments_upload.py
"""
import csv
import psycopg2
from datetime import datetime
from pathlib import Path

# Supabase 직접 연결 URL
DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:aibio1234!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def convert_payment_method(method):
    """결제 방법 한글 -> 영문 변환"""
    method_map = {
        "카드": "card",
        "이체": "transfer",
        "현금": "cash"
    }
    return method_map.get(method, method.lower())

def upload_payments():
    """결제 데이터 직접 업로드"""
    
    print("🚀 Supabase로 결제 데이터 직접 업로드")
    print("=" * 50)
    
    # CSV 파일 경로
    csv_path = Path("backend/seed/payments_real.csv")
    
    if not csv_path.exists():
        print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_path}")
        return False
    
    try:
        # PostgreSQL 연결
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # 현재 데이터 확인
        cursor.execute("SELECT COUNT(*) FROM payments")
        current_count = cursor.fetchone()[0]
        print(f"\n📊 현재 payments 테이블: {current_count}건")
        
        # CSV 데이터 읽기
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            success_count = 0
            skip_count = 0
            
            for row in reader:
                try:
                    # 중복 확인
                    cursor.execute("""
                        SELECT payment_id FROM payments 
                        WHERE customer_id = %s AND payment_date = %s AND amount = %s
                    """, (row['customer_id'], row['payment_date'], row['amount']))
                    
                    if cursor.fetchone():
                        skip_count += 1
                        continue
                    
                    # 데이터 삽입
                    cursor.execute("""
                        INSERT INTO payments (customer_id, payment_date, amount, payment_method, created_at)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        int(row['customer_id']),
                        row['payment_date'],
                        float(row['amount']),
                        convert_payment_method(row['payment_method']),
                        row['created_at'] or datetime.now().isoformat()
                    ))
                    
                    success_count += 1
                    
                    if success_count % 50 == 0:
                        print(f"  진행중... {success_count}건 추가")
                        conn.commit()
                        
                except Exception as e:
                    print(f"  ⚠️ 오류 (행 {reader.line_num}): {e}")
                    continue
            
            # 최종 커밋
            conn.commit()
            
            print(f"\n✅ 업로드 완료!")
            print(f"  - 추가: {success_count}건")
            print(f"  - 중복 스킵: {skip_count}건")
            
            # 최종 통계
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_count,
                    COUNT(DISTINCT customer_id) as unique_customers,
                    SUM(amount) as total_revenue
                FROM payments
            """)
            
            stats = cursor.fetchone()
            print(f"\n📈 최종 통계:")
            print(f"  - 총 결제 건수: {stats[0]:,}건")
            print(f"  - 고유 고객 수: {stats[1]:,}명")
            print(f"  - 총 매출액: ₩{stats[2]:,.0f}")
            
            cursor.close()
            conn.close()
            
            return True
            
    except Exception as e:
        print(f"❌ 연결 오류: {e}")
        return False

def main():
    """메인 실행 함수"""
    success = upload_payments()
    
    if success:
        print("\n🎉 완료!")
        print("💡 확인:")
        print("   https://center-ten.vercel.app/payments")

if __name__ == "__main__":
    main()