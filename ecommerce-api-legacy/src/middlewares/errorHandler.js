function errorHandler(err, req, res, next) {
    const statusCode = err.statusCode || 500;
    if (err.name === 'AppError') {
        return res.status(statusCode).send(err.message || 'Error');
    }

    const payload = {
        error_code: err.errorCode || 'INTERNAL_SERVER_ERROR',
        message: err.message || 'Internal Server Error'
    };

    if (err.details && process.env.NODE_ENV !== 'production') {
        payload.details = err.details;
    }

    return res.status(statusCode).json(payload);
}

module.exports = errorHandler;