from pymongo import MongoClient
from dotenv import load_dotenv
import os


load_dotenv()

mongo_uri = os.getenv("Mongourl") or os.getenv("MONGO_URL") or os.getenv("MONGO_URI")
if not mongo_uri:
    raise RuntimeError("Mongo URI not configured. Set Mongourl or MONGO_URL or MONGO_URI")

client = MongoClient(mongo_uri)
db = client[os.getenv("MONGO_DB", "cagedb")]

user_collection = db["user"]
answers_collection = db["useranswers"]


