from pymongo import MongoClient
from dotenv import load_dotenv
import os


load_dotenv()

mongo_uri = os.getenv("Mongourl")
client = MongoClient(mongo_uri)
db = client[os.getenv("MONGO_DB", "cagedb")]

user_collection = db["user"]
answers_collection = db["useranswers"]