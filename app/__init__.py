"""
Jenga Equipment Rental Service
---
Jenga is a web application that allows people to rent out heavy machinery
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager # type: ignore for now
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(test_config=None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app.auth import auth
    from app.main import main
    app.register_blueprint(auth)
    app.register_blueprint(main)
    return app