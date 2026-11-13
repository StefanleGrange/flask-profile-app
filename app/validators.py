"""Manual validation for the forms.
Validation is done on every post because client-side html checks are easily bypassed.
"""

import re

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

MIN_USERNAME_LEN = 3
MAX_USERNAME_LEN = 30
MAX_BIO_LEN = 160


def validate_profile(username, email, bio="", taken=None):
    """Return a dictionary of errors, if its empty the profile is valid"""
    errors = {}

    username = (username or "").strip()
    if len(username) < MIN_USERNAME_LEN:
        errors["username"] = f"Username must be at least {MIN_USERNAME_LEN} characters"
    elif len(username) > MAX_USERNAME_LEN:
        errors["username"] = f"Username must be {MAX_USERNAME_LEN} characters or fewer."
    elif not username.replace("_", "").isalnum():
        errors["username"] = "Letters, numbers and underscores only."
    elif taken and taken(username):
        errors["username"] = "That username is already taken."

    if not EMAIL_RE.match((email or "").strip()):
        errors["email"] = "Enter a valid email address (e.g. you@example.com)."

    if len(bio or "") > MAX_BIO_LEN:
        errors["bio"] = f"Bio must be {MAX_BIO_LEN} characters or fewer."

    return errors