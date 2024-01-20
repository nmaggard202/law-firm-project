import os

from flask import (
    Blueprint,
    render_template,
    session,
    current_app,
    send_from_directory,
    redirect,
    url_for,
)

from db import User
from db import Appointment
from auth.decorators import requires_auth, requires_admin

webapp_bp = Blueprint("webapp", __name__, template_folder="templates")


@webapp_bp.route("/")
def home():
    """
    Home endpoint
    """
    name = "Guest"
    try:
        name = (
            User.query.filter_by(email=session.get("user").get("userinfo").get("email"))
            .first()
            .name
        )
    except Exception as e:
        name = "Guest"
    features = [
        {
            "title": "Expert Legal Team",
            "description": "Our firm boasts a team of highly experienced and knowledgeable lawyers who specialize in various fields of law. With their expertise, clients are assured of receiving informed, effective legal advice and representation.",
            "icon": "https://cdn.auth0.com/blog/hello-auth0/identity-providers-logo.svg",
        },
        {
            "title": "Client-Centric Approach",
            "description": "We prioritize our clients' needs and goals, offering personalized legal strategies tailored to each unique situation. Our commitment to client satisfaction ensures a more responsive and individualized service experience.",
            "icon": "https://cdn.auth0.com/blog/hello-auth0/mfa-logo.svg",
        },
        {
            "title": "Proven Track Record",
            "description": "Our firm has a history of successful case outcomes, demonstrating our ability to handle complex legal challenges effectively. This track record is a testament to our skill, dedication, and thorough understanding of the law.",
            "icon": "https://cdn.auth0.com/blog/hello-auth0/advanced-protection-logo.svg",
        },
        {
            "title": "Innovative Legal Solutions",
            "description": "We utilize the latest legal technologies and innovative approaches to stay ahead in the rapidly evolving legal landscape. This enables us to provide more efficient, cutting-edge solutions to our clients' legal issues.",
            "icon": "https://cdn.auth0.com/blog/hello-auth0/private-cloud-logo.svg",
        },
    ]

    return render_template("home.html", features=features, name=name)


@webapp_bp.route("/appointments")
@requires_auth
def appointments():
    """
    Appointments page lists the user's appointments. Shows all appointments if signed in as an admin.
    """
    user = User.query.filter_by(
        email=session.get("user").get("userinfo").get("email")
    ).first()
    if user.type == "admin":
        appointments = [a.serialize() for a in Appointment.query.all()]
    else:
        appointments = [
            a.serialize() for a in Appointment.query.filter_by(client=user.id)
        ] + [a.serialize() for a in Appointment.query.filter_by(lawyer=user.id)]
    return render_template(
        "appointments.html",
        user_profile=session.get("user").get("userinfo"),
        appointments=appointments,
        type=user.type,
        name=user.name,
    )


@webapp_bp.route("/appointments/<int:appointment_id>/")
@requires_auth
def appointment_details(appointment_id):
    """
    Appointments details page gives specific information, and notes, for the selected appointment.
    """
    user = User.query.filter_by(
        email=session.get("user").get("userinfo").get("email")
    ).first()
    appointment_non = Appointment.query.filter_by(id=appointment_id).first()
    appointment = appointment_non.serialize()
    if appointment_non.client != user.id and appointment_non.lawyer != user.id:
        return redirect(url_for("webapp.home"))
    return render_template(
        "appointment_details.html",
        appointment=appointment,
    )


@webapp_bp.route("/appointments/<int:appointment_id>/notes/")
@requires_auth
def appointment_note_create(appointment_id):
    """
    Appointment note create page provides a form for creating a new note for a given appointment.
    """
    user = User.query.filter_by(
        email=session.get("user").get("userinfo").get("email")
    ).first()
    appointment_non = Appointment.query.filter_by(id=appointment_id).first()
    appointment = appointment_non.serialize()
    if appointment_non.client != user.id and appointment_non.lawyer != user.id:
        return redirect(url_for("webapp.home"))
    return render_template(
        "appointment_note_create.html",
        appointment=appointment,
    )


@webapp_bp.route("/register/<int:user_id>/", methods=["GET", "POST"])
def set_name(user_id):
    """
    Set name page is for setting the name of a user who signed up with an email address instead of a social login.
    """
    user = User.query.filter_by(
        email=session.get("user").get("userinfo").get("email")
    ).first()
    if user.id != user_id:
        return redirect(url_for("webapp.home"))
    user_profile = session.get("user").get("userinfo")
    return render_template(
        "user_name.html",
        user=user_id,
        user_profile=user_profile,
    )


@webapp_bp.route("/appointments/schedule/")
@requires_auth
def appointment_schedule():
    """
    Appointments schedule page is for scheduling a new appointment.
    """
    users_filtered = []
    users = User.query.all()
    for user in users:
        if user.type == "lawyer":
            users_filtered.append(user)
    return render_template(
        "appointment_create.html",
        users=users_filtered,
    )


@webapp_bp.route("/admin")
@requires_auth
@requires_admin
def admin():
    """
    Admin page is used for managing the user's type as well as approving users.
    """
    users = User.query.all()
    return render_template("admin.html", users=users)


@webapp_bp.route("/uploads/<path:filename>/")
@requires_auth
def download_file(filename):
    """
    Endpoint for downloading file (from appointment note).
    """
    uploads = os.path.join(current_app.root_path, "uploads/")
    return send_from_directory(uploads, filename)


@webapp_bp.route("/pending")
def pending_approval():
    """
    Pending approval page is shown for users who are signed in but not approved by admin.
    """
    return render_template(
        "pending_approval.html",
        user_profile=session.get("user").get("userinfo"),
    )
