import string
import random
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, URL

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'  # This must match the function name below
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper function to generate random short code
def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# --- ROUTES ---

@app.route('/')
def login():
    # If user is already logged in, send them to the dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        login_user(user)
        return redirect(url_for('dashboard'))
    
    flash('Invalid username or password', 'danger')
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Validation Logic: Range 5 to 9
        if not (5 <= len(username) <= 9):
            flash('Username must be between 5 to 9 characters long', 'danger')
            return redirect(url_for('signup'))
        
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('This username already exists...', 'danger')
            return redirect(url_for('signup'))

        # Password Hashing (Secure Default)
        new_user = User(username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        
        flash('Signup successful! Please login.', 'success')
        return redirect(url_for('login')) # This matches def login() above
        
    return render_template('signup.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/shorten', methods=['POST'])
@login_required
def shorten():
    original_url = request.form.get('url')
    # Simple validation to ensure URL starts with http
    if not original_url.startswith(('http://', 'https://')):
        original_url = 'http://' + original_url
        
    short_code = generate_short_code()
    
    new_link = URL(original_url=original_url, short_code=short_code, owner=current_user)
    db.session.add(new_link)
    db.session.commit()
    
    return redirect(url_for('dashboard', shortened=short_code))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/<short_code>')
def redirect_to_url(short_code):
    link = URL.query.filter_by(short_code=short_code).first_or_404()
    return redirect(link.original_url)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)