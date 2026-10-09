from flask import Flask
from flask_cors import CORS

from config.settings import Config
from middlewares.errors import register_error_handlers
from models.database import get_db
from routes.api_routes import api_bp

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
register_error_handlers(app)
app.register_blueprint(api_bp)

if __name__ == "__main__":
    get_db()
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
