"""
1월 취소 건 및 누락 데이터 처리
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

def fix_january_data():
    """1월 데이터 정정"""
    engine = create_engine(settings.DATABASE_URL)
    
    # Excel에서 1월 데이터 읽기
    df = pd.read_excel(EXCEL_PATH, sheet_name="2025년 1월", header=2)
    excel_data = df.dropna(subset=['결제일자', '고객명', '결제 금액'])
    
    print("1월 Excel 데이터 확인:")
    print(f"총 {len(excel_data)}건")
    
    # 송선경 취소 건 찾기
    cancellations = excel_data[excel_data['결제 금액'] < 0]
    print(f"\n취소 건: {len(cancellations)}건")
    for _, row in cancellations.iterrows():
        print(f"  {row['결제일자']} {row['고객명']} {row['결제 금액']:,.0f}원")
    
    # 현재 DB 상태 확인
    query = text("""
        SELECT c.name, COUNT(*), SUM(p.amount)
        FROM payments p
        JOIN customers c ON p.customer_id = c.customer_id
        WHERE p.payment_date >= '2025-01-01' AND p.payment_date < '2025-02-01'
        GROUP BY c.name
        ORDER BY c.name
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query)
        db_data = {row[0]: (row[1], float(row[2])) for row in result}
    
    print("\n현재 DB 상태:")
    for name, (count, total) in db_data.items():
        print(f"  {name}: {count}건, {total:,.0f}원")
    
    # Excel과 비교
    excel_by_customer = excel_data.groupby('고객명').agg({
        '결제 금액': ['count', 'sum']
    })
    
    print("\nExcel vs DB 차이:")
    missing_customers = []
    
    for customer_name in excel_by_customer.index:
        excel_count = excel_by_customer.loc[customer_name, ('결제 금액', 'count')]
        excel_sum = excel_by_customer.loc[customer_name, ('결제 금액', 'sum')]
        
        if customer_name in db_data:
            db_count, db_sum = db_data[customer_name]
            if excel_count != db_count or abs(excel_sum - db_sum) > 1:
                print(f"  {customer_name}: Excel({excel_count}건, {excel_sum:,.0f}원) vs DB({db_count}건, {db_sum:,.0f}원)")
        else:
            print(f"  {customer_name}: DB에 없음 (Excel: {excel_count}건, {excel_sum:,.0f}원)")
            missing_customers.append(customer_name)
    
    # 누락된 고객 데이터 추가
    if missing_customers:
        print(f"\n누락된 고객 {len(missing_customers)}명의 데이터를 추가합니다...")
        
        with engine.begin() as conn:
            for customer_name in missing_customers:
                customer_data = excel_data[excel_data['고객명'] == customer_name]
                customer_id = get_or_create_customer(conn, customer_name)
                
                for _, row in customer_data.iterrows():
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
                    
                    payment_date = pd.to_datetime(row['결제일자']).date()
                    amount = float(row['결제 금액'])
                    
                    conn.execute(insert_query, {
                        "customer_id": customer_id,
                        "payment_date": payment_date,
                        "amount": amount,
                        "payment_method": "카드",
                        "card_holder_name": row.get('카드 명의자명', customer_name),
                        "approval_number": str(row.get('승인번호', '')),
                        "payment_staff": row.get('결제 담당자', '미입력'),
                        "service_type": row.get('결제 프로그램', '미입력')
                    })
                    
                    print(f"  추가: {payment_date} {customer_name} {amount:,.0f}원")

def verify_final_state():
    """최종 상태 검증"""
    print("\n" + "="*60)
    print("최종 검증")
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
        
        if len(excel_data) == db_count and abs(excel_total - float(db_total)) < 1:
            print("  ✓ 일치")
        else:
            print(f"  ✗ 불일치 - 건수 차이: {db_count - len(excel_data)}, 금액 차이: {float(db_total) - excel_total:,.0f}원")

def main():
    print("1월 데이터 정정")
    print("="*60)
    
    fix_january_data()
    verify_final_state()

if __name__ == "__main__":
    main()