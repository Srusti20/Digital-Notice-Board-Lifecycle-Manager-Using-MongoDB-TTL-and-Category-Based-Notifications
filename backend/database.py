from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["smart_notice_board"]

# Collections
notices_collection = db["notices"]
subscribers_collection = db["subscribers"]  # Registered students
admins_collection = db["admins"]

