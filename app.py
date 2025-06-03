from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import webbrowser
import re
import imaplib
import email
from bs4 import BeautifulSoup
from datetime import datetime
from difflib import SequenceMatcher
from flask_socketio import SocketIO, emit

# Step 1: Create Flask App
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['DEBUG'] = True  # Debug mode ON
socketio = SocketIO(app)

# Step 2: Setup Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Step 3: Configure logging to hide normal 200/302 logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Step 4: Create Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    gmail_app_password = db.Column(db.String(200), nullable=False)

class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(300))
    body = db.Column(db.Text)
    received_date = db.Column(db.DateTime)
    is_spam = db.Column(db.Boolean)
    image_count = db.Column(db.Integer)

# Step 5: Utility Functions
def is_spam_email(subject, body):
    spam_keywords = ['lottery', 'win', 'free', 'prize', 'money', 'urgent']
    text = f"{subject} {body}".lower()
    return any(word in text for word in spam_keywords)

def count_images_in_body(body):
    return len(re.findall(r'<img\s', body))

def similar_subjects(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def group_emails_by_similarity(emails, threshold=0.7):
    groups = []
    used = set()
    for i, email1 in enumerate(emails):
        if i in used:
            continue
        group = [email1]
        used.add(i)
        for j, email2 in enumerate(emails[i+1:], start=i+1):
            if j not in used and similar_subjects(email1.subject, email2.subject) > threshold:
                group.append(email2)
                used.add(j)
        groups.append(group)
    return groups

def fetch_emails_from_gmail(user_email, app_password, max_emails=20):
    emails = []
    try:
        imap_server = 'imap.gmail.com'
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(user_email, app_password)
        mail.select('inbox')

        status, messages = mail.search(None, 'ALL')
        email_ids = messages[0].split()

        for eid in email_ids[-max_emails:][::-1]:
            res, msg = mail.fetch(eid, "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):
                    msg_obj = email.message_from_bytes(response[1])
                    subject = msg_obj.get("Subject", "")
                    date = msg_obj.get("Date", "")
                    received_date = None
                    try:
                        received_date = datetime.strptime(date[:31], '%a, %d %b %Y %H:%M:%S %z')
                    except Exception:
                        received_date = datetime.now()

                    body = ""
                    if msg_obj.is_multipart():
                        for part in msg_obj.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                try:
                                    body = part.get_payload(decode=True).decode()
                                    break
                                except Exception:
                                    pass
                            elif content_type == "text/html" and "attachment" not in content_disposition:
                                try:
                                    html_body = part.get_payload(decode=True).decode()
                                    soup = BeautifulSoup(html_body, "html.parser")
                                    body = soup.get_text()
                                    break
                                except Exception:
                                    pass
                    else:
                        try:
                            body = msg_obj.get_payload(decode=True).decode()
                        except Exception:
                            body = ""

                    emails.append({
                        'subject': subject,
                        'body': body,
                        'received_date': received_date
                    })
        mail.logout()

    except Exception as e:
        print("Error fetching emails:", e)

    return emails

# Step 6: Flask Routes
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    emails = Email.query.filter_by(user_id=session['user_id']).all()
    email_groups = group_emails_by_similarity(emails)

    spam_count = sum(email.is_spam for email in emails)
    not_spam_count = len(emails) - spam_count
    total_images = sum(email.image_count for email in emails)

    return render_template('dashboard.html',
                           email_groups=email_groups,
                           spam_count=spam_count,
                           not_spam_count=not_spam_count,
                           total_images=total_images)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        gmail_password = request.form['gmail_password']

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Email already registered. Please login.', 'danger')
            return redirect(url_for('login'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(email=email, password=hashed_password, gmail_app_password=gmail_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registered successfully! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_email'] = user.email
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/fetch_emails')
def fetch_emails():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('dashboard'))

    fetched_emails = fetch_emails_from_gmail(user.email, user.gmail_app_password)

    for email_data in fetched_emails:
        subject = email_data['subject']
        body = email_data['body']
        received_date = email_data['received_date']

        spam = is_spam_email(subject, body)
        image_count = count_images_in_body(body)

        new_email = Email(user_id=user.id, subject=subject, body=body,
                          received_date=received_date, is_spam=spam, image_count=image_count)
        db.session.add(new_email)

    db.session.commit()

    flash(f'Fetched and saved {len(fetched_emails)} new emails!', 'success')
    return redirect(url_for('dashboard'))

# Step 7: Real-time update using Socket.IO
@socketio.on('request_email_data')
def handle_request_email_data():
    if 'user_id' in session:
        emails = Email.query.filter_by(user_id=session['user_id']).all()
        spam_count = sum(email.is_spam for email in emails)
        not_spam_count = len(emails) - spam_count
        total_images = sum(email.image_count for email in emails)

        emit('update_email_data', {
            'spam_emails': spam_count,
            'not_spam_emails': not_spam_count,
            'image_emails': total_images
        })

# Step 8: Initialize Database
with app.app_context():
    db.create_all()

# Step 9: Run App
if __name__ == '__main__':
    try:
        # Auto open in Microsoft Edge
        edge_path = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe %s"
        webbrowser.get(edge_path).open('http://127.0.0.1:5000/')
    except webbrowser.Error:
        print("Could not open Edge browser. Please open http://127.0.0.1:5000/ manually.")

    socketio.run(app, host='0.0.0.0', port=5000)
