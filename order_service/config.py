import os
from dotenv import load_dotenv

load_dotenv() # For local development if you use a .env file

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'postgresql://postgres:password@db:5432/ecommerce')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-fallback-secret-key')
    PRODUCT_SERVICE_URL = os.environ.get('PRODUCT_SERVICE_URL', 'http://localhost:5001')
    # AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL', 'http://localhost:5000')
