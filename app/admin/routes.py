"""
admin app routes
"""

from app.admin import admin
from flask import render_template, jsonify
from flask_jwt_extended import jwt_required, current_user


@admin.route("/dashboard")
def dashboard():
    """
    Dashboard
    """
    return render_template(
        "layouts/dashboard.html",
        notifications = [
            {
                "status": "unread",
                "title": "Hello there",
                "body": "A simple notification"
            }
        ])


@admin.route("/equipment")
@admin.route("/equipment/all")
def get_equipment_list():
    """
    Equipment
    """
    return render_template(
        "layouts/dash-equipment.html"    
    )


@admin.route("/equipment/<int:equipment_id>")
def get_equipment(equipment_id):
    """
    Equipment
    """
    return render_template(
        "layouts/equipment-details.html"    
    )


@admin.route("/cart")
def cart():
    """
    Cart
    """
    return render_template(
        "layouts/cart.html"
    )


@admin.route("/checkout")
def checkout():
    """
    Checkout
    """
    return render_template(
        "layouts/checkout.html"
    )