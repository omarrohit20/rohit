from pymongo import MongoClient, ASCENDING
from datetime import datetime
import json

class MongoDBHandler:
    def __init__(self, db_name="chartlink", collection_name="sentiment_analysis"):
        """Initialize MongoDB connection"""
        try:
            self.client = MongoClient('mongodb://localhost:27017/')
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
            
            # Create indexes for better query performance
            self.collection.create_index([("scrip", ASCENDING)])
            self.collection.create_index([("company", ASCENDING)])
            self.collection.create_index([("news_analysis.news.Date", ASCENDING)])
            self.collection.create_index([("last_updated", ASCENDING)])
            
            print(f"Connected to MongoDB database: {db_name}")
            print(f"Using collection: {collection_name}")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            raise
    
    def insert_sentiment_data(self, sentiment_results):
        """Insert or update sentiment analysis data"""
        inserted_count = 0
        updated_count = 0
        
        try:
            for scrip, data in sentiment_results.items():
                # Add metadata
                data['last_updated'] = datetime.now()
                data['scrip'] = scrip
                
                # Upsert: Update if exists, insert if not
                result = self.collection.update_one(
                    {'scrip': scrip},
                    {
                        '$set': data,
                        '$setOnInsert': {'created_at': datetime.now()}
                    },
                    upsert=True
                )
                
                if result.upserted_id:
                    inserted_count += 1
                elif result.modified_count > 0:
                    updated_count += 1
            
            print(f"\nMongoDB Import Summary:")
            print(f"  - Inserted: {inserted_count} new records")
            print(f"  - Updated: {updated_count} existing records")
            print(f"  - Total processed: {len(sentiment_results)}")
            
            return True
            
        except Exception as e:
            print(f"Error inserting data into MongoDB: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_sentiment_by_scrip(self, scrip):
        """Retrieve sentiment data for a specific scrip"""
        return self.collection.find_one({'scrip': scrip})
    
    def get_all_sentiments(self):
        """Retrieve all sentiment data"""
        return list(self.collection.find())
    
    def get_sentiments_by_impact(self, impact):
        """Get all stocks with specific impact (Positive/Negative/Neutral)"""
        return list(self.collection.find({
            'news_analysis.overall_sentiment': impact
        }))
    
    def get_recent_sentiments(self, days=1):
        """Get sentiments updated in the last N days"""
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        return list(self.collection.find({
            'last_updated': {'$gte': cutoff_date}
        }))
    
    def clear_collection(self):
        """Clear all data from collection (use with caution)"""
        result = self.collection.delete_many({})
        print(f"Deleted {result.deleted_count} documents from collection")
        return result.deleted_count
    
    def close(self):
        """Close MongoDB connection"""
        self.client.close()
        print("MongoDB connection closed")


def get_mongodb_handler(db_name="chartlink", collection_name="sentiment_analysis"):
    """Factory function to get MongoDB handler instance"""
    return MongoDBHandler(db_name=db_name, collection_name=collection_name)
