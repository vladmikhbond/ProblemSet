import os
import logging
import httpx

from fastapi import APIRouter, Depends, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..models.schemas import ProblemHeader, ProblemSchema, AnswerSchema
from .login_router import PSS_HOST

# логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# шаблони Jinja2
path = os.path.join(os.getcwd(), 'app', 'templates')
templates = Jinja2Templates(directory=path)

router = APIRouter()

@router.get("/problems", summary="List of problem headers (id, title, attr)")
async def get_probs(request: Request):
    
    api_url = f"{PSS_HOST}/api/problems/lang/py"
    token = request.session.get("token", "upset")
    
    # redirect to login page
    if token == "upset":
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "No token"})
    
    headers = { "Authorization": f"Bearer {token}" }
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


@router.post("/check")
async def post_check(answer: AnswerSchema):
    """
    Виймає рішення з відповіді, відправляє його на перевірку до PSS і повертає відповідь від PSS   
    """
    api_url = f"{PSS_HOST}/api/check"
    data = { "id": answer.id, "solving": answer.solving }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=data)
        # state = response.status_code
        json = response.json()
    except Exception as e:
        err_mes = f"Error during a check solving: {e}"
        logger.error(err_mes)
        return err_mes
    else:
        return json
