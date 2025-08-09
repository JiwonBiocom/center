#!/usr/bin/env python3
"""Test API endpoint directly"""
import requests
import subprocess
import json

# Get token
login_resp = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    data={"username": "admin@aibio.com", "password": "admin123"}
)
token = login_resp.json()["access_token"]

# Test campaign stats
resp = requests.get(
    "http://localhost:8000/api/v1/customer-leads/campaigns/stats",
    headers={"Authorization": f"Bearer {token}"}
)

print(f"Status Code: {resp.status_code}")
print(f"Response: {resp.text}")

# Also test campaigns list
resp2 = requests.get(
    "http://localhost:8000/api/v1/customer-leads/campaigns",
    headers={"Authorization": f"Bearer {token}"}
)

print(f"\nCampaigns List Status: {resp2.status_code}")
print(f"Campaigns List Response: {resp2.text}")