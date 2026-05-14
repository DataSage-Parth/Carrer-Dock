from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Student, Drive, Company, Application, User, Placement
from db.database import db
from datetime import datetime, date

student_bp = Blueprint("student", __name__, url_prefix="/student")


# Student Role Protection
def student_required():
    return current_user.role == "student"


# Dashboard
@student_bp.route("/dashboard")
@login_required
def dashboard():
    if not student_required():
        return redirect(url_for("auth.login"))

    student = Student.query.filter_by(user_id=current_user.id).first_or_404()

    applied = (
        db.session.query(Application, Drive, Company)
        .join(Drive, Application.drive_id == Drive.id)
        .join(Company, Drive.company_id == Company.id)
        .filter(Application.student_id == student.id)
        .order_by(Application.id.desc())
        .limit(5)
        .all()
    )

    total_applications = Application.query.filter_by(student_id=student.id).count()
    shortlisted = Application.query.filter_by(student_id=student.id, status="Shortlisted").count()
    placements = Placement.query.filter_by(student_id=student.id).count()

    stats = {
        "applications": total_applications,
        "shortlisted": shortlisted,
        "placements": placements
    }

    return render_template("student/dashboard.html", applied=applied, student=student, stats=stats)


# View Drives
@student_bp.route("/drives")
@login_required
def drives():
    if not student_required():
        return redirect(url_for("auth.login"))

    student = Student.query.filter_by(user_id=current_user.id).first_or_404()

    drives = (
        db.session.query(Drive, Company)
        .join(Company, Drive.company_id == Company.id)
        .filter(Drive.status == "approved")
        .order_by(Drive.id.desc())
        .all()
    )

    applied_ids = {
        app.drive_id
        for app in Application.query.filter_by(student_id=student.id).all()
    }

    return render_template(
        "student/drives.html",
        drives=drives,
        applied_ids=applied_ids
    )


# Apply for Drive
@student_bp.route("/apply/<int:drive_id>")
@login_required
def apply(drive_id):
    if not student_required():
        return redirect(url_for("auth.login"))

    student = Student.query.filter_by(user_id=current_user.id).first_or_404()

    existing = Application.query.filter_by(
        student_id=student.id,
        drive_id=drive_id
    ).first()

    if existing:
        flash("Already applied to this drive.", "warning")
        return redirect(url_for("student.drives"))

    drive = Drive.query.get_or_404(drive_id)

    if drive.deadline and drive.deadline < date.today():
        flash("Application deadline has passed for this drive.", "danger")
        return redirect(url_for("student.drives"))

    new_application = Application(
        student_id=student.id,
        drive_id=drive_id,
        applied_on=datetime.utcnow(),
        status="Applied"
    )

    db.session.add(new_application)
    db.session.commit()

    flash("Successfully applied.", "success")
    return redirect(url_for("student.drives"))

# View Applications
@student_bp.route("/applications")
@login_required
def applications():
    if not student_required():
        return redirect(url_for("auth.login"))

    student = Student.query.filter_by(user_id=current_user.id).first_or_404()

    apps = (
        db.session.query(Application, Drive, Company)
        .join(Drive, Application.drive_id == Drive.id)
        .join(Company, Drive.company_id == Company.id)
        .filter(Application.student_id == student.id)
        .order_by(Application.id.desc())
        .all()
    )

    return render_template("student/applications.html", applications=apps)

# Profile
@student_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if not student_required():
        return redirect(url_for("auth.login"))

    student = Student.query.filter_by(user_id=current_user.id).first_or_404()
    user = User.query.get(current_user.id)

    if request.method == "POST":
        skills = request.form.get("skills", "").strip()
        resume_link = request.form.get("resume_link", "").strip()

        student.skills = skills

        if resume_link:
            student.resume_link = resume_link
        else:
            flash("Please provide your resume link.")
            return redirect(url_for("student.profile"))

        db.session.commit()
        flash("Profile updated.")
        return redirect(url_for("student.profile"))

    return render_template("student/profile.html", student=student, user=user)

@student_bp.route("/placements")
@login_required
def placements():
    if not student_required():
        return redirect(url_for("auth.login"))

    student = Student.query.filter_by(user_id=current_user.id).first_or_404()

    my_placements = Placement.query.filter_by(student_id=student.id).all()

    return render_template("student/placements.html", placements=my_placements)