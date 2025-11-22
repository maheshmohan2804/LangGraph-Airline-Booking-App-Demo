"""
Simple test script to verify Flask API is working
Run this while flask_app.py is running to test the API
"""

import requests
import json

API_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("Testing /api/health...")
    try:
        response = requests.get(f"{API_URL}/api/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}\n")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}\n")
        return False

def test_start_session():
    """Test start session endpoint"""
    print("Testing /api/start_session...")
    try:
        response = requests.post(
            f"{API_URL}/api/start_session",
            json={'session_id': 'test_session'}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}\n")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}\n")
        return False

def test_chat(message):
    """Test chat endpoint"""
    print(f"Testing /api/chat with message: '{message}'")
    try:
        response = requests.post(
            f"{API_URL}/api/chat",
            json={
                'session_id': 'test_session',
                'message': message
            },
            timeout=30
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}\n")
        if data.get('status') == 'success':
            print(f"Agent said: {data.get('response')}\n")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}\n")
        return False

def test_end_session():
    """Test end session endpoint"""
    print("Testing /api/end_session...")
    try:
        response = requests.post(
            f"{API_URL}/api/end_session",
            json={'session_id': 'test_session'}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}\n")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}\n")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Flask API Test Script")
    print("=" * 60)
    print("\nMake sure flask_app.py is running before running this test!\n")
    print("=" * 60)

    # Test health
    if not test_health():
        print("❌ Health check failed. Is flask_app.py running?")
        exit(1)

    print("✅ Health check passed\n")
    print("=" * 60)

    # Test session workflow
    if test_start_session():
        print("✅ Session started\n")
        print("=" * 60)

        # Test chat
        test_chat("CUST001")  # Send customer ID
        test_chat("Show me available flights")

        print("=" * 60)

        # End session
        if test_end_session():
            print("✅ Session ended\n")

    print("=" * 60)
    print("Test completed!")
    print("=" * 60)
