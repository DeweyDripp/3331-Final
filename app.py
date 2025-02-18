from Flask import Flask, render_template, request, redirect, url_for, jsonify # type: ignore
import sqlite3
import os

app = Flask(__name__)

# Initialize the database and create the table if it doesn't exist
def init_db():
    db_path = 'db/expenses.db'
    if not os.path.exists(db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

# Route to display the index page with expenses
@app.route('/')
def index():
    conn = sqlite3.connect('db/expenses.db')
    c = conn.cursor()
    c.execute('SELECT * FROM expenses')
    expenses = c.fetchall()
    conn.close()
    return render_template('index.html', expenses=expenses)

# Route to add an expense
@app.route('/add_expense', methods=['POST'])
def add_expense():
    description = request.form['description']
    amount = float(request.form['amount'])
    category = request.form['category']
    date = request.form['date']

    conn = sqlite3.connect('db/expenses.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO expenses (description, amount, category, date)
        VALUES (?, ?, ?, ?)
    ''', (description, amount, category, date))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Route to get all expenses as JSON (for testing or front-end use)
@app.route('/get_expenses', methods=['GET'])
def get_expenses():
    conn = sqlite3.connect('db/expenses.db')
    c = conn.cursor()
    c.execute('SELECT * FROM expenses')
    expenses = c.fetchall()
    conn.close()
    return jsonify(expenses)

# Run the app
if __name__ == '__main__':
    init_db()  # Initialize the database on app start
    app.run(debug=True)