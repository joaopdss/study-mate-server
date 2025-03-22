import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    # Initialize Flask app
    app = Flask(__name__)
    
    # Configure app
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    
    # Initialize extensions
    CORS(app)
    JWTManager(app)
    
    # Register blueprints
    from app.routes.exam_routes import exam_bp
    from app.routes.study_plan_routes import study_plan_bp
    from app.routes.quiz_routes import quiz_bp
    
    app.register_blueprint(exam_bp, url_prefix='/api')
    app.register_blueprint(study_plan_bp, url_prefix='/api')
    app.register_blueprint(quiz_bp, url_prefix='/api')
    
    return app

if __name__ == '__main__':
    app = create_app()

    cert_path = os.environ.get('SSL_CERT_PATH', './certificates/cert1.pem')
    key_path = os.environ.get('SSL_KEY_PATH', './certificates/key1.pem')
    app.run(host='0.0.0.0', port=5003) 