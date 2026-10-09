const { findPaymentByEnrollmentId, findUserById, listCourses, listEnrollmentsByCourse } = require('../models/repositories');

async function financialReport(req, res, next) {
    try {
        const courses = await listCourses();
        const report = [];

        for (const course of courses) {
            const enrollments = await listEnrollmentsByCourse(course.id);
            const courseData = { course: course.title, revenue: 0, students: [] };

            for (const enrollment of enrollments) {
                const user = await findUserById(enrollment.user_id);
                const payment = await findPaymentByEnrollmentId(enrollment.id);

                if (payment && payment.status === 'PAID') {
                    courseData.revenue += payment.amount;
                }

                courseData.students.push({
                    student: user ? user.name : 'Unknown',
                    paid: payment ? payment.amount : 0
                });
            }

            report.push(courseData);
        }

        res.json(report);
    } catch (error) {
        next(error);
    }
}

module.exports = { financialReport };