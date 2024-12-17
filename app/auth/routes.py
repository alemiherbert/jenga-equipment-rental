"""
Authentification routes
"""

from app.auth import auth
from app.models import User, Role, Equipment, Booking, Location


@auth.route("/login")
def login():
    """
    Login functionality
    """
    return "Login"

@auth.route("/register")
def register():
    """
    Registration functionality
    """
    return "Register"
