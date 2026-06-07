import logging
from uuid import uuid4

from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from .config import settings

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

logger = logging.getLogger("social_media.auth")

def create_access_token(data: dict):
    """Create a short-lived access token, marked with its type so it
    can never be accepted where a refresh token is expected."""
    to_encode = data.copy()
    expire = (datetime.now(timezone.utc)
              + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: int, db: Session) -> str:
    """Issue a long-lived refresh token and record it server-side.

    The database record is what makes rotation, logout, and reuse
    detection possible; the JWT alone would be irrevocable.
    """
    jti = uuid4().hex
    expires_at = (datetime.now(timezone.utc)
                  + timedelta(days=settings.refresh_token_expire_days))
    db.add(models.RefreshToken(jti=jti, user_id=user_id,
                               expires_at=expires_at))
    db.commit()
    payload = {"user_id": user_id, "jti": jti, "type": "refresh",
               "exp": expires_at}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def consume_refresh_token(token: str, db: Session) -> int:
    """Validate a refresh token and revoke it (rotation).

    Reuse of an already-revoked token is treated as a breach signal:
    every refresh token belonging to that user is revoked.
    Returns the user id on success.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise credentials_exception

    if payload.get("type") != "refresh":
        raise credentials_exception

    record = db.query(models.RefreshToken).filter(
        models.RefreshToken.jti == payload.get("jti")).first()
    if record is None:
        raise credentials_exception

    if record.revoked:
        # Rotated tokens are single-use. Seeing one again means it was
        # stolen or replayed, so the whole family is revoked.
        logger.warning("Refresh token reuse detected for user %s; "
                       "revoking all sessions", record.user_id)
        db.query(models.RefreshToken).filter(
            models.RefreshToken.user_id == record.user_id).update(
            {"revoked": True})
        db.commit()
        raise credentials_exception

    record.revoked = True
    db.commit()
    return record.user_id

def verify_access_token(token: str, credentials_exception):
    """
    Decodes the token to extract the user ID.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # A refresh token must never grant access to protected routes.
        if payload.get("type") != "access":
            raise credentials_exception

        token_user_id = payload.get("user_id")
        if token_user_id is None:
            raise credentials_exception

        token_data = schemas.TokenData(id=str(token_user_id))
        
    except JWTError:
        raise credentials_exception
    
    return token_data

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    """
    Dependency: It takes the token from the request, verifies it, 
    and fetches the user from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = verify_access_token(token, credentials_exception)

    user = db.query(models.User).filter(models.User.id == token.id).first()

    # A syntactically valid token for a deleted account must not yield
    # None here, or every downstream current_user.id access crashes.
    if user is None:
        raise credentials_exception

    return user