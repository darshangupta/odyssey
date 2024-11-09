from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Connection string (in production, use environment variables)
MONGO_URI = "mongodb+srv://OdysseyUser:testpass@odysseysamplecluster.elyfw.mongodb.net/?retryWrites=true&w=majority&appName=OdysseySampleCluster"

def get_database():
    try:
        # Create MongoDB client
        client = MongoClient(MONGO_URI)
        
        # Test connection
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        
        # Get database
        return client.odyssey_db
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

def init_db():
    try:
        db = get_database()
        if db is not None:
            # Create or get collections
            users = db.users
            posts = db.posts
            
            # Create indexes if needed
            users.create_index("email", unique=True)
            
            return True
        return False
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

def insert_test_data():
    db = get_database()
    if db is not None:
        try:
            # Trial Information
            trials = [
                {
                    "trial_id": "TRIAL001",
                    "associated_sites": ["SITE001", "SITE002"],
                    "associated_patients": ["PAT001", "PAT002"],
                    "collection_devices": ["DEV001", "DEV002"],
                    "diagnostic_kits_template": "KIT_TEMPLATE_001",
                    "default_send_receive_address": {
                        "exists": True,
                        "address": "123 Main St, Boston, MA 02115"
                    }
                }
            ]

            # Patient Information
            patients = [
                {
                    "patient_id": "PAT001",
                    "email": "patient1@example.com",
                    "phone": "555-0101",
                    "associated_trials": ["TRIAL001"],
                    "associated_sites": ["SITE001"],
                    "scheduled_collection_dates": ["2024-01-15T09:00:00Z"],
                    "contact_person": {
                        "name": "Jane Nurse",
                        "phone": "555-0102",
                        "email": "nurse@hospital.com",
                        "associated_sites": ["SITE001"]
                    }
                }
            ]

            # Site Information
            sites = [
                {
                    "site_id": "SITE001",
                    "address": "456 Hospital Drive",
                    "saved_to_address_book": True,
                    "associated_trials": ["TRIAL001"],
                    "associated_patients": ["PAT001", "PAT002"],
                    "associated_kits": {
                        "inventory_count": 50,
                        "inventory_threshold": 10
                    },
                    "contact_person": {
                        "name": "Dr. Smith",
                        "phone": "555-0103",
                        "email": "smith@hospital.com"
                    }
                }
            ]

            # Test/Diagnostic Kit Information
            kits = [
                {
                    "kit_id": "KIT001",
                    "manufacturer": "BioTech Inc",
                    "expiration_date": "2025-01-01",
                    "batch_no": "BATCH123",
                    "sample_type": "Blood",
                    "temp_range": {
                        "min": 2,
                        "max": 8,
                        "unit": "Celsius"
                    },
                    "hazardous": False,
                    "iot_device": {
                        "id": "IOT001",
                        "manufacturer": "TempTrack",
                        "battery_life": "6 months",
                        "cycle_count": 0
                    }
                }
            ]

            # Parcel Information
            parcels = [
                {
                    "parcel_id": "PARCEL001",
                    "dimensions": {
                        "length": 20,
                        "width": 15,
                        "height": 10,
                        "unit": "cm"
                    },
                    "weight": {
                        "value": 2.5,
                        "unit": "kg"
                    },
                    "total_pieces": 1
                }
            ]

            # Shipment Information
            shipments = [
                {
                    "tracking_number": "SHIP001",
                    "inbound_outbound": "Outbound",
                    "origin": "SITE001",
                    "destination": "LAB001",
                    "pickup_datetime": "2024-01-15T10:00:00Z",
                    "expected_dropoff": "2024-01-16T10:00:00Z",
                    "actual_dropoff": None,
                    "status": "In Transit",
                    "carrier": "FedEx",
                    "service": "FedEx Express Saver",
                    "price": 150.00,
                    "trial_id": "TRIAL001",
                    "collection_device_ids": ["DEV001"],
                    "sample_ids": ["SAMPLE001"],
                    "notification_emails": ["lab@example.com"],
                    "require_signature": True,
                    "hold_at_location": {
                        "required": False,
                        "address": None
                    },
                    "shipment_box_id": "BOX001",
                    "contains_dry_ice": True
                }
            ]

            # Failure Records
            failures = [
                {
                    "failure_id": "FAIL001",
                    "aggregated_shipment_locator": "ASL001",
                    "reason": "Temperature Excursion",
                    "experiment": "EXP001"
                }
            ]

            # Insert all test data
            db.trials.insert_many(trials)
            db.patients.insert_many(patients)
            db.sites.insert_many(sites)
            db.kits.insert_many(kits)
            db.parcels.insert_many(parcels)
            db.shipments.insert_many(shipments)
            db.failures.insert_many(failures)

            # Create indexes
            db.trials.create_index("trial_id", unique=True)
            db.patients.create_index("patient_id", unique=True)
            db.sites.create_index("site_id", unique=True)
            db.kits.create_index("kit_id", unique=True)
            db.shipments.create_index("tracking_number", unique=True)
            
            print("Test data inserted successfully!")
            print("Collections in database:", db.list_collection_names())
            return True
            
        except Exception as e:
            print(f"Error inserting test data: {e}")
            return False

def get_shipment_details(tracking_number):
    """Get complete shipment details including related data"""
    db = get_database()
    if db is not None:
        pipeline = [
            {
                "$match": {"tracking_number": tracking_number}
            },
            {
                "$lookup": {
                    "from": "trials",
                    "localField": "trial_id",
                    "foreignField": "trial_id",
                    "as": "trial_info"
                }
            },
            {
                "$lookup": {
                    "from": "sites",
                    "localField": "origin",
                    "foreignField": "site_id",
                    "as": "origin_site"
                }
            },
            {
                "$lookup": {
                    "from": "sites",
                    "localField": "destination",
                    "foreignField": "site_id",
                    "as": "destination_site"
                }
            },
            {
                "$lookup": {
                    "from": "kits",
                    "localField": "kit_id",
                    "foreignField": "kit_id",
                    "as": "kit_info"
                }
            }
        ]
        return list(db.shipments.aggregate(pipeline))
    return None