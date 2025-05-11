import os

class Config:
    # Use environment variables or hardcode for learning
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URI",
        "postgresql://postgres:password@db:5432/ecommerce"
    )
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
