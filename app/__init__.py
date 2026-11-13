"""Build application instance"""
import os
import sqlite3
from flask import Flask, g, current_app

# Use environment variable for DATABASE_URL; fall back to SQLite for local dev.
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Render PostgreSQL format: postgres://user:pass@host:port/dbname
    # Parse it to create a SQLite-compatible path is NOT needed;
    # we'll use psycopg2 or the default adapter.
    # For simplicity, we'll use sqlite3 for local and note that
    # Render's free PostgreSQL requires an adapter.
    # ALTERNATIVE: Use a local SQLite file in Render's ephemeral filesystem
    # (data persists during the dyno lifecycle).
    DB_PATH = os.path.join(os.path.dirname(__file__), "..", "instance", "users.db")
else:
    DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "instance", "users.db"))

# Ensure instance directory exists
INSTANCE_DIR = os.path.dirname(DB_PATH)
os.makedirs(INSTANCE_DIR, exist_ok=True)


def create_app(db_path=DB_PATH):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "prod-key-change-me")
    app.config["DATABASE"] = db_path

    init_db(app)

    from .views import main_bp
    app.register_blueprint(main_bp)

    app.teardown_appcontext(close_db)
    return app


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    with app.app_context():
        db = sqlite3.connect(app.config["DATABASE"])
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                username   TEXT UNIQUE NOT NULL,
                email      TEXT NOT NULL,
                bio        TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        db.commit()
        db.close()
