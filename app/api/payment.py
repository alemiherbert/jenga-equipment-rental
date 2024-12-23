"""
Payment app routes
"""
from app import db
from app.api import api
from app.api.utils import error_response
from app.models import Payment, Booking
from flask import request, jsonify
from flask_jwt_extended import jwt_required, current_user
from sqlalchemy import select
from datetime import datetime

@api.route("/payments", methods=["GET"])
@jwt_required()
def get_payment_list():
    """Get paginated list of payments"""
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)
    query = select(Payment)
    
    # For non-admin users, only show their own payments
    if current_user.role.name != "admin":
        query = query.where(Payment.user_id == current_user.id)
    
    # Add filters if provided
    if request.args.get("status"):
        try:
            status = Payment.Status(request.args.get("status"))
            query = query.where(Payment.status == status)
        except ValueError:
            return error_response("Invalid status value", 400)
    
    if request.args.get("booking_id"):
        query = query.where(Payment.booking_id == request.args.get("booking_id", type=int))
    
    # Add amount range filters
    if request.args.get("min_amount"):
        query = query.where(Payment.total_amount >= float(request.args.get("min_amount")))
    if request.args.get("max_amount"):
        query = query.where(Payment.total_amount <= float(request.args.get("max_amount")))
    
    # Add date range filters
    if request.args.get("start_date"):
        query = query.where(Payment.created_at >= datetime.fromisoformat(request.args.get("start_date")))
    if request.args.get("end_date"):
        query = query.where(Payment.created_at <= datetime.fromisoformat(request.args.get("end_date")))
    
    return jsonify(Payment.to_collection_dict(
        query=query,
        page=page,
        per_page=per_page,
        endpoint="main.get_payment_list"
    )), 200


@api.route("/payments/<int:payment_id>", methods=["GET"])
@jwt_required()
def get_payment(payment_id):
    """Get payment details"""
    payment = db.session.get(Payment, payment_id)
    if not payment:
        return error_response("Payment not found", 404)
    
    # Ensure user can only access their own payments or admin can see all
    if current_user.role.name != "admin" and payment.user_id != current_user.id:
        return error_response("Unauthorized access", 403)
    
    return jsonify(payment.to_dict()), 200


@api.route("/payments", methods=["POST"])
@jwt_required()
def create_payment():
    """Create new payment"""
    if not request.is_json:
        return error_response("Missing JSON in request", 400)
    
    data = request.json
    
    required_fields = ["booking_id", "rental_amount", "transport_amount", "total_amount"]
    
    if not all(field in data for field in required_fields):
        return error_response(f"Missing required fields: {', '.join(required_fields)}", 400)
    
    try:
        # Validate booking exists and is in a state that allows payment
        booking = db.session.get(Booking, data["booking_id"])
        if not booking:
            return error_response("Booking not found", 404)
        
        # Check booking status and user
        if booking.status not in [Booking.Status.PAYMENT_REQUIRED, Booking.Status.PENDING]:
            return error_response("Booking is not eligible for payment", 400)
        
        if current_user.role.name != "admin" and booking.user_id != current_user.id:
            return error_response("Unauthorized access", 403)
        
        payment = Payment(
            booking_id=data["booking_id"],
            user_id=current_user.id,
            rental_amount=data["rental_amount"],
            transport_amount=data["transport_amount"],
            total_amount=data["total_amount"],
            currency=data.get("currency", "UGX"),
            stripe_payment_intent_id=data.get("stripe_payment_intent_id"),
            stripe_payment_method_id=data.get("stripe_payment_method_id")
        )
        
        # Update booking status
        booking.status = Booking.Status.CONFIRMED
        
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            "msg": "Payment created successfully",
            "payment": payment.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error creating payment: {str(e)}", 500)


@api.route("/payments/<int:payment_id>", methods=["PUT"])
@jwt_required()
def update_payment(payment_id):
    """Update payment details"""
    if not request.is_json:
        return error_response("Missing JSON in request", 400)
    
    payment = db.session.get(Payment, payment_id)
    if not payment:
        return error_response("Payment not found", 404)
    
    # Ensure only admin can update payments
    if current_user.role.name != "admin":
        return error_response("Unauthorized access", 403)
    
    data = request.json
    
    try:
        # Allow updating status and Stripe-related fields
        allowed_fields = ["status", "stripe_payment_intent_id", "stripe_payment_method_id"]
        
        for field in allowed_fields:
            if field in data:
                if field == "status":
                    try:
                        payment.status = Payment.Status(data["status"])
                    except ValueError:
                        return error_response("Invalid status value", 400)
                else:
                    setattr(payment, field, data[field])
        
        db.session.commit()
        return jsonify({
            "msg": "Payment updated successfully",
            "payment": payment.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error updating payment: {str(e)}", 500)


@api.route("/payments/<int:payment_id>", methods=["DELETE"])
@jwt_required()
def delete_payment(payment_id):
    """Delete payment"""
    if current_user.role.name != "admin":
        return error_response("Unauthorized access", 403)
    
    payment = db.session.get(Payment, payment_id)
    if not payment:
        return error_response("Payment not found", 404)
    
    try:
        # Only allow deletion of pending or failed payments
        if payment.status not in [Payment.Status.PENDING, Payment.Status.FAILED]:
            return error_response("Payment cannot be deleted in current status", 400)
        
        db.session.delete(payment)
        db.session.commit()
        return jsonify({"msg": "Payment deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error deleting payment: {str(e)}", 500)
