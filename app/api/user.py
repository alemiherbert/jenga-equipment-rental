"""
User app routes
"""

from app import db
from app.api import api
from app.api.utils import error_response
from app.models import User
from flask import request, jsonify
from flask_jwt_extended import jwt_required, current_user
from sqlalchemy import select


@api.route("/users", methods=["GET"])
@jwt_required()
def get_users():
    """Get paginated list of users"""
    if not current_user.role != "admin":
        return error_response("Unauthorized access", 403)
    
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)
    query = select(User)
    
    # Add filters if provided
    if request.args.get("status"):
        try:
            status = User.Status(request.args.get("status"))
            query = query.where(User.status == status)
        except ValueError:
            return error_response("Invalid status value", 400)
    
    return jsonify(User.to_collection_dict(
        query=query, 
        page=page, 
        per_page=per_page,
        endpoint="api.get_users"
    )), 200


@api.route("/users/me", methods=["GET"])
@jwt_required()
def get_self():
    """Return the current user"""
    return jsonify({
        "id": current_user.id,
        "name": current_user.name.split()[0]
    })


@api.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    """Get user details"""
    if current_user.id != user_id and current_user.role != "admin":
        return error_response("Unauthorized access", 403)
    
    user = db.session.get(User, user_id)
    if not user:
        return error_response("User not found", 404)
    
    return jsonify(user.to_dict())


@api.route("/users/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    """Update user details"""
    if current_user.id != user_id and current_user.role != "admin":
        return error_response("Unauthorized access", 403)
    
    if not request.is_json:
        return error_response("Missing JSON in request", 400)
    
    user = db.session.get(User, user_id)
    if not user:
        return error_response("User not found", 404)
    
    data = request.json
    
    # Update allowed fields
    allowed_fields = ["name", "phone", "company"]
    for field in allowed_fields:
        if field in data:
            setattr(user, field, data[field])
    
    try:
        db.session.commit()
        return jsonify({
            "msg": "User updated successfully",
            "user": user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error updating user: {str(e)}", 500)
