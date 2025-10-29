"""
API Gateway for the Cab Booking System
Provides RESTful API endpoints that communicate with backend RPC services
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
import xmlrpc.client
import time
import logging
import os
import sys
import threading
import bcrypt

# Add the parent directory to sys.path to allow relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from util.clock.lamport_clock import LamportClock
from util.auth import generate_token, decode_token, require_auth
from database.mongodb import db

# Create log directory if it doesn't exist (before logging setup)
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = settings.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True

CORS(app, supports_credentials=True)  # Enable CORS for all routes
Session(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("APIGateway")

# Initialize RPC client to connect to load balancer (optional, for backward compatibility)
try:
    rpc_client = xmlrpc.client.ServerProxy(
        f"http://{settings.SERVER_HOST}:{settings.LOAD_BALANCER_PORT}{settings.RPC_PATH}", 
        allow_none=True
    )
except Exception as e:
    logger.warning(f"Could not connect to RPC server: {e}")
    rpc_client = None

# Initialize Lamport clock
lamport_clock = LamportClock()

# Thread-local storage for request context
thread_local = threading.local()

def _before_request():
    """Prepare request context with a new Lamport clock timestamp"""
    thread_local.request_clock = lamport_clock.increment()
    return thread_local.request_clock

def _after_response(response_data):
    """Update Lamport clock after receiving response"""
    if isinstance(response_data, dict) and "server_clock" in response_data:
        lamport_clock.update(response_data["server_clock"])
    return response_data

@app.route('/api/health', methods=['GET'])
def health_check():
    """API endpoint for health check"""
    try:
        # Check MongoDB connection
        db.db.command('ping')
        mongo_status = "connected"
    except Exception as e:
        mongo_status = f"error: {str(e)}"
    
    try:
        # Check RPC connection if available
        if rpc_client:
            _before_request()
            result = rpc_client.ping(thread_local.request_clock)
            _after_response(result)
            rpc_status = result
        else:
            rpc_status = "not configured"
    except Exception as e:
        rpc_status = f"error: {str(e)}"
    
    return jsonify({
        "status": "ok", 
        "mongodb": mongo_status,
        "rpc_backend": rpc_status,
        "timestamp": time.time()
    })

@app.route('/api/register', methods=['POST'])
def register():
    """API endpoint for user registration"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['username', 'password', 'user_type', 'name', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"success": False, "message": f"Missing required field: {field}"}), 400
        
        # Check if user already exists
        existing_user = db.users.find_one({"username": data['username']})
        if existing_user:
            return jsonify({"success": False, "message": "Username already exists"}), 400
        
        # Check if email already exists
        existing_email = db.users.find_one({"email": data['email']})
        if existing_email:
            return jsonify({"success": False, "message": "Email already registered"}), 400
        
        # Hash password
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        
        # Create user document
        user_doc = {
            'username': data['username'],
            'password': hashed_password,
            'user_type': data['user_type'],
            'name': data['name'],
            'email': data['email'],
            'phone': data.get('phone', ''),
            'current_location': None,
            'rating': 5.0,
            'created_at': time.time(),
            'last_active': time.time(),
            'is_available': False if data['user_type'] == 'DRIVER' else None,
            'vehicle_info': {} if data['user_type'] == 'DRIVER' else None
        }
        
        # Insert user into database
        result = db.users.insert_one(user_doc)
        
        logger.info(f"User registered successfully: {data['username']}")
        
        return jsonify({
            "success": True, 
            "message": "Registration successful",
            "user_id": str(result.inserted_id)
        }), 201
        
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """API endpoint for user authentication"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('username') or not data.get('password'):
            return jsonify({"success": False, "message": "Username and password required"}), 400
        
        # Find user in database
        user = db.users.find_one({"username": data['username']})
        
        if not user:
            return jsonify({"success": False, "message": "Invalid username or password"}), 401
        
        # Verify password
        if not bcrypt.checkpw(data['password'].encode('utf-8'), user['password']):
            return jsonify({"success": False, "message": "Invalid username or password"}), 401
        
        # Generate JWT token
        token = generate_token(user['username'], user['user_type'])
        
        # Update last active time
        db.users.update_one(
            {"username": user['username']},
            {"$set": {"last_active": time.time()}}
        )
        
        # Create session
        session['username'] = user['username']
        session['user_type'] = user['user_type']
        
        logger.info(f"User logged in successfully: {user['username']}")
        
        return jsonify({
            "success": True,
            "message": "Login successful",
            "token": token,
            "user_type": user['user_type'],
            "user_info": {
                "username": user['username'],
                "name": user['name'],
                "email": user['email'],
                "phone": user.get('phone', ''),
                "rating": user.get('rating', 5.0),
                "user_type": user['user_type']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """API endpoint for user logout"""
    try:
        session.clear()
        return jsonify({"success": True, "message": "Logout successful"}), 200
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/me', methods=['GET'])
@require_auth
def get_current_user():
    """API endpoint for getting current user info"""
    try:
        username = request.current_user['username']
        user = db.users.find_one({"username": username}, {"password": 0})
        
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404
        
        # Convert ObjectId to string
        user['_id'] = str(user['_id'])
        
        return jsonify({"success": True, "user": user}), 200
    except Exception as e:
        logger.error(f"Getting current user failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/book_cab', methods=['POST'])
@require_auth
def book_cab():
    """API endpoint for booking a cab"""
    try:
        data = request.json
        username = request.current_user['username']
        
        # Validate required fields
        if not data.get('pickup') or not data.get('destination'):
            return jsonify({"success": False, "message": "Pickup and destination required"}), 400
        
        # Generate unique ride ID
        import uuid
        ride_id = str(uuid.uuid4())
        
        # Calculate fare (simplified)
        base_fare = settings.BASE_FARE
        estimated_distance = data.get('estimated_distance', 10)  # km
        estimated_time = data.get('estimated_time', 20)  # minutes
        
        fare = base_fare + (estimated_distance * settings.PER_KM_RATE) + (estimated_time * settings.PER_MINUTE_RATE)
        
        # Create ride document
        ride_doc = {
            'ride_id': ride_id,
            'rider_name': username,
            'driver_name': None,
            'pickup': data['pickup'],
            'destination': data['destination'],
            'status': 'REQUESTED',
            'booking_time': time.time(),
            'start_time': None,
            'end_time': None,
            'estimated_time': estimated_time,
            'estimated_distance': estimated_distance,
            'fare': fare,
            'payment_status': 'PENDING',
            'rider_rating': None,
            'driver_rating': None,
            'version': 0,
            'vector_clock': {}
        }
        
        # Insert ride into database
        result = db.rides.insert_one(ride_doc)
        
        logger.info(f"Cab booked successfully: {ride_id}")
        
        return jsonify({
            "success": True,
            "message": "Cab booked successfully",
            "ride_id": ride_id,
            "fare": fare,
            "estimated_time": estimated_time
        }), 201
        
    except Exception as e:
        logger.error(f"Booking failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/ride/<ride_id>', methods=['GET'])
@require_auth
def get_ride_status(ride_id):
    """API endpoint for getting ride status"""
    try:
        ride = db.rides.find_one({"ride_id": ride_id}, {"_id": 0})
        
        if not ride:
            return jsonify({"success": False, "message": "Ride not found"}), 404
        
        return jsonify({"success": True, "ride": ride}), 200
        
    except Exception as e:
        logger.error(f"Getting ride status failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/ride/<ride_id>/cancel', methods=['POST'])
@require_auth
def cancel_ride(ride_id):
    """API endpoint for cancelling a ride with rating penalty"""
    try:
        username = request.current_user['username']
        user_type = request.current_user['user_type']
        
        # Find the ride
        ride = db.rides.find_one({"ride_id": ride_id})
        
        if not ride:
            return jsonify({"success": False, "message": "Ride not found"}), 404
        
        # Check if user is authorized to cancel
        if ride['rider_name'] != username and ride.get('driver_name') != username:
            return jsonify({"success": False, "message": "Unauthorized"}), 403
        
        # Check if ride can be cancelled
        if ride['status'] in ['COMPLETED', 'CANCELLED']:
            return jsonify({"success": False, "message": f"Cannot cancel a {ride['status'].lower()} ride"}), 400
        
        # Determine penalty based on ride status and who is cancelling
        rating_penalty = 0.0
        cancellation_reason = ""
        
        if ride['status'] == 'REQUESTED':
            # Early cancellation - smaller penalty
            rating_penalty = 0.1
            cancellation_reason = "Cancelled before driver assignment"
        elif ride['status'] == 'ACCEPTED':
            # Cancelling after driver accepted - medium penalty
            rating_penalty = 0.3
            if user_type == 'DRIVER':
                cancellation_reason = "Driver cancelled after accepting"
            else:
                cancellation_reason = "Rider cancelled after driver accepted"
        elif ride['status'] == 'IN_PROGRESS':
            # Cancelling during ride - highest penalty
            rating_penalty = 0.5
            if user_type == 'DRIVER':
                cancellation_reason = "Driver cancelled during ride"
            else:
                cancellation_reason = "Rider cancelled during ride"
        
        # Apply rating penalty to the user who cancelled
        user = db.users.find_one({"username": username})
        if user:
            current_rating = user.get('rating', 5.0)
            new_rating = max(1.0, current_rating - rating_penalty)  # Minimum rating is 1.0
            
            db.users.update_one(
                {"username": username},
                {"$set": {"rating": new_rating}}
            )
        
        # Update ride status
        result = db.rides.update_one(
            {"ride_id": ride_id},
            {"$set": {
                "status": "CANCELLED",
                "cancelled_by": username,
                "cancellation_reason": cancellation_reason,
                "cancellation_time": time.time()
            }}
        )
        
        # If driver was assigned, make them available again
        if ride.get('driver_name'):
            db.users.update_one(
                {"username": ride['driver_name']},
                {"$set": {"is_available": True}}
            )
        
        if result.modified_count > 0:
            logger.info(f"Ride cancelled: {ride_id} by {username} (penalty: {rating_penalty})")
            return jsonify({
                "success": True, 
                "message": "Ride cancelled successfully",
                "rating_penalty": rating_penalty,
                "new_rating": new_rating if user else None,
                "reason": cancellation_reason
            }), 200
        else:
            return jsonify({"success": False, "message": "Failed to cancel ride"}), 400
            
    except Exception as e:
        logger.error(f"Cancelling ride failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/user/<username>/rides', methods=['GET'])
@require_auth
def get_user_rides(username):
    """API endpoint for getting user rides"""
    try:
        current_username = request.current_user['username']
        
        # Users can only view their own rides
        if current_username != username:
            return jsonify({"success": False, "message": "Unauthorized"}), 403
        
        # Get user type to determine query
        user = db.users.find_one({"username": username})
        
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404
        
        # Query based on user type
        if user['user_type'] == 'DRIVER':
            rides = list(db.rides.find({"driver_name": username}, {"_id": 0}).sort("booking_time", -1))
        else:
            rides = list(db.rides.find({"rider_name": username}, {"_id": 0}).sort("booking_time", -1))
        
        return jsonify({"success": True, "rides": rides, "count": len(rides)}), 200
        
    except Exception as e:
        logger.error(f"Getting user rides failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/rides/active', methods=['GET'])
@require_auth
def get_active_rides():
    """API endpoint for getting active rides"""
    try:
        username = request.current_user['username']
        user_type = request.current_user['user_type']
        
        # Query based on user type
        if user_type == 'DRIVER':
            rides = list(db.rides.find({
                "status": {"$in": ["REQUESTED", "ACCEPTED", "IN_PROGRESS"]},
                "$or": [
                    {"driver_name": username},
                    {"driver_name": None}  # Unassigned rides
                ]
            }, {"_id": 0}).sort("booking_time", -1))
        else:
            rides = list(db.rides.find({
                "rider_name": username,
                "status": {"$in": ["REQUESTED", "ACCEPTED", "IN_PROGRESS"]}
            }, {"_id": 0}).sort("booking_time", -1))
        
        return jsonify({"success": True, "rides": rides, "count": len(rides)}), 200
        
    except Exception as e:
        logger.error(f"Getting active rides failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/rides/available', methods=['GET'])
@require_auth
def get_available_rides_for_drivers():
    """API endpoint for getting available rides (for drivers only)"""
    try:
        user_type = request.current_user['user_type']
        
        # Only drivers can access this endpoint
        if user_type != 'DRIVER':
            return jsonify({"success": False, "message": "Only drivers can access this endpoint"}), 403
        
        # Find unassigned rides
        rides = list(db.rides.find({
            "status": "REQUESTED",
            "driver_name": None
        }, {"_id": 0}).sort("booking_time", 1))
        
        return jsonify({"success": True, "rides": rides, "count": len(rides)}), 200
        
    except Exception as e:
        logger.error(f"Getting available rides failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/ride/<ride_id>/accept', methods=['POST'])
@require_auth
def accept_ride(ride_id):
    """API endpoint for driver to accept a ride"""
    try:
        username = request.current_user['username']
        user_type = request.current_user['user_type']
        
        # Only drivers can accept rides
        if user_type != 'DRIVER':
            return jsonify({"success": False, "message": "Only drivers can accept rides"}), 403
        
        # Find the ride
        ride = db.rides.find_one({"ride_id": ride_id})
        
        if not ride:
            return jsonify({"success": False, "message": "Ride not found"}), 404
        
        if ride['status'] != 'REQUESTED':
            return jsonify({"success": False, "message": "Ride is not available"}), 400
        
        if ride.get('driver_name') is not None:
            return jsonify({"success": False, "message": "Ride already assigned"}), 400
        
        # Accept the ride
        result = db.rides.update_one(
            {"ride_id": ride_id, "driver_name": None},
            {"$set": {
                "driver_name": username,
                "status": "ACCEPTED",
                "accept_time": time.time()
            }}
        )
        
        if result.modified_count > 0:
            logger.info(f"Ride accepted: {ride_id} by {username}")
            return jsonify({"success": True, "message": "Ride accepted successfully"}), 200
        else:
            return jsonify({"success": False, "message": "Failed to accept ride"}), 400
            
    except Exception as e:
        logger.error(f"Accepting ride failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/driver/availability', methods=['POST'])
@require_auth
def set_driver_availability():
    """API endpoint for setting driver availability"""
    try:
        data = request.json
        username = request.current_user['username']
        user_type = request.current_user['user_type']
        
        # Check if user is a driver
        if user_type != 'DRIVER':
            return jsonify({"success": False, "message": "Only drivers can set availability"}), 403
        
        # Update driver availability
        result = db.users.update_one(
            {"username": username},
            {
                "$set": {
                    "is_available": data.get('is_available', True),
                    "current_location": data.get('location'),
                    "last_active": time.time()
                }
            }
        )
        
        if result.modified_count > 0:
            logger.info(f"Driver availability updated: {username}")
            return jsonify({"success": True, "message": "Availability updated successfully"}), 200
        else:
            return jsonify({"success": False, "message": "Failed to update availability"}), 400
            
    except Exception as e:
        logger.error(f"Setting driver availability failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/drivers/available', methods=['GET'])
@require_auth
def get_available_drivers():
    """API endpoint for getting available drivers"""
    try:
        location = request.args.get('location', '')
        
        # Find available drivers
        drivers = list(db.users.find(
            {"user_type": "DRIVER", "is_available": True},
            {"password": 0, "_id": 0}
        ))
        
        return jsonify({"success": True, "drivers": drivers, "count": len(drivers)}), 200
        
    except Exception as e:
        logger.error(f"Getting available drivers failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/cabs', methods=['GET'])
@require_auth
def get_available_cabs():
    """API endpoint for getting available cabs (alias for available drivers)"""
    try:
        location = request.args.get('location', '')
        
        # Find available drivers near the location
        query = {"user_type": "DRIVER", "is_available": True}
        if location:
            query["current_location"] = location
        
        drivers = list(db.users.find(query, {"password": 0, "_id": 0}))
        
        return jsonify({
            "success": True, 
            "available_drivers": drivers, 
            "count": len(drivers)
        }), 200
        
    except Exception as e:
        logger.error(f"Getting available cabs failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """API endpoint for getting system statistics"""
    try:
        # Count statistics
        total_users = db.users.count_documents({})
        total_drivers = db.users.count_documents({"user_type": "DRIVER"})
        total_riders = db.users.count_documents({"user_type": "RIDER"})
        available_drivers = db.users.count_documents({"user_type": "DRIVER", "is_available": True})
        
        total_rides = db.rides.count_documents({})
        active_rides = db.rides.count_documents({"status": {"$in": ["REQUESTED", "ACCEPTED", "IN_PROGRESS"]}})
        completed_rides = db.rides.count_documents({"status": "COMPLETED"})
        cancelled_rides = db.rides.count_documents({"status": "CANCELLED"})
        
        stats = {
            "server_id": "api-gateway-1",
            "is_leader": True,
            "system_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "lamport_clock": lamport_clock.time,
            "vector_clock": {"server-1": lamport_clock.time},
            "users": {
                "total": total_users,
                "riders": total_riders,
                "drivers": total_drivers
            },
            "drivers": {
                "available": available_drivers,
                "busy": total_drivers - available_drivers
            },
            "rides": {
                "total": total_rides,
                "active": active_rides,
                "completed": completed_rides,
                "cancelled": cancelled_rides
            },
            "timestamp": time.time()
        }
        
        return jsonify({"success": True, "stats": stats}), 200
        
    except Exception as e:
        logger.error(f"Getting stats failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/time', methods=['GET'])
def get_time():
    """API endpoint for getting server time"""
    try:
        return jsonify({
            "success": True,
            "server_time": time.time(),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "lamport_clock": lamport_clock.time
        }), 200
    except Exception as e:
        logger.error(f"Getting time failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/time/sync', methods=['POST'])
def sync_time():
    """API endpoint for time synchronization"""
    try:
        data = request.json
        client_time = data.get('client_time', 0)
        
        # Get server time
        server_time = time.time()
        
        # Calculate offset
        offset = server_time - client_time
        
        # Increment Lamport clock
        lamport_clock.increment()
        
        return jsonify({
            "success": True,
            "server_time": server_time,
            "client_time": client_time,
            "offset": offset,
            "lamport_clock": lamport_clock.time,
            "message": "Time synchronized successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Time sync failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


def main():
    """Run the API Gateway"""
    # Create directory for logs if it doesn't exist
    os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
    
    # Initialize MongoDB connection
    try:
        db.db.command('ping')
        logger.info("MongoDB connection established successfully")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        logger.warning("API Gateway will start but database operations may fail")
    
    # Start the Flask server
    logger.info(f"Starting API Gateway on port 5000")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )


if __name__ == '__main__':
    main()