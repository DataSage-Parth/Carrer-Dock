from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from sqlalchemy import text

db = SQLAlchemy()


def init_db(app):
    db.init_app(app)
    # making automatically student roll no from 1000+
    with app.app_context():
        db.create_all()
        try:
            result = db.session.execute(text("SELECT COUNT(*) FROM students"))
            count = result.scalar()

            if count == 0:
                db.session.execute(text("DELETE FROM sqlite_sequence WHERE name='students'"))
                db.session.execute(
                    text("INSERT INTO sqlite_sequence (name, seq) VALUES ('students', 1000)")
                )
                db.session.commit()
        except Exception:
            db.session.rollback()

        
        # ADMIN CREATION
        # to avoid circular import
        from models import User

        admin = User.query.filter_by(email="admin@placement.com").first()

        if not admin:
            admin_user = User(
                name="Admin",
                email="admin@placement.com",
                password=generate_password_hash("admin123"),
                role="admin",
                is_active=True
            )
            db.session.add(admin_user)
            db.session.commit()
        else:
            admin.role = "admin"
            admin.is_active = True
            db.session.commit()