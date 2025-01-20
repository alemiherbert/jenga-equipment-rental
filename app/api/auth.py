"""
Authentication Routes
"""

from app import db
from app.api import api
from app.api.utils import error_response, validate_fields
from app.models import User, TokenBlocklist
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
import validators
from datetime import datetime, timezone
from flasgger import swag_from

@api.route("/login", methods=["POST"])
@swag_from({
    'tags': ['Authentication'],
    'description': 'Authenticate a user and return JWT tokens',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string', 'example': 'user@example.com'},
                    'password': {'type': 'string', 'example': 'yourpassword'}
                },
                'required': ['email', 'password']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Successfully authenticated',
            'examples': {
                'application/json': {
                    'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                    'refresh_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
                }
            }
        },
        400: {
            'description': 'Missing JSON or required fields',
            'examples': {
                'application/json': {
                    'msg': 'Missing JSON in request'
                }
            }
        },
        401: {
            'description': 'Invalid email or password',
            'examples': {
                'application/json': {
                    'msg': 'Invalid email or password'
                }
            }
        }
    }
})
def login():
    if not request.is_json:
        return error_response("Missing JSON in request", 400)

    email = request.json.get("email")
    password = request.json.get("password")

    if not email or not password:
        return error_response("Missing email or password", 400)

    user = User.verify_by_email(email)
    if user is None or not user.check_password(password):
        return error_response("Invalid email or password", 401)

    tokens = user.get_tokens()
    return jsonify(tokens), 200


@api.route("/register", methods=["POST"])
@swag_from({
    'tags': ['Authentication'],
    'description': 'Register a new user and return JWT tokens',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'John Doe'},
                    'email': {'type': 'string', 'example': 'user@example.com'},
                    'phone': {'type': 'string', 'example': '1234567890'},
                    'company': {'type': 'string', 'example': 'Example Corp'},
                    'password': {'type': 'string', 'example': 'yourpassword'}
                },
                'required': ['name', 'email', 'phone', 'company', 'password']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'User registered successfully',
            'examples': {
                'application/json': {
                    'msg': 'User registered successfully',
                    'tokens': {
                        'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
                        'refresh_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
                    }
                }
            }
        },
        400: {
            'description': 'Missing JSON or required fields',
            'examples': {
                'application/json': {
                    'msg': 'Missing required fields: name, email'
                }
            }
        },
        409: {
            'description': 'Email already registered',
            'examples': {
                'application/json': {
                    'msg': 'Email already registered'
                }
            }
        },
        500: {
            'description': 'Error creating user',
            'examples': {
                'application/json': {
                    'msg': 'Error creating user',
                    'error': 'Some error message'
                }
            }
        }
    }
})
def register():
    if not request.is_json:
        return error_response("Missing JSON in request", 400)

    # Extract required fields
    required_fields = {
        "name": request.json.get("name"),
        "email": request.json.get("email"),
        "phone": request.json.get("phone"),
        "company": request.json.get("company"),
        "password": request.json.get("password"),
    }

    # Check for missing fields
    missing_fields = [field for field, value in required_fields.items() if not value]
    if missing_fields:
        return error_response(f"Missing required fields: {', '.join(missing_fields)}", 400)

    # Validation rules
    validations = {
        "name": [validators.length],
        "email": [validators.length, validators.email],
        "phone": [validators.length],
        "company": [validators.length],
    }

    # Validate fields
    is_valid, error_message = validate_fields(required_fields, validations)
    if not is_valid:
        return error_response(error_message, 400)

    # Check if the email is already registered
    if User.verify_by_email(required_fields["email"]):
        return error_response("Email already registered", 409)

    # Create new user
    try:
        new_user = User(
            name=required_fields["name"],
            email=required_fields["email"],
            phone=required_fields["phone"],            
            company=required_fields["company"],
        )
        new_user.set_password(required_fields["password"])
        db.session.add(new_user)
        db.session.commit()

        # Generate tokens
        tokens = new_user.get_tokens()
        return jsonify({"msg": "User registered successfully", "tokens": tokens}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error creating user", "error": str(e)}), 500

@api.route("/logout", methods=["DELETE"])
@jwt_required()
@swag_from({
    'tags': ['Authentication'],
    'description': 'Logout a user by revoking the JWT token',
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {
            'description': 'Successfully logged out',
            'examples': {
                'application/json': {
                    'msg': 'Successfully logged out'
                }
            }
        },
        500: {
            'description': 'Error during logout',
            'examples': {
                'application/json': {
                    'msg': 'Error during logout',
                    'error': 'Some error message'
                }
            }
        }
    }
})
def logout():
    try:
        jti = get_jwt()["jti"]
        now = datetime.now(timezone.utc)
        
        # Store the revoked token
        db.session.add(TokenBlocklist(jti=jti, created_at=now))
        db.session.commit()
        
        return jsonify({"msg": "Successfully logged out"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error during logout", "error": str(e)}), 500
