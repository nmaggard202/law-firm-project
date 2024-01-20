from flask import Blueprint, redirect, session, url_for, current_app
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from config import config
from db import db
from db import User

auth_bp = Blueprint("auth", __name__)

auth0_config = config["AUTH0"]
oauth = OAuth(current_app)

domain = auth0_config["DOMAIN"]
client_id = auth0_config["CLIENT_ID"]
client_secret = auth0_config["CLIENT_SECRET"]

oauth.register(
    "auth0",
    client_id=client_id,
    client_secret=client_secret,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{domain}/.well-known/openid-configuration",
)


@auth_bp.route("/login")
def login():
    """
    Redirects the user to the Auth0 Universal Login (https://auth0.com/docs/authenticate/login/auth0-universal-login)
    """
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("auth.callback", _external=True)
    )


@auth_bp.route("/signup")
def signup():
    """
    Redirects the user to the Auth0 Universal Login (https://auth0.com/docs/authenticate/login/auth0-universal-login)
    """
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("auth.callback", _external=True), screen_hint="signup"
    )


@auth_bp.route("/callback", methods=["GET", "POST"])
def callback():
    """
    Callback redirect from Auth0
    Creates user in database
    """
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    user_profile = session.get("user").get("userinfo")
    if User.query.filter_by(email=user_profile.get("email")).first() is None:
        try:
            new_user = User(
                name=user_profile.get("given_name")
                + " "
                + user_profile.get("family_name"),
                email=user_profile.get("email"),
                image=user_profile.get("picture"),
                type="client",
                key=user_profile.get("aud"),
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect("/appointments")
        except Exception as e:
            new_user = User(
                email=user_profile.get("email"),
                type="client",
                key=user_profile.get("aud"),
            )
            db.session.add(new_user)
            db.session.commit()
            user = User.query.filter_by(email=user_profile.get("email")).first().id
            return redirect("/register/" + str(user) + "/")
    return redirect("/appointments")


@auth_bp.route("/logout")
def logout():
    """
    Logs the user out of the session and from the Auth0 tenant
    """
    session.clear()
    return redirect(
        "https://"
        + domain
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("webapp.home", _external=True),
                "client_id": client_id,
            },
            quote_via=quote_plus,
        )
    )
