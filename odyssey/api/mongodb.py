from bson import ObjectId
from datetime import datetime
from django.conf import settings
from pymongo import MongoClient
import certifi

def get_db():
    client = MongoClient(
        settings.MONGODB_URI,
        tlsCAFile=certifi.where()
    )
    return client.odyssey_db

def serialize_mongodb_object(obj):
    """Convert MongoDB object to JSON-serializable format"""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: serialize_mongodb_object(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_mongodb_object(item) for item in obj]
    return obj 