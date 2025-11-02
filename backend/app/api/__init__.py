"""
API Blueprint
"""
from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Import routes to register them with the blueprint
from app.api import products, search, config, export

