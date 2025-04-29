import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import requests

app = Flask(__name__)
app.secret_key = 'temp_secret_key_for_ryan'
RECAPTCHA_SECRET_KEY = '6Lcr6icrAAAAACZNznfshSKSjgrFPIiQttmrhZ4V'

def init_db():
    os.makedirs('db', exist_ok=True)
    with sqlite3.connect('db/expenses.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          username TEXT NOT NULL UNIQUE,
                          password TEXT NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_id INTEGER,
                          date TEXT NOT NULL,
                          category TEXT NOT NULL,
                          amount REAL NOT NULL,
                          description TEXT NOT NULL,
                          FOREIGN KEY (user_id) REFERENCES users (id))''')
        conn.commit()

init_db()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('db/expenses.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            if user and check_password_hash(user[2], password):
                session['user_id'] = user[0]
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return redirect(url_for('register'))
        recaptcha_response = request.form.get('g-recaptcha-response')
        verify_url = 'https://www.google.com/recaptcha/api/siteverify'
        payload = {'secret': RECAPTCHA_SECRET_KEY, 'response': recaptcha_response}
        recaptcha_check = requests.post(verify_url, data=payload).json()
        if not recaptcha_check.get('success'):
            flash('reCAPTCHA verification failed.', 'error')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password)
        with sqlite3.connect('db/expenses.db') as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                               (username, hashed_password))
                conn.commit()
                flash('Registration successful, please log in.', 'success')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Username already exists.', 'error')
    return render_template('register.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    with sqlite3.connect('db/expenses.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM users WHERE id = ?', (session['user_id'],))
        user = cursor.fetchone()
        username = user[0] if user else 'User'

        # Handle expense submission
        if request.method == 'POST':
            date = request.form['date']
            category = request.form['category']
            amount = request.form['amount']
            description = request.form['description']
            cursor.execute('''INSERT INTO expenses (user_id, date, category, amount, description)
                              VALUES (?, ?, ?, ?, ?)''',
                           (session['user_id'], date, category, amount, description))
            conn.commit()

        # Handle search + filter
        search = request.args.get('search', '').strip()
        category_filter = request.args.get('category', '').strip()

        query = 'SELECT * FROM expenses WHERE user_id = ?'
        params = [session['user_id']]

        if search:
            query += ' AND UPPER(description) LIKE ?'
            params.append(f'%{search.upper()}%')
        if category_filter:
            query += ' AND UPPER(category) LIKE ?'
            params.append(f'%{category_filter.upper()}%')

        cursor.execute(query, params)
        expenses = cursor.fetchall()

        # Format date
        for i, expense in enumerate(expenses):
            try:
                date_obj = datetime.strptime(expense[2], '%Y-%m-%d')
                expenses[i] = expense[:2] + (date_obj.strftime('%m-%d-%Y'),) + expense[3:]
            except ValueError:
                continue

    return render_template('dashboard.html', username=username, expenses=expenses)

@app.route('/add_expense', methods=['POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    date = request.form['date']
    category = request.form['category']
    amount = request.form['amount']
    description = request.form['description']

    with sqlite3.connect('db/expenses.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO expenses (user_id, date, category, amount, description)
                          VALUES (?, ?, ?, ?, ?)''',
                       (session['user_id'], date, category, amount, description))
        conn.commit()

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
