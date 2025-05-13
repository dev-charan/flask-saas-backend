from functools import wraps
from flask import request, jsonify, current_app
import jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Bearer token malformed'}), 401

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode the token using the shared secret key
            data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
            current_user_id = data.get('sub') # Assuming 'sub' (subject) claim holds the user_id
            if not current_user_id:
                return jsonify({'message': 'Token is invalid or user ID not found in token!'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        # Pass the user_id to the decorated function
        return f(current_user_id, *args, **kwargs)
    return decorated
