from flask import Blueprint, render_template, redirect, url_for, flash, request, session, abort
from werkzeug.security import check_password_hash
from models import User, ROLE_ADMIN, ROLE_STUDENT
from forms import LoginForm, RegistrationForm, AdminLoginForm
from app import db
import functools

auth_bp = Blueprint('auth', __name__)

# Decorator for student login required
def student_login_required(func):
    @functools.wraps(func)
    def decorated_view(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return decorated_view

# Decorator for admin login required
def admin_login_required(func):
    @functools.wraps(func)
    def decorated_view(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.admin_login'))
        
        user = User.query.get(session['user_id'])
        if not user or user.role != ROLE_ADMIN:
            abort(403)  # Forbidden
        return func(*args, **kwargs)
    return decorated_view

@auth_bp.route('/')
def index():
    return render_template('index.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('auth.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data) and user.role == ROLE_STUDENT:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash('Login successful!', 'success')
            return redirect(url_for('courses.student_dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('auth.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=ROLE_STUDENT
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'user_id' in session and session.get('role') == ROLE_ADMIN:
        return redirect(url_for('admin.dashboard'))
    
    form = AdminLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data) and user.role == ROLE_ADMIN:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid email or password or not an admin account', 'danger')
    
    return render_template('auth/admin_login.html', form=form)
