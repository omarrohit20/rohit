from pymongo import MongoClient
from datetime import datetime, timedelta

connection = MongoClient('localhost', 27017)
db = connection.Nsedata
dbchartlink = connection.chartlink

# Source and target database/collection
source_collection = db["breakoutMH"]
target_collection = dbchartlink["breakoutMH"]

# Copy documents from source to target
documents = source_collection.find()  # Fetch all documents
target_collection.insert_many(documents)  # Insert into target collection

print("Collection copied successfully!")

# Close the MongoDB connection
connection.close()