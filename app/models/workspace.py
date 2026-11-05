# -*- coding: utf-8 -*-
"""
Workspace models — University Lab Code Vault, Peer Code-Duel rooms,
and ScopeSentry audits.

These are separate, opt-in tables. Flask's `create_all()` picks them up
automatically on boot (safe: it only creates missing tables), so no manual
migration is required.
"""
from datetime import datetime, timedelta

from app.extensions import db


class LabVaultEntry(db.Model):
    """A peer-sourced university lab solution (code + viva notes)."""
    __tablename__ = "lab_vault_entries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    subject = db.Column(db.String(120), nullable=False)      # e.g. "Data Structures"
    lab_no = db.Column(db.String(20))                        # e.g. "Lab 04"
    program = db.Column(db.String(240), nullable=False)       # program/exercise title
    language = db.Column(db.String(20), default="python")
    code = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text)                          # approach / comments
    viva_questions = db.Column(db.Text)                       # JSON list
    tags = db.Column(db.String(240))                          # comma-separated
    upvotes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("lab_vault_entries", lazy="dynamic"))


class DuelRoom(db.Model):
    """A 1v1 time problem-solving room."""
    __tablename__ = "duel_rooms"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(8), unique=True, nullable=False, index=True)
    creator_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    opponent_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    topic = db.Column(db.String(120), default="Mixed")
    duration_min = db.Column(db.Integer, default=15)
    status = db.Column(db.String(20), default="waiting")  # waiting | active | finished
    creator_score = db.Column(db.Integer, default=0)
    opponent_score = db.Column(db.Integer, default=0)
    question_ids = db.Column(db.Text)                      # JSON array of question ids
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    finished_at = db.Column(db.DateTime)

    @property
    def active(self):
        if self.status != "active":
            return False
        if not self.started_at:
            return False
        return datetime.utcnow() < self.started_at + timedelta(minutes=self.duration_min)

    def is_member(self, user_id):
        return user_id in (self.creator_id, self.opponent_id)


class ScopeSentryAudit(db.Model):
    """Stored audit results from the resume/README risk auditor."""
    __tablename__ = "scope_sentry_audits"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    source = db.Column(db.String(20), default="resume")   # resume | readme
    score = db.Column(db.Integer, default=0)              # 0–100 readiness
    findings = db.Column(db.Text)                          # JSON list of {severity, title, note}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("scope_sentry_audits", lazy="dynamic"))
