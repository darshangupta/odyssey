from pymongo import MongoClient
import certifi
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def upload_test_data():
    try:
        # Connect to MongoDB using environment variables
        client = MongoClient(
            os.getenv('MONGODB_URI'),
            tlsCAFile=certifi.where()
        )
        db = client.odyssey_db
        print("Connected to MongoDB successfully!")

        # Sample test data
        test_data = {
            "devices": [
                {
                    "device_id": "DEV001",
                    "manufacturer": "TestMfg",
                    "device_name": "Blood Test Kit",
                    "expiration_date": datetime.utcnow() + timedelta(days=180),
                    "batch_no": "BATCH001",
                    "sample_type": "Blood",
                    "temp_range": "2-8°C",
                    "is_hazardous": True
                },
                {
                    "device_id": "DEV002",
                    "manufacturer": "TestMfg",
                    "device_name": "Saliva Test Kit",
                    "expiration_date": datetime.utcnow() + timedelta(days=365),
                    "batch_no": "BATCH002",
                    "sample_type": "Saliva",
                    "temp_range": "15-25°C",
                    "is_hazardous": False
                }
            ],
            "iot_devices": [
                {
                    "device_id": "IOT001",
                    "manufacturer": "IoTMfg",
                    "battery_life": "6 months",
                    "cycle_count": 0,
                    "exists": True
                }
            ],
            "kits": [
                {
                    "kit_id": "KIT001",
                    "kit_name": "Complete Blood Test Kit",
                    "device_id": "DEV001",
                    "iot_device": {
                        "device_id": "IOT001",
                        "manufacturer": "IoTMfg",
                        "battery_life": "6 months",
                        "cycle_count": 0,
                        "exists": True
                    },
                    "return_box_dimensions": "12x8x6in",
                    "return_box_weight": 2.5,
                    "is_template": True
                }
            ],
            "parcels": [
                {
                    "dimensions": "24x18x12in",
                    "weight": 5.5,
                    "total_pieces": 3,
                    "contents": [
                        {
                            "kit_id": "KIT001",
                            "quantity": 2
                        }
                    ],
                    "additional_items": ["Ice pack", "Instructions"],
                    "is_template": True
                }
            ],
            "trials": [
                {
                    "trial_id": "TRIAL001",
                    "associated_sites": ["SITE001"],
                    "associated_patients": ["PAT001"],
                    "diagnostic_kits_template": ["KIT001"],
                    "default_send_address": "ADDR001",
                    "default_receive_address": "ADDR002"
                }
            ],
            "sites": [
                {
                    "site_id": "SITE001",
                    "name": "Test Site 1",
                    "address": "ADDR001",
                    "associated_trials": ["TRIAL001"]
                }
            ],
            "addresses": [
                {
                    "address_id": "ADDR001",
                    "street": "123 Test St",
                    "city": "Test City",
                    "state": "TS",
                    "postal_code": "12345",
                    "country": "Test Country"
                }
            ],
            "shipments": [
                {
                    "tracking_number": "SHIP001",
                    "trial_id": "TRIAL001",
                    "origin": "SITE001",
                    "destination": "SITE002",
                    "status": "PENDING",
                    "carrier": "FedEx",
                    "service_type": "Express",
                    "cost": 45.50,
                    "created_at": datetime.utcnow(),
                    "failures": [],
                    "sample_ids": ["SAMPLE001"],
                    "notification_emails": ["test@example.com"]
                }
            ]
        }

        # Clear existing data
        print("\nClearing existing data...")
        for collection in test_data.keys():
            db[collection].delete_many({})
            print(f"Cleared {collection} collection")

        # Insert new test data
        print("\nInserting test data...")
        for collection, documents in test_data.items():
            if documents:
                result = db[collection].insert_many(documents)
                print(f"Inserted {len(result.inserted_ids)} documents into {collection}")

        print("\nTest data uploaded successfully!")
        
        # Print collection counts
        print("\nCollection counts:")
        for collection in test_data.keys():
            count = db[collection].count_documents({})
            print(f"{collection}: {count} documents")

    except Exception as e:
        print(f"Error: {str(e)}")
        return False

    return True

if __name__ == "__main__":
    upload_test_data() 