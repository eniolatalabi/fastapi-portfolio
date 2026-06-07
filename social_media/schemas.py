from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
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


# Output for returning a user
# we DO NOT include 'password' here. This keeps it secure.
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    phone_number: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Model for RETURNING posts (Output serialization)
# Reordered fields to match Database Schema exactly.
class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    published: bool
    created_at: datetime
    owner_id : int
    owner: UserResponse
    
    # Config to allow Pydantic to read from ORM objects or Dictionaries
    model_config = ConfigDict(from_attributes=True)


# Model for Post with Vote Count
# This expects the query to return a tuple: (Post Object, Votes Count)
class PostOut(BaseModel):
    Post: PostResponse
    votes: int

    model_config = ConfigDict(from_attributes=True)


# Input for creating a user
class UserUpdate(BaseModel):
    """Partial update of the authenticated user's own account."""
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    phone_number: Optional[str] = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    phone_number: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


# Vote Schemas
class Vote(BaseModel):
    post_id: int
    dir: int # 1 = Like, 0 = Unlike

    # Ensure user only sends 0 or 1
    @field_validator('dir')
    def validate_dir(cls, v):
        if v not in [0, 1]:
            raise ValueError('dir must be 0 (unlike) or 1 (like)')
        return v