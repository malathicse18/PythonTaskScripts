from pymongo import MongoClient

def get_db(db_name):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    return db