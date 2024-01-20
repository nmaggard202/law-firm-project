from flask import redirect, session, url_for
from functools import wraps
from db import User


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def requires_admin(f):
    """
    Use on routes that require a valid session as an administrator.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        user_profile = session.get("user").get("userinfo")
        user = User.query.filter_by(email=user_profile.get("email")).first()
        if user.type != "admin":
            return redirect(url_for("webapp.home"))

        return f(*args, **kwargs)

    return decorated


def requires_auth(f):
    """
    Use on routes that require a valid session as an approved user.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("user") is None:
            return redirect(url_for("auth.login"))
        user_profile = session.get("user").get("userinfo")
        user = User.query.filter_by(email=user_profile.get("email")).first()
        if user.approved != "True":
            return redirect("/pending")

        return f(*args, **kwargs)

    return decorated
