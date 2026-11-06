"""
User model — authentication, roles, password management,
email verification, and password-reset tokens.
"""
from datetime import datetime, timedelta

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default="student")  # admin | student
    college = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Password-reset
    password_reset_token = db.Column(db.String(256), nullable=True)
    password_reset_expiry = db.Column(db.DateTime, nullable=True)

    # Email verification
    email_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(256), nullable=True)
    verification_sent_at = db.Column(db.DateTime, nullable=True)

    # ── Password helpers ──────────────────────────────────────────
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    # ── Password-reset token ──────────────────────────────────────
    def generate_reset_token(self) -> str:
        """Generate a secure reset token that expires in 30 minutes."""
        self.password_reset_token = secrets.token_urlsafe(48)
        self.password_reset_expiry = datetime.utcnow() + timedelta(minutes=30)
        return self.password_reset_token

    def verify_reset_token(self, token: str) -> bool:
        if not self.password_reset_token or not self.password_reset_expiry:
            return False
        if datetime.utcnow() > self.password_reset_expiry:
            self.clear_reset_token()
            return False
        return secrets.compare_digest(self.password_reset_token, token)

    def clear_reset_token(self) -> None:
        self.password_reset_token = None
        self.password_reset_expiry = None

    # ── Email verification token ──────────────────────────────────
    def generate_verification_token(self) -> str:
        """Generate a verification token that expires in 24 hours."""
        self.verification_token = secrets.token_urlsafe(48)
        self.verification_sent_at = datetime.utcnow()
        return self.verification_token

    def verify_email_token(self, token: str) -> bool:
        if not self.verification_token or not self.verification_sent_at:
            return False
        if datetime.utcnow() > self.verification_sent_at + timedelta(hours=24):
            return False
        return secrets.compare_digest(self.verification_token, token)

    def verify_email(self) -> None:
        self.email_verified = True
        self.verification_token = None
        self.verification_sent_at = None
