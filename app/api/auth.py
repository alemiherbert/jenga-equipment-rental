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

@api.route("/login", methods=["POST"])
def login():
    """
    User login route.

    ---
    tags:
      - Authentication
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              email:
                type: string
                example: "user@example.com"
              password:
                type: string
                example: "password123"
    responses:
      200:
        description: Successful login
        content:
          application/json:
            schema:
              type: object
              properties:
                access_token:
                  type: string
                refresh_token:
                  type: string
      400:
        description: Missing JSON in request or missing email/password
      401:
        description: Invalid email or password
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


@api.route("/register", methods=["POST"])
def register():
    """
    User registration route.

    ---
    tags:
      - Authentication
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              name:
                type: string
                example: "John Doe"
              email:
                type: string
                example: "user@example.com"
              phone:
                type: string
                example: "1234567890"
              company:
                type: string
                example: "Example Inc."
              password:
                type: string
                example: "password123"
    responses:
      201:
        description: User registered successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                msg:
                  type: string
                  example: "User registered successfully"
                tokens:
                  type: object
                  properties:
                    access_token:
                      type: string
                    refresh_token:
                      type: string
      400:
        description: Missing JSON in request or missing required fields
      409:
        description: Email already registered
      500:
        description: Error creating user
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

@api.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    """
    Logout user and revoke access token

    ---
    tags:
      - Authentication
    responses:
      200:
        description: Successfully logged out
        content:
          application/json:
            schema:
              type: object
              properties:
                msg:
                  type: string
                  example: "Successfully logged out"
      500:
        description: Error during logout
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
