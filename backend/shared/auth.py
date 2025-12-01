"""
Authentication and Authorization utilities
JWT token validation with Keycloak
"""
import os
import jwt
import requests
from functools import wraps
from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "https://talentlink-erfan.nl/auth")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "talentlink")
KEYCLOAK_PUBLIC_KEY = None


def get_keycloak_public_key():
    """Fetch Keycloak public key for JWT verification"""
    global KEYCLOAK_PUBLIC_KEY

    if KEYCLOAK_PUBLIC_KEY:
        return KEYCLOAK_PUBLIC_KEY

    try:
        url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            realm_info = response.json()
            KEYCLOAK_PUBLIC_KEY = f"-----BEGIN PUBLIC KEY-----\n{realm_info['public_key']}\n-----END PUBLIC KEY-----"
            logger.info("Keycloak public key fetched successfully")
            return KEYCLOAK_PUBLIC_KEY
        else:
            logger.error(f"Failed to fetch Keycloak public key: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error fetching Keycloak public key: {e}")
        return None


def decode_token(token: str):
    """Decode and validate JWT token"""
    try:
        # Try without verification first (for development)
        unverified = jwt.decode(token, options={"verify_signature": False})

        # For production, verify signature
        public_key = get_keycloak_public_key()
        if public_key:
            decoded = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience="account"
            )
            return decoded
        else:
            # Fallback to unverified for now
            logger.warning("Using unverified token - not recommended for production")
            return unverified
    except jwt.ExpiredSignatureError:
        logger.error("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {e}")
        return None


def get_token_from_request():
    """Extract JWT token from request headers"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None

    return parts[1]


def require_auth(func):
    """Decorator to require authentication"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = get_token_from_request()
        if not token:
            return jsonify({'error': 'Missing authentication token'}), 401

        decoded = decode_token(token)
        if not decoded:
            return jsonify({'error': 'Invalid or expired token'}), 401

        # Attach user info to request
        request.user = {
            'sub': decoded.get('sub'),
            'email': decoded.get('email'),
            'preferred_username': decoded.get('preferred_username'),
            'roles': decoded.get('realm_access', {}).get('roles', [])
        }

        return func(*args, **kwargs)
    return wrapper


def require_role(*allowed_roles):
    """Decorator to require specific roles"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = get_token_from_request()
            if not token:
                return jsonify({'error': 'Missing authentication token'}), 401

            decoded = decode_token(token)
            if not decoded:
                return jsonify({'error': 'Invalid or expired token'}), 401

            user_roles = decoded.get('realm_access', {}).get('roles', [])

            if not any(role in user_roles for role in allowed_roles):
                return jsonify({'error': 'Insufficient permissions'}), 403

            # Attach user info to request
            request.user = {
                'sub': decoded.get('sub'),
                'email': decoded.get('email'),
                'preferred_username': decoded.get('preferred_username'),
                'roles': user_roles
            }

            return func(*args, **kwargs)
        return wrapper
    return decorator


def get_current_user():
    """Get current user from request context"""
    return getattr(request, 'user', None)
