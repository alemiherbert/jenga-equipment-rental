"""
Authentification routes
"""

from app.auth import auth

@auth.route
def login():
    """
    Login functionality
    """
    pass

@auth.route
def register():
    """
    Registration functionality
    """
    pass
