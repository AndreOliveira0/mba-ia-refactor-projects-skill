from flask import jsonify


class AppError(Exception):
    def __init__(self, message, status_code=400, error_code="APP_ERROR", details=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        payload = {
            "error_code": err.error_code,
            "message": err.message,
        }
        if err.details:
            payload["details"] = err.details
        return jsonify(payload), err.status_code

    @app.errorhandler(Exception)
    def handle_unexpected_error(_err):
        return jsonify({"error_code": "INTERNAL_ERROR", "message": "Erro interno"}), 500
