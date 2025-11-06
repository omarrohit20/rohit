from pymongo import MongoClient
from datetime import datetime, timedelta

connection = MongoClient('localhost', 27017)
db = connection.Nsedata
dbchartlink = connection.chartlink

# Copy documents from source to target
def copy_collection(source_collection, target_collection):
    documents = source_collection.find()  # Fetch all documents
    target_collection.insert_many(documents)  # Insert into target collection
    print("Collection copied successfully!")

copy_collection(db["breakoutMH"], dbchartlink["breakoutMH"])
copy_collection(db["breakoutM2H"], dbchartlink["breakoutM2H"])
copy_collection(db["breakoutML"], dbchartlink["breakoutML"])
copy_collection(db["breakoutM2L"], dbchartlink["breakoutM2L"])
copy_collection(db["breakoutMHR"], dbchartlink["breakoutMHR"])
copy_collection(db["breakoutM2HR"], dbchartlink["breakoutM2HR"])
copy_collection(db["breakoutW2HR"], dbchartlink["breakoutW2HR"])

# Close the MongoDB connection
connection.close()