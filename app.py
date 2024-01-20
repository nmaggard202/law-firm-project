import json

from flask import Flask, render_template, request, session

from auth.decorators import requires_auth, requires_admin

from config import config
from webapp.views import webapp_bp
from auth.views import auth_bp

from db import db
from db import Appointment
from db import User
from db import Appointment_Note


def to_pretty_json(obj: dict) -> str:
    return json.dumps(obj, default=lambda o: o.__dict__, indent=4)


def page_not_found(e):
    return render_template("404.html"), 404


def success_response(data, code=200):
    return json.dumps(data), code


def failure_response(message, code=404):
    return json.dumps({"error": message}), code


def create_app():
    """
    Configuration of the app
    """
    app = Flask(__name__)

    app.secret_key = config["WEBAPP"]["SECRET_KEY"]

    app.jinja_env.filters["to_pretty_json"] = to_pretty_json

    app.register_error_handler(404, page_not_found)

    app.register_blueprint(auth_bp, url_prefix="/")
    app.register_blueprint(webapp_bp, url_prefix="/")

    db_filename = "appointment_tracker.db"

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = True
    app.config["UPLOAD_FOLDER"] = "/uploads/"
    app.config["MAX_CONTENT_PATH"] = 1073741824

    db.init_app(app)
    with app.app_context():
        db.create_all()

    return app


app = create_app()


# USERS
@app.route("/")
@app.route("/api/users/")
@requires_auth
def get_users():
    """
    Endpoint for getting all users.
    """
    users = [user.serialize() for user in User.query.all()]
    return success_response({"users": users})


@app.route("/api/users/", methods=["POST"])
@requires_auth
def create_user():
    """
    Endpoint for creating a new user.
    """
    body = json.loads(request.data)
    new_user = User(
        name=body.get("name"),
        email=body.get("email"),
        image=body.get("image"),
        type=body.get("type"),
        key=body.get("key"),
    )
    db.session.add(new_user)
    db.session.commit()
    return success_response(new_user.serialize(), 201)


@app.route("/api/users/<int:user_id>/")
@requires_auth
def get_user(user_id):
    """
    Endpoint for getting a user by id.
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!")
    return success_response(user.serialize())


@app.route("/api/users/<int:user_id>/approve/", methods=["POST"])
@requires_auth
def approve_user(user_id):
    """
    Endpoint for approving a user by id.
    """
    user = User.query.filter_by(id=user_id).first()
    user.approved = "True"
    db.session.commit()
    return success_response(user.serialize(), 201)


@app.route("/api/users/<int:user_id>/type/", methods=["POST"])
@requires_auth
def update_user_type(user_id):
    """
    Endpoint for updating a user's type by id.
    """
    type = request.form["type"]
    user = User.query.filter_by(id=user_id).first()
    user.type = type
    db.session.commit()
    return success_response(user.serialize(), 201)


@app.route("/api/users/<int:user_id>/type/admin/", methods=["POST"])
@requires_auth
def make_admin(user_id):
    """
    Endpoint for updating a user's type by id to admin.
    """
    user = User.query.filter_by(id=user_id).first()
    user.type = "admin"
    db.session.commit()
    return success_response(user.serialize(), 201)


@app.route("/api/users/<int:user_id>/name/", methods=["POST"])
def update_user_name(user_id):
    """
    Endpoint for updating a user's name by id.
    """
    name = request.form["name"]
    user = User.query.filter_by(id=user_id).first()
    user.name = name
    db.session.commit()
    return success_response(user.serialize(), 201)


@app.route("/api/users/<int:user_id>/delete/", methods=["POST"])
@requires_auth
def delete_user(user_id):
    """
    Endpoint for deleting an user by id.
    """
    user = User.query.filter_by(id=user_id).first()
    db.session.delete(user)
    db.session.commit()
    return success_response(user.serialize(), 201)


# APPOINTMENTS
@app.route("/")
@app.route("/api/appointments/")
@requires_auth
def get_appointments():
    """
    Endpoint for getting all appointments.
    """
    appointments = [appointment.serialize() for appointment in Appointment.query.all()]
    return success_response({"appointments": appointments})


@app.route("/api/appointments/", methods=["POST"])
@requires_auth
def create_appointment():
    """
    Endpoint for creating a new appointment.
    """
    new_appointment = Appointment(
        time=request.form["time"],
        location=request.form["location"],
        description=request.form["description"],
        client=User.query.filter_by(
            email=session.get("user").get("userinfo").get("email")
        )
        .first()
        .id,
        lawyer=request.form["lawyer"],
    )
    db.session.add(new_appointment)
    db.session.commit()
    return success_response(new_appointment.serialize(), 201)


@app.route("/api/appointments/<int:appointment_id>/")
@requires_auth
def get_appointment(appointment_id):
    """
    Endpoint for getting an appointment by id.
    """
    appointment = Appointment.query.filter_by(id=appointment_id).first()
    if appointment is None:
        return failure_response("Appointment not found!")
    return success_response(appointment.serialize())


@app.route("/api/appointments/user_<int:user_id>/")
@requires_auth
def get_appointments_by_user(user_id):
    """
    Endpoint for getting a user's appointments by user id.
    """
    appointments = [
        a.serialize() for a in Appointment.query.filter_by(client=user_id)
    ] + [a.serialize() for a in Appointment.query.filter_by(lawyer=user_id)]
    return success_response({"appointments": appointments})


@app.route("/api/appointments/<int:appointment_id>/delete/", methods=["POST"])
@requires_auth
def delete_appointment(appointment_id):
    """
    Endpoint for deleting an appointment by id.
    """
    appointment = Appointment.query.filter_by(id=appointment_id).first()
    db.session.delete(appointment)
    db.session.commit()
    return success_response(appointment.serialize(), 201)


@app.route("/api/appointments/<int:appointment_id>/approve/", methods=["POST"])
@requires_auth
def approve_appointment(appointment_id):
    """
    Endpoint for approving an appointment by id.
    """
    appointment = Appointment.query.filter_by(id=appointment_id).first()
    appointment.approved = "True"
    db.session.commit()
    return success_response(appointment.serialize(), 201)


# APPOINTMENT NOTES
@app.route("/api/appointments/<int:appointment_id>/notes/")
@requires_auth
def get_note_by_appointment(appointment_id):
    """
    Endpoint for getting an appointment's notes by appointment id.
    """
    appointment = Appointment.query.filter_by(id=appointment_id).first()
    notes = [n.serialize() for n in appointment.notes]
    return success_response({"notes": notes})


@app.route("/api/appointments/<int:appointment_id>/notes/", methods=["POST"])
@requires_auth
def create_note(appointment_id):
    """
    Endpoint for creating a new appointment note.
    """
    f = request.files["file"]
    f.save(dst="uploads/" + f.filename, buffer_size=1073741824)

    new_note = Appointment_Note(
        description=request.form["description"],
        file="uploads/" + f.filename,
    )
    db.session.add(new_note)

    appointment = Appointment.query.filter_by(id=appointment_id).first()
    appointment.notes.append(new_note)
    db.session.commit()
    return success_response(new_note.serialize(), 201)


@app.route("/api/appointments/<int:appointment_id>/notes/<int:note_id>/")
@requires_auth
def get_note_by_id(appointment_id, note_id):
    """
    Endpoint for getting an appointment by id.
    """
    note = Appointment_Note.query.filter_by(id=note_id).first()
    if note is None:
        return failure_response("Appointment note not found!")
    return success_response(note.serialize())


if __name__ == "__main__":
    app.run(host="0.0.0.0")
