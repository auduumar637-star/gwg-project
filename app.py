from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

app = Flask(__name__)
app.secret_key = "gwg_secret_key"  # Used for session security

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
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

# Automatically initialize database tables on startup
with app.app_context():
    db.create_all()

# --- ROUTES ---

# 1. Main Landing Page (Index)
@app.route('/')
def index():
    return render_template('index.html')

# 2. Separate Products Overview Page
@app.route('/products')
def products():
    return render_template('products.html')

# 3. Handle Inquiry Form Submission
@app.route('/submit_order', methods=['POST'])
def submit_order():
    if request.method == 'POST':
        try:
            # Capture data exactly as defined by the HTML input 'name' fields
            new_inquiry = Inquiry(
                name=request.form['name'],
                phone=request.form['phone'],
                email=request.form['email'],
                details=request.form['details']
            )
            db.session.add(new_inquiry)
            db.session.commit()
            
            # Returns a clean confirmation string matching your UI intent
            return "<h1>Success!</h1><p>Your request has been sent.</p><a href='/'>Go Back</a>"
            
        except Exception as e:
            db.session.rollback()  # Cleans up the database thread session state on error
            return f"There was an issue saving your request: {str(e)}"

# 4. Manager Authentication Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Validation checks
        if username == 'admin' and password == 'gwg2024':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
            
        return "Invalid Credentials"
    return render_template('login.html')

# 5. Protected Admin Dashboard Viewing Hub
@app.route('/manager/dashboard')
def dashboard():
    # If session does not exist, kick user back to login gate
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    # Gather inquiries ordered from newest to oldest
    all_inquiries = Inquiry.query.order_by(Inquiry.date_posted.desc()).all()
    return render_template('dashboard.html', inquiries=all_inquiries)

# 6. Session Termination Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)