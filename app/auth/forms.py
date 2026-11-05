from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo
from app.models import User


def _normalize_email(value):
    """Trim whitespace and lowercase emails so login is case-insensitive."""
    return value.strip().lower() if value else value


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')

    def validate_email(self, field):
        field.data = _normalize_email(field.data)


class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')
    ])
    college = StringField('College/University', validators=[DataRequired(), Length(max=200)])
    submit = SubmitField('Register')

    def validate_email(self, field):
        field.data = _normalize_email(field.data)
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered. Please use a different email.')


class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Link')

    def validate_email(self, field):
        field.data = _normalize_email(field.data)


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(), EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')
