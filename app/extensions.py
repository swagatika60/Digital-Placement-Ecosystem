"""
Flask extension instances.

Import these from ``app.extensions`` anywhere in the project.  They are
initialised (``init_app``) later in the app factory inside ``app/__init__.py``.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."

csrf = CSRFProtect()
