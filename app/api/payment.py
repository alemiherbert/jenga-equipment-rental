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
from werkzeug.exceptions import HTTPException
import requests
from flasgger import swag_from


# PESA Pay API configuration
PESA_PAY_API_URL = "http://localhost:8000/v1/payments"
PESA_PAY_API_KEY = "sk_test_123"


@api.route("/payments", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Payments'],
    'description': 'Get a paginated list of payments',
    'security': [{'BearerAuth': []}],
    'parameters': [
        {
            'name': 'page',
            'in': 'query',
            'type': 'integer',
            'description': 'Page number for pagination',
            'default': 1
        },
        {
            'name': 'per_page',
            'in': 'query',
            'type': 'integer',
            'description': 'Number of items per page (max 100)',
            'default': 10
        },
        {
            'name': 'status',
            'in': 'query',
            'type': 'string',
            'description': 'Filter payments by status (e.g., PENDING, SUCCESS, FAILED)'
        },
        {
            'name': 'booking_id',
            'in': 'query',
            'type': 'integer',
            'description': 'Filter payments by booking ID'
        },
        {
            'name': 'min_amount',
            'in': 'query',
            'type': 'number',
            'description': 'Filter payments by minimum amount'
        },
        {
            'name': 'max_amount',
            'in': 'query',
            'type': 'number',
            'description': 'Filter payments by maximum amount'
        },
        {
            'name': 'start_date',
            'in': 'query',
            'type': 'string',
            'format': 'date-time',
            'description': 'Filter payments by start date (ISO format)'
        },
        {
            'name': 'end_date',
            'in': 'query',
            'type': 'string',
            'format': 'date-time',
            'description': 'Filter payments by end date (ISO format)'
        }
    ],
    'responses': {
        200: {
            'description': 'Paginated list of payments',
            'examples': {
                'application/json': {
                    'items': [
                        {
                            'id': 1,
                            'user_id': 1,
                            'total_amount': 500.0,
                            'currency': 'UGX',
                            'status': 'SUCCESS'
                        }
                    ],
                    'meta': {
                        'page': 1,
                        'per_page': 10,
                        'total_pages': 5,
                        'total_items': 50
                    }
                }
            }
        },
        400: {
            'description': 'Invalid status value or other validation errors',
            'examples': {
                'application/json': {
                    'msg': 'Invalid status value'
                }
            }
        },
        403: {
            'description': 'Unauthorized access',
            'examples': {
                'application/json': {
                    'msg': 'Unauthorized access'
                }
            }
        }
    }
})
def get_payment_list():
    """Get paginated list of payments"""
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)
    query = select(Payment)
    
    # For non-admin users, only show their own payments
    if current_user.role != "admin":
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
        endpoint="api.get_payment_list"
    )), 200


@api.route("/payments/<int:payment_id>", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Payments'],
    'description': 'Get details of a specific payment',
    'security': [{'BearerAuth': []}],
    'parameters': [
        {
            'name': 'payment_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the payment to retrieve'
        }
    ],
    'responses': {
        200: {
            'description': 'Payment details',
            'examples': {
                'application/json': {
                    'id': 1,
                    'user_id': 1,
                    'total_amount': 500.0,
                    'currency': 'UGX',
                    'status': 'SUCCESS'
                }
            }
        },
        403: {
            'description': 'Unauthorized access',
            'examples': {
                'application/json': {
                    'msg': 'Unauthorized access'
                }
            }
        },
        404: {
            'description': 'Payment not found',
            'examples': {
                'application/json': {
                    'msg': 'Payment not found'
                }
            }
        }
    }
})
def get_payment(payment_id):
    """Get payment details"""
    payment = db.session.get(Payment, payment_id)
    if not payment:
        return error_response("Payment not found", 404)
    
    # Ensure user can only access their own payments or admin can see all
    if current_user.role != "admin" and payment.user_id != current_user.id:
        return error_response("Unauthorized access", 403)
    
    return jsonify(payment.to_dict()), 200


