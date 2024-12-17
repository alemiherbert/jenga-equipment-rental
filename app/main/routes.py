"""
Main app routes
"""

from app.main import main
from flask import jsonify

@main.route("/")
def index():
    return jsonify({"greeting": "Hello, World!"})