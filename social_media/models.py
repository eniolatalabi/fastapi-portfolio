from sqlalchemy import Column, Integer, String, Boolean, text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship
from .database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column (String, nullable=False)
    published = Column(Boolean, server_default=text("true"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(),)

    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable = False, unique = True)
    password = Column(String, nullable = False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(),)
    
    # PHONE NUMBER COLUMN ADDED HERE
    phone_number = Column(String, nullable=True)

#The Vote Model
class Vote(Base):
    __tablename__ = "votes"
    
    # Composite Primary Key (Both set to True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)

class RefreshToken(Base):
    """Server-side record of an issued refresh token.

    Storing tokens lets the API rotate them on every use, revoke them
    on logout, and treat reuse of a rotated token as a breach signal.
    """

    __tablename__ = "refresh_tokens"
    jti = Column(String, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False)
    revoked = Column(Boolean, server_default=text("false"), nullable=False)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False,
                        server_default=func.now())
