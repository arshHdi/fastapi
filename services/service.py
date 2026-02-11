import bcrypt
from datetime import datetime
from typing import Dict

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from models.user import User
from schemas.user import (
    UserChangePassword,
    UserCreate,
    UserProfileView,
    UserSignIn,
    UserUpdate,
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()


def _user_to_dict(user: User) -> Dict:
    return {
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
        "phone_number": user.phone_number,
        "date_of_birth": user.date_of_birth,
        "age": user.age,
        "blood_group": user.blood_group,
    }


def signin_user(payload: UserSignIn, db: Session) -> Dict:
    """Handle user signin logic: validate credentials and return user profile data."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return _user_to_dict(user)


def health_check(db: Session) -> Dict:
    """Simple health check to verify database connection."""
    try:
        # Minimal query to ensure DB connection is alive
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection error: {exc}",
        )

def signup_user(payload: UserCreate, db: Session) -> Dict:
    """Handle user signup: ensure email is unique, hash password, create user."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        name=payload.name,
        email=payload.email,
        password=hash_password(payload.password),
        phone_number=payload.phone_number,
        date_of_birth=payload.date_of_birth,
        age=payload.age,
        blood_group=payload.blood_group,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return _user_to_dict(user)


def update_user(payload: UserUpdate, db: Session) -> Dict:
    """Update basic profile fields for a user authenticated by email+password."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if payload.name is not None:
        user.name = payload.name
    if payload.phone_number is not None:
        user.phone_number = payload.phone_number
    if payload.date_of_birth is not None:
        user.date_of_birth = payload.date_of_birth
    if payload.age is not None:
        user.age = payload.age
    if payload.blood_group is not None:
        user.blood_group = payload.blood_group

    user.updated_ts = datetime.utcnow()

    db.commit()
    db.refresh(user)

    return _user_to_dict(user)


def change_password(payload: UserChangePassword, db: Session) -> Dict:
    """Change a user's password after verifying current password."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.current_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user.password = hash_password(payload.new_password)
    user.updated_ts = datetime.utcnow()

    db.commit()
    db.refresh(user)

    return _user_to_dict(user)


def view_profile(payload: UserProfileView, db: Session) -> Dict:
    """Return a user's profile after verifying email+password."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return _user_to_dict(user)
