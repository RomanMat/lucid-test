import os
import jwt
import datetime
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.dependencies import get_db
from app.models import User

# Configuration variables
SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hashes the provided password."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the hashed version."""
    return pwd_context.verify(plain_password, hashed_password)

def create_token(user_id: int) -> str:
    """
    Generates a JWT token for a given user ID.
    Token expires in 1 day.
    """
    payload: dict[str, str | datetime.datetime] = {"sub": str(user_id), "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)}
    token: str = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)  # type: ignore
    return token

def decode_token(token: str) -> int:
    """
    Decodes a JWT token and returns the user ID.
    Raises an HTTPException if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # type: ignore
        return int(payload["sub"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def get_current_user(token: str, db: Session = Depends(get_db)) -> User:
    """
    Retrieves the current user from the database based on the token.
    """
    user_id = decode_token(token)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")
    return user
