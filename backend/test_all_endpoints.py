#!/usr/bin/env python3
"""Test all API endpoints for data connectivity"""

import requests
import json
from typing import Dict, Any
from datetime import datetime

# Read the token
with open('/Users/vibetj/.test_token', 'r') as f:
    token = f.read().strip()

# Base URL
BASE_URL = "http://localhost:8000"

# Headers with authentication
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Endpoints to test
endpoints = [
    {
        "name": "고객 관리 (Customers)",
        "url": "/api/v1/customers",
        "method": "GET"
    },
    {
        "name": "서비스 (Services)",
        "url": "/api/v1/services",
        "method": "GET"
    },
    {
        "name": "결제 (Payments)",
        "url": "/api/v1/payments",
        "method": "GET"
    },
    {
        "name": "패키지 (Packages)",
        "url": "/api/v1/packages",
        "method": "GET"
    },
    {
        "name": "리드 (Leads)",
        "url": "/api/v1/leads",
        "method": "GET"
    },
    {
        "name": "검사키트 (Kits)",
        "url": "/api/v1/kits",
        "method": "GET"
    },
    {
        "name": "리포트 (Reports)",
        "url": "/api/v1/reports/summary",
        "method": "GET"
    },
    {
        "name": "대시보드 (Dashboard)",
        "url": "/api/v1/dashboard/stats",
        "method": "GET"
    }
]

def test_endpoint(endpoint: Dict[str, str]) -> Dict[str, Any]:
    """Test a single endpoint"""
    url = BASE_URL + endpoint["url"]
    
    try:
        if endpoint["method"] == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        
        result = {
            "name": endpoint["name"],
            "url": endpoint["url"],
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "error": None,
            "data_count": None,
            "sample_data": None
        }
        
        if response.status_code == 200:
            data = response.json()
            
            # Handle different response formats
            if isinstance(data, list):
                result["data_count"] = len(data)
                result["sample_data"] = data[:2] if data else "No data"
            elif isinstance(data, dict):
                # For paginated responses
                if "items" in data:
                    result["data_count"] = len(data["items"])
                    result["sample_data"] = data["items"][:2] if data["items"] else "No data"
                # For summary/stats responses
                else:
                    result["data_count"] = "N/A (summary data)"
                    result["sample_data"] = data
            else:
                result["sample_data"] = data
        else:
            result["error"] = response.text
            
    except requests.exceptions.ConnectionError:
        result = {
            "name": endpoint["name"],
            "url": endpoint["url"],
            "status_code": None,
            "success": False,
            "error": "Connection failed - server may not be running",
            "data_count": None,
            "sample_data": None
        }
    except requests.exceptions.Timeout:
        result = {
            "name": endpoint["name"],
            "url": endpoint["url"],
            "status_code": None,
            "success": False,
            "error": "Request timed out",
            "data_count": None,
            "sample_data": None
        }
    except Exception as e:
        result = {
            "name": endpoint["name"],
            "url": endpoint["url"],
            "status_code": None,
            "success": False,
            "error": str(e),
            "data_count": None,
            "sample_data": None
        }
    
    return result

def main():
    print("=" * 80)
    print(f"API Endpoint Connectivity Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print(f"Base URL: {BASE_URL}")
    print(f"Token: {token[:20]}...{token[-10:]}")
    print("-" * 80)
    
    all_results = []
    
    for endpoint in endpoints:
        print(f"\nTesting: {endpoint['name']} ({endpoint['url']})...")
        result = test_endpoint(endpoint)
        all_results.append(result)
        
        if result["success"]:
            print(f"✅ SUCCESS - Status: {result['status_code']}")
            print(f"   Data count: {result['data_count']}")
            if result["sample_data"] != "No data" and result["sample_data"] != "N/A (summary data)":
                print(f"   Sample data available: Yes")
        else:
            print(f"❌ FAILED - Status: {result['status_code']}")
            print(f"   Error: {result['error']}")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    successful = sum(1 for r in all_results if r["success"])
    failed = len(all_results) - successful
    
    print(f"Total endpoints tested: {len(all_results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        print("\nFailed endpoints:")
        for result in all_results:
            if not result["success"]:
                print(f"  - {result['name']}: {result['error']}")
    
    # Detailed results
    print("\n" + "-" * 80)
    print("DETAILED RESULTS")
    print("-" * 80)
    
    for result in all_results:
        print(f"\n{result['name']} ({result['url']}):")
        print(f"  Status: {'✅ Success' if result['success'] else '❌ Failed'}")
        print(f"  HTTP Status Code: {result['status_code']}")
        
        if result["success"]:
            print(f"  Data Count: {result['data_count']}")
            if isinstance(result["sample_data"], dict):
                print(f"  Response Type: Summary/Stats")
                # Print first few keys for summary data
                keys = list(result["sample_data"].keys())[:5]
                print(f"  Available Fields: {', '.join(keys)}{'...' if len(result['sample_data'].keys()) > 5 else ''}")
            elif isinstance(result["sample_data"], list) and result["sample_data"]:
                print(f"  Response Type: List")
                print(f"  First item keys: {', '.join(result['sample_data'][0].keys()) if result['sample_data'] else 'N/A'}")
            elif result["sample_data"] == "No data":
                print(f"  Response Type: Empty list")
        else:
            print(f"  Error: {result['error']}")

if __name__ == "__main__":
    main()