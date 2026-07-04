from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User


DEMO_USERS = [
    {
        "name": "Admin",
        "email": "admin@example.com",
        "password": "password123",
        "role": "admin",
    },
    {
        "name": "Manager",
        "email": "manager@example.com",
        "password": "password123",
        "role": "manager",
    },
    {
        "name": "Employee",
        "email": "employee@example.com",
        "password": "password123",
        "role": "employee",
    },
]


def seed_demo_data() -> None:
    db = SessionLocal()
    try:
        created = 0
        for demo_user in DEMO_USERS:
            existing = (
                db.query(User).filter(User.email == demo_user["email"]).first()
            )
            if existing:
                continue

            db.add(
                User(
                    name=demo_user["name"],
                    email=demo_user["email"],
                    password_hash=hash_password(demo_user["password"]),
                    role=demo_user["role"],
                )
            )
            created += 1

        db.commit()
        print(f"Demo seed complete. Created {created} users.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
