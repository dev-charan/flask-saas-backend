from flask import Flask
from config import Config
from models.user import db, bcrypt
from views.auth_view import auth_bp
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

app.register_blueprint(auth_bp)

with app.app_context():
    db.create_all()  # Creates tables if not exist

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

