from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import datetime as dt
from flask import request, jsonify

db = SQLAlchemy()
migrate = Migrate()

from app.config import Config
from app.routes import auth_bp, file_ops_bp, genai_bp, speech_bp,profile_bp,logout_bp,search_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(file_ops_bp, url_prefix='/file')
    app.register_blueprint(genai_bp, url_prefix='/genai')
    app.register_blueprint(speech_bp, url_prefix='/speech')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(logout_bp, url_prefix='/logout') 
    app.register_blueprint(search_bp, url_prefix='/search')

    
    @app.route('/', methods=['GET'])
    def get_result():
        return jsonify({'default':'welcome to flask application'})
    return app
