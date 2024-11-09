import requests
import json

def get_token():
    url = "http://localhost:8000/api/token/"
    
    # These credentials need to match a user in your Django admin
    credentials = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(url, json=credentials)
        if response.status_code == 200:
            tokens = response.json()
            print("\n✅ Successfully obtained tokens!")
            print("\nAccess Token (use this for API calls):")
            print(tokens['access'])
            print("\nRefresh Token (use this to get new access tokens):")
            print(tokens['refresh'])
            return tokens
        else:
            print(f"\n❌ Failed to get token. Status code: {response.status_code}")
            print(f"Response: {response.json()}")
            return None
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    print("🔑 Getting test token...")
    get_token() 