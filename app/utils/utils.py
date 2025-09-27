
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


def payload_from_token(request: Request):
    try:
        token = request.session.get("token", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])        
    except InvalidTokenError as e:
        raise credentials_exception
    else:
        return payload

def username_from_session(request: Request):
    try:
        token = request.session.get("token", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])        
    except InvalidTokenError as e:
        raise credentials_exception
    else:
        return payload.get("sub")




