from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from utils import dependencies
import models, schemas

# Secret key to encode the JWT token
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# This will require the user to send their access token in the Authorization header of the request.
# If the token is provided, FastAPI will decode the token and get the data from it.
# If the token is invalid, FastAPI will return an HTTP 401 Unauthorized error.
# This will be used to protect the routes that require authentication.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create an access token with the data provided in the data parameter."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user(db: Session, username: str) -> models.User:
    """Get a user by their username."""
    return db.query(models.User).filter(models.User.username == username).first()

def authenticate_user(db: Session, username: str, password: str) -> models.User:
    """Authenticate a user by their username and password."""
    user = get_user(db, username)
    if not user:
        return False
    if not dependencies.verify_password(password, user.hashed_password):
        return False
    return user

def get_current_user(db: Session = Depends(dependencies.get_db), token: str = Depends(oauth2_scheme)) -> models.User:
    """Get the current user from the database using the token provided."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: schemas.User = Depends(get_current_user)) -> schemas.User:
    """Check if the user is active. If not, raise an HTTPException with status code 400 and detail Inactive user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_active_superuser(current_user: schemas.User = Depends(get_current_user)) -> schemas.User:
    """Check if the user is a superuser. If not, raise an HTTPException with status code 400 and detail The user doesn't have enough privileges."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")
    return current_user
