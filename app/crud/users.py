from sqlalchemy.orm import Session
from typing import List, Optional
from passlib.hash import bcrypt

from app.models.user import User, UserRole


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def create_user(
    db: Session,
    email: str,
    password: str,
    first_name: str = "",
    last_name: str = "",
    role: UserRole = UserRole.VENDEDOR,
    provider: Optional[str] = None,
) -> User:
    if get_user_by_email(db, email):
        raise ValueError("Email ya registrado")
    user = User(
        email=email,
        password_hash=bcrypt.hash(password),
        first_name=first_name,
        last_name=last_name,
        role=role,
        oauth_provider=provider,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if user and bcrypt.verify(password, user.password_hash):
        return user
    return None


def get_users(db: Session) -> List[User]:
    return db.query(User).all()


def change_user_role(db: Session, user_id: int, role: UserRole) -> bool:
    user = get_user(db, user_id)
    if not user:
        return False
    user.role = role
    db.commit()
    return True


def delete_user(db: Session, user_id: int) -> bool:
    user = get_user(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True


def update_user(
    db: Session,
    user_id: int,
    first_name: str,
    last_name: str,
    email: str,
    password: Optional[str] = None,
) -> Optional[User]:
    user = get_user(db, user_id)
    if not user:
        return None
    # check email uniqueness if changed
    if user.email != email and get_user_by_email(db, email):
        raise ValueError("Email ya registrado")
    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    if password:
        user.password_hash = bcrypt.hash(password)
    db.commit()
    db.refresh(user)
    return user
