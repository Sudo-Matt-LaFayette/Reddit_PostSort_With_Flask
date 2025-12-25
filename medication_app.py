from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'medication-app-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medication_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='doctor')  # 'doctor' or 'student'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    medications = db.relationship('Medication', backref='creator', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    dosage_amount = db.Column(db.String(100))  # e.g., "500mg", "2 tablets"
    dosage_count = db.Column(db.Integer, default=1)  # Number of times
    frequency_type = db.Column(db.String(50), default='daily')  # 'daily', 'weekly', 'as_needed', 'custom'
    frequency_value = db.Column(db.Integer, default=1)  # e.g., 3 for "3 times"
    frequency_unit = db.Column(db.String(50), default='per day')  # e.g., "per day", "per week", "hours"
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def get_frequency_display(self):
        """Generate human-readable frequency string"""
        if self.frequency_type == 'as_needed':
            return 'As needed'
        elif self.frequency_type == 'custom':
            return f'{self.frequency_value} {self.frequency_unit}'
        else:
            if self.frequency_value == 1:
                if self.frequency_type == 'daily':
                    return 'Once daily'
                elif self.frequency_type == 'weekly':
                    return 'Once weekly'
            else:
                if self.frequency_type == 'daily':
                    return f'{self.frequency_value} times daily'
                elif self.frequency_type == 'weekly':
                    return f'{self.frequency_value} times weekly'
        return f'{self.frequency_value} {self.frequency_unit}'

    def __repr__(self):
        return f'<Medication {self.name}: {self.get_frequency_display()}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
@login_required
def index():
    """Dashboard with statistics"""
    total_medications = Medication.query.filter_by(created_by=current_user.id).count()
    
    # Count by frequency type
    frequency_stats = db.session.query(
        Medication.frequency_type,
        func.count(Medication.id)
    ).filter_by(created_by=current_user.id).group_by(Medication.frequency_type).all()
    
    # Recent medications
    recent_medications = Medication.query.filter_by(created_by=current_user.id)\
        .order_by(Medication.created_at.desc()).limit(5).all()
    
    # Daily medications count
    daily_count = Medication.query.filter_by(
        created_by=current_user.id,
        frequency_type='daily'
    ).count()
    
    return render_template('medication_dashboard.html',
                         total_medications=total_medications,
                         frequency_stats=dict(frequency_stats),
                         recent_medications=recent_medications,
                         daily_count=daily_count)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        if not username or not password:
            flash('Please provide both username and password.', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'doctor')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('register.html')
        
        # Create user
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/medications')
@login_required
def medications():
    """List all medications with search and filter"""
    search = request.args.get('search', '').strip()
    frequency_filter = request.args.get('frequency', '')
    
    query = Medication.query.filter_by(created_by=current_user.id)
    
    if search:
        query = query.filter(Medication.name.contains(search))
    
    if frequency_filter:
        query = query.filter_by(frequency_type=frequency_filter)
    
    medications_list = query.order_by(Medication.created_at.desc()).all()
    
    # Get frequency type counts for filter
    frequency_counts = db.session.query(
        Medication.frequency_type,
        func.count(Medication.id)
    ).filter_by(created_by=current_user.id).group_by(Medication.frequency_type).all()
    
    return render_template('medications.html',
                         medications=medications_list,
                         search_term=search,
                         frequency_filter=frequency_filter,
                         frequency_counts=dict(frequency_counts))

@app.route('/medications/new', methods=['GET', 'POST'])
@login_required
def new_medication():
    """Create a new medication"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        dosage_amount = request.form.get('dosage_amount', '').strip()
        dosage_count = request.form.get('dosage_count', '1')
        frequency_type = request.form.get('frequency_type', 'daily')
        frequency_value = request.form.get('frequency_value', '1')
        frequency_unit = request.form.get('frequency_unit', 'per day')
        notes = request.form.get('notes', '').strip()
        
        if not name:
            flash('Medication name is required.', 'error')
            return render_template('medication_form.html')
        
        try:
            dosage_count = int(dosage_count) if dosage_count else 1
            frequency_value = int(frequency_value) if frequency_value else 1
        except ValueError:
            flash('Invalid number format for dosage count or frequency.', 'error')
            return render_template('medication_form.html')
        
        medication = Medication(
            name=name,
            dosage_amount=dosage_amount,
            dosage_count=dosage_count,
            frequency_type=frequency_type,
            frequency_value=frequency_value,
            frequency_unit=frequency_unit,
            notes=notes,
            created_by=current_user.id
        )
        
        db.session.add(medication)
        db.session.commit()
        
        flash(f'Medication "{name}" added successfully!', 'success')
        return redirect(url_for('medications'))
    
    return render_template('medication_form.html')

@app.route('/medications/<int:medication_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_medication(medication_id):
    """Edit an existing medication"""
    medication = Medication.query.get_or_404(medication_id)
    
    # Check ownership
    if medication.created_by != current_user.id:
        flash('You do not have permission to edit this medication.', 'error')
        return redirect(url_for('medications'))
    
    if request.method == 'POST':
        medication.name = request.form.get('name', '').strip()
        medication.dosage_amount = request.form.get('dosage_amount', '').strip()
        medication.dosage_count = int(request.form.get('dosage_count', '1') or 1)
        medication.frequency_type = request.form.get('frequency_type', 'daily')
        medication.frequency_value = int(request.form.get('frequency_value', '1') or 1)
        medication.frequency_unit = request.form.get('frequency_unit', 'per day')
        medication.notes = request.form.get('notes', '').strip()
        medication.updated_at = datetime.utcnow()
        
        if not medication.name:
            flash('Medication name is required.', 'error')
            return render_template('medication_form.html', medication=medication)
        
        db.session.commit()
        flash(f'Medication "{medication.name}" updated successfully!', 'success')
        return redirect(url_for('medications'))
    
    return render_template('medication_form.html', medication=medication)

@app.route('/medications/<int:medication_id>/delete', methods=['POST'])
@login_required
def delete_medication(medication_id):
    """Delete a medication"""
    medication = Medication.query.get_or_404(medication_id)
    
    # Check ownership
    if medication.created_by != current_user.id:
        flash('You do not have permission to delete this medication.', 'error')
        return redirect(url_for('medications'))
    
    name = medication.name
    db.session.delete(medication)
    db.session.commit()
    
    flash(f'Medication "{name}" deleted successfully!', 'success')
    return redirect(url_for('medications'))

@app.route('/medications/<int:medication_id>')
@login_required
def medication_detail(medication_id):
    """View medication details"""
    medication = Medication.query.get_or_404(medication_id)
    
    # Check ownership
    if medication.created_by != current_user.id:
        flash('You do not have permission to view this medication.', 'error')
        return redirect(url_for('medications'))
    
    return render_template('medication_detail.html', medication=medication)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create a default admin user if no users exist
        if User.query.count() == 0:
            admin = User(username='admin', email='admin@example.com', role='doctor')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created: username='admin', password='admin123'")
    
    app.run(debug=True, port=5001)
