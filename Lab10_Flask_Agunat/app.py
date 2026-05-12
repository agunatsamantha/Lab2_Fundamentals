# Step 1: Import necessary libraries and modules
import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename # Import for security

# Step 2: Import forms and models
from forms import RegisterForm, LoginForm
from models import db, User, Student

# Step 3: Initialize Flask app with instance-relative config
app = Flask(__name__, instance_relative_config=True)

# ADD'L EXER 2: File Upload Config
# Gagamitin ang 'static/images' folder na nasa directory mo
UPLOAD_FOLDER = os.path.join('static', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Step 5: Configuration settings
app.config['SECRET_KEY'] = 'my-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Step 6: Initialize database and login manager
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('home.html')

# About page
@app.route('/about')
def about():
    return render_template('about.html')

# Contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email already registered.")
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(form.password.data)
        # Default role is 'viewer'
        new_user = User(email=form.email.data, password=hashed_pw, role='viewer')
        
        db.session.add(new_user)
        db.session.commit()
        
        flash("Registration successful! Please login.")
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(f"Welcome back! Logged in as {user.role}.")
            return redirect(url_for('students'))
        else:
            flash("Invalid email or password.")
    return render_template('login.html', form=form)

# NEW: Profile Route para sa Image Upload at Display Name
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # 1. Update Display Name
        new_display_name = request.form.get('display_name')
        if new_display_name:
            current_user.display_name = new_display_name

        # 2. Handle Profile Picture Upload
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and allowed_file(file.filename):
                # Secure the filename and save it
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = secure_filename(f"user_{current_user.id}.{ext}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                # Update database field
                current_user.profile_pic = filename
        
        db.session.commit()
        flash("Profile updated successfully!")
        return redirect(url_for('profile'))

    return render_template('profile.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('home'))

@app.route('/students')
@login_required
def students():
    student_list = Student.query.order_by(Student.full_name).all()
    return render_template('students.html', students=student_list)

@app.route('/add-student', methods=['POST'])
@login_required
def add_student():
    name = request.form['name']
    email = request.form['email']
    student = Student(full_name=name, email=email)
    db.session.add(student)
    db.session.commit()
    flash("Student added successfully!")
    return redirect(url_for('students'))

@app.route('/delete-student/<int:id>')
@login_required
def delete_student(id):
    # Security Check: Admins only
    if current_user.role != 'admin':
        flash("Access Denied: You do not have Admin privileges!", "danger")
        return redirect(url_for('students'))
    
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash("Student record deleted.")
    return redirect(url_for('students'))

@app.errorhandler(404)
def page_not_found(e):    
    return render_template('404.html'), 404

if __name__ == '__main__':
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path, exist_ok=True)
        
    # Siguraduhin na ang upload folder ay nage-exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    with app.app_context():
        db.create_all()
        
    app.run(debug=True)