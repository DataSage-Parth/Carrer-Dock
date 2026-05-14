from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import User, Student, Company, Drive, Application, Placement
from db.database import db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# Admin Role Check
def admin_only():
    if current_user.role != "admin":
        abort(403)

# Dashboard
@admin_bp.route("/dashboard")
@login_required
def dashboard():
    admin_only()

    stats = {
        "students": Student.query.count(),
        "companies": Company.query.count(),
        "drives": Drive.query.count(),
        "applications": Application.query.count(),
        "placements": Placement.query.count()
    }

    return render_template("admin/dashboard.html", stats=stats)


# View Students
@admin_bp.route("/students")
@login_required
def students():
    admin_only()

    students = (
        db.session.query(Student, User)
        .join(User, Student.user_id == User.id)
        .order_by(Student.id.desc())
        .all()
    )

    return render_template("admin/students.html", students=students)


# View Companies
@admin_bp.route("/companies")
@login_required
def companies():
    admin_only()

    companies = (
        db.session.query(Company, User)
        .join(User, Company.user_id == User.id)
        .order_by(Company.id.desc())
        .all()
    )

    return render_template("admin/companies.html", companies=companies)


# Change User Active Status
@admin_bp.route("/toggle_user/<int:user_id>/<source>")
@login_required
def toggle_user(user_id, source):
    admin_only()

    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()

    flash("User status updated.")

    if source == "students":
        return redirect(url_for("admin.students"))
    return redirect(url_for("admin.companies"))



# Approve / Reject Company
@admin_bp.route("/company/approve/<int:company_id>")
@login_required
def approve_company(company_id):
    admin_only()

    company = Company.query.get_or_404(company_id)
    company.status = "approved"
    db.session.commit()

    flash("Company approved.")
    return redirect(url_for("admin.companies"))


@admin_bp.route("/company/reject/<int:company_id>")
@login_required
def reject_company(company_id):
    admin_only()

    company = Company.query.get_or_404(company_id)
    company.status = "rejected"
    db.session.commit()

    flash("Company rejected.")
    return redirect(url_for("admin.companies"))


# View Drives
@admin_bp.route("/drives")
@login_required
def drives():
    admin_only()

    drives = (
        db.session.query(Drive, Company)
        .join(Company, Drive.company_id == Company.id)
        .order_by(Drive.id.desc())
        .all()
    )

    return render_template("admin/drives.html", drives=drives)


# Approve/ reject / Close Drive
@admin_bp.route("/drive/approve/<int:drive_id>")
@login_required
def approve_drive(drive_id):
    admin_only()

    drive = Drive.query.get_or_404(drive_id)
    drive.status = "approved"
    db.session.commit()

    flash("Drive approved.")
    return redirect(url_for("admin.drives"))


@admin_bp.route("/drive/reject/<int:drive_id>")
@login_required
def reject_drive(drive_id):
    admin_only()

    drive = Drive.query.get_or_404(drive_id)
    drive.status = "rejected"
    db.session.commit()

    flash("Drive rejected.", "danger")
    return redirect(url_for("admin.drives"))


@admin_bp.route("/drive/close/<int:drive_id>")
@login_required
def close_drive(drive_id):
    admin_only()

    drive = Drive.query.get_or_404(drive_id)
    drive.status = "closed_by_admin"
    db.session.commit()

    flash("Drive closed.")
    return redirect(url_for("admin.drives"))


# View Applications
@admin_bp.route("/applications")
@login_required
def applications():
    admin_only()

    applications = (
        db.session.query(
            Application.id,
            User.name.label("student_name"),
            User.email.label("student_email"),
            Student.id.label("student_id"),
            Student.branch,
            Company.company_name,
            Company.id.label("company_id"),
            Drive.title.label("drive_title"),
            Application.status,
            Application.applied_on
        )
        .join(Student, Application.student_id == Student.id)
        .join(User, Student.user_id == User.id)
        .join(Drive, Application.drive_id == Drive.id)
        .join(Company, Drive.company_id == Company.id)
        .order_by(Application.id.desc())
        .all()
    )

    return render_template("admin/applications.html", applications=applications)



# View Placements
@admin_bp.route("/placements")
@login_required
def placements():
    admin_only()

    placements = (
        db.session.query(Placement, Student, User, Company, Drive)
        .join(Student, Placement.student_id == Student.id)
        .join(User, Student.user_id == User.id)
        .join(Company, Placement.company_id == Company.id)
        .join(Drive, Placement.drive_id == Drive.id)
        .order_by(Placement.id.desc())
        .all()
    )

    return render_template("admin/placements.html", placements=placements)


# Search Students / Companies
@admin_bp.route("/search", methods=["GET", "POST"])
@login_required
def search():
    admin_only()

    results_students = []
    results_companies = []
    query = ""

    if request.method == "POST":
        query = request.form.get("query", "").strip()

        # STUDENT SEARCH 
        results_students = (
            db.session.query(Student, User)
            .join(User, Student.user_id == User.id)
            .filter(
                (User.name.ilike(f"%{query}%")) |
                (User.email.ilike(f"%{query}%")) |
                (db.cast(Student.id, db.String).ilike(f"%{query}%"))
            )
            .all()
        )

        # COMPANY SEARCH
        company_id = None

        # Only accept proper company id
        if query.startswith("C") and len(query) == 4 and query[1:].isdigit():
            company_id = int(query[1:])

        results_companies = (
            db.session.query(Company, User)
            .join(User, Company.user_id == User.id)
            .filter(
                (Company.company_name.ilike(f"%{query}%")) |
                (User.email.ilike(f"%{query}%")) |
                (Company.id == company_id if company_id else False)
            )
            .all()
        )

    return render_template(
        "admin/search.html",
        query=query,
        results_students=results_students,
        results_companies=results_companies
    )

# Blacklist Company Permanent Delete
@admin_bp.route("/company/blacklist/<int:company_id>", methods=["POST"])
@login_required
def blacklist_company(company_id):
    admin_only()

    company = Company.query.get_or_404(company_id)

    # Delete all applications related to company's drives
    drives = Drive.query.filter_by(company_id=company.id).all()
    for drive in drives:
        Application.query.filter_by(drive_id=drive.id).delete()

    # Delete drives
    Drive.query.filter_by(company_id=company.id).delete()

    # Delete company user
    user = User.query.get(company.user_id)

    db.session.delete(company)
    if user:
        db.session.delete(user)

    db.session.commit()

    flash("Company blacklisted and all data removed!", "danger")
    return redirect(url_for("admin.companies"))

# Blacklist Student (Permanent Delete)
@admin_bp.route("/student/blacklist/<int:student_id>", methods=["POST"])
@login_required
def blacklist_student(student_id):
    admin_only()

    student = Student.query.get_or_404(student_id)

    # Delete applications
    Application.query.filter_by(student_id=student.id).delete()

    # Delete user 
    user = User.query.get(student.user_id)

    db.session.delete(student)
    if user:
        db.session.delete(user)

    db.session.commit()

    flash("Student blacklisted and removed!", "danger")
    return redirect(url_for("admin.students"))