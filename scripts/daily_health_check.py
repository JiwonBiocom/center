#!/usr/bin/env python3
"""
Daily Health Check Script
매일 실행되어 시스템 상태를 점검하고 필수 데이터를 확인합니다.
"""
import os
import sys
import psycopg2
import requests
from datetime import datetime
import json

# 환경 변수에서 설정 읽기
DATABASE_URL = os.getenv('DATABASE_URL')
API_URL = os.getenv('API_URL', 'https://aibio-api.railway.app')

def check_database_health():
    """데이터베이스 연결 및 필수 데이터 확인"""
    print("🔍 Checking database health...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # 1. 테이블 존재 확인
        essential_tables = [
            'customers', 'payments', 'packages', 'reservations',
            'service_types', 'users'  # reservation_services는 실제로 존재하지 않음
        ]
        
        for table in essential_tables:
            cur.execute(f"""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                )
            """, (table,))
            exists = cur.fetchone()[0]
            if not exists:
                print(f"❌ Table '{table}' does not exist!")
                return False
            print(f"✅ Table '{table}' exists")
        
        # 2. 필수 데이터 확인
        # service_types 테이블에 데이터가 있는지 확인
        cur.execute("SELECT COUNT(*) FROM service_types")
        service_count = cur.fetchone()[0]
        if service_count == 0:
            print("⚠️ Warning: No service types found. Creating default services...")
            create_default_services(cur)
            conn.commit()
        else:
            print(f"✅ Found {service_count} service types")
        
        # 3. 최소 데이터 확인
        checks = [
            ("customers", 0),  # 고객은 0명일 수 있음
            ("users", 1),      # 최소 1명의 사용자 필요
            ("packages", 0),   # 패키지는 0개일 수 있음
        ]
        
        for table, min_count in checks:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            if count < min_count:
                print(f"❌ Table '{table}' has {count} rows (minimum: {min_count})")
                return False
            print(f"✅ Table '{table}' has {count} rows")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def create_default_services(cursor):
    """기본 서비스 타입 생성"""
    default_services = [
        ('카이로프랙틱', 'chiropractic', True),
        ('물리치료', 'physical_therapy', True),
        ('마사지', 'massage', True),
        ('재활운동', 'rehabilitation', True),
        ('도수치료', 'manual_therapy', True)
    ]
    
    for name, code, active in default_services:
        cursor.execute("""
            INSERT INTO service_types (name, code, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, NOW(), NOW())
            ON CONFLICT (code) DO NOTHING
        """, (name, code, active))
    
    print("✅ Created default service types")

def check_api_health():
    """API 서버 상태 확인"""
    print("\n🔍 Checking API health...")
    
    endpoints = [
        ("/health", "Health check"),
        ("/dashboard/stats", "Dashboard stats"),
        ("/customers/", "Customers list"),
        ("/reservations/", "Reservations list"),
    ]
    
    all_healthy = True
    
    for endpoint, description in endpoints:
        try:
            url = f"{API_URL}{endpoint}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {description}: OK")
            elif response.status_code == 401:
                print(f"⚠️ {description}: Requires authentication")
            elif response.status_code == 404:
                # /api/v1 prefix를 시도
                alt_url = f"{API_URL}/api/v1{endpoint}"
                alt_response = requests.get(alt_url, timeout=10)
                if alt_response.status_code in [200, 401]:
                    print(f"⚠️ {description}: Found at /api/v1{endpoint}")
                else:
                    print(f"❌ {description}: Not found")
            else:
                print(f"❌ {description}: Status {response.status_code}")
                all_healthy = False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {description}: Failed - {e}")
            all_healthy = False
    
    return all_healthy

def generate_health_report():
    """건강 체크 리포트 생성"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "database_healthy": False,
        "api_healthy": False,
        "overall_status": "unhealthy",
        "details": []
    }
    
    # 데이터베이스 체크
    report["database_healthy"] = check_database_health()
    
    # API 체크
    report["api_healthy"] = check_api_health()
    
    # 전체 상태
    if report["database_healthy"] and report["api_healthy"]:
        report["overall_status"] = "healthy"
        print("\n✅ Overall system status: HEALTHY")
    else:
        print("\n❌ Overall system status: UNHEALTHY")
        
        # 이메일 알림 발송
        send_email_alert(report)
    
    # 리포트 저장
    with open('health_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    return report["overall_status"] == "healthy"

def send_email_alert(report):
    """이메일 알림 발송"""
    try:
        # 이메일 수신자 환경 변수에서 가져오기
        recipients = os.getenv('ALERT_EMAIL_RECIPIENTS', '').split(',')
        if not recipients or recipients == ['']:
            print("⚠️ No email recipients configured (ALERT_EMAIL_RECIPIENTS)")
            return
        
        # Gmail 토큰이 있는 경우에만 발송
        if os.path.exists('config/gmail_token.json'):
            from email_notifier import EmailNotifier
            notifier = EmailNotifier()
            notifier.send_health_check_alert(recipients, report)
        else:
            print("⚠️ Gmail not configured. Run: python scripts/setup_gmail_oauth.py")
    except Exception as e:
        print(f"⚠️ Failed to send email alert: {e}")

def main():
    print(f"🏥 Daily Health Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not set!")
        sys.exit(1)
    
    # 건강 체크 실행
    is_healthy = generate_health_report()
    
    # 결과에 따라 종료 코드 설정
    sys.exit(0 if is_healthy else 1)

if __name__ == "__main__":
    main()