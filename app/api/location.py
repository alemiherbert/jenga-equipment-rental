"""
Location app routes
"""
from app import db
from app.api import api
from app.api.utils import error_response
from app.models import Location
from flask import request, jsonify
from flask_jwt_extended import jwt_required, current_user
from sqlalchemy import select


# Location Routes
@api.route("/locations", methods=["GET"])
def get_location_list():
    """Get paginated list of locations"""
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)
    query = select(Location)
    
    # Add filters if provided
    if request.args.get("city"):
        query = query.where(Location.city.ilike(f"%{request.args.get('city')}%"))
    
    if request.args.get("country"):
        query = query.where(Location.country == request.args.get("country"))
    
    if request.args.get("region"):
        query = query.where(Location.region == request.args.get("region"))
    
    return jsonify(Location.to_collection_dict(
        query=query,
        page=page,
        per_page=per_page,
        endpoint="api.get_location_list"
    )), 200


@api.route("/locations/<int:location_id>", methods=["GET"])
def get_location(location_id):
    """Get location details"""
    location = db.session.get(Location, location_id)
    if not location:
        return error_response("Location not found", 404)
    
    return jsonify(location.to_dict()), 200


@api.route("/locations", methods=["POST"])
@jwt_required()
def create_location():
    """Create new location"""
    if current_user != "admin":
        return error_response("Unauthorized access", 403)
    
    if not request.is_json:
        return error_response("Missing JSON in request", 400)
    
    data = request.json
    
    required_fields = ["name", "city", "country"]
    
    if not all(field in data for field in required_fields):
        return error_response(f"Missing required fields: {', '.join(required_fields)}", 400)
    
    try:
        location = Location(
            name=data["name"],
            city=data["city"],
            country=data["country"],
            address=data.get("address"),
            region=data.get("region"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude")
        )
        db.session.add(location)
        db.session.commit()
        
        return jsonify({
            "msg": "Location created successfully",
            "location": location.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error creating location: {str(e)}", 500)


@api.route("/locations/<int:location_id>", methods=["PUT"])
@jwt_required()
def update_location(location_id):
    """Update location details"""
    
    if not request.is_json:
        return error_response("Missing JSON in request", 400)
    
    location = db.session.get(Location, location_id)
    if not location:
        return error_response("Location not found", 404)
    
    data = request.json
    allowed_fields = ["name", "address", "city", "region", "country", "latitude", "longitude"]
    
    for field in allowed_fields:
        if field in data:
            setattr(location, field, data[field])
    
    try:
        db.session.commit()
        return jsonify({
            "msg": "Location updated successfully",
            "location": location.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error updating location: {str(e)}", 500)


@api.route("/locations/<int:location_id>", methods=["DELETE"])
@jwt_required()
def delete_location(location_id):
    """Delete location"""
    if current_user.role != "admin":
        return error_response("Unauthorized access", 403)
    
    location = db.session.get(Location, location_id)
    if not location:
        return error_response("Location not found", 404)
    
    try:
        db.session.delete(location)
        db.session.commit()
        return jsonify({"msg": "Location deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error deleting location: {str(e)}", 500)

