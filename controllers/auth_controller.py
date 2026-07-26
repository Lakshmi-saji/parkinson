from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        gender = request.form.get('gender', '')
        age_str = request.form.get('age', '')

        # Validation
        errors = []
        if not name or len(name) < 2:
            errors.append('Name must be at least 2 characters.')
        if not email or '@' not in email:
            errors.append('Please enter a valid email address.')
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm:
            errors.append('Passwords do not match.')
        if age_str:
            age = int(age_str)
            if age < 1 or age > 120:
                errors.append('Please enter a valid age (1-120).')

        if errors:
            for err in errors:
                flash(err, 'error')
            return render_template('register.html', form_data=request.form)

        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists.', 'error')
            return render_template('register.html', form_data=request.form)

        user = User(
            name=name,
            email=email,
            gender=gender,
            age=int(age_str) if age_str else None,
            role='registered'
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user, remember=True)
        flash(f'Welcome, {user.name}! Your account has been created.', 'success')
        return redirect(url_for('main.questionnaire'))

    return render_template('register.html', form_data={})


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.questionnaire'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(next_page or url_for('main.questionnaire'))
        else:
            flash('Invalid email or password. Please try again.', 'error')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/guest')
def guest():
    """Allow guest access without registration."""
    session['is_guest'] = True
    return redirect(url_for('main.questionnaire'))
