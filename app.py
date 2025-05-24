from flask import Flask, request, render_template, redirect
import sqlite3

app = Flask(__name__)

# Initialize database
def init_db():
    with sqlite3.connect('contact.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS contact (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                number TEXT,
                subject TEXT,
                message TEXT
            )
        ''')
init_db()

# Route to display form
@app.route('/')
def index():
    return render_template('index.html')

# Handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['user_name']
    email = request.form['user_email']
    number = request.form['user_number']
    subject = request.form['subject']
    message = request.form['message']

    with sqlite3.connect('contact.db') as conn:
        conn.execute('''
            INSERT INTO contact (name, email, number, subject, message)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, email, number, subject, message))
    
    return "Form submitted successfully!"

if __name__ == '__main__':
    app.run(debug=True)
