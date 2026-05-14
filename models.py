from db.database import db
from flask_login import UserMixin
from datetime import datetime

# USER MODEL
class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    # User role (student, company, admin)
    role = db.Column(
        db.String(20),
        nullable=False
    )
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    company = db.relationship("Company", backref="user", uselist=False, cascade="all, delete")
    student = db.relationship("Student", backref="user", uselist=False, cascade="all, delete")


# COMPANY MODEL
class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    company_name = db.Column(db.String(200), nullable=False)
    hr_contact = db.Column(db.String(150))
    website = db.Column(db.String(200))
    description = db.Column(db.Text)

    status = db.Column(db.String(20), default="pending")

    drives = db.relationship("Drive", backref="company", cascade="all, delete")
    placements = db.relationship("Placement", backref="company", cascade="all, delete")

    @property
    def display_id(self):
        return f"C{str(self.id).zfill(3)}"


# STUDENT MODEL
class Student(db.Model):
    __tablename__ = "students"

    __table_args__ = {'sqlite_autoincrement': True}  

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    branch = db.Column(db.String(100))
    skills = db.Column(db.Text)
    resume_link = db.Column(db.String(500))
    cgpa = db.Column(db.Float)

    applications = db.relationship("Application", backref="student", cascade="all, delete")
    placements = db.relationship("Placement", backref="student", cascade="all, delete")

# DRIVE MODEL
class Drive(db.Model):
    __tablename__ = "drives"

    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(
        db.Integer,
        db.ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False
    )

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    eligibility = db.Column(db.String(200))
    deadline = db.Column(db.Date)
    status = db.Column(db.String(20), default="pending")

    applications = db.relationship("Application", backref="drive", cascade="all, delete")
    placements = db.relationship("Placement", backref="drive", cascade="all, delete")


# APPLICATION MODEL
class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False
    )

    drive_id = db.Column(
        db.Integer,
        db.ForeignKey("drives.id", ondelete="CASCADE"),
        nullable=False
    )

    applied_on = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="Applied")

    # UNIQUE(student_id, drive_id)
    __table_args__ = (
        db.UniqueConstraint("student_id", "drive_id", name="unique_student_drive"),
    )


# PLACEMENT MODEL
class Placement(db.Model):
    __tablename__ = "placements"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False
    )

    drive_id = db.Column(
        db.Integer,
        db.ForeignKey("drives.id", ondelete="CASCADE"),
        nullable=False
    )

    company_id = db.Column(
        db.Integer,
        db.ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False
    )

    package = db.Column(db.Float)
    placed_on = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="Placed")
