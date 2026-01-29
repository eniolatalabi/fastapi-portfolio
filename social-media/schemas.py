from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# --- Pydantic Models (Schemas) ---

# Base model for shared attributes (Used for Input)
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True 


# Model for CREATING posts (Input validation)
class PostCreate(PostBase):
    pass

# Model for RETURNING posts (Output serialization)
# Reordered fields to match Database Schema exactly.
# Order: id -> title -> content -> published -> created_at
class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    published: bool
    created_at: datetime
    owner_id : int
    
    # Config to allow Pydantic to read from ORM objects or Dictionaries
    class Config:
        from_attributes = True

# Input for creating a user
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# Output for returning a user
# Notice we DO NOT include 'password' here. This keeps it secure.
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None