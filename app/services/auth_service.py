from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import verify_password
from app.core.auth import create_access_token


class AuthService:

    @staticmethod
    def login(db, email, password):

        user = db.query(User).filter(User.email == email).first()

        print("USER:", user)

        if user:
            print("INPUT PASSWORD:", password)
            print("HASH:", user.password_hash)
            print("VERIFY RESULT:", verify_password(password, user.password_hash))

        if not user:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return create_access_token({"sub": str(user.id), "role": user.role})
