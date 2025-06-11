import os
from datetime import timedelta


class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'your_jwt_secret_key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=2)
    JWT_BLACKLIST_ENABLED = True
    ALGORITHM = "HS256"
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
