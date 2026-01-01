"""
Import sentiment data from sentiment.json into MongoDB chartlink database
"""

import json
import sys
from pymongo import MongoClient
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def import_sentiment_data(drop_collection=False):
    """
    Import sentiment data from JSON file to MongoDB
    
    Args:
        drop_collection: If True, drop the collection before importing
    """
    
    # MongoDB connection
    connection = MongoClient('localhost', 27017)
    db = connection.chartlink
    
    # Collection name
    collection_name = 'sentiment'
    collection = db[collection_name]
    
    # Drop collection if requested
    if drop_collection:
        logger.info(f"Dropping existing collection: {collection_name}")
        db.drop_collection(collection_name)
        logger.info("Collection dropped successfully")
    
    # Read JSON file
    json_file = 'sentiment.json'
    logger.info(f"Reading data from {json_file}")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            sentiment_data = json.load(f)
    except FileNotFoundError:
        logger.error(f"File {json_file} not found!")
        connection.close()
        return
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON file: {e}")
        connection.close()
        return
    
    logger.info(f"Found {len(sentiment_data)} records to import")
    
    # Import data
    imported_count = 0
    updated_count = 0
    error_count = 0
    
    for record in sentiment_data:
        try:
            scrip = record.get('scrip', '')
            
            if not scrip:
                logger.warning("Skipping record with no scrip field")
                error_count += 1
                continue
            
            # Add timestamp
            record['imported_at'] = datetime.now()
            
            # Use upsert to update if exists, insert if new
            result = collection.update_one(
                {'scrip': scrip},
                {'$set': record},
                upsert=True
            )
            
            if result.upserted_id:
                imported_count += 1
                logger.info(f"✓ Imported: {scrip} - {record.get('company', 'N/A')}")
            else:
                updated_count += 1
                logger.info(f"↻ Updated: {scrip} - {record.get('company', 'N/A')}")
                
        except Exception as e:
            logger.error(f"Error importing record for {record.get('scrip', 'Unknown')}: {e}")
            error_count += 1
            continue
    
    # Summary
    logger.info("=" * 60)
    logger.info("Import Summary:")
    logger.info(f"  Total records: {len(sentiment_data)}")
    logger.info(f"  Imported (new): {imported_count}")
    logger.info(f"  Updated (existing): {updated_count}")
    logger.info(f"  Errors: {error_count}")
    logger.info(f"  Collection: {collection_name}")
    logger.info(f"  Database: chartlink")
    logger.info("=" * 60)
    
    # Close connection
    connection.close()
    logger.info("Import completed!")


if __name__ == "__main__":
    # Check for command line argument to drop collection
    drop_collection = False
    if len(sys.argv) > 1 and sys.argv[1] in ['--drop', '-d']:
        drop_collection = True
        logger.info("Drop collection flag detected")
    
    import_sentiment_data(drop_collection=drop_collection)

