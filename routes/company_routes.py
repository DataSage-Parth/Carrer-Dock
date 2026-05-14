from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Company, Drive, Application, Student, User, Placement
from db.database import db
from datetime import datetime, date

company_bp = Blueprint("company", __name__, url_prefix="/company")


# Company Role Protection
def company_required():
    if current_user.role != "company":
        return False
    return True



# Dashboard
@company_bp.route("/dashboard")
@login_required
def dashboard():
    if not company_required():
        return redirect(url_for("auth.login"))

    company = Company.query.filter_by(user_id=current_user.id).first_or_404()

    # Deactivation check
    if company.status == "inactive":
        flash(
            " Company Account Deactivated. "
            "Please contact the placement cell.",
            "danger"
        )
        return redirect(url_for("auth.logout"))

    # Get drives with per-drive applicant count
    drives = Drive.query.filter_by(company_id=company.id).order_by(Drive.id.desc()).all()

    drive_data = []
    for drive in drives:
        count = Application.query.filter_by(drive_id=drive.id).count()
        drive_data.append({
            "drive": drive,
            "applicant_count": count
        })

    # Total Applications
    total_applications = sum(d["applicant_count"] for d in drive_data)

    # Total Placements
    total_placements = Placement.query.filter_by(company_id=company.id).count()

    stats = {
        "drives": len(drives),
        "applications": total_applications,
        "placements": total_placements
    }

    return render_template(
        "company/dashboard.html",
        company=company,
        stats=stats,
        drive_data=drive_data        
    )


# Create Drive
@company_bp.route("/create_drive", methods=["GET", "POST"])
@login_required
def create_drive():
    if not company_required():
        return redirect(url_for("auth.login"))

    company = Company.query.filter_by(user_id=current_user.id).first_or_404()

    if request.method == "POST":
        new_drive = Drive(
            company_id=company.id,
            title=request.form["title"],
            description=request.form["description"],
            eligibility=request.form["eligibility"],
            deadline=datetime.strptime(request.form["deadline"], "%Y-%m-%d").date(),
            status="pending"
        )

        db.session.add(new_drive)
        db.session.commit()

        flash("Drive created (pending admin approval).")
        return redirect(url_for("company.dashboard"))

    return render_template("company/create_drive.html")



# View Drives
@company_bp.route("/drives")
@login_required
def drives():
    if not company_required():
        return redirect(url_for("auth.login"))

    company = Company.query.filter_by(user_id=current_user.id).first_or_404()

    drives = (
        db.session.query(Drive)
        .filter_by(company_id=company.id)
        .order_by(Drive.id.desc())
        .all()
    )
    return render_template("company/drives.html", drives=drives)


# Edit Drive
@company_bp.route("/drive/edit/<int:drive_id>", methods=["GET", "POST"])
@login_required
def edit_drive(drive_id):
    if not company_required():
        return redirect(url_for("auth.login"))

    drive = Drive.query.get_or_404(drive_id)

    # Ensure company owns this drive
    company = Company.query.filter_by(user_id=current_user.id).first_or_404()
    if drive.company_id != company.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("company.drives"))

    if request.method == "POST":
        drive.title = request.form["title"]
        drive.description = request.form["description"]
        drive.eligibility = request.form["eligibility"]
        drive.deadline = datetime.strptime(request.form["deadline"], "%Y-%m-%d").date()

        #admin re-approval after editing the drive
        drive.status = "pending"

        # DELETE all previous applications
        # Students must reapply after approval
        for application in drive.applications:
            db.session.delete(application)

        db.session.commit()

        flash(
            "Drive updated. Previous applications cleared. "
            "Reapply after approval.",
            "info"
        )
        return redirect(url_for("company.drives"))

    return render_template("company/edit_drive.html", drive=drive)



# Close Drive
@company_bp.route("/drive/close/<int:drive_id>")
@login_required
def close_drive(drive_id):
    if not company_required():
        return redirect(url_for("auth.login"))

    drive = Drive.query.get_or_404(drive_id)
    drive.status = "closed_by_company" 
    db.session.commit()

    flash("Drive closed.")
    return redirect(url_for("company.drives"))


# Delete Drive

@company_bp.route("/drive/delete/<int:drive_id>")
@login_required
def delete_drive(drive_id):
    if not company_required():
        return redirect(url_for("auth.login"))

    drive = Drive.query.get_or_404(drive_id)

    # Ensure company owns this drive
    company = Company.query.filter_by(user_id=current_user.id).first_or_404()
    if drive.company_id != company.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("company.drives"))

    db.session.delete(drive)
    db.session.commit()

    flash("Drive deleted successfully.")
    return redirect(url_for("company.drives"))



# Applicants

@company_bp.route("/applicants")
@login_required
def applicants():
    if not company_required():
        return redirect(url_for("auth.login"))

    company = Company.query.filter_by(user_id=current_user.id).first_or_404()

    applicants = (
        db.session.query(Application, Student, User, Drive)
        .join(Student, Application.student_id == Student.id)
        .join(User, Student.user_id == User.id)
        .join(Drive, Application.drive_id == Drive.id)
        .filter(Drive.company_id == company.id)
        .order_by(Application.id.desc())
        .all()
    )

    return render_template("company/applicants.html", applicants=applicants)


# Update Application Status
@company_bp.route("/update_application/<int:application_id>/<status>")
@login_required
def update_application(application_id, status):
    if not company_required():
        return redirect(url_for("auth.login"))

    if status not in ["Shortlisted", "Selected", "Rejected"]:
        flash("Invalid status")
        return redirect(url_for("company.applicants"))

    application = Application.query.get_or_404(application_id)

    # Ensure company dont approve students before admin approve edit
    if application.drive.status != "approved":
        flash("Cannot update application. Drive is not approved.", "danger")
        return redirect(url_for("company.applicants"))

    application.status = status
    db.session.commit()

    flash(f"Application marked as {status}")
    return redirect(url_for("company.applicants"))


# Mark Selected (Placement)
# ctc add 
@company_bp.route("/mark_selected", methods=["POST"])
@login_required
def mark_selected():
    if not company_required():
        return redirect(url_for("auth.login"))

    application_id = request.form["application_id"]
    package = request.form["package"]

    application = Application.query.get_or_404(application_id)

    new_placement = Placement(
        student_id=application.student_id,
        drive_id=application.drive_id,
        company_id=application.drive.company_id,
        package=package,
        status="Placed"
    )

    application.status = "Selected"

    db.session.add(new_placement)
    db.session.commit()

    flash("Student marked as Placed successfully!")
    return redirect(url_for("company.applicants"))


# View Placements
@company_bp.route("/placements")
@login_required
def placements():
    if not company_required():
        return redirect(url_for("auth.login"))

    company = Company.query.filter_by(user_id=current_user.id).first_or_404()

    placements = (
        db.session.query(Placement, Student, User, Drive)
        .join(Student, Placement.student_id == Student.id)
        .join(User, Student.user_id == User.id)
        .join(Drive, Placement.drive_id == Drive.id)
        .filter(Placement.company_id == company.id)
        .order_by(Placement.id.desc())
        .all()
    )

    return render_template("company/placements.html", placements=placements)

@company_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if not company_required():
        return redirect(url_for("auth.login"))

    company = Company.query.filter_by(user_id=current_user.id).first_or_404()

    if request.method == "POST":
        company.hr_contact = request.form.get("hr_contact", "").strip()
        company.website = request.form.get("website", "").strip()
        company.description = request.form.get("description", "").strip()

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("company.profile"))

    return render_template("company/profile.html", company=company)