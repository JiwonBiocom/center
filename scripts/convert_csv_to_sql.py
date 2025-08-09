#!/usr/bin/env python3
"""
CSV 파일을 SQL INSERT 문으로 변환
실행: python scripts/convert_csv_to_sql.py
"""
import csv
from pathlib import Path

def convert_payment_method(method):
    """결제 방법 한글 -> 영문 변환"""
    method_map = {
        "카드": "card",
        "이체": "transfer",
        "현금": "cash"
    }
    return method_map.get(method, method.lower())

def convert_csv_to_sql():
    """CSV를 SQL INSERT 문으로 변환"""
    
    print("🚀 CSV를 SQL INSERT 문으로 변환")
    print("=" * 50)
    
    # CSV 파일 경로
    csv_path = Path("backend/seed/payments_real.csv")
    sql_path = Path("sql/insert_payments.sql")
    
    if not csv_path.exists():
        print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_path}")
        return False
    
    # SQL 디렉토리 생성
    sql_path.parent.mkdir(exist_ok=True)
    
    with open(csv_path, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        
        with open(sql_path, "w", encoding="utf-8") as sqlfile:
            # 헤더 작성
            sqlfile.write("-- 로컬 결제 데이터 마이그레이션\n")
            sqlfile.write("-- 생성일: 2025-06-21\n")
            sqlfile.write("-- 총 데이터: 412건\n\n")
            
            # 트랜잭션 시작
            sqlfile.write("BEGIN;\n\n")
            
            # 임시 테이블 생성
            sqlfile.write("-- 임시 테이블 생성 (중복 방지)\n")
            sqlfile.write("CREATE TEMP TABLE temp_payments AS\n")
            sqlfile.write("SELECT * FROM payments WHERE 1=0;\n\n")
            
            # INSERT 문 생성
            sqlfile.write("-- 결제 데이터 삽입\n")
            
            batch_count = 0
            for row in reader:
                # 10개씩 배치로 처리
                if batch_count % 10 == 0:
                    if batch_count > 0:
                        sqlfile.write(";\n\n")
                    sqlfile.write("INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, created_at) VALUES\n")
                else:
                    sqlfile.write(",\n")
                
                # 값 작성
                payment_method = convert_payment_method(row['payment_method'])
                created_at = row['created_at'] if row['created_at'] else 'NOW()'
                
                sqlfile.write(f"({row['customer_id']}, '{row['payment_date']}', {row['amount']}, '{payment_method}', '{created_at}')")
                
                batch_count += 1
            
            sqlfile.write(";\n\n")
            
            # 중복 제거하고 실제 테이블에 삽입
            sqlfile.write("-- 중복을 제거하고 실제 테이블에 삽입\n")
            sqlfile.write("""INSERT INTO payments (customer_id, payment_date, amount, payment_method, created_at)
SELECT DISTINCT t.customer_id, t.payment_date, t.amount, t.payment_method, t.created_at
FROM temp_payments t
LEFT JOIN payments p ON 
    p.customer_id = t.customer_id AND 
    p.payment_date = t.payment_date AND 
    p.amount = t.amount
WHERE p.payment_id IS NULL;\n\n""")
            
            # 통계 출력
            sqlfile.write("-- 결과 확인\n")
            sqlfile.write("SELECT COUNT(*) as total_payments FROM payments;\n\n")
            
            # 트랜잭션 커밋
            sqlfile.write("COMMIT;\n\n")
            
            # 최종 통계
            sqlfile.write("-- 최종 통계 확인\n")
            sqlfile.write("""SELECT 
    COUNT(*) as total_count,
    COUNT(DISTINCT customer_id) as unique_customers,
    SUM(amount) as total_revenue,
    MIN(payment_date) as first_payment,
    MAX(payment_date) as last_payment
FROM payments;\n""")
    
    print(f"✅ SQL 파일 생성 완료: {sql_path}")
    print(f"📁 파일 크기: {sql_path.stat().st_size / 1024:.1f} KB")
    print(f"\n💡 사용 방법:")
    print(f"   1. Supabase SQL Editor 열기")
    print(f"   2. {sql_path} 파일 내용 복사")
    print(f"   3. SQL Editor에 붙여넣기")
    print(f"   4. Run 버튼 클릭")
    
    return True

def main():
    """메인 실행 함수"""
    success = convert_csv_to_sql()
    
    if success:
        print("\n🎉 변환 완료!")

if __name__ == "__main__":
    main()