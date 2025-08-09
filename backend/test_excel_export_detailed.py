"""엑셀 내보내기 상세 디버그"""
import requests
import traceback
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import SessionLocal
from models.customer_extended import MarketingLead
import pandas as pd
from io import BytesIO
from datetime import date

def test_direct_export():
    """직접 DB에서 엑셀 생성 테스트"""
    print("=== 1. 직접 엑셀 생성 테스트 ===")
    db = SessionLocal()
    try:
        leads = db.query(MarketingLead).limit(3).all()
        data = []
        
        for lead in leads:
            data.append({
                '이름': lead.name,
                '연락처': lead.phone,
                '나이': lead.age,
                '거주지역': lead.region,
                '유입경로': lead.lead_channel,
                'DB작성 채널': lead.db_channel,
                '매출': float(lead.revenue) if lead.revenue else None
            })
        
        df = pd.DataFrame(data)
        
        # Excel 저장
        output = BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)
        
        print(f"✅ 직접 생성 성공: {len(output.getvalue())} bytes")
        
        # 파일로 저장해서 확인
        with open("test_direct.xlsx", "wb") as f:
            f.write(output.getvalue())
        print("✅ test_direct.xlsx 파일 생성")
        
    except Exception as e:
        print(f"❌ 직접 생성 실패: {str(e)}")
        traceback.print_exc()
    finally:
        db.close()

def test_api_with_curl():
    """curl 명령으로 API 테스트"""
    print("\n=== 2. CURL로 API 테스트 ===")
    
    # 로그인
    login_cmd = """curl -X POST http://localhost:8000/api/v1/auth/login \
        -H 'Content-Type: application/x-www-form-urlencoded' \
        -d 'username=admin@aibio.com&password=admin123' 2>/dev/null"""
    
    import subprocess
    import json
    
    result = subprocess.run(login_cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        try:
            token = json.loads(result.stdout)['access_token']
            print("✅ 로그인 성공")
            
            # Export 테스트
            export_cmd = f"""curl -X GET 'http://localhost:8000/api/v1/customer-leads/export?format=excel' \
                -H 'Authorization: Bearer {token}' \
                -o test_api.xlsx -w '%{{http_code}}' 2>/dev/null"""
            
            result = subprocess.run(export_cmd, shell=True, capture_output=True, text=True)
            status_code = result.stdout
            
            print(f"Export API 응답: {status_code}")
            
            if status_code == "200":
                print("✅ 파일 다운로드 성공")
                # 파일 크기 확인
                if os.path.exists("test_api.xlsx"):
                    print(f"   파일 크기: {os.path.getsize('test_api.xlsx')} bytes")
            else:
                print(f"❌ API 실패: HTTP {status_code}")
                
        except Exception as e:
            print(f"❌ 파싱 실패: {str(e)}")
    else:
        print("❌ 로그인 실패")

def test_api_endpoint():
    """Python requests로 상세 테스트"""
    print("\n=== 3. Python Requests 상세 테스트 ===")
    
    # 로그인
    login_response = requests.post("http://localhost:8000/api/v1/auth/login", data={
        "username": "admin@aibio.com",
        "password": "admin123"
    })
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Export 요청
        try:
            response = requests.get(
                "http://localhost:8000/api/v1/customer-leads/export",
                params={"format": "excel"},
                headers=headers,
                timeout=30
            )
            
            print(f"응답 상태: {response.status_code}")
            print(f"응답 헤더: {dict(response.headers)}")
            
            if response.status_code == 200:
                print(f"✅ 성공! 파일 크기: {len(response.content)} bytes")
                
                # 파일 저장
                with open("test_requests.xlsx", "wb") as f:
                    f.write(response.content)
                print("✅ test_requests.xlsx 파일 생성")
                
                # 파일 검증
                try:
                    df = pd.read_excel("test_requests.xlsx")
                    print(f"✅ 파일 검증 성공: {len(df)}행, {len(df.columns)}열")
                except Exception as e:
                    print(f"❌ 파일 검증 실패: {str(e)}")
            else:
                print(f"❌ 실패: {response.text[:500]}")
                
        except requests.Timeout:
            print("❌ 요청 타임아웃")
        except Exception as e:
            print(f"❌ 요청 실패: {str(e)}")
            traceback.print_exc()

def test_api_code():
    """API 코드 직접 호출 테스트"""
    print("\n=== 4. API 코드 직접 호출 테스트 ===")
    
    from api.v1.customer_leads import export_leads
    from core.database import get_db
    from models.user import User
    
    db = SessionLocal()
    try:
        # 가짜 현재 사용자
        current_user = db.query(User).filter(User.email == "admin@aibio.com").first()
        
        if current_user:
            # 직접 함수 호출
            result = export_leads(
                format="excel",
                db=db,
                current_user=current_user
            )
            
            print(f"✅ 함수 호출 성공: {type(result)}")
            
            # StreamingResponse인 경우 내용 읽기
            if hasattr(result, 'body_iterator'):
                content = b''.join(result.body_iterator)
                print(f"   콘텐츠 크기: {len(content)} bytes")
                
                with open("test_direct_call.xlsx", "wb") as f:
                    f.write(content)
                print("✅ test_direct_call.xlsx 파일 생성")
        else:
            print("❌ 사용자를 찾을 수 없음")
            
    except Exception as e:
        print(f"❌ 직접 호출 실패: {str(e)}")
        traceback.print_exc()
    finally:
        db.close()

def check_dependencies():
    """의존성 확인"""
    print("\n=== 5. 의존성 확인 ===")
    
    try:
        import pandas
        print(f"✅ pandas: {pandas.__version__}")
    except:
        print("❌ pandas 없음")
    
    try:
        import openpyxl
        print(f"✅ openpyxl: {openpyxl.__version__}")
    except:
        print("❌ openpyxl 없음")
    
    try:
        from io import BytesIO
        print("✅ BytesIO 사용 가능")
    except:
        print("❌ BytesIO 사용 불가")
    
    try:
        from fastapi.responses import StreamingResponse
        print("✅ StreamingResponse 사용 가능")
    except:
        print("❌ StreamingResponse 사용 불가")

if __name__ == "__main__":
    print("엑셀 내보내기 기능 상세 분석")
    print("="*60)
    
    check_dependencies()
    test_direct_export()
    test_api_code()
    test_api_with_curl()
    test_api_endpoint()
    
    print("\n분석 완료!")