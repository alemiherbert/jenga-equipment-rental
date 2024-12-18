from flask import jsonify, request
import validators

def error_response(message, status_code):
    """
    Helper function to return error responses.
    """
    return jsonify({"msg": message}), status_code


def validate_fields(required_fields, validations):
    """
    Validates required fields based on provided validation rules.

    Args:
        required_fields (dict): Dictionary of field names and their values.
        validations (dict): Dictionary of field names and their validation functions.

    Returns:
        tuple: (is_valid (bool), error_message (str))
    """
    for field, funcs in validations.items():
        value = required_fields.get(field)
        for func in funcs:
            if func == validators.length and not func(value, max_val=64):
                return False, f"{field.title()} must not exceed 64 characters"
            elif func != validators.length and not func(value):
                return False, f"Invalid {field} format"
    return True, None

