
from flask_bcrypt import Bcrypt
from datetime import datetime
from extension import db


bcrypt = Bcrypt()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)


class BlacklistedToken(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jti = db.Column(db.String(36), nullable=False, unique=True)
    token_type = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    revoked_at = db.Column(db.DateTime)
    expires = db.Column(db.DateTime, nullable=False)

    user = db.relationship("User")