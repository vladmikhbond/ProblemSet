import os

import httpx

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..utils.utils import PSS_HOST, payload_from_token

# шаблони Jinja2
templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

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
    data = {
        "username": username,
        "password": password
    }
   
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data)
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





