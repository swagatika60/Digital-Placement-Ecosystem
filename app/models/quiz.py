"""
Quiz domain models — Category, Question, QuizResult, QuestionBookmark.
"""
from datetime import datetime

from app.extensions import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))  # aptitude | technical
    description = db.Column(db.Text)

    questions = db.relationship("Question", backref="category", lazy=True)


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(500))
    option_b = db.Column(db.String(500))
    option_c = db.Column(db.String(500))
    option_d = db.Column(db.String(500))
    correct_answer = db.Column(db.String(1))  # A, B, C, or D
    explanation = db.Column(db.Text)
    difficulty = db.Column(db.String(20))  # easy | medium | hard
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class QuizResult(db.Model):
    __tablename__ = "quiz_results"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    score = db.Column(db.Integer)
    total_questions = db.Column(db.Integer)
    percentage = db.Column(db.Float)
    taken_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class QuestionBookmark(db.Model):
    """A question a user saved to review later."""
    __tablename__ = "question_bookmarks"
    __table_args__ = (
        db.UniqueConstraint("user_id", "question_id", name="uq_user_question"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    question = db.relationship("Question", backref=db.backref("bookmarked_by", lazy="dynamic"))
