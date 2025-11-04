import os
from typing import Optional

import httpx
import jwt
from jwt.exceptions import InvalidTokenError

from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..utils.utils import PSS_HOST, payload_from_token
from  ..config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
PSS_HOST = settings.PSS_HOST


# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# ----------------------- login

@router.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    url = f"{PSS_HOST}/token"
    data = {"username": username, "password": password}
    client = httpx.AsyncClient()
    try:
        response = await client.post(url, data=data)
    except Exception as e:
        raise HTTPException(500, f"{e}\nА чи працює pss_cont на :7000 у мережі докера mynet?")
    finally:
        await client.aclose()

    if response.is_success:
        json = response.json()
        token = json["access_token"]
    else: 
        print(f"Error. Response status_code: {response.status_code}")
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": "Invalid credentials"
        })
    
    # crate session
    request.session["token"] = token

    # redirect
    payload = payload_from_token(request)
    if payload.get("role") == "tutor":
        return RedirectResponse(url="/problemset/list", status_code=302)
    else:
        return RedirectResponse(url="/problems/active", status_code=302)

# --------------------------------------------------

def get_current_user(request: Request) -> dict:    
    # get token from session
    try:
        token = request.session.get("token", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])        
    except InvalidTokenError as e:
        raise HTTPException(401, detail="Could not validate credentials")
    
    # get username from token
    username: Optional[str] = payload.get("sub")
    if username is None:
        raise HTTPException(401, detail="Token missing username")
    
    return {"username": username}


