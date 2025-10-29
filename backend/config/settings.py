"""
Configuration settings for the Cab Booking System
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Server Configuration
SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
LOAD_BALANCER_PORT = int(os.getenv("LOAD_BALANCER_PORT", 5000))
BASE_SERVER_PORT = 5001
SERVER_COUNT = 3

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "cab_booking_system")

# Flask Configuration
SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")
FLASK_ENV = os.getenv("FLASK_ENV", "development")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-change-in-production")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", 24))

# RPC Configuration
RPC_PATH = "/RPC2"
REQUEST_TIMEOUT = 10  # seconds

# Clock Synchronization
CLOCK_SYNC_INTERVAL = 60  # seconds
SYNC_ALGORITHM = "ntp"  # ntp or lamport or vector

# Database Configuration (Using in-memory store for now, but could be extended)
USE_PERSISTENT_STORAGE = True
DATABASE_PATH = "database/"

# Security Configuration
AUTH_TOKEN_EXPIRY = 3600 * JWT_EXPIRATION_HOURS  # seconds
ENCRYPT_PASSWORDS = True

# Replication Configuration
REPLICATION_MODE = "synchronous"  # synchronous or asynchronous
CONSISTENCY_LEVEL = "quorum"  # one, quorum, all

# Pricing Configuration
BASE_FARE = 50  # in INR
PER_KM_RATE = 12  # in INR
PER_MINUTE_RATE = 2  # in INR
SURGE_FACTOR = 1.0  # Multiplier for peak times

# System Constants
RIDE_STATUSES = ["REQUESTED", "ACCEPTED", "IN_PROGRESS", "COMPLETED", "CANCELLED"]
USER_TYPES = ["RIDER", "DRIVER"]
PAYMENT_METHODS = ["CASH", "CARD", "WALLET"]
PAYMENT_STATUSES = ["PENDING", "COMPLETED", "FAILED"]

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = "logs/cab_service.log"