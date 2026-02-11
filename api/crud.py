from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from database.db import SessionLocal
from dependencies.auth import get_current_user_optional, get_current_user_required
from schemas.user import (
    UserChangePassword,
    UserCreate,
    UserProfileView,
    UserSignIn,
    UserUpdate,
)
from services.activity_service import get_user_activities, get_all_activities
from services.service import (
    change_password,
    health_check,
    signin_user,
    signup_user,
    update_user,
    view_profile,
)


class APISettings:
    def __init__(self) -> None:
        self.app_name: str = "User Log API"
        self.app_version: str = "1.0.0"


api_settings = APISettings()


app = FastAPI(
    title=api_settings.app_name,
    description="Backend API for user log and account management",
    version=api_settings.app_version,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health(current_user: dict = Depends(get_current_user_required), db: Session = Depends(get_db)):
    return health_check(db)


@app.post("/signin")
def user_signin(payload: UserSignIn, current_user: dict = Depends(get_current_user_required), db: Session = Depends(get_db)):
    return signin_user(payload, db)


@app.post("/signup")
def user_signup(payload: UserCreate, current_user: dict = Depends(get_current_user_required), db: Session = Depends(get_db)):
    return signup_user(payload, db)


@app.post("/update")
def user_update(payload: UserUpdate, current_user: dict = Depends(get_current_user_required), db: Session = Depends(get_db)):
    return update_user(payload, db)


@app.post("/change-password")
def user_change_password(payload: UserChangePassword, current_user: dict = Depends(get_current_user_required), db: Session = Depends(get_db)):
    return change_password(payload, db)


@app.post("/profile")
def user_profile(payload: UserProfileView, db: Session = Depends(get_db)):
    return view_profile(payload, db)


# Admin endpoints for monitoring
@app.get("/admin/activities")
def get_all_activities_endpoint(current_user: dict = Depends(get_current_user_required), db: Session = Depends(get_db)):
    """Get all user activities (admin endpoint)."""
    activities = get_all_activities(db)
    return {
        "activities": activities,
        "total": len(activities)
    }


@app.get("/admin/users")
def get_all_users(current_user: dict = Depends(get_current_user_required), db: Session = Depends(get_db)):
    """Get list of all registered users (admin endpoint)."""
    from models.user import User
    
    users = db.query(User).all()
    user_list = []
    
    for user in users:
        user_list.append({
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "phone_number": user.phone_number,
            "date_of_birth": user.date_of_birth.isoformat() if user.date_of_birth else None,
            "age": user.age,
            "blood_group": user.blood_group,
            "created_ts": user.created_ts.isoformat() if user.created_ts else None,
        })
    
    return {
        "users": user_list,
        "total": len(user_list)
    }
