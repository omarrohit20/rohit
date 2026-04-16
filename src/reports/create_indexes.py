#!/usr/bin/env python
"""
MongoDB Index Creation Script
Creates all necessary indexes for optimal query performance in the reports application.
"""

from pymongo import MongoClient, ASCENDING
import sys
from datetime import datetime

def create_indexes():
    """Create all necessary indexes for the reports application"""
    
    try:
        # Connect to MongoDB
        print("🔗 Connecting to MongoDB at localhost:27017...")
        connection = MongoClient('localhost', 27017, serverSelectionTimeoutMS=5000)
        dbcl = connection.chartlink
        
        # Test connection
        connection.server_info()
        print("✅ Connected successfully!\n")
        
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        print("   Make sure MongoDB is running on localhost:27017")
        sys.exit(1)
    
    # Define indexes: (collection_name, [(field, direction), ...])
    indexes = [
        # buy-morning-volume-breakout collections
        ('buy-morning-volume-breakout(Check-News)', [
            [('systemtime', ASCENDING)],
            [('scrip', ASCENDING)],
            [('scrip', ASCENDING), ('yearLowChange', ASCENDING)],
            [('systemtime', ASCENDING), ('scrip', ASCENDING)],
        ]),
        
        # sell-morning-volume-breakout collections
        ('sell-morning-volume-breakout(Check-News)', [
            [('systemtime', ASCENDING)],
            [('scrip', ASCENDING)],
            [('scrip', ASCENDING), ('yearLowChange', ASCENDING)],
            [('systemtime', ASCENDING), ('scrip', ASCENDING)],
        ]),
        
        # Breakout collections
        ('Breakout-Buy-after-10', [
            [('systemtime', ASCENDING)],
            [('scrip', ASCENDING)],
        ]),
        
        ('Breakout-Sell-after-10', [
            [('systemtime', ASCENDING)],
            [('scrip', ASCENDING)],
        ]),
        
        # Morning pattern collections
        ('09_30:checkChartBuy/Sell-morningDown(LastDaybeforeGT0-OR-MidacpCrossedMorningHigh)', [
            [('systemtime', ASCENDING)],
            [('scrip', ASCENDING)],
        ]),
        
        ('09_30:checkChartSell/Buy-morningup(LastDaybeforeLT0-OR-MidacpCrossedMorningLow)', [
            [('systemtime', ASCENDING)],
            [('scrip', ASCENDING)],
        ]),
        
        # Supertrend collections
        ('supertrend-morning-buy', [
            [('systemtime', ASCENDING)],
            [('scrip', ASCENDING)],
        ]),
        
        ('supertrend-morning-sell', [
            [('systemtime', ASCENDING)],
            [('scrip', ASCENDING)],
        ]),
        
        # Day high/low crossovers
        ('crossed-day-high', [
            [('scrip', ASCENDING)],
        ]),
        
        ('crossed-day-low', [
            [('scrip', ASCENDING)],
        ]),
        
        # Volume breakout
        ('morning-volume-breakout-buy', [
            [('systemtime', ASCENDING)],
        ]),
        
        ('morning-volume-breakout-sell', [
            [('systemtime', ASCENDING)],
        ]),
    ]
    
    total_created = 0
    total_skipped = 0
    failed_collections = []
    
    print("📊 Creating indexes...\n")
    print("-" * 80)
    
    for collection_name, index_list in indexes:
        try:
            collection = dbcl[collection_name]
            print(f"\n📦 Collection: {collection_name}")
            
            # Check if collection exists
            if collection_name not in dbcl.list_collection_names():
                print(f"   ⚠️  Collection does not exist yet (will be created when data is inserted)")
                continue
            
            for index_fields in index_list:
                try:
                    # Create the index
                    index_name = collection.create_index(index_fields)
                    total_created += 1
                    
                    # Format field names for display
                    field_str = ", ".join([f"{field[0]} ({['DESC', 'ASC'][field[1]][:3]})" for field in index_fields])
                    print(f"   ✅ Created: {field_str}")
                    
                except Exception as e:
                    if "already exists" in str(e).lower():
                        total_skipped += 1
                        field_str = ", ".join([f"{field[0]}" for field in index_fields])
                        print(f"   ⏭️  Skipped: {field_str} (already exists)")
                    else:
                        raise
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed_collections.append((collection_name, str(e)))
    
    print("\n" + "-" * 80)
    print("\n📈 Index Creation Summary:")
    print(f"   ✅ New indexes created: {total_created}")
    print(f"   ⏭️  Existing indexes skipped: {total_skipped}")
    print(f"   ❌ Collections with errors: {len(failed_collections)}")
    
    if failed_collections:
        print("\n⚠️  Failed Collections:")
        for coll_name, error in failed_collections:
            print(f"   - {coll_name}: {error}")
    
    print("\n" + "=" * 80)
    print("📋 Verifying Index Creation")
    print("=" * 80)
    
    # Verify indexes were created
    for collection_name, _ in indexes:
        try:
            collection = dbcl[collection_name]
            if collection_name not in dbcl.list_collection_names():
                continue
            
            # Get all indexes
            indexes_info = collection.list_indexes()
            print(f"\n📦 {collection_name}:")
            
            for idx in indexes_info:
                if idx['name'] != '_id_':  # Skip default id index
                    key_str = ", ".join([f"{k[0]}" for k in idx['key']])
                    print(f"   • {idx['name']}: {key_str}")
        
        except Exception as e:
            print(f"   Error listing indexes: {e}")
    
    print("\n" + "=" * 80)
    print("✅ Index creation completed successfully!")
    print("=" * 80)
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    connection.close()
    return len(failed_collections) == 0

if __name__ == '__main__':
    success = create_indexes()
    sys.exit(0 if success else 1)
