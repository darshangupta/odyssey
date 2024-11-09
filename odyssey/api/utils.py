from typing import List, Dict
from datetime import datetime
from pymongo import UpdateOne

def bulk_validate_references(db, collection: str, field: str, values: List[str]) -> bool:
    """Validate that all referenced documents exist"""
    count = db[collection].count_documents({field: {'$in': values}})
    return count == len(values)

def bulk_create_with_timestamp(db, collection: str, documents: List[Dict]) -> List[Dict]:
    """Create multiple documents with timestamps"""
    for doc in documents:
        doc['created_at'] = datetime.now()
    result = db[collection].insert_many(documents)
    return list(db[collection].find({'_id': {'$in': result.inserted_ids}}))

def bulk_update_with_timestamp(db, collection: str, filter_field: str, 
                             updates: List[Dict]) -> List[Dict]:
    """Update multiple documents with timestamps"""
    operations = []
    for update in updates:
        filter_value = update.pop(filter_field)
        operations.append(
            UpdateOne(
                {filter_field: filter_value},
                {'$set': {**update, 'updated_at': datetime.now()}}
            )
        )
    result = db[collection].bulk_write(operations)
    return list(db[collection].find({filter_field: {'$in': [u[filter_field] for u in updates]}})) 