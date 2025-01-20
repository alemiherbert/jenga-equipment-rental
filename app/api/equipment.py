"""
Equipment app routes
"""

from app import db
from app.api import api
from app.api.utils import error_response
from app.models import Equipment, Location
from config import Config
from flask import request, jsonify
from flask_jwt_extended import jwt_required, current_user
from sqlalchemy import select
from werkzeug.utils import secure_filename
import os
from flasgger import swag_from

# Todo: Delegate this to a CRON job
def update_all_featured_status():
    """Recalculate and update the featured status for all equipment."""
    equipment_list = db.session.query(Equipment).all()
    for equipment in equipment_list:
        equipment.update_featured_status()
    db.session.commit()


@api.route("/equipment", methods=["GET"])
@swag_from({
    'tags': ['Equipment'],
    'description': 'Get a paginated list of equipment',
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
            'default': 12
        },
        {
            'name': 'search',
            'in': 'query',
            'type': 'string',
            'description': 'Search term to filter equipment by name'
        },
        {
            'name': 'location',
            'in': 'query',
            'type': 'string',
            'description': 'Filter equipment by location name'
        },
        {
            'name': 'category',
            'in': 'query',
            'type': 'string',
            'description': 'Filter equipment by category'
        }
    ],
    'responses': {
        200: {
            'description': 'Paginated list of equipment',
            'examples': {
                'application/json': {
                    'items': [
                        {'id': 1, 'name': 'Excavator', 'category': 'Heavy Machinery', 'price_per_day': 500.0},
                        {'id': 2, 'name': 'Crane', 'category': 'Heavy Machinery', 'price_per_day': 700.0}
                    ],
                    'meta': {
                        'page': 1,
                        'per_page': 12,
                        'total_pages': 5,
                        'total_items': 60
                    }
                }
            }
        }
    }
})
def get_equipment_list():
    """Get paginated list of equipment"""
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 12, type=int), 100)
    query = select(Equipment).join(Equipment.location)
    update_all_featured_status()

    if request.args.get("search"):
        search = f"%{request.args.get('search')}%"
        query = query.where(Equipment.name.ilike(search))
    
    if request.args.get("location"):
        query = query.where(Location.name == request.args.get("location"))
    
    if request.args.get("category"):
        query = query.where(Equipment.category == request.args.get("category"))
        
    return jsonify(Equipment.to_collection_dict(
        query=query,
        page=page,
        per_page=per_page,
        endpoint="api.get_equipment_list"
    )), 200


@api.route("/equipment/featured", methods=["GET"])
@swag_from({
    'tags': ['Equipment'],
    'description': 'Get a list of featured equipment',
    'responses': {
        200: {
            'description': 'List of featured equipment',
            'examples': {
                'application/json': {
                    'featured_equipment': [
                        {'id': 1, 'name': 'Excavator', 'category': 'Heavy Machinery', 'price_per_day': 500.0},
                        {'id': 2, 'name': 'Crane', 'category': 'Heavy Machinery', 'price_per_day': 700.0}
                    ]
                }
            }
        }
    }
})
def get_featured_equipment():
    """Get a list of featured equipment."""
    query = select(Equipment).where(Equipment.featured == True)
    featured_equipment = db.session.execute(query).scalars().all()
    return jsonify({
        "featured_equipment": [equipment.to_dict() for equipment in featured_equipment]
    }), 200


