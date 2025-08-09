#!/usr/bin/env python3
"""
시스템 전체 상태 진단 스크립트
각 해결 단계 전에 현재 상태를 정확히 파악
"""

import requests
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import subprocess
from datetime import datetime

class SystemDiagnostic:
    def __init__(self):
        self.backend_url = "https://center-production-1421.up.railway.app"
        self.frontend_url = "https://center-ten.vercel.app"
        self.db_config = {
            'host': 'aws-0-ap-northeast-2.pooler.supabase.com',
            'port': 6543,
            'database': 'postgres',
            'user': 'postgres.wvcxzyvmwwrbjpeuyvuh',
            'password': 'bico6819!!'
        }
        self.diagnosis_report = {
            'timestamp': datetime.now().isoformat(),
            'backend_status': {},
            'database_status': {},
            'frontend_status': {},
            'api_endpoints': {},
            'recommendations': []
        }
    
    def check_backend_health(self):
        """백엔드 서버 상태 확인"""
        print("🔍 백엔드 서버 상태 확인...")
        
        try:
            # 기본 연결 확인
            response = requests.get(f"{self.backend_url}/", timeout=10)
            self.diagnosis_report['backend_status']['basic_connection'] = {
                'status': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'content': response.json() if response.headers.get('content-type', '').startswith('application/json') else 'HTML'
            }
            print(f"   ✅ 기본 연결: {response.status_code}")
            
            # API 문서 확인
            docs_response = requests.get(f"{self.backend_url}/docs", timeout=10)
            self.diagnosis_report['backend_status']['api_docs'] = {
                'status': docs_response.status_code,
                'available': docs_response.status_code == 200
            }
            print(f"   📚 API 문서: {docs_response.status_code}")
            
            # OpenAPI 스펙 확인
            openapi_response = requests.get(f"{self.backend_url}/openapi.json", timeout=10)
            if openapi_response.status_code == 200:
                openapi_data = openapi_response.json()
                endpoints = list(openapi_data.get('paths', {}).keys())
                self.diagnosis_report['backend_status']['total_endpoints'] = len(endpoints)
                print(f"   📡 총 엔드포인트: {len(endpoints)}개")
            
        except Exception as e:
            self.diagnosis_report['backend_status']['error'] = str(e)
            print(f"   ❌ 백엔드 연결 실패: {e}")
    
    def check_critical_api_endpoints(self):
        """핵심 API 엔드포인트 상태 확인"""
        print("\n🔍 핵심 API 엔드포인트 상태 확인...")
        
        critical_endpoints = [
            ('/api/v1/auth/login', 'POST', {'email': 'test@test.com', 'password': 'test'}),
            ('/api/v1/customers/', 'GET', None),
            ('/api/v1/customers/count', 'GET', None),
            ('/api/v1/payments/', 'GET', None),
            ('/api/v1/packages/', 'GET', None),
            ('/api/v1/services/', 'GET', None),
        ]
        
        for endpoint, method, data in critical_endpoints:
            try:
                url = f"{self.backend_url}{endpoint}"
                if method == 'GET':
                    response = requests.get(url, timeout=10)
                elif method == 'POST':
                    response = requests.post(url, json=data, timeout=10)
                
                endpoint_status = {
                    'status': response.status_code,
                    'response_time': response.elapsed.total_seconds(),
                    'content_length': len(response.content)
                }
                
                if response.status_code < 500:
                    try:
                        endpoint_status['response_data'] = response.json()
                    except:
                        endpoint_status['response_data'] = response.text[:200]
                
                self.diagnosis_report['api_endpoints'][endpoint] = endpoint_status
                
                status_icon = "✅" if response.status_code < 400 else "⚠️" if response.status_code < 500 else "❌"
                print(f"   {status_icon} {method} {endpoint}: {response.status_code}")
                
            except Exception as e:
                self.diagnosis_report['api_endpoints'][endpoint] = {'error': str(e)}
                print(f"   ❌ {method} {endpoint}: {str(e)}")
    
    def check_database_status(self):
        """데이터베이스 상태 확인"""
        print("\n🔍 데이터베이스 상태 확인...")
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # 테이블 목록 확인
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = [row['table_name'] for row in cur.fetchall()]
            self.diagnosis_report['database_status']['tables'] = tables
            print(f"   📊 테이블 수: {len(tables)}개")
            
            # 각 테이블의 레코드 수 확인
            table_counts = {}
            for table in tables:
                try:
                    cur.execute(f"SELECT COUNT(*) as count FROM {table}")
                    count = cur.fetchone()['count']
                    table_counts[table] = count
                    print(f"   📈 {table}: {count}건")
                except Exception as e:
                    table_counts[table] = f"Error: {str(e)}"
                    print(f"   ❌ {table}: {str(e)}")
            
            self.diagnosis_report['database_status']['table_counts'] = table_counts
            
            # 중요 테이블 스키마 확인
            important_tables = ['customers', 'payments', 'packages', 'service_types']
            for table in important_tables:
                if table in tables:
                    cur.execute(f"""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns 
                        WHERE table_name = '{table}'
                        ORDER BY ordinal_position
                    """)
                    columns = cur.fetchall()
                    self.diagnosis_report['database_status'][f'{table}_schema'] = [
                        f"{col['column_name']}:{col['data_type']}" for col in columns
                    ]
            
            conn.close()
            print("   ✅ 데이터베이스 연결 성공")
            
        except Exception as e:
            self.diagnosis_report['database_status']['error'] = str(e)
            print(f"   ❌ 데이터베이스 연결 실패: {e}")
    
    def check_frontend_status(self):
        """프론트엔드 상태 확인"""
        print("\n🔍 프론트엔드 상태 확인...")
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            self.diagnosis_report['frontend_status'] = {
                'status': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'content_length': len(response.content)
            }
            print(f"   ✅ 프론트엔드 접속: {response.status_code}")
            
        except Exception as e:
            self.diagnosis_report['frontend_status']['error'] = str(e)
            print(f"   ❌ 프론트엔드 접속 실패: {e}")
    
    def generate_recommendations(self):
        """현재 상황에 따른 권장사항 생성"""
        print("\n🎯 권장사항 생성...")
        
        recommendations = []
        
        # API 엔드포인트 분석
        failed_endpoints = []
        for endpoint, status in self.diagnosis_report['api_endpoints'].items():
            if isinstance(status, dict) and status.get('status', 0) >= 500:
                failed_endpoints.append(endpoint)
        
        if failed_endpoints:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'API_SERVER',
                'issue': f'{len(failed_endpoints)}개 API 엔드포인트에서 500 에러',
                'action': 'API 서버 내부 오류 수정 필요',
                'endpoints': failed_endpoints
            })
        
        # 로그인 시스템 분석
        login_status = self.diagnosis_report['api_endpoints'].get('/api/v1/auth/login', {})
        if login_status.get('status') == 401:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'AUTHENTICATION',
                'issue': '로그인 API 401 에러',
                'action': '관리자 계정 생성 또는 기존 계정 패스워드 확인 필요'
            })
        
        # 데이터베이스 분석
        db_counts = self.diagnosis_report['database_status'].get('table_counts', {})
        if db_counts.get('customers', 0) > 0 and db_counts.get('payments', 0) == 0:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'DATA_MIGRATION',
                'issue': '고객 데이터만 있고 결제/패키지 데이터 없음',
                'action': '완전한 데이터 마이그레이션 필요'
            })
        
        self.diagnosis_report['recommendations'] = recommendations
        
        for rec in recommendations:
            priority_icon = "🚨" if rec['priority'] == 'HIGH' else "⚠️"
            print(f"   {priority_icon} [{rec['category']}] {rec['issue']}")
            print(f"      → {rec['action']}")
    
    def save_report(self):
        """진단 리포트 저장"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"/Users/vibetj/coding/center/system_diagnosis_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.diagnosis_report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 진단 리포트 저장: {report_file}")
        return report_file
    
    def run_full_diagnosis(self):
        """전체 시스템 진단 실행"""
        print("🏥 === 시스템 전체 진단 시작 ===")
        print("=" * 60)
        
        self.check_backend_health()
        self.check_critical_api_endpoints()
        self.check_database_status()
        self.check_frontend_status()
        self.generate_recommendations()
        
        report_file = self.save_report()
        
        print("\n" + "=" * 60)
        print("📋 진단 완료 요약:")
        print(f"   백엔드 상태: {'✅' if not self.diagnosis_report['backend_status'].get('error') else '❌'}")
        print(f"   데이터베이스: {'✅' if not self.diagnosis_report['database_status'].get('error') else '❌'}")
        print(f"   프론트엔드: {'✅' if not self.diagnosis_report['frontend_status'].get('error') else '❌'}")
        print(f"   권장사항: {len(self.diagnosis_report['recommendations'])}개")
        
        return self.diagnosis_report

def main():
    diagnostic = SystemDiagnostic()
    diagnostic.run_full_diagnosis()

if __name__ == "__main__":
    main()