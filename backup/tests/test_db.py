from ..config.database import get_database, init_db, insert_test_data
from datetime import datetime
from pprint import pprint

def test_collections():
    db = get_database()
    if db is not None:
        print("\nCollections in database:", db.list_collection_names())
        
        # Count documents in each collection
        for collection in db.list_collection_names():
            count = db[collection].count_documents({})
            print(f"{collection}: {count} documents")
            
            # Print first document as sample
            sample = db[collection].find_one()
            if sample:
                print(f"Sample {collection} document:")
                pprint(sample)
            print("-" * 50)

def test_kit_relationships():
    db = get_database()
    if db is not None:
        # Test Kit relationships with Devices and IoT Devices
        pipeline = [
            {
                "$match": {"kit_id": "KIT001"}
            },
            {
                "$lookup": {
                    "from": "devices",
                    "localField": "device_id",
                    "foreignField": "device_id",
                    "as": "device_details"
                }
            },
            {
                "$lookup": {
                    "from": "iot_devices",
                    "localField": "iot_device.device_id",
                    "foreignField": "device_id",
                    "as": "iot_device_details"
                }
            }
        ]
        
        print("\nKit with related device information:")
        results = list(db.kits.aggregate(pipeline))
        pprint(results)

def test_trial_relationships():
    db = get_database()
    if db is not None:
        # Test Trial relationships with Sites, Patients, and Kit Templates
        pipeline = [
            {
                "$match": {"trial_id": "TRIAL001"}
            },
            {
                "$lookup": {
                    "from": "sites",
                    "localField": "associated_sites",
                    "foreignField": "site_id",
                    "as": "site_details"
                }
            },
            {
                "$lookup": {
                    "from": "patients",
                    "localField": "associated_patients",
                    "foreignField": "patient_id",
                    "as": "patient_details"
                }
            },
            {
                "$lookup": {
                    "from": "parcels",
                    "localField": "diagnostic_kits_template",
                    "foreignField": "kit_id",
                    "as": "kit_templates"
                }
            }
        ]
        
        print("\nTrial with related information:")
        results = list(db.trials.aggregate(pipeline))
        pprint(results)

def test_shipment_analytics():
    db = get_database()
    if db is not None:
        # Comprehensive shipment analytics
        pipeline = [
            {
                "$facet": {
                    "status_summary": [
                        {
                            "$group": {
                                "_id": "$status",
                                "count": {"$sum": 1},
                                "total_cost": {"$sum": "$cost"},
                                "avg_cost": {"$avg": "$cost"}
                            }
                        }
                    ],
                    "failure_analysis": [
                        {"$unwind": "$failures"},
                        {
                            "$group": {
                                "_id": "$failures",
                                "count": {"$sum": 1},
                                "affected_shipments": {"$push": "$tracking_number"}
                            }
                        }
                    ],
                    "monthly_trends": [
                        {
                            "$group": {
                                "_id": {
                                    "year": {"$year": "$created_at"},
                                    "month": {"$month": "$created_at"}
                                },
                                "shipment_count": {"$sum": 1},
                                "total_cost": {"$sum": "$cost"}
                            }
                        },
                        {"$sort": {"_id": 1}}
                    ]
                }
            }
        ]
        
        print("\nComprehensive shipment analytics:")
        analytics_results = list(db.shipments.aggregate(pipeline))
        pprint(analytics_results)

def test_parcel_templates():
    db = get_database()
    if db is not None:
        # Test parcel templates
        pipeline = [
            {
                "$match": {"is_template": True}
            },
            {
                "$lookup": {
                    "from": "kits",
                    "localField": "contents.kit_id",
                    "foreignField": "kit_id",
                    "as": "kit_details"
                }
            }
        ]
        
        print("\nParcel templates with kit details:")
        results = list(db.parcels.aggregate(pipeline))
        pprint(results)

def test_data_validation():
    db = get_database()
    if db is not None:
        print("\nTesting data validation...")
        
        # Test 1: Kit validation
        try:
            invalid_kit = {
                "kit_id": "TEST_KIT",
                "kit_name": "Test Kit",
                # Missing required device_id
                "iot_device": {
                    "device_id": "IOT001",
                    "exists": "invalid_boolean"  # Invalid boolean type
                }
            }
            db.kits.insert_one(invalid_kit)
            print("❌ Kit validation failed")
        except Exception as e:
            print("✅ Kit validation working:", str(e))
            
        # Test 2: Parcel dimensions validation
        try:
            invalid_parcel = {
                "dimensions": "10x10x10cm",  # Should be in inches
                "weight": "invalid_weight",
                "total_pieces": 1
            }
            db.parcels.insert_one(invalid_parcel)
            print("❌ Parcel validation failed")
        except Exception as e:
            print("✅ Parcel validation working:", str(e))
            
        # Test 3: Shipment status validation
        try:
            invalid_shipment = {
                "tracking_number": "TEST001",
                "trial_id": "TRIAL001",
                "origin": "SITE001",
                "destination": "SITE002",
                "status": "INVALID_STATUS"  # Invalid status
            }
            db.shipments.insert_one(invalid_shipment)
            print("❌ Shipment validation failed")
        except Exception as e:
            print("✅ Shipment validation working:", str(e))

if __name__ == "__main__":
    if init_db():
        print("Database initialized successfully!")
        if insert_test_data():
            print("\nRunning tests...")
            test_collections()
            test_kit_relationships()
            test_trial_relationships()
            test_shipment_analytics()
            test_parcel_templates()
            test_data_validation()
        else:
            print("Failed to insert test data")
    else:
        print("Failed to initialize database") 