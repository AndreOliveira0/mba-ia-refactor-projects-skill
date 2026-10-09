const crypto = require('crypto');

function hashPassword(password) {
    const salt = crypto.randomBytes(16).toString('hex');
    const derivedKey = crypto.scryptSync(String(password), salt, 64).toString('hex');
    return `scrypt:${salt}:${derivedKey}`;
}

module.exports = { hashPassword };