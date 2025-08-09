"""
Week 2 고급 기능 테스트
"""
import requests
import json
from datetime import date, datetime, timedelta
import pandas as pd
from io import BytesIO

BASE_URL = "http://localhost:8000/api/v1"

class TestWeek2Features:
    def __init__(self):
        self.headers = None
        self.test_lead_ids = []
    
    def login(self):
        """로그인 및 토큰 획득"""
        response = requests.post(f"{BASE_URL}/auth/login", data={
            "username": "admin@aibio.com",
            "password": "admin123"
        })
        if response.status_code == 200:
            token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {token}"}
            print("✅ 로그인 성공")
            return True
        print(f"❌ 로그인 실패: {response.text}")
        return False
    
    def test_advanced_filtering(self):
        """고급 필터링 테스트"""
        print("\n=== 1. 고급 필터링 API 테스트 ===")
        
        # 1-1. 날짜 범위 필터
        print("\n1-1. 날짜 범위 필터 테스트")
        params = {
            "db_entry_date_from": "2025-01-01",
            "db_entry_date_to": "2025-05-31",
            "page_size": 5
        }
        response = requests.get(f"{BASE_URL}/customer-leads/", params=params, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 2025년 1-5월 데이터: {data['total']}건")
        else:
            print(f"❌ 실패: {response.status_code}")
        
        # 1-2. 상태 필터
        print("\n1-2. 상태 필터 테스트")
        params = {
            "status": ["new", "phone_consulted"],
            "page_size": 5
        }
        response = requests.get(f"{BASE_URL}/customer-leads/", params=params, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ new/phone_consulted 상태: {data['total']}건")
        else:
            print(f"❌ 실패: {response.status_code}")
        
        # 1-3. 복합 필터
        print("\n1-3. 복합 필터 테스트")
        params = {
            "lead_channel": ["인스타그램", "네이버"],
            "region": ["서울", "경기"],
            "has_phone_consult": True,
            "is_registered": False,
            "page_size": 5
        }
        response = requests.get(f"{BASE_URL}/customer-leads/", params=params, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 복합 필터 결과: {data['total']}건")
        else:
            print(f"❌ 실패: {response.status_code}")
        
        # 1-4. 검색 기능
        print("\n1-4. 검색 기능 테스트")
        params = {
            "search": "김",
            "page_size": 5
        }
        response = requests.get(f"{BASE_URL}/customer-leads/", params=params, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ '김' 검색 결과: {data['total']}건")
        else:
            print(f"❌ 실패: {response.status_code}")
        
        # 1-5. 정렬 테스트
        print("\n1-5. 정렬 테스트")
        params = {
            "sort_by": "lead_date",
            "sort_order": "desc",
            "page_size": 3
        }
        response = requests.get(f"{BASE_URL}/customer-leads/", params=params, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            if data['items']:
                print(f"✅ 최신순 정렬 (상위 3개):")
                for item in data['items']:
                    print(f"   - {item['name']}: {item['lead_date']}")
        else:
            print(f"❌ 실패: {response.status_code}")
    
    def test_statistics_api(self):
        """통계 API 테스트"""
        print("\n\n=== 2. 통계 API 테스트 ===")
        
        # 2-1. 전체 통계
        print("\n2-1. 전체 통계")
        response = requests.get(f"{BASE_URL}/customer-leads/stats", headers=self.headers)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ 전체 통계:")
            print(f"   - 총 유입고객: {stats['total_count']}명")
            print(f"   - 전환 고객: {stats['converted_count']}명")
            print(f"   - 전환율: {stats['conversion_rate']}%")
            
            # 채널별 통계
            if stats.get('channel_stats'):
                print("\n   채널별 통계:")
                for ch in stats['channel_stats'][:3]:  # 상위 3개만
                    print(f"   - {ch['channel']}: {ch['count']}명 (전환율 {ch['conversion_rate']}%)")
            
            # 상태별 통계
            if stats.get('status_stats'):
                print("\n   상태별 통계:")
                for st in stats['status_stats']:
                    print(f"   - {st['status']}: {st['count']}명")
        else:
            print(f"❌ 실패: {response.status_code}")
        
        # 2-2. 기간별 통계
        print("\n2-2. 특정 기간 통계")
        params = {
            "db_entry_date_from": "2025-05-01",
            "db_entry_date_to": "2025-05-31"
        }
        response = requests.get(f"{BASE_URL}/customer-leads/stats", params=params, headers=self.headers)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ 2025년 5월 통계:")
            print(f"   - 유입고객: {stats['total_count']}명")
            print(f"   - 전환율: {stats['conversion_rate']}%")
        else:
            print(f"❌ 실패: {response.status_code}")
    
    def test_consultation_workflow(self):
        """상담 워크플로우 테스트"""
        print("\n\n=== 3. 상담 워크플로우 API 테스트 ===")
        
        # 테스트용 고객 생성
        print("\n3-1. 테스트용 고객 생성")
        test_lead = {
            "name": "워크플로우 테스트",
            "phone": f"010-9999-{datetime.now().strftime('%H%M')}",
            "lead_date": str(date.today()),
            "age": 35,
            "region": "서울",
            "lead_channel": "인스타그램"
        }
        response = requests.post(f"{BASE_URL}/customer-leads/", json=test_lead, headers=self.headers)
        if response.status_code == 200:
            lead_id = response.json()["lead_id"]
            self.test_lead_ids.append(lead_id)
            print(f"✅ 테스트 고객 생성: ID {lead_id}")
            
            # 3-2. 전화 상담 추가
            print("\n3-2. 전화 상담 이력 추가")
            consultation1 = {
                "lead_id": lead_id,
                "consultation_type": "phone",
                "consultation_date": datetime.now().isoformat(),
                "result": "관심있음",
                "notes": "가격 문의, 패키지 설명 완료",
                "next_action": "방문 상담 예약"
            }
            response = requests.post(
                f"{BASE_URL}/customer-leads/{lead_id}/consultations", 
                json=consultation1, 
                headers=self.headers
            )
            if response.status_code == 200:
                print("✅ 전화 상담 이력 추가 완료")
            else:
                print(f"❌ 실패: {response.text}")
            
            # 3-3. 방문 상담 추가
            print("\n3-3. 방문 상담 이력 추가")
            consultation2 = {
                "lead_id": lead_id,
                "consultation_type": "visit",
                "consultation_date": (datetime.now() + timedelta(days=3)).isoformat(),
                "result": "등록 결정",
                "notes": "올케어 80 패키지 결정",
                "next_action": "계약서 작성"
            }
            response = requests.post(
                f"{BASE_URL}/customer-leads/{lead_id}/consultations", 
                json=consultation2, 
                headers=self.headers
            )
            if response.status_code == 200:
                print("✅ 방문 상담 이력 추가 완료")
            else:
                print(f"❌ 실패: {response.text}")
            
            # 3-4. 상담 이력 조회
            print("\n3-4. 상담 이력 조회")
            response = requests.get(
                f"{BASE_URL}/customer-leads/{lead_id}/consultations", 
                headers=self.headers
            )
            if response.status_code == 200:
                consultations = response.json()
                print(f"✅ 상담 이력 {len(consultations)}건:")
                for c in consultations:
                    print(f"   - {c['consultation_type']}: {c['result']} ({c['consultation_date'][:10]})")
            else:
                print(f"❌ 실패: {response.status_code}")
            
            # 3-5. 고객 상태 확인
            print("\n3-5. 고객 상태 변경 확인")
            response = requests.get(f"{BASE_URL}/customer-leads/{lead_id}", headers=self.headers)
            if response.status_code == 200:
                lead_data = response.json()
                print(f"✅ 상태: {lead_data['status']}")
                print(f"   전화상담일: {lead_data.get('phone_consult_date')}")
                print(f"   방문상담일: {lead_data.get('visit_consult_date')}")
            else:
                print(f"❌ 실패: {response.status_code}")
        else:
            print(f"❌ 테스트 고객 생성 실패: {response.text}")
    
    def test_bulk_operations(self):
        """일괄 작업 테스트"""
        print("\n\n=== 4. 일괄 작업 테스트 ===")
        
        # 4-1. 담당자 일괄 지정
        print("\n4-1. 담당자 일괄 지정")
        if len(self.test_lead_ids) >= 1:
            assign_data = {
                "lead_ids": self.test_lead_ids,
                "staff_id": 1  # admin user
            }
            response = requests.post(
                f"{BASE_URL}/customer-leads/assign-staff", 
                json=assign_data, 
                headers=self.headers
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {result['message']}")
            else:
                print(f"❌ 실패: {response.text}")
        
        # 4-2. 재등록 대상 조회
        print("\n4-2. 재등록 대상 조회")
        response = requests.get(
            f"{BASE_URL}/customer-leads/reregistration-targets",
            params={"page_size": 5},
            headers=self.headers
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 재등록 대상: {data['total']}명")
            if data['items']:
                print("   상위 5명:")
                for item in data['items'][:5]:
                    print(f"   - {item['name']} (마지막 이용: {item.get('last_service_date', '없음')})")
        else:
            print(f"❌ 실패: {response.status_code}")
    
    def test_excel_operations(self):
        """엑셀 연동 테스트"""
        print("\n\n=== 5. 엑셀 연동 테스트 ===")
        
        # 5-1. 엑셀 내보내기
        print("\n5-1. 엑셀 내보내기")
        response = requests.get(
            f"{BASE_URL}/customer-leads/export?format=excel",
            headers=self.headers
        )
        if response.status_code == 200:
            # 파일 저장
            filename = f"test_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"✅ 엑셀 파일 생성: {filename}")
            
            # 파일 내용 확인
            df = pd.read_excel(filename)
            print(f"   - 총 {len(df)}행")
            print(f"   - 컬럼: {', '.join(df.columns[:5])}...")
        else:
            print(f"❌ 실패: {response.status_code}")
        
        # 5-2. CSV 내보내기
        print("\n5-2. CSV 내보내기")
        response = requests.get(
            f"{BASE_URL}/customer-leads/export?format=csv",
            headers=self.headers
        )
        if response.status_code == 200:
            filename = f"test_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"✅ CSV 파일 생성: {filename}")
        else:
            print(f"❌ 실패: {response.status_code}")
        
        # 5-3. 엑셀 가져오기 (테스트 파일 생성)
        print("\n5-3. 엑셀 가져오기 테스트")
        # 테스트용 엑셀 파일 생성
        test_data = pd.DataFrame([
            {
                "이름": "엑셀테스트1",
                "연락처": "010-1111-1111",
                "나이": 30,
                "거주지역": "서울",
                "유입경로": "인스타그램",
                "DB작성 채널": "구글폼",
                "가격안내": "예",
                "DB입력일": date.today().strftime("%Y-%m-%d")
            },
            {
                "이름": "엑셀테스트2",
                "연락처": "010-2222-2222",
                "나이": 35,
                "거주지역": "경기",
                "유입경로": "네이버",
                "DB작성 채널": "전화",
                "가격안내": "아니오",
                "DB입력일": date.today().strftime("%Y-%m-%d")
            }
        ])
        
        import_filename = "test_import.xlsx"
        test_data.to_excel(import_filename, index=False)
        
        # 파일 업로드
        with open(import_filename, "rb") as f:
            files = {"file": (import_filename, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            response = requests.post(
                f"{BASE_URL}/customer-leads/bulk-import",
                files=files,
                headers=self.headers
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 엑셀 가져오기 완료:")
            print(f"   - 성공: {result['success_count']}건")
            print(f"   - 실패: {result['error_count']}건")
            if result.get('errors'):
                print(f"   - 에러: {result['errors'][:3]}")
        else:
            print(f"❌ 실패: {response.text}")
    
    def cleanup(self):
        """테스트 데이터 정리"""
        print("\n\n=== 테스트 데이터 정리 ===")
        for lead_id in self.test_lead_ids:
            response = requests.delete(
                f"{BASE_URL}/customer-leads/{lead_id}",
                headers=self.headers
            )
            if response.status_code == 200:
                print(f"✅ 테스트 데이터 삭제: ID {lead_id}")
            else:
                print(f"❌ 삭제 실패: ID {lead_id}")
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("="*60)
        print("Week 2 고급 기능 종합 테스트")
        print("="*60)
        
        if not self.login():
            return
        
        try:
            self.test_advanced_filtering()
            self.test_statistics_api()
            self.test_consultation_workflow()
            self.test_bulk_operations()
            self.test_excel_operations()
        finally:
            self.cleanup()
        
        print("\n\n✅ Week 2 테스트 완료!")


if __name__ == "__main__":
    tester = TestWeek2Features()
    tester.run_all_tests()