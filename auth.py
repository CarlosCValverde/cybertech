from functools import wraps
from sqlalchemy.exc import IntegrityError

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
import models
import utils

from models import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


@bp.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user."""

    if request.method == "POST":
        
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        db = get_db()
        error = None

        if not email:
            error = "Email is required"
        elif not username:
            error = "Username is required"
        elif not password:
            error = "Password is required"
        elif not confirmation:
            error = "Confirmation is required"
        elif password != confirmation:
            error = "Passwords do not match"

        # Hash the password
        hashed_password = utils.hash(password)

        if error is None:
            try:
                new_user = models.User(
                    email=email,
                    username=username,
                    password=hashed_password
                )
                db.add(new_user)
                db.commit()
            except IntegrityError:
                # The email was already taken, which caused the
                # commit to fail. Show a validation error.
                error = f"Email {email} is already registered."
            else:
                # Log user in (keeps track of which user is logged in)
                session["user_id"] = new_user.id

                # Confirm registration
                flash("Your details have been added successfully!")
                # Success, go to the login page.
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        error = None

        if not email:
            error = "Email is required"
        elif not password:
            error = "Password is required"

        db = get_db()
        user = db.query(models.User).filter_by(email=email).first()

        if user is None:
            error = "Invalid Credentials."
        #if user is None:
        #    abort(404, description=f"Invalid Credentials.")
        if not utils.verify(password, user.password):
            error = "Invalid Credentials."
            #abort(404, description=f"Invalid Credentials.")
            
        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = user.id
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for("index"))