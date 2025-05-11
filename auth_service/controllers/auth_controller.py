from flask_jwt_extended import create_access_token, create_refresh_token
from models.user import User, db

def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user
    return None

def generate_tokens(user):
    access_token = create_access_token(identity=user.username)
    refresh_token = create_refresh_token(identity=user.username)
    return access_token, refresh_token

def register_user(username, password):
    if User.query.filter_by(username=username).first():
        return None, "Username already exists"
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user, None
