"""Shared role-guard helpers for full admin/student role separation."""
from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def reject_admin():
    """Flash a message and send admins to their own panel (student pages only)."""
    flash('Admins cannot access student pages. Please use the Admin Panel.', 'warning')
    return redirect(url_for('admin.dashboard'))


def student_required(f):
    """Require the student role.

    Stack below @login_required on any student-facing route. Admins are
    redirected to the Admin Panel instead of seeing student content.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.role == 'admin':
            return reject_admin()
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Require the admin role.

    Stack below @login_required on any admin-only route. Non-admins are
    redirected to the home page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function
