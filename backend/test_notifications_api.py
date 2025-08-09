"""알림 API 테스트 스크립트"""
import httpx
import asyncio

# 테스트용 토큰 (실제 사용 시 유효한 토큰으로 교체 필요)
TEST_TOKEN = "test-token"

async def test_notifications_api():
    """알림 API 테스트"""
    base_url = "http://localhost:8000/api/v1"
    headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        # 1. 알림 목록 조회 테스트
        print("1. 알림 목록 조회 테스트")
        try:
            response = await client.get(f"{base_url}/notifications/", headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 알림 목록 조회 성공")
                print(f"전체 알림 수: {data.get('total', 0)}")
                print(f"조회된 알림 수: {len(data.get('items', []))}")
            else:
                print(f"❌ 에러: {response.text}")
        except Exception as e:
            print(f"❌ 요청 실패: {e}")
        
        print("\n" + "="*50 + "\n")
        
        # 2. 읽지 않은 알림 개수 조회 테스트
        print("2. 읽지 않은 알림 개수 조회 테스트")
        try:
            response = await client.get(f"{base_url}/notifications/unread-count", headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 읽지 않은 알림 개수: {data.get('count', 0)}")
            else:
                print(f"❌ 에러: {response.text}")
        except Exception as e:
            print(f"❌ 요청 실패: {e}")

if __name__ == "__main__":
    print("알림 API 테스트 시작\n")
    asyncio.run(test_notifications_api())
    print("\n테스트 완료!")