# # from flask import Flask, render_template, request, jsonify
# # from flask_socketio import SocketIO, emit
# # from flask_login import LoginManager, login_user, login_required, current_user, logout_user
# # from werkzeug.security import generate_password_hash, check_password_hash
# # from models import User  # assuming User model is defined
# # from utils.db_helper import get_email_stats  # assuming function to fetch stats
# # import time

# # app = Flask(__name__)
# # app.config['SECRET_KEY'] = 'your_secret_key'
# # socketio = SocketIO(app)

# # login_manager = LoginManager(app)

# # # Dummy function to fetch email stats
# # def fetch_email_data():
# #     # Simulate fetching real-time email stats
# #     time.sleep(2)  # Simulate delay from DB/API
# #     return get_email_stats(current_user.email)  # You should adjust this to your DB logic

# # @app.route('/')
# # @login_required
# # def home():
# #     return render_template('dashboard.html', email=current_user.email)

# # @app.route('/dashboard')
# # @login_required
# # def dashboard():
# #     # Initial email stats
# #     total_emails, spam_emails, not_spam_emails, image_emails = fetch_email_data()
# #     return render_template('dashboard.html', 
# #                            email=current_user.email,
# #                            total_emails=total_emails, 
# #                            spam_emails=spam_emails,
# #                            not_spam_emails=not_spam_emails,
# #                            image_emails=image_emails)

# # # SocketIO event to send real-time email data
# # @socketio.on('request_email_data')
# # def handle_email_data():
# #     email_data = fetch_email_data()
# #     emit('update_email_data', email_data)  # Send real-time data to client

# # # To handle user login
# # @app.route('/login', methods=['GET', 'POST'])
# # def login():
# #     # Your login logic
# #     pass

# # @app.route('/logout')
# # @login_required
# # def logout():
# #     logout_user()
# #     return redirect(url_for('login'))

# # if __name__ == '__main__':
# #     socketio.run(app, debug=True)
# from flask import Flask, render_template, redirect, url_for, request, session
# from flask_socketio import SocketIO, emit
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_sqlalchemy import SQLAlchemy

# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your_secret_key'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Use your database URI here
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)
# socketio = SocketIO(app)

# # User model for authentication
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(200), nullable=False)

# # Example functions for fetching email data
# def get_email_data():
#     # In a real project, this would interact with your database
#     total_emails = 1200
#     spam_emails = 300
#     not_spam_emails = 900
#     image_emails = 50
#     return total_emails, spam_emails, not_spam_emails, image_emails

# @app.route('/dashboard')
# def dashboard():
#     # Get email data
#     total_emails, spam_emails, not_spam_emails, image_emails = get_email_data()
    
#     if 'email' not in session:
#         return redirect(url_for('login'))
    
#     return render_template('dashboard.html', 
#                            total_emails=total_emails,
#                            spam_emails=spam_emails,
#                            not_spam_emails=not_spam_emails,
#                            image_emails=image_emails,
#                            email=session['email'])

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if 'email' in session:
#         return redirect(url_for('dashboard'))
    
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         user = User.query.filter_by(email=email).first()
        
#         if user and check_password_hash(user.password, password):
#             session['email'] = user.email
#             return redirect(url_for('dashboard'))
#         else:
#             return 'Invalid credentials, please try again.'

#     return render_template('login.html')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if 'email' in session:
#         return redirect(url_for('dashboard'))
    
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         hashed_password = generate_password_hash(password, method='sha256')
        
#         new_user = User(email=email, password=hashed_password)
#         db.session.add(new_user)
#         db.session.commit()
        
#         return redirect(url_for('login'))
    
#     return render_template('register.html')

# @app.route('/logout')
# def logout():
#     session.pop('email', None)
#     return redirect(url_for('login'))

# # Socket.IO for real-time data
# @socketio.on('request_email_data')
# def handle_email_data():
#     total_emails, spam_emails, not_spam_emails, image_emails = get_email_data()
#     emit('update_email_data', {
#         'total_emails': total_emails,
#         'spam_emails': spam_emails,
#         'not_spam_emails': not_spam_emails,
#         'image_emails': image_emails
#     })

# if __name__ == '__main__':
#     db.create_all()  # Creates the database if it doesn't exist
#     socketio.run(app, debug=True)
from flask import Flask, render_template, redirect, url_for, request, session
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app)

# User model for authentication
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Email model to simulate email storage
class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    date_received = db.Column(db.DateTime, default=datetime.utcnow)
    is_spam = db.Column(db.Boolean, default=False)
    has_image = db.Column(db.Boolean, default=False)

# Dummy similarity classifier
def classify_email(subject, body):
    keywords_spam = ['lottery', 'prize', 'win', 'free', 'money']
    combined_text = f"{subject.lower()} {body.lower()}"
    is_spam = any(keyword in combined_text for keyword in keywords_spam)
    has_image = random.choice([True, False])  # Random for now
    return is_spam, has_image

# Insert dummy emails for testing
def insert_dummy_emails(user_email):
    subjects = ["Win a lottery!", "Meeting schedule", "Free Prize", "Invoice attached", "Hello friend"]
    bodies = [
        "Congratulations, you've won a prize!",
        "Let's schedule the meeting tomorrow.",
        "Claim your free prize now!",
        "Attached is your invoice for last month.",
        "Hope you are doing well!"
    ]
    for _ in range(20):
        subject = random.choice(subjects)
        body = random.choice(bodies)
        is_spam, has_image = classify_email(subject, body)
        email = Email(user_email=user_email, subject=subject, body=body, is_spam=is_spam, has_image=has_image)
        db.session.add(email)
    db.session.commit()

# Fetch emails by date range
def get_email_data(user_email, from_date=None, to_date=None):
    query = Email.query.filter_by(user_email=user_email)

    if from_date and to_date:
        query = query.filter(Email.date_received.between(from_date, to_date))

    emails = query.all()
    total_emails = len(emails)
    spam_emails = len([email for email in emails if email.is_spam])
    not_spam_emails = total_emails - spam_emails
    image_emails = len([email for email in emails if email.has_image])

    return total_emails, spam_emails, not_spam_emails, image_emails

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'email' not in session:
        return redirect(url_for('login'))

    total_emails, spam_emails, not_spam_emails, image_emails = get_email_data(session['email'])

    return render_template('dashboard.html',
                           total_emails=total_emails,
                           spam_emails=spam_emails,
                           not_spam_emails=not_spam_emails,
                           image_emails=image_emails,
                           email=session['email'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'email' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['email'] = user.email

            # Optional: Insert dummy emails after login if empty
            if Email.query.filter_by(user_email=user.email).count() == 0:
                insert_dummy_emails(user.email)

            return redirect(url_for('dashboard'))
        else:
            return 'Invalid credentials, please try again.'

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'email' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')

        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

# Real-time SocketIO event
@socketio.on('request_email_data')
def handle_email_data(data):
    if 'email' not in session:
        return

    from_date_str = data.get('from_date')
    to_date_str = data.get('to_date')

    from_date = datetime.strptime(from_date_str, '%Y-%m-%d') if from_date_str else None
    to_date = datetime.strptime(to_date_str, '%Y-%m-%d') if to_date_str else None

    total_emails, spam_emails, not_spam_emails, image_emails = get_email_data(session['email'], from_date, to_date)

    emit('update_email_data', {
        'total_emails': total_emails,
        'spam_emails': spam_emails,
        'not_spam_emails': not_spam_emails,
        'image_emails': image_emails
    })

# Start the server
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if not exist
    socketio.run(app, debug=True)
