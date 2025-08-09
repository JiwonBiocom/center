#!/usr/bin/env python3
"""
Railway 배포 상태 모니터링
"""
import requests
import time
import sys

API_URL = "https://center-production-1421.up.railway.app"

def check_health():
    """헬스 체크"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_payments_api():
    """Payments API 체크"""
    try:
        response = requests.get(f"{API_URL}/api/v1/payments/?limit=1", timeout=5)
        return response.status_code, response.text[:100]
    except Exception as e:
        return None, str(e)

def monitor_deployment(max_wait=300):
    """배포 모니터링 (최대 5분)"""
    print("🚀 Railway 배포 상태 모니터링")
    print("=" * 50)
    
    start_time = time.time()
    last_status = None
    
    while time.time() - start_time < max_wait:
        # 헬스 체크
        is_healthy = check_health()
        
        if is_healthy:
            # Payments API 체크
            status_code, response = check_payments_api()
            
            current_status = f"Health: ✅ | Payments API: {status_code}"
            
            if current_status != last_status:
                print(f"\n[{time.strftime('%H:%M:%S')}] {current_status}")
                
                if status_code == 200:
                    print("✅ 배포 완료! Payments API 정상 작동")
                    print(f"응답: {response}")
                    return True
                elif status_code == 500:
                    print("⚠️ 500 에러 발생")
                    print(f"응답: {response}")
                
                last_status = current_status
        else:
            if last_status != "unhealthy":
                print(f"\n[{time.strftime('%H:%M:%S')}] Health: ❌ (재배포 중...)")
                last_status = "unhealthy"
        
        time.sleep(5)
    
    print("\n⏱️ 타임아웃: 5분 내에 배포가 완료되지 않았습니다.")
    return False

if __name__ == "__main__":
    success = monitor_deployment()
    sys.exit(0 if success else 1)