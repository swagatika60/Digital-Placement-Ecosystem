"""
DSA Practice models — topics, questions, code submissions, and algorithm data.
"""
from datetime import datetime

from app.extensions import db


class DSATopic(db.Model):
    """A DSA topic like Arrays, Strings, Trees, etc."""
    __tablename__ = "dsa_topics"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    icon = db.Column(db.String(10))  # emoji
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)

    questions = db.relationship("DSAQuestion", backref="topic", lazy="dynamic")


class DSAQuestion(db.Model):
    """A coding question tied to a DSA topic and difficulty level."""
    __tablename__ = "dsa_questions"

    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("dsa_topics.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    difficulty = db.Column(db.String(10), nullable=False)  # easy | medium | hard
    description = db.Column(db.Text, nullable=False)
    examples = db.Column(db.Text)  # JSON: [{input, output, explanation}]
    constraints = db.Column(db.Text)
    starter_code = db.Column(db.Text)  # Python starter code
    solution_code = db.Column(db.Text)  # Reference solution
    test_cases = db.Column(db.Text)  # JSON: [{input, expected_output}]
    time_limit_ms = db.Column(db.Integer, default=2000)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class DSASubmission(db.Model):
    """A user's code submission for a DSA question."""
    __tablename__ = "dsa_submissions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey("dsa_questions.id"), nullable=False)
    code = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(20), default="python")
    status = db.Column(db.String(20), default="pending")  # pending | passed | failed | error
    output = db.Column(db.Text)
    test_results = db.Column(db.Text)  # JSON array of test results
    runtime_ms = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("dsa_submissions", lazy="dynamic"))
    question = db.relationship("DSAQuestion", backref="submissions")


class AlgorithmVisualizer(db.Model):
    """Stores algorithm data for visualization."""
    __tablename__ = "algorithm_visualizers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50))  # sorting | searching | graph | dp
    description = db.Column(db.Text)
    steps_json = db.Column(db.Text)  # JSON: array of visualization steps
    code_json = db.Column(db.Text)   # JSON: code lines with highlighting info
    best_time = db.Column(db.String(20))
    worst_time = db.Column(db.String(20))
    space = db.Column(db.String(20))
