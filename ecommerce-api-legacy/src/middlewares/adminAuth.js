const AppError = require('./appError');
const config = require('../config');

function requireAdminToken(req, res, next) {
    if (!config.adminToken) {
        return next(new AppError('ADMIN_TOKEN_NOT_CONFIGURED', 500, 'Admin token not configured'));
    }

    const adminToken = req.header('x-admin-token');

    if (!adminToken || adminToken !== config.adminToken) {
        return next(new AppError('UNAUTHORIZED', 401, 'Unauthorized'));
    }

    return next();
}

module.exports = requireAdminToken;