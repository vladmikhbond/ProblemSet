import os
from typing import Optional

from fastapi.security import APIKeyCookie
import httpx
import jwt
from jwt.exceptions import InvalidTokenError

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response, Security
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from ..models.pss_models import User

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_LIFETIME = int(os.getenv("TOKEN_LIFETIME"))
PSS_HOST = os.getenv("PSS_HOST")

# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# ----------------------- login

@router.get("/")
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    url = f"{PSS_HOST}/token"
    data = {"username": username, "password": password}
    client = httpx.AsyncClient()
    try:
        pss_response = await client.post(url, data=data)
    except Exception as e:
        raise HTTPException(500, f"{e}\nА чи працює pss_cont на :7000 у мережі докера mynet?")
    finally:
        await client.aclose()

    if pss_response.is_success:
        json = pss_response.json()
        token = json["access_token"]
    else: 
        print(f"Error. Response status_code: {pss_response.status_code}")
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": "Invalid credentials"
        })
    
    # crate session
    request.session["token"] = token

    redirect = RedirectResponse("/problemset/list", status_code=302)

    # Встановлюємо cookie у відповідь
    redirect.set_cookie(
        key="access_token",
        value=token,
        httponly=True,        # ❗ Забороняє доступ з JS
        # secure=True,        # ❗ Передавати лише по HTTPS
        samesite="lax",       # ❗ Захист від CSRF
        # max_age=TOKEN_LIFETIME * 60,  # in seconds 
    )
    return redirect    

@router.get("/logout")
def logout(response: Response):
    response.delete_cookie(
        key="access_token"
    )
    return {"message": "Session ended"}   

# =================================================================

# описуємо джерело токена (cookie)
cookie_scheme = APIKeyCookie(name="access_token")

def get_current_user(token: str = Security(cookie_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return User(username=payload.get("sub"), role=payload.get("role"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def get_current_tutor(token: str = Security(cookie_scheme)):
    user = get_current_user(token)
    if user.role != "tutor":
        raise HTTPException(status_code=401, detail="You are not a tutor.")
    return user











# # --------------------------------------------------

# def get_current_user(request: Request) -> dict:    
#     # get token from session
#     try:
#         token = request.session.get("token", "")
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])        
#     except InvalidTokenError as e:
#         raise HTTPException(401, detail="Could not validate credentials")
    
#     # get payload from token
#     username: Optional[str] = payload.get("sub")
#     if username is None:
#         raise HTTPException(401, detail="Token missing username")
#     role: str = payload.get("role")
    
#     return {"username": username, "role": role}


