import datetime as dt
import logging
from flask import request, jsonify
from app import db
from app.models import User
from app.routes import profile_bp
from app.services.jwt_service import verify_custom_token

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@profile_bp.before_request
def before_request():
    logger.info(f"Request: {request.method} ")

@profile_bp.route('/get_profile', methods=['GET'])
def get_profile():
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

    profile = user.user_profile
    profile_data = {
        'language': profile.language,
        'application_theme': profile.application_theme,
        'is_speech': profile.is_speech,
        'is_mic': profile.is_mic,
        'is_holcim_data': profile.is_holcim_data,
        'is_my_library': profile.is_my_library,
        'is_custom_copilot': profile.is_custom_copilot,
        'temp': profile.converse_style,
        'context': profile.custom_instruction,
    }

    logger.info(f"Profile retrieved for email: {email}")
    return jsonify(profile_data)

@profile_bp.before_request
def before_request():
    logger.info(f"Request: {request.method} ")
    
@profile_bp.route('/update_profile', methods=['POST'])
def update_profile():
    custom_token = request.headers.get('token')
    if not custom_token:
        logger.warning("Missing custom token in request to /update_profile")
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

    profile = user.user_profile
    data = request.json

    if 'language' in data:
        profile.language = data['language']
    
    if 'application_theme' in data:
        profile.application_theme = data['application_theme']

    if 'is_speech' in data:
        profile.is_speech = data['is_speech']

    if 'is_mic' in data:
        profile.is_mic = data['is_mic']

    if 'is_holcim_data' in data:
        profile.is_holcim_data = data['is_holcim_data']

    if 'is_my_library' in data:
        profile.is_my_library = data['is_my_library']

    if 'is_custom_copilot' in data:
        profile.is_custom_copilot = data['is_custom_copilot']

    if 'temp' in data:
        profile.converse_style = data['temp']

    if 'context' in data:
        profile.custom_instruction = data['context']

    profile.modified_datetime = dt.datetime.utcnow()
    profile.modified_by = 'user'

    db.session.commit()

    logger.info(f"Profile updated for email: {email}")
    return jsonify({'message': 'Profile updated successfully'})
