import os
import re
import logging
from pymongo import MongoClient, errors
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fallback In-Memory Storage Emulator for seamless operation when Mongo instance is unreachable
class InMemoryCollection:
    def __init__(self, name):
        self.name = name
        self.data = []

    def _matches(self, doc, query):
        if not query:
            return True
        for k, v in query.items():
            doc_val = doc.get(k)
            if k == '_id':
                if str(doc_val) != str(v):
                    return False
            elif isinstance(v, dict):
                if '$ne' in v and doc_val == v['$ne']:
                    return False
                if '$in' in v and doc_val not in v['$in']:
                    return False
            elif doc_val != v:
                return False
        return True

    def find_one(self, query):
        for doc in self.data:
            if self._matches(doc, query):
                return doc.copy()
        return None

    def find(self, query=None):
        if not query:
            return [doc.copy() for doc in self.data]
        return [doc.copy() for doc in self.data if self._matches(doc, query)]

    def insert_one(self, doc):
        from bson import ObjectId
        doc_copy = doc.copy()
        if '_id' not in doc_copy:
            doc_copy['_id'] = str(ObjectId())
        self.data.append(doc_copy)
        class InsertResult:
            inserted_id = doc_copy['_id']
        return InsertResult()

    def update_one(self, query, update):
        target = self.find_one(query)
        if target:
            idx = next(i for i, d in enumerate(self.data) if str(d.get('_id')) == str(target.get('_id')))
            if '$set' in update:
                self.data[idx].update(update['$set'])
            return True
        return False

    def update_many(self, query, update):
        targets = self.find(query)
        target_ids = {str(t.get('_id')) for t in targets}
        count = 0
        for doc in self.data:
            if str(doc.get('_id')) in target_ids:
                if '$set' in update:
                    doc.update(update['$set'])
                count += 1
        return count

    def delete_one(self, query):
        target = self.find_one(query)
        if target:
            self.data = [d for d in self.data if str(d.get('_id')) != str(target.get('_id'))]
            return True
        return False

    def delete_many(self, query=None):
        if not query:
            self.data = []
            return True
        to_delete = self.find(query)
        delete_ids = {str(d.get('_id')) for d in to_delete}
        self.data = [d for d in self.data if str(d.get('_id')) not in delete_ids]
        return True

    def create_index(self, keys, unique=False, **kwargs):
        pass

class InMemoryDatabase:
    def __init__(self):
        self.collections = {}

    def get_collection(self, name):
        if name not in self.collections:
            self.collections[name] = InMemoryCollection(name)
        return self.collections[name]

    def __getitem__(self, name):
        return self.get_collection(name)

_in_memory_db = InMemoryDatabase()
_client = None
_db = None

def get_db():
    global _client, _db
    if _db is not None:
        return _db

    mongo_uri = Config.MONGO_URI
    db_name = Config.MONGO_DB_NAME

    if not mongo_uri or mongo_uri.lower() in ('inmemory', 'local', 'none'):
        logger.info("Using resilient in-memory datastore mode.")
        _db = _in_memory_db
        return _db

    try:
        # Fast 1s timeout for localhost, 3s for remote
        timeout_ms = 1000 if 'localhost' in mongo_uri or '127.0.0.1' in mongo_uri else 3000
        _client = MongoClient(mongo_uri, serverSelectionTimeoutMS=timeout_ms)
        # Test connection
        _client.admin.command('ping')
        _db = _client[db_name]
        logger.info(f"Successfully connected to MongoDB database at {mongo_uri}")
        
        # Ensure unique indexes on students collection
        try:
            _db.students.create_index("email", unique=True)
            _db.students.create_index("roll_number", unique=True)
        except Exception as e:
            logger.warning(f"Could not create unique indexes: {e}")

        return _db
    except Exception as e:
        safe_uri = re.sub(r'://.*@', '://***:***@', mongo_uri) if mongo_uri else mongo_uri
        logger.info(f"MongoDB not active ({safe_uri}). Running seamlessly with in-memory datastore.")
        _db = _in_memory_db
        return _db

def get_collection(collection_name):
    db = get_db()
    if isinstance(db, InMemoryDatabase):
        return db.get_collection(collection_name)
    return db[collection_name]

def serialize_mongo(obj):
    """
    Recursively converts MongoDB documents and ObjectIds into JSON-serializable Python data structures.
    Converts any ObjectId (including '_id') into a string representation.
    """
    from bson import ObjectId
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, dict):
        res = {}
        for key, val in obj.items():
            if key == '_id' and val is not None:
                res['_id'] = str(val)
            else:
                res[key] = serialize_mongo(val)
        return res
    if isinstance(obj, list):
        return [serialize_mongo(item) for item in obj]
    if isinstance(obj, tuple):
        return tuple(serialize_mongo(item) for item in obj)
    return obj

