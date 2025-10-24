#!/usr/bin/env python3
"""
Test script for CrewAI AMP API endpoints
"""

import requests
import json

# Replace with your actual AMP deployment URL
BASE_URL = "https://api.amp.crewai.com/crews/YOUR_CREW_ID"
API_KEY = "YOUR_API_KEY"

def test_detect_endpoint():
    """Test disease detection endpoint"""
    url = f"{BASE_URL}/detect"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "num_images": 3,
        "detection_threshold": 0.25,
        "preferred_language": "en"
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"Detection API: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_chatbot_endpoint():
    """Test chatbot endpoint"""
    url = f"{BASE_URL}/chatbot"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "question": "How do I treat apple scab?",
        "language": "en"
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"Chatbot API: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_trends_endpoint():
    """Test trends endpoint"""
    url = f"{BASE_URL}/trends?days=30"
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    
    response = requests.get(url, headers=headers)
    print(f"Trends API: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    print("Testing CrewAI AMP API Endpoints...")
    print("=" * 50)
    
    test_detect_endpoint()
    print("\n" + "=" * 50)
    
    test_chatbot_endpoint()
    print("\n" + "=" * 50)
    
    test_trends_endpoint()
