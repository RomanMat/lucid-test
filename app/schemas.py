from pydantic import BaseModel, EmailStr, constr
from typing import Annotated

class UserCreate(BaseModel):
    """Pydantic schema for creating a user."""
    email: EmailStr
    password: Annotated[str, constr(min_length=6)]

class UserResponse(BaseModel):
    """Pydantic schema for user responses."""
    id: int
    email: EmailStr

    class Config:
        orm_mode = True

class PostCreate(BaseModel):
    """Pydantic schema for creating a post."""
    text: Annotated[str, constr(min_length=1, max_length=1000000)]  # Limit text size to 1 MB

class PostResponse(BaseModel):
    """Pydantic schema for post responses."""
    id: int
    text: str
    owner_id: int

    class Config:
        orm_mode = True
