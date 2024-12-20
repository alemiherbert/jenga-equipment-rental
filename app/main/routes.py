"""
Main app routes
"""

from app.main import main
from flask import render_template, jsonify


@main.route("/")
@main.route("/home")
def index():
    """
    Homepage
    """
    return render_template(
        "index.html",
        notifications = [
            {
                "status": "unread",
                "title": "Hello there",
                "body": "A simple notification"
            }
        ])
