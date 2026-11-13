"""SQLite Data-access layer for the Flask application."""

from . import get_db

def get_all_users():
    """Return all users from the database."""
    db = get_db()
    return db.execute("SELECT id, username, email, bio, created_at  FROM users ORDER BY id DESC"
                      ).fetchall()

def get_user_by_id(user_id):
    """Return a user by their ID."""
    db = get_db()
    return db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

def username_taken(username, exclude_id=None):
    """Check if a username is already taken. Exclude a specific user ID if provided (useful for updates)."""
    db = get_db()
    query = "SELECT id FROM users WHERE username = ?"
    params = (username,)
    if exclude_id is not None:
        query += " AND id != ?"
        params += (exclude_id,)
    return db.execute(query, params).fetchone() is not None

def create_user(username, email, bio=""):
    """Create a new user in the database."""
    db = get_db()
    cursor = db.execute(
        "INSERT INTO users (username, email, bio) VALUES (?, ?, ?)",
        (username, email, bio)
    )
    db.commit()
    return cursor.lastrowid  # Return the ID of the newly created user

def update_user(user_id, username, email, bio=""):
    """Update an existing user's information."""
    db = get_db()
    db.execute(
        "UPDATE users SET username = ?, email = ?, bio = ? WHERE id = ?",
        (username, email, bio, user_id),
    )
    db.commit()