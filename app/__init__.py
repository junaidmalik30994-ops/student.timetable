from flask import Flask
from flask.json.provider import DefaultJSONProvider
from bson import ObjectId
from config import Config
from app.utils.db import get_db

class MongoJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.json_provider_class = MongoJSONProvider
    app.json = MongoJSONProvider(app)

    # Initialize Database Connection & Default Admin
    with app.app_context():
        get_db()
        from app.services.admin_service import AdminService
        AdminService.ensure_default_admin()

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)

    return app

