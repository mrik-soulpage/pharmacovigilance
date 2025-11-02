"""
Configuration API routes
"""
import logging
from flask import request, jsonify, current_app
from app.api import api_bp
from app.services.pubmed_service import PubMedService
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)


@api_bp.route('/config', methods=['GET'])
def get_config():
    """Get current configuration (without sensitive values)"""
    try:
        config = {
            'pubmed_configured': bool(current_app.config.get('PUBMED_API_KEY')),
            'openai_configured': bool(current_app.config.get('OPENAI_API_KEY')),
            'pubmed_email': current_app.config.get('PUBMED_EMAIL'),
            'openai_model': current_app.config.get('OPENAI_MODEL'),
            'max_articles_per_search': current_app.config.get('MAX_ARTICLES_PER_SEARCH'),
            'confidence_threshold_high': current_app.config.get('CONFIDENCE_THRESHOLD_HIGH'),
            'confidence_threshold_medium': current_app.config.get('CONFIDENCE_THRESHOLD_MEDIUM'),
        }
        
        return jsonify({
            'success': True,
            'data': config
        })
    except Exception as e:
        logger.error(f"Error fetching configuration: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/config/test-pubmed', methods=['POST'])
def test_pubmed_connection():
    """Test PubMed API connection"""
    try:
        data = request.get_json() or {}
        api_key = data.get('api_key') or current_app.config.get('PUBMED_API_KEY')
        email = data.get('email') or current_app.config.get('PUBMED_EMAIL')
        
        pubmed = PubMedService(api_key=api_key, email=email)
        success = pubmed.test_connection()
        
        return jsonify({
            'success': success,
            'message': 'PubMed connection successful' if success else 'PubMed connection failed'
        })
    except Exception as e:
        logger.error(f"Error testing PubMed connection: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/config/test-openai', methods=['POST'])
def test_openai_connection():
    """Test OpenAI API connection"""
    try:
        data = request.get_json() or {}
        api_key = data.get('api_key') or current_app.config.get('OPENAI_API_KEY')
        model = data.get('model') or current_app.config.get('OPENAI_MODEL')
        
        ai_service = AIService(api_key=api_key, model=model)
        success = ai_service.test_connection()
        
        return jsonify({
            'success': success,
            'message': 'OpenAI connection successful' if success else 'OpenAI connection failed'
        })
    except Exception as e:
        logger.error(f"Error testing OpenAI connection: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

