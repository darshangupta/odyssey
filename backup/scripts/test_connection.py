from pymongo import MongoClient
import certifi
from dotenv import load_dotenv
import os

load_dotenv()

def test_connection():
    try:
        # Print the URI (remove password for security)
        uri = os.getenv('MONGODB_URI')
        safe_uri = uri.replace(uri.split(':')[2].split('@')[0], '****')
        print(f"Attempting to connect with: {safe_uri}")
        
        # Try to connect
        client = MongoClient(uri, tlsCAFile=certifi.where())
        
        # Test the connection
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        
        return True
    except Exception as e:
        print(f"Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection() 