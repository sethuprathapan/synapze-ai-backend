from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import hash_password, verify_password


def seed_admin():
    db = SessionLocal()

    existing_user = db.query(User).filter(User.email == "admin@test.com").first()

    if existing_user:
        if not verify_password("admin123", existing_user.password_hash):
            existing_user.password_hash = hash_password("admin123")
            db.commit()
            print("Admin password updated successfully")
        else:
            print("Admin already exists")
        return

    admin = User(
        name="Admin",
        email="admin@test.com",
        password_hash=hash_password("admin123"),
        role="admin",
    )

    db.add(admin)
    db.commit()

    print("Admin created successfully")


if __name__ == "__main__":
    seed_admin()
