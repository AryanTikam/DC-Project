"""
JWT Authentication utilities
"""

import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
import logging
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings

logger = logging.getLogger(__name__)

def generate_token(username, user_type):
    """Generate JWT token for authenticated user"""
    try:
        payload = {
            'username': username,
            'user_type': user_type,
            'exp': datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')
        return token
    except Exception as e:
        logger.error(f"Error generating token: {e}")
        return None

def decode_token(token):
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None

def require_auth(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'success': False, 'message': 'Invalid authorization header format'}), 401
        
        if not token:
            return jsonify({'success': False, 'message': 'Authentication token is missing'}), 401
        
        # Decode and validate token
        payload = decode_token(token)
        if not payload:
            return jsonify({'success': False, 'message': 'Invalid or expired token'}), 401
        
        # Add user info to request context
        request.current_user = payload
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_role(allowed_roles):
    """Decorator to restrict access based on user role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'success': False, 'message': 'Authentication required'}), 401
            
            user_type = request.current_user.get('user_type')
            if user_type not in allowed_roles:
                return jsonify({'success': False, 'message': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
