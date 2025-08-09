"""데이터베이스 인덱스 추가 스크립트"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from core.config import settings

def add_indexes():
    """성능 향상을 위한 인덱스 추가"""
    engine = create_engine(settings.DATABASE_URL)
    
    indexes = [
        # 고객 테이블 - 검색 성능 최적화
        "CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);",
        "CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name);",
        "CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);",
        "CREATE INDEX IF NOT EXISTS idx_customers_first_visit_date ON customers(first_visit_date);",
        "CREATE INDEX IF NOT EXISTS idx_customers_created_at ON customers(created_at);",
        
        # 예약 테이블 - 달력 및 검색 최적화
        "CREATE INDEX IF NOT EXISTS idx_reservations_date_time ON reservations(reservation_date, reservation_time);",
        "CREATE INDEX IF NOT EXISTS idx_reservations_customer_id ON reservations(customer_id);",
        "CREATE INDEX IF NOT EXISTS idx_reservations_staff_id ON reservations(staff_id);",
        "CREATE INDEX IF NOT EXISTS idx_reservations_status ON reservations(status);",
        "CREATE INDEX IF NOT EXISTS idx_reservations_service_type_id ON reservations(service_type_id);",
        "CREATE INDEX IF NOT EXISTS idx_reservations_composite ON reservations(reservation_date, status, customer_id);",
        
        # 결제 테이블 - 매출 분석 최적화
        "CREATE INDEX IF NOT EXISTS idx_payments_payment_date ON payments(payment_date);",
        "CREATE INDEX IF NOT EXISTS idx_payments_customer_id ON payments(customer_id);",
        "CREATE INDEX IF NOT EXISTS idx_payments_payment_method ON payments(payment_method);",
        "CREATE INDEX IF NOT EXISTS idx_payments_date_customer ON payments(payment_date, customer_id);",
        "CREATE INDEX IF NOT EXISTS idx_payments_amount ON payments(amount);",
        
        # 서비스 이용 테이블 - 통계 및 분석 최적화
        "CREATE INDEX IF NOT EXISTS idx_service_usage_service_date ON service_usage(service_date);",
        "CREATE INDEX IF NOT EXISTS idx_service_usage_customer_id ON service_usage(customer_id);",
        "CREATE INDEX IF NOT EXISTS idx_service_usage_service_type_id ON service_usage(service_type_id);",
        "CREATE INDEX IF NOT EXISTS idx_service_usage_package_id ON service_usage(package_id);",
        "CREATE INDEX IF NOT EXISTS idx_service_usage_reservation_id ON service_usage(reservation_id);",
        "CREATE INDEX IF NOT EXISTS idx_service_usage_date_customer ON service_usage(service_date, customer_id);",
        "CREATE INDEX IF NOT EXISTS idx_service_usage_date_type ON service_usage(service_date, service_type_id);",
        
        # 패키지 구매 테이블 - 잔여 세션 및 만료일 최적화
        "CREATE INDEX IF NOT EXISTS idx_package_purchases_customer_id ON package_purchases(customer_id);",
        "CREATE INDEX IF NOT EXISTS idx_package_purchases_purchase_date ON package_purchases(purchase_date);",
        "CREATE INDEX IF NOT EXISTS idx_package_purchases_expiry_date ON package_purchases(expiry_date);",
        "CREATE INDEX IF NOT EXISTS idx_package_purchases_remaining_sessions ON package_purchases(remaining_sessions);",
        "CREATE INDEX IF NOT EXISTS idx_package_purchases_active ON package_purchases(customer_id, remaining_sessions) WHERE remaining_sessions > 0;",
        
        # 리드 테이블 - 마케팅 분석 최적화
        "CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);",
        "CREATE INDEX IF NOT EXISTS idx_leads_source ON leads(source);",
        "CREATE INDEX IF NOT EXISTS idx_leads_phone ON leads(phone);",
        "CREATE INDEX IF NOT EXISTS idx_leads_status_source ON leads(status, source);",
        
        # 키트 테이블 - 배송 및 상태 최적화
        "CREATE INDEX IF NOT EXISTS idx_kits_customer_id ON kits(customer_id);",
        "CREATE INDEX IF NOT EXISTS idx_kits_kit_type ON kits(kit_type);",
        "CREATE INDEX IF NOT EXISTS idx_kits_delivery_date ON kits(delivery_date);",
        "CREATE INDEX IF NOT EXISTS idx_kits_status ON kits(status);",
        "CREATE INDEX IF NOT EXISTS idx_kits_customer_status ON kits(customer_id, status);",
        
        # 사용자 테이블 - 인증 최적화
        "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
        "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);",
        "CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);",
        
        # 전체 텍스트 검색 인덱스
        "CREATE INDEX IF NOT EXISTS idx_customers_name_search ON customers USING gin(to_tsvector('korean', name)) WHERE name IS NOT NULL;",
        "CREATE INDEX IF NOT EXISTS idx_customers_memo_search ON customers USING gin(to_tsvector('korean', memo)) WHERE memo IS NOT NULL;"
    ]
    
    with engine.connect() as conn:
        for index_sql in indexes:
            try:
                conn.execute(text(index_sql))
                conn.commit()
                print(f"✅ 인덱스 생성 성공: {index_sql.split('idx_')[1].split(' ')[0]}")
            except Exception as e:
                print(f"❌ 인덱스 생성 실패: {str(e)}")
    
    print("\n인덱스 추가 완료!")

if __name__ == "__main__":
    add_indexes()