@api.route("/payments", methods=["POST"])
@jwt_required()
@swag_from({
    'tags': ['Payments'],
    'description': 'Create a new payment',
    'security': [{'BearerAuth': []}],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'booking_ids': {
                        'type': 'array',
                        'items': {'type': 'integer'},
                        'example': [1, 2],
                        'description': 'List of booking IDs to pay for'
                    },
                    'total_amount': {
                        'type': 'number',
                        'example': 500.0,
                        'description': 'Total amount to pay'
                    },
                    'billing': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string', 'example': 'John Doe'},
                            'email': {'type': 'string', 'example': 'john@example.com'},
                            'phone': {'type': 'string', 'example': '+256700000000'}
                        },
                        'required': ['name', 'email', 'phone']
                    },
                    'card_details': {
                        'type': 'object',
                        'properties': {
                            'number': {'type': 'string', 'example': '4242424242424242'},
                            'exp_month': {'type': 'integer', 'example': 12},
                            'exp_year': {'type': 'integer', 'example': 2025},
                            'cvc': {'type': 'string', 'example': '123'}
                        },
                        'required': ['number', 'exp_month', 'exp_year', 'cvc']
                    }
                },
                'required': ['booking_ids', 'total_amount', 'billing', 'card_details']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Payment created successfully',
            'examples': {
                'application/json': {
                    'msg': 'Payment created successfully',
                    'payment': {
                        'id': 1,
                        'user_id': 1,
                        'total_amount': 500.0,
                        'currency': 'UGX',
                        'status': 'SUCCESS'
                    }
                }
            }
        },
        400: {
            'description': 'Missing required fields or invalid data',
            'examples': {
                'application/json': {
                    'msg': 'Missing required fields: booking_ids, total_amount, billing, card_details'
                }
            }
        },
        403: {
            'description': 'Unauthorized access',
            'examples': {
                'application/json': {
                    'msg': 'Unauthorized access'
                }
            }
        },
        404: {
            'description': 'Booking not found',
            'examples': {
                'application/json': {
                    'msg': 'Booking not found'
                }
            }
        },
        500: {
            'description': 'Error creating payment',
            'examples': {
                'application/json': {
                    'msg': 'Error creating payment',
                    'error': 'Some error message'
                }
            }
        }
    }
})
def create_payment():
    """Create new payment"""
    if not request.is_json:
        return error_response("Missing JSON in request", 400)
    
    data = request.json
    
    # Required fields
    required_fields = ["booking_ids", "total_amount", "billing", "card_details"]
    if not all(field in data for field in required_fields):
        return error_response(f"Missing required fields: {', '.join(required_fields)}", 400)
    
    try:
        # Validate bookings exist and are eligible for payment
        bookings = Booking.query.filter(Booking.id.in_(data["booking_ids"])).all()
        if len(bookings) != len(data["booking_ids"]):
            return error_response("One or more bookings not found", 404)
        
        for booking in bookings:
            if booking.status not in [Booking.Status.PAYMENT_REQUIRED, Booking.Status.PENDING]:
                return error_response("One or more bookings are not eligible for payment", 400)
        
        # Prepare payment request for PESA Pay API
        payment_request = {
            "amount": data["total_amount"],
            "currency": "UGX",
            "description": f"Payment for bookings {', '.join(map(str, data['booking_ids']))}",
            "metadata": {
                "booking_ids": data["booking_ids"],
                "total_amount": data["total_amount"]
            },
            "card_details": data["card_details"]
        }
        
        # Call PESA Pay API
        headers = {
            "X-API-Key": PESA_PAY_API_KEY,
            "Content-Type": "application/json"
        }
        response = requests.post(PESA_PAY_API_URL, json=payment_request, headers=headers)
        
        # Handle PESA Pay API response
        if response.status_code != 201:
            error_detail = response.json().get("detail", "Payment failed")
            raise HTTPException(description=error_detail)
        
        payment_result = response.json()
        
        # Create payment record in database
        payment = Payment(
            user_id=current_user.id,
            total_amount=data["total_amount"],
            currency="UGX",
            status=Payment.Status(payment_result["status"]),
            payment_reference=payment_result["id"]
        )
        
        # Update booking statuses
        for booking in bookings:
            booking.status = Booking.Status.CONFIRMED
        
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            "msg": "Payment created successfully",
            "payment": payment.to_dict()
        }), 201
    except HTTPException as e:
        db.session.rollback()
        return error_response(str(e.description), e.code)
    except Exception as e:
        db.session.rollback()
        print(e)
        return error_response(f"Error creating payment: {str(e)}", 500)


@api.route("/payments/<int:payment_id>", methods=["PUT"])
@jwt_required()
@swag_from({
    'tags': ['Payments'],
    'description': 'Update payment details',
    'security': [{'BearerAuth': []}],
    'parameters': [
        {
            'name': 'payment_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the payment to update'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'example': 'SUCCESS'},
                    'stripe_payment_intent_id': {'type': 'string', 'example': 'pi_123'},
                    'stripe_payment_method_id': {'type': 'string', 'example': 'pm_123'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Payment updated successfully',
            'examples': {
                'application/json': {
                    'msg': 'Payment updated successfully',
                    'payment': {
                        'id': 1,
                        'user_id': 1,
                        'total_amount': 500.0,
                        'currency': 'UGX',
                        'status': 'SUCCESS'
                    }
                }
            }
        },
        400: {
            'description': 'Invalid status value or other validation errors',
            'examples': {
                'application/json': {
                    'msg': 'Invalid status value'
                }
            }
        },
        403: {
            'description': 'Unauthorized access',
            'examples': {
                'application/json': {
                    'msg': 'Unauthorized access'
                }
            }
        },
        404: {
            'description': 'Payment not found',
            'examples': {
                'application/json': {
                    'msg': 'Payment not found'
                }
            }
        },
        500: {
            'description': 'Error updating payment',
            'examples': {
                'application/json': {
                    'msg': 'Error updating payment',
                    'error': 'Some error message'
                }
            }
        }
    }
})
def update_payment(payment_id):
    """Update payment details"""
    if not request.is_json:
        return error_response("Missing JSON in request", 400)
    
    payment = db.session.get(Payment, payment_id)
    if not payment:
        return error_response("Payment not found", 404)
    
    # Ensure only admin can update payments
    if current_user.role != "admin":
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
@swag_from({
    'tags': ['Payments'],
    'description': 'Delete a payment',
    'security': [{'BearerAuth': []}],
    'parameters': [
        {
            'name': 'payment_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the payment to delete'
        }
    ],
    'responses': {
        200: {
            'description': 'Payment deleted successfully',
            'examples': {
                'application/json': {
                    'msg': 'Payment deleted successfully'
                }
            }
        },
        400: {
            'description': 'Payment cannot be deleted in current status',
            'examples': {
                'application/json': {
                    'msg': 'Payment cannot be deleted in current status'
                }
            }
        },
        403: {
            'description': 'Unauthorized access',
            'examples': {
                'application/json': {
                    'msg': 'Unauthorized access'
                }
            }
        },
        404: {
            'description': 'Payment not found',
            'examples': {
                'application/json': {
                    'msg': 'Payment not found'
                }
            }
        },
        500: {
            'description': 'Error deleting payment',
            'examples': {
                'application/json': {
                    'msg': 'Error deleting payment',
                    'error': 'Some error message'
                }
            }
        }
    }
})
def delete_payment(payment_id):
    """Delete payment"""
    if current_user.role != "admin":
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
