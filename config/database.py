from pymongo import MongoClient
import motor.motor_asyncio
from decouple import config

MONGO_DETAILS = config("MONGO_DETAILS")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

db = client.skillshare

user_collection = db.get_collection("users")
article_collection = db.get_collection("articles")