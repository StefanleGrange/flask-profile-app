"""HTTP Routes"""

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, abort,
)
from .models import (
    get_all_users, get_user_by_id, create_user, update_user, username_taken
)
from .validators import validate_profile

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    """Dynamically render all stored users"""
    users = get_all_users()
    return render_template("index.html", users = users)

@main_bp.route("/register", methods=["GET", "POST"])
def register():
    """Show the registration form and Validate on POST"""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        bio = request.form.get("bio", "").strip()

        # Server-side validation gate
        errors = validate_profile(username, email, bio,
                                  taken=username_taken)
        if errors:
            # Render errors and the submitted values so nothing is lost.
            return render_template("register.html", errors=errors,
                                   form={"username": username,
                                         "email": email, "bio": bio}), 400

        new_id = create_user(username, email, bio)
        flash("Registration successful!", "success")

        return redirect(url_for("main.profile", user_id=new_id))

    return render_template("register.html", errors={}, form={})

@main_bp.route("/users/<int:user_id>")
def profile(user_id):
    """Single-user detail page (404 if the id doesn't exist)."""
    user = get_user_by_id(user_id)
    if user is None:
        abort(404)
    return render_template("profile.html", user=user)

@main_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
def update(user_id):
    """GET preloads the form with current data; POST validates and saves."""
    user = get_user_by_id(user_id)
    if user is None:
        abort(404)

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        bio = request.form.get("bio", "").strip()

        errors = validate_profile(
            username, email, bio,
            taken=lambda u: username_taken(u, exclude_id=user_id),
            )
        if errors:
            return render_template("update.html", user=user, errors=errors,
                                   form={"username": username,
                                         "email": email, "bio": bio}), 400

        update_user(user_id, username, email, bio)
        flash("Profile updated.", "success")
        return redirect(url_for("main.profile", user_id=user_id))

    return render_template("update.html", user=user, errors={}, form=dict(user))