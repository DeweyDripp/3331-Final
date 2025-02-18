import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Ensure you have a secret key for session management

# Database initialization function
def init_db():
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

# Initialize the database
init_db()

# Route for the home page (dashboard)
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    return render_template('index.html')

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user exists in the database
        with sqlite3.connect('db/expenses.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user[2], password):  # Check hashed password
                session['user_id'] = user[0]  # Store user_id in session
                return redirect(url_for('dashboard'))  # Redirect to the dashboard
            else:
                flash('Invalid credentials', 'error')  # Show error message
    return render_template('login.html')

# Route for the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
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

# Route for the user dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Fetch the username and expenses from the database
    with sqlite3.connect('db/expenses.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM users WHERE id = ?', (session['user_id'],))
        user = cursor.fetchone()
        username = user[0] if user else 'User'

        cursor.execute('SELECT * FROM expenses WHERE user_id = ?', (session['user_id'],))
        expenses = cursor.fetchall()

        # Format the date in MM-DD-YYYY format
        for i, expense in enumerate(expenses):
            date_str = expense[2]  # Date is the 3rd column (index 2)
            try:
                # Try parsing the date and reformat it
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')  # Adjust format if needed
                expenses[i] = expense[:2] + (date_obj.strftime('%m-%d-%Y'),) + expense[3:]
            except ValueError:
                # If the date format is incorrect, leave it unchanged
                continue

    return render_template('dashboard.html', username=username, expenses=expenses)

# Route for adding an expense
@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    if request.method == 'POST':
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

        return redirect(url_for('dashboard'))  # Redirect to the dashboard after adding the expense

    return render_template('index.html')

# Route for logging out
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user_id from session to log out
    return redirect(url_for('login'))  # Redirect to the login page

if __name__ == '__main__':
    app.run(debug=True)