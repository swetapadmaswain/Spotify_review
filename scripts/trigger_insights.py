"""Trigger insight generation via API"""
import requests

response = requests.post("http://localhost:8000/api/insights/generate", json={})
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
