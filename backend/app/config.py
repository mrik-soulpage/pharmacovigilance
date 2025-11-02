"""
Configuration module for Pharmacovigilance Literature Monitoring application
"""
import os
from pathlib import Path

class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///pharma_pv.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # PubMed API
    PUBMED_API_KEY = os.environ.get('PUBMED_API_KEY', '')
    PUBMED_EMAIL = os.environ.get('PUBMED_EMAIL', 'user@example.com')
    PUBMED_RATE_LIMIT = int(os.environ.get('PUBMED_RATE_LIMIT', '10'))  # requests per second
    
    # OpenAI API
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4.1-mini')
    
    # File paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / 'data'
    EXPORTS_DIR = BASE_DIR / 'exports'
    SYNTHETIC_DATA_DIR = BASE_DIR.parent / 'synthetic_data'
    
    # Ensure directories exist
    DATA_DIR.mkdir(exist_ok=True)
    EXPORTS_DIR.mkdir(exist_ok=True)
    
    # Application settings
    MAX_ARTICLES_PER_SEARCH = int(os.environ.get('MAX_ARTICLES_PER_SEARCH', '100'))
    CONFIDENCE_THRESHOLD_HIGH = float(os.environ.get('CONFIDENCE_THRESHOLD_HIGH', '0.85'))
    CONFIDENCE_THRESHOLD_MEDIUM = float(os.environ.get('CONFIDENCE_THRESHOLD_MEDIUM', '0.60'))
    
    # CORS - Allow common development origins by default
    CORS_ORIGINS = os.environ.get(
        'CORS_ORIGINS', 
        'http://localhost:3000,http://localhost:5173,http://localhost:5174,http://localhost:80,http://localhost'
    ).split(',')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

