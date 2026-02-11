from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, constr


class UserCreate(BaseModel):
    """Schema for signing up a new user."""

    name: constr(strip_whitespace=True, min_length=1)
    email: EmailStr
    password: constr(min_length=6)  # plain text input; hash before storing in DB

    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    age: Optional[int] = None
    blood_group: Optional[str] = None

class UserSignIn(BaseModel):
    """Schema for signing in an existing user."""

    email: EmailStr
    password: constr(min_length=6)

class UserUpdate(BaseModel):
    """Schema for editing/updating a user.

    Email + password are used for authentication; other fields are optional
    and represent the values to be updated.
    """
    email: EmailStr
    password: constr(min_length=6)

    name: Optional[constr(strip_whitespace=True, min_length=1)] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    age: Optional[int] = None
    blood_group: Optional[str] = None


class UserChangePassword(BaseModel):
    """Schema for changing an existing user's password."""

    email: EmailStr
    current_password: constr(min_length=6)
    new_password: constr(min_length=6)


class UserProfileView(BaseModel):
    """Schema for viewing a user's profile (auth by email + password)."""

    email: EmailStr
    password: constr(min_length=6)
