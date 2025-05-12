import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate() 
def create_app():
    # Load environment variables from .env file
    load_dotenv()

    app = Flask(__name__)

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from routes.product_routes import product_bp
    app.register_blueprint(product_bp, url_prefix='/api/products')

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
        migrate.init_app(app, db)

    return app
