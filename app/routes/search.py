import datetime as dt
import logging
from flask import request, jsonify
from app import db
from app.models import User
from app.routes import search_bp
from app.services.jwt_service import verify_custom_token
from app.services.search_service import holcimCopilotBackend
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@search_bp.before_request
def before_request():
    logger.info(f"Request: {request.method} ")

@search_bp.route('/search', methods=['GET'])
def get_result():
    
    custom_token = request.headers.get('token')
    if not custom_token:
        logger.warning("Missing custom token in request to /get_profile")
        return jsonify({'error': 'Missing custom token'}), 401

    token_validation_response = verify_custom_token(custom_token)
    if 'error' in token_validation_response:
        logger.warning(f"Token validation failed: {token_validation_response['error']}")
        return jsonify(token_validation_response), 401

    email = token_validation_response['email']
    user = User.query.filter_by(email=email).first()

    if not user or not user.user_profile:
        logger.warning(f"Profile not found for email: {email}")
        return jsonify({'error': 'Profile not found'}), 404

    data = request.get_json()
    question=data.get('quetion')
    answer = holcimCopilotBackend.callLLM(question)
    return jsonify({'answer':answer['output']})
