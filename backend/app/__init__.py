"""
Flask application factory
"""
import os
import logging
from flask import Flask
from flask_cors import CORS
from app.config import config
from app.models import db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def create_app(config_name=None):
    """
    Application factory pattern
    
    Args:
        config_name: Configuration name (development, production, testing)
        
    Returns:
        Flask application instance
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    # Configure CORS - allow all origins for development
    CORS(app, 
         resources={r"/api/*": {"origins": "*"}},
         supports_credentials=False)
    
    # Register blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return {'status': 'healthy', 'service': 'Pharmacovigilance Literature Monitoring'}
    
    return app

