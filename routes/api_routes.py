from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from models import Drive, Company, Student, User, Application

api_bp = Blueprint("api", __name__, url_prefix="/api")


# GET all approved drives
@api_bp.route("/drives", methods=["GET"])
def get_drives():
    drives = Drive.query.filter_by(status="approved").all()

    result = []
    for drive in drives:
        result.append({
            "id": drive.id,
            "title": drive.title,
            "company": drive.company.company_name,
            "eligibility": drive.eligibility,
            "deadline": str(drive.deadline),
            "status": drive.status
        })

    return jsonify(result)


#  GET all students
@api_bp.route("/students", methods=["GET"])
def get_students():
    students = Student.query.all()

    result = []
    for student in students:
        result.append({
            "id": student.id,
            "name": student.user.name,
            "email": student.user.email,
            "branch": student.branch,
            "skills": student.skills
        })

    return jsonify(result)


# GET applications for a drive
@api_bp.route("/drives/<int:drive_id>/applications", methods=["GET"])
def get_applications(drive_id):
    applications = Application.query.filter_by(drive_id=drive_id).all()

    result = []
    for app in applications:
        result.append({
            "application_id": app.id,
            "student_name": app.student.user.name,
            "student_email": app.student.user.email,
            "status": app.status,
            "applied_on": str(app.applied_on)
        })

    return jsonify(result)


# GET student profile
@api_bp.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    student = Student.query.get_or_404(student_id)

    result = {
        "id": student.id,
        "name": student.user.name,
        "email": student.user.email,
        "branch": student.branch,
        "skills": student.skills,
        "resume_link": student.resume_link
    }

    return jsonify(result)