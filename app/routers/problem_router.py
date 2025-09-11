import os
import logging
import httpx
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Request, Response, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..models.schemas import ProblemHeaderSchema, ProblemSchema, AnswerSchema
from ..utils.utils import PSS_HOST, delta2str, username_from_session
from sqlalchemy.orm import Session
from ..dal import get_db, writedown_to_ticket  # Функція для отримання сесії БД
from ..models.pss_models import ProblemSet

# шаблони Jinja2
path = os.path.join(os.getcwd(), 'app', 'templates')
templates = Jinja2Templates(directory=path)

router = APIRouter()


@router.get("/problems/lang/{lang}", summary="List of problem headers. Header is {id, title, attr}")
async def get_problem_heads(
    request: Request,
    lang:str,
):
    token = request.session.get("token", "")
    headers = {"Authorization": f"Bearer {token}"}
    api_url = f"{PSS_HOST}/api/problems/lang/{lang}"
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, headers=headers)
        if response.is_success:
            # {"id", "title", "attr"}
            json = response.json()
            return json
        else: 
            return {}     # TODO



@router.get("/problems/me", summary="List of problem headers. Header is {id, title, attr}")
async def get_open_problems(
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

    headers = {"Authorization": f"Bearer {token}"}
    psets = []
    for problemset in open_problemsets:
        pheaders = []
        for id in problemset.problem_ids.split():
            api_url = f"{PSS_HOST}/api/problems/{id}"
            async with httpx.AsyncClient() as client:
                response = await client.get(api_url, headers=headers)
                if response.is_success:
                    json = response.json()
                    problem_header = ProblemHeaderSchema(
                        id=json["id"], title=json["title"], attr=json["attr"])
                    pheaders.append(problem_header)

        rest_time: timedelta = problemset.open_time - datetime.now() + timedelta(minutes=problemset.open_minutes)
        psets.append({
            "id": problemset.id,
            "user_id": problemset.user_id,
            "rest_time": delta2str(rest_time),
            "headers": pheaders})

    return templates.TemplateResponse("open_problems.html", {"request": request, "psets": psets})


@router.get("/problem/{prob_id}", summary="Get a problem.")
async def get_problem(
    prob_id: str,
    request: Request
):
    """Відкриває студенту вікно для вирішення задачі.
       Створює тікет, якщо такий ще не існує.
    """
    api_url = f"{PSS_HOST}/api/problems/{prob_id}"
    token = request.session.get("token", "")
    headers = {"Authorization": f"Bearer {token}"}

    # redirect to login page
    if token == "":
        return templates.TemplateResponse("login.html", {"request": request, "error": "No token"})

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers)
        json_obj = response.json()
    except Exception as e:
        err_mes = f"Error during a problem request: {e}"
        print(err_mes)
        return RedirectResponse(url="/open_problems", status_code=302)
    else:
        # create a ticket
        username = username_from_session(request)
        writedown_to_ticket(username, prob_id)

        # open a problem window
        problem = ProblemSchema(**json_obj)
        return templates.TemplateResponse(
            "problem.html",
            {"request": request, "problem": problem})


@router.post("/check", summary="Check the answer of a problem")
async def post_check(answer: AnswerSchema, request: Request):
    """
    Виймає рішення з відповіді, відправляє його на перевірку до PSS і повертає відповідь від PSS 
    Створює тіскет з чергвим вирішенням
    """
    api_url = f"{PSS_HOST}/api/check"
    data = {"id": answer.id, "solving": answer.solving}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, json=data)
        # state = response.status_code
        json = response.json()
    except Exception as e:
        err_mes = f"Error during a check solving: {e}"
        print(err_mes)
        return err_mes
    else:
        # append a ticket
        username = username_from_session(request)
        writedown_to_ticket(username, answer.id, answer.solving, json)

        return json
