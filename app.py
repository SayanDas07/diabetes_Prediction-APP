# app.py
from flask import Flask
from flask_login import LoginManager
import os

# Import our modules
from config import config
from models import DatabaseManager
from ml_model import DiabetesPredictor
from auth import create_auth_blueprint
from main import create_main_blueprint

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Initialize database manager
    db_manager = DatabaseManager(app.config['DATABASE'])
    
    # Initialize ML predictor
    try:
        predictor = DiabetesPredictor()
    except Exception as e:
        print(f"Warning: Could not load ML models: {e}")
        predictor = None
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return db_manager.get_user_by_id(user_id)
    
    # Register blueprints
    app.register_blueprint(create_auth_blueprint(db_manager))
    app.register_blueprint(create_main_blueprint(db_manager, predictor))
    
    # Initialize database if it doesn't exist
    if not os.path.exists(app.config['DATABASE']):
        db_manager.init_db()
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    # Get configuration from environment
    config_name = os.environ.get('FLASK_CONFIG', 'development')
    app = create_app(config_name)
    app.run(debug=True)