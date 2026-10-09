import os
import secrets
from dotenv import load_dotenv

load_dotenv()


class Settings:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///tasks.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY') or secrets.token_hex(32)
    DEBUG = os.getenv('DEBUG', 'False').lower() in {'1', 'true', 'yes'}


settings = Settings()


def get_settings():
    return settings
