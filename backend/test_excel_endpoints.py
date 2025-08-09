"""엑셀 가져오기/내보내기 엔드포인트 테스트"""
import requests
import os

BASE_URL = "http://localhost:8010"
TOKEN = os.getenv("SUPABASE_TOKEN", "")

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

def test_excel_export():
    """엑셀 내보내기 테스트"""
    print("엑셀 내보내기 테스트 중...")
    
    response = requests.get(
        f"{BASE_URL}/api/v1/customers/export/excel",
        headers=headers
    )
    
    if response.status_code == 200:
        print("✅ 엑셀 내보내기 성공")
        print(f"   파일 크기: {len(response.content):,} bytes")
        
        # 파일 저장
        with open("test_customers_export.xlsx", "wb") as f:
            f.write(response.content)
        print("   test_customers_export.xlsx 파일로 저장됨")
    else:
        print(f"❌ 엑셀 내보내기 실패: {response.status_code}")
        print(f"   오류: {response.text}")

def test_excel_import():
    """엑셀 가져오기 테스트"""
    print("\n엑셀 가져오기 테스트 중...")
    
    # 샘플 엑셀 파일 생성
    import pandas as pd
    
    sample_data = pd.DataFrame({
        '이름': ['테스트고객1', '테스트고객2', '테스트고객3'],
        '전화번호': ['010-1234-5678', '010-2345-6789', '010-3456-7890'],
        '이메일': ['test1@test.com', 'test2@test.com', 'test3@test.com'],
        '지역': ['서울', '경기', '인천'],
        '유입경로': ['인스타그램', '지인소개', '네이버검색']
    })
    
    sample_data.to_excel('test_import.xlsx', index=False)
    print("   샘플 파일 생성됨: test_import.xlsx")
    
    # 파일 업로드
    with open('test_import.xlsx', 'rb') as f:
        files = {'file': ('test_import.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        response = requests.post(
            f"{BASE_URL}/api/v1/customers/import/excel",
            headers=headers,
            files=files
        )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ 엑셀 가져오기 성공")
        print(f"   성공: {result['success_count']}건")
        print(f"   실패: {result['error_count']}건")
        if result.get('errors'):
            print("   오류:")
            for error in result['errors']:
                print(f"     - {error}")
    else:
        print(f"❌ 엑셀 가져오기 실패: {response.status_code}")
        print(f"   오류: {response.text}")
    
    # 임시 파일 삭제
    os.remove('test_import.xlsx')

if __name__ == "__main__":
    print("엑셀 기능 테스트 시작\n")
    
    # 토큰 확인
    if not TOKEN:
        print("⚠️  SUPABASE_TOKEN 환경 변수를 설정해주세요")
        print("   export SUPABASE_TOKEN='your-token-here'")
    else:
        test_excel_export()
        test_excel_import()
    
    print("\n테스트 완료")