from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
import string
import random
import re

app = Flask(__name__)
app.secret_key = "secret_key_for_session"

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class URLModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)

# Helper function: Generate short code
def generate_short_code():
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choice(chars) for _ in range(6))
        # Ensure the code doesn't already exist in the DB
        if not URLModel.query.filter_by(short_code=code).first():
            return code

# Helper function: Validate URL format
def is_valid_url(url):
    regex = re.compile(
        r'^https?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|' # domain
        r'localhost|' # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

@app.route('/', methods=['GET', 'POST'])
def home():
    shortened_url = None
    if request.method == 'POST':
        original = request.form['long_url']
        
        if is_valid_url(original):
            # Check if URL already exists to avoid duplicates
            found_url = URLModel.query.filter_by(original_url=original).first()
            if found_url:
                code = found_url.short_code
            else:
                code = generate_short_code()
                new_url = URLModel(original_url=original, short_code=code)
                db.session.add(new_url)
                db.session.commit()
            
            shortened_url = request.host_url + code
        else:
            flash("Invalid URL! Please include http:// or https://")
            
    return render_template('home.html', shortened_url=shortened_url)

@app.route('/history')
def history():
    all_urls = URLModel.query.all()
    return render_template('history.html', urls=all_urls)

@app.route('/<short_code>')
def redirect_to_url(short_code):
    url_entry = URLModel.query.filter_by(short_code=short_code).first_or_404()
    return redirect(url_entry.original_url)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)