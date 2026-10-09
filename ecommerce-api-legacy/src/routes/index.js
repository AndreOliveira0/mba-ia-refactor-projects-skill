const express = require('express');
const { checkout } = require('../controllers/checkoutController');
const { financialReport } = require('../controllers/reportController');
const { deleteUser } = require('../controllers/userController');
const requireAdminToken = require('../middlewares/adminAuth');

const router = express.Router();

router.post('/checkout', checkout);
router.get('/admin/financial-report', requireAdminToken, financialReport);
router.delete('/users/:id', deleteUser);

module.exports = router;