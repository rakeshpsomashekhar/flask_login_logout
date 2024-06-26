import datetime as dt
from redis import Redis
from flask import request, jsonify, current_app

from app import db
from app.routes import auth_bp
from app.models import User, UserLoginHistory, UserProfile
from app.services.jwt_service import verify_google_jwt, generate_custom_token, verify_custom_token

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@auth_bp.before_request
def before_request():
    logger.info(f"Request: {request.method}")

@auth_bp.route('/verify-oauth-token', methods=['POST'])
def verify_google_token():
    redis_client = Redis.from_url(current_app.config['REDIS_URL'])
    data = request.get_json()
    google_jwt = data.get('google_jwt')
    email = data.get('email')

    if not google_jwt or not email:
        logger.warning("Missing parameters in request to /verify-oauth-token")
        return jsonify({'error': 'Missing parameters'}), 401

    validated_data = verify_google_jwt(google_jwt, email)
    
    if validated_data:
        token, expiration_time = generate_custom_token(email)
        redis_client.set(token, email, expiration_time)
        redis_client.close()
        user = User.query.filter_by(email=email).first()
        
        if not user:
            logger.info(f"Creating new user for email: {email}")
            user = User(
                email=email,
                first_name=validated_data.get('given_name'),
                last_name=validated_data.get('family_name'),
                created_datetime=dt.datetime.utcnow(),
                created_by='google_oauth',
                user_type='holcim'
            )
            db.session.add(user)
            logger.info(f"Created new user for email: {email}")
            db.session.flush()  # Ensure user.id is available
            user_profile = UserProfile(
                user_id=user.id,
                language=current_app.config['LANGUAGE'], 
                application_theme=current_app.config['APPLICATION_THEME'],
                is_speech=current_app.config['IS_SPEECH'],
                is_mic=current_app.config['IS_MIC'],
                is_holcim_data=current_app.config['IS_HOLCIM_DATA'],
                is_my_library=current_app.config['IS_MY_LIBRARY'],
                is_custom_copilot=current_app.config['IS_CUSTOM_COPILOT'],
                converse_style=current_app.config['CONVERSE_STYLE'],
                custom_instruction=current_app.config['CUSTOM_INSTRUCTION'],
                created_datetime=dt.datetime.utcnow(),  # Use current time for created_datetime
                created_by=current_app.config['CREATED_BY']
            )
            db.session.add(user_profile)
            logger.info(f"Created user profile for email: {email}")
        else:
            logger.info(f"User exists for email: {email}, logging login history")
            login_history = UserLoginHistory(
                user_id=user.id,
                login_datetime=dt.datetime.utcnow(),
                login_success=True,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(login_history)
        
        db.session.commit()
        logger.info(f"Token generated ")
        return jsonify({'custom_token': token})
    else:
        logger.warning("Invalid Google JWT token or email")
        return jsonify({'error': 'Invalid Google JWT token or email'}), 401

@auth_bp.route('/verify-token', methods=['POST'])
def verify_own_token():
    redis_client = Redis.from_url(current_app.config['REDIS_URL'])
    data = request.get_json()
    custom_token = data.get('custom_token')

    if not custom_token:
        logger.warning("Missing custom token in request to /verify-token")
        return jsonify({'error': 'Missing custom token'}), 400

    # result = verify_custom_token(custom_token)
    result = redis_client.get(custom_token)
    
    if not result:
        logger.warning(f"Token verification failed: {result['error']}")
        return jsonify(result), 401

    logger.info(f"Token verified successfully for email: {result}")
    return jsonify({'email': result, 'message': 'Token is valid'})

@auth_bp.route('/logout', methods=['POST'])
def logout():
    redis_client = Redis.from_url(current_app.config['REDIS_URL'])
    custom_token = request.headers.get('token')
    data = request.get_json()
    email = data.get('email')
    redis_client.delete(custom_token)
    return jsonify({'message': "Logout successfull"}), 200