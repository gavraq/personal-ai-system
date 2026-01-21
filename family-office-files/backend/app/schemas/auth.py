"""
Authentication schemas for request/response validation
"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class RegisterRequest(BaseModel):
    """Schema for user registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        """Validate password meets complexity requirements"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserResponse(BaseModel):
    """Schema for user response (excludes sensitive fields)"""
    id: UUID
    email: str
    role: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
