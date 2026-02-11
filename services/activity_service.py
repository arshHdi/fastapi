from datetime import datetime
from typing import Dict, Optional

from sqlalchemy.orm import Session

from models.activity import UserActivity


def log_user_activity(
    db: Session,
    user_id: str,
    action: str,
    user_email: Optional[str] = None,
    endpoint: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    status: str = "SUCCESS",
    details: Optional[str] = None,
) -> Dict:
    """Log user activity to the database."""
    activity = UserActivity(
        user_id=user_id,
        user_email=user_email,
        action=action,
        endpoint=endpoint,
        ip_address=ip_address,
        user_agent=user_agent,
        timestamp=datetime.utcnow(),
        status=status,
        details=details,
    )
    
    db.add(activity)
    db.commit()
    db.refresh(activity)
    
    return {
        "id": str(activity.id),
        "user_id": activity.user_id,
        "action": activity.action,
        "timestamp": activity.timestamp.isoformat(),
        "status": activity.status,
    }


def get_user_activities(db: Session, user_id: str, limit: int = 50) -> list:
    """Get recent activities for a specific user."""
    activities = (
        db.query(UserActivity)
        .filter(UserActivity.user_id == user_id)
        .order_by(UserActivity.timestamp.desc())
        .limit(limit)
        .all()
    )
    
    return [
        {
            "id": str(activity.id),
            "action": activity.action,
            "endpoint": activity.endpoint,
            "timestamp": activity.timestamp.isoformat(),
            "status": activity.status,
            "details": activity.details,
        }
        for activity in activities
    ]


def get_all_activities(db: Session, limit: int = 100) -> list:
    """Get all recent activities (for admin purposes)."""
    activities = (
        db.query(UserActivity)
        .order_by(UserActivity.timestamp.desc())
        .limit(limit)
        .all()
    )
    
    return [
        {
            "id": str(activity.id),
            "user_id": activity.user_id,
            "user_email": activity.user_email,
            "action": activity.action,
            "endpoint": activity.endpoint,
            "timestamp": activity.timestamp.isoformat(),
            "status": activity.status,
            "details": activity.details,
        }
        for activity in activities
    ]
