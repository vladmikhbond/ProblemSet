import os
import logging
import httpx

from fastapi import APIRouter, Depends, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..models.schemas import ProblemHeader, ProblemSchema

# логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# шаблони Jinja2
path = os.path.join(os.getcwd(), 'app', 'templates')
templates = Jinja2Templates(directory=path)

router = APIRouter()

# PSS_HOST = "http://localhost:7000"            # for internet
PSS_HOST = "http://172.17.0.1:7000"           # for docker default net

@router.get("/problems")
async def get_probs(request: Request):
    
    api_url = f"{PSS_HOST}/api/problems/lang/py"
    token = request.session.get("token", "upset")
    headers = { "Authorization": f"Bearer {token}" }

    if token == "upset":
        # redirect to login page
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "No token"})
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers)
        json = response.json()
    except Exception as e:
        err_mes = f"Error during login request: {e}"
        logger.error(err_mes)
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": err_mes
        })
    else:
        headers = [ProblemHeader(id=x["id"], title=x["title"], attr=x["attr"]) for x in json]
        return templates.TemplateResponse("problem_list.html", {"request": request, "headers": headers})

@router.get("/problem/{id}")
async def get_probs(id: str, request: Request):
    api_url = f"{PSS_HOST}/api/problems/{id}"
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
        json_obj = response.json()
    except Exception as e:
        err_mes = f"Error during a problem request: {e}"
        logger.error(err_mes)
        return RedirectResponse(url="/problems", status_code=302)
    else:
        problem = ProblemSchema(**json_obj) 
        return templates.TemplateResponse(
            "problem.html", 
            {"request": request, "problem": problem} )


# ========================= Login suit =================================

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
