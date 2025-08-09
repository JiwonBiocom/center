"""
1월 장재미 데이터 최종 수정
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from core.config import settings

def check_and_fix_january():
    """1월 장재미 데이터 확인 및 수정"""
    engine = create_engine(settings.DATABASE_URL)
    
    # 장재미의 1월 결제 데이터 확인
    query = text("""
        SELECT payment_id, payment_date, amount, service_type
        FROM payments p
        JOIN customers c ON p.customer_id = c.customer_id
        WHERE c.name = '장재미' 
        AND p.payment_date >= '2025-01-01' 
        AND p.payment_date < '2025-02-01'
        ORDER BY p.payment_date
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query)
        payments = result.fetchall()
        
    print("현재 DB의 장재미 1월 결제:")
    total = 0
    for payment in payments:
        print(f"  ID: {payment[0]}, 날짜: {payment[1]}, 금액: {payment[2]:,.0f}원, 서비스: {payment[3]}")
        total += float(payment[2])
    print(f"  합계: {total:,.0f}원")
    
    # Excel 데이터에 따르면:
    # 1/18: 4,000,000원
    # 취소 예정: -4,000,000원
    # 1/23: 500,000원
    # 1/23: 13,500,000원
    # 합계: 14,000,000원
    
    print("\n\nExcel의 장재미 1월 결제:")
    print("  1/18: 4,000,000원")
    print("  취소 예정: -4,000,000원")
    print("  1/23: 500,000원")
    print("  1/23: 13,500,000원")
    print("  합계: 14,000,000원")
    
    # 누락된 1/18 4,000,000원 추가
    with engine.begin() as conn:
        # 장재미 customer_id 조회
        query = text("SELECT customer_id FROM customers WHERE name = '장재미'")
        result = conn.execute(query).fetchone()
        
        if result:
            customer_id = result[0]
            
            # 1/18 4,000,000원 건이 있는지 확인
            check_query = text("""
                SELECT COUNT(*) FROM payments 
                WHERE customer_id = :customer_id 
                AND payment_date = '2025-01-18' 
                AND amount = 4000000
            """)
            count = conn.execute(check_query, {"customer_id": customer_id}).scalar()
            
            if count == 0:
                # 추가
                insert_query = text("""
                    INSERT INTO payments (
                        customer_id, payment_date, amount, 
                        payment_method, card_holder_name, 
                        payment_staff, service_type, created_at
                    ) VALUES (
                        :customer_id, '2025-01-18', 4000000,
                        '카드', '장재미', 
                        '미입력', '미입력', NOW()
                    )
                """)
                conn.execute(insert_query, {"customer_id": customer_id})
                print("\n\n1/18 장재미 4,000,000원 추가 완료")

def verify_final():
    """최종 검증"""
    engine = create_engine(settings.DATABASE_URL)
    
    print("\n\n최종 검증:")
    print("="*60)
    
    # 전체 1월 데이터 확인
    query = text("""
        SELECT COUNT(*), SUM(amount)
        FROM payments
        WHERE payment_date >= '2025-01-01' 
        AND payment_date < '2025-02-01'
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query).fetchone()
        count, total = result
        
    print(f"1월 DB 총계: {count}건, {float(total):,.0f}원")
    print(f"1월 Excel 총계: 17건, 18,033,000원")
    
    # 차이가 있는 경우 상세 확인
    if count == 17 and abs(float(total) - 18033000) < 1:
        print("\n✓ 데이터가 일치합니다!")
    else:
        print(f"\n✗ 아직 차이가 있습니다: 건수 {count-17}, 금액 {float(total)-18033000:,.0f}원")

def main():
    print("1월 장재미 데이터 최종 수정")
    print("="*60)
    
    check_and_fix_january()
    verify_final()

if __name__ == "__main__":
    main()