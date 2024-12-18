"""
Location app routes
"""
from app import db
from app.api import api
from app.api.utils import error_response
from app.models import Booking, Equipment
from flask import request, jsonify
from flask_jwt_extended import jwt_required, current_user
from sqlalchemy import select
from datetime import datetime

@api.route("/bookings", methods=["GET"])
@jwt_required()
def get_booking_list():
    """Get paginated list of bookings"""
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)
    query = select(Booking)
    
    # For non-admin users, only show their own bookings
    if current_user.role.name != "admin":
        query = query.where(Booking.user_id == current_user.id)
    
    # Add filters if provided
    if request.args.get("status"):
        try:
            status = Booking.Status(request.args.get("status"))
            query = query.where(Booking.status == status)
        except ValueError:
            return error_response("Invalid status value", 400)
    
    if request.args.get("equipment_id"):
        query = query.where(Booking.equipment_id == request.args.get("equipment_id", type=int))
    
    # Add date range filters
    if request.args.get("start_date"):
        query = query.where(Booking.start_date >= request.args.get("start_date"))
    if request.args.get("end_date"):
        query = query.where(Booking.end_date <= request.args.get("end_date"))
    
    return jsonify(Booking.to_collection_dict(
        query=query,
        page=page,
        per_page=per_page,
        endpoint="main.get_booking_list"
    )), 200


@api.route("/bookings/<int:booking_id>", methods=["GET"])
@jwt_required()
def get_booking(booking_id):
    """Get booking details"""
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return error_response("Booking not found", 404)
    
    # Ensure user can only access their own bookings or admin can see all
    if current_user.role.name != "admin" and booking.user_id != current_user.id:
        return error_response("Unauthorized access", 403)
    
    return jsonify(booking.to_dict()), 200


@api.route("/bookings", methods=["POST"])
@jwt_required()
def create_booking():
    """Create new booking"""
    if not request.is_json:
        return error_response("Missing JSON in request", 400)
    
    data = request.json
    
    required_fields = ["equipment_id", "start_date", "end_date", "distance_km"]
    
    if not all(field in data for field in required_fields):
        return error_response(f"Missing required fields: {', '.join(required_fields)}", 400)
    
    try:
        # Validate equipment exists and is available
        equipment = db.session.get(Equipment, data["equipment_id"])
        if not equipment:
            return error_response("Equipment not found", 404)
        
        if equipment.status != Equipment.Status.AVAILABLE:
            return error_response("Equipment is not available", 400)
        
        # Calculate booking amounts (simplified calculation)
        start_date = datetime.fromisoformat(data["start_date"])
        end_date = datetime.fromisoformat(data["end_date"])
        days = (end_date - start_date).days + 1
        rental_amount = equipment.price_per_day * days
        transport_amount = equipment.transport_cost_per_km * data["distance_km"]
        total_amount = rental_amount + transport_amount
        
        booking = Booking(
            user_id=current_user.id,
            equipment_id=data["equipment_id"],
            start_date=start_date,
            end_date=end_date,
            distance_km=data["distance_km"],
            rental_amount=rental_amount,
            transport_amount=transport_amount,
            total_amount=total_amount
        )
        
        # Update equipment status
        equipment.status = Equipment.Status.RENTED
        
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            "msg": "Booking created successfully",
            "booking": booking.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error creating booking: {str(e)}", 500)


@api.route("/bookings/<int:booking_id>", methods=["PUT"])
@jwt_required()
def update_booking(booking_id):
    """Update booking details"""
    if not request.is_json:
        return error_response("Missing JSON in request", 400)
    
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return error_response("Booking not found", 404)
    
    # Ensure user can only update their own bookings or admin can update any
    if current_user.role.name != "admin" and booking.user_id != current_user.id:
        return error_response("Unauthorized access", 403)
    
    data = request.json
    
    try:
        # Only allow updating certain fields based on booking status
        if booking.status in [Booking.Status.PENDING, Booking.Status.PAYMENT_REQUIRED]:
            allowed_fields = ["start_date", "end_date", "distance_km"]
            
            for field in allowed_fields:
                if field in data:
                    if field == "start_date" or field == "end_date":
                        setattr(booking, field, datetime.fromisoformat(data[field]))
                    else:
                        setattr(booking, field, data[field])
            
            # Recalculate amounts if dates or distance changed
            if "start_date" in data or "end_date" in data or "distance_km" in data:
                equipment = booking.equipment
                start_date = booking.start_date
                end_date = booking.end_date
                days = (end_date - start_date).days + 1
                rental_amount = equipment.price_per_day * days
                transport_amount = equipment.transport_cost_per_km * booking.distance_km
                booking.rental_amount = rental_amount
                booking.transport_amount = transport_amount
                booking.total_amount = rental_amount + transport_amount
        
        # Allow status updates for specific transitions
        if "status" in data:
            try:
                new_status = Booking.Status(data["status"])
                
                # Define valid status transitions
                status_transitions = {
                    Booking.Status.PENDING: [Booking.Status.PAYMENT_REQUIRED, Booking.Status.CANCELLED],
                    Booking.Status.PAYMENT_REQUIRED: [Booking.Status.CONFIRMED, Booking.Status.CANCELLED],
                    Booking.Status.CONFIRMED: [Booking.Status.COMPLETED, Booking.Status.CANCELLED]
                }
                
                # Check if status transition is valid
                if booking.status not in status_transitions or new_status not in status_transitions[booking.status]:
                    return error_response("Invalid status transition", 400)
                
                booking.status = new_status
                
                # Handle equipment status if booking is cancelled or completed
                if new_status == Booking.Status.CANCELLED or new_status == Booking.Status.COMPLETED:
                    booking.equipment.status = Equipment.Status.AVAILABLE
            except ValueError:
                return error_response("Invalid status value", 400)
        
        db.session.commit()
        return jsonify({
            "msg": "Booking updated successfully",
            "booking": booking.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error updating booking: {str(e)}", 500)


@api.route("/bookings/<int:booking_id>", methods=["DELETE"])
@jwt_required()
def delete_booking(booking_id):
    """Delete booking"""
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return error_response("Booking not found", 404)
    
    # Only allow deletion of pending or cancelled bookings
    if booking.status not in [Booking.Status.PENDING, Booking.Status.CANCELLED]:
        return error_response("Booking cannot be deleted in current status", 400)
    
    # Ensure user can only delete their own bookings or admin can delete any
    if current_user.role.name != "admin" and booking.user_id != current_user.id:
        return error_response("Unauthorized access", 403)
    
    try:
        # Set equipment back to available if not already
        if booking.equipment:
            booking.equipment.status = Equipment.Status.AVAILABLE
        
        db.session.delete(booking)
        db.session.commit()
        return jsonify({"msg": "Booking deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error deleting booking: {str(e)}", 500)

