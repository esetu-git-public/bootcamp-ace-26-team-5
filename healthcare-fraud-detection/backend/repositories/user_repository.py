from models import User
from database import db

def find_user_by_id(user_id: int) -> User:
    """
    Retrieve a user by their unique primary key ID.
    """
    return db.session.get(User, user_id)


def find_user_by_email(email: str) -> User:
    """
    Retrieve a user by their email address.
    """
    if not email:
        return None
    return User.query.filter_by(email=email.strip().lower()).first()


def create_user(full_name: str, email: str, password_hash: str, role: str = "employee") -> User:
    """
    Insert a new user record into the database.
    """
    user = User(
        full_name=full_name.strip(),
        email=email.strip().lower(),
        password_hash=password_hash,
        role=role.strip().lower()
    )
    db.session.add(user)
    db.session.commit()
    return user
