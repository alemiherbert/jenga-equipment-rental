"""
admin app routes
"""

from app.admin import admin
from app.models import User, Equipment, Booking
from flask import render_template, jsonify
from flask_jwt_extended import jwt_required, current_user


@admin.route("/dashboard")
def dashboard():
    """
    Dashboard
    """
    num_users = len(User.query.all())
    num_equipment = len(Equipment.query.all())
    num_bookings = len(Booking.query.all())
    
    return render_template(
        "layouts/dashboard.html",
        data=[num_users, num_equipment, num_bookings],
        notifications = [
            {
                "status": "unread",
                "title": "Hello there",
                "body": "A simple notification"
            }
        ])


@admin.route("/equipment")
def get_equipment_list():
    """
    Equipment
    """
    return render_template(
        "layouts/dash-equipment.html",
        title="Equipment" 
    )


@admin.route("/equipment/add")
def add_equipment():
    """
    New equipment
    """
    return render_template(
        "layouts/dash-new-equipment.html",
        title="Add Equipment"
    )

@admin.route("/equipment/edit/<int:equipment_id>")
def edit_equipment(equipment_id):
    """
    Equipment
    """
    return render_template(
        "layouts/dash-edit-equipment.html",
        title="Edit Equipment"
    )

@admin.route("/bookings")
def get_bookings_list():
    """
    Bookings
    """
    return render_template(
        "layouts/dash-bookings.html"    
    )


@admin.route("/payments")
def get_payments_list():
    """
    Payments
    """
    return render_template(
        "layouts/dash-payments.html",
        title="Bookings"
    )


@admin.route("/users")
def get_Users_list():
    """
    Users
    """
    return render_template(
        "layouts/dash-users.html",
        title="Users"
    )
