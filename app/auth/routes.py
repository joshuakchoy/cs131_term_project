from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from ..forms import LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm
from ..models import db, User
import os

bp = Blueprint("auth", __name__, url_prefix="/auth", template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("main.index"))
        else:
            flash("Invalid email or password.", "danger")
    return render_template("auth/login.html", form=form)

@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check for existing user
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered.", "danger")
            return redirect(url_for("auth.login"))
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already taken.", "danger")
            return redirect(url_for("auth.register"))
        
        # Create new user
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
            flash(f"Account created! Please log in with your credentials.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating account: {str(e)}", "danger")
            return redirect(url_for("auth.register"))
    
    # Show form validation errors
    if form.is_submitted() and not form.validate():
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "danger")
    
    return render_template("auth/register.html", form=form)

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))

@bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.get_reset_token()
            reset_url = url_for("auth.reset_password", token=token, _external=True)
            # TODO: Send email with reset link
            flash(f"Password reset link: {reset_url}", "info")
        else:
            flash("Email not found.", "danger")
    return render_template("auth/forgot_password.html", form=form)

@bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    
    user = User.verify_reset_token(token)
    if not user:
        flash("Invalid or expired token.", "danger")
        return redirect(url_for("auth.login"))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been reset. Please log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form)

