"""
Study Planner & Social models — daily goals, streaks, comments.
"""
from datetime import datetime

from app.extensions import db


class StudyGoal(db.Model):
    """Daily study goal for a user."""
    __tablename__ = "study_goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False)
    target_questions = db.Column(db.Integer, default=10)
    completed_questions = db.Column(db.Integer, default=0)
    target_minutes = db.Column(db.Integer, default=30)
    completed_minutes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("study_goals", lazy="dynamic",
                                                       cascade="all, delete-orphan"))


class StudyStreak(db.Model):
    """Tracks consecutive days of study activity."""
    __tablename__ = "study_streaks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_study_date = db.Column(db.Date, nullable=True)
    total_study_days = db.Column(db.Integer, default=0)

    user = db.relationship("User", backref=db.backref("study_streak", uselist=False,
                                                       cascade="all, delete-orphan"))


class UserComment(db.Model):
    """Comments on quiz results or questions."""
    __tablename__ = "user_comments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    target_type = db.Column(db.String(20), nullable=False)  # 'question' | 'result'
    target_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("comments", lazy="dynamic",
                                                       cascade="all, delete-orphan"))
