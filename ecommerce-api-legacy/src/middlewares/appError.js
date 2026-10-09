class AppError extends Error {
    constructor(errorCode, statusCode, message, details) {
        super(message);
        this.name = 'AppError';
        this.errorCode = errorCode;
        this.statusCode = statusCode;
        this.details = details;
    }
}

module.exports = AppError;