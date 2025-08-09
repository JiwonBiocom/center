#!/usr/bin/env python3
"""
대시보드 성능 향상을 위한 인덱스 추가
"""
import psycopg2
from datetime import datetime

DATABASE_URL = "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def add_performance_indexes():
    """성능 최적화를 위한 인덱스 추가"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print(f"🚀 대시보드 성능 최적화 인덱스 추가")
    print(f"시간: {datetime.now()}")
    print("=" * 60)
    
    indexes = [
        # Payment 테이블 인덱스
        {
            "name": "idx_payments_date_amount",
            "table": "payments",
            "columns": "(payment_date, amount)",
            "description": "대시보드 매출 통계용"
        },
        {
            "name": "idx_payments_customer_date",
            "table": "payments",
            "columns": "(customer_id, payment_date)",
            "description": "고객별 결제 조회용"
        },
        
        # Customer 테이블 인덱스
        {
            "name": "idx_customers_first_visit",
            "table": "customers",
            "columns": "(first_visit_date)",
            "description": "신규 고객 통계용"
        },
        {
            "name": "idx_customers_last_visit",
            "table": "customers",
            "columns": "(last_visit_date)",
            "description": "고객 상태 조회용"
        },
        
        # ServiceUsage 테이블 인덱스
        {
            "name": "idx_service_usage_date",
            "table": "service_usage",
            "columns": "(service_date)",
            "description": "일별 방문 통계용"
        },
        {
            "name": "idx_service_usage_customer_date",
            "table": "service_usage",
            "columns": "(customer_id, service_date)",
            "description": "고객별 서비스 이용 조회용"
        },
        
        # PackagePurchase 테이블 인덱스
        {
            "name": "idx_package_purchase_active",
            "table": "package_purchases",
            "columns": "(remaining_sessions, expiry_date)",
            "where": "remaining_sessions > 0",
            "description": "활성 패키지 조회용"
        },
        
        # LeadConsultationHistory 테이블 인덱스
        {
            "name": "idx_lead_consultation_date_type",
            "table": "lead_consultation_history",
            "columns": "(consultation_date, consultation_type)",
            "description": "주간 방문 상담 통계용"
        }
    ]
    
    created_count = 0
    for idx in indexes:
        try:
            # 인덱스 존재 여부 확인
            cursor.execute("""
                SELECT 1 FROM pg_indexes 
                WHERE indexname = %s
            """, (idx['name'],))
            
            if cursor.fetchone():
                print(f"✓ {idx['name']} - 이미 존재")
            else:
                # 인덱스 생성
                where_clause = f"WHERE {idx['where']}" if idx.get('where') else ""
                sql = f"""
                    CREATE INDEX IF NOT EXISTS {idx['name']} 
                    ON {idx['table']} {idx['columns']} {where_clause}
                """
                cursor.execute(sql)
                created_count += 1
                print(f"✅ {idx['name']} - 생성됨 ({idx['description']})")
                
        except Exception as e:
            print(f"❌ {idx['name']} - 실패: {e}")
            # CONCURRENTLY 옵션은 트랜잭션 내에서 사용할 수 없으므로 개별 실행
            conn.rollback()
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
    
    # 통계 업데이트
    try:
        cursor.execute("ANALYZE payments;")
        cursor.execute("ANALYZE customers;")
        cursor.execute("ANALYZE service_usage;")
        cursor.execute("ANALYZE package_purchases;")
        cursor.execute("ANALYZE lead_consultation_history;")
        print(f"\n✅ 테이블 통계 업데이트 완료")
    except Exception as e:
        print(f"\n❌ 통계 업데이트 실패: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n📊 결과:")
    print(f"  - 생성된 인덱스: {created_count}개")
    print(f"  - 대시보드 API 성능 향상 예상")
    print(f"\n💡 권장사항:")
    print(f"  1. Railway 서버 재시작으로 쿼리 플랜 갱신")
    print(f"  2. 성능 측정하여 개선 효과 확인")

if __name__ == "__main__":
    add_performance_indexes()