from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

from models import User, Student, Company
from db.database import db

auth_bp = Blueprint("auth", __name__, url_prefix="")


# LOGIN
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Invalid email or password", "danger")
            return redirect(url_for("auth.login"))

        if not check_password_hash(user.password, password):
            flash("Invalid email or password", "danger")
            return redirect(url_for("auth.login"))

        if not user.is_active:
            flash(
                "Account Deactivated. "
                "Please contact the placement cell.",
                "danger"
            )
            return redirect(url_for("auth.login"))

        # Company approval check
        if user.role == "company":
            company = Company.query.filter_by(user_id=user.id).first()
            if not company or company.status != "approved":
                flash("Company not approved yet", "warning")
                return redirect(url_for("auth.login"))

        login_user(user)

        flash("Login successful!", "success")
        return redirect(url_for(f"{user.role}.dashboard"))

    return render_template("auth/login.html")


# LOGOUT
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.")
    return redirect(url_for("home"))


# REGISTER STUDENT
@auth_bp.route("/register/student", methods=["GET", "POST"])
def register_student():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        branch = request.form["branch"]
        resume_link = request.form.get("resume_link", "").strip()
        cgpa = float(request.form.get("cgpa", 0)) 

        try:
            new_user = User(
                name=name,
                email=email,
                password=password,
                role="student",
                is_active=True
            )
            db.session.add(new_user)
            db.session.flush()  

            new_student = Student(
                user_id=new_user.id,
                branch=branch,
                skills="",
                resume_link=resume_link,
                cgpa=cgpa  
            )
            db.session.add(new_student)

            db.session.commit()

            flash("Student registered successfully")
            return redirect(url_for("auth.login"))

        except IntegrityError:
            db.session.rollback()
            flash("Email already exists", "danger")

    return render_template("auth/register_student.html")


# REGISTER COMPANY
@auth_bp.route("/register/company", methods=["GET", "POST"])
def register_company():
    if current_user.is_authenticated:                                    
        return redirect(url_for(f"{current_user.role}.dashboard"))       

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        company_name = request.form["company_name"]
        hr_contact = request.form["hr_contact"]
        website = request.form.get("website", "").strip()                

        try:
            new_user = User(
                name=name,
                email=email,
                password=password,
                role="company",
                is_active=True
            )
            db.session.add(new_user)
            db.session.flush()

            new_company = Company(
                user_id=new_user.id,
                company_name=company_name,
                hr_contact=hr_contact,
                website=website,
                description="",
                status="pending"
            )
            db.session.add(new_company)

            db.session.commit()

            flash("Company registered. Await admin approval.")
            return redirect(url_for("auth.login"))

        except IntegrityError:
            db.session.rollback()
            flash("Email already exists", "danger")

    return render_template("auth/register_company.html")