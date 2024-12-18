"""
Authentication Routes
"""

from app import db
from app.auth import auth
from app.auth.utils import error_response, validate_fields
from app.models import User, TokenBlocklist
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
import validators
from datetime import datetime, timezone

@auth.route("/login", methods=["POST"])
def login():
    """
    User login route.

    Returns:
        JSON response with access token or error message.
    """
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


@auth.route("/register", methods=["POST"])
def register():
    """
    User registration route.

    Returns:
        JSON response with success message or error details.
    """
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

@auth.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    """
    Logout user and revoke access token
    
    Returns:
        JSON response indicating logout status
    """
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
