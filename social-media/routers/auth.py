from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import database, schemas, models, utils, oauth2

router = APIRouter(tags=['Authentication'])

@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    
    # 1. Find the user by email
    # OAuth2PasswordRequestForm stores the email in a field called 'username'
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Invalid Credentials"
        )

    # 2. Verify the password
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Invalid Credentials"
        )

    # 3. Create the Token
    # We embed the user's ID into the token so we know who they are later
    access_token = oauth2.create_access_token(data={"user_id": user.id})

    # 4. Return the Token
    # Must match the 'Token' schema we created earlier
    return {"access_token": access_token, "token_type": "bearer"}