const config = {
    port: Number(process.env.PORT || 3000),
    adminToken: process.env.ADMIN_TOKEN || '',
    databaseFilename: process.env.DATABASE_FILENAME || ':memory:'
};

module.exports = config;