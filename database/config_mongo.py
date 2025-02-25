import datetime
from pymongo import MongoClient, errors
from dotenv import load_dotenv
import os
from typing import Any

load_dotenv()

USER_ADMIN_MONGO = os.getenv("USER_ADMIN_MONGO")
PASS_ADMIN_MONGO = os.getenv("PASS_ADMIN_MONGO")
MONGO_DB = "test"
MONGO_URI = f"mongodb://{USER_ADMIN_MONGO}:{PASS_ADMIN_MONGO}@localhost:27017/"

db = None

def initialize_mongo() -> dict[str, Any]:
    global db
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, maxPoolSize=50)
    db = mongo_client[MONGO_DB]

    collections = ["pilot", "session", "sessions_log"]
    for collection in collections:
        if collection not in db.list_collection_names():
            db.create_collection(collection)
    
    return mongo_client.server_info()

def get_or_create_pilot(identification: str, username: str = None, company: str = None) -> dict:
    pilot_collection = db['pilot']
    pilot = pilot_collection.find_one({"identification": identification})
    if not pilot:
        pilot = pilot_collection.insert_one({
            "username": username,
            "identification": identification,
            "company": company
        })
        print("Piloto registrado en la base de datos.")
    else:
        print("Piloto encontrado en la base de datos.")
    return pilot

def new_session(pilot_id: str, meta_data: dict) -> dict:
    session_collection = db['session']
    pilot_sessions = list(session_collection.find({"pilot_id": pilot_id}))
    session_number = 1 if not pilot_sessions else len(pilot_sessions) + 1

    session = session_collection.insert_one({
        "pilot_id": pilot_id,
        "session_number": session_number,
        "create_at": datetime.datetime.now(),
        "meta_data": meta_data,
    })
    return session

def add_session_log(session_id: str, log: dict) -> dict:
    sessions_log_collection = db['sessions_log']
    session_log = sessions_log_collection.insert_one({
        "session_id": session_id,
        "log": log,
        "create_at": datetime.datetime.now().isoformat(timespec='milliseconds'),
    })
    return session_log