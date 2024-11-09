import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def get_auth_token():
    """Get JWT token for authentication"""
    url = f"{BASE_URL}/token/"
    credentials = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    response = requests.post(url, json=credentials)
    if response.status_code == 200:
        return response.json()['access']
    else:
        raise Exception("Failed to get auth token")

def test_endpoints():
    """Test all main API endpoints"""
    token = get_auth_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("\n🧪 Testing API Endpoints...")

    # Test Device Creation
    print("\n1. Testing Device Creation:")
    device_data = {
        "device_id": "TEST001",
        "manufacturer": "Test Manufacturer",
        "device_name": "Test Device",
        "expiration_date": datetime.utcnow().isoformat(),
        "sample_type": "Blood"
    }
    
    response = requests.post(f"{BASE_URL}/devices/", 
                           json=device_data, 
                           headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test Kit Creation
    print("\n2. Testing Kit Creation:")
    kit_data = {
        "kit_id": "KIT001",
        "device_id": "TEST001",
        "kit_name": "Test Kit"
    }
    
    response = requests.post(f"{BASE_URL}/kits/", 
                           json=kit_data, 
                           headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    # Test Shipment Creation
    print("\n3. Testing Shipment Creation:")
    shipment_data = {
        "tracking_number": "SHIP001",
        "kit_id": "KIT001",
        "status": "PENDING"
    }
    
    response = requests.post(f"{BASE_URL}/shipments/", 
                           json=shipment_data, 
                           headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    try:
        test_endpoints()
        print("\n✅ All tests completed!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}") 