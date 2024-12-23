"""
Equipment app routes
"""

from app import db
from app.api import api
from app.api.utils import error_response
from app.models import Equipment
from flask import request, jsonify
from flask_jwt_extended import jwt_required, current_user
from sqlalchemy import select


@api.route("/equipment", methods=["GET"])
def get_equipment_list():
    """Get paginated list of equipment"""
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)
    query = select(Equipment)
    
    # Add filters if provided
    if request.args.get("status"):
        try:
            status = Equipment.Status(request.args.get("status"))
            query = query.where(Equipment.status == status)
        except ValueError:
            return error_response("Invalid status value", 400)
    
    if request.args.get("location_id"):
        query = query.where(Equipment.location_id == request.args.get("location_id", type=int))
    
    # Add price range filter
    if request.args.get("min_price"):
        query = query.where(Equipment.price_per_day >= float(request.args.get("min_price")))
    if request.args.get("max_price"):
        query = query.where(Equipment.price_per_day <= float(request.args.get("max_price")))
    
    return jsonify(Equipment.to_collection_dict(
        query=query,
        page=page,
        per_page=per_page,
        endpoint="api.get_equipment_list"
    )), 200


@api.route("/equipment/<int:equipment_id>", methods=["GET"])
def get_equipment(equipment_id):
    """Get equipment details"""
    equipment = db.session.get(Equipment, equipment_id)
    if not equipment:
        return error_response("Equipment not found", 404)
    
    return jsonify(equipment.to_dict()), 200


@api.route("/equipment", methods=["POST"])
@jwt_required()
def create_equipment():
    """Create new equipment"""
    if not current_user.role or current_user.role.name != "admin":
        return error_response("Unauthorized access", 403)
    
    if not request.is_json:
        return error_response("Missing JSON in request", 400)
    
    data = request.json
    
    # To do: This must be changed
    required_fields = ["name", "price_per_day", "transport_cost_per_km"]
    
    if not all(field in data for field in required_fields):
        return error_response(f"Missing required fields: {', '.join(required_fields)}", 400)
    
    try:
        equipment = Equipment(
            name=data["name"],
            price_per_day=data["price_per_day"],
            transport_cost_per_km=data["transport_cost_per_km"],
            location_id=data.get("location_id")
        )
        db.session.add(equipment)
        db.session.commit()
        
        return jsonify({
            "msg": "Equipment created successfully",
            "equipment": equipment.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error creating equipment: {str(e)}", 500)


@api.route("/equipment/<int:equipment_id>", methods=["PUT"])
@jwt_required()
def update_equipment(equipment_id):
    """Update equipment details"""
    if not current_user.role or current_user.role.name != "admin":
        return error_response("Unauthorized access", 403)
    
    if not request.is_json:
        return error_response("Missing JSON in request", 400)
    
    equipment = db.session.get(Equipment, equipment_id)
    if not equipment:
        return error_response("Equipment not found", 404)
    
    data = request.json
    allowed_fields = ["name", "price_per_day", "transport_cost_per_km", "status", "location_id"]
    
    for field in allowed_fields:
        if field in data:
            if field == "status":
                try:
                    equipment.status = Equipment.Status(data["status"])
                except ValueError:
                    return error_response("Invalid status value", 400)
            else:
                setattr(equipment, field, data[field])
    
    try:
        db.session.commit()
        return jsonify({
            "msg": "Equipment updated successfully",
            "equipment": equipment.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error updating equipment: {str(e)}", 500)


@api.route("/equipment/<int:equipment_id>", methods=["DELETE"])
@jwt_required()
def delete_equipment(equipment_id):
    """Delete equipment"""
    if not current_user.role or current_user.role.name != "admin":
        return error_response("Unauthorized access", 403)
    
    equipment = db.session.get(Equipment, equipment_id)
    if not equipment:
        return error_response("Equipment not found", 404)
    
    try:
        db.session.delete(equipment)
        db.session.commit()
        return jsonify({"msg": "Equipment deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error deleting equipment: {str(e)}", 500)
