
from fastapi import HTTPException, status, Request
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta
from  ..config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
PSS_HOST = settings.PSS_HOST


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"} )





