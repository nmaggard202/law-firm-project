from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

association_table = db.Table(
    "association",
    db.Model.metadata,
    db.Column("appointment_id", db.Integer, db.ForeignKey("appointment.id")),
    db.Column("appointment_note_id", db.Integer, db.ForeignKey("appointment_note.id")),
)


class User(db.Model):
    """
    User Model
    """

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=True)
    type = db.Column(db.String, nullable=False)
    approved = db.Column(db.String, nullable=False)
    key = db.Column(db.String, nullable=False)

    def __init__(self, **kwargs):
        """
        Initialize a User object
        """
        self.name = kwargs.get("name", "")
        self.email = kwargs.get("email", "")
        self.image = kwargs.get("image", "")
        self.type = kwargs.get("type", "")
        self.approved = "False"
        self.key = kwargs.get("key")

    def check_user_type(self):
        """
        Returns the user type.
        """
        return self.type

    def serialize(self):
        """
        Serialize a User object.
        """
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "image": self.image,
            "type": self.type,
            "approved": self.approved,
        }


class Appointment(db.Model):
    """
    Appointment Model.
    """

    __tablename__ = "appointment"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    approved = db.Column(db.String, nullable=False)
    client = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    lawyer = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    notes = db.relationship(
        "Appointment_Note", secondary=association_table, back_populates="appointment"
    )

    def __init__(self, **kwargs):
        """
        Initialize an Appointment object.
        """
        self.time = kwargs.get("time", "")
        self.location = kwargs.get("location", "")
        self.description = kwargs.get("description", "")
        self.client = kwargs.get("client", "")
        self.lawyer = kwargs.get("lawyer", "")
        self.approved = "False"

    def simple_serialize(self):
        """
        Simple serialize an Appointment object.
        """
        return {
            "id": self.id,
            "time": self.time,
            "location": self.location,
            "client": self.client,
            "lawyer": self.lawyer,
            "description": self.description,
            "approved": self.approved,
        }

    def serialize(self):
        """
        Serialize an Appointment object.
        """
        return {
            "id": self.id,
            "time": self.time,
            "location": self.location,
            "client": User.query.filter_by(id=self.client).first().name,
            "lawyer": User.query.filter_by(id=self.lawyer).first().name,
            "description": self.description,
            "approved": self.approved,
            "notes": [n.serialize() for n in self.notes],
        }


class Appointment_Note(db.Model):
    """
    Appointment Note model.
    """

    __tablename__ = "appointment_note"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String, nullable=False)
    file = db.Column(db.String, nullable=True)
    appointment = db.relationship(
        "Appointment", secondary=association_table, back_populates="notes"
    )

    def __init__(self, **kwargs):
        """
        Initialize an Appointment Note object.
        """
        self.description = kwargs.get("description", "")
        self.file = kwargs.get("file", "")

    def serialize(self):
        """
        Serialize an Appointment Note object.
        """
        return {
            "id": self.id,
            "appointment": [a.simple_serialize() for a in self.appointment],
            "description": self.description,
            "file": self.file,
        }
