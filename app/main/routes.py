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
@main.route("/login")

def signin():
    """
    Login
    """
    return render_template(
        "layouts/sign-in.html"
    )


@main.route("/signup")
@main.route("/register")
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
def equipment():
    """
    Equipment
    """
    return render_template(
        "layouts/equipment.html"    
    )