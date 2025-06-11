from sqlalchemy.exc import NoResultFound

from logger import get_logger
from models import BlacklistedToken
from flask_jwt_extended import decode_token
from datetime import datetime
from extension import db
import jwt
from flask import request, jsonify
from config import Config
from functools import wraps
from load_services import ServicesLoaderSingleton

s = ServicesLoaderSingleton()
logger_utils = get_logger("utils_logger")


def is_token_blacklisted(jwt_payload):
    jti = jwt_payload["jti"]
    user_id = jwt_payload["sub"]
    try:
        token = BlacklistedToken.query.filter_by(jti=jti, user_id=user_id).one()
        return token.revoked_at is not None
    except NoResultFound:
        raise Exception(f"Could not find token {jti}")


def add_token_to_database(encoded_token):
    decoded_token = decode_token(encoded_token)
    jti = decoded_token["jti"]
    token_type = decoded_token["type"]
    user_id = decoded_token["sub"]
    expires = datetime.fromtimestamp(decoded_token["exp"])

    db_token = BlacklistedToken(
        jti=jti,
        token_type=token_type,
        user_id=user_id,
        expires=expires,
    )
    db.session.add(db_token)
    db.session.commit()


def revoke_token(token_jti, user_id):
    try:
        token = BlacklistedToken.query.filter_by(jti=token_jti, user_id=user_id).one()
        token.revoked_at = datetime.utcnow()
        db.session.commit()
    except NoResultFound:
        raise Exception(f"Could not find token {token_jti}")


def verify_jwt(token):
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.ALGORITHM])
        if is_token_blacklisted(payload):
            return None
        return payload["sub"]

    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_token_from_headers():
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    return None


def requires_auth(logger_instance=logger_utils):
    def _authenticate(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = get_token_from_headers()
            path = request.path.split("/")[2]
            logger_gateway = logger_instance
            for service in s.get_json_as_list():
                if service["slug"] == path:
                    if service["protected_key"] not in request.path.split("/"):
                        return f(*args, **kwargs)
                    break
            if token is None or verify_jwt(token) is None:
                logger_gateway.info(f"Unauthorised {request.method} request {request.path}")
                return jsonify({"error": "Unauthorized"}), 401
            logger_gateway.info(f"Authorised {request.method} request {request.path}")
            return f(*args, **kwargs)

        return decorated_function
    return _authenticate
