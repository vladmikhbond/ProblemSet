import os
import logging
import httpx
import datetime as dt

from fastapi import APIRouter, Depends, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..models.schemas import ProblemHeader, ProblemSchema, AnswerSchema
from .login_router import PSS_HOST, logger, payload_from_token
from sqlalchemy.orm import Session
from ..dal import get_db  # Функція для отримання сесії БД
from ..models.pss_models import ProblemSet

# шаблони Jinja2
path = os.path.join(os.getcwd(), 'app', 'templates')
templates = Jinja2Templates(directory=path)

router = APIRouter()


@router.get("/problems", summary="List of problem headers. Header is {id, title, attr}")
async def get_problem_list(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Показує студенту сторінку з задачами, розподіленими по відкритим задачникам.
    """
    problemsets: list[ProblemSet] = db.query(ProblemSet).all()
    open_problemsets = [ps for ps in problemsets if ps.is_open()]

    token = request.session.get("token", "")
    if token == "":
        # redirect to login page
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": "No token"
        })
    
    headers = { "Authorization": f"Bearer {token}" }

    psets = []
    for problemset in open_problemsets:
        pheaders = []
        for id in problemset.problem_ids.split():
            api_url = f"{PSS_HOST}/api/problems/{id}"
            async with httpx.AsyncClient() as client:
                response = await client.get(api_url, headers=headers)
            if response.is_success:
                json = response.json()
                problem_header = ProblemHeader(id=json["id"], title=json["title"], attr=json["attr"])
                pheaders.append(problem_header)

        delta = problemset.open_time - dt.datetime.now()
        rest_minutes:int = delta.total_seconds() / 60 + problemset.open_minutes
        psets.append({
                "id": problemset.id,
                "user_id": problemset.user_id,
                "rest_minutes": rest_minutes, 
                "headers": pheaders })

    return templates.TemplateResponse("problem_list.html", {"request": request, "psets": psets})


@router.get("/problem/{id}", summary="Get a problem.")
async def get_problem(
    id: str, 
    request: Request
):
    """Відкриває студенту вікно длоя вирішення задачі.
       Створює тікет, якщо такий ще не існує.
    """
    api_url = f"{PSS_HOST}/api/problems/{id}"
    token = request.session.get("token", "")
    headers = { "Authorization": f"Bearer {token}" }

    if token == "":
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


@router.post("/check", summary="Check the answer of a problem")
async def post_check(answer: AnswerSchema):
    """
    Виймає рішення з відповіді, відправляє його на перевірку до PSS і повертає відповідь від PSS 
    Створює тіскет з чергвим вирішенням
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
