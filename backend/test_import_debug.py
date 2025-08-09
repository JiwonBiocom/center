"""엑셀 가져오기 디버그"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from datetime import date
import requests

def test_import():
    # 테스트용 엑셀 파일 생성
    test_data = pd.DataFrame([
        {
            "이름": "가져오기테스트1",
            "연락처": "010-8888-8888",
            "나이": 30,
            "거주지역": "서울",
            "유입경로": "인스타그램",
            "DB작성 채널": "구글폼",
            "가격안내": "예",
            "DB입력일": date.today().strftime("%Y-%m-%d")
        }
    ])
    
    test_file = "test_import_debug.xlsx"
    test_data.to_excel(test_file, index=False)
    print(f"테스트 파일 생성: {test_file}")
    
    # 로그인
    login_response = requests.post("http://localhost:8000/api/v1/auth/login", data={
        "username": "admin@aibio.com",
        "password": "admin123"
    })
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 파일 업로드
        with open(test_file, "rb") as f:
            files = {"file": (test_file, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            
            try:
                response = requests.post(
                    "http://localhost:8000/api/v1/customer-leads/bulk-import",
                    files=files,
                    headers=headers,
                    timeout=30
                )
                
                print(f"\n응답 상태: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ 성공!")
                    print(f"   - 성공: {result['success_count']}건")
                    print(f"   - 실패: {result['error_count']}건")
                    if result.get('errors'):
                        print(f"   - 에러: {result['errors']}")
                else:
                    print(f"❌ 실패: {response.text[:500]}")
                    
            except Exception as e:
                print(f"❌ 요청 실패: {str(e)}")
                import traceback
                traceback.print_exc()
    else:
        print("로그인 실패")

if __name__ == "__main__":
    test_import()