"""
Main app routes
"""

from app.main import main
from flask import render_template


@main.route("/")
@main.route("/home")
def index():
    """
    Homepage
    """
    return "<h1>Welcome to Jenga </h1>"
