from bson import ObjectId
from datetime import datetime
from django.conf import settings
from pymongo import MongoClient, ASCENDING, DESCENDING
import certifi

def get_db():
    client = MongoClient(
        settings.MONGODB_URI,
        tlsCAFile=certifi.where()
    )
    db = client.odyssey_db
    
    # Create indexes and schemas
    setup_mongodb_schemas(db)
    return db

def setup_mongodb_schemas(db):
    """Setup MongoDB schemas and indexes"""
    
    # Trials Collection
    db.trials.create_index([("trial_id", ASCENDING)], unique=True)
    db.trials.create_index([("associated_sites", ASCENDING)])
    db.trials.create_index([("associated_patients", ASCENDING)])
    
    # Devices Collection
    db.devices.create_index([("device_id", ASCENDING)], unique=True)
    db.devices.create_index([("manufacturer", ASCENDING)])
    db.devices.create_index([("expiration_date", ASCENDING)])
    
    # IoT Devices Collection
    db.iot_devices.create_index([("device_id", ASCENDING)], unique=True)
    db.iot_devices.create_index([("manufacturer", ASCENDING)])
    
    # Kits Collection
    db.kits.create_index([("kit_id", ASCENDING)], unique=True)
    db.kits.create_index([("is_template", ASCENDING)])
    db.kits.create_index([("device_id", ASCENDING)])
    
    # Parcels Collection
    db.parcels.create_index([("shipment_id", ASCENDING)])
    db.parcels.create_index([("is_template", ASCENDING)])
    
    # Patients Collection
    db.patients.create_index([("patient_id", ASCENDING)], unique=True)
    db.patients.create_index([("associated_trials", ASCENDING)])
    db.patients.create_index([("associated_sites", ASCENDING)])
    
    # Contact Persons Collection
    db.contact_persons.create_index([("email", ASCENDING)])
    db.contact_persons.create_index([("role", ASCENDING)])
    
    # Shipments Collection
    db.shipments.create_index([("tracking_number", ASCENDING)], unique=True)
    db.shipments.create_index([("trial_id", ASCENDING)])
    db.shipments.create_index([("origin", ASCENDING)])
    db.shipments.create_index([("destination", ASCENDING)])
    db.shipments.create_index([("status", ASCENDING)])
    db.shipments.create_index([("created_at", DESCENDING)])
    
    # Addresses Collection
    db.addresses.create_index([
        ("street", ASCENDING),
        ("city", ASCENDING),
        ("postal_code", ASCENDING)
    ])

    # Define collection validators
    db.command({
        'collMod': 'kits',
        'validator': {
            '$jsonSchema': {
                'bsonType': 'object',
                'required': ['kit_id', 'kit_name', 'device_id'],
                'properties': {
                    'kit_id': {'bsonType': 'string'},
                    'kit_name': {'bsonType': 'string'},
                    'device_id': {'bsonType': 'string'},
                    'iot_device': {
                        'bsonType': 'object',
                        'properties': {
                            'device_id': {'bsonType': 'string'},
                            'manufacturer': {'bsonType': 'string'},
                            'battery_life': {'bsonType': 'string'},
                            'cycle_count': {'bsonType': 'int'},
                            'exists': {'bsonType': 'bool'}
                        }
                    },
                    'return_box_dimensions': {'bsonType': 'string'},
                    'return_box_weight': {'bsonType': 'double'},
                    'is_template': {'bsonType': 'bool'}
                }
            }
        }
    })

    db.command({
        'collMod': 'parcels',
        'validator': {
            '$jsonSchema': {
                'bsonType': 'object',
                'required': ['dimensions', 'weight', 'total_pieces'],
                'properties': {
                    'dimensions': {'bsonType': 'string'},  # Must be in inches (LxWxH)
                    'weight': {'bsonType': 'double'},      # Must be in lbs
                    'total_pieces': {'bsonType': 'int'},
                    'contents': {
                        'bsonType': 'array',
                        'items': {
                            'bsonType': 'object',
                            'required': ['kit_id', 'quantity'],
                            'properties': {
                                'kit_id': {'bsonType': 'string'},
                                'quantity': {'bsonType': 'int'}
                            }
                        }
                    },
                    'additional_items': {'bsonType': 'array'},
                    'is_template': {'bsonType': 'bool'}
                }
            }
        }
    })

    db.command({
        'collMod': 'shipments',
        'validator': {
            '$jsonSchema': {
                'bsonType': 'object',
                'required': ['tracking_number', 'trial_id', 'origin', 'destination', 'status'],
                'properties': {
                    'tracking_number': {'bsonType': 'string'},
                    'trial_id': {'bsonType': 'string'},
                    'origin': {'bsonType': 'string'},
                    'destination': {'bsonType': 'string'},
                    'status': {
                        'enum': ['PENDING', 'IN_TRANSIT', 'DELIVERED', 'CANCELLED']
                    },
                    'failures': {
                        'bsonType': 'array',
                        'items': {'bsonType': 'string'}
                    },
                    'sample_ids': {
                        'bsonType': 'array',
                        'items': {'bsonType': 'string'}
                    },
                    'notification_emails': {
                        'bsonType': 'array',
                        'items': {'bsonType': 'string'}
                    }
                }
            }
        }
    })

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