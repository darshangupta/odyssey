import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi
import uuid

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:8000/api"
MONGODB_URI = os.getenv('MONGODB_URI')

def test_mongodb_connection():
    """Test MongoDB connection"""
    print("\n📡 Testing MongoDB Connection...")
    try:
        client = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
        client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {str(e)}")
        return False

def get_auth_token():
    """Get JWT token for authentication"""
    print("\n🔑 Getting authentication token...")
    url = f"{BASE_URL}/token/"
    credentials = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(url, json=credentials)
        response.raise_for_status()  # Raise exception for bad status codes
        token = response.json()['access']
        print("✅ Token obtained successfully!")
        print(f"Token: {token[:20]}...") # Print first 20 chars of token for debugging
        return token
    except Exception as e:
        print(f"❌ Failed to get token: {str(e)}")
        if hasattr(response, 'text'):
            print(f"Response: {response.text}")
        raise

def make_request(method, endpoint, data=None, token=None):
    """Make an authenticated request"""
    headers = {
        "Content-Type": "application/json"
    }
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    url = f"{BASE_URL}{endpoint}"
    print(f"Making {method} request to: {url}")
    print(f"Request data: {json.dumps(data, indent=2)}")
    
    response = requests.request(
        method=method,
        url=url,
        json=data,
        headers=headers
    )
    return response

def generate_unique_id(prefix):
    """Generate a unique ID with given prefix"""
    return f"{prefix}{uuid.uuid4().hex[:8]}"

def test_api_endpoints():
    """Test all main API endpoints"""
    token = get_auth_token()
    
    print("\n🧪 Testing API Endpoints...")

    # Generate unique IDs for this test run
    trial_id = generate_unique_id("TRIAL")
    site_id = generate_unique_id("SITE")
    device_id = generate_unique_id("DEV")
    kit_id = generate_unique_id("KIT")
    shipment_id = generate_unique_id("SHIP")

    test_cases = [
        # 1. Create Trial first (needed for shipments)
        {
            "name": "Trial Creation",
            "endpoint": "/trials/",
            "method": "POST",
            "data": {
                "trial_id": trial_id,
                "name": "Test Trial",
                "description": "Test trial description",
                "start_date": datetime.utcnow().isoformat(),
                "end_date": datetime.utcnow().isoformat()
            }
        },
        # 2. Create Site
        {
            "name": "Site Creation",
            "endpoint": "/sites/",
            "method": "POST",
            "data": {
                "site_id": site_id,
                "name": "Test Site",
                "address": {
                    "street": "123 Test St",
                    "city": "Test City",
                    "state": "TS",
                    "postal_code": "12345",
                    "country": "US"
                },
                "associated_trials": [trial_id]
            }
        },
        # 3. Create Device
        {
            "name": "Device Creation",
            "endpoint": "/devices/",
            "method": "POST",
            "data": {
                "device_id": device_id,
                "manufacturer": "Test Manufacturer",
                "device_name": "Test Device",
                "expiration_date": datetime.utcnow().isoformat(),
                "sample_type": "Blood"
            }
        },
        # 4. Create Kit
        {
            "name": "Kit Creation",
            "endpoint": "/kits/",
            "method": "POST",
            "data": {
                "kit_id": kit_id,
                "device_id": device_id,
                "kit_name": "Test Kit",
                "return_box_dimensions": "10x10x10in",
                "return_box_weight": 2.5,
                "is_template": False,
                "total_pieces": 1,
                "contents": {
                    "devices": [
                        {
                            "device_id": device_id,
                            "quantity": 1
                        }
                    ]
                }
            }
        },
        # 5. Create Shipment
        {
            "name": "Shipment Creation",
            "endpoint": "/shipments/",
            "method": "POST",
            "data": {
                "tracking_number": shipment_id,
                "trial_id": trial_id,
                "kit_id": kit_id,
                "status": "PENDING",
                "origin": site_id,
                "destination": site_id,
                "carrier": "Test Carrier",
                "service_type": "Standard",
                "cost": "10.00"
            }
        }
    ]

    results = {}
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. Testing {test['name']}:")
        try:
            response = make_request(
                method=test['method'],
                endpoint=test['endpoint'],
                data=test['data'],
                token=token
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code != 204:  # No content
                response_data = response.json()
                print(f"Response: {json.dumps(response_data, indent=2)}")
            
            results[test['name']] = response_data
            
            if response.status_code not in [200, 201, 204]:
                print(f"⚠️  Warning: Unexpected status code {response.status_code}")
        except Exception as e:
            print(f"❌ Error in {test['name']}: {str(e)}")

    return results

def main():
    print("🚀 Starting API Test Suite...")
    
    # Test MongoDB connection first
    if not test_mongodb_connection():
        print("⚠️  Warning: MongoDB connection failed, but continuing with API tests...")
    
    # Test API endpoints
    try:
        test_api_endpoints()
        print("\n✅ All tests completed!")
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")

if __name__ == "__main__":
    main()