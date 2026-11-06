from urllib.parse import urlsplit
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.auth.forms import LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm
from app.models import User
from app.extensions import db


def _safe_next_url(target):
    """Allow only same-site relative URLs for the ?next= redirect (blocks open redirects)."""
    if not target:
        return None
    parts = urlsplit(target)
    if parts.scheme or parts.netloc or not target.startswith('/'):
        return None
    return target

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            # Block unverified users (skip check for admin accounts)
            if not user.email_verified and user.role != 'admin':
                # Resend a fresh verification token so the user can verify
                token = user.generate_verification_token()
                db.session.commit()
                verify_url = url_for('auth.verify_email', token=token, _external=True)
                flash('Your email is not verified. Please verify before logging in.', 'warning')
                return render_template('auth/verify_pending.html',
                                       email=user.email, verify_url=verify_url)

            login_user(user, remember=form.remember.data)
            flash('Login successful!', 'success')

            # Strict role-based landing: admins go to the Admin Panel,
            # students go to their Dashboard. The ?next= target (from a
            # login-required redirect) is honored only when it is same-site
            # AND belongs to the user's own role.
            next_page = _safe_next_url(request.args.get('next'))
            if next_page:
                is_admin_target = next_page.startswith('/admin/')
                if (user.role == 'admin' and is_admin_target) or (user.role == 'student' and not is_admin_target):
                    return redirect(next_page)
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('auth/login.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Handle student registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        college = form.college.data

        # Create new user (default role is 'student', email normalized)
        user = User(name=name, email=form.email.data, college=college, role='student')
        user.set_password(password)
        user.email_verified = False
        token = user.generate_verification_token()

        db.session.add(user)
        db.session.commit()

        # Show verification link (in production, this would be sent via email)
        verify_url = url_for('auth.verify_email', token=token, _external=True)
        flash('Registration successful! Please verify your email to continue.', 'success')
        return render_template('auth/verify_pending.html',
                               email=form.email.data, verify_url=verify_url)

    return render_template('auth/register.html', form=form)


@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password — generate a reset token."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            db.session.commit()
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            # In production you would email this link.  For now we show it
            # on-screen so the feature works without an SMTP server.
            flash('If an account with that email exists, a password reset link has been generated.', 'success')
            return render_template('auth/reset_link_display.html',
                                   reset_url=reset_url, email=form.email.data)
        else:
            # Always show the same message to avoid email enumeration
            flash('If an account with that email exists, a password reset link has been generated.', 'success')
            return render_template('auth/reset_link_display.html',
                                   reset_url=None, email=form.email.data)

    return render_template('auth/forgot_password.html', form=form)


@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset via token."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    # Find the user with this token
    user = User.query.filter_by(password_reset_token=token).first()
    if not user or not user.verify_reset_token(token):
        flash('Invalid or expired reset link. Please request a new one.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.new_password.data)
        user.clear_reset_token()
        db.session.commit()
        flash('Your password has been reset successfully! Please log in with your new password.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form, token=token)


@auth.route('/verify-email/<token>')
def verify_email(token):
    """Verify email address via token."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    user = User.query.filter_by(verification_token=token).first()
    if not user or not user.verify_email_token(token):
        flash('Invalid or expired verification link. Please log in to resend.', 'danger')
        return redirect(url_for('auth.login'))

    user.verify_email()
    db.session.commit()
    flash('Email verified successfully! You can now log in.', 'success')
    return redirect(url_for('auth.login'))


@auth.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    """Resend the email verification link."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    from app.auth.forms import ForgotPasswordForm
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and not user.email_verified and user.role != 'admin':
            token = user.generate_verification_token()
            db.session.commit()
            verify_url = url_for('auth.verify_email', token=token, _external=True)
            return render_template('auth/verify_pending.html',
                                   email=form.email.data, verify_url=verify_url)
        else:
            flash('If an unverified account exists with that email, a new link has been generated.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('auth/resend_verification.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))
