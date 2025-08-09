import requests
import json
from datetime import datetime, date

# Base URL for the API
BASE_URL = "http://localhost:8000"

# Test user credentials
USERNAME = "admin"
PASSWORD = "admin123"

def get_token():
    """Login and get access token"""
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        data={"username": USERNAME, "password": PASSWORD}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_consultation_history():
    """Test consultation history CRUD operations"""
    token = get_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("=== Testing Consultation History API ===\n")
    
    # 1. Get first lead ID
    print("1. Getting first lead ID...")
    response = requests.get(f"{BASE_URL}/api/v1/customer-leads/", headers=headers)
    if response.status_code == 200:
        leads = response.json()["items"]
        if leads:
            lead_id = leads[0]["lead_id"]
            print(f"   Using lead ID: {lead_id}")
        else:
            print("   No leads found!")
            return
    else:
        print(f"   Failed to get leads: {response.status_code}")
        return
    
    # 2. Add consultation history
    print("\n2. Adding consultation history...")
    consultation_data = {
        "lead_id": lead_id,
        "consultation_type": "phone",
        "consultation_date": datetime.now().isoformat(),
        "consulted_by": "테스트 상담원",
        "consultation_content": "초기 전화 상담 진행. 서비스에 대한 관심도가 높음.",
        "next_action": "방문 상담 예약",
        "next_action_date": date.today().isoformat(),
        "result": "긍정적"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/customer-leads/{lead_id}/consultations",
        headers=headers,
        json=consultation_data
    )
    
    if response.status_code == 200:
        consultation = response.json()
        consultation_id = consultation["consultation_id"]
        print(f"   Consultation added successfully! ID: {consultation_id}")
    else:
        print(f"   Failed to add consultation: {response.status_code} - {response.text}")
        return
    
    # 3. Get consultation history
    print("\n3. Getting consultation history...")
    response = requests.get(
        f"{BASE_URL}/api/v1/customer-leads/{lead_id}/consultations",
        headers=headers
    )
    
    if response.status_code == 200:
        consultations = response.json()
        print(f"   Found {len(consultations)} consultations")
        for c in consultations:
            print(f"   - {c['consultation_type']} on {c['consultation_date'][:10]}: {c['consultation_content'][:50]}...")
    else:
        print(f"   Failed to get consultations: {response.status_code}")
    
    # 4. Update consultation
    print("\n4. Updating consultation...")
    update_data = {
        "consultation_content": "전화 상담 완료. 방문 상담 일정 확정.",
        "result": "방문 예약 완료"
    }
    
    response = requests.put(
        f"{BASE_URL}/api/v1/customer-leads/{lead_id}/consultations/{consultation_id}",
        headers=headers,
        json=update_data
    )
    
    if response.status_code == 200:
        print("   Consultation updated successfully!")
    else:
        print(f"   Failed to update consultation: {response.status_code} - {response.text}")
    
    # 5. Delete consultation
    print("\n5. Deleting consultation...")
    response = requests.delete(
        f"{BASE_URL}/api/v1/customer-leads/{lead_id}/consultations/{consultation_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        print("   Consultation deleted successfully!")
    else:
        print(f"   Failed to delete consultation: {response.status_code}")
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    test_consultation_history()