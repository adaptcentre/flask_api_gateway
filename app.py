import argparse
from pathlib import Path
from load_services import ServicesLoaderSingleton
from flask_cors import CORS

parser = argparse.ArgumentParser()
parser.add_argument("file_path", type=Path)
p = parser.parse_args()
s = ServicesLoaderSingleton(json_path=str(p.file_path))

from flask import Flask
from extension import db, jwt
from auth_routes import auth_bp
from config import Config
from gateway_routes import app_bp
from utils import is_token_blacklisted

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize extensions
db.init_app(app)
jwt.init_app(app)


# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(app_bp, url_prefix='/app')


# JWT Token Blacklist Check
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    return is_token_blacklisted(jwt_payload)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8000)
