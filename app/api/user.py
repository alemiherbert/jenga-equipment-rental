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
from flasgger import swag_from


@api.route("/users", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Users'],
    'description': 'Get a paginated list of users (Admin only)',
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
            'description': 'Filter users by status (e.g., ACTIVE, INACTIVE)'
        }
    ],
    'responses': {
        200: {
            'description': 'Paginated list of users',
            'examples': {
                'application/json': {
                    'items': [
                        {
                            'id': 1,
                            'name': 'John Doe',
                            'email': 'john@example.com',
                            'phone': '+256700000000',
                            'company': 'Example Corp',
                            'status': 'ACTIVE'
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
            'description': 'Invalid status value',
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
def get_users():
    """Get paginated list of users"""
    if current_user.role != "admin":
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
@swag_from({
    'tags': ['Users'],
    'description': 'Get details of the current user',
    'security': [{'BearerAuth': []}],
    'responses': {
        200: {
            'description': 'Current user details',
            'examples': {
                'application/json': {
                    'id': 1,
                    'name': 'John'
                }
            }
        }
    }
})
def get_self():
    """Return the current user"""
    return jsonify({
        "id": current_user.id,
        "name": current_user.name.split()[0]
    })


@api.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Users'],
    'description': 'Get details of a specific user',
    'security': [{'BearerAuth': []}],
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the user to retrieve'
        }
    ],
    'responses': {
        200: {
            'description': 'User details',
            'examples': {
                'application/json': {
                    'id': 1,
                    'name': 'John Doe',
                    'email': 'john@example.com',
                    'phone': '+256700000000',
                    'company': 'Example Corp',
                    'status': 'ACTIVE'
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
            'description': 'User not found',
            'examples': {
                'application/json': {
                    'msg': 'User not found'
                }
            }
        }
    }
})
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
@swag_from({
    'tags': ['Users'],
    'description': 'Update user details',
    'security': [{'BearerAuth': []}],
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the user to update'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'John Doe'},
                    'phone': {'type': 'string', 'example': '+256700000000'},
                    'company': {'type': 'string', 'example': 'Example Corp'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'User updated successfully',
            'examples': {
                'application/json': {
                    'msg': 'User updated successfully',
                    'user': {
                        'id': 1,
                        'name': 'John Doe',
                        'email': 'john@example.com',
                        'phone': '+256700000000',
                        'company': 'Example Corp',
                        'status': 'ACTIVE'
                    }
                }
            }
        },
        400: {
            'description': 'Missing JSON in request or invalid data',
            'examples': {
                'application/json': {
                    'msg': 'Missing JSON in request'
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
            'description': 'User not found',
            'examples': {
                'application/json': {
                    'msg': 'User not found'
                }
            }
        },
        500: {
            'description': 'Error updating user',
            'examples': {
                'application/json': {
                    'msg': 'Error updating user',
                    'error': 'Some error message'
                }
            }
        }
    }
})
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
