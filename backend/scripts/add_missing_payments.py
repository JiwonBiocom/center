"""
Excel에는 있지만 DB에 없는 결제 데이터 추가
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text
from core.config import settings

# Excel 파일 경로
EXCEL_PATH = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/★2025년 AIBIO 결제현황.xlsx"

def get_or_create_customer(conn, name, phone=None):
    """고객 조회 또는 생성"""
    # 먼저 고객이 있는지 확인
    query = text("SELECT customer_id FROM customers WHERE name = :name")
    result = conn.execute(query, {"name": name}).fetchone()
    
    if result:
        return result[0]
    else:
        # 고객이 없으면 생성
        insert_query = text("""
            INSERT INTO customers (name, phone, first_visit_date, created_at, updated_at)
            VALUES (:name, :phone, :visit_date, NOW(), NOW())
            RETURNING customer_id
        """)
        result = conn.execute(insert_query, {
            "name": name,
            "phone": phone or "미입력",
            "visit_date": datetime.now().date()
        }).fetchone()
        print(f"  새 고객 생성: {name}")
        return result[0]

def add_missing_payments(month):
    """특정 월의 누락된 결제 데이터 추가"""
    sheet_name = f"2025년 {month}월"
    
    # Excel 데이터 읽기
    df = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name, header=2)
    excel_data = df.dropna(subset=['결제일자', '고객명', '결제 금액'])
    
    print(f"\n{sheet_name} 데이터 추가:")
    print(f"Excel 총 {len(excel_data)}건")
    
    engine = create_engine(settings.DATABASE_URL)
    
    # DB에서 해당 월 기존 데이터 조회
    start_date = f"2025-{month:02d}-01"
    end_date = f"2025-{month+1:02d}-01" if month < 4 else "2025-05-01"
    
    query = text("""
        SELECT c.name, p.payment_date, p.amount
        FROM payments p
        JOIN customers c ON p.customer_id = c.customer_id
        WHERE p.payment_date >= :start_date 
        AND p.payment_date < :end_date
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query, {"start_date": start_date, "end_date": end_date})
        existing_payments = set()
        for row in result:
            existing_payments.add((row[0], row[1].strftime('%Y-%m-%d'), float(row[2])))
    
    print(f"DB 기존 {len(existing_payments)}건")
    
    # 추가할 결제 찾기
    added_count = 0
    with engine.begin() as conn:
        for _, row in excel_data.iterrows():
            payment_date = pd.to_datetime(row['결제일자']).date()
            customer_name = row['고객명']
            amount = float(row['결제 금액'])
            
            # 이미 존재하는지 확인
            key = (customer_name, payment_date.strftime('%Y-%m-%d'), amount)
            if key not in existing_payments:
                # 고객 ID 가져오기 또는 생성
                customer_id = get_or_create_customer(conn, customer_name)
                
                # 결제 추가
                insert_query = text("""
                    INSERT INTO payments (
                        customer_id, payment_date, amount, 
                        payment_method, card_holder_name, approval_number,
                        payment_staff, service_type, created_at
                    ) VALUES (
                        :customer_id, :payment_date, :amount,
                        :payment_method, :card_holder_name, :approval_number,
                        :payment_staff, :service_type, NOW()
                    )
                """)
                
                # Excel에서 추가 정보 가져오기
                payment_method = "카드"
                card_holder_name = row.get('카드 명의자명', customer_name)
                approval_number = str(row.get('승인번호', ''))
                payment_staff = row.get('결제 담당자', '미입력')
                service_type = row.get('결제 프로그램', '미입력')
                
                conn.execute(insert_query, {
                    "customer_id": customer_id,
                    "payment_date": payment_date,
                    "amount": amount,
                    "payment_method": payment_method,
                    "card_holder_name": card_holder_name,
                    "approval_number": approval_number,
                    "payment_staff": payment_staff,
                    "service_type": service_type
                })
                
                added_count += 1
                print(f"  추가: {payment_date} {customer_name} {amount:,.0f}원")
    
    print(f"총 {added_count}건 추가 완료")
    return added_count

def verify_data():
    """데이터 추가 후 검증"""
    print("\n" + "="*60)
    print("데이터 추가 후 검증")
    print("="*60)
    
    engine = create_engine(settings.DATABASE_URL)
    
    for month in range(1, 5):
        # Excel 데이터
        sheet_name = f"2025년 {month}월"
        df = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name, header=2)
        excel_data = df.dropna(subset=['결제일자', '고객명', '결제 금액'])
        excel_total = excel_data['결제 금액'].sum()
        
        # DB 데이터
        start_date = f"2025-{month:02d}-01"
        end_date = f"2025-{month+1:02d}-01" if month < 4 else "2025-05-01"
        
        query = text("""
            SELECT COUNT(*), SUM(amount)
            FROM payments
            WHERE payment_date >= :start_date 
            AND payment_date < :end_date
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, {"start_date": start_date, "end_date": end_date}).fetchone()
            db_count, db_total = result
        
        print(f"\n{month}월:")
        print(f"  Excel: {len(excel_data)}건, {excel_total:,.0f}원")
        print(f"  DB: {db_count}건, {float(db_total):,.0f}원")
        print(f"  차이: {db_count - len(excel_data)}건, {float(db_total) - excel_total:,.0f}원")

def main():
    print("누락된 결제 데이터 추가")
    print("="*60)
    
    # 1월 취소 건 추가
    print("\n[1] 1월 취소 건 처리")
    # 취소 건은 별도 처리 필요 (음수 금액)
    
    # 3월과 4월 데이터 추가
    print("\n[2] 3월 데이터 추가")
    add_missing_payments(3)
    
    print("\n[3] 4월 데이터 추가")
    add_missing_payments(4)
    
    # 검증
    print("\n[4] 데이터 검증")
    verify_data()

if __name__ == "__main__":
    main()