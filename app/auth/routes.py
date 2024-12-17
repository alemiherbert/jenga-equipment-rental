"""
Authentification routes
"""

from app import db
from app.auth import auth
from app.models import User, Role, Equipment, Booking, Location
from flask import jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required  # type: ignore
from sqlalchemy import select
from werkzeug.security import generate_password_hash


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

    email = request.json.get("email")
    password = request.json.get("password")
    name = request.json.get("name")

    # Validate required fields
    # Todo: Validate emails
    if not email or not password or not name:
        return jsonify({"msg": "Missing required fields"}), 400

    existing_user = db.session.scalar(select(User).where(User.email == email))
    if existing_user:
        return jsonify({"msg": "Email already registered"}), 409

    try:
        new_user = User(
            email=email,
            password_hash=generate_password_hash(password),
            name=name
        )
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
