"""
This module contains the configuration settings for the application.

Attributes:
    SQLALCHEMY_DATABASE_URL (str): The URL of the database.
    FRONTEND_URL (str): The URL of the frontend application.
    JWT_SECRET_KEY (str): The secret key used for JWT token generation.
    JWT_ALGORITHM (str): The algorithm used for JWT token generation.
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES (str): The expiration time in minutes for access tokens.
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES (str): The expiration time in minutes for refresh tokens.
"""

from decouple import config

SQLALCHEMY_DATABASE_URL = config("DEV_DATABASE_URL")
FRONTEND_URL = config("FRONTEND_URL")
JWT_SECRET_KEY = config("JWT_SECRET_KEY")
JWT_ALGORITHM = config("JWT_ALGORITHM")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = config("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
JWT_REFRESH_TOKEN_EXPIRE_MINUTES = config("JWT_REFRESH_TOKEN_EXPIRE_MINUTES")
