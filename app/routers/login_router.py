import os

from fastapi.security import APIKeyCookie
import httpx
import jwt
from typing import List
from fastapi import APIRouter, HTTPException, Request, Form, Security
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.models.schemas import HelpItem

from ..models.models import User

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
TOKEN_LIFETIME = int(os.getenv("TOKEN_LIFETIME"))
TOKEN_URL = os.getenv("TOKEN_URL")

JUDGE = {"cs": "http://judge_cs_cont:7010/verify",
         "py": "http://judge_py_cont:7011/verify",
         "js": "http://judge_js_cont:7012/verify"}


# шаблони Jinja2
templates = Jinja2Templates(directory=f"{os.getcwd()}/app/templates")
print(f"Current working directory: {os.getcwd()}")

router = APIRouter()

# ----------------------- login

@router.get("/")
async def get_login(request: Request):
    return templates.TemplateResponse(request, "login/login.html")


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
        return templates.TemplateResponse(request, "login/login.html", { 
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
async def help(request: Request):
    """
    Читає вміст файлу app/static/help/help.txt в список HelpItem.
    В head рядок без відступу, в body рядки з відступом.
    """
    items: List[HelpItem] = []
    with open("app/static/help/help.txt", "r", encoding="utf-8") as f:
        current_item = None
        for line in f:
            line = line.rstrip('\n')
            if line and line[0] != ' ':  # is a head
                line = line.replace("(", "<small>(").replace(")", ")</small>")
                if current_item is not None:
                    items.append(current_item)
                current_item = HelpItem(head=line, body=[])
            elif line and current_item is not None:  # is a body
                current_item.body.append(line.strip())
        if current_item is not None:
            items.append(current_item)
    return templates.TemplateResponse(request, "login/help.html", {"items": items})
    
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
