"""
StudentActivity model — activity logging for user actions.
"""
from datetime import datetime

from app.extensions import db


class StudentActivity(db.Model):
    __tablename__ = "student_activities"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    activity_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
