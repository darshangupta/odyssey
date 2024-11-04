from ..config.database import get_database, init_db, insert_test_data
from pprint import pprint

def test_collections():
    db = get_database()
    if db is not None:
        print("\nCollections in database:", db.list_collection_names())
        
        # Count documents in each collection
        for collection in db.list_collection_names():
            count = db[collection].count_documents({})
            print(f"{collection}: {count} documents")

def test_relationships():
    db = get_database()
    if db is not None:
        # Example 1: Get all shipments for a trial with patient and site info
        pipeline = [
            {
                "$match": {"trial_id": "TRIAL001"}
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
                    "from": "patients",
                    "localField": "trial_id",
                    "foreignField": "associated_trials",
                    "as": "trial_patients"
                }
            }
        ]
        
        print("\nShipments with related data for TRIAL001:")
        results = list(db.shipments.aggregate(pipeline))
        pprint(results)

        # Example 2: Get site information with all associated patients
        site_pipeline = [
            {
                "$match": {"site_id": "SITE001"}
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
                    "from": "kits",
                    "localField": "site_id",
                    "foreignField": "site_id",
                    "as": "available_kits"
                }
            }
        ]
        
        print("\nSite information with associated patients and kits:")
        site_results = list(db.sites.aggregate(site_pipeline))
        pprint(site_results)

def test_shipment_analytics():
    db = get_database()
    if db is not None:
        # Example 3: Shipment analytics pipeline
        analytics_pipeline = [
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1},
                    "average_price": {"$avg": "$price"},
                    "shipments": {"$push": "$tracking_number"}
                }
            },
            {
                "$sort": {"count": -1}
            }
        ]
        
        print("\nShipment analytics by status:")
        analytics_results = list(db.shipments.aggregate(analytics_pipeline))
        pprint(analytics_results)

if __name__ == "__main__":
    if init_db():
        print("Database initialized successfully!")
        if insert_test_data():
            print("\nRunning tests...")
            test_collections()
            test_relationships()
            test_shipment_analytics()
        else:
            print("Failed to insert test data")
    else:
        print("Failed to initialize database") 