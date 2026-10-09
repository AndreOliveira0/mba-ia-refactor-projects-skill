const express = require('express');
const config = require('./config');
const routes = require('./routes');
const errorHandler = require('./middlewares/errorHandler');
const { initializeDatabase } = require('./models/database');

async function bootstrap() {
    await initializeDatabase();

    const app = express();

    app.use(express.json());
    app.use('/api', routes);
    app.use(errorHandler);

    app.listen(config.port, () => {
        console.log(`Frankenstein LMS rodando na porta ${config.port}...`);
    });
}

bootstrap().catch((error) => {
    console.error('Falha ao inicializar a aplicação:', error);
    process.exit(1);
});
