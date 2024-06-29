from flask import request, jsonify
import logging
import datetime as dt
from app import db

from app.models import User, UserLoginHistory
from app.routes import logout_bp
from app.services.jwt_service import revoke_custom_token,verify_custom_token

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@logout_bp.before_request
def before_request():
    logger.info(f"Request: {request.method} ")

@logout_bp.route('/logout', methods=['POST'])
def logout():
    custom_token = request.headers.get('token')
    data = request.get_json()
    email = data.get('email')

    if not custom_token:
        return jsonify({'error': 'Missing custom token'}), 401
    
    tokenValidationResponse = verify_custom_token(custom_token)

    if 'error' in tokenValidationResponse:
        return jsonify(tokenValidationResponse), 401
    
    user = User.query.filter_by(email=email).first()
    if revoke_custom_token(custom_token):
        logger.info("Logout successfull")
        logout_history = UserLoginHistory(
                user_id=user.id,
                logout_datetime=dt.datetime.utcnow(),
                logout_success=True,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
        db.session.add(logout_history)
        
        db.session.commit()
        return jsonify({'message': "Logout successfull"}), 200

        
    
    else:
        logger.error("Failed to revoke token")
        return jsonify({'error': 'Failed to revoke token'}), 400