from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db
from flask_login import UserMixin

ACCESS = {
    "staff": 1,
    "admin": 2,
}

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String, nullable=False)
    lastName = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    access = db.Column(db.Integer, nullable=False)

    def __init__(self, email, password, firstName, lastName, access=ACCESS["staff"]):
        self.email = email
        self.set_password(password)
        self.firstName = firstName
        self.lastName = lastName
        self.access = access

    def is_admin(self):
        return self.access == ACCESS["admin"]

    def allowed(self, access_level):
        return self.access >= access_level

    def to_json(self):
        return {
                "id": self.id,
                "firstName": self.firstName,
                "lastName": self.lastName,
                "email": self.email,
                "access": self.access
                }

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password, method="sha256")

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)