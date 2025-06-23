import os
from flask import Flask, request, render_template, redirect, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure PostgreSQL database
database_url = os.environ.get("DATABASE_URL")
if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    # Fallback for development
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///contact.db"

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

# Contact model
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    number = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Contact {self.name}>'

# Create tables
with app.app_context():
    db.create_all()

# Route to display form
@app.route('/')
def index():
    return render_template('index.html')

# Handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    try:
        name = request.form['user_name']
        email = request.form['user_email']
        number = request.form['user_number']
        subject = request.form['subject']
        message = request.form['message']

        # Create new contact entry
        new_contact = Contact(
            name=name,
            email=email,
            number=number,
            subject=subject,
            message=message
        )
        
        # Add to database
        db.session.add(new_contact)
        db.session.commit()
        
        return render_template('success.html')
    
    except Exception as e:
        db.session.rollback()
        print(f"Error submitting form: {e}")
        return "An error occurred while submitting your message. Please try again.", 500

# Route to serve CV
@app.route('/download-cv')
def download_cv():
    return send_from_directory('static', 'cv.html', as_attachment=True, download_name='Ashutosh_Sahu_CV.html')

# Admin route to view contact submissions
@app.route('/admin/contacts')
def admin_contacts():
    try:
        contacts = Contact.query.order_by(Contact.created_at.desc()).all()
        return render_template('admin_contacts.html', contacts=contacts)
    except Exception as e:
        print(f"Error fetching contacts: {e}")
        return "Database connection error", 500
if __name__ == '__main__':
    app.run(debug=True)
