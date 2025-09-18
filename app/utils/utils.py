
from fastapi import HTTPException, status, Request
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta
import httpx
from  ..config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
PSS_HOST = settings.PSS_HOST



credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"} )


# PSS_HOST = "http://178.151.21.169:7000"       # for internet
# PSS_HOST = "http://pss_cont:7000"               # for docker net "mynet"
    

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


def dat2str(d): return d.strftime("%Y-%m-%dT%H:%M")

def str2dat(s): return datetime.strptime(s, "%Y-%m-%dT%H:%M")

def delta2str(delta: timedelta):
    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60

    # Форматуємо рядок
    return f"{days}дн. {hours}год. {minutes:02}хв."


async def get_poblem_headers(request: Request):
    token = request.session.get("token", "") 
    headers = { "Authorization": f"Bearer {token}" }
    api_url = f"{PSS_HOST}/api/problems/lang/py"
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, headers=headers)
    if response.is_success:
        json = response.json()
    return json


