import os

from fastapi.security import APIKeyCookie
import httpx
import jwt

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, Request, Form, Response, Security
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..models.models import User

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_LIFETIME = int(os.getenv("TOKEN_LIFETIME"))
TOKEN_URL = os.getenv("TOKEN_URL")

JUDGE = {"cs": "http://judge_cs_cont:7010/verify",
         "py": "http://judge_py_cont:7011/verify",
         "js": "http://judge_js_cont:7012/verify"}


# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# ----------------------- login

@router.get("/")
async def get_login(request: Request):
    return templates.TemplateResponse("login/login.html", {"request": request})


@router.post("/")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    client = httpx.AsyncClient()
    try:
        client_response = await client.post(
                TOKEN_URL, data={"username": username, "password": password})
    except httpx.RequestError as e:
        raise HTTPException(500, e)
    finally:
        await client.aclose()

    if client_response.is_success:
        token = client_response.json()
    else: 
        return templates.TemplateResponse("login/login.html", {
            "request": request, 
            "error": "Invalid credentials."
        })

    redirect = RedirectResponse("/problemset/list", status_code=302)

    # Встановлюємо cookie у відповідь
    redirect.set_cookie(
        key="access_token",
        value=token,
        httponly=True,        # ❗ Забороняє доступ з JS
        # secure=True,        # ❗ Передавати лише по HTTPS
        samesite="lax",       # ❗ Захист від CSRF
        max_age=TOKEN_LIFETIME * 60,  # in seconds 
    )
    return redirect    
  
# -------------------------- logout

@router.get("/login/logout")
async def get_logout(request: Request):
    resp = RedirectResponse("/", status_code=302)
    resp.delete_cookie("access_token", path="/")
    return resp

# -------------------------- help

@router.get("/login/help")
async def logout(request: Request, response: Response):
    
    return templates.TemplateResponse("login/help.html", {"request": request})  

# ---------------------------- aux

# описуємо джерело токена (cookie)
cookie_scheme = APIKeyCookie(name="access_token")


def get_current_user(token: str = Security(cookie_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    role = payload.get("role")
    return User(username=payload.get("sub"), role=role)


def get_current_tutor(token: str = Security(cookie_scheme)) -> User:
    user = get_current_user(token)
    if user.role != "tutor":
        raise HTTPException(status_code=403, detail="Permission denied: tutors only.")
    return user
