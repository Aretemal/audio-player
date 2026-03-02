from typing import Optional

from sqlalchemy.orm import Session

from app.auth.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_in: UserCreate) -> User:
    existing_user = get_user_by_email(db, user_in.email)

    if existing_user:
        raise ValueError("User with this email already exists")
    
    hashed_password = hash_password(user_in.password)
    
    db_user = User(
        email=user_in.email,
        username=user_in.username,
        password_hash=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    if user_update.username is not None:
        user.username = user_update.username
    if user_update.theme is not None:
        if user_update.theme in ["light", "dark"]:
            user.theme = user_update.theme
    
    db.commit()
    db.refresh(user)
    return user

