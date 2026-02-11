import uuid

from sqlalchemy import Column, Date, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from database.db import Base


class User(Base):
    __tablename__ = "user_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    # Store the bcrypt-hashed password (e.g., using bcrypt or passlib in your logic)
    password = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    age = Column(Integer, nullable=True)
    blood_group = Column(String, nullable=True)

    created_ts = Column(DateTime, nullable=True)
    created_by = Column(String, nullable=True)
    deleted_ts = Column(DateTime, nullable=True)
    deleted_by = Column(String, nullable=True)
    updated_ts = Column(DateTime, nullable=True)
    updated_by = Column(String, nullable=True)
