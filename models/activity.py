import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID

from database.db import Base


class UserActivity(Base):
    __tablename__ = "user_activity"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True)  # Auth0 user ID
    user_email = Column(String, nullable=True, index=True)
    action = Column(String, nullable=False)  # LOGIN, LOGOUT, SIGNUP, PROFILE_UPDATE, etc.
    endpoint = Column(String, nullable=True)  # API endpoint accessed
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String, nullable=False, default="SUCCESS")  # SUCCESS, FAILED
    details = Column(String, nullable=True)  # Additional details about the activity
