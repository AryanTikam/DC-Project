"""
Configuration settings for the Cab Booking System
"""

# Server Configuration
SERVER_HOST = "localhost"
LOAD_BALANCER_PORT = 5000
BASE_SERVER_PORT = 5001
SERVER_COUNT = 3

# RPC Configuration
RPC_PATH = "/RPC2"
REQUEST_TIMEOUT = 10  # seconds

# Clock Synchronization
CLOCK_SYNC_INTERVAL = 60  # seconds
SYNC_ALGORITHM = "ntp"  # ntp or lamport or vector

# Database Configuration (Using in-memory store for now, but could be extended)
USE_PERSISTENT_STORAGE = False
DATABASE_PATH = "database/"

# Security Configuration
AUTH_TOKEN_EXPIRY = 3600  # seconds
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