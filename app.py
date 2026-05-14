from flask import Flask, render_template
from flask_login import LoginManager
from db.database import init_db, db
from models import User
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.student_routes import student_bp
from routes.company_routes import company_bp
from routes.api_routes import api_bp

app = Flask(__name__)

# Secret key
app.secret_key = "placement_portal_secret_key"

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

init_db(app)

# Flask-Login Setup
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route("/")
def home():
    return render_template("home.html")


# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(student_bp)
app.register_blueprint(company_bp)
app.register_blueprint(api_bp)


if __name__ == "__main__":
    app.run(debug=True)