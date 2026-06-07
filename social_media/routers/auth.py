from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import database, schemas, models, utils, oauth2

router = APIRouter(tags=['Authentication'])

@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    
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
    return {"access_token": access_token, "token_type": "bearer"}