"""
Authentification routes
"""

from app import db
from app.auth import auth
from app.models import User, Role, Equipment, Booking, Location
from flask import jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from sqlalchemy import select
import validators

@auth.route("/login", methods=["POST"])
def login():
    """
    Login functionality
    
    Returns:
        JSON response with access token or error message
    """
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    email = request.json.get("email")
    password = request.json.get("password")

    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400

    user = db.session.scalar(select(User).where(User.email == email))
    
    if user is None or not user.check_password(password):
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token)


@auth.route("/register", methods=["POST"])
def register():
    """
    Registration functionality
    
    Returns:
        JSON response with success message or error details
    """
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    name = request.json.get("name")
    email = request.json.get("email")
    phone = request.json.get("phone")
    company = request.json.get("company")
    password = request.json.get("password")


    # Validate required fields
    required_fields = {
        "name": name,
        "email": email,
        "phone": phone,
        "company": company,
        "password": password,
    }
    
    if missing_fields := [field for field, value in required_fields.items() if not value]:
        return jsonify({"msg": f"Missing required fields: [{', '.join(missing_fields)}]"}), 400
    
    validations = {
        "name": [validators.length],
        "email": [validators.length, validators.email],
        "phone": [validators.length],
        "company": [validators.length]
    }
    
    for field, funcs in validations.items():
        value = required_fields[field]
        for func in funcs:
            if func == validators.length and not func(value, max_val=64):
                return jsonify({"msg": f"{field.title()} must not exceed 64 characters"}), 400
            elif func != validators.length and not func(value):
                return jsonify({"msg": f"Invalid {field} format"}), 400

    existing_user = db.session.scalar(select(User).where(User.email == email))
    if existing_user:
        return jsonify({"msg": "Email already registered!"}), 409

    try:
        new_user = User(
            email=email,
            name=name,
            company=company
        )
        # Todo: Obtain and store user location
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        # Generate access token
        access_token = create_access_token(identity=email)
        return jsonify({
            "msg": "User registered successfully",
            "access_token": access_token
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error creating user", "error": str(e)}), 500
