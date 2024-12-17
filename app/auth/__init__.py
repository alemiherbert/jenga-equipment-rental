"""
The authentification blueprint
"""

from flask import Blueprint

auth = Blueprint(__name__, "auth", url_prefix="auth/")
import routes