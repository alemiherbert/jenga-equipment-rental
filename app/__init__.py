"""
Jenga Equipment Rental API
"""

from flask import Flask
from flasgger import Swagger
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config
from os import makedirs

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
swagger = Swagger()


def create_app(test_config=None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    swagger.init_app(app)
    makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    from app.models import User, TokenBlocklist

    def setup_jwt_callbacks(app):
        """Set up JWT callbacks for token verification"""
        jwt = app.extensions['jwt']
        
        @jwt.token_in_blocklist_loader
        def check_if_token_revoked(jwt_header, jwt_payload):
            jti = jwt_payload["jti"]
            token = db.session.scalar(
                select(TokenBlocklist).where(TokenBlocklist.jti == jti)
            )
            return token is not None

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        """
        Convert user entered as identity into serialisable object
        """
        return user.id

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """
        Loads a user from your database whenever a protected route is accessed.
        """
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity).one_or_none()

    from app.api import api
    from flask import send_from_directory
    from os import path
    app.register_blueprint(api)
    
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        upload_dir = path.abspath(app.config['UPLOAD_FOLDER'])
        return send_from_directory(upload_dir, filename)

    return app