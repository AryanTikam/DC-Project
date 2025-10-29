"""
MongoDB Database Connection and Operations
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class MongoDB:
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self.connect()
    
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
            db_name = os.getenv('MONGODB_DB_NAME', 'cab_booking_system')
            
            self._client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
            # Test connection
            self._client.admin.command('ping')
            self._db = self._client[db_name]
            
            # Create indexes for better performance
            self._create_indexes()
            
            logger.info(f"Successfully connected to MongoDB: {db_name}")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def _create_indexes(self):
        """Create database indexes for better query performance"""
        try:
            # Users collection indexes
            self._db.users.create_index("username", unique=True)
            self._db.users.create_index("email", sparse=True)
            self._db.users.create_index([("user_type", 1), ("is_available", 1)])
            
            # Rides collection indexes
            self._db.rides.create_index("ride_id", unique=True)
            self._db.rides.create_index("rider_name")
            self._db.rides.create_index("driver_name")
            self._db.rides.create_index("status")
            self._db.rides.create_index("booking_time")
            
            logger.info("Database indexes created successfully")
        except OperationFailure as e:
            logger.warning(f"Failed to create indexes: {e}")
    
    @property
    def db(self):
        """Get database instance"""
        if self._db is None:
            self.connect()
        return self._db
    
    @property
    def users(self):
        """Get users collection"""
        return self.db.users
    
    @property
    def rides(self):
        """Get rides collection"""
        return self.db.rides
    
    @property
    def sessions(self):
        """Get sessions collection"""
        return self.db.sessions
    
    def close(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            logger.info("MongoDB connection closed")

# Global instance
db = MongoDB()
