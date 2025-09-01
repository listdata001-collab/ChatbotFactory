from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from models import User
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Foydalanuvchi nomi va parol kiritilishi shart!', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            if user.is_active:
                login_user(user, remember=True)
                next_page = request.args.get('next')
                flash(f'Xush kelibsiz, {user.username}!', 'success')
                return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
            else:
                flash('Sizning hisobingiz bloklangan!', 'error')
        else:
            flash('Noto\'g\'ri foydalanuvchi nomi yoki parol!', 'error')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([username, email, password, confirm_password]):
            flash('Barcha maydonlar to\'ldirilishi shart!', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Parollar mos kelmaydi!', 'error')
            return render_template('register.html')
        
        if password and len(password) < 6:
            flash('Parol kamida 6 ta belgidan iborat bo\'lishi kerak!', 'error')
            return render_template('register.html')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Bu foydalanuvchi nomi band!', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Bu email band!', 'error')
            return render_template('register.html')
        
        # Create new user with test subscription (14 days)
        user = User()
        user.username = username
        user.email = email
        user.password_hash = generate_password_hash(password or '')
        user.language = 'uz'
        user.subscription_type = 'free'
        user.subscription_end_date = datetime.utcnow() + timedelta(days=14)
        user.is_active = True
        
        db.session.add(user)
        db.session.commit()
        
        flash('Ro\'yxatdan o\'tish muvaffaqiyatli! Endi tizimga kirishingiz mumkin.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Tizimdan muvaffaqiyatli chiqdingiz!', 'info')
    return redirect(url_for('main.index'))
