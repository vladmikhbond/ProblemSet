import os
import logging
import httpx

from fastapi import APIRouter, Depends, Request, Response, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from ..models.schemas import ProblemHeader

# логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# шаблони Jinja2
path = os.path.join(os.getcwd(), 'app', 'templates')
templates = Jinja2Templates(directory=path)

router = APIRouter()

# HOST = "http://localhost:7000"
PSS_HOST = "http://172.17.0.1:7000"


@router.get("/probs")
async def get_probs(request: Request):
    
    api_url = f"{PSS_HOST}/api/problems/lang/py"
    token = request.session.get("token", "upset")
    headers = { "Authorization": f"Bearer {token}" }

    if token == "upset":
        # redirect to login page
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": "No token"
        })
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers)
        json = response.json()
    except Exception as e:
        logger.error(f"Error during login request: {e}")
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": "Invalid credentials"
        })
    else:
        headers = [ProblemHeader(id=x["id"], title=x["title"], attr=x["attr"]) for x in json]
        return headers   
   


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
    return {
        "status_code": response.status_code,
        "response": response.json()
    }    
