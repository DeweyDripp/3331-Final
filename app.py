import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

# Initialize the database and create the table if it doesn't exist
def init_db():
    # Get the absolute path of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'db', 'expenses.db')

    # Ensure the directory exists
    if not os.path.exists(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path))
    
    print(f"Database path: {db_path}")
    
    # Connect to the SQLite database (it will create the db file if it doesn't exist)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Create the expenses table if it doesn't exist
    try:
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
        print("Table created or already exists.")
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")
    
    conn.close()

# Call init_db to initialize the database
init_db()

@app.route('/')
def index():
    # Get expenses from the database
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'db', 'expenses.db')
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    expenses = c.execute('SELECT * FROM expenses').fetchall()
    conn.close()

    return render_template('index.html', expenses=expenses)

@app.route('/add_expense', methods=['POST'])
def add_expense():
    # Get the data from the form
    description = request.form['description']
    amount = request.form['amount']
    category = request.form['category']
    date = request.form['date']

    # Insert the new expense into the database
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'db', 'expenses.db')

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        INSERT INTO expenses (description, amount, category, date)
        VALUES (?, ?, ?, ?)
    ''', (description, amount, category, date))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

@app.route('/delete_expense/<int:expense_id>', methods=['GET'])
def delete_expense(expense_id):
    # Delete the expense from the database
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'db', 'expenses.db')

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)