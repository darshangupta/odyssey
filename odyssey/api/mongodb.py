from pymongo import MongoClient
from django.conf import settings
from functools import lru_cache

@lru_cache(maxsize=None)
def get_mongodb_client():
    """Get MongoDB client (cached to avoid multiple connections)"""
    return MongoClient(settings.MONGODB_URI)

def get_db():
    """Get database instance"""
    client = get_mongodb_client()
    return client[settings.MONGODB_NAME]

def serialize_mongodb_object(obj):
    """Helper function to serialize MongoDB objects for JSON response"""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == '_id':
                obj[key] = str(value)
            else:
                obj[key] = serialize_mongodb_object(value)
    return obj 