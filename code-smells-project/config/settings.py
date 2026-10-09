import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
    DB_PATH = os.environ.get("DB_PATH", "loja.db")
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")