@api.route("/equipment/<int:equipment_id>", methods=["GET"])
@swag_from({
    'tags': ['Equipment'],
    'description': 'Get details of a specific equipment',
    'parameters': [
        {
            'name': 'equipment_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the equipment to retrieve'
        }
    ],
    'responses': {
        200: {
            'description': 'Equipment details',
            'examples': {
                'application/json': {
                    'id': 1,
                    'name': 'Excavator',
                    'category': 'Heavy Machinery',
                    'price_per_day': 500.0,
                    'transport_cost_per_km': 50.0,
                    'location_id': 1,
                    'image': 'excavator_1.jpg'
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
        }
    }
})
def get_equipment(equipment_id):
    """Get equipment details"""
    equipment = db.session.get(Equipment, equipment_id)
    if not equipment:
        return error_response("Equipment not found", 404)
    
    return jsonify(equipment.to_dict()), 200


@api.route("/equipment", methods=["POST"])
@jwt_required()
@swag_from({
    'tags': ['Equipment'],
    'description': 'Create new equipment',
    'security': [{'BearerAuth': []}],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'Excavator'},
                    'category': {'type': 'string', 'example': 'Heavy Machinery'},
                    'price_per_day': {'type': 'number', 'example': 500.0},
                    'transport_cost_per_km': {'type': 'number', 'example': 50.0},
                    'location_id': {'type': 'integer', 'example': 1},
                    'image': {'type': 'string', 'format': 'binary', 'description': 'Image file'}
                },
                'required': ['name', 'category', 'location_id']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Equipment created successfully',
            'examples': {
                'application/json': {
                    'msg': 'Equipment created successfully',
                    'equipment': {
                        'id': 1,
                        'name': 'Excavator',
                        'category': 'Heavy Machinery',
                        'price_per_day': 500.0,
                        'transport_cost_per_km': 50.0,
                        'location_id': 1,
                        'image': 'excavator_1.jpg'
                    }
                }
            }
        },
        400: {
            'description': 'Missing form data or required fields',
            'examples': {
                'application/json': {
                    'msg': 'Missing required fields: name, category, location_id'
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
        500: {
            'description': 'Error creating equipment',
            'examples': {
                'application/json': {
                    'msg': 'Error creating equipment',
                    'error': 'Some error message'
                }
            }
        }
    }
})
def create_equipment():
    """Create new equipment"""
    if current_user.role != "admin":
        return error_response("Unauthorized access", 403)
    
    if not request.form and not request.files:
        return error_response("Missing form data or file in request", 400)
    
    data = request.form
    image_file = request.files.get('image')

    # Handle file upload
    if image_file:
        if image_file.content_length > Config.MAX_CONTENT_LENGTH:
            return error_response("File size must not exceed 5 MB", 400)
        
        # Save the file temporarily
        temp_filename = secure_filename(image_file.filename)
        temp_image_path = os.path.join(Config.UPLOAD_FOLDER, temp_filename)
        image_file.save(temp_image_path)
    else:
        temp_image_path = None

    required_fields = ["name", "category", "location_id"]
    
    if not all(field in data for field in required_fields):
        return error_response(f"Missing required fields: {', '.join(required_fields)}", 400)
    
    try:
        price_per_day = float(data.get("price_per_day", 0))
        transport_cost_per_km = float(data.get("transport_cost_per_km", 0))

        # Create the equipment without the image URL initially
        equipment = Equipment(
            name=data["name"],
            category=data["category"],
            price_per_day=price_per_day,
            transport_cost_per_km=transport_cost_per_km,
            location_id=int(data["location_id"]),
            image=None
        )
        db.session.add(equipment)
        db.session.commit()

        if temp_image_path:
            equipment_name = data["name"].replace(" ", "_").lower()
            file_extension = os.path.splitext(temp_filename)[1]
            new_filename = f"{equipment_name}{equipment.id}{file_extension}"
            new_image_path = os.path.join(Config.UPLOAD_FOLDER, new_filename)

            os.rename(temp_image_path, new_image_path)

            equipment.image = new_filename
            db.session.commit()

        return jsonify({
            "msg": "Equipment created successfully",
            "equipment": equipment.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        if temp_image_path and os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        return error_response(f"Error creating equipment: {str(e)}", 500)


@api.route("/equipment/<int:equipment_id>", methods=["PUT"])
@jwt_required()
@swag_from({
    'tags': ['Equipment'],
    'description': 'Update equipment details',
    'security': [{'BearerAuth': []}],
    'parameters': [
        {
            'name': 'equipment_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the equipment to update'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'example': 'Excavator'},
                    'category': {'type': 'string', 'example': 'Heavy Machinery'},
                    'price_per_day': {'type': 'number', 'example': 500.0},
                    'transport_cost_per_km': {'type': 'number', 'example': 50.0},
                    'location_id': {'type': 'integer', 'example': 1},
                    'image': {'type': 'string', 'format': 'binary', 'description': 'Image file'}
                },
                'required': ['name', 'category', 'location_id']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Equipment updated successfully',
            'examples': {
                'application/json': {
                    'msg': 'Equipment updated successfully',
                    'equipment': {
                        'id': 1,
                        'name': 'Excavator',
                        'category': 'Heavy Machinery',
                        'price_per_day': 500.0,
                        'transport_cost_per_km': 50.0,
                        'location_id': 1,
                        'image': 'excavator_1.jpg'
                    }
                }
            }
        },
        400: {
            'description': 'Missing form data or required fields',
            'examples': {
                'application/json': {
                    'msg': 'Missing required fields: name, category, location_id'
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
            'description': 'Error updating equipment',
            'examples': {
                'application/json': {
                    'msg': 'Error updating equipment',
                    'error': 'Some error message'
                }
            }
        }
    }
})
def update_equipment(equipment_id):
    """Update equipment details"""
    if current_user.role != "admin":
        return error_response("Unauthorized access", 403)
    
    equipment = db.session.get(Equipment, equipment_id)
    if not equipment:
        return error_response("Equipment not found", 404)
    
    data = request.form
    image_file = request.files.get('image')

    # Handle file upload
    if image_file:
        if image_file.content_length > Config.MAX_CONTENT_LENGTH:
            return error_response("File size must not exceed 5 MB", 400)
        
        # Save the file temporarily
        temp_filename = secure_filename(image_file.filename)
        temp_image_path = os.path.join(Config.UPLOAD_FOLDER, temp_filename)
        image_file.save(temp_image_path)
    else:
        temp_image_path = None

    required_fields = ["name", "category", "location_id"]
    
    if not all(field in data for field in required_fields):
        return error_response(f"Missing required fields: {', '.join(required_fields)}", 400)
    
    try:
        equipment.name = data["name"]
        equipment.category = data["category"]
        equipment.location_id = int(data["location_id"])
        equipment.price_per_day = float(data.get("price_per_day", 0))
        equipment.transport_cost_per_km = float(data.get("transport_cost_per_km", 0))

        if temp_image_path:
            equipment_name = data["name"].replace(" ", "_").lower()
            file_extension = os.path.splitext(temp_filename)[1]
            new_filename = f"{equipment_name}{equipment.id}{file_extension}"
            new_image_path = os.path.join(Config.UPLOAD_FOLDER, new_filename)

            os.rename(temp_image_path, new_image_path)

            if equipment.image and os.path.exists(os.path.join(Config.UPLOAD_FOLDER, equipment.image)):
                os.remove(os.path.join(Config.UPLOAD_FOLDER, equipment.image))

            equipment.image = new_filename

        db.session.commit()
        return jsonify({
            "msg": "Equipment updated successfully",
            "equipment": equipment.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        if temp_image_path and os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        return error_response(f"Error updating equipment: {str(e)}", 500)


@api.route("/equipment/<int:equipment_id>", methods=["DELETE"])
@jwt_required()
@swag_from({
    'tags': ['Equipment'],
    'description': 'Delete equipment',
    'security': [{'BearerAuth': []}],
    'parameters': [
        {
            'name': 'equipment_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the equipment to delete'
        }
    ],
    'responses': {
        200: {
            'description': 'Equipment deleted successfully',
            'examples': {
                'application/json': {
                    'msg': 'Equipment deleted successfully'
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
            'description': 'Error deleting equipment',
            'examples': {
                'application/json': {
                    'msg': 'Error deleting equipment',
                    'error': 'Some error message'
                }
            }
        }
    }
})
def delete_equipment(equipment_id):
    """Delete equipment"""
    if current_user.role != "admin":
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
