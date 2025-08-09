#!/usr/bin/env python3
"""
API를 통해 로컬 결제 데이터를 Railway/Supabase로 업로드
실행: python scripts/upload_payments_via_api.py
"""
import csv
import requests
import json
from datetime import datetime
from pathlib import Path
import time

# API 설정
API_BASE_URL = "https://center-production-1421.up.railway.app"
ADMIN_EMAIL = "admin@aibio.kr"
ADMIN_PASSWORD = "admin123"

def get_auth_token():
    """관리자 로그인하여 토큰 획득"""
    login_url = f"{API_BASE_URL}/api/v1/auth/login"
    
    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(login_url, json=login_data, headers=headers)
    
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get("access_token")
    else:
        print(f"❌ 로그인 실패: {response.status_code}")
        print(response.text)
        return None

def convert_payment_method(method):
    """결제 방법 한글 -> 영문 변환"""
    method_map = {
        "카드": "card",
        "이체": "transfer", 
        "현금": "cash"
    }
    return method_map.get(method, method.lower())

def upload_payments():
    """API를 통해 결제 데이터 업로드"""
    
    print("🚀 API를 통한 결제 데이터 업로드 시작")
    print("=" * 50)
    
    # CSV 파일 경로
    csv_path = Path("backend/seed/local_payments_export.csv")
    
    if not csv_path.exists():
        print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_path}")
        return False
    
    # 인증 토큰 획득
    print("\n🔐 관리자 로그인 중...")
    token = get_auth_token()
    
    if not token:
        print("❌ 인증 실패")
        return False
    
    print("✅ 로그인 성공!")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 현재 결제 데이터 확인
    print("\n📊 현재 결제 데이터 확인 중...")
    response = requests.get(f"{API_BASE_URL}/api/v1/payments/", headers=headers)
    
    if response.status_code == 200:
        current_payments = response.json()
        print(f"현재 결제 건수: {len(current_payments)}건")
        
        # 기존 데이터를 (customer_id, payment_date, amount) 튜플로 저장
        existing = set()
        for p in current_payments:
            existing.add((p['customer_id'], p['payment_date'], float(p['amount'])))
    else:
        print(f"⚠️ 현재 데이터 확인 실패: {response.status_code}")
        existing = set()
    
    # CSV 데이터 읽기
    payments_to_upload = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 중복 확인
            check_tuple = (
                int(row['customer_id']), 
                row['payment_date'], 
                float(row['amount'])
            )
            
            if check_tuple not in existing:
                payment_data = {
                    "customer_id": int(row['customer_id']),
                    "payment_date": row['payment_date'],
                    "amount": float(row['amount']),
                    "payment_method": convert_payment_method(row['payment_method'])
                }
                payments_to_upload.append(payment_data)
    
    print(f"\n📥 업로드할 신규 결제 데이터: {len(payments_to_upload)}건")
    
    if len(payments_to_upload) == 0:
        print("ℹ️ 추가할 새로운 데이터가 없습니다.")
        return True
    
    # 결제 데이터 업로드
    print("\n📤 결제 데이터 업로드 중...")
    success_count = 0
    fail_count = 0
    
    # 배치 처리 (10개씩)
    batch_size = 10
    for i in range(0, len(payments_to_upload), batch_size):
        batch = payments_to_upload[i:i+batch_size]
        
        for payment in batch:
            try:
                response = requests.post(
                    f"{API_BASE_URL}/api/v1/payments/",
                    headers=headers,
                    json=payment
                )
                
                if response.status_code in [200, 201]:
                    success_count += 1
                else:
                    fail_count += 1
                    print(f"  ❌ 실패: {payment['payment_date']} - {response.status_code}")
                    
            except Exception as e:
                fail_count += 1
                print(f"  ❌ 오류: {e}")
        
        # 진행 상황 표시
        progress = ((i + len(batch)) / len(payments_to_upload)) * 100
        print(f"  진행률: {progress:.1f}% ({success_count}건 성공, {fail_count}건 실패)")
        
        # API 부하 방지를 위한 대기
        time.sleep(0.5)
    
    print(f"\n✅ 업로드 완료!")
    print(f"  - 성공: {success_count}건")
    print(f"  - 실패: {fail_count}건")
    
    # 최종 결제 데이터 확인
    print("\n📊 최종 결제 데이터 확인 중...")
    response = requests.get(f"{API_BASE_URL}/api/v1/payments/stats", headers=headers)
    
    if response.status_code == 200:
        stats = response.json()
        print("\n📈 최종 통계:")
        print(f"  - 총 결제 건수: {stats.get('total_count', 0):,}건")
        print(f"  - 총 매출액: ₩{stats.get('total_revenue', 0):,.0f}")
    
    return True

def main():
    """메인 실행 함수"""
    success = upload_payments()
    
    if success:
        print("\n🎉 작업 완료!")
        print("💡 확인 방법:")
        print("   - API: https://center-production-1421.up.railway.app/api/v1/payments/")
        print("   - UI: https://center-ten.vercel.app/payments")

if __name__ == "__main__":
    main()