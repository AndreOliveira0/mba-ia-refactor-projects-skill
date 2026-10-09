const { deleteUserById } = require('../models/repositories');

async function deleteUser(req, res, next) {
    try {
        await deleteUserById(req.params.id);
        res.send('Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.');
    } catch (error) {
        next(error);
    }
}

module.exports = { deleteUser };