const AppError = require('../middlewares/appError');
const { hashPassword } = require('../services/passwordHasher');
const {
    createAuditLog,
    createEnrollment,
    createPayment,
    createUser,
    findCourseById,
    findUserByEmail
} = require('../models/repositories');

async function checkout(req, res, next) {
    try {
        const userName = req.body.usr;
        const email = req.body.eml;
        const password = req.body.pwd;
        const courseId = req.body.c_id;
        const cardNumber = req.body.card;

        if (!userName || !email || !courseId || !cardNumber) {
            throw new AppError('BAD_REQUEST', 400, 'Bad Request');
        }

        const course = await findCourseById(courseId);

        if (!course) {
            throw new AppError('COURSE_NOT_FOUND', 404, 'Curso não encontrado');
        }

        const existingUser = await findUserByEmail(email);
        let userId = existingUser ? existingUser.id : null;

        if (!existingUser) {
            userId = await createUser({
                name: userName,
                email,
                pass: hashPassword(password || '123456')
            });
        }

        const paymentStatus = cardNumber.startsWith('4') ? 'PAID' : 'DENIED';

        if (paymentStatus === 'DENIED') {
            throw new AppError('PAYMENT_DECLINED', 400, 'Pagamento recusado');
        }

        const enrollmentId = await createEnrollment({ userId, courseId });
        await createPayment({ enrollmentId, amount: course.price, status: paymentStatus });
        await createAuditLog(`Checkout curso ${courseId} por ${userId}`);

        res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
    } catch (error) {
        next(error);
    }
}

module.exports = { checkout };