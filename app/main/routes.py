"""
Main app routes
"""

from app.main import main
from flask import jsonify
from flask_jwt_extended import jwt_required, current_user
@main.route("/")
def index():
    return jsonify({"greeting": "Hello, World!"})


@main.route("/clandestine")
@jwt_required()
def clandestine():
    return jsonify(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
    )