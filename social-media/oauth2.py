from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

# 1. SECRET_KEY: A secret text used to sign the JWT (keep this safe!)
# You can generate a random one by running `openssl rand -hex 32` in terminal
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7" 

# 2. ALGORITHM: How we encrypt the data
ALGORITHM = "HS256"

# 3. EXPIRATION: How long the token lasts (e.g., 30 minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# This tells FastAPI that the route to get a token is "/login"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

def create_access_token(data: dict):
    """
    Creates a JWT token with an expiration time.
    """
    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)   
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    """
    Decodes the token to extract the user ID.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract the 'user_id' we put in the payload earlier
        id: str = payload.get("user_id")
        
        if id is None:
            raise credentials_exception
            
        token_data = schemas.TokenData(id=str(id))
        
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
    
    return user