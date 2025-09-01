import os
import logging
import httpx

from fastapi import APIRouter, Depends, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..models.schemas import ProblemHeader, ProblemSchema, AnswerSchema


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


