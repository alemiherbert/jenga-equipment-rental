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
from flasgger import swag_from


@api.route("/bookings", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Bookings'],
    'description': 'Get a paginated list of bookings',
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
            'description': 'Filter bookings by status (e.g., PENDING, CONFIRMED, CANCELLED)'
        },
        {
            'name': 'equipment_id',
            'in': 'query',
            'type': 'integer',
            'description': 'Filter bookings by equipment ID'
        },
        {
            'name': 'start_date',
            'in': 'query',
            'type': 'string',
            'format': 'date',
            'description': 'Filter bookings by start date (ISO format)'
        },
        {
            'name': 'end_date',
            'in': 'query',
            'type': 'string',
            'format': 'date',
            'description': 'Filter bookings by end date (ISO format)'
        }
    ],
    'responses': {
        200: {
            'description': 'Paginated list of bookings',
            'examples': {
                'application/json': {
                    'items': [
                        {
                            'id': 1,
                            'user_id': 1,
                            'equipment_id': 1,
                            'start_date': '2023-10-01T00:00:00',
                            'end_date': '2023-10-05T00:00:00',
                            'status': 'CONFIRMED'
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
def get_booking_list():
    """Get paginated list of bookings"""
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)
    query = select(Booking)
    
    # For non-admin users, only show their own bookings
    if current_user.role != "admin":
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
        endpoint="api.get_booking_list"
    )), 200


@api.route("/bookings/<int:booking_id>", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Bookings'],
    'description': 'Get details of a specific booking',
    'security': [{'BearerAuth': []}],
    'parameters': [
        {
            'name': 'booking_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the booking to retrieve'
        }
    ],
    'responses': {
        200: {
            'description': 'Booking details',
            'examples': {
                'application/json': {
                    'id': 1,
                    'user_id': 1,
                    'equipment_id': 1,
                    'start_date': '2023-10-01T00:00:00',
                    'end_date': '2023-10-05T00:00:00',
                    'status': 'CONFIRMED'
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
        }
    }
})
def get_booking(booking_id):
    """Get booking details"""
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return error_response("Booking not found", 404)
    
    # Ensure user can only access their own bookings or admin can see all
    if current_user.role != "admin" and booking.user_id != current_user.id:
        return error_response("Unauthorized access", 403)
    
    return jsonify(booking.to_dict()), 200


@api.route("/bookings", methods=["POST"])
@jwt_required()
@swag_from({
    'tags': ['Bookings'],
    'description': 'Create new booking(s)',
    'security': [{'BearerAuth': []}],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'bookings': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'equipment_id': {'type': 'integer', 'example': 1},
                                'start_date': {'type': 'string', 'format': 'date-time', 'example': '2023-10-01T00:00:00'},
                                'end_date': {'type': 'string', 'format': 'date-time', 'example': '2023-10-05T00:00:00'},
                                'distance_km': {'type': 'number', 'example': 50.0}
                            },
                            'required': ['equipment_id', 'start_date', 'end_date']
                        }
                    }
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Bookings created successfully',
            'examples': {
                'application/json': {
                    'msg': 'Bookings created successfully',
                    'bookings': [
                        {
                            'id': 1,
                            'user_id': 1,
                            'equipment_id': 1,
                            'start_date': '2023-10-01T00:00:00',
                            'end_date': '2023-10-05T00:00:00',
                            'status': 'PENDING'
                        }
                    ]
                }
            }
        },
        400: {
            'description': 'Missing required fields or invalid data',
            'examples': {
                'application/json': {
                    'msg': 'Missing required fields: equipment_id, start_date, end_date'
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
            'description': 'Equipment not found',
            'examples': {
                'application/json': {
                    'msg': 'Equipment not found'
                }
            }
        },
        500: {
            'description': 'Error creating bookings',
            'examples': {
                'application/json': {
                    'msg': 'Error creating bookings',
                    'error': 'Some error message'
                }
            }
        }
    }
})
def create_booking():
    """Create new booking(s)"""
    if not request.is_json:
        return error_response("Missing JSON in request", 400)
    
    data = request.json
    
    # Check if the request contains a single booking or multiple bookings
    if "bookings" in data and isinstance(data["bookings"], list):
        # Handle multiple bookings
        bookings_data = data["bookings"]
    else:
        # Handle single booking
        bookings_data = [data]
    
    try:
        bookings = []
        for booking_data in bookings_data:
            # Validate required fields for each booking
            required_fields = ["equipment_id", "start_date", "end_date"]
            if not all(field in booking_data for field in required_fields):
                return error_response(f"Missing required fields in one or more bookings: {', '.join(required_fields)}", 400)
            
            # Validate equipment exists and is available
            equipment = Equipment.query.get(booking_data["equipment_id"])
            if not equipment:
                return error_response(f"Equipment not found: {booking_data['equipment_id']}", 404)
            
            if equipment.status != Equipment.Status.AVAILABLE:
                return error_response(f"Equipment is not available: {booking_data['equipment_id']}", 400)
            
            # Calculate booking amounts
            start_date = datetime.fromisoformat(booking_data["start_date"])
            end_date = datetime.fromisoformat(booking_data["end_date"])
            days = (end_date - start_date).days + 1
            rental_amount = equipment.price_per_day * days
            transport_amount = 100_000  # Flat rate for now
            total_amount = rental_amount + transport_amount
            
            # Create booking
            booking = Booking(
                user_id=current_user.id,
                equipment_id=booking_data["equipment_id"],
                start_date=start_date,
                end_date=end_date,
                distance_km=booking_data.get("distance_km", 0),
                rental_amount=rental_amount,
                transport_amount=transport_amount,
                total_amount=total_amount
            )
            
            # Update equipment status
            equipment.status = Equipment.Status.RENTED
            
            db.session.add(booking)
            bookings.append(booking)
        
        db.session.commit()
        
        return jsonify({
            "msg": "Bookings created successfully",
            "bookings": [booking.to_dict() for booking in bookings]
        }), 201
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error creating bookings: {str(e)}", 500)


@api.route("/bookings/<int:booking_id>", methods=["PUT"])
@jwt_required()
@swag_from({
    'tags': ['Bookings'],
    'description': 'Update booking details',
    'security': [{'BearerAuth': []}],
    'parameters': [
        {
            'name': 'booking_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the booking to update'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'start_date': {'type': 'string', 'format': 'date-time', 'example': '2023-10-01T00:00:00'},
                    'end_date': {'type': 'string', 'format': 'date-time', 'example': '2023-10-05T00:00:00'},
                    'distance_km': {'type': 'number', 'example': 50.0},
                    'status': {'type': 'string', 'example': 'CONFIRMED'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Booking updated successfully',
            'examples': {
                'application/json': {
                    'msg': 'Booking updated successfully',
                    'booking': {
                        'id': 1,
                        'user_id': 1,
                        'equipment_id': 1,
                        'start_date': '2023-10-01T00:00:00',
                        'end_date': '2023-10-05T00:00:00',
                        'status': 'CONFIRMED'
                    }
                }
            }
        },
        400: {
            'description': 'Invalid status transition or other validation errors',
            'examples': {
                'application/json': {
                    'msg': 'Invalid status transition'
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
            'description': 'Error updating booking',
            'examples': {
                'application/json': {
                    'msg': 'Error updating booking',
                    'error': 'Some error message'
                }
            }
        }
    }
})
def update_booking(booking_id):
    """Update booking details"""
    if not request.is_json:
        return error_response("Missing JSON in request", 400)
    
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return error_response("Booking not found", 404)
    
    # Ensure user can only update their own bookings or admin can update any
    if current_user.role != "admin" and booking.user_id != current_user.id:
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
@swag_from({
    'tags': ['Bookings'],
    'description': 'Delete a booking',
    'security': [{'BearerAuth': []}],
    'parameters': [
        {
            'name': 'booking_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the booking to delete'
        }
    ],
    'responses': {
        200: {
            'description': 'Booking deleted successfully',
            'examples': {
                'application/json': {
                    'msg': 'Booking deleted successfully'
                }
            }
        },
        400: {
            'description': 'Booking cannot be deleted in current status',
            'examples': {
                'application/json': {
                    'msg': 'Booking cannot be deleted in current status'
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
            'description': 'Error deleting booking',
            'examples': {
                'application/json': {
                    'msg': 'Error deleting booking',
                    'error': 'Some error message'
                }
            }
        }
    }
})
def delete_booking(booking_id):
    """Delete booking"""
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return error_response("Booking not found", 404)
    
    # Only allow deletion of pending or cancelled bookings
    if booking.status not in [Booking.Status.PENDING, Booking.Status.CANCELLED]:
        return error_response("Booking cannot be deleted in current status", 400)
    
    # Ensure user can only delete their own bookings or admin can delete any
    if current_user.role != "admin" and booking.user_id != current_user.id:
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
