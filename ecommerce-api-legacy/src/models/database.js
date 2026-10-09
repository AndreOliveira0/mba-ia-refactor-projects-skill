const sqlite3 = require('sqlite3').verbose();
const config = require('../config');
const { hashPassword } = require('../services/passwordHasher');

const database = new sqlite3.Database(config.databaseFilename);

function run(sql, params = []) {
    return new Promise((resolve, reject) => {
        database.run(sql, params, function onRun(err) {
            if (err) {
                reject(err);
                return;
            }

            resolve({ lastID: this.lastID, changes: this.changes });
        });
    });
}

function get(sql, params = []) {
    return new Promise((resolve, reject) => {
        database.get(sql, params, (err, row) => {
            if (err) {
                reject(err);
                return;
            }

            resolve(row);
        });
    });
}

function all(sql, params = []) {
    return new Promise((resolve, reject) => {
        database.all(sql, params, (err, rows) => {
            if (err) {
                reject(err);
                return;
            }

            resolve(rows);
        });
    });
}

let initializationPromise = null;

function initializeDatabase() {
    if (initializationPromise) {
        return initializationPromise;
    }

    initializationPromise = (async () => {
        await run('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, pass TEXT NOT NULL)');
        await run('CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT NOT NULL, price REAL NOT NULL, active INTEGER NOT NULL)');
        await run('CREATE TABLE enrollments (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, course_id INTEGER NOT NULL)');
        await run('CREATE TABLE payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER NOT NULL, amount REAL NOT NULL, status TEXT NOT NULL)');
        await run('CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, action TEXT NOT NULL, created_at DATETIME NOT NULL)');

        await run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', ['Leonan', 'leonan@fullcycle.com.br', hashPassword('123')]);
        await run('INSERT INTO courses (title, price, active) VALUES (?, ?, ?), (?, ?, ?)', ['Clean Architecture', 997.00, 1, 'Docker', 497.00, 1]);
        await run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [1, 1]);
        await run('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)', [1, 997.00, 'PAID']);
    })();

    return initializationPromise;
}

module.exports = {
    all,
    database,
    get,
    initializeDatabase,
    run
};