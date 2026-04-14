# schemas.py
# Pydantic schemas — request validation and response serialization

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


# ---------------------------------------------------------------------------
# Request schemas (used for incoming data)
# ---------------------------------------------------------------------------

class StudentCreate(BaseModel):
    """
    Schema for creating a new student.
    All fields are required; age must be a positive integer.

    Example request body:
    {
        "name":   "Alice Johnson",
        "email":  "alice@example.com",
        "age":    21,
        "course": "Computer Science"
    }
    """
    name:   str       = Field(..., min_length=2, max_length=100, examples=["Alice Johnson"])
    email:  EmailStr  = Field(..., examples=["alice@example.com"])
    age:    int       = Field(..., gt=0, examples=[21])          # gt=0 → must be > 0
    course: str       = Field(..., min_length=2, max_length=100, examples=["Computer Science"])

    @field_validator("name", "course")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        """Trim leading/trailing whitespace from string fields."""
        return v.strip()


class StudentUpdate(BaseModel):
    """
    Schema for updating an existing student.
    Every field is optional so callers can perform partial updates.

    Example request body (partial update):
    {
        "age":    22,
        "course": "Data Science"
    }
    """
    name:   Optional[str]      = Field(None, min_length=2, max_length=100, examples=["Alice Johnson"])
    email:  Optional[EmailStr] = Field(None, examples=["alice_new@example.com"])
    age:    Optional[int]      = Field(None, gt=0, examples=[22])
    course: Optional[str]      = Field(None, min_length=2, max_length=100, examples=["Data Science"])

    @field_validator("name", "course", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


# ---------------------------------------------------------------------------
# Response schemas (used for outgoing data)
# ---------------------------------------------------------------------------

class StudentResponse(BaseModel):
    """
    Schema returned to the client after any successful student operation.
    Includes the auto-generated database id.
    """
    id:     int
    name:   str
    email:  EmailStr
    age:    int
    course: str

    model_config = {"from_attributes": True}  # Enables ORM-mode (replaces orm_mode in Pydantic v2)


class MessageResponse(BaseModel):
    """Generic response used for delete confirmations and similar messages."""
    message: str
