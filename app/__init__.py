"""
Jenga Equipment Rental API
"""

from flask import Flask, jsonify, send_from_directory
from flasgger import Swagger
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config
from os import makedirs, path

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
    app.register_blueprint(api)
    
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        upload_dir = path.abspath(app.config['UPLOAD_FOLDER'])
        return send_from_directory(upload_dir, filename)

    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad request", "message": str(error)}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({"error": "Unauthorized", "message": "Authentication is required to access this resource."}), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({"error": "Forbidden", "message": "You do not have permission to access this resource."}), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found", "message": "The requested resource was not found."}), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({"error": "Internal server error", "message": "An unexpected error occurred."}), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        # Pass through HTTP errors
        if hasattr(error, 'code'):
            return error
        # Now you're handling non-HTTP exceptions only
        app.logger.error(f"Unexpected error: {error}")
        return jsonify({"error": "Internal server error", "message": "An unexpected error occurred."}), 500

    return app
