"""
Application configuration.

Environment variables override class defaults.  Set ``FLASK_ENV`` to
switch between configs (defaults to ``development``).
"""
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Shared settings across all environments."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "placement-portal-secret-key-2024")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or (
        "sqlite:///" + os.path.join(basedir, "app", "placement.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True

    # GitHub (optional — raises API rate limit)
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")


class DevelopmentConfig(Config):
    """Local development defaults."""
    DEBUG = True


class ProductionConfig(Config):
    """Hardened settings for deployed environments."""
    DEBUG = False
    # In production you should set SECRET_KEY and DATABASE_URL via env vars.


class TestingConfig(Config):
    """Used by unit / integration tests."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
