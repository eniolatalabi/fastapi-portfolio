from fastapi import (APIRouter, Depends, HTTPException, Request, Response,
                     status)
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import database, models, oauth2, schemas, utils
from ..config import settings
from ..limiter import limiter

router = APIRouter(tags=['Authentication'])


@router.post('/login', response_model=schemas.Token)
@limiter.limit(settings.login_rate_limit)
def login(request: Request,
          user_credentials: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(database.get_db)):
    
    # OAuth2PasswordRequestForm carries the email in its username field.
    user = db.query(models.User).filter(
        models.User.email == user_credentials.username).first()

    # Same response for unknown email and wrong password: failed
    # authentication is 401, and the message must not reveal which
    # half of the credentials was wrong.
    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not user:
        raise invalid_credentials
    if not utils.verify_password(user_credentials.password, user.password):
        raise invalid_credentials

    access_token = oauth2.create_access_token(data={"user_id": user.id})
    refresh_token = oauth2.create_refresh_token(user.id, db)
    return {"access_token": access_token, "refresh_token": refresh_token,
            "token_type": "bearer"}


@router.post('/refresh', response_model=schemas.Token)
def refresh(body: schemas.RefreshRequest,
            db: Session = Depends(database.get_db)):
    """Rotate a refresh token: the presented token is revoked and a
    fresh access/refresh pair is issued."""
    user_id = oauth2.consume_refresh_token(body.refresh_token, db)
    access_token = oauth2.create_access_token(data={"user_id": user_id})
    refresh_token = oauth2.create_refresh_token(user_id, db)
    return {"access_token": access_token, "refresh_token": refresh_token,
            "token_type": "bearer"}


@router.post('/logout', status_code=status.HTTP_204_NO_CONTENT)
def logout(body: schemas.RefreshRequest,
           db: Session = Depends(database.get_db)):
    """Revoke the presented refresh token, ending that session."""
    oauth2.consume_refresh_token(body.refresh_token, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)