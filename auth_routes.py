from flask import Blueprint, request, jsonify

from logger import get_logger
from models import User, db
from utils import is_token_blacklisted, add_token_to_database, revoke_token
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
)
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)
logger = get_logger("auth_logger")


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return jsonify({'message': 'User already exists'}), 409

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        logger.info(f"New User Registered: {username}")
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        logger.error(str(e))
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            access_token = create_access_token(identity=user.username)
            refresh_token = create_refresh_token(identity=user.username)
            add_token_to_database(access_token)
            add_token_to_database(refresh_token)
            logger.info(f"User {username} logged in")
            return jsonify({'access_token': access_token, "refresh_token": refresh_token}), 200
        logger.info(f"Invalid credentials for {username}")
        return jsonify({'message': 'Invalid credentials'}), 401
    except Exception as e:
        logger.error(f"{e}")
        return jsonify({"error": str(e)})


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    user_id = get_jwt_identity()
    revoke_token(jti, user_id)
    logger.info(f"{user_id} logged out")
    return jsonify({'message': 'Successfully logged out'}), 200


@auth_bp.route('/reset_password', methods=['POST'])
def reset_password():
    try:
        data = request.json
        username = data.get('username')
        new_password = data.get('new_password')
        user = User.query.filter_by(username=username).first()
        if user:
            user.set_password(new_password)
            db.session.commit()
            logger.info(f"Password reset for user {data.get('username')}")
            return jsonify({'message': 'Password updated successfully'}), 200
        logger.info(f"Invalid password reset request from {data.get('username')}")
        return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        logger.error(f"{e}")
        return jsonify({"error": str(e)})





