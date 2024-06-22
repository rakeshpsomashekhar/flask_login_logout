import jwt
import datetime
from google.oauth2 import id_token
from google.auth.transport import requests
from flask import current_app
import logging
logger = logging.getLogger(__name__)

def verify_google_jwt(google_jwt, email):
    try:
        idinfo = id_token.verify_oauth2_token(google_jwt, requests.Request())
        if idinfo['email'] == email:
            return idinfo
    except Exception as e:
        return None
def generate_custom_token(email):
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=current_app.config['TOKEN_EXPIRATION_MINUTES'])
    token = jwt.encode({'email': email, 'exp': expiration_time}, current_app.config['SECRET_KEY'], algorithm='HS256')
    
    return token, expiration_time

def verify_custom_token(token):
    try:
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        
        logger.info(f"Token verified for email: {data['email']}")
        return {'email': data['email']}
    
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return {'error': 'Token expired'}
    except jwt.InvalidTokenError:
        logger.error("Invalid token")
        return {'error': 'Invalid token'}
    
def revoke_custom_token(token):
    try:
        decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'], options={'verify_exp': False})
        
        decoded_token['exp'] = datetime.datetime.utcnow()

        revoked_token = jwt.encode(decoded_token, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        logger.info(f"Token revoked for email: {decoded_token['email']}")
        return revoked_token
    
    except jwt.InvalidTokenError:
        logger.error("Invalid token")
        return None