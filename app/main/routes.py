"""
Main app routes
"""

from app.main import main
from flask import render_template, jsonify
from flask_jwt_extended import jwt_required, current_user


@main.route("/")
@main.route("/home")
def index():
    """
    Homepage
    """
    return render_template(
        "layouts/index.html",
        notifications = [
            {
                "status": "unread",
                "title": "Hello there",
                "body": "A simple notification"
            }
        ])


@main.route("/signin")
def signin():
    """
    Sign in
    """
    return render_template(
        "layouts/sign-in.html"
    )


@main.route("/signup")
def signup():
    """
    Sign Up
    """
    return render_template(
        "layouts/sign-up.html"
    )
    
@main.route("/password-reset")
def reset_password():
    """
    Password Reset
    """
    return render_template(
        "layouts/password-reset.html"
    )
    

@main.route("/equipment")
@main.route("/equipment/all")
def get_equipment_list():
    """
    Equipment
    """
    return render_template(
        "layouts/equipment.html"    
    )


@main.route("/equipment/<int:equipment_id>")
def get_equipment(equipment_id):
    """
    Equipment
    """
    return render_template(
        "layouts/equipment-details.html"    
    )


@main.route("/cart")
def cart():
    """
    Cart
    """
    return render_template(
        "layouts/cart.html"
    )


@main.route("/checkout")
def checkout():
    """
    Checkout
    """
    return render_template(
        "layouts/checkout.html"
    )