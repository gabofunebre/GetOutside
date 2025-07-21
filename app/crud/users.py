import os
import requests
from sqlalchemy.orm import Session
from typing import List, Optional
from passlib.hash import bcrypt
from fastapi import UploadFile
from app.core.config import USER_PHOTOS_DIR

from app.models.user import User, UserRole
from app.core.config import ADMIN_EMAIL


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
    oauth_provider: Optional[str] = None,
) -> User:
    if get_user_by_email(db, email):
        raise ValueError("Email ya registrado")
    user = User(
        email=email,
        password_hash=bcrypt.hash(password),
        first_name=first_name,
        last_name=last_name,
        role=role,
        oauth_provider=oauth_provider,
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


def _save_photo(user_id: int, foto: UploadFile) -> str:
    """Save uploaded photo to user's folder and return filename."""
    ext = os.path.splitext(foto.filename)[1].lower() or ".jpg"
    user_dir = os.path.join(USER_PHOTOS_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    filename = f"foto{ext}"
    dest_path = os.path.join(user_dir, filename)
    with open(dest_path, "wb") as out:
        out.write(foto.file.read())
    return filename


def save_remote_photo(user_id: int, url: str) -> Optional[str]:
    """Download remote image and store it."""
    try:
        resp = requests.get(url, timeout=10)
        if not resp.ok:
            return None
        _, ext = os.path.splitext(url.split("?")[0])
        ext = ext or ".jpg"
        user_dir = os.path.join(USER_PHOTOS_DIR, str(user_id))
        os.makedirs(user_dir, exist_ok=True)
        filename = f"foto{ext}"
        dest_path = os.path.join(user_dir, filename)
        with open(dest_path, "wb") as out:
            out.write(resp.content)
        return filename
    except Exception:
        return None


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
    if user.email == ADMIN_EMAIL:
        return False
    db.query(User).filter(User.id == user_id).delete()
    db.commit()
    return True


def update_user(
    db: Session,
    user_id: int,
    first_name: str,
    last_name: str,
    email: str,
    password: Optional[str] = None,
    foto: UploadFile | None = None,
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
    if foto is not None and foto.filename:
        filename = _save_photo(user_id, foto)
        # remove old file if different
        if user.foto_filename and user.foto_filename != filename:
            old_path = os.path.join(USER_PHOTOS_DIR, str(user_id), user.foto_filename)
            if os.path.exists(old_path):
                os.remove(old_path)
        user.foto_filename = filename
    db.commit()
    db.refresh(user)
    return user
