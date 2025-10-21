"""
API Gateway for the Cab Booking System
Provides RESTful API endpoints that communicate with backend RPC services
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import xmlrpc.client
import time
import logging
import os
import sys
import threading

# Add the parent directory to sys.path to allow relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from util.clock.lamport_clock import LamportClock

# Create log directory if it doesn't exist (before logging setup)
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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

# Initialize RPC client to connect to load balancer
rpc_client = xmlrpc.client.ServerProxy(
    f"http://{settings.SERVER_HOST}:{settings.LOAD_BALANCER_PORT}{settings.RPC_PATH}", 
    allow_none=True
)

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
        _before_request()
        result = rpc_client.ping(thread_local.request_clock)
        _after_response(result)
        return jsonify({"status": "ok", "backend_status": result})
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/register', methods=['POST'])
def register():
    """API endpoint for user registration"""
    try:
        data = request.json
        _before_request()
        result = rpc_client.register_user(
            data.get('username'),
            data.get('password'),
            data.get('user_type'),
            data.get('name'),
            data.get('email'),
            data.get('phone'),
            thread_local.request_clock
        )
        _after_response(result)
        
        if result.get('success', False):
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """API endpoint for user authentication"""
    try:
        data = request.json
        _before_request()
        result = rpc_client.authenticate_user(
            data.get('username'),
            data.get('password'),
            thread_local.request_clock
        )
        _after_response(result)
        
        if result.get('success', False):
            return jsonify(result), 200
        else:
            return jsonify(result), 401
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/book_cab', methods=['POST'])
def book_cab():
    """API endpoint for booking a cab"""
    try:
        data = request.json
        _before_request()
        result = rpc_client.book_cab(
            data.get('username'),
            data.get('pickup'),
            data.get('destination'),
            thread_local.request_clock
        )
        _after_response(result)
        
        if result.get('success', False):
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"Booking failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/ride/<ride_id>', methods=['GET'])
def get_ride_status(ride_id):
    """API endpoint for getting ride status"""
    try:
        _before_request()
        result = rpc_client.get_ride_status(
            ride_id,
            thread_local.request_clock
        )
        _after_response(result)
        
        if result.get('success', False):
            return jsonify(result), 200
        else:
            return jsonify(result), 404
    except Exception as e:
        logger.error(f"Getting ride status failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/ride/<ride_id>/cancel', methods=['POST'])
def cancel_ride(ride_id):
    """API endpoint for cancelling a ride"""
    try:
        _before_request()
        result = rpc_client.cancel_ride(
            ride_id,
            thread_local.request_clock
        )
        _after_response(result)
        
        if result.get('success', False):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"Cancelling ride failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/ride/<ride_id>/status', methods=['PUT'])
def update_ride_status(ride_id):
    """API endpoint for updating ride status"""
    try:
        data = request.json
        _before_request()
        result = rpc_client.update_ride_status(
            ride_id,
            data.get('status'),
            thread_local.request_clock
        )
        _after_response(result)
        
        if result.get('success', False):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"Updating ride status failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/driver/availability', methods=['POST'])
def set_driver_availability():
    """API endpoint for setting driver availability"""
    try:
        data = request.json
        _before_request()
        result = rpc_client.set_driver_available(
            data.get('driver_name'),
            data.get('location'),
            data.get('is_available', True),
            thread_local.request_clock
        )
        _after_response(result)
        
        if result.get('success', False):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"Setting driver availability failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/cabs', methods=['GET'])
def get_available_cabs():
    """API endpoint for getting available cabs"""
    try:
        location = request.args.get('location', '')
        _before_request()
        result = rpc_client.get_available_cabs(
            location,
            thread_local.request_clock
        )
        _after_response(result)
        
        if result.get('success', False):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"Getting available cabs failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/rides/active', methods=['GET'])
def get_active_rides():
    """API endpoint for getting all active rides"""
    try:
        _before_request()
        result = rpc_client.get_active_rides(thread_local.request_clock)
        _after_response(result)
        
        if result.get('success', False):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"Getting active rides failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/user/<username>/rides', methods=['GET'])
def get_user_rides(username):
    """API endpoint for getting rides for a specific user"""
    try:
        _before_request()
        result = rpc_client.get_user_rides(
            username,
            thread_local.request_clock
        )
        _after_response(result)
        
        if result.get('success', False):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"Getting user rides failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/time', methods=['GET'])
def get_server_time():
    """API endpoint for getting server time"""
    try:
        _before_request()
        result = rpc_client.get_server_time(thread_local.request_clock)
        _after_response(result)
        
        if result.get('success', False):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"Getting server time failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/time/sync', methods=['POST'])
def sync_time():
    """API endpoint for synchronizing time with server"""
    try:
        data = request.json
        _before_request()
        result = rpc_client.synchronize_clocks(
            data.get('client_time', time.time()),
            thread_local.request_clock
        )
        _after_response(result)
        
        if result.get('success', False):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"Time synchronization failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """API endpoint for getting system statistics"""
    try:
        _before_request()
        result = rpc_client.get_server_stats(thread_local.request_clock)
        _after_response(result)
        
        if result.get('success', False):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        logger.error(f"Getting stats failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/load_balancer/stats', methods=['GET'])
def get_load_balancer_stats():
    """API endpoint for getting load balancer statistics"""
    try:
        _before_request()
        result = rpc_client.get_stats()
        _after_response(result)
        
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Getting load balancer stats failed: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


def main():
    """Run the API Gateway"""
    # Create directory for logs if it doesn't exist
    os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
    
    # Start the Flask server
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True
    )


if __name__ == '__main__':
    main()