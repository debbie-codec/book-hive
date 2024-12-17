import os
from flask_login import current_user, login_required, login_user, LoginManager, logout_user
from flask import flash, render_template, redirect, session, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import User, Book, History
from sqlalchemy import or_
import random
import string

# Define directories for uploads
STATIC_FOLDER = 'static/uploads'
UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, 'users')  # For images
BOOK_FOLDER = os.path.join(STATIC_FOLDER, 'books')     # For PDFs

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BOOK_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['BOOK_FOLDER'] = BOOK_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}
ALLOWED_BOOK_EXTENSIONS = {'pdf', 'doc'}

def allowed_file(filename, allowed_extensions):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Initialize the login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route
@app.route('/')
def homepage():
    return render_template("landing.html", user=current_user)

@app.route('/index', endpoint="index")
@login_required
def home():
    # Fetch Top Books
    
    return render_template("index.html", user=current_user)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('profile'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')

# Profile route
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = current_user
    user_id = user.id
    if request.method == 'POST':
        # Retrieve files and form data
        book_file = request.files.get('book_file')
        book_cover = request.files.get('book_cover')
        title = request.form.get('title')
        author = request.form.get('author')
        genre = request.form.get('genre')

        # Validate and save files
        if book_file and allowed_file(book_file.filename, ALLOWED_BOOK_EXTENSIONS):
            book_file_path = os.path.join(app.config['BOOK_FOLDER'], book_file.filename)
            book_file.save(book_file_path)

        if book_cover and allowed_file(book_cover.filename, ALLOWED_IMAGE_EXTENSIONS):
            book_cover_path = os.path.join(app.config['UPLOAD_FOLDER'], book_cover.filename)
            book_cover.save(book_cover_path)

        # Save book to the database
        new_book = Book(title=title, author=author, genre=genre, book_url=book_file_path, book_cover=book_cover_path,
                         publication='None', keywords="None", description="None", word_counts='', pen_name='', ratings='', user_id=user_id)
        db.session.add(new_book)
        db.session.commit()

        flash(f"Book '{title}' by {author} uploaded successfully!")
        return redirect(request.url)

    # Retrieve books from the database
    books = Book.query.filter_by(user_id=user_id).all()
    return render_template('profile.html', user=current_user, uploaded_books=books)

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')

        # Check if email already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists. Try logging in.')
            return redirect(url_for('signup'))

        # Create new user
        new_user = User(email=email, name=name, password=generate_password_hash(password, method='scrypt'))
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template("signup.html")

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/edit_history/<int:history_id>', methods=['GET', 'POST'])
@login_required
def edit_history(history_id):
    history = History.query.get_or_404(history_id)
    if request.method == 'POST':
        history.video_title = request.form['video_title']
        db.session.commit()
        flash('History item updated successfully.')
        return redirect(url_for('profile'))
    return render_template('edit_history.html', history=history)

# Search route
@app.route('/search', methods=['GET'])
def search():
    search_query = request.args.get('q')  # Get the search query from the URL
    if search_query:
        results = Book.query.filter(
            (Book.title.ilike(f'%{search_query}%')) | (Book.author.ilike(f'%{search_query}%'))
        ).all()
    else:
        results = []
    top_books = Book.query.limit(5).all()
    suggestions = Book.query.limit(5).all()
    return render_template('index.html', results=results, search_query=search_query, top_books=top_books, suggestions=suggestions)

# History route
@app.route('/history')
@login_required
def history():
    user_id = current_user.id
    history_records = History.query.filter_by(user_id=user_id).all()
    return render_template('history.html', user=current_user, history_records=history_records)

# Route to delete an individual history item
@app.route('/delete_history_item/<int:history_id>', methods=['POST'])
@login_required
def delete_history_item(history_id):
    history_item = History.query.get_or_404(history_id)
    if history_item.user_id == current_user.id:
        db.session.delete(history_item)
        db.session.commit()
        flash('History item deleted successfully.')
    else:
        flash('You cannot delete this item.')
    return redirect(url_for('history'))

# Route to clear all search history
@app.route('/delete_all_history', methods=['POST'])
@login_required
def delete_all_history():
    History.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash('All history cleared.')
    return redirect(url_for('history'))

# Settings route
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def update_settings():
    if request.method == 'POST':
        name = request.form.get('name')
        bio = request.form.get('bio')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password and new_password == confirm_password:
            current_user.password = generate_password_hash(new_password)
        
        current_user.name = name
        current_user.bio = bio
        db.session.commit()

        flash('Settings updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('settings.html', user=current_user)

if __name__ == '__main__':
    app.run(debug=True)
