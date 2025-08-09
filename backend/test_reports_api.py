#!/usr/bin/env python3
"""Test script to verify reports API endpoints are working"""
import requests
from datetime import datetime, timedelta
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_reports_api():
    """Test all report endpoints"""
    
    # Test report summary
    print("Testing /reports/summary...")
    try:
        response = requests.get(f"{BASE_URL}/reports/summary")
        if response.status_code == 200:
            print("✓ Summary endpoint working")
            print(f"  Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"✗ Summary endpoint failed: {response.status_code}")
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ Summary endpoint error: {e}")
    
    print("\n" + "-"*50 + "\n")
    
    # Test monthly revenue
    print("Testing /reports/revenue/monthly...")
    try:
        params = {
            "start_date": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
            "end_date": datetime.now().strftime("%Y-%m-%d")
        }
        response = requests.get(f"{BASE_URL}/reports/revenue/monthly", params=params)
        if response.status_code == 200:
            print("✓ Monthly revenue endpoint working")
            data = response.json()
            print(f"  Total revenue: ₩{data['summary']['total_revenue']:,.0f}")
            print(f"  Months with data: {len(data['data'])}")
        else:
            print(f"✗ Monthly revenue endpoint failed: {response.status_code}")
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ Monthly revenue endpoint error: {e}")
    
    print("\n" + "-"*50 + "\n")
    
    # Test customer acquisition
    print("Testing /reports/customers/acquisition...")
    try:
        params = {
            "start_date": (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d"),
            "end_date": datetime.now().strftime("%Y-%m-%d")
        }
        response = requests.get(f"{BASE_URL}/reports/customers/acquisition", params=params)
        if response.status_code == 200:
            print("✓ Customer acquisition endpoint working")
            data = response.json()
            print(f"  Total customers: {data['summary']['total_customers']}")
            print(f"  New customers in period: {data['summary']['new_customers_period']}")
        else:
            print(f"✗ Customer acquisition endpoint failed: {response.status_code}")
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ Customer acquisition endpoint error: {e}")
    
    print("\n" + "-"*50 + "\n")
    
    # Test service usage
    print("Testing /reports/services/usage...")
    try:
        params = {
            "start_date": (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),
            "end_date": datetime.now().strftime("%Y-%m-%d")
        }
        response = requests.get(f"{BASE_URL}/reports/services/usage", params=params)
        if response.status_code == 200:
            print("✓ Service usage endpoint working")
            data = response.json()
            print(f"  Total services: {data['total_services']}")
            print(f"  Service types: {len(data['summary'])}")
        else:
            print(f"✗ Service usage endpoint failed: {response.status_code}")
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ Service usage endpoint error: {e}")
    
    print("\n" + "-"*50 + "\n")
    
    # Test staff performance
    print("Testing /reports/staff/performance...")
    try:
        params = {
            "start_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            "end_date": datetime.now().strftime("%Y-%m-%d")
        }
        response = requests.get(f"{BASE_URL}/reports/staff/performance", params=params)
        if response.status_code == 200:
            print("✓ Staff performance endpoint working")
            data = response.json()
            print(f"  Staff members: {len(data['data'])}")
            print(f"  Period: {data['period']['start']} to {data['period']['end']}")
        else:
            print(f"✗ Staff performance endpoint failed: {response.status_code}")
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ Staff performance endpoint error: {e}")

if __name__ == "__main__":
    print("Testing Reports API Endpoints...")
    print("="*50)
    test_reports_api()
    print("\n" + "="*50)
    print("Test completed!")