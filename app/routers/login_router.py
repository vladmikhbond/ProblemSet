import os
import logging
import httpx

from fastapi import APIRouter, Depends, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates


# логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# шаблони Jinja2
path = os.path.join(os.getcwd(), 'app', 'templates')
templates = Jinja2Templates(directory=path)

router = APIRouter()

# PSS_HOST = "http://178.151.21.169:7000"            # for internet
PSS_HOST = "http://172.17.0.1:7000"           # for docker default net


@router.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    url = f"{PSS_HOST}/token"
    data = {
        "username": username,
        "password": password
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)
        json = response.json()
        token = json["access_token"]
    except Exception as e:
        logger.error(f"Error during login request: {e}")
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": "Invalid credentials"
        })
    
    # crate session
    request.session["username"] = username
    request.session["token"] = token

    # redirect to list of problems
    return RedirectResponse(url="/problems", status_code=302)


# ===================================== get_current_user ============================================

from fastapi import Depends, HTTPException, status
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from ..dal import get_db  # Функція для отримання сесії БД
from sqlalchemy.orm import Session
from ..models.models import User
from ..models.schemas import Token, TokenData
import jwt
from jwt.exceptions import InvalidTokenError

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(request: Request) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"} )
    
    token = request.session.get("token", "")
    if token == "":
        credentials_exception 

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
       
        if username is None:
            raise credentials_exception
        role = payload.get("role")
        return username
    except InvalidTokenError:
        raise credentials_exception
    





# async def get_current_user(
#         token: Annotated[str, Depends(oauth2_scheme)],
#         db: Session = Depends(get_db)
# ):
#     """
#     Декодує токен і виймає з нього ім'я юзера.
#     Знаходить в БД юзера, чіє ім'я записано в токені.
#     """
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"} )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username = payload.get("sub")
#         role = payload.get("role")
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except InvalidTokenError:
#         raise credentials_exception
    
#     user = db.get(User, token_data.username)    #  read_user(username=token_data.username)
#     if user is None:
#         raise credentials_exception
#     return user

# AuthType = Annotated[str, Depends(get_current_user111)]
