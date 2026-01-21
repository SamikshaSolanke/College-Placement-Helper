from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from extensions import db

auth = Blueprint('auth', __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    """Handles user login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
            
    return render_template("login.html")

@auth.route("/register", methods=["GET", "POST"])
def register():
    """Handles user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == "POST":
        email = request.form.get('email')
        display_name = request.form.get('displayName')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('auth.register'))

        try:
            new_user = User(email=email, display_name=display_name)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            login_user(new_user) # Log them in immediately
            flash('Account created successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating account: {e}', 'danger')
            
    return render_template("register.html")

@auth.route("/logout")
@login_required
def logout():
    """Logs out the current user."""
    logout_user()
    return redirect(url_for('auth.login'))
