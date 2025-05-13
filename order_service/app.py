from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from models import db as app_db # Import db instance from models.py
from routes import orders_bp # Import the blueprint
import logging

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    app_db.init_app(app)
    Migrate(app, app_db)

    # Register blueprints
    app.register_blueprint(orders_bp)

    # Basic logging setup
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)
    
    # Test route
    @app.route('/ping')
    def ping():
        return "Order Service: Pong!"

    return app

app = create_app() # For Gunicorn or `flask run` to pick up

if __name__ == '__main__':
    # This part is for running with `python app.py` directly
    # For Docker, `flask run` or Gunicorn specified in CMD is preferred
    app.run(host='0.0.0.0', port=5002, debug=True)
