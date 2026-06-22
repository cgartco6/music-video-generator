from flask import Blueprint
from flask_restx import Api

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import routes
from app.api import routes, websocket

def init_api(app):
    """Initialize API with app"""
    app.register_blueprint(api_bp)
    return app
