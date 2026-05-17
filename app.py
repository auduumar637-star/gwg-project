import os
from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

app = Flask(__name__)
app.secret_key = "gwg_secret_key"  # Required for session handling

# --- DATABASE SETUP CONFIGURATION ---
# Checks for Render's Persistent Volume Disk URL, falls back to local SQLite if missing
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model for Customer Project Inquiries
class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# Automatically initialize database tables safely within app context
with app.app_context():
    db.create_all()

# --- WEB APP ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/submit_order', methods=['POST'])
def submit_order():
    if request.method == 'POST':
        try:
            new_inquiry = Inquiry(
                name=request.form['name'],
                phone=request.form['phone'],
                email=request.form['email'],
                details=request.form['details']
            )
            db.session.add(new_inquiry)
            db.session.commit()
            return "<h1>Success!</h1><p>Your request has been sent.</p><a href='/'>Go Back</a>"
        except Exception as e:
            db.session.rollback()
            return f"There was an issue saving your request: {str(e)}"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'gwg2024':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        return "Invalid Credentials"
    return render_template('login.html')

@app.route('/manager/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    all_inquiries = Inquiry.query.order_by(Inquiry.date_posted.desc()).all()
    return render_template('dashboard.html', inquiries=all_inquiries)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Dynamic Port handling required for live production deployment
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)