from app.schemas.auth import UserCreate

def register_user(user: UserCreate):
    # DB logic later
    return {
        "email": user.email,
        "message": "User registered (dummy)"
    }
