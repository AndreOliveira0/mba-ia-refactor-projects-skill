const { all, get, run } = require('./database');

async function findCourseById(courseId) {
    return get('SELECT id, title, price, active FROM courses WHERE id = ? AND active = 1', [courseId]);
}

async function findUserByEmail(email) {
    return get('SELECT id, name, email, pass FROM users WHERE email = ?', [email]);
}

async function findUserById(userId) {
    return get('SELECT id, name, email FROM users WHERE id = ?', [userId]);
}

async function listCourses() {
    return all('SELECT id, title, price, active FROM courses ORDER BY id');
}

async function listEnrollmentsByCourse(courseId) {
    return all('SELECT id, user_id, course_id FROM enrollments WHERE course_id = ?', [courseId]);
}

async function findPaymentByEnrollmentId(enrollmentId) {
    return get('SELECT amount, status FROM payments WHERE enrollment_id = ?', [enrollmentId]);
}

async function createUser({ name, email, pass }) {
    const result = await run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [name, email, pass]);
    return result.lastID;
}

async function createEnrollment({ userId, courseId }) {
    const result = await run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [userId, courseId]);
    return result.lastID;
}

async function createPayment({ enrollmentId, amount, status }) {
    return run('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)', [enrollmentId, amount, status]);
}

async function createAuditLog(action) {
    return run("INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))", [action]);
}

async function deleteUserById(userId) {
    return run('DELETE FROM users WHERE id = ?', [userId]);
}

module.exports = {
    createAuditLog,
    createEnrollment,
    createPayment,
    createUser,
    deleteUserById,
    findCourseById,
    findPaymentByEnrollmentId,
    findUserByEmail,
    findUserById,
    listCourses,
    listEnrollmentsByCourse
};