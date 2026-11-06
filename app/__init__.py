import os
import sqlite3
from flask import Flask
from config import Config
from app.extensions import db, login_manager, csrf


# ── Auto-migration: add new columns to existing tables ──────────────
# SQLAlchemy's create_all() only creates new tables; it never adds
# columns to tables that already exist.  This function handles that
# gracefully so the app keeps working after model changes.
_MIGRATIONS = {
    "users": [
        ("password_reset_token", "VARCHAR(256)"),
        ("password_reset_expiry", "DATETIME"),
        ("email_verified", "BOOLEAN DEFAULT 1"),
        ("verification_token", "VARCHAR(256)"),
        ("verification_sent_at", "DATETIME"),
    ],
}


def _auto_migrate():
    """Add any missing columns to existing tables (safe no-ops if already present)."""
    db_uri = db.engine.url
    if "sqlite" not in str(db_uri):
        return  # only needed for SQLite file-based DBs

    db_path = db.engine.url.database
    if not db_path or not os.path.exists(db_path):
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    added = 0
    for table, columns in _MIGRATIONS.items():
        cursor.execute(f"PRAGMA table_info({table})")
        existing = {row[1] for row in cursor.fetchall()}
        for col_name, col_type in columns:
            if col_name not in existing:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}")
                added += 1
    conn.commit()
    conn.close()
    if added:
        print(f"[auto-migrate] Added {added} missing column(s) to the database.")


# Define user loader (imports inside the function to avoid circular imports)
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with the app instance
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints (imports stay inside the function to avoid circular imports)
    from app.auth.routes import auth
    from app.main.routes import main
    from app.quiz.routes import quiz
    from app.admin.routes import admin
    from app.dsa.routes import dsa_bp
    from app.workspace.routes import workspace

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(main)
    app.register_blueprint(quiz, url_prefix='/quiz')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(dsa_bp)
    app.register_blueprint(workspace)

    # Create database tables (create_all only creates missing tables)
    with app.app_context():
        db.create_all()
        _auto_migrate()

    # Globals available in every template
    @app.context_processor
    def inject_globals():
        from flask_login import current_user
        from app.models import QuestionBookmark
        bookmark_count = 0
        if current_user.is_authenticated:
            bookmark_count = QuestionBookmark.query.filter_by(user_id=current_user.id).count()
        return {'bookmark_count': bookmark_count}

    # Jinja filter: parse JSON strings stored in columns
    @app.template_filter('from_json')
    def from_json(value):
        import json
        if not value:
            return []
        try:
            return json.loads(value)
        except Exception:
            return []

    return app
