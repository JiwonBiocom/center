#!/usr/bin/env python3
"""
결제 데이터 시드 및 검증 스크립트
실행: python scripts/seed_and_verify_payments.py
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import random
from datetime import date, timedelta

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

# 환경 변수 로드
load_dotenv()

def seed_payments():
    """테스트용 결제 데이터 생성"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL이 설정되지 않았습니다.")
        print("💡 .env 파일에 DATABASE_URL을 설정하거나 Supabase URL을 사용하세요.")
        return False
    
    try:
        # 데이터베이스 연결
        conn = psycopg2.connect(database_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🎯 결제 데이터 시딩 시작...")
        
        # 기존 payments 데이터 확인
        cur.execute("SELECT COUNT(*) as count FROM payments")
        existing_count = cur.fetchone()['count']
        print(f"📊 기존 결제 데이터: {existing_count}개")
        
        if existing_count > 0:
            response = input("⚠️ 기존 데이터가 있습니다. 계속 진행하시겠습니까? (y/N): ")
            if response.lower() != 'y':
                print("❌ 작업을 취소했습니다.")
                return False
        
        # 고객 ID 목록 가져오기
        cur.execute("SELECT customer_id FROM customers ORDER BY customer_id LIMIT 20")
        customer_ids = [row['customer_id'] for row in cur.fetchall()]
        
        if not customer_ids:
            print("❌ 고객 데이터가 없습니다. 먼저 고객 데이터를 생성하세요.")
            return False
        
        print(f"👥 고객 {len(customer_ids)}명의 결제 데이터를 생성합니다...")
        
        # 테스트 결제 데이터 생성
        payment_methods = ['card', 'transfer', 'cash']
        base_date = date.today()
        
        insert_query = """
        INSERT INTO payments (customer_id, payment_date, amount, payment_method)
        VALUES (%s, %s, %s, %s)
        """
        
        payments_data = []
        for i, customer_id in enumerate(customer_ids):
            # 각 고객당 1-3개의 결제 데이터 생성
            num_payments = random.randint(1, 3)
            
            for j in range(num_payments):
                payment_date = base_date - timedelta(days=random.randint(1, 30))
                amount = random.choice([50000, 80000, 100000, 150000, 200000, 250000])
                method = random.choice(payment_methods)
                
                payments_data.append((customer_id, payment_date, amount, method))
        
        # 배치 삽입
        cur.executemany(insert_query, payments_data)
        conn.commit()
        
        print(f"✅ {len(payments_data)}개의 결제 데이터를 생성했습니다.")
        
        # 결과 확인
        cur.execute("SELECT COUNT(*) as count FROM payments")
        total_count = cur.fetchone()['count']
        print(f"📊 총 결제 데이터: {total_count}개")
        
        # 샘플 데이터 표시
        cur.execute("""
            SELECT p.payment_id, c.name, p.payment_date, p.amount, p.payment_method
            FROM payments p
            JOIN customers c ON p.customer_id = c.customer_id
            ORDER BY p.payment_id DESC
            LIMIT 5
        """)
        samples = cur.fetchall()
        
        print("\n📋 생성된 샘플 데이터:")
        for sample in samples:
            print(f"  - {sample['name']}: {sample['payment_date']} | ₩{sample['amount']:,} | {sample['payment_method']}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def verify_api():
    """API 동작 확인"""
    
    try:
        print("\n🔍 API 동작 확인 중...")
        
        # Railway API 테스트
        api_url = "https://center-production-1421.up.railway.app/api/v1/payments/"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API 정상 응답: {len(data)}개의 결제 데이터 반환")
            
            if data:
                print("\n📋 API 응답 샘플:")
                for i, payment in enumerate(data[:3]):
                    print(f"  {i+1}. ID:{payment.get('payment_id')} | {payment.get('payment_date')} | ₩{payment.get('amount'):,}")
            else:
                print("⚠️ API 응답은 정상이지만 데이터가 비어있습니다.")
        else:
            print(f"❌ API 에러: {response.status_code}")
            print(f"응답: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ API 테스트 실패: {e}")

def main():
    """메인 실행 함수"""
    print("🚀 결제 데이터 시드 및 검증 도구")
    print("=" * 50)
    
    # 1. 결제 데이터 시딩
    success = seed_payments()
    
    if success:
        # 2. API 검증
        verify_api()
        
        print("\n🎉 작업 완료!")
        print("💡 이제 https://center-ten.vercel.app/payments 에서 결제 데이터를 확인할 수 있습니다.")
    else:
        print("\n❌ 시딩 실패. 환경 설정을 확인하세요.")

if __name__ == "__main__":
    main